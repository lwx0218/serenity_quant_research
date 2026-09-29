"""候选自动入账:三路分流(入账 / 例行 / 交给 AI)、重跑不重复、AI 交回关待办、人只剩「不算」、重建后事件回来。
Run with `pytest` or `python -m unittest`."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

_tmp = Path(tempfile.mkdtemp())
os.environ.setdefault("SQR_DB_PATH", str(_tmp / "unused.sqlite"))

from fastapi.testclient import TestClient  # noqa: E402

from app import market  # noqa: E402
from app.db import connect  # noqa: E402
from app.deps import get_conn  # noqa: E402
from app.ingest import accounting as ACC  # noqa: E402
from app.ingest import candidates as C  # noqa: E402
from app.ingest import news, recompute  # noqa: E402
from app.ingest.upload import upload  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import rebuild  # noqa: E402


def cand(key: str, *, tier: int = 0, source_type: str = "cninfo_announcement", company: str | None = "cn.300308",
         companies: list[str] | None = None, category: str | None = "order", date: str | None = "2026-09-21",
         relevance: int = 1, also: list[str] | None = None) -> dict:
    url = f"https://t/{key}"
    ids = companies if companies is not None else ([company] if company else [])
    return {"id": news.cand_id(url), "date": date, "title": f"候选 {key}", "url": url, "summary": "", "source": "巨潮资讯 · 公告" if tier == 0 else "讯石光通讯",
            "source_type": source_type, "tier": tier, "weight": 1.0, "evidence": news.TIER_EVIDENCE[tier], "category": category,
            "companies": [{"companyId": i, "name": i} for i in ids], "part_ids": [], "also_reported_by": also or [], "relevance": relevance}


POOL = {
    "official": cand("official"),                                                        # 公告,齐全 → 入账
    "irm": cand("irm", source_type="cninfo_irm", company="cn.688498", category="price"),  # 互动易 → 入账
    "media2": cand("media2", tier=1, source_type="rss", company="cn.300394", category="qualification", also=["光纤在线"]),  # 两家媒体 → 入账
    "media1": cand("media1", tier=1, source_type="rss", company="cn.300502", category="capex"),   # 一家媒体 → 交给 AI
    "routine": cand("routine", relevance=0, category=None),                                  # 例行 → 不算
    "multi": cand("multi", companies=["cn.300308", "cn.300502"]),                            # 命中两家 → 交给 AI
    "nocat": cand("nocat", category=None),                                                   # 缺类别 → 交给 AI
    "nocompany": cand("nocompany", company=None, companies=[]),                              # 没命中公司 → 交给 AI
    "general": cand("general", tier=2, source_type="rss", company="cn.300308", category="supply"),   # 综合媒体 → 交给 AI
}


class AccountingTests(unittest.TestCase):
    def setUp(self):
        self.db = Path(tempfile.mkdtemp()) / "sqr.sqlite"
        rebuild(self.db, include_sample=False)
        self.conn = connect(self.db)
        for cid in ("cn.300308", "cn.688498", "cn.300394", "cn.300502", "cn.688048"):
            upload(self.conn, "bars", cid, [{"date": f"2026-09-{d:02d}", "close": 100 + d + len(cid) % 3} for d in (17, 18, 21, 22, 23, 24, 25)])
        recompute.recompute_all(self.conn)                                           # 行情 → 序列(生产上是 daily 作业做的)
        news.store(self.conn, list(POOL.values()))

    def tearDown(self):
        self.conn.close()

    def _status(self, key: str) -> tuple:
        r = self.conn.execute("SELECT status, decided_by FROM candidates WHERE id=?", (POOL[key]["id"],)).fetchone()
        return (r["status"], r["decided_by"])

    def test_three_ways(self):
        out = ACC.account(self.conn)
        self.assertEqual((out["auto"], out["routine"], out["triage"]), (3, 1, 5))
        for k in ("official", "irm", "media2"):
            self.assertEqual(self._status(k), ("confirmed", "rule"), k)
        self.assertEqual(self._status("routine"), ("rejected", "rule"))
        for k in ("media1", "multi", "nocat", "nocompany", "general"):
            self.assertEqual(self._status(k), ("pending", None), k)
        todos = {r["company_id"]: r["reason"] for r in self.conn.execute("SELECT company_id, reason FROM ingest_todo WHERE kind='candidate_triage' AND status='open'")}
        self.assertEqual(set(todos), {POOL[k]["id"] for k in ("media1", "multi", "nocat", "nocompany", "general")})
        self.assertIn("命中 2 家公司", todos[POOL["multi"]["id"]])
        self.assertIn("只有一家行业媒体报道", todos[POOL["media1"]["id"]])
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM events WHERE is_sample=0").fetchone()[0], 3)
        e = market.list_events(self.conn, company="cn.300308")[0]
        self.assertIsNotNone(e["reaction"]["t1"])                                   # 批量入账最后统一重算了反应

    def test_rerun_is_idempotent(self):
        ACC.account(self.conn)
        again = ACC.account(self.conn)
        self.assertEqual((again["auto"], again["routine"]), (0, 0))
        self.assertEqual(again["triage"], 5)                                        # 还在等 AI 的会再过一遍规则,但不重复开待办
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM ingest_todo WHERE kind='candidate_triage'").fetchone()[0], 5)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM events WHERE is_sample=0").fetchone()[0], 3)

    def test_ai_hands_back_and_todo_closes(self):
        ACC.account(self.conn)
        app.dependency_overrides[get_conn] = lambda: self.conn
        try:
            client = TestClient(app)
            r = client.post(f"/api/candidates/{POOL['multi']['id']}/confirm", json={"company_id": "cn.300502"})
            self.assertEqual(r.status_code, 200)
            r = client.post(f"/api/candidates/{POOL['general']['id']}/reject", json={"note": "传闻,原文没说"})
            self.assertEqual(r.status_code, 200)
            s = client.get("/api/ingest/status").json()["accounting"]
        finally:
            app.dependency_overrides.pop(get_conn, None)
        self.assertEqual(self._status("multi"), ("confirmed", "ai"))
        self.assertEqual(self._status("general"), ("rejected", "ai"))
        self.assertEqual((s["accounted"], s["by_rule"], s["by_ai"], s["to_ai"], s["routine"], s["not_counted"]), (4, 3, 1, 3, 1, 1))

    def test_human_only_says_not_counted(self):
        ACC.account(self.conn)
        eid = self.conn.execute("SELECT event_id FROM candidates WHERE id=?", (POOL["official"]["id"],)).fetchone()[0]
        C.dismiss_event(self.conn, eid, "不算")
        self.assertNotIn(eid, [e["id"] for e in market.list_events(self.conn)])
        self.assertEqual(self._status("official"), ("rejected", "human"))
        ACC.account(self.conn)                                                      # 规则不会把人判的不算翻回来
        self.assertEqual(self._status("official"), ("rejected", "human"))
        C.restore_event(self.conn, eid)
        self.assertIn(eid, [e["id"] for e in market.list_events(self.conn)])
        self.assertEqual(self._status("official"), ("confirmed", "human"))

    def test_rebuild_replays_accounted_events(self):
        ACC.account(self.conn)
        dismissed = self.conn.execute("SELECT event_id FROM candidates WHERE id=?", (POOL["irm"]["id"],)).fetchone()[0]
        C.dismiss_event(self.conn, dismissed)
        before = {r[0] for r in self.conn.execute("SELECT id FROM events WHERE is_sample=0 AND status!='ignored'")}
        self.conn.close()
        counts = rebuild(self.db, include_sample=False)
        self.conn = connect(self.db)
        self.assertEqual(counts["events_replayed"], 2)
        after = {r[0] for r in self.conn.execute("SELECT id FROM events WHERE is_sample=0")}
        self.assertEqual(after, before)
        self.assertNotIn(dismissed, after)                                          # 人判的不算,重建后也不回来
        self.assertTrue(market.list_events(self.conn, company="cn.300308")[0]["reaction"]["t1"] is not None)

    def test_classify_reasons(self):
        self.assertEqual(ACC.classify(self.conn, {**POOL["official"], "companies": json.dumps(POOL["official"]["companies"]),
                                                  "also_reported_by": "[]", "company_id": "cn.300308"})[0], "auto")
        way, why = ACC.classify(self.conn, {**POOL["nocat"], "companies": json.dumps(POOL["nocat"]["companies"]), "also_reported_by": "[]", "company_id": "cn.300308"})
        self.assertEqual((way, why), ("triage", "没有类别"))


if __name__ == "__main__":
    unittest.main()
