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
os.environ["SQR_DB_PATH"] = str(_tmp / "unused.sqlite")

from fastapi.testclient import TestClient  # noqa: E402

from tests import IsolatedTestCase  # noqa: E402
from app import market  # noqa: E402
from app import physical as PH  # noqa: E402
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
    # v2.1 软组:募投 / 增资 / 调研在标题同时有产品词与类别动词时不挡
    "mujin-line": (cand("mujin-line", "关于使用募集资金投资建设 1.6T 硅光模块产线的公告", category="roadmap"), "auto"),
    "mujin-noverb": (cand("mujin-noverb", "关于使用募集资金向子公司增资用于硅光项目的公告"), "routine"),      # 有产品词没动词:照旧挡
    "diaoyan": (cand("diaoyan", "机构调研：中际旭创 1.6T 光模块小批量出货", EASTMONEY, category="qualification"), "triage"),
    "diaoyan-plain": (cand("diaoyan-plain", "9月机构调研中际旭创", EASTMONEY, category="qualification"), "routine"),
}
POOL = {**REAL, **MORE}


class AccountingV2Tests(IsolatedTestCase):
    def setUp(self):
        super().setUp()
        self.db = Path(tempfile.mkdtemp()) / "sqr.sqlite"
        rebuild(self.db, include_sample=False)
        self.conn = connect(self.db)
        for cid in ("cn.300308", "cn.300502", "cn.300394", "cn.688498", "cn.688048", "cn.002902"):
            upload(self.conn, "bars", cid, [{"date": f"2026-09-{d:02d}", "close": 100 + d + len(cid) % 3} for d in (17, 18, 21, 22, 23, 24, 25)])
        recompute.recompute_all(self.conn)                                           # 行情 → 序列(生产上是 daily 作业做的)
        news.store(self.conn, [c for c, _ in POOL.values()])
        # 测试不出网:默认当作服务器没装 pypdf(读不了正文);要读正文的用例自己打开并给出正文
        nopdf = mock.patch.object(news, "can_read_pdf", return_value=False)
        nopdf.start(); self.addCleanup(nopdf.stop)

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

    def test_soft_routine_words(self):
        way, why, part = self._classify("mujin-line")
        self.assertEqual(way, "auto")
        self.assertEqual(self._classify("mujin-noverb")[1], "例行(「使用募集资金」),不算")
        self.assertEqual(self._classify("diaoyan-plain")[1], "例行(「调研」),不算")
        self.assertEqual(self._classify("sy-zengzi")[0], "routine")                  # 09-29 那条募资增资:没有产品词,照旧挡
        ACC.account(self.conn)
        r = self._row("mujin-line")
        self.assertEqual((r["status"], r["decided_by"], r["category"]), ("confirmed", "rule", "capex"))

    def test_categorize_english_whole_words(self):
        cats = news.load_spec()["categories"]
        self.assertIsNone(news.categorize("Cross-border fabric makers meet in Taipei", cats))   # 不再撞 order / fab
        self.assertEqual(news.categorize("TSMC wins new orders", cats), "order")
        self.assertEqual(news.categorize("Two new fabs to ramp in 2027", cats), "capex")
        self.assertEqual(news.categorize("台积电宣布新fab", cats), "capex")                      # 紧挨中文也算整词

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
        n_auto = sum(1 for _, w in POOL.values() if w == "auto")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM events WHERE is_sample=0 AND status!='ignored'").fetchone()[0], n_auto)   # 只剩强命中的
        self.assertEqual(runner.job_triage(self.conn, log=lambda *_: None)["rejudged"], 0)

    def test_version_bump_rejudges_rule_routine_too(self):
        ACC.account(self.conn)
        mujin = POOL["mujin-line"][0]["id"]
        C.reopen(self.conn, mujin)
        C.reject(self.conn, mujin, note="例行(「使用募集资金」),不算", by="rule")       # v2 当时把它挡成了例行
        self.conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('accounting_rules', 'v2')")
        n_rule = self.conn.execute("SELECT COUNT(*) FROM candidates WHERE decided_by='rule'").fetchone()[0]
        out = runner.job_triage(self.conn, log=lambda *_: None)
        self.assertEqual(out["rejudged"], n_rule)                                   # 入账的和例行的都重开
        r = self._row("mujin-line")
        self.assertEqual((r["status"], r["decided_by"], r["category"]), ("confirmed", "rule", "capex"))
        self.assertEqual(self._row("sy-zengzi")["status"], "rejected")                 # 其余照旧
        self.assertEqual(self.conn.execute("SELECT value FROM settings WHERE key='accounting_rules'").fetchone()[0], ACC.RULES_VERSION)
        self.assertEqual(ACC.RULES_VERSION, "v2.3")

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
        self.assertEqual(counts["events_replayed"], 1 + sum(1 for _, w in POOL.values() if w == "auto"))
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
                ann("a1", "中际旭创：关于投资建设1.6T硅光模块产线的公告", "2026-07-06"),             # 标题强命中 → 入账
                ann("a2", "中际旭创：2026年半年度报告摘要", "2026-07-20"),                           # 例行
                ann("a3", "中际旭创：关于签订日常经营重大合同的公告", "2026-07-21"),                 # 套话标题,正文有 1.6T → 交 AI
                {"announcementId": "bad", "announcementTitle": "", "adjunctUrl": "finalpage/x.PDF"}], "hasMore": True},   # 缺标题:跳过并计数
            ("中际旭创", "2026-07-01", 2): {"announcements": [
                ann("a4", "中际旭创：关于硅光产品研发进展的自愿性信息披露公告", "2026-07-28"),        # 已在池里(定时抓取先抓到)
                ann("a5", "新易盛：关于投资建设光模块产线的公告", "2026-07-29", code="300502")], "hasMore": False},   # 别家的,不要
            ("中际旭创", "2026-08-01", 1): {"announcements": [
                ann("a6", "中际旭创：投资者关系活动记录表", "2026-08-12"),                           # 没取到正文 → 交 AI 读原文
                ann("a7", "中际旭创：关于对外投资的公告", "2026-08-13"),                             # 正文是理财 → 例行
                ann("a8", "中际旭创：关于对外投资设立子公司的公告", "2026-08-14"),                   # 正文有硅光 → 交 AI
                ann("a1", "中际旭创：关于投资建设1.6T硅光模块产线的公告", "2026-07-06")], "totalpages": 1},
        }
        bodies = {"a3": "公司与客户签订日常经营重大合同,标的为 1.6T 光模块,合同金额 12 亿元。",
                  "a7": "公司拟使用自有闲置资金购买银行理财产品,额度不超过 5 亿元。",
                  "a8": "子公司主营硅光芯片的研发与封测,注册资本 2 亿元。",
                  "a1": "公司拟投资建设 1.6T 硅光模块产线。"}
        calls, read = [], []

        def fake(url, params=None, **kw):
            calls.append((params["searchkey"], params["sdate"], params["edate"], params["pageNum"]))
            return pages.get((params["searchkey"], params["sdate"], params["pageNum"]), {"announcements": [], "totalAnnouncement": 0})

        def body(url, limit=1500):
            read.append(url)
            return bodies.get(url.rsplit("/", 1)[-1].split(".")[0])

        live = cand("live-a4", "中际旭创：关于硅光产品研发进展的自愿性信息披露公告", category="roadmap", date="2026-07-28",
                    url="http://static.cninfo.com.cn/finalpage/2026-07-28/a4.PDF")
        news.store(self.conn, [live])                                                  # 定时抓取先抓到的,回填不改它的 origin
        with mock.patch.object(news.http, "get_json", side_effect=fake), mock.patch.object(news, "BACKFILL_PAUSE", 0), \
                mock.patch.object(news, "can_read_pdf", return_value=True), mock.patch.object(news, "announcement_text", side_effect=body):
            out = runner.job_backfill(self.conn, since="2026-07-01", until="2026-08-31", log=lambda *_: None)
        self.assertIn(("中际旭创", "2026-07-01", "2026-07-31", 2), calls)
        self.assertNotIn(("中际旭创", "2026-07-01", "2026-07-31", 3), calls)            # hasMore=false 就停
        f = out["fetch"]
        self.assertEqual(f["segments"], 2)
        self.assertEqual((f["fetched"], f["new"], f["merged"]), (7, 6, 0))              # a5 别家、a1 重复;a4 已在池里
        self.assertEqual((f["skipped"], f["segments_failed"], f["complete"]), (1, 0, True))   # 缺标题那条按条记,整页不算失败
        self.assertEqual([(x["kind"], x["error"]) for x in f["failures"]], [("item", "缺标题")])
        rows = {r["title"].split("：", 1)[1]: dict(r) for r in self.conn.execute("SELECT * FROM candidates WHERE origin='backfill'")}
        self.assertEqual({k: (r["status"], r["decided_by"]) for k, r in rows.items()}, {
            "关于投资建设1.6T硅光模块产线的公告": ("confirmed", "rule"),
            "2026年半年度报告摘要": ("rejected", "rule"),
            "关于签订日常经营重大合同的公告": ("pending", None),
            "投资者关系活动记录表": ("pending", None),
            "关于对外投资的公告": ("rejected", "rule"),
            "关于对外投资设立子公司的公告": ("pending", None),
        })
        self.assertIn("1.6T 光模块", rows["关于签订日常经营重大合同的公告"]["summary"])     # 正文写进 summary
        self.assertIn("产品词只在正文里", self.conn.execute("SELECT reason FROM ingest_todo WHERE company_id=?",
                                                       (rows["关于签订日常经营重大合同的公告"]["id"],)).fetchone()[0])
        self.assertEqual(rows["关于对外投资的公告"]["decided_note"], "标题没有类别动词,正文也没有部件 / 产品词")
        self.assertIn("没取到正文", self.conn.execute("SELECT reason FROM ingest_todo WHERE company_id=?",
                                                  (rows["投资者关系活动记录表"]["id"],)).fetchone()[0])
        self.assertIsNotNone(rows["投资者关系活动记录表"]["body_at"])                      # 取不到也记,不每轮重抓
        self.assertFalse(any("a2" in u for u in read))                                   # 例行标题不读正文
        self.assertEqual(out["backfill"], {"confirmed": 1, "rejected": 2, "pending": 3})
        self.assertEqual((out["summary"]["backfill"], out["summary"]["backfill_accounted"]), (6, 1))
        a4 = dict(self.conn.execute("SELECT * FROM candidates WHERE id=?", (live["id"],)).fetchone())
        self.assertEqual((a4["origin"], a4["status"], a4["also_reported_by"]), ("live", "pending", "[]"))   # 同一个源再抓一遍不算第二家
        e = market.get_event(self.conn, rows["关于投资建设1.6T硅光模块产线的公告"]["event_id"])
        self.assertEqual((e["date"], e["category"]), ("2026-07-06", "capex"))
        n = len(read)
        with mock.patch.object(news, "can_read_pdf", return_value=True), mock.patch.object(news, "announcement_text", side_effect=body):
            ACC.account(self.conn)
        self.assertEqual(len(read), n)                                                   # 读过的(包括没取到的)不再读

    def test_v22_body_rules(self):
        """评审 §4.1 的三条:套话标题 + 正文决定去向;正文里的产品词不够自动入账。"""
        bodies = {"c1": "本合同标的为 1.6T 光模块,合同金额 3 亿元。", "c2": "拟投资设立硅光芯片子公司。", "c3": "使用闲置自有资金购买理财产品。"}
        items = [cand("c1", "关于签订日常经营重大合同的公告", category="order", url="http://static.cninfo.com.cn/finalpage/c1.PDF"),
                 cand("c2", "关于对外投资的公告", category=None, url="http://static.cninfo.com.cn/finalpage/c2.PDF"),
                 cand("c3", "关于对外投资的公告(二)", category=None, url="http://static.cninfo.com.cn/finalpage/c3.PDF")]
        for it in items:                                                                  # 和抓取一样打 relevance
            it["relevance"] = news.relevance_of({"type": "cninfo_announcement"}, it["title"], it["category"], [], title=it["title"])
        self.assertEqual([it["relevance"] for it in items], [1, 1, 1])                   # 套话标题不再因为没类别词判 0
        news.store(self.conn, items)
        with mock.patch.object(news, "can_read_pdf", return_value=True), \
                mock.patch.object(news, "announcement_text", side_effect=lambda url, limit=1500: bodies.get(url.rsplit("/", 1)[-1][:2])):
            ACC.account(self.conn)
        st = {it["key"]: tuple(self.conn.execute("SELECT status, decided_by FROM candidates WHERE id=?", (it["id"],)).fetchone())
              for it in [dict(x, key=k) for x, k in zip(items, ("c1", "c2", "c3"))]}
        self.assertEqual(st, {"c1": ("pending", None), "c2": ("pending", None), "c3": ("rejected", "rule")})
        self.assertIsNotNone(self.conn.execute("SELECT 1 FROM ingest_todo WHERE company_id=? AND status='open'", (items[0]["id"],)).fetchone())
        # 读不了正文(没装 pypdf):套话标题照旧交 AI 读原文,不判例行
        it = cand("c4", "关于对外投资的公告(三)", category=None, url="http://static.cninfo.com.cn/finalpage/c4.PDF")
        news.store(self.conn, [it])
        ACC.account(self.conn)
        self.assertEqual(self.conn.execute("SELECT status FROM candidates WHERE id=?", (it["id"],)).fetchone()[0], "pending")
        # 正文里的硬例行词不让 relevance 变 0(「无需提交股东大会审议」是正文常见句)
        self.assertEqual(news.relevance_of({"type": "cninfo_announcement"}, "关于签订日常经营重大合同的公告 本合同无需提交股东大会审议",
                                           "order", [], title="关于签订日常经营重大合同的公告"), 1)

    # ---------------------------------------------------------------- v2.3:归位底线与映射提议
    def test_event_only_on_mapped_part(self):
        ACC.account(self.conn)
        ir = POOL["ir-record"][0]["id"]                                              # 中际旭创:driver / pic / engine-assembly / module-maker
        out = C.judge(self.conn, [{"id": ir, "is_chokepoint": True, "part_id": "part.mpo", "category": "order",
                                   "thesis": "t", "confidence": 3}])
        self.assertIn("不站在 part.mpo 上", out["results"][0]["error"])
        self.assertIn("/api/mapping/candidates", out["results"][0]["error"])
        self.assertEqual(self._row("ir-record")["status"], "pending")                # 报错的原样不动
        mpo = POOL["mpo-short"][0]["id"]                                             # 没命中公司,规则初判 part.mpo(部件词)
        self.assertEqual(self._row("mpo-short")["part_id"], "part.mpo")
        r = C.judge(self.conn, [{"id": mpo, "is_chokepoint": True, "company_id": "cn.300308", "category": "supply",
                                 "thesis": "t", "confidence": 2}])
        self.assertTrue(r["ok"], r)                                                  # 存着的初判不在映射里:不用它,按映射排
        e = market.get_event(self.conn, r["results"][0]["event_id"])
        self.assertIn(e["part"]["part_id"], {p["part_id"] for p in PH.company_parts(self.conn, "cn.300308")})
        meta = POOL["meta-glasses"][0]["id"]
        C.reopen(self.conn, meta)
        self.assertIn("不在这只模块的任何部件上", C.judge(self.conn, [{"id": meta, "is_chokepoint": True, "category": "capex",
                                                               "thesis": "t", "confidence": 2}])["results"][0]["error"])
        app.dependency_overrides[get_conn] = lambda: self.conn
        r = TestClient(app).post(f"/api/candidates/{ir}/confirm", json={"part_id": "part.mpo", "category": "order"})
        self.assertEqual(r.status_code, 422)
        # 读的时候也守底线:库里一条事件的 part_id 不在映射里,页面不认,退回按映射排
        self.conn.execute("UPDATE events SET part_id='part.mpo' WHERE id=?", (e["id"],))
        self.assertNotEqual(market.get_event(self.conn, e["id"])["part"]["part_id"], "part.mpo")

    def test_mapping_candidate_lifecycle(self):
        ACC.account(self.conn)
        app.dependency_overrides[get_conn] = lambda: self.conn
        client = TestClient(app)
        cand_id = POOL["ir-record"][0]["id"]
        body = {"company_id": "cn.300308", "part_id": "part.mpo", "stage": "device", "role": "MPO 插座",
                "sources": [{"title": "年报", "url": "http://static.cninfo.com.cn/x.PDF", "quote": "公司生产 MPO 插座"}],
                "reason": "年报原文写明自产 MPO 插座", "candidate_id": cand_id}
        for bad, why in (({**body, "sources": [{"url": "u"}]}, "quote"), ({**body, "part_id": "part.pic"}, "已经站在"),
                         ({**body, "stage": "x"}, "stage")):
            r = client.post("/api/mapping/candidates", json=bad)
            self.assertEqual(r.status_code, 422, bad); self.assertIn(why, r.json()["detail"])
        self.assertEqual(client.post("/api/mapping/candidates", json=body).status_code, 200)
        items = client.get("/api/mapping/candidates").json()["items"]
        self.assertEqual([(t["company_id"], t["payload"]["part_id"], t["payload"]["sources"][0]["quote"]) for t in items],
                         [("cn.300308@part.mpo", "part.mpo", "公司生产 MPO 插座")])
        self.assertEqual(ACC.account(self.conn)["mappings_resolved"], 0)             # 实物层还没有这条映射
        # 交 AI 的待办作废了;映射按证据流程进了实物层(这里直接插一行模拟重建后的状态)
        self.conn.execute("UPDATE ingest_todo SET status='dropped' WHERE company_id=?", (cand_id,))
        self.conn.execute("""INSERT INTO physical_part_companies (part_id, seq, company_id, name, stage, evidence, sources)
                             VALUES ('part.mpo', 99, 'cn.300308', '中际旭创', 'device', 'verified', '[]')""")
        self.assertEqual(ACC.account(self.conn)["mappings_resolved"], 1)
        self.assertEqual(client.get("/api/mapping/candidates?status=done").json()["count"], 1)
        self.assertEqual(self._todo("ir-record")["status"], "open")                  # 牵出的候选重新交 AI
        r = C.judge(self.conn, [{"id": cand_id, "is_chokepoint": True, "part_id": "part.mpo", "category": "order",
                                 "thesis": "t", "confidence": 3}])
        self.assertTrue(r["ok"], r)

    def test_v23_raise_fund_wrap_up_is_routine(self):
        for t in ("关于部分募投项目结项并将节余募集资金永久补充流动资金的公告", "关于调整部分募投项目内部投资结构的公告",
                  "关于部分募投项目延期的公告", "关于变更部分募投项目实施地点的公告", "关于增加募集资金投资项目实施主体及实施地点的公告"):
            self.assertIsNotNone(news.routine_hit(t, "cninfo_announcement"), t)
        self.assertIsNone(news.routine_hit("关于投资建设 1.6T 硅光模块产线的公告", "cninfo_announcement"))
        ACC.account(self.conn)
        hint = self._todo("mingpu-lpo")["hint"]
        self.assertIn("募投项目结项、延期、变更实施地点、调整内部投资结构也不是", hint)
        self.assertIn("部件只能是这家公司在实物映射里站着的:part.shell", hint)
        self.assertIn("POST /api/mapping/candidates", hint)

    # ---------------------------------------------------------------- v2.3:互动问答
    def test_irm_routing(self):
        def irm(key, q, a, company="cn.300308"):
            c = cand(key, q, ("互动易 · 投资者问答", "cninfo_irm", 0), company=company, category=None, summary=a)
            return {**c, "companies": json.dumps(c["companies"]), "part_ids": "[]", "also_reported_by": "[]", "company_id": company}
        vocab = news.build_vocab(self.conn)
        way = lambda c: ACC.classify(self.conn, c, vocab)[0]  # noqa: E731
        # 问题里有产品词 + 动词也不自动入账:问题不是事实
        self.assertEqual(way(irm("q1", "请问贵公司1.6T光模块是否已批量出货?", "公司1.6T光模块已实现批量出货,感谢关注。")), "triage")
        self.assertEqual(way(irm("q2", "请问贵公司1.6T光模块是否已批量出货?", "感谢您的关注,请以公司公告为准。")), "routine")
        self.assertEqual(way(irm("q3", "公司明年有什么规划?", "公司将持续加大研发投入,感谢关注。")), "routine")
        self.assertEqual(way(irm("q4", "800G 产品进展如何?", "目前已向多家客户送样,部分进入小批量阶段。")), "triage")
        self.assertEqual(way(irm("q5", "公司市值管理有何举措?", "公司光模块订单饱满。")), "routine")       # 问题命中硬例行

    def test_irm_fetch_and_backfill(self):
        def row(i, q, a, when="2026-07-15"):
            return {"indexId": f"q{i}", "mainContent": q, "attachedContent": a, "stockCode": "300308",
                    "pubDate": int(datetime.fromisoformat(when).timestamp() * 1000) - 86400000,
                    "updateDate": int(datetime.fromisoformat(when).timestamp() * 1000)}
        pages = {("2026-07-01", 1): {"rows": [row(1, "1.6T 光模块出货情况?", "公司1.6T光模块已批量出货。"),
                                              row(2, "公司分红计划?", "请关注公告。"),
                                              row(3, "还没回答的问题", "")], "totalPage": 2},
                 ("2026-07-01", 2): {"rows": [row(4, "800G 新客户?", "已完成新客户送样认证,即将批量交付。", "2026-07-20")], "totalPage": 2},
                 ("2026-08-01", 1): {"rows": [], "totalPage": 0}}
        calls = []

        def fake(url, params=None, data=None, **kw):
            if url.endswith("queryKeyboardInfo"):
                return {"data": [{"code": "300308", "secid": "9900012345", "zwjc": "中际旭创"}]}
            calls.append((params["stockcode"], params["startDay"], params["endDay"], params["pageNum"]))
            return pages.get((params["startDay"], params["pageNum"]), {"rows": [], "totalPage": 0})

        news._IRM_ORG.clear()
        with mock.patch.object(news.http, "get_json", side_effect=fake), mock.patch.object(news, "BACKFILL_PAUSE", 0), \
                mock.patch.object(news, "irm_companies", return_value=[{"companyId": "cn.300308", "name": "中际旭创", "ticker": "300308"}]):
            out = runner.job_backfill(self.conn, since="2026-07-01", until="2026-08-31", only="cninfo_irm", log=lambda *_: None)
        f = out["fetch"]
        self.assertEqual((f["source"], f["pages"], f["fetched"], f["new"], f["skipped"], f["complete"]), ("cninfo_irm", 3, 3, 3, 1, True))
        self.assertIn(("300308", "2026-07-01", "2026-07-31", 2), calls)
        rows = {r["title"]: dict(r) for r in self.conn.execute("SELECT * FROM candidates WHERE source_type='cninfo_irm'")}
        self.assertEqual({k: (r["status"], r["origin"]) for k, r in rows.items()}, {
            "1.6T 光模块出货情况?": ("pending", "backfill"), "公司分红计划?": ("rejected", "backfill"),
            "800G 新客户?": ("pending", "backfill")})
        self.assertEqual(rows["800G 新客户?"]["date"], "2026-07-20")                   # 回答的日子是可知日
        self.assertTrue(rows["800G 新客户?"]["url"].endswith("questionId=q4"))
        # 定时抓取:只取深交所公司,只取已回答的
        companies, _ = news.build_vocab(self.conn)
        src = next(x for x in news.load_spec()["sources"] if x["type"] == "cninfo_irm")
        live_calls = []

        def live(url, params=None, data=None, **kw):
            if url.endswith("queryKeyboardInfo"):
                return {"data": [{"code": params and params.get("keyWord") or "", "secid": "99000"}]}
            live_calls.append(params["stockcode"])
            return pages[("2026-07-01", 1)]

        with mock.patch.object(news.http, "get_json", side_effect=live), mock.patch.object(news.time, "sleep"):
            items = news.fetch_cninfo_irm(src, {"timeout": 5, "recent_days": 14}, companies, log=lambda *_: None)
        self.assertTrue(items and all(it["summary"] for it in items))                 # 没回答的不要
        self.assertTrue(live_calls and all(news.is_szse(c) for c in live_calls))      # 只问深交所公司,上交所 / 北交所不走互动易

    def test_irm_upload_fallback(self):
        out = upload(self.conn, "candidates", None, [
            {"url": "https://sns.sseinfo.com/q/1", "title": "公司CW光源进展?", "summary": "公司CW光源已通过客户认证并小批量出货。",
             "date": "2026-07-10", "source": "上证e互动", "source_type": "cninfo_irm", "company_id": "cn.688498", "origin": "backfill"}])
        r = dict(self.conn.execute("SELECT * FROM candidates WHERE id=?", (news.cand_id("https://sns.sseinfo.com/q/1"),)).fetchone())
        self.assertEqual((r["source_type"], r["tier"], r["status"], r["part_id"]), ("cninfo_irm", 0, "pending", "part.cw-laser"))
        with self.assertRaises(ValueError):
            upload(self.conn, "candidates", None, [{"url": "https://x/2", "title": "t", "source_type": "rss"}])

    def test_hint_calibration(self):
        ACC.account(self.conn)
        hint = self._todo("mingpu-lpo")["hint"]
        self.assertIn("只要包含这个部件所属的产品族就算", hint)
        self.assertIn("不要求点名本型号或 NVIDIA", hint)
        self.assertIn("募资公告里明确的建设项目本身按扩产判", hint)

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
