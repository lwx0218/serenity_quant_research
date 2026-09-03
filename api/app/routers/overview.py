from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import insights, market, research
from ..deps import Conn

router = APIRouter(prefix="/api", tags=["overview"])


@router.get("/overview/{product_id}")
def overview(product_id: str, conn: Conn, days: int = Query(7, ge=1, le=60)):
    """首页第一行: what changed, per-layer activity and the counts behind the links."""
    if market.product_id(conn) != product_id:
        raise HTTPException(404, f"product {product_id!r} not found")
    when = market.as_of(conn)
    activity = market.layer_activity(conn, days, when)
    events = market.list_events(conn, days=days, limit=100, when=when)
    states = [e["freshness"]["state"] for e in events]
    dec = research.decisions(conn, when)
    return {
        "as_of": when.isoformat(), "window_days": days, "sample": market.is_sample(conn),
        "conclusion": insights.overview(activity, events, days),
        "counts": {
            "events": len(events),
            "reacted": states.count("window") + states.count("priced"),
            "unreacted": states.count("unreacted") + states.count("expired"),
            "pending": states.count("pending"),
            "verifications": sum(1 for d in dec if d["kind"] == "verify"),
            "theses_expiring": sum(1 for d in dec if d["kind"] == "thesis"),
        },
        "layers": [{"node_id": a["id"], "events": a["events"], "basket_excess": a["basket_excess"], "direction": a["direction"]} for a in activity],
    }
