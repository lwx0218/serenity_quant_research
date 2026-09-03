"""Rule-based conclusion lines. Every analytic section on a page starts with
one of these: a direction (pos / neg / neu) and one sentence. The direction
is decided by thresholds, never by wording; the wording just reads the
numbers back. Sentences are Chinese-first and avoid developer vocabulary."""
from __future__ import annotations

from typing import Any

from . import analytics as A


def pct(x: float | None, digits: int = 1) -> str:
    if x is None:
        return "—"
    v = round(x * 100, digits)
    if v == 0:
        v = 0.0
    s = f"{abs(v):.{digits}f}%"
    return ("+" if v > 0 else "−" if v < 0 else "") + s


def sigma(x: float | None) -> str:
    if x is None:
        return "—"
    return ("+" if x > 0 else "−" if x < 0 else "") + f"{abs(x):.1f}σ"


def _short(c: dict | None) -> str:
    return (c or {}).get("short_name") or (c or {}).get("name") or ""


def _subject(e: dict) -> str:
    return _short(e["company"]) if e.get("company") else (e.get("node") or {}).get("name", "")


# ------------------------------------------------------------------- overview
def overview(activity: list[dict], events: list[dict], days: int) -> dict:
    """首页第一行:资金本周在给谁投票。"""
    active = [a for a in activity if a["events"] > 0 and a["basket_excess"] is not None]
    if not events:
        return {"direction": "neu", "text": f"过去 {days} 天没有新的卡口事件;篮子读数按日更新。"}
    if not active:
        return {"direction": "neu", "text": f"过去 {days} 天有 {len(events)} 条卡口事件,但没有一层的篮子给出方向。"}
    def score(a: dict) -> tuple:
        evs = [e for e in events if a["id"] in e["layer_ids"]]
        reacted = [e for e in evs if e["freshness"]["state"] in ("window", "priced")]
        return (len(reacted), abs(a["basket_excess"]))
    lead = max(active, key=score)
    lead_events = [e for e in events if lead["id"] in e["layer_ids"]]
    reacted = [e for e in lead_events if e["freshness"]["state"] in ("window", "priced")]
    same = [e for e in reacted if (e["reaction"]["t1"] or 0) * lead["basket_excess"] > 0]
    trigger = max(lead_events, key=lambda e: abs(e["reaction"]["t1"] or 0)) if lead_events else None
    direction = "pos" if lead["basket_excess"] > 0 else "neg"
    parts = [f"资金本周在给 {lead['name']} 投票" if direction == "pos" else f"资金本周在离开 {lead['name']}"]
    if trigger:
        parts[0] += f":{trigger['date'][5:]} {trigger['category_label']}后环节内 {len(same)}/{len(lead_events)} 同向,篮子 {days} 天相对整机 {pct(lead['basket_excess'])}"
    followers = [a for a in active if a["id"] != lead["id"] and a["basket_excess"] * lead["basket_excess"] > 0 and abs(a["basket_excess"]) >= A.REACTION_THRESHOLD]
    if followers:
        f = max(followers, key=lambda a: abs(a["basket_excess"]))
        parts.append(f"{f['name']}跟随 {pct(f['basket_excess'])}")
    sold = [e for e in events if e["reaction"]["t1"] is not None and e["reaction"]["t1"] <= -A.REACTION_THRESHOLD]
    unre = [e for e in events if e["freshness"]["state"] in ("unreacted", "expired")]
    if sold:
        u = min(sold, key=lambda e: e["reaction"]["t1"])
        parts.append(f"{_subject(u)}的{u['category_label']}{'传闻' if u['source_kind'] == 'news' else ''}被卖出 {pct(u['reaction']['t1'])}")
    elif unre:
        u = unre[0]
        parts.append(f"{_subject(u)}的{u['category_label']}{'传闻' if u['source_kind'] == 'news' else ''}没有反应({pct(u['reaction']['t1'])})")
    return {"direction": direction, "text": ",".join(parts[:2]) + (";" + parts[2] if len(parts) > 2 else "") + "。"}


