# -*- coding: utf-8 -*-
"""可交互原型:方向 A(揭盖等距图 + 九站)的单文件 HTML,用来体验 UX。
复用 gen_physical.py 的几何与数据;交互(选中 / 发收切换 / 浅深 / Esc)在页面 JS 里。

    python3 build_prototype.py   # → ../dist/teardown-1.6t-prototype.html
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "gen_physical.py"), encoding="utf-8").read()
exec(SRC.rsplit("# ---------------------------------------------------------------- write", 1)[0])

OUT = os.path.join(HERE, "..", "dist", "teardown-1.6t-prototype.html")

# ---- pre-render the drawing: 2 themes × 2 directions, with the real accent colour
SVGS = {}
for theme in ("light", "dark"):
    set_theme(theme)
    acc = T["accent_default"]
    SVGS[theme] = {}
    for d in ("tx", "rx"):
        svg = section_svg(path=d, stations=True, captions=True).replace("{{accent}}", acc).replace(' role="img" aria-label="1.6T 光模块揭盖示意"', "")
        svg = svg.replace('width="1278" height="517"', 'width="1278" height="517"')
        SVGS[theme][d] = svg
set_theme("light")
ANCHORS = {k: [round(v[0], 1), round(v[1], 1)] for k, v in ANCH().items()}

DATA = {
    "module": {k: M[k] for k in ("name", "nameEn", "formFactor", "spec", "hostContext")},
    "stages": M["stages"], "parts": M["parts"], "tx": M["signalPath"]["tx"], "rx": M["signalPath"]["rx"],
    "anchors": ANCHORS, "svgs": SVGS,
}

FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Geist:wght@300;400;500;600&family=Geist+Mono:wght@400;500&display=swap">')

CSS = """
:root{--bg:#f7f6f3;--ink:#1a1b1e;--ink-2:#44474d;--muted:#6f737b;--faint:#b8bbc1;--hair:#e4e2dd;--hair-2:#d3d0ca;--accent:#2f5fc9;--dim:.22;
  --sans:"Geist","PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif;--mono:"Geist Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace}
