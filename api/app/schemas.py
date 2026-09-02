"""Response models. Kept permissive (extra fields allowed) so the JSON shape can
grow without breaking the client; the names here are the contract."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

EvidenceLevel = Literal["reference", "candidate", "reviewed"]


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow")


class NodeRef(_Base):
    id: str
    kind: str
    name: str
    name_en: str | None = None
    code: str | None = None


class ChainRef(_Base):
    id: str
    name: str


class Node(_Base):
    id: str
    parent_id: str | None = None
    kind: Literal["product", "module", "part"]
    sort: int
    code: str | None = None
    name: str
    name_en: str | None = None
    name_full: str | None = None
    summary: str | None = None
    description: str | None = None
    status: str | None = None
    visual: str | None = None
    eyebrow: str | None = None
    source_note: str | None = None
    extra: dict[str, Any] | None = None


class ModuleWithParts(Node):
    children: list[Node] = []
    chain_nodes: list[ChainRef] = []


class CompanyExposureRef(_Base):
    id: str
    name: str
    evidence_level: EvidenceLevel


class CompanySummary(_Base):
    id: str
    name: str
    short_name: str | None = None
    ticker: str | None = None
    exchange: str | None = None
    country_region: str | None = None
    universe_layer: str | None = None
    coverage_priority: str | None = None
    evidence_level: EvidenceLevel | None = None
    chain_nodes: list[CompanyExposureRef] = []
    roles: list[str] = []


class ChainNode(_Base):
    id: str
    sort: int
    name: str
    display_name: str | None = None
    node_type: str | None = None
    keywords: str | None = None
    companies: list[CompanySummary] = []
    modules: list[NodeRef] = []


class Technology(_Base):
    id: str
    name: str
    description: str | None = None


class Product(Node):
    children: list[ModuleWithParts] = []
    chain: list[ChainNode] = []
    signal_path: dict[str, Any] | None = None


class NodeDetail(_Base):
    node: Node
    ancestors: list[NodeRef]
    children: list[Node]
    siblings: list[NodeRef]
    chain_nodes: list[ChainNode]
    technologies: list[Technology]
    companies: list[CompanySummary]


class Exposure(_Base):
    id: int
    chain_node_id: str
    chain_name: str | None = None
    node_id: str | None = None
    node_name: str | None = None
    role: str | None = None
    evidence_level: EvidenceLevel
    note: str | None = None
    source_id: str | None = None
    source_publisher: str | None = None
    source_title: str | None = None
    source_kind: str | None = None
    source_url: str | None = None
    source_year_range: str | None = None


class CompanyDetail(CompanySummary):
    official_url: str | None = None
    exposures: list[Exposure] = []
    modules: list[NodeRef] = []
