import os
# -*- coding: utf-8 -*-
"""Teardown — the 'big update' direction: events, judgement, baskets.
Reuses the geometry/tokens of the first canvas (gen.py) and adds five artboards."""
import json, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_base.py"), encoding="utf-8").read()
exec(SRC.split("# ---------------------------------------------------------------- write")[0])  # tokens, geometry, helpers

T = LIGHT
ACC = "{{accent}}"

# ---------------------------------------------------------------- shared pieces
def nav2(crumbs=None, active="光模块", inbox=True):
    t = T
    crumb_html = ""
    if crumbs:
        parts = []
        for i, c in enumerate(crumbs):
            if i:
                parts.append(f'<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="{t["faint"]}" stroke-width="1.4"><path d="M4.5 2.5 8 6l-3.5 3.5"/></svg>')
            col = t["ink"] if i == len(crumbs) - 1 else t["muted"]
            parts.append(f'<span style="color:{col}">{c}</span>')
        crumb_html = f'<div style="display:flex;align-items:center;gap:10px;font-size:13px;color:{t["muted"]}">{"".join(parts)}</div>'
    def item(label):
        col = t["ink"] if label == active else t["muted"]
        w = "500" if label == active else "400"
        dot = f'<span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:{ACC};margin-left:6px;vertical-align:2px"></span>' if (label == "研究" and inbox) else ""
        return f'<span style="color:{col};font-weight:{w}">{label}{dot}</span>'
    sun = f'<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="{t["muted"]}" stroke-width="1.3" stroke-linecap="round"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.8M8 12.7v1.8M1.5 8h1.8M12.7 8h1.8M3.4 3.4l1.3 1.3M11.3 11.3l1.3 1.3M3.4 12.6l1.3-1.3M11.3 4.7l1.3-1.3"/></svg>'
    return f"""<header style="height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 80px">
  <div style="display:flex;align-items:center;gap:28px">
    <span style="font-weight:600;font-size:15px;letter-spacing:-0.01em;color:{t['ink']}">Teardown</span>
    {crumb_html}
  </div>
  <nav style="display:flex;align-items:center;gap:32px;font-size:14px">
    {item("光模块")}{item("公司")}{item("研究")}
    <span style="display:inline-flex;width:32px;height:32px;align-items:center;justify-content:center">{sun}</span>
  </nav>
</header>"""

def eyebrow(txt, accent=False):
    return f'<span style="font-family:{MONO};font-size:12px;letter-spacing:0.14em;text-transform:uppercase;color:{ACC if accent else T["muted"]}">{txt}</span>'

def rows_head(left, right=""):
    r = f'<span style="font-size:13px;color:{T["muted"]}">{right}</span>' if right and not right.startswith("<") else right
    return f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">{eyebrow(left)}{r}</div>'

def row(cols, cells, pad="14px 0"):
    return (f'<div style="display:grid;grid-template-columns:{cols};gap:20px;align-items:baseline;padding:{pad};border-top:1px solid {T["hair"]}">'
            + "".join(cells) + "</div>")

def rows_end():
    return f'<div style="border-top:1px solid {T["hair"]}"></div>'

def mono(txt, color=None, size=12):
    return f'<span style="font-family:{MONO};font-size:{size}px;color:{color or T["muted"]};letter-spacing:0.02em">{txt}</span>'

def title(txt, size=16):
    return f'<span style="font-size:{size}px;font-weight:500;color:{T["ink"]}">{txt}</span>'

def text(txt, size=13, color=None):
    return f'<span style="font-size:{size}px;color:{color or T["ink_2"] if False else color or T["ink2"]};line-height:1.5">{txt}</span>'

def link(txt, size=13):
    return f'<span style="font-size:{size}px;color:{ACC}">{txt}</span>'

def chev():
    return f'<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="{T["faint"]}" stroke-width="1.4" style="align-self:center;justify-self:end"><path d="M4.5 2.5 8 6l-3.5 3.5"/></svg>'

def wikilink(txt):
    return f'<span style="color:{ACC};border-bottom:1px solid color-mix(in srgb, {ACC} 35%, transparent)">{txt}</span>'

def footer(note):
    return f"""<footer style="padding:72px 80px 56px;display:flex;justify-content:space-between;align-items:flex-end;gap:40px">
  <p style="margin:0;font-size:12px;line-height:1.6;color:{T['muted']};max-width:720px">{note}</p>
  <span style="font-family:{MONO};font-size:11px;letter-spacing:0.1em;color:{T['faint']}">TEARDOWN · FROM PART TO POSITION</span>
</footer>"""

