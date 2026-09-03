from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import insights, market
from ..deps import Conn

router = APIRouter(prefix="/api", tags=["events"])


@router.get("/events")
def list_events(
    conn: Conn,
    node: str | None = Query(None, description="module/part id: events touching this layer"),
    company: str | None = Query(None),
    days: int | None = Query(None, ge=1, le=400),
    limit: int = Query(50, ge=1, le=200),
):
    when = market.as_of(conn)
    items = market.list_events(conn, node=node, company=company, days=days, limit=limit, when=when)
    conclusion = None
    if node:
        m = market.module_of(conn, node)
        conclusion = insights.layer_events(items, m["name"] if m else "这一层")
    elif company:
        conclusion = insights.company_events(items)
    validity = market.validity_days(conn, market.module_of(conn, node)["id"]) if node and market.module_of(conn, node) else None
    return {"as_of": when.isoformat(), "window_days": days, "count": len(items), "items": items,
            "conclusion": conclusion, "validity_days": validity, "sample": market.is_sample(conn)}


@router.get("/events/{event_id}")
def get_event(event_id: str, conn: Conn):
    e = market.get_event(conn, event_id)
    if not e:
        raise HTTPException(404, f"event {event_id!r} not found")
    return e


@router.get("/events/{event_id}/resonance")
def resonance(event_id: str, conn: Conn):
    r = market.resonance(conn, event_id)
    if not r:
        raise HTTPException(404, f"event {event_id!r} not found")
    r["conclusion"] = insights.resonance(r)
    return r
