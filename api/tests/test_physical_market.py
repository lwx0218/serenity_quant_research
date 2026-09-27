"""物理页「资金投票」:部件篮子规则、反应 / 共振 / 偏离的参照按部件、首页结论按部件、两个接口。
夹具是 tests/scenario_physical.py 的演示库;另建一个没有行情的空库,看「—」的情况。
Run with `pytest` or `python -m unittest`."""
from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date
from pathlib import Path

_tmp = Path(tempfile.mkdtemp())
os.environ.setdefault("SQR_DB_PATH", str(_tmp / "unused.sqlite"))

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics as A  # noqa: E402
from app import insights, market  # noqa: E402
from app.db import connect  # noqa: E402
from app.deps import get_conn  # noqa: E402
from app.ingest import recompute  # noqa: E402
from app.ingest.recompute import MIN_PART_BASKET, part_basket_members, part_members  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import rebuild  # noqa: E402
from tests.scenario_physical import AS_OF, OBJECT, build_demo_db  # noqa: E402


class PartMarketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = build_demo_db(_tmp / "scenario.sqlite")
        app.dependency_overrides[get_conn] = lambda: cls.conn
        cls.client = TestClient(app)          # 不进 lifespan:不碰 config.DB_PATH

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_conn, None)
        cls.conn.close()

    # ---------------------------------------------------------------- 篮子规则
    def test_module_stage_only_counts_in_module_maker(self):
        self.assertIn("cn.300308", part_members(self.conn, "part.module-maker"))
        stage = self.conn.execute("SELECT stage FROM physical_part_companies WHERE part_id='part.host-cage' AND company_id='global.nvidia'").fetchone()
        self.assertEqual(stage["stage"], "module")
        self.assertNotIn("global.nvidia", part_members(self.conn, "part.host-cage"))

    def test_candidate_evidence_does_not_count(self):
        ev = self.conn.execute("SELECT evidence FROM physical_part_companies WHERE part_id='part.pic' AND company_id='cn.688981'").fetchone()
        self.assertEqual(ev["evidence"], "candidate")
        self.assertNotIn("cn.688981", part_members(self.conn, "part.pic"))

    def test_fewer_than_three_members_gives_count_only(self):
        self.assertLess(len(part_basket_members(self.conn, "part.pd")), MIN_PART_BASKET)
        self.assertIsNone(self.conn.execute("SELECT 1 FROM series WHERE instrument='basket:part.pd' LIMIT 1").fetchone())
        row = next(p for p in market.physical_market(self.conn, OBJECT)["parts"] if p["id"] == "part.pd")
        self.assertEqual(row["members"], 2)
        self.assertFalse(row["has_basket"])
        self.assertIsNone(row["basket_excess"]); self.assertIsNone(row["excess_3m"]); self.assertIsNone(row["crowd"])
        d = market.part_market(self.conn, OBJECT, "part.pd")
        self.assertFalse(d["has_basket"])
        self.assertIsNone(d["conclusion"]); self.assertIsNone(d["crowding"]); self.assertEqual(d["series"]["basket"], [])

    def test_event_lands_on_a_verified_mapping_first(self):
        # 深南电路在金手指上只是候选,在主 PCB 上已核验:扩产落在主 PCB,而不是信号顺序更靠前的金手指
        ev = {r["part_id"]: r["evidence"] for r in self.conn.execute("SELECT part_id, evidence FROM physical_part_companies WHERE company_id='cn.002916'")}
        self.assertEqual((ev["part.edge-fingers"], ev["part.pcb"]), ("candidate", "verified"))
        self.assertEqual(market.PH.part_for_event(self.conn, "cn.002916", "capex")["part_id"], "part.pcb")

    # ---------------------------------------------------------------- 参照
    def test_reaction_is_read_against_the_part_basket(self):
        e = market.get_event(self.conn, self._event("cn.300308"))
        self.assertEqual(e["part"]["part_id"], "part.module-maker")
        peers = [c for c in part_basket_members(self.conn, "part.module-maker") if c != "cn.300308"]
        ref = A.basket_series([market.load_series(self.conn, f"company:{c}") for c in peers])
        want = A.reaction(market.load_series(self.conn, "company:cn.300308"), ref, date.fromisoformat(e["date"]), 1, AS_OF)["excess"]
        self.assertAlmostEqual(e["reaction"]["t1"], want, places=9)
        self.assertEqual(e["reaction"]["reference"], "篮子")

    def test_no_basket_reference_when_part_is_too_small(self):
        cache = {r["instrument"]: None for r in self.conn.execute("SELECT DISTINCT instrument FROM series")}
        self.assertEqual(market.PH.part_for_event(self.conn, "cn.600703", "supply")["part_id"], "part.pd")
        self.assertIsNone(recompute.reference_for(self.conn, {"company_id": "cn.600703", "category": "supply"}, cache))

    def test_resonance_scope_is_the_part(self):
        r = market.resonance(self.conn, self._event("cn.300308"))
        self.assertEqual((r["scope"]["kind"], r["scope"]["id"]), ("part", "part.module-maker"))
        self.assertEqual({p["company"]["id"] for p in r["peers"]}, set(part_basket_members(self.conn, "part.module-maker")) - {"cn.300308"})
        self.assertEqual(r["adjacent"], [])                  # 整模块不在信号路径上
        r = market.resonance(self.conn, self._event("cn.688498"))
        self.assertEqual(r["scope"]["id"], "part.cw-laser")
        self.assertEqual([(a["relation"], a["node"]["id"]) for a in r["adjacent"]], [("上一站", "part.driver"), ("下一站", "part.pic")])
        self.assertIn("部件", insights.resonance(r)["text"])
        self.assertNotIn("环节", insights.resonance(r)["text"])

    def test_crowding_deviation_reference_is_the_part_basket(self):
        from app.ingest.crowding import reference_instrument
        self.assertEqual(reference_instrument(self.conn, "cn.688498", "cpo"), "basket:part.cw-laser")
        self.assertEqual(reference_instrument(self.conn, "cn.600703", "cpo"), "basket:cpo")      # 光电探测器不成篮子

    # ---------------------------------------------------------------- 首页与选中部件
    def test_home_conclusion_is_by_part(self):
        d = market.physical_market(self.conn, OBJECT, days=7)
        self.assertEqual(d["as_of"], AS_OF.isoformat())
        c = d["conclusion"]
        self.assertEqual(c["direction"], "pos")
        self.assertTrue(c["text"].startswith("资金本周在给 CW 激光器 投票"), c["text"])
        self.assertIn("部件内", c["text"])
        self.assertNotIn("环节", c["text"])
        cw = next(p for p in d["parts"] if p["id"] == "part.cw-laser")
        self.assertEqual(cw["events"], 3)
        self.assertEqual(cw["direction"], "pos")
        self.assertGreater(cw["basket_excess"], 0)
        self.assertEqual(cw["last_event"]["company"]["short_name"], "长光华芯")
        self.assertEqual([p["id"] for p in d["parts"]][:2], ["part.host-cage", "part.edge-fingers"])   # 发送信号顺序

    def test_part_market_for_selected_part(self):
        d = market.part_market(self.conn, OBJECT, "part.cw-laser", months=3)
        self.assertTrue(d["has_basket"])
        self.assertGreaterEqual(d["members"], MIN_PART_BASKET)
        self.assertTrue(d["series"]["basket"] and d["series"]["product"])
        self.assertIn("部件篮子相对整机 3 个月", d["conclusion"]["text"])
        self.assertEqual(len(d["events"]), 4)
        self.assertIn("资金在给 CW 激光器这一段投票", d["events_conclusion"]["text"])
        self.assertTrue(d["crowding"]["metrics"])
        self.assertEqual(len(d["chart_events"]), 4)
        row = next(p for p in market.physical_market(self.conn, OBJECT)["parts"] if p["id"] == "part.cw-laser")
        self.assertEqual(row["excess_3m"], d["readings"]["excess_months"])      # 首页一行与选中部件同一个「3 个月」
        self.assertEqual(row["basket_excess"], d["readings"]["excess_window"])

    def test_endpoints(self):
        r = self.client.get(f"/api/physical/{OBJECT}/market?days=7")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["parts"]), 17)
        r = self.client.get(f"/api/physical/{OBJECT}/parts/part.cw-laser/market?months=3")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["part"]["label"], "CW 激光器")
        self.assertEqual(self.client.get(f"/api/physical/{OBJECT}/parts/part.nope/market").status_code, 404)
        self.assertEqual(self.client.get("/api/physical/om.nope/market").status_code, 404)

    def _event(self, company_id: str) -> str:
        return self.conn.execute("SELECT id FROM events WHERE company_id=? ORDER BY date DESC LIMIT 1", (company_id,)).fetchone()["id"]


