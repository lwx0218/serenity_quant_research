import { useEffect, useState, type ReactNode } from "react";
import { mkt } from "../lib/api";
import { Link, useRouter } from "../lib/router";
import { useSignalPref } from "../lib/signal";
import { ThemeToggle } from "./ThemeToggle";

export interface Crumb {
  label: string;
  to?: string;
}

const PRODUCT_ID = "cpo";
let pendingPromise: Promise<number> | null = null;
/** How many things wait in the inbox (drives the dot after 研究). Fetched once per page load. */
function pendingCount(): Promise<number> {
  if (!pendingPromise) {
    pendingPromise = mkt
      .overview(PRODUCT_ID)
      .then((o) => o.counts.verifications + o.counts.theses_expiring)
      .catch(() => 0);
  }
  return pendingPromise as Promise<number>;
}
export function invalidatePending() {
  pendingPromise = null;
}

/**
 * The page frame: wordmark, breadcrumb (the hierarchy the user is inside),
 * the three areas, the colour-convention switch and the theme toggle.
 * No sidebar, no panels.
 */
export function Shell({ crumbs = [], children, footer }: { crumbs?: Crumb[]; children: ReactNode; footer?: ReactNode }) {
  const { route } = useRouter();
  const p = route.path;
  const area = p.startsWith("/physical") ? "physical" : p.startsWith("/companies") || p.startsWith("/baskets") ? "companies" : p.startsWith("/research") || p.startsWith("/judgement") ? "research" : "explore";
  const [pending, setPending] = useState(0);
  useEffect(() => {
    let live = true;
    pendingCount().then((n) => { if (live) setPending(n); });
    return () => { live = false; };
  }, [p]);

  return (
    <>
      <header className="top">
        <div className="top-left">
          <Link to="/" className="wordmark">
            Teardown
          </Link>
          {crumbs.length > 0 && (
            <nav className="crumbs" aria-label="位置">
              {crumbs.map((c, i) => (
                <span key={i} style={{ display: "contents" }}>
                  {i > 0 && <Chevron />}
                  {c.to && i < crumbs.length - 1 ? (
                    <Link to={c.to}>{c.label}</Link>
                  ) : (
                    <span className={i === crumbs.length - 1 ? "is-current" : undefined}>{c.label}</span>
                  )}
                </span>
              ))}
            </nav>
          )}
        </div>
        <nav className="top-nav" aria-label="主导航">
          <Link to="/physical" className={area === "physical" ? "is-active" : undefined}>
            实物
          </Link>
          <Link to="/" className={area === "explore" ? "is-active" : undefined}>
            光模块
          </Link>
          <Link to="/companies" className={area === "companies" ? "is-active" : undefined}>
            公司
          </Link>
          <Link to="/research" className={area === "research" ? "is-active" : undefined} title={pending ? `${pending} 件事要决定` : undefined}>
            研究{pending > 0 && <span className="nav-dot" aria-label={`${pending} 件事要决定`} />}
          </Link>
          <SignalSwitch />
          <ThemeToggle />
        </nav>
      </header>
      {children}
      {footer}
    </>
  );
}

/** 红涨绿跌 ⇄ 绿涨红跌. A two-glyph button: the current convention is drawn in its own colours. */
function SignalSwitch() {
  const { pref, toggle } = useSignalPref();
  const title = pref === "cn" ? "红涨绿跌(A 股习惯)· 点击切换为绿涨红跌" : "绿涨红跌 · 点击切换为红涨绿跌";
  return (
    <button type="button" className="signal-btn" onClick={toggle} title={title} aria-label={title}>
      <span className="dir is-pos">▲</span>
      <span className="dir is-neg">▼</span>
    </button>
  );
}

export function Chevron() {
  return (
    <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
      <path d="M4.5 2.5 8 6l-3.5 3.5" />
    </svg>
  );
}

/** Page footer: one note (sources / 示例) and the wordmark line. */
export function Footer({ note }: { note?: ReactNode }) {
  return (
    <footer className="footer page">
      <p style={{ maxWidth: 720 }}>{note}</p>
      <span className="mono" style={{ fontSize: 11, letterSpacing: "0.1em", color: "var(--faint)" }}>
        TEARDOWN · FROM PART TO POSITION
      </span>
    </footer>
  );
}
