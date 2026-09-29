"""卡口事件候选池：从 data/sources/news_sources.json 的信息源抓最近条目，只留命中公司 / 部件词表的，
去重、打类别、按来源层定证据级，写进 candidates 表（status=pending）。入账由 accounting.py 的规则与 AI 判定决定。
巨潮公告另有历史回填（backfill，按月分段、翻页到空，origin=backfill）。

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
MAX_CONSECUTIVE_FAILS = 5   # 按公司逐家查的源：连续失败这么多家就停，别把 74 家都试一遍
# 公告标题里的例行事项：不是卡口事件，进池但标为不相关，收件箱默认不显示
ROUTINE_ANNOUNCEMENT = re.compile(
    r"股东大会|减持|增持计划|质押|解除质押|冻结|独立董事|监事|审计|会计|更正|补充|提示性公告|关联交易|担保|理财|募集资金存放|"
    r"限售股|解禁|期权|激励|换届|辞职|聘任|选举|章程|自查|问询函|监管函|警示函|简式权益|详式权益|可转债|转股|付息|评级|"
    r"回购进展|回购股份|摘要|意见书|法律意见|核查意见|保荐|持续督导|年度报告|半年度报告|季度报告|业绩预告|业绩快报|分红|派息|"
    r"停牌|复牌|异常波动|风险提示|投资者关系活动记录|"
    # v2 追加:募资安排、发行上市、定期报告,以及财经媒体的盘面 / 汇总稿(「募投」不是扩产,「出让合同」不是订单)
    r"募集资金置换|募集资金专户|使用部分募集资金|使用募集资金|自筹资金|增资|借款|土地使用权|出让合同|投资进展|"
    r"中签|发行价|IPO|上市公告书|招股|询价|三季报|半年报|年报|预约披露|财经早餐|利好消息一览|公告最新快递|重大事项公告|晚间公告|"
    r"涨停|跌停|市值|回购|调研|机构密集|一览|名单|早盘|午盘|收评")
# 英文源(rss / upload)标题里的例行与泛科技
ROUTINE_EN = re.compile(r"(?<![A-Za-z])(?:buybacks?|share price|market cap|glasses|VR|smartphones?|earnings call|dividends?|layoffs?|lawsuits?)(?![A-Za-z])", re.I)
IR_RECORD = "投资者关系活动记录"     # 标题本身没信息,不挡,交给 AI 读正文
# 强产品词:这只 1.6T 硅光模块自己的东西。DSP / TIA 太泛,只在和光模块类词同现时算
_A, _Z = r"(?<![A-Za-z0-9])", r"(?![A-Za-z0-9])"
PRODUCT_TERMS = re.compile(r"(?<![\d.])(?:1\.6|3\.2)[Tt]|(?<!\d)800[Gg]|硅光|光模块|CW\s*光源|CW\s*激光|光引擎|MT\s*插芯|高多层|光芯片|"
                           rf"{_A}(?:EML|DR8|OSFP|FAU|MPO|M8|InP){_Z}")
PRODUCT_CO_TERMS = re.compile(rf"{_A}(?:DSP|TIA){_Z}")
OPTICAL_CONTEXT = re.compile(r"光模块|光通信|光器件|光电|光芯片|光引擎|硅光|光互连|transceiver|optical", re.I)
# 类别动词:标题里得有「做了什么」,不是只提到一个产品。动词本身就说明了类别(关键词计数的 categorize 会把
# 「投资建设 1.6T 硅光产线」数成技术路线),自动入账时以它为准
CATEGORY_VERBS = re.compile(r"(?P<capex>投资建设|新建|扩建|产线|投产)|(?P<order>签订.*?合同|中标|框架协议|供货协议)|"
                            r"(?P<qualification>批量出货|小批量|送样|通过.*?认证|导入)|(?P<price>涨价|提价|调价)")
STRONG_TERMS = re.compile(r"1\.6T|3\.2T|硅光|光模块|CPO|LPO|CW\s*光源|CW\s*激光|EML|DR8|OSFP|光引擎|FAU|MPO|光芯片|投产|扩产|中标|框架协议|供货协议|1\.6t|silicon photonics|transceiver", re.I)
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
            companies.setdefault(a, {"companyId": r["id"], "name": short, "market": market,
                                     "ticker": r["ticker"] if market == "A" else None})
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


def parts_in_order(text: str, parts: dict) -> list[str]:
    """命中的部件,按在文中第一次出现的位置排(「MPO 连接器」→ MPO 在前,连接器在后)。"""
    t = text or ""
    tl = t.lower()
    first: dict[str, int] = {}
    for kw, rec in parts.items():
        if rec["partId"] and _hit(kw, t, tl):
            i = tl.find(kw.lower())
            first[rec["partId"]] = min(first.get(rec["partId"], 1 << 30), i if i >= 0 else 1 << 29)
    return sorted(first, key=first.get)


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


CNINFO_HEADERS = {"Referer": "http://www.cninfo.com.cn/"}
CNINFO_MAX_PAGES = 30          # 一家公司一个月翻到空为止;这是防死循环的上限
BACKFILL_PAUSE = 0.5           # 回填:段间歇(秒)


def cninfo_page(src: dict, cfg: dict, name: str, sdate: str, edate: str = "", page: int = 1) -> dict:
    """巨潮全文检索一页(GET;返回 JSON announcements[])。sdate / edate 为 YYYY-MM-DD,edate 空 = 到今天。"""
    return http.get_json(src["url"], {"searchkey": name, "sdate": sdate, "edate": edate, "isfulltext": "false",
                                      "sortName": "pubdate", "sortType": "desc", "pageNum": page},
                         timeout=cfg["timeout"], headers=CNINFO_HEADERS, retries=1) or {}


def _cninfo_item(a: dict, rec: dict) -> dict | None:
    """一条公告 → 原始条目。别家的公告(标题里提到了这家)不要:归属会错。
    证券代码与简称都对不上才算别家(北交所换过代码,只看代码会误伤)。"""
    code, sec_name = a.get("secCode"), re.sub(r"<[^>]+>", "", a.get("secName") or "")
    if code and rec.get("ticker") and str(code) != rec["ticker"] and rec["name"] not in sec_name:
        return None
    ts = a.get("announcementTime")
    title = re.sub(r"<[^>]+>", "", a.get("announcementTitle", ""))
    url = "http://static.cninfo.com.cn/" + a.get("adjunctUrl", "")
    summary = announcement_text(url) if IR_RECORD in title else None      # 活动记录表:标题没信息,补正文前 600 字
    return {"title": title, "url": url, "summary": summary or "",
            "date": datetime.fromtimestamp(ts / 1000).isoformat() if ts else "", "_company": rec["companyId"]}


def announcement_text(url: str, limit: int = 600) -> str | None:
    """公告 PDF 正文前 limit 字。要 pypdf(可选依赖,`pip install pypdf`);没有或取不到就返回 None,照旧交 AI 读原文。"""
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        import io
        reader = PdfReader(io.BytesIO(http.get(url, timeout=20, retries=0)))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            if len(text) >= limit:
                break
        text = re.sub(r"\s+", " ", text).strip()
        return text[:limit] or None
    except Exception:  # noqa: BLE001
        return None


def fetch_cninfo_announcements(src: dict, cfg: dict, companies: dict, log=print, sdate: str | None = None,
                               edate: str = "", max_pages: int = 1) -> list[dict]:
    """巨潮全文检索:按 A 股公司简称逐家查。默认只取最近 recent_days 天的第一页(定时抓取);
    回填用 backfill(),按月分段、翻页到空。"""
    out, seen = [], set()
    since = sdate or (datetime.now() - timedelta(days=cfg["recent_days"])).strftime("%Y-%m-%d")
    fails = 0
    for name, rec in a_share_names(companies).items():
        try:
            items = _cninfo_pages(src, cfg, name, rec, since, edate, max_pages)
            fails = 0
        except Exception as e:  # noqa: BLE001
            log(f"  cninfo {name}: {e}")
            fails += 1
            if fails >= MAX_CONSECUTIVE_FAILS:
                log(f"  cninfo: 连续 {fails} 家失败，这个源本轮停止"); break
            continue
        for aid, it in items:
            if aid not in seen:
                seen.add(aid); out.append(it)
        time.sleep(0.3)
    return out


def _cninfo_pages(src: dict, cfg: dict, name: str, rec: dict, sdate: str, edate: str, max_pages: int) -> list[tuple]:
    """一家公司一个时间段:翻页到空(或 hasMore=false / 到 totalpages / 到 max_pages)。→ [(announcementId, 条目)]"""
    out = []
    for page in range(1, max_pages + 1):
        data = cninfo_page(src, cfg, name, sdate, edate, page)
        anns = data.get("announcements") or []
        for a in anns:
            it = _cninfo_item(a, rec)
            if it:
                out.append((a.get("announcementId") or it["url"], it))
        total = data.get("totalpages")
        if not anns or data.get("hasMore") is False or (isinstance(total, int) and page >= total):
            break
    return out


def month_segments(since: str, until: str) -> list[tuple[str, str]]:
    """[since, until] 按自然月切段:(2025-10-15, 2025-10-31), (2025-11-01, 2025-11-30), …"""
    s, u = datetime.fromisoformat(since).date(), datetime.fromisoformat(until).date()
    out = []
    while s <= u:
        nxt = (s.replace(day=1) + timedelta(days=32)).replace(day=1)
        e = min(nxt - timedelta(days=1), u)
        out.append((s.isoformat(), e.isoformat()))
        s = nxt
    return out


def fetch_cninfo_irm(src: dict, cfg: dict, companies: dict, log=print) -> list[dict]:
    """互动易搜索（POST JSON）；接口偶有变动，失败只记日志。"""
    out = []
    fails = 0
    for name, rec in a_share_names(companies).items():
        try:
            data = http.post_json(src["url"], {"pageNo": 1, "pageSize": 20, "searchTypes": "11,1", "keyWord": name}, timeout=cfg["timeout"], retries=1)
            fails = 0
        except Exception as e:  # noqa: BLE001
            log(f"  irm {name}: {e}")
            fails += 1
            if fails >= MAX_CONSECUTIVE_FAILS:
                log(f"  irm: 连续 {fails} 家失败（多半是接口变了），这个源本轮停止"); break
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


def relevance_of(src: dict, text: str, cat: str | None, parts_hit: list) -> int:
    """1 = 值得看（有类别 / 命中部件 / 强关键词），0 = 例行（公告里的减持、质押、会议……），默认不进收件箱。
    投资者关系活动记录表例外：它常常藏着送样 / 供货的口径，算相关。"""
    if "投资者关系活动记录" in text:
        return 1
    if src["type"] == "cninfo_announcement" and ROUTINE_ANNOUNCEMENT.search(text) and not STRONG_TERMS.search(text):
        return 0
    if cat or parts_hit or STRONG_TERMS.search(text):
        return 1
    return 0 if src["type"] == "cninfo_announcement" else 1


def routine_hit(title: str, source_type: str | None) -> str | None:
    """标题命中例行正则 → 命中的词(入账规则 §1.1 挡);投资者关系活动记录表不挡。"""
    t = title or ""
    if IR_RECORD in t:
        return None
    m = ROUTINE_ANNOUNCEMENT.search(t) or (ROUTINE_EN.search(t) if source_type in ("rss", "upload") else None)
    return m.group(0) if m else None


def category_verb(title: str) -> tuple[str, str] | None:
    """标题里第一个类别动词 → (动词, 类别)。"""
    m = CATEGORY_VERBS.search(title or "")
    return (m.group(0), m.lastgroup) if m else None


def product_hit(text: str) -> bool:
    """强产品词命中(DSP / TIA 要和光模块类词同现)。"""
    t = text or ""
    return bool(PRODUCT_TERMS.search(t) or (PRODUCT_CO_TERMS.search(t) and OPTICAL_CONTEXT.search(t)))


def cand_id(url: str) -> str:
    return "cand." + hashlib.sha1(norm_url(url).encode()).hexdigest()[:12]


# ------------------------------------------------------------------ pipeline
def probe(spec: dict | None = None, log=print) -> list[dict]:
    spec = spec or load_spec()
    out = []
    for s in spec["sources"]:
        if not s.get("enabled", True):
            out.append({"name": s["name"], "ok": None, "note": f"已停用：{s.get('disabled_reason', '')}"}); continue
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
    sources = [s for s in spec["sources"] if s.get("enabled", True) and (not only or s["type"] == only)]
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
    cands = [c for c in (tag(src, it, companies, parts, spec, cutoff) for src, it in raw) if c]
    return dedupe(cands, len(raw), log)


def tag(src: dict, it: dict, companies: dict, parts: dict, spec: dict, cutoff: str | None = None) -> dict | None:
    """一条原始条目 → 候选(打公司 / 部件 / 类别 / 值得看);红线词、过期、没命中实体的返回 None。定时抓取与回填共用。"""
    text = f"{it.get('title', '')} {it.get('summary', '')}"
    tl = text.lower()
    if any(k.lower() in tl for k in spec.get("redline_keywords", [])):
        return None
    d = parse_date(it.get("date", ""))
    if cutoff and d and d < cutoff:
        return None
    cs, ps = match_entities(text, companies, parts)
    if it.get("_company"):
        cs = [c for c in companies.values() if c["companyId"] == it["_company"]][:1] or cs
    if src.get("entity_match") in ("required", "by_company") and not cs and not (ps and src["tier"] <= 1):
        return None
    cat = categorize(text, spec["categories"])
    if src["tier"] >= 2 and not cat:
        return None
    title = (it.get("title") or "").strip()
    return {
        "relevance": relevance_of(src, text, cat, ps),
        "id": cand_id(it.get("url", "")), "date": d, "title": title, "url": it.get("url", ""),
        "summary": re.sub(r"\s+", " ", it.get("summary") or "")[:600 if IR_RECORD in title else 240],
        "source": src["name"], "source_type": src["type"], "tier": src["tier"], "weight": src.get("weight", 0.5),
        "evidence": TIER_EVIDENCE.get(src["tier"], "candidate"), "category": cat,
        "companies": [{"companyId": c["companyId"], "name": c["name"]} for c in cs],
        "part_ids": [p["partId"] for p in ps if p["partId"]], "also_reported_by": [],
    }


def dedupe(cands: list[dict], n_raw: int, log=print, fuzzy: bool = True) -> list[dict]:
    """同 url 并来源;fuzzy 时标题三元组相似 ≥ 0.8 的当同一条,并来源(跨源转载)。
    回填只有巨潮一个源,同一家公司标题相近的公告(每月一份的合同公告)是不同的事,不做 fuzzy。"""
    by_url: dict[str, dict] = {}
    for c in sorted(cands, key=lambda c: (c["tier"], -c["weight"])):
        k = norm_url(c["url"])
        if k in by_url:
            by_url[k]["also_reported_by"].append(c["source"]); continue
        by_url[k] = c
    kept: list[dict] = []
    if not fuzzy:
        kept = sorted(by_url.values(), key=lambda c: (c["date"] or "", -c["weight"]), reverse=True)
        log(f"候选 {len(kept)} 条（原始 {n_raw}）")
        return kept
    for c in by_url.values():
        tg = trigrams(norm_title(c["title"]))
        dup = next((k for k in kept if jaccard(tg, trigrams(norm_title(k["title"]))) >= 0.8), None)
        if dup:
            dup["also_reported_by"].append(c["source"])
        else:
            kept.append(c)
    kept.sort(key=lambda c: (c["date"] or "", -c["weight"]), reverse=True)
    log(f"候选 {len(kept)} 条（原始 {n_raw}）")
    return kept


def store(conn: sqlite3.Connection, items: list[dict], source_type_override: str | None = None) -> dict:
    """写 candidates 表。已存在（同 id）的只补 also_reported_by，不动状态（也不动 origin：先抓到的为准）。"""
    now = datetime.now().isoformat(timespec="seconds")
    new = merged = 0
    for c in items:
        row = conn.execute("SELECT id, source, also_reported_by FROM candidates WHERE id=?", (c["id"],)).fetchone()
        if row:
            prev = set(json.loads(row["also_reported_by"] or "[]"))
            more = (set(c.get("also_reported_by") or []) | ({c["source"]} if c["source"] else set())) - {row["source"]}   # 同一个源再抓一遍不算第二家
            if more - prev:
                conn.execute("UPDATE candidates SET also_reported_by=? WHERE id=?", (json.dumps(sorted(prev | more), ensure_ascii=False), c["id"]))
                merged += 1
            continue
        cid = (c.get("companies") or [{}])[0].get("companyId")
        conn.execute(
            """INSERT INTO candidates (id, date, title, url, summary, source, source_type, tier, evidence, category, company_id, companies,
                                       part_ids, also_reported_by, status, fetched_at, relevance, origin)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pending',?,?,?)""",
            (c["id"], c.get("date"), c["title"], c["url"], c.get("summary"), c["source"], source_type_override or c["source_type"], c["tier"],
             c["evidence"], c.get("category"), cid, json.dumps(c.get("companies") or [], ensure_ascii=False),
             json.dumps(c.get("part_ids") or [], ensure_ascii=False), json.dumps(c.get("also_reported_by") or [], ensure_ascii=False), now,
             int(c.get("relevance", 1)), c.get("origin") or "live"))
        new += 1
    conn.commit()
    return {"new": new, "merged": merged, "seen": len(items)}


