from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import repo
from ..deps import Conn
from ..schemas import CompanyDetail, CompanySummary

router = APIRouter(prefix="/api", tags=["companies"])


@router.get("/companies", response_model=list[CompanySummary])
def list_companies(
    conn: Conn,
    chain: str | None = Query(None, description="chain node id"),
    node: str | None = Query(None, description="module/part id (wins over chain)"),
    q: str | None = Query(None, description="name / ticker / id contains"),
):
    return repo.list_companies(conn, chain=chain, node=node, q=q)


@router.get("/companies/{company_id}", response_model=CompanyDetail)
def get_company(company_id: str, conn: Conn):
    c = repo.get_company(conn, company_id)
    if not c:
        raise HTTPException(404, f"company {company_id!r} not found")
    return c
