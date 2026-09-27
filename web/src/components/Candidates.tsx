/**
 * 候选事件：自动抓取进来的条目，人确认后才成为卡口事件。
 * 一行 = 日期 · 来源（证据级）· 标题（原文链接）· 公司 · 类别 · → 部件 · 确认 / 驳回。
 * 没有类别或公司的条目不能确认，先在行内补上。
 */
import { useState } from "react";
import { CATEGORY_OPTIONS, PHYS_EVIDENCE_LABEL, md, mkt, type Candidate, type CandidateStatus } from "../lib/api";
import { Link } from "../lib/router";

const EV_CLASS: Record<string, string> = { verified: "is-verified", consensus: "is-consensus", candidate: "is-candidate" };

export function CandidateRows({ items, onChange }: { items: Candidate[]; onChange: () => void }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [picks, setPicks] = useState<Record<string, { category?: string; company_id?: string }>>({});
  const [err, setErr] = useState<string | null>(null);

  const decide = async (c: Candidate, action: "confirm" | "reject") => {
    setBusy(c.id); setErr(null);
    try {
      if (action === "confirm") {
        const p = picks[c.id] ?? {};
        await mkt.confirmCandidate(c.id, { category: p.category ?? c.category, company_id: p.company_id ?? c.company?.id ?? c.companies[0]?.companyId ?? null });
      } else {
        await mkt.rejectCandidate(c.id);
      }
      onChange();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(null);
    }
  };

  if (items.length === 0) return <p className="quiet" style={{ padding: "12px 0", borderTop: "1px solid var(--hair)" }}>候选池是空的。抓取在收盘后与每几小时自动跑；也可以让 AI 从网页端补。</p>;
  return (
    <div className="rows">
      <div className="row cand-row is-head">
        <span className="row-meta">日期</span><span className="row-meta">来源</span><span className="row-meta">标题</span><span className="row-meta">公司</span><span className="row-meta">类别</span><span className="row-meta">→ 部件</span><span />
      </div>
      {err && <p className="quiet" style={{ color: "var(--sig-neg)", padding: "6px 0" }}>{err}</p>}
      {items.map((c) => {
        const p = picks[c.id] ?? {};
        const category = p.category ?? c.category ?? "";
        const companyId = p.company_id ?? c.company?.id ?? c.companies[0]?.companyId ?? "";
        const canConfirm = Boolean(category && companyId && c.date);
        return (
          <div key={c.id} className={`row cand-row${busy === c.id ? " is-busy" : ""}${c.relevance === 0 ? " is-routine" : ""}`}>
            <span className="row-meta">{md(c.date) || "—"}</span>
            <span className="cand-src">
              <span className={`cand-ev ${EV_CLASS[c.evidence] ?? ""}`} title={`${c.source}${c.also_reported_by.length ? " · 另见 " + c.also_reported_by.join("、") : ""}`}>{PHYS_EVIDENCE_LABEL[c.evidence]}</span>
              <span className="row-meta">{c.source_label}{c.also_reported_by.length ? ` +${c.also_reported_by.length}` : ""}</span>
            </span>
            <span className="cand-title">
              <a href={c.url} target="_blank" rel="noreferrer" style={{ color: "inherit" }}>{c.title}</a>
              {c.summary && <span className="cand-sum">{c.summary}</span>}
            </span>
            <span className="cand-co">
              {c.companies.length > 1 ? (
                <select className="cand-select" value={companyId} onChange={(e) => setPicks((s) => ({ ...s, [c.id]: { ...s[c.id], company_id: e.target.value } }))}>
                  {c.companies.map((x) => <option key={x.companyId} value={x.companyId}>{x.name}</option>)}
                </select>
              ) : c.company ? (
                <Link to={`/companies/${c.company.id}`} style={{ fontSize: 13 }}>{c.company.short_name ?? c.company.name}</Link>
              ) : (
                <span className="row-meta" style={{ color: "var(--faint)" }}>未命中</span>
              )}
            </span>
            <span>
              <select className={`cand-select${category ? "" : " is-empty"}`} value={category} onChange={(e) => setPicks((s) => ({ ...s, [c.id]: { ...s[c.id], category: e.target.value } }))}>
                <option value="">类别…</option>
                {CATEGORY_OPTIONS.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </span>
            <span className="cand-part">
              {c.part ? <Link to={`/physical/${c.part.object_id}?part=${c.part.part_id}`} style={{ fontSize: 13 }}>{c.part.part_name.split("（")[0]}</Link>
                : c.parts.length ? <span className="row-meta">{c.parts.map((x) => x.name.split("（")[0]).join(" · ")}</span>
                : <span className="row-meta" style={{ color: "var(--faint)" }}>—</span>}
            </span>
            <span className="actions" style={{ justifySelf: "end", whiteSpace: "nowrap" }}>
              <button type="button" className="btn" disabled={!canConfirm || busy === c.id} title={canConfirm ? "写入事件表，反应随收盘重算" : "先补公司与类别"} onClick={() => decide(c, "confirm")}>确认</button>
              <button type="button" className="btn-quiet" disabled={busy === c.id} onClick={() => decide(c, "reject")}>驳回</button>
            </span>
          </div>
        );
      })}
    </div>
  );
}

export function candidateNote(counts: Partial<Record<CandidateStatus, number>>): string {
  const c = counts.confirmed ?? 0, r = counts.rejected ?? 0;
  return c || r ? `已确认 ${c} · 已驳回 ${r}` : "";
}