# sample data (marked 示例 on the canvas note)
EVENTS_PIC = [
    ("08-29", "中际旭创", "关于投资建设硅光芯片封测产线的公告", "扩产"),
    ("08-28", "Intel", "Integrated photonics 产品线路线图更新", "认证导入"),
    ("08-27", "源杰科技", "投资者关系活动记录:CW 激光器送样进展", "订单合同"),
    ("08-25", "Broadcom", "CPO 交换机平台出货节奏说明", "供需"),
]
CATEGORY_HINT = {"扩产": "供给侧动作;看资本开支与达产节奏", "订单合同": "需求兑现;看金额占营收比例", "认证导入": "进入客户体系的前置信号", "供需": "供给紧张或过剩的直接表述", "涨价": "供给紧的直接证据", "管制制裁": "外部约束"}

# ---------------------------------------------------------------- 1. overview
def overview2():
    svg, anchors = stack_svg(T)
    STACK_LEFT, STACK_TOP, LABEL_X = 300, 294, 872
    activity = {"pic": 3, "laser": 2, "board": 1}
    lines, labels = [], []
    for layer in LAYERS:
        ax, ay = anchors[layer["id"]]
        px, py = STACK_LEFT + ax, STACK_TOP + ay
        n = activity.get(layer["id"])
        dot_col = ACC if n else T["ink2"]
        lines.append(
            f'<div style="position:absolute;left:{px:.0f}px;top:{py:.0f}px;width:{LABEL_X - 20 - px:.0f}px;height:1px;background:{T["hair2"]}"></div>'
            f'<div style="position:absolute;left:{px - 3:.0f}px;top:{py - 3:.0f}px;width:7px;height:7px;border-radius:50%;background:{ACC if n else T["bg"]};border:1.5px solid {dot_col}"></div>')
        count = f'<span style="font-family:{MONO};font-size:11px;color:{ACC};letter-spacing:0.04em;margin-left:6px">· {n} 条事件</span>' if n else ""
        labels.append(f"""
    <div style="position:absolute;left:{LABEL_X}px;top:{py - 12:.0f}px;width:480px;display:flex;gap:18px;align-items:baseline">
      <span style="font-family:{MONO};font-size:12px;color:{ACC if n else T['muted']};letter-spacing:0.06em;width:22px;flex:none">{layer['idx']}</span>
      <div style="display:flex;flex-direction:column;gap:3px">
        <div style="display:flex;gap:10px;align-items:baseline">
          <span style="font-size:17px;font-weight:500;color:{T['ink']};letter-spacing:-0.005em">{layer['name']}</span>
          <span style="font-size:12px;color:{T['muted']}">{layer['en']}</span>{count}
        </div>
        <span style="font-size:13px;color:{T['ink2']};line-height:1.4">{layer['fn']}</span>
      </div>
    </div>""")
    changed = (f'<div style="display:flex;gap:22px;align-items:baseline;font-size:15px;color:{T["ink2"]};margin-top:4px">'
               f'<span style="font-family:{MONO};font-size:12px;letter-spacing:0.12em;color:{T["muted"]}">过去 7 天</span>'
               f'{link("6 条卡口事件", 15)}<span style="color:{T["faint"]}">·</span>{link("2 条待核验", 15)}<span style="color:{T["faint"]}">·</span>{link("1 个未决问题", 15)}'
               f'<span style="color:{T["faint"]}">·</span><span style="color:{T["muted"]};font-size:13px">最近一条 08-29 中际旭创 · 扩产</span></div>')
    hero = f"""
<section style="position:relative;height:1070px">
  <div style="position:absolute;left:80px;top:56px;display:flex;flex-direction:column;gap:18px;width:820px">
    {eyebrow("CO-PACKAGED OPTICS · 1.6T / 3.2T")}
    <h1 style="margin:0;font-size:68px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">CPO 光模块</h1>
    <p style="margin:6px 0 0;font-size:19px;line-height:1.55;color:{T['ink2']};font-weight:300;max-width:600px;text-wrap:pretty">九层结构,从散热上盖到高速主板。点击任意一层,看它由什么构成、谁在做、最近发生了什么。</p>
    {changed}
  </div>
  <div style="position:absolute;left:{STACK_LEFT}px;top:{STACK_TOP}px">{svg}</div>
  {''.join(lines)}
  {''.join(labels)}
</section>"""
    body = nav2() + hero
    return wrap(T, body, height=1134)

