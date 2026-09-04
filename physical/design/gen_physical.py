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

# materials (light, from web/src/styles/tokens.css)
ALU = ("#DCDFE3", "#AEB3BA"); PCB = ("#3E5A4C", "#25382F"); DIE = ("#2A2D33", "#151719")
SI = ("#9DB2C8", "#6D8299"); GOLD = ("#D4B369", "#A3843F"); TAN = ("#D9C89C", "#A5945F")
BLK = ("#3A3C40", "#1D1E21"); GLASS = ("#E9ECEF", "#B8BBC1"); FIBER = "#6FA3E0"
INK_LINE = T["ink2"]

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

# ---------------------------------------------------------------- 2D section (side view)
# geometry in a 1280 × 300 box; every part → (x, y, w, h, fill, stroke, label)
SEC = OrderedDict([
    ("part.host-cage",     (0, 56, 100, 206, *ALU, "主机笼子")),
    ("part.shell",         (100, 236, 960, 16, *BLK, "")),
    ("part.lid-thermal",   (130, 112, 930, 18, *ALU, "")),
    ("part.pcb",           (60, 212, 980, 16, *PCB, "")),
    ("part.edge-fingers",  (60, 206, 52, 28, *GOLD, "")),
    ("part.power-mgmt",    (170, 190, 80, 22, *BLK, "")),
    ("part.dsp",           (300, 156, 130, 56, *DIE, "DSP")),
    ("part.cw-laser",      (480, 188, 60, 24, *GOLD, "CW")),
    ("part.laser-coupling",(544, 192, 14, 18, *GLASS, "")),
    ("part.pic",           (562, 186, 290, 26, *SI, "PIC")),
    ("part.driver",        (582, 160, 70, 26, *DIE, "DRV")),
    ("part.tia",           (700, 160, 70, 26, *DIE, "TIA")),
    ("part.pd",            (790, 190, 50, 18, "#84999F", "#6D8299", "PD")),
    ("part.fau",           (854, 182, 50, 34, *GLASS, "FAU")),
    ("part.mpo",           (960, 150, 220, 102, *BLK, "MPO")),
])
ENGINE_BOX = (470, 150, 440, 68)   # dashed outline: 光引擎
ANCH = {  # station anchor points on the drawing
    "part.host-cage": (40, 220), "part.edge-fingers": (88, 220), "part.pcb": (230, 220), "part.dsp": (365, 184),
    "part.driver": (617, 173), "part.cw-laser": (510, 200), "part.pic": (640, 199), "part.fau": (879, 199), "part.mpo": (1070, 199),
    "part.pd": (815, 199), "part.tia": (735, 173), "part.lid-thermal": (595, 121), "part.shell": (400, 244),
    "part.power-mgmt": (210, 201), "part.laser-coupling": (551, 201), "part.engine-assembly": (900, 150), "part.module-maker": (1180, 90),
}
TX = M["signalPath"]["tx"]
RX = M["signalPath"]["rx"]

