"""数据接入：解析器（离线 fixture）、上传 → 重算 → 读数、候选确认成事件。
不出网；接口形状以 fixture 记录，真接口变了先改 fixture 再改解析器。
Run with `pytest` or `python -m unittest`."""
from __future__ import annotations

import json
import math
import os
import random
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

_tmp = tempfile.mkdtemp()
os.environ["SQR_DB_PATH"] = str(Path(_tmp) / "ingest.sqlite")

from app import insights, market  # noqa: E402
from app.db import connect  # noqa: E402
from app.ingest import candidates as C  # noqa: E402
from app.ingest import crowding as CR  # noqa: E402
from app.ingest import eastmoney, news, quotes, recompute, runner  # noqa: E402
from app.ingest.schema import ensure_schema  # noqa: E402
from app.ingest.symbols import em_secid, quotable, stooq_symbol, yahoo_symbol  # noqa: E402
from app.ingest.upload import upload  # noqa: E402
from app.seed import rebuild  # noqa: E402

EM_KLINE = {"rc": 0, "data": {"code": "300308", "market": 0, "name": "中际旭创", "klines": [
    "2026-09-10,180.00,182.50,184.00,178.80,251234,4512345678.00,2.89,1.39,2.50,2.35",
    "2026-09-11,182.00,181.00,183.30,180.10,201234,3612345678.00,1.76,-0.82,-1.50,1.88"]}}
EM_MARGIN = {"result": {"pages": 1, "data": [{"DATE": "2026-09-11 00:00:00", "SCODE": "300308", "RZYE": 5.2e9, "RQYE": 3.1e7, "RZYEZB": 3.42},
                                             {"date": "2026-09-10 00:00:00", "scode": "300308", "rzye": 5.1e9, "rqye": 3.0e7, "rzyezb": 3.39}]}, "success": True}
EM_HOLDERS = {"result": {"pages": 1, "data": [{"END_DATE": "2026-06-30 00:00:00", "HOLDER_NUM": 123456, "HOLDER_NUM_RATIO": -2.15, "AVG_MARKET_CAP": 512345.6}]}}
EM_VALUE = {"result": {"pages": 1, "data": [{"TRADE_DATE": "2026-09-11 00:00:00", "PE_TTM": 41.2, "PB_MRQ": 9.8, "TOTAL_MARKET_CAP": 2.1e11}]}}
_TS = [int(__import__("datetime").datetime(2026, 9, d, 13, 30, tzinfo=__import__("datetime").timezone.utc).timestamp()) for d in (10, 11)]
YAHOO = {"chart": {"result": [{"meta": {"gmtoffset": -14400}, "timestamp": _TS,
                               "indicators": {"quote": [{"open": [170.0, 171.0], "high": [172, 173], "low": [169, 170], "close": [171.0, 172.5], "volume": [1e8, 1.2e8]}],
                                              "adjclose": [{"adjclose": [171.0, 172.5]}]}}], "error": None}}
STOOQ = "Date,Open,High,Low,Close,Volume\n2026-09-10,170,172,169,171,100000000\n2026-09-11,171,173,170,172.5,120000000\n"


