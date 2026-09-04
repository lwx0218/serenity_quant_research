# -*- coding: utf-8 -*-
"""physical-first 方向稿 v0:1.6T 光模块剖面 · 四块画板(浅色)。
复用 docs/product/prototypes/teardown-v3/gen 的 tokens / 等距几何 / html 骨架,
数据取自 ../data/module-1.6t-dr8-siph.json。

    python3 gen_physical.py   # 产出 *.dc.html 与 canvas.json
"""
import json, os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
GEN3 = os.path.join(REPO, "docs", "product", "prototypes", "teardown-v3", "gen")
SRC = open(os.path.join(GEN3, "gen_base.py"), encoding="utf-8").read()
exec(SRC.split("# ---------------------------------------------------------------- write")[0])  # LIGHT/DARK, MONO, SANS, P, slab, helmet, wrap …

T = LIGHT
ACC = "{{accent}}"
DATA = json.load(open(os.path.join(HERE, "..", "data", "module-1.6t-dr8-siph.json"), encoding="utf-8"))
M = DATA["module"]
PARTS = OrderedDict((p["id"], p) for p in M["parts"])
STAGE_NAME = {s["id"]: s["name"] for s in M["stages"]}
STAGE_ORDER = [s["id"] for s in sorted(M["stages"], key=lambda s: s["order"])]

MATS = {
    "light": dict(ALU=("#DCDFE3", "#AEB3BA"), FIN="#B9BEC5", PCB=("#3E5A4C", "#25382F"), DIE=("#2A2D33", "#151719"), DIETXT="#8E949C",
                  SI=("#9DB2C8", "#6D8299"), GOLD=("#D4B369", "#A3843F"), TAN=("#D9C89C", "#A5945F"), BLK=("#3A3C40", "#1D1E21"),
                  GLASS=("#E9ECEF", "#B8BBC1"), FIBER="#6FA3E0", PD="#84999F", TRACE="#4A6A5A"),
    "dark": dict(ALU=("#E3E6EA", "#9EA4AB"), FIN="#B0B6BD", PCB=("#4B6D5B", "#2A3F34"), DIE=("#34383F", "#191B1F"), DIETXT="#A2A8B1",
                 SI=("#A9BFD6", "#74899F"), GOLD=("#E0C07A", "#A98B47"), TAN=("#E2D3AB", "#AB9A66"), BLK=("#45484E", "#212327"),
                 GLASS=("#D3D0CA", "#9EA4AB"), FIBER="#7FB2F0", PD="#8EA3AD", TRACE="#5A7D6A"),
}
THEME = "light"
def set_theme(name):
    global T, THEME, INK_LINE, ALU, FIN, PCB, DIE, DIETXT, SI, GOLD, TAN, BLK, GLASS, FIBER, PD, TRACE
    THEME = name; T = LIGHT if name == "light" else DARK; INK_LINE = T["ink2"]
    m = MATS[name]
    ALU, FIN, PCB, DIE, DIETXT, SI, GOLD, TAN, BLK, GLASS, FIBER, PD, TRACE = (m[k] for k in ("ALU", "FIN", "PCB", "DIE", "DIETXT", "SI", "GOLD", "TAN", "BLK", "GLASS", "FIBER", "PD", "TRACE"))
set_theme("light")

def mkt(m):
    return "A" if m.startswith("A") else ("US" if m.startswith("US") else ("—" if m in ("—",) else ("私有" if m == "私有" else m)))

def a_count(p):
    return sum(1 for c in p["companies"] if c["market"].startswith("A"))

# ---------------------------------------------------------------- shared html
def nav(crumbs, active="实物"):
    parts = []
    for i, c in enumerate(crumbs):
        if i:
            parts.append(f'<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="{T["faint"]}" stroke-width="1.4"><path d="M4.5 2.5 8 6l-3.5 3.5"/></svg>')
        parts.append(f'<span style="color:{T["ink"] if i == len(crumbs) - 1 else T["muted"]}">{c}</span>')
    crumb = f'<div style="display:flex;align-items:center;gap:10px;font-size:13px;color:{T["muted"]}">{"".join(parts)}</div>'
    def item(l):
        return f'<span style="color:{T["ink"] if l == active else T["muted"]};font-weight:{500 if l == active else 400}">{l}</span>'
    return f"""<header style="height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 80px">
  <div style="display:flex;align-items:center;gap:28px"><span style="font-weight:600;font-size:15px;letter-spacing:-0.01em;color:{T['ink']}">Teardown</span>{crumb}</div>
  <nav style="display:flex;align-items:center;gap:32px;font-size:14px">{item("实物")}{item("公司")}{item("研究")}</nav>
</header>"""

def eyebrow(txt, accent=False):
    return f'<span style="font-family:{MONO};font-size:12px;letter-spacing:0.14em;text-transform:uppercase;color:{ACC if accent else T["muted"]}">{txt}</span>'

