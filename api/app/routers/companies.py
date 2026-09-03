from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import insights, market, repo, research
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


@router.get("/companies/{company_id}/market")
def company_market(company_id: str, conn: Conn, months: int = Query(6, ge=1, le=24)):
    d = market.company_market(conn, company_id, months=months)
    if not d:
        raise HTTPException(404, f"company {company_id!r} not found")
    d["crowding_conclusion"] = insights.crowding(d["crowding"], kind="company")
    d["events_conclusion"] = insights.company_events(d["events_30d"])
    d["headline"] = insights.company_headline(d["events_30d"], d["crowding"])
    d["thesis"] = research.thesis_view(conn, company_id) or (research.thesis_for_node(conn, d["primary_layer"]["id"]) if d["primary_layer"] else None)
    names = {d["company"]["short_name"], d["company"]["name"]} - {None}
    d["backlinks"] = research.backlinks(conn, names, {f"company:{company_id}"}, exclude=company_id)
    return d
