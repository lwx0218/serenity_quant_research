import { forwardRef, useCallback, useEffect, useMemo, useRef, useState, type MouseEvent as RMouseEvent } from "react";
import { Footer, Shell } from "../components/Shell";
import { Head } from "../components/Signal";
import { api, type PhysDrawing, type PhysLink, type PhysObject, type PhysPart, type PhysStep } from "../lib/api";
import { Evidence } from "../components/Evidence";
import { Link, useRouter } from "../lib/router";
import "./physical.css";

const DEFAULT_OBJECT = "om.1p6t.osfp.dr8.siph";
const LEFT = 80;                       // page margin, matches --page-x
const OV = { top: 360, scale: 1 };     // drawing in the overview
const SEL = { top: 150, scale: 0.6 };  // drawing once a part is selected
const GRID_TOP = 1000;

/** The theme actually painted: explicit data-theme wins, else the OS. Follows the toggle live. */
function useEffectiveTheme(): "light" | "dark" {
  const read = () => {
    const t = document.documentElement.getAttribute("data-theme");
    if (t === "light" || t === "dark") return t;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };
  const [theme, setTheme] = useState<"light" | "dark">(read);
  useEffect(() => {
    const mo = new MutationObserver(() => setTheme(read()));
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const on = () => setTheme(read());
    mq.addEventListener("change", on);
    return () => { mo.disconnect(); mq.removeEventListener("change", on); };
  }, []);
  return theme;
}

export function short(name: string): string {
  return name.split("（")[0].split("(")[0];
}
export function mkt(m: string | null): string {
  if (!m) return "—";
  return m.startsWith("A") ? "A" : m.startsWith("US") ? "US" : m;
}
const aCount = (p: PhysPart) => p.companies.filter((c) => (c.market ?? "").startsWith("A")).length;

/**
 * 实物: one shipping object, opened. The drawing is the protagonist; nine
 * stations below it in signal order; click a part and it becomes the page.
 */
