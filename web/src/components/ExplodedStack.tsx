/**
 * Data-driven exploded view. Each module carries a `visual` kind; this file
 * turns the ordered list into a stack of dimetric slabs, and exposes each
 * layer's anchor so the page can draw leader lines to HTML labels.
 *
 * Geometry is deliberately simple (flat faces, three tones per material) so
 * it reads at any size and re-themes through CSS variables.
 */
import type { CSSProperties, MouseEvent } from "react";

export interface StackLayer {
  id: string;
  visual: string | null;
  label?: string; // short text drawn on the die, if any
}

export interface Pt { x: number; y: number }

/* ---------- projection ---------- */
const CX = 0.95; // x-axis foreshortening
const SY = 0.3;  // elevation
const W = 270;   // base footprint (world units)
const D = 170;
const GAP = 66;  // vertical spacing between layers
const WB = W * 1.08, DB = D * 1.04; // the host board is a little larger
const TOP_T = 20;

export interface StackGeometry {
  width: number;
  height: number;
  ox: number;
  oy: number;
  n: number;
}

export function stackGeometry(n: number): StackGeometry {
  const ox = (WB / 2 + DB / 2) * CX + 6;
  const oy = (W / 2 + D / 2) * SY + (n - 1) * GAP + TOP_T + 8;
  return { ox, oy, n, width: Math.round(ox * 2 + 6), height: Math.round(oy + (WB / 2 + DB / 2) * SY + 12) };
}

function proj(g: StackGeometry, x: number, y: number, z: number): Pt {
  return { x: g.ox + (x - y) * CX, y: g.oy + (x + y) * SY - z };
}

function pts(seq: Pt[]): string {
  return seq.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
}

type Mat = "alu" | "pcb" | "die" | "si" | "gold" | "tan" | "blk";
const face = (m: Mat, f: "t" | "l" | "r"): CSSProperties => ({ fill: `var(--m-${m}-${f})` });

function Slab({
  g, w, d, z, t, m, cx = 0, cy = 0, children,
}: { g: StackGeometry; w: number; d: number; z: number; t: number; m: Mat; cx?: number; cy?: number; children?: React.ReactNode }) {
  const x0 = cx - w / 2, x1 = cx + w / 2, y0 = cy - d / 2, y1 = cy + d / 2, zt = z + t;
  const left = [proj(g, x0, y1, zt), proj(g, x1, y1, zt), proj(g, x1, y1, z), proj(g, x0, y1, z)];
  const right = [proj(g, x1, y0, zt), proj(g, x1, y1, zt), proj(g, x1, y1, z), proj(g, x1, y0, z)];
  const top = [proj(g, x0, y0, zt), proj(g, x1, y0, zt), proj(g, x1, y1, zt), proj(g, x0, y1, zt)];
  return (
    <>
      <polygon points={pts(left)} style={face(m, "l")} />
      <polygon points={pts(right)} style={face(m, "r")} />
      <polygon points={pts(top)} style={face(m, "t")} />
      {children}
    </>
  );
}

function Row({ g, n, bw, bd, z, t, m, cy, span }: { g: StackGeometry; n: number; bw: number; bd: number; z: number; t: number; m: Mat; cy: number; span: number }) {
  const step = span / n, start = -span / 2 + step / 2;
  return (
    <>
      {Array.from({ length: n }, (_, i) => (
        <Slab key={i} g={g} w={bw} d={bd} z={z} t={t} m={m} cx={start + i * step} cy={cy} />
      ))}
    </>
  );
}

function Line({ a, b, stroke, width, opacity }: { a: Pt; b: Pt; stroke: string; width: number; opacity?: number }) {
  return <line x1={a.x.toFixed(1)} y1={a.y.toFixed(1)} x2={b.x.toFixed(1)} y2={b.y.toFixed(1)} style={{ stroke }} strokeWidth={width} strokeLinecap="round" opacity={opacity} />;
}

/** Footprint + thickness per visual kind (used for anchors and hit areas). */
function dims(kind: string | null): { w: number; d: number; t: number } {
  switch (kind) {
    case "lid": return { w: W, d: D, t: TOP_T };
    case "substrate": return { w: W, d: D, t: 12 };
    case "pcb-fingers": return { w: WB, d: DB, t: 10 };
    default: return { w: W * 0.94, d: D * 0.94, t: 7 };
  }
}

