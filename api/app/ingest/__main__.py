"""python -m app.ingest <job> [--full] [--only rss|cninfo_announcement|cninfo_irm] [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--db path]"""
from __future__ import annotations

import argparse
import json
import signal
import sys

from .runner import JOBS, run


def _terminate(signum, frame):
    raise SystemExit(128 + signum)


def main() -> int:
    ap = argparse.ArgumentParser(description="Teardown 数据接入")
    ap.add_argument("job", choices=JOBS, help="triage:对现有候选跑一遍自动入账规则;backfill:巨潮公告历史回填")
    ap.add_argument("--full", action="store_true", help="行情全量重拉（首次或修数）")
    ap.add_argument("--only", choices=["rss", "cninfo_announcement", "cninfo_irm"], help="news：只跑一类源")
    ap.add_argument("--since", default=None, help="backfill:起(默认一年前)")
    ap.add_argument("--until", default=None, help="backfill:止(默认今天)")
    ap.add_argument("--db", default=None)
    a = ap.parse_args()
    # CLI only: API 后台线程不注册信号；TERM 让 runner 收尾自己这一条 run。
    previous = signal.signal(signal.SIGTERM, _terminate)
    try:
        r = run(a.job, db_path=a.db, full=a.full, only=a.only, since=a.since, until=a.until)
    finally:
        signal.signal(signal.SIGTERM, previous)
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
