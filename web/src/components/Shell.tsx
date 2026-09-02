import type { ReactNode } from "react";
import { Link, useRouter } from "../lib/router";
import { ThemeToggle } from "./ThemeToggle";

export interface Crumb {
  label: string;
  to?: string;
}

/**
 * The page frame: wordmark, breadcrumb (the hierarchy the user is inside),
 * the three areas, and the theme toggle. No sidebar, no panels.
 */
export function Shell({ crumbs = [], children }: { crumbs?: Crumb[]; children: ReactNode }) {
  const { route } = useRouter();
  const area = route.path.startsWith("/companies") ? "companies" : "explore";

  return (
    <>
      <header className="top">
        <div className="top-left">
          <Link to="/" className="wordmark">
            Serenity
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
          <Link to="/" className={area === "explore" ? "is-active" : undefined}>
            光模块
          </Link>
          <Link to="/companies" className={area === "companies" ? "is-active" : undefined}>
            公司
          </Link>
          <ThemeToggle />
        </nav>
      </header>
      {children}
    </>
  );
}

export function Chevron() {
  return (
    <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
      <path d="M4.5 2.5 8 6l-3.5 3.5" />
    </svg>
  );
}
