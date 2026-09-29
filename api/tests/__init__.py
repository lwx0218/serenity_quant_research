"""Set isolation before any test imports app.config (which caches paths at import).

Never inherit the server's SQR_DB_PATH, even when running with runtime.env loaded.
Individual fixtures may select another temporary DB, but the initial cached path
must already be disposable.
"""
import os
import tempfile
from pathlib import Path

_TEST_ROOT = Path(tempfile.mkdtemp(prefix="sqr-tests-"))
os.environ["SQR_DB_PATH"] = str(_TEST_ROOT / "suite.sqlite")
