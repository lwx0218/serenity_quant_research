"""Import the market layer: events, series, reactions, crowding readings.

Today the only input is `cpo-sample-market.json` — style-sample data that
exists so the interface can be used before real feeds are wired in. Every
row it writes carries is_sample=1, and `python -m app.seed --rebuild --no-sample`
builds a database without it. Real adapters will write the same tables.
"""
from __future__ import annotations

import json
import random
import sqlite3
from datetime import date, datetime
from pathlib import Path

from . import analytics as A


def _d(s: str) -> date:
    return date.fromisoformat(s)


# ------------------------------------------------------------------ structure
def company_layers(conn: sqlite3.Connection, company_id: str) -> list[str]:
    """Modules a company is exposed to: exposure → chain node → parts → module."""
    rows = conn.execute(
        """SELECT DISTINCT m.id FROM exposures e
           JOIN node_chain_links l ON l.chain_node_id = e.chain_node_id
           JOIN nodes p ON p.id = l.node_id
           JOIN nodes m ON m.id = p.parent_id
           WHERE e.company_id = ? AND m.kind = 'module' ORDER BY m.sort""",
        (company_id,),
    ).fetchall()
    return [r["id"] for r in rows]


def basket_members(conn: sqlite3.Connection, node_id: str) -> list[str]:
    """Companies exposed to any chain node linked from this module's parts (or the part itself)."""
    rows = conn.execute(
        """SELECT DISTINCT e.company_id FROM exposures e
           WHERE e.chain_node_id IN (
             SELECT l.chain_node_id FROM node_chain_links l
             JOIN nodes n ON n.id = l.node_id
             WHERE n.id = ? OR n.parent_id = ?)
           ORDER BY e.company_id""",
        (node_id, node_id),
    ).fetchall()
    return [r["company_id"] for r in rows]


def product_members(conn: sqlite3.Connection) -> list[str]:
    return [r["company_id"] for r in conn.execute("SELECT DISTINCT company_id FROM exposures ORDER BY company_id")]


def primary_layer(conn: sqlite3.Connection, ev: dict) -> str | None:
    if ev.get("node_id"):
        return ev["node_id"]
    layers = company_layers(conn, ev["company_id"]) if ev.get("company_id") else []
    if not layers:
        return None
    # prefer the layer the event's chain node maps to, else the first
    if ev.get("chain_node_id"):
        for l in layers:
            hit = conn.execute(
                """SELECT 1 FROM node_chain_links l JOIN nodes p ON p.id = l.node_id
                   WHERE p.parent_id = ? AND l.chain_node_id = ?""", (l, ev["chain_node_id"])).fetchone()
            if hit:
                return l
    return layers[0]


# ------------------------------------------------------------- synthetic series
def synth_company_series(rng: random.Random, days: list[date], drift: float, vol: float,
                         impulses: list[tuple[date, float]]) -> A.Series:
    """Random walk plus event impulses: the full impulse lands on T+1 and 75% of it
    is given back over T+3..T+7, so efficacy stats come out event-like (half-life ≈ 4–6 days)."""
    shocks: dict[date, float] = {}
    quiet: set[date] = set()        # noise is damped around events so the sample reads as intended
    for ev_date, imp in impulses:
        t1 = A.add_trading_days(ev_date, 1)
        shocks[t1] = shocks.get(t1, 0.0) + imp
        for k in range(1, 8):
            quiet.add(A.add_trading_days(ev_date, k))
        for k in range(3, 8):                       # 75% given back over T+3..T+7 → half-life ≈ 5 days
            dk = A.add_trading_days(ev_date, k)
            shocks[dk] = shocks.get(dk, 0.0) - imp * 0.75 / 5
    out: A.Series = {}
    level = 100.0
    for i, d in enumerate(days):
        if i > 0:
            noise = rng.gauss(0.0, vol) * (0.2 if d in quiet else 1.0)
            level *= 1.0 + drift + noise + shocks.get(d, 0.0)
        out[d] = level
    return out


