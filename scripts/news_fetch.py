#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""卡口事件候选池:从 data/sources/news_sources.json 里的信息源抓最近的条目,
只保留命中 physical/ 公司词表或部件词表的,去重、打事件类别、按来源层定证据级,
写到 data/events/candidates.json。人工升格后才进正式事件表。

    python3 scripts/news_fetch.py                 # 抓取 + 打标
    python3 scripts/news_fetch.py --dry-run       # 只打印会抓哪些源、词表多大
    python3 scripts/news_fetch.py --only rss      # 只跑 rss(或 cninfo_announcement / cninfo_irm)

标准库实现,无第三方依赖。抓取骨架(线程池 / 超时 / 红线词 / 原子写缓存)参考
simonlin1212/investment-news 的 fetch.py;实体白名单、去重、类别与证据级是本项目的。
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
SOURCES = REPO / "data" / "sources" / "news_sources.json"
PHYS_DIR = REPO / "physical" / "data"
OUT = REPO / "data" / "events" / "candidates.json"
CACHE = REPO / "data" / "events" / ".raw-cache.json"
UA = "Mozilla/5.0 (compatible; TeardownNewsFetch/0.1; +https://github.com/lwx0218/serenity_quant_research)"

TIER_EVIDENCE = {0: "verified", 1: "consensus", 2: "candidate", 3: "candidate"}
TRACK_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "spm", "from", "ref", "share_token"}


# ------------------------------------------------------------------ vocabulary
def build_vocab() -> tuple[dict[str, dict], dict[str, dict]]:
    """company aliases → {companyId, name, market}; part keywords → {partId, name}"""
    companies: dict[str, dict] = {}
    parts: dict[str, dict] = {}
    for f in sorted(PHYS_DIR.glob("module-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for p in d["module"]["parts"]:
            base = re.split(r"[（(]", p["name"])[0].strip()
            for kw in {base, base.replace(" ", ""), *(re.findall(r"[A-Za-z][A-Za-z0-9/\-]{2,}", p["name"]))}:
                if len(kw) >= 3 and kw.lower() not in ("host", "unit", "and", "the"):
                    parts.setdefault(kw, {"partId": p["id"], "name": base})
            for c in p["companies"]:
                if not c.get("companyId"):
                    continue
                short = re.split(r"[（(]", c["name"])[0].strip()
                aliases = {short}
                if " / " in short:
                    aliases.update(x.strip() for x in short.split(" / "))
                tk = (c.get("ticker") or "").split(" / ")[0].split(".")[0]
                if re.fullmatch(r"\d{6}", tk):
                    aliases.add(tk)
                for a in aliases:
                    if len(a) >= 2:
                        companies.setdefault(a, {"companyId": c["companyId"], "name": short, "market": c.get("market")})
    # part keywords that would match everything
    for noisy in ("PCB", "DSP", "MPO", "FAU", "PIC", "TIA"):
        parts.setdefault(noisy, parts.get(noisy, {"partId": None, "name": noisy}))
    return companies, parts


def match_entities(text: str, companies: dict, parts: dict) -> tuple[list[dict], list[dict]]:
    t = text or ""
    tl = t.lower()
    cs = {}
    for alias, rec in companies.items():
        if (alias in t) if re.search(r"[一-鿿]", alias) else re.search(r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])", tl):
            cs[rec["companyId"]] = rec
    ps = {}
    for kw, rec in parts.items():
        if rec["partId"] and ((kw in t) if re.search(r"[一-鿿]", kw) else re.search(r"(?<![a-z0-9])" + re.escape(kw.lower()) + r"(?![a-z0-9])", tl)):
            ps[rec["partId"]] = rec
    return list(cs.values()), list(ps.values())


def categorize(text: str, categories: dict) -> str | None:
    tl = (text or "").lower()
    best, score = None, 0
    for key, spec in categories.items():
        n = sum(1 for kw in spec["zh"] if kw.lower() in tl) + sum(1 for kw in spec["en"] if kw.lower() in tl)
        if n > score:
            best, score = key, n
    return best


# ------------------------------------------------------------------ fetchers
def http_get(url: str, timeout: int, data: bytes | None = None, headers: dict | None = None) -> bytes:
    req = Request(url, data=data, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})})
    with urlopen(req, timeout=timeout) as r:
        return r.read()


def _text(el, *names) -> str:
    for n in names:
        x = el.find(n)
        if x is not None and (x.text or "").strip():
            return (x.text or "").strip()
    return ""


