"""日线行情。A 股走东财 K 线（akshare.stock_zh_a_hist 底下就是这个接口），海外走 Yahoo chart，
再退到 stooq；三条路都不通就记进 ingest_todo。"""
from __future__ import annotations

import csv
import io
import sqlite3
import time
from datetime import date, datetime, timedelta, timezone

from . import http
from .progress import log as progress_log
from .symbols import em_secid, stooq_symbol, yahoo_symbol

EM_KLINE = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
STOOQ_CSV = "https://stooq.com/q/d/l/"
HISTORY_DAYS = 800          # 首次拉两年多，够算 250 日分位
OVERLAP_DAYS = 10           # 增量时往回多拉几天，覆盖复权 / 补数
EM_CHUNK_DAYS = 120         # 东财一次只要 4 个月，长窗口在服务器上会断连
EM_PAUSE = 1.5              # 段间歇（秒）


def _f(x) -> float | None:
    try:
        v = float(x)
        return v if v == v else None       # NaN
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ fetchers
def _em_chunk(secid: str, beg: date, end: date) -> tuple[list[dict], bool]:
    d = http.get_json(EM_KLINE, {
        "secid": secid, "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": 101, "fqt": 1, "beg": beg.strftime("%Y%m%d"), "end": end.strftime("%Y%m%d"), "lmt": 10000,
    }, headers={"Referer": "https://quote.eastmoney.com/"}, timeout=12, retries=1)
    data = (d or {}).get("data") or {}
    rows = []
    for line in data.get("klines") or []:
        p = line.split(",")
        if len(p) < 11:
            continue
        # 日期,开,收,高,低,成交量(手),成交额,振幅,涨跌幅,涨跌额,换手率
        rows.append({"date": p[0], "open": _f(p[1]), "close": _f(p[2]), "high": _f(p[3]), "low": _f(p[4]),
                     "volume": (_f(p[5]) or 0) * 100, "amount": _f(p[6]), "turnover_pct": _f(p[10]), "source": "eastmoney"})
    return rows, bool(data)


def fetch_eastmoney(secid: str, since: date, chunk_days: int = EM_CHUNK_DAYS) -> list[dict]:
    """长窗口分段拉（服务器上长窗口经常在响应前断连，短窗口能过），段间歇一下。
    某一段失败就抛，让上层退到下一条路。本来源的分段尚未入库，会丢弃：
    不能简单把部分复权序列写入 bars，推进 MAX(date) 后可能永久跳过历史缺口。"""
    rows: list[dict] = []
    beg = since
    today = date.today()
    while beg <= today:
        end = min(beg + timedelta(days=chunk_days), today)
        started = time.monotonic()
        progress_log(f"  eastmoney 请求 {secid} {beg}~{end}")
        part, ok = _em_chunk(secid, beg, end)
        progress_log(f"  eastmoney 返回 {secid} {beg}~{end} rows={len(part)} {time.monotonic() - started:.1f}s（本公司尚未提交）")
        if not ok and not rows:
            raise http.FetchError(f"eastmoney kline empty for {secid} ({beg}~{end})")
        rows.extend(part)
        beg = end + timedelta(days=1)
        if beg <= today:
            time.sleep(EM_PAUSE)
    return rows


def fetch_yahoo(sym: str, since: date) -> list[dict]:
    p1 = int(datetime(since.year, since.month, since.day, tzinfo=timezone.utc).timestamp())
    p2 = int(datetime.now(timezone.utc).timestamp()) + 86400
    d = http.get_json(YAHOO_CHART.format(sym=sym), {"period1": p1, "period2": p2, "interval": "1d", "events": "div,splits"})
    res = ((d or {}).get("chart") or {}).get("result") or []
    if not res:
        err = ((d or {}).get("chart") or {}).get("error")
        raise http.FetchError(f"yahoo {sym}: {err or 'no result'}")
    r = res[0]
    ts = r.get("timestamp") or []
    q = ((r.get("indicators") or {}).get("quote") or [{}])[0]
    adj = ((r.get("indicators") or {}).get("adjclose") or [{}])[0].get("adjclose") or []
    off = (r.get("meta") or {}).get("gmtoffset") or 0
    rows = []
    for i, t in enumerate(ts):
        close = _f(adj[i]) if i < len(adj) and adj[i] is not None else _f((q.get("close") or [None] * len(ts))[i])
        if close is None:
            continue
        dd = (datetime.fromtimestamp(t, timezone.utc) + timedelta(seconds=off)).date().isoformat()
        rows.append({"date": dd, "open": _f((q.get("open") or [None] * len(ts))[i]), "close": close,
                     "high": _f((q.get("high") or [None] * len(ts))[i]), "low": _f((q.get("low") or [None] * len(ts))[i]),
                     "volume": _f((q.get("volume") or [None] * len(ts))[i]), "amount": None, "turnover_pct": None, "source": "yahoo"})
    return rows


