"""Composition for the research pages: thesis tracking, the inbox's decision
list, and the per-layer rail. Sits on top of market.py and notes.py."""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import Any

from . import insights, market, notes as N
from .analytics import CROWD_SIGMA


def _label_for(conn: sqlite3.Connection, instrument: str) -> str:
    kind, _, ident = instrument.partition(":")
    if kind == "basket":
        m = market.module_of(conn, ident)
        return f"{m['name']}篮子相对整机" if m else f"{ident} 相对整机"
    c = market.company_brief(conn, ident)
    return (c["short_name"] if c else ident)


def thesis_view(conn: sqlite3.Connection, subject: str, when: date | None = None) -> dict | None:
    """A note plus its live tracking readings and a rule-based verdict line."""
    when = when or market.as_of(conn)
    n = N.load_note(subject)
    if not n:
        return None
    d = n.to_dict()
    pid = market.product_id(conn)
    since = date.fromisoformat(n.since) if n.since else None
    readings = []
    for inst in n.track:
        kind, _, ident = inst.partition(":")
        if not since:
            readings.append({"instrument": inst, "label": _label_for(conn, inst), "excess": None})
            continue
        if kind == "basket":
            exc = market.excess_since(conn, inst, f"basket:{pid}", since, when)
        else:
            layers = market.company_layers(conn, ident)
            ref = f"basket:{layers[0]}" if layers else f"basket:{pid}"
            exc = market.excess_since(conn, inst, ref, since, when)
        readings.append({"instrument": inst, "label": _label_for(conn, inst), "excess": exc})
    d["readings"] = readings
    d["conclusion"] = insights.thesis_tracking(d, readings)
    d["as_of"] = when.isoformat()
    until = date.fromisoformat(n.window_until) if n.window_until else None
    d["days_left"] = (until - when).days if until else None
    d["expired"] = bool(until and until <= when)
    d["expiring"] = bool(until and 0 <= (until - when).days <= 7)
    return d


def thesis_for_node(conn: sqlite3.Connection, node_id: str, when: date | None = None) -> dict | None:
    """A part inherits its module's judgement when it has none of its own."""
    v = thesis_view(conn, node_id, when)
    if v:
        return v
    m = market.module_of(conn, node_id)
    if m and m["id"] != node_id:
        return thesis_view(conn, m["id"], when)
    return None


def open_questions(conn: sqlite3.Connection) -> list[dict]:
    out = []
    for n in N.list_notes():
        for q in n.questions:
            if q["status"] != "open":
                continue
            out.append({"subject": n.subject, "subject_title": n.title or n.subject, "kind": n.kind, "index": q["index"],
                        "text": q["text"], "date": q["date"], "status": "待验证"})
    out.sort(key=lambda q: (q["date"] or ""), reverse=True)
    return out


def recent_notes(conn: sqlite3.Connection, limit: int = 5) -> list[dict]:
    items = []
    for n in N.list_notes():
        items.append({"subject": n.subject, "title": n.title or n.subject, "kind": n.kind, "direction": n.direction,
                      "updated": n.updated, "excerpt": N.excerpt(n.stance or n.body), "path": n.path})
    items.sort(key=lambda x: x["updated"] or "", reverse=True)
    return items[:limit]


