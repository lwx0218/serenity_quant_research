"""Import the seed files into SQLite.

    python -m app.seed --rebuild      # drop and recreate data/sqr.sqlite

Three inputs, three kinds of knowledge:
- cpo-research-seed.json        research facts: stable IDs, taxonomy, chain, links
- cpo-presentation.json         how the Explorer talks about them (names, copy, visuals)
- cpo-reference-exposures.json  company ↔ chain-node placements from a public infographic
                                (evidence level `reference`)
- cpo-sample-market.json        style-sample market layer (events, series, crowding);
                                skipped with --no-sample. See market_seed.py.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from .config import DB_PATH, REPO_ROOT, SEED_DIR
from .db import connect, init_schema
from .market_seed import import_market
from .physical import import_physical


def _load(seed_dir: Path, name: str) -> dict:
    with open(seed_dir / name, encoding="utf-8") as f:
        return json.load(f)


def _split_bilingual(name: str) -> tuple[str, str | None]:
    if " / " in name:
        zh, en = name.split(" / ", 1)
        return zh.strip(), en.strip()
    return name.strip(), None


def import_seed(conn: sqlite3.Connection, seed_dir: Path = SEED_DIR, include_sample: bool = True) -> dict[str, int]:
    research = _load(seed_dir, "cpo-research-seed.json")
    pres = _load(seed_dir, "cpo-presentation.json")
    ref = _load(seed_dir, "cpo-reference-exposures.json")

    cur = conn.cursor()
    counts: dict[str, int] = {}

    # ---- product node ------------------------------------------------------
    product = pres["product"]
    cur.execute(
        """INSERT OR REPLACE INTO nodes
           (id, parent_id, kind, sort, code, name, name_en, name_full, summary, description,
            status, visual, eyebrow, source_note, extra)
           VALUES (?, NULL, 'product', 0, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?)""",
        (
            product["id"], product["id"].upper(), product["name"], product.get("nameEn"),
            research["theme"]["name"], product.get("summary"), product.get("eyebrow"),
            product.get("sourceNote"), json.dumps({"signalPath": product.get("signalPath")}, ensure_ascii=False),
        ),
    )

    # ---- modules -----------------------------------------------------------
    pres_modules = pres.get("modules", {})
    for m in research["modules"]:
        zh, en = _split_bilingual(m["name"])
        p = pres_modules.get(m["id"], {})
        cur.execute(
            """INSERT OR REPLACE INTO nodes
               (id, parent_id, kind, sort, code, name, name_en, name_full, summary, description,
                status, visual, eyebrow, source_note, extra)
               VALUES (?, ?, 'module', ?, ?, ?, ?, ?, ?, ?, NULL, ?, NULL, NULL, NULL)""",
            (
                m["id"], product["id"], m["sortOrder"], p.get("code"), p.get("name", zh),
                p.get("nameEn", en), m["name"], p.get("summary"), p.get("description"), p.get("visual"),
            ),
        )
    counts["modules"] = len(research["modules"])

    # ---- parts -------------------------------------------------------------
    for part in research["parts"]:
        cur.execute(
            """INSERT OR REPLACE INTO nodes
               (id, parent_id, kind, sort, code, name, name_en, name_full, summary, description,
                status, visual, eyebrow, source_note, extra)
               VALUES (?, ?, 'part', ?, NULL, ?, NULL, ?, ?, NULL, ?, NULL, NULL, NULL, NULL)""",
            (part["id"], part["moduleId"], part["sortOrder"], part["name"], part["name"],
             part.get("functionSummary"), part.get("researchStatus")),
        )
    counts["parts"] = len(research["parts"])

    # ---- chain nodes -------------------------------------------------------
    pres_chain = pres.get("chainNodes", {})
    for c in research["chainNodes"]:
        p = pres_chain.get(c["id"], {})
        cur.execute(
            "INSERT OR REPLACE INTO chain_nodes (id, sort, name, display_name, node_type, keywords) VALUES (?,?,?,?,?,?)",
            (c["id"], c["sortOrder"], c["name"], p.get("displayName", c["name"]), c.get("nodeType"), p.get("keywords")),
        )
    counts["chain_nodes"] = len(research["chainNodes"])

    for link in research["partChainMappings"]:
        cur.execute("INSERT OR IGNORE INTO node_chain_links (node_id, chain_node_id) VALUES (?, ?)",
                    (link["partId"], link["chainNodeId"]))

    # ---- technologies ------------------------------------------------------
    for t in research["technologyLinks"]:
        cur.execute("INSERT OR REPLACE INTO technologies (id, name, description) VALUES (?,?,?)",
                    (t["id"], t["name"], t.get("description")))
    for link in research["partTechnologyMappings"]:
        cur.execute("INSERT OR IGNORE INTO node_tech_links (node_id, tech_id) VALUES (?, ?)",
                    (link["partId"], link["technologyId"]))
    counts["technologies"] = len(research["technologyLinks"])

    # ---- companies ---------------------------------------------------------
    short_names = ref.get("shortNames", {})
    for c in research["companies"]:
        cur.execute(
            """INSERT OR REPLACE INTO companies
               (id, name, short_name, ticker, exchange, country_region, universe_layer, coverage_priority, official_url)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (c["id"], c["name"], short_names.get(c["id"], c["name"]), c.get("ticker"), c.get("exchange"),
             c.get("countryRegion"), c.get("universeLayer"), c.get("coveragePriority"), c.get("officialUrl")),
        )
    for c in ref.get("companies", []):
        cur.execute(
            """INSERT OR IGNORE INTO companies
               (id, name, short_name, ticker, exchange, country_region, universe_layer, coverage_priority, official_url)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (c["id"], c["name"], c.get("shortName", c["name"]), c.get("ticker"), c.get("exchange"),
             c.get("countryRegion"), c.get("universeLayer", "reference"), c.get("coveragePriority"), c.get("officialUrl")),
        )
    counts["companies"] = cur.execute("SELECT COUNT(*) FROM companies").fetchone()[0]

    # ---- sources + exposures ----------------------------------------------
    src = ref["source"]
    cur.execute(
        "INSERT OR REPLACE INTO sources (id, publisher, title, kind, year_range, url, note) VALUES (?,?,?,?,?,?,?)",
        (src["id"], src.get("publisher"), src.get("title"), src.get("kind"), src.get("yearRange"), src.get("url"), src.get("note")),
    )
    cur.execute("DELETE FROM exposures")
    level = ref.get("evidenceLevel", "reference")
    n = 0
    for group in ref.get("exposures", []):
        for cid in group["companyIds"]:
            cur.execute(
                """INSERT INTO exposures (company_id, chain_node_id, node_id, role, evidence_level, source_id, note)
                   VALUES (?, ?, NULL, ?, ?, ?, ?)""",
                (cid, group["chainNodeId"], group.get("role", "代表企业"), level, src["id"], None),
            )
            n += 1

    # The research seed carries one worked example with a real source: keep it as
    # the first `candidate` exposure so all three evidence levels exist in the data.
    ex = research.get("exampleChain")
    if ex:
        s = ex["source"]
        cur.execute(
            "INSERT OR REPLACE INTO sources (id, publisher, title, kind, year_range, url, note) VALUES (?,?,?,?,?,?,?)",
            (s["id"], s.get("publisher"), s.get("title"), "official-website", None, s.get("url"),
             f"source level {s.get('sourceLevel')}" if s.get("sourceLevel") else None),
        )
        e = ex["exposure"]
        cur.execute(
            """INSERT INTO exposures (company_id, chain_node_id, node_id, role, evidence_level, source_id, note)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ex["companyId"], ex["chainNodeId"], ex["partId"], e.get("role"),
             "candidate" if e.get("verificationState") == "candidate" else "reviewed",
             s["id"], e.get("scopeNote")),
        )
        n += 1
    counts["exposures"] = n
    conn.commit()

    counts.update(import_market(conn, seed_dir, include_sample=include_sample))
    counts.update(import_physical(conn))
    if include_sample:                  # 样例层的部件篮子要等实物导入之后才能算
        from .ingest.recompute import sample_part_baskets
        counts.update(sample_part_baskets(conn))
    return counts