# ---------------------------------------------------------------- 2. selected layer (with events + judgement)
def selected2():
    sel = "pic"
    svg, anchors = stack_svg(T, selected=sel, transform="scale(0.92)")
    STACK_LEFT, STACK_TOP, CONTENT_X = 120, 150, 820
    ax, ay = anchors[sel]; ax, ay = ax * 0.92, ay * 0.92
    px, py = STACK_LEFT + ax, STACK_TOP + ay
    kx, ky = CONTENT_X - 30, 96 + 8
    leader = (f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1440" height="1200" viewBox="0 0 1440 1200" fill="none">'
              f'<path d="M{px:.0f} {py:.0f} H{kx} V{ky}" stroke="{ACC}" stroke-width="1" opacity="0.55"/>'
              f'<circle cx="{px:.0f}" cy="{py:.0f}" r="3.5" fill="{ACC}"/><circle cx="{kx}" cy="{ky}" r="2.5" fill="{ACC}"/></svg>')

    judgement = f"""
  <div style="display:flex;flex-direction:column;gap:12px">
    {rows_head("我的判断 · 更新于 08-30", link("编辑"))}
    <p style="margin:0;font-size:16px;line-height:1.7;color:{T['ink']};font-weight:400;text-wrap:pretty">硅光环节的瓶颈不在 PIC 设计,而在耦合与测试良率;国内厂商在 PIC 代工上仍依赖外部 fab。关注 {wikilink("源杰科技")} 的 CW 激光器送样进展,以及 {wikilink("光纤阵列")} 环节的耦合方案会不会改变对 PIC 端面工艺的要求。</p>
    <div style="display:flex;flex-direction:column;margin-top:6px">
      {row("28px minmax(0,1fr) 90px 60px", [mono("Q1"), text("1.6T 世代硅光 PIC 的国产代工份额是多少?", 14, T["ink"]), mono("待验证"), mono("08-30")], "10px 0")}
      {row("28px minmax(0,1fr) 90px 60px", [mono("Q2"), text("外置光源架构对激光器颗数需求的影响方向?", 14, T["ink"]), mono("待验证"), mono("08-26")], "10px 0")}
      {rows_end()}
    </div>
    {link("+ 新问题")}
  </div>"""

    ev_rows = "".join(row("48px 90px minmax(0,1fr) 72px", [mono(d), text(c, 13, T["ink"]), text(tt, 13), mono(cat, ACC)], "11px 0") for d, c, tt, cat in EVENTS_PIC)
    events = f"""
  <div style="display:flex;flex-direction:column">
    {rows_head("最近事件 · 7 天 · 4 条", link("全部事件 →"))}
    {ev_rows}{rows_end()}
    <span style="font-size:12px;color:{T['muted']};margin-top:8px">类别来自卡口事件分类:扩产 / 订单合同 / 认证导入 / 供需 / 涨价 / 管制制裁。</span>
  </div>"""

    parts = "".join(row("28px 200px minmax(0,1fr) 16px", [mono(i), title(n), text(f), chev()], "12px 0") for i, n, f in PIC_PARTS)
    cos = "".join(row("150px 130px 70px minmax(0,1fr)", [title(n), mono(t, size=11), text("行业图示", 12), mono(last, T["muted"], 11)], "12px 0")
                  for (n, t, role), last in zip(PIC_COMPANIES, ["08-28 认证导入", "08-25 供需", "08-29 扩产", "08-27 订单合同"]))

    content = f"""
<div style="position:absolute;left:{CONTENT_X}px;top:96px;width:540px;display:flex;flex-direction:column;gap:44px">
  <div style="display:flex;flex-direction:column;gap:14px">
    {eyebrow("04 / 09 · SIPH-PIC", accent=True)}
    <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">硅光芯片</h1>
    <span style="font-size:15px;color:{T['muted']}">Silicon photonics PIC · 硅光环节 · {link("篮子 →", 15)}</span>
    <p style="margin:10px 0 0;font-size:17px;line-height:1.6;color:{T['ink2']};font-weight:300;text-wrap:pretty">把电信号调制到光载波、按波长复用,并通过片上波导把光耦合进出光纤。它是 CPO 的光学核心,对应产业链中的硅光环节。</p>
  </div>
  {judgement}
  {events}
  <div style="display:flex;flex-direction:column">{rows_head("部件 · 3", "点击进入下一层")}{parts}{rows_end()}</div>
  <div style="display:flex;flex-direction:column">{rows_head("公司 · 硅光环节 · 4", link("查看该环节全部公司 →"))}{cos}{rows_end()}</div>
</div>"""
    hint = f"""<div style="position:absolute;left:80px;top:1010px;display:flex;align-items:center;gap:14px;font-size:12px;color:{T['muted']}"><span style="font-family:{MONO};font-size:11px;letter-spacing:0.08em;padding:3px 6px;border:1px solid {T['hair2']};border-radius:4px">ESC</span><span>或点击空白处回到整机</span></div>"""
    body = nav2(["CPO 光模块", "硅光芯片"]) + f"""
<section style="position:relative;height:1560px">
  <div style="position:absolute;left:{STACK_LEFT}px;top:{STACK_TOP}px">{svg}</div>
  {leader}{content}{hint}
</section>"""
    return wrap(T, body, height=1624)