# --------------------------------------------------------------------- events
def layer_events(events: list[dict], layer_name: str) -> dict:
    """选中一层 · 最近事件:资金在给这一层的哪一段投票。"""
    if not events:
        return {"direction": "neu", "text": f"窗口内没有触及{layer_name}的卡口事件。"}
    with_t1 = [e for e in events if e["reaction"]["t1"] is not None]
    if not with_t1:
        return {"direction": "neu", "text": f"{len(events)} 条事件都还没有 T+1 收盘,先别下结论。"}
    pos = [e for e in with_t1 if e["reaction"]["t1"] >= A.REACTION_THRESHOLD]
    neg = [e for e in with_t1 if e["reaction"]["t1"] <= -A.REACTION_THRESHOLD]
    cn = [e for e in pos if e.get("company") and (e["company"].get("country_region") or "").startswith("中")]
    heavy = [e for e in pos if (e.get("volume_ratio") or 0) >= 1.5]
    n = len(with_t1)
    if len(pos) >= max(2, n // 2 + 1):
        d = "pos"
        who = "、".join(_subject(e) for e in pos[:3])
        tail = f"量集中在 {'、'.join(_subject(e) for e in heavy[:2])}" if heavy else "但没有一条放量"
        laggards = [e for e in with_t1 if e not in pos]
        lag = f",{'、'.join(_subject(e) for e in laggards[:2])}未跟随" if laggards else ""
        seg = "国内" if cn and len(cn) == len(pos) else ""
        text = f"{n} 条里 {len(pos)} 条同向({who}){lag};{tail} —— 资金在给{seg}{layer_name}这一段投票。"
    elif len(neg) >= max(2, n // 2 + 1):
        d = "neg"
        text = f"{n} 条里 {len(neg)} 条被卖出({'、'.join(_subject(e) for e in neg[:3])});这一层的利好没有被买单。"
    else:
        d = "neu"
        text = f"{n} 条事件方向分散(同向 {len(pos)}、反向 {len(neg)}),资金还没有对{layer_name}形成一致看法。"
    return {"direction": d, "text": text}


def company_events(events: list[dict]) -> dict:
    """公司页 · 卡口事件 30 天。"""
    if not events:
        return {"direction": "neu", "text": "30 天内没有卡口事件。"}
    voted = [e for e in events if e["freshness"]["state"] in ("window", "priced") and (e.get("volume_ratio") or 0) >= 1.5]
    reacted = [e for e in events if e["freshness"]["state"] in ("window", "priced")]
    dead = [e for e in events if e["freshness"]["state"] == "expired"]
    n = len(events)
    if voted:
        v = voted[0]
        d = "pos" if (v["reaction"]["t1"] or 0) > 0 else "neg"
        text = f"{n} 条里只有 {v['date'][5:]} 那条被资金真正投票(有量、{'有共振' if abs(v['reaction']['t1'] or 0) >= 0.02 else '有反应'})"
        if dead:
            text += f";{dead[0]['source_label']}那条过期未反应,信息已被消化"
        return {"direction": d, "text": text + "。"}
    if reacted:
        return {"direction": "neu", "text": f"{n} 条里 {len(reacted)} 条有反应但都没放量;还没有被资金确认的事件。"}
    return {"direction": "neu", "text": f"{n} 条事件都没有被资金买入;要么已在价格里,要么市场不认。"}


# ------------------------------------------------------------------- crowding
def crowding(cr: dict | None, kind: str = "company", dispersion: dict | None = None) -> dict:
    """拥挤度 / 脆弱性:状态量,不是信号。"""
    if not cr:
        return {"direction": "neu", "text": "没有拥挤度读数。"}
    m, d = cr["metrics"], cr["direction"]
    if d == "neg":
        if kind == "basket":
            parts = ["篮子整体进入拥挤区"]
            if dispersion and (dispersion["high"] + dispersion["low"] + dispersion["mid"]) > 0 and dispersion["low"] > 0:
                parts[0] += f",但分化明显:{dispersion['high']} 家高、{dispersion['low']} 家低"
            text = parts[0] + "。环节级仓位此时加,买到的是“已被投票过的”那一半。"
        else:
            reasons = []
            if (m.get("ret20_pct_rank") or 0) >= A.CROWD_HI:
                reasons.append("短期获利盘厚")
            if m.get("holders_change_pct") is not None and m["holders_change_pct"] < 0:
                reasons.append("筹码在集中")
            if (m.get("margin_to_float_pct") or 0) >= 4.0:
                reasons.append("融资占比高")
            text = "拥挤:" + "、".join(reasons or ["读数在脆弱区"]) + ";利好边际递减,小利空会被放大。"
    elif d == "pos":
        text = "出清:涨幅与换手都在低分位,筹码松动已经发生;利空边际递减,利好容易被买入。"
    else:
        text = "不拥挤也不出清;拥挤度不构成加减仓的理由,看事件。"
    return {"direction": d, "text": text}


# ------------------------------------------------------------------ resonance
def resonance(res: dict) -> dict:
    ev, s, sd = res["event"], res["self"], res["same_direction"]
    t1 = s["t1"]
    if t1 is None:
        return {"direction": "neu", "text": "T+1 还没有收盘,共振要等一天。"}
    d = "pos" if t1 >= A.REACTION_THRESHOLD else "neg" if t1 <= -A.REACTION_THRESHOLD else "neu"
    broad = sd["n"] >= 2 and sd["k"] / sd["n"] >= 0.6
    adj = [a for a in res["adjacent"] if a["t1"] is not None and a["t1"] * t1 > 0 and abs(a["t1"]) >= A.REACTION_THRESHOLD]
    scale = "环节级事件而非个股事件" if broad else "个股事件而非环节级事件"
    detail = ("同环节" + ("与相邻层" if adj else "") + "同向") if broad else "同环节没有跟随"
    conf = "资金用量确认" if (s.get("volume_ratio") or 0) >= 1.5 else "但没有放量"
    text = f"{scale}:{detail},{conf}。"
    tr = s.get("turnover_pct_rank")
    if d == "pos" and tr and tr >= A.CROWD_HI:
        v = ev["freshness"]["validity"]
        text += f"但换手分位 {tr:.0f}% 说明追价者多,若 T+{v} 前没有二次确认(订单 / 涨价),回吐概率高。"
    elif d == "pos" and res.get("baseline") and res["baseline"]["above"]:
        text += "反应高于这家公司同类事件的历史基线。"
    return {"direction": d, "text": text}


# ------------------------------------------------------------------- efficacy
def efficacy(eff: dict | None, layer_name: str) -> dict:
    if not eff:
        return {"direction": "neu", "text": f"过去 90 天没有足够的{layer_name}事件来估计效力。"}
    a = eff["avg"]
    v = eff["validity_days"]
    d = "pos" if (a.get("t1") or 0) >= A.REACTION_THRESHOLD and eff["hit_rate"] >= 0.55 else "neg" if (a.get("t1") or 0) <= -A.REACTION_THRESHOLD else "neu"
    if d == "pos":
        text = f"这一环节的卡口事件“有效但短”:当交易信号看 T+{v},当研究信号看是否出现二次确认(订单 → 扩产 → 涨价)。"
    elif d == "neg":
        text = f"这一环节的卡口事件平均被卖出:利好在价格里,事件后追价是反向指标。"
    else:
        text = f"这一环节的事件效力弱(命中率 {eff['hit_rate']*100:.0f}%),事件本身不构成交易信号,只作研究线索。"
    return {"direction": d, "text": text}


def basket(detail: dict) -> dict:
    """篮子页第一行:趋势、拥挤、时效三者合成。"""
    exc = detail.get("excess_window")
    cr = detail.get("crowding")
    eff = detail.get("efficacy")
    months = detail.get("window_months", 6)
    trend = "pos" if (exc or 0) >= 0.02 else "neg" if (exc or 0) <= -0.02 else "neu"
    crowded = cr and cr["direction"] == "neg"
    v = eff["validity_days"] if eff else A.DEFAULT_VALIDITY_DAYS
    if trend == "pos" and crowded:
        d = "neu"
        text = (f"环节相对整机 {months} 个月 {pct(exc)},趋势偏多;但当前拥挤({sigma(cr['metrics'].get('deviation_sigma'))})且事件效力只有约 {v} 天。"
                f"结论:不追,等回到 +1σ 以内或出现二次确认再加。")
    elif trend == "pos":
        d = "pos"
        text = f"环节相对整机 {months} 个月 {pct(exc)},趋势偏多且不拥挤;按事件加,时效约 {v} 天。"
    elif trend == "neg" and cr and cr["direction"] == "pos":
        d = "pos"
        text = f"环节相对整机 {months} 个月 {pct(exc)},但拥挤度已出清;下一条被资金确认的事件值得跟。"
    elif trend == "neg":
        d = "neg"
        text = f"环节相对整机 {months} 个月 {pct(exc)},资金在离开;不做左侧。"
    else:
        d = "neu"
        text = f"环节相对整机 {months} 个月 {pct(exc)},没有趋势;只看事件,不看仓位。"
    return {"direction": d, "text": text}


# ------------------------------------------------------------------- company
def company_headline(events_30d: list[dict], cr: dict | None) -> dict:
    """公司页第一行:事件面 vs 结构面。"""
    reacted = [e for e in events_30d if e["freshness"]["state"] in ("window", "priced")]
    pos_ev = [e for e in reacted if (e["reaction"]["t1"] or 0) > 0]
    ev_face = "pos" if len(pos_ev) >= max(1, len(reacted) // 2 + 1) and reacted else "neg" if reacted and not pos_ev else "neu"
    st_face = cr["direction"] if cr else "neu"
    n = len(events_30d)
    ev_txt = {"pos": f"事件面偏多(30 天 {n} 条卡口事件,{len(reacted)} 条已见资金反应)", "neg": f"事件面偏空(30 天 {n} 条事件,反应为负)",
              "neu": f"事件面中性(30 天 {n} 条事件,{len(reacted)} 条有反应)"}[ev_face]
    st_txt = {"neg": "结构面偏空(拥挤区)", "pos": "结构面偏多(已出清)", "neu": "结构面中性"}[st_face]
    if ev_face == "pos" and st_face == "neg":
        return {"direction": "neu", "text": f"{ev_txt},{st_txt}。两者相抵:有新事件才追,没有就等它出清。"}
    if ev_face == "pos" and st_face != "neg":
        return {"direction": "pos", "text": f"{ev_txt},{st_txt}。顺着事件做,时效看该层的事件效力。"}
    if ev_face == "neg" and st_face == "neg":
        return {"direction": "neg", "text": f"{ev_txt},{st_txt}。两面都不支持,回避。"}
    if ev_face == "neu" and st_face == "pos":
        return {"direction": "pos", "text": f"{ev_txt},{st_txt}。等下一条被确认的事件。"}
    return {"direction": "neu", "text": f"{ev_txt},{st_txt}。没有动作。"}


# --------------------------------------------------------------------- thesis
def thesis_tracking(note: dict, readings: list[dict]) -> dict:
    """自判断起的跟踪读数 vs 阈值。"""
    d = note.get("direction", "neu")
    thr = (note.get("threshold_pct") or 3.0) / 100.0
    obs = [r for r in readings if r["excess"] is not None]
    if not obs:
        return {"direction": d, "text": note.get("stance") or "", "verdict": None}
    head = (note.get("stance") or "").rstrip(";;。") + ";" if note.get("stance") else ""
    parts = [f"自判断起{r['label']} {pct(r['excess'])}" if i == 0 else f"{r['label']} {pct(r['excess'])}" for i, r in enumerate(obs)]
    lead = obs[0]["excess"]
    sign = 1 if d == "pos" else -1 if d == "neg" else 0
    if sign == 0:
        verdict = "观察中,不记分"
    elif lead * sign >= thr:
        verdict = f"方向对,幅度已过阈值(±{thr*100:.0f}%)"
    elif lead * sign > 0:
        verdict = f"方向对,但幅度还在噪声内(阈值 ±{thr*100:.0f}%)"
    elif lead * sign <= -thr:
        verdict = f"方向错,已触及阈值(±{thr*100:.0f}%),该回顾"
    else:
        verdict = f"方向暂时不对,还在噪声内(阈值 ±{thr*100:.0f}%)"
    return {"direction": d, "text": head + ",".join(parts) + " —— " + verdict + "。", "verdict": verdict}


# ---------------------------------------------------------------------- inbox
def inbox(decisions: list[dict], events: list[dict]) -> dict:
    n = len(decisions)
    states = [e["freshness"]["state"] for e in events]
    win, priced, unre = states.count("window"), states.count("priced"), states.count("unreacted") + states.count("expired")
    head = f"{n} 件事要决定" if n else "没有要决定的事"
    if decisions:
        head += f",最紧急的是{decisions[0]['headline']}"
    tail = f";{len(events)} 条事件里 {win} 条还在窗口内、{priced} 条已定价、{unre} 条未反应。" if events else "。"
    d = decisions[0]["direction"] if decisions and decisions[0]["direction"] != "neu" else "neu"
    return {"direction": d, "text": head + tail}


def efficacy_rows(eff: dict | None) -> list[dict]:
    """The four hairline rows under 事件效力, with the numbers already read back."""
    if not eff:
        return []
    cats = sorted(eff["by_category_label"].items(), key=lambda kv: -kv[1]["n"])
    sample = f"{eff['sample_n']} 条卡口事件(" + " · ".join(f"{k} {v['n']}" for k, v in cats) + ")"
    a = eff["avg"]
    best = max(cats, key=lambda kv: kv[1]["hit_rate"]) if cats else None
    worst = min(cats, key=lambda kv: kv[1]["hit_rate"]) if cats else None
    hit = f"{eff['hit_rate']*100:.0f}%({round(eff['hit_rate']*eff['sample_n'])}/{eff['sample_n']} 同向)"
    if best and worst and best[0] != worst[0]:
        hit += f" · {best[0]}类最高 {best[1]['hits']}/{best[1]['n']} · {worst[0]}类最低 {worst[1]['hits']}/{worst[1]['n']}"
    v = eff["validity_days"]
    gb = eff.get("give_back_t5_t20")
    if gb is not None and gb > 0.15:
        half = f"T+5 到 T+20 回吐 {gb*100:.0f}% → 事件信号的有效期约 {v} 个交易日;过期后的价格里已经没有这条事件了"
    elif gb is not None and gb < -0.15:
        half = f"单条事件约 {v} 个交易日后回到一半,但 T+20 平均反而更高 —— 后续事件在接力,不是单条事件在持续"
    else:
        half = f"单条事件约 {v} 个交易日后回到一半;T+5 到 T+20 基本走平"
    return [
        {"key": "样本", "text": sample, "parts": []},
        {"key": "平均反应", "text": "", "parts": [["T+1 ", a.get("t1")], [" · T+5 ", a.get("t5")], [" · T+20 ", a.get("t20")], ["(相对整机篮子)", None]]},
        {"key": "命中率", "text": hit, "parts": []},
        {"key": "半衰期", "text": half, "parts": [], "strong": f"{v} 个交易日"},
    ]
