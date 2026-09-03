"""Market layer: analytics rules, notes round-trip and the research endpoints.
Run with `pytest` or `python -m unittest`."""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

_tmp = tempfile.mkdtemp()
os.environ["SQR_DB_PATH"] = str(Path(_tmp) / "test.sqlite")
_notes_src = Path(__file__).resolve().parents[2] / "data" / "notes"
_notes_tmp = Path(_tmp) / "notes"
shutil.copytree(_notes_src, _notes_tmp)
os.environ["SQR_NOTES_DIR"] = str(_notes_tmp)

from fastapi.testclient import TestClient  # noqa: E402

from app import analytics as A  # noqa: E402
from app import config, notes  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import rebuild  # noqa: E402


class AnalyticsTests(unittest.TestCase):
    def test_trading_day_arithmetic_skips_weekends(self):
        fri = date(2026, 8, 28)
        self.assertEqual(A.add_trading_days(fri, 1), date(2026, 8, 31))
        self.assertEqual(A.trading_days_between(date(2026, 8, 26), fri), 2)
        self.assertEqual(A.trading_days_between(date(2026, 8, 21), fri), 5)

    def test_freshness_states(self):
        f = A.freshness(date(2026, 8, 26), date(2026, 8, 28), 5, 0.02)
        self.assertEqual((f["state"], f["label"]), ("window", "窗口内 T+2/5"))
        self.assertEqual(A.freshness(date(2026, 8, 13), date(2026, 8, 28), 5, 0.01)["state"], "priced")
        self.assertEqual(A.freshness(date(2026, 8, 26), date(2026, 8, 28), 5, 0.001)["state"], "unreacted")
        self.assertEqual(A.freshness(date(2026, 8, 4), date(2026, 8, 28), 5, 0.001)["label"], "过期 · 未反应")
        self.assertEqual(A.freshness(date(2026, 8, 28), date(2026, 8, 28), 5, None)["state"], "pending")

    def test_crowding_directions_follow_thresholds(self):
        d = A.crowding_directions({"ret20_pct_rank": 92, "turnover_pct_rank": 88, "deviation_sigma": 1.8, "margin_to_float_pct": 4.1})
        self.assertEqual(d["overall"], "neg")
        self.assertEqual(d["per_metric"]["ret20_pct_rank"], "neg")
        self.assertEqual(A.crowding_directions({"ret20_pct_rank": 15, "turnover_pct_rank": 18, "deviation_sigma": -0.5})["overall"], "pos")
        self.assertEqual(A.crowding_directions({"ret20_pct_rank": 55, "turnover_pct_rank": 50, "deviation_sigma": 0.3})["overall"], "neu")

    def test_efficacy_half_life_is_median_of_event_fades(self):
        fade = [1.0, 0.9, 0.8, 0.6, 0.45, 0.4] + [0.4] * 14           # falls below half on T+5 → holds through T+4
        hold = [1.0] * 20                                              # never fades → 20
        eff = A.efficacy([{"category": "capex", "path": fade}, {"category": "order", "path": fade}, {"category": "capex", "path": hold}])
        self.assertEqual(eff["sample_n"], 3)
        self.assertEqual(eff["half_life_days"], 4)
        self.assertEqual(eff["validity_days"], 4)
        self.assertEqual(eff["hit_rate"], 1.0)
        self.assertEqual(eff["by_category"]["capex"]["n"], 2)

    def test_reaction_and_basket(self):
        d0, d1, d2 = date(2026, 8, 26), date(2026, 8, 27), date(2026, 8, 28)
        s = {d0: 100.0, d1: 103.0, d2: 104.0}
        b = {d0: 100.0, d1: 101.0, d2: 101.0}
        r = A.reaction(s, b, d0, 1, d2)
        self.assertAlmostEqual(r["abs_return"], 0.03)
        self.assertAlmostEqual(r["excess"], 0.02)
        self.assertIsNone(A.reaction(s, b, d0, 5, d2))            # not observable yet
        bs = A.basket_series([s, b])
        self.assertAlmostEqual(bs[d1], 102.0)


class NotesTests(unittest.TestCase):
    def test_round_trip_keeps_front_matter_and_questions(self):
        n = notes.load_note("cpo.mod.pic")
        self.assertEqual(n.direction, "pos")
        self.assertIn("basket:cpo.mod.pic", n.track)
        self.assertEqual(n.questions[0]["status"], "open")
        text = notes.render_note(n)
        again = notes.parse_note(text)
        self.assertEqual(again.indicators, n.indicators)
        self.assertEqual(again.questions, n.questions)
        self.assertEqual(again.body, n.body)
        self.assertIn("[[中际旭创]]", again.to_dict()["body"])
        self.assertIn("中际旭创", again.to_dict()["links"])


class ResearchApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rebuild(config.DB_PATH, config.SEED_DIR)
        cls.client = TestClient(app)

    def test_overview_counts_match_inbox_events(self):
        o = self.client.get("/api/overview/cpo").json()
        i = self.client.get("/api/research/inbox").json()
        self.assertEqual(o["as_of"], i["as_of"])
        self.assertEqual(o["counts"]["events"], len(i["events"]))
        self.assertEqual(o["counts"]["reacted"] + o["counts"]["unreacted"] + o["counts"]["pending"], o["counts"]["events"])
        self.assertIn(o["conclusion"]["direction"], ("pos", "neg", "neu"))
        self.assertEqual(len(o["layers"]), 9)
        self.assertTrue(o["sample"])

    def test_layer_event_counts_agree_between_overview_and_node(self):
        o = self.client.get("/api/overview/cpo").json()
        for layer in o["layers"]:
            if layer["events"]:
                r = self.client.get(f"/api/nodes/{layer['node_id']}/market").json()
                self.assertEqual(len(r["events"]), layer["events"], layer["node_id"])

    def test_every_event_carries_a_freshness_label_and_as_of(self):
        r = self.client.get("/api/events?days=60").json()
        self.assertTrue(r["items"])
        for e in r["items"]:
            self.assertIn(e["freshness"]["state"], ("window", "priced", "unreacted", "expired", "pending"))
            self.assertTrue(e["freshness"]["label"])
            self.assertTrue(e["company"] or e["node"])
        self.assertEqual(r["as_of"], "2026-08-28")

    def test_resonance_and_basket_pages(self):
        r = self.client.get("/api/events/evt.2026-08-26.cn.300308.capex/resonance").json()
        self.assertEqual(r["same_direction"]["n"], 4)
        self.assertEqual(len(r["adjacent"]), 2)
        b = self.client.get("/api/baskets/cpo.mod.pic").json()
        self.assertEqual(len(b["members"]), 4)
        self.assertTrue(b["series"]["basket"] and b["series"]["product"])
        self.assertEqual(len(b["efficacy_rows"]), 4)
        self.assertIn(b["efficacy"]["validity_days"], range(3, 11))
        self.assertEqual(b["crowding"]["direction"], "neg")

    def test_company_market_has_headline_thesis_and_events(self):
        r = self.client.get("/api/companies/cn.300308/market").json()
        self.assertEqual(r["primary_layer"]["id"], "cpo.mod.pic")
        self.assertTrue(r["events_30d"])
        self.assertEqual(r["thesis"]["subject"], "cn.300308")
        self.assertIn(r["headline"]["direction"], ("pos", "neg", "neu"))
        self.assertTrue(r["series"])

    def test_part_inherits_module_thesis(self):
        r = self.client.get("/api/nodes/cpo.part.pic.modulator/market").json()
        self.assertEqual(r["thesis"]["subject"], "cpo.mod.pic")

    def test_note_save_writes_markdown_and_questions(self):
        body = {"kind": "module", "title": "光纤阵列", "direction": "neg", "stance": "看空耦合环节", "body": "测试 [[天孚通信]]。",
                "window_until": "2026-12-31", "threshold_pct": 3, "track": ["basket:cpo.mod.fiber-interface"], "indicators": ["a ≥ 1"], "invalidation": ["b < 0"]}
        r = self.client.put("/api/notes/cpo.mod.fiber-interface", json=body)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertTrue((_notes_tmp / "cpo.mod.fiber-interface.md").exists())
        r = self.client.post("/api/notes/cpo.mod.fiber-interface/questions", json={"text": "耦合良率多少?"}).json()
        self.assertEqual(r["questions"][0]["text"], "耦合良率多少?")
        r = self.client.patch("/api/notes/cpo.mod.fiber-interface/questions/1", json={"status": "verified"}).json()
        self.assertEqual(r["questions"][0]["status"], "verified")
        text = (_notes_tmp / "cpo.mod.fiber-interface.md").read_text(encoding="utf-8")
        self.assertIn("- [x] 耦合良率多少?", text)
        self.assertIn("direction: neg", text)

    def test_verification_upgrades_exposure(self):
        inbox = self.client.get("/api/research/inbox").json()
        up = next(d for d in inbox["decisions"] if d["kind"] == "verify" and "升级为候选" in [a["label"] for a in d["actions"]])
        r = self.client.post("/api/verifications", json={"action": "upgrade", "event_id": up["event_id"], "exposure_id": up["exposure_id"]})
        self.assertEqual(r.status_code, 200, r.text)
        c = self.client.get("/api/companies/cn.300308").json()
        self.assertIn("candidate", [e["evidence_level"] for e in c["exposures"]])
        again = self.client.get("/api/research/inbox").json()
        self.assertNotIn(up["event_id"], [d.get("event_id") for d in again["decisions"]])

    def test_links_suggest(self):
        r = self.client.get("/api/links/suggest?q=源").json()
        self.assertTrue(any(x["label"] == "源杰科技" for x in r))


if __name__ == "__main__":
    unittest.main()