# ---------------------------------------------------------------- 3. company page with price strip + timeline
def price_strip(w=760, h=180, events=((0.36, "认证导入"), (0.62, "订单合同"), (0.88, "扩产"))):
    # a calm single series; sample shape
    import random
    random.seed(7)
    pts_ = []
    v = 100.0
    n = 130
    for i in range(n):
        v += random.uniform(-1.6, 1.9) + (0.12 if i > 80 else 0)
        pts_.append(v)
    lo, hi = min(pts_), max(pts_)
    def X(i): return 40 + i * (w - 60) / (n - 1)
    def Y(val): return 16 + (hi - val) / (hi - lo) * (h - 48)
    d = "M" + " L".join(f"{X(i):.1f},{Y(p):.1f}" for i, p in enumerate(pts_))
    grid = "".join(f'<line x1="40" x2="{w-20}" y1="{16 + k*(h-48)/2:.1f}" y2="{16 + k*(h-48)/2:.1f}" stroke="{T["hair"]}" stroke-width="1"/>' for k in range(3))
    months = ["3月", "4月", "5月", "6月", "7月", "8月"]
    xl = "".join(f'<text x="{40 + k*(w-60)/5:.1f}" y="{h-6}" font-family="{MONO_ATTR[1:-1]}" font-size="11" fill="{T["muted"]}" text-anchor="middle">{m}</text>' for k, m in enumerate(months))
    marks = ""
    for fx, cat in events:
        i = int(fx * (n - 1)); x, y = X(i), Y(pts_[i])
        marks += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{ACC}" stroke="{T["bg"]}" stroke-width="2"/>'
                  f'<text x="{x:.1f}" y="{y-12:.1f}" font-family="{MONO_ATTR[1:-1]}" font-size="11" fill="{ACC}" text-anchor="middle" letter-spacing="0.06em">{cat}</text>')
    last = pts_[-1]
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block;overflow:visible">{grid}'
            f'<path d="{d}" fill="none" stroke="{T["ink2"]}" stroke-width="2" stroke-linejoin="round"/>{marks}{xl}'
            f'<text x="{w-16}" y="{Y(last)+4:.1f}" font-family="{MONO_ATTR[1:-1]}" font-size="12" fill="{T["ink"]}">{last:.0f}</text></svg>')

