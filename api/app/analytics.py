"""Pure market analytics: trading-day arithmetic, event reactions, freshness,
crowding rules and event efficacy. No SQL in here — functions take plain
sequences so they can be unit-tested and reused by the offline pipeline.

Conventions
- A "series" is a dict {date -> index value}; dates are datetime.date.
- Trading days are weekdays. Exchange holidays are not modelled yet; the
  error this introduces is a day or two around holidays, which is inside the
  tolerance of the T+N readings we show. (Tracked in docs/README.md.)
- Reactions are simple returns of the subject relative to a reference basket
  over the same window: (S_t/S_0 - 1) - (B_t/B_0 - 1).
"""
from __future__ import annotations

from datetime import date, timedelta
from statistics import mean, median
from typing import Iterable, Sequence

Series = dict[date, float]

HORIZONS = (1, 3, 5, 20)
REACTION_THRESHOLD = 0.005      # |T+1 excess| below this = "未反应"
DEFAULT_VALIDITY_DAYS = 5       # event signal validity when no efficacy stats exist
VALIDITY_MIN, VALIDITY_MAX = 3, 10

CROWD_HI, CROWD_LO, CROWD_SIGMA = 80.0, 20.0, 1.5


# ----------------------------------------------------------------- trading days
def is_trading_day(d: date) -> bool:
    return d.weekday() < 5


def next_trading_day(d: date) -> date:
    d = d + timedelta(days=1)
    while not is_trading_day(d):
        d += timedelta(days=1)
    return d


def prev_trading_day(d: date) -> date:
    d = d - timedelta(days=1)
    while not is_trading_day(d):
        d -= timedelta(days=1)
    return d


def add_trading_days(d: date, n: int) -> date:
    step = next_trading_day if n >= 0 else prev_trading_day
    for _ in range(abs(n)):
        d = step(d)
    return d


def trading_days(start: date, end: date) -> list[date]:
    out, d = [], start
    while d <= end:
        if is_trading_day(d):
            out.append(d)
        d += timedelta(days=1)
    return out


def trading_days_between(a: date, b: date) -> int:
    """Number of trading days strictly after `a` up to and including `b`."""
    if b <= a:
        return 0
    return len(trading_days(a + timedelta(days=1), b))


# ---------------------------------------------------------------------- series
def value_at(series: Series, d: date) -> float | None:
    """Value on `d`, or the last value before it (holiday / missing day)."""
    if d in series:
        return series[d]
    prior = [k for k in series if k < d]
    if prior:
        return series[max(prior)]
    later = [k for k in series if k > d]          # asked before the series starts: use its first value
    return series[min(later)] if later and (min(later) - d).days <= 10 else None


def period_return(series: Series, start: date, end: date) -> float | None:
    a, b = value_at(series, start), value_at(series, end)
    if a is None or b is None or a == 0:
        return None
    return b / a - 1.0


def excess_return(subject: Series, reference: Series, start: date, end: date) -> float | None:
    s, r = period_return(subject, start, end), period_return(reference, start, end)
    if s is None or r is None:
        return None
    return s - r


def basket_series(members: Sequence[Series], base: float = 100.0) -> Series:
    """Equal-weight, daily-rebalanced index of the members' returns."""
    if not members:
        return {}
    days = sorted(set().union(*[m.keys() for m in members]))
    out: Series = {}
    level = base
    prev: date | None = None
    for d in days:
        if prev is not None:
            rets = []
            for m in members:
                a, b = value_at(m, prev), value_at(m, d)
                if a and b:
                    rets.append(b / a - 1.0)
            if rets:
                level *= 1.0 + mean(rets)
        out[d] = level
        prev = d
    return out


def index_to(series: Series, base_date: date, base: float = 100.0) -> Series:
    b = value_at(series, base_date)
    if not b:
        return dict(series)
    return {d: v / b * base for d, v in series.items() if d >= base_date}


# ------------------------------------------------------------------- reactions
def reaction(subject: Series, reference: Series | None, event_date: date, horizon: int,
             as_of: date | None = None) -> dict | None:
    """Return of the subject from the event-day close to T+horizon, and the
    excess over the reference basket. None when T+horizon is beyond as_of."""
    target = add_trading_days(event_date, horizon)
    if as_of is not None and target > as_of:
        return None
    abs_ret = period_return(subject, event_date, target)
    if abs_ret is None:
        return None
    exc = None
    if reference:
        r = period_return(reference, event_date, target)
        exc = abs_ret - r if r is not None else None
    return {"horizon": horizon, "abs_return": abs_ret, "excess": exc, "date": target}


def excess_path(subject: Series, reference: Series | None, event_date: date, days: int = 20,
                as_of: date | None = None) -> list[float | None]:
    """Cumulative excess return for T+1..T+days (None where not yet observable)."""
    out: list[float | None] = []
    for h in range(1, days + 1):
        r = reaction(subject, reference, event_date, h, as_of)
        out.append(None if r is None else (r["excess"] if reference else r["abs_return"]))
    return out


# ------------------------------------------------------------------- freshness
def freshness(event_date: date, as_of: date, validity_days: int, t1_excess: float | None,
              threshold: float = REACTION_THRESHOLD) -> dict:
    """Where an event sits on its own clock.

    window    窗口内 T+d/v   reacted, still inside the validity window
    priced    已定价          reacted, window over — the price already carries it
    unreacted 未反应          no T+1 reaction (yet)
    expired   过期 · 未反应   no reaction and the window is over
    pending   T+0             the T+1 close is not in yet
    """
    d = trading_days_between(event_date, as_of)
    if d < 1 or t1_excess is None:
        return {"state": "pending", "days": d, "validity": validity_days, "label": f"T+{d}"}
    reacted = abs(t1_excess) >= threshold
    if reacted and d <= validity_days:
        return {"state": "window", "days": d, "validity": validity_days, "label": f"窗口内 T+{d}/{validity_days}"}
    if reacted:
        return {"state": "priced", "days": d, "validity": validity_days, "label": "已定价"}
    if d <= validity_days:
        return {"state": "unreacted", "days": d, "validity": validity_days, "label": "未反应"}
    return {"state": "expired", "days": d, "validity": validity_days, "label": "过期 · 未反应"}


