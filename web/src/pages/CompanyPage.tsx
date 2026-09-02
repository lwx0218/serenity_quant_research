import { useEffect, useState } from "react";
import { Shell } from "../components/Shell";
import { api, EVIDENCE_LABEL, market, pad2, roleLabel, type CompanyDetail } from "../lib/api";
import { Link } from "../lib/router";
import "./companies.css";

const LAYER_LABEL: Record<string, string> = {
  global_anchor: "全球锚点",
  a_share_focus: "A 股重点",
  reference: "行业图示收录",
};

export function CompanyPage({ id }: { id: string }) {
  const [c, setC] = useState<CompanyDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setC(null);
    api.company(id).then(setC).catch((e) => setError(String(e)));
  }, [id]);

  const crumbs = [{ label: "公司", to: "/companies" }, { label: c?.short_name ?? c?.name ?? "…" }];

  return (
    <Shell crumbs={crumbs}>
      <main className="page">
        {error && <p className="quiet" style={{ paddingTop: 40 }}>加载失败:{error}</p>}
        {!c && !error && <p className="quiet" style={{ paddingTop: 40 }}>加载中…</p>}
        {c && (
          <div className="cpage">
            <div className="cpage-main">
              <header className="co-head" style={{ paddingTop: 0 }}>
                <span className="eyebrow">{market(c) || "Private"}</span>
                <h1 className="h1">{c.short_name ?? c.name}</h1>
                {c.short_name && c.short_name !== c.name && <span className="focus-sub muted">{c.name}</span>}
                <p className="lead" style={{ marginTop: 6 }}>
                  {c.exposures.length > 0
                    ? `在 CPO 产业链的 ${new Set(c.exposures.map((e) => e.chain_node_id)).size} 个环节被提及;当前最高证据级:${c.evidence_level ? EVIDENCE_LABEL[c.evidence_level] : "—"}。`
                    : "尚未关联到任何产业链环节。"}
                </p>
              </header>

              <section className="rows">
                <div className="rows-head">
                  <span className="eyebrow">Position in chain · {c.exposures.length}</span>
                </div>
                {c.exposures.map((e) => (
                  <div key={e.id} className="row exp-row">
                    <span className="row-title">
                      <Link to={`/companies?chain=${encodeURIComponent(e.chain_node_id)}`} style={{ color: "inherit" }}>
                        {e.chain_name}
                      </Link>
                      {e.node_name && <span className="row-full" style={{ display: "block", fontSize: 12, color: "var(--muted)", fontWeight: 400 }}>{e.node_name}</span>}
                    </span>
                    <span className="row-text">{EVIDENCE_LABEL[e.evidence_level]}{e.role && e.role !== "代表企业" ? ` · ${roleLabel(e.role)}` : ""}</span>
                    <span className="row-note">
                      {e.note ?? (e.evidence_level === "reference" ? "公开行业图示将其列为该环节代表企业。" : "")}
                      {e.source_title && (
                        <span className="row-src">
                          来源:{e.source_publisher ? `${e.source_publisher} · ` : ""}
                          {e.source_url ? <a href={e.source_url} target="_blank" rel="noreferrer">{e.source_title}</a> : e.source_title}
                          {e.source_year_range ? ` · ${e.source_year_range}` : ""}
                        </span>
                      )}
                    </span>
                  </div>
                ))}
              </section>

              {c.modules.length > 0 && (
                <section className="rows">
                  <div className="rows-head">
                    <span className="eyebrow">In the device · {c.modules.length}</span>
                    <Link to="/" className="small">回到整机 →</Link>
                  </div>
                  {c.modules.map((m) => (
                    <Link key={m.id} to={`/explore/${m.id}`} className="row mod-row">
                      <span className="row-index">{pad2(m.sort ?? 0)}</span>
                      <span className="row-meta">{m.code}</span>
                      <span className="row-title">{m.name}</span>
                      <svg className="row-chev" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true"><path d="M4.5 2.5 8 6l-3.5 3.5" /></svg>
                    </Link>
                  ))}
                </section>
              )}
            </div>

            <aside className="cpage-aside">
              <dl className="kv">
                <dt>市场</dt><dd>{market(c) || "非上市 / 未收录"}</dd>
                <dt>地区</dt><dd>{c.country_region ?? "—"}</dd>
                <dt>覆盖层</dt><dd>{c.universe_layer ? LAYER_LABEL[c.universe_layer] ?? c.universe_layer : "—"}</dd>
                {c.official_url && (
                  <>
                    <dt>官网</dt>
                    <dd><a href={c.official_url} target="_blank" rel="noreferrer">{new URL(c.official_url).hostname}</a></dd>
                  </>
                )}
              </dl>
              <p className="focus-note">
                证据级说明:<span className="ink">已核验</span> 有经人工审核的证据;<span className="ink">候选</span> 有来源但未审核;<span className="ink">行业图示</span> 仅见于公开产业链示意图。
              </p>
            </aside>
          </div>
        )}
        <footer className="footer"><span /></footer>
      </main>
    </Shell>
  );
}
