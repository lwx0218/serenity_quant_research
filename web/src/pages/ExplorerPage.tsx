import { useEffect, useMemo, useState } from "react";
import { ExplodedStack, stackAnchors, type StackLayer } from "../components/ExplodedStack";
import { Shell, type Crumb } from "../components/Shell";
import { api, EVIDENCE_LABEL, market, pad2, statusLabel, type ModuleWithParts, type NodeDetail, type Product } from "../lib/api";
import { Link, useRouter } from "../lib/router";
import "./explorer.css";

const PRODUCT_ID = "cpo";

/* Layout constants (px, relative to .hero). Desktop-first; see design-rules.md. */
const OVERVIEW = { stackLeft: 220, stackTop: 230, labelX: 792, scale: 1 };
const FOCUSED = { stackLeft: 40, stackTop: 86, contentX: 740, scale: 0.92 };

export function ExplorerPage({ nodeId }: { nodeId?: string }) {
  const { navigate } = useRouter();
  const [product, setProduct] = useState<Product | null>(null);
  const [detail, setDetail] = useState<NodeDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hoverId, setHoverId] = useState<string | null>(null);

  useEffect(() => {
    api.product(PRODUCT_ID).then(setProduct).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (!nodeId) { setDetail(null); return; }
    let live = true;
    api.node(nodeId).then((d) => { if (live) setDetail(d); }).catch((e) => setError(String(e)));
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

  const crumbs: Crumb[] = [{ label: product?.name ?? "CPO 光模块", to: "/" }];
  if (detail && nodeId) {
    for (const a of detail.ancestors) if (a.kind !== "product") crumbs.push({ label: a.name, to: `/explore/${a.id}` });
    crumbs.push({ label: detail.node.name });
  } else if (nodeId && product) {
    const m = modules.find((x) => x.id === nodeId);
    if (m) crumbs.push({ label: m.name });
  }

  return (
    <Shell crumbs={crumbs}>
      <main className="page">
        {error && <p className="quiet" style={{ paddingTop: 40 }}>加载失败:{error}</p>}
        <section className={`hero${focused ? " is-selected" : ""}`}>
          {/* title (overview only) */}
          <div className="hero-title">
            <span className="eyebrow">{product?.eyebrow ?? ""}</span>
            <h1 className="display">{product?.name ?? ""}</h1>
            <p className="lead" style={{ maxWidth: 600 }}>{product?.summary ?? ""}</p>
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
                onBackgroundClick={() => focused && navigate("/")}
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
                return (
                  <g key={m.id} className={hoverId === m.id ? "is-hot" : undefined}>
                    <line x1={px} y1={py} x2={OVERVIEW.labelX - 20} y2={py} />
                    <circle cx={px} cy={py} r={3.5} />
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

          {/* layer index (overview) */}
          {modules.map((m, i) => {
            const a = anchors[m.id];
            if (!a) return null;
            const py = OVERVIEW.stackTop + a.y;
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
                <span className="row-index">{pad2(i + 1)}</span>
                <span className="layer-label-body">
                  <span className="layer-label-head">
                    <span className="layer-label-name">{m.name}</span>
                    <span className="layer-label-en">{m.name_en}</span>
                  </span>
                  <span className="layer-label-fn">{m.summary}</span>
                </span>
              </button>
            );
          })}

          {/* focused content */}
          {focused && (
            <Focus key={nodeId} nodeId={nodeId!} detail={detail} modules={modules} />
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
            <footer className="footer">
              <p style={{ maxWidth: 720 }}>{product.source_note}</p>
              <span className="mono" style={{ fontSize: 11, letterSpacing: "0.1em", color: "var(--faint)" }}>
                SERENITY · CPO EXPLORER
              </span>
            </footer>
          </>
        )}
      </main>
    </Shell>
  );
}

/* ------------------------------------------------------------------ focus column */
function Focus({ nodeId, detail, modules }: { nodeId: string; detail: NodeDetail | null; modules: ModuleWithParts[] }) {
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

  return (
    <div className="focus">
      <div className="focus-head">
        <span className="eyebrow is-accent">{eyebrow}</span>
        <h1 className="h1">{node.name}</h1>
        {isModule ? (
          <span className="focus-sub">{node.name_en}{chainNames.length > 0 && ` · ${chainNames.join(" / ")}`}</span>
        ) : (
          <div className="focus-tags">
            {st && <span>{st}</span>}
            {detail?.technologies.map((t) => <span key={t.id}>{t.name}</span>)}
            {chainNames.length > 0 && <span>产业链 · {chainNames.join(" / ")}</span>}
          </div>
        )}
        <p className="body">{node.description ?? node.summary}</p>
      </div>

      {isModule ? (
        <div className="rows">
          <div className="rows-head">
            <span className="eyebrow">PARTS · {detail?.children.length ?? fallbackModule?.children.length ?? 0}</span>
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
          <span className="eyebrow">COMPANIES{chainNames.length > 0 && ` · ${chainNames.join(" / ")}`}</span>
          {companies.length > 0 && <Link to={companiesTo} className="small">查看该环节全部公司 →</Link>}
        </div>
        {companies.length === 0 && <p className="quiet" style={{ padding: "12px 0", borderTop: "1px solid var(--hair)" }}>这一环节暂无已整理的公司。</p>}
        {companies.map((c) => (
          <Link key={c.id} to={`/companies/${c.id}`} className="row co-row">
            <span className="row-title">{c.short_name ?? c.name}</span>
            <span className="row-meta">{market(c)}</span>
            <span className="row-text">{c.evidence_level ? EVIDENCE_LABEL[c.evidence_level] : ""}</span>
          </Link>
        ))}
      </div>

      <p className="focus-note">
        代表企业来自公开行业图示,示意性;进入公司页可查看证据级与来源。
      </p>
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
