/** Typed fetchers for the FastAPI backend. Shapes mirror api/app/schemas.py. */

export type EvidenceLevel = "reference" | "candidate" | "reviewed";
export type NodeKind = "product" | "module" | "part";

export interface NodeRef {
  id: string;
  kind: NodeKind;
  name: string;
  name_en?: string | null;
  code?: string | null;
  sort?: number;
}

export interface Node {
  id: string;
  parent_id: string | null;
  kind: NodeKind;
  sort: number;
  code: string | null;
  name: string;
  name_en: string | null;
  name_full: string | null;
  summary: string | null;
  description: string | null;
  status: string | null;
  visual: string | null;
  eyebrow: string | null;
  source_note: string | null;
  extra: Record<string, unknown> | null;
}

export interface ChainRef { id: string; name: string }

export interface ModuleWithParts extends Node {
  children: Node[];
  chain_nodes: ChainRef[];
}

export interface CompanyExposureRef { id: string; name: string; evidence_level: EvidenceLevel }

export interface CompanySummary {
  id: string;
  name: string;
  short_name: string | null;
  ticker: string | null;
  exchange: string | null;
  country_region: string | null;
  universe_layer: string | null;
  coverage_priority: string | null;
  evidence_level: EvidenceLevel | null;
  chain_nodes: CompanyExposureRef[];
  roles: string[];
}

export interface ChainNode {
  id: string;
  sort: number;
  name: string;
  display_name: string | null;
  node_type: string | null;
  keywords: string | null;
  companies: CompanySummary[];
  modules: NodeRef[];
}

export interface Technology { id: string; name: string; description: string | null }

export interface SignalStep { label: string; kind: string; moduleId?: string }
export interface SignalPath { summary: string; steps: SignalStep[] }

export interface Product extends Node {
  children: ModuleWithParts[];
  chain: ChainNode[];
  signal_path: SignalPath | null;
}

export interface NodeDetail {
  node: Node;
  ancestors: NodeRef[];
  children: Node[];
  siblings: NodeRef[];
  chain_nodes: ChainNode[];
  technologies: Technology[];
  companies: CompanySummary[];
}

export interface Exposure {
  id: number;
  chain_node_id: string;
  chain_name: string | null;
  node_id: string | null;
  node_name: string | null;
  role: string | null;
  evidence_level: EvidenceLevel;
  note: string | null;
  source_id: string | null;
  source_publisher: string | null;
  source_title: string | null;
  source_kind: string | null;
  source_url: string | null;
  source_year_range: string | null;
}

export interface CompanyDetail extends CompanySummary {
  official_url: string | null;
  exposures: Exposure[];
  modules: NodeRef[];
}

const BASE = import.meta.env.VITE_API_BASE ?? "";

async function get<T>(path: string): Promise<T> {
  const r = await fetch(BASE + path, { headers: { Accept: "application/json" } });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} — ${path}`);
  return (await r.json()) as T;
}

export const api = {
  product: (id: string) => get<Product>(`/api/products/${encodeURIComponent(id)}`),
  node: (id: string) => get<NodeDetail>(`/api/nodes/${encodeURIComponent(id)}`),
  chain: () => get<ChainNode[]>(`/api/chain`),
  companies: (q: { chain?: string; node?: string; q?: string } = {}) => {
    const p = new URLSearchParams();
    if (q.chain) p.set("chain", q.chain);
    if (q.node) p.set("node", q.node);
    if (q.q) p.set("q", q.q);
    const s = p.toString();
    return get<CompanySummary[]>(`/api/companies${s ? "?" + s : ""}`);
  },
  company: (id: string) => get<CompanyDetail>(`/api/companies/${encodeURIComponent(id)}`),
};

/* ---------- labels (zh) ---------- */
export const EVIDENCE_LABEL: Record<EvidenceLevel, string> = {
  reference: "行业图示",
  candidate: "候选 · 待核验",
  reviewed: "已核验",
};

export const STATUS_LABEL: Record<string, string> = {
  validated_category: "已确认类别",
  validated_system_category: "系统级类别",
  product_candidate: "候选产品形态",
  architecture_option: "架构选项",
  interface_option: "接口选项",
  product_boundary_pending: "产品边界待定",
};

export function statusLabel(s: string | null | undefined): string | null {
  if (!s) return null;
  return STATUS_LABEL[s] ?? s.replace(/_/g, " ");
}

export function pad2(n: number): string {
  return n < 10 ? `0${n}` : String(n);
}

export const EXCHANGE_LABEL: Record<string, string> = {
  SZSE: "深交所",
  SSE: "上交所",
  HKEX: "港交所",
  NASDAQ: "NASDAQ",
  NYSE: "NYSE",
};

/** "300308 · 深交所" / "AVGO · NASDAQ" / "" */
export function market(c: { ticker: string | null; exchange: string | null }): string {
  const ex = c.exchange ? EXCHANGE_LABEL[c.exchange] ?? c.exchange : null;
  return [c.ticker, ex].filter(Boolean).join(" · ");
}

export const ROLE_LABEL: Record<string, string> = {
  chip_vendor: "芯片供应商",
  module_vendor: "模块供应商",
  component_vendor: "器件供应商",
  material_vendor: "材料供应商",
  equipment_vendor: "设备供应商",
  system_vendor: "系统厂商",
  customer: "需求方",
};

export function roleLabel(r: string): string {
  return ROLE_LABEL[r] ?? r.replace(/_/g, " ");
}
