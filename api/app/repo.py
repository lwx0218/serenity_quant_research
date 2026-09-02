"""Read queries. Plain dicts in, plain dicts out; routers wrap them in schemas."""
from __future__ import annotations

import json
import sqlite3
from typing import Any

from .config import EVIDENCE_LEVELS

_LEVEL_RANK = {lvl: i for i, lvl in enumerate(EVIDENCE_LEVELS)}


def _row(r: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(r) if r is not None else None


def _rows(rs: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rs]


def _node_public(n: dict[str, Any]) -> dict[str, Any]:
    n = dict(n)
    extra = n.pop("extra", None)
    n["extra"] = json.loads(extra) if extra else None
    return n


# --------------------------------------------------------------------------- nodes
def get_node(conn: sqlite3.Connection, node_id: str) -> dict[str, Any] | None:
    r = conn.execute("SELECT * FROM nodes WHERE id = ?", (node_id,)).fetchone()
    return _node_public(_row(r)) if r else None


def children(conn: sqlite3.Connection, node_id: str) -> list[dict[str, Any]]:
    rs = conn.execute("SELECT * FROM nodes WHERE parent_id = ? ORDER BY sort, id", (node_id,)).fetchall()
    return [_node_public(x) for x in _rows(rs)]


def ancestors(conn: sqlite3.Connection, node_id: str) -> list[dict[str, Any]]:
    """Root first, excluding the node itself."""
    out: list[dict[str, Any]] = []
    cur = conn.execute("SELECT parent_id FROM nodes WHERE id = ?", (node_id,)).fetchone()
    pid = cur["parent_id"] if cur else None
    while pid:
        n = conn.execute("SELECT id, kind, name, name_en, code FROM nodes WHERE id = ?", (pid,)).fetchone()
        if not n:
            break
        out.append(dict(n))
        pid = conn.execute("SELECT parent_id FROM nodes WHERE id = ?", (pid,)).fetchone()["parent_id"]
    out.reverse()
    return out


def descendant_ids(conn: sqlite3.Connection, node_id: str) -> list[str]:
    ids, frontier = [node_id], [node_id]
    while frontier:
        q = ",".join("?" * len(frontier))
        nxt = [r["id"] for r in conn.execute(f"SELECT id FROM nodes WHERE parent_id IN ({q})", frontier)]
        ids.extend(nxt)
        frontier = nxt
    return ids


def chain_nodes_for(conn: sqlite3.Connection, node_id: str) -> list[dict[str, Any]]:
    """Chain nodes linked to this node or any descendant (a module inherits its parts' links)."""
    ids = descendant_ids(conn, node_id)
    q = ",".join("?" * len(ids))
    rs = conn.execute(
        f"""SELECT DISTINCT cn.* FROM chain_nodes cn
            JOIN node_chain_links l ON l.chain_node_id = cn.id
            WHERE l.node_id IN ({q}) ORDER BY cn.sort""",
        ids,
    ).fetchall()
    return _rows(rs)


def technologies_for(conn: sqlite3.Connection, node_id: str) -> list[dict[str, Any]]:
    ids = descendant_ids(conn, node_id)
    q = ",".join("?" * len(ids))
    rs = conn.execute(
        f"""SELECT DISTINCT t.* FROM technologies t
            JOIN node_tech_links l ON l.tech_id = t.id
            WHERE l.node_id IN ({q}) ORDER BY t.id""",
        ids,
    ).fetchall()
    return _rows(rs)


# ------------------------------------------------------------------------ companies
def _fold_exposures(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group exposure rows by company, keeping the strongest evidence level per company
    and the list of chain nodes it touches."""
    by_company: dict[str, dict[str, Any]] = {}
    for r in rows:
        c = by_company.setdefault(
            r["company_id"],
            {
                "id": r["company_id"],
                "name": r["name"],
                "short_name": r["short_name"],
                "ticker": r["ticker"],
                "exchange": r["exchange"],
                "country_region": r["country_region"],
                "universe_layer": r["universe_layer"],
                "coverage_priority": r["coverage_priority"],
                "evidence_level": r["evidence_level"],
                "chain_nodes": [],
                "roles": [],
            },
        )
        if _LEVEL_RANK.get(r["evidence_level"], -1) > _LEVEL_RANK.get(c["evidence_level"], -1):
            c["evidence_level"] = r["evidence_level"]
        cn = {"id": r["chain_node_id"], "name": r["chain_display_name"], "evidence_level": r["evidence_level"]}
        if cn not in c["chain_nodes"]:
            c["chain_nodes"].append(cn)
        if r["role"] and r["role"] not in c["roles"]:
            c["roles"].append(r["role"])
    # strongest evidence first; otherwise keep the seed's (infographic) order
    return sorted(by_company.values(), key=lambda c: -_LEVEL_RANK.get(c["evidence_level"], -1))


_EXPOSURE_SELECT = """
SELECT e.company_id, e.chain_node_id, e.node_id, e.role, e.evidence_level, e.note,
       c.name, c.short_name, c.ticker, c.exchange, c.country_region, c.universe_layer, c.coverage_priority,
       cn.display_name AS chain_display_name, cn.sort AS chain_sort
FROM exposures e
JOIN companies c ON c.id = e.company_id
JOIN chain_nodes cn ON cn.id = e.chain_node_id
"""


def companies_for_chain(conn: sqlite3.Connection, chain_node_id: str) -> list[dict[str, Any]]:
    rs = conn.execute(_EXPOSURE_SELECT + " WHERE e.chain_node_id = ? ORDER BY e.id", (chain_node_id,)).fetchall()
    return _fold_exposures(_rows(rs))


def companies_for_node(conn: sqlite3.Connection, node_id: str) -> list[dict[str, Any]]:
    """Companies exposed to any chain node this node (or its descendants) maps to,
    plus companies with an exposure pinned directly to one of those nodes."""
    ids = descendant_ids(conn, node_id)
    q = ",".join("?" * len(ids))
    rs = conn.execute(
        _EXPOSURE_SELECT
        + f""" WHERE e.chain_node_id IN (SELECT chain_node_id FROM node_chain_links WHERE node_id IN ({q}))
                  OR e.node_id IN ({q})
               ORDER BY e.id""",
        ids + ids,
    ).fetchall()
    return _fold_exposures(_rows(rs))


def list_companies(conn: sqlite3.Connection, chain: str | None = None, node: str | None = None,
                   q: str | None = None) -> list[dict[str, Any]]:
    if node:
        items = companies_for_node(conn, node)
    elif chain:
        items = companies_for_chain(conn, chain)
    else:
        rs = conn.execute(_EXPOSURE_SELECT + " ORDER BY e.id").fetchall()
        items = _fold_exposures(_rows(rs))
        # companies with no exposure at all still belong to the universe
        seen = {c["id"] for c in items}
        for r in conn.execute("SELECT * FROM companies ORDER BY universe_layer, short_name"):
            if r["id"] not in seen:
                d = dict(r)
                d.update({"evidence_level": None, "chain_nodes": [], "roles": []})
                items.append(d)
    if q:
        needle = q.strip().lower()
        items = [c for c in items if needle in (c["name"] or "").lower()
                 or needle in (c["short_name"] or "").lower()
                 or needle in (c["ticker"] or "").lower()
                 or needle in c["id"].lower()]
    return items


def get_company(conn: sqlite3.Connection, company_id: str) -> dict[str, Any] | None:
    c = _row(conn.execute("SELECT * FROM companies WHERE id = ?", (company_id,)).fetchone())
    if not c:
        return None
    exps = _rows(conn.execute(
        """SELECT e.id, e.chain_node_id, cn.display_name AS chain_name, cn.sort AS chain_sort,
                  e.node_id, n.name AS node_name, e.role, e.evidence_level, e.note,
                  s.id AS source_id, s.publisher AS source_publisher, s.title AS source_title,
                  s.kind AS source_kind, s.url AS source_url, s.year_range AS source_year_range
           FROM exposures e
           JOIN chain_nodes cn ON cn.id = e.chain_node_id
           LEFT JOIN nodes n ON n.id = e.node_id
           LEFT JOIN sources s ON s.id = e.source_id
           WHERE e.company_id = ? ORDER BY cn.sort, e.id""",
        (company_id,),
    ).fetchall())
    # modules whose parts map to any of the company's chain nodes
    chain_ids = sorted({e["chain_node_id"] for e in exps})
    modules: list[dict[str, Any]] = []
    if chain_ids:
        qm = ",".join("?" * len(chain_ids))
        modules = _rows(conn.execute(
            f"""SELECT DISTINCT m.id, m.kind, m.code, m.name, m.name_en, m.sort FROM nodes m
                JOIN nodes p ON p.parent_id = m.id
                JOIN node_chain_links l ON l.node_id = p.id
                WHERE m.kind = 'module' AND l.chain_node_id IN ({qm}) ORDER BY m.sort""",
            chain_ids,
        ).fetchall())
    best = None
    for e in exps:
        if best is None or _LEVEL_RANK.get(e["evidence_level"], -1) > _LEVEL_RANK.get(best, -1):
            best = e["evidence_level"]
    c.update({"evidence_level": best, "exposures": exps, "modules": modules})
    return c


# ---------------------------------------------------------------------------- chain
def list_chain(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    out = []
    for cn in _rows(conn.execute("SELECT * FROM chain_nodes ORDER BY sort").fetchall()):
        comps = companies_for_chain(conn, cn["id"])
        mods = _rows(conn.execute(
            """SELECT DISTINCT m.id, m.kind, m.code, m.name, m.name_en, m.sort FROM nodes m
               JOIN nodes p ON p.parent_id = m.id
               JOIN node_chain_links l ON l.node_id = p.id
               WHERE m.kind = 'module' AND l.chain_node_id = ? ORDER BY m.sort""",
            (cn["id"],),
        ).fetchall())
        cn["companies"] = comps
        cn["modules"] = mods
        out.append(cn)
    return out


# -------------------------------------------------------------------------- product
def product_tree(conn: sqlite3.Connection, product_id: str) -> dict[str, Any] | None:
    root = get_node(conn, product_id)
    if not root or root["kind"] != "product":
        return None
    mods = []
    for m in children(conn, product_id):
        m["children"] = children(conn, m["id"])
        m["chain_nodes"] = [{"id": c["id"], "name": c["display_name"]} for c in chain_nodes_for(conn, m["id"])]
        mods.append(m)
    root["children"] = mods
    root["chain"] = list_chain(conn)
    root["signal_path"] = (root.get("extra") or {}).get("signalPath")
    return root
