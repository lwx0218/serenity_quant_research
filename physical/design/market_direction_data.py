# -*- coding: utf-8 -*-
"""方向稿「物理页 · 事件 / 资金投票」的数据：一个演示库 + 部件级读数。

演示库：按服务器的样子建（--no-sample），行情是按一套情景合成的，事件走真实的
候选 → 确认路径写进去；反应、篮子、拥挤度、结论句全部由 api/app 里的现成代码算。
所以方向稿上的数字是「实现以后会怎么算」，不是手填的；但行情与事件本身是编的，页脚标样式示例。

部件级读数（part_activity / part_detail）是这次要新加的后端，先在这里成形，
方向稿通过后搬进 api/app/market.py。

    python3 physical/design/market_direction_data.py   # 打印读数，自检用
"""
from __future__ import annotations

import os
import random
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_DB = Path(tempfile.mkdtemp(prefix="teardown-direction-")) / "demo.sqlite"
os.environ["SQR_DB_PATH"] = str(_DB)
sys.path.insert(0, str(REPO / "api"))

from app import analytics as A  # noqa: E402
from app import insights, market  # noqa: E402
from app.db import connect  # noqa: E402
from app.ingest import candidates as C  # noqa: E402
from app.ingest import crowding as CR  # noqa: E402
from app.ingest import news, recompute  # noqa: E402
from app.ingest.recompute import part_basket_members  # noqa: E402
from app.ingest.schema import ensure_schema  # noqa: E402
from app.ingest.symbols import is_a_share, quotable  # noqa: E402
from app.ingest.upload import upload  # noqa: E402
from app.seed import rebuild  # noqa: E402

AS_OF = date(2026, 9, 25)
WINDOW = 7          # 首页读数窗口（天），与 Explorer 首页一致
EVENTS_DAYS = 30    # 选中部件：卡口事件窗口
MONTHS = 3          # 选中部件：篮子走势窗口

# ---------------------------------------------------------------- 情景
# 每个部件的日漂移：(近三个月, 最近一周)。公司取它所在部件的平均。
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


def build_demo_db():
    rebuild(_DB, include_sample=False)
    conn = connect(_DB)
    ensure_schema(conn)
    rng = random.Random(20260925)
    days = _trading_days(date(2025, 6, 2), AS_OF)
    last3m, last7 = days[-63], AS_OF - timedelta(days=WINDOW)
    parts_of: dict[str, list[str]] = {}
    for r in conn.execute("SELECT part_id, company_id FROM physical_part_companies WHERE company_id IS NOT NULL"):
        parts_of.setdefault(r["company_id"], []).append(r["part_id"])
    impulse = {}
    for d, cid, *_rest in EVENTS:
        d0 = date.fromisoformat(d)
        d0 = d0 if A.is_trading_day(d0) else A.next_trading_day(d0)      # 与确认时的顺延同一条规则
        t1 = A.add_trading_days(d0, 1)
        impulse[(cid, t1)] = (_rest[4], _rest[5])
    missing = {"cn.920821", "cn.920045", "cn.920060", "cn.920179", "global.tuc"}     # 服务器上现在拿不到的五家
    cos = [dict(r) for r in conn.execute("SELECT * FROM companies") if quotable(dict(r)) and r["id"] not in missing]
    drift = {}
    for c in cos:
        themes = [THEME.get(p, (0.0, 0.0)) for p in parts_of.get(c["id"], [])] or [(0.0, 0.0)]
        drift[c["id"]] = (sum(t[0] for t in themes) / len(themes), sum(t[1] for t in themes) / len(themes))
    m3, m7 = (sum(v[i] for v in drift.values()) / len(drift) for i in (0, 1))      # 只留相对强弱,没有整体行情
    for c in cos:
        d3, d7 = drift[c["id"]][0] - m3, drift[c["id"]][1] - m7
        px, rows = 20 + rng.random() * 80, []
        for day in days:
            r = rng.gauss(0.0003, 0.014)
            if day >= last3m:
                r += d3
            if day > last7:
                r += d7
            imp, vm = impulse.get((c["id"], day), (0.0, 1.0))
            px *= 1 + r + imp
            vol = abs(rng.gauss(1, 0.18)) * 1e7 * vm
            rows.append({"date": day.isoformat(), "open": px, "high": px * 1.01, "low": px * 0.99, "close": px, "volume": vol,
                         "amount": vol * px, "turnover_pct": vol / 2e8 * 100 if is_a_share(c) else None})
        upload(conn, "bars", c["id"], rows, source="demo")
    recompute.recompute_all(conn)
    CR.rebuild_crowding(conn)
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