def company2():
    left = f"""
<div style="display:flex;flex-direction:column;gap:48px">
  <header style="display:flex;flex-direction:column;gap:14px">
    {eyebrow("300308 · 深交所")}
    <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">中际旭创</h1>
    <span style="font-size:15px;color:{T['muted']}">中际旭创股份有限公司 · 硅光芯片 / 光引擎与封装</span>
    <p style="margin:6px 0 0;font-size:17px;line-height:1.6;color:{T['ink2']};font-weight:300;text-wrap:pretty">在 CPO 产业链的 2 个环节被提及,证据级均为行业图示,有 1 条升级建议待你核验。过去 30 天 3 条卡口事件,最近一条 08-29 扩产。</p>
  </header>

  <div style="display:flex;flex-direction:column;gap:10px">
    {rows_head("价格 · 6 个月 · 指数化 = 100 · 示例数据", '<span style="font-size:13px;color:' + T['muted'] + '">圆点为卡口事件</span>')}
    {price_strip()}
    <div style="display:flex;gap:28px;font-size:13px;color:{T['ink2']};margin-top:6px">
      <span>{mono("PE TTM")} 28.4</span><span>{mono("5 年分位")} 35%</span><span>{mono("3M")} +12.6%</span><span>{mono("相对篮子")} +4.1%</span><span style="color:{T['muted']}">示例</span>
    </div>
  </div>

  <div style="display:flex;flex-direction:column">
    {rows_head("卡口事件 · 30 天 · 3 条", link("全部公告与新闻 →"))}
    {row("48px 60px minmax(0,1fr) 72px", [mono("08-29"), mono("公告"), text("关于投资建设硅光芯片封测产线的公告", 14, T["ink"]), mono("扩产", ACC)], "12px 0")}
    {row("48px 60px minmax(0,1fr) 72px", [mono("08-21"), mono("新闻"), text("1.6T 光模块批量出货节奏(媒体报道,需回到公告核验)", 14, T["ink"]), mono("供需", ACC)], "12px 0")}
    {row("48px 60px minmax(0,1fr) 72px", [mono("08-12"), mono("互动易"), text("回复投资者:硅光方案在 800G 产品中的占比持续提升", 14, T["ink"]), mono("认证导入", ACC)], "12px 0")}
    {rows_end()}
  </div>

  <div style="display:flex;flex-direction:column;gap:12px">
    {rows_head("我的判断 · 更新于 08-30", link("编辑"))}
    <p style="margin:0;font-size:16px;line-height:1.7;color:{T['ink']};text-wrap:pretty">硅光方案渗透率是它在这个环节的核心变量;封测产线是往上游走的信号,但产能兑现要看 2027 年。与 {wikilink("硅光芯片")} 层的判断一致。</p>
    <div style="display:flex;flex-direction:column">
      {row("28px minmax(0,1fr) 90px 60px", [mono("Q3"), text("封测产线投产后硅光 PIC 是否自供?", 14, T["ink"]), mono("待验证"), mono("08-30")], "10px 0")}
      {rows_end()}
    </div>
  </div>

  <div style="display:flex;flex-direction:column">
    {rows_head("在产业链中的位置 · 2")}
    {row("200px 130px minmax(0,1fr)", [title("硅光芯片"), text("行业图示"), text("公开行业图示将其列为该环节代表企业。")], "12px 0")}
    {row("200px 130px minmax(0,1fr)", [title("光引擎 / 封装"), text("行业图示"), text("公开行业图示将其列为该环节代表企业。")], "12px 0")}
    {rows_end()}
  </div>
</div>"""
    aside = f"""
<aside style="display:flex;flex-direction:column;gap:32px;padding-top:8px">
  <dl style="display:grid;grid-template-columns:96px minmax(0,1fr);gap:10px 16px;font-size:14px;margin:0">
    <dt style="color:{T['muted']}">市场</dt><dd style="margin:0;color:{T['ink']}">300308 · 深交所</dd>
    <dt style="color:{T['muted']}">地区</dt><dd style="margin:0;color:{T['ink']}">中国</dd>
    <dt style="color:{T['muted']}">覆盖层</dt><dd style="margin:0;color:{T['ink']}">A 股重点</dd>
    <dt style="color:{T['muted']}">在整机中</dt><dd style="margin:0;color:{T['ink']}">{link("04 硅光芯片", 14)} · {link("03 电处理层", 14)}</dd>
  </dl>
  <div style="display:flex;flex-direction:column;gap:10px">
    {eyebrow("待核验 · 1")}
    <div style="display:flex;flex-direction:column;gap:8px;padding:12px 0;border-top:1px solid {T['hair']};border-bottom:1px solid {T['hair']}">
      <span style="font-size:14px;color:{T['ink']}">硅光芯片环节 · 行业图示 → 候选</span>
      <span style="font-size:13px;color:{T['ink2']}">08-29 公告提到硅光芯片封测产线,可作为来源升级这条关系。</span>
      <div style="display:flex;gap:18px;margin-top:4px">{link("以此公告升级为候选")}<span style="font-size:13px;color:{T['muted']}">忽略</span></div>
    </div>
  </div>
  <p style="margin:0;font-size:12px;line-height:1.6;color:{T['muted']}">证据级:已核验 有经人工审核的证据;候选 有来源但未审核;行业图示 仅见于公开产业链示意图。</p>
</aside>"""
    body = nav2(["公司", "中际旭创"], active="公司") + f"""
<main style="max-width:1440px;margin:0 auto;padding:56px 80px 0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:96px;align-items:start">
  {left}{aside}
</main>""" + footer("价格、估值与事件为样式示例;接入公告、新闻与行情源后替换为真实数据,并保留每条事件的原文链接。")
    return wrap(T, body, height=1380)