export function PhysicalPage({ id = DEFAULT_OBJECT, part = null }: { id?: string; part?: string | null }) {
  const { navigate } = useRouter();
  const theme = useEffectiveTheme();
  const [obj, setObj] = useState<PhysObject | null>(null);
  const [drawing, setDrawing] = useState<PhysDrawing | null>(null);
  const [svg, setSvg] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [dir, setDir] = useState<"tx" | "rx">("tx");
  const [hover, setHover] = useState<string | null>(null);
  const [settled, setSettled] = useState(true);   // false while the drawing is moving
  const selected = part;
  const stageRef = useRef<HTMLDivElement>(null);
  const companiesRef = useRef<HTMLDivElement>(null);
  const detailRef = useRef<HTMLDivElement>(null);
  const stationsRef = useRef<HTMLDivElement>(null);
  const [stageH, setStageH] = useState(1500);

  useEffect(() => {
    let live = true;
    setObj(null); setError(null);
    api.physicalObject(id).then((o) => { if (live) setObj(o); }).catch((e) => { if (live) setError(String(e)); });
    api.physicalDrawing(id).then((d) => { if (live) setDrawing(d); }).catch(() => { if (live) setDrawing(null); });
    return () => { live = false; };
  }, [id]);
  useEffect(() => {
    let live = true;
    api.physicalSvg(id, theme, dir).then((t) => { if (live) setSvg(t); }).catch(() => { if (live) setSvg(""); });
    return () => { live = false; };
  }, [id, theme, dir]);

  const parts = useMemo(() => Object.fromEntries((obj?.parts ?? []).map((p) => [p.id, p])), [obj]);
  const seq: PhysStep[] = useMemo(() => {
    if (!obj) return [];
    return dir === "rx" ? obj.signal.rx.slice().reverse() : obj.signal.tx;   // rx columns follow the board, right to left
  }, [obj, dir]);

  const select = useCallback((pid: string | null) => {
    const next = pid && pid !== selected ? pid : null;
    navigate(next ? `/physical/${encodeURIComponent(id)}?part=${encodeURIComponent(next)}` : `/physical/${encodeURIComponent(id)}`);
  }, [id, navigate, selected]);

  // drawing moves for 360ms; leaders are drawn only once it has settled
  useEffect(() => {
    setSettled(false);
    const t = setTimeout(() => setSettled(true), 380);
    return () => clearTimeout(t);
  }, [selected]);

  // Esc / blank click returns to the whole object
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape" && selected) select(null); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [selected, select]);

  // click / hover on the injected svg, by delegation
  const onStageClick = (e: RMouseEvent) => {
    const t = (e.target as Element).closest("[data-part],[data-station]") as HTMLElement | null;
    if (t) { e.stopPropagation(); select(t.dataset.part ?? t.dataset.station ?? null); return; }
    if ((e.target as Element).closest(".ph-detail,.ph-companies,.ph-legend")) return;
    if (selected) select(null);
  };
  const onStageMove = (e: RMouseEvent) => {
    const t = (e.target as Element).closest("[data-part],[data-station]") as HTMLElement | null;
    setHover(t ? (t.dataset.part ?? t.dataset.station ?? null) : null);
  };

  // stage height follows content
  useEffect(() => {
    const h = selected
      ? Math.max(540 + (companiesRef.current?.offsetHeight ?? 0), 96 + (detailRef.current?.offsetHeight ?? 0)) + 120
      : GRID_TOP + (stationsRef.current?.offsetHeight ?? 0) + 120;
    setStageH(Math.max(h, 900));
  }, [selected, obj, dir, seq]);

  // mark selected / hovered groups inside the svg (it is plain DOM, not React)
  useEffect(() => {
    const root = stageRef.current?.querySelector(".ph-drawing");
    if (!root) return;
    root.classList.toggle("is-sel", !!selected);
    root.querySelectorAll<HTMLElement>("g[data-part]").forEach((g) => {
      g.classList.toggle("on", g.dataset.part === selected);
      g.classList.toggle("hov", g.dataset.part === hover);
    });
    root.querySelectorAll<HTMLElement>("g[data-station]").forEach((g) => g.classList.toggle("hov", g.dataset.station === hover));
  }, [svg, selected, hover]);

  const sel = selected ? parts[selected] ?? null : null;
  const crumbs = [{ label: obj?.host?.platforms?.[0]?.name?.split(" ")[1] ?? "Quantum-X800" }, { label: obj?.name ?? "…", to: `/physical/${id}` }, ...(sel ? [{ label: short(sel.name) }] : [])];

  return (
    <Shell crumbs={crumbs} footer={<Footer note={`示意图按 OSFP224 DR8 硅光方案的通用结构摆放,不对应任何一家的具体设计 · 公司映射 ${obj?.parts.reduce((n, p) => n + p.companies.length, 0) ?? "…"} 条 · 证据级三档`} />}>
      <main className="page">
        {error && <p className="quiet" style={{ paddingTop: 40 }}>加载失败:{error}</p>}
        {!obj && !error && <p className="quiet" style={{ paddingTop: 40 }}>加载中…</p>}
        {obj && (
          <div ref={stageRef} className={`ph-stage${selected ? " is-sel" : ""}`} style={{ height: stageH }} onClick={onStageClick} onMouseMove={onStageMove} onMouseLeave={() => setHover(null)}>
            <div className="ph-hero ph-fade">
              <div className="ph-hero-title">
                <span className="eyebrow">{crumbs[0].label} · {obj.form_factor?.split("（")[0] ?? ""} · 1.6T DR8 · 硅光</span>
                <h1 className="display">{short(obj.name).replace(" OSFP DR8 硅光模块", " 光模块")}</h1>
                <p className="lead" style={{ maxWidth: 640 }}>一只正在出货的模块,揭开上盖。电信号从左边金手指进来,在硅光芯片上变成光,从右边 MPO 出去。沿这条线走一遍,每一站是一个部件,点任何一站,看它背后的公司。</p>
              </div>
              <div className="ph-readouts">
                <div className="readings">
                  <span className="reading"><span className="row-meta">通道</span><span className="reading-v" style={{ fontSize: 13 }}>{obj.spec.lanes?.split("（")[0]}</span></span>
                  <span className="reading"><span className="row-meta">波长</span><span className="reading-v" style={{ fontSize: 13 }}>{obj.spec.wavelength?.split("（")[0]} · {obj.spec.reach}</span></span>
                  <span className="reading"><span className="row-meta">功耗</span><span className="reading-v" style={{ fontSize: 13 }}>{obj.spec.power?.split("；")[0]}</span></span>
                </div>
                <div className="readings">
                  <span className="reading"><span className="row-meta">架构</span><span className="reading-v" style={{ fontSize: 13 }}>{obj.spec.architecture}</span></span>
                </div>
              </div>
            </div>

            <div className="ph-drawing" style={{ top: selected ? SEL.top : OV.top, transform: `scale(${selected ? SEL.scale : OV.scale})` }} dangerouslySetInnerHTML={{ __html: svg }} />

            {drawing && settled && (
              <svg className="ph-overlay" width="1440" height={stageH} viewBox={`0 0 1440 ${stageH}`}>
                {!selected && <Leaders seq={seq} drawing={drawing} hover={hover} />}
                {selected && drawing.anchors[selected] && <SelectedLeader anchor={drawing.anchors[selected]} />}
              </svg>
            )}

            <div className="ph-legend ph-fade" onClick={(e) => e.stopPropagation()}>
              <div className="ph-legend-cap"><span>{obj.host?.platforms?.[0]?.name ?? "主机"} · 前面板 OSFP 笼子</span><span>后方是交换机主板与交换 ASIC · 蒙层示意</span></div>
              <div className="ph-legend-row"><span className="row-meta">电信号<i /></span><span className="row-meta">光信号<i className="o" /></span></div>
              <div className="ph-legend-row ph-seg">
                <button type="button" className={dir === "tx" ? "on" : undefined} onClick={() => setDir("tx")}>发送 TX</button>
                <button type="button" className={dir === "rx" ? "on" : undefined} onClick={() => setDir("rx")}>接收 RX</button>
              </div>
            </div>

            <div className={`ph-stations-head ph-fade${selected ? " is-hidden" : ""}`}>
              <span className="eyebrow">{dir === "tx" ? "信号怎么走 · 发送 · 九站" : "信号怎么走 · 接收 · 七站 · 从右往左读"}</span>
            </div>
            <div ref={stationsRef} className={`ph-stations ph-fade${selected ? " is-hidden" : ""}`} style={{ gridTemplateColumns: `repeat(${seq.length || 9}, minmax(0, 1fr))` }}>
              {seq.map((s) => {
                const p = parts[s.partId];
                if (!p) return null;
                const optical = s.signal === "光" || s.partId === "part.pic" || s.partId === "part.pd";
                return (
                  <button key={s.partId} type="button" className={`ph-st${hover === s.partId ? " hov" : ""}`} data-part={s.partId}
                          onMouseEnter={() => setHover(s.partId)} onMouseLeave={() => setHover(null)}>
                    <span className={`row-meta${optical ? " is-opt" : ""}`} style={{ letterSpacing: "0.06em" }}>{String(s.step).padStart(2, "0")} · {s.signal}</span>
                    <span className="ph-st-name">{short(p.name)}</span>
                    <span className="ph-st-text">{s.text}</span>
                    <span className="row-meta" style={{ fontSize: 11, marginTop: 4 }}>{p.companies.length} 家 · {aCount(p)} 家 A 股</span>
                  </button>
                );
              })}
            </div>

            {sel && <PartDetail ref={detailRef} p={sel} step={obj.signal[dir].find((s) => s.partId === sel.id)?.step ?? null} total={obj.signal[dir].length} dir={dir} />}
            {sel && <PartCompanies ref={companiesRef} p={sel} stages={obj.stages} onBack={() => select(null)} />}
          </div>
        )}
      </main>
    </Shell>
  );
}

