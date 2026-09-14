import { useEffect, useRef, useState } from "react";
import { api } from "../lib/api";
import { Link } from "../lib/router";
import "../pages/physical.css";

/** The opened-module drawing, small, with the given parts lit and everything else dimmed. Links to the object. */
export function PhysicalThumb({ objectId, parts, width = 540 }: { objectId: string; parts: string[]; width?: number }) {
  const [svg, setSvg] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const theme = (): "light" | "dark" => {
    const t = document.documentElement.getAttribute("data-theme");
    if (t === "light" || t === "dark") return t;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };
  const [th, setTh] = useState(theme);
  useEffect(() => {
    const mo = new MutationObserver(() => setTh(theme()));
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => mo.disconnect();
  }, []);
  useEffect(() => {
    let live = true;
    api.physicalSvg(objectId, th, "tx").then((t) => { if (live) setSvg(t); }).catch(() => { if (live) setSvg(""); });
    return () => { live = false; };
  }, [objectId, th]);
  useEffect(() => {
    const root = ref.current; if (!root) return;
    root.querySelectorAll<HTMLElement>("g[data-part]").forEach((g) => g.classList.toggle("on", parts.includes(g.dataset.part ?? "")));
    root.querySelectorAll<SVGElement>("g[data-station]").forEach((g) => { g.style.display = "none"; });
  }, [svg, parts]);
  const scale = width / 1278;
  return (
    <Link to={`/physical/${encodeURIComponent(objectId)}`} className="phys-thumb" style={{ display: "block", width, height: Math.round(517 * scale) + 22, position: "relative", color: "inherit" }}>
      <div ref={ref} className="ph-drawing is-sel" style={{ top: 0, transform: `scale(${scale})`, pointerEvents: "none" }} dangerouslySetInnerHTML={{ __html: svg }} />
      <span className="row-meta" style={{ position: "absolute", left: 0, bottom: 0, fontSize: 11, letterSpacing: "0.06em" }}>亮着的是它的部件 · 点开这只模块</span>
    </Link>
  );
}