def mono(txt, color=None, size=12):
    return f'<span style="font-family:{MONO};font-size:{size}px;color:{color or T["muted"]};letter-spacing:0.02em;font-variant-numeric:tabular-nums">{txt}</span>'

def text(txt, size=13, color=None):
    return f'<span style="font-size:{size}px;color:{color or T["ink2"]};line-height:1.5">{txt}</span>'

def title(txt, size=16):
    return f'<span style="font-size:{size}px;font-weight:500;color:{T["ink"]}">{txt}</span>'

def link(txt, size=13):
    return f'<span style="font-size:{size}px;color:{ACC}">{txt}</span>'

def row(cols, cells, pad="12px 0"):
    return (f'<div style="display:grid;grid-template-columns:{cols};gap:20px;align-items:baseline;padding:{pad};border-top:1px solid {T["hair"]}">' + "".join(cells) + "</div>")

def rows_end():
    return f'<div style="border-top:1px solid {T["hair"]}"></div>'

def head(left, right=""):
    r = f'<span style="font-size:13px;color:{T["muted"]}">{right}</span>' if right and not right.startswith("<") else right
    return f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">{eyebrow(left)}{r}</div>'

def readouts(pairs):
    out = []
    for k, v in pairs:
        out.append(f'<span style="display:inline-flex;gap:8px;align-items:baseline">{mono(k)}<span style="font-family:{MONO};font-size:13px;color:{T["ink"]}">{v}</span></span>')
    return f'<div style="display:flex;flex-wrap:wrap;gap:8px 26px;align-items:baseline">{"".join(out)}</div>'

def footer(note):
    return f"""<footer style="padding:64px 80px 56px;display:flex;justify-content:space-between;align-items:flex-end;gap:40px">
  <p style="margin:0;font-size:12px;line-height:1.6;color:{T['muted']};max-width:760px">{note}</p>
  <span style="font-family:{MONO};font-size:11px;letter-spacing:0.1em;color:{T['faint']}">TEARDOWN · FROM PART TO POSITION</span>
</footer>"""

EV = {"verified": "已核验", "consensus": "行业共识", "candidate": "候选 · 待核验"}

# ---------------------------------------------------------------- plan view (lid removed, looking down at the PCB)
# drawing box 1280 × 360; left = 金手指 (host side), right = MPO (fiber side)
def SEC():
    return OrderedDict([
        ("part.shell",         (60, 40, 1160, 280, BLK[0], BLK[1], "")),
        ("part.pcb",           (74, 54, 1060, 252, PCB[0], PCB[1], "")),
        ("part.edge-fingers",  (74, 54, 46, 252, GOLD[0], GOLD[1], "")),
        ("part.power-mgmt",    (160, 84, 70, 52, BLK[0], BLK[1], "PMIC")),
        ("part.dsp",           (280, 108, 150, 144, DIE[0], DIE[1], "DSP")),
        ("part.cw-laser",      (482, 128, 40, 34, GOLD[0], GOLD[1], "CW")),
        ("part.cw-laser-2",    (482, 198, 40, 34, GOLD[0], GOLD[1], "CW")),
        ("part.laser-coupling",(528, 130, 20, 30, GLASS[0], GLASS[1], "")),
        ("part.laser-coupling-2",(528, 200, 20, 30, GLASS[0], GLASS[1], "")),
        ("part.pic",           (560, 98, 280, 164, SI[0], SI[1], "")),
        ("part.driver",        (592, 112, 70, 46, DIE[0], DIE[1], "DRV")),
        ("part.tia",           (592, 202, 70, 46, DIE[0], DIE[1], "TIA")),
        ("part.pd",            (780, 206, 46, 40, PD, SI[1], "PD")),
        ("part.fau",           (840, 116, 58, 128, GLASS[0], GLASS[1], "FAU")),
        ("part.mpo",           (1134, 62, 86, 108, BLK[0], BLK[1], "MPO")),
        ("part.mpo-2",         (1134, 190, 86, 108, BLK[0], BLK[1], "MPO")),
    ])
ALIAS = {"part.cw-laser-2": "part.cw-laser", "part.laser-coupling-2": "part.laser-coupling", "part.mpo-2": "part.mpo"}
def ANCH():
    return {"part.host-cage": (30, 180), "part.edge-fingers": (97, 180), "part.pcb": (230, 180), "part.dsp": (355, 180),
            "part.driver": (627, 135), "part.cw-laser": (502, 145), "part.pic": (720, 150), "part.fau": (869, 150), "part.mpo": (1177, 116),
            "part.pd": (803, 226), "part.tia": (627, 225), "part.lid-thermal": (640, 20), "part.shell": (640, 330),
            "part.power-mgmt": (195, 110), "part.laser-coupling": (538, 145), "part.engine-assembly": (700, 84), "part.module-maker": (1240, 30)}
