"""从接入层的事实表推导既有分析代码要读的东西：
series（公司指数 + 篮子指数）→ reactions（每条事件各 horizon 的反应）→ 事件的量比 / 换手分位 → as_of。
只要 bars 变了就整体重算；几万行的 SQLite 上是秒级的事。"""
from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta
from statistics import mean, pstdev

from .. import analytics as A
from .. import physical as PH
from ..market_seed import basket_members, company_layers, primary_layer

CORE_STAGES = ("chip", "device", "engine", "module")


# ------------------------------------------------------------------ series
def company_close_series(conn: sqlite3.Connection, company_id: str) -> A.Series:
    return {date.fromisoformat(r["date"]): r["close"] for r in conn.execute(
        "SELECT date, close FROM bars WHERE company_id=? ORDER BY date", (company_id,))}


def companies_with_bars(conn: sqlite3.Connection) -> list[str]:
    return [r["company_id"] for r in conn.execute("SELECT DISTINCT company_id FROM bars ORDER BY company_id")]


def product_basket_members(conn: sqlite3.Connection) -> list[str]:
    """整机篮子 = main 的 exposures 成员 ∪ 站在芯片 / 器件 / 引擎 / 模块阶段且证据已核验的实物公司，且有行情。"""
    have = set(companies_with_bars(conn))
    ids = {r["company_id"] for r in conn.execute("SELECT DISTINCT company_id FROM exposures")}
    ids |= {r["company_id"] for r in conn.execute(
        "SELECT DISTINCT company_id FROM physical_part_companies WHERE company_id IS NOT NULL AND evidence='verified' AND stage IN (?,?,?,?)", CORE_STAGES)}
    return sorted(ids & have)


def part_basket_members(conn: sqlite3.Connection, part_id: str) -> list[str]:
    have = set(companies_with_bars(conn))
    ids = {r["company_id"] for r in conn.execute(
        "SELECT DISTINCT company_id FROM physical_part_companies WHERE part_id=? AND company_id IS NOT NULL AND evidence IN ('verified','consensus')", (part_id,))}
    return sorted(ids & have)


def rebuild_series(conn: sqlite3.Connection) -> dict:
    cur = conn.cursor()
    cur.execute("DELETE FROM series")                     # 样例序列一起清掉；真数据进来后不再混用
    series: dict[str, A.Series] = {}
    for cid in companies_with_bars(conn):
        s = company_close_series(conn, cid)
        if len(s) >= 2:
            series[f"company:{cid}"] = s
    # main 的层篮子
    for r in conn.execute("SELECT id FROM nodes WHERE kind='module' ORDER BY sort"):
        members = [c for c in basket_members(conn, r["id"]) if f"company:{c}" in series]
        if members:
            series[f"basket:{r['id']}"] = A.basket_series([series[f"company:{c}"] for c in members])
    # 实物部件篮子
    for r in conn.execute("SELECT id FROM physical_parts"):
        members = part_basket_members(conn, r["id"])
        if len(members) >= 2:
            series[f"basket:{r['id']}"] = A.basket_series([series[f"company:{c}"] for c in members])
    # 整机
    pid = conn.execute("SELECT id FROM nodes WHERE kind='product'").fetchone()["id"]
    members = product_basket_members(conn)
    if members:
        series[f"basket:{pid}"] = A.basket_series([series[f"company:{c}"] for c in members])
    cur.executemany("INSERT INTO series (instrument, date, value, is_sample) VALUES (?,?,?,0)",
                    [(inst, d.isoformat(), v) for inst, s in series.items() for d, v in s.items()])
    conn.commit()
    return {"instruments": len(series), "points": sum(len(s) for s in series.values()), "product_members": len(members)}


# ------------------------------------------------------------------ reactions
def _load(conn: sqlite3.Connection, inst: str) -> A.Series:
    return {date.fromisoformat(r["date"]): r["value"] for r in conn.execute("SELECT date, value FROM series WHERE instrument=? ORDER BY date", (inst,))}


def reference_for(conn: sqlite3.Connection, ev: dict, cache: dict) -> A.Series | None:
    """公司事件的参照：所在层的其他成员；不在 main 任何层的实物公司用它主要部件的篮子（去掉自己）。"""
    cid = ev.get("company_id")
    if not cid:
        return None
    layer = primary_layer(conn, ev)
    if layer:
        peers = [c for c in basket_members(conn, layer) if c != cid and f"company:{c}" in cache]
        return A.basket_series([cache[f"company:{c}"] for c in peers]) if peers else None
    part = PH.part_for_event(conn, cid, ev.get("category"))
    if part:
        peers = [c for c in part_basket_members(conn, part["part_id"]) if c != cid and f"company:{c}" in cache]
        return A.basket_series([cache[f"company:{c}"] for c in peers]) if peers else None
    return None