# -------------------------------------------------------------------- crowding
def _dir_rank(v: float | None) -> str | None:
    if v is None:
        return None
    if v >= CROWD_HI:
        return "neg"
    if v <= CROWD_LO:
        return "pos"
    return "neu"


def _dir_sigma(v: float | None) -> str | None:
    if v is None:
        return None
    if v >= CROWD_SIGMA:
        return "neg"
    if v <= -CROWD_SIGMA:
        return "pos"
    return "neu"


def crowding_directions(metrics: dict) -> dict:
    """Per-metric direction for the readings we show, plus the overall call.

    Overall: neg (脆弱) if ≥2 readings are neg or the deviation alone is ≥σ
    threshold; pos (出清) if ≥2 readings are pos and none neg; else neu.
    """
    dirs = {
        "ret20_pct_rank": _dir_rank(metrics.get("ret20_pct_rank")),
        "turnover_pct_rank": _dir_rank(metrics.get("turnover_pct_rank")),
        "deviation_sigma": _dir_sigma(metrics.get("deviation_sigma")),
    }
    m = metrics.get("margin_to_float_pct")
    dirs["margin_to_float_pct"] = None if m is None else ("neg" if m >= 4.0 else "neu")
    share, share_mean = metrics.get("turnover_share_pct"), metrics.get("turnover_share_mean_pct")
    dirs["turnover_share_pct"] = None if share is None or not share_mean else ("neg" if share >= 1.5 * share_mean else "neu")
    h = metrics.get("holders_change_pct")
    dirs["holders_change_pct"] = None if h is None else "neu"   # 集中/分散 is context, not a call
    votes = [v for v in dirs.values() if v]
    negs, poss = votes.count("neg"), votes.count("pos")
    if negs >= 2 or dirs["deviation_sigma"] == "neg":
        overall = "neg"
    elif poss >= 2 and negs == 0:
        overall = "pos"
    else:
        overall = "neu"
    return {"per_metric": dirs, "overall": overall}


def crowd_level(pct_rank: float | None) -> str:
    """One-word level for tables: 高 / 中 / 低."""
    if pct_rank is None:
        return "—"
    return "高" if pct_rank >= CROWD_HI else "低" if pct_rank <= CROWD_LO else "中"


# -------------------------------------------------------------------- efficacy
def efficacy(paths: Iterable[dict]) -> dict | None:
    """Event efficacy for one basket.

    `paths` items: {"category": str, "path": [T+1..T+20 cumulative excess or None]}.
    Returns averages at T+1/T+5/T+20, hit rate (T+1 same sign as the average),
    per-category counts and hit rates, the T+5→T+20 give-back and the derived
    signal validity in trading days.
    """
    items = [p for p in paths if p.get("path") and p["path"][0] is not None]
    if not items:
        return None
    n = len(items)

    def avg_at(h: int) -> float | None:
        vals = [p["path"][h - 1] for p in items if len(p["path"]) >= h and p["path"][h - 1] is not None]
        return mean(vals) if vals else None

    avg = {h: avg_at(h) for h in (1, 3, 5, 20)}
    sign = 1 if (avg[1] or 0) >= 0 else -1
    hits = sum(1 for p in items if (p["path"][0] or 0) * sign > 0)
    by_cat: dict[str, dict] = {}
    for p in items:
        c = by_cat.setdefault(p["category"], {"n": 0, "hits": 0, "t1": []})
        c["n"] += 1
        c["hits"] += 1 if (p["path"][0] or 0) * sign > 0 else 0
        c["t1"].append(p["path"][0])
    for c in by_cat.values():
        c["hit_rate"] = c["hits"] / c["n"]
        c["avg_t1"] = mean(c["t1"])
        del c["t1"]

    # half-life: per event, the first day its path falls below half of its T+1
    # reaction (events that never fade count as the full depth); the basket's
    # half-life is the median. Robust to later events landing inside the window.
    depth = min(len(p["path"]) for p in items)
    avg_path = []
    for h in range(depth):
        vals = [p["path"][h] for p in items if p["path"][h] is not None]
        avg_path.append(mean(vals) if vals else None)
    per_event = []
    for p in items:
        t1 = p["path"][0]
        if t1 is None or t1 * sign <= 0:
            continue
        hl = depth
        for h in range(1, depth):
            v = p["path"][h]
            if v is None:
                hl = h
                break
            if v * sign < 0.5 * t1 * sign:
                hl = h            # T+(h+1) is the first day below half → holds through T+h
                break
        per_event.append(hl)
    half_life = int(median(per_event)) if per_event else None
    give_back = None
    if avg[5] and avg[20] is not None and avg[5] != 0:
        give_back = (avg[5] - avg[20]) / avg[5]
    validity = DEFAULT_VALIDITY_DAYS if half_life is None else max(VALIDITY_MIN, min(VALIDITY_MAX, half_life))
    return {
        "sample_n": n,
        "avg": {f"t{h}": v for h, v in avg.items()},
        "hit_rate": hits / n,
        "by_category": by_cat,
        "half_life_days": half_life,
        "give_back_t5_t20": give_back,
        "validity_days": validity,
        "avg_path": avg_path,
    }
