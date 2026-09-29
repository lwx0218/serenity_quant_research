"""候选自动入账 v2(docs/claude/teardown-accounting-v2.md):规则只挡与归位,判定交 AI;AI 批量交回;历史回填。
夹具里的 12 条是 09-29 真数据上 v1 规则自动入账的那 12 条(快照 56cb689),v2 下一条都不该自动入账。
Run with `pytest` or `python -m unittest`."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

_tmp = Path(tempfile.mkdtemp())
os.environ.setdefault("SQR_DB_PATH", str(_tmp / "unused.sqlite"))

from fastapi.testclient import TestClient  # noqa: E402

from app import market  # noqa: E402
from app.db import connect  # noqa: E402
from app.deps import get_conn  # noqa: E402
from app.ingest import accounting as ACC  # noqa: E402
from app.ingest import candidates as C  # noqa: E402
from app.ingest import news, recompute, runner  # noqa: E402
from app.ingest.upload import upload  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import rebuild  # noqa: E402

CNINFO = ("巨潮资讯 · 公告", "cninfo_announcement", 0)
DIGITIMES = ("DIGITIMES", "rss", 1)
EASTMONEY = ("东方财富 · 股票", "rss", 2)


def cand(key: str, title: str, src: tuple = CNINFO, *, company: str | None = "cn.300308", companies: list[str] | None = None,
         category: str | None = "capex", date: str | None = "2026-09-21", relevance: int = 1, summary: str = "",
         origin: str = "live", url: str | None = None) -> dict:
    url = url or f"https://t/{key}"
    ids = companies if companies is not None else ([company] if company else [])
    name, stype, tier = src
    return {"id": news.cand_id(url), "date": date, "title": title, "url": url, "summary": summary, "source": name,
            "source_type": stype, "tier": tier, "weight": 1.0, "evidence": news.TIER_EVIDENCE[tier], "category": category,
            "companies": [{"companyId": i, "name": i} for i in ids], "part_ids": [], "also_reported_by": [], "relevance": relevance,
            "origin": origin}


# 09-29 真数据:v1 规则自动入账的 12 条 → v2 的去向
REAL = {
    "sy-zengzi": (cand("sy-zengzi", "生益电子：生益电子关于使用部分募集资金向全资子公司增资以实施募投项目的公告", company="cn.688183"), "routine"),
    "sy-zhihuan": (cand("sy-zhihuan", "生益电子：生益电子关于使用募集资金置换预先投入募投项目及已支付发行费用的自筹资金的公告", company="cn.688183"), "routine"),
    "meta-glasses": (cand("meta-glasses", "Meta adds camera-free AI glasses as Samsung prepares 2026 launch", DIGITIMES, company="global.meta"), "routine"),
    "ms-cooling": (cand("ms-cooling", "LG expands AI data center cooling ties with Microsoft, SK Enmove", DIGITIMES, company="global.microsoft",
                        category="supply"), "routine"),
    "tsmc-fab": (cand("tsmc-fab", "TSMC helps VSMC build first Singapore fab in 22 months at lower cost than US", DIGITIMES, company="global.tsmc"), "triage"),
    # 规格 §6 写「NVIDIA 进 triage」,但这条标题有 buyback,§1.1 的英文例行词先挡掉;另一条 NVIDIA(GMI Cloud)进 triage
    "nv-buyback": (cand("nv-buyback", "Nvidia adds a record US$150 billion to its stock buyback", DIGITIMES, company="global.nvidia",
                        category="order"), "routine"),
    "fz-jiekuan": (cand("fz-jiekuan", "方正科技：方正科技关于使用募集资金向全资子公司提供借款以实施募投项目的公告", company="cn.600601"), "routine"),
    "nv-gmi": (cand("nv-gmi", "Interview: GMI Cloud bets on Taiwan as a proving ground for global AI expansion", DIGITIMES, company="global.nvidia"), "triage"),
    "meta-lineup": (cand("meta-lineup", "Meta stretches its glasses lineup from US$249 to US$1,299.99 as rivals close in", DIGITIMES,
                         company="global.meta"), "routine"),
    "dt-zhuanhu": (cand("dt-zhuanhu", "鼎通科技：关于部分募投项目增加实施主体、实施地点及开立募集资金专户并向全资子公司提供无息借款以实施募投项目的公告",
                        company="cn.688668"), "routine"),
    "wyt-thai": (cand("wyt-thai", "[临时公告]万源通:关于泰国子公司进展情况的公告", company="cn.920060"), "triage"),
    "cd-land": (cand("cd-land", "崇达技术：关于子公司普诺威签署国有土地使用权出让合同暨端侧功能性IC封装载板项目投资进展公告", company="cn.002815",
                     category="order"), "routine"),
}
MORE = {
    "mingpu-lpo": (cand("mingpu-lpo", "铭普光磁：公司800G LPO光模块已实现小批量出货", EASTMONEY, company="cn.002902", category="qualification",
                        summary="铭普光磁 9月29日在互动平台表示，公司800G LPO光模块已实现小批量出货"), "triage"),
    "siph-line": (cand("siph-line", "关于投资建设硅光光引擎产线的公告", category="roadmap"), "auto"),         # 类别以动词为准 → capex
    "em-plain": (cand("em-plain", "中际旭创：签订日常经营合同", EASTMONEY, category="order"), "routine"),        # 综合媒体,标题没有产品词
    "two-cos": (cand("two-cos", "中际旭创与新易盛 1.6T 光模块份额之争", DIGITIMES, companies=["cn.300308", "cn.300502"], category="order"), "triage"),
    "mpo-short": (cand("mpo-short", "MPO 连接器交期拉长", DIGITIMES, company=None, companies=[], category="supply"), "triage"),
    "ir-record": (cand("ir-record", "中际旭创：投资者关系活动记录表", category=None), "triage"),
    "rel0": (cand("rel0", "关于股份质押的公告", category=None, relevance=0), "routine"),
}
POOL = {**REAL, **MORE}


class AccountingV2Tests(unittest.TestCase):
    def setUp(self):
        self.db = Path(tempfile.mkdtemp()) / "sqr.sqlite"
        rebuild(self.db, include_sample=False)
        self.conn = connect(self.db)
        for cid in ("cn.300308", "cn.300502", "cn.300394", "cn.688498", "cn.688048", "cn.002902"):
            upload(self.conn, "bars", cid, [{"date": f"2026-09-{d:02d}", "close": 100 + d + len(cid) % 3} for d in (17, 18, 21, 22, 23, 24, 25)])
        recompute.recompute_all(self.conn)                                           # 行情 → 序列(生产上是 daily 作业做的)
        news.store(self.conn, [c for c, _ in POOL.values()])

    def tearDown(self):
        app.dependency_overrides.pop(get_conn, None)
        self.conn.close()

    def _row(self, key: str) -> dict:
        return dict(self.conn.execute("SELECT * FROM candidates WHERE id=?", (POOL[key][0]["id"],)).fetchone())

    def _classify(self, key: str) -> tuple:
        return ACC.classify(self.conn, self._row(key), news.build_vocab(self.conn))

    def _todo(self, key: str) -> dict | None:
        r = self.conn.execute("SELECT * FROM ingest_todo WHERE kind='candidate_triage' AND company_id=?", (POOL[key][0]["id"],)).fetchone()
        return dict(r) if r else None

    # ---------------------------------------------------------------- §1 规则 v2
    def test_real_12_none_auto(self):
        ways = {k: self._classify(k)[0] for k in REAL}
        self.assertEqual(ways, {k: want for k, (_, want) in REAL.items()})
        self.assertNotIn("auto", ways.values())
        self.assertEqual(self._classify("meta-glasses")[1], "例行(「glasses」),不算")
        self.assertEqual(self._classify("ms-cooling")[1], "公司不在这只模块的任何部件上")
        self.assertIn("募集资金", self._classify("sy-zhihuan")[1])
        self.assertEqual(self._classify("tsmc-fab")[1], "行业媒体,要核实")

    def test_more_cases(self):
        for k, (_, want) in MORE.items():
            self.assertEqual(self._classify(k)[0], want, k)
        way, why, part = self._classify("mingpu-lpo")
        self.assertEqual((way, why, part), ("triage", "综合 / 泛科技媒体,要核实", "part.shell"))
        self.assertEqual(self._classify("siph-line")[2], "part.engine-assembly")      # 类别 capex 最近的是引擎阶段
        self.assertIn("命中 2 家公司", self._classify("two-cos")[1])
        self.assertEqual(self._classify("mpo-short")[2], "part.mpo")                   # 没命中公司,部件词给初判
        self.assertIn("投资者关系活动记录", self._classify("ir-record")[1])

    def test_part_initial_prefers_hit_part(self):
        c = cand("hit", "中际旭创：硅光 PIC 通过客户认证", category="qualification")
        c = {**c, "companies": json.dumps(c["companies"]), "part_ids": "[]", "also_reported_by": "[]", "company_id": "cn.300308"}
        self.assertEqual(ACC.classify(self.conn, c, news.build_vocab(self.conn))[2], "part.pic")
        c2 = {**c, "title": "中际旭创：整模块通过客户认证"}
        self.assertEqual(ACC.classify(self.conn, c2, news.build_vocab(self.conn))[2], "part.module-maker")   # 不是 part_for_event 的 pic

    def test_account_writes_rule_judgement(self):
        out = ACC.account(self.conn)
        want = {w: sum(1 for _, x in POOL.values() if x == w) for w in ("auto", "routine", "triage")}
        self.assertEqual({k: out[k] for k in want}, want)
        r = self._row("siph-line")
        self.assertEqual((r["status"], r["decided_by"], r["category"], r["confidence"], r["thesis"], r["part_id"]),
                         ("confirmed", "rule", "capex", 3, "关于投资建设硅光光引擎产线的公告", "part.engine-assembly"))
        e = market.get_event(self.conn, r["event_id"])
        self.assertEqual((e["decided_by"], e["confidence"], e["part"]["part_id"]), ("rule", 3, "part.engine-assembly"))
        self.assertIsNotNone(e["reaction"]["t1"])                                    # 批量入账最后统一重算了反应
        self.assertEqual(self._row("mingpu-lpo")["part_id"], "part.shell")           # 交给 AI 的也带部件初判
        hint = self._todo("mingpu-lpo")["hint"]
        self.assertIn("「铭普光磁 在 ", hint)
        self.assertIn("(part.shell) 上的卡口事件」", hint)
        self.assertIn("POST /api/candidates/judge", hint)
        again = ACC.account(self.conn)                                               # 重跑不重复
        self.assertEqual((again["auto"], again["routine"], again["triage"]), (0, 0, want["triage"]))
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM ingest_todo WHERE kind='candidate_triage'").fetchone()[0], want["triage"])

    def test_expired_todo_is_dropped_and_stays_dropped(self):
        ACC.account(self.conn)
        old = (datetime.now() - timedelta(days=8)).isoformat(timespec="seconds")
        self.conn.execute("UPDATE ingest_todo SET created_at=? WHERE company_id=?", (old, POOL["tsmc-fab"][0]["id"]))
        self.assertEqual(ACC.expire_triage(self.conn), 1)
        self.assertEqual(self._todo("tsmc-fab")["status"], "dropped")
        self.assertEqual(self._row("tsmc-fab")["status"], "pending")
        ACC.account(self.conn)
        self.assertEqual(self._todo("tsmc-fab")["status"], "dropped")               # 规则重跑不重开作废的待办
        s = ACC.summary(self.conn)
        self.assertEqual((s["expired"], s["unprocessed"]), (1, 0))

    def test_rejudge_v1_rule_entries_once(self):
        C.confirm(self.conn, POOL["sy-zengzi"][0]["id"], by="rule")                  # v1 规则入账的募资公告
        C.confirm(self.conn, POOL["fz-jiekuan"][0]["id"], by="rule")
        eid = self._row("fz-jiekuan")["event_id"]
        C.dismiss_event(self.conn, eid, "不算")                                       # 人已判不算:不动
        out = runner.job_triage(self.conn, log=lambda *_: None)
        self.assertEqual(out["rejudged"], 1)
        self.assertEqual((self._row("sy-zengzi")["status"], self._row("sy-zengzi")["decided_by"]), ("rejected", "rule"))
        self.assertEqual((self._row("fz-jiekuan")["status"], self._row("fz-jiekuan")["decided_by"]), ("rejected", "human"))
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM events WHERE is_sample=0 AND status!='ignored'").fetchone()[0], 1)   # 只剩 siph-line
        self.assertEqual(runner.job_triage(self.conn, log=lambda *_: None)["rejudged"], 0)

    # ---------------------------------------------------------------- §2 AI 交回
    def test_judge_batch_true_false_error(self):
        ACC.account(self.conn)
        app.dependency_overrides[get_conn] = lambda: self.conn
        client = TestClient(app)
        ir = POOL["ir-record"][0]["id"]
        body = {"by": "ai", "items": [
            {"id": ir, "is_chokepoint": True, "part_id": "part.module-maker", "category": "qualification", "date": "2026-09-22",
             "thesis": "1.6T 硅光模块在北美第二家客户通过认证,整模块的供给多了一条", "confidence": 4, "reason": "纪要原文"},
            {"id": POOL["tsmc-fab"][0]["id"], "is_chokepoint": False, "reason": "代工厂新建晶圆厂,与这只模块无关"},
            {"id": POOL["mingpu-lpo"][0]["id"], "is_chokepoint": True, "category": "qualification"},          # 缺 thesis / confidence
        ]}
        r = client.post("/api/candidates/judge", json=body)
        self.assertEqual(r.status_code, 200)
        out = r.json()
        self.assertEqual((out["ok"], out["confirmed"], out["rejected"], out["errors"]), (False, 1, 1, 1))
        self.assertIn("thesis", out["results"][2]["error"])
        self.assertEqual(self._row("mingpu-lpo")["status"], "pending")               # 报错的原样不动,待办还开着
        self.assertEqual(self._todo("mingpu-lpo")["status"], "open")
        row = self._row("ir-record")
        self.assertEqual((row["status"], row["decided_by"], row["confidence"], row["part_id"], row["category"]),
                         ("confirmed", "ai", 4, "part.module-maker", "qualification"))
        self.assertEqual(self._todo("ir-record")["status"], "done")
        e = client.get(f"/api/events/{row['event_id']}").json()
        self.assertEqual((e["decided_by"], e["confidence"]), ("ai", 4))
        self.assertIn("北美第二家客户", e["thesis"])
        self.assertEqual(e["part"]["part_id"], "part.module-maker")                  # AI 的归位压过 part_for_event(会给 pic)
        self.assertIsNotNone(e["reaction"]["t1"])                                    # 处理完统一重算了反应
        self.assertEqual((self._row("tsmc-fab")["status"], self._row("tsmc-fab")["decided_by"]), ("rejected", "ai"))
        self.assertEqual(client.post("/api/candidates/judge", json={"items": [{"id": ir}] * 201}).status_code, 422)
        bad = client.post("/api/candidates/judge", json={"items": [{"id": "cand.nope", "is_chokepoint": False},
                                                                   {"id": ir, "is_chokepoint": True, "thesis": "x", "confidence": 9}]}).json()
        self.assertIn("not found", bad["results"][0]["error"])
        self.assertIn("confidence", bad["results"][1]["error"])

    def test_judge_overrides_rule_but_not_human(self):
        ACC.account(self.conn)
        rule_auto = self._row("siph-line")
        out = C.judge(self.conn, [{"id": rule_auto["id"], "is_chokepoint": False, "reason": "只是规划"}])
        self.assertEqual(out["rejected"], 1)
        self.assertIsNone(market.get_event(self.conn, rule_auto["event_id"]))       # AI 说不算,规则入账的事件删掉
        C.judge(self.conn, [{"id": rule_auto["id"], "is_chokepoint": True, "thesis": "引擎产线扩产", "confidence": 3}])
        eid = self._row("siph-line")["event_id"]
        C.dismiss_event(self.conn, eid)
        out = C.judge(self.conn, [{"id": rule_auto["id"], "is_chokepoint": True, "thesis": "再来一次", "confidence": 5}])
        self.assertIn("人判过", out["results"][0]["error"])

    def test_single_confirm_accepts_judgement_and_multi_company_needs_company(self):
        ACC.account(self.conn)
        app.dependency_overrides[get_conn] = lambda: self.conn
        client = TestClient(app)
        two = POOL["two-cos"][0]["id"]
        self.assertIn("company_id", C.judge(self.conn, [{"id": two, "is_chokepoint": True, "thesis": "t", "confidence": 2}])["results"][0]["error"])
        r = client.post(f"/api/candidates/{two}/confirm", json={"company_id": "cn.300502", "part_id": "part.pic", "thesis": "份额", "confidence": 2})
        self.assertEqual(r.status_code, 200)
        e = market.get_event(self.conn, r.json()["event_id"])
        self.assertEqual((e["company"]["id"], e["part"]["part_id"], e["confidence"], e["thesis"]), ("cn.300502", "part.pic", 2, "份额"))
        self.assertEqual(client.post(f"/api/candidates/{two}/confirm", json={"confidence": 7}).status_code, 422)

    def test_rebuild_replays_judgement(self):
        ACC.account(self.conn)
        C.judge(self.conn, [{"id": POOL["ir-record"][0]["id"], "is_chokepoint": True, "part_id": "part.module-maker", "category": "order",
                             "thesis": "订单", "confidence": 4, "reason": "r"}])
        before = {r["id"]: (r["thesis"], r["confidence"], r["decided_by"], r["part_id"])
                  for r in self.conn.execute("SELECT * FROM events WHERE is_sample=0")}
        self.conn.close()
        counts = rebuild(self.db, include_sample=False)
        self.conn = connect(self.db)
        self.assertEqual(counts["events_replayed"], 2)
        after = {r["id"]: (r["thesis"], r["confidence"], r["decided_by"], r["part_id"])
                 for r in self.conn.execute("SELECT * FROM events WHERE is_sample=0")}
        self.assertEqual(after, before)

    # ---------------------------------------------------------------- §3 回填
    def test_backfill_two_months(self):
        def ts(d):
            return int(datetime.fromisoformat(d).timestamp() * 1000)

        def ann(aid, title, d, code="300308"):
            return {"announcementId": aid, "announcementTitle": title, "announcementTime": ts(d), "adjunctUrl": f"finalpage/{d}/{aid}.PDF",
                    "secCode": code, "secName": title.split("：")[0]}

        pages = {
            ("中际旭创", "2026-07-01", 1): {"announcements": [
                ann("a1", "中际旭创：关于投资建设1.6T硅光模块产线的公告", "2026-07-06"),             # 强命中 → 入账
                ann("a2", "中际旭创：2026年半年度报告摘要", "2026-07-20"),                           # 例行
                ann("a3", "中际旭创：关于签订日常经营重大合同的公告", "2026-07-21")], "hasMore": True},  # 回填没有产品词 → 例行
            ("中际旭创", "2026-07-01", 2): {"announcements": [
                ann("a4", "中际旭创：关于硅光产品研发进展的自愿性信息披露公告", "2026-07-28"),        # 有产品词没动词 → 交 AI
                ann("a5", "新易盛：关于投资建设光模块产线的公告", "2026-07-29", code="300502")], "hasMore": False},   # 别家的,不要
            ("中际旭创", "2026-08-01", 1): {"announcements": [
                ann("a6", "中际旭创：投资者关系活动记录表", "2026-08-12"),                           # 没取到正文 → 交 AI 读原文
                ann("a1", "中际旭创：关于投资建设1.6T硅光模块产线的公告", "2026-07-06")], "totalpages": 1},
        }
        calls = []

        def fake(url, params=None, **kw):
            calls.append((params["searchkey"], params["sdate"], params["edate"], params["pageNum"]))
            return pages.get((params["searchkey"], params["sdate"], params["pageNum"]), {"announcements": []})

        live = cand("live-a4", "中际旭创：关于硅光产品研发进展的自愿性信息披露公告", category="roadmap", date="2026-07-28",
                    url="http://static.cninfo.com.cn/finalpage/2026-07-28/a4.PDF")
        news.store(self.conn, [live])                                                  # 定时抓取先抓到的,回填不改它的 origin
        with mock.patch.object(news.http, "get_json", side_effect=fake), mock.patch.object(news, "BACKFILL_PAUSE", 0):
            out = runner.job_backfill(self.conn, since="2026-07-01", until="2026-08-31", log=lambda *_: None)
        self.assertIn(("中际旭创", "2026-07-01", "2026-07-31", 2), calls)
        self.assertNotIn(("中际旭创", "2026-07-01", "2026-07-31", 3), calls)            # hasMore=false 就停
        self.assertEqual(out["fetch"]["segments"], 2)
        self.assertEqual((out["fetch"]["fetched"], out["fetch"]["new"], out["fetch"]["merged"]), (5, 4, 0))   # a5 别家、a1 重复;a4 已在池里
        self.assertEqual(out["fetch"]["companies_failed"], 0)
        rows = {r["title"].split("：", 1)[1]: dict(r) for r in self.conn.execute("SELECT * FROM candidates WHERE origin='backfill'")}
        self.assertEqual({k: (r["status"], r["decided_by"]) for k, r in rows.items()}, {
            "关于投资建设1.6T硅光模块产线的公告": ("confirmed", "rule"),
            "2026年半年度报告摘要": ("rejected", "rule"),
            "关于签订日常经营重大合同的公告": ("rejected", "rule"),
            "投资者关系活动记录表": ("pending", None),
        })
        self.assertEqual(rows["关于签订日常经营重大合同的公告"]["decided_note"], "回填,没有部件 / 产品词")
        self.assertEqual(out["backfill"], {"confirmed": 1, "rejected": 2, "pending": 1})
        self.assertEqual((out["summary"]["backfill"], out["summary"]["backfill_accounted"]), (4, 1))
        a4 = dict(self.conn.execute("SELECT * FROM candidates WHERE id=?", (live["id"],)).fetchone())
        self.assertEqual((a4["origin"], a4["status"], a4["also_reported_by"]), ("live", "pending", "[]"))   # 同一个源再抓一遍不算第二家
        e = market.get_event(self.conn, rows["关于投资建设1.6T硅光模块产线的公告"]["event_id"])
        self.assertEqual((e["date"], e["category"]), ("2026-07-06", "capex"))

    def test_backfill_breaker_and_segments(self):
        self.assertEqual(news.month_segments("2025-10-15", "2026-01-10"),
                         [("2025-10-15", "2025-10-31"), ("2025-11-01", "2025-11-30"), ("2025-12-01", "2025-12-31"), ("2026-01-01", "2026-01-10")])
        with mock.patch.object(news.http, "get_json", side_effect=news.http.FetchError("boom")) as m:
            out = news.backfill(self.conn, "2026-07-01", "2026-08-31", log=lambda *_: None, pause=0)
        self.assertTrue(out["stopped"])
        self.assertEqual(out["companies_failed"], news.MAX_CONSECUTIVE_FAILS)
        self.assertEqual(m.call_count, news.MAX_CONSECUTIVE_FAILS * 2)

    def test_upload_candidates_backfill_origin_goes_through_rules(self):
        out = upload(self.conn, "candidates", None, [
            {"url": "https://m/1", "title": "讯石:源杰科技 CW 光源通过硅光模块客户验证", "date": "2026-06-10", "tier": 1, "origin": "backfill",
             "source": "讯石光通讯", "company_id": "cn.688498"},
            {"url": "https://m/2", "title": "Meta glasses sell out", "date": "2026-06-11", "tier": 1, "origin": "backfill", "source": "DIGITIMES"}])
        self.assertEqual(out["rows"], 2)
        r1 = dict(self.conn.execute("SELECT * FROM candidates WHERE id=?", (news.cand_id("https://m/1"),)).fetchone())
        r2 = dict(self.conn.execute("SELECT * FROM candidates WHERE id=?", (news.cand_id("https://m/2"),)).fetchone())
        self.assertEqual((r1["origin"], r1["status"], r1["part_id"]), ("backfill", "pending", "part.cw-laser"))     # 交 AI
        self.assertEqual((r2["origin"], r2["status"], r2["company_id"]), ("backfill", "rejected", "global.meta"))    # 现打的公司,例行
        with self.assertRaises(ValueError):
            upload(self.conn, "candidates", None, [{"url": "https://m/3", "title": "t", "origin": "old"}])

    def test_human_only_says_not_counted(self):
        ACC.account(self.conn)
        eid = self._row("siph-line")["event_id"]
        C.dismiss_event(self.conn, eid, "不算")
        self.assertNotIn(eid, [e["id"] for e in market.list_events(self.conn)])
        self.assertEqual(self._row("siph-line")["decided_by"], "human")
        ACC.account(self.conn)                                                      # 规则不会把人判的不算翻回来
        self.assertEqual(self._row("siph-line")["status"], "rejected")
        C.restore_event(self.conn, eid)
        self.assertIn(eid, [e["id"] for e in market.list_events(self.conn)])


if __name__ == "__main__":
    unittest.main()