# ---------------------------------------------------------------------- import
def import_market(conn: sqlite3.Connection, seed_dir: Path, include_sample: bool = True) -> dict[str, int]:
    counts = {"events": 0, "series_points": 0, "reactions": 0, "crowding": 0}
    path = seed_dir / "cpo-sample-market.json"
    if not include_sample or not path.exists():
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('as_of', ?)", (date.today().isoformat(),))
        conn.commit()
        return counts
    with open(path, encoding="utf-8") as f:
        mk = json.load(f)
    as_of = _d(mk["asOf"])
    sample = 1 if mk.get("sample", True) else 0
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('as_of', ?)", (as_of.isoformat(),))
    cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('sample', ?)", (str(sample),))

    # ---- events -------------------------------------------------------------
    events = mk.get("events", [])
    cur.execute("DELETE FROM reactions"); cur.execute("DELETE FROM event_layers"); cur.execute("DELETE FROM events")
    for ev in events:
        cur.execute(
            """INSERT INTO events (id, date, company_id, node_id, chain_node_id, source_kind, source_title, source_url,
                                   category, title, summary, volume_ratio, turnover_pct_rank, status, is_sample)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (ev["id"], ev["date"], ev.get("company_id"), ev.get("node_id"), ev.get("chain_node_id"),
             ev["source_kind"], ev.get("source_title"), ev.get("source_url"), ev["category"], ev["title"],
             ev.get("summary"), ev.get("volume_ratio"), ev.get("turnover_pct_rank"), ev.get("status", "candidate"), sample),
        )
        layers = [ev["node_id"]] if ev.get("node_id") else company_layers(conn, ev["company_id"])
        for l in layers:
            cur.execute("INSERT OR IGNORE INTO event_layers (event_id, node_id) VALUES (?, ?)", (ev["id"], l))
    counts["events"] = len(events)

    # ---- synthetic series ----------------------------------------------------
    sp = mk["series"]
    rng = random.Random(sp.get("seed", 1))
    days = A.trading_days(_d(sp["start"]), as_of)
    per_company: dict[str, list[tuple[date, float]]] = {}
    for ev in events:
        if ev.get("company_id") and ev.get("impulse") is not None:
            imp = float(ev["impulse"])
            per_company.setdefault(ev["company_id"], []).append((_d(ev["date"]), imp))
            # a big event spills over to the same layer's other members (that is what "环节级" means)
            if abs(imp) >= 0.015:
                for layer in company_layers(conn, ev["company_id"])[:1]:
                    for peer in basket_members(conn, layer):
                        if peer != ev["company_id"]:
                            per_company.setdefault(peer, []).append((_d(ev["date"]), imp * float(sp.get("spillover", 0.2))))
    series: dict[str, A.Series] = {}
    companies = [r["id"] for r in conn.execute("SELECT id FROM companies ORDER BY id")]
    for cid in companies:
        prm = sp.get("companies", {}).get(cid, {})
        series[f"company:{cid}"] = synth_company_series(
            rng, days, prm.get("drift", sp.get("defaultDrift", 0.0005)), prm.get("vol", sp.get("defaultVol", 0.016)),
            per_company.get(cid, []))
    # layer baskets + whole-device basket
    modules = [r["id"] for r in conn.execute("SELECT id FROM nodes WHERE kind='module' ORDER BY sort")]
    product_id = conn.execute("SELECT id FROM nodes WHERE kind='product'").fetchone()["id"]
    for m in modules:
        members = basket_members(conn, m)
        if members:
            series[f"basket:{m}"] = A.basket_series([series[f"company:{c}"] for c in members])
    series[f"basket:{product_id}"] = A.basket_series([series[f"company:{c}"] for c in product_members(conn)])
    # layer-subject events shock the layer basket directly (e.g. a PCB price rumour)
    for ev in events:
        if ev.get("node_id") and ev.get("impulse") is not None and f"basket:{ev['node_id']}" in series:
            s = series[f"basket:{ev['node_id']}"]
            t1 = A.add_trading_days(_d(ev["date"]), 1)
            scale = 1.0 + float(ev["impulse"])
            for d in list(s.keys()):
                if d >= t1:
                    s[d] *= scale
    cur.execute("DELETE FROM series")
    cur.executemany(
        "INSERT INTO series (instrument, date, value, is_sample) VALUES (?,?,?,?)",
        [(inst, d.isoformat(), v, sample) for inst, s in series.items() for d, v in s.items()],
    )
    counts["series_points"] = sum(len(s) for s in series.values())

    # ---- reactions (computed, not typed in) ----------------------------------
    now = datetime.now().isoformat(timespec="seconds")
    n = 0
    for ev in events:
        subj_key = f"company:{ev['company_id']}" if ev.get("company_id") else f"basket:{ev['node_id']}"
        layer = primary_layer(conn, ev)
        # a company's reference is the *other* members of its layer, so it is not measured against itself
        basket = None
        if layer and ev.get("company_id"):
            peers = [c for c in basket_members(conn, layer) if c != ev["company_id"]]
            basket = A.basket_series([series[f"company:{c}"] for c in peers]) if peers else None
        product = series[f"basket:{product_id}"]
        subj = series.get(subj_key)
        if not subj:
            continue
        for h in A.HORIZONS:
            r_abs = A.reaction(subj, None, _d(ev["date"]), h, as_of)
            if r_abs is None:
                continue
            r_b = A.reaction(subj, basket, _d(ev["date"]), h, as_of) if basket else None
            r_p = A.reaction(subj, product, _d(ev["date"]), h, as_of)
            cur.execute(
                "INSERT OR REPLACE INTO reactions (event_id, horizon, abs_return, excess_basket, excess_product, computed_at) VALUES (?,?,?,?,?,?)",
                (ev["id"], h, r_abs["abs_return"], r_b["excess"] if r_b else None, r_p["excess"] if r_p else None, now),
            )
            n += 1
    counts["reactions"] = n

    # ---- crowding + valuation -----------------------------------------------
    cur.execute("DELETE FROM crowding"); cur.execute("DELETE FROM valuation")
    cr = mk.get("crowding", {})
    k = 0
    for cid, m in cr.get("companies", {}).items():
        cur.execute("INSERT INTO crowding (instrument, as_of, window_days, metrics, is_sample) VALUES (?,?,?,?,?)",
                    (f"company:{cid}", as_of.isoformat(), 20, json.dumps(m, ensure_ascii=False), sample)); k += 1
    for nid, m in cr.get("baskets", {}).items():
        cur.execute("INSERT INTO crowding (instrument, as_of, window_days, metrics, is_sample) VALUES (?,?,?,?,?)",
                    (f"basket:{nid}", as_of.isoformat(), 20, json.dumps(m, ensure_ascii=False), sample)); k += 1
    counts["crowding"] = k
    for cid, v in mk.get("valuation", {}).items():
        cur.execute("INSERT OR REPLACE INTO valuation (company_id, as_of, pe_ttm, pe_pct_rank_5y, is_sample) VALUES (?,?,?,?,?)",
                    (cid, as_of.isoformat(), v.get("pe_ttm"), v.get("pe_pct_rank_5y"), sample))
    conn.commit()
    return counts
