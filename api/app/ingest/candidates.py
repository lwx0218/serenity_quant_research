"""候选 → 事件。确认时可以改日期 / 公司 / 类别 / 标题，并带上判定（部件 / 一句话 thesis / 把握 confidence）；驳回只记状态。
确认后的事件 is_sample=0、status=reviewed，来源随事件走（source_url 就是原文）。
AI 批量交回走 judge()（POST /api/candidates/judge）。"""
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
        "part": PH.part_for_event(conn, r.get("company_id"), r.get("category"), r.get("part_id")),
        "also_reported_by": json.loads(r.get("also_reported_by") or "[]"),
        "relevance": r.get("relevance", 1), "status": r["status"], "event_id": r.get("event_id"), "decided_at": r.get("decided_at"), "decided_note": r.get("decided_note"),
        "decided_by": r.get("decided_by"), "thesis": r.get("thesis"), "confidence": r.get("confidence"), "origin": r.get("origin") or "live",
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


def _event_id(r: dict, company_id: str, category: str, d0: date) -> str:
    return f"evt.{d0.isoformat()}.{company_id}.{category}.{r['id'][-6:]}"


def _write_event(conn: sqlite3.Connection, r: dict, company_id: str, category: str, d0: date,
                 title: str | None = None, summary: str | None = None) -> str:
    """r 是候选行(判定字段 part_id / thesis / confidence / decided_by 已经写在上面),事件照抄。"""
    eid = _event_id(r, company_id, category, d0)
    conn.execute(
        """INSERT OR REPLACE INTO events (id, date, company_id, node_id, chain_node_id, source_kind, source_title, source_url, category, title, summary,
                                          volume_ratio, turnover_pct_rank, status, is_sample, thesis, confidence, decided_by, part_id)
           VALUES (?,?,?,NULL,NULL,?,?,?,?,?,?,NULL,NULL,'reviewed',0,?,?,?,?)""",
        (eid, d0.isoformat(), company_id, SOURCE_KIND.get(r["source_type"], "news"), r["source"], r["url"], category,
         title or r["title"], summary if summary is not None else r.get("summary"),
         r.get("thesis"), r.get("confidence"), r.get("decided_by"), r.get("part_id")))
    for layer in company_layers(conn, company_id):
        conn.execute("INSERT OR IGNORE INTO event_layers (event_id, node_id) VALUES (?, ?)", (eid, layer))
    return eid


def _check_part(conn: sqlite3.Connection, part_id: str | None) -> None:
    if part_id and not conn.execute("SELECT 1 FROM physical_parts WHERE id=?", (part_id,)).fetchone():
        raise LookupError(f"part {part_id!r} not found")


def _check_confidence(confidence) -> None:
    if confidence is not None and (isinstance(confidence, bool) or not isinstance(confidence, int) or not 1 <= confidence <= 5):
        raise ValueError("confidence 是 1–5 的整数")


def confirm(conn: sqlite3.Connection, cand_id: str, *, company_id: str | None = None, category: str | None = None,
            event_date: str | None = None, title: str | None = None, summary: str | None = None, note: str | None = None,
            by: str = "ai", recompute: bool = True, part_id: str | None = None, thesis: str | None = None,
            confidence: int | None = None) -> dict:
    """候选 → 事件。by:rule(自动入账规则)/ ai(服务器上的 AI 判完交回)/ human。
    part_id / thesis / confidence 是判定:归到哪个部件(以它为准)、这件事对这个部件意味着什么、把握 1–5。
    recompute=False 时不重算反应(批量入账最后统一算一次)。"""
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
    _check_part(conn, part_id)
    _check_confidence(confidence)
    # 事件日 = 可知日；非交易日顺延到下一交易日
    d0 = date.fromisoformat(d)
    if not A.is_trading_day(d0):
        d0 = A.next_trading_day(d0)
    now = datetime.now().isoformat(timespec="seconds")
    r.update({"part_id": part_id or r.get("part_id"), "thesis": thesis if thesis is not None else r.get("thesis"),
              "confidence": confidence if confidence is not None else r.get("confidence"), "decided_by": by})
    eid = _write_event(conn, r, company_id, category, d0, title, summary)
    conn.execute("""UPDATE candidates SET status='confirmed', event_id=?, decided_at=?, decided_note=?, decided_by=?, company_id=?, category=?, date=?,
                                          part_id=?, thesis=?, confidence=? WHERE id=?""",
                 (eid, now, note, by, company_id, category, d0.isoformat(), r["part_id"], r["thesis"], r["confidence"], r["id"]))
    conn.execute("INSERT INTO verifications (kind, event_id, exposure_id, note, created_at) VALUES ('accept', ?, NULL, ?, ?)", (eid, note or "candidate confirmed", now))
    _close_triage(conn, r["id"])
    conn.commit()
    when = latest_bar_date(conn) if recompute else None
    if when:
        rebuild_reactions(conn, when)
    return {"ok": True, "event_id": eid}


