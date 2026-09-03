# -*- coding: utf-8 -*-
"""Generates the CPO Explorer direction artboards (.dc.html) + canvas.json."""
import json, math, os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- tokens
LIGHT = dict(
    bg="#F7F6F3", ink="#1A1B1E", ink2="#44474D", muted="#8A8E96", faint="#B8BBC1",
    hair="#E4E2DD", hair2="#D3D0CA", accent_default="#2F5FC9",
    accent_opts=["#2F5FC9", "#B07A2E", "#2A7A6B", "#1A1B1E"],
    dim_opacity="0.14",
)
DARK = dict(
    bg="#0F1012", ink="#F1F0EC", ink2="#C3C4C8", muted="#7E8189", faint="#4E5158",
    hair="#25272B", hair2="#33363B", accent_default="#7AA2F5",
    accent_opts=["#7AA2F5", "#D9A45C", "#5FB3A1", "#F1F0EC"],
    dim_opacity="0.16",
)

FONT_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500'
             '&amp;family=Noto+Sans+SC:wght@300;400;500;600&amp;display=swap">')
SANS = '"Geist", "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", system-ui, sans-serif'
MONO = "'Geist Mono', 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace"

# ---------------------------------------------------------------- content
LAYERS = [
    dict(id="thermal", idx="01", code="THERMAL", name="散热与上盖", en="Heat spreader / lid",
         fn="均热板与冷板把 ASIC 与光引擎的热量导出", chain="07 散热与结构"),
    dict(id="host-asic", idx="02", code="HOST-ASIC", name="交换 ASIC", en="Switch ASIC",
         fn="1.6T / 3.2T 交换芯片,完成数据交换与调度", chain="02 交换 ASIC"),
    dict(id="eic", idx="03", code="EIC", name="电处理层", en="Driver / TIA / Retimer",
         fn="224G PAM4 电信号驱动、放大与重定时", chain="05 光引擎与封装"),
    dict(id="pic", idx="04", code="SIPH-PIC", name="硅光芯片", en="Silicon photonics PIC",
         fn="调制、波分复用与片上波导耦合,光学引擎核心", chain="03 硅光"),
    dict(id="laser", idx="05", code="LASER", name="激光器阵列", en="EML / DFB laser array",
         fn="外置连续波光源,为硅光芯片供光", chain="04 光源 / 激光器"),
    dict(id="receiver", idx="06", code="PD-ARRAY", name="光电探测阵列", en="Photodetector array",
         fn="接收光信号并转换为电流", chain="09 光器件与连接"),
    dict(id="fiber", idx="07", code="FAU", name="光纤阵列", en="Fiber array unit / MPO",
         fn="多通道光纤对准、耦合与出入光接口", chain="09 光器件与连接"),
    dict(id="substrate", idx="08", code="SUBSTRATE", name="共封装基板", en="Package substrate / interposer",
         fn="共同承载 ASIC 与光引擎的高密度互连基板", chain="06 基板与互连"),
    dict(id="board", idx="09", code="HOST-PCB", name="高速主板", en="Host PCB / edge connector",
         fn="系统级供电、控制与高速连接,金手指对接背板", chain="06 基板与互连"),
]

CHAIN = [
    ("01", "需求侧", "AI 集群 · 数据中心 · 交换机升级", "NVIDIA · Arista · Cisco · Meta · Microsoft"),
    ("02", "交换芯片 / ASIC", "Tomahawk · SerDes · 高密度端口", "Broadcom · NVIDIA · Marvell"),
    ("03", "硅光芯片", "PIC · 调制器 MZM · WDM", "Intel · Broadcom · 中际旭创 · 源杰科技"),
    ("04", "光源 / 激光器", "CW · EML · 高功率窄线宽", "Coherent · Lumentum · 仕佳光子 · 长光华芯"),
    ("05", "光引擎 / 封装", "共封装趋势 · 高密度封装 · 低损耗耦合", "Broadcom · Intel · Cisco · 光迅科技 · 新易盛"),
    ("06", "基板与互连", "高层数 PCB · FCBGA · 玻璃基板", "深南电路 · 沪电股份 · 东山精密"),
    ("07", "散热与结构件", "冷板 · 均热板 · 导热界面", "飞荣达 · 中石科技 · 领益智造"),
    ("08", "测试与设备", "耦合封装 · 光学对准 · 老化测试", "VIAVI · Keysight · Jabil · 罗博特科"),
    ("09", "光器件 / 连接", "FAU · MPO · 透镜 · 隔离器", "US Conec · Senko · 太辰光 · 天孚通信"),
    ("10", "下游整机与交换机", "数据中心交换机 · AI 服务器互联", "NVIDIA · Arista · Cisco · Juniper · HPE"),
]