# ---------------------------------------------------------------- 4. research inbox
def inbox2():
    t = T
    def q(i, qtext, obj, status, date):
        return row("28px minmax(0,1fr) 150px 80px 60px", [mono(i), text(qtext, 15, t["ink"]), link(obj, 13), mono(status), mono(date)], "13px 0")
    open_q = "".join([
        q("Q1", "1.6T 世代硅光 PIC 的国产代工份额是多少?", "硅光芯片", "待验证", "08-30"),
        q("Q3", "封测产线投产后硅光 PIC 是否自供?", "中际旭创", "待验证", "08-30"),
        q("Q2", "外置光源架构对激光器颗数需求的影响方向?", "激光器阵列", "待验证", "08-26"),
    ])
    pend = "".join([
        row("minmax(0,1fr) 130px 200px", [text("中际旭创 → 硅光芯片 · 08-29 公告提到硅光芯片封测产线", 14, t["ink"]), mono("行业图示 → 候选"), f'<span style="display:flex;gap:16px">{link("升级")}<span style="font-size:13px;color:{t["muted"]}">忽略</span></span>'], "12px 0"),
        row("minmax(0,1fr) 130px 200px", [text("Broadcom → 交换 ASIC · 官网交换产品线(既有候选)", 14, t["ink"]), mono("候选 → 已核验"), f'<span style="display:flex;gap:16px">{link("审核")}<span style="font-size:13px;color:{t["muted"]}">驳回</span></span>'], "12px 0"),
    ])
    def ev(d, obj, kind, tt, cat):
        return row("48px 110px 56px minmax(0,1fr) 72px", [mono(d), link(obj, 13), mono(kind), text(tt, 14, t["ink"]), mono(cat, ACC)], "11px 0")
    events = "".join([
        ev("08-29", "中际旭创", "公告", "关于投资建设硅光芯片封测产线的公告", "扩产"),
        ev("08-29", "高速主板", "新闻", "高层数 PCB 涨价函流传(需回到公告核验)", "涨价"),
        ev("08-28", "Intel", "新闻", "Integrated photonics 产品线路线图更新", "认证导入"),
        ev("08-27", "源杰科技", "互动易", "CW 激光器送样进展", "订单合同"),
        ev("08-26", "长光华芯", "公告", "关于股份回购进展的公告", "—"),
        ev("08-25", "Broadcom", "新闻", "CPO 交换机平台出货节奏说明", "供需"),
    ])
    notes = "".join([
        row("110px minmax(0,1fr) 60px", [link("硅光芯片", 13), text("硅光环节的瓶颈不在 PIC 设计,而在耦合与测试良率……", 14), mono("08-30")], "11px 0"),
        row("110px minmax(0,1fr) 60px", [link("中际旭创", 13), text("硅光方案渗透率是它在这个环节的核心变量……", 14), mono("08-30")], "11px 0"),
        row("110px minmax(0,1fr) 60px", [link("激光器阵列", 13), text("外置光源是可维护性与成本的权衡,不是技术路线之争……", 14), mono("08-24")], "11px 0"),
    ])
    rail_layers = [("01", "散热与上盖", 0), ("02", "交换 ASIC", 1), ("03", "电处理层", 0), ("04", "硅光芯片", 3), ("05", "激光器阵列", 2), ("06", "光电探测阵列", 0), ("07", "光纤阵列", 0), ("08", "共封装基板", 0), ("09", "高速主板", 1)]
    rail = "".join(
        f'<div style="display:grid;grid-template-columns:28px minmax(0,1fr) 40px;gap:12px;align-items:baseline;padding:9px 0;border-top:1px solid {t["hair"]}">'
        f'{mono(i, ACC if n else t["muted"])}<span style="font-size:14px;color:{t["ink"] if n else t["ink2"]}">{nm}</span>'
        f'<span style="font-family:{MONO};font-size:12px;color:{ACC if n else t["faint"]};text-align:right">{n if n else "—"}</span></div>'
        for i, nm, n in rail_layers)
    body = nav2(["研究"], active="研究") + f"""
<main style="max-width:1440px;margin:0 auto;padding:56px 80px 0;display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:96px;align-items:start">
  <div style="display:flex;flex-direction:column;gap:52px">
    <header style="display:flex;flex-direction:column;gap:14px">
      {eyebrow("Research · this week")}
      <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{t['ink']}">研究</h1>
      <p style="margin:6px 0 0;font-size:17px;line-height:1.6;color:{t['ink2']};font-weight:300">本周 6 条卡口事件、2 条待核验、3 个未决问题。先处理待核验,再看事件,笔记随手写。</p>
    </header>
    <div style="display:flex;flex-direction:column">{rows_head("未决问题 · 3", link("+ 新问题"))}{open_q}{rows_end()}</div>
    <div style="display:flex;flex-direction:column">{rows_head("待核验 · 2")}{pend}{rows_end()}</div>
    <div style="display:flex;flex-direction:column">{rows_head("卡口事件 · 7 天 · 6 条", link("全部 →"))}{events}{rows_end()}</div>
    <div style="display:flex;flex-direction:column">{rows_head("最近笔记 · 3")}{notes}{rows_end()}</div>
  </div>
  <aside style="display:flex;flex-direction:column;gap:14px;padding-top:120px">
    {eyebrow("整机 · 本周事件")}
    <div style="display:flex;flex-direction:column">{rail}{rows_end()}</div>
    <span style="font-size:12px;color:{t['muted']};line-height:1.6">点层回到整机对应位置。笔记以 Markdown 文件保存在仓库 data/notes/,可直接用 Obsidian 打开。</span>
  </aside>
</main>""" + footer("事件为样式示例。")
    return wrap(T, body, height=1400)

