"""卡口事件候选池：从 data/sources/news_sources.json 的信息源抓最近条目，只留命中公司 / 部件词表的，
去重、打类别、按来源层定证据级，写进 candidates 表（status=pending）。人在收件箱确认后才成事件。

抓取骨架（线程池 / 超时 / 红线词）参考 simonlin1212/investment-news；词表来自库里的公司主数据与实物部件。"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ..config import REPO_ROOT
from . import http

SOURCES = REPO_ROOT / "data" / "sources" / "news_sources.json"
TIER_EVIDENCE = {0: "verified", 1: "consensus", 2: "candidate", 3: "candidate"}
TRACK_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "spm", "from", "ref", "share_token"}
GENERIC_ACRONYMS = {"PCB", "DSP", "MCU", "EMI", "TIM", "IHS", "EEPROM", "COB", "MZM", "PAM4"}   # 半导体新闻里到处都是，不能单靠它们入池
SOURCE_KIND = {"cninfo_announcement": "announcement", "cninfo_irm": "irm", "rss": "news", "upload": "news"}


def load_spec() -> dict:
    return json.loads(SOURCES.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ vocabulary
def build_vocab(conn: sqlite3.Connection) -> tuple[dict[str, dict], dict[str, dict]]:
    """company aliases → {companyId, name, market}; part keywords → {partId, name}"""
    companies: dict[str, dict] = {}
    for r in conn.execute("SELECT id, name, short_name, ticker, exchange FROM companies"):
        short = re.split(r"[（(]", r["short_name"] or r["name"])[0].strip()
        aliases = {short}
        if " / " in short:
            aliases.update(x.strip() for x in short.split(" / "))
        # 「上詮 FOCI」这类中英并列名，两半都算别名
        if re.search(r"[一-鿿]", short) and re.search(r"[A-Za-z]{3,}", short):
            aliases.update(x for x in re.split(r"\s+", short) if len(x) >= 2)
        if r["exchange"] in ("SSE", "SZSE", "BSE") and re.fullmatch(r"\d{6}", r["ticker"] or ""):
            aliases.add(r["ticker"])
        market = "A" if r["exchange"] in ("SSE", "SZSE", "BSE") else (r["exchange"] or "")
        for a in aliases:
            if len(a) < 2 or a.lower() in ("inc", "corp", "the"):
                continue
            if not re.search(r"[一-鿿]", a) and len(a) <= 3 and not a.isupper():
                continue                                   # 「Dow」这种三字母英文词不做别名，会撞上 Dow Jones
            companies.setdefault(a, {"companyId": r["id"], "name": short, "market": market})
    parts: dict[str, dict] = {}
    for p in conn.execute("SELECT id, name, name_en FROM physical_parts"):
        base = re.split(r"[（(]", p["name"])[0].strip()
        kws = {base, base.replace(" ", "")}
        for seg in re.split(r"[/：:、（）()]", p["name"]):           # 「隔离器 / 透镜 / 保偏光纤」→ 三个词
            seg = seg.strip()
            if len(seg) >= 3 and re.search(r"[一-鿿]", seg):
                kws.add(seg); kws.add(seg.replace(" ", ""))
        kws.update(re.findall(r"\b[A-Z][A-Z0-9]{2,}\b", p["name"] + " " + (p["name_en"] or "")))   # 只取缩写
        for kw in kws:
            if len(kw) < 3 or kw.lower() in ("the", "and"):
                continue
            parts.setdefault(kw, {"partId": None if kw in GENERIC_ACRONYMS else p["id"], "name": base})
    return companies, parts


def _hit(alias: str, text: str, tl: str) -> bool:
    if re.search(r"[一-鿿]", alias):
        return alias in text
    if len(alias) <= 4 and alias.isupper():           # FIT / TUC / ASE：短大写缩写只按原样匹配，别撞上英文单词
        return re.search(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])", text) is not None
    return re.search(r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])", tl) is not None


def match_entities(text: str, companies: dict, parts: dict) -> tuple[list[dict], list[dict]]:
    t = text or ""
    tl = t.lower()
    cs = {rec["companyId"]: rec for alias, rec in companies.items() if _hit(alias, t, tl)}
    ps = {rec["partId"]: rec for kw, rec in parts.items() if rec["partId"] and _hit(kw, t, tl)}
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
def _text(el, *names) -> str:
    for n in names:
        x = el.find(n)
        if x is not None and (x.text or "").strip():
            return (x.text or "").strip()
    return ""


def parse_feed(raw: bytes) -> list[dict]:
    """RSS 2.0 or Atom → [{title,url,summary,date}]"""
    root = ET.fromstring(raw)
    A = "{http://www.w3.org/2005/Atom}"
    out = []
    for it in root.iter("item"):
        d = _text(it, "pubDate", "{http://purl.org/dc/elements/1.1/}date")
        guid = it.find("guid")
        out.append({"title": _text(it, "title"), "url": _text(it, "link") or (guid.text if guid is not None else ""),
                    "summary": re.sub(r"<[^>]+>", " ", _text(it, "description") or _text(it, "{http://purl.org/rss/1.0/modules/content/}encoded")), "date": d})
    for e in root.iter(A + "entry"):
        link = e.find(A + "link")
        out.append({"title": _text(e, A + "title"), "url": link.get("href", "") if link is not None else "",
                    "summary": re.sub(r"<[^>]+>", " ", _text(e, A + "summary", A + "content")),
                    "date": _text(e, A + "updated", A + "published")})
    return out


def fetch_rss(src: dict, cfg: dict) -> list[dict]:
    return parse_feed(http.get(src["url"], timeout=cfg["timeout"]))[: cfg["per_source"]]


def a_share_names(companies: dict) -> dict[str, dict]:
    return {rec["name"]: rec for rec in companies.values() if rec.get("market") == "A"}


def fetch_cninfo_announcements(src: dict, cfg: dict, companies: dict, log=print) -> list[dict]:
    """巨潮全文检索：按 A 股公司简称逐家查（GET；返回 JSON announcements[]）"""
    out, seen = [], set()
    since = (datetime.now() - timedelta(days=cfg["recent_days"])).strftime("%Y-%m-%d")
    for name, rec in a_share_names(companies).items():
        try:
            data = http.get_json(src["url"], {"searchkey": name, "sdate": since, "edate": "", "isfulltext": "false",
                                              "sortName": "pubdate", "sortType": "desc", "pageNum": 1}, timeout=cfg["timeout"],
                                 headers={"Referer": "http://www.cninfo.com.cn/"}, retries=1)
        except Exception as e:  # noqa: BLE001
            log(f"  cninfo {name}: {e}")
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


def fetch_cninfo_irm(src: dict, cfg: dict, companies: dict, log=print) -> list[dict]:
    """互动易搜索（POST JSON）；接口偶有变动，失败只记日志。"""
    out = []
    for name, rec in a_share_names(companies).items():
        try:
            data = http.post_json(src["url"], {"pageNo": 1, "pageSize": 20, "searchTypes": "11,1", "keyWord": name}, timeout=cfg["timeout"], retries=1)
        except Exception as e:  # noqa: BLE001
            log(f"  irm {name}: {e}")
            continue
        for r in (data.get("results") or data.get("data") or []):
            out.append({"title": (r.get("mainContent") or r.get("content") or "")[:120],
                        "url": f"https://irm.cninfo.com.cn/ircs/question/questionDetail?questionId={r.get('indexId') or r.get('id')}",
                        "summary": r.get("attachedContent") or r.get("answerContent") or "", "date": r.get("pubDate") or r.get("updateDate") or "",
                        "_company": rec["companyId"]})
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


def cand_id(url: str) -> str:
    return "cand." + hashlib.sha1(norm_url(url).encode()).hexdigest()[:12]


# ------------------------------------------------------------------ pipeline
def probe(spec: dict | None = None, log=print) -> list[dict]:
    spec = spec or load_spec()
    out = []
    for s in spec["sources"]:
        if s["type"] != "rss":
            out.append({"name": s["name"], "ok": None, "note": f"{s['type']}：按公司查询，跳过探测"}); continue
        try:
            n = len(parse_feed(http.get(s["url"], timeout=spec["fetch"]["timeout"], retries=0)))
            out.append({"name": s["name"], "ok": True, "items": n})
        except Exception as e:  # noqa: BLE001
            out.append({"name": s["name"], "ok": False, "error": f"{type(e).__name__}: {str(e)[:120]}"})
    for r in out:
        log(f"  {'ok ' if r['ok'] else '-- ' if r['ok'] is None else 'ERR'} {r['name']}: {r.get('items', r.get('note', r.get('error')))}")
    return out


def collect(conn: sqlite3.Connection, only: str | None = None, spec: dict | None = None, log=print) -> list[dict]:
    """抓取 + 打标 + 去重 → 候选列表（还没写库）。"""
    spec = spec or load_spec()
    cfg = spec["fetch"]
    companies, parts = build_vocab(conn)
    sources = [s for s in spec["sources"] if not only or s["type"] == only]
    log(f"词表：{len(companies)} 个公司别名，{len(parts)} 个部件关键词；信息源 {len(sources)} 个")
    raw: list[tuple[dict, dict]] = []

    def run(src):
        if src["type"] == "rss":
            return src, fetch_rss(src, cfg)
        if src["type"] == "cninfo_announcement":
            return src, fetch_cninfo_announcements(src, cfg, companies, log)
        if src["type"] == "cninfo_irm":
            return src, fetch_cninfo_irm(src, cfg, companies, log)
        return src, []

    with ThreadPoolExecutor(max_workers=cfg.get("threads", 8)) as ex:
        futs = {ex.submit(run, s): s for s in sources}
        for fut in as_completed(futs):
            src = futs[fut]
            try:
                s, items = fut.result()
                log(f"  ok  {src['name']}: {len(items)}")
                raw.extend((s, it) for it in items)
            except Exception as e:  # noqa: BLE001
                log(f"  ERR {src['name']}: {e}")

    cutoff = (datetime.now() - timedelta(days=cfg["recent_days"])).date().isoformat()
    redline = [k.lower() for k in spec.get("redline_keywords", [])]
    cands: list[dict] = []
    for src, it in raw:
        text = f"{it.get('title', '')} {it.get('summary', '')}"
        tl = text.lower()
        if any(k in tl for k in redline):
            continue
        d = parse_date(it.get("date", ""))
        if d and d < cutoff:
            continue
        cs, ps = match_entities(text, companies, parts)
        if it.get("_company"):
            cs = [c for c in companies.values() if c["companyId"] == it["_company"]][:1] or cs
        if src.get("entity_match") in ("required", "by_company") and not cs and not (ps and src["tier"] <= 1):
            continue
        cat = categorize(text, spec["categories"])
        if src["tier"] >= 2 and not cat:
            continue
        cands.append({
            "id": cand_id(it.get("url", "")), "date": d, "title": (it.get("title") or "").strip(), "url": it.get("url", ""),
            "summary": re.sub(r"\s+", " ", it.get("summary") or "")[:240],
            "source": src["name"], "source_type": src["type"], "tier": src["tier"], "weight": src.get("weight", 0.5),
            "evidence": TIER_EVIDENCE.get(src["tier"], "candidate"), "category": cat,
            "companies": [{"companyId": c["companyId"], "name": c["name"]} for c in cs],
            "part_ids": [p["partId"] for p in ps if p["partId"]], "also_reported_by": [],
        })
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
    log(f"候选 {len(kept)} 条（原始 {len(raw)}）")
    return kept


def store(conn: sqlite3.Connection, items: list[dict], source_type_override: str | None = None) -> dict:
    """写 candidates 表。已存在（同 id）的只补 also_reported_by，不动状态。"""
    now = datetime.now().isoformat(timespec="seconds")
    new = merged = 0
    for c in items:
        row = conn.execute("SELECT id, also_reported_by FROM candidates WHERE id=?", (c["id"],)).fetchone()
        if row:
            prev = set(json.loads(row["also_reported_by"] or "[]"))
            more = set(c.get("also_reported_by") or []) | ({c["source"]} if c["source"] else set())
            if more - prev:
                conn.execute("UPDATE candidates SET also_reported_by=? WHERE id=?", (json.dumps(sorted(prev | more), ensure_ascii=False), c["id"]))
                merged += 1
            continue
        cid = (c.get("companies") or [{}])[0].get("companyId")
        conn.execute(
            """INSERT INTO candidates (id, date, title, url, summary, source, source_type, tier, evidence, category, company_id, companies,
                                       part_ids, also_reported_by, status, fetched_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pending',?)""",
            (c["id"], c.get("date"), c["title"], c["url"], c.get("summary"), c["source"], source_type_override or c["source_type"], c["tier"],
             c["evidence"], c.get("category"), cid, json.dumps(c.get("companies") or [], ensure_ascii=False),
             json.dumps(c.get("part_ids") or [], ensure_ascii=False), json.dumps(c.get("also_reported_by") or [], ensure_ascii=False), now))
        new += 1
    conn.commit()
    return {"new": new, "merged": merged, "seen": len(items)}


def run_news(conn: sqlite3.Connection, only: str | None = None, log=print) -> dict:
    items = collect(conn, only=only, log=log)
    return store(conn, items)