def parse_feed(raw: bytes) -> list[dict]:
    """RSS 2.0 or Atom → [{title,url,summary,date}]"""
    root = ET.fromstring(raw)
    ns = {"atom": "http://www.w3.org/2005/Atom", "content": "http://purl.org/rss/1.0/modules/content/", "dc": "http://purl.org/dc/elements/1.1/"}
    out = []
    for it in root.iter("item"):
        d = _text(it, "pubDate", "dc:date") or _text(it, "{http://purl.org/dc/elements/1.1/}date")
        out.append({"title": _text(it, "title"), "url": _text(it, "link") or (it.find("guid").text if it.find("guid") is not None else ""),
                    "summary": re.sub(r"<[^>]+>", " ", _text(it, "description") or _text(it, "{http://purl.org/rss/1.0/modules/content/}encoded")), "date": d})
    for e in root.iter("{http://www.w3.org/2005/Atom}entry"):
        link = e.find("{http://www.w3.org/2005/Atom}link")
        out.append({"title": _text(e, "{http://www.w3.org/2005/Atom}title"), "url": link.get("href", "") if link is not None else "",
                    "summary": re.sub(r"<[^>]+>", " ", _text(e, "{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content")),
                    "date": _text(e, "{http://www.w3.org/2005/Atom}updated", "{http://www.w3.org/2005/Atom}published")})
    return out


def fetch_rss(src: dict, cfg: dict) -> list[dict]:
    raw = http_get(src["url"], cfg["timeout"])
    return parse_feed(raw)[: cfg["per_source"]]


def fetch_cninfo_announcements(src: dict, cfg: dict, companies: dict) -> list[dict]:
    """巨潮全文检索:按 A 股公司简称逐家查(GET 即可;返回 JSON announcements[])"""
    out, seen = [], set()
    names = {rec["name"]: rec for rec in companies.values() if (rec.get("market") or "").startswith("A")}
    since = (datetime.now() - timedelta(days=cfg["recent_days"])).strftime("%Y-%m-%d")
    for name, rec in names.items():
        q = urlencode({"searchkey": name, "sdate": since, "edate": "", "isfulltext": "false", "sortName": "pubdate", "sortType": "desc", "pageNum": 1})
        try:
            data = json.loads(http_get(f"{src['url']}?{q}", cfg["timeout"]).decode("utf-8", "ignore"))
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"  cninfo {name}: {e}\n")
            continue
        for a in data.get("announcements") or []:
            aid = a.get("announcementId")
            if aid in seen:
                continue
            seen.add(aid)
            ts = a.get("announcementTime")
            out.append({"title": re.sub(r"<[^>]+>", "", a.get("announcementTitle", "")), "url": "http://static.cninfo.com.cn/" + a.get("adjunctUrl", ""),
                        "summary": "", "date": datetime.fromtimestamp(ts / 1000).isoformat() if ts else "", "_company": rec["companyId"]})
        time.sleep(0.3)
    return out


def fetch_cninfo_irm(src: dict, cfg: dict, companies: dict) -> list[dict]:
    """互动易搜索(POST JSON);接口偶有变动,失败只记日志。"""
    out = []
    names = {rec["name"]: rec for rec in companies.values() if (rec.get("market") or "").startswith("A")}
    for name, rec in names.items():
        body = json.dumps({"pageNo": 1, "pageSize": 20, "searchTypes": "11,1", "keyWord": name}).encode()
        try:
            data = json.loads(http_get(src["url"], cfg["timeout"], data=body, headers={"Content-Type": "application/json"}).decode("utf-8", "ignore"))
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"  irm {name}: {e}\n")
            continue
        for r in (data.get("results") or data.get("data") or []):
            out.append({"title": (r.get("mainContent") or r.get("content") or "")[:120], "url": f"https://irm.cninfo.com.cn/ircs/question/questionDetail?questionId={r.get('indexId') or r.get('id')}",
                        "summary": r.get("attachedContent") or r.get("answerContent") or "", "date": r.get("pubDate") or r.get("updateDate") or "", "_company": rec["companyId"]})
        time.sleep(0.3)
    return out


# ------------------------------------------------------------------ normalise / dedupe
def norm_url(u: str) -> str:
    try:
        p = urlsplit(u.strip())
        q = [(k, v) for k, v in parse_qsl(p.query) if k.lower() not in TRACK_PARAMS]
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), urlencode(q), ""))
    except Exception:  # noqa: BLE001
        return u.strip()


def norm_title(t: str) -> str:
    return re.sub(r"[\s\W_]+", "", (t or "").lower())