# ---------------------------------------------------------------- 部件级读数（待搬进 api/app/market.py）
def short(n: str) -> str:
    return n.split("（")[0].split("(")[0]


def label(n: str) -> str:
    """句子里用的短名:「光源耦合：隔离器 / 透镜 / 保偏光纤」→「光源耦合」。"""
    return short(n).split("：")[0]


def part_rows(conn) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT id, name, sort FROM physical_parts ORDER BY sort, id")]


def part_events(conn, part_id: str, days: int, when: date) -> list[dict]:
    """落在这个部件上的事件：与收件箱「→ 部件」同一条规则（physical.part_for_event）。"""
    return [e for e in market.list_events(conn, days=days, limit=500, when=when) if (e.get("part") or {}).get("part_id") == part_id]


def part_activity(conn, days: int = WINDOW, when: date | None = None) -> list[dict]:
    """每个部件：窗口内落在它上面的事件数、部件篮子相对整机的超额与方向（与 layer_activity 同一套阈值）。"""
    when = when or market.as_of(conn)
    start = when - timedelta(days=days)
    product = market.load_series(conn, f"basket:{market.product_id(conn)}", start - timedelta(days=10))
    events = market.list_events(conn, days=days, limit=500, when=when)
    out = []
    for p in part_rows(conn):
        n = sum(1 for e in events if (e.get("part") or {}).get("part_id") == p["id"])
        basket = market.load_series(conn, f"basket:{p['id']}", start - timedelta(days=10))
        exc = A.excess_return(basket, product, start, when) if basket else None
        direction = None
        if exc is not None and (n > 0 or abs(exc) >= 0.01):
            direction = "pos" if exc >= A.REACTION_THRESHOLD else "neg" if exc <= -A.REACTION_THRESHOLD else "neu"
        out.append({"id": p["id"], "name": label(p["name"]), "full_name": short(p["name"]), "events": n, "basket_excess": exc, "direction": direction,
                    "members": len(part_basket_members(conn, p["id"])), "has_basket": bool(basket)})
    return out


def overview_conclusion(activity: list[dict], events: list[dict], days: int) -> dict:
    """首页那句「资金本周在给谁投票」，单位从层换成部件。"""
    evs = [dict(e, layer_ids=[(e.get("part") or {}).get("part_id")]) for e in events]
    c = insights.overview(activity, evs, days)
    return {**c, "text": c["text"].replace("环节内", "部件内")}


