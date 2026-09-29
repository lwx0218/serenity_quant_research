"""Offline regression tests for page commits, interruption and job isolation."""
from __future__ import annotations

import io
import os
import sqlite3
import signal
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

os.environ["SQR_DB_PATH"] = str(Path(tempfile.mkdtemp()) / "unused.sqlite")

from app.db import connect
from app.ingest import crowding, news, progress, runner
from app.ingest import __main__ as cli
from app.seed import rebuild


class IngestReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "test.sqlite"
        rebuild(self.db, include_sample=False)
        self.conn = connect(self.db)
        self.addCleanup(self.conn.close)
        self.target = {"companyId": "cn.300308", "name": "中际旭创", "ticker": "300308"}
        self.messages = []
        patch = mock.patch.object(news, "backfill_companies", return_value=[self.target])
        patch.start(); self.addCleanup(patch.stop)

    def page(self, aid="a", more=True):
        return {"announcements": [{"announcementId": aid, "announcementTitle": "中际旭创：关于投资建设硅光模块产线的公告",
                                  "announcementTime": 1783296000000, "adjunctUrl": f"finalpage/{aid}.PDF",
                                  "secCode": "300308", "secName": "中际旭创"}], "hasMore": more}

    def backfill(self):
        return news.backfill(self.conn, "2026-07-01", "2026-07-31", log=self.messages.append, pause=0)

    def count(self):
        with sqlite3.connect(self.db) as reader:
            return reader.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]

    def test_committed_page_survives_later_fetch_failure_and_rerun_is_idempotent(self):
        def fetch(*args):
            page = args[-1]
            self.assertIn(f"页 {page}", self.messages[-1])  # before network request
            if page == 2:
                self.assertEqual(self.count(), 1)  # another connection sees page 1
                raise news.http.FetchError("later page failed")
            return self.page()
        with mock.patch.object(news, "cninfo_page", side_effect=fetch):
            first = self.backfill()
            second = self.backfill()
        self.assertFalse(first["complete"])
        self.assertEqual((first["new"], first["fetched"], first["segments_failed"]), (1, 1, 1))
        self.assertEqual((second["new"], second["fetched"]), (0, 1))
        self.assertEqual(self.count(), 1)
        self.assertEqual(first["last_position"]["page"], 2)
        self.assertTrue(any("已提交" in m and "fetched 1" in m for m in self.messages))

    def test_keyboard_interrupt_preserves_prior_page(self):
        with mock.patch.object(news, "cninfo_page", side_effect=[self.page(), KeyboardInterrupt()]):
            with self.assertRaises(KeyboardInterrupt):
                self.backfill()
        self.assertEqual(self.count(), 1)

    def test_storage_failure_is_not_network_failure_and_rolls_back_current_page(self):
        original = news.store
        def store(conn, items):
            if self.count() == 0:
                return original(conn, items)
            conn.execute("INSERT INTO settings VALUES ('unfinished-page', '1')")
            raise sqlite3.OperationalError("disk full")
        with mock.patch.object(news, "cninfo_page", side_effect=[self.page(), self.page("b", False)]), \
                mock.patch.object(news, "store", side_effect=store):
            with self.assertRaisesRegex(sqlite3.OperationalError, "disk full"):
                self.backfill()
        self.assertEqual(self.count(), 1)
        self.assertIsNone(self.conn.execute("SELECT value FROM settings WHERE key='unfinished-page'").fetchone())
        self.assertFalse(any("ERR" in m for m in self.messages))

    def test_page_cap_and_invalid_responses_are_incomplete(self):
        with mock.patch.object(news, "CNINFO_MAX_PAGES", 1), \
                mock.patch.object(news, "cninfo_page", return_value={**self.page(), "totalpages": 1}):
            out = self.backfill()
        self.assertFalse(out["complete"])
        self.assertEqual(out["new"], 1)
        for data in ({}, {"announcements": None}, {"announcements": []}, {"announcements": [{}]},
                     {"announcements": [], "hasMore": True}):
            with self.subTest(data=data), mock.patch.object(news, "cninfo_page", return_value=data):
                out = self.backfill()
                self.assertFalse(out["complete"])
                self.assertEqual(out["segments_failed"], 1)
        for data in ({"announcements": [], "hasMore": False}, {"announcements": None, "totalAnnouncement": 0}):
            with self.subTest(data=data), mock.patch.object(news, "cninfo_page", return_value=data):
                self.assertTrue(self.backfill()["complete"])

    def test_run_rolls_back_only_uncommitted_data_and_does_not_touch_other_runs(self):
        other = self.conn.execute("INSERT INTO ingest_runs (job, started_at) VALUES ('news', '2026-07-01')").lastrowid
        self.conn.commit()
        def job(conn, **kw):
            conn.execute("INSERT INTO settings VALUES ('committed-unit', '1')")
            conn.commit()
            conn.execute("INSERT INTO settings VALUES ('unfinished-unit', '1')")
            raise RuntimeError("failed after commit")
        with mock.patch.object(runner, "job_backfill", side_effect=job):
            out = runner.run("backfill", db_path=self.db, log=self.messages.append)
        self.assertFalse(out["ok"])
        self.assertIsNotNone(self.conn.execute("SELECT value FROM settings WHERE key='committed-unit'").fetchone())
        self.assertIsNone(self.conn.execute("SELECT value FROM settings WHERE key='unfinished-unit'").fetchone())
        current = self.conn.execute("SELECT * FROM ingest_runs WHERE id=?", (out["run_id"],)).fetchone()
        self.assertEqual(current["ok"], 0)
        self.assertIsNotNone(current["finished_at"])
        self.assertIsNone(self.conn.execute("SELECT finished_at FROM ingest_runs WHERE id=?", (other,)).fetchone()[0])

    def test_run_records_keyboard_interrupt_then_reraises(self):
        with mock.patch.object(runner, "job_backfill", side_effect=KeyboardInterrupt()):
            with self.assertRaises(KeyboardInterrupt):
                runner.run("backfill", db_path=self.db, log=self.messages.append)
        row = self.conn.execute("SELECT * FROM ingest_runs ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(row["ok"], 0)
        self.assertIn("KeyboardInterrupt", row["error"])

    def test_incomplete_fetch_marks_run_failed_but_preserves_summary(self):
        with mock.patch.object(runner, "job_backfill", return_value={"fetch": {"complete": False, "new": 1}}):
            out = runner.run("backfill", db_path=self.db, log=self.messages.append)
        self.assertFalse(out["ok"])
        row = self.conn.execute("SELECT * FROM ingest_runs WHERE id=?", (out["run_id"],)).fetchone()
        self.assertEqual(row["ok"], 0)
        self.assertIn('"new": 1', row["summary"])

    def test_margin_is_committed_before_holders_request(self):
        def holders(code):
            self.assertFalse(self.conn.in_transaction)
            with sqlite3.connect(self.db) as reader:
                self.assertEqual(reader.execute("SELECT COUNT(*) FROM margin").fetchone()[0], 1)
            raise KeyboardInterrupt()
        row = {"date": "2026-07-01", "rz_balance": 1, "rq_balance": 2, "rz_to_float_pct": 3, "source": "test"}
        with mock.patch.object(crowding.eastmoney, "fetch_margin", return_value=[row]), \
                mock.patch.object(crowding.eastmoney, "fetch_holders", side_effect=holders):
            with self.assertRaises(KeyboardInterrupt):
                crowding.ingest_margin_holders(self.conn, {"id": "cn.300308", "ticker": "300308", "exchange": "SZSE"},
                                              log=self.messages.append)

    def test_cli_sigterm_records_own_run_and_restores_handler(self):
        def interrupted(conn, **kw):
            cli._terminate(signal.SIGTERM, None)
        with mock.patch.object(runner, "job_backfill", side_effect=interrupted), \
                mock.patch.object(cli.signal, "signal", return_value=signal.SIG_DFL) as register, \
                mock.patch.object(cli.sys, "argv", ["ingest", "backfill", "--db", str(self.db)]), \
                redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as exc:
                cli.main()
        self.assertEqual(exc.exception.code, 128 + signal.SIGTERM)
        self.assertEqual(register.call_args_list, [mock.call(signal.SIGTERM, cli._terminate),
                                                  mock.call(signal.SIGTERM, signal.SIG_DFL)])
        row = self.conn.execute("SELECT * FROM ingest_runs ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(row["ok"], 0)
        self.assertIn("SystemExit", row["error"])

    def test_valuation_storage_failure_is_fatal_and_not_a_source_todo(self):
        self.conn.execute("""CREATE TRIGGER fail_valuation BEFORE INSERT ON valuation_daily
                          WHEN NEW.date='2026-07-02' BEGIN SELECT RAISE(ABORT, 'write failure'); END""")
        self.conn.commit()
        rows = [{"date": d, "pe_ttm": 1, "pb": 2, "market_cap": 3, "source": "test"}
                for d in ("2026-07-01", "2026-07-02")]
        company = {"id": "cn.300308", "ticker": "300308", "exchange": "SZSE"}
        with mock.patch.object(runner, "companies", return_value=[company]), \
                mock.patch.object(runner.eastmoney, "fetch_valuation", return_value=rows):
            out = runner.run("valuation", db_path=self.db, log=self.messages.append)
        self.assertFalse(out["ok"])
        self.assertIn("write failure", out["error"])
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM valuation_daily").fetchone()[0], 0)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM ingest_todo WHERE kind='valuation'").fetchone()[0], 0)

    def test_progress_flushes_redirected_output(self):
        stream = mock.Mock(wraps=io.StringIO())
        with redirect_stdout(stream):
            progress.log("page committed")
        stream.flush.assert_called_once()
        self.assertIn("page committed", stream.getvalue())
