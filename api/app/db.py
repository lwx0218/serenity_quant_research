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

-- ---------------------------------------------------------------- market layer
-- Everything below is dated. `as_of` in settings is the last close the data
-- knows about; every reading the API returns carries it.
CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT
);

-- 卡口事件: something public that could move capital toward a part of the chain.
CREATE TABLE IF NOT EXISTS events (
  id             TEXT PRIMARY KEY,
  date           TEXT NOT NULL,          -- knowable date (YYYY-MM-DD, trading day)
  company_id     TEXT REFERENCES companies(id),
  node_id        TEXT REFERENCES nodes(id),        -- when the subject is a layer, not a company
  chain_node_id  TEXT REFERENCES chain_nodes(id),
  source_kind    TEXT NOT NULL,          -- announcement | irm | news | official | filing
  source_title   TEXT,
  source_url     TEXT,
  category       TEXT NOT NULL,          -- capex | order | qualification | supply | price | buyback | roadmap | other
  title          TEXT NOT NULL,
  summary        TEXT,
  volume_ratio   REAL,                   -- T+1 volume / 20d average
  turnover_pct_rank REAL,                -- T+1 turnover percentile (60d)
  status         TEXT NOT NULL DEFAULT 'candidate',   -- candidate | reviewed | ignored
  is_sample      INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_events_date ON events(date);
CREATE INDEX IF NOT EXISTS ix_events_company ON events(company_id, date);

-- an event touches every layer its subject is exposed to
CREATE TABLE IF NOT EXISTS event_layers (
  event_id TEXT NOT NULL REFERENCES events(id),
  node_id  TEXT NOT NULL REFERENCES nodes(id),
  PRIMARY KEY (event_id, node_id)
);

-- price reaction per horizon, relative to the reference basket
CREATE TABLE IF NOT EXISTS reactions (
  event_id      TEXT NOT NULL REFERENCES events(id),
  horizon       INTEGER NOT NULL,        -- 1, 3, 5, 20 trading days
  abs_return    REAL,
  excess_basket REAL,                    -- vs the subject's layer basket
  excess_product REAL,                   -- vs the whole-device basket
  computed_at   TEXT,
  PRIMARY KEY (event_id, horizon)
);

-- daily index series (close, base 100 at series start) for companies and baskets
CREATE TABLE IF NOT EXISTS series (
  instrument TEXT NOT NULL,              -- company:<id> | basket:<node_id> | basket:<product_id>
  date       TEXT NOT NULL,
  value      REAL NOT NULL,
  is_sample  INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (instrument, date)
);

-- crowding / fragility readings: state quantities, recomputed daily
CREATE TABLE IF NOT EXISTS crowding (
  instrument TEXT NOT NULL,
  as_of      TEXT NOT NULL,
  window_days INTEGER NOT NULL DEFAULT 20,
  metrics    TEXT NOT NULL,              -- JSON
  is_sample  INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (instrument, as_of)
);

CREATE TABLE IF NOT EXISTS valuation (
  company_id TEXT PRIMARY KEY REFERENCES companies(id),
  as_of      TEXT NOT NULL,
  pe_ttm     REAL,
  pe_pct_rank_5y REAL,
  is_sample  INTEGER NOT NULL DEFAULT 0
);

-- verification actions taken from the inbox (audit trail)
CREATE TABLE IF NOT EXISTS verifications (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  kind       TEXT NOT NULL,              -- upgrade | ignore | accept | reject
  event_id   TEXT REFERENCES events(id),
  exposure_id INTEGER REFERENCES exposures(id),
  note       TEXT,
  created_at TEXT NOT NULL
);
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
