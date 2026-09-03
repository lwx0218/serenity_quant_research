from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import insights, market
from ..deps import Conn

router = APIRouter(prefix="/api", tags=["baskets"])


@router.get("/baskets")
def list_baskets(conn: Conn):
    when = market.as_of(conn)
    items = [market.basket_summary(conn, m, when) for m in market.module_rows(conn)]
    return {"as_of": when.isoformat(), "items": [i for i in items if i["members"] > 0], "sample": market.is_sample(conn)}


@router.get("/baskets/{node_id}")
def get_basket(node_id: str, conn: Conn, months: int = Query(6, ge=1, le=24)):
    d = market.basket_detail(conn, node_id, months=months)
    if not d:
        raise HTTPException(404, f"basket for {node_id!r} not found")
    d["conclusion"] = insights.basket(d)
    d["efficacy_conclusion"] = insights.efficacy(d["efficacy"], d["node"]["name"])
    d["efficacy_rows"] = insights.efficacy_rows(d["efficacy"])
    d["crowding_conclusion"] = insights.crowding(d["crowding"], kind="basket", dispersion=d["member_dispersion"])
    d["sample"] = market.is_sample(conn)
    return d