TX = M["signalPath"]["tx"]
RX = M["signalPath"]["rx"]

def section_svg(selected=None, scale=1.0, stations=True, path="tx", captions=True):
    dim = "0.3"
    g = []
    A = ANCH()
    # fingers pads + engine outline + fiber ribbon drawn per layer
    pads = "".join(f'<rect x="78" y="{y}" width="38" height="10" fill="{GOLD[1]}" opacity="0.35"/>' for y in range(64, 300, 24))
    ribbon = "".join(f'<line x1="898" y1="{y}" x2="1134" y2="{y2}" stroke="{FIBER}" stroke-width="1.2"/>' for y, y2 in ((130, 100), (150, 116), (170, 132), (190, 228), (210, 244), (230, 260)))
    for pid, (x, y, w, h, fill, stroke, lab) in SEC().items():
        key = ALIAS.get(pid, pid)
        op = f' opacity="{dim}"' if (selected and key != selected) else ""
        extra = pads if pid == "part.edge-fingers" else (ribbon if pid == "part.fau" else "")
        sel = f'<rect x="{x - 4}" y="{y - 4}" width="{w + 8}" height="{h + 8}" rx="2" fill="none" stroke="{ACC}" stroke-width="1"/>' if selected == key else ""
        col = DIETXT if fill in (DIE[0], BLK[0], PCB[0]) else T["ink2"]
        ly = y + h - 12 if h > 44 else y + h / 2 + 4
        lbl = f'<text x="{x + w / 2}" y="{ly}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{col}" letter-spacing="0.06em">{lab}</text>' if lab else ""
        g.append(f'<g data-part="{key}"{op}><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="0.8"/>{extra}{sel}{lbl}</g>')
    g.append(f'<rect x="466" y="84" width="446" height="192" fill="none" stroke="{T["hair2"]}" stroke-dasharray="3 3"/>')
    g.append(f'<text x="472" y="78" font-family="{MONO}" font-size="10" fill="{T["muted"]}" letter-spacing="0.1em">光引擎</text>')
    g.append(f'<text x="720" y="94" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{T["ink2"]}" letter-spacing="0.1em">硅光 PIC · 分束 · MZM · 波导</text>')
    if captions:
        for cx, cy, tx, anc, col in [(60, 30, "顶盖已揭开 · 俯视", "start", T["muted"]), (1220, 30, "壳体", "end", T["muted"]), (97, 318, "金手指", "middle", T["muted"]), (230, 292, "主 PCB", "middle", DIETXT), (1177, 312, "MPO × 2", "middle", T["muted"]), (30, 200, "主机", "middle", T["muted"])]:
            g.append(f'<text x="{cx}" y="{cy}" text-anchor="{anc}" font-family="{MONO}" font-size="10" fill="{col}" letter-spacing="0.08em">{tx}</text>')
    if path:
        seq = TX if path == "tx" else RX
        f = lambda seq_: " ".join(f"{x},{y}" for x, y in seq_)
        if path == "tx":
            e = [(-10, 180), (97, 180), (230, 180), (355, 180), (430, 150), (592, 135), (662, 135), (700, 150)]
            o = [(700, 150), (840, 150), (869, 150), (898, 150), (1134, 116), (1177, 116), (1280, 116)]
            g.append(f'<polyline points="{f(e)}" fill="none" stroke="{INK_LINE}" stroke-width="1.4" stroke-linejoin="round"/>')
            g.append(f'<polyline points="{f(o)}" fill="none" stroke="{ACC}" stroke-width="1.6" stroke-linejoin="round"/>')
            g.append(f'<polyline points="502,145 528,145 560,150 600,150" fill="none" stroke="{ACC}" stroke-width="1.6"/><polyline points="502,215 528,215 560,210 600,210" fill="none" stroke="{ACC}" stroke-width="1.6" opacity="0.6"/>')
        else:
            o = [(1280, 244), (1177, 244), (1134, 244), (898, 226), (869, 226), (803, 226)]
            e = [(803, 226), (662, 225), (592, 225), (430, 210), (355, 210), (230, 210), (97, 210), (-10, 210)]
            g.append(f'<polyline points="{f(o)}" fill="none" stroke="{ACC}" stroke-width="1.6" stroke-dasharray="4 4"/><polyline points="{f(e)}" fill="none" stroke="{INK_LINE}" stroke-width="1.4" stroke-dasharray="4 4"/>')
        if stations:
            for s_ in seq:
                x, y = A[s_["partId"]]
                if path == "rx": y += 30 if s_["partId"] not in ("part.pd", "part.tia") else 0
                optical = s_["signal"] == "光" or s_["partId"] in ("part.pic", "part.pd")
                col = ACC if optical else INK_LINE
                g.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{T["bg"]}" stroke="{col}" stroke-width="1.2"/>'
                         f'<text x="{x}" y="{y + 3.5}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="500" fill="{col}">{s_["step"]:02d}</text>')
    tr = f' transform="scale({scale})"' if scale != 1 else ""
    return (f'<svg viewBox="0 0 1280 360" width="{1280 * scale:.0f}" height="{360 * scale:.0f}" style="display:block;overflow:visible" role="img" aria-label="1.6T 光模块俯视拆解">'
            f'<g{tr}>{"".join(g)}</g></svg>')