# ---------------------------------------------------------------- 5. chain basket
def basket_chart(w=1280, h=300):
    import random
    random.seed(11)
    n = 130
    a, b = [100.0], [100.0]
    for i in range(1, n):
        a.append(a[-1] + random.uniform(-1.5, 1.8) + (0.15 if i > 70 else 0.02))
        b.append(b[-1] + random.uniform(-1.1, 1.2))
    lo, hi = min(a + b) - 2, max(a + b) + 2
    def X(i): return 40 + i * (w - 120) / (n - 1)
    def Y(v): return 14 + (hi - v) / (hi - lo) * (h - 50)
    def path(s): return "M" + " L".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(s))
    grid = "".join(f'<line x1="40" x2="{w-80}" y1="{14 + k*(h-50)/3:.1f}" y2="{14 + k*(h-50)/3:.1f}" stroke="{T["hair"]}" stroke-width="1"/>' for k in range(4))
    ylab = "".join(f'<text x="30" y="{14 + k*(h-50)/3 + 4:.1f}" font-family="{MONO_ATTR[1:-1]}" font-size="11" fill="{T["muted"]}" text-anchor="end">{hi - k*(hi-lo)/3:.0f}</text>' for k in range(4))
    months = ["3月", "4月", "5月", "6月", "7月", "8月"]
    xl = "".join(f'<text x="{40 + k*(w-120)/5:.1f}" y="{h-8}" font-family="{MONO_ATTR[1:-1]}" font-size="11" fill="{T["muted"]}" text-anchor="middle">{m}</text>' for k, m in enumerate(months))
    marks = ""
    for fx, cat in ((0.55, "认证导入"), (0.74, "订单合同"), (0.97, "扩产")):
        i = int(fx * (n - 1)); x, y = X(i), Y(a[i])
        marks += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{ACC}" stroke="{T["bg"]}" stroke-width="2"/><text x="{x:.1f}" y="{y-12:.1f}" font-family="{MONO_ATTR[1:-1]}" font-size="11" fill="{ACC}" text-anchor="middle" letter-spacing="0.06em">{cat}</text>'
    lab = (f'<text x="{X(n-1)+10:.1f}" y="{Y(a[-1])+4:.1f}" font-size="13" font-weight="500" fill="{T["ink"]}">硅光芯片篮子 {a[-1]:.0f}</text>'
           f'<text x="{X(n-1)+10:.1f}" y="{Y(b[-1])+4:.1f}" font-size="13" fill="{T["muted"]}">整机篮子 {b[-1]:.0f}</text>')
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block;overflow:visible">{grid}{ylab}'
            f'<path d="{path(b)}" fill="none" stroke="{T["faint"]}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="{path(a)}" fill="none" stroke="{ACC}" stroke-width="2" stroke-linejoin="round"/>{marks}{lab}{xl}</svg>')