PIC_PARTS = [
    ("01", "光调制器", "把电信号调制到光载波"),
    ("02", "WDM 复用 / 解复用", "组合或分离波长通道"),
    ("03", "波导与片上耦合结构", "在 PIC 内传输、分合与耦合光信号"),
]
PIC_COMPANIES = [
    ("Intel", "INTC · NASDAQ", "硅光平台"),
    ("Broadcom", "AVGO · NASDAQ", "CPO 光引擎"),
    ("中际旭创", "300308 · 深交所", "光模块 / 硅光"),
    ("源杰科技", "688498 · 上交所", "光芯片"),
]

SOURCE_LINE = "结构与代表企业整理自公开行业图示(图财社,2024–2026),为示意性梳理,不构成研究结论或投资建议。"

# ---------------------------------------------------------------- iso geometry
CX_, SY_ = 0.95, 0.30     # low-elevation dimetric (reference-like side view)
W, D = 270, 170           # base footprint (world units)
GAP = 66
# screen origin: computed so the whole stack fits the viewBox with a small margin
_WB, _DB = W * 1.08, D * 1.04
OX = (_WB / 2 + _DB / 2) * CX_ + 6
_TOP_T = 20
OY = (W / 2 + D / 2) * SY_ + (len([1]*9) - 1) * GAP + _TOP_T + 8
VB_W = int(OX * 2 + 6)
VB_H = int(OY + (_WB / 2 + _DB / 2) * SY_ + 12)

def P(x, y, z):
    return (OX + (x - y) * CX_, OY + (x + y) * SY_ - z)

def pts(seq):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in seq)

def slab(w, d, z, t, top, left, right, cx=0.0, cy=0.0, stroke=None, extra_top=""):
    """A box centred at (cx,cy) with footprint w×d, bottom at z, thickness t."""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
    zt = z + t
    left_face = [P(x0, y1, zt), P(x1, y1, zt), P(x1, y1, z), P(x0, y1, z)]
    right_face = [P(x1, y0, zt), P(x1, y1, zt), P(x1, y1, z), P(x1, y0, z)]
    top_face = [P(x0, y0, zt), P(x1, y0, zt), P(x1, y1, zt), P(x0, y1, zt)]
    sk = f' stroke="{stroke}" stroke-width="0.6"' if stroke else ""
    return (f'<polygon points="{pts(left_face)}" fill="{left}"{sk}/>'
            f'<polygon points="{pts(right_face)}" fill="{right}"{sk}/>'
            f'<polygon points="{pts(top_face)}" fill="{top}"{sk}/>' + extra_top)

def row_of_blocks(n, bw, bd, z, t, top, left, right, cy, span):
    out = []
    step = span / n
    start = -span / 2 + step / 2
    for i in range(n):
        out.append(slab(bw, bd, z, t, top, left, right, cx=start + i * step, cy=cy))
    return "".join(out)

