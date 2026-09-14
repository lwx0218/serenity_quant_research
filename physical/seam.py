# -*- coding: utf-8 -*-
"""物理 → 投研的接缝:给 physical 数据里的每条公司映射写上 main 侧的公司 id,
并把 main 还没有主数据的公司补进 data/seeds/physical/companies.json。

    python3 physical/seam.py          # 写回 companyId,生成公司主数据,打印覆盖情况
    python3 physical/seam.py --check  # 只检查,不写

id 规则沿用 data/seeds/cpo:A 股 cn.<六位代码>;海外 global.<slug>;未上市 private.<slug>;
不是一家公司的占位(如「国产 DSP(暂无成熟量产者)」)companyId 为 null,保留 note。
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PHYS = HERE / "data" / "module-1.6t-dr8-siph.json"
SEED = REPO / "data" / "seeds" / "cpo"
OUT = REPO / "data" / "seeds" / "physical" / "companies.json"

# 海外 / 未上市公司的 id 与主数据(name 用法定全名,shortName 用页面上叫的名字)
GLOBAL = {
    "NVIDIA": ("global.nvidia", "NVIDIA Corporation", "NVDA", "NASDAQ", "美国"),
    "Broadcom": ("global.broadcom", "Broadcom Inc.", "AVGO", "NASDAQ", "美国"),
    "Cisco": ("global.cisco", "Cisco Systems, Inc.", "CSCO", "NASDAQ", "美国"),
    "Marvell": ("global.marvell", "Marvell Technology, Inc.", "MRVL", "NASDAQ", "美国"),
    "Coherent": ("global.coherent", "Coherent Corp.", "COHR", "NYSE", "美国"),
    "Lumentum": ("global.lumentum", "Lumentum Holdings Inc.", "LITE", "NASDAQ", "美国"),
    "Arista": ("global.arista", "Arista Networks, Inc.", "ANET", "NYSE", "美国"),
    "Keysight": ("global.keysight", "Keysight Technologies, Inc.", "KEYS", "NYSE", "美国"),
    "Viavi": ("global.viavi", "Viavi Solutions Inc.", "VIAV", "NASDAQ", "美国"),
    "Senko": ("global.senko", "Senko Advanced Components", None, None, "日本"),
    "US Conec": ("global.us-conec", "US Conec Ltd.", None, None, "美国"),
    "Amphenol": ("global.amphenol", "Amphenol Corporation", "APH", "NYSE", "美国"),
    "TE Connectivity": ("global.te", "TE Connectivity plc", "TEL", "NYSE", "瑞士/美国"),
    "Molex": ("global.molex", "Molex LLC (Koch Industries)", None, None, "美国"),
    "TTM Technologies": ("global.ttm", "TTM Technologies, Inc.", "TTMI", "NASDAQ", "美国"),
    "Panasonic": ("global.panasonic", "Panasonic Holdings Corporation", "6752", "TSE", "日本"),
    "Rogers": ("global.rogers", "Rogers Corporation", "ROG", "NYSE", "美国"),
    "Credo": ("global.credo", "Credo Technology Group Holding Ltd", "CRDO", "NASDAQ", "美国"),
    "TSMC": ("global.tsmc", "Taiwan Semiconductor Manufacturing Company", "2330", "TWSE", "中国台湾"),
    "Monolithic Power Systems": ("global.mps", "Monolithic Power Systems, Inc.", "MPWR", "NASDAQ", "美国"),
    "Texas Instruments": ("global.ti", "Texas Instruments Incorporated", "TXN", "NASDAQ", "美国"),
    "Analog Devices": ("global.adi", "Analog Devices, Inc.", "ADI", "NASDAQ", "美国"),
    "MACOM": ("global.macom", "MACOM Technology Solutions Holdings, Inc.", "MTSI", "NASDAQ", "美国"),
    "Semtech": ("global.semtech", "Semtech Corporation", "SMTC", "NASDAQ", "美国"),
    "Sumitomo Electric": ("global.sumitomo-electric", "Sumitomo Electric Industries, Ltd.", "5802", "TSE", "日本"),
    "Mitsubishi Electric": ("global.mitsubishi-electric", "Mitsubishi Electric Corporation", "6503", "TSE", "日本"),
    "AXT / 北京通美": ("global.axt", "AXT, Inc.(北京通美晶体)", "AXTI", "NASDAQ", "美国/中国"),
    "JX Advanced Metals": ("global.jx-metals", "JX Advanced Metals Corporation", "5016", "TSE", "日本"),
    "Aixtron": ("global.aixtron", "AIXTRON SE", "AIXA", "XETRA", "德国"),
    "Veeco": ("global.veeco", "Veeco Instruments Inc.", "VECO", "NASDAQ", "美国"),
    "Fujikura": ("global.fujikura", "Fujikura Ltd.", "5803", "TSE", "日本"),
    "Tower Semiconductor": ("global.tower", "Tower Semiconductor Ltd.", "TSEM", "NASDAQ", "以色列"),
    "GlobalFoundries": ("global.globalfoundries", "GlobalFoundries Inc.", "GFS", "NASDAQ", "美国"),
    "Soitec": ("global.soitec", "Soitec S.A.", "SOI", "Euronext Paris", "法国"),
    "Fabrinet": ("global.fabrinet", "Fabrinet", "FN", "NYSE", "泰国/开曼"),
    "ASMPT": ("global.asmpt", "ASMPT Limited", "0522", "HKEX", "中国香港"),
    "Mycronic": ("global.mycronic", "Mycronic AB (MRSI Systems)", "MYCR", "Nasdaq Stockholm", "瑞典"),
    "Palomar Technologies": ("private.palomar", "Palomar Technologies", None, None, "美国"),
    "Corning": ("global.corning", "Corning Incorporated", "GLW", "NYSE", "美国"),
    "Celestica": ("global.celestica", "Celestica Inc.", "CLS", "NYSE", "加拿大"),
    "Anritsu": ("global.anritsu", "Anritsu Corporation", "6754", "TSE", "日本"),
    "EXFO": ("private.exfo", "EXFO Inc.", None, None, "加拿大"),
    "Honeywell / Dow": ("global.honeywell", "Honeywell International Inc.(TIM 材料;Dow 同列)", "HON", "NASDAQ", "美国"),
    "台光电子": ("tw.2383", "台光電子材料股份有限公司", "2383", "TWSE", "中国台湾"),
}
PRIVATE_CN = {
    "厦门优迅": ("private.yourui", "厦门优迅芯片股份有限公司"),
    "武汉敏芯": ("private.minxin", "武汉敏芯半导体股份有限公司"),
    "云岭光电": ("private.yunling", "武汉云岭光电股份有限公司"),
    "联合微电子中心 CUMEC": ("private.cumec", "联合微电子中心有限责任公司"),
    "长芯盛": ("private.changxinsheng", "长芯盛(武汉)科技有限公司"),
}
PLACEHOLDER = {"国产 DSP（暂无成熟量产者）", "随硅光 PIC 代工（Tower / GF / TSMC）", "东莞 / 深圳压铸厂（未上市为主）"}

# A 股法定全名(main 的 seed 用全名;这里只补 main 没有的)
CN_NAMES = {
    "600703": "三安光电股份有限公司", "300408": "潮州三环(集团)股份有限公司", "002080": "中材科技股份有限公司",
    "003031": "河北中瓷电子科技股份有限公司", "688981": "中芯国际集成电路制造有限公司", "002428": "云南锗业股份有限公司",
    "600487": "江苏亨通光电股份有限公司", "300620": "珠海光库科技股份有限公司", "688629": "四川华丰科技股份有限公司",
    "000936": "江苏华西村股份有限公司", "300661": "圣邦微电子(北京)股份有限公司", "603203": "快克智能装备股份有限公司",
    "688126": "上海硅产业集团股份有限公司", "600183": "广东生益科技股份有限公司", "002222": "福建福晶科技股份有限公司",
    "002475": "立讯精密工业股份有限公司", "300709": "江苏精研科技股份有限公司", "301205": "武汉联特科技股份有限公司",
    "300476": "胜宏科技(惠州)股份有限公司", "688195": "腾景科技股份有限公司", "300395": "菲利华石英玻璃股份有限公司",
    "002902": "东莞铭普光磁股份有限公司", "601869": "长飞光纤光缆股份有限公司", "920045": "蘅东光通讯技术(深圳)股份有限公司",
}


def base_name(n: str) -> str:
    return re.split(r"[（(]", n)[0].strip()


def resolve(c: dict) -> tuple[str | None, dict | None]:
    """→ (companyId, master-record-or-None)"""
    n = c["name"]
    if n in PLACEHOLDER:
        return None, None
    b = base_name(n)
    if b == "Cisco / Acacia":
        b = "Cisco"
    if c["market"].startswith("A"):
        code = re.match(r"(\d{6})", c["ticker"]).group(1)
        cid = f"cn.{code}"
        exch = "BSE" if code.startswith(("8", "9", "4")) else ("SSE" if code.startswith("6") else "SZSE")
        return cid, {"id": cid, "name": CN_NAMES.get(code, b), "shortName": b, "ticker": code, "exchange": exch,
                     "countryRegion": "中国", "universeLayer": "a_share_focus", "coveragePriority": "physical"}
    if b in GLOBAL:
        cid, name, tk, ex, region = GLOBAL[b]
        return cid, {"id": cid, "name": name, "shortName": b, "ticker": tk, "exchange": ex, "countryRegion": region,
                     "universeLayer": "global_anchor" if tk else "reference", "coveragePriority": "physical"}
    if b in PRIVATE_CN:
        cid, name = PRIVATE_CN[b]
        return cid, {"id": cid, "name": name, "shortName": b, "ticker": None, "exchange": None, "countryRegion": "中国",
                     "universeLayer": "private", "coveragePriority": "physical"}
    raise SystemExit(f"没有 id 规则:{n}")


def main(check_only: bool) -> int:
    phys = json.loads(PHYS.read_text(encoding="utf-8"))
    existing = {c["id"] for f in ("cpo-research-seed.json", "cpo-reference-exposures.json")
                for c in json.loads((SEED / f).read_text(encoding="utf-8"))["companies"]}
    masters: dict[str, dict] = {}
    linked = unlinked = 0
    for p in phys["module"]["parts"]:
        for c in p["companies"]:
            cid, rec = resolve(c)
            c["companyId"] = cid
            if cid:
                linked += 1
                if cid not in existing:
                    masters.setdefault(cid, rec)
            else:
                unlinked += 1
    phys["schemaVersion"] = "0.2"
    ids = {c["companyId"] for p in phys["module"]["parts"] for c in p["companies"] if c["companyId"]}
    print(f"公司映射 {linked + unlinked} 条:{linked} 条有 companyId({len(ids)} 家),{unlinked} 条是占位;"
          f"main 已有 {len(ids & existing)} 家,新增主数据 {len(masters)} 家 → {OUT.relative_to(REPO)}")
    if check_only:
        return 0
    PHYS.write_text(json.dumps(phys, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "$comment": "physical/ 里出现、而 data/seeds/cpo 还没有主数据的公司。coveragePriority=physical 表示来自实物拆解映射;"
                    "ticker 为交易所本地代码(与 cpo seed 一致),未上市为 null。",
        "companies": sorted(masters.values(), key=lambda r: r["id"]),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--check" in sys.argv))