def reject(conn: sqlite3.Connection, cand_id: str, note: str | None = None, by: str = "ai", commit: bool = True) -> dict:
    """不算。by:rule(例行公告)/ ai / human。已入账的先重开(事件删掉)再记不算。"""
    r = _row(conn, cand_id)
    if r["status"] == "confirmed" and r.get("event_id"):
        _drop_event(conn, r["event_id"])
    conn.execute("UPDATE candidates SET status='rejected', event_id=NULL, decided_at=?, decided_note=?, decided_by=? WHERE id=?",
                 (datetime.now().isoformat(timespec="seconds"), note, by, cand_id))
    _close_triage(conn, cand_id)
    if commit:
        conn.commit()
    return {"ok": True}


def reopen(conn: sqlite3.Connection, cand_id: str) -> dict:
    """撤回判定:事件删掉,判定字段清空,交给 AI 的待办也删掉(规则重判时重新开)。"""
    r = _row(conn, cand_id)
    if r["status"] == "confirmed" and r.get("event_id"):
        _drop_event(conn, r["event_id"])
    conn.execute("""UPDATE candidates SET status='pending', event_id=NULL, decided_at=NULL, decided_note=NULL, decided_by=NULL,
                                          part_id=NULL, thesis=NULL, confidence=NULL WHERE id=?""", (cand_id,))
    conn.execute("DELETE FROM ingest_todo WHERE kind='candidate_triage' AND company_id=?", (cand_id,))
    conn.commit()
    return {"ok": True}


def _drop_event(conn: sqlite3.Connection, event_id: str) -> None:
    conn.execute("DELETE FROM reactions WHERE event_id=?", (event_id,))
    conn.execute("DELETE FROM verifications WHERE event_id=?", (event_id,))
    conn.execute("DELETE FROM event_layers WHERE event_id=?", (event_id,))
    conn.execute("DELETE FROM events WHERE id=? AND is_sample=0", (event_id,))


def _close_triage(conn: sqlite3.Connection, cand_id: str) -> None:
    """判过了(无论谁判的),交给 AI 的那条待办就关掉。candidate_triage 的待办 company_id 列放的是候选 id。"""
    conn.execute("UPDATE ingest_todo SET status='done', done_at=? WHERE kind='candidate_triage' AND company_id=? AND status='open'",
                 (datetime.now().isoformat(timespec="seconds"), cand_id))


# ------------------------------------------------------------------ AI 批量交回
EVENT_CATEGORIES = ("capex", "order", "qualification", "supply", "price", "roadmap")     # 卡口事件的六类
JUDGE_MAX = 200


def _judge_one(conn: sqlite3.Connection, it: dict, by: str) -> dict:
    """先把一条交回校验完,再动库:校验失败的候选保持原样。"""
    cid = it.get("id")
    if not cid:
        raise ValueError("缺 id")
    if not isinstance(it.get("is_chokepoint"), bool):
        raise ValueError("缺 is_chokepoint(true / false)")
    r = _row(conn, cid)
    if r.get("decided_by") == "human":
        raise ValueError("人判过(不算 / 撤回不算),不改")
    reason = it.get("reason")
    if not it["is_chokepoint"]:
        reject(conn, cid, note=reason, by=by, commit=False)
        return {"id": cid, "ok": True, "status": "rejected"}
    thesis, confidence = it.get("thesis"), it.get("confidence")
    if not (isinstance(thesis, str) and thesis.strip()):
        raise ValueError("算卡口事件要给 thesis(一句话:这件事对这个部件意味着什么)")
    if confidence is None:
        raise ValueError("算卡口事件要给 confidence(1–5)")
    _check_confidence(confidence)
    category = it.get("category") or r.get("category")
    if category not in EVENT_CATEGORIES:
        raise ValueError(f"category 要是六类之一:{' / '.join(EVENT_CATEGORIES)}")
    d = it.get("date") or r.get("date")
    try:
        date.fromisoformat(d or "")
    except ValueError:
        raise ValueError("date 要是 YYYY-MM-DD") from None
    ids = {x.get("companyId") for x in json.loads(r.get("companies") or "[]") if x.get("companyId")} | ({r["company_id"]} if r.get("company_id") else set())
    company_id = it.get("company_id") or (next(iter(ids)) if len(ids) == 1 else None)
    if not company_id:
        raise ValueError(f"候选命中 {len(ids)} 家公司,要给 company_id" if ids else "候选没命中公司,要给 company_id")
    if not conn.execute("SELECT 1 FROM companies WHERE id=?", (company_id,)).fetchone():
        raise LookupError(f"company {company_id!r} not found")
    part_id = it.get("part_id") or r.get("part_id")
    _check_part(conn, part_id)
    if r["status"] != "pending":
        reopen(conn, cid)                                   # 规则判过的,以 AI 为准
    out = confirm(conn, cid, company_id=company_id, category=category, event_date=d, note=reason, by=by, recompute=False,
                  part_id=part_id, thesis=thesis.strip(), confidence=confidence)
    return {"id": cid, "ok": True, "status": "confirmed", "event_id": out["event_id"]}


