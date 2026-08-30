#!/usr/bin/env python3
"""Read-only Markdown governance checker for serenity_quant_research."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS_PATH = ROOT / "docs/manual/document-governance-exceptions.json"

STABLE_FIELDS = [
    "Project",
    "Document type",
    "Status",
    "Owner",
    "Last updated",
    "Source of truth",
]
OPERATIONS_FIELDS = [
    "Project",
    "Task",
    "Timestamp (UTC)",
    "Owner",
    "Route",
    "Source of truth",
]
CANONICAL_PREAMBLE_KEYS = [
    "Plan approval",
    "Git baseline",
    "Accepted-effective Rounds",
    "Active Round",
    "Branch",
    "Approval authority",
    "Approval scope",
]
CANONICAL_METADATA_KEYS = ["Route", "Canonical Plan", "Canonical orchestration"]
DOCUMENT_TYPE_VALUES = {
    "manual-reference",
    "human-manual",
    "intake",
    "product-spec",
    "product-contract",
    "research-baseline",
    "external-reference-summary",
    "guide",
    "index",
    "template",
    "orchestration",
    "plan-pointer",
    "other",
}
STATUS_VALUES = {"draft", "active", "approved", "superseded", "archived", "external-reference"}
ROUTE_VALUES = {"direct-execute", "plan", "review-only", "needs-extension", "fixed-round-plan"}
ROOT_SPECIAL = {"AGENTS.md"}
README_RE = re.compile(r"README\.md$")
KEBAB_MD_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
DATE_SLUG_RE = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
DATE_REVIEW_RE = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*-review\.md$")
ROUND_WORKLOG_RE = re.compile(r"research-experience-reboot-r([1-9][0-9]*)\.md$")
ROUND_REVIEW_RE = re.compile(r"research-experience-reboot-r([1-9][0-9]*)-independent-review\.md$")
MD_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
REF_LINK_RE = re.compile(r"^\s*\[[^\]]+\]:\s+(\S+)")


@dataclass
class Issue:
    severity: str
    path: str
    reason: str


@dataclass
class CheckResult:
    passes: list[str] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    failures: list[Issue] = field(default_factory=list)
    legacy: list[Issue] = field(default_factory=list)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_exceptions() -> dict:
    if not EXCEPTIONS_PATH.exists():
        return {"canonicalPlans": [], "supersededPlanPointers": [], "legacyExceptions": [], "excluded": []}
    with EXCEPTIONS_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)
    data.setdefault("canonicalPlans", [])
    data.setdefault("supersededPlanPointers", [])
    data.setdefault("legacyExceptions", [])
    data.setdefault("excluded", [])
    return data


def validate_exception_file(data: dict, result: CheckResult) -> None:
    seen: set[str] = set()
    for entry in data.get("legacyExceptions", []):
        path = entry.get("path", "")
        rules = entry.get("rules", [])
        reason = entry.get("reason", "")
        lifecycle = entry.get("lifecycle", "")
        if not path or path.startswith("/") or ".." in Path(path).parts:
            result.failures.append(Issue("error", "docs/manual/document-governance-exceptions.json", f"invalid legacy exception path {path!r}"))
        if path in seen:
            result.failures.append(Issue("error", "docs/manual/document-governance-exceptions.json", f"duplicate legacy exception for {path}"))
        seen.add(path)
        if any(ch in path for ch in "*?["):
            result.failures.append(Issue("error", "docs/manual/document-governance-exceptions.json", f"legacy exception must be precise, not wildcard: {path}"))
        if not rules or not all(isinstance(rule, str) for rule in rules):
            result.failures.append(Issue("error", "docs/manual/document-governance-exceptions.json", f"legacy exception for {path} has no precise rules"))
        if not reason:
            result.failures.append(Issue("error", "docs/manual/document-governance-exceptions.json", f"legacy exception for {path} has no reason"))
        if lifecycle == "permanent":
            if not entry.get("permanent reason"):
                result.failures.append(Issue("error", "docs/manual/document-governance-exceptions.json", f"permanent exception for {path} lacks permanent reason"))
        elif not entry.get("review-after"):
            result.failures.append(Issue("error", "docs/manual/document-governance-exceptions.json", f"non-permanent exception for {path} lacks review-after"))


def is_excluded(path: str, data: dict) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in data.get("excluded", []))


def legacy_entry(path: str, data: dict) -> dict | None:
    for entry in data.get("legacyExceptions", []):
        if entry.get("path") == path:
            return entry
    return None


def has_rule(path: str, rule: str, data: dict) -> bool:
    entry = legacy_entry(path, data)
    return bool(entry and rule in entry.get("rules", []))


def iter_markdown(data: dict) -> list[Path]:
    paths: set[Path] = set()
    for root_file in ["AGENTS.md", "Harness_manual.md", "README.md"]:
        p = ROOT / root_file
        if p.exists():
            paths.add(p)
    for base in ["docs", "operations", "assets/templates"]:
        d = ROOT / base
        if d.exists():
            paths.update(d.rglob("*.md"))
    return sorted(p for p in paths if not is_excluded(rel(p), data))


def file_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def h2_headings(lines: list[str]) -> list[tuple[int, str]]:
    out = []
    in_fence = False
    for idx, line in enumerate(lines):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("## ") and not line.startswith("### "):
            out.append((idx, line[3:].strip()))
    return out


def parse_metadata(lines: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    heads = h2_headings(lines)
    md_indices = [idx for idx, title in heads if title == "Metadata"]
    if not md_indices:
        return [], []
    start = md_indices[0] + 1
    end = len(lines)
    for idx, _ in heads:
        if idx > md_indices[0]:
            end = idx
            break
    entries: list[tuple[str, str]] = []
    raw_keys: list[str] = []
    for line in lines[start:end]:
        m = re.match(r"-\s+([^:：]+)[:：]\s*(.*)$", line.strip())
        if m:
            key = m.group(1).strip()
            entries.append((key, m.group(2).strip()))
            raw_keys.append(key)
    return entries, raw_keys


def first_metadata_ok(path: str, lines: list[str], data: dict) -> tuple[bool, str]:
    if path in ROOT_SPECIAL:
        return True, "root AGENTS.md uses managed/project sections"
    heads = h2_headings(lines)
    if not heads:
        return False, "missing H2 section; expected ## Metadata"
    if heads[0][1] == "Metadata":
        return True, "first H2 is Metadata"
    if path in data.get("canonicalPlans", []):
        titles = [title for _, title in heads]
        if "Metadata" in titles and heads[0][1] == "Metadata":
            return True, "canonical plan metadata present"
        return False, "canonical Plan must keep ## Metadata after approved preamble"
    if re.match(r"operations/work_logs/research-experience-reboot-r[1-9][0-9]*\.md$", path):
        return True, "fixed-Round work log parser preamble allowed"
    if re.match(r"operations/reviews/research-experience-reboot-r[1-9][0-9]*-independent-review\.md$", path):
        return True, "fixed-Round review parser preamble allowed"
    if has_rule(path, "metadata", data):
        return True, "legacy metadata exception"
    return False, f"first H2 is ## {heads[0][1]}, expected ## Metadata"


def required_fields_for(path: str, data: dict) -> list[str]:
    if path in ROOT_SPECIAL or path in data.get("canonicalPlans", []):
        return []
    if path.startswith("operations/") and not path.startswith("operations/orchestration/") and path not in data.get("supersededPlanPointers", []) and path not in data.get("canonicalPlans", []):
        if DATE_SLUG_RE.search(path) or DATE_REVIEW_RE.search(path):
            return OPERATIONS_FIELDS
    return STABLE_FIELDS


def enum_values(value: str, allow_alternatives: bool) -> list[str]:
    values = [value]
    if allow_alternatives:
        values = value.split("|")
    return [item.strip().strip("`") for item in values if item.strip()]


def check_enum_field(path: str, key: str, value: str, allowed: set[str], result: CheckResult) -> None:
    allow_alternatives = path.startswith("assets/templates/")
    values = enum_values(value, allow_alternatives)
    if not values or any(item not in allowed for item in values):
        allowed_text = ", ".join(sorted(allowed))
        result.failures.append(Issue("error", path, f"Metadata field {key} must be one of: {allowed_text}"))


def check_metadata_enums(path: str, entries: list[tuple[str, str]], result: CheckResult) -> None:
    for key, value in entries:
        if key == "Document type":
            check_enum_field(path, key, value, DOCUMENT_TYPE_VALUES, result)
        elif key == "Status":
            check_enum_field(path, key, value, STATUS_VALUES, result)
        elif key == "Route":
            check_enum_field(path, key, value, ROUTE_VALUES, result)


def check_metadata(path: str, lines: list[str], data: dict, result: CheckResult) -> None:
    heads = h2_headings(lines)
    metadata_count = sum(1 for _, title in heads if title == "Metadata")
    if metadata_count > 1:
        result.failures.append(Issue("error", path, "duplicate ## Metadata sections"))
    if has_rule(path, "metadata", data):
        entry = legacy_entry(path, data) or {}
        result.legacy.append(Issue("legacy", path, f"metadata exception: {entry.get('reason', 'legacy preserve')}"))
        return
    ok, reason = first_metadata_ok(path, lines, data)
    if not ok:
        result.failures.append(Issue("error", path, reason))
    entries, keys = parse_metadata(lines)
    if entries:
        check_metadata_enums(path, entries, result)
    fields = required_fields_for(path, data)
    if not fields:
        return
    if not entries:
        result.failures.append(Issue("error", path, "missing parseable Metadata bullet fields"))
        return
    seen: set[str] = set()
    for key in keys:
        if key in seen:
            result.failures.append(Issue("error", path, f"duplicate Metadata field {key}"))
        seen.add(key)
    prefix = keys[: len(fields)]
    if prefix != fields:
        result.failures.append(Issue("error", path, f"Metadata fields must start in order: {', '.join(fields)}"))
    for key in fields:
        val = next((value for k, value in entries if k == key), "")
        if not val:
            result.failures.append(Issue("error", path, f"Metadata field {key} is missing or empty"))


def check_h1(path: str, lines: list[str], result: CheckResult) -> None:
    if not lines or not lines[0].startswith("# "):
        result.failures.append(Issue("error", path, "file must start with an H1 (# Title)"))


def check_naming(path: str, data: dict, result: CheckResult) -> None:
    name = Path(path).name
    if has_rule(path, "naming", data):
        entry = legacy_entry(path, data) or {}
        result.legacy.append(Issue("legacy", path, f"naming exception: {entry.get('reason', 'legacy preserve')}"))
        return
    if path in {"AGENTS.md", "Harness_manual.md", "README.md"}:
        return
    if README_RE.search(name):
        return
    if path.startswith("docs/") or path.startswith("assets/templates/"):
        if not KEBAB_MD_RE.fullmatch(name):
            result.failures.append(Issue("error", path, "stable docs/templates must use kebab-case .md filename or README.md"))
        return
    if path.startswith("operations/planning/"):
        if path in data.get("canonicalPlans", []) or path in data.get("supersededPlanPointers", []) or DATE_SLUG_RE.fullmatch(name):
            return
        result.failures.append(Issue("error", path, "planning docs must be canonical, superseded pointer, or YYYY-MM-DD-<slug>.md"))
        return
    if path.startswith("operations/orchestration/"):
        if KEBAB_MD_RE.fullmatch(name) or DATE_SLUG_RE.fullmatch(name):
            return
        result.failures.append(Issue("error", path, "orchestration docs must use kebab-case topic filename or date-prefixed evidence"))
        return
    if path.startswith("operations/work_logs/"):
        if ROUND_WORKLOG_RE.fullmatch(name) or DATE_SLUG_RE.fullmatch(name):
            return
        result.failures.append(Issue("error", path, "work logs must be fixed-Round filename or YYYY-MM-DD-<slug>.md"))
        return
    if path.startswith("operations/reviews/"):
        if ROUND_REVIEW_RE.fullmatch(name) or DATE_REVIEW_RE.fullmatch(name):
            return
        result.failures.append(Issue("error", path, "reviews must be fixed-Round independent-review filename or YYYY-MM-DD-<slug>-review.md"))


def find_label(lines: Iterable[str], key: str) -> str | None:
    for line in lines:
        if line.startswith(key + ":"):
            return line.split(":", 1)[1].strip()
    return None


def check_round_consistency(path: str, lines: list[str], result: CheckResult) -> None:
    name = Path(path).name
    wm = ROUND_WORKLOG_RE.fullmatch(name)
    rm = ROUND_REVIEW_RE.fullmatch(name)
    if not (wm or rm):
        return
    expected = f"R{(wm or rm).group(1)}"
    value = find_label(lines[:12], "Round")
    if not value:
        result.failures.append(Issue("error", path, f"missing top-level Round label for {expected}"))
    elif not re.match(rf"{expected}(\b|\s|$|—|-)", value):
        result.failures.append(Issue("error", path, f"Round label {value!r} does not match filename {expected}"))
    if rm and not has_rule(path, "metadata", load_exceptions()):
        for key in ["Unresolved P0", "Unresolved P1", "Unresolved P2"]:
            count = find_label(lines[:12], key)
            if count is None:
                result.failures.append(Issue("error", path, f"missing {key} label"))
            elif not re.match(r"\d+\b", count):
                result.failures.append(Issue("error", path, f"{key} must start with an integer"))


def metadata_value(entries: list[tuple[str, str]], key: str) -> str | None:
    for k, value in entries:
        if k == key:
            return value.strip().strip("`")
    return None


def check_canonical_plan(path: str, text: str, lines: list[str], data: dict, result: CheckResult) -> None:
    if path not in data.get("canonicalPlans", []):
        return
    for key in CANONICAL_PREAMBLE_KEYS:
        if not any(line.startswith(key + ":") for line in lines[:20]):
            result.failures.append(Issue("error", path, f"canonical Plan missing preamble key {key}"))
    entries, _ = parse_metadata(lines)
    for key in CANONICAL_METADATA_KEYS:
        if metadata_value(entries, key) is None:
            result.failures.append(Issue("error", path, f"canonical Plan missing Metadata key {key}"))
    canonical_path = metadata_value(entries, "Canonical Plan")
    if canonical_path != path:
        result.failures.append(Issue("error", path, f"Canonical Plan metadata must equal {path}"))
    if "## Round Ledger" not in text:
        result.failures.append(Issue("error", path, "canonical Plan missing ## Round Ledger heading"))


def strip_title(target: str) -> str:
    target = target.strip()
    if not target:
        return target
    if target[0] in "'<\"":
        quote = ">" if target[0] == "<" else target[0]
        end = target.find(quote, 1)
        return target[1:end] if end != -1 else target[1:]
    return target.split()[0]


def is_external_link(target: str) -> bool:
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)) or target.startswith("#")


def check_links(path: str, text: str, data: dict, result: CheckResult) -> None:
    warn_only = has_rule(path, "links", data)
    targets = [m.group(1) for m in MD_LINK_RE.finditer(text)]
    targets.extend(m.group(1) for m in REF_LINK_RE.finditer(text))
    for raw in targets:
        target = unquote(strip_title(raw))
        if not target or is_external_link(target):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        if target.startswith("/"):
            candidate = ROOT / target.lstrip("/")
        else:
            candidate = (ROOT / path).parent / target
        if not candidate.exists():
            issue = Issue("warn" if warn_only else "error", path, f"broken relative Markdown link: {raw}")
            if warn_only:
                result.warnings.append(issue)
            else:
                result.failures.append(issue)


def validate_exception_targets(data: dict, paths: set[str], result: CheckResult) -> None:
    for entry in data.get("legacyExceptions", []):
        p = entry.get("path", "")
        if p and p not in paths and not (ROOT / p).exists():
            result.failures.append(Issue("error", "docs/manual/document-governance-exceptions.json", f"legacy exception target does not exist: {p}"))
    for key in ["canonicalPlans", "supersededPlanPointers"]:
        for p in data.get(key, []):
            if p not in paths and not (ROOT / p).exists():
                result.failures.append(Issue("error", "docs/manual/document-governance-exceptions.json", f"{key} target does not exist: {p}"))


def detect_new_legacy_bypass(data: dict, paths: set[str], result: CheckResult) -> None:
    # New fixed-Round evidence must be deliberately added to the precise exception list or fully pass active metadata.
    allowed = {entry.get("path") for entry in data.get("legacyExceptions", [])}
    for path in paths:
        if re.match(r"operations/(work_logs|reviews)/research-experience-reboot-r[6-9][0-9]*", path) and path not in allowed:
            lines = file_text(ROOT / path).splitlines()
            _, keys = parse_metadata(lines)
            if not keys:
                result.failures.append(Issue("error", path, "new fixed-Round file cannot bypass governance by legacy-style filename; add active Metadata or an approved precise exception"))


def run_checks() -> CheckResult:
    result = CheckResult()
    data = load_exceptions()
    validate_exception_file(data, result)
    paths = iter_markdown(data)
    rel_paths = {rel(p) for p in paths}
    validate_exception_targets(data, rel_paths, result)
    detect_new_legacy_bypass(data, rel_paths, result)
    for path_obj in paths:
        path = rel(path_obj)
        try:
            text = file_text(path_obj)
        except UnicodeDecodeError as exc:
            result.failures.append(Issue("error", path, f"cannot read as UTF-8: {exc}"))
            continue
        lines = text.splitlines()
        check_h1(path, lines, result)
        check_naming(path, data, result)
        check_metadata(path, lines, data, result)
        check_round_consistency(path, lines, result)
        check_canonical_plan(path, text, lines, data, result)
        check_links(path, text, data, result)
        if not any(issue.path == path for issue in result.failures):
            result.passes.append(path)
    return result


def print_report(result: CheckResult) -> None:
    print("Document governance report")
    print(f"PASS: {len(result.passes)}")
    for path in result.passes:
        print(f"  pass: {path}")
    print(f"LEGACY EXCEPTION: {len(result.legacy)}")
    for issue in result.legacy:
        print(f"  legacy: {issue.path} - {issue.reason}")
    print(f"WARN: {len(result.warnings)}")
    for issue in result.warnings:
        print(f"  {issue.severity}: {issue.path} - {issue.reason}")
    print(f"FAIL: {len(result.failures)}")
    for issue in result.failures:
        print(f"  {issue.severity}: {issue.path} - {issue.reason}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check project Markdown document governance.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--report", action="store_true", help="print inventory and return 0")
    mode.add_argument("--check", action="store_true", help="return nonzero on failures")
    args = parser.parse_args(argv)

    result = run_checks()
    print_report(result)
    if args.check and result.failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
