"""测试夹具:物理页「资金投票」的演示库(原方向稿 market_direction_data.build_demo_db)。

按服务器的样子建(--no-sample),行情按一套情景合成,事件走真实的候选 → 确认路径写进去;
反应、篮子、拥挤度都由 app 里的代码算。情景行情只进测试库,不进业务库。

情景(截至 2026-09-25):CW 激光器本周被买(三条事件同向、篮子跑赢整机)、光纤阵列单元跟随、
DSP 与主 PCB 走弱、光库科技的技术路线传闻被卖出;另有 5 家拿不到行情(与服务器首轮一致)。"""
from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from app import analytics as A
from app.db import connect
from app.ingest import candidates as C
from app.ingest import crowding as CR
from app.ingest import news, recompute
from app.ingest.schema import ensure_schema
from app.ingest.symbols import is_a_share, quotable
from app.ingest.upload import upload
from app.seed import rebuild

AS_OF = date(2026, 9, 25)
OBJECT = "om.1p6t.osfp.dr8.siph"
MISSING = {"cn.920821", "cn.920045", "cn.920060", "cn.920179", "global.tuc"}     # 服务器上现在拿不到的五家

# 每个部件的日漂移:(近三个月, 最近一周)。公司取它所在部件的平均,再减去全体均值(只留相对强弱)。
THEME = {
    "part.cw-laser": (0.0026, 0.0085), "part.fau": (0.0010, 0.0040), "part.laser-coupling": (0.0006, -0.0020),
    "part.module-maker": (0.0012, 0.0012), "part.pic": (0.0010, 0.0008), "part.engine-assembly": (0.0008, 0.0010),
    "part.dsp": (-0.0004, -0.0045), "part.driver": (0.0, -0.0012), "part.tia": (0.0, -0.0010),
    "part.pcb": (0.0016, -0.0030), "part.mpo": (0.0006, 0.0020), "part.pd": (0.0006, 0.0010),
    "part.host-cage": (0.0, 0.0), "part.power-mgmt": (0.0, 0.0), "part.lid-thermal": (0.0002, 0.0), "part.shell": (0.0, 0.0),
}
# (日期, 公司, 类别, 来源类型, 层级, 标题, T+1 冲击, T+1 量比倍数)
EVENTS = [
    ("2026-09-03", "cn.688313", "capex", "cninfo_announcement", 0, "仕佳光子:关于投资建设高功率 CW 光源芯片产线的公告", 0.015, 1.4),
    ("2026-09-10", "cn.300570", "order", "cninfo_announcement", 0, "太辰光:关于签订日常经营重大合同的公告", 0.020, 1.7),
    ("2026-09-15", "cn.300308", "order", "cninfo_announcement", 0, "中际旭创:关于签订日常经营重大合同的公告", 0.035, 2.2),
    ("2026-09-15", "cn.300502", "capex", "cninfo_announcement", 0, "新易盛:关于泰国工厂三期扩产项目的公告", 0.000, 1.0),
    ("2026-09-18", "global.lumentum", "supply", "rss", 1, "Lumentum:200G EML 与 CW 光源供给紧张将持续到 2027 年", 0.048, 2.0),
    ("2026-09-18", "global.marvell", "roadmap", "rss", 1, "Marvell 更新 1.6T / 3.2T 路线图,线性直驱方案占比预期上调", -0.040, 1.8),
    ("2026-09-21", "cn.688498", "price", "cninfo_irm", 0, "源杰科技:投资者关系活动记录表(CW 光源报价上调)", 0.055, 2.6),
    ("2026-09-21", "cn.300394", "qualification", "cninfo_irm", 0, "天孚通信:投资者关系活动记录表(1.6T FAU 与光引擎送样进展)", 0.032, 1.9),
    ("2026-09-22", "cn.300620", "roadmap", "rss", 1, "光库科技薄膜铌酸锂调制器进入 3.2T 平台验证", -0.030, 0.7),
    ("2026-09-23", "cn.688048", "qualification", "cninfo_announcement", 0, "长光华芯:关于大功率 CW 光源通过客户认证的公告", 0.030, 1.8),
    ("2026-09-23", "cn.002281", "capex", "cninfo_announcement", 0, "光迅科技:关于投资建设高速光器件产线的公告", -0.005, 1.5),
    ("2026-09-24", "cn.300476", "capex", "cninfo_announcement", 0, "胜宏科技:关于投资建设高多层板产能的公告", 0.002, 1.1),
]
SOURCE_NAME = {"cninfo_announcement": "巨潮资讯 · 公告", "cninfo_irm": "互动易", "rss": "行业媒体"}


