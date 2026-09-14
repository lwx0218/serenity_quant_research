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
  physical: () => get<PhysObjectRef[]>(`/api/physical`),
  physicalObject: (id: string) => get<PhysObject>(`/api/physical/${encodeURIComponent(id)}`),
  companyPhysical: (id: string) => get<CompanyPart[]>(`/api/companies/${encodeURIComponent(id)}/physical`),
  /** static drawing assets exported by physical/design/build_prototype.py */
  physicalDrawing: (id: string) => fetch(`/physical/${encodeURIComponent(id)}.json`).then((r) => r.json() as Promise<PhysDrawing>),
  physicalSvg: (id: string, theme: "light" | "dark", dir: "tx" | "rx") => fetch(`/physical/${encodeURIComponent(id)}.${theme}.${dir}.svg`).then((r) => r.text()),
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

/* ======================================================================
   Market layer (api/app/market.py, insights.py, research.py)
   ====================================================================== */
export type Direction = "pos" | "neg" | "neu";
export interface Conclusion { direction: Direction; text: string; verdict?: string | null }
export interface Freshness { state: "window" | "priced" | "unreacted" | "expired" | "pending" | "nodata"; days: number; validity: number; label: string }

export interface CompanyBrief { id: string; name: string; short_name: string | null; ticker: string | null; exchange: string | null; country_region: string | null }
export interface ModuleBrief { id: string; sort: number; code: string | null; name: string; name_en: string | null }

export interface MarketEvent {
  id: string; date: string; title: string; summary: string | null;
  category: string; category_label: string; source_kind: string; source_label: string;
  source_title: string | null; source_url: string | null;
  company: CompanyBrief | null; node: ModuleBrief | null; layer_id: string | null; layer_ids: string[];
  reaction: { t1: number | null; t3: number | null; t5: number | null; t20: number | null; reference: string; abs_t1: number | null };
  volume_ratio: number | null; turnover_pct_rank: number | null;
  freshness: Freshness; status: string; is_sample: boolean;
  part?: EventPart | null;
}

/** Where an event lands on a physical object (the seam physical → market). */
export interface EventPart { object_id: string; object_name: string; part_id: string; part_name: string; step: number | null; stage: string; others: number }

/* --------------------------------------------------------------- physical layer */
export type PhysEvidence = "verified" | "consensus" | "candidate";
export const PHYS_EVIDENCE_LABEL: Record<PhysEvidence, string> = { verified: "已核验", consensus: "行业图示", candidate: "候选 · 待核验" };
export interface PhysStage { id: string; name: string; order: number }
export interface PhysStep { step: number; partId: string; signal: string; text: string }
export interface PhysLink { company_id: string | null; name: string; short_name: string | null; ticker: string | null; market: string | null; stage: string; role: string | null; evidence: PhysEvidence }
export interface PhysPart { id: string; sort: number; name: string; name_en: string | null; function: string | null; key_specs: string[]; materials: string[]; companies: PhysLink[] }
export interface PhysObject {
  id: string; name: string; name_en: string | null; form_factor: string | null; as_of: string | null;
  spec: Record<string, string>; host: { summary?: string; platforms?: { name: string; role: string }[] };
  stages: PhysStage[]; signal: { tx: PhysStep[]; rx: PhysStep[] }; parts: PhysPart[];
}
export interface PhysObjectRef { id: string; name: string; name_en: string | null; form_factor: string | null; as_of: string | null; parts: number }
export interface CompanyPart { object_id: string; object_name: string; part_id: string; part_name: string; step: number | null; stage: string; role: string | null; evidence: PhysEvidence }
export interface PhysDrawing { object: string; width: number; height: number; anchors: Record<string, [number, number]> }

export interface EventsResponse { as_of: string; window_days: number | null; count: number; items: MarketEvent[]; conclusion: Conclusion | null; validity_days: number | null; sample: boolean }

export interface Overview {
  as_of: string; window_days: number; sample: boolean; conclusion: Conclusion;
  counts: { events: number; reacted: number; unreacted: number; pending: number; verifications: number; theses_expiring: number };
  layers: { node_id: string; events: number; basket_excess: number | null; direction: Direction | null }[];
}

export interface Crowding {
  instrument: string; as_of: string; window_days: number; metrics: Record<string, any>;
  directions: Record<string, Direction | null>; direction: Direction; level: string; is_sample: boolean;
}

