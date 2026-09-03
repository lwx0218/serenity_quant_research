import { useCallback, useEffect, useState } from "react";
import { LineChart } from "../components/LineChart";
import { Backlinks, CROWD_RULE, CrowdingReadings, DirLegend, EventsWide, ResonanceBlock, ThesisBlock } from "../components/Research";
import { Footer, Shell, invalidatePending } from "../components/Shell";
import { AsOf, Conclusion, Head, Sig } from "../components/Signal";
import { api, EVIDENCE_LABEL, market, md, mkt, pct, roleLabel, type CompanyDetail, type CompanyMarket, type Resonance, type Thesis } from "../lib/api";
import { Link } from "../lib/router";
import "./companies.css";
import "./research.css";

const LAYER_LABEL: Record<string, string> = {
  global_anchor: "全球锚点",
  a_share_focus: "A 股重点",
  reference: "行业图示收录",
};

/**
 * One company: price with its events, crowding (state), events (30 天),
 * the resonance of one event, the judgement, and where it sits in the chain.
 */
export function CompanyPage({ id }: { id: string }) {
  const [c, setC] = useState<CompanyDetail | null>(null);
  const [m, setM] = useState<CompanyMarket | null>(null);
  const [res, setRes] = useState<Resonance | null>(null);
  const [resId, setResId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback((live: { on: boolean } = { on: true }) => {
    setError(null);
    api.company(id).then((x) => { if (live.on) setC(x); }).catch((e) => { if (live.on) setError(String(e)); });
    mkt.companyMarket(id).then((x) => { if (live.on) setM(x); }).catch(() => { if (live.on) setM(null); });
  }, [id]);

  useEffect(() => {
    const live = { on: true };
    setC(null); setM(null); setRes(null); setResId(null);
    load(live);
    return () => { live.on = false; };
  }, [load]);

  // resonance defaults to the most recent event that reacted
  useEffect(() => {
    if (!m) return;
    const pick = resId ?? (m.events_30d.find((e) => e.freshness.state === "window" || e.freshness.state === "priced") ?? m.events_30d[0])?.id ?? null;
    if (!pick) { setRes(null); return; }
    let live = true;
    mkt.resonance(pick).then((r) => { if (live) setRes(r); }).catch(() => setRes(null));
    return () => { live = false; };
  }, [m, resId]);

  const onThesis = (t: Thesis) => setM((prev) => (prev ? { ...prev, thesis: t } : prev));
  const nextEvent = () => {
    if (!m || m.events_30d.length < 2) return;
    const ids = m.events_30d.map((e) => e.id);
    const i = ids.indexOf(res?.event.id ?? "");
    setResId(ids[(i + 1) % ids.length]);
  };
  const verify = async (action: string, eventId?: string | null, exposureId?: number | null) => {
    await mkt.verify({ action, event_id: eventId ?? null, exposure_id: exposureId ?? null });
    invalidatePending();
    load();
  };

  const crumbs = [{ label: "公司", to: "/companies" }, { label: c?.short_name ?? c?.name ?? "…" }];
  const layer = m?.primary_layer ?? null;

  return (
    <Shell crumbs={crumbs} footer={<Footer note={m?.sample ? "价格、估值、反应与拥挤读数为样式示例;每条事件保留原文链接。" : "每条事件保留原文链接;反应按 T+N 收盘计算。"} />}>
      <main className="page">
        {error && <p className="quiet" style={{ paddingTop: 40 }}>加载失败:{error}</p>}
        {!c && !error && <p className="quiet" style={{ paddingTop: 40 }}>加载中…</p>}
        {c && (
          <div className="cpage">
            <div className="cpage-main">
              <header className="co-head" style={{ paddingTop: 0 }}>
                <span className="eyebrow">{market(c) || "Private"}</span>
                <h1 className="h1">{c.short_name ?? c.name}</h1>
                <span className="focus-sub">
                  {c.name}{c.exposures.length > 0 && <> · {Array.from(new Set(c.exposures.map((e) => e.chain_name))).join(" / ")}</>}
                  {layer && <> · <Link to={`/baskets/${layer.id}`}>{layer.name}篮子 →</Link></>}
                </span>
                {m ? <Conclusion c={m.headline} lead /> : c.exposures.length === 0 && <p className="lead">尚未关联到任何产业链环节。</p>}
              </header>

              {m && m.series.length > 0 && (
                <section className="block">
                  <Head title={`价格 · ${m.window_months} 个月 · 指数化 = 100`} right={<AsOf date={m.as_of} extra={`圆点为卡口事件,点开看共振${m.sample ? " · 示例数据" : ""}`} />} />
                  <LineChart
                    height={260}
                    series={[{ key: "co", label: c.short_name ?? c.name, points: m.series, kind: "subject" }]}
                    events={m.chart_events.map((e) => ({ id: e.id, date: e.date, label: e.category_label, value: e.value, hot: res?.event.id === e.id, onClick: () => setResId(e.id) }))}
                  />
                  <div className="price-meta">
                    {m.metrics.pe_ttm != null && <span><span className="row-meta">PE TTM</span>{m.metrics.pe_ttm.toFixed(1)}</span>}
                    {m.metrics.pe_pct_rank_5y != null && <span><span className="row-meta">5 年分位</span>{Math.round(m.metrics.pe_pct_rank_5y)}%</span>}
                    <span><span className="row-meta">3M</span><Sig v={m.metrics.ret_3m} size={13} /></span>
                    {m.metrics.excess_basket_3m != null && <span><span className="row-meta">相对篮子</span><Sig v={m.metrics.excess_basket_3m} size={13} /></span>}
                    <span><span className="row-meta">相对整机</span><Sig v={m.metrics.excess_product_3m} size={13} /></span>
                  </div>
                </section>
              )}

              {m?.crowding && (
                <section className="block">
                  <Head title="拥挤度 · 脆弱性" right={<AsOf date={m.crowding.as_of} horizon={`${m.crowding.window_days} 日`} extra="状态量,每日重算,不是信号" />} />
                  <Conclusion c={m.crowding_conclusion} />
                  <CrowdingReadings metrics={m.crowding.metrics} directions={m.crowding.directions} kind="company" />
                  <span className="rule-note">{CROWD_RULE}</span>
                </section>
              )}

              {m && (
                <section className="block">
                  <Head title={`卡口事件 · 30 天 · ${m.events_30d.length} 条`} right={<><AsOf date={m.as_of} horizon="T+1 相对篮子" extra={res ? `时效 T+${res.event.freshness.validity}` : null} /><Link to={`/research?company=${encodeURIComponent(id)}`} className="btn">全部公告与新闻 →</Link></>} />
                  <Conclusion c={m.events_conclusion} />
                  <EventsWide items={m.events_30d} who="source" onPick={(e) => setResId(e.id)} hotId={res?.event.id ?? null} />
                </section>
              )}

              {res && <ResonanceBlock r={res} onSwitch={nextEvent} canSwitch={(m?.events_30d.length ?? 0) > 1} />}

              <ThesisBlock t={m?.thesis ?? null} subject={id} onChange={onThesis} />

              <section className="rows">
                <div className="rows-head">
                  <span className="eyebrow">在产业链中的位置 · {c.exposures.length}</span>
                </div>
                {c.exposures.map((e) => (
                  <div key={e.id} className="row pos-row">
                    <span className="row-title">
                      <Link to={`/companies?chain=${encodeURIComponent(e.chain_node_id)}`} style={{ color: "inherit" }}>{e.chain_name}</Link>
                      {e.node_name && <span style={{ display: "block", fontSize: 12, color: "var(--muted)", fontWeight: 400 }}>{e.node_name}</span>}
                    </span>
                    <span className="row-text">{EVIDENCE_LABEL[e.evidence_level]}{e.role && e.role !== "代表企业" ? ` · ${roleLabel(e.role)}` : ""}</span>
                    <span className="row-note" style={{ fontSize: 13, color: "var(--ink-2)", lineHeight: 1.5 }}>
                      {e.note ?? (e.evidence_level === "reference" ? "公开行业图示将其列为该环节代表企业。" : "")}
                      {e.source_title && (
                        <span style={{ display: "block", fontSize: 12, color: "var(--muted)", marginTop: 4 }}>
                          来源:{e.source_publisher ? `${e.source_publisher} · ` : ""}
                          {e.source_url ? <a href={e.source_url} target="_blank" rel="noreferrer">{e.source_title}</a> : e.source_title}
                          {e.source_year_range ? ` · ${e.source_year_range}` : ""}
                        </span>
                      )}
                    </span>
                  </div>
                ))}
              </section>
            </div>

            <aside className="cpage-aside">
              <dl className="kv">
                <dt>市场</dt><dd>{market(c) || "非上市 / 未收录"}</dd>
                <dt>地区</dt><dd>{c.country_region ?? "—"}</dd>
                <dt>覆盖层</dt><dd>{c.universe_layer ? LAYER_LABEL[c.universe_layer] ?? c.universe_layer : "—"}</dd>
                {m && m.layers.length > 0 && (
                  <>
                    <dt>在整机中</dt>
                    <dd>{m.layers.map((l, i) => <span key={l.id}>{i > 0 && " · "}<Link to={`/explore/${l.id}`}>{String(l.sort).padStart(2, "0")} {l.name}</Link></span>)}</dd>
                  </>
                )}
                {m && (
                  <>
                    <dt>被引用</dt>
                    <dd><Backlinks items={m.backlinks} /></dd>
                  </>
                )}
                {c.official_url && (
                  <>
                    <dt>官网</dt>
                    <dd><a href={c.official_url} target="_blank" rel="noreferrer">{new URL(c.official_url).hostname}</a></dd>
                  </>
                )}
              </dl>

              {m && m.pending_verifications.length > 0 && (
                <div className="block">
                  <span className="eyebrow">待核验 · {m.pending_verifications.length}</span>
                  {m.pending_verifications.map((v, i) => (
                    <div key={i} className="verify-item">
                      <span style={{ fontSize: 14, color: "var(--ink)" }}>{v.chain_name}环节 · {EVIDENCE_LABEL[v.from_level as keyof typeof EVIDENCE_LABEL]} → {EVIDENCE_LABEL[v.to_level as keyof typeof EVIDENCE_LABEL]}</span>
                      <span className="row-text">{v.detail || v.text}</span>
                      <span className="actions">
                        {v.kind === "upgrade" ? (
                          <>
                            <button type="button" className="btn" onClick={() => verify("upgrade", v.event?.id, v.exposure_id)}>以此{v.event?.source_label ?? "来源"}升级为候选</button>
                            <button type="button" className="btn-quiet" onClick={() => verify("ignore", v.event?.id, v.exposure_id)}>忽略</button>
                          </>
                        ) : (
                          <>
                            <button type="button" className="btn" onClick={() => verify("accept", null, v.exposure_id)}>审核通过</button>
                            <button type="button" className="btn-quiet" onClick={() => verify("reject", null, v.exposure_id)}>驳回</button>
                          </>
                        )}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <div className="block">
                <span className="eyebrow">颜色怎么读</span>
                <DirLegend />
              </div>
              <p className="focus-note">
                证据级:<span className="ink">已核验</span> 有经人工审核的证据;<span className="ink">候选</span> 有来源但未审核;<span className="ink">行业图示</span> 仅见于公开产业链示意图。
              </p>
            </aside>
          </div>
        )}
      </main>
    </Shell>
  );
}

export { md, pct };