def section_svg(selected=None, scale=1.0, stations=True, path="tx"):
    dim = "0.32"
    g = []
    # fins on the lid
    fins = "".join(f'<rect x="{x}" y="92" width="9" height="20" rx="1" fill="#B9BEC5"/>' for x in range(140, 1050, 18))
    for pid, (x, y, w, h, fill, stroke, lab) in SEC.items():
        op = f' opacity="{dim}"' if (selected and pid != selected) else ""
        extra = fins if pid == "part.lid-thermal" else ""
        sel = f'<rect x="{x - 3}" y="{y - 3}" width="{w + 6}" height="{h + 6}" rx="2" fill="none" stroke="{ACC}" stroke-width="1"/>' if selected == pid else ""
        lbl = (f'<text x="{x + w / 2}" y="{y + h / 2 + 4}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{"#8E949C" if fill in (DIE[0], BLK[0], PCB[0]) else T["ink2"]}" letter-spacing="0.06em">{lab}</text>' if lab else "")
        g.append(f'<g data-part="{pid}"{op}>{extra}<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="0.8"/>{sel}{lbl}</g>')
    caps = [(1190, 126, "顶盖 · TIM", "start", T["muted"]), (1190, 249, "壳体", "start", T["muted"]), (275, 224, "PCB", "middle", "#8E949C"), (86, 199, "金手指", "middle", T["muted"]), (210, 184, "电源", "middle", T["muted"])]
    for cx, cy, tx, anc, col in caps:
        g.append(f'<text x="{cx}" y="{cy}" text-anchor="{anc}" font-family="{MONO}" font-size="10" fill="{col}" letter-spacing="0.08em">{tx}</text>')
    # TIM strip + engine outline + fiber
    ex, ey, ew, eh = ENGINE_BOX
    g.append(f'<rect x="130" y="130" width="930" height="5" fill="{TAN[0]}" stroke="{TAN[1]}" stroke-width="0.5" opacity="{dim if selected and selected != "part.lid-thermal" else 1}"/>')
    g.append(f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" fill="none" stroke="{T["hair2"]}" stroke-dasharray="3 3"/>'
             f'<text x="{ex + 6}" y="{ey - 6}" font-family="{MONO}" font-size="10" fill="{T["muted"]}" letter-spacing="0.1em">光引擎</text>')
    g.append(f'<line x1="1180" y1="199" x2="1280" y2="199" stroke="{FIBER}" stroke-width="1.5"/>')
    # signal path
    if path:
        seq = TX if path == "tx" else RX
        pts = [ANCH[s["partId"]] for s in seq]
        if path == "tx":
            pts = [(-10, 220)] + pts + [(1280, 199)]
        else:
            pts = [(1280, 205)] + pts + [(-10, 226)]
        # split at PIC (electric → optical) for tx; at PD for rx
        cut = next(i for i, s in enumerate(seq) if s["partId"] == ("part.pic" if path == "tx" else "part.pd")) + 1
        e_pts, o_pts = (pts[:cut + 1], pts[cut:]) if path == "tx" else (pts[cut:], pts[:cut + 1])
        dash = ' stroke-dasharray="4 4"' if path == "rx" else ""
        g.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in e_pts)}" fill="none" stroke="{INK_LINE}" stroke-width="1.4" stroke-linejoin="round"{dash}/>')
        g.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in o_pts)}" fill="none" stroke="{ACC}" stroke-width="1.6" stroke-linejoin="round"{dash}/>')
        if path == "tx":  # CW feed
            g.append(f'<polyline points="510,200 562,199 600,199" fill="none" stroke="{ACC}" stroke-width="1.6"/>')
        if stations:
            for s in seq:
                x, y = ANCH[s["partId"]]
                optical = s["signal"] == "光" or s["partId"] in ("part.pic", "part.pd")
                col = ACC if optical else INK_LINE
                g.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{T["bg"]}" stroke="{col}" stroke-width="1.2"/>'
                         f'<text x="{x}" y="{y + 3.5}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="500" fill="{col}">{s["step"]:02d}</text>')
    tr = f' transform="scale({scale})"' if scale != 1 else ""
    return (f'<svg viewBox="0 0 1280 300" width="{1280 * scale:.0f}" height="{300 * scale:.0f}" style="display:block;overflow:visible" role="img" aria-label="1.6T 光模块剖面">'
            f'<g{tr}>{"".join(g)}</g></svg>')