# ---------------------------------------------------------------- A. 剖面
def board_section():
    hero = f"""
<section style="position:relative;padding:40px 80px 0">
  <div style="display:grid;grid-template-columns:minmax(0,1fr) 420px;gap:60px;align-items:end">
    <div style="display:flex;flex-direction:column;gap:18px">
      {eyebrow("Quantum-X800 · OSFP224 · 1.6T DR8 · 硅光")}
      <h1 style="margin:0;font-size:68px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">1.6T 光模块</h1>
      <p style="margin:6px 0 0;font-size:19px;line-height:1.55;color:{T['ink2']};font-weight:300;max-width:640px;text-wrap:pretty">一只正在出货的模块,揭开上盖往下看。电信号从左边金手指进来,在硅光芯片上变成光,从右边 MPO 出去。沿这条线走一遍,每一站是一个部件,每个部件背后是一列公司。</p>
    </div>
    <div style="display:flex;flex-direction:column;gap:10px;padding-bottom:6px">
      {readouts([("通道", "8 × 200G PAM4"), ("波长", "1310 nm · 500 m"), ("功耗", "约 22 W"), ("光口", "MPO-16 APC")])}
      {readouts([("架构", "硅光 PIC · 外置 CW × 2 · 3nm DSP"), ("在哪", "Quantum-X800 · Spectrum-X800 · CX-9")])}
    </div>
  </div>
</section>"""
    drawing = f"""
<section style="padding:64px 80px 0">
  {section_svg()}
  <div style="display:flex;gap:26px;margin-top:14px;align-items:baseline">
    <span style="display:inline-flex;align-items:center;gap:8px">{mono("电信号")}<span style="display:inline-block;width:22px;height:0;border-top:1.4px solid {INK_LINE}"></span></span>
    <span style="display:inline-flex;align-items:center;gap:8px">{mono("光信号")}<span style="display:inline-block;width:22px;height:0;border-top:1.6px solid {ACC}"></span></span>
    {mono("发送方向 · 接收沿虚线原路返回")}
  </div>
</section>"""
    cols = []
    for s in TX:
        p = PARTS[s["partId"]]
        optical = s["signal"] == "光" or s["partId"] == "part.pic"
        cols.append(f"""
    <div style="display:flex;flex-direction:column;gap:6px;padding:16px 0 0;border-top:1px solid {T['hair']}">
      <span style="font-family:{MONO};font-size:12px;letter-spacing:0.06em;color:{ACC if optical else T['muted']}">{s['step']:02d} · {s['signal']}</span>
      <span style="font-size:16px;font-weight:500;color:{T['ink']};line-height:1.3">{p['name'].split('（')[0].split('(')[0]}</span>
      <span style="font-size:12.5px;color:{T['ink2']};line-height:1.45">{s['text']}</span>
      <span style="font-family:{MONO};font-size:11px;color:{T['muted']};margin-top:4px">{len(p['companies'])} 家 · {a_count(p)} 家 A 股</span>
    </div>""")
    stations = f"""
<section style="padding:40px 80px 0">
  {head("信号怎么走 · 九站", link("接收 RX →"))}
  <div style="display:grid;grid-template-columns:repeat(9, minmax(0,1fr));gap:20px">{"".join(cols)}</div>
</section>"""
    body = nav(["Quantum-X800", "1.6T 光模块"]) + hero + drawing + stations + footer("剖面为示意,不按比例;部件与信号顺序对应 OSFP224 DR8 硅光方案的通用结构。公司映射 126 条,证据级见各部件与公司页。")
    return wrap(T, body, height=1240)

