import { useEffect, useState } from "react";
import { Shell } from "../components/Shell";
import { api, EVIDENCE_LABEL, market, pad2, type ChainNode, type CompanySummary, type NodeDetail } from "../lib/api";
import { Link, useRouter } from "../lib/router";
import "./companies.css";

/**
 * /companies            every company in the universe
 * /companies?chain=…    one industry-chain link
 * /companies?node=…     companies relevant to a module / part (from the Explorer)
 */
export function CompaniesPage() {
  const { route } = useRouter();
  const chainId = route.params.get("chain");
  const nodeId = route.params.get("node");

  const [chain, setChain] = useState<ChainNode[]>([]);
  const [items, setItems] = useState<CompanySummary[] | null>(null);
  const [node, setNode] = useState<NodeDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.chain().then(setChain).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    setItems(null);
    setNode(null);
    const q = nodeId ? { node: nodeId } : chainId ? { chain: chainId } : {};
    api.companies(q).then(setItems).catch((e) => setError(String(e)));
    if (nodeId) api.node(nodeId).then(setNode).catch(() => undefined);
  }, [chainId, nodeId]);

  const current = chainId ? chain.find((c) => c.id === chainId) : undefined;
  const title = node ? `${node.node.name} 相关公司` : current ? (current.display_name ?? current.name) : "公司池";
  const crumbs = node
    ? [{ label: "CPO 光模块", to: "/" }, { label: node.node.name, to: `/explore/${node.node.id}` }, { label: "公司" }]
    : [{ label: "公司" }, ...(current ? [{ label: current.display_name ?? current.name }] : [])];

  const levels = items ? Array.from(new Set(items.map((c) => c.evidence_level).filter(Boolean))) : [];

  return (
    <Shell crumbs={crumbs}>
      <main className="page">
        <header className="co-head">
          <span className="eyebrow">{current ? `Chain · ${pad2(current.sort)} / ${pad2(chain.length || 10)}` : node ? "Companies" : "Universe"}</span>
          <h1 className="h1">{title}</h1>
          <p className="lead">
            {current?.keywords && <>{current.keywords}。</>}
            {node && node.chain_nodes.length > 0 && <>对应产业链环节:{node.chain_nodes.map((c) => c.display_name ?? c.name).join(" / ")}。</>}
            {!current && !node && <>按产业链环节整理的公司,证据级从行业图示到已核验。</>}
          </p>
        </header>

        {!node && (
          <nav className="chain-nav" aria-label="产业链环节">
            <Link to="/companies" className={!chainId ? "is-active" : undefined}>全部</Link>
            {chain.map((c) => (
              <Link key={c.id} to={`/companies?chain=${encodeURIComponent(c.id)}`} className={c.id === chainId ? "is-active" : undefined}>
                {c.display_name ?? c.name}
              </Link>
            ))}
          </nav>
        )}

        {error && <p className="quiet" style={{ paddingTop: 40 }}>加载失败:{error}</p>}
        {items === null && !error && <p className="quiet" style={{ paddingTop: 40 }}>加载中…</p>}

        {items && (
          <section className="co-list">
            <div className="rows-head">
              <span className="eyebrow">{items.length} 家</span>
              <span className="small muted">{levels.length > 0 && `证据级:${levels.map((l) => EVIDENCE_LABEL[l!]).join(" · ")}`}</span>
            </div>
            <div className="rows">
              {items.map((c, i) => (
                <Link key={c.id} to={`/companies/${encodeURIComponent(c.id)}`} className="row co-list-row">
                  <span className="row-index">{pad2(i + 1)}</span>
                  <span className="row-title">
                    {c.short_name ?? c.name}
                    {c.short_name && c.short_name !== c.name && <span className="row-full">{c.name}</span>}
                  </span>
                  <span className="row-meta">{market(c) || c.country_region}</span>
                  <span className="row-text">{c.chain_nodes.map((x) => x.name).join(" · ") || "尚未关联环节"}</span>
                  <span className="row-level">{c.evidence_level ? EVIDENCE_LABEL[c.evidence_level] : "—"}</span>
                </Link>
              ))}
            </div>
          </section>
        )}

        <footer className="footer">
          <p style={{ maxWidth: 720 }}>
            “行业图示”一级来自公开产业链示意图,只说明公开资料把公司归到这一环节,不代表已核验的产品或供应关系。
          </p>
        </footer>
      </main>
    </Shell>
  );
}
