/**
 * The semantic colour axis (design-rules §5). Direction is always carried by a
 * glyph or a sign as well as by colour, so it survives colour-blindness and print.
 */
import type { ReactNode } from "react";
import { DIR_GLYPH, DIR_LABEL, dirOf, pct, type Conclusion as C, type Direction, type Freshness as F } from "../lib/api";

/** ▲ 偏多 / ▼ 偏空 / ● 中性 */
export function Dir({ d, label, className }: { d: Direction; label?: string; className?: string }) {
  return <span className={`dir is-${d}${className ? " " + className : ""}`}>{DIR_GLYPH[d]} {label ?? DIR_LABEL[d]}</span>;
}

/** A signed percentage coloured by its sign. */
export function Sig({ v, digits = 1, size, d }: { v: number | null | undefined; digits?: number; size?: number; d?: Direction }) {
  const dir = d ?? dirOf(v);
  return <span className={`sig is-${dir}`} style={size ? { fontSize: size } : undefined}>{pct(v, digits)}</span>;
}

/** Any reading coloured by an explicit direction (percentiles, σ, levels). */
export function Reading({ label, children, d }: { label: string; children: ReactNode; d?: Direction | null }) {
  return (
    <span className="reading">
      <span className="row-meta">{label}</span>
      <span className={`reading-v${d && d !== "neu" ? " is-" + d : ""}`}>{children}</span>
    </span>
  );
}

/** First line of every analytic section: direction first, sentence second. */
export function Conclusion({ c, lead, children }: { c: C | null | undefined; lead?: boolean; children?: ReactNode }) {
  if (!c) return null;
  return (
    <div className={`concl${lead ? " is-lead" : ""}`}>
      <Dir d={c.direction} />
      <span className="concl-text">{children ?? c.text}</span>
    </div>
  );
}

/** 截至 … · 窗口 … · extra */
export function AsOf({ date, horizon, extra }: { date: string | null | undefined; horizon?: string | null; extra?: string | null }) {
  const bits = [date ? `截至 ${date.slice(5)} 收盘` : null, horizon ? `窗口 ${horizon}` : null, extra ?? null].filter(Boolean) as string[];
  return (
    <span className="asof">
      {bits.map((b, i) => (
        <span key={i}>{i > 0 && <span className="sep">·</span>}{b}</span>
      ))}
    </span>
  );
}

export function Fresh({ f }: { f: F | null | undefined }) {
  if (!f) return <span className="fresh">—</span>;
  return <span className={`fresh is-${f.state}`}>{f.label}</span>;
}

/** Section head: eyebrow left, as-of / actions right. */
export function Head({ title, right, accent }: { title: ReactNode; right?: ReactNode; accent?: boolean }) {
  return (
    <div className="head">
      <span className={`eyebrow${accent ? " is-accent" : ""}`}>{title}</span>
      {right && <span className="head-right">{right}</span>}
    </div>
  );
}