export function layerAnchor(g: StackGeometry, index: number, kind: string | null): Pt {
  const z = (g.n - 1 - index) * GAP;
  const { w, d, t } = dims(kind);
  return proj(g, w / 2, -d / 4, z + t / 2);
}

function LayerShape({ g, kind, z, label }: { g: StackGeometry; kind: string | null; z: number; label?: string }) {
  const w = W, d = D;
  const board = (children?: React.ReactNode) => <Slab g={g} w={w * 0.94} d={d * 0.94} z={z} t={7} m="pcb">{children}</Slab>;
  switch (kind) {
    case "lid": {
      const fins = Array.from({ length: 9 }, (_, k) => {
        const yy = -d / 2 + 18 + k * ((d - 36) / 8);
        return <Line key={k} a={proj(g, -w / 2 + 14, yy, z + TOP_T)} b={proj(g, w / 2 - 14, yy, z + TOP_T)} stroke="var(--m-alu-fin)" width={3} />;
      });
      return <Slab g={g} w={w} d={d} z={z} t={TOP_T} m="alu">{fins}</Slab>;
    }
    case "board-die": {
      const c = proj(g, w * 0.06, d * 0.1, z + 7 + 9);
      return board(
        <Slab g={g} w={w * 0.34} d={d * 0.42} z={z + 7} t={9} m="die" cx={w * 0.06} cy={d * 0.1}>
          {label && (
            <text x={c.x.toFixed(1)} y={(c.y + 4).toFixed(1)} textAnchor="middle" style={{ fill: "var(--m-die-txt)", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: "0.12em" }}>
              {label}
            </text>
          )}
        </Slab>,
      );
    }
    case "board-chips":
      return board(
        <>
          <Row g={g} n={4} bw={34} bd={30} z={z + 7} t={6} m="blk" cy={-d * 0.06} span={w * 0.62} />
          <Row g={g} n={4} bw={34} bd={30} z={z + 7} t={6} m="blk" cy={d * 0.24} span={w * 0.62} />
        </>,
      );
    case "board-die-traces": {
      const traces = Array.from({ length: 5 }, (_, k) => {
        const yy = -d * 0.1 + 10 + k * 12;
        return <Line key={k} a={proj(g, -w * 0.16, yy, z + 7 + 5)} b={proj(g, w * 0.28, yy, z + 7 + 5)} stroke="var(--m-si-trace)" width={1} opacity={0.8} />;
      });
      return board(<Slab g={g} w={w * 0.46} d={d * 0.4} z={z + 7} t={5} m="si" cx={w * 0.06} cy={d * 0.1}>{traces}</Slab>);
    }
    case "board-row-gold":
      return board(<Row g={g} n={8} bw={20} bd={26} z={z + 7} t={12} m="gold" cy={d * 0.18} span={w * 0.74} />);
    case "board-row-dark":
      return board(<Row g={g} n={8} bw={20} bd={24} z={z + 7} t={8} m="blk" cy={d * 0.18} span={w * 0.74} />);
    case "board-connector-fibers": {
      const fibers = Array.from({ length: 8 }, (_, k) => {
        const xx = -w * 0.36 + k * ((w * 0.72) / 7);
        const a = proj(g, xx, d * 0.36, z + 7 + 8);
        const b = { x: a.x - 26, y: a.y + 58 };
        const c1 = { x: a.x + 2, y: a.y + 24 };
        const dpath = `M${a.x.toFixed(1)},${a.y.toFixed(1)} C${c1.x.toFixed(1)},${c1.y.toFixed(1)} ${(b.x + 10).toFixed(1)},${(b.y - 26).toFixed(1)} ${b.x.toFixed(1)},${b.y.toFixed(1)}`;
        return <path key={k} d={dpath} fill="none" style={{ stroke: "var(--m-fiber)" }} strokeWidth={2.4} strokeLinecap="round" opacity={0.9} />;
      });
      return board(
        <>
          <Slab g={g} w={w * 0.8} d={d * 0.2} z={z + 7} t={16} m="blk" cy={d * 0.26} />
          {fibers}
        </>,
      );
    }
    case "substrate": {
      const grid = Array.from({ length: 6 }, (_, k) => {
        const yy = -d / 2 + 22 + k * ((d - 44) / 5);
        return <Line key={k} a={proj(g, -w / 2 + 18, yy, z + 12)} b={proj(g, w / 2 - 18, yy, z + 12)} stroke="var(--m-tan-grid)" width={1} />;
      });
      return <Slab g={g} w={w} d={d} z={z} t={12} m="tan">{grid}</Slab>;
    }
    case "pcb-fingers": {
      const n = 14;
      const fingers = Array.from({ length: n }, (_, k) => {
        const xx = -WB / 2 + 22 + k * ((WB - 44) / (n - 1));
        return <Line key={k} a={proj(g, xx, DB / 2 - 4, z + 10)} b={proj(g, xx, DB / 2 - 24, z + 10)} stroke="var(--m-gold-t)" width={5} />;
      });
      return <Slab g={g} w={WB} d={DB} z={z} t={10} m="pcb">{fingers}</Slab>;
    }
    default:
      return board();
  }
}

