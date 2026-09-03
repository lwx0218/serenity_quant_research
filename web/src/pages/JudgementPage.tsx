import { useEffect, useMemo, useRef, useState } from "react";
import { ExplodedStack, type StackLayer } from "../components/ExplodedStack";
import { Footer, Shell, invalidatePending } from "../components/Shell";
import { Conclusion, Dir, Sig } from "../components/Signal";
import { api, DIR_LABEL, md, mkt, pad2, type Direction, type LinkSuggestion, type Product, type Thesis } from "../lib/api";
import { useRouter } from "../lib/router";
import "./explorer.css";
import "./research.css";

const PRODUCT_ID = "cpo";
const DIRS: Direction[] = ["pos", "neg", "neu"];

interface Draft {
  kind: string; title: string; direction: Direction; stance: string; body: string; since: string | null;
  window_until: string; window_label: string; threshold_pct: number; position: string; track: string[]; indicators: string[]; invalidation: string[];
}

function toDraft(t: Thesis | null, fallback: Partial<Draft>): Draft {
  return {
    kind: t?.kind ?? fallback.kind ?? "module", title: t?.title ?? fallback.title ?? "", direction: t?.direction ?? "neu",
    stance: t?.stance ?? "", body: t?.body ?? "", since: t?.since ?? null,
    window_until: t?.window_until ?? "", window_label: t?.window_label ?? "", threshold_pct: t?.threshold_pct ?? 3,
    position: t?.position ?? "", track: t?.track ?? fallback.track ?? [], indicators: t?.indicators ?? [], invalidation: t?.invalidation ?? [],
  };
}

/**
 * Edit one judgement: direction first, then the thesis, then what would prove
 * it wrong. Saves to data/notes/<subject>.md through the API.
 */
