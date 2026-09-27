"""接入层自己的表。都是 CREATE IF NOT EXISTS，可以在已有库上直接加。"""
from __future__ import annotations

import sqlite3

SCHEMA = """
-- 日线：接入层的原始事实。series 表（收盘指数）由它派生，供既有分析代码用。
CREATE TABLE IF NOT EXISTS bars (
  company_id   TEXT NOT NULL REFERENCES companies(id),
  date         TEXT NOT NULL,
  open         REAL, high REAL, low REAL,
  close        REAL NOT NULL,                 -- 前复权收盘
  volume       REAL,                          -- 股 / 份
  amount       REAL,                          -- 成交额（本币）
  turnover_pct REAL,                          -- 换手率 %（海外通常没有）
  source       TEXT NOT NULL,                 -- eastmoney | yahoo | stooq | upload
  PRIMARY KEY (company_id, date)
);
CREATE INDEX IF NOT EXISTS ix_bars_date ON bars(date);

-- 融资余额（A 股）
CREATE TABLE IF NOT EXISTS margin (
  company_id    TEXT NOT NULL REFERENCES companies(id),
  date          TEXT NOT NULL,
  rz_balance    REAL,                         -- 融资余额（元）
  rq_balance    REAL,                         -- 融券余额（元）
  rz_to_float_pct REAL,                       -- 融资余额 / 流通市值 %
  source        TEXT NOT NULL,
  PRIMARY KEY (company_id, date)
);

-- 股东户数（A 股，按报告期）
CREATE TABLE IF NOT EXISTS holders (
  company_id   TEXT NOT NULL REFERENCES companies(id),
  end_date     TEXT NOT NULL,
  holder_num   REAL,
  change_pct   REAL,                          -- 较上期 %
  avg_cap      REAL,                          -- 户均持股市值
  source       TEXT NOT NULL,
  PRIMARY KEY (company_id, end_date)
);

-- 估值日线（PE TTM 等），valuation 表的当前值 + 5 年分位由它算
CREATE TABLE IF NOT EXISTS valuation_daily (
  company_id  TEXT NOT NULL REFERENCES companies(id),
  date        TEXT NOT NULL,
  pe_ttm      REAL,
  pb          REAL,
  market_cap  REAL,
  source      TEXT NOT NULL,
  PRIMARY KEY (company_id, date)
);

-- 事件候选池：自动抓取进来，人确认后才写 events
CREATE TABLE IF NOT EXISTS candidates (
  id            TEXT PRIMARY KEY,             -- cand.<sha1 of url>
  date          TEXT,
  title         TEXT NOT NULL,
  url           TEXT NOT NULL,
  summary       TEXT,
  source        TEXT NOT NULL,                -- 信息源名
  source_type   TEXT NOT NULL,                -- rss | cninfo_announcement | cninfo_irm | upload
  tier          INTEGER NOT NULL,
  evidence      TEXT NOT NULL,                -- verified | consensus | candidate（由 tier 决定）
  category      TEXT,                         -- capex | order | qualification | supply | price | roadmap
  company_id    TEXT REFERENCES companies(id),
  companies     TEXT,                         -- JSON [{companyId,name}]（命中多家时）
  part_ids      TEXT,                         -- JSON [partId]
  also_reported_by TEXT,                      -- JSON [source]
  status        TEXT NOT NULL DEFAULT 'pending',   -- pending | confirmed | rejected
  event_id      TEXT,                         -- 确认后对应的 events.id
  decided_at    TEXT,
  decided_note  TEXT,
  fetched_at    TEXT NOT NULL,
  relevance     INTEGER NOT NULL DEFAULT 1    -- 1 值得看 / 0 例行公告（减持、质押、会议……），收件箱默认不显示
);
CREATE INDEX IF NOT EXISTS ix_cand_status ON candidates(status, date);

-- 每次抓取的记录
CREATE TABLE IF NOT EXISTS ingest_runs (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  job         TEXT NOT NULL,                  -- quotes | crowding | valuation | news | recompute | daily
  started_at  TEXT NOT NULL,
  finished_at TEXT,
  ok          INTEGER,                        -- 1 成功 0 失败 NULL 进行中
  summary     TEXT,                           -- JSON 计数
  error       TEXT
);

-- 抓不到的，交给 AI（PI + web-access）去网页端取，再 POST /api/ingest/upload 交回
CREATE TABLE IF NOT EXISTS ingest_todo (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  kind        TEXT NOT NULL,                  -- bars | margin | holders | valuation | candidates
  company_id  TEXT,
  hint        TEXT,                           -- 人话：去哪里取、取什么
  reason      TEXT,                           -- 自动抓取失败的原因
  status      TEXT NOT NULL DEFAULT 'open',   -- open | done | dropped
  created_at  TEXT NOT NULL,
  done_at     TEXT,
  UNIQUE (kind, company_id)
);
"""


MIGRATIONS = [("candidates", "relevance", "INTEGER NOT NULL DEFAULT 1")]


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    for table, col, decl in MIGRATIONS:                     # 已有库上补列
        cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        if col not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")
    conn.commit()
