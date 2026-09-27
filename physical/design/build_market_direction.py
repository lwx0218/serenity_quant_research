# -*- coding: utf-8 -*-
"""方向稿:物理页 · 事件 / 资金投票。在可交互原型(build_prototype.py)上加两处:

  整只模块  图上落了事件的部件亮一个呼吸点(颜色 = 部件篮子 7 天方向);九站下面一段「资金投票 · 按部件」
            —— 结论行 + 每个部件一行(事件数、篮子 7 天 / 3 个月相对整机、拥挤、最近一条事件)。
  选中部件  右栏在部件说明之后加「资金投票」(结论、部件篮子对整机走势、读数)与「卡口事件 · 30 天」,
            与 Explorer 选中一层同一个位置;左栏公司列表不动。

数据来自 market_direction_data.py(演示库 + 真实计算代码),页脚标样式示例。

    python3 physical/design/build_market_direction.py   # → physical/dist/teardown-1.6t-market-direction.html
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = open(os.path.join(HERE, "build_prototype.py"), encoding="utf-8").read()
exec(_SRC.split("\ndef build():", 1)[0])          # CSS / JS / DATA / FONT / M,与原型同一份几何

sys.path.insert(0, HERE)
import market_direction_data as MDD  # noqa: E402

OUT = os.path.join(HERE, "..", "dist", "teardown-1.6t-market-direction.html")
DATA["market"] = MDD.build()

CSS_MORE = """
:root{--sig-pos:#c0392b;--sig-neg:#2e7d5b;--sig-neu:#8a8e96}
:root[data-theme="dark"]{--sig-pos:#f07a6a;--sig-neg:#5dc391;--sig-neu:#7e8189}
.dir{font-family:var(--mono);font-size:12px;letter-spacing:.06em;white-space:nowrap}
.is-pos.dir,.sig.is-pos,.reading-v.is-pos{color:var(--sig-pos)}.is-neg.dir,.sig.is-neg,.reading-v.is-neg{color:var(--sig-neg)}.is-neu.dir,.sig.is-neu{color:var(--sig-neu)}
.sig{font-family:var(--mono);font-size:13px;font-variant-numeric:tabular-nums;font-weight:500;white-space:nowrap}
.concl{display:flex;gap:14px;align-items:baseline;padding:2px 0 4px}.concl .dir{flex:none;min-width:52px;letter-spacing:.08em}
.concl-text{font-size:15px;line-height:1.55;color:var(--ink);text-wrap:pretty}.concl.is-lead .concl-text{font-size:16px}
.asof{font-family:var(--mono);font-size:11px;letter-spacing:.04em;color:var(--muted);white-space:nowrap}.asof .sep{margin:0 8px;color:var(--faint)}
.head{gap:24px}
.readings{display:flex;flex-wrap:wrap;gap:8px 26px;align-items:baseline}.reading{display:inline-flex;gap:8px;align-items:baseline}
.reading-v{font-family:var(--mono);font-size:14px;font-variant-numeric:tabular-nums;color:var(--ink)}
.rule-note{margin:0;font-size:12px;line-height:1.6;color:var(--muted)}
.fresh{font-family:var(--mono);font-size:11px;color:var(--muted);white-space:nowrap}.fresh.is-window{color:var(--ink-2)}
.cat{font-family:var(--mono);font-size:12px;color:var(--accent);white-space:nowrap}
.faint{color:var(--faint)}

#stage{overflow:hidden}   /* 引线层固定 1600 高,内容短的选中态别被它撑长 */
#votes{position:absolute;left:80px;width:1280px;display:flex;flex-direction:column;gap:12px}
#votes .rows{margin-top:10px}
button.vrow{appearance:none;background:none;border:0;border-top:1px solid var(--hair);margin:0;font:inherit;color:inherit;text-align:left;width:100%;cursor:pointer}
.vrow{grid-template-columns:40px minmax(0,1.15fr) 72px 84px 84px 84px minmax(0,1.5fr);padding:12px 0}
.vrow.is-head{cursor:default;padding:6px 0}
.vrow .nm{font-size:15px;font-weight:500;transition:color .15s}.vrow .vn{display:flex;gap:10px;align-items:baseline;min-width:0}
.vrow.hov .nm,button.vrow:hover .nm{color:var(--accent)}
.vrow .vl{display:flex;gap:10px;align-items:baseline;font-size:13px;color:var(--ink-2);min-width:0;white-space:nowrap;overflow:hidden}
.num{font-family:var(--mono);font-size:13px;font-variant-numeric:tabular-nums;color:var(--ink)}

.mblock{display:flex;flex-direction:column;gap:12px}
#detail .head .eyebrow{white-space:nowrap}
.erow{grid-template-columns:40px minmax(0,1fr) 58px 84px;padding:11px 0}
.erow .em{display:flex;flex-direction:column;gap:3px;min-width:0}.erow .ew{font-size:13px;color:var(--ink)}
.erow .et{font-size:13px;line-height:1.45;color:var(--ink-2)}.erow .en{display:flex;flex-direction:column;gap:3px}.erow.is-head{padding:6px 0}

.chart-box{position:relative;margin:4px 0 2px}
.chart-tick{font-family:var(--mono);font-size:11px;fill:var(--muted)}.chart-label{font-size:12px;fill:var(--ink)}.chart-label.is-muted{fill:var(--muted)}
.chart-ev{font-family:var(--mono);font-size:10px;fill:var(--accent);transition:opacity .12s}.is-hover .chart-ev{opacity:0}.chart-tip{font-family:var(--mono);font-size:11px;fill:var(--ink-2)}

#overlay .live-dot.is-pos,#overlay .live-ring.is-pos{fill:var(--sig-pos)}#overlay .live-dot.is-neg,#overlay .live-ring.is-neg{fill:var(--sig-neg)}#overlay .live-dot.is-neu,#overlay .live-ring.is-neu{fill:var(--sig-neu)}
#overlay .live-dot{stroke:var(--bg);stroke-width:1.5}
#overlay .live-ring{transform-box:fill-box;transform-origin:center;opacity:0;animation:td-breathe 2.6s ease-out infinite}
@keyframes td-breathe{0%{transform:scale(1);opacity:.55}70%{transform:scale(3.2);opacity:0}100%{transform:scale(3.2);opacity:0}}
@media (prefers-reduced-motion:reduce){#overlay .live-ring{animation:none}}
"""

JS_MORE = r"""
const MK = D.market;
const ACT = Object.fromEntries(MK.activity.map(a => [a.id, a]));
const GLYPH = {pos: "▲", neg: "▼", neu: "●"}, DLABEL = {pos: "偏多", neg: "偏空", neu: "中性"};
const pct = x => { if (x == null) return "—"; const v = Math.round(x * 1000) / 10; return v === 0 ? "0.0%" : (v > 0 ? "+" : "−") + Math.abs(v).toFixed(1) + "%"; };
const sgn = x => x == null || Math.abs(x) < 0.0005 ? "neu" : x > 0 ? "pos" : "neg";   // 与显示一致:四舍五入成 0.0% 的不着色
const sig = x => `<span class="sig is-${sgn(x)}">${pct(x)}</span>`;
const md = d => d ? d.slice(5) : "";
const pad = n => n + (/[A-Za-z0-9]$/.test(n) ? " " : "");
const concl = (c, lead) => c ? `<div class="concl${lead ? " is-lead" : ""}"><span class="dir is-${c.direction}">${GLYPH[c.direction]} ${DLABEL[c.direction]}</span><span class="concl-text">${c.text}</span></div>` : "";
const asof = bits => `<span class="asof">${bits.filter(Boolean).map((b, i) => (i ? '<span class="sep">·</span>' : "") + b).join("")}</span>`;
const rank = (r, d) => r == null ? `<span class="num faint">—</span>` : `<span class="reading-v is-${d || "neu"}" style="font-size:13px">${Math.round(r)}%</span>`;
const sigma = x => x == null ? "—" : (x > 0 ? "+" : x < 0 ? "−" : "") + Math.abs(x).toFixed(1) + "σ";
const CROWD_NOTE = "读数着色:分位高于 80 或偏离 ≥ +1.5σ 视为脆弱(偏空),低于 20 视为出清(偏多);成交占比 ≥ 1.5 倍均值也计偏空。拥挤度是状态量,不是信号。";

/* ---- 整只模块:图上的呼吸点 */
function activityDots(){
  return MK.activity.filter(a => a.events > 0 && a.direction && D.anchors[a.id]).map(a => {
    const [ax, ay] = D.anchors[a.id]; const x = (LEFT + ax + 12).toFixed(0), y = (OV.top + ay - 12).toFixed(0);   // 站号圆圈的右上角
    return `<circle data-part="${a.id}" class="live-ring is-${a.direction}" cx="${x}" cy="${y}" r="3.5"/><circle data-part="${a.id}" class="live-dot is-${a.direction}" cx="${x}" cy="${y}" r="4"/>`;
  }).join("");
}

/* ---- 整只模块:资金投票 · 按部件 */
function stepOf(pid){ const seq = dir === "rx" ? D.rx : D.tx; const s = seq.find(s => s.partId === pid); return s ? String(s.step).padStart(2, "0") : "—"; }
function renderVotes(){
  const seq = (dir === "rx" ? D.rx : D.tx).map(s => s.partId);     // 表格按信号顺序读(九站是按板上位置排的,接收时左右翻转)
  const order = [...seq, ...D.parts.map(p => p.id).filter(id => !seq.includes(id))];
  const rows = order.map(id => ACT[id]).filter(a => a && (a.has_basket || a.events > 0));
  const skipped = order.map(id => ACT[id]).filter(a => a && !a.has_basket && !a.events).map(a => a.full_name);
  const head = `<div class="row vrow is-head"><span class="mono">站</span><span class="mono">部件 · 篮子成员</span><span class="mono">事件 ${MK.window_days} 天</span><span class="mono">篮子 ${MK.window_days} 天</span><span class="mono">3 个月</span><span class="mono">20 日涨幅分位</span><span class="mono">最近一条 · ${MK.events_days} 天 · T+1</span></div>`;
  const body = rows.map(a => {
    const le = a.last_event, cr = a.crowd;
    return `<button class="row vrow" data-part="${a.id}">
      <span class="mono">${stepOf(a.id)}</span>
      <span class="vn"><span class="nm">${a.full_name}</span><span class="mono" style="font-size:11px">${a.members} 家</span></span>
      <span class="num${a.events ? "" : " faint"}">${a.events || "—"}</span>
      ${a.basket_excess == null ? `<span class="num faint">—</span>` : sig(a.basket_excess)}
      ${a.excess_3m == null ? `<span class="num faint">—</span>` : sig(a.excess_3m)}
      ${cr ? rank(cr.ret20, cr.ret20 >= 80 ? "neg" : cr.ret20 <= 20 ? "pos" : "neu") : rank(null)}
      <span class="vl">${le ? `<span class="mono">${md(le.date)}</span><span>${le.company}</span><span class="cat">${le.category_label}</span>${sig(le.t1)}` : `<span class="faint">—</span>`}</span>
    </button>`;
  }).join("");
  $("votes").innerHTML = `<div class="head"><span class="eyebrow">资金投票 · 按部件</span>${asof([`截至 ${md(MK.as_of)} 收盘`, `窗口 ${MK.window_days} 天`, "篮子 = 部件上已核验的上市公司等权 · 相对整机"])}</div>
    ${concl(MK.conclusion, true)}
    <div class="rows">${head}${body}<div class="rows-end"></div></div>
    <p class="rule-note">${skipped.length ? skipped.join("、") + "没有上市公司,不成篮子,不列。" : ""}分位高于 80 视为脆弱(偏空),低于 20 视为出清(偏多);拥挤度是状态量,不是信号。点任何一行看这个部件。</p>`;
  document.querySelectorAll(".vrow[data-part]").forEach(n => { n.addEventListener("click", e => { e.stopPropagation(); select(n.dataset.part); }); bindHover(n, n.dataset.part); });
  placeVotes();
}
function placeVotes(){ $("votes").style.top = (GRID_TOP + $("stations").offsetHeight + 72) + "px"; }
function overviewHeight(){ placeVotes(); return GRID_TOP + $("stations").offsetHeight + 72 + $("votes").offsetHeight + 80; }

/* ---- 选中部件:资金投票 + 卡口事件(右栏 460,窄栏两行式,同 Explorer 选中一层) */
function marketBlocks(pid){
  const p = MK.parts[pid]; if (!p) return "";
  const hasBasket = p.series.subject.length > 1;
  if (!hasBasket && !p.events.length) return "";      // 没有上市公司也没有事件(金手指):两段都不放
  let out = "";
  if (hasBasket) {
    const r = p.readings, cr = r.crowding, m = cr ? cr.metrics : {}, d = cr ? cr.directions : {};
    out += `<section class="mblock">
      <div class="head"><span class="eyebrow">资金投票 · 部件篮子 ${p.members} 家</span>${asof([`截至 ${md(p.as_of)} 收盘`, `窗口 ${MK.months} 个月`])}</div>
      ${concl(p.basket_conclusion)}
      <div class="chart-box" data-chart="${pid}"></div>
      <div class="readings">
        <span class="reading"><span class="mono">${MK.window_days} 天</span>${sig(r.excess_7d)}</span>
        <span class="reading"><span class="mono">${MK.months} 个月</span>${sig(r.excess_3m)}</span>
        ${cr ? `<span class="reading"><span class="mono">20 日涨幅分位</span><span class="reading-v is-${d.ret20_pct_rank || "neu"}">${Math.round(m.ret20_pct_rank)}%</span></span>` : ""}
        ${cr && m.deviation_sigma != null ? `<span class="reading"><span class="mono">相对整机偏离</span><span class="reading-v is-${d.deviation_sigma || "neu"}">${sigma(m.deviation_sigma)}</span></span>` : ""}
      </div>
      ${cr ? `<p class="rule-note">篮子相对整机。${CROWD_NOTE}</p>` : ""}
    </section>`;
  }
  const evs = p.events;
  out += `<section class="mblock">
    <div class="head"><span class="eyebrow">卡口事件 · ${MK.events_days} 天 · ${evs.length} 条</span>${asof([`截至 ${md(p.as_of)} 收盘`, "T+1 相对篮子"])}</div>
    ${evs.length ? concl(p.events_conclusion) : ""}
    ${evs.length ? `<div class="rows"><div class="row erow is-head"><span class="mono">日期</span><span class="mono">公司 · 类别 · 事件</span><span class="mono">T+1</span><span class="mono">时效</span></div>
      ${evs.map(e => `<div class="row erow"><span class="mono">${md(e.date)}</span>
        <span class="em"><span class="ew">${e.company || "—"}<span class="cat" style="margin-left:8px">${e.category_label}</span><span class="mono" style="margin-left:8px;font-size:11px">${e.source_label}</span></span><span class="et">${e.title}</span></span>
        <span class="en">${sig(e.reaction.t1)}<span class="mono" style="font-size:11px">${e.volume_ratio != null ? "量比 " + e.volume_ratio.toFixed(1) : "—"}</span></span><span class="fresh is-${e.freshness.state}">${e.freshness.label}</span></div>`).join("")}
      <div class="rows-end"></div></div>` : `<p style="margin:0;padding:12px 0;border-top:1px solid var(--hair);font-size:13px;color:var(--muted)">${MK.events_days} 天内没有落在这个部件上的卡口事件。</p>`}
  </section>`;
  return out;
}

/* ---- 部件篮子对整机:与 web/src/components/LineChart.tsx 同一套画法(指数化 100、线尾标名、事件点、十字线) */
function drawChart(box, p){
  const W0 = 460, H0 = 210, Mg = {l: 36, r: 76, t: 30, b: 28};
  const S = [{label: "篮子", pts: p.series.subject, kind: "subject"}, {label: "整机", pts: p.series.reference, kind: "reference"}];
  const dates = [...new Set(S.flatMap(s => s.pts.map(q => q[0])))].sort(), ix = new Map(dates.map((d, i) => [d, i]));
  const vals = S.flatMap(s => s.pts.map(q => q[1])), lo = Math.min(...vals), hi = Math.max(...vals), padv = (hi - lo) * .1 || 1, y0 = lo - padv, y1 = hi + padv;
  const W = W0 - Mg.l - Mg.r, H = H0 - Mg.t - Mg.b;
  const snap = d => { if (ix.has(d)) return ix.get(d); let k = 0; for (let i = 0; i < dates.length; i++) { if (dates[i] <= d) k = i; else break; } return k; };
  const X = d => Mg.l + snap(d) / Math.max(1, dates.length - 1) * W, Y = v => Mg.t + (1 - (v - y0) / (y1 - y0)) * H;
  const span = y1 - y0, raw = span / 4, mag = 10 ** Math.floor(Math.log10(raw)), step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= raw);
  let svg = "";
  for (let v = Math.ceil(y0 / step) * step; v <= y1 + 1e-9; v += step) svg += `<line x1="${Mg.l}" x2="${W0 - Mg.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--hair)"/><text x="${Mg.l - 10}" y="${Y(v) + 4}" text-anchor="end" class="chart-tick">${Math.round(v)}</text>`;
  const mt = []; dates.forEach(d => { if (!mt.length || mt[mt.length - 1].ym !== d.slice(0, 7)) mt.push({ym: d.slice(0, 7), x: X(d)}); });
  if (mt.length > 1 && mt[1].x - mt[0].x < 34) mt.shift();      // 窗口起点只剩月底几天:这个月不标
  mt.forEach(t => { svg += `<text x="${t.x}" y="${H0 - 8}" class="chart-tick">${parseInt(t.ym.slice(5), 10)}月</text>`; });
  const ends = S.map(s => { const l = s.pts[s.pts.length - 1]; return {s, x: X(l[0]) + 10, y: Y(l[1]) + 4, v: l[1]}; });
  if (Math.abs(ends[0].y - ends[1].y) < 14) { const up = ends[0].y <= ends[1].y ? 0 : 1; ends[up].y -= 7; ends[1 - up].y += 7; }   // 线尾标签不打架
  S.forEach((s, i) => {
    svg += `<path d="${s.pts.map((q, j) => `${j ? "L" : "M"}${X(q[0]).toFixed(1)} ${Y(q[1]).toFixed(1)}`).join(" ")}" fill="none" stroke="${s.kind === "subject" ? "var(--accent)" : "var(--faint)"}" stroke-width="${s.kind === "subject" ? 1.6 : 1.3}" stroke-linejoin="round"/>`;
    svg += `<text x="${ends[i].x}" y="${ends[i].y}" class="chart-label${s.kind === "reference" ? " is-muted" : ""}">${s.label} ${Math.round(ends[i].v)}</text>`;
  });
  let lastX = -1e9, lvl = 0;
  p.chart_events.slice().sort((a, b) => a.date < b.date ? -1 : 1).forEach(e => {
    const x = X(e.date), y = Y(e.value); lvl = x - lastX < 56 ? lvl + 1 : 0; lastX = x;
    svg += `<g><title>${md(e.date)} ${e.company || ""} ${e.label}</title><circle cx="${x}" cy="${y}" r="4.5" fill="var(--accent)" stroke="var(--bg)" stroke-width="2"/>${lvl < 3 ? `<text x="${x}" y="${y - 12 - 13 * lvl}" text-anchor="middle" class="chart-ev">${e.label}</text>` : ""}</g>`;
  });
  box.innerHTML = `<svg viewBox="0 0 ${W0} ${H0}" width="${W0}" height="${H0}" style="display:block;overflow:visible" role="img" aria-label="${pad(p.name)}篮子与整机,${MK.months} 个月指数化">${svg}<g class="hov"></g></svg>`;
  const el = box.querySelector("svg"), hg = el.querySelector("g.hov");
  el.addEventListener("mousemove", ev => {
    el.classList.add("is-hover");     // 十字线读数在上沿,事件标签先让开
    const r = el.getBoundingClientRect(), x = (ev.clientX - r.left) / r.width * W0, i = Math.max(0, Math.min(dates.length - 1, Math.round((x - Mg.l) / W * (dates.length - 1)))), d = dates[i];
    const vals = S.map(s => (s.pts.find(q => q[0] === d) || [])[1]);
    hg.innerHTML = `<line x1="${X(d)}" x2="${X(d)}" y1="${Mg.t}" y2="${H0 - Mg.b}" stroke="var(--hair-2)"/>` + S.map((s, k) => vals[k] != null ? `<circle cx="${X(d)}" cy="${Y(vals[k])}" r="3" fill="${s.kind === "subject" ? "var(--accent)" : "var(--muted)"}"/>` : "").join("")
      + `<text x="${X(d) + (X(d) > W0 - Mg.r - 150 ? -8 : 8)}" y="${Mg.t - 14}" text-anchor="${X(d) > W0 - Mg.r - 150 ? "end" : "start"}" class="chart-tip">${md(d)}${S.map((s, k) => vals[k] != null ? ` · ${s.label} ${vals[k].toFixed(1)}` : "").join("")}</text>`;
  });
  el.addEventListener("mouseleave", () => { hg.innerHTML = ""; el.classList.remove("is-hover"); });
}
"""

REPLACE = [
    # 选中部件:左栏先放资金投票与卡口事件,再是公司
    ('    </div>\n    ${p.materials.length ? `<div><div class="head"><span class="eyebrow">上游材料',
     '    </div>\n    ${marketBlocks(pid)}\n    ${p.materials.length ? `<div><div class="head"><span class="eyebrow">上游材料'),
    ('  $("crumb-part").textContent = short(p.name);\n}',
     '  $("crumb-part").textContent = short(p.name);\n  document.querySelectorAll("[data-chart]").forEach(b => drawChart(b, MK.parts[b.dataset.chart]));\n}'),
    # 悬停联动:资金投票的行
    ('  document.querySelectorAll(".st").forEach(n => n.classList.toggle("hov", n.dataset.part === pid));',
     '  document.querySelectorAll(".st,.vrow").forEach(n => n.classList.toggle("hov", n.dataset.part === pid));'),
    # 图上的呼吸点跟着总览的引线一起画
    ('  overlay.innerHTML = out;\n}', '  overlay.innerHTML = out + activityDots();\n}'),
    # 九站换方向时,按部件的行跟着换顺序
    ('  $("stations-head").textContent = dir === "tx"', '  renderVotes();\n  $("stations-head").textContent = dir === "tx"'),
    # 选中时收起按部件的段;高度把它算进去
    ('$("legend").classList.toggle("hidden", sel);', '$("legend").classList.toggle("hidden", sel); $("votes").classList.toggle("hidden", sel);'),
    ('  else { stage.style.height = (GRID_TOP + $("stations").offsetHeight + 120) + "px"; }',
     '  else { stage.style.height = overviewHeight() + "px"; }'),
    ('renderDrawing(); renderStations(); leadersOverview(); stage.style.height = (GRID_TOP + $("stations").offsetHeight + 120) + "px";',
     'renderDrawing(); renderStations(); leadersOverview(); stage.style.height = overviewHeight() + "px";'),
    ('$("detail").addEventListener("click", e => e.stopPropagation());',
     '$("detail").addEventListener("click", e => e.stopPropagation()); $("votes").addEventListener("click", e => e.stopPropagation());'),
]


def build():
    js = JS
    for old, new in REPLACE:
        assert js.count(old) == 1, f"原型 JS 变了,找不到:{old[:60]}"
        js = js.replace(old, new)
    anchor = '$("crumb-mod").addEventListener("click"'
    assert js.count(anchor) == 1
    js = js.replace(anchor, JS_MORE + "\n" + anchor)
    mk = DATA["market"]
    data_js = json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")
    n_links = sum(len(p["companies"]) for p in M["parts"])
    html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=1440"><title>Teardown · 1.6T 光模块 · 资金投票</title>{FONT}<style>{CSS}{CSS_MORE}</style></head>
<body><div class="page">
<header>
  <div style="display:flex;align-items:center"><span class="brand">Teardown</span>
    <div class="crumbs"><span>Quantum-X800</span><svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke-width="1.4"><path d="M4.5 2.5 8 6l-3.5 3.5"/></svg><span id="crumb-mod">1.6T 光模块</span><svg id="crumb-sep" class="hidden" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke-width="1.4"><path d="M4.5 2.5 8 6l-3.5 3.5"/></svg><span id="crumb-part" class="hidden"></span></div></div>
  <nav><span class="on">实物</span><span>公司</span><span>研究</span>
    <button class="tbtn" id="theme" aria-label="切换到深色"><svg id="ic-moon" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"><path d="M13.5 9.8A5.8 5.8 0 0 1 6.2 2.5a5.8 5.8 0 1 0 7.3 7.3z"/></svg><svg id="ic-sun" hidden width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.8M8 12.7v1.8M1.5 8h1.8M12.7 8h1.8M3.4 3.4l1.3 1.3M11.3 11.3l1.3 1.3M3.4 12.6l1.3-1.3M11.3 4.7l1.3-1.3"/></svg></button></nav>
</header>
<div id="stage">
  <div id="hero" class="fade">
    <div style="display:flex;flex-direction:column;gap:18px">
      <span class="eyebrow">Quantum-X800 · OSFP224 · 1.6T DR8 · 硅光</span>
      <h1>1.6T 光模块</h1>
      <p>一只正在出货的模块,揭开上盖。电信号从左边金手指进来,在硅光芯片上变成光,从右边 MPO 出去。沿这条线走一遍,每一站是一个部件,点任何一站,看它背后的公司。</p>
    </div>
    <div style="display:flex;flex-direction:column;gap:10px;padding-bottom:6px">
      <div class="readouts"><span><span class="mono">通道</span><b>8 × 200G PAM4</b></span><span><span class="mono">波长</span><b>1310 nm · 500 m</b></span><span><span class="mono">功耗</span><b>约 22 W</b></span><span><span class="mono">光口</span><b>MPO-16 APC</b></span></div>
      <div class="readouts"><span><span class="mono">架构</span><b>硅光 PIC · 外置 CW × 2 · 3nm DSP</b></span><span><span class="mono">在哪</span><b>Quantum-X800 · Spectrum-X800 · CX-9</b></span></div>
    </div>
  </div>
  <div id="drawing"></div>
  <svg id="overlay" width="1440" height="1600" viewBox="0 0 1440 1600"></svg>
  <div id="legend" class="fade">
    <div class="lg-cap"><span>主机侧 · Quantum-X800 前面板 OSFP 笼子</span><span>后方是交换机主板与交换 ASIC · 蒙层示意</span></div>
    <div class="lg-row"><span class="mono">电信号<i></i></span><span class="mono">光信号<i class="o"></i></span></div>
    <div class="lg-row"><span class="seg"><button class="segb on" data-dir="tx">发送 TX</button><button class="segb" data-dir="rx">接收 RX</button></span></div>
  </div>
  <div style="position:absolute;left:80px;top:966px" class="fade" id="stations-headwrap"><span class="eyebrow" id="stations-head"></span></div>
  <div id="stations" class="fade"></div>
  <div id="votes" class="fade"></div>
  <div id="detail" class="fade hidden"></div>
  <div id="companies" class="fade hidden"></div>
</div>
<footer><p>示意图按 OSFP224 DR8 硅光方案的通用结构摆放,不对应任何一家的具体设计 · 公司映射 {n_links} 条 · 证据级三档 · 事件、行情与读数为样式示例(截至 {mk['as_of'][5:]})</p><span class="mono" style="font-size:11px;letter-spacing:.1em;color:var(--faint)">TEARDOWN · FROM PART TO POSITION</span></footer>
</div>
<script>window.__DATA__ = {data_js};</script>
<script>{js}</script>
</body></html>"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(html)
    print("ok →", os.path.relpath(OUT, os.path.join(HERE, "..", "..")), f"{len(html) // 1024} KB")


build()
