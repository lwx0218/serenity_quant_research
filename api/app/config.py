"""Paths and settings. Everything is relative to the repository root so the
api works the same from a checkout, a venv or a container."""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_DIR = Path(os.environ.get("SQR_SEED_DIR", REPO_ROOT / "data" / "seeds" / "cpo"))
DB_PATH = Path(os.environ.get("SQR_DB_PATH", REPO_ROOT / "data" / "sqr.sqlite"))
WEB_DIST = Path(os.environ.get("SQR_WEB_DIST", REPO_ROOT / "web" / "dist"))

# Ordered from weakest to strongest. The UI shows the strongest level a
# company has for a given chain node.
EVIDENCE_LEVELS = ("reference", "candidate", "reviewed")
