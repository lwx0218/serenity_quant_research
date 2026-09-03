import { useEffect, useState } from "react";
import { LineChart } from "../components/LineChart";
import { CROWD_RULE, CrowdingReadings } from "../components/Research";
import { Footer, Shell } from "../components/Shell";
import { AsOf, Conclusion, Head, Sig } from "../components/Signal";
import { EVIDENCE_LABEL, market, md, mkt, pad2, type Basket } from "../lib/api";
import { Link, useRouter } from "../lib/router";
import "./companies.css";
import "./research.css";

/**
 * A layer's basket: how capital treats the whole segment, how effective its
 * events are (and for how long), how crowded it is, and who is in it.
 */
export function BasketPage({ nodeId }: { nodeId: string }) {
  const { navigate } = useRouter();
  const [b, setB] = useState<Basket | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hot, setHot] = useState<string | null>(null);

  useEffect(() => {
    setB(null);
    mkt.basket(nodeId).then(setB).catch((e) => setError(String(e)));
  }, [nodeId]);

  const crumbs = [{ label: "公司", to: "/companies" }, { label: b?.node.name ?? "…", to: `/explore/${nodeId}` }, { label: "篮子" }];

  return (
    <Shell crumbs={crumbs} footer={<Footer note={b?.sample ? "行情、反应与拥挤读数为样式示例;接入免费行情源(A 股:腾讯/新浪/东财;美股:Yahoo)后替换。" : "篮子为等权、每日再平衡;跨市场成分按各自本币指数化。"} />}>
      <main className="page">
        {error && <p className="quiet" style={{ paddingTop: 40 }}>加载失败:{error}</p>}
        {!b && !error && <p className="quiet" style={{ paddingTop: 40 }}>加载中…</p>}
        {b && (
          <div className="stack-44" style={{ paddingBottom: 40 }}>
            <header className="basket-head">
              <span className="eyebrow">Basket · {pad2(b.node.sort)} / 09 · {b.node.name}</span>
              <h1 className="h1">{b.node.name}篮子</h1>
              <Conclusion c={b.conclusion} lead />
              <p className="body" style={{ maxWidth: 820, fontSize: 15 }}>
                这一环节的 <span className="mono">{b.members.length}</span> 家公司等权组成一个篮子,与整机全部公司的篮子比较;卡口事件标在篮子曲线上。公司页看的是单一标的,这里看的是整个环节被资金对待的方式。
              </p>
            </header>

            <section className="block">
              <div className="head">
                <span className="legend">
                  <span><span className="swatch" />{b.node.name}篮子 · {b.members.length} 家 · 等权</span>
                  <span><span className="swatch is-ref" />整机篮子 · {b.product_members} 家 · 等权</span>
                </span>
                <AsOf date={b.as_of} horizon={`${b.window_months} 个月`} extra={`指数化 = 100 · 各自本币${b.sample ? " · 示例数据" : ""}`} />
              </div>
              <LineChart
                height={300}
                width={1280}
                series={[
                  { key: "b", label: `${b.node.name}篮子`, points: b.series.basket, kind: "subject" },
                  { key: "p", label: "整机篮子", points: b.series.product, kind: "reference" },
                ]}
                events={b.chart_events.slice(0, 6).map((e) => ({ id: e.id, date: e.date, label: e.category_label, value: e.value, hot: hot === e.id, onClick: () => setHot(e.id) }))}
              />
            </section>

            <div className="two-col">
              <section className="block">
                <Head title="事件效力 · 该环节" right={<AsOf date={b.as_of} horizon="滚动 90 天" extra="每周重算" />} />
                <Conclusion c={b.efficacy_conclusion} />
                <div className="rows">
                  {b.efficacy_rows.map((r) => (
                    <div key={r.key} className="row kv-row">
                      <span className="row-meta">{r.key}</span>
                      <span className="inline" style={{ color: r.key === "样本" || r.key === "命中率" ? "var(--ink)" : undefined }}>
                        {r.parts.length > 0
                          ? r.parts.map((p, i) => <span key={i}>{p[0]}{p[1] != null && <Sig v={p[1]} />}</span>)
                          : r.strong && r.text.includes(r.strong)
                            ? <>{r.text.split(r.strong)[0]}<span style={{ color: "var(--ink)", fontWeight: 500 }}>{r.strong}</span>{r.text.split(r.strong).slice(1).join(r.strong)}</>
                            : r.text}
                      </span>
                    </div>
                  ))}
                  {b.efficacy_rows.length === 0 && <p className="quiet" style={{ padding: "12px 0", borderTop: "1px solid var(--hair)" }}>过去 90 天没有足够的事件。</p>}
                </div>
              </section>

              <section className="block">
                <Head title="篮子拥挤度" right={<AsOf date={b.crowding?.as_of ?? b.as_of} horizon={`${b.crowding?.window_days ?? 20} 日`} extra="状态量,每日重算" />} />
                <Conclusion c={b.crowding_conclusion} />
                {b.crowding && <CrowdingReadings metrics={b.crowding.metrics} directions={b.crowding.directions} kind="basket" />}
                <div className="readings">
                  <span className="reading"><span className="row-meta">成分内分化</span><span className="reading-v">{b.member_dispersion.high} 高 {b.member_dispersion.mid} 中 {b.member_dispersion.low} 低</span></span>
                </div>
                <span className="rule-note">{CROWD_RULE}</span>
              </section>
            </div>

            <section className="rows">
              <div className="rows-head">
                <span className="eyebrow">成分 · {b.members.length} 家</span>
                <span className="small muted">等权 · 每日再平衡</span>
              </div>
              <div className="row mem-row" style={{ padding: "8px 0" }}>
                <span className="row-meta">公司</span><span className="row-meta">市场</span><span className="row-meta">3M</span><span className="row-meta">6M</span>
                <span className="row-meta">估值分位</span><span className="row-meta">拥挤</span><span className="row-meta">最近卡口事件 · T+1</span><span className="row-meta">证据级</span>
              </div>
              {b.members.map((m) => (
                <Link key={m.company.id} to={`/companies/${m.company.id}`} className="row mem-row">
                  <span className="row-title">{m.company.short_name ?? m.company.name}</span>
                  <span className="row-meta">{market(m.company)}</span>
                  <Sig v={m.ret_3m} size={14} />
                  <Sig v={m.ret_6m} size={14} />
                  <span style={{ fontSize: 14, color: "var(--ink-2)" }}>{m.pe_pct_rank_5y != null ? `${Math.round(m.pe_pct_rank_5y)}%` : "—"}</span>
                  <span className={`crowd-lvl is-${m.crowd_direction ?? "neu"}`}>{m.crowd_level ?? "—"}{m.crowd_pct != null && ` ${Math.round(m.crowd_pct)}%`}</span>
                  <span className="inline" style={{ fontSize: 13 }}>{m.last_event ? <>{md(m.last_event.date)} {m.last_event.category_label} <Sig v={m.last_event.t1} size={13} /></> : "—"}</span>
                  <span className="row-text" style={{ fontSize: 13 }}>{m.evidence_level ? EVIDENCE_LABEL[m.evidence_level] : "—"}</span>
                </Link>
              ))}
            </section>

            <div className="two-col" style={{ gridTemplateColumns: "minmax(0, 1.6fr) minmax(0, 1fr)" }}>
              <section className="rows">
                <div className="rows-head">
                  <span className="eyebrow">其他环节 · 3M · 拥挤</span>
                  <Link to="/" className="small">回到整机 →</Link>
                </div>
                {b.others.map((o) => (
                  <button key={o.node_id} type="button" className="row oth-row" onClick={() => navigate(`/baskets/${o.node_id}`)} style={{ textAlign: "left" }}>
                    <span className="row-index">{pad2(o.sort)}</span>
                    <span className="row-title" style={{ fontSize: 15 }}>{o.name}</span>
                    <Sig v={o.ret_3m} size={14} />
                    <span className={`crowd-lvl is-${o.crowd_direction ?? "neu"}`}>{o.crowd_level ?? "—"}{o.crowd_pct != null && ` ${Math.round(o.crowd_pct)}%`}</span>
                    <span className="row-text" style={{ fontSize: 13 }}>{o.members} 家{o.last_event ? <> · 最近 {md(o.last_event.date)} {o.last_event.category_label} · <Sig v={o.last_event.t1} size={13} /></> : " · —"}</span>
                  </button>
                ))}
              </section>
              <p className="rule-note" style={{ fontSize: 13, lineHeight: 1.7, paddingTop: 30 }}>
                篮子回答两个问题:这一环节作为整体相对整机在走强还是走弱、拐点是否和卡口事件对得上;以及资金给这个环节的事件投的是长票还是短票。跨市场成分按各自本币指数化;权重默认等权,可手动调整并记录理由。
              </p>
            </div>
          </div>
        )}
      </main>
    </Shell>
  );
}
