"""Set isolation before any test imports app.config (which caches paths at import).

Never inherit the server's SQR_DB_PATH, even when running with runtime.env loaded.
Individual fixtures may select another temporary DB, but the initial cached path
must already be disposable.

两道防线(真数据评审 §4.3.1,硬要求):
1. 这里在导入 app 之前把 SQR_DB_PATH 指到临时文件,并设 SQR_TESTING=1;
   app.db.connect() 看到 SQR_TESTING / PYTEST_CURRENT_TEST 时只许连临时目录里的库,默认库与生产库一律抛错。
2. 所有用例继承 IsolatedTestCase:setUpClass / setUp 先确认 SQR_DB_PATH 与 app.config.DB_PATH
   都在临时目录里,不在就强制换成新的临时文件。
"""
import os
import tempfile
import unittest
from pathlib import Path

_TEST_ROOT = Path(tempfile.mkdtemp(prefix="sqr-tests-"))
os.environ["SQR_DB_PATH"] = str(_TEST_ROOT / "suite.sqlite")
os.environ["SQR_TESTING"] = "1"


def _is_temp(path: str | Path) -> bool:
    return Path(path).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())


def ensure_temp_db() -> Path:
    """SQR_DB_PATH 与 app.config.DB_PATH 都必须是临时文件;不是就换成一个新的临时文件。返回当前的测试库路径。"""
    from app import config
    if not (_is_temp(os.environ.get("SQR_DB_PATH", "")) and _is_temp(config.DB_PATH)):
        path = Path(tempfile.mkdtemp(prefix="db-", dir=_TEST_ROOT)) / "test.sqlite"
        os.environ["SQR_DB_PATH"] = str(path)
        config.DB_PATH = path
    return Path(config.DB_PATH)


class IsolatedTestCase(unittest.TestCase):
    """setUpClass / setUp 先强制测试库在临时目录(子类覆盖时要先调 super())。"""

    @classmethod
    def setUpClass(cls):
        ensure_temp_db()
        super().setUpClass()

    def setUp(self):
        ensure_temp_db()
        super().setUp()