def part_detail(conn, part_id: str, when: date | None = None) -> dict:
    when = when or market.as_of(conn)
    pid = market.product_id(conn)
    start = when - timedelta(days=30 * MONTHS)
    b = market.load_series(conn, f"basket:{part_id}", start - timedelta(days=10))
    p = market.load_series(conn, f"basket:{pid}", start - timedelta(days=10))
    name = label(conn.execute("SELECT name FROM physical_parts WHERE id=?", (part_id,)).fetchone()["name"])
    members = part_basket_members(conn, part_id)
    cr = market.crowding_for(conn, f"basket:{part_id}")
    evs30 = part_events(conn, part_id, EVENTS_DAYS, when)
    exc7 = A.excess_return(b, p, when - timedelta(days=WINDOW), when) if b else None
    exc3 = A.excess_return(b, p, start, when) if b else None
    basket_c = insights.basket({"excess_window": exc3, "crowding": cr, "efficacy": None, "window_months": MONTHS}) if b else None
    if basket_c:
        basket_c["text"] = basket_c["text"].replace("环节相对整机", "部件篮子相对整机").replace("环节级仓位", "部件级仓位")
    chart_events = []
    if b:
        idx = A.index_to(b, start)
        for e in part_events(conn, part_id, 30 * MONTHS, when):
            v = A.value_at(idx, date.fromisoformat(e["date"]))
            if v is not None:
                chart_events.append({"id": e["id"], "date": e["date"], "label": e["category_label"], "value": round(v, 2),
                                     "company": (e["company"] or {}).get("short_name")})
    return {
        "part_id": part_id, "name": name, "as_of": when.isoformat(), "members": len(members),
        "series": {"subject": market.series_points(b, start) if b else [], "reference": market.series_points(p, start) if p else []},
        "chart_events": chart_events,
        "readings": {"excess_7d": exc7, "excess_3m": exc3,
                     "crowding": ({"metrics": cr["metrics"], "directions": cr["directions"], "level": cr["level"], "direction": cr["direction"]} if cr else None)},
        "basket_conclusion": basket_c,
        "events": [{k: e[k] for k in ("id", "date", "title", "category_label", "source_label", "source_url", "reaction", "volume_ratio", "freshness")}
                   | {"company": (e["company"] or {}).get("short_name"), "company_id": (e["company"] or {}).get("id")} for e in evs30],
        "events_conclusion": insights.layer_events(evs30, name),
    }


def build() -> dict:
    conn = build_demo_db()
    when = market.as_of(conn)
    act = part_activity(conn, WINDOW, when)
    events = market.list_events(conn, days=WINDOW, limit=500, when=when)
    last = {}
    for e in market.list_events(conn, days=EVENTS_DAYS, limit=500, when=when):
        pid = (e.get("part") or {}).get("part_id")
        if pid and pid not in last:
            last[pid] = {"date": e["date"], "company": (e["company"] or {}).get("short_name"), "category_label": e["category_label"],
                         "t1": e["reaction"]["t1"], "freshness": e["freshness"]}
    out = {
        "as_of": when.isoformat(), "window_days": WINDOW, "events_days": EVENTS_DAYS, "months": MONTHS,
        "conclusion": overview_conclusion(act, events, WINDOW),
        "activity": [a | {"last_event": last.get(a["id"])} for a in act],
        "parts": {},
    }
    for a in out["activity"]:
        d = part_detail(conn, a["id"], when)
        out["parts"][a["id"]] = d
        a["excess_3m"] = d["readings"]["excess_3m"]
        cr = d["readings"]["crowding"]
        a["crowd"] = {"level": cr["level"], "direction": cr["direction"], "ret20": cr["metrics"].get("ret20_pct_rank")} if cr else None
    conn.close()
    return out


if __name__ == "__main__":
    import json
    d = build()
    print(d["conclusion"])
    for a in d["activity"]:
        print(f"{a['name'][:10]:12} ev={a['events']} 7d={insights.pct(a['basket_excess']):>7} 3m={insights.pct(a['excess_3m']):>7} crowd={a['crowd'] and a['crowd']['level']}/{a['crowd'] and a['crowd']['direction']} dir={a['direction']} members={a['members']} last={a['last_event'] and (a['last_event']['date'], a['last_event']['company'])}")
    for pid in ("part.cw-laser", "part.dsp", "part.laser-coupling"):
        p = d["parts"][pid]
        print(pid, p["basket_conclusion"], p["events_conclusion"], len(p["events"]), len(p["chart_events"]))
    print(len(json.dumps(d, ensure_ascii=False)) // 1024, "KB")
