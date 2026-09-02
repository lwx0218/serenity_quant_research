"""SQLite access. One short-lived connection per request; schema lives here
so a fresh database can always be rebuilt from the seed files."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
  id          TEXT PRIMARY KEY,
  parent_id   TEXT REFERENCES nodes(id),
  kind        TEXT NOT NULL,           -- product | module | part
  sort        INTEGER NOT NULL DEFAULT 0,
  code        TEXT,                    -- short mono code, e.g. SIPH-PIC
  name        TEXT NOT NULL,           -- display name (zh)
  name_en     TEXT,
  name_full   TEXT,                    -- original bilingual name from the research seed
  summary     TEXT,                    -- one line
  description TEXT,                    -- one paragraph
  status      TEXT,                    -- research status from the seed (parts)
  visual      TEXT,                    -- visual kind for the exploded-stack renderer
  eyebrow     TEXT,
  source_note TEXT,
  extra       TEXT                     -- JSON blob (signal path etc.)
);
CREATE INDEX IF NOT EXISTS ix_nodes_parent ON nodes(parent_id, sort);

CREATE TABLE IF NOT EXISTS chain_nodes (
  id           TEXT PRIMARY KEY,
  sort         INTEGER NOT NULL DEFAULT 0,
  name         TEXT NOT NULL,
  display_name TEXT,
  node_type    TEXT,                   -- supply | context
  keywords     TEXT
);

CREATE TABLE IF NOT EXISTS node_chain_links (
  node_id       TEXT NOT NULL REFERENCES nodes(id),
  chain_node_id TEXT NOT NULL REFERENCES chain_nodes(id),
  PRIMARY KEY (node_id, chain_node_id)
);

CREATE TABLE IF NOT EXISTS technologies (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS node_tech_links (
  node_id TEXT NOT NULL REFERENCES nodes(id),
  tech_id TEXT NOT NULL REFERENCES technologies(id),
  PRIMARY KEY (node_id, tech_id)
);

CREATE TABLE IF NOT EXISTS companies (
  id                TEXT PRIMARY KEY,
  name              TEXT NOT NULL,
  short_name        TEXT,
  ticker            TEXT,
  exchange          TEXT,
  country_region    TEXT,
  universe_layer    TEXT,              -- global_anchor | a_share_focus | reference
  coverage_priority TEXT,              -- core | gap_fill | context
  official_url      TEXT
);

CREATE TABLE IF NOT EXISTS sources (
  id         TEXT PRIMARY KEY,
  publisher  TEXT,
  title      TEXT,
  kind       TEXT,
  year_range TEXT,
  url        TEXT,
  note       TEXT
);

CREATE TABLE IF NOT EXISTS exposures (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id     TEXT NOT NULL REFERENCES companies(id),
  chain_node_id  TEXT NOT NULL REFERENCES chain_nodes(id),
  node_id        TEXT REFERENCES nodes(id),      -- optional: a specific module/part
  role           TEXT,
  evidence_level TEXT NOT NULL,                 -- reference | candidate | reviewed
  source_id      TEXT REFERENCES sources(id),
  note           TEXT
);
CREATE INDEX IF NOT EXISTS ix_exposures_chain ON exposures(chain_node_id);
CREATE INDEX IF NOT EXISTS ix_exposures_company ON exposures(company_id);
"""


def connect(path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


@contextmanager
def session(path: Path | str = DB_PATH) -> Iterator[sqlite3.Connection]:
    conn = connect(path)
    try:
        yield conn
    finally:
        conn.close()