INGEST_TABLES = ("bars", "margin", "holders", "valuation_daily", "candidates", "ingest_runs", "ingest_todo")
COMPANY_TABLES = ("bars", "margin", "holders", "valuation_daily", "candidates", "ingest_todo")     # 带 company_id 的
RENAMES = REPO_ROOT / "data" / "seeds" / "physical" / "company-renames.json"


def company_renames() -> dict[str, str]:
    if not RENAMES.exists():
        return {}
    return json.loads(RENAMES.read_text(encoding="utf-8")).get("renames", {})


def _cols(conn: sqlite3.Connection, schema: str, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA {schema}.table_info({table})")]


def _restore_ingest(conn: sqlite3.Connection, src: str) -> dict[str, int]:
    """把附加库 src 里的接入层数据倒回新库:旧公司 id 先换成新 id;仍然对不上任何公司的行跳过并计数,
    不让整次重建失败。按两边都有的列插入(旧版 keep 少列也倒得回来);主键已有的行不覆盖(先倒的为准)。"""
    out = {"ingest_renamed": 0, "ingest_orphans": 0}
    tables = [t for t in INGEST_TABLES if _cols(conn, src, t)]
    for old, new in company_renames().items():
        for t in (t for t in COMPANY_TABLES if t in tables):
            cur = conn.execute(f"UPDATE OR IGNORE {src}.{t} SET company_id=? WHERE company_id=?", (new, old))
            out["ingest_renamed"] += cur.rowcount
            conn.execute(f"DELETE FROM {src}.{t} WHERE company_id=?", (old,))        # 新旧两个 id 撞主键时留新的
        if "candidates" in tables and "companies" in _cols(conn, src, "candidates"):
            conn.execute(f"UPDATE {src}.candidates SET companies=REPLACE(companies, ?, ?) WHERE companies LIKE ?",
                         (f'"{old}"', f'"{new}"', f'%"{old}"%'))
    for t in tables:
        cols = ", ".join(c for c in _cols(conn, src, t) if c in set(_cols(conn, "main", t)))
        where = ""
        if t in COMPANY_TABLES and t != "ingest_todo":       # 这些表的 company_id 有外键
            orphans = "company_id IS NOT NULL AND company_id NOT IN (SELECT id FROM main.companies)"
            out["ingest_orphans"] += conn.execute(f"SELECT COUNT(*) FROM {src}.{t} WHERE {orphans}").fetchone()[0]
            where = f" WHERE NOT ({orphans})"
        conn.execute(f"INSERT OR IGNORE INTO main.{t} ({cols}) SELECT {cols} FROM {src}.{t}{where}")
    conn.commit()
    return out


def keep_files(db_path: Path) -> list[Path]:
    """已有的 keep 文件(上一次重建中途失败时,接入数据可能只在这里),新的在前。"""
    return sorted(db_path.parent.glob(db_path.stem + ".ingest-keep*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)


def rebuild(db_path: Path = DB_PATH, seed_dir: Path = SEED_DIR, include_sample: bool = True) -> dict[str, int]:
    """Drop and recreate from the seeds. Ingested facts (bars, candidates, …) are
    carried over: they are not seeds, they are what was fetched.

    接入数据先存进一个带时间戳的 keep 文件,新库建好再倒回;全部倒回成功才删 keep。
    已经存在的 keep 文件是上一次失败留下的,不删,当作第二来源一起倒回(当前库的在前,同一主键以它为准)。"""
    from datetime import datetime

    from .ingest.schema import ensure_schema as ensure_ingest_schema
    db_path = Path(db_path)
    leftovers = keep_files(db_path)
    snapshot = None
    if db_path.exists():
        snapshot = db_path.with_name(f"{db_path.stem}.ingest-keep.{datetime.now():%Y%m%dT%H%M%S%f}.sqlite")
        conn = connect(db_path)
        try:
            ensure_ingest_schema(conn)
            conn.execute("ATTACH DATABASE ? AS keep", (str(snapshot),))
            for t in INGEST_TABLES:
                conn.execute(f"CREATE TABLE keep.{t} AS SELECT * FROM {t}")
            conn.commit()
            conn.execute("DETACH DATABASE keep")
        finally:
            conn.close()
        db_path.unlink()
    sources = ([snapshot] if snapshot else []) + leftovers
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path)
    try:
        init_schema(conn)
        ensure_ingest_schema(conn)
        counts = import_seed(conn, seed_dir, include_sample=include_sample)
        if sources:
            restored = {"ingest_renamed": 0, "ingest_orphans": 0}
            for i, src in enumerate(sources):
                conn.execute("ATTACH DATABASE ? AS ?", (str(src), f"keep{i}"))
                for k, v in _restore_ingest(conn, f"keep{i}").items():
                    restored[k] += v
                conn.execute(f"DETACH DATABASE keep{i}")
            counts.update(restored)
            counts["ingest_keep_files"] = len(sources)
            counts["ingest_leftover_keep_files"] = len(leftovers)
            for src in sources:                   # 全部倒回之后才删
                src.unlink()
            from .ingest.candidates import replay
            counts.update(replay(conn))           # 事件不倒回:按已入账的候选重新写出来
            n_bars = conn.execute("SELECT COUNT(*) FROM bars").fetchone()[0]
            counts["ingest_restored_bars"] = n_bars
            if n_bars:
                from .ingest import crowding as CR
                from .ingest import recompute
                counts.update(recompute.recompute_all(conn))
                counts.update(CR.rebuild_crowding(conn))
        return counts
    finally:
        conn.close()


def ensure_database(db_path: Path = DB_PATH, seed_dir: Path = SEED_DIR) -> None:
    """Create and seed the database on first run; leave an existing one alone."""
    if not Path(db_path).exists():
        rebuild(db_path, seed_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Seed the research database")
    ap.add_argument("--rebuild", action="store_true", help="delete and recreate the database")
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--seed-dir", default=str(SEED_DIR))
    ap.add_argument("--no-sample", action="store_true", help="skip the style-sample market layer")
    args = ap.parse_args()
    if args.rebuild:
        print(rebuild(Path(args.db), Path(args.seed_dir), include_sample=not args.no_sample))
    else:
        ensure_database(Path(args.db), Path(args.seed_dir))
        print("ok", args.db)
