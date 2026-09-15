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


@router.post("/ingest/run/{job}")
def run_job(job: str, body: RunIn | None = None):
    if job not in runner.JOBS:
        raise HTTPException(404, f"unknown job {job!r}; one of {runner.JOBS}")
    body = body or RunIn()
    if not _lock.acquire(blocking=False):
        raise HTTPException(409, "另一个作业还在跑，稍后再试（GET /api/ingest/runs）")

    def work():
        try:
            runner.run(job, full=body.full, only=body.only, log=lambda *_: None)
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
            "how": "逐条按 hint 去网页端取数，整理成 rows 后 POST /api/ingest/upload；bars/margin/holders/valuation 传完再 POST /api/ingest/run/recompute。"}


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
                    company: str | None = None, limit: int = Query(100, ge=1, le=500)):
    ensure_schema(conn)
    return {"counts": C.counts(conn), "items": C.list_candidates(conn, status=status, limit=limit, company=company)}


class ConfirmIn(BaseModel):
    company_id: str | None = None
    category: str | None = Field(None, pattern="^(capex|order|qualification|supply|price|roadmap|buyback|other)$")
    date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    title: str | None = None
    summary: str | None = None
    note: str | None = None


@router.post("/candidates/{cand_id}/confirm")
def confirm(cand_id: str, body: ConfirmIn | None, conn: Conn):
    ensure_schema(conn)
    body = body or ConfirmIn()
    try:
        return C.confirm(conn, cand_id, company_id=body.company_id, category=body.category, event_date=body.date,
                         title=body.title, summary=body.summary, note=body.note)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))


class NoteIn(BaseModel):
    note: str | None = None


@router.post("/candidates/{cand_id}/reject")
def reject(cand_id: str, body: NoteIn | None, conn: Conn):
    ensure_schema(conn)
    try:
        return C.reject(conn, cand_id, (body or NoteIn()).note)
    except LookupError as e:
        raise HTTPException(404, str(e))


@router.post("/candidates/{cand_id}/reopen")
def reopen(cand_id: str, conn: Conn):
    ensure_schema(conn)
    try:
        return C.reopen(conn, cand_id)
    except LookupError as e:
        raise HTTPException(404, str(e))
