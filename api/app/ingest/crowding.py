"""拥挤度 / 脆弱性读数（20 日窗口），metrics 字段与样例数据一致，analytics.crowding_directions 直接能读：
ret20_pct_rank · turnover_pct_rank · deviation_sigma · margin_to_float_pct · holders_change_pct ·
turnover_share_pct / turnover_share_mean_pct · attention{margin_change_3d_pct, irm_questions_7d}。

分位都是「现在这个值在过去 250 个交易日同类值里的百分位」；偏离是「公司 20 日收益 − 参照篮子 20 日收益」
相对其一年分布的 σ 数。参照：主要部件篮子 → 整机（部件不成篮子时）。"""
from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta
from statistics import mean, pstdev

from .. import physical as PH
from . import eastmoney
from .progress import log as progress_log
from .symbols import is_a_share

WINDOW = 20
LOOKBACK = 250


def _pct_rank(hist: list[float], cur: float | None) -> float | None:
    hist = [h for h in hist if h is not None]
    if cur is None or len(hist) < WINDOW:
        return None
    return round(100.0 * sum(1 for h in hist if h <= cur) / len(hist))


def _rolling_returns(closes: list[float], w: int = WINDOW) -> list[float]:
    return [closes[i] / closes[i - w] - 1.0 for i in range(w, len(closes)) if closes[i - w]]


def _rolling_means(xs: list[float | None], w: int = WINDOW) -> list[float]:
    out = []
    for i in range(w, len(xs) + 1):
        seg = [x for x in xs[i - w:i] if x is not None]
        if len(seg) >= w // 2:
            out.append(mean(seg))
    return out


def _series(conn: sqlite3.Connection, inst: str, n: int = LOOKBACK + WINDOW + 5) -> dict[str, float]:
    rows = conn.execute("SELECT date, value FROM series WHERE instrument=? ORDER BY date DESC LIMIT ?", (inst, n)).fetchall()
    return {r["date"]: r["value"] for r in reversed(rows)}


def _deviation_sigma(subject: dict[str, float], ref: dict[str, float]) -> float | None:
    days = [d for d in subject if d in ref]
    if len(days) < WINDOW * 2:
        return None
    s = [subject[d] for d in days]
    r = [ref[d] for d in days]
    rel = [(s[i] / s[i - WINDOW] - 1.0) - (r[i] / r[i - WINDOW] - 1.0) for i in range(WINDOW, len(days))]
    rel = rel[-LOOKBACK:]
    if len(rel) < WINDOW:
        return None
    sd = pstdev(rel)
    return round((rel[-1] - mean(rel)) / sd, 2) if sd else None


def reference_instrument(conn: sqlite3.Connection, company_id: str, pid: str) -> str:
    """偏离的参照:公司主要部件的篮子(与反应同一条规则),部件不成篮子时用整机。"""
    part = PH.part_for_event(conn, company_id, None)
    if part and conn.execute("SELECT 1 FROM series WHERE instrument=? LIMIT 1", (f"basket:{part['part_id']}",)).fetchone():
        return f"basket:{part['part_id']}"
    return f"basket:{pid}"


# ------------------------------------------------------------------ inputs (A 股)
def ingest_margin_holders(conn: sqlite3.Connection, company: dict, log=progress_log) -> dict:
    """融资余额 + 股东户数，只对 A 股。失败原因返回给 runner 记 todo。"""
    out = {"margin": 0, "holders": 0, "errors": []}
    if not is_a_share(company):
        return out
    code = company["ticker"]
    log(f"  margin 请求 {company['id']}")
    try:
        rows = eastmoney.fetch_margin(code, date.today() - timedelta(days=400))
    except Exception as e:  # noqa: BLE001
        out["errors"].append(f"margin: {str(e)[:200]}")
    else:
        with conn:
            conn.executemany("INSERT OR REPLACE INTO margin (company_id, date, rz_balance, rq_balance, rz_to_float_pct, source) VALUES (?,?,?,?,?,?)",
                             [(company["id"], r["date"], r["rz_balance"], r["rq_balance"], r["rz_to_float_pct"], r["source"]) for r in rows])
        out["margin"] = len(rows)
        log(f"  margin 已提交 {company['id']} rows={len(rows)}")
    log(f"  holders 请求 {company['id']}")
    try:
        rows = eastmoney.fetch_holders(code)
    except Exception as e:  # noqa: BLE001
        out["errors"].append(f"holders: {str(e)[:200]}")
    else:
        with conn:
            conn.executemany("INSERT OR REPLACE INTO holders (company_id, end_date, holder_num, change_pct, avg_cap, source) VALUES (?,?,?,?,?,?)",
                             [(company["id"], r["end_date"], r["holder_num"], r["change_pct"], r["avg_cap"], r["source"]) for r in rows])
        out["holders"] = len(rows)
        log(f"  holders 已提交 {company['id']} rows={len(rows)}")
    return out