def trigrams(s: str) -> set[str]:
    return {s[i:i + 3] for i in range(max(0, len(s) - 2))}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def parse_date(s: str) -> str | None:
    if not s:
        return None
    for f in (parsedate_to_datetime, datetime.fromisoformat):
        try:
            d = f(s.replace("Z", "+00:00")) if f is datetime.fromisoformat else f(s)
            if d.tzinfo:
                d = d.astimezone(timezone(timedelta(hours=8)))
            return d.date().isoformat()
        except Exception:  # noqa: BLE001
            continue
    m = re.search(r"(20\d\d)[-/.](\d{1,2})[-/.](\d{1,2})", s)
    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", choices=["rss", "cninfo_announcement", "cninfo_irm"])
    ap.add_argument("--probe", action="store_true", help="只探测每个源能不能打开、返回多少条,不写候选池")
    args = ap.parse_args()

    spec = json.loads(SOURCES.read_text(encoding="utf-8"))
    cfg = spec["fetch"]
    companies, parts = build_vocab()
    sources = [s for s in spec["sources"] if not args.only or s["type"] == args.only]
    print(f"词表:{len(companies)} 个公司别名,{len(parts)} 个部件关键词;信息源 {len(sources)} 个")
    if args.dry_run:
        for s in sources:
            print(f"  [{s['tier']}] {s['type']:20s} {s['name']}")
        return 0
    if args.probe:
        for s in sources:
            if s["type"] != "rss":
                print(f"  --  {s['name']}: {s['type']}(按公司查询,跳过探测)"); continue
            try:
                n = len(parse_feed(http_get(s["url"], cfg["timeout"])))
                print(f"  ok  {s['name']}: {n} 条")
            except Exception as e:  # noqa: BLE001
                print(f"  ERR {s['name']}: {type(e).__name__}: {str(e)[:80]}  ← 换 URL 或删掉这个源")
        return 0

    raw: list[tuple[dict, dict]] = []   # (source, item)
    def run(src):
        if src["type"] == "rss":
            return src, fetch_rss(src, cfg)
        if src["type"] == "cninfo_announcement":
            return src, fetch_cninfo_announcements(src, cfg, companies)
        if src["type"] == "cninfo_irm":
            return src, fetch_cninfo_irm(src, cfg, companies)
        return src, []
    with ThreadPoolExecutor(max_workers=cfg.get("threads", 8)) as ex:
        futs = {ex.submit(run, s): s for s in sources}
        for fut in as_completed(futs):
            src = futs[fut]
            try:
                s, items = fut.result()
                print(f"  ok  {src['name']}: {len(items)}")
                raw.extend((s, it) for it in items)
            except Exception as e:  # noqa: BLE001
                print(f"  ERR {src['name']}: {e}")

    cutoff = (datetime.now() - timedelta(days=cfg["recent_days"])).date().isoformat()
    redline = [k.lower() for k in spec.get("redline_keywords", [])]
    cands: list[dict] = []
    for src, it in raw:
        text = f"{it.get('title', '')} {it.get('summary', '')}"
        tl = text.lower()
        if any(k in tl for k in redline):
            continue
        date = parse_date(it.get("date", ""))
        if date and date < cutoff:
            continue
        cs, ps = match_entities(text, companies, parts)
        if it.get("_company"):
            cs = [c for c in companies.values() if c["companyId"] == it["_company"]][:1] or cs
        if src.get("entity_match") in ("required", "by_company") and not cs and not (ps and src["tier"] <= 1):
            continue
        cat = categorize(text, spec["categories"])
        if src["tier"] >= 2 and not cat:
            continue   # 综合财经 / 泛科技:没有类别关键词的不要
        cands.append({
            "id": "cand." + hashlib.sha1(norm_url(it.get("url", "")).encode()).hexdigest()[:12],
            "date": date, "title": (it.get("title") or "").strip(), "url": it.get("url", ""),
            "summary": re.sub(r"\s+", " ", it.get("summary") or "")[:240],
            "source": src["name"], "source_type": src["type"], "tier": src["tier"], "weight": src.get("weight", 0.5),
            "evidence_level": TIER_EVIDENCE.get(src["tier"], "candidate"),
            "category": cat, "category_label": spec["categories"][cat]["label"] if cat else None,
            "companies": [{"companyId": c["companyId"], "name": c["name"]} for c in cs],
            "part_ids": [p["partId"] for p in ps if p["partId"]],
            "status": "candidate", "also_reported_by": [],
        })

    # dedupe: exact url, then title trigram jaccard ≥ .8 → keep highest tier, remember the rest
    by_url: dict[str, dict] = {}
    for c in sorted(cands, key=lambda c: (c["tier"], -c["weight"])):
        k = norm_url(c["url"])
        if k in by_url:
            by_url[k]["also_reported_by"].append(c["source"]); continue
        by_url[k] = c
    kept: list[dict] = []
    for c in by_url.values():
        tg = trigrams(norm_title(c["title"]))
        dup = next((k for k in kept if jaccard(tg, trigrams(norm_title(k["title"]))) >= 0.8), None)
        if dup:
            dup["also_reported_by"].append(c["source"])
        else:
            kept.append(c)
    kept.sort(key=lambda c: (c["date"] or "", -c["weight"]), reverse=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {"$comment": "卡口事件候选池:自动抓取 + 实体白名单 + 类别关键词 + 来源分层。status=candidate 的条目需人工升格(accepted)后才进正式事件表。",
               "generated_at": datetime.now().isoformat(timespec="seconds"), "window_days": cfg["recent_days"],
               "counts": {"raw": len(raw), "kept": len(kept)}, "items": kept}
    tmp = tempfile.NamedTemporaryFile("w", delete=False, dir=OUT.parent, encoding="utf-8", suffix=".tmp")
    json.dump(payload, tmp, ensure_ascii=False, indent=1); tmp.close(); os.replace(tmp.name, OUT)
    print(f"候选 {len(kept)} 条(原始 {len(raw)})→ {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