export interface ExplodedStackProps {
  layers: StackLayer[];
  selectedId?: string | null;
  hoverId?: string | null;
  onSelect?: (id: string) => void;
  onHover?: (id: string | null) => void;
  onBackgroundClick?: () => void;
  /** CSS transform applied to the whole stack (used to re-centre when a layer is selected). */
  transform?: string;
  className?: string;
}

export function ExplodedStack({ layers, selectedId, hoverId, onSelect, onHover, onBackgroundClick, transform, className }: ExplodedStackProps) {
  const g = stackGeometry(layers.length);
  const interactive = Boolean(onSelect);
  const handleBg = (e: MouseEvent) => {
    if (e.target === e.currentTarget) onBackgroundClick?.();
  };
  return (
    <svg
      className={className}
      viewBox={`0 0 ${g.width} ${g.height}`}
      width={g.width}
      height={g.height}
      style={{ display: "block", overflow: "visible", transform, transformOrigin: "0 0", transition: "transform 0.5s cubic-bezier(.2,.7,.2,1)" }}
      role={interactive ? "group" : "img"}
      aria-label="分层结构"
      onClick={handleBg}
    >
      {[...layers].reverse().map((layer, ri) => {
        const i = layers.length - 1 - ri;
        const z = (layers.length - 1 - i) * GAP;
        const isSel = selectedId === layer.id;
        const isDim = Boolean(selectedId) && !isSel;
        const isHover = hoverId === layer.id;
        const style: CSSProperties = {
          opacity: isDim ? "var(--dim)" : 1,
          transform: isSel ? "translateY(-22px)" : isHover && !selectedId ? "translateY(-6px)" : "none",
          filter: isSel ? "drop-shadow(0 18px 14px rgba(0,0,0,0.22))" : "none",
          transition: "opacity 0.35s ease, transform 0.35s cubic-bezier(.2,.7,.2,1), filter 0.35s ease",
          cursor: interactive ? "pointer" : "default",
        };
        return (
          <g
            key={layer.id}
            data-layer={layer.id}
            style={style}
            onClick={interactive ? (e) => { e.stopPropagation(); onSelect?.(layer.id); } : undefined}
            onMouseEnter={onHover ? () => onHover(layer.id) : undefined}
            onMouseLeave={onHover ? () => onHover(null) : undefined}
            tabIndex={interactive ? 0 : undefined}
            role={interactive ? "button" : undefined}
            aria-pressed={interactive ? isSel : undefined}
            onKeyDown={interactive ? (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect?.(layer.id); } } : undefined}
          >
            <LayerShape g={g} kind={layer.visual} z={z} label={layer.label} />
          </g>
        );
      })}
    </svg>
  );
}

/** Anchor points for every layer, in the svg's own pixel space (1:1 when rendered at intrinsic size). */
export function stackAnchors(layers: StackLayer[], selectedId?: string | null): Record<string, Pt> {
  const g = stackGeometry(layers.length);
  const out: Record<string, Pt> = {};
  layers.forEach((l, i) => {
    const a = layerAnchor(g, i, l.visual);
    out[l.id] = selectedId === l.id ? { x: a.x, y: a.y - 22 } : a;
  });
  return out;
}
