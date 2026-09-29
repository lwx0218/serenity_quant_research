"""作业：quotes / crowding / valuation / news / recompute，以及打包的 daily。
每次运行记 ingest_runs；抓不到的公司记 ingest_todo，交给 AI 去网页端取。

    python -m app.ingest daily            # 收盘后：行情 → 拥挤度输入 → 估值 → 重算
    python -m app.ingest news             # 每几小时：候选池
    python -m app.ingest quotes --full    # 首次或修数：全量拉两年
    python -m app.ingest probe            # 每条路各试一家，看服务器出网情况
"""
from __future__ import annotations

import json
import sqlite3
import traceback
from datetime import date, datetime, timedelta

from .. import config
from ..db import connect
from . import crowding as CR
from . import accounting, eastmoney, news, quotes, recompute
from .schema import ensure_schema
from .symbols import is_a_share, quotable

JOBS = ("quotes", "crowding", "valuation", "news", "triage", "recompute", "daily", "probe")


def companies(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT id, name, short_name, ticker, exchange FROM companies ORDER BY id")]


# ------------------------------------------------------------------ todo
def add_todo(conn: sqlite3.Connection, kind: str, company_id: str | None, hint: str, reason: str) -> None:
    conn.execute(
        """INSERT INTO ingest_todo (kind, company_id, hint, reason, status, created_at) VALUES (?,?,?,?,'open',?)
           ON CONFLICT(kind, company_id) DO UPDATE SET reason=excluded.reason, hint=excluded.hint,
             status=CASE WHEN ingest_todo.status='done' THEN 'done' ELSE 'open' END""",
        (kind, company_id, hint, reason, datetime.now().isoformat(timespec="seconds")))


def close_todo(conn: sqlite3.Connection, kind: str, company_id: str | None) -> None:
    conn.execute("UPDATE ingest_todo SET status='done', done_at=? WHERE kind=? AND company_id IS ? AND status='open'",
                 (datetime.now().isoformat(timespec="seconds"), kind, company_id))


def _hint_bars(c: dict) -> str:
    where = ("东方财富行情页（quote.eastmoney.com）或新浪财经的历史行情" if is_a_share(c)
             else f"Yahoo Finance / Google Finance 的 {c.get('ticker')} 历史行情页")
    return (f"到{where}取 {c.get('short_name') or c['name']}（{c.get('ticker')}，{c.get('exchange')}）最近 500 个交易日的日线：日期、开、高、低、收（前复权）、成交量、成交额、换手率，"
            f"POST /api/ingest/upload {{kind:'bars', company_id:'{c['id']}', rows:[{{date,open,high,low,close,volume,amount,turnover_pct}}]}}")


# ------------------------------------------------------------------ jobs
def job_quotes(conn: sqlite3.Connection, full: bool = False, log=print) -> dict:
    ok = fail = skip = 0
    rows = 0
    for c in companies(conn):
        if not quotable(c):
            skip += 1
            continue
        r = quotes.ingest_company(conn, c, full=full)
        conn.commit()
        if r["rows"]:
            ok += 1; rows += r["rows"]
            close_todo(conn, "bars", c["id"])
            if r["errors"]:
                log(f"  {c['id']}: {r['source']} {r['rows']} 行（前面失败：{r['errors'][0][:80]}）")
        else:
            fail += 1
            add_todo(conn, "bars", c["id"], _hint_bars(c), " | ".join(r["errors"])[:400])
            log(f"  ERR {c['id']}: {r['errors'][0][:120]}")
    conn.commit()
    return {"companies_ok": ok, "companies_failed": fail, "unquotable": skip, "rows": rows}


def job_crowding_inputs(conn: sqlite3.Connection, log=print) -> dict:
    ok = fail = 0
    for c in companies(conn):
        if not is_a_share(c):
            continue
        r = CR.ingest_margin_holders(conn, c)
        if r["errors"]:
            fail += 1
            add_todo(conn, "margin", c["id"],
                     f"到东方财富数据中心「融资融券 · 个股」页取 {c.get('short_name')}（{c['ticker']}）最近 60 个交易日的融资余额、融券余额、融资余额占流通市值比，"
                     f"以及「股东户数」页最近 8 期的户数与较上期变化，POST /api/ingest/upload {{kind:'margin'|'holders', company_id:'{c['id']}', rows:[…]}}",
                     " | ".join(r["errors"])[:400])
            log(f"  ERR {c['id']}: {r['errors'][0][:120]}")
        else:
            ok += 1
            close_todo(conn, "margin", c["id"])
    conn.commit()
    return {"companies_ok": ok, "companies_failed": fail}


def job_valuation(conn: sqlite3.Connection, log=print) -> dict:
    ok = fail = 0
    for c in companies(conn):
        if not is_a_share(c):
            continue
        try:
            last = conn.execute("SELECT MAX(date) AS d FROM valuation_daily WHERE company_id=?", (c["id"],)).fetchone()["d"]
            since = (date.fromisoformat(last) - timedelta(days=10)) if last else None
            rows = eastmoney.fetch_valuation(c["ticker"], since)
            conn.executemany("INSERT OR REPLACE INTO valuation_daily (company_id, date, pe_ttm, pb, market_cap, source) VALUES (?,?,?,?,?,?)",
                             [(c["id"], r["date"], r["pe_ttm"], r["pb"], r["market_cap"], r["source"]) for r in rows])
            conn.commit()
            ok += 1
            close_todo(conn, "valuation", c["id"])
        except Exception as e:  # noqa: BLE001
            fail += 1
            add_todo(conn, "valuation", c["id"],
                     f"到东方财富「估值分析」页或理杏仁取 {c.get('short_name')}（{c['ticker']}）近 5 年 PE(TTM) 日序列，POST /api/ingest/upload {{kind:'valuation', company_id:'{c['id']}', rows:[{{date, pe_ttm, pb, market_cap}}]}}",
                     str(e)[:400])
            log(f"  ERR {c['id']}: {str(e)[:120]}")
    conn.commit()
    return {"companies_ok": ok, "companies_failed": fail}


def job_recompute(conn: sqlite3.Connection, log=print) -> dict:
    out = recompute.recompute_all(conn)
    out.update(CR.rebuild_crowding(conn))
    return out


def job_news(conn: sqlite3.Connection, only: str | None = None, log=print) -> dict:
    out = news.run_news(conn, only=only, log=log)
    out["triage"] = news.retriage(conn)        # 规则可能改过：给整个池子重算一遍「值得看 / 例行」
    out["accounting"] = accounting.account(conn)   # 新候选按规则入账 / 不算 / 交给 AI
    return out


def job_triage(conn: sqlite3.Connection, log=print) -> dict:
    """对库里所有还没人判过的候选跑一遍入账规则（上线时对现有候选跑一次；之后 news 作业每次都跑）。"""
    out = {"relevance": news.retriage(conn), **accounting.account(conn)}
    out["summary"] = accounting.summary(conn)
    log(f"  入账 {out['auto']} · 例行 {out['routine']} · 交给 AI {out['triage']}")
    return out


def job_probe(conn: sqlite3.Connection, log=print) -> dict:
    """每条路各试一家，看这台机器出不出得去。"""
    out = {}
    tests = [("eastmoney kline 300308", lambda: len(quotes.fetch_eastmoney("0.300308", date.today() - timedelta(days=30)))),
             ("eastmoney margin 300308", lambda: len(eastmoney.fetch_margin("300308", date.today() - timedelta(days=30)))),
             ("eastmoney holders 300308", lambda: len(eastmoney.fetch_holders("300308"))),
             ("eastmoney valuation 300308", lambda: len(eastmoney.fetch_valuation("300308", date.today() - timedelta(days=30)))),
             ("yahoo NVDA", lambda: len(quotes.fetch_yahoo("NVDA", date.today() - timedelta(days=30)))),
             ("yahoo 5802.T", lambda: len(quotes.fetch_yahoo("5802.T", date.today() - timedelta(days=30)))),
             ("stooq nvda.us", lambda: len(quotes.fetch_stooq("nvda.us", date.today() - timedelta(days=30))))]
    for name, fn in tests:
        try:
            n = fn(); out[name] = f"ok {n} rows"; log(f"  ok  {name}: {n} rows")
        except Exception as e:  # noqa: BLE001
            out[name] = f"ERR {str(e)[:160]}"; log(f"  ERR {name}: {str(e)[:160]}")
    out["rss"] = news.probe(log=log)
    return out


def job_daily(conn: sqlite3.Connection, full: bool = False, log=print) -> dict:
    out = {"quotes": job_quotes(conn, full=full, log=log)}
    out["inputs"] = job_crowding_inputs(conn, log=log)
    out["valuation"] = job_valuation(conn, log=log)
    out["recompute"] = job_recompute(conn, log=log)
    return out


# ------------------------------------------------------------------ run with log
def run(job: str, *, db_path=None, full: bool = False, only: str | None = None, log=print) -> dict:
    if job not in JOBS:
        raise ValueError(f"unknown job {job!r}; one of {JOBS}")
    conn = connect(db_path or config.DB_PATH)
    ensure_schema(conn)
    started = datetime.now().isoformat(timespec="seconds")
    cur = conn.execute("INSERT INTO ingest_runs (job, started_at) VALUES (?, ?)", (job, started))
    run_id = cur.lastrowid
    conn.commit()
    try:
        fn = {"quotes": lambda: job_quotes(conn, full=full, log=log), "crowding": lambda: job_crowding_inputs(conn, log=log),
              "valuation": lambda: job_valuation(conn, log=log), "news": lambda: job_news(conn, only=only, log=log),
              "triage": lambda: job_triage(conn, log=log),
              "recompute": lambda: job_recompute(conn, log=log), "daily": lambda: job_daily(conn, full=full, log=log),
              "probe": lambda: job_probe(conn, log=log)}[job]
        summary = fn()
        conn.execute("UPDATE ingest_runs SET finished_at=?, ok=1, summary=? WHERE id=?",
                     (datetime.now().isoformat(timespec="seconds"), json.dumps(summary, ensure_ascii=False), run_id))
        conn.commit()
        return {"run_id": run_id, "job": job, "ok": True, "summary": summary}
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-1500:]}"
        conn.execute("UPDATE ingest_runs SET finished_at=?, ok=0, error=? WHERE id=?", (datetime.now().isoformat(timespec="seconds"), err, run_id))
        conn.commit()
        return {"run_id": run_id, "job": job, "ok": False, "error": err}
    finally:
        conn.close()


