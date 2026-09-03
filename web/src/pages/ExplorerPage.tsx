import { useCallback, useEffect, useMemo, useState } from "react";
import { ExplodedStack, stackAnchors, type StackLayer } from "../components/ExplodedStack";
import { Backlinks, EventsNarrow, ThesisBlock } from "../components/Research";
import { Footer, Shell, type Crumb } from "../components/Shell";
import { AsOf, Conclusion, Fresh, Head, Sig } from "../components/Signal";
import { api, EVIDENCE_LABEL, market, md, mkt, pad2, pct, statusLabel, type ModuleWithParts, type NodeDetail, type NodeMarket, type Overview, type Product, type Thesis } from "../lib/api";
import { Link, useRouter } from "../lib/router";
import "./explorer.css";

const PRODUCT_ID = "cpo";
const WINDOW_DAYS = 7;

/* Layout constants (px, relative to .hero). Desktop-first; see design-rules.md. */
const OVERVIEW = { stackLeft: 220, stackTop: 400, labelX: 792, scale: 1 };
const FOCUSED = { stackLeft: 40, stackTop: 86, contentX: 740, scale: 0.92 };

export function ExplorerPage({ nodeId }: { nodeId?: string }) {
  const { navigate } = useRouter();
  const [product, setProduct] = useState<Product | null>(null);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [detail, setDetail] = useState<NodeDetail | null>(null);
  const [nm, setNm] = useState<NodeMarket | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hoverId, setHoverId] = useState<string | null>(null);

  useEffect(() => {
    api.product(PRODUCT_ID).then(setProduct).catch((e) => setError(String(e)));
    mkt.overview(PRODUCT_ID, WINDOW_DAYS).then(setOverview).catch(() => setOverview(null));
  }, []);

  useEffect(() => {
    if (!nodeId) { setDetail(null); setNm(null); return; }
    let live = true;
    api.node(nodeId).then((d) => { if (live) setDetail(d); }).catch((e) => setError(String(e)));
    mkt.nodeMarket(nodeId, WINDOW_DAYS).then((m) => { if (live) setNm(m); }).catch(() => { if (live) setNm(null); });
    return () => { live = false; };
  }, [nodeId]);

  // Esc returns to the whole device
  useEffect(() => {
    if (!nodeId) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") navigate("/"); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [nodeId, navigate]);

  const modules = product?.children ?? [];
  const layers: StackLayer[] = useMemo(
    () => modules.map((m) => ({ id: m.id, visual: m.visual, label: m.visual === "board-die" ? "ASIC" : undefined })),
    [modules],
  );
  const activity = useMemo(() => Object.fromEntries((overview?.layers ?? []).map((l) => [l.node_id, l])), [overview]);

  // Which module is highlighted in the stack: the node itself (module) or its parent (part)
  const selectedModuleId = useMemo(() => {
    if (!nodeId || !product) return null;
    if (modules.some((m) => m.id === nodeId)) return nodeId;
    const parent = modules.find((m) => m.children.some((p) => p.id === nodeId));
    return parent?.id ?? null;
  }, [nodeId, product, modules]);

  const focused = Boolean(nodeId);
  const anchors = stackAnchors(layers, selectedModuleId);
  const pos = focused ? FOCUSED : OVERVIEW;

  const crumbs: Crumb[] = focusedCrumbs(Boolean(nodeId), product?.name);
  if (detail && nodeId) {
    for (const a of detail.ancestors) if (a.kind !== "product") crumbs.push({ label: a.name, to: `/explore/${a.id}` });
    crumbs.push({ label: detail.node.name });
  } else if (nodeId && product) {
    const m = modules.find((x) => x.id === nodeId);
    if (m) crumbs.push({ label: m.name });
  }

  const onThesis = useCallback((t: Thesis) => setNm((prev) => (prev ? { ...prev, thesis: t } : prev)), []);

  return (
    <Shell crumbs={crumbs} footer={<Footer note={<>{product?.source_note}{overview?.sample && " 事件、反应与读数为样式示例。"}</>} />}>
      <main
        className="page"
        style={focused ? { minHeight: "calc(100vh - 64px)" } : undefined}
        onClick={(e) => {
          // In the selected state any click on the page background (not a layer, link,
          // button, input or the content column) returns to the whole device.
          if (!focused) return;
          const t = e.target as HTMLElement;
          if (t.closest("a, button, input, textarea, [data-layer], .focus, .hint")) return;
          navigate("/");
        }}
      >
        {error && <p className="quiet" style={{ paddingTop: 40 }}>加载失败:{error}</p>}
        <section className={`hero${focused ? " is-selected" : ""}`}>
          {/* title + what changed (overview only) */}
          <div className="hero-title">
            <span className="eyebrow">{product?.eyebrow ?? ""}</span>
            <h1 className="display">{product?.name ?? ""}</h1>
            <p className="lead" style={{ maxWidth: 600 }}>{product?.summary ?? ""}</p>
            {overview && <WhatChanged o={overview} />}
          </div>

          {/* the device */}
          <div className="hero-stack" style={{ left: pos.stackLeft, top: pos.stackTop }}>
            {layers.length > 0 && (
              <ExplodedStack
                layers={layers}
                selectedId={selectedModuleId}
                hoverId={hoverId}
                onSelect={(id) => navigate(`/explore/${id}`)}
                onHover={setHoverId}
                transform={focused ? `scale(${FOCUSED.scale})` : undefined}
              />
            )}
          </div>

          {/* leader lines */}
          <svg className="hero-leaders" aria-hidden="true">
            {!focused &&
              modules.map((m) => {
                const a = anchors[m.id];
                if (!a) return null;
                const px = OVERVIEW.stackLeft + a.x, py = OVERVIEW.stackTop + a.y;
                const act = activity[m.id];
                return (
                  <g key={m.id} className={hoverId === m.id ? "is-hot" : undefined}>
                    <line x1={px} y1={py} x2={OVERVIEW.labelX - 20} y2={py} />
                    {!act?.direction && <circle cx={px} cy={py} r={3.5} />}
                  </g>
                );
              })}
            {focused && selectedModuleId && anchors[selectedModuleId] && (() => {
              const a = anchors[selectedModuleId];
              const px = FOCUSED.stackLeft + a.x * FOCUSED.scale, py = FOCUSED.stackTop + a.y * FOCUSED.scale;
              const kx = FOCUSED.contentX - 30, ky = 32 + 8;
              return (
                <g className="leader-sel">
                  <path d={`M${px} ${py} H${kx} V${ky}`} />
                  <circle cx={px} cy={py} r={3.5} />
                  <circle cx={kx} cy={ky} r={2.5} />
                </g>
              );
            })()}
          </svg>

          {/* live dots: colour = the layer basket's direction this week */}
          {!focused &&
            modules.map((m) => {
              const a = anchors[m.id], act = activity[m.id];
              if (!a || !act?.direction) return null;
              const px = OVERVIEW.stackLeft + a.x, py = OVERVIEW.stackTop + a.y;
              return (
                <span key={m.id} style={{ display: "contents" }}>
                  <span className={`live-ring is-${act.direction}`} style={{ left: px - 3.5, top: py - 3.5 }} />
                  <span className={`live is-${act.direction}`} style={{ left: px - 3.5, top: py - 3.5 }} />
                </span>
              );
            })}

          {/* layer index (overview) */}
          {modules.map((m, i) => {
            const a = anchors[m.id];
            if (!a) return null;
            const py = OVERVIEW.stackTop + a.y;
            const act = activity[m.id];
            return (
              <button
                key={m.id}
                type="button"
                className={`layer-label${hoverId === m.id ? " is-hot" : ""}`}
                style={{ left: OVERVIEW.labelX, top: py - 12 }}
                onMouseEnter={() => setHoverId(m.id)}
                onMouseLeave={() => setHoverId(null)}
                onClick={() => navigate(`/explore/${m.id}`)}
                tabIndex={focused ? -1 : 0}
              >
                <span className={`row-index${act?.direction ? ` is-${act.direction}` : ""}`}>{pad2(i + 1)}</span>
                <span className="layer-label-body">
                  <span className="layer-label-head">
                    <span className="layer-label-name">{m.name}</span>
                    <span className="layer-label-en">{m.name_en}</span>
                    {act && (act.events > 0 || act.direction) && (
                      <span className="layer-label-act">
                        · {act.events > 0 ? `${act.events} 条事件` : "无事件"} · 篮子 {WINDOW_DAYS} 天 <Sig v={act.basket_excess} size={12} />
                      </span>
                    )}
                  </span>
                  <span className="layer-label-fn">{m.summary}</span>
                </span>
              </button>
            );
          })}

          {/* focused content */}
          {focused && (
            <Focus key={nodeId} nodeId={nodeId!} detail={detail} nm={nm} modules={modules} onThesis={onThesis} />
          )}
          {focused && (
            <div className="hint">
              <span className="kbd">ESC</span>
              <span>或点击空白处回到整机</span>
            </div>
          )}
        </section>

        {!focused && product && (
          <>
            <SignalPath product={product} />
            <ChainList product={product} />
          </>
        )}
      </main>
    </Shell>
  );
}

function focusedCrumbs(focused: boolean, name?: string): Crumb[] {
  return focused ? [{ label: name ?? "CPO 光模块", to: "/" }] : [];
}

/* ------------------------------------------------------------- what changed */
function WhatChanged({ o }: { o: Overview }) {
  const c = o.counts;
  return (
    <div className="changed">
      <Conclusion c={o.conclusion} lead />
      <div className="changed-meta">
        <AsOf date={o.as_of} horizon={`过去 ${o.window_days} 天`} extra="反应 = T+1 相对同环节其他公司" />
        <Link to="/research">{c.events} 条卡口事件</Link>
        <span className="faint">·</span>
        <span>已反应 <span className="ink">{c.reacted}</span> · 未反应 <span className="ink">{c.unreacted}</span>{c.pending > 0 && <> · 待收盘 <span className="ink">{c.pending}</span></>}</span>
        {c.verifications > 0 && <><span className="faint">·</span><Link to="/research">{c.verifications} 条待核验</Link></>}
        {c.theses_expiring > 0 && <><span className="faint">·</span><Link to="/research">{c.theses_expiring} 个判断到期</Link></>}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ focus column */
function Focus({ nodeId, detail, nm, modules, onThesis }: { nodeId: string; detail: NodeDetail | null; nm: NodeMarket | null; modules: ModuleWithParts[]; onThesis: (t: Thesis) => void }) {
  const moduleIndex = (id: string) => modules.findIndex((m) => m.id === id);
  const fallbackModule = modules.find((m) => m.id === nodeId);
  const node = detail?.node ?? fallbackModule ?? null;
  if (!node) return <div className="focus"><p className="quiet">加载中…</p></div>;

  const isModule = node.kind === "module";
  const parentModule = isModule ? null : modules.find((m) => m.children.some((p) => p.id === nodeId)) ?? null;
  const mi = isModule ? moduleIndex(node.id) : parentModule ? moduleIndex(parentModule.id) : -1;
  const partIndex = parentModule ? parentModule.children.findIndex((p) => p.id === nodeId) : -1;

  const eyebrow = isModule
    ? `${pad2(mi + 1)} / ${pad2(modules.length)} · ${node.code ?? ""}`
    : `${parentModule?.code ?? ""} · PART ${pad2(partIndex + 1)} / ${pad2(parentModule?.children.length ?? 0)}`;

  const chainNames = detail?.chain_nodes.map((c) => c.display_name ?? c.name) ?? [];
  const companies = detail?.companies ?? [];
  const companiesTo = `/companies?node=${encodeURIComponent(node.id)}`;
  const st = statusLabel(node.status);
  const basketId = nm?.module.id ?? parentModule?.id ?? node.id;

  return (
    <div className="focus">
      <div className="focus-head">
        <span className="eyebrow is-accent">{eyebrow}</span>
        <h1 className="h1">{node.name}</h1>
        {isModule ? (
          <span className="focus-sub">
            {node.name_en}{chainNames.length > 0 && ` · ${chainNames.join(" / ")}环节`}
            {nm?.basket.excess != null && <> · 篮子 {nm.window_days} 天 <Sig v={nm.basket.excess} size={14} /> · <Link to={`/baskets/${basketId}`}>篮子 →</Link></>}
          </span>
        ) : (
          <div className="focus-tags">
            {st && <span>{st}</span>}
            {detail?.technologies.map((t) => <span key={t.id}>{t.name}</span>)}
            {chainNames.length > 0 && <span>产业链 · {chainNames.join(" / ")}</span>}
          </div>
        )}
        <p className="body">{node.description ?? node.summary}</p>
      </div>

      {/* judgement */}
      <ThesisBlock t={nm?.thesis ?? null} subject={node.id} onChange={onThesis} />
      {nm && nm.backlinks.length > 0 && (
        <p className="rule-note" style={{ marginTop: -28 }}>被引用:<Backlinks items={nm.backlinks} /></p>
      )}

      {/* events */}
      {nm && (
        <div className="block">
          <Head title={`最近事件 · ${nm.window_days} 天 · ${nm.events.length} 条`} right={<AsOf date={nm.as_of} horizon="T+1 相对篮子" extra={`时效 = T+${nm.validity_days}`} />} />
          <Conclusion c={nm.events_conclusion} />
          <EventsNarrow items={nm.events} />
        </div>
      )}

      {isModule ? (
        <div className="rows">
          <div className="rows-head">
            <span className="eyebrow">部件 · {detail?.children.length ?? fallbackModule?.children.length ?? 0}</span>
            <span className="small muted">点击进入下一层</span>
          </div>
          {(detail?.children ?? fallbackModule?.children ?? []).map((p, i) => (
            <Link key={p.id} to={`/explore/${p.id}`} className="row parts-row">
              <span className="row-index">{pad2(i + 1)}</span>
              <span className="row-title">{p.name}</span>
              <span className="row-text">{p.summary}</span>
              <Chev />
            </Link>
          ))}
        </div>
      ) : (
        parentModule && (
          <div className="rows">
            <div className="rows-head">
              <span className="eyebrow">同属 {parentModule.name} · {parentModule.children.length}</span>
              <Link to={`/explore/${parentModule.id}`} className="small">回到 {parentModule.name} →</Link>
            </div>
            {parentModule.children.map((p, i) => (
              <Link key={p.id} to={`/explore/${p.id}`} className={`row sib-row${p.id === node.id ? " is-current-row" : ""}`}>
                <span className="row-index">{pad2(i + 1)}</span>
                <span className="row-title">{p.name}</span>
                {p.id !== node.id ? <Chev /> : <span />}
              </Link>
            ))}
          </div>
        )
      )}

      <div className="rows">
        <div className="rows-head">
          <span className="eyebrow">公司{chainNames.length > 0 && ` · ${chainNames.join(" / ")}`} · {companies.length} · 最近事件与 T+1</span>
          {companies.length > 0 && <Link to={companiesTo} className="small">全部公司 →</Link>}
        </div>
        {companies.length === 0 && <p className="quiet" style={{ padding: "12px 0", borderTop: "1px solid var(--hair)" }}>这一环节暂无已整理的公司。</p>}
        {companies.map((c) => {
          const le = nm?.company_events[c.id] ?? null;
          return (
            <Link key={c.id} to={`/companies/${c.id}`} className="row co-row">
              <span className="row-title">{c.short_name ?? c.name}</span>
              <span className="row-meta">{market(c)}</span>
              <span className="row-text" style={{ fontSize: 12 }}>{c.evidence_level ? EVIDENCE_LABEL[c.evidence_level] : ""}</span>
              {le ? <Sig v={le.t1} size={13} /> : <span className="row-meta">—</span>}
              <span style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <span className="row-meta" style={{ color: "var(--ink-2)", fontSize: 11 }}>{le ? `${md(le.date)} ${le.category_label}` : "无事件"}</span>
                {le && <Fresh f={le.freshness} />}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}


/* ------------------------------------------------------------------ signal path */
function SignalPath({ product }: { product: Product }) {
  const sp = product.signal_path;
  if (!sp) return null;
  return (
    <section className="section signal">
      <div className="section-head">
        <span className="eyebrow">Signal path</span>
        <h2 className="h2">信号怎么走</h2>
        <p className="body">{sp.summary}</p>
      </div>
      <div className="signal-steps">
        {sp.steps.map((s, i) => (
          <span key={i} style={{ display: "contents" }}>
            {i > 0 && (
              <svg className="signal-arrow" width="40" height="12" viewBox="0 0 40 12" fill="none" aria-hidden="true">
                <path d="M0 6h36M31 1l5 5-5 5" stroke="currentColor" strokeWidth="1.2" />
              </svg>
            )}
            {s.moduleId ? (
              <Link to={`/explore/${s.moduleId}`} className="signal-step">
                <span className="signal-step-label">{s.label}</span>
                <span className="signal-step-kind">{s.kind}</span>
              </Link>
            ) : (
              <span className="signal-step">
                <span className="signal-step-label">{s.label}</span>
                <span className="signal-step-kind">{s.kind}</span>
              </span>
            )}
          </span>
        ))}
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ chain list */
function ChainList({ product }: { product: Product }) {
  return (
    <section className="section">
      <div className="chain-head">
        <div className="section-head">
          <span className="eyebrow">Industry chain</span>
          <h2 className="h2">谁在造它</h2>
          <p className="body">十个环节,每个环节对应上面的一到两层。点击环节进入公司池。</p>
        </div>
        <Link to="/companies" style={{ fontSize: 14 }}>全部公司 →</Link>
      </div>
      <div className="rows">
        {product.chain.map((c, i) => (
          <Link key={c.id} to={`/companies?chain=${encodeURIComponent(c.id)}`} className="row chain-row">
            <span className="row-index">{pad2(i + 1)}</span>
            <span className="row-title">{c.display_name ?? c.name}</span>
            <span className="row-sub">{c.keywords}</span>
            <span className="row-who">{c.companies.map((x) => x.short_name ?? x.name).join(" · ")}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}

function Chev() {
  return (
    <svg className="row-chev" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
      <path d="M4.5 2.5 8 6l-3.5 3.5" />
    </svg>
  );
}

export { pct };
