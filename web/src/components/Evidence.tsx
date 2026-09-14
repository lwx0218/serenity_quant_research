import { PHYS_EVIDENCE_LABEL, PHYS_SOURCE_LABEL, type PhysEvidence, type PhysSource } from "../lib/api";

/**
 * 证据级 + 它的来源。The label is the link: click opens the strongest source
 * (announcement > irm > filing > official > media > report); the title carries
 * the quote so hovering shows what the source actually says. No badge, no colour.
 */
const RANK: PhysSource["type"][] = ["announcement", "irm", "filing", "official", "media", "report"];
export function best(sources: PhysSource[] | undefined): PhysSource | null {
  if (!sources || sources.length === 0) return null;
  return sources.slice().sort((a, b) => RANK.indexOf(a.type) - RANK.indexOf(b.type) + (a.partial ? 10 : 0) - (b.partial ? 10 : 0))[0];
}

export function Evidence({ level, sources, note }: { level: PhysEvidence; sources?: PhysSource[]; note?: string | null }) {
  const s = best(sources);
  const label = PHYS_EVIDENCE_LABEL[level];
  const color = level === "candidate" ? "var(--muted)" : "var(--ink-2)";
  if (!s) return <span className="row-meta" style={{ fontSize: 11, color }} title={note ?? undefined}>{label}</span>;
  const tip = [PHYS_SOURCE_LABEL[s.type] + (s.publisher ? ` · ${s.publisher}` : "") + (s.date ? ` · ${s.date}` : ""), s.title ?? "", s.quote ? `“${s.quote}”` : "", note ?? ""].filter(Boolean).join("\n");
  return (
    <a href={s.url} target="_blank" rel="noreferrer" className="row-meta ev-link" style={{ fontSize: 11, color }} title={tip}>
      {label}
      <span className="ev-src">{PHYS_SOURCE_LABEL[s.type]}{(sources?.length ?? 0) > 1 ? ` +${sources!.length - 1}` : ""}</span>
    </a>
  );
}