# ------------------------------------------------------------------ status
def status(conn: sqlite3.Connection) -> dict:
    ensure_schema(conn)
    q = lambda s, *a: conn.execute(s, a).fetchone()  # noqa: E731
    n_co = q("SELECT COUNT(*) AS n FROM companies")["n"]
    with_bars = q("SELECT COUNT(DISTINCT company_id) AS n FROM bars")["n"]
    quotable_n = sum(1 for c in companies(conn) if quotable(c))
    last_bar = q("SELECT MAX(date) AS d FROM bars")["d"]
    last_news = q("SELECT MAX(fetched_at) AS d FROM candidates")["d"]
    runs = [dict(r) for r in conn.execute("SELECT id, job, started_at, finished_at, ok, summary, error FROM ingest_runs ORDER BY id DESC LIMIT 20")]
    for r in runs:
        r["summary"] = json.loads(r["summary"]) if r.get("summary") else None
        r["error"] = (r["error"] or "")[:300] or None
    events_real = q("SELECT COUNT(*) AS n FROM events WHERE is_sample=0")["n"]
    events_sample = q("SELECT COUNT(*) AS n FROM events WHERE is_sample=1")["n"]
    sample = q("SELECT value FROM settings WHERE key='sample'")
    return {
        "as_of": (q("SELECT value FROM settings WHERE key='as_of'") or {"value": None})["value"],
        "sample": bool(sample and sample["value"] == "1"),
        "companies": n_co, "quotable": quotable_n, "with_bars": with_bars, "last_bar_date": last_bar,
        "with_margin": q("SELECT COUNT(DISTINCT company_id) AS n FROM margin")["n"],
        "with_valuation": q("SELECT COUNT(*) AS n FROM valuation WHERE is_sample=0")["n"],
        "events": {"real": events_real, "sample": events_sample},
        "candidates": {**{r["status"]: r["n"] for r in conn.execute("SELECT status, COUNT(*) AS n FROM candidates GROUP BY status")},
                       "pending_relevant": q("SELECT COUNT(*) AS n FROM candidates WHERE status='pending' AND relevance=1")["n"]},
        "accounting": accounting.summary(conn),
        "last_news_fetch": last_news,
        "todo_open": q("SELECT COUNT(*) AS n FROM ingest_todo WHERE status='open' AND kind != 'candidate_triage'")["n"],   # 补数;候选判定在 accounting.to_ai
        "runs": runs,
    }