:root[data-theme="dark"]{--bg:#0f1012;--ink:#f1f0ec;--ink-2:#c3c4c8;--muted:#7e8189;--faint:#4e5158;--hair:#25272b;--hair-2:#33363b;--accent:#7aa2f5}
*{box-sizing:border-box}[hidden]{display:none!important}html,body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
.page{width:1440px;margin:0 auto;position:relative}
header{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 80px}
.brand{font-weight:600;font-size:15px;letter-spacing:-.01em}
.crumbs{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--muted);margin-left:28px}
.crumbs span:last-child{color:var(--ink)}.crumbs svg{stroke:var(--faint)}
nav{display:flex;align-items:center;gap:32px;font-size:14px;color:var(--muted)}nav .on{color:var(--ink);font-weight:500}
.tbtn{width:32px;height:32px;display:inline-flex;align-items:center;justify-content:center;background:none;border:0;cursor:pointer;color:var(--muted);padding:0}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}.eyebrow.acc{color:var(--accent)}
.mono{font-family:var(--mono);font-size:12px;color:var(--muted);letter-spacing:.02em;font-variant-numeric:tabular-nums}
#stage{position:relative;height:1500px;transition:height .36s cubic-bezier(.2,.7,.2,1)}
.fade{transition:opacity .28s ease, transform .36s cubic-bezier(.2,.7,.2,1)}
#hero{position:absolute;left:80px;top:40px;width:1280px;display:grid;grid-template-columns:minmax(0,1fr) 420px;gap:60px;align-items:end}
#hero h1{margin:0;font-size:68px;line-height:1.02;font-weight:600;letter-spacing:-.025em}
#hero p{margin:6px 0 0;font-size:19px;line-height:1.55;color:var(--ink-2);font-weight:300;max-width:640px;text-wrap:pretty}
.readouts{display:flex;flex-wrap:wrap;gap:8px 26px;align-items:baseline}.readouts span{display:inline-flex;gap:8px;align-items:baseline}.readouts b{font-family:var(--mono);font-size:13px;font-weight:400;color:var(--ink)}
#drawing{position:absolute;left:80px;top:360px;transform-origin:0 0;transition:transform .36s cubic-bezier(.2,.7,.2,1),top .36s cubic-bezier(.2,.7,.2,1)}
#drawing svg{display:block;overflow:visible}
#drawing g[data-part],#drawing g[data-station]{cursor:pointer;transition:opacity .2s}
#drawing.sel g[data-part]:not(.on){opacity:var(--dim)}#drawing.sel g[data-station]{opacity:0}#drawing.sel svg>:not(g[data-part]):not(g[data-station]){opacity:.3}
#drawing g[data-part].hov polygon,#drawing g[data-part].on polygon{stroke:var(--accent);stroke-width:.7;stroke-linejoin:round;filter:brightness(1.08)}
#drawing g[data-station].hov circle{stroke-width:1.2;fill:var(--accent)}#drawing g[data-station].hov text{fill:var(--bg)}
#overlay path.hov{stroke:var(--accent)!important;stroke-width:1.4}#overlay circle.hov{stroke:var(--accent)!important;fill:var(--accent)!important}
.st.hov .n{color:var(--accent)}.st.hov{border-top-color:var(--accent)}
button.st,button.segb{appearance:none;background:none;border:0;padding:0;margin:0;font:inherit;color:inherit}
:focus-visible{outline:1px solid var(--accent);outline-offset:3px}
#drawing.sel g[data-part]:not(.on).hov{opacity:.6}
#crumb-mod.back{cursor:pointer}#crumb-mod.back:hover{color:var(--accent)}
@media (prefers-reduced-motion:reduce){#stage,#drawing,.fade,#drawing g{transition:none!important}}
#overlay{position:absolute;left:0;top:0;overflow:visible;pointer-events:none;transition:opacity .2s}
#legend{position:absolute;right:80px;top:966px;display:flex;gap:26px;align-items:baseline}
#legend i{display:inline-block;width:22px;height:0;border-top:1.4px solid var(--ink-2);vertical-align:middle;margin-left:8px}#legend i.o{border-top:1.6px solid var(--accent)}
.seg{display:inline-flex;gap:14px;font-family:var(--mono);font-size:12px;color:var(--muted);margin-left:14px}.seg button{cursor:pointer;font:inherit;color:inherit}.seg .on{color:var(--ink);border-bottom:1px solid var(--ink)}
#stations{position:absolute;left:80px;top:1000px;width:1280px;display:grid;grid-template-columns:repeat(9,minmax(0,1fr));gap:20px}
.st{display:flex;flex-direction:column;gap:6px;padding:16px 0 0;border-top:1px solid var(--hair);cursor:pointer;text-align:left;font:inherit;color:inherit}
.st .n{font-size:16px;font-weight:500;line-height:1.3;transition:color .15s}.st{transition:border-top-color .15s}
.st .t{font-size:12.5px;color:var(--ink-2);line-height:1.45}.st .k{font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--muted)}.st .k.o{color:var(--accent)}
.hidden{opacity:0;pointer-events:none}
#detail{position:absolute;left:900px;top:96px;width:460px;display:flex;flex-direction:column;gap:36px}
#detail h1{margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-.025em}
#detail .sub{font-size:15px;color:var(--muted)}#detail .lead{margin:10px 0 0;font-size:17px;line-height:1.6;color:var(--ink-2);font-weight:300;text-wrap:pretty}
.head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px}
.row{display:grid;gap:20px;align-items:baseline;padding:11px 0;border-top:1px solid var(--hair)}.rows-end{border-top:1px solid var(--hair)}
.row .nm{font-size:15px;font-weight:500}.row .rl{font-size:13px;color:var(--ink-2)}.row .cand{color:var(--muted)}
#companies{position:absolute;left:80px;top:540px;width:740px;display:flex;flex-direction:column}
.stage-h{margin-top:18px}.stage-h .eyebrow{display:block;margin-bottom:8px}
#hint{display:inline-flex;align-items:center;gap:10px;font-size:12px;color:var(--muted)}
#hint kbd{font-family:var(--mono);font-size:11px;letter-spacing:.08em;padding:3px 6px;border:1px solid var(--hair-2);border-radius:4px}
footer{padding:0 80px 56px;display:flex;justify-content:space-between;align-items:flex-end;gap:40px}
footer p{margin:0;font-size:12px;line-height:1.6;color:var(--muted);max-width:760px}
"""

JS = r"""
const D = window.__DATA__;
const parts = Object.fromEntries(D.parts.map(p => [p.id, p]));
const stages = D.stages.slice().sort((a,b) => a.order - b.order);
const stageName = Object.fromEntries(stages.map(s => [s.id, s.name]));
const EV = {verified: "已核验", consensus: "行业图示", candidate: "候选 · 待核验"};
const mkt = m => m.startsWith("A") ? "A" : m.startsWith("US") ? "US" : m;
const aCount = p => p.companies.filter(c => c.market.startsWith("A")).length;
const short = n => n.split("（")[0].split("(")[0];