def decisions(conn: sqlite3.Connection, when: date | None = None) -> list[dict]:
    """What needs a human today, most urgent first. Each item carries the
    direction it has for the reader's *current* judgements."""
    when = when or market.as_of(conn)
    items: list[dict] = []
    # 1. basket deviation alerts
    for m in market.module_rows(conn):
        cr = market.crowding_for(conn, f"basket:{m['id']}")
        if not cr:
            continue
        dev = cr["metrics"].get("deviation_sigma")
        if dev is not None and abs(dev) >= 2.0:
            side = "高位" if dev > 0 else "低位"
            items.append({
                "kind": "deviation", "urgency": 0, "label": "篮子偏离", "direction": "neg" if dev > 0 else "pos",
                "headline": f"{m['name']}篮子的{'拥挤告警' if dev > 0 else '出清信号'}",
                "text": f"{m['name']}篮子相对整机 {insights.sigma(dev)}({cr['window_days']} 日),拥挤度进入{side} —— "
                        + ("环节级仓位此时加,买到的是被投票过的那一半" if dev > 0 else "左侧位置,等第一条被确认的事件"),
                "actions": [{"label": "看篮子", "to": f"/baskets/{m['id']}"}, {"label": "知道了", "action": "dismiss"}],
                "subject": m["id"],
            })
    # 2. theses expiring / expired
    for n in N.list_notes():
        v = thesis_view(conn, n.subject, when)
        if not v or v["days_left"] is None or v["days_left"] > 7:
            continue
        lead = next((r for r in v["readings"] if r["excess"] is not None), None)
        reading = f"自判断起{lead['label']} {insights.pct(lead['excess'])}" if lead else "没有跟踪读数"
        thr = v.get("threshold_pct") or 3
        hit = lead and abs(lead["excess"]) * 100 >= thr
        score = "观察项,不记分" if v["direction"] == "neu" else ("已达" if hit else "未达") + f" ±{thr:g}% 阈值"
        items.append({
            "kind": "thesis", "urgency": 1, "label": "判断到期", "direction": "neu",
            "headline": f"{v['title']}的判断到期回顾",
            "text": f"{v['title']} · “{N.excerpt(v['stance'], 18)}” · 窗口 {v['window_until'][5:]} {'已到期' if v['expired'] else '到期'} · {reading},{score}",
            "actions": [{"label": "回顾", "to": f"/judgement/{v['subject']}"}, {"label": "延长一季", "action": "extend", "subject": v["subject"]}],
            "subject": v["subject"],
        })
    # 3. pending verifications
    for p in market.pending_verifications(conn, when=when):
        acts = ([{"label": "升级为候选", "action": "upgrade"}, {"label": "忽略", "action": "ignore"}] if p["kind"] == "upgrade"
                else [{"label": "审核", "action": "accept"}, {"label": "驳回", "action": "reject"}])
        items.append({"kind": "verify", "urgency": 2, "label": "待核验", "direction": p["direction"], "headline": f"{p['company']['short_name']}的一条待核验关系",
                      "text": p["text"], "actions": acts, "event_id": p.get("event", {}).get("id") if p.get("event") else None,
                      "exposure_id": p.get("exposure_id"), "subject": p["company"]["id"]})
    items.sort(key=lambda x: x["urgency"])
    return items


def rail(conn: sqlite3.Connection, days: int, when: date | None = None) -> list[dict]:
    return [{"node_id": a["id"], "sort": a["sort"], "name": a["name"], "events": a["events"],
             "basket_excess": a["basket_excess"], "direction": a["direction"]} for a in market.layer_activity(conn, days, when)]


def inbox(conn: sqlite3.Connection, days: int = 7, when: date | None = None) -> dict[str, Any]:
    when = when or market.as_of(conn)
    dec = decisions(conn, when)
    events = market.list_events(conn, days=days, limit=50, when=when)
    return {
        "as_of": when.isoformat(), "window_days": days, "sample": market.is_sample(conn),
        "conclusion": insights.inbox(dec, events),
        "decisions": dec, "events": events, "questions": open_questions(conn), "notes": recent_notes(conn),
        "rail": rail(conn, days, when),
    }


def extend_thesis(subject: str, months: int = 3) -> dict | None:
    n = N.load_note(subject)
    if not n:
        return None
    base = date.fromisoformat(n.window_until) if n.window_until else date.today()
    y, m = base.year, base.month + months
    while m > 12:
        y, m = y + 1, m - 12
    n.window_until = date(y, m, min(base.day, 28)).isoformat()
    n.window_label = f"延长至 {n.window_until}"
    n.updated = date.today().isoformat()
    N.save_note(n)
    return n.to_dict()


def excess_alerts_threshold() -> float:
    return CROWD_SIGMA + 0.5