def _trading_days(start: date, end: date) -> list[date]:
    out, d = [], start
    while d <= end:
        if A.is_trading_day(d):
            out.append(d)
        d += timedelta(days=1)
    return out


def build_demo_db(db_path: Path) -> sqlite3.Connection:
    """在 db_path 建好演示库并返回连接(调用方负责关)。"""
    rebuild(Path(db_path), include_sample=False)
    conn = connect(db_path)
    ensure_schema(conn)
    rng = random.Random(20260925)
    days = _trading_days(date(2025, 6, 2), AS_OF)
    last3m, last7 = days[-63], AS_OF - timedelta(days=7)
    parts_of: dict[str, list[str]] = {}
    for r in conn.execute("SELECT part_id, company_id FROM physical_part_companies WHERE company_id IS NOT NULL"):
        parts_of.setdefault(r["company_id"], []).append(r["part_id"])
    impulse = {}
    for d, cid, *_rest in EVENTS:
        d0 = date.fromisoformat(d)
        d0 = d0 if A.is_trading_day(d0) else A.next_trading_day(d0)      # 与确认时的顺延同一条规则
        impulse[(cid, A.add_trading_days(d0, 1))] = (_rest[4], _rest[5])
    cos = [dict(r) for r in conn.execute("SELECT * FROM companies") if quotable(dict(r)) and r["id"] not in MISSING]
    drift = {}
    for c in cos:
        themes = [THEME.get(p, (0.0, 0.0)) for p in parts_of.get(c["id"], [])] or [(0.0, 0.0)]
        drift[c["id"]] = (sum(t[0] for t in themes) / len(themes), sum(t[1] for t in themes) / len(themes))
    m3, m7 = (sum(v[i] for v in drift.values()) / len(drift) for i in (0, 1))
    for c in cos:
        d3, d7 = drift[c["id"]][0] - m3, drift[c["id"]][1] - m7
        px, rows = 20 + rng.random() * 80, []
        for day in days:
            r = rng.gauss(0.0003, 0.014) + (d3 if day >= last3m else 0.0) + (d7 if day > last7 else 0.0)
            imp, vm = impulse.get((c["id"], day), (0.0, 1.0))
            px *= 1 + r + imp
            vol = abs(rng.gauss(1, 0.18)) * 1e7 * vm
            rows.append({"date": day.isoformat(), "open": px, "high": px * 1.01, "low": px * 0.99, "close": px, "volume": vol,
                         "amount": vol * px, "turnover_pct": vol / 2e8 * 100 if is_a_share(c) else None})
        upload(conn, "bars", c["id"], rows, source="scenario")
    recompute.recompute_all(conn)
    names = {r["id"]: r["short_name"] or r["name"] for r in conn.execute("SELECT id, name, short_name FROM companies")}
    items = []
    for d, cid, cat, st, tier, title, *_ in EVENTS:
        url = f"https://example.invalid/{cid}/{d}/{cat}"
        items.append({"id": news.cand_id(url), "date": d, "title": title, "url": url, "summary": "", "source": SOURCE_NAME[st],
                      "source_type": st, "tier": tier, "weight": 1.0, "evidence": news.TIER_EVIDENCE[tier], "category": cat,
                      "companies": [{"companyId": cid, "name": names[cid]}], "part_ids": [], "also_reported_by": []})
    news.store(conn, items)
    for it in items:
        C.confirm(conn, it["id"])
    CR.rebuild_crowding(conn)
    return conn
