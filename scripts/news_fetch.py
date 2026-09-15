#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""卡口事件候选池（命令行入口）。逻辑在 api/app/ingest/news.py，候选写进库的 candidates 表，
收件箱里确认后才成事件。

    python3 scripts/news_fetch.py --probe        # 先跑这个：每个 RSS 源能不能打开、几条
    python3 scripts/news_fetch.py                # 抓取 + 打标 + 入库
    python3 scripts/news_fetch.py --only rss     # 只跑一类源（rss / cninfo_announcement / cninfo_irm）
    python3 scripts/news_fetch.py --dry-run      # 只列源和词表大小
    python3 scripts/news_fetch.py --json out.json  # 顺便把本次候选导出成 JSON

等价于 `cd api && python -m app.ingest news`。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "api"))

from app import config  # noqa: E402
from app.db import connect  # noqa: E402
from app.ingest import news  # noqa: E402
from app.ingest.schema import ensure_schema  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", choices=["rss", "cninfo_announcement", "cninfo_irm"])
    ap.add_argument("--probe", action="store_true", help="只探测每个源能不能打开、返回多少条，不写库")
    ap.add_argument("--json", help="把本次候选另存为 JSON")
    args = ap.parse_args()
    spec = news.load_spec()
    if args.probe:
        news.probe(spec)
        return 0
    if not config.DB_PATH.exists():
        print(f"库还没建：先 `cd api && python -m app.seed --rebuild`（{config.DB_PATH}）")
        return 1
    conn = connect(config.DB_PATH)
    ensure_schema(conn)
    if args.dry_run:
        companies, parts = news.build_vocab(conn)
        print(f"词表：{len(companies)} 个公司别名，{len(parts)} 个部件关键词")
        for s in spec["sources"]:
            if not args.only or s["type"] == args.only:
                print(f"  [{s['tier']}] {s['type']:20s} {s['name']}")
        return 0
    items = news.collect(conn, only=args.only, spec=spec)
    r = news.store(conn, items)
    print(f"入库：新增 {r['new']}，合并来源 {r['merged']}（本次 {r['seen']} 条）→ 收件箱「候选」")
    if args.json:
        Path(args.json).write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