def layer_svg(layer, z, theme, selected=None):
    """Returns svg markup for one layer at bottom height z."""
    lid = layer["id"]
    dark = theme is DARK
    # materials (top / left / right)
    alu = ("#DCDFE3", "#AEB3BA", "#C4C8CE")
    pcb = ("#3E5A4C", "#25382F", "#31473C")
    pcb_top_line = "#4A6A5A"
    die = ("#2A2D33", "#151719", "#1F2226")
    si = ("#9DB2C8", "#6D8299", "#84999F")
    gold = ("#D4B369", "#A3843F", "#BC9C55")
    tan = ("#D9C89C", "#A5945F", "#C0AE7B")
    blk = ("#3A3C40", "#1D1E21", "#2B2D31")
    fiber = "#6FA3E0" if not dark else "#7FB2F0"
    out = []
    w, d = W, D
    if lid == "thermal":
        t = 20
        out.append(slab(w, d, z, t, *alu))
        # fins: lines across the top face along x
        fins = []
        for k in range(9):
            yy = -d / 2 + 18 + k * ((d - 36) / 8)
            a, b = P(-w / 2 + 14, yy, z + t), P(w / 2 - 14, yy, z + t)
            fins.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#B9BEC5" stroke-width="3" stroke-linecap="round"/>')
        out.append("".join(fins))
    elif lid == "host-asic":
        t = 7
        out.append(slab(w * 0.94, d * 0.94, z, t, *pcb))
        out.append(slab(w * 0.34, d * 0.42, z + t, 9, *die, cx=w * 0.06, cy=d * 0.10))
        c = P(w * 0.06, d * 0.10, z + t + 9)
        out.append(f'<text x="{c[0]:.1f}" y="{c[1] + 4:.1f}" text-anchor="middle" font-family={MONO_ATTR} font-size="11" letter-spacing="0.12em" fill="#8E949C">ASIC</text>')
    elif lid == "eic":
        t = 7
        out.append(slab(w * 0.94, d * 0.94, z, t, *pcb))
        out.append(row_of_blocks(4, 34, 30, z + t, 6, *blk, cy=-d * 0.06, span=w * 0.62))
        out.append(row_of_blocks(4, 34, 30, z + t, 6, *blk, cy=d * 0.24, span=w * 0.62))
    elif lid == "pic":
        t = 7
        out.append(slab(w * 0.94, d * 0.94, z, t, *pcb))
        out.append(slab(w * 0.46, d * 0.40, z + t, 5, *si, cx=w * 0.06, cy=d * 0.10))
        # waveguide traces on the die
        wg = []
        for k in range(5):
            yy = -d * 0.10 + 10 + k * 12
            a, b = P(-w * 0.16, yy, z + t + 5), P(w * 0.28, yy, z + t + 5)
            wg.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#DCE7F2" stroke-width="1" opacity="0.8"/>')
        out.append("".join(wg))
    elif lid == "laser":
        t = 7
        out.append(slab(w * 0.94, d * 0.94, z, t, *pcb))
        out.append(row_of_blocks(8, 20, 26, z + t, 12, *gold, cy=d * 0.18, span=w * 0.74))
    elif lid == "receiver":
        t = 7
        out.append(slab(w * 0.94, d * 0.94, z, t, *pcb))
        out.append(row_of_blocks(8, 20, 24, z + t, 8, *blk, cy=d * 0.18, span=w * 0.74))
    elif lid == "fiber":
        t = 7
        out.append(slab(w * 0.94, d * 0.94, z, t, *pcb))
        out.append(slab(w * 0.80, d * 0.20, z + t, 16, *blk, cy=d * 0.26))
        fl = []
        for k in range(8):
            xx = -w * 0.36 + k * (w * 0.72 / 7)
            a = P(xx, d * 0.36, z + t + 8)
            b = (a[0] - 26, a[1] + 58)
            c1 = (a[0] + 2, a[1] + 24)
            fl.append(f'<path d="M{a[0]:.1f},{a[1]:.1f} C{c1[0]:.1f},{c1[1]:.1f} {b[0] + 10:.1f},{b[1] - 26:.1f} {b[0]:.1f},{b[1]:.1f}" fill="none" stroke="{fiber}" stroke-width="2.4" stroke-linecap="round" opacity="0.9"/>')
        out.append("".join(fl))
    elif lid == "substrate":
        t = 12
        out.append(slab(w, d, z, t, *tan))
        grid = []
        for k in range(6):
            yy = -d / 2 + 22 + k * ((d - 44) / 5)
            a, b = P(-w / 2 + 18, yy, z + t), P(w / 2 - 18, yy, z + t)
            grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#C9B77F" stroke-width="1"/>')
        out.append("".join(grid))
    elif lid == "board":
        t = 10
        w2, d2 = w * 1.08, d * 1.04
        out.append(slab(w2, d2, z, t, *pcb))
        # gold fingers along the left-front edge (y = +d2/2), on the top face
        fg = []
        n = 14
        for k in range(n):
            xx = -w2 / 2 + 22 + k * ((w2 - 44) / (n - 1))
            a, b = P(xx, d2 / 2 - 4, z + t), P(xx, d2 / 2 - 24, z + t)
            fg.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#D4B369" stroke-width="5"/>')
        out.append("".join(fg))
    return "".join(out), t

MONO_ATTR = "'Geist Mono', ui-monospace, monospace"
MONO_ATTR = f'"{MONO_ATTR}"'

