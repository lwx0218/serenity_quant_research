"""候选 → 事件。确认时人可以改日期 / 公司 / 类别 / 标题；驳回只记状态。
确认后的事件 is_sample=0、status=reviewed，来源随事件走（source_url 就是原文）。"""
from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime

from .. import analytics as A
from .. import physical as PH
from ..market import CATEGORY_LABEL, SOURCE_LABEL, company_brief
from ..market_seed import company_layers
from .news import SOURCE_KIND
from .recompute import latest_bar_date, rebuild_reactions


def _row(conn: sqlite3.Connection, cand_id: str) -> dict:
    r = conn.execute("SELECT * FROM candidates WHERE id=?", (cand_id,)).fetchone()
    if not r:
        raise LookupError(f"candidate {cand_id!r} not found")
    return dict(r)


def public(conn: sqlite3.Connection, r: dict) -> dict:
    comps = json.loads(r.get("companies") or "[]")
    company = company_brief(conn, r["company_id"]) if r.get("company_id") else None
    part_ids = json.loads(r.get("part_ids") or "[]")
    parts = [dict(conn.execute("SELECT id, name FROM physical_parts WHERE id=?", (p,)).fetchone() or {"id": p, "name": p}) for p in part_ids]
    return {
        "id": r["id"], "date": r["date"], "title": r["title"], "url": r["url"], "summary": r["summary"],
        "source": r["source"], "source_type": r["source_type"], "source_label": SOURCE_LABEL.get(SOURCE_KIND.get(r["source_type"], "news"), r["source"]),
        "tier": r["tier"], "evidence": r["evidence"], "category": r["category"],
        "category_label": CATEGORY_LABEL.get(r["category"], r["category"]) if r["category"] else None,
        "company": company, "companies": comps, "parts": parts,
        "part": PH.part_for_event(conn, r.get("company_id"), r.get("category")),
        "also_reported_by": json.loads(r.get("also_reported_by") or "[]"),
        "relevance": r.get("relevance", 1), "status": r["status"], "event_id": r.get("event_id"), "decided_at": r.get("decided_at"), "decided_note": r.get("decided_note"),
        "fetched_at": r["fetched_at"],
    }


def list_candidates(conn: sqlite3.Connection, status: str = "pending", limit: int = 100, company: str | None = None,
                    relevant: bool | None = True) -> list[dict]:
    q, args = "SELECT * FROM candidates WHERE 1=1", []
    if status and status != "all":
        q += " AND status=?"; args.append(status)
    if relevant is not None:
        q += " AND relevance=?"; args.append(1 if relevant else 0)
    if company:
        q += " AND company_id=?"; args.append(company)
    q += " ORDER BY COALESCE(date,'') DESC, tier ASC, fetched_at DESC LIMIT ?"; args.append(limit)
    return [public(conn, dict(r)) for r in conn.execute(q, args)]


def counts(conn: sqlite3.Connection) -> dict:
    out = {r["status"]: r["n"] for r in conn.execute("SELECT status, COUNT(*) AS n FROM candidates GROUP BY status")}
    out["pending_relevant"] = conn.execute("SELECT COUNT(*) FROM candidates WHERE status='pending' AND relevance=1").fetchone()[0]
    out["pending_routine"] = conn.execute("SELECT COUNT(*) FROM candidates WHERE status='pending' AND relevance=0").fetchone()[0]
    return out


def confirm(conn: sqlite3.Connection, cand_id: str, *, company_id: str | None = None, category: str | None = None,
            event_date: str | None = None, title: str | None = None, summary: str | None = None, note: str | None = None) -> dict:
    r = _row(conn, cand_id)
    if r["status"] == "confirmed" and r.get("event_id"):
        return {"ok": True, "already": True, "event_id": r["event_id"]}
    company_id = company_id or r.get("company_id")
    category = category or r.get("category")
    d = event_date or r.get("date")
    if not company_id:
        raise ValueError("要先指定这条候选属于哪家公司")
    if not category:
        raise ValueError("要先给这条候选一个类别（扩产 / 订单 / 认证 / 供需 / 涨价 / 技术路线）")
    if not d:
        raise ValueError("这条候选没有日期")
    if not conn.execute("SELECT 1 FROM companies WHERE id=?", (company_id,)).fetchone():
        raise LookupError(f"company {company_id!r} not found")
    # 事件日 = 可知日；非交易日顺延到下一交易日
    d0 = date.fromisoformat(d)
    if not A.is_trading_day(d0):
        d0 = A.next_trading_day(d0)
    eid = f"evt.{d0.isoformat()}.{company_id}.{category}.{r['id'][-6:]}"
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """INSERT OR REPLACE INTO events (id, date, company_id, node_id, chain_node_id, source_kind, source_title, source_url, category, title, summary,
                                          volume_ratio, turnover_pct_rank, status, is_sample)
           VALUES (?,?,?,NULL,NULL,?,?,?,?,?,?,NULL,NULL,'reviewed',0)""",
        (eid, d0.isoformat(), company_id, SOURCE_KIND.get(r["source_type"], "news"), r["source"], r["url"], category,
         title or r["title"], summary if summary is not None else r.get("summary")))
    for layer in company_layers(conn, company_id):
        conn.execute("INSERT OR IGNORE INTO event_layers (event_id, node_id) VALUES (?, ?)", (eid, layer))
    conn.execute("UPDATE candidates SET status='confirmed', event_id=?, decided_at=?, decided_note=?, company_id=?, category=?, date=? WHERE id=?",
                 (eid, now, note, company_id, category, d0.isoformat(), r["id"]))
    conn.execute("INSERT INTO verifications (kind, event_id, exposure_id, note, created_at) VALUES ('accept', ?, NULL, ?, ?)", (eid, note or "candidate confirmed", now))
    conn.commit()
    when = latest_bar_date(conn)
    if when:
        rebuild_reactions(conn, when)
    return {"ok": True, "event_id": eid}


def reject(conn: sqlite3.Connection, cand_id: str, note: str | None = None) -> dict:
    _row(conn, cand_id)
    conn.execute("UPDATE candidates SET status='rejected', decided_at=?, decided_note=? WHERE id=?",
                 (datetime.now().isoformat(timespec="seconds"), note, cand_id))
    conn.commit()
    return {"ok": True}


def reopen(conn: sqlite3.Connection, cand_id: str) -> dict:
    r = _row(conn, cand_id)
    if r["status"] == "confirmed" and r.get("event_id"):
        conn.execute("DELETE FROM reactions WHERE event_id=?", (r["event_id"],))
        conn.execute("DELETE FROM verifications WHERE event_id=?", (r["event_id"],))
        conn.execute("DELETE FROM event_layers WHERE event_id=?", (r["event_id"],))
        conn.execute("DELETE FROM events WHERE id=? AND is_sample=0", (r["event_id"],))
    conn.execute("UPDATE candidates SET status='pending', event_id=NULL, decided_at=NULL, decided_note=NULL WHERE id=?", (cand_id,))
    conn.commit()
    return {"ok": True}