# ------------------------------------------------------------------ readings
def company_metrics(conn: sqlite3.Connection, company_id: str, pid: str, product_amount: dict[str, float]) -> dict | None:
    bars = conn.execute("SELECT date, close, volume, amount, turnover_pct FROM bars WHERE company_id=? ORDER BY date DESC LIMIT ?",
                        (company_id, LOOKBACK + WINDOW + 5)).fetchall()
    bars = list(reversed(bars))
    if len(bars) < WINDOW + 5:
        return None
    closes = [b["close"] for b in bars]
    r20 = _rolling_returns(closes)
    m = {"ret20_pct_rank": _pct_rank(r20[-LOOKBACK:], r20[-1] if r20 else None)}
    # 换手：有换手率用换手率，没有用成交量
    tos = [b["turnover_pct"] if b["turnover_pct"] is not None else b["volume"] for b in bars]
    tm = _rolling_means(tos)
    m["turnover_pct_rank"] = _pct_rank(tm[-LOOKBACK:], tm[-1] if tm else None)
    # 相对参照的偏离
    subj = {b["date"]: b["close"] for b in bars}
    ref = _series(conn, reference_instrument(conn, company_id, pid))
    m["deviation_sigma"] = _deviation_sigma(subj, ref)
    # 成交占比（相对整机成员）
    amts = [(b["date"], b["amount"]) for b in bars[-WINDOW:] if b["amount"] and product_amount.get(b["date"])]
    if amts:
        shares = [100.0 * a / product_amount[d] for d, a in amts]
        m["turnover_share_pct"] = round(shares[-1], 2)
        m["turnover_share_mean_pct"] = round(mean(shares), 2)
    # 融资
    mg = conn.execute("SELECT date, rz_balance, rz_to_float_pct FROM margin WHERE company_id=? ORDER BY date DESC LIMIT 5", (company_id,)).fetchall()
    if mg:
        m["margin_to_float_pct"] = mg[0]["rz_to_float_pct"]
        att = {}
        if len(mg) >= 4 and mg[3]["rz_balance"]:
            att["margin_change_3d_pct"] = round(100.0 * (mg[0]["rz_balance"] / mg[3]["rz_balance"] - 1.0), 2)
        m["attention"] = att
    # 股东户数
    h = conn.execute("SELECT change_pct FROM holders WHERE company_id=? ORDER BY end_date DESC LIMIT 1", (company_id,)).fetchone()
    if h and h["change_pct"] is not None:
        m["holders_change_pct"] = h["change_pct"]
    # 互动易 7 日提问数（候选池里来源类型为 cninfo_irm 的条目）
    n = conn.execute("SELECT COUNT(*) FROM candidates WHERE company_id=? AND source_type='cninfo_irm' AND date>=?",
                     (company_id, (date.today() - timedelta(days=7)).isoformat())).fetchone()[0]
    if n:
        m.setdefault("attention", {})["irm_questions_7d"] = n
    return m


def basket_metrics(conn: sqlite3.Connection, inst: str, pid: str) -> dict | None:
    s = _series(conn, inst)
    if len(s) < WINDOW * 2:
        return None
    closes = list(s.values())
    r20 = _rolling_returns(closes)
    m = {"ret20_pct_rank": _pct_rank(r20[-LOOKBACK:], r20[-1] if r20 else None)}
    if inst != f"basket:{pid}":
        m["deviation_sigma"] = _deviation_sigma(s, _series(conn, f"basket:{pid}"))
    return m


def rebuild_crowding(conn: sqlite3.Connection) -> dict:
    when = conn.execute("SELECT MAX(date) AS d FROM bars").fetchone()["d"]
    if not when:
        return {"skipped": "no bars"}
    pid = conn.execute("SELECT id FROM nodes WHERE kind='product'").fetchone()["id"]
    from .recompute import product_basket_members
    members = product_basket_members(conn)
    product_amount: dict[str, float] = {}
    if members:
        q = f"SELECT date, SUM(amount) AS a FROM bars WHERE company_id IN ({','.join('?' * len(members))}) AND amount IS NOT NULL GROUP BY date"
        product_amount = {r["date"]: r["a"] for r in conn.execute(q, members)}
    cur = conn.cursor()
    cur.execute("DELETE FROM crowding WHERE is_sample=1")
    n = 0
    for r in conn.execute("SELECT DISTINCT company_id FROM bars"):
        m = company_metrics(conn, r["company_id"], pid, product_amount)
        if m:
            cur.execute("INSERT OR REPLACE INTO crowding (instrument, as_of, window_days, metrics, is_sample) VALUES (?,?,?,?,0)",
                        (f"company:{r['company_id']}", when, WINDOW, json.dumps(m, ensure_ascii=False)))
            n += 1
    for r in conn.execute("SELECT DISTINCT instrument FROM series WHERE instrument LIKE 'basket:%'"):
        m = basket_metrics(conn, r["instrument"], pid)
        if m:
            cur.execute("INSERT OR REPLACE INTO crowding (instrument, as_of, window_days, metrics, is_sample) VALUES (?,?,?,?,0)",
                        (r["instrument"], when, WINDOW, json.dumps(m, ensure_ascii=False)))
            n += 1
    conn.commit()
    return {"crowding": n, "as_of": when}