def anchor_for(z, t, lid):
    w, d = (W * 1.08, D * 1.04) if lid == "board" else ((W, D) if lid in ("thermal", "substrate") else (W * 0.94, D * 0.94))
    return P(w / 2, -d / 4, z + t / 2)

def stack_svg(theme, selected=None, vb_w=None, vb_h=None, transform=None):
    vb_w = vb_w or VB_W
    vb_h = vb_h or VB_H
    """Returns (svg_markup, anchors) — anchors are in svg user units."""
    n = len(LAYERS)
    parts, anchors = [], {}
    # bottom layer first
    for i, layer in reversed(list(enumerate(LAYERS))):
        z = (n - 1 - i) * GAP
        lift = 22 if (selected and layer["id"] == selected) else 0
        markup, t = layer_svg(layer, z + lift, theme)
        op = ""
        if selected and layer["id"] != selected:
            op = f' opacity="{theme["dim_opacity"]}"'
        filt = ' filter="url(#lift)"' if (selected and layer["id"] == selected) else ""
        parts.append(f'<g data-layer="{layer["id"]}"{op}{filt}>{markup}</g>')
        anchors[layer["id"]] = anchor_for(z + lift, t, layer["id"])
    defs = ('<defs><filter id="lift" x="-20%" y="-20%" width="140%" height="160%">'
            '<feDropShadow dx="0" dy="18" stdDeviation="14" flood-color="#000" flood-opacity="0.22"/></filter></defs>')
    tr = f' transform="{transform}"' if transform else ""
    svg = (f'<svg viewBox="0 0 {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" '
           f'style="display:block;overflow:visible" role="img" aria-label="CPO 光模块九层分解">{defs}<g{tr}>{"".join(parts)}</g></svg>')
    return svg, anchors

# ---------------------------------------------------------------- html helpers
def helmet(theme):
    return f"""<helmet>
  {FONT_LINK}
  <style>
    html, body {{ margin: 0; background: {theme['bg']}; }}
    body {{ font-family: {SANS}; color: {theme['ink']}; -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }}
    a {{ color: {theme['accent_default']}; text-decoration: none; }}
    a:hover {{ color: {theme['ink']}; }}
    * {{ box-sizing: border-box; }}
  </style>
</helmet>"""

def nav(theme, crumb=None):
    t = theme
    crumb_html = ""
    if crumb:
        crumb_html = (f'<div style="display:flex;align-items:center;gap:10px;font-size:13px;color:{t["muted"]}">'
                      f'<span>CPO 光模块</span>'
                      f'<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="{t["faint"]}" stroke-width="1.4"><path d="M4.5 2.5 8 6l-3.5 3.5"/></svg>'
                      f'<span style="color:{t["ink"]}">{crumb}</span></div>')
    return f"""<header style="height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 80px">
  <div style="display:flex;align-items:center;gap:28px">
    <span style="font-weight:600;font-size:15px;letter-spacing:-0.01em;color:{t['ink']}">Serenity</span>
    {crumb_html}
  </div>
  <nav style="display:flex;align-items:center;gap:32px;font-size:14px">
    <span style="color:{t['ink']};font-weight:500">光模块</span>
    <span style="color:{t['muted']}">公司</span>
    <span style="color:{t['muted']}">研究</span>
  </nav>
</header>"""

def script_block(theme):
    props = {"accent": {"editor": "color", "default": theme["accent_default"], "options": theme["accent_opts"]}}
    return (f"<script data-dc-script data-props='{json.dumps(props)}'>\n"
            "class Component extends DCLogic {\n"
            "  renderVals() { return { accent: this.props.accent ?? '" + theme["accent_default"] + "' }; }\n"
            "}\n</script>")

