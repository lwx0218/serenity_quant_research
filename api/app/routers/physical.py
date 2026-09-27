from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import market, physical
from ..deps import Conn

router = APIRouter(prefix="/api", tags=["physical"])


@router.get("/physical")
def list_objects(conn: Conn):
    return physical.list_objects(conn)


@router.get("/physical/{object_id}")
def get_object(object_id: str, conn: Conn):
    o = physical.get_object(conn, object_id)
    if not o:
        raise HTTPException(404, f"physical object {object_id!r} not found")
    return o


@router.get("/physical/{object_id}/market")
def object_market(object_id: str, conn: Conn, days: int = Query(7, ge=1, le=60)):
    """首页:每个部件的事件数与部件篮子读数,第一行是「资金本周在给哪个部件投票」。"""
    d = market.physical_market(conn, object_id, days=days)
    if not d:
        raise HTTPException(404, f"physical object {object_id!r} not found")
    return d


@router.get("/physical/{object_id}/parts/{part_id}/market")
def part_market(object_id: str, part_id: str, conn: Conn, months: int = Query(3, ge=1, le=24)):
    """选中一个部件:篮子走势与读数、卡口事件 30 天。"""
    d = market.part_market(conn, object_id, part_id, months=months)
    if not d:
        raise HTTPException(404, f"part {part_id!r} not found on {object_id!r}")
    return d


@router.get("/companies/{company_id}/physical")
def company_parts(company_id: str, conn: Conn):
    return physical.company_parts(conn, company_id)
