/**
 * Shared research blocks: the events table (narrow two-line / wide), the
 * judgement block (thesis + falsifiers + questions) and the resonance block.
 * Each block starts with its conclusion line and carries its as-of.
 */
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { mkt, md, pct, quarter, sigma, type LinkSuggestion, type MarketEvent, type Resonance, type Thesis } from "../lib/api";
import { Link } from "../lib/router";
import { AsOf, Conclusion, Dir, Fresh, Head, Reading, Sig } from "./Signal";

/* ------------------------------------------------------------------ [[links]] */
const linkCache = new Map<string, Promise<LinkSuggestion | null>>();
function resolveLink(name: string): Promise<LinkSuggestion | null> {
  if (!linkCache.has(name)) {
    linkCache.set(name, mkt.suggest(name).then((xs) => xs.find((x) => x.label === name) ?? xs[0] ?? null).catch(() => null));
  }
  return linkCache.get(name)!;
}
export function routeFor(s: LinkSuggestion): string {
  if (s.kind === "公司") return `/companies/${s.id}`;
  if (s.kind === "环节") return `/companies?chain=${encodeURIComponent(s.id)}`;
  return `/explore/${s.id}`;
}

/** Render Markdown-ish text: paragraphs, [[wikilinks]] resolved to routes, **bold**. */
export function Prose({ text, className }: { text: string; className?: string }) {
  const names = useMemo(() => Array.from(new Set(Array.from(text.matchAll(/\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g)).map((m) => m[1]))), [text]);
  const [targets, setTargets] = useState<Record<string, LinkSuggestion | null>>({});
  useEffect(() => {
    let live = true;
    Promise.all(names.map((n) => resolveLink(n).then((s) => [n, s] as const))).then((pairs) => {
      if (live) setTargets(Object.fromEntries(pairs));
    });
    return () => { live = false; };
  }, [names]);
  const paras = text.split(/\n{2,}/).filter((p) => p.trim());
  return (
    <>
      {paras.map((p, i) => (
        <p key={i} className={className ?? "prose"}>
          {p.split(/(\[\[[^\]]+\]\]|\*\*[^*]+\*\*)/g).map((seg, j) => {
            const wl = seg.match(/^\[\[([^\]|]+)(?:\|([^\]]+))?\]\]$/);
            if (wl) {
              const t = targets[wl[1]];
              const label = wl[2] ?? wl[1];
              return t ? <Link key={j} to={routeFor(t)} className="wikilink">{label}</Link> : <span key={j} className="wikilink is-unresolved">{label}</span>;
            }
            const b = seg.match(/^\*\*([^*]+)\*\*$/);
            if (b) return <strong key={j}>{b[1]}</strong>;
            return <span key={j}>{seg}</span>;
          })}
        </p>
      ))}
    </>
  );
}

/* --------------------------------------------------------------- events table */
function subjectOf(e: MarketEvent): { label: string; to: string | null } {
  if (e.company) return { label: e.company.short_name ?? e.company.name, to: `/companies/${e.company.id}` };
  if (e.node) return { label: e.node.name, to: `/explore/${e.node.id}` };
  return { label: "—", to: null };
}

/** Narrow (≤ 560px) two-line events table: 日期 · 公司+类别/标题 · T+1+量比 · 时效 */
export function EventsNarrow({ items, onPick, hotId }: { items: MarketEvent[]; onPick?: (e: MarketEvent) => void; hotId?: string | null }) {
  return (
    <div className="rows">
      <div className="row ev-row is-head">
        <span className="row-meta">日期</span><span className="row-meta">公司 · 事件 · 类别</span><span className="row-meta">T+1 · 量比</span><span className="row-meta">时效</span>
      </div>
      {items.map((e) => {
        const s = subjectOf(e);
        const Row: any = onPick ? "button" : "div";
        return (
          <Row key={e.id} className={`row ev-row${onPick ? " is-pick" : ""}${hotId === e.id ? " is-hot-row" : ""}`} onClick={onPick ? () => onPick(e) : undefined} type={onPick ? "button" : undefined} style={onPick ? { textAlign: "left" } : undefined}>
            <span className="row-meta">{md(e.date)}</span>
            <span className="ev-main">
              <span className="ev-who">{s.to ? <Link to={s.to} style={{ color: "inherit" }}>{s.label}</Link> : s.label}<span className="ev-cat">{e.category_label}</span></span>
              <span className="ev-title">{e.source_url ? <a href={e.source_url} target="_blank" rel="noreferrer" style={{ color: "inherit" }}>{e.title}</a> : e.title}</span>
            </span>
            <span className="ev-num"><Sig v={e.reaction.t1} size={13} /><span className="row-meta">{e.volume_ratio != null ? e.volume_ratio.toFixed(1) : "—"}</span></span>
            <Fresh f={e.freshness} />
          </Row>
        );
      })}
      {items.length === 0 && <p className="quiet" style={{ padding: "12px 0", borderTop: "1px solid var(--hair)" }}>窗口内没有卡口事件。</p>}
    </div>
  );
}

