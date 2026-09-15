"""公司主数据 → 各数据源的代码。companies.ticker 是交易所本地代码（A 股六位、美股字母、日股四位数…），
exchange 是交易所名；这里把它们翻成东财 secid / Yahoo 符号 / stooq 符号。"""
from __future__ import annotations

import re

# Yahoo 后缀
YAHOO_SUFFIX = {
    "SSE": ".SS", "SZSE": ".SZ", "BSE": ".BJ",
    "TSE": ".T", "TWSE": ".TW", "TPEx": ".TWO", "HKEX": ".HK", "XETRA": ".DE", "Euronext Paris": ".PA",
    "LSE": ".L", "Nasdaq Stockholm": ".ST", "KRX": ".KS", "KOSDAQ": ".KQ", "Euronext Amsterdam": ".AS",
    "NASDAQ": "", "NYSE": "", "US": "",
}
# stooq 后缀（只做美 / 日 / 港 / 德 / 英 / 法；台湾、A 股 stooq 没有）
STOOQ_SUFFIX = {"NASDAQ": ".us", "NYSE": ".us", "US": ".us", "TSE": ".jp", "HKEX": ".hk", "XETRA": ".de", "LSE": ".uk", "Euronext Paris": ".fr"}


def is_a_share(c: dict) -> bool:
    return (c.get("exchange") or "") in ("SSE", "SZSE", "BSE") and bool(re.fullmatch(r"\d{6}", c.get("ticker") or ""))


def em_secid(c: dict) -> str | None:
    """东财 secid：1.<代码> 沪市，0.<代码> 深市 / 北交所。"""
    if not is_a_share(c):
        return None
    return f"{'1' if c['exchange'] == 'SSE' else '0'}.{c['ticker']}"


def yahoo_symbol(c: dict) -> str | None:
    tk, ex = c.get("ticker"), c.get("exchange") or ""
    if not tk or ex not in YAHOO_SUFFIX:
        return None
    if ex == "HKEX":
        tk = tk.zfill(4)
    return f"{tk}{YAHOO_SUFFIX[ex]}"


def stooq_symbol(c: dict) -> str | None:
    tk, ex = c.get("ticker"), c.get("exchange") or ""
    if not tk or ex not in STOOQ_SUFFIX:
        return None
    if ex == "HKEX":
        tk = tk.zfill(4)
    return f"{tk}{STOOQ_SUFFIX[ex]}".lower()


def quotable(c: dict) -> bool:
    """有没有任何一条路能取到行情（未上市公司没有）。"""
    return bool(em_secid(c) or yahoo_symbol(c) or stooq_symbol(c))
