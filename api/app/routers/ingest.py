"""数据接入的接口：状态、触发作业、AI 交接（todo / upload）、候选事件的确认与驳回。

作业在后台线程跑（BackgroundTasks），触发后立刻返回 run_id；进度看 GET /api/ingest/runs。
定时任务用 cron 调 `python -m app.ingest daily|news`，或 curl 这里的 POST。"""
from __future__ import annotations

import threading
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..deps import Conn
from ..ingest import candidates as C
from ..ingest import runner
from ..ingest.schema import ensure_schema
from ..ingest.upload import upload as do_upload

router = APIRouter(prefix="/api", tags=["ingest"])
_lock = threading.Lock()          # 同一时间只跑一个作业，SQLite 单写


# ------------------------------------------------------------------ status / runs
@router.get("/ingest/status")
def status(conn: Conn):
    return runner.status(conn)


@router.get("/ingest/runs")
def runs(conn: Conn, limit: int = Query(20, ge=1, le=200)):
    ensure_schema(conn)
    return runner.status(conn)["runs"][:limit]


class RunIn(BaseModel):
    full: bool = False
    only: str | None = Field(None, pattern="^(rss|cninfo_announcement|cninfo_irm)$")
    since: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="backfill:起")
    until: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="backfill:止")


@router.post("/ingest/run/{job}")
def run_job(job: str, body: RunIn | None = None):
    if job not in runner.JOBS:
        raise HTTPException(404, f"unknown job {job!r}; one of {runner.JOBS}")
    body = body or RunIn()
    if not _lock.acquire(blocking=False):
        raise HTTPException(409, "另一个作业还在跑，稍后再试（GET /api/ingest/runs）")

    def work():
        try:
            runner.run(job, full=body.full, only=body.only, since=body.since, until=body.until, log=lambda *_: None)
        finally:
            _lock.release()

    threading.Thread(target=work, daemon=True, name=f"ingest-{job}").start()
    return {"ok": True, "job": job, "started": True, "watch": "/api/ingest/runs"}


# ------------------------------------------------------------------ AI 交接
@router.get("/ingest/todo")
def todo(conn: Conn, status: str = Query("open", pattern="^(open|done|dropped|all)$")):
    ensure_schema(conn)
    q, args = "SELECT * FROM ingest_todo", []
    if status != "all":
        q += " WHERE status=?"; args.append(status)
    q += " ORDER BY created_at DESC"
    items = [dict(r) for r in conn.execute(q, args)]
    return {"count": len(items), "items": items,
            "how": "逐条按 hint 去网页端取数，整理成 rows 后 POST /api/ingest/upload；bars/margin/holders/valuation 传完再 POST /api/ingest/run/recompute。"
                   "kind=candidate_triage 是交给你判的候选：读原文，按 hint 判定后 POST /api/candidates/judge 批量交回（一批最多 200 条）。"}


class TodoPatch(BaseModel):
    status: str = Field(pattern="^(open|done|dropped)$")


@router.patch("/ingest/todo/{todo_id}")
def patch_todo(todo_id: int, body: TodoPatch, conn: Conn):
    ensure_schema(conn)
    if not conn.execute("SELECT 1 FROM ingest_todo WHERE id=?", (todo_id,)).fetchone():
        raise HTTPException(404, "todo not found")
    conn.execute("UPDATE ingest_todo SET status=? WHERE id=?", (body.status, todo_id))
    conn.commit()
    return {"ok": True}


class UploadIn(BaseModel):
    kind: str = Field(pattern="^(bars|margin|holders|valuation|candidates)$")
    company_id: str | None = None
    rows: list[dict[str, Any]]
    source: str = "upload"


@router.post("/ingest/upload")
def upload(body: UploadIn, conn: Conn):
    ensure_schema(conn)
    try:
        return do_upload(conn, body.kind, body.company_id, body.rows, body.source)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except (ValueError, KeyError) as e:
        raise HTTPException(422, str(e))