def basket2():
    t = T
    legend = (f'<div style="display:flex;gap:22px;font-size:13px;color:{t["ink2"]};align-items:center">'
              f'<span style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:2px;background:{ACC};display:inline-block"></span>硅光芯片篮子 · 4 家 · 等权</span>'
              f'<span style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:2px;background:{t["faint"]};display:inline-block"></span>整机篮子 · 32 家 · 等权</span>'
              f'<span style="color:{t["muted"]}">指数化 = 100 · 各自本币 · 示例数据</span></div>')
    hdr = row("170px 150px 70px 70px 90px minmax(0,1fr) 90px", [mono("公司"), mono("市场"), mono("3M"), mono("6M"), mono("估值分位"), mono("最近卡口事件"), mono("证据级")], "8px 0")
    def r(n, m, m3, m6, pct, ev, lvl):
        return row("170px 150px 70px 70px 90px minmax(0,1fr) 90px", [title(n), mono(m), text(m3, 14, t["ink"]), text(m6, 14, t["ink"]), text(pct, 14), text(ev, 13), text(lvl, 13)], "13px 0")
    table = hdr + "".join([
        r("中际旭创", "300308 · 深交所", "+12.6%", "+31.2%", "35%", "08-29 扩产", "行业图示"),
        r("源杰科技", "688498 · 上交所", "+8.1%", "+19.4%", "62%", "08-27 订单合同", "行业图示"),
        r("Intel", "INTC · NASDAQ", "−3.4%", "+2.0%", "18%", "08-28 认证导入", "行业图示"),
        r("Broadcom", "AVGO · NASDAQ", "+6.9%", "+24.8%", "88%", "08-25 供需", "候选 · 待核验"),
    ]) + rows_end()
    others = "".join(row("40px 220px 70px minmax(0,1fr)", [mono(i), title(n, 15), text(v, 14, t["ink"]), text(k, 13)], "10px 0") for i, n, v, k in [
        ("04", "光源 / 激光器", "+15.2%", "3 家 · 最近 08-27 订单合同"), ("02", "交换芯片 / ASIC", "+9.8%", "3 家 · 最近 08-25 供需"), ("06", "基板与互连", "+7.4%", "3 家 · 最近 08-29 涨价"), ("07", "散热与结构件", "+4.1%", "3 家 · —")])
    body = nav2(["公司", "硅光芯片", "篮子"], active="公司") + f"""
<main style="max-width:1440px;margin:0 auto;padding:56px 80px 0;display:flex;flex-direction:column;gap:48px">
  <header style="display:flex;flex-direction:column;gap:14px;max-width:760px">
    {eyebrow("Basket · 03 / 10 · 硅光芯片")}
    <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{t['ink']}">硅光芯片篮子</h1>
    <p style="margin:6px 0 0;font-size:17px;line-height:1.6;color:{t['ink2']};font-weight:300;text-wrap:pretty">这一环节的 4 家公司等权组成一个篮子,与整机全部公司的篮子比较;卡口事件标在篮子曲线上。它不是投资建议,是把“环节”变成一条可以观察的线。</p>
  </header>
  <div style="display:flex;flex-direction:column;gap:14px">{legend}{basket_chart()}</div>
  <div style="display:flex;flex-direction:column">{rows_head("成分 · 4 家", link("编辑权重"))}{table}</div>
  <div style="display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:96px;align-items:start">
    <div style="display:flex;flex-direction:column">{rows_head("其他环节 · 3M · 示例", link("全部环节 →"))}{others}{rows_end()}</div>
    <p style="margin:0;font-size:13px;line-height:1.7;color:{t['ink2']}">篮子只回答一个问题:这一环节作为整体,相对整机在走强还是走弱,拐点是否和卡口事件对得上。跨市场成分按各自本币指数化,不做汇率换算;权重默认等权,可手动调整并记录理由。</p>
  </div>
</main>""" + footer("行情为样式示例;接入免费行情源(A 股:腾讯/新浪;美股:Yahoo)后替换。")
    return wrap(T, body, height=1360)

# ---------------------------------------------------------------- write
files = {
    "Main.dc.html": overview2(),
    "Selected.dc.html": selected2(),
    "Company.dc.html": company2(),
    "Inbox.dc.html": inbox2(),
    "Basket.dc.html": basket2(),
}
for name, html in files.items():
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(html)

canvas = {
    "artboards": [
        {"file": "Main.dc.html", "title": "1 · 总览:什么变了", "x": 0, "y": 0, "w": 1440, "h": 1134},
        {"file": "Selected.dc.html", "title": "2 · 选中一层:事件 + 判断", "x": 1560, "y": 0, "w": 1440, "h": 1624},
        {"file": "Company.dc.html", "title": "3 · 公司:价格 + 事件 + 证据升级", "x": 0, "y": 1780, "w": 1440, "h": 1380},
        {"file": "Inbox.dc.html", "title": "4 · 研究:收件箱", "x": 1560, "y": 1780, "w": 1440, "h": 1400},
        {"file": "Basket.dc.html", "title": "5 · 环节篮子", "x": 0, "y": 3340, "w": 1440, "h": 1360},
    ],
    "annotations": [
        {"id": "brief", "x": 0, "y": -300, "w": 560,
         "text": "Teardown · 大更新方向稿\n\n三层叠在原有结构上:\n· 事件(什么变了):卡口事件分类 —— 扩产 / 订单合同 / 认证导入 / 供需 / 涨价 / 管制制裁\n· 判断(我怎么想):挂在对象上的笔记与未决问题,Markdown + [[双链]],文件存 data/notes/\n· 量化(篮子):每个环节一个等权组合,与整机篮子比较,事件标在线上\n\n所有事件、价格、估值均为样式示例,不是数据。"},
        {"id": "read-order", "x": 1560, "y": 1660, "w": 440,
         "text": "看什么\n1. 总览多的那一行和层上的点,够不够“知道该干什么”?\n2. 选中一层后,“我的判断”放在事件之前对不对?\n3. 公司页的价格带:要不要,以及事件标在线上是否有用?\n4. 收件箱是不是你每天想打开的那一页?\n5. 篮子页:等权 + 和整机比,这个定义能接受吗?"},
    ],
    "launch": {"view": "canvas"},
}
with open(os.path.join(HERE, "canvas.json"), "w", encoding="utf-8") as f:
    json.dump(canvas, f, ensure_ascii=False, indent=2)
print("ok", list(files))