def fetch_stooq(sym: str, since: date) -> list[dict]:
    raw = http.get(STOOQ_CSV, {"s": sym, "i": "d", "d1": since.strftime("%Y%m%d"), "d2": date.today().strftime("%Y%m%d")})
    text = raw.decode("utf-8", "ignore")
    if "Date" not in text[:200]:
        raise http.FetchError(f"stooq {sym}: {text[:80]!r}")
    rows = []
    for rec in csv.DictReader(io.StringIO(text)):
        c = _f(rec.get("Close"))
        if c is None:
            continue
        rows.append({"date": rec["Date"], "open": _f(rec.get("Open")), "close": c, "high": _f(rec.get("High")), "low": _f(rec.get("Low")),
                     "volume": _f(rec.get("Volume")), "amount": None, "turnover_pct": None, "source": "stooq"})
    return rows


def fetch_bars(company: dict, since: date) -> tuple[list[dict], list[str]]:
    """按优先级试每条路；返回 (rows, 失败原因列表)。"""
    errors: list[str] = []
    routes = []
    if em_secid(company):
        routes.append(("eastmoney", lambda: fetch_eastmoney(em_secid(company), since)))
    if yahoo_symbol(company):
        routes.append(("yahoo", lambda: fetch_yahoo(yahoo_symbol(company), since)))
    if stooq_symbol(company):
        routes.append(("stooq", lambda: fetch_stooq(stooq_symbol(company), since)))
    for name, fn in routes:
        try:
            rows = fn()
            if rows:
                return rows, errors
            errors.append(f"{name}: 0 rows")
        except Exception as e:  # noqa: BLE001 — 下一条路
            errors.append(f"{name}: {str(e)[:200]}")
    return [], errors or ["no route: 没有可用的行情代码（未上市或交易所未映射）"]


# ------------------------------------------------------------------ storage
def last_bar_date(conn: sqlite3.Connection, company_id: str) -> date | None:
    r = conn.execute("SELECT MAX(date) AS d FROM bars WHERE company_id=?", (company_id,)).fetchone()
    return date.fromisoformat(r["d"]) if r and r["d"] else None


def upsert_bars(conn: sqlite3.Connection, company_id: str, rows: list[dict]) -> int:
    conn.executemany(
        """INSERT INTO bars (company_id, date, open, high, low, close, volume, amount, turnover_pct, source)
           VALUES (?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(company_id, date) DO UPDATE SET open=excluded.open, high=excluded.high, low=excluded.low, close=excluded.close,
             volume=excluded.volume, amount=excluded.amount, turnover_pct=COALESCE(excluded.turnover_pct, bars.turnover_pct), source=excluded.source""",
        [(company_id, r["date"], r["open"], r["high"], r["low"], r["close"], r["volume"], r["amount"], r["turnover_pct"], r["source"]) for r in rows])
    return len(rows)


def ingest_company(conn: sqlite3.Connection, company: dict, full: bool = False) -> dict:
    last = None if full else last_bar_date(conn, company["id"])
    since = (last - timedelta(days=OVERLAP_DAYS)) if last else (date.today() - timedelta(days=HISTORY_DAYS))
    rows, errors = fetch_bars(company, since)
    n = upsert_bars(conn, company["id"], rows) if rows else 0
    return {"company_id": company["id"], "rows": n, "source": rows[0]["source"] if rows else None,
            "last": max(r["date"] for r in rows) if rows else (last.isoformat() if last else None), "errors": errors}