export function JudgementPage({ subject }: { subject: string }) {
  const { navigate, route } = useRouter();
  const review = route.params.get("review") === "1";
  const [product, setProduct] = useState<Product | null>(null);
  const [existing, setExisting] = useState<Thesis | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isNode = subject.startsWith(PRODUCT_ID + ".");
  const isCompany = !isNode;

  useEffect(() => {
    api.product(PRODUCT_ID).then(setProduct).catch(() => null);
  }, []);

  useEffect(() => {
    let live = true;
    (async () => {
      let t: Thesis | null = null;
      try { t = await mkt.note(subject); } catch { t = null; }
      let fallback: Partial<Draft> = {};
      if (isNode) {
        try {
          const d = await api.node(subject);
          const mod = d.node.kind === "module" ? d.node : d.ancestors.find((a) => a.kind === "module");
          fallback = { kind: d.node.kind, title: d.node.name, track: mod ? [`basket:${mod.id}`] : [] };
        } catch { /* keep defaults */ }
      } else {
        try {
          const c = await api.company(subject);
          fallback = { kind: "company", title: c.short_name ?? c.name, track: [`company:${c.id}`] };
        } catch { /* keep defaults */ }
      }
      if (!live) return;
      setExisting(t);
      setDraft(toDraft(t, fallback));
    })();
    return () => { live = false; };
  }, [subject, isNode]);

  const modules = product?.children ?? [];
  const layers: StackLayer[] = useMemo(() => modules.map((m) => ({ id: m.id, visual: m.visual, label: m.visual === "board-die" ? "ASIC" : undefined })), [modules]);
  const moduleId = useMemo(() => {
    if (!isNode) return null;
    if (modules.some((m) => m.id === subject)) return subject;
    return modules.find((m) => m.children.some((p) => p.id === subject))?.id ?? null;
  }, [modules, subject, isNode]);
  const mi = modules.findIndex((m) => m.id === moduleId);
  const back = isCompany ? `/companies/${subject}` : `/explore/${subject}`;

  const save = async () => {
    if (!draft) return;
    setSaving(true); setError(null);
    try {
      await mkt.saveNote(subject, {
        kind: draft.kind, title: draft.title, direction: draft.direction, stance: draft.stance, body: draft.body, since: draft.since ?? undefined,
        window_until: draft.window_until || null, window_label: draft.window_label || null, threshold_pct: draft.threshold_pct, position: draft.position || null,
        track: draft.track, indicators: draft.indicators, invalidation: draft.invalidation,
      } as Partial<Thesis>);
      invalidatePending();
      navigate(back);
    } catch (e) {
      setError(String(e)); setSaving(false);
    }
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") { e.preventDefault(); save(); }
      if (e.key === "Escape") navigate(back);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const crumbs = isCompany
    ? [{ label: "公司", to: "/companies" }, { label: draft?.title ?? "…", to: back }, { label: review ? "回顾判断" : "编辑判断" }]
    : [{ label: product?.name ?? "CPO 光模块", to: "/" }, { label: draft?.title ?? "…", to: back }, { label: review ? "回顾判断" : "编辑判断" }];

  return (
    <Shell crumbs={crumbs} footer={<Footer note="判断以 Markdown 保存在 data/notes/,可直接用 Obsidian 打开;带阈值的指标会每天用行情重算。" />}>
      <main className="page">
        <section className="hero is-selected judge">
          <div className="hero-stack" style={{ left: 40, top: 86, opacity: "var(--judge-dim)" }}>
            {layers.length > 0 && isNode && <ExplodedStack layers={layers} selectedId={moduleId} hoverId={null} onSelect={() => undefined} onHover={() => undefined} transform="scale(0.92)" />}
          </div>
          <div className="focus" style={{ paddingTop: 96 }}>
            {!draft ? <p className="quiet">加载中…</p> : (
              <>
                <div className="focus-head">
                  <span className="eyebrow is-accent">{isNode && mi >= 0 ? `${pad2(mi + 1)} / ${pad2(modules.length)} · ${modules[mi].code} · ` : ""}{review ? "回顾判断" : "编辑判断"}</span>
                  <h1 className="h1" style={{ fontSize: 48 }}>{draft.title} · 我的判断</h1>
                  <span className="focus-sub" style={{ fontSize: 13 }}>Markdown 笔记 · data/notes/{subject}.md · 可直接用 Obsidian 打开{existing?.updated && ` · 上次保存 ${md(existing.updated)}`}</span>
                </div>

                {review && existing && (
                  <div className="block">
                    <span className="eyebrow">回顾 · 自 {md(existing.since)} 起的读数</span>
                    <Conclusion c={existing.conclusion} />
                    <div className="readings">{existing.readings.map((r) => <span key={r.instrument} className="reading"><span className="row-meta">{r.label}</span><Sig v={r.excess} /></span>)}</div>
                  </div>
                )}

                <div className="block">
                  <span className="eyebrow">方向 · 先选,再写</span>
                  <div className="choices">
                    {DIRS.map((d) => (
                      <button key={d} type="button" className={`choice is-${d}${draft.direction === d ? " is-on" : ""}`} onClick={() => setDraft({ ...draft, direction: d })}>
                        <Dir d={d} label={d === "neu" ? "中性 / 观察" : DIR_LABEL[d]} />
                      </button>
                    ))}
                    <span className="row-meta" style={{ marginLeft: "auto" }}>方向决定这条判断用什么颜色出现在其他页面</span>
                  </div>
                </div>

                <div className="block">
                  <span className="eyebrow">论点</span>
                  <div className="field" style={{ gridTemplateColumns: "96px minmax(0,1fr)" }}>
                    <span className="row-meta">一句话</span>
                    <input value={draft.stance} onChange={(e) => setDraft({ ...draft, stance: e.target.value })} placeholder="看多 / 看空什么,不做什么" />
                  </div>
                  <LinkedEditor value={draft.body} onChange={(v) => setDraft({ ...draft, body: v })} />
                  <span className="row-meta">Markdown · 输入 [[ 链接公司 / 环节 / 层 / 部件 · 链接会出现在对方页面的“被引用”里</span>
                </div>

                <div className="block">
                  <span className="eyebrow">让它可被证伪 · 数字会被自动跟踪</span>
                  <div className="rows">
                    <div className="field"><span className="row-meta">窗口</span>
                      <span style={{ display: "flex", gap: 16 }}>
                        <input value={draft.window_label} onChange={(e) => setDraft({ ...draft, window_label: e.target.value })} placeholder="2 个季度(至 2027-Q1)" />
                        <input type="date" value={draft.window_until} onChange={(e) => setDraft({ ...draft, window_until: e.target.value })} style={{ width: 160 }} title="到期日:到期自动进收件箱回顾" />
                      </span>
                    </div>
                    <div className="field"><span className="row-meta">验证指标</span>
                      <textarea rows={Math.max(2, draft.indicators.length + 1)} value={draft.indicators.join("\n")} onChange={(e) => setDraft({ ...draft, indicators: e.target.value.split("\n").filter((x) => x.trim()) })} placeholder={"一行一条,例如:硅光篮子相对整机 ≥ +3%"} /></div>
                    <div className="field"><span className="row-meta">失效条件</span>
                      <textarea rows={Math.max(2, draft.invalidation.length + 1)} value={draft.invalidation.join("\n")} onChange={(e) => setDraft({ ...draft, invalidation: e.target.value.split("\n").filter((x) => x.trim()) })} placeholder={"一行一条,例如:篮子相对整机 < −5%"} /></div>
                    <div className="field"><span className="row-meta">头寸含义</span>
                      <input value={draft.position} onChange={(e) => setDraft({ ...draft, position: e.target.value })} placeholder="触发验证 → 加环节篮子;触发失效 → 减至基准" /></div>
                    <div className="field"><span className="row-meta">跟踪 · 阈值</span>
                      <span style={{ display: "flex", gap: 16, alignItems: "baseline" }}>
                        <input value={draft.track.join(", ")} onChange={(e) => setDraft({ ...draft, track: e.target.value.split(",").map((x) => x.trim()).filter(Boolean) })} placeholder="basket:cpo.mod.pic, company:cn.300308" style={{ flex: 1 }} />
                        <span className="row-meta">±</span>
                        <input type="number" step="0.5" min="0" value={draft.threshold_pct} onChange={(e) => setDraft({ ...draft, threshold_pct: parseFloat(e.target.value) || 0 })} style={{ width: 56 }} />
                        <span className="row-meta">%</span>
                      </span>
                    </div>
                  </div>
                  <span className="row-meta">带阈值的指标(≥ / &lt;)会每天用行情重算,达到即在收件箱提示;没有阈值的只做记录。</span>
                </div>

                {error && <p className="quiet">保存失败:{error}</p>}
                <div style={{ display: "flex", gap: 22, alignItems: "center" }}>
                  <button type="button" className="btn-primary" onClick={save} disabled={saving}>{saving ? "保存中…" : "保存"}</button>
                  <button type="button" className="btn-quiet" onClick={() => navigate(back)}>取消</button>
                  <span className="row-meta" style={{ marginLeft: "auto" }}>⌘S 保存 · Esc 取消</span>
                </div>
              </>
            )}
          </div>
        </section>
      </main>
    </Shell>
  );
}

/* --------------------------------------------------------- [[ autocomplete */
function LinkedEditor({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [query, setQuery] = useState<string | null>(null);
  const [items, setItems] = useState<LinkSuggestion[]>([]);
  const [hot, setHot] = useState(0);

  const detect = (v: string, caret: number) => {
    const before = v.slice(0, caret);
    const open = before.lastIndexOf("[[");
    if (open < 0 || before.slice(open).includes("]]")) { setQuery(null); return; }
    setQuery(before.slice(open + 2));
  };

  useEffect(() => {
    if (query === null) { setItems([]); return; }
    let live = true;
    mkt.suggest(query).then((xs) => { if (live) { setItems(xs.slice(0, 6)); setHot(0); } }).catch(() => setItems([]));
    return () => { live = false; };
  }, [query]);

  const pick = (s: LinkSuggestion) => {
    const el = ref.current;
    if (!el) return;
    const caret = el.selectionStart;
    const before = value.slice(0, caret), after = value.slice(caret);
    const open = before.lastIndexOf("[[");
    const next = before.slice(0, open) + `[[${s.label}]]` + after;
    onChange(next);
    setQuery(null);
    requestAnimationFrame(() => { const pos = open + s.label.length + 4; el.setSelectionRange(pos, pos); el.focus(); });
  };

  return (
    <div style={{ position: "relative" }}>
      <textarea
        ref={ref}
        className="editor"
        value={value}
        placeholder="为什么这么看?瓶颈在哪、谁受益、什么时候能验证。用 [[ 链接公司或环节。"
        onChange={(e) => { onChange(e.target.value); detect(e.target.value, e.target.selectionStart); }}
        onKeyDown={(e) => {
          if (query === null || items.length === 0) return;
          if (e.key === "ArrowDown") { e.preventDefault(); setHot((h) => (h + 1) % items.length); }
          else if (e.key === "ArrowUp") { e.preventDefault(); setHot((h) => (h - 1 + items.length) % items.length); }
          else if (e.key === "Enter" || e.key === "Tab") { e.preventDefault(); pick(items[hot]); }
          else if (e.key === "Escape") { e.stopPropagation(); setQuery(null); }
        }}
        onClick={(e) => detect(value, (e.target as HTMLTextAreaElement).selectionStart)}
      />
      {query !== null && items.length > 0 && (
        <div className="suggest" style={{ left: 0, top: "100%" }}>
          {items.map((s, i) => (
            <button key={s.id} type="button" className={i === hot ? "is-hot" : undefined} onMouseDown={(e) => { e.preventDefault(); pick(s); }}>
              <span>{s.label}</span><span className="row-meta">{s.kind}{s.meta ? ` · ${s.meta}` : ""}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
