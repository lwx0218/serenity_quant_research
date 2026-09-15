"""东财数据中心（datacenter-web.eastmoney.com/api/data/v1/get）的几张报表：融资余额、股东户数、估值。
akshare 的 stock_margin_*、stock_zh_a_gdhs_detail_em、stock_value_em 走的是同一批接口。
字段名大小写不稳，这里统一转小写再取。"""
from __future__ import annotations

from datetime import date, timedelta

from . import http

DC = "https://datacenter-web.eastmoney.com/api/data/v1/get"


def _rows(report: str, flt: str, sort: str, pages: int = 1, page_size: int = 500) -> list[dict]:
    out = []
    for page in range(1, pages + 1):
        d = http.get_json(DC, {"reportName": report, "columns": "ALL", "filter": flt, "sortColumns": sort, "sortTypes": -1,
                               "pageSize": page_size, "pageNumber": page, "source": "WEB", "client": "WEB"},
                          headers={"Referer": "https://data.eastmoney.com/"})
        res = (d or {}).get("result") or {}
        data = res.get("data") or []
        out.extend({k.lower(): v for k, v in r.items()} for r in data)
        if page >= int(res.get("pages") or 1):
            break
    return out


def _f(x):
    try:
        return float(x) if x is not None and x != "-" else None
    except (TypeError, ValueError):
        return None


def _d(s) -> str | None:
    return str(s)[:10] if s else None


def _pick(r: dict, *keys):
    for k in keys:
        if k in r and r[k] not in (None, "-"):
            return r[k]
    return None


# ------------------------------------------------------------------ 融资余额
def fetch_margin(code: str, since: date | None = None) -> list[dict]:
    """个股融资融券明细。→ [{date, rz_balance, rq_balance, rz_to_float_pct}]"""
    rows = _rows("RPTA_WEB_RZRQ_GGMX", f'(scode="{code}")', "date", pages=2, page_size=300)
    out = []
    for r in rows:
        dd = _d(_pick(r, "date", "trade_date"))
        if not dd or (since and dd < since.isoformat()):
            continue
        out.append({"date": dd, "rz_balance": _f(_pick(r, "rzye", "rz_balance")), "rq_balance": _f(_pick(r, "rqye")),
                    "rz_to_float_pct": _f(_pick(r, "rzyezb", "rz_ratio")), "source": "eastmoney"})
    return out


# ------------------------------------------------------------------ 股东户数
def fetch_holders(code: str) -> list[dict]:
    rows = _rows("RPT_HOLDERNUM_DET", f'(SECURITY_CODE="{code}")', "END_DATE", page_size=40)
    out = []
    for r in rows:
        dd = _d(_pick(r, "end_date"))
        if not dd:
            continue
        out.append({"end_date": dd, "holder_num": _f(_pick(r, "holder_num")), "change_pct": _f(_pick(r, "holder_num_ratio", "interval_chrate")),
                    "avg_cap": _f(_pick(r, "avg_market_cap")), "source": "eastmoney"})
    return out


# ------------------------------------------------------------------ 估值
def fetch_valuation(code: str, since: date | None = None) -> list[dict]:
    since = since or (date.today() - timedelta(days=5 * 366))
    rows = _rows("RPT_VALUEANALYSIS_DET", f'(SECURITY_CODE="{code}")', "TRADE_DATE", pages=4, page_size=500)
    out = []
    for r in rows:
        dd = _d(_pick(r, "trade_date"))
        if not dd or dd < since.isoformat():
            continue
        out.append({"date": dd, "pe_ttm": _f(_pick(r, "pe_ttm")), "pb": _f(_pick(r, "pb_mrq")),
                    "market_cap": _f(_pick(r, "total_market_cap")), "source": "eastmoney"})
    return out
