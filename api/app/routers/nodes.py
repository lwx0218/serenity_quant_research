from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import repo
from ..deps import Conn
from ..schemas import NodeDetail, Product

router = APIRouter(prefix="/api", tags=["nodes"])


@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str, conn: Conn):
    tree = repo.product_tree(conn, product_id)
    if not tree:
        raise HTTPException(404, f"product {product_id!r} not found")
    return tree


@router.get("/nodes/{node_id}", response_model=NodeDetail)
def get_node(node_id: str, conn: Conn):
    node = repo.get_node(conn, node_id)
    if not node:
        raise HTTPException(404, f"node {node_id!r} not found")
    siblings = []
    if node["parent_id"]:
        siblings = [
            {"id": s["id"], "kind": s["kind"], "name": s["name"], "name_en": s["name_en"], "code": s["code"]}
            for s in repo.children(conn, node["parent_id"])
        ]
    chain_nodes = repo.chain_nodes_for(conn, node_id)
    for cn in chain_nodes:
        cn["companies"] = repo.companies_for_chain(conn, cn["id"])
    return {
        "node": node,
        "ancestors": repo.ancestors(conn, node_id),
        "children": repo.children(conn, node_id),
        "siblings": siblings,
        "chain_nodes": chain_nodes,
        "technologies": repo.technologies_for(conn, node_id),
        "companies": repo.companies_for_node(conn, node_id),
    }