/* --------------------------------------------------------------- leaders */
function Leaders({ seq, drawing, hover }: { seq: PhysStep[]; drawing: PhysDrawing; hover: string | null }) {
  const n = seq.length; if (!n) return null;
  const colw = (1280 - (n - 1) * 20) / n;
  const rank = seq.map((s, i) => [drawing.anchors[s.partId]?.[0] ?? 0, i] as [number, number]).sort((a, b) => a[0] - b[0]).map((x) => x[1]);
  return (
    <>
      {seq.map((s, i) => {
        const a = drawing.anchors[s.partId]; if (!a) return null;
        const px = LEFT + a[0], py = OV.top + a[1];
        const cx = LEFT + i * (colw + 20) + 12, ym = 892 + rank.indexOf(i) * 6;
        const hot = hover === s.partId;
        return (
          <g key={s.partId} className={hot ? "is-hot" : undefined}>
            <path d={`M${px.toFixed(0)} ${(py + 12).toFixed(0)} V${ym} H${cx} V${GRID_TOP - 6}`} />
            <circle cx={cx} cy={GRID_TOP - 6} r={2.5} />
          </g>
        );
      })}
    </>
  );
}
function SelectedLeader({ anchor }: { anchor: [number, number] }) {
  const px = LEFT + anchor[0] * SEL.scale, py = SEL.top + anchor[1] * SEL.scale;
  const CX = 900, ky = 104;
  return (
    <g className="leader-sel">
      <path d={`M${px.toFixed(0)} ${py.toFixed(0)} V${SEL.top - 36} H${CX - 30} V${ky}`} />
      <circle cx={px} cy={py} r={3.5} /><circle cx={CX - 30} cy={ky} r={2.5} />
    </g>
  );
}

