"""Read side of the market layer: events with reactions and freshness, layer
activity, baskets, crowding, efficacy, resonance. Everything is computed from
SQLite at request time (the data is small); every result carries `as_of`."""
from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from typing import Any

from . import analytics as A
from . import physical as PH
from .market_seed import basket_members, company_layers, primary_layer, product_members

CATEGORY_LABEL = {
    "capex": "扩产", "order": "订单合同", "qualification": "认证导入", "supply": "供需", "price": "涨价",
    "buyback": "回购", "roadmap": "技术路线", "other": "其他",
}
SOURCE_LABEL = {"announcement": "公告", "irm": "互动易", "news": "新闻", "official": "官网", "filing": "文件"}
DIRECTIONAL_CATEGORIES = ("capex", "order", "qualification", "supply", "price")  # can upgrade an exposure


def _d(s: str | date | None) -> date | None:
    if s is None or isinstance(s, date):
        return s
    return date.fromisoformat(s)


def as_of(conn: sqlite3.Connection) -> date:
    r = conn.execute("SELECT value FROM settings WHERE key='as_of'").fetchone()
    return _d(r["value"]) if r else date.today()


def is_sample(conn: sqlite3.Connection) -> bool:
    r = conn.execute("SELECT value FROM settings WHERE key='sample'").fetchone()
    return bool(r and r["value"] == "1")


def product_id(conn: sqlite3.Connection) -> str:
    return conn.execute("SELECT id FROM nodes WHERE kind='product'").fetchone()["id"]


# ---------------------------------------------------------------------- series
def load_series(conn: sqlite3.Connection, instrument: str, start: date | None = None) -> A.Series:
    if start:
        rs = conn.execute("SELECT date, value FROM series WHERE instrument=? AND date>=? ORDER BY date", (instrument, start.isoformat()))
    else:
        rs = conn.execute("SELECT date, value FROM series WHERE instrument=? ORDER BY date", (instrument,))
    return {date.fromisoformat(r["date"]): r["value"] for r in rs}


def series_points(s: A.Series, base_date: date | None = None) -> list[list[Any]]:
    if base_date:
        s = A.index_to(s, base_date)
    return [[d.isoformat(), round(v, 3)] for d, v in sorted(s.items())]


def excess_since(conn: sqlite3.Connection, instrument: str, reference: str, since: date, until: date) -> float | None:
    return A.excess_return(load_series(conn, instrument, since - timedelta(days=7)), load_series(conn, reference, since - timedelta(days=7)), since, until)