def wrap(theme, body, width=1440, height=1000):
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
{helmet(theme)}
<div style="width:{width}px;min-height:{height}px;background:{theme['bg']};position:relative;overflow:hidden">
{body}
</div>
</x-dc>
{script_block(theme)}
</body>
</html>
"""

# ---------------------------------------------------------------- MAIN (overview)
def overview(theme):
    t = theme
    svg, anchors = stack_svg(theme)
    # Stack block position on the page
    STACK_LEFT, STACK_TOP = 300, 262
    LABEL_X = 872
    labels = []
    lines = []
    for layer in LAYERS:
        ax, ay = anchors[layer["id"]]
        px, py = STACK_LEFT + ax, STACK_TOP + ay
        lines.append(
            f'<div style="position:absolute;left:{px:.0f}px;top:{py:.0f}px;width:{LABEL_X - 20 - px:.0f}px;height:1px;background:{t["hair2"]}"></div>'
            f'<div style="position:absolute;left:{px - 3:.0f}px;top:{py - 3:.0f}px;width:7px;height:7px;border-radius:50%;background:{t["bg"]};border:1.5px solid {t["ink2"]}"></div>')
        labels.append(f"""
    <div style="position:absolute;left:{LABEL_X}px;top:{py - 12:.0f}px;width:500px;display:flex;gap:18px;align-items:baseline">
      <span style="font-family:{MONO};font-size:12px;color:{t['muted']};letter-spacing:0.06em;width:22px;flex:none">{layer['idx']}</span>
      <div style="display:flex;flex-direction:column;gap:3px">
        <div style="display:flex;gap:10px;align-items:baseline">
          <span style="font-size:17px;font-weight:500;color:{t['ink']};letter-spacing:-0.005em">{layer['name']}</span>
          <span style="font-size:12px;color:{t['muted']}">{layer['en']}</span>
        </div>
        <span style="font-size:13px;color:{t['ink2']};line-height:1.4">{layer['fn']}</span>
      </div>
    </div>""")

    hero = f"""
<section style="position:relative;height:1000px">
  <div style="position:absolute;left:80px;top:56px;display:flex;flex-direction:column;gap:18px;width:720px">
    <span style="font-family:{MONO};font-size:12px;letter-spacing:0.14em;color:{t['muted']}">CO-PACKAGED OPTICS · 1.6T / 3.2T</span>
    <h1 style="margin:0;font-size:68px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{t['ink']}">CPO 光模块</h1>
    <p style="margin:6px 0 0;font-size:19px;line-height:1.55;color:{t['ink2']};font-weight:300;max-width:600px;text-wrap:pretty">九层结构,从散热上盖到高速主板。点击任意一层,看它由什么构成、谁在做。</p>
  </div>
  <div style="position:absolute;left:{STACK_LEFT}px;top:{STACK_TOP}px">{svg}</div>
  {''.join(lines)}
  {''.join(labels)}
</section>"""

    # signal path
    nodes = [("PCB / 金手指", "电信号"), ("交换 ASIC", "电信号"), ("Driver / TIA", "电信号"), ("SiPh PIC", "电 → 光"), ("FAU / MPO", "光信号")]
    node_html = []
    for i, (nm, kind) in enumerate(nodes):
        node_html.append(f"""
      <div style="display:flex;flex-direction:column;gap:8px;min-width:118px">
        <span style="font-size:18px;font-weight:500;color:{t['ink']}">{nm}</span>
        <span style="font-family:{MONO};font-size:11px;letter-spacing:0.1em;color:{t['muted']}">{kind}</span>
      </div>""")
        if i < len(nodes) - 1:
            col = t['faint']
            node_html.append(f"""
      <svg width="40" height="12" viewBox="0 0 40 12" fill="none" style="flex:none;margin-top:9px"><path d="M0 6h36M31 1l5 5-5 5" stroke="{col}" stroke-width="1.2"/></svg>""")
    signal = f"""
<section style="padding:96px 80px 0;display:grid;grid-template-columns:300px minmax(0,1fr);gap:56px;align-items:start">
  <div style="display:flex;flex-direction:column;gap:14px">
    <span style="font-family:{MONO};font-size:12px;letter-spacing:0.14em;color:{t['muted']}">SIGNAL PATH</span>
    <h2 style="margin:0;font-size:34px;font-weight:600;letter-spacing:-0.02em;line-height:1.1;color:{t['ink']}">信号怎么走</h2>
    <p style="margin:4px 0 0;font-size:15px;line-height:1.6;color:{t['ink2']};font-weight:300;text-wrap:pretty">电信号从主板经交换芯片与驱动层进入硅光芯片,转换为光后由光纤阵列送出;返程由探测阵列完成光电转换。</p>
  </div>
  <div style="display:flex;align-items:flex-start;gap:10px;padding-top:12px">{''.join(node_html)}
  </div>
