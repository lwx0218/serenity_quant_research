"""The physical layer: a real object (one shipping module), its parts in signal
order, and the companies standing on each part. Source of truth is
physical/data/*.json (schema 0.2); companies link to the same ids as the
market layer through `companyId`, and the master data main lacks comes from
data/seeds/physical/companies.json.

Read side is here; the seam into the market layer is `part_for_event`."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .config import REPO_ROOT

PHYS_DIR = REPO_ROOT / "physical" / "data"
PHYS_COMPANIES = REPO_ROOT / "data" / "seeds" / "physical" / "companies.json"

SCHEMA = """
CREATE TABLE IF NOT EXISTS physical_objects (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  name_en     TEXT,
  form_factor TEXT,
  as_of       TEXT,
  spec        TEXT,                     -- JSON
  host        TEXT,                     -- JSON hostContext
  stages      TEXT,                     -- JSON [{id,name,order}]
  signal      TEXT                      -- JSON {tx:[…], rx:[…]}
);
CREATE TABLE IF NOT EXISTS physical_parts (
  id          TEXT PRIMARY KEY,
  object_id   TEXT NOT NULL REFERENCES physical_objects(id),
  sort        INTEGER NOT NULL DEFAULT 0,
  name        TEXT NOT NULL,
  name_en     TEXT,
  function    TEXT,
  key_specs   TEXT,                     -- JSON list
  materials   TEXT                      -- JSON list
);
CREATE TABLE IF NOT EXISTS physical_part_companies (
  part_id     TEXT NOT NULL REFERENCES physical_parts(id),
  seq         INTEGER NOT NULL,
  company_id  TEXT,                     -- NULL for placeholders (e.g. 国产 DSP 暂无)
  name        TEXT NOT NULL,
  ticker      TEXT,
  market      TEXT,
  stage       TEXT NOT NULL,
  role        TEXT,
  evidence    TEXT NOT NULL,            -- verified | consensus | candidate
  sources     TEXT,                     -- JSON [{type,title,url,publisher,date,quote}]
  note        TEXT,
  PRIMARY KEY (part_id, seq)
);
CREATE INDEX IF NOT EXISTS ix_ppc_company ON physical_part_companies(company_id);
"""

# 事件类别 → 最相关的产业阶段(一家公司站在多个部件上时用来挑一站)
CATEGORY_STAGES = {
    "capex": ["engine", "module", "device", "chip"],          # 扩产
    "order": ["module", "device", "chip", "engine"],          # 订单合同
    "qualification": ["chip", "device", "engine", "module"],  # 认证导入
    "supply": ["chip", "material", "device", "module"],       # 供需
    "price": ["material", "device", "chip", "module"],        # 涨价
    "roadmap": ["chip", "engine", "device", "module"],        # 技术路线
}
STAGE_RANK = ["material", "chip", "device", "engine", "connect", "module", "equip"]


def import_physical(conn: sqlite3.Connection) -> dict[str, int]:
    conn.executescript("DROP TABLE IF EXISTS physical_part_companies; DROP TABLE IF EXISTS physical_parts; DROP TABLE IF EXISTS physical_objects;")
    conn.executescript(SCHEMA)
    cur = conn.cursor()
    n_obj = n_part = n_link = n_co = 0
    if PHYS_COMPANIES.exists():
        for c in json.loads(PHYS_COMPANIES.read_text(encoding="utf-8")).get("companies", []):
            cur.execute(
                """INSERT OR IGNORE INTO companies
                   (id, name, short_name, ticker, exchange, country_region, universe_layer, coverage_priority, official_url)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (c["id"], c["name"], c.get("shortName", c["name"]), c.get("ticker"), c.get("exchange"),
                 c.get("countryRegion"), c.get("universeLayer"), c.get("coveragePriority"), c.get("officialUrl")),
            )
            n_co += 1
    for f in sorted(PHYS_DIR.glob("module-*.json")) if PHYS_DIR.exists() else []:
        d = json.loads(f.read_text(encoding="utf-8"))
        m = d["module"]
        cur.execute("DELETE FROM physical_part_companies WHERE part_id IN (SELECT id FROM physical_parts WHERE object_id=?)", (m["id"],))
        cur.execute("DELETE FROM physical_parts WHERE object_id=?", (m["id"],))
        cur.execute(
            "INSERT OR REPLACE INTO physical_objects (id, name, name_en, form_factor, as_of, spec, host, stages, signal) VALUES (?,?,?,?,?,?,?,?,?)",
            (m["id"], m["name"], m.get("nameEn"), m.get("formFactor"), d.get("asOf"),
             json.dumps(m.get("spec", {}), ensure_ascii=False), json.dumps(m.get("hostContext", {}), ensure_ascii=False),
             json.dumps(m.get("stages", []), ensure_ascii=False), json.dumps(m.get("signalPath", {}), ensure_ascii=False)),
        )
        n_obj += 1
        order = {s["partId"]: i for i, s in enumerate(m["signalPath"]["tx"])}
        for i, p in enumerate(m["parts"]):
            cur.execute(
                "INSERT INTO physical_parts (id, object_id, sort, name, name_en, function, key_specs, materials) VALUES (?,?,?,?,?,?,?,?)",
                (p["id"], m["id"], order.get(p["id"], 100 + i), p["name"], p.get("nameEn"), p.get("function"),
                 json.dumps(p.get("keySpecs", []), ensure_ascii=False), json.dumps(p.get("materials", []), ensure_ascii=False)),
            )
            n_part += 1
            for j, c in enumerate(p["companies"]):
                cur.execute(
                    "INSERT INTO physical_part_companies (part_id, seq, company_id, name, ticker, market, stage, role, evidence, sources, note) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (p["id"], j, c.get("companyId"), c["name"], c.get("ticker") or None, c.get("market"), c["stage"], c.get("role"), c["evidence"],
                     json.dumps(c.get("sources", []), ensure_ascii=False), c.get("note")),
                )
                n_link += 1
    conn.commit()
    return {"physical_objects": n_obj, "physical_parts": n_part, "physical_links": n_link, "physical_companies": n_co}