# ---------------------------------------------------------------- B. 站点 (dense, companies on the page)
def board_stations():
    cols = []
    for s in TX:
        p = PARTS[s["partId"]]
        optical = s["signal"] == "光" or s["partId"] == "part.pic"
        groups = []
        for st in STAGE_ORDER:
            cs = [c for c in p["companies"] if c["stage"] == st]
            if not cs:
                continue
            items = "".join(
                f'<div style="display:flex;justify-content:space-between;gap:8px;align-items:baseline;padding:5px 0;border-top:1px solid {T["hair"]}">'
                f'<span style="font-size:13px;color:{T["ink"] if c["evidence"] != "candidate" else T["muted"]};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{c["name"].split("（")[0]}</span>'
                f'{mono(mkt(c["market"]), size=11)}</div>' for c in cs[:6])
            more = f'<div style="padding:5px 0 0">{mono(f"+ {len(cs) - 6}", size=11)}</div>' if len(cs) > 6 else ""
            groups.append(f'<div style="display:flex;flex-direction:column;margin-top:12px">{mono(STAGE_NAME[st], size=11)}<div style="height:6px"></div>{items}{more}</div>')
        cols.append(f"""
    <div style="display:flex;flex-direction:column;padding-top:16px;border-top:1px solid {T['hair2']}">
      <span style="font-family:{MONO};font-size:12px;letter-spacing:0.06em;color:{ACC if optical else T['muted']}">{s['step']:02d} · {s['signal']}</span>
      <span style="font-size:16px;font-weight:500;color:{T['ink']};line-height:1.3;margin-top:6px">{p['name'].split('（')[0].split('(')[0]}</span>
      <span style="font-family:{MONO};font-size:11px;color:{T['muted']};margin-top:4px">{len(p['companies'])} 家 · {a_count(p)} A 股</span>
      {"".join(groups)}
    </div>""")
    body = nav(["Quantum-X800", "1.6T 光模块"]) + f"""
<section style="padding:40px 80px 0;display:grid;grid-template-columns:520px minmax(0,1fr);gap:60px;align-items:end">
  <div style="display:flex;flex-direction:column;gap:14px">
    {eyebrow("Quantum-X800 · OSFP224 · 1.6T DR8 · 硅光")}
    <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">1.6T 光模块<br>信号怎么走</h1>
    <p style="margin:6px 0 0;font-size:17px;line-height:1.55;color:{T['ink2']};font-weight:300;text-wrap:pretty">九站,从金手指到 MPO。每一站底下直接列出谁在做,按材料 → 芯片 → 器件 → 引擎 → 连接的顺序;一家公司出现在几站,它就吃到几个环节。</p>
  </div>
  <div style="display:flex;flex-direction:column;gap:10px;align-items:flex-end">{section_svg(scale=0.62, stations=True, captions=False)}</div>
</section>
<section style="padding:44px 80px 0">
  <div style="display:grid;grid-template-columns:repeat(9, minmax(0,1fr));gap:18px">{"".join(cols)}</div>
</section>""" + footer("同一家公司跨站出现时不合并;这是设计上的选择,让「一家公司吃几个环节」直接从页面上数出来。证据级:名字为墨色 = 已核验或行业共识,灰色 = 候选 · 待核验。")
    return wrap(T, body, height=1140)

