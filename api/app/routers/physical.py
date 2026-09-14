from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import physical
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


@router.get("/companies/{company_id}/physical")
def company_parts(company_id: str, conn: Conn):
    return physical.company_parts(conn, company_id)