# ------------------------------------------------------------------- structure
def module_rows(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT id, sort, code, name, name_en, summary FROM nodes WHERE kind='module' ORDER BY sort")]


def module_of(conn: sqlite3.Connection, node_id: str) -> dict | None:
    r = conn.execute("SELECT id, sort, code, name, name_en, kind, parent_id FROM nodes WHERE id=?", (node_id,)).fetchone()
    if not r:
        return None
    r = dict(r)
    if r["kind"] == "part" and r["parent_id"]:
        return module_of(conn, r["parent_id"])
    return r


def company_brief(conn: sqlite3.Connection, company_id: str) -> dict | None:
    r = conn.execute("SELECT id, name, short_name, ticker, exchange, country_region FROM companies WHERE id=?", (company_id,)).fetchone()
    return dict(r) if r else None


def primary_layer_id(conn: sqlite3.Connection, ev: dict) -> str | None:
    """The one layer an event is read against — same rule as the reaction computation."""
    if ev.get("node_id"):
        m = module_of(conn, ev["node_id"])
        return m["id"] if m else None
    return primary_layer(conn, ev)


def peer_basket(conn: sqlite3.Connection, layer: str, company_id: str, start: date | None = None) -> A.Series:
    """Equal-weight basket of the layer's other members (the reference for a company's reaction)."""
    peers = [c for c in basket_members(conn, layer) if c != company_id]
    return A.basket_series([load_series(conn, f"company:{c}", start) for c in peers]) if peers else {}


# -------------------------------------------------------------------- efficacy
def efficacy_for(conn: sqlite3.Connection, node_id: str, days: int = 90, when: date | None = None) -> dict | None:
    """Event efficacy of a layer basket over a rolling window, from the event
    paths recomputed against the whole-device basket."""
    when = when or as_of(conn)
    since = when - timedelta(days=days)
    rows = conn.execute(
        """SELECT e.* FROM events e JOIN event_layers l ON l.event_id = e.id
           WHERE l.node_id = ? AND e.date >= ? AND e.date <= ? AND e.status != 'ignored' ORDER BY e.date""",
        (node_id, since.isoformat(), when.isoformat()),
    ).fetchall()
    if not rows:
        return None
    pid = product_id(conn)
    product = load_series(conn, f"basket:{pid}", since - timedelta(days=10))
    paths = []
    for r in rows:
        ev = dict(r)
        inst = f"company:{ev['company_id']}" if ev["company_id"] else f"basket:{ev['node_id']}"
        subj = load_series(conn, inst, since - timedelta(days=10))
        if not subj:
            continue
        paths.append({"category": ev["category"], "path": A.excess_path(subj, product, _d(ev["date"]), 20, when)})
    eff = A.efficacy(paths)
    if eff:
        eff.update({"node_id": node_id, "window_days": days, "as_of": when.isoformat(), "reference": "整机篮子",
                    "by_category_label": {CATEGORY_LABEL.get(k, k): v for k, v in eff["by_category"].items()}})
    return eff


def validity_days(conn: sqlite3.Connection, node_id: str | None, cache: dict | None = None) -> int:
    if not node_id:
        return A.DEFAULT_VALIDITY_DAYS
    if cache is not None and node_id in cache:
        return cache[node_id]
    eff = efficacy_for(conn, node_id)
    v = eff["validity_days"] if eff else A.DEFAULT_VALIDITY_DAYS
    if cache is not None:
        cache[node_id] = v
    return v


# ---------------------------------------------------------------------- events
def _reactions(conn: sqlite3.Connection, event_id: str) -> dict[int, dict]:
    return {r["horizon"]: dict(r) for r in conn.execute("SELECT * FROM reactions WHERE event_id=?", (event_id,))}


def event_public(conn: sqlite3.Connection, ev: dict, when: date, vcache: dict | None = None) -> dict:
    rx = _reactions(conn, ev["id"])
    layer = primary_layer_id(conn, ev)
    # a company's reaction is read against its layer basket; a layer's against the whole device
    key = "excess_basket" if ev.get("company_id") else "excess_product"
    t = {f"t{h}": (rx[h][key] if h in rx and rx[h][key] is not None else rx[h]["excess_product"] if h in rx else None) for h in A.HORIZONS}
    fr = A.freshness(_d(ev["date"]), when, validity_days(conn, layer, vcache), t["t1"])
    layers = [r["node_id"] for r in conn.execute("SELECT node_id FROM event_layers WHERE event_id=?", (ev["id"],))]
    subject_node = module_of(conn, ev["node_id"]) if ev.get("node_id") else None
    company = company_brief(conn, ev["company_id"]) if ev.get("company_id") else None
    return {
        "id": ev["id"], "date": ev["date"], "title": ev["title"], "summary": ev.get("summary"),
        "category": ev["category"], "category_label": CATEGORY_LABEL.get(ev["category"], ev["category"]),
        "source_kind": ev["source_kind"], "source_label": SOURCE_LABEL.get(ev["source_kind"], ev["source_kind"]),
        "source_title": ev.get("source_title"), "source_url": ev.get("source_url"),
        "company": company, "node": subject_node, "layer_id": layer, "layer_ids": layers,
        "reaction": {**t, "reference": "篮子" if ev.get("company_id") else "整机",
                     "abs_t1": rx[1]["abs_return"] if 1 in rx else None},
        "volume_ratio": ev.get("volume_ratio"), "turnover_pct_rank": ev.get("turnover_pct_rank"),
        "freshness": fr, "status": ev.get("status", "candidate"), "is_sample": bool(ev.get("is_sample")),
        "part": PH.part_for_event(conn, ev.get("company_id"), ev.get("category")),
    }


def list_events(conn: sqlite3.Connection, node: str | None = None, company: str | None = None,
                days: int | None = None, limit: int = 50, when: date | None = None) -> list[dict]:
    when = when or as_of(conn)
    sql, args = "SELECT DISTINCT e.* FROM events e", []
    where = ["e.status != 'ignored'", "e.date <= ?"]
    args.append(when.isoformat())
    if node:
        m = module_of(conn, node)
        sql += " JOIN event_layers l ON l.event_id = e.id"
        where.append("l.node_id = ?"); args.append(m["id"] if m else node)
    if company:
        where.append("e.company_id = ?"); args.append(company)
    if days:
        where.append("e.date >= ?"); args.append((when - timedelta(days=days)).isoformat())
    sql += " WHERE " + " AND ".join(where) + " ORDER BY e.date DESC, e.id LIMIT ?"
    args.append(limit)
    vcache: dict = {}
    return [event_public(conn, dict(r), when, vcache) for r in conn.execute(sql, args)]


def get_event(conn: sqlite3.Connection, event_id: str, when: date | None = None) -> dict | None:
    r = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    return event_public(conn, dict(r), when or as_of(conn)) if r else None


# ------------------------------------------------------------------- activity
def layer_activity(conn: sqlite3.Connection, days: int = 7, when: date | None = None) -> list[dict]:
    """Per module: events in the window and the basket's excess over the whole
    device across the window (the 'basket 7 天' reading)."""
    when = when or as_of(conn)
    start = when - timedelta(days=days)
    pid = product_id(conn)
    product = load_series(conn, f"basket:{pid}", start - timedelta(days=10))
    out = []
    for m in module_rows(conn):
        n = conn.execute(
            """SELECT COUNT(DISTINCT e.id) FROM events e JOIN event_layers l ON l.event_id=e.id
               WHERE l.node_id=? AND e.date>=? AND e.date<=? AND e.status!='ignored'""",
            (m["id"], start.isoformat(), when.isoformat())).fetchone()[0]
        basket = load_series(conn, f"basket:{m['id']}", start - timedelta(days=10))
        exc = A.excess_return(basket, product, start, when) if basket else None
        direction = None
        if exc is not None and (n > 0 or abs(exc) >= 0.01):
            direction = "pos" if exc >= A.REACTION_THRESHOLD else "neg" if exc <= -A.REACTION_THRESHOLD else "neu"
        out.append({**m, "events": n, "basket_excess": exc, "direction": direction, "has_basket": bool(basket)})
    return out


# -------------------------------------------------------------------- crowding
def crowding_for(conn: sqlite3.Connection, instrument: str) -> dict | None:
    r = conn.execute("SELECT * FROM crowding WHERE instrument=? ORDER BY as_of DESC LIMIT 1", (instrument,)).fetchone()
    if not r:
        return None
    metrics = json.loads(r["metrics"])
    dirs = A.crowding_directions(metrics)
    return {"instrument": instrument, "as_of": r["as_of"], "window_days": r["window_days"], "metrics": metrics,
            "directions": dirs["per_metric"], "direction": dirs["overall"], "is_sample": bool(r["is_sample"]),
            "level": A.crowd_level(metrics.get("ret20_pct_rank"))}


# --------------------------------------------------------------------- baskets
def basket_summary(conn: sqlite3.Connection, m: dict, when: date) -> dict:
    members = basket_members(conn, m["id"])
    pid = product_id(conn)
    start3 = when - timedelta(days=91)
    b = load_series(conn, f"basket:{m['id']}", start3 - timedelta(days=10))
    p = load_series(conn, f"basket:{pid}", start3 - timedelta(days=10))
    cr = crowding_for(conn, f"basket:{m['id']}")
    last = list_events(conn, node=m["id"], limit=1, when=when)
    return {
        "node_id": m["id"], "sort": m["sort"], "code": m["code"], "name": m["name"], "name_en": m["name_en"],
        "members": len(members), "ret_3m": A.period_return(b, start3, when) if b else None,
        "excess_3m": A.excess_return(b, p, start3, when) if b else None,
        "crowd_pct": cr["metrics"].get("ret20_pct_rank") if cr else None, "crowd_level": cr["level"] if cr else None,
        "crowd_direction": cr["directions"]["ret20_pct_rank"] if cr else None,
        "last_event": ({"date": last[0]["date"], "category_label": last[0]["category_label"], "t1": last[0]["reaction"]["t1"],
                        "freshness": last[0]["freshness"]} if last else None),
    }


def basket_detail(conn: sqlite3.Connection, node_id: str, months: int = 6, when: date | None = None) -> dict | None:
    when = when or as_of(conn)
    m = module_of(conn, node_id)
    if not m:
        return None
    pid = product_id(conn)
    start = when - timedelta(days=30 * months)
    b = load_series(conn, f"basket:{m['id']}", start - timedelta(days=10))
    p = load_series(conn, f"basket:{pid}", start - timedelta(days=10))
    members = basket_members(conn, m["id"])
    start3 = when - timedelta(days=91)
    rows = []
    for cid in members:
        c = company_brief(conn, cid)
        s = load_series(conn, f"company:{cid}", start - timedelta(days=10))
        cr = crowding_for(conn, f"company:{cid}")
        val = conn.execute("SELECT pe_ttm, pe_pct_rank_5y FROM valuation WHERE company_id=?", (cid,)).fetchone()
        ev = list_events(conn, company=cid, limit=1, when=when)
        lvl = conn.execute(
            """SELECT evidence_level FROM exposures WHERE company_id=? ORDER BY
               CASE evidence_level WHEN 'reviewed' THEN 0 WHEN 'candidate' THEN 1 ELSE 2 END LIMIT 1""", (cid,)).fetchone()
        rows.append({
            "company": c, "ret_3m": A.period_return(s, start3, when) if s else None,
            "ret_6m": A.period_return(s, start, when) if s else None,
            "pe_pct_rank_5y": val["pe_pct_rank_5y"] if val else None,
            "crowd_pct": cr["metrics"].get("ret20_pct_rank") if cr else None, "crowd_level": cr["level"] if cr else None,
            "crowd_direction": A.crowding_directions(cr["metrics"])["per_metric"]["ret20_pct_rank"] if cr else None,
            "last_event": ({"id": ev[0]["id"], "date": ev[0]["date"], "category_label": ev[0]["category_label"],
                            "t1": ev[0]["reaction"]["t1"], "freshness": ev[0]["freshness"]} if ev else None),
            "evidence_level": lvl["evidence_level"] if lvl else None,
        })
    # events drawn on the basket line: window events whose subject is a member
    chart_events = []
    for e in list_events(conn, node=m["id"], days=30 * months, limit=12, when=when):
        v = A.value_at(A.index_to(b, start), _d(e["date"])) if b else None
        if v is not None:
            chart_events.append({"id": e["id"], "date": e["date"], "category_label": e["category_label"], "value": round(v, 3),
                                 "company": e["company"]["short_name"] if e["company"] else None})
    others = [basket_summary(conn, mm, when) for mm in module_rows(conn) if mm["id"] != m["id"]]
    others = [o for o in others if o["members"] > 0]
    return {
        "as_of": when.isoformat(), "node": m, "members": rows, "window_months": months,
        "series": {"basket": series_points(b, start) if b else [], "product": series_points(p, start) if p else []},
        "chart_events": chart_events,
        "excess_window": A.excess_return(b, p, start, when) if b else None,
        "ret_window": A.period_return(b, start, when) if b else None,
        "efficacy": efficacy_for(conn, m["id"], when=when),
        "crowding": crowding_for(conn, f"basket:{m['id']}"),
        "member_dispersion": _dispersion(rows),
        "others": others,
        "product_members": len(product_members(conn)),
    }


def _dispersion(rows: list[dict]) -> dict:
    hi = sum(1 for r in rows if r["crowd_level"] == "高")
    lo = sum(1 for r in rows if r["crowd_level"] == "低")
    mid = sum(1 for r in rows if r["crowd_level"] == "中")
    return {"high": hi, "mid": mid, "low": lo}


# ------------------------------------------------------------------- resonance
def resonance(conn: sqlite3.Connection, event_id: str, when: date | None = None) -> dict | None:
    when = when or as_of(conn)
    ev = get_event(conn, event_id, when)
    if not ev:
        return None
    ev_date = _d(ev["date"])
    layer = ev["layer_id"]
    pid = product_id(conn)
    t1d, t3d = A.add_trading_days(ev_date, 1), A.add_trading_days(ev_date, 3)
    start = ev_date - timedelta(days=10)
    product = load_series(conn, f"basket:{pid}", start)
    layer_b = load_series(conn, f"basket:{layer}", start) if layer else {}

    peers = []
    if layer and ev["company"]:
        for cid in basket_members(conn, layer):
            if cid == ev["company"]["id"]:
                continue
            s = load_series(conn, f"company:{cid}", start)
            r = A.reaction(s, None, ev_date, 1, when)
            peers.append({"company": company_brief(conn, cid), "t1": r["abs_return"] if r else None})
    self_t1 = ev["reaction"]["abs_t1"]
    self_excess = ev["reaction"]["t1"]
    rx3 = conn.execute("SELECT abs_return FROM reactions WHERE event_id=? AND horizon=3", (event_id,)).fetchone()
    same = [p for p in peers if p["t1"] is not None and self_t1 is not None and (p["t1"] >= 0) == (self_t1 >= 0)]
    n_peers = sum(1 for p in peers if p["t1"] is not None)
    basket_t1 = A.excess_return(layer_b, product, ev_date, t1d) if layer_b and t1d <= when else None

    # adjacent layers in the stack (the neighbours in sort order)
    adjacent = []
    mods = module_rows(conn)
    idx = next((i for i, m in enumerate(mods) if m["id"] == layer), None)
    if idx is not None:
        for j in (idx - 1, idx + 1):
            if 0 <= j < len(mods):
                nb = load_series(conn, f"basket:{mods[j]['id']}", start)
                r = A.excess_return(nb, product, ev_date, t1d) if nb and t1d <= when else None
                adjacent.append({"node": {"id": mods[j]["id"], "name": mods[j]["name"], "sort": mods[j]["sort"]},
                                 "t1": r, "relation": "上一层" if j < idx else "下一层"})

    attention = None
    if ev["company"]:
        cr = crowding_for(conn, f"company:{ev['company']['id']}")
        if cr:
            attention = {**cr["metrics"].get("attention", {}), "turnover_pct_rank": cr["metrics"].get("turnover_pct_rank")}

    baseline = None
    if ev["company"]:
        hist = [e for e in list_events(conn, company=ev["company"]["id"], days=365, limit=100, when=when)
                if e["category"] == ev["category"] and e["id"] != ev["id"] and e["reaction"]["t1"] is not None]
        if hist:
            vals = [e["reaction"]["t1"] for e in hist]
            avg = sum(vals) / len(vals)
            baseline = {"n": len(hist), "avg_t1": avg, "hits": sum(1 for v in vals if v > 0),
                        "above": self_excess is not None and self_excess > avg}

    return {
        "as_of": when.isoformat(), "event": ev,
        "self": {"t1": self_t1, "t3": (rx3["abs_return"] if rx3 else None), "excess_t1": ev["reaction"]["t1"],
                 "volume_ratio": ev["volume_ratio"], "turnover_pct_rank": ev["turnover_pct_rank"]},
        "peers": peers, "same_direction": {"k": len(same) + (1 if self_t1 is not None else 0), "n": n_peers + (1 if self_t1 is not None else 0)},
        "basket_t1": basket_t1, "adjacent": adjacent, "attention": attention, "baseline": baseline,
        "layer": module_of(conn, layer) if layer else None,
    }


# ------------------------------------------------------------- verifications
def pending_verifications(conn: sqlite3.Connection, company: str | None = None, when: date | None = None) -> list[dict]:
    """Two kinds of things waiting for a human: an event that could lift a
    `reference` exposure to `candidate`, and a `candidate` exposure awaiting review."""
    when = when or as_of(conn)
    out = []
    handled = {r["event_id"] for r in conn.execute("SELECT event_id FROM verifications WHERE event_id IS NOT NULL")}
    for e in list_events(conn, company=company, days=14, limit=100, when=when):
        if e["id"] in handled or not e["company"] or e["category"] not in DIRECTIONAL_CATEGORIES or e["source_kind"] not in ("announcement", "official", "filing"):
            continue
        layer = e["layer_id"]
        if not layer:
            continue
        exp = conn.execute(
            """SELECT e.id, e.evidence_level, cn.display_name AS chain_name, cn.id AS chain_id FROM exposures e
               JOIN chain_nodes cn ON cn.id = e.chain_node_id
               WHERE e.company_id = ? AND e.chain_node_id IN (
                 SELECT l.chain_node_id FROM node_chain_links l JOIN nodes p ON p.id = l.node_id WHERE p.parent_id = ? OR p.id = ?)
               ORDER BY CASE e.evidence_level WHEN 'reference' THEN 0 WHEN 'candidate' THEN 1 ELSE 2 END LIMIT 1""",
            (e["company"]["id"], layer, layer)).fetchone()
        if exp and exp["evidence_level"] == "reference":
            out.append({"kind": "upgrade", "event": e, "exposure_id": exp["id"], "chain_name": exp["chain_name"],
                        "company": e["company"], "from_level": "reference", "to_level": "candidate",
                        "text": f"{e['company']['short_name']} → {exp['chain_name']} · {e['date'][5:]} {e['source_label']}可作为来源,行业图示 → 候选",
                        "detail": f"{e['date'][5:]} {e['source_label']}提到{exp['chain_name']}相关产线或产品,可作为来源升级这条关系。",
                        "direction": "pos" if (e["reaction"]["t1"] or 0) > 0 else "neu"})
    handled_exp = {r["exposure_id"] for r in conn.execute("SELECT exposure_id FROM verifications WHERE exposure_id IS NOT NULL AND kind IN ('accept','reject')")}
    q = "SELECT e.id, e.company_id, e.evidence_level, e.note, cn.display_name AS chain_name, s.title AS source_title, s.url AS source_url FROM exposures e JOIN chain_nodes cn ON cn.id=e.chain_node_id LEFT JOIN sources s ON s.id=e.source_id WHERE e.evidence_level='candidate'"
    args: list = []
    if company:
        q += " AND e.company_id=?"; args.append(company)
    for r in conn.execute(q, args):
        if r["id"] in handled_exp:
            continue
        c = company_brief(conn, r["company_id"])
        out.append({"kind": "review", "exposure_id": r["id"], "company": c, "chain_name": r["chain_name"],
                    "from_level": "candidate", "to_level": "reviewed",
                    "text": f"{c['short_name']} → {r['chain_name']} · {r['source_title'] or '已有来源'}(既有候选)· 候选 → 已核验",
                    "detail": r["note"] or "", "source_url": r["source_url"], "direction": "neu"})
    return out


def apply_verification(conn: sqlite3.Connection, action: str, event_id: str | None, exposure_id: int | None, note: str | None = None) -> dict:
    from datetime import datetime
    now = datetime.now().isoformat(timespec="seconds")
    if exposure_id is not None:
        row = conn.execute("SELECT evidence_level FROM exposures WHERE id=?", (exposure_id,)).fetchone()
        if not row:
            raise LookupError(f"exposure {exposure_id} not found")
        expected = {"upgrade": "reference", "ignore": "reference", "accept": "candidate", "reject": "candidate"}.get(action)
        if expected and row["evidence_level"] != expected:
            raise ValueError(f"exposure {exposure_id} is {row['evidence_level']}, expected {expected} for {action}")
    if event_id is not None and not conn.execute("SELECT 1 FROM events WHERE id=?", (event_id,)).fetchone():
        raise LookupError(f"event {event_id!r} not found")
    if action == "upgrade" and exposure_id:
        ev = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone() if event_id else None
        src_id = None
        if ev and ev["source_url"]:
            src_id = f"src.event.{ev['id']}"
            conn.execute("INSERT OR REPLACE INTO sources (id, publisher, title, kind, year_range, url, note) VALUES (?,?,?,?,?,?,?)",
                         (src_id, ev["source_title"], ev["title"], ev["source_kind"], ev["date"][:4], ev["source_url"], "upgraded from inbox"))
        conn.execute("UPDATE exposures SET evidence_level='candidate', source_id=COALESCE(?, source_id), note=COALESCE(?, note) WHERE id=? AND evidence_level='reference'",
                     (src_id, note, exposure_id))
    elif action == "accept" and exposure_id:
        conn.execute("UPDATE exposures SET evidence_level='reviewed' WHERE id=? AND evidence_level='candidate'", (exposure_id,))
    elif action == "reject" and exposure_id:
        conn.execute("UPDATE exposures SET evidence_level='reference' WHERE id=? AND evidence_level='candidate'", (exposure_id,))
    elif action == "ignore":
        pass
    else:
        raise ValueError(f"unknown action {action!r}")
    conn.execute("INSERT INTO verifications (kind, event_id, exposure_id, note, created_at) VALUES (?,?,?,?,?)",
                 (action, event_id, exposure_id, note, now))
    conn.commit()
    return {"ok": True, "action": action, "event_id": event_id, "exposure_id": exposure_id}


# ------------------------------------------------------------------- companies
def company_market(conn: sqlite3.Connection, company_id: str, months: int = 6, when: date | None = None) -> dict | None:
    when = when or as_of(conn)
    c = company_brief(conn, company_id)
    if not c:
        return None
    pid = product_id(conn)
    start = when - timedelta(days=30 * months)
    s = load_series(conn, f"company:{company_id}", start - timedelta(days=10))
    layers = company_layers(conn, company_id)
    layer = layers[0] if layers else None
    b = peer_basket(conn, layer, company_id, start - timedelta(days=10)) if layer else {}
    p = load_series(conn, f"basket:{pid}", start - timedelta(days=10))
    start3 = when - timedelta(days=91)
    val = conn.execute("SELECT pe_ttm, pe_pct_rank_5y FROM valuation WHERE company_id=?", (company_id,)).fetchone()
    events = list_events(conn, company=company_id, days=30, limit=20, when=when)
    chart_events = []
    if s:
        idx = A.index_to(s, start)
        for e in list_events(conn, company=company_id, days=30 * months, limit=12, when=when):
            v = A.value_at(idx, _d(e["date"]))
            if v is not None:
                chart_events.append({"id": e["id"], "date": e["date"], "category_label": e["category_label"], "value": round(v, 3)})
    mods = [module_of(conn, l) for l in layers]
    return {
        "as_of": when.isoformat(), "company": c, "layers": [m for m in mods if m], "primary_layer": module_of(conn, layer) if layer else None,
        "series": series_points(s, start) if s else [], "chart_events": chart_events, "window_months": months,
        "metrics": {
            "pe_ttm": val["pe_ttm"] if val else None, "pe_pct_rank_5y": val["pe_pct_rank_5y"] if val else None,
            "ret_3m": A.period_return(s, start3, when) if s else None,
            "excess_basket_3m": A.excess_return(s, b, start3, when) if s and b else None,
            "excess_product_3m": A.excess_return(s, p, start3, when) if s else None,
            "last": round(A.value_at(A.index_to(s, start), when) or 0, 1) if s else None,
        },
        "crowding": crowding_for(conn, f"company:{company_id}"),
        "events_30d": events,
        "pending_verifications": pending_verifications(conn, company=company_id, when=when),
        "sample": is_sample(conn),
    }


def companies_with_last_event(conn: sqlite3.Connection, company_ids: list[str], when: date | None = None) -> dict[str, dict]:
    """For a company list on a layer page: the latest event and its T+1."""
    when = when or as_of(conn)
    out = {}
    for cid in company_ids:
        ev = list_events(conn, company=cid, limit=1, when=when)
        out[cid] = ({"id": ev[0]["id"], "date": ev[0]["date"], "category_label": ev[0]["category_label"],
                     "t1": ev[0]["reaction"]["t1"], "freshness": ev[0]["freshness"]} if ev else None)
    return out


def node_market(conn: sqlite3.Connection, node_id: str, days: int = 7, when: date | None = None) -> dict | None:
    """What the selected-layer page needs beyond the taxonomy: basket reading,
    events in the window with their conclusion, and each company's last event."""
    from . import insights, research  # local import: research depends on market
    when = when or as_of(conn)
    m = module_of(conn, node_id)
    if not m:
        return None
    act = next((a for a in layer_activity(conn, days, when) if a["id"] == m["id"]), None)
    events = list_events(conn, node=m["id"], days=days, limit=20, when=when)
    members = basket_members(conn, m["id"])
    return {
        "as_of": when.isoformat(), "window_days": days, "module": m, "sample": is_sample(conn),
        "basket": {"excess": act["basket_excess"] if act else None, "direction": act["direction"] if act else None, "members": len(members)},
        "events": events, "events_conclusion": insights.layer_events(events, m["name"]),
        "validity_days": validity_days(conn, m["id"]),
        "thesis": research.thesis_for_node(conn, node_id, when),
        "company_events": companies_with_last_event(conn, members, when),
        "backlinks": research.backlinks(conn, {m["name"]}, {f"basket:{m['id']}"}, exclude=m["id"]),
    }
