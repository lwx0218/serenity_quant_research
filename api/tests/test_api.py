"""API tests. Run with `pytest` (or `python -m unittest` — no pytest required)."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

_tmp = tempfile.mkdtemp()
os.environ["SQR_DB_PATH"] = str(Path(_tmp) / "test.sqlite")

from fastapi.testclient import TestClient  # noqa: E402

from app import config  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import rebuild  # noqa: E402


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rebuild(config.DB_PATH, config.SEED_DIR)
        cls.client = TestClient(app)

    def test_product_tree_has_nine_modules_and_21_parts(self):
        r = self.client.get("/api/products/cpo")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["kind"], "product")
        self.assertEqual(len(body["children"]), 9)
        self.assertEqual(sum(len(m["children"]) for m in body["children"]), 21)
        self.assertEqual([m["code"] for m in body["children"]][:3], ["THERMAL", "HOST-ASIC", "EIC"])
        self.assertTrue(all(m["visual"] for m in body["children"]))
        self.assertEqual(len(body["chain"]), 10)
        self.assertEqual(len(body["signal_path"]["steps"]), 5)

    def test_module_detail_inherits_parts_chain_links_and_companies(self):
        r = self.client.get("/api/nodes/cpo.mod.pic")
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["node"]["name"], "硅光芯片")
        self.assertEqual([a["id"] for a in d["ancestors"]], ["cpo"])
        self.assertEqual(len(d["children"]), 3)
        self.assertEqual([c["id"] for c in d["chain_nodes"]], ["cpo.chain.silicon-photonics"])
        names = [c["short_name"] for c in d["companies"]]
        self.assertEqual(names, ["Intel", "Broadcom", "中际旭创", "源杰科技"])
        self.assertTrue(all(c["evidence_level"] == "reference" for c in d["companies"]))

    def test_part_detail_breadcrumb_and_siblings(self):
        d = self.client.get("/api/nodes/cpo.part.pic.modulator").json()
        self.assertEqual([a["id"] for a in d["ancestors"]], ["cpo", "cpo.mod.pic"])
        self.assertEqual(len(d["siblings"]), 3)
        self.assertEqual(d["node"]["status"], "validated_category")
        self.assertEqual([t["id"] for t in d["technologies"]], ["cpo.tech.silicon-photonics"])

    def test_strongest_evidence_level_wins(self):
        d = self.client.get("/api/nodes/cpo.mod.host-asic").json()
        by_id = {c["id"]: c for c in d["companies"]}
        self.assertEqual(by_id["global.broadcom"]["evidence_level"], "candidate")
        self.assertEqual(by_id["global.nvidia"]["evidence_level"], "reference")
        # candidate sorts before reference
        self.assertEqual(d["companies"][0]["id"], "global.broadcom")

    def test_chain_list(self):
        r = self.client.get("/api/chain")
        self.assertEqual(r.status_code, 200)
        chain = r.json()
        self.assertEqual(len(chain), 10)
        sp = next(c for c in chain if c["id"] == "cpo.chain.silicon-photonics")
        self.assertEqual(sp["display_name"], "硅光芯片")
        self.assertEqual([m["id"] for m in sp["modules"]], ["cpo.mod.pic"])
        self.assertEqual(len(sp["companies"]), 4)

    def test_company_filters(self):
        all_ = self.client.get("/api/companies").json()
        self.assertEqual(len(all_), 35)
        by_chain = self.client.get("/api/companies", params={"chain": "cpo.chain.light-source"}).json()
        self.assertEqual([c["short_name"] for c in by_chain], ["Coherent", "Lumentum", "仕佳光子", "长光华芯"])
        by_node = self.client.get("/api/companies", params={"node": "cpo.mod.thermal"}).json()
        self.assertEqual({c["short_name"] for c in by_node}, {"飞荣达", "中石科技", "领益智造"})
        q = self.client.get("/api/companies", params={"q": "300308"}).json()
        self.assertEqual([c["id"] for c in q], ["cn.300308"])

    def test_company_detail(self):
        d = self.client.get("/api/companies/global.broadcom").json()
        self.assertEqual(d["short_name"], "Broadcom")
        self.assertEqual(d["evidence_level"], "candidate")
        levels = {(e["chain_node_id"], e["evidence_level"]) for e in d["exposures"]}
        self.assertIn(("cpo.chain.asic", "candidate"), levels)
        self.assertIn(("cpo.chain.silicon-photonics", "reference"), levels)
        cand = next(e for e in d["exposures"] if e["evidence_level"] == "candidate")
        self.assertEqual(cand["node_id"], "cpo.part.host-asic.switch-die")
        self.assertEqual(cand["source_publisher"], "Broadcom Inc.")
        self.assertIn("cpo.mod.host-asic", [m["id"] for m in d["modules"]])

    def test_404s(self):
        self.assertEqual(self.client.get("/api/nodes/nope").status_code, 404)
        self.assertEqual(self.client.get("/api/companies/nope").status_code, 404)
        self.assertEqual(self.client.get("/api/products/cpo.mod.pic").status_code, 404)


if __name__ == "__main__":
    unittest.main()