# ---------------------------------------------------------------- C. 分层 (isometric exploded, physically faithful)
def exploded_svg():
    """four physical layers of the OSFP module, exploded; signal path drawn across."""
    global OX, OY
    n, gap = 4, 78
    W_, D_ = 300, 110
    OX_, OY_ = 330, (W_ / 2 + D_ / 2) * SY_ + (n - 1) * gap + 40
    def Q(x, y, z):
        return (OX_ + (x - y) * CX_, OY_ + (x + y) * SY_ - z)
    def box(w, d, z, t, top, left, right, cx=0.0, cy=0.0, op=""):
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
        zt = z + t
        f = lambda seq: " ".join(f"{x:.1f},{y:.1f}" for x, y in seq)
        L = [Q(x0, y1, zt), Q(x1, y1, zt), Q(x1, y1, z), Q(x0, y1, z)]
        R = [Q(x1, y0, zt), Q(x1, y1, zt), Q(x1, y1, z), Q(x1, y0, z)]
        Tp = [Q(x0, y0, zt), Q(x1, y0, zt), Q(x1, y1, zt), Q(x0, y1, zt)]
        return f'<g{op}><polygon points="{f(L)}" fill="{left}"/><polygon points="{f(R)}" fill="{right}"/><polygon points="{f(Tp)}" fill="{top}"/></g>'
    L = THEME == "light"; tri = lambda m, r: (m[0], m[1], r)
    alu = tri(ALU, "#C4C8CE" if L else "#BFC4CA"); pcb = tri(PCB, "#31473C" if L else "#3A5546"); die = tri(DIE, "#1F2226" if L else "#262A30")
    si = tri(SI, "#84999F" if L else "#8EA3AD"); gold = tri(GOLD, "#BC9C55" if L else "#C5A55F"); tan = tri(TAN, "#C0AE7B" if L else "#C8B786"); blk = tri(BLK, "#2B2D31" if L else "#33363B")
    parts, anchors = [], {}
    # z levels bottom → top: shell 0, pcb 1, engine 2, lid 3
    z = 0
    parts.append(box(W_, D_, z, 10, *blk)); anchors["shell"] = Q(0, D_ / 2, z + 5)
    z += gap
    parts.append(box(W_, D_, z, 6, *pcb))
    parts.append(box(44, D_ - 20, z + 6, 2, *gold, cx=-W_ / 2 + 22))            # fingers
    parts.append(box(60, 60, z + 6, 12, *die, cx=-60))                          # DSP
    parts.append(box(30, 24, z + 6, 6, *blk, cx=-118, cy=30))                   # power
    anchors["pcb"] = Q(0, D_ / 2, z + 3); anchors["dsp"] = Q(-60, 0, z + 18); anchors["fingers"] = Q(-W_ / 2 + 22, 0, z + 8)
    z += gap
    parts.append(box(200, 90, z, 4, *tan, cx=40))                               # engine substrate
    parts.append(box(110, 50, z + 4, 4, *si, cx=40))                            # PIC
    parts.append(box(22, 18, z + 8, 6, *die, cx=12, cy=-12)); parts.append(box(22, 18, z + 8, 6, *die, cx=60, cy=-12))  # DRV / TIA
    parts.append(box(26, 20, z + 4, 8, *gold, cx=-36, cy=8))                    # CW lasers
    parts.append(box(18, 40, z + 4, 10, GLASS[0], GLASS[1], GLASS[1], cx=106))  # FAU
    anchors["engine"] = Q(40, 45, z + 2); anchors["pic"] = Q(40, 0, z + 8); anchors["laser"] = Q(-36, 8, z + 12); anchors["fau"] = Q(106, 0, z + 14)
    z += gap
    parts.append(box(W_, D_, z, 14, *alu))
    fins = []
    for k in range(9):
        yy = -D_ / 2 + 12 + k * ((D_ - 24) / 8)
        a, b = Q(-W_ / 2 + 12, yy, z + 14), Q(W_ / 2 - 12, yy, z + 14)
        fins.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{FIN}" stroke-width="3" stroke-linecap="round"/>')
    parts.append("".join(fins)); anchors["lid"] = Q(0, D_ / 2, z + 7)
    # signal path (dashed hops between layers)
    zp, ze = gap + 8, 2 * gap + 8
    p1 = [Q(-W_ / 2 - 30, 0, zp), Q(-W_ / 2 + 22, 0, zp), Q(-60, 0, zp + 12)]
    p2 = [Q(-60, 0, zp + 12), Q(12, -12, ze + 6)]
    p3 = [Q(12, -12, ze + 6), Q(40, 0, ze + 4), Q(106, 0, ze + 8), Q(W_ / 2 + 60, 0, ze + 8)]
    f = lambda seq: " ".join(f"{x:.1f},{y:.1f}" for x, y in seq)
    path = (f'<polyline points="{f(p1)}" fill="none" stroke="{INK_LINE}" stroke-width="1.4"/>'
            f'<polyline points="{f(p2)}" fill="none" stroke="{INK_LINE}" stroke-width="1.2" stroke-dasharray="3 3"/>'
            f'<polyline points="{f(p3)}" fill="none" stroke="{ACC}" stroke-width="1.6"/>')
    svg = f'<svg viewBox="0 0 660 {OY_ + 60:.0f}" width="660" height="{OY_ + 60:.0f}" style="display:block;overflow:visible">{"".join(parts)}{path}</svg>'
    return svg, anchors

