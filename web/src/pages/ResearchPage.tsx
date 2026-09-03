import { useCallback, useEffect, useState } from "react";
import { EventsWide } from "../components/Research";
import { Footer, Shell, invalidatePending } from "../components/Shell";
import { AsOf, Conclusion, Dir, Head, Sig } from "../components/Signal";
import { md, mkt, type Decision, type Inbox } from "../lib/api";
import { Link, useRouter } from "../lib/router";
import "./research.css";

const WINDOW_DAYS = 7;

/**
 * 研究 = the inbox. What to decide first, then this week's events, open
 * questions and recent notes; the device rail on the right for orientation.
 */
export function ResearchPage() {
  const { navigate } = useRouter();
  const [ib, setIb] = useState<Inbox | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const load = useCallback(() => {
    mkt.inbox(WINDOW_DAYS).then(setIb).catch((e) => setError(String(e)));
  }, []);
  useEffect(load, [load]);

  const act = async (d: Decision, a: Decision["actions"][number]) => {
    if (a.to) { navigate(a.to); return; }
    if (a.action === "dismiss") { setDismissed((s) => new Set(s).add(d.kind + d.subject)); return; }
    if (a.action === "extend" && a.subject) { await mkt.extendNote(a.subject); }
    else if (a.action) { await mkt.verify({ action: a.action, event_id: d.event_id ?? null, exposure_id: d.exposure_id ?? null }); }
    invalidatePending();
    load();
  };

  const decisions = (ib?.decisions ?? []).filter((d) => !dismissed.has(d.kind + d.subject));

  return (
    <Shell crumbs={[{ label: "研究" }]} footer={<Footer note={ib?.sample ? "事件、反应与偏离读数为样式示例。" : undefined} />}>
      <main className="page">
        {error && <p className="quiet" style={{ paddingTop: 40 }}>加载失败:{error}</p>}
        {!ib && !error && <p className="quiet" style={{ paddingTop: 40 }}>加载中…</p>}
        {ib && (
          <div className="inbox">
            <div className="inbox-main">
              <header className="inbox-head">
                <span className="eyebrow">Research · this week</span>
                <h1 className="h1">研究</h1>
                <Conclusion c={ib.conclusion} lead />
                <AsOf date={ib.as_of} horizon="本周" extra="每日收盘后重算" />
              </header>

              <section className="rows">
                <div className="rows-head">
                  <span className="eyebrow">要决定 · {decisions.length}</span>
                  <span className="small muted">按紧急程度 · 方向标记 = 对你现有判断的含义</span>
                </div>
                {decisions.length === 0 && <p className="quiet" style={{ padding: "12px 0", borderTop: "1px solid var(--hair)" }}>没有要决定的事。</p>}
                {decisions.map((d, i) => (
                  <div key={i} className="row dec-row">
                    <span className="row-meta">{d.label}</span>
                    <Dir d={d.direction} />
                    <span className="row-text">{d.text}</span>
                    <span className="actions" style={{ justifySelf: "end" }}>
                      {d.actions.map((a, j) => (
                        <button key={j} type="button" className={j === 0 ? "btn" : "btn-quiet"} onClick={() => act(d, a)}>{a.label}</button>
                      ))}
                    </span>
                  </div>
                ))}
              </section>

              <section className="block">
                <Head title={`卡口事件 · ${ib.window_days} 天 · ${ib.events.length} 条`} right={<AsOf date={ib.as_of} horizon="T+1 相对篮子" extra="时效按各层事件效力" />} />
                <EventsWide items={ib.events} who="subject" />
              </section>

              <section className="rows">
                <div className="rows-head">
                  <span className="eyebrow">未决问题 · {ib.questions.length}</span>
                </div>
                {ib.questions.length === 0 && <p className="quiet" style={{ padding: "12px 0", borderTop: "1px solid var(--hair)" }}>没有未决问题。在任意一层或公司的判断里加。</p>}
                {ib.questions.map((q, i) => (
                  <div key={q.subject + q.index} className="row oq-row">
                    <span className="row-index">Q{i + 1}</span>
                    <span className="row-text">{q.text}</span>
                    <Link to={q.kind === "company" ? `/companies/${q.subject}` : `/explore/${q.subject}`} style={{ fontSize: 13 }}>{q.subject_title}</Link>
                    <span className="row-meta">{q.status}</span>
                    <span className="row-meta">{md(q.date)}</span>
                  </div>
                ))}
              </section>

              <section className="rows">
                <div className="rows-head">
                  <span className="eyebrow">最近笔记 · {ib.notes.length}</span>
                  <span className="small muted">标记 = 判断方向</span>
                </div>
                {ib.notes.map((n) => (
                  <div key={n.subject} className="row note-row">
                    <Dir d={n.direction} />
                    <Link to={n.kind === "company" ? `/companies/${n.subject}` : `/explore/${n.subject}`} style={{ fontSize: 13 }}>{n.title}</Link>
                    <span className="row-text">{n.excerpt}</span>
                    <span className="row-meta">{md(n.updated)}</span>
                  </div>
                ))}
              </section>
            </div>

            <aside className="inbox-aside">
              <Head title="整机 · 本周" right={<AsOf date={ib.as_of} horizon={`${ib.window_days} 天`} />} />
              <div className="rail-head"><span /><span className="row-meta">层</span><span className="row-meta" style={{ fontSize: 11 }}>事件</span><span className="row-meta" style={{ textAlign: "right", fontSize: 11 }}>篮子</span></div>
              <div className="rows">
                {ib.rail.map((r) => (
                  <Link key={r.node_id} to={`/explore/${r.node_id}`} className="rail-row">
                    <span className={`row-index${r.direction ? ` is-${r.direction}` : ""}`} style={r.direction ? { color: `var(--sig-${r.direction})` } : undefined}>{String(r.sort).padStart(2, "0")}</span>
                    <span className="rail-name" style={{ color: r.events ? "var(--ink)" : "var(--ink-2)" }}>{r.name}</span>
                    <span className="rail-n" style={{ color: r.events ? "var(--ink-2)" : "var(--faint)" }}>{r.events || "·"}</span>
                    <span style={{ textAlign: "right" }}>{r.direction ? <Sig v={r.basket_excess} size={12} /> : <span className="row-meta" style={{ color: "var(--faint)" }}>—</span>}</span>
                  </Link>
                ))}
              </div>
              <span className="rule-note">点层回到整机对应位置。判断与问题以 Markdown 保存在 data/notes/,可直接用 Obsidian 打开。</span>
            </aside>
          </div>
        )}
      </main>
    </Shell>
  );
}
