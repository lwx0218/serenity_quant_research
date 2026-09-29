"""AI（或人）从网页端取来的数据交回来：POST /api/ingest/upload {kind, company_id, rows}。
kind: bars | margin | holders | valuation | candidates。写完把对应的 ingest_todo 关掉；bars 之后要跑 recompute 才会体现。
candidates 的每行可带 origin（live | backfill，媒体回填用 backfill）与 tier（行业媒体 1）；进池后立刻按入账规则分流。"""
from __future__ import annotations

import sqlite3
from datetime import datetime

from . import accounting, news
from .quotes import upsert_bars
from .runner import close_todo


def _num(x):
    try:
        return float(x) if x is not None and x != "" else None
    except (TypeError, ValueError):
        return None


def upload(conn: sqlite3.Connection, kind: str, company_id: str | None, rows: list[dict], source: str = "upload") -> dict:
    if kind in ("bars", "margin", "holders", "valuation"):
        if not company_id or not conn.execute("SELECT 1 FROM companies WHERE id=?", (company_id,)).fetchone():
            raise LookupError(f"company {company_id!r} not found")
    n = 0
    if kind == "bars":
        clean = [{"date": r["date"][:10], "open": _num(r.get("open")), "high": _num(r.get("high")), "low": _num(r.get("low")),
                  "close": _num(r.get("close")), "volume": _num(r.get("volume")), "amount": _num(r.get("amount")),
                  "turnover_pct": _num(r.get("turnover_pct")), "source": source} for r in rows if r.get("date") and _num(r.get("close"))]
        n = upsert_bars(conn, company_id, clean)
    elif kind == "margin":
        data = [(company_id, r["date"][:10], _num(r.get("rz_balance")), _num(r.get("rq_balance")), _num(r.get("rz_to_float_pct")), source) for r in rows if r.get("date")]
        conn.executemany("INSERT OR REPLACE INTO margin (company_id, date, rz_balance, rq_balance, rz_to_float_pct, source) VALUES (?,?,?,?,?,?)", data)
        n = len(data)
    elif kind == "holders":
        data = [(company_id, r["end_date"][:10], _num(r.get("holder_num")), _num(r.get("change_pct")), _num(r.get("avg_cap")), source) for r in rows if r.get("end_date")]
        conn.executemany("INSERT OR REPLACE INTO holders (company_id, end_date, holder_num, change_pct, avg_cap, source) VALUES (?,?,?,?,?,?)", data)
        n = len(data)
    elif kind == "valuation":
        data = [(company_id, r["date"][:10], _num(r.get("pe_ttm")), _num(r.get("pb")), _num(r.get("market_cap")), source) for r in rows if r.get("date")]
        conn.executemany("INSERT OR REPLACE INTO valuation_daily (company_id, date, pe_ttm, pb, market_cap, source) VALUES (?,?,?,?,?,?)", data)
        n = len(data)
    elif kind == "candidates":
        items = []
        spec = news.load_spec()
        companies, parts = news.build_vocab(conn)
        for r in rows:
            if not r.get("url") or not r.get("title"):
                continue
            tier = int(r.get("tier", 2))
            origin = r.get("origin") or "live"
            if origin not in ("live", "backfill"):
                raise ValueError(f"origin {origin!r}: live | backfill")
            text = f"{r['title']} {r.get('summary') or ''}"
            cs, ps = news.match_entities(text, companies, parts)          # 没给公司 / 部件 / 类别的,和抓取一样现打
            items.append({"id": news.cand_id(r["url"]), "date": news.parse_date(r.get("date") or ""), "title": r["title"], "url": r["url"],
                          "summary": (r.get("summary") or "")[:600], "source": r.get("source") or "AI 网页端", "source_type": "upload",
                          "tier": tier, "weight": 0.5, "evidence": news.TIER_EVIDENCE.get(tier, "candidate"),
                          "category": r.get("category") or news.categorize(text, spec["categories"]),
                          "companies": ([{"companyId": r["company_id"], "name": r.get("company_name") or r["company_id"]}] if r.get("company_id")
                                        else [{"companyId": c["companyId"], "name": c["name"]} for c in cs]),
                          "part_ids": r.get("part_ids") or [p["partId"] for p in ps if p["partId"]], "also_reported_by": [], "origin": origin})
        n = news.store(conn, items)["new"]
        acc = accounting.account(conn)                                   # 进池就走同一套规则:大多数进交给 AI 的待办
    else:
        raise ValueError(f"unknown kind {kind!r}")
    if kind in ("bars", "margin", "holders", "valuation"):
        close_todo(conn, "bars" if kind == "bars" else "margin" if kind in ("margin", "holders") else "valuation", company_id)
    conn.commit()
    out = {"ok": True, "kind": kind, "company_id": company_id, "rows": n, "at": datetime.now().isoformat(timespec="seconds"),
           "next": "POST /api/ingest/run/recompute 之后页面才会读到" if kind != "candidates"
                   else "候选已按入账规则分流;交给 AI 的看 GET /api/ingest/todo?status=open(kind=candidate_triage),判完 POST /api/candidates/judge"}
    if kind == "candidates":
        out["accounting"] = acc
    return out
