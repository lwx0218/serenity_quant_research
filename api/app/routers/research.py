from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .. import market, research
from ..deps import Conn

router = APIRouter(prefix="/api", tags=["research"])


class VerificationIn(BaseModel):
    action: str = Field(pattern="^(upgrade|ignore|accept|reject)$")
    event_id: str | None = None
    exposure_id: int | None = None
    note: str | None = None


@router.get("/research/inbox")
def inbox(conn: Conn, days: int = Query(7, ge=1, le=60)):
    return research.inbox(conn, days)


@router.post("/verifications")
def verify(v: VerificationIn, conn: Conn):
    try:
        return market.apply_verification(conn, v.action, v.event_id, v.exposure_id, v.note)
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(409, str(e))