def judge(conn: sqlite3.Connection, items: list[dict], by: str = "ai") -> dict:
    """AI 批量交回(POST /api/candidates/judge)。is_chokepoint=true → 入账(带 part_id / thesis / confidence),
    false → 不算。每条各自成败,返回每条的结果或错误;人判过的不改。全部处理完统一重算一次反应。"""
    if len(items) > JUDGE_MAX:
        raise ValueError(f"一批最多 {JUDGE_MAX} 条")
    results = []
    for it in items:
        it = it if isinstance(it, dict) else {}
        try:
            results.append(_judge_one(conn, it, by))
        except (ValueError, LookupError) as e:
            results.append({"id": it.get("id"), "ok": False, "error": str(e)})
    conn.commit()
    out = {"ok": all(x["ok"] for x in results), "confirmed": sum(1 for x in results if x.get("status") == "confirmed"),
           "rejected": sum(1 for x in results if x.get("status") == "rejected"), "errors": sum(1 for x in results if not x["ok"]),
           "results": results}
    when = latest_bar_date(conn) if out["confirmed"] else None
    if when:
        out.update(rebuild_reactions(conn, when))
    return out


# ------------------------------------------------------------------ 人工只剩「不算」
def dismiss_event(conn: sqlite3.Connection, event_id: str, note: str | None = None) -> dict:
    """人对已入账的事件说「不算」:事件不再计入(status=ignored),它的候选记为人判的不算。可撤回。"""
    if not conn.execute("SELECT 1 FROM events WHERE id=?", (event_id,)).fetchone():
        raise LookupError(f"event {event_id!r} not found")
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute("UPDATE events SET status='ignored' WHERE id=?", (event_id,))
    conn.execute("UPDATE candidates SET status='rejected', decided_at=?, decided_note=?, decided_by='human' WHERE event_id=?",
                 (now, note or "人工:不算", event_id))
    conn.commit()
    return {"ok": True, "event_id": event_id, "status": "ignored"}


def restore_event(conn: sqlite3.Connection, event_id: str) -> dict:
    """撤回「不算」。"""
    if not conn.execute("SELECT 1 FROM events WHERE id=?", (event_id,)).fetchone():
        raise LookupError(f"event {event_id!r} not found")
    conn.execute("UPDATE events SET status='reviewed' WHERE id=?", (event_id,))
    conn.execute("UPDATE candidates SET status='confirmed', decided_at=?, decided_note='人工:撤回不算', decided_by='human' WHERE event_id=?",
                 (datetime.now().isoformat(timespec="seconds"), event_id))
    conn.commit()
    return {"ok": True, "event_id": event_id, "status": "reviewed"}


# ------------------------------------------------------------------ 重建之后
def replay(conn: sqlite3.Connection) -> dict:
    """seed --rebuild 只倒回候选,不倒回事件:按已入账的候选把事件重新写出来(被人判「不算」的候选是 rejected,不会回来)。"""
    n = 0
    for r in [dict(x) for x in conn.execute("SELECT * FROM candidates WHERE status='confirmed' AND company_id IS NOT NULL AND category IS NOT NULL AND date IS NOT NULL")]:
        if not conn.execute("SELECT 1 FROM companies WHERE id=?", (r["company_id"],)).fetchone():
            continue
        eid = _write_event(conn, r, r["company_id"], r["category"], date.fromisoformat(r["date"]))
        if eid != r.get("event_id"):
            conn.execute("UPDATE candidates SET event_id=? WHERE id=?", (eid, r["id"]))
        conn.execute("INSERT INTO verifications (kind, event_id, exposure_id, note, created_at) SELECT 'accept', ?, NULL, 'replayed', ? "
                     "WHERE NOT EXISTS (SELECT 1 FROM verifications WHERE event_id=?)", (eid, datetime.now().isoformat(timespec="seconds"), eid))
        n += 1
    conn.commit()
    return {"events_replayed": n}