# ---------------------------------------------------------------- A. 剖面
def board_section():
    hero = f"""
<section style="position:relative;padding:40px 80px 0">
  <div style="display:grid;grid-template-columns:minmax(0,1fr) 420px;gap:60px;align-items:end">
    <div style="display:flex;flex-direction:column;gap:18px">
      {eyebrow("Quantum-X800 · OSFP224 · 1.6T DR8 · 硅光")}
      <h1 style="margin:0;font-size:68px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">1.6T 光模块</h1>
      <p style="margin:6px 0 0;font-size:19px;line-height:1.55;color:{T['ink2']};font-weight:300;max-width:640px;text-wrap:pretty">一只正在出货的模块,从侧面切开。电信号从左边金手指进来,在硅光芯片上变成光,从右边 MPO 出去。沿这条线走一遍,每一站是一个部件,每个部件背后是一列公司。</p>
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
    return wrap(T, body, height=1180)

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
  <div style="display:flex;flex-direction:column;gap:10px;align-items:flex-end">{section_svg(scale=0.62, stations=True)}</div>
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
    alu = ("#DCDFE3", "#AEB3BA", "#C4C8CE"); pcb = ("#3E5A4C", "#25382F", "#31473C"); die = ("#2A2D33", "#151719", "#1F2226")
    si = ("#9DB2C8", "#6D8299", "#84999F"); gold = ("#D4B369", "#A3843F", "#BC9C55"); tan = ("#D9C89C", "#A5945F", "#C0AE7B"); blk = ("#3A3C40", "#1D1E21", "#2B2D31")
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
    parts.append(box(18, 40, z + 4, 10, "#E9ECEF", "#B8BBC1", "#D3D0CA", cx=106))  # FAU
    anchors["engine"] = Q(40, 45, z + 2); anchors["pic"] = Q(40, 0, z + 8); anchors["laser"] = Q(-36, 8, z + 12); anchors["fau"] = Q(106, 0, z + 14)
    z += gap
    parts.append(box(W_, D_, z, 14, *alu))
    fins = []
    for k in range(9):
        yy = -D_ / 2 + 12 + k * ((D_ - 24) / 8)
        a, b = Q(-W_ / 2 + 12, yy, z + 14), Q(W_ / 2 - 12, yy, z + 14)
        fins.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#B9BEC5" stroke-width="3" stroke-linecap="round"/>')
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
    svg = section_svg(selected=pid, scale=0.62, stations=False)
    ax, ay = ANCH[pid]
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
<div style="position:absolute;left:80px;top:{TOP + 300}px;width:740px;display:flex;flex-direction:column">
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
    ("DirectionA", board_section, 1180, "A · 剖面 — 侧视剖面是主角,九站在下面"),
    ("DirectionB", board_stations, 1140, "B · 站点 — 九站是主角,公司直接铺在页面上"),
    ("DirectionC", board_exploded, 1180, "C · 分层 — 沿用现在 main 的等距分层语言,但只画实物真有的四层"),
    ("Main", board_selected, 1444, "选中一个部件 — 剖面 A 的选中态(CW 激光器)"),
]
NOTES = {
    "DirectionA": "A · 剖面\n\n为什么:最接近你说的「横截面上写着信号怎么走」。一张侧视图,一条线,九个编号站点;公司不在这一屏出现,只给数量,点进去才展开(渐进披露)。\n\n代价:剖面是二维示意,没有等距分层那种「实物感」;九站的字要小。",
    "DirectionB": "B · 站点\n\n为什么:把你截图里的「信号怎么走」那一条抬成主角,每站底下直接列公司,按阶段分组。一屏就能数出「一家公司吃几个环节」。\n\n代价:密;剖面只剩一张缩略图;与现在 main 的「一屏一个主角」原则有张力。",
    "DirectionC": "C · 分层\n\n为什么:和现在 main 的视觉语言完全连续(等距、材质、右侧引线标注),只是把「九个研究模块」换成「这只模块真有的四层」。\n\n代价:信号线在等距图上穿层不好读;它回答「有哪几层」多过「信号怎么走」。",
    "Main": "选中态(以 A 为例)\n\n点一个部件:剖面缩到左上并变淡,该部件成为主角,右栏是功能 / 参数 / 上游材料,下方是公司,按 材料 → 芯片 → 器件 → 设备 分组,每行带 ticker · 市场 · 证据级。\n\n这一页不管选 A/B/C 都需要,结构大致一样。",
}
files, artboards, annotations = [], [], []
x = 0
for name, fn, h, ttl in BOARDS:
    fname = f"{name}.dc.html"
    with open(os.path.join(HERE, fname), "w", encoding="utf-8") as f:
        f.write(fn())
    files.append(fname)
    artboards.append({"file": fname, "title": ttl, "x": x, "y": 0, "w": 1440, "h": h})
    annotations.append({"id": f"note-{name.lower()}", "x": x, "y": -230, "w": 460, "text": NOTES[name]})
    x += 1440 + 140
annotations.insert(0, {"id": "brief", "x": -560, "y": 0, "w": 480, "text":
    "physical-first · 方向稿 v0(2026-09-04)\n\n问题:现在 main 上的「CPO 光模块」是产业链分类,不是一只在出货的模块。这里反过来:先拿一只真实模块(1.6T OSFP DR8 硅光,Quantum-X800 在用),让信号从金手指走到 MPO,每一站挂公司。\n\n三个方向只差「谁是主角」:A 剖面 · B 站点 · C 分层。选一个,再出深色版和其余状态。\n\n全部沿用 design-rules v3:页面即背景、无卡片、hairline rows、Geist + 系统中文、唯一强调色。公司名单来自 physical/data 的 126 条映射,证据级三档。"})
canvas = {"artboards": artboards, "annotations": annotations, "launch": {"view": "canvas"}}
with open(os.path.join(HERE, "canvas.json"), "w", encoding="utf-8") as f:
    json.dump(canvas, f, ensure_ascii=False, indent=2)
print("ok", files)