export interface Reading { instrument: string; label: string; excess: number | null }
export interface Question { index: number; text: string; status: "open" | "verified"; date: string | null }
export interface Thesis {
  subject: string; kind: string; title: string; direction: Direction; stance: string; updated: string | null; since: string | null;
  window_until: string | null; window_label: string | null; threshold_pct: number; position: string | null; sample: boolean;
  track: string[]; indicators: string[]; invalidation: string[]; body: string; questions: Question[]; path: string; links: string[];
  readings: Reading[]; conclusion: Conclusion; as_of: string; days_left: number | null; expired: boolean; expiring: boolean;
}

export interface LastEvent { id?: string; date: string; category_label: string; t1: number | null; freshness: Freshness }
export interface NodeMarket {
  as_of: string; window_days: number; module: ModuleBrief; sample: boolean;
  basket: { excess: number | null; direction: Direction | null; members: number };
  events: MarketEvent[]; events_conclusion: Conclusion; validity_days: number;
  thesis: Thesis | null; company_events: Record<string, LastEvent | null>;
  backlinks: Backlink[];
}
export interface Backlink { subject: string; title: string; kind: string; direction: Direction }

export interface Resonance {
  as_of: string; event: MarketEvent; conclusion: Conclusion;
  self: { t1: number | null; t3: number | null; excess_t1: number | null; volume_ratio: number | null; turnover_pct_rank: number | null };
  peers: { company: CompanyBrief; t1: number | null }[]; same_direction: { k: number; n: number }; basket_t1: number | null;
  adjacent: { node: { id: string; name: string; sort: number }; t1: number | null; relation: string }[];
  attention: Record<string, any> | null; baseline: { n: number; avg_t1: number; hits: number; above: boolean } | null;
  layer: ModuleBrief | null;
}

export interface CompanyMarket {
  as_of: string; company: CompanyBrief; layers: ModuleBrief[]; primary_layer: ModuleBrief | null;
  series: [string, number][]; chart_events: { id: string; date: string; category_label: string; value: number }[]; window_months: number;
  metrics: { pe_ttm: number | null; pe_pct_rank_5y: number | null; ret_3m: number | null; excess_basket_3m: number | null; excess_product_3m: number | null; last: number | null };
  crowding: Crowding | null; events_30d: MarketEvent[]; pending_verifications: Verification[]; sample: boolean;
  crowding_conclusion: Conclusion; events_conclusion: Conclusion; headline: Conclusion; thesis: Thesis | null; backlinks: Backlink[];
}

export interface Verification {
  kind: "upgrade" | "review"; event?: MarketEvent; exposure_id: number | null; chain_name: string; company: CompanyBrief;
  from_level: string; to_level: string; text: string; detail: string; source_url?: string | null; direction: Direction;
}

export interface BasketMember {
  company: CompanyBrief; ret_3m: number | null; ret_6m: number | null; pe_pct_rank_5y: number | null;
  crowd_pct: number | null; crowd_level: string | null; crowd_direction: Direction | null; last_event: LastEvent | null; evidence_level: EvidenceLevel | null;
}
export interface BasketSummary {
  node_id: string; sort: number; code: string | null; name: string; name_en: string | null; members: number;
  ret_3m: number | null; excess_3m: number | null; crowd_pct: number | null; crowd_level: string | null; crowd_direction: Direction | null; last_event: LastEvent | null;
}
export interface EfficacyRow { key: string; text: string; parts: [string, number | null][]; strong?: string }
export interface Basket {
  as_of: string; node: ModuleBrief; members: BasketMember[]; window_months: number;
  series: { basket: [string, number][]; product: [string, number][] };
  chart_events: { id: string; date: string; category_label: string; value: number; company: string | null }[];
  excess_window: number | null; ret_window: number | null;
  efficacy: { sample_n: number; avg: Record<string, number | null>; hit_rate: number; half_life_days: number | null; validity_days: number; give_back_t5_t20: number | null } | null;
  crowding: Crowding | null; member_dispersion: { high: number; mid: number; low: number }; others: BasketSummary[]; product_members: number;
  conclusion: Conclusion; efficacy_conclusion: Conclusion; crowding_conclusion: Conclusion; efficacy_rows: EfficacyRow[]; sample: boolean;
}

export interface Decision {
  kind: "deviation" | "thesis" | "verify"; urgency: number; label: string; direction: Direction; headline: string; text: string;
  actions: { label: string; to?: string; action?: string; subject?: string }[]; subject: string; event_id?: string | null; exposure_id?: number | null;
}
export interface Inbox {
  as_of: string; window_days: number; sample: boolean; conclusion: Conclusion; decisions: Decision[]; events: MarketEvent[];
  questions: { subject: string; subject_title: string; kind: string; index: number; text: string; date: string | null; status: string }[];
  notes: { subject: string; title: string; kind: string; direction: Direction; updated: string | null; excerpt: string; path: string }[];
  rail: { node_id: string; sort: number; name: string; events: number; basket_excess: number | null; direction: Direction | null }[];
}