</section>"""

    # chain list
    rows = []
    for idx, nm, what, who in CHAIN:
        rows.append(f"""
    <div style="display:grid;grid-template-columns:40px 220px minmax(0,1fr) 420px;gap:24px;align-items:baseline;padding:18px 0;border-top:1px solid {t['hair']}">
      <span style="font-family:{MONO};font-size:12px;color:{t['muted']};letter-spacing:0.06em">{idx}</span>
      <span style="font-size:17px;font-weight:500;color:{t['ink']}">{nm}</span>
      <span style="font-size:13px;color:{t['muted']}">{what}</span>
      <span style="font-size:15px;color:{t['ink2']};line-height:1.5">{who}</span>
    </div>""")
    chain = f"""
<section style="padding:112px 80px 0">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:28px">
    <div style="display:flex;flex-direction:column;gap:14px;max-width:640px">
      <span style="font-family:{MONO};font-size:12px;letter-spacing:0.14em;color:{t['muted']}">INDUSTRY CHAIN</span>
      <h2 style="margin:0;font-size:34px;font-weight:600;letter-spacing:-0.02em;line-height:1.1;color:{t['ink']}">谁在造它</h2>
      <p style="margin:4px 0 0;font-size:15px;line-height:1.6;color:{t['ink2']};font-weight:300">十个环节,每个环节对应上面的一到两层。点击环节进入公司池。</p>
    </div>
    <span style="font-size:14px;color:{{{{accent}}}}">查看全部 20 家公司 →</span>
  </div>
  <div style="display:flex;flex-direction:column">{''.join(rows)}
    <div style="border-top:1px solid {t['hair']}"></div>
  </div>
</section>"""

    footer = f"""
<footer style="padding:72px 80px 56px;display:flex;justify-content:space-between;align-items:flex-end;gap:40px">
  <p style="margin:0;font-size:12px;line-height:1.6;color:{t['muted']};max-width:720px">{SOURCE_LINE}</p>
  <span style="font-family:{MONO};font-size:11px;letter-spacing:0.1em;color:{t['faint']}">SERENITY · CPO EXPLORER</span>
</footer>"""

    body = nav(theme) + hero + signal + chain + footer
    return wrap(theme, body, height=2440)

# ---------------------------------------------------------------- SELECTED (one layer)
def selected(theme):
    t = theme
    sel = "pic"
    svg, anchors = stack_svg(theme, selected=sel, transform="translate(0 0) scale(0.92)")
    STACK_LEFT, STACK_TOP = 120, 150
    ax, ay = anchors[sel]
    # apply the same transform to the anchor
    ax, ay = ax * 0.92, ay * 0.92
    px, py = STACK_LEFT + ax, STACK_TOP + ay
    CONTENT_X = 820
    EYEBROW_Y = 96 + 8   # page y of the mono eyebrow's centre line
    kx = CONTENT_X - 30
    line = (f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1440" height="1100" viewBox="0 0 1440 1100" fill="none">'
            f'<path d="M{px:.0f} {py:.0f} H{kx} V{EYEBROW_Y}" stroke="{{{{accent}}}}" stroke-width="1" opacity="0.55"/>'
            f'<circle cx="{px:.0f}" cy="{py:.0f}" r="3.5" fill="{{{{accent}}}}"/>'
            f'<circle cx="{kx}" cy="{EYEBROW_Y}" r="2.5" fill="{{{{accent}}}}"/></svg>')

    parts_rows = []
    for idx, nm, fn in PIC_PARTS:
        parts_rows.append(f"""
      <div style="display:grid;grid-template-columns:28px 200px minmax(0,1fr) 16px;gap:16px;align-items:baseline;padding:14px 0;border-top:1px solid {t['hair']}">
        <span style="font-family:{MONO};font-size:12px;color:{t['muted']}">{idx}</span>
        <span style="font-size:16px;font-weight:500;color:{t['ink']}">{nm}</span>
        <span style="font-size:13px;color:{t['ink2']}">{fn}</span>
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="{t['faint']}" stroke-width="1.4" style="align-self:center"><path d="M4.5 2.5 8 6l-3.5 3.5"/></svg>
      </div>""")

    co_rows = []
    for nm, tk, role in PIC_COMPANIES:
        co_rows.append(f"""
      <div style="display:grid;grid-template-columns:200px 170px minmax(0,1fr);gap:16px;align-items:baseline;padding:12px 0;border-top:1px solid {t['hair']}">
        <span style="font-size:16px;font-weight:500;color:{t['ink']}">{nm}</span>
        <span style="font-family:{MONO};font-size:12px;color:{t['muted']};letter-spacing:0.02em">{tk}</span>
        <span style="font-size:13px;color:{t['ink2']}">{role}</span>
      </div>""")

    content = f"""
