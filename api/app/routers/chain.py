from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import repo
from ..deps import Conn
from ..schemas import ChainNode

router = APIRouter(prefix="/api", tags=["chain"])


@router.get("/chain", response_model=list[ChainNode])
def list_chain(conn: Conn):
    return repo.list_chain(conn)


@router.get("/chain/{chain_node_id}", response_model=ChainNode)
def get_chain_node(chain_node_id: str, conn: Conn):
    for cn in repo.list_chain(conn):
        if cn["id"] == chain_node_id:
            return cn
    raise HTTPException(404, f"chain node {chain_node_id!r} not found")