def rebuild_reactions(conn: sqlite3.Connection, when: date) -> dict:
    cache = {r["instrument"]: None for r in conn.execute("SELECT DISTINCT instrument FROM series")}
    for inst in list(cache):
        cache[inst] = _load(conn, inst)
    pid = conn.execute("SELECT id FROM nodes WHERE kind='product'").fetchone()["id"]
    product = cache.get(f"basket:{pid}") or {}
    now = datetime.now().isoformat(timespec="seconds")
    cur = conn.cursor()
    cur.execute("DELETE FROM reactions")
    n = 0
    for ev in conn.execute("SELECT * FROM events WHERE status != 'ignored'"):
        ev = dict(ev)
        subj = cache.get(f"company:{ev['company_id']}") if ev.get("company_id") else cache.get(f"basket:{ev.get('node_id')}")
        if not subj:
            continue
        ref = reference_for(conn, ev, cache)
        d0 = date.fromisoformat(ev["date"])
        for h in A.HORIZONS:
            r_abs = A.reaction(subj, None, d0, h, when)
            if r_abs is None:
                continue
            r_b = A.reaction(subj, ref, d0, h, when) if ref else None
            r_p = A.reaction(subj, product, d0, h, when) if product else None
            cur.execute("INSERT OR REPLACE INTO reactions (event_id, horizon, abs_return, excess_basket, excess_product, computed_at) VALUES (?,?,?,?,?,?)",
                        (ev["id"], h, r_abs["abs_return"], r_b["excess"] if r_b else None, r_p["excess"] if r_p else None, now))
            n += 1
        # 事件日 T+1 的量比与换手分位（60 日）
        vr, tp = event_volume_stats(conn, ev.get("company_id"), d0)
        if vr is not None or tp is not None:
            cur.execute("UPDATE events SET volume_ratio=COALESCE(?, volume_ratio), turnover_pct_rank=COALESCE(?, turnover_pct_rank) WHERE id=?", (vr, tp, ev["id"]))
    conn.commit()
    return {"reactions": n}


def event_volume_stats(conn: sqlite3.Connection, company_id: str | None, d0: date) -> tuple[float | None, float | None]:
    if not company_id:
        return None, None
    rows = conn.execute("SELECT date, volume, turnover_pct FROM bars WHERE company_id=? AND date<=? ORDER BY date DESC LIMIT 61",
                        (company_id, (d0 + timedelta(days=10)).isoformat())).fetchall()
    after = [r for r in rows if r["date"] > d0.isoformat()]
    if not after:
        return None, None
    t1 = after[-1]                                     # 事件后的第一个交易日
    before = [r for r in rows if r["date"] <= d0.isoformat()]
    vols = [r["volume"] for r in before[:20] if r["volume"]]
    vr = (t1["volume"] / mean(vols)) if vols and t1["volume"] else None
    tos = [r["turnover_pct"] if r["turnover_pct"] is not None else r["volume"] for r in before[:60]]
    tos = [x for x in tos if x is not None]
    cur = t1["turnover_pct"] if t1["turnover_pct"] is not None else t1["volume"]
    tp = (100.0 * sum(1 for x in tos if x <= cur) / len(tos)) if tos and cur is not None else None
    return (round(vr, 2) if vr else None), (round(tp) if tp is not None else None)


# ------------------------------------------------------------------ valuation
def rebuild_valuation(conn: sqlite3.Connection) -> dict:
    cur = conn.cursor()
    n = 0
    for r in conn.execute("SELECT DISTINCT company_id FROM valuation_daily"):
        hist = [x for x in conn.execute("SELECT date, pe_ttm FROM valuation_daily WHERE company_id=? AND pe_ttm IS NOT NULL ORDER BY date", (r["company_id"],))]
        if not hist:
            continue
        last = hist[-1]
        pes = [x["pe_ttm"] for x in hist if x["pe_ttm"] and x["pe_ttm"] > 0]
        pct = round(100.0 * sum(1 for p in pes if p <= last["pe_ttm"]) / len(pes)) if pes and last["pe_ttm"] else None
        cur.execute("INSERT OR REPLACE INTO valuation (company_id, as_of, pe_ttm, pe_pct_rank_5y, is_sample) VALUES (?,?,?,?,0)",
                    (r["company_id"], last["date"], last["pe_ttm"], pct))
        n += 1
    conn.commit()
    return {"valuation": n}


# ------------------------------------------------------------------ as_of
def latest_bar_date(conn: sqlite3.Connection) -> date | None:
    r = conn.execute("SELECT MAX(date) AS d FROM bars").fetchone()
    return date.fromisoformat(r["d"]) if r and r["d"] else None


def set_as_of(conn: sqlite3.Connection, when: date) -> None:
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('as_of', ?)", (when.isoformat(),))
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('sample', '0')")
    conn.commit()


def recompute_all(conn: sqlite3.Connection) -> dict:
    """bars → series → reactions / 量比 → valuation → as_of。crowding 另在 crowding.py（它要读 series）。"""
    when = latest_bar_date(conn)
    if not when:
        return {"skipped": "no bars"}
    out = rebuild_series(conn)
    out.update(rebuild_reactions(conn, when))
    out.update(rebuild_valuation(conn))
    set_as_of(conn, when)
    out["as_of"] = when.isoformat()
    return out