/** Wide events table for full-width columns: 日期 · 来源/对象 · 事件 · 类别 · T+1 · 量比 · 时效 */
export function EventsWide({ items, who = "source", onPick, hotId }: { items: MarketEvent[]; who?: "source" | "subject"; onPick?: (e: MarketEvent) => void; hotId?: string | null }) {
  return (
    <div className="rows">
      <div className="row ev-wide is-head" style={{ padding: "6px 0" }}>
        <span className="row-meta">日期</span><span className="row-meta">{who === "source" ? "来源" : "对象"}</span><span className="row-meta">事件</span>
        <span className="row-meta">类别</span><span className="row-meta">T+1</span><span className="row-meta">量比</span><span className="row-meta">时效</span>
      </div>
      {items.map((e) => {
        const s = subjectOf(e);
        return (
          <div key={e.id} className={`row ev-wide${hotId === e.id ? " is-hot-row" : ""}`} onClick={onPick ? () => onPick(e) : undefined} style={onPick ? { cursor: "pointer" } : undefined}>
            <span className="row-meta">{md(e.date)}</span>
            {who === "source" ? <span className="row-meta">{e.source_label}</span> : <span style={{ fontSize: 13 }}>{s.to ? <Link to={s.to}>{s.label}</Link> : s.label}</span>}
            <span className="ev-title">{e.source_url ? <a href={e.source_url} target="_blank" rel="noreferrer" style={{ color: "inherit" }}>{e.title}</a> : e.title}</span>
            <span className="ev-cat">{e.category_label}</span>
            <Sig v={e.reaction.t1} size={13} />
            <span className="row-meta" style={{ color: "var(--ink-2)" }}>{e.volume_ratio != null ? e.volume_ratio.toFixed(1) : "—"}</span>
            <Fresh f={e.freshness} />
          </div>
        );
      })}
      {items.length === 0 && <p className="quiet" style={{ padding: "12px 0", borderTop: "1px solid var(--hair)" }}>窗口内没有卡口事件。</p>}
    </div>
  );
}