def run_news(conn: sqlite3.Connection, only: str | None = None, log=print) -> dict:
    items = collect(conn, only=only, log=log)
    return store(conn, items)


# ------------------------------------------------------------------ 历史回填
def backfill_companies(conn: sqlite3.Connection) -> list[dict]:
    """回填对象:站在某个实物部件上的 A 股公司(与入账规则 §1.2「公司必须站在某个部件上」同一口径)。"""
    rows = conn.execute("""SELECT DISTINCT c.id, c.name, c.short_name, c.ticker FROM companies c
                           JOIN physical_part_companies l ON l.company_id = c.id
                           WHERE c.exchange IN ('SSE','SZSE','BSE') ORDER BY c.id""").fetchall()
    return [{"companyId": r["id"], "name": re.split(r"[（(]", r["short_name"] or r["name"])[0].strip(),
             "ticker": r["ticker"] if re.fullmatch(r"\d{6}", r["ticker"] or "") else None} for r in rows]


def backfill(conn: sqlite3.Connection, since: str, until: str, spec: dict | None = None, log=print,
             pause: float | None = None) -> dict:
    """巨潮公告回填:实物层上的 A 股公司 × 按月分段 × 翻页到空,入候选池(origin=backfill)。
    沿用连续 5 家失败即停的熔断(一家的所有段都失败才算这家失败)。只入池,不判;判由 accounting.account 做。"""
    spec = spec or load_spec()
    cfg = spec["fetch"]
    pause = BACKFILL_PAUSE if pause is None else pause
    src = next((s for s in spec["sources"] if s["type"] == "cninfo_announcement"), None)
    if not src:
        return {"skipped": "没有巨潮公告源"}
    companies, parts = build_vocab(conn)
    targets = backfill_companies(conn)
    segs = month_segments(since, until)
    log(f"回填 {since} → {until}:{len(targets)} 家 × {len(segs)} 段")
    raw, seen = [], set()
    ok = failed = fails = 0
    stopped = False
    for rec in targets:
        seg_ok = 0
        for sdate, edate in segs:
            try:
                items = _cninfo_pages(src, cfg, rec["name"], rec, sdate, edate, CNINFO_MAX_PAGES)
                seg_ok += 1
            except Exception as e:  # noqa: BLE001
                log(f"  cninfo {rec['name']} {sdate}: {e}")
                items = []
            for aid, it in items:
                if aid not in seen:
                    seen.add(aid); raw.append(it)
            if pause:
                time.sleep(pause)
        if seg_ok:
            ok += 1; fails = 0
        else:
            failed += 1; fails += 1
            if fails >= MAX_CONSECUTIVE_FAILS:
                log(f"  cninfo: 连续 {fails} 家失败，回填停止"); stopped = True; break
    cands = [c for c in (tag(src, it, companies, parts, spec) for it in raw) if c]
    for c in cands:
        c["origin"] = "backfill"
    kept = dedupe(cands, len(raw), log, fuzzy=False)
    out = store(conn, kept)
    out.update({"since": since, "until": until, "companies": len(targets), "segments": len(segs), "companies_ok": ok,
                "companies_failed": failed, "stopped": stopped, "fetched": len(raw), "tagged": len(kept)})
    return out


def retriage(conn: sqlite3.Connection, spec: dict | None = None) -> dict:
    """给库里已有的候选重算 relevance（规则改了之后跑一次）。"""
    spec = spec or load_spec()
    companies, parts = build_vocab(conn)
    n = {0: 0, 1: 0}
    for r in conn.execute("SELECT id, title, summary, source_type, category, part_ids FROM candidates").fetchall():
        text = f"{r['title']} {r['summary'] or ''}"
        _, ps = match_entities(text, companies, parts)
        rel = relevance_of({"type": r["source_type"]}, text, r["category"], ps or json.loads(r["part_ids"] or "[]"))
        conn.execute("UPDATE candidates SET relevance=? WHERE id=?", (rel, r["id"]))
        n[rel] += 1
    conn.commit()
    return {"relevant": n[1], "routine": n[0]}
