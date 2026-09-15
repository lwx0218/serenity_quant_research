# -*- coding: utf-8 -*-
"""把「从全集往里收」的反向扫描结果并进 physical JSON。

    python3 physical/merge_scan.py scan1.json scan2.json ...

输入格式见 physical/data/coverage-1.6t-dr8-siph.json 的 $comment（name / ticker / market / verdict / parts[] / why）。
verdict=on 的 parts 并进 module.parts[].companies（同名同部件不重复）；所有条目（on / off / pending）
都记进 coverage 文件——「不在这只模块上」是一个决定，不是一个遗漏。
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHYS = HERE / "data" / "module-1.6t-dr8-siph.json"
COV = HERE / "data" / "coverage-1.6t-dr8-siph.json"

A_TICKER = re.compile(r"^(\d{6})\.(SH|SZ|BJ)$")


def norm_market(ticker: str | None, market: str) -> tuple[str | None, str, str | None]:
    """→ (ticker, market, status-note)。A 股要有六位代码 + 交易所后缀才算 A；新三板 / 在审 IPO 记为私有并保留状态。"""
    status = None
    m = re.match(r"^([A-Z一-鿿]+)(?:（(.+)）)?$", market or "")
    base = (m.group(1) if m else market or "").strip()
    if m and m.group(2):
        status = m.group(2)
    if base == "A":
        if ticker and A_TICKER.match(ticker):
            return ticker, "A", status
        return None, "私有", status or ("新三板" if ticker and ticker.endswith(".NQ") else "拟上市")
    if base == "HK":
        if ticker and re.match(r"^\d{4}\.HK$", ticker):
            return ticker, "HK", status
        return None, "私有", status or "拟港股上市"
    return ticker, base, status


def main(paths: list[str]) -> int:
    phys = json.loads(PHYS.read_text(encoding="utf-8"))
    parts = {p["id"]: p for p in phys["module"]["parts"]}
    cov = json.loads(COV.read_text(encoding="utf-8")) if COV.exists() else {
        "$comment": "反向扫描的全集：每家公司对这只模块的判定。verdict: on 站在某个部件上（已并进 module.parts）· off 明确不在（why 说明）· pending 方向对但没有可打开的来源。"
                    "扫描来源：概念板块成分、招股书竞争对手/客户/供应商、互动易按部件词检索、海外官网产品页。",
        "objectId": phys["module"]["id"], "entries": []}
    seen = {(e["name"], e.get("ticker")) for e in cov["entries"]}
    added_links = added_cos = 0
    for path in paths:
        for x in json.loads(Path(path).read_text(encoding="utf-8")):
            ticker, market, status = norm_market(x.get("ticker"), x.get("market", ""))
            entry = {"name": x["name"], "fullName": x.get("fullName"), "ticker": ticker, "market": market, "status": status,
                     "verdict": x["verdict"], "parts": [p["partId"] for p in x.get("parts", [])], "why": x.get("why")}
            if (entry["name"], ticker) not in seen:
                cov["entries"].append(entry)
                seen.add((entry["name"], ticker))
            if x["verdict"] != "on":
                continue
            new_co = True
            for p in x.get("parts", []):
                part = parts.get(p["partId"])
                if not part:
                    print("未知部件", p["partId"], x["name"]); continue
                if any(c["name"] == x["name"] and c.get("ticker") == (ticker or "") for c in part["companies"]):
                    new_co = False
                    continue
                note = p.get("note") or ""
                if status:
                    note = f"[{status}] " + note
                part["companies"].append({
                    "name": x["name"], "fullName": x.get("fullName"), "ticker": ticker or "", "market": market,
                    "stage": p["stage"], "role": p["role"], "evidence": p["evidence"], "companyId": None,
                    "sources": p.get("sources", []), "note": note})
                added_links += 1
            added_cos += new_co
    PHYS.write_text(json.dumps(phys, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    COV.write_text(json.dumps(cov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    from collections import Counter
    v = Counter(e["verdict"] for e in cov["entries"])
    print(f"并入 {added_links} 条映射（{added_cos} 家新公司）；全集 {len(cov['entries'])} 家：on {v['on']} · off {v['off']} · pending {v['pending']} → {COV.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