def board_exploded():
    svg, anchors = exploded_svg()
    LEFT, TOP, LX = 120, 250, 800
    items = [
        ("lid", "01", "顶盖与散热", "Finned top · TIM", "翅片顶盖把 DSP 与激光器的热量导到笼子", "4 家"),
        ("engine", "02", "光引擎", "PIC · Driver / TIA · CW · FAU", "信号在这一层由电变光;良率与产能的瓶颈", "9 家"),
        ("pic", "", "硅光芯片", "SiPh PIC", "分束、调制、波导、Ge PD 在同一颗芯片", "15 家 · 6 A 股"),
        ("laser", "", "CW 激光器", "External CW × 2", "硅光路线最紧的上游", "16 家 · 4 A 股"),
        ("fau", "", "光纤阵列", "FAU → MPO", "与 PIC 边缘对准耦合", "7 家 · 4 A 股"),
        ("pcb", "03", "主 PCB 与 DSP", "Host PCB · 3nm DSP", "金手指进来的 224G 在这里重定时", "10 家 · 6 A 股"),
        ("shell", "04", "壳体", "OSFP housing · MPO", "机械、EMI、拉环、光口", "4 家 · 3 A 股"),
    ]
    lines, labels = [], []
    for i, (aid, idx, name, en, fn, cnt) in enumerate(items):
        ax, ay = anchors[aid]
        px, py = LEFT + ax, TOP + ay
        ly = 330 + i * 82
        lines.append(f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1440" height="1200" viewBox="0 0 1440 1200" fill="none"><path d="M{px:.0f} {py:.0f} H{LX - 60} V{ly + 8} H{LX - 20}" stroke="{T["hair2"]}" stroke-width="1"/><circle cx="{px:.0f}" cy="{py:.0f}" r="3" fill="{T["bg"]}" stroke="{T["ink2"]}" stroke-width="1.4"/></svg>')
        labels.append(f"""
    <div style="position:absolute;left:{LX}px;top:{ly - 6}px;width:520px;display:flex;gap:18px;align-items:baseline">
      <span style="font-family:{MONO};font-size:12px;color:{T['muted']};letter-spacing:0.06em;width:22px;flex:none">{idx}</span>
      <div style="display:flex;flex-direction:column;gap:3px">
        <div style="display:flex;gap:10px;align-items:baseline"><span style="font-size:{17 if idx else 15}px;font-weight:500;color:{T['ink']}">{name}</span><span style="font-size:12px;color:{T['muted']}">{en}</span>{mono("· " + cnt, size=11)}</div>
        <span style="font-size:13px;color:{T['ink2']};line-height:1.4">{fn}</span>
      </div>
    </div>""")
    body = nav(["Quantum-X800", "1.6T 光模块"]) + f"""
<section style="position:relative;height:1040px">
  <div style="position:absolute;left:80px;top:40px;display:flex;flex-direction:column;gap:18px;width:820px">
    {eyebrow("Quantum-X800 · OSFP224 · 1.6T DR8 · 硅光")}
    <h1 style="margin:0;font-size:68px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">1.6T 光模块</h1>
    <p style="margin:6px 0 0;font-size:19px;line-height:1.55;color:{T['ink2']};font-weight:300;max-width:600px;text-wrap:pretty">四层实物,从顶盖到壳体。这不是产业链分类,是这只模块拆开真的有的四层;信号线从金手指穿到 MPO。</p>
  </div>
  <div style="position:absolute;left:{LEFT}px;top:{TOP}px">{svg}</div>
  {''.join(lines)}{''.join(labels)}
</section>""" + footer("分层几何为示意;层内部件的相对位置按 OSFP224 硅光模块通用结构摆放,不对应任何一家的具体设计。")
    return wrap(T, body, height=1180)

# ---------------------------------------------------------------- D. 选中一个部件(剖面 A 的选中态)
def board_selected():
    pid = "part.cw-laser"
    p = PARTS[pid]
    svg = section_svg(selected=pid, scale=0.62, stations=False, captions=False)
    ax, ay = ANCH()[pid]
    LEFT, TOP = 80, 150
    px, py = LEFT + ax * 0.62, TOP + ay * 0.62
    CX_, ky = 900, 104
    leader = (f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1440" height="1400" viewBox="0 0 1440 1400" fill="none">'
              f'<path d="M{px:.0f} {py:.0f} V{TOP - 30} H{CX_ - 30} V{ky}" stroke="{ACC}" stroke-width="1" opacity="0.55"/>'
              f'<circle cx="{px:.0f}" cy="{py:.0f}" r="3.5" fill="{ACC}"/><circle cx="{CX_ - 30}" cy="{ky}" r="2.5" fill="{ACC}"/></svg>')
    mats = "".join(row("28px minmax(0,1fr)", [mono(f"{i + 1:02d}"), text(m, 14, T["ink"])], "10px 0") for i, m in enumerate(p["materials"]))
    groups = []
    for st in STAGE_ORDER:
        cs = [c for c in p["companies"] if c["stage"] == st]
        if not cs:
            continue
        rows = "".join(row("150px 96px 40px minmax(0,1fr) 84px",
                           [title(c["name"].split("（")[0], 15), mono(c["ticker"] or "—", size=11), mono(mkt(c["market"]), size=11),
                            text(c["role"], 13), mono(EV[c["evidence"]], T["muted"] if c["evidence"] == "candidate" else T["ink2"], 11)], "11px 0") for c in cs)
        groups.append(f'<div style="display:flex;flex-direction:column;margin-top:18px">{eyebrow(STAGE_NAME[st] + f" · {len(cs)}")}<div style="height:8px"></div>{rows}{rows_end()}</div>')
    content = f"""
<div style="position:absolute;left:{CX_}px;top:96px;width:460px;display:flex;flex-direction:column;gap:36px">
  <div style="display:flex;flex-direction:column;gap:14px">
    {eyebrow("06 / 09 · CW-LASER", accent=True)}
    <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">CW 激光器</h1>
    <span style="font-size:15px;color:{T['muted']}">{p['nameEn']} · 光源环节 · {link("篮子 →", 15)}</span>
    <p style="margin:10px 0 0;font-size:17px;line-height:1.6;color:{T['ink2']};font-weight:300;text-wrap:pretty">{p['function']}</p>
    {readouts([(k, v) for k, v in zip(["器件", "功率", "温控", "耦合"], p["keySpecs"])])}
  </div>
  <div style="display:flex;flex-direction:column">{head("上游材料 · 3")}{mats}{rows_end()}</div>
</div>
<div style="position:absolute;left:80px;top:{TOP + 320}px;width:740px;display:flex;flex-direction:column">
  {head(f"公司 · {len(p['companies'])} · {a_count(p)} 家 A 股", link("查看该环节全部公司 →"))}
  {"".join(groups)}
</div>"""
    hint = f"""<div style="position:absolute;left:80px;top:1330px;display:flex;align-items:center;gap:14px;font-size:12px;color:{T['muted']}"><span style="font-family:{MONO};font-size:11px;letter-spacing:0.08em;padding:3px 6px;border:1px solid {T['hair2']};border-radius:4px">ESC</span><span>或点击空白处回到整只模块</span></div>"""
    body = nav(["Quantum-X800", "1.6T 光模块", "CW 激光器"]) + f"""
<section style="position:relative;height:1380px">
  <div style="position:absolute;left:{LEFT}px;top:{TOP}px">{svg}</div>
  {leader}{content}{hint}
</section>"""
    return wrap(T, body, height=1444)

# ---------------------------------------------------------------- write
BOARDS = [
    ("DirectionA", board_section, 1240, "A · 俯视 — 揭开上盖的俯视图是主角,九站在下面"),
    ("DirectionB", board_stations, 1140, "B · 站点 — 九站是主角,公司直接铺在页面上"),
    ("DirectionC", board_exploded, 1180, "C · 分层 — 沿用现在 main 的等距分层语言,但只画实物真有的四层"),
    ("Main", board_selected, 1444, "选中一个部件 — 剖面 A 的选中态(CW 激光器)"),
]
NOTES = {
    "DirectionA": "A · 剖面\n\n为什么:最接近你说的「横截面上写着信号怎么走」。一张揭开上盖的俯视图,一条线,九个编号站点;公司不在这一屏出现,只给数量,点进去才展开(渐进披露)。\n\n代价:剖面是二维示意,没有等距分层那种「实物感」;九站的字要小。",
    "DirectionB": "B · 站点\n\n为什么:把你截图里的「信号怎么走」那一条抬成主角,每站底下直接列公司,按阶段分组。一屏就能数出「一家公司吃几个环节」。\n\n代价:密;剖面只剩一张缩略图;与现在 main 的「一屏一个主角」原则有张力。",
    "DirectionC": "C · 分层\n\n为什么:和现在 main 的视觉语言完全连续(等距、材质、右侧引线标注),只是把「九个研究模块」换成「这只模块真有的四层」。\n\n代价:信号线在等距图上穿层不好读;它回答「有哪几层」多过「信号怎么走」。",
    "Main": "选中态(以 A 为例)\n\n点一个部件:剖面缩到左上并变淡,该部件成为主角,右栏是功能 / 参数 / 上游材料,下方是公司,按 材料 → 芯片 → 器件 → 设备 分组,每行带 ticker · 市场 · 证据级。\n\n这一页不管选 A/B/C 都需要,结构大致一样。",
}
files, artboards, annotations = [], [], []
for theme, yy in (("light", 0), ("dark", 1760)):
    set_theme(theme)
    x = 0
    for name, fn, h, ttl in BOARDS:
        fname = f"{name}{'' if theme == 'light' else 'Dark'}.dc.html"
        with open(os.path.join(HERE, fname), "w", encoding="utf-8") as f:
            f.write(fn())
        files.append(fname)
        artboards.append({"file": fname, "title": f"{ttl} · {'浅' if theme == 'light' else '深'}", "x": x, "y": yy, "w": 1440, "h": h})
        if theme == "light":
            annotations.append({"id": f"note-{name.lower()}", "x": x, "y": -230, "w": 460, "text": NOTES[name]})
        x += 1440 + 140
set_theme("light")
annotations.insert(0, {"id": "brief", "x": -560, "y": 0, "w": 480, "text":
    "physical-first · 方向稿 v0(2026-09-04)\n\n问题:现在 main 上的「CPO 光模块」是产业链分类,不是一只在出货的模块。这里反过来:先拿一只真实模块(1.6T OSFP DR8 硅光,Quantum-X800 在用),让信号从金手指走到 MPO,每一站挂公司。\n\n三个方向只差「谁是主角」:A 剖面 · B 站点 · C 分层。上排浅色,下排深色。\n\n全部沿用 design-rules v3:页面即背景、无卡片、hairline rows、Geist + 系统中文、唯一强调色。公司名单来自 physical/data 的 126 条映射,证据级三档。"})
canvas = {"artboards": artboards, "annotations": annotations, "launch": {"view": "canvas"}}
with open(os.path.join(HERE, "canvas.json"), "w", encoding="utf-8") as f:
    json.dump(canvas, f, ensure_ascii=False, indent=2)
print("ok", files)
