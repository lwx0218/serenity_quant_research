/**
 * A very small history router. Three routes do not need a dependency, and
 * keeping it here makes navigation behaviour easy to read and change.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export interface Route {
  path: string;                       // "/explore/cpo.mod.pic"
  params: URLSearchParams;            // ?chain=...
}

interface RouterCtx {
  route: Route;
  navigate: (to: string, opts?: { replace?: boolean }) => void;
}

const Ctx = createContext<RouterCtx | null>(null);

function read(): Route {
  return { path: window.location.pathname || "/", params: new URLSearchParams(window.location.search) };
}

export function RouterProvider({ children }: { children: ReactNode }) {
  const [route, setRoute] = useState<Route>(read);

  useEffect(() => {
    const onPop = () => setRoute(read());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const navigate = useCallback((to: string, opts?: { replace?: boolean }) => {
    if (opts?.replace) window.history.replaceState(null, "", to);
    else window.history.pushState(null, "", to);
    setRoute(read());
    window.scrollTo({ top: 0 });
  }, []);

  const value = useMemo(() => ({ route, navigate }), [route, navigate]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useRouter(): RouterCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useRouter outside RouterProvider");
  return ctx;
}

/** Match "/explore/:id" style patterns. Returns params or null. */
export function match(pattern: string, path: string): Record<string, string> | null {
  const p = pattern.split("/").filter(Boolean);
  const s = path.split("/").filter(Boolean);
  if (p.length !== s.length) return null;
  const out: Record<string, string> = {};
  for (let i = 0; i < p.length; i++) {
    if (p[i].startsWith(":")) out[p[i].slice(1)] = decodeURIComponent(s[i]);
    else if (p[i] !== s[i]) return null;
  }
  return out;
}

export function Link({
  to,
  children,
  className,
  replace,
  ...rest
}: { to: string; children: ReactNode; className?: string; replace?: boolean } & Omit<
  React.AnchorHTMLAttributes<HTMLAnchorElement>,
  "href" | "onClick"
>) {
  const { navigate } = useRouter();
  return (
    <a
      href={to}
      className={className}
      onClick={(e) => {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
        e.preventDefault();
        navigate(to, { replace });
      }}
      {...rest}
    >
      {children}
    </a>
  );
}