# ------------------------------------------------------------------- read
def _j(s: str | None):
    return json.loads(s) if s else None


def list_objects(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT id, name, name_en, form_factor, as_of, host FROM physical_objects ORDER BY id").fetchall()
    out = []
    for r in rows:
        n = conn.execute("SELECT COUNT(*) FROM physical_parts WHERE object_id=?", (r["id"],)).fetchone()[0]
        out.append({"id": r["id"], "name": r["name"], "name_en": r["name_en"], "form_factor": r["form_factor"],
                    "as_of": r["as_of"], "host": _j(r["host"]), "parts": n})
    return out


def _companies_of_part(conn: sqlite3.Connection, part_id: str) -> list[dict]:
    rows = conn.execute(
        """SELECT l.*, c.short_name FROM physical_part_companies l LEFT JOIN companies c ON c.id = l.company_id
           WHERE l.part_id=? ORDER BY l.seq""", (part_id,)).fetchall()
    return [{"company_id": r["company_id"], "name": r["name"], "short_name": r["short_name"], "ticker": r["ticker"],
             "market": r["market"], "stage": r["stage"], "role": r["role"], "evidence": r["evidence"],
             "sources": _j(r["sources"]) or [], "note": r["note"]} for r in rows]


def get_object(conn: sqlite3.Connection, object_id: str) -> dict | None:
    r = conn.execute("SELECT * FROM physical_objects WHERE id=?", (object_id,)).fetchone()
    if not r:
        return None
    parts = []
    for p in conn.execute("SELECT * FROM physical_parts WHERE object_id=? ORDER BY sort", (object_id,)):
        parts.append({"id": p["id"], "sort": p["sort"], "name": p["name"], "name_en": p["name_en"], "function": p["function"],
                      "key_specs": _j(p["key_specs"]) or [], "materials": _j(p["materials"]) or [],
                      "companies": _companies_of_part(conn, p["id"])})
    return {"id": r["id"], "name": r["name"], "name_en": r["name_en"], "form_factor": r["form_factor"], "as_of": r["as_of"],
            "spec": _j(r["spec"]) or {}, "host": _j(r["host"]) or {}, "stages": _j(r["stages"]) or [],
            "signal": _j(r["signal"]) or {"tx": [], "rx": []}, "parts": parts}


def company_parts(conn: sqlite3.Connection, company_id: str) -> list[dict]:
    """Where one company stands: every part (across objects) it is mapped to."""
    rows = conn.execute(
        """SELECT l.part_id, l.stage, l.role, l.evidence, l.sources, l.note, p.name AS part_name, p.sort, p.object_id, o.name AS object_name
           FROM physical_part_companies l JOIN physical_parts p ON p.id = l.part_id JOIN physical_objects o ON o.id = p.object_id
           WHERE l.company_id=? ORDER BY o.id, p.sort, l.seq""", (company_id,)).fetchall()
    out, seen = [], set()
    for r in rows:
        if r["part_id"] in seen:
            continue
        seen.add(r["part_id"])
        out.append({"object_id": r["object_id"], "object_name": r["object_name"], "part_id": r["part_id"], "part_name": r["part_name"],
                    "step": r["sort"] + 1 if r["sort"] < 100 else None, "stage": r["stage"], "role": r["role"], "evidence": r["evidence"],
                    "sources": _j(r["sources"]) or [], "note": r["note"]})
    return out


def part_for_event(conn: sqlite3.Connection, company_id: str | None, category: str | None) -> dict | None:
    """The one part an event most likely lands on: the company's parts, ranked by
    how close their stage is to the event category. None when the company is
    not on any physical object."""
    if not company_id:
        return None
    parts = company_parts(conn, company_id)
    if not parts:
        return None
    pref = CATEGORY_STAGES.get(category or "", STAGE_RANK)
    rank = {s: i for i, s in enumerate(pref)}
    best = min(parts, key=lambda p: (rank.get(p["stage"], 99), p["step"] or 99))
    return {"object_id": best["object_id"], "object_name": best["object_name"], "part_id": best["part_id"],
            "part_name": best["part_name"], "step": best["step"], "stage": best["stage"], "others": len(parts) - 1}
