"""Judgement notes: Markdown files with a small YAML front matter, kept in
data/notes/ so they can be opened and edited in Obsidian as well as here.

    ---
    subject: cpo.mod.pic          # node id | company id
    kind: module                  # module | part | company | chain
    title: 硅光芯片
    direction: pos                # pos | neg | neu
    stance: 看多环节,超配国内封测/耦合
    updated: 2026-08-28
    since: 2026-07-01             # tracking start for 自判断起 readings
    window_until: 2027-03-31
    window_label: 2 个季度(至 2027-Q1)
    threshold_pct: 3
    track: [basket:cpo.mod.pic, company:cn.300308]
    indicators: [...]
    invalidation: [...]
    position: 触发验证 → 加环节篮子;触发失效 → 减至基准
    ---
    thesis body in Markdown, [[中际旭创]] links allowed

    ## 问题
    - [ ] open question (2026-08-28)
    - [x] answered question (2026-08-20)

Only the YAML subset above is supported (scalars and lists of scalars), so
there is no dependency on a YAML library and the files round-trip cleanly.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from . import config

LIST_KEYS = ("track", "indicators", "invalidation")
KNOWN_KEYS = ("subject", "kind", "title", "direction", "stance", "updated", "since", "window_until",
              "window_label", "threshold_pct", "position", "sample") + LIST_KEYS

_Q_RE = re.compile(r"^- \[( |x|X)\]\s*(.+?)(?:\s*\((\d{4}-\d{2}-\d{2})\))?\s*$")
_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


@dataclass
class Note:
    subject: str
    kind: str = "module"
    title: str = ""
    direction: str = "neu"
    stance: str = ""
    updated: str | None = None
    since: str | None = None
    window_until: str | None = None
    window_label: str | None = None
    threshold_pct: float = 3.0
    position: str | None = None
    sample: bool = False
    track: list[str] = field(default_factory=list)
    indicators: list[str] = field(default_factory=list)
    invalidation: list[str] = field(default_factory=list)
    body: str = ""
    questions: list[dict[str, Any]] = field(default_factory=list)
    path: str = ""
    extra: dict[str, Any] = field(default_factory=dict)   # front-matter keys we do not interpret
    tail: str = ""                                         # anything after the 问题 list (kept verbatim)

    def to_dict(self) -> dict[str, Any]:
        d = {k: getattr(self, k) for k in KNOWN_KEYS}
        d.update({"body": self.body, "questions": self.questions, "path": self.path,
                  "links": [m.group(1) for m in _LINK_RE.finditer(self.body)]})
        return d


# ------------------------------------------------------------------ front matter
def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] == '"':
        return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(v) >= 2 and v[0] == v[-1] and v[0] == "'":
        return v[1:-1]
    return v


def _quote(v: object) -> str:
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v)
    if s == "" or s[0] in "[\"'{&*!|>%@`#" or ": " in s or s.endswith(":") or s.strip() != s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n", 1)
    if len(parts) < 2:
        return {}, text
    rest = parts[1]
    end = re.search(r"^---\s*$", rest, flags=re.M)
    if not end:
        return {}, text
    head, body = rest[: end.start()], rest[end.end():].lstrip("\n")
    meta: dict[str, Any] = {}
    key: str | None = None
    for line in head.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and line.strip().startswith("- ") and key:
            if not isinstance(meta.get(key), list):
                meta[key] = []
            meta[key].append(_unquote(line.strip()[2:]))
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            key = k.strip()
            v = v.strip()
            if v == "":
                meta[key] = None          # becomes a list if indented "- " items follow
            elif v.startswith("[") and v.endswith("]"):
                meta[key] = [_unquote(x) for x in v[1:-1].split(",") if x.strip()]
            else:
                meta[key] = _unquote(v)
    return meta, body


def dump_front_matter(meta: dict[str, Any]) -> str:
    lines = ["---"]
    order = list(KNOWN_KEYS) + [k for k in meta if k not in KNOWN_KEYS]   # Obsidian tags/aliases etc. survive a save
    for k in order:
        if k not in meta or meta[k] in (None, "", []):
            continue
        v = meta[k]
        if isinstance(v, list):
            lines.append(f"{k}:")
            lines.extend(f"  - {_quote(x)}" for x in v)
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        else:
            lines.append(f"{k}: {_quote(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------- questions
def split_questions(body: str) -> tuple[str, list[dict[str, Any]], str]:
    """Return (thesis body without the 问题 section, parsed questions, anything after them)."""
    m = re.search(r"^##\s*问题\s*$", body, flags=re.M)
    if not m:
        return body.strip(), [], ""
    thesis, qsec = body[: m.start()].strip(), body[m.end():]
    qs = []
    tail_lines: list[str] = []
    seen_item = False
    for line in qsec.splitlines():
        mm = _Q_RE.match(line.strip())
        if mm and not tail_lines:
            seen_item = True
            qs.append({"index": len(qs) + 1, "text": mm.group(2).strip(), "status": "verified" if mm.group(1).lower() == "x" else "open",
                       "date": mm.group(3)})
        elif line.strip() == "" and not tail_lines:
            continue
        elif seen_item or tail_lines or line.strip():
            tail_lines.append(line)
    return thesis, qs, "\n".join(tail_lines).strip()


def render_questions(qs: list[dict[str, Any]]) -> str:
    if not qs:
        return ""
    out = ["", "## 问题", ""]
    for q in qs:
        box = "x" if q.get("status") == "verified" else " "
        tail = f" ({q['date']})" if q.get("date") else ""
        out.append(f"- [{box}] {q['text']}{tail}")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------- file i/o
def note_path(subject: str, notes_dir: Path | None = None) -> Path:
    notes_dir = notes_dir or config.NOTES_DIR
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", subject)
    return notes_dir / f"{safe}.md"


def _display_path(p: Path, notes_dir: Path) -> str:
    """data/notes/x.md when the notes dir sits inside the repo, else the full path."""
    root = notes_dir.parent.parent
    return str(p.relative_to(root)) if root in p.parents else str(p)


def load_note(subject: str, notes_dir: Path | None = None) -> Note | None:
    notes_dir = notes_dir or config.NOTES_DIR
    p = note_path(subject, notes_dir)
    if not p.exists():
        return None
    return parse_note(p.read_text(encoding="utf-8"), path=_display_path(p, notes_dir))


def parse_note(text: str, path: str = "") -> Note:
    meta, body = parse_front_matter(text)
    thesis, qs, tail = split_questions(body)
    n = Note(subject=str(meta.get("subject", "")), body=thesis, questions=qs, path=path, tail=tail,
             extra={k: v for k, v in meta.items() if k not in KNOWN_KEYS})
    for k in ("kind", "title", "direction", "stance", "updated", "since", "window_until", "window_label", "position"):
        if meta.get(k) not in (None, ""):
            setattr(n, k, str(meta[k]))
    if meta.get("threshold_pct") not in (None, ""):
        try:
            n.threshold_pct = float(meta["threshold_pct"])
        except (TypeError, ValueError):
            pass
    n.sample = str(meta.get("sample", "")).lower() in ("true", "1", "yes")
    for k in LIST_KEYS:
        v = meta.get(k)
        if isinstance(v, list):
            setattr(n, k, [str(x) for x in v])
        elif isinstance(v, str) and v:
            setattr(n, k, [v])
    return n


def render_note(n: Note) -> str:
    meta = {k: getattr(n, k) for k in KNOWN_KEYS}
    meta["sample"] = n.sample or None
    meta.update({k: v for k, v in n.extra.items() if k not in meta})
    out = dump_front_matter(meta) + "\n" + n.body.strip() + "\n" + render_questions(n.questions)
    if n.tail:
        out += "\n" + n.tail.strip() + "\n"
    return out


def save_note(n: Note, notes_dir: Path | None = None) -> Path:
    notes_dir = notes_dir or config.NOTES_DIR
    notes_dir.mkdir(parents=True, exist_ok=True)
    p = note_path(n.subject, notes_dir)
    n.updated = n.updated or date.today().isoformat()
    p.write_text(render_note(n), encoding="utf-8")
    return p


def list_notes(notes_dir: Path | None = None) -> list[Note]:
    notes_dir = notes_dir or config.NOTES_DIR
    if not notes_dir.exists():
        return []
    out = []
    for p in sorted(notes_dir.glob("*.md")):
        try:
            n = parse_note(p.read_text(encoding="utf-8"), path=_display_path(p, notes_dir))
        except Exception:  # a hand-edited file should never take the API down
            continue
        if n.subject:
            out.append(n)
    return out


def excerpt(body: str, n: int = 40) -> str:
    text = _LINK_RE.sub(lambda m: m.group(2) or m.group(1), body).replace("\n", " ").strip()
    return text if len(text) <= n else text[:n].rstrip() + "……"
