"""python -m app.ingest <job> [--full] [--only rss|cninfo_announcement|cninfo_irm] [--db path]"""
from __future__ import annotations

import argparse
import json
import sys

from .runner import JOBS, run


def main() -> int:
    ap = argparse.ArgumentParser(description="Teardown 数据接入")
    ap.add_argument("job", choices=JOBS)
    ap.add_argument("--full", action="store_true", help="行情全量重拉（首次或修数）")
    ap.add_argument("--only", choices=["rss", "cninfo_announcement", "cninfo_irm"], help="news：只跑一类源")
    ap.add_argument("--db", default=None)
    a = ap.parse_args()
    r = run(a.job, db_path=a.db, full=a.full, only=a.only)
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
