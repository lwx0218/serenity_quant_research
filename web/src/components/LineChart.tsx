/**
 * A small indexed line chart (base 100) with event markers, hairline grid,
 * direct end labels and a crosshair tooltip. One or two series: the subject
 * in --accent, the reference (whole-device basket) in --muted.
 */
import { useMemo, useState } from "react";

export interface ChartSeries { key: string; label: string; points: [string, number][]; kind: "subject" | "reference" }
export interface ChartEvent { id?: string; date: string; label: string; value: number; onClick?: () => void; hot?: boolean }

const M = { l: 44, r: 150, t: 14, b: 30 };

function niceTicks(lo: number, hi: number, n: number): number[] {
  const span = hi - lo;
  const raw = span / n;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? raw;
  const start = Math.ceil(lo / step) * step;
  const out: number[] = [];
  for (let v = start; v <= hi + 1e-9; v += step) out.push(Number(v.toFixed(6)));
  return out;
}

function monthTicks(dates: string[]): { x: string; label: string }[] {
  const out: { x: string; label: string }[] = [];
  let last = "";
  for (const d of dates) {
    const ym = d.slice(0, 7);
    if (ym !== last) { out.push({ x: d, label: `${parseInt(d.slice(5, 7), 10)}月` }); last = ym; }
  }
  return out;
}

export function LineChart({ series, events = [], height = 300, width = 800, yTicks = 5 }: { series: ChartSeries[]; events?: ChartEvent[]; height?: number; width?: number; yTicks?: number }) {
  const [hover, setHover] = useState<number | null>(null);
  const dates = useMemo(() => Array.from(new Set(series.flatMap((s) => s.points.map((p) => p[0])))).sort(), [series]);
  const idx = useMemo(() => new Map(dates.map((d, i) => [d, i])), [dates]);
  const values = series.flatMap((s) => s.points.map((p) => p[1]));
  const lo = Math.min(...values), hi = Math.max(...values);
  const pad = (hi - lo) * 0.08 || 1;
  const y0 = lo - pad, y1 = hi + pad;
  const W = width - M.l - M.r, H = height - M.t - M.b;
  const X = (d: string) => M.l + ((idx.get(d) ?? 0) / Math.max(1, dates.length - 1)) * W;
  const Y = (v: number) => M.t + (1 - (v - y0) / (y1 - y0)) * H;
  const ticks = niceTicks(y0, y1, yTicks);
  // labels: stagger when events sit close together, hide past the third level
  const sortedEv = [...events].sort((a, b) => X(a.date) - X(b.date));
  const labelLevel = new Map<string, number>();
  let lastX = -Infinity, level = 0;
  for (const e of sortedEv) {
    const x = X(e.date);
    level = e.hot ? 0 : x - lastX < 56 ? level + 1 : 0;   // the selected event always keeps its label
    labelLevel.set(e.id ?? e.date, level);
    lastX = x;
  }
  const months = monthTicks(dates);
  const hoverDate = hover !== null ? dates[hover] : null;

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} width="100%" style={{ display: "block", overflow: "visible" }} role="img"
      onMouseMove={(e) => {
        const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect();
        const x = ((e.clientX - r.left) / r.width) * width;
        const i = Math.round(((x - M.l) / W) * (dates.length - 1));
        setHover(Math.max(0, Math.min(dates.length - 1, i)));
      }}
      onMouseLeave={() => setHover(null)}>
      {ticks.map((t, i) => (
        <g key={i}>
          <line x1={M.l} x2={width - M.r} y1={Y(t)} y2={Y(t)} stroke="var(--hair)" />
          <text x={M.l - 10} y={Y(t) + 4} textAnchor="end" className="chart-tick">{Math.round(t)}</text>
        </g>
      ))}
      {months.map((m) => (
        <text key={m.x} x={X(m.x)} y={height - 8} className="chart-tick">{m.label}</text>
      ))}
      {series.map((s) => {
        const d = s.points.map((p, i) => `${i ? "L" : "M"}${X(p[0]).toFixed(1)} ${Y(p[1]).toFixed(1)}`).join(" ");
        const last = s.points[s.points.length - 1];
        return (
          <g key={s.key}>
            <path d={d} fill="none" stroke={s.kind === "subject" ? "var(--accent)" : "var(--faint)"} strokeWidth={s.kind === "subject" ? 1.6 : 1.3} strokeLinejoin="round" />
            {last && (
              <text x={X(last[0]) + 10} y={Y(last[1]) + 4} className={`chart-label${s.kind === "reference" ? " is-muted" : ""}`}>
                {s.label} {Math.round(last[1])}
              </text>
            )}
          </g>
        );
      })}
      {events.map((e) => (
        <g key={e.id ?? e.date} onClick={e.onClick} style={e.onClick ? { cursor: "pointer" } : undefined}>
          <circle cx={X(e.date)} cy={Y(e.value)} r={e.hot ? 6 : 4.5} fill="var(--accent)" stroke="var(--bg)" strokeWidth={2} />
          {(labelLevel.get(e.id ?? e.date) ?? 0) < 3 && (
            <text x={X(e.date)} y={Y(e.value) - 12 - 13 * (labelLevel.get(e.id ?? e.date) ?? 0)} textAnchor="middle" className={`chart-ev${e.hot ? " is-hot" : ""}`}>{e.label}</text>
          )}
          <circle cx={X(e.date)} cy={Y(e.value)} r={12} fill="transparent" />
        </g>
      ))}
      {hoverDate && (
        <g pointerEvents="none">
          <line x1={X(hoverDate)} x2={X(hoverDate)} y1={M.t} y2={height - M.b} stroke="var(--hair-2)" />
          {series.map((s) => {
            const p = s.points.find((q) => q[0] === hoverDate);
            return p ? <circle key={s.key} cx={X(p[0])} cy={Y(p[1])} r={3} fill={s.kind === "subject" ? "var(--accent)" : "var(--muted)"} /> : null;
          })}
          <text x={X(hoverDate) + 8} y={M.t + 12} className="chart-tip">
            {hoverDate.slice(5)}
            {series.map((s) => { const p = s.points.find((q) => q[0] === hoverDate); return p ? ` · ${s.label} ${p[1].toFixed(1)}` : ""; })}
          </text>
        </g>
      )}
    </svg>
  );
}