export interface LinkSuggestion { label: string; kind: string; id: string; meta: string }

async function send<T>(method: string, path: string, body?: unknown): Promise<T> {
  const r = await fetch(BASE + path, { method, headers: { Accept: "application/json", "Content-Type": "application/json" }, body: body === undefined ? undefined : JSON.stringify(body) });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} — ${path}`);
  return (await r.json()) as T;
}

export const mkt = {
  overview: (productId: string, days = 7) => get<Overview>(`/api/overview/${encodeURIComponent(productId)}?days=${days}`),
  nodeMarket: (id: string, days = 7) => get<NodeMarket>(`/api/nodes/${encodeURIComponent(id)}/market?days=${days}`),
  events: (q: { node?: string; company?: string; days?: number; limit?: number } = {}) => {
    const p = new URLSearchParams();
    if (q.node) p.set("node", q.node);
    if (q.company) p.set("company", q.company);
    if (q.days) p.set("days", String(q.days));
    if (q.limit) p.set("limit", String(q.limit));
    const s = p.toString();
    return get<EventsResponse>(`/api/events${s ? "?" + s : ""}`);
  },
  resonance: (id: string) => get<Resonance>(`/api/events/${encodeURIComponent(id)}/resonance`),
  companyMarket: (id: string, months = 6) => get<CompanyMarket>(`/api/companies/${encodeURIComponent(id)}/market?months=${months}`),
  basket: (nodeId: string, months = 6) => get<Basket>(`/api/baskets/${encodeURIComponent(nodeId)}?months=${months}`),
  baskets: () => get<{ as_of: string; items: BasketSummary[]; sample: boolean }>(`/api/baskets`),
  note: (subject: string) => get<Thesis>(`/api/notes/${encodeURIComponent(subject)}`),
  saveNote: (subject: string, body: Partial<Thesis>) => send<Thesis>("PUT", `/api/notes/${encodeURIComponent(subject)}`, body),
  addQuestion: (subject: string, text: string) => send<Thesis>("POST", `/api/notes/${encodeURIComponent(subject)}/questions`, { text }),
  setQuestion: (subject: string, index: number, status: "open" | "verified") => send<Thesis>("PATCH", `/api/notes/${encodeURIComponent(subject)}/questions/${index}`, { status }),
  extendNote: (subject: string) => send<Thesis>("POST", `/api/notes/${encodeURIComponent(subject)}/extend`),
  inbox: (days = 7) => get<Inbox>(`/api/research/inbox?days=${days}`),
  verify: (body: { action: string; event_id?: string | null; exposure_id?: number | null }) => send<{ ok: boolean }>("POST", `/api/verifications`, body),
  suggest: (q: string) => get<LinkSuggestion[]>(`/api/links/suggest?q=${encodeURIComponent(q)}`),
};

/* ---------- formatting ---------- */
/** "+2.4%" / "−0.6%" (typographic minus) / "—" */
export function pct(x: number | null | undefined, digits = 1): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  const v = Math.round(x * 100 * 10 ** digits) / 10 ** digits;
  const s = Math.abs(v).toFixed(digits) + "%";
  return v > 0 ? "+" + s : v < 0 ? "−" + s : s;
}
export function sigma(x: number | null | undefined): string {
  if (x === null || x === undefined) return "—";
  return (x > 0 ? "+" : x < 0 ? "−" : "") + Math.abs(x).toFixed(1) + "σ";
}
export function dirOf(x: number | null | undefined, eps = 0): Direction {
  if (x === null || x === undefined) return "neu";
  return x > eps ? "pos" : x < -eps ? "neg" : "neu";
}
export const DIR_GLYPH: Record<Direction, string> = { pos: "▲", neg: "▼", neu: "●" };
export const DIR_LABEL: Record<Direction, string> = { pos: "偏多", neg: "偏空", neu: "中性" };
/** "08-26" from "2026-08-26" */
export const md = (d: string | null | undefined) => (d ? d.slice(5) : "");
/** "08-28 收盘" */
export const asOfLabel = (d: string | null | undefined) => (d ? `${d.slice(5)} 收盘` : "");
/** "2027-Q1" from "2027-03-31" */
export function quarter(d: string): string {
  const m = parseInt(d.slice(5, 7), 10);
  return `${d.slice(0, 4)}-Q${Math.ceil(m / 3)}`;
}
