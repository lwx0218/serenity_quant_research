"""候选自动入账:事件入账与价值判定是系统的事,人不逐条确认。

每条待判的候选按下面的规则分三路(规则都在 classify 里,门槛改这里):

  入账   值得看(relevance=1)、只命中一家公司、有类别与日期,并且
         · 来源是第 0 层(巨潮公告 / 互动易,或 AI 从这类来源交回的)→ 直接入账;
         · 来源是第 1 层(行业垂直媒体)且另有至少一家来源报道(also_reported_by)→ 入账。
  例行   例行公告(relevance=0:减持、质押、股东大会……)→ 不算。
  拿不准 其余(命中多家 / 没命中公司 / 缺类别或日期 / 只有一家媒体 / 综合与泛科技媒体)
         → 留在候选池,开一条 ingest_todo(kind=candidate_triage,company_id 列放候选 id)交给服务器上的 AI 判;
           AI 判完用 POST /api/candidates/{id}/confirm(补公司 / 类别 / 日期)或 /reject 交回,待办随之关闭。

规则只动还没人判过的候选(pending 且 decided_by 为空);AI 或人判过的不再改。
人工只剩「不算」:对已入账的事件说不算(POST /api/events/{id}/dismiss),可撤回。"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from ..market import CATEGORY_LABEL
from . import candidates as C
from .recompute import latest_bar_date, rebuild_reactions

EVENT_CATEGORIES = ("capex", "order", "qualification", "supply", "price", "roadmap")     # 卡口事件的六类
OFFICIAL_TIER = 0          # 公告 / 互动易
TRADE_MEDIA_TIER = 1       # 行业垂直媒体:要有第二家来源


def _companies(c: dict) -> set[str]:
    ids = {x.get("companyId") for x in json.loads(c.get("companies") or "[]") if x.get("companyId")}
    if c.get("company_id"):
        ids.add(c["company_id"])
    return ids


def classify(conn: sqlite3.Connection, c: dict) -> tuple[str, str]:
    """→ ("auto" | "routine" | "triage", 一句话理由)。"""
    if not c.get("relevance", 1):
        return "routine", "例行公告,不算"
    missing = []
    ids = _companies(c)
    if not ids:
        missing.append("没命中公司")
    elif len(ids) > 1:
        missing.append(f"命中 {len(ids)} 家公司,要定是哪一家")
    elif not conn.execute("SELECT 1 FROM companies WHERE id=?", (next(iter(ids)),)).fetchone():
        missing.append("公司不在主数据里")
    if c.get("category") not in EVENT_CATEGORIES:
        missing.append("没有类别" if not c.get("category") else f"类别「{CATEGORY_LABEL.get(c['category'], c['category'])}」不是卡口事件")
    if not c.get("date"):
        missing.append("没有日期")
    others = json.loads(c.get("also_reported_by") or "[]")
    tier = c.get("tier")
    if not missing:
        if tier == OFFICIAL_TIER:
            return "auto", f"自动入账 · {c.get('source') or '公告'}"
        if tier == TRADE_MEDIA_TIER and others:
            return "auto", f"自动入账 · {c.get('source')} 等 {1 + len(others)} 家报道"
        missing.append("只有一家行业媒体报道" if tier == TRADE_MEDIA_TIER else "综合 / 泛科技媒体,要核实")
    return "triage", ";".join(missing)


def _hint(c: dict, reason: str) -> str:
    return (f"判断这条候选算不算卡口事件({reason}):「{c['title']}」{c['url']}(来源 {c.get('source')},{c.get('date') or '无日期'})。"
            f"算:POST /api/candidates/{c['id']}/confirm {{company_id, category, date}}(类别:扩产 capex / 订单 order / 认证 qualification / "
            f"供需 supply / 涨价 price / 技术路线 roadmap);不算:POST /api/candidates/{c['id']}/reject {{note}}。")


def account(conn: sqlite3.Connection, recompute: bool = True) -> dict:
    """对所有还没人判过的候选跑一遍规则。入账的写成事件,例行的记不算,拿不准的开 candidate_triage 待办。"""
    out = {"auto": 0, "routine": 0, "triage": 0, "failed": 0}
    rows = [dict(r) for r in conn.execute("SELECT * FROM candidates WHERE status='pending' AND decided_by IS NULL ORDER BY COALESCE(date,''), id")]
    now = datetime.now().isoformat(timespec="seconds")
    for c in rows:
        way, reason = classify(conn, c)
        try:
            if way == "auto":
                C.confirm(conn, c["id"], company_id=next(iter(_companies(c))), note=reason, by="rule", recompute=False)
            elif way == "routine":
                C.reject(conn, c["id"], note=reason, by="rule")
            else:
                conn.execute(
                    """INSERT INTO ingest_todo (kind, company_id, hint, reason, status, created_at) VALUES ('candidate_triage',?,?,?,'open',?)
                       ON CONFLICT(kind, company_id) DO UPDATE SET hint=excluded.hint, reason=excluded.reason""",
                    (c["id"], _hint(c, reason), reason, now))
            out[way] += 1
        except (ValueError, LookupError) as e:        # 数据不全到连规则都判不了:也交给 AI
            conn.execute(
                """INSERT INTO ingest_todo (kind, company_id, hint, reason, status, created_at) VALUES ('candidate_triage',?,?,?,'open',?)
                   ON CONFLICT(kind, company_id) DO UPDATE SET hint=excluded.hint, reason=excluded.reason""",
                (c["id"], _hint(c, str(e)), str(e), now))
            out["failed"] += 1
    conn.commit()
    if recompute and out["auto"]:
        when = latest_bar_date(conn)
        if when:
            out.update(rebuild_reactions(conn, when))
    return out


def summary(conn: sqlite3.Connection) -> dict:
    """收件箱那一行状态:候选多少,入账多少(规则 / AI),交给 AI 判多少,例行多少,不算多少。"""
    q = lambda s: conn.execute(s).fetchone()[0]  # noqa: E731
    return {
        "total": q("SELECT COUNT(*) FROM candidates"),
        "accounted": q("SELECT COUNT(*) FROM candidates WHERE status='confirmed'"),
        "by_rule": q("SELECT COUNT(*) FROM candidates WHERE status='confirmed' AND decided_by='rule'"),
        "by_ai": q("SELECT COUNT(*) FROM candidates WHERE status='confirmed' AND COALESCE(decided_by,'ai')='ai'"),
        "by_human": q("SELECT COUNT(*) FROM candidates WHERE status='confirmed' AND decided_by='human'"),
        "to_ai": q("SELECT COUNT(*) FROM ingest_todo WHERE kind='candidate_triage' AND status='open'"),
        "routine": q("SELECT COUNT(*) FROM candidates WHERE status='rejected' AND decided_by='rule'"),
        "not_counted": q("SELECT COUNT(*) FROM candidates WHERE status='rejected' AND COALESCE(decided_by,'ai') IN ('ai','human')"),
        "dismissed_by_human": q("SELECT COUNT(*) FROM candidates WHERE status='rejected' AND decided_by='human'"),
        "unprocessed": q("SELECT COUNT(*) FROM candidates WHERE status='pending' AND decided_by IS NULL AND id NOT IN "
                         "(SELECT company_id FROM ingest_todo WHERE kind='candidate_triage' AND status='open')"),
    }