class EmptyDatabaseTests(unittest.TestCase):
    """服务器现在的样子:没有示例、事件为 0;没有行情时部件读数都是空的,首页结论是一句中性话。"""

    def test_no_events_no_bars(self):
        db = _tmp / "empty.sqlite"
        rebuild(db, include_sample=False)
        conn = connect(db)
        try:
            d = market.physical_market(conn, OBJECT)
            self.assertEqual(d["conclusion"]["direction"], "neu")
            self.assertIn("没有新的卡口事件", d["conclusion"]["text"])
            self.assertTrue(all(not p["has_basket"] and p["events"] == 0 and p["members"] == 0 for p in d["parts"]))
            p = market.part_market(conn, OBJECT, "part.cw-laser")
            self.assertFalse(p["has_basket"]); self.assertEqual(p["events"], [])
            self.assertEqual(p["events_conclusion"]["text"], "窗口内没有落在 CW 激光器上的卡口事件。")
        finally:
            conn.close()


class UnitWordingTests(unittest.TestCase):
    def test_layer_events_unit(self):
        self.assertEqual(insights.layer_events([], "DSP")["text"], "窗口内没有落在 DSP 上的卡口事件。")
        self.assertEqual(insights.layer_events([], "硅光芯片", unit="层")["text"], "窗口内没有触及硅光芯片的卡口事件。")
        neg = [{"company": {"short_name": n}, "category_label": "技术路线", "reaction": {"t1": -0.02}} for n in ("甲", "乙")]
        self.assertIn("这个部件的利好没有被买单", insights.layer_events(neg, "DSP")["text"])
        self.assertIn("这一层的利好没有被买单", insights.layer_events(neg, "硅光芯片", unit="层")["text"])

    def test_basket_unit(self):
        c = insights.basket({"excess_window": 0.05, "crowding": None, "efficacy": None, "window_months": 3}, unit="部件")
        self.assertTrue(c["text"].startswith("部件篮子相对整机 3 个月"))
        self.assertTrue(insights.basket({"excess_window": 0.05, "crowding": None, "efficacy": None, "window_months": 6})["text"].startswith("环节相对整机"))


if __name__ == "__main__":
    unittest.main()