let theme = "light", dir = "tx", selected = null;
const $ = id => document.getElementById(id);
const drawing = $("drawing"), overlay = $("overlay"), stage = $("stage");

const OV = {top: 360, scale: 1}, SEL = {top: 150, scale: .6};
const GRID_TOP = 1000, LEFT = 80;

let hovered = null;
function setHover(pid){
  hovered = pid;
  drawing.querySelectorAll("g[data-part]").forEach(g => g.classList.toggle("hov", g.dataset.part === pid));
  drawing.querySelectorAll("g[data-station]").forEach(g => g.classList.toggle("hov", g.dataset.station === pid));
  document.querySelectorAll(".st").forEach(n => n.classList.toggle("hov", n.dataset.part === pid));
  overlay.querySelectorAll("[data-part]").forEach(n => n.classList.toggle("hov", n.dataset.part === pid));
}
function bindHover(el, pid){ el.addEventListener("mouseenter", () => setHover(pid)); el.addEventListener("mouseleave", () => setHover(null)); }
function renderDrawing(){
  drawing.innerHTML = D.svgs[theme][dir];
  drawing.querySelectorAll("g[data-part]").forEach(g => bindHover(g, g.dataset.part));
  drawing.querySelectorAll("g[data-station]").forEach(g => { bindHover(g, g.dataset.station); g.setAttribute("tabindex", "0"); g.setAttribute("role", "button"); g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); select(g.dataset.station); } }); });
  drawing.querySelectorAll("g[data-part]").forEach(g => g.addEventListener("click", e => { e.stopPropagation(); select(g.dataset.part); }));
  drawing.querySelectorAll("g[data-station]").forEach(g => g.addEventListener("click", e => { e.stopPropagation(); select(g.dataset.station); }));
  applySel();
}
function renderStations(){
  const seq = dir === "rx" ? D.rx.slice().reverse() : D.tx;
  $("stations").style.gridTemplateColumns = `repeat(${seq.length}, minmax(0,1fr))`;
  $("stations").innerHTML = seq.map(s => {
    const p = parts[s.partId]; const o = s.signal === "光" || s.partId === "part.pic" || s.partId === "part.pd";
    return `<button class="st" data-part="${s.partId}" aria-label="${String(s.step).padStart(2,"0")} ${short(p.name)}"><span class="k${o ? " o" : ""}">${String(s.step).padStart(2,"0")} · ${s.signal}</span><span class="n">${short(p.name)}</span><span class="t">${s.text}</span><span class="mono" style="font-size:11px;margin-top:4px">${p.companies.length} 家 · ${aCount(p)} 家 A 股</span></button>`;
  }).join("");
  document.querySelectorAll(".st").forEach(n => { n.addEventListener("click", e => { e.stopPropagation(); select(n.dataset.part); }); bindHover(n, n.dataset.part); });
  $("stations-head").textContent = dir === "tx" ? "信号怎么走 · 发送 · 九站" : "信号怎么走 · 接收 · 七站 · 从右往左读";
}
function leadersOverview(){
  const seq = dir === "rx" ? D.rx.slice().reverse() : D.tx, n = seq.length, colw = (1280 - (n - 1) * 20) / n;
  const hair = getComputedStyle(document.documentElement).getPropertyValue("--hair-2").trim();
  const ink2 = getComputedStyle(document.documentElement).getPropertyValue("--ink-2").trim();
  const bg = getComputedStyle(document.documentElement).getPropertyValue("--bg").trim();
  let out = "";
  const rank = seq.map((s, i) => [D.anchors[s.partId][0], i]).sort((a, b) => a[0] - b[0]).map(x => x[1]);
  seq.forEach((s, i) => {
    const [ax, ay] = D.anchors[s.partId]; const px = LEFT + ax, py = OV.top + ay;
    const cx = LEFT + i * (colw + 20) + 12, ym = 892 + rank.indexOf(i) * 6;
    out += `<path data-part="${s.partId}" d="M${px.toFixed(0)} ${(py + 12).toFixed(0)} V${ym} H${cx} V${GRID_TOP - 6}" fill="none" stroke="${hair}" stroke-width="1"/><circle data-part="${s.partId}" cx="${cx}" cy="${GRID_TOP - 6}" r="2.5" fill="${bg}" stroke="${ink2}" stroke-width="1.2"/>`;
  });
  overlay.innerHTML = out;
}
function leaderSelected(pid){
  const acc = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim();
  const [ax, ay] = D.anchors[pid]; const px = LEFT + ax * SEL.scale, py = SEL.top + ay * SEL.scale;
  const CX = 900, ky = 104;
  overlay.innerHTML = `<path d="M${px.toFixed(0)} ${py.toFixed(0)} V${SEL.top - 36} H${CX - 30} V${ky}" stroke="${acc}" stroke-width="1" opacity=".55" fill="none"/><circle cx="${px.toFixed(0)}" cy="${py.toFixed(0)}" r="3.5" fill="${acc}"/><circle cx="${CX - 30}" cy="${ky}" r="2.5" fill="${acc}"/>`;
}
function renderDetail(pid){
  const p = parts[pid]; const seq = dir === "rx" ? D.rx : D.tx; const idx = seq.findIndex(s => s.partId === pid);
  const code = idx >= 0 ? `${dir === "rx" ? "接收" : "发送"} ${String(idx + 1).padStart(2,"0")} / ${String(seq.length).padStart(2,"0")}` : "部件 · 不在信号路径上";
  const specs = p.keySpecs.map(s => `<span><b>${s}</b></span>`).join("");
  const mats = p.materials.map((m, i) => `<div class="row" style="grid-template-columns:28px minmax(0,1fr);padding:10px 0"><span class="mono">${String(i + 1).padStart(2,"0")}</span><span style="font-size:14px">${m}</span></div>`).join("");
  $("detail").innerHTML = `<div style="display:flex;flex-direction:column;gap:14px">
      <span class="eyebrow acc">${code}</span>
      <h1>${short(p.name)}</h1>
      <span class="sub">${p.nameEn}</span>
      <p class="lead">${p.function}</p>
      <div class="readouts">${specs}</div>
    </div>
    ${p.materials.length ? `<div><div class="head"><span class="eyebrow">上游材料 · ${p.materials.length}</span></div>${mats}<div class="rows-end"></div></div>` : ""}`;
  const groups = stages.filter(s => p.companies.some(c => c.stage === s.id)).map(s => {
    const cs = p.companies.filter(c => c.stage === s.id);
    return `<div class="stage-h"><span class="eyebrow">${s.name} · ${cs.length}</span>${cs.map(c => `<div class="row" style="grid-template-columns:150px 96px 40px minmax(0,1fr) 84px"><span class="nm">${c.name.split("（")[0]}</span><span class="mono" style="font-size:11px">${c.ticker || "—"}</span><span class="mono" style="font-size:11px">${mkt(c.market)}</span><span class="rl">${c.role}</span><span class="mono${c.evidence === "candidate" ? " cand" : ""}" style="font-size:11px">${EV[c.evidence]}</span></div>`).join("")}<div class="rows-end"></div></div>`;
  }).join("");
  $("companies").innerHTML = `<div class="head"><span class="eyebrow">公司 · ${p.companies.length} · ${aCount(p)} 家 A 股</span><span id="hint"><kbd>ESC</kbd><span>或点面包屑 / 空白处回到整只模块</span></span></div>${groups}`;
  $("crumb-part").textContent = short(p.name);
}
function applySel(){
  drawing.classList.toggle("sel", !!selected);
  drawing.querySelectorAll("g[data-part]").forEach(g => g.classList.toggle("on", g.dataset.part === selected));
}
function select(pid){
  if (selected === pid) pid = null;
  selected = pid;
  const sel = !!pid;
  $("hero").classList.toggle("hidden", sel); $("stations").classList.toggle("hidden", sel); $("stations-headwrap").classList.toggle("hidden", sel); $("legend").classList.toggle("hidden", sel);
  $("detail").classList.toggle("hidden", !sel); $("companies").classList.toggle("hidden", !sel);
  $("crumb-sep").classList.toggle("hidden", !sel); $("crumb-part").classList.toggle("hidden", !sel); $("crumb-mod").classList.toggle("back", sel);
  drawing.style.top = (sel ? SEL.top : OV.top) + "px";
  drawing.style.transform = `scale(${sel ? SEL.scale : OV.scale})`;
  applySel();
  overlay.style.opacity = 0;
  if (sel) { renderDetail(pid); const h = Math.max(540 + $("companies").offsetHeight, 96 + $("detail").offsetHeight) + 120; stage.style.height = Math.max(h, 900) + "px"; }
  else { stage.style.height = (GRID_TOP + $("stations").offsetHeight + 120) + "px"; }
  clearTimeout(select._t); select._t = setTimeout(() => { sel ? leaderSelected(pid) : leadersOverview(); overlay.style.opacity = 1; }, 380);
}
function setTheme(t){ theme = t; document.documentElement.dataset.theme = t; $("ic-moon").hidden = t !== "light"; $("ic-sun").hidden = t === "light"; $("theme").setAttribute("aria-label", t === "light" ? "切换到深色" : "切换到浅色"); renderDrawing(); selected ? leaderSelected(selected) : leadersOverview(); }
function setDir(d){ dir = d; document.querySelectorAll(".seg button").forEach(s => s.classList.toggle("on", s.dataset.dir === d)); renderDrawing(); renderStations(); if (!selected) leadersOverview(); }