<div style="position:absolute;left:{CONTENT_X}px;top:96px;width:540px;display:flex;flex-direction:column;gap:40px">
  <div style="display:flex;flex-direction:column;gap:14px">
    <span style="font-family:{MONO};font-size:12px;letter-spacing:0.14em;color:{{{{accent}}}}">04 / 09 · SIPH-PIC</span>
    <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{t['ink']}">硅光芯片</h1>
    <span style="font-size:15px;color:{t['muted']}">Silicon photonics PIC · 光学引擎</span>
    <p style="margin:10px 0 0;font-size:17px;line-height:1.6;color:{t['ink2']};font-weight:300;text-wrap:pretty">把电信号调制到光载波、按波长复用,并通过片上波导把光耦合进出光纤。它是 CPO 的光学核心,对应产业链中的硅光环节。</p>
  </div>

  <div style="display:flex;flex-direction:column">
    <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">
      <span style="font-family:{MONO};font-size:12px;letter-spacing:0.14em;color:{t['muted']}">PARTS · 3</span>
      <span style="font-size:13px;color:{t['muted']}">点击进入下一层</span>
    </div>{''.join(parts_rows)}
    <div style="border-top:1px solid {t['hair']}"></div>
  </div>

  <div style="display:flex;flex-direction:column">
    <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">
      <span style="font-family:{MONO};font-size:12px;letter-spacing:0.14em;color:{t['muted']}">COMPANIES · 硅光环节</span>
      <span style="font-size:13px;color:{{{{accent}}}}">查看该环节全部公司 →</span>
    </div>{''.join(co_rows)}
    <div style="border-top:1px solid {t['hair']}"></div>
  </div>

  <p style="margin:0;font-size:12px;line-height:1.6;color:{t['muted']}">代表企业来自公开行业图示,示意性;进入公司页可查看已核验的证据与状态。</p>
</div>"""

    hint = f"""
<div style="position:absolute;left:80px;bottom:44px;display:flex;align-items:center;gap:14px;font-size:12px;color:{t['muted']}">
  <span style="font-family:{MONO};font-size:11px;letter-spacing:0.08em;padding:3px 6px;border:1px solid {t['hair2']};border-radius:4px">ESC</span>
  <span>或点击空白处回到整机</span>
</div>"""

    body = nav(theme, crumb="硅光芯片") + f"""
<section style="position:relative;height:980px">
  <div style="position:absolute;left:{STACK_LEFT}px;top:{STACK_TOP}px">{svg}</div>
  {line}
  {content}
  {hint}
</section>"""
    return wrap(theme, body, height=1044)

# ---------------------------------------------------------------- write
files = {
    "Main.dc.html": overview(LIGHT),
    "Selected.dc.html": selected(LIGHT),
    "DarkMain.dc.html": overview(DARK),
    "DarkSelected.dc.html": selected(DARK),
}
for name, html in files.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(html)

canvas = {
    "artboards": [
        {"file": "Main.dc.html", "title": "总览 · 浅色", "x": 0, "y": 0, "w": 1440, "h": 2440},
        {"file": "Selected.dc.html", "title": "选中一层 · 浅色", "x": 1560, "y": 0, "w": 1440, "h": 1044},
        {"file": "DarkMain.dc.html", "title": "总览 · 深色", "x": 0, "y": 2600, "w": 1440, "h": 2440},
        {"file": "DarkSelected.dc.html", "title": "选中一层 · 深色", "x": 1560, "y": 2600, "w": 1440, "h": 1044},
    ],
    "annotations": [
        {"id": "how-to-read", "x": 1560, "y": 1220, "w": 440,
         "text": "看什么\n\n1. 没有任何容器边框,层级只靠留白、字号和对比——成立吗?\n2. 分层图作为主角,大小和位置舒服吗?\n3. 选中一层后,内容直接铺在页面上而不是弹出卡片——这是你要的\"部件像产品\"吗?\n4. 文字量:每屏不超过一段说明。哪里还嫌多?\n5. 浅色 / 深色,下面一行是同一页面的深色版。\n\n上方色块可以换强调色试试。"},
    ],
    "launch": {"view": "canvas"},
}
with open(os.path.join(OUT, "canvas.json"), "w", encoding="utf-8") as f:
    json.dump(canvas, f, ensure_ascii=False, indent=2)
print("ok", list(files))
