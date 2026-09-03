from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import market, notes as N, research
from ..deps import Conn

router = APIRouter(prefix="/api", tags=["notes"])


class NoteIn(BaseModel):
    kind: str = "module"
    title: str = ""
    direction: str = Field("neu", pattern="^(pos|neg|neu)$")
    stance: str = ""
    body: str = ""
    since: str | None = None
    window_until: str | None = None
    window_label: str | None = None
    threshold_pct: float = 3.0
    position: str | None = None
    track: list[str] = []
    indicators: list[str] = []
    invalidation: list[str] = []


class QuestionIn(BaseModel):
    text: str
    date: str | None = None


class QuestionPatch(BaseModel):
    status: str = Field(pattern="^(open|verified)$")


@router.get("/notes")
def list_notes(conn: Conn):
    return {"items": research.recent_notes(conn, limit=100), "questions": research.open_questions(conn)}


@router.get("/notes/{subject}")
def get_note(subject: str, conn: Conn):
    v = research.thesis_view(conn, subject)
    if not v:
        raise HTTPException(404, f"no note for {subject!r}")
    return v


@router.put("/notes/{subject}")
def put_note(subject: str, body: NoteIn, conn: Conn):
    existing = N.load_note(subject)
    n = existing or N.Note(subject=subject)
    for k in ("kind", "title", "direction", "stance", "body", "since", "window_until", "window_label",
              "threshold_pct", "position", "track", "indicators", "invalidation"):
        setattr(n, k, getattr(body, k))
    if not n.title:
        m = market.module_of(conn, subject)
        c = market.company_brief(conn, subject)
        n.title = (m or {}).get("name") or (c or {}).get("short_name") or subject
    n.updated = date.today().isoformat()
    n.since = n.since or n.updated
    n.sample = False
    N.save_note(n)
    return research.thesis_view(conn, subject)


@router.post("/notes/{subject}/questions")
def add_question(subject: str, q: QuestionIn, conn: Conn):
    n = N.load_note(subject)
    if not n:
        m = market.module_of(conn, subject)
        c = market.company_brief(conn, subject)
        n = N.Note(subject=subject, kind="company" if c else "module", title=(m or {}).get("name") or (c or {}).get("short_name") or subject)
    n.questions.append({"index": len(n.questions) + 1, "text": q.text.strip(), "status": "open", "date": q.date or date.today().isoformat()})
    N.save_note(n)
    return research.thesis_view(conn, subject)


@router.patch("/notes/{subject}/questions/{index}")
def patch_question(subject: str, index: int, p: QuestionPatch, conn: Conn):
    n = N.load_note(subject)
    if not n or index < 1 or index > len(n.questions):
        raise HTTPException(404, "question not found")
    n.questions[index - 1]["status"] = p.status
    N.save_note(n)
    return research.thesis_view(conn, subject)


@router.post("/notes/{subject}/extend")
def extend(subject: str, conn: Conn, months: int = 3):
    r = research.extend_thesis(subject, months)
    if not r:
        raise HTTPException(404, f"no note for {subject!r}")
    return research.thesis_view(conn, subject)


@router.get("/links/suggest")
def suggest_links(conn: Conn, q: str = ""):
    """[[ autocomplete: companies, chain nodes, modules and parts by name."""
    needle = q.strip().lower()
    out = []
    for r in conn.execute("SELECT id, short_name, name, ticker FROM companies ORDER BY short_name"):
        label = r["short_name"] or r["name"]
        if not needle or needle in label.lower() or needle in (r["ticker"] or "").lower() or needle in (r["name"] or "").lower():
            out.append({"label": label, "kind": "公司", "id": r["id"], "meta": r["ticker"] or ""})
    for r in conn.execute("SELECT id, display_name, name FROM chain_nodes ORDER BY sort"):
        label = r["display_name"] or r["name"]
        if not needle or needle in label.lower():
            out.append({"label": label, "kind": "环节", "id": r["id"], "meta": ""})
    for r in conn.execute("SELECT id, kind, name, sort FROM nodes WHERE kind IN ('module','part') ORDER BY kind DESC, sort"):
        if not needle or needle in r["name"].lower():
            out.append({"label": r["name"], "kind": "层" if r["kind"] == "module" else "部件", "id": r["id"],
                        "meta": f"{r['sort']:02d}" if r["kind"] == "module" else ""})
    return out[:12]