/* --------------------------------------------------------------- thesis block */
export function ThesisBlock({ t, subject, onChange, compact }: { t: Thesis | null; subject: string; onChange?: (t: Thesis) => void; compact?: boolean }) {
  const [q, setQ] = useState("");
  const [adding, setAdding] = useState(false);
  if (!t) {
    return (
      <div className="block">
        <Head title="我的判断" right={<Link to={`/judgement/${subject}`} className="btn">写判断</Link>} />
        <p className="quiet" style={{ padding: "12px 0", borderTop: "1px solid var(--hair)" }}>还没有判断。先选方向,再写一句可被证伪的话。</p>
      </div>
    );
  }
  const inherited = t.subject !== subject;
  const add = async () => {
    if (!q.trim()) return;
    const next = await mkt.addQuestion(t.subject, q.trim());
    setQ(""); setAdding(false); onChange?.(next);
  };
  const verify = async (index: number, status: "open" | "verified") => onChange?.(await mkt.setQuestion(t.subject, index, status));
  return (
    <div className="block">
      <Head
        title={<>我的判断 · 更新于 {md(t.updated)}{inherited && <span style={{ marginLeft: 8 }}>· 继承自 {t.title}</span>}</>}
        right={<><AsOf date={t.as_of} horizon={t.window_until ? `至 ${quarter(t.window_until)}` : null} /><Link to={`/judgement/${t.subject}`} className="btn">编辑</Link><Link to={`/judgement/${t.subject}?review=1`} className="btn">回顾</Link></>}
      />
      <Conclusion c={t.conclusion} />
      {!compact && <Prose text={t.body} className="prose" />}
      <div className="rows">
        <div className="row kv-row"><span className="row-meta">方向</span><span className="row-text" style={{ color: "var(--ink)", fontSize: 14 }}>{t.stance || "—"}</span></div>
        <div className="row kv-row"><span className="row-meta">窗口</span><span className="row-text" style={{ color: "var(--ink)", fontSize: 14 }}>{t.window_label ?? t.window_until ?? "—"},到期自动回顾;中途每次卡口事件后重新记分</span></div>
        <div className="row kv-row"><span className="row-meta">验证指标</span><span className="row-text" style={{ color: "var(--ink)", fontSize: 14 }}><Prose text={t.indicators.join(" · ")} className="inline-p" /></span></div>
        <div className="row kv-row"><span className="row-meta">失效条件</span><span className="row-text" style={{ color: "var(--ink)", fontSize: 14 }}>{t.invalidation.join(",") || "—"}</span></div>
      </div>
      <div className="rows" style={{ marginTop: 8 }}>
        {t.questions.map((qq) => (
          <div key={qq.index} className="row q-row">
            <span className="row-index">Q{qq.index}</span>
            <span className="row-text" style={{ textDecoration: qq.status === "verified" ? "line-through" : undefined, color: qq.status === "verified" ? "var(--muted)" : undefined }}>{qq.text}</span>
            <button type="button" className="row-meta" style={{ textAlign: "left" }} onClick={() => verify(qq.index, qq.status === "open" ? "verified" : "open")} title="点击切换 待验证 / 已验证">
              {qq.status === "open" ? "待验证" : "已验证"}
            </button>
            <span className="row-meta">{md(qq.date)}</span>
          </div>
        ))}
        <div style={{ borderTop: "1px solid var(--hair)", padding: "10px 0" }}>
          {adding ? (
            <span style={{ display: "flex", gap: 14, alignItems: "baseline" }}>
              <input autoFocus value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") add(); if (e.key === "Escape") setAdding(false); }}
                placeholder="一个能被查证的问题" style={{ flex: 1, font: "inherit", fontSize: 14, color: "var(--ink)", background: "transparent", border: 0, borderBottom: "1px solid var(--hair-2)", outline: "none", paddingBottom: 4 }} />
              <button type="button" className="btn" onClick={add}>加入</button>
              <button type="button" className="btn-quiet" onClick={() => setAdding(false)}>取消</button>
            </span>
          ) : (
            <button type="button" className="btn" onClick={() => setAdding(true)}>+ 新问题</button>
          )}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------ resonance block */
export function ResonanceBlock({ r, onSwitch, canSwitch }: { r: Resonance; onSwitch?: () => void; canSwitch?: boolean }) {
  const ev = r.event;
  const peers = r.peers.map((p) => <span key={p.company.id}>{p.company.short_name ?? p.company.name} <Sig v={p.t1} /></span>);
  return (
    <div className="block" style={{ gap: 12 }}>
      <Head title={`共振 · ${md(ev.date)} ${ev.category_label}`} right={<><AsOf date={r.as_of} horizon="事件后 T+1 / T+3" extra={`时效 T+${ev.freshness.validity}`} />{canSwitch && <button type="button" className="btn" onClick={onSwitch}>换一个事件</button>}</>} />
      <Conclusion c={r.conclusion} />
      <div className="rows">
        <Row k="本公司">T+1 <Sig v={r.self.t1} /> · T+3 <Sig v={r.self.t3} /> · 量比 {r.self.volume_ratio?.toFixed(1) ?? "—"}{r.self.turnover_pct_rank != null && <> · 换手分位 {Math.round(r.self.turnover_pct_rank)}%</>}</Row>
        <Row k="同环节">{peers.length ? peers.reduce<ReactNode[]>((acc, x, i) => (i ? [...acc, " · ", x] : [x]), [])
          : "没有同环节公司"} → {r.same_direction.k}/{r.same_direction.n} 同向{r.basket_t1 != null && <>,{r.layer?.name}篮子 T+1 相对整机 <Sig v={r.basket_t1} /></>}</Row>
        <Row k="相邻层">{r.adjacent.map((a, i) => <span key={a.node.id}>{i ? " · " : ""}{a.relation} {a.node.name} 篮子 {a.t1 == null ? "—" : Math.abs(a.t1) < 0.005 ? "无反应" : <Sig v={a.t1} />}</span>)}</Row>
        {r.attention && (
          <Row k="资金与关注">
            {r.attention.margin_change_3d_pct != null && <>融资余额 <Sig v={r.attention.margin_change_3d_pct / 100} />(3 日)· </>}
            {r.attention.irm_questions_7d != null && <>互动易提问 +{r.attention.irm_questions_7d} 条 · </>}
            龙虎榜:{r.attention.dragon_tiger ?? "无"} · 北向:{r.attention.northbound ?? "不披露"}
          </Row>
        )}
        {r.baseline && (
          <Row k="历史基线">该公司近 1 年 {r.baseline.n} 次“{ev.category_label}”事件,T+1 平均超额 <Sig v={r.baseline.avg_t1} />,命中率 {r.baseline.hits}/{r.baseline.n};本次{r.baseline.above ? "高于" : "低于"}基线</Row>
        )}
      </div>
    </div>
  );
}

function Row({ k, children }: { k: string; children: ReactNode }) {
  return (
    <div className="row kv-row">
      <span className="row-meta">{k}</span>
      <span className="inline">{children}</span>
    </div>
  );
}

/* ------------------------------------------------------------ crowding readings */
export function CrowdingReadings({ metrics, directions, kind }: { metrics: Record<string, any>; directions: Record<string, any>; kind: "company" | "basket" }) {
  const m = metrics, d = directions;
  return (
    <div className="readings">
      {m.ret20_pct_rank != null && <Reading label="20日涨幅分位" d={d.ret20_pct_rank}>{Math.round(m.ret20_pct_rank)}%</Reading>}
      {kind === "basket" && m.turnover_share_pct != null && <Reading label="成交额占整机" d={d.turnover_share_pct}>{Math.round(m.turnover_share_pct)}%{m.turnover_share_mean_pct != null && <span className="row-meta" style={{ marginLeft: 6 }}>(均值 {Math.round(m.turnover_share_mean_pct)}%)</span>}</Reading>}
      {m.turnover_pct_rank != null && <Reading label="换手率分位" d={d.turnover_pct_rank}>{Math.round(m.turnover_pct_rank)}%</Reading>}
      {m.margin_to_float_pct != null && <Reading label="融资余额/流通市值" d={d.margin_to_float_pct}>{m.margin_to_float_pct.toFixed(1)}%</Reading>}
      {m.holders_change_pct != null && <Reading label="股东户数">{m.holders_change_pct < 0 ? "↓" : "↑"} {Math.abs(m.holders_change_pct).toFixed(1)}% {m.holders_change_pct < 0 ? "集中" : "分散"}</Reading>}
      {m.deviation_sigma != null && <Reading label={kind === "basket" ? "相对整机偏离" : "相对篮子偏离"} d={d.deviation_sigma}>{sigma(m.deviation_sigma)}</Reading>}
    </div>
  );
}

export const CROWD_RULE = "读数着色规则:高于 80 分位或 +1.5σ 视为脆弱(偏空),低于 20 分位视为出清(偏多),其余中性。阈值可调。";

export function DirLegend() {
  return (
    <p className="rule-note">
      <Dir d="pos" /> 对资金方向是正向 · <Dir d="neg" /> 负向 · <Dir d="neu" /> 中性或状态量。A 股习惯:红涨绿跌;顶栏 ▲▼ 可切换为绿涨红跌。颜色只用在数字、方向标记和结论行,正文保持墨色。
    </p>
  );
}

export { pct };