/* --------------------------------------------------------------- selected part */

const PartDetail = forwardRef<HTMLDivElement, { p: PhysPart; step: number | null; total: number; dir: "tx" | "rx" }>(function PartDetail({ p, step, total, dir }, ref) {
  return (
    <div ref={ref} className="ph-detail ph-fade">
      <div className="focus-head">
        <span className="eyebrow" style={{ color: "var(--accent)" }}>{step ? `${dir === "rx" ? "接收" : "发送"} ${String(step).padStart(2, "0")} / ${String(total).padStart(2, "0")}` : "部件 · 不在信号路径上"}</span>
        <h1 className="h1">{short(p.name)}</h1>
        <span className="focus-sub">{p.name_en}</span>
        <p className="body">{p.function}</p>
        <div className="readings">{p.key_specs.map((s, i) => <span key={i} className="reading"><span className="reading-v" style={{ fontSize: 13 }}>{s}</span></span>)}</div>
      </div>
      {p.materials.length > 0 && (
        <div className="rows">
          <div className="rows-head"><span className="eyebrow">上游材料 · {p.materials.length}</span></div>
          {p.materials.map((m, i) => (
            <div key={i} className="row" style={{ gridTemplateColumns: "28px minmax(0,1fr)", padding: "10px 0" }}><span className="row-meta">{String(i + 1).padStart(2, "0")}</span><span style={{ fontSize: 14 }}>{m}</span></div>
          ))}
          <div className="rows-end" />
        </div>
      )}
    </div>
  );
});

const PartCompanies = forwardRef<HTMLDivElement, { p: PhysPart; stages: PhysObject["stages"]; onBack: () => void }>(function PartCompanies({ p, stages, onBack }, ref) {
  const a = aCount(p);
  const sourced = p.companies.filter((c) => c.sources && c.sources.length > 0).length;
  const groups = stages.slice().sort((x, y) => x.order - y.order).map((s) => ({ s, cs: p.companies.filter((c) => c.stage === s.id) })).filter((g) => g.cs.length > 0);
  return (
    <div ref={ref} className="ph-companies ph-fade">
      <Head title={`公司 · ${p.companies.length} · ${a} 家 A 股 · ${sourced} 条有来源`} right={<span className="quiet" style={{ display: "inline-flex", gap: 10, alignItems: "center" }}><kbd className="kbd">ESC</kbd><span>或点面包屑 / 空白处回到整只模块</span><button type="button" className="btn-quiet" onClick={onBack}>返回</button></span>} />
      {groups.map(({ s, cs }) => (
        <div key={s.id} className="rows" style={{ marginTop: 18 }}>
          <span className="eyebrow" style={{ marginBottom: 8 }}>{s.name} · {cs.length}</span>
          {cs.map((c, i) => <CompanyRow key={i} c={c} />)}
          <div className="rows-end" />
        </div>
      ))}
    </div>
  );
});

function CompanyRow({ c }: { c: PhysLink }) {
  const name = c.name.split("（")[0];
  return (
    <div className="row ph-co-row">
      <span className="row-title" style={{ fontSize: 15 }}>{c.company_id ? <Link to={`/companies/${encodeURIComponent(c.company_id)}`} style={{ color: "inherit" }}>{name}</Link> : name}</span>
      <span className="row-meta" style={{ fontSize: 11 }}>{c.ticker ?? "—"}</span>
      <span className="row-meta" style={{ fontSize: 11 }}>{mkt(c.market)}</span>
      <span className="row-text">{c.role}</span>
      <Evidence level={c.evidence} sources={c.sources} note={c.note} />
    </div>
  );
}