# ------------------------------------------------------------------ 候选事件
@router.get("/candidates")
def list_candidates(conn: Conn, status: str = Query("pending", pattern="^(pending|confirmed|rejected|all)$"),
                    company: str | None = None, limit: int = Query(200, ge=1, le=1000),
                    relevant: str = Query("1", pattern="^(1|0|all)$", description="1 值得看（默认）· 0 例行公告 · all 全部")):
    ensure_schema(conn)
    rel = None if relevant == "all" else relevant == "1"
    return {"counts": C.counts(conn), "items": C.list_candidates(conn, status=status, limit=limit, company=company, relevant=rel)}


@router.post("/candidates/account")
def account(conn: Conn):
    """对还没人判过的候选跑一遍自动入账规则(同 python -m app.ingest triage)。"""
    from ..ingest import accounting
    ensure_schema(conn)
    out = accounting.account(conn)
    out["summary"] = accounting.summary(conn)
    return out


@router.post("/events/{event_id}/dismiss")
def dismiss_event(event_id: str, body: NoteIn | None, conn: Conn):
    """人工只剩这一个动作:这条已入账的事件「不算」。可撤回。"""
    ensure_schema(conn)
    try:
        return C.dismiss_event(conn, event_id, (body or NoteIn()).note)
    except LookupError as e:
        raise HTTPException(404, str(e))


@router.post("/events/{event_id}/restore")
def restore_event(event_id: str, conn: Conn):
    ensure_schema(conn)
    try:
        return C.restore_event(conn, event_id)
    except LookupError as e:
        raise HTTPException(404, str(e))


@router.post("/candidates/retriage")
def retriage(conn: Conn):
    """规则改了之后给库里的候选重算 relevance。"""
    from ..ingest.news import retriage as do
    ensure_schema(conn)
    return do(conn)


class JudgeIn(BaseModel):
    by: str = Field("ai", pattern="^(ai|human)$")
    items: list[dict[str, Any]] = Field(min_length=1, max_length=C.JUDGE_MAX)


@router.post("/candidates/judge")
def judge(body: JudgeIn, conn: Conn):
    """AI 批量交回判定(交给 AI 的待办的 hint 里有格式)。每条:
    {id, is_chokepoint:true, part_id, category, date, thesis, confidence 1–5, reason, company_id?} → 入账;
    {id, is_chokepoint:false, reason} → 不算。每条各自成败,返回每条的结果或错误;处理完统一重算一次反应。"""
    ensure_schema(conn)
    return C.judge(conn, body.items, by=body.by)


class ConfirmIn(BaseModel):
    company_id: str | None = None
    category: str | None = Field(None, pattern="^(capex|order|qualification|supply|price|roadmap|buyback|other)$")
    date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    title: str | None = None
    summary: str | None = None
    note: str | None = None
    by: str = Field("ai", pattern="^(rule|ai|human)$", description="谁判的;接口默认是服务器上的 AI")
    part_id: str | None = None
    thesis: str | None = None
    confidence: int | None = Field(None, ge=1, le=5)


@router.post("/candidates/{cand_id}/confirm")
def confirm(cand_id: str, body: ConfirmIn | None, conn: Conn):
    ensure_schema(conn)
    body = body or ConfirmIn()
    try:
        return C.confirm(conn, cand_id, company_id=body.company_id, category=body.category, event_date=body.date,
                         title=body.title, summary=body.summary, note=body.note, by=body.by,
                         part_id=body.part_id, thesis=body.thesis, confidence=body.confidence)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))


class NoteIn(BaseModel):
    note: str | None = None
    by: str = Field("ai", pattern="^(rule|ai|human)$")


@router.post("/candidates/{cand_id}/reject")
def reject(cand_id: str, body: NoteIn | None, conn: Conn):
    ensure_schema(conn)
    try:
        b = body or NoteIn()
        return C.reject(conn, cand_id, b.note, by=b.by)
    except LookupError as e:
        raise HTTPException(404, str(e))


@router.post("/candidates/{cand_id}/reopen")
def reopen(cand_id: str, conn: Conn):
    ensure_schema(conn)
    try:
        return C.reopen(conn, cand_id)
    except LookupError as e:
        raise HTTPException(404, str(e))
