"""候选自动入账 v2:规则只挡与归位,判定交 AI。事件入账与价值判定是系统的事,人不逐条确认。

规格:docs/claude/teardown-accounting-v2.md §1。每条还没人判过的候选按下面的顺序走,前一步命中即返回:

  1.1 挡     relevance=0,或标题命中例行正则(募资安排 / 发行上市 / 定期报告 / 盘面汇总;英文源另有一组)→ 例行,不算。
             投资者关系活动记录表不挡(标题没信息,交给 AI 读正文)。
  1.2 归位   命中的公司都不站在这只模块的任何部件上(Meta / 微软 / 需求侧)→ 例行。
             只命中一家时给一个部件初判:标题 / 摘要命中的部件词里有它站着的部件就取它,否则取 physical.part_for_event。
  1.3 强命中 第 0 层来源(巨潮公告 / 互动易 / tier=0 的 upload)+ 部件词或强产品词 + 标题有类别动词 + 六类之一且有日期
             → 自动入账(decided_by=rule,thesis=标题,confidence=3;类别取标题里那个动词的类别)。
  1.4 其余   → 交给 AI:开一条 ingest_todo(kind=candidate_triage,company_id 列放候选 id),hint 是结构化任务,
             AI 判完 POST /api/candidates/judge 批量交回。综合媒体(tier ≥ 2)标题里没有部件 / 产品词的、
             回填(origin=backfill)的没有部件 / 产品词的(没取到正文的活动记录表除外),直接例行,不喂给 AI。
             7 天没判的待办作废(dropped),候选保持 pending。

规则只动还没人判过的候选(pending 且 decided_by 为空);AI 或人判过的不再改。
v1 规则自动入账的候选在第一次跑 v2 的 triage 时重开重判(rejudge);人工「不算」过的不动。
人工只剩「不算」:对已入账的事件说不算(POST /api/events/{id}/dismiss),可撤回。"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta

from .. import physical as PH
from ..market import CATEGORY_LABEL
from . import candidates as C
from . import news
from .recompute import latest_bar_date, rebuild_reactions

EVENT_CATEGORIES = C.EVENT_CATEGORIES     # 卡口事件的六类
OFFICIAL_TIER = 0          # 公告 / 互动易
RULES_VERSION = "v2"       # settings.accounting_rules:库里的候选按哪一版规则判过
TRIAGE_TTL_DAYS = 7        # 交给 AI 的待办,这么多天没判就作废
RULE_CONFIDENCE = 3


def _companies(c: dict) -> set[str]:
    ids = {x.get("companyId") for x in json.loads(c.get("companies") or "[]") if x.get("companyId")}
    if c.get("company_id"):
        ids.add(c["company_id"])
    return ids


def _parts_hit(c: dict, vocab: tuple[dict, dict] | None, text: str) -> list[str]:
    """标题 / 摘要命中的部件(词表现算一遍,加上抓取时记下的 part_ids)。"""
    hits = list(json.loads(c.get("part_ids") or "[]")) if isinstance(c.get("part_ids"), str) else list(c.get("part_ids") or [])
    if vocab:
        hits = news.parts_in_order(text, vocab[1]) + hits
    return list(dict.fromkeys(h for h in hits if h))


def initial_part(conn: sqlite3.Connection, company_id: str, category: str | None, hits: list[str]) -> str | None:
    """部件初判:命中的部件词里有这家公司站着的部件就取它(按在文中出现的先后取第一个),否则按 part_for_event。"""
    mine = {p["part_id"] for p in PH.company_parts(conn, company_id)}
    for p in hits:
        if p in mine:
            return p
    best = PH.part_for_event(conn, company_id, category)
    return best["part_id"] if best else None


def classify(conn: sqlite3.Connection, c: dict, vocab: tuple[dict, dict] | None = None) -> tuple[str, str, str | None]:
    """→ ("auto" | "routine" | "triage", 一句话理由, 部件初判)。vocab = news.build_vocab(conn),批量跑时传进来省得重建。"""
    title = c.get("title") or ""
    text = f"{title} {c.get('summary') or ''}"
    tier = c.get("tier")
    # 1.1 挡
    if not c.get("relevance", 1):
        return "routine", "例行公告,不算", None
    hit = news.routine_hit(title, c.get("source_type"))
    if hit:
        return "routine", f"例行(「{hit}」),不算", None
    # 1.2 归位
    ids = _companies(c)
    placed = [i for i in ids if PH.company_parts(conn, i)]
    if ids and not placed:
        return "routine", "公司不在这只模块的任何部件上", None
    hits = _parts_hit(c, vocab, text)
    title_hits = _parts_hit({}, vocab, title) if vocab else []
    verb = news.category_verb(title)
    part_id, problem = None, None
    if not ids:
        problem = "没命中公司"
        part_id = hits[0] if hits else None
    elif len(ids) > 1:
        problem = f"命中 {len(ids)} 家公司,要定是哪一家"
    else:
        part_id = initial_part(conn, next(iter(ids)), verb[1] if verb else c.get("category"), hits)   # 动词的类别比关键词计数准
    # 1.3 强命中
    product = news.product_hit(text) or bool(hits)
    category_ok = c.get("category") in EVENT_CATEGORIES
    if not problem and tier == OFFICIAL_TIER and product and verb and category_ok and c.get("date"):
        return "auto", f"自动入账 · {c.get('source') or '公告'} · 「{verb[0]}」", part_id
    # 1.4 其余交给 AI;综合媒体与回填先过一道门槛
    ir = news.IR_RECORD in title
    if (tier or 0) >= 2 and not (news.product_hit(title) or title_hits):
        return "routine", "综合媒体,标题里没有部件 / 产品词", None
    if c.get("origin") == "backfill" and not product and not (ir and not (c.get("summary") or "").strip()):
        return "routine", "回填,没有部件 / 产品词", None               # 活动记录表没取到正文的,照旧交 AI 读原文
    why = [problem] if problem else []
    if ir:
        why.append("投资者关系活动记录,要读正文")
    elif tier == OFFICIAL_TIER:
        if not product:
            why.append("公告里没有部件 / 产品词")
        if not verb:
            why.append("标题里没有类别动词")
        if not category_ok:
            why.append("没有类别" if not c.get("category") else f"类别「{CATEGORY_LABEL.get(c['category'], c['category'])}」不是卡口事件")
        if not c.get("date"):
            why.append("没有日期")
    elif tier == 1:
        why.append("行业媒体,要核实")
    else:
        why.append("综合 / 泛科技媒体,要核实")
    return "triage", ";".join(why), part_id


# ------------------------------------------------------------------ 交给 AI 的任务
JUDGE_FORMAT = ('{"by":"ai","items":[{"id":"<候选 id>","is_chokepoint":true,"part_id":"part.…","category":"capex|order|qualification|supply|price|roadmap",'
                '"date":"YYYY-MM-DD","thesis":"一句话:这件事对这个部件意味着什么","confidence":1-5,"reason":"原文依据"},'
                '{"id":"<候选 id>","is_chokepoint":false,"reason":"为什么不是"}]}')


def _hint(conn: sqlite3.Connection, c: dict, reason: str, part_id: str | None) -> str:
    ids = sorted(_companies(c))
    if len(ids) == 1:
        b = conn.execute("SELECT short_name, name FROM companies WHERE id=?", (ids[0],)).fetchone()
        who = (b["short_name"] or b["name"]) if b else ids[0]
    else:
        who = f"命中的 {len(ids)} 家之一({'、'.join(ids)};交回时给 company_id)" if ids else "某家公司(没命中,交回时给 company_id)"
    p = conn.execute("SELECT name FROM physical_parts WHERE id=?", (part_id,)).fetchone() if part_id else None
    where = f"{PH.short_name(p['name'])}({part_id})" if p else "未定的部件(交回时给 part_id)"
    return (f"判断这条候选是不是「{who} 在 {where} 上的卡口事件」:「{c['title']}」{c['url']}"
            f"(来源 {c.get('source')},{c.get('date') or '无日期'};候选 {c['id']};规则交给你的原因:{reason})。\n"
            "卡口事件 = 会改变这家公司在这个部件上的供给 / 需求 / 价格 / 技术路线的事:扩产(新产线、投产)、订单合同、"
            "认证导入(送样、批量出货、通过认证)、供需(缺货、交期、分配)、涨价、技术路线(CPO / LPO / 硅光 / 1.6T 路线变化)。\n"
            "不是:融资安排、股权变动、人事、会议、财报预告、泛行业新闻、与这只 1.6T 光模块无关的业务。\n"
            f"交回:POST /api/candidates/judge,格式 {JUDGE_FORMAT}(一批最多 200 条)。")


def _open_triage(conn: sqlite3.Connection, c: dict, reason: str, part_id: str | None, now: str) -> None:
    """已经作废(dropped)的待办不重开;hint / reason 跟着最新一次规则走。"""
    conn.execute(
        """INSERT INTO ingest_todo (kind, company_id, hint, reason, status, created_at) VALUES ('candidate_triage',?,?,?,'open',?)
           ON CONFLICT(kind, company_id) DO UPDATE SET hint=excluded.hint, reason=excluded.reason""",
        (c["id"], _hint(conn, c, reason, part_id), reason, now))


def account(conn: sqlite3.Connection, recompute: bool = True) -> dict:
    """对所有还没人判过的候选跑一遍规则。入账的写成事件,例行的记不算,拿不准的开 candidate_triage 待办。"""
    out = {"auto": 0, "routine": 0, "triage": 0, "failed": 0}
    rows = [dict(r) for r in conn.execute("SELECT * FROM candidates WHERE status='pending' AND decided_by IS NULL ORDER BY COALESCE(date,''), id")]
    now = datetime.now().isoformat(timespec="seconds")
    vocab = news.build_vocab(conn) if rows else None
    for c in rows:
        way, reason, part_id = classify(conn, c, vocab)
        try:
            conn.execute("UPDATE candidates SET part_id=? WHERE id=?", (part_id, c["id"]))
            if way == "auto":                            # 类别以标题里的动词为准(强命中一定有)
                C.confirm(conn, c["id"], company_id=next(iter(_companies(c))), category=news.category_verb(c["title"])[1],
                          note=reason, by="rule", recompute=False, part_id=part_id, thesis=c["title"], confidence=RULE_CONFIDENCE)
            elif way == "routine":
                C.reject(conn, c["id"], note=reason, by="rule", commit=False)
            else:
                _open_triage(conn, c, reason, part_id, now)
            out[way] += 1
        except (ValueError, LookupError) as e:        # 数据不全到连规则都判不了:也交给 AI
            _open_triage(conn, c, str(e), part_id, now)
            out["failed"] += 1
    conn.commit()
    if recompute and out["auto"]:
        when = latest_bar_date(conn)
        if when:
            out.update(rebuild_reactions(conn, when))
    return out


def expire_triage(conn: sqlite3.Connection, days: int = TRIAGE_TTL_DAYS, now: datetime | None = None) -> int:
    """交给 AI 超过 days 天还没判的待办作废(dropped);候选保持 pending,规则改了之后仍会重判。"""
    now = now or datetime.now()
    cur = conn.execute("UPDATE ingest_todo SET status='dropped', done_at=? WHERE kind='candidate_triage' AND status='open' AND created_at < ?",
                       (now.isoformat(timespec="seconds"), (now - timedelta(days=days)).isoformat(timespec="seconds")))
    conn.commit()
    return cur.rowcount


def rejudge(conn: sqlite3.Connection) -> int:
    """规则换版后第一次跑:上一版规则自动入账的候选全部重开(事件随之删掉),交给这一版重判。
    人判过的(不算 / 撤回)与 AI 判过的不动。版本记在 settings.accounting_rules,同一版只做一次。"""
    r = conn.execute("SELECT value FROM settings WHERE key='accounting_rules'").fetchone()
    if r and r["value"] == RULES_VERSION:
        return 0
    ids = [x["id"] for x in conn.execute("SELECT id FROM candidates WHERE status='confirmed' AND decided_by='rule'")]
    for cid in ids:
        C.reopen(conn, cid)
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('accounting_rules', ?)", (RULES_VERSION,))
    conn.commit()
    return len(ids)


def summary(conn: sqlite3.Connection) -> dict:
    """收件箱那一行状态:候选多少,入账多少(规则 / AI),交给 AI 判多少,例行多少,不算多少;回填多少、其中入账多少;作废的待办。"""
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
        "backfill": q("SELECT COUNT(*) FROM candidates WHERE origin='backfill'"),
        "backfill_accounted": q("SELECT COUNT(*) FROM candidates WHERE origin='backfill' AND status='confirmed'"),
        "expired": q("SELECT COUNT(*) FROM ingest_todo t JOIN candidates c ON c.id = t.company_id "
                     "WHERE t.kind='candidate_triage' AND t.status='dropped' AND c.status='pending'"),
        "unprocessed": q("SELECT COUNT(*) FROM candidates WHERE status='pending' AND decided_by IS NULL AND id NOT IN "
                         "(SELECT company_id FROM ingest_todo WHERE kind='candidate_triage' AND status IN ('open','dropped'))"),
    }