class ParserTests(unittest.TestCase):
    def test_eastmoney_kline(self):
        with mock.patch.object(quotes.http, "get_json", return_value=EM_KLINE):
            rows = quotes.fetch_eastmoney("0.300308", date(2026, 9, 1))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["date"], "2026-09-10")
        self.assertAlmostEqual(rows[0]["close"], 182.5)
        self.assertAlmostEqual(rows[0]["volume"], 25123400)      # 手 → 股
        self.assertAlmostEqual(rows[1]["turnover_pct"], 1.88)

    def test_eastmoney_datacenter_case_insensitive(self):
        with mock.patch.object(eastmoney.http, "get_json", return_value=EM_MARGIN):
            rows = eastmoney.fetch_margin("300308")
        self.assertEqual([r["date"] for r in rows], ["2026-09-11", "2026-09-10"])
        self.assertAlmostEqual(rows[1]["rz_to_float_pct"], 3.39)
        with mock.patch.object(eastmoney.http, "get_json", return_value=EM_HOLDERS):
            self.assertAlmostEqual(eastmoney.fetch_holders("300308")[0]["change_pct"], -2.15)
        with mock.patch.object(eastmoney.http, "get_json", return_value=EM_VALUE):
            self.assertAlmostEqual(eastmoney.fetch_valuation("300308", date(2026, 1, 1))[0]["pe_ttm"], 41.2)

    def test_yahoo_and_stooq(self):
        with mock.patch.object(quotes.http, "get_json", return_value=YAHOO):
            rows = quotes.fetch_yahoo("NVDA", date(2026, 9, 1))
        self.assertEqual([r["date"] for r in rows], ["2026-09-10", "2026-09-11"])
        self.assertEqual(rows[0]["source"], "yahoo")
        with mock.patch.object(quotes.http, "get", return_value=STOOQ.encode()):
            rows = quotes.fetch_stooq("nvda.us", date(2026, 9, 1))
        self.assertAlmostEqual(rows[1]["close"], 172.5)

    def test_symbols(self):
        a = {"ticker": "300308", "exchange": "SZSE"}
        self.assertEqual(em_secid(a), "0.300308")
        self.assertEqual(yahoo_symbol(a), "300308.SZ")
        self.assertIsNone(stooq_symbol(a))
        self.assertEqual(yahoo_symbol({"ticker": "522", "exchange": "HKEX"}), "0522.HK")
        self.assertEqual(stooq_symbol({"ticker": "NVDA", "exchange": "NASDAQ"}), "nvda.us")
        self.assertFalse(quotable({"ticker": None, "exchange": None}))

    def test_route_fallback(self):
        c = {"id": "global.nvidia", "ticker": "NVDA", "exchange": "NASDAQ"}
        with mock.patch.object(quotes, "fetch_yahoo", side_effect=quotes.http.FetchError("boom")), \
             mock.patch.object(quotes.http, "get", return_value=STOOQ.encode()):
            rows, errors = quotes.fetch_bars(c, date(2026, 9, 1))
        self.assertEqual(rows[0]["source"], "stooq")
        self.assertTrue(errors and errors[0].startswith("yahoo"))

    def test_feed_and_vocab_matching(self):
        rss = b"""<rss><channel><item><title>New 1.6T DR8 module from Innolight</title><link>https://x/a?utm_source=t</link>
                  <pubDate>Mon, 14 Sep 2026 08:00:00 GMT</pubDate><description>silicon photonics &amp; MPO</description></item></channel></rss>"""
        items = news.parse_feed(rss)
        self.assertEqual(items[0]["title"], "New 1.6T DR8 module from Innolight")
        self.assertEqual(news.parse_date(items[0]["date"]), "2026-09-14")
        self.assertEqual(news.norm_url("https://x/a?utm_source=t"), news.norm_url("https://x/a"))
        spec = news.load_spec()
        self.assertEqual(news.categorize("公司拟投资建设泰国封测产线", spec["categories"]), "capex")


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rebuild(Path(os.environ["SQR_DB_PATH"]))
        cls.conn = connect(os.environ["SQR_DB_PATH"])
        ensure_schema(cls.conn)
        rng = random.Random(1)
        d, days = date(2025, 6, 2), []
        while d <= date(2026, 9, 11):
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(days=1)
        cls.days = days
        for cid in ("cn.300308", "cn.688498", "cn.688048", "global.broadcom", "global.nvidia", "cn.002384", "cn.300620", "cn.300394"):
            if not cls.conn.execute("SELECT 1 FROM companies WHERE id=?", (cid,)).fetchone():
                continue
            lvl, rows = 100.0, []
            for dd in days:
                lvl *= 1 + rng.gauss(0.0004, 0.018)
                rows.append({"date": dd.isoformat(), "open": lvl, "high": lvl, "low": lvl, "close": lvl, "volume": rng.uniform(1e6, 3e6),
                             "amount": rng.uniform(1e8, 3e8), "turnover_pct": rng.uniform(1, 6) if cid.startswith("cn.") else None})
            upload(cls.conn, "bars", cid, rows)
        upload(cls.conn, "margin", "cn.300308", [{"date": days[-1 - i].isoformat(), "rz_balance": 1e9 + i * 1e6, "rq_balance": 1e7, "rz_to_float_pct": 3.3} for i in range(6)])
        upload(cls.conn, "holders", "cn.300308", [{"end_date": "2026-06-30", "holder_num": 100000, "change_pct": -1.5, "avg_cap": 4e5}])
        upload(cls.conn, "valuation", "cn.300308", [{"date": dd.isoformat(), "pe_ttm": 30 + 10 * math.sin(i / 40), "pb": 5, "market_cap": 1e11} for i, dd in enumerate(days)])
        cls.out = recompute.recompute_all(cls.conn)
        cls.cr = CR.rebuild_crowding(cls.conn)

    def test_series_and_as_of_are_real(self):
        self.assertEqual(self.out["as_of"], "2026-09-11")
        self.assertFalse(market.is_sample(self.conn))
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM series WHERE is_sample=1").fetchone()[0], 0)
        self.assertTrue(self.conn.execute("SELECT 1 FROM series WHERE instrument LIKE 'basket:%' LIMIT 1").fetchone())

    def test_reactions_recomputed_for_sample_events_with_real_series(self):
        ev = market.list_events(self.conn, company="cn.300308", limit=5)
        self.assertTrue(ev)
        self.assertIsNotNone(ev[0]["reaction"]["t1"])
        self.assertIsNotNone(ev[0]["volume_ratio"])

    def test_crowding_metrics_shape(self):
        cr = market.crowding_for(self.conn, "company:cn.300308")
        self.assertFalse(cr["is_sample"])
        for k in ("ret20_pct_rank", "turnover_pct_rank", "deviation_sigma", "margin_to_float_pct", "holders_change_pct"):
            self.assertIn(k, cr["metrics"])
        self.assertIn(cr["direction"], ("pos", "neg", "neu"))
        v = self.conn.execute("SELECT pe_ttm, pe_pct_rank_5y, is_sample FROM valuation WHERE company_id='cn.300308'").fetchone()
        self.assertEqual(v["is_sample"], 0)
        self.assertTrue(0 <= v["pe_pct_rank_5y"] <= 100)

    def test_candidate_confirm_becomes_event_with_reaction(self):
        item = {"id": news.cand_id("https://t/1"), "date": "2026-09-08", "title": "关于投资建设硅光产线的公告", "url": "https://t/1", "summary": "",
                "source": "巨潮资讯 · 公告", "source_type": "cninfo_announcement", "tier": 0, "weight": 1.0, "evidence": "verified", "category": "capex",
                "companies": [{"companyId": "cn.300308", "name": "中际旭创"}], "part_ids": [], "also_reported_by": []}
        self.assertEqual(news.store(self.conn, item and [item])["new"], 1)
        self.assertEqual(news.store(self.conn, [dict(item, source="讯石光通讯")])["merged"], 1)     # 同 url 只并来源
        r = C.confirm(self.conn, item["id"], note="ok")
        e = market.get_event(self.conn, r["event_id"])
        self.assertEqual(e["source_kind"], "announcement")
        self.assertFalse(e["is_sample"])
        self.assertIsNotNone(e["reaction"]["t1"])
        self.assertEqual(C.list_candidates(self.conn, status="confirmed")[0]["event_id"], r["event_id"])
        C.reopen(self.conn, item["id"])
        self.assertIsNone(market.get_event(self.conn, r["event_id"]))
        nocat = dict(item, id=news.cand_id("https://t/none"), url="https://t/none", category=None)
        news.store(self.conn, [nocat])
        with self.assertRaises(ValueError):
            C.confirm(self.conn, nocat["id"])
        self.assertTrue(C.confirm(self.conn, nocat["id"], category="order")["ok"])

    def test_resonance_for_physical_only_company_uses_its_part(self):
        # 光库科技只在实物层（光源耦合），不在 main 任何层：共振比同部件（天孚通信），不能说「同环节没有跟随」
        self.assertIsNone(self.conn.execute("SELECT 1 FROM exposures WHERE company_id='cn.300620'").fetchone())
        item = {"id": news.cand_id("https://t/fl"), "date": "2026-09-08", "title": "光库科技薄膜铌酸锂调制器送样", "url": "https://t/fl", "summary": "",
                "source": "讯石光通讯", "source_type": "rss", "tier": 1, "weight": 0.8, "evidence": "consensus", "category": "qualification",
                "companies": [{"companyId": "cn.300620", "name": "光库科技"}], "part_ids": [], "also_reported_by": []}
        news.store(self.conn, [item])
        eid = C.confirm(self.conn, item["id"])["event_id"]
        try:
            r = market.resonance(self.conn, eid)
            self.assertIsNone(r["layer"])
            self.assertEqual(r["scope"]["kind"], "part")
            self.assertIn("cn.300394", [p["company"]["id"] for p in r["peers"]])
            text = insights.resonance(r)["text"]
            self.assertNotIn("同环节", text)
            self.assertIn("部件", text)
            # 同行一个都没有时如实说分不清，而不是「没有跟随」
            lone = dict(r, peers=[], same_direction={"k": 1, "n": 1})
            self.assertIn("没有可比的同部件公司", insights.resonance(lone)["text"])
        finally:
            C.reopen(self.conn, item["id"])

    def test_single_event_is_not_called_dispersed(self):
        one = [{"company": {"short_name": "Marvell"}, "category_label": "技术路线", "reaction": {"t1": -0.031}}]
        c = insights.layer_events(one, "DSP")
        self.assertEqual(c["direction"], "neu")
        self.assertNotIn("分散", c["text"])
        self.assertIn("被卖出", c["text"])

    def test_relevance_triage(self):
        src = {"type": "cninfo_announcement"}
        self.assertEqual(news.relevance_of(src, "关于持股5%以上股东减持股份计划的预披露公告", None, []), 0)
        self.assertEqual(news.relevance_of(src, "2026年第三次临时股东大会决议公告", None, []), 0)
        self.assertEqual(news.relevance_of(src, "关于泰国二期 1.6T 硅光模块产线投产的公告", "capex", []), 1)
        self.assertEqual(news.relevance_of(src, "投资者关系活动记录表", None, []), 1)
        self.assertEqual(news.relevance_of({"type": "rss"}, "anything from a vertical feed", None, []), 1)
        routine = {"id": news.cand_id("https://t/r1"), "date": "2026-09-09", "title": "关于股份质押的公告", "url": "https://t/r1", "summary": "",
                   "source": "巨潮资讯 · 公告", "source_type": "cninfo_announcement", "tier": 0, "weight": 1.0, "evidence": "verified", "category": None,
                   "companies": [{"companyId": "cn.300308", "name": "中际旭创"}], "part_ids": [], "also_reported_by": [], "relevance": 0}
        news.store(self.conn, [routine])
        self.assertNotIn(routine["id"], [c["id"] for c in C.list_candidates(self.conn)])
        self.assertIn(routine["id"], [c["id"] for c in C.list_candidates(self.conn, relevant=None)])
        self.assertGreaterEqual(C.counts(self.conn)["pending_routine"], 1)
        self.assertEqual(news.retriage(self.conn)["routine"] >= 1, True)

    def test_status_and_todo(self):
        st = runner.status(self.conn)
        self.assertGreaterEqual(st["with_bars"], 5)
        runner.add_todo(self.conn, "bars", "private.sicoya", "hint", "no route")
        runner.add_todo(self.conn, "bars", "private.sicoya", "hint2", "still")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM ingest_todo").fetchone()[0], 1)
        runner.close_todo(self.conn, "bars", "private.sicoya")
        self.assertEqual(self.conn.execute("SELECT status FROM ingest_todo").fetchone()[0], "done")

    def test_rebuild_keeps_ingested_facts(self):
        n = self.conn.execute("SELECT COUNT(*) FROM bars").fetchone()[0]
        copy = Path(os.environ["SQR_DB_PATH"]).with_name("copy.sqlite")
        self.conn.execute("VACUUM INTO ?", (str(copy),))
        counts = rebuild(copy)
        self.assertEqual(counts["ingest_restored_bars"], n)
        conn = connect(copy)
        self.assertEqual(conn.execute("SELECT value FROM settings WHERE key='sample'").fetchone()[0], "0")
        conn.close()


if __name__ == "__main__":
    unittest.main()