$("crumb-mod").addEventListener("click", e => { if (selected) { e.stopPropagation(); select(selected); } });
$("theme").addEventListener("click", () => setTheme(theme === "light" ? "dark" : "light"));
document.querySelectorAll(".seg button").forEach(s => s.addEventListener("click", e => { e.stopPropagation(); setDir(s.dataset.dir); }));
stage.addEventListener("click", () => { if (selected) select(selected); });
document.addEventListener("keydown", e => { if (e.key === "Escape" && selected) select(selected); });
$("detail").addEventListener("click", e => e.stopPropagation()); $("companies").addEventListener("click", e => e.stopPropagation());
if (matchMedia("(prefers-color-scheme: dark)").matches) theme = "dark";
document.documentElement.dataset.theme = theme; $("ic-moon").hidden = theme !== "light"; $("ic-sun").hidden = theme === "light";
renderDrawing(); renderStations(); leadersOverview(); stage.style.height = (GRID_TOP + $("stations").offsetHeight + 120) + "px";
"""

def build():
    m = DATA["module"]
    DATA_JS = json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")
    html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=1440"><title>Teardown · 1.6T 光模块</title>{FONT}<style>{CSS}</style></head>
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
  <div id="legend" class="fade"><span class="mono">电信号<i></i></span><span class="mono">光信号<i class="o"></i></span><span class="seg"><button class="segb on" data-dir="tx">发送 TX</button><button class="segb" data-dir="rx">接收 RX</button></span></div>
  <div style="position:absolute;left:80px;top:966px" class="fade" id="stations-headwrap"><span class="eyebrow" id="stations-head"></span></div>
  <div id="stations" class="fade"></div>
  <div id="detail" class="fade hidden"></div>
  <div id="companies" class="fade hidden"></div>
</div>
<footer><p>示意图按 OSFP224 DR8 硅光方案的通用结构摆放,不对应任何一家的具体设计 · 公司映射 {sum(len(p['companies']) for p in M['parts'])} 条 · 证据级三档</p><span class="mono" style="font-size:11px;letter-spacing:.1em;color:var(--faint)">TEARDOWN · FROM PART TO POSITION</span></footer>
</div>
<script>window.__DATA__ = {DATA_JS};</script>
<script>{JS}</script>
</body></html>"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(html)
    print("ok →", os.path.relpath(OUT, os.path.join(HERE, "..", "..")), f"{len(html) // 1024} KB")

build()
