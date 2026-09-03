# -*- coding: utf-8 -*-
"""Teardown — v3: conclusion-first sections, a semantic signal colour axis
(利多 / 利空 / 中性, A-share convention red-up), every reading time-stamped
with an as-of date and a horizon, and light + dark variants of all pages."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
G2 = open(os.path.join(HERE, "gen_helpers.py"), encoding="utf-8").read()
exec(G2.rsplit("# ---------------------------------------------------------------- write", 1)[0])  # helpers + charts (+gen.py)

# ---- signal axis: direction of capital, not decoration ---------------------
SIGNALS = {
    "light": {"pos": "#C0392B", "neg": "#2E7D5B", "neu": "#8A8E96"},
    "dark":  {"pos": "#F07A6A", "neg": "#5DC391", "neu": "#7E8189"},
}
SIG = SIGNALS["light"]
THEME_NAME = "light"

def set_theme(name):
    global T, SIG, THEME_NAME
    T = LIGHT if name == "light" else DARK
    SIG = SIGNALS[name]
    THEME_NAME = name

BREATHE = """
    @keyframes td-breathe { 0%,100% { opacity: .45; transform: scale(1); } 50% { opacity: 1; transform: scale(1.3); } }
    .td-live { animation: td-breathe 2.6s ease-in-out infinite; transform-origin: center; }
    .td-live-ring { position:absolute; width:7px; height:7px; border-radius:50%; animation: td-ring 2.6s ease-out infinite; }
    @keyframes td-ring { 0% { box-shadow: 0 0 0 0 color-mix(in srgb, %ACC% 45%, transparent); } 70% { box-shadow: 0 0 0 9px color-mix(in srgb, %ACC% 0%, transparent); } 100% { box-shadow: 0 0 0 9px transparent; } }
    @media (prefers-reduced-motion: reduce) { .td-live, .td-live-ring { animation: none; } }
"""

def wrap2(body, height):
    html = wrap(T, body, height=height)
    return html.replace("  </style>\n</helmet>", BREATHE.replace("%ACC%", ACC) + "  </style>\n</helmet>", 1)

# ---- semantic primitives -----------------------------------------------------
GLYPH = {"pos": "▲", "neg": "▼", "neu": "●"}
LABEL = {"pos": "偏多", "neg": "偏空", "neu": "中性"}

def sig(v, size=14, weight=500):
    """a signed number coloured by direction; '+' = red (A股), '−' = green"""
    s = str(v)
    d = "pos" if s.startswith("+") else "neg" if s.startswith("−") or s.startswith("-") else "neu"
    return f'<span style="font-family:{MONO};font-size:{size}px;font-weight:{weight};color:{SIG[d]};font-variant-numeric:tabular-nums">{s}</span>'

def tag(d, txt=None, size=12):
    return f'<span style="font-family:{MONO};font-size:{size}px;letter-spacing:0.06em;color:{SIG[d]};white-space:nowrap">{GLYPH[d]} {txt or LABEL[d]}</span>'

def inline(*parts, size=14, color=None):
    """one grid cell made of several inline fragments (text + coloured numbers)"""
    return f'<span style="font-size:{size}px;line-height:1.6;color:{color or T["ink2"]}">{"".join(parts)}</span>'

def conclusion(d, txt, size=15):
    """first line of every analytic section: direction first, sentence second"""
    return (f'<div style="display:flex;gap:14px;align-items:baseline;padding:2px 0 4px">'
            f'<span style="font-family:{MONO};font-size:12px;letter-spacing:0.08em;color:{SIG[d]};flex:none;min-width:52px">{GLYPH[d]} {LABEL[d]}</span>'
            f'<span style="font-size:{size}px;line-height:1.55;color:{T["ink"]}">{txt}</span></div>')

def asof(date="08-30 收盘", horizon=None, extra=None):
    bits = [f"截至 {date}"]
    if horizon: bits.append(f"窗口 {horizon}")
    if extra: bits.append(extra)
    return f'<span style="font-family:{MONO};font-size:11px;letter-spacing:0.04em;color:{T["muted"]}">{" · ".join(bits)}</span>'

def head(left, right_html=""):
    return f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">{eyebrow(left)}{right_html}</div>'

def kv(pairs, size=14):
    parts = []
    for k, v, d in pairs:
        col = SIG[d] if d else T["ink"]
        parts.append(f'<span style="display:inline-flex;gap:8px;align-items:baseline">{mono(k)}<span style="font-family:{MONO};font-size:{size}px;color:{col};font-variant-numeric:tabular-nums">{v}</span></span>')
    return f'<div style="display:flex;flex-wrap:wrap;gap:8px 26px;align-items:baseline">{"".join(parts)}</div>'

def freshness(state):
    """时效 for an event: 窗口内 / 已定价 / 过期"""
    d = {"窗口内": "pos", "已定价": "neu", "过期": "neu", "未反应": "neu"}.get(state.split(" ")[0], "neu")
    col = T["ink2"] if state.startswith("窗口内") else T["muted"]
    return f'<span style="font-family:{MONO};font-size:11px;color:{col}">{state}</span>'

# ---------------------------------------------------------------- 1. overview
def overview4():
    svg, anchors = stack_svg(T)
    STACK_LEFT, STACK_TOP, LABEL_X = 300, 400, 872
    activity = {"pic": (4, "+2.4%", "pos"), "laser": (2, "+1.1%", "pos"), "board": (1, "−0.6%", "neg")}
    lines, labels = [], []
    for layer in LAYERS:
        ax, ay = anchors[layer["id"]]
        px, py = STACK_LEFT + ax, STACK_TOP + ay
        act = activity.get(layer["id"])
        lines.append(f'<div style="position:absolute;left:{px:.0f}px;top:{py:.0f}px;width:{LABEL_X - 20 - px:.0f}px;height:1px;background:{T["hair2"]}"></div>')
        if act:
            col = SIG[act[2]]
            lines.append(f'<div class="td-live-ring" style="left:{px - 3:.0f}px;top:{py - 3:.0f}px;background:{col}"></div>'
                         f'<div class="td-live" style="position:absolute;left:{px - 3:.0f}px;top:{py - 3:.0f}px;width:7px;height:7px;border-radius:50%;background:{col}"></div>')
        else:
            lines.append(f'<div style="position:absolute;left:{px - 3:.0f}px;top:{py - 3:.0f}px;width:7px;height:7px;border-radius:50%;background:{T["bg"]};border:1.5px solid {T["ink2"]}"></div>')
        tail = (f'<span style="font-family:{MONO};font-size:11px;color:{T["muted"]};letter-spacing:0.04em;margin-left:6px">· {act[0]} 条事件 · 篮子 7 天</span> {sig(act[1], 12)}' if act else "")
        labels.append(f"""
    <div style="position:absolute;left:{LABEL_X}px;top:{py - 12:.0f}px;width:480px;display:flex;gap:18px;align-items:baseline">
      <span style="font-family:{MONO};font-size:12px;color:{SIG[act[2]] if act else T['muted']};letter-spacing:0.06em;width:22px;flex:none">{layer['idx']}</span>
      <div style="display:flex;flex-direction:column;gap:3px">
        <div style="display:flex;gap:10px;align-items:baseline">
          <span style="font-size:17px;font-weight:500;color:{T['ink']};letter-spacing:-0.005em">{layer['name']}</span>
          <span style="font-size:12px;color:{T['muted']}">{layer['en']}</span>{tail}
        </div>
        <span style="font-size:13px;color:{T['ink2']};line-height:1.4">{layer['fn']}</span>
      </div>
    </div>""")
    changed = f"""
    <div style="display:flex;flex-direction:column;gap:10px;margin-top:8px">
      {conclusion("pos", f"资金本周在给 <span style='font-weight:500'>硅光芯片</span> 投票:08-29 扩产后环节内 3/4 同向,篮子 T+1 超额 {sig('+1.9%', 15)},上游光纤阵列跟随 {sig('+1.2%', 15)};高速主板的涨价传闻未被买入 {sig('−0.6%', 15)}。", 16)}
      <div style="display:flex;gap:22px;align-items:baseline;font-size:14px;color:{T['ink2']}">
        {asof("08-30 收盘", "过去 7 天", "反应 = T+1 相对篮子")}
        {link("6 条卡口事件", 14)}<span style="color:{T['faint']}">·</span><span>已反应 <span style="color:{T['ink']}">4</span> · 未反应 <span style="color:{T['ink']}">2</span></span>
        <span style="color:{T['faint']}">·</span>{link("2 条待核验", 14)}<span style="color:{T['faint']}">·</span>{link("1 个判断到期", 14)}
      </div>
    </div>"""
    hero = f"""
<section style="position:relative;height:1100px">
  <div style="position:absolute;left:80px;top:56px;display:flex;flex-direction:column;gap:18px;width:960px">
    {eyebrow("CO-PACKAGED OPTICS · 1.6T / 3.2T")}
    <h1 style="margin:0;font-size:68px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">CPO 光模块</h1>
    <p style="margin:6px 0 0;font-size:19px;line-height:1.55;color:{T['ink2']};font-weight:300;max-width:600px;text-wrap:pretty">九个模块,从散热上盖到高速主板。点击任意一个,看它由什么构成、谁在做、资金最近在给谁投票。</p>
    {changed}
  </div>
  <div style="position:absolute;left:{STACK_LEFT}px;top:{STACK_TOP}px">{svg}</div>
  {''.join(lines)}
  {''.join(labels)}
</section>"""
    return wrap2(nav2() + hero + footer("分层按研究模块排列(公开图示命名,经 OIF 术语核验),不是物理拆解:光接收多集成在 PIC 内,光源可外置,主板属系统边界。事件、反应与读数为样式示例。"), 1340)

# ---------------------------------------------------------------- shared blocks
def thesis_block(updated="08-30"):
    return f"""
  <div style="display:flex;flex-direction:column;gap:12px">
    {head(f"我的判断 · 更新于 {updated}", f'<span style="display:flex;gap:16px;align-items:baseline">{asof("08-30 收盘", "至 2027-Q1")}{link("编辑")}{link("回顾")}</span>')}
    {conclusion("pos", f"看多环节、超配国内封测/耦合;自判断起硅光篮子相对整机 {sig('+2.4%', 15)},中际旭创 {sig('+5.1%', 15)} —— 方向对,但幅度还在噪声内(阈值 ±3%)。")}
    <p style="margin:0;font-size:15px;line-height:1.7;color:{T['ink2']};text-wrap:pretty">硅光环节的瓶颈不在 PIC 设计,而在耦合与测试良率;国内厂商在 PIC 代工上仍依赖外部 fab。{wikilink("中际旭创")} 的封测产线是往上游走的信号,但产能兑现要看 2027 年;关注 {wikilink("源杰科技")} 的 CW 激光器送样与 {wikilink("光纤阵列")} 环节的耦合方案。</p>
    <div style="display:flex;flex-direction:column">
      {row("96px minmax(0,1fr)", [mono("方向"), text("看多环节,超配国内封测/耦合;不做 PIC 设计端", 14, T["ink"])], "9px 0")}
      {row("96px minmax(0,1fr)", [mono("窗口"), text("2 个季度(至 2027-Q1),到期自动回顾;中途每次卡口事件后重新记分", 14, T["ink"])], "9px 0")}
      {row("96px minmax(0,1fr)", [mono("验证指标"), text("硅光篮子相对整机 ≥ +3% · 中际旭创毛利率 · 1.6T 出货中硅光占比 ≥ 30%", 14, T["ink"])], "9px 0")}
      {row("96px minmax(0,1fr)", [mono("失效条件"), text("硅光占比 < 30%,或封测产线投产延后 > 1 季度,或篮子相对整机 < −5%", 14, T["ink"])], "9px 0")}
      {rows_end()}
    </div>
    <div style="display:flex;flex-direction:column">
      {row("28px minmax(0,1fr) 90px 60px", [mono("Q1"), text("1.6T 世代硅光 PIC 的国产代工份额是多少?", 14, T["ink"]), mono("待验证"), mono("08-30")], "10px 0")}
      {row("28px minmax(0,1fr) 90px 60px", [mono("Q2"), text("外置光源架构对激光器颗数需求的影响方向?", 14, T["ink"]), mono("待验证"), mono("08-26")], "10px 0")}
      {rows_end()}
    </div>
    {link("+ 新问题")}
  </div>"""

EV = [
    ("08-29", "中际旭创", "关于投资建设硅光芯片封测产线的公告", "扩产", "+3.1%", "2.4", "窗口内 T+2/5"),
    ("08-28", "Intel", "Integrated photonics 产品线路线图更新", "认证导入", "−0.4%", "0.9", "未反应"),
    ("08-27", "源杰科技", "投资者关系活动记录:CW 激光器送样进展", "订单合同", "+2.1%", "1.6", "窗口内 T+4/5"),
    ("08-25", "Broadcom", "CPO 交换机平台出货节奏说明", "供需", "+0.6%", "1.1", "已定价"),
]

def events_block(rows, title="最近事件 · 7 天 · 4 条", concl=("pos", "四条里三条同向(国内两条 + Broadcom),Intel 未跟随;量集中在国内两条 —— 资金在给“国产封测/耦合”投票,不是给硅光整体。")):
    cols = "48px minmax(0,1fr) 76px 92px"
    hdr = row(cols, [mono("日期"), mono("公司 · 事件 · 类别"), mono("T+1 · 量比"), mono("时效")], "6px 0")
    def _r(d, c, tt, cat, r, q, f):
        main = (f'<div style="display:flex;flex-direction:column;gap:3px;min-width:0">'
                f'<span style="font-size:13px;color:{T["ink"]}">{c} <span style="font-family:{MONO};font-size:11px;color:{ACC};margin-left:6px">{cat}</span></span>'
                f'<span style="font-size:13px;color:{T["ink2"]};line-height:1.45">{tt}</span></div>')
        num = f'<div style="display:flex;flex-direction:column;gap:3px">{sig(r, 13)}{mono(q, T["ink2"], 11)}</div>'
        return row(cols, [mono(d), main, num, freshness(f)], "10px 0")
    body = "".join(_r(*x) for x in rows)
    return f"""
  <div style="display:flex;flex-direction:column;gap:10px">
    {head(title, asof("08-30 收盘", "T+1 相对篮子 · 时效 = T+5"))}
    {conclusion(*concl)}
    <div style="display:flex;flex-direction:column">{hdr}{body}{rows_end()}</div>
  </div>"""

# ---------------------------------------------------------------- 2. selected layer
def selected4():
    sel = "pic"
    svg, anchors = stack_svg(T, selected=sel, transform="scale(0.92)")
    STACK_LEFT, STACK_TOP, CONTENT_X = 120, 150, 820
    ax, ay = anchors[sel]; ax, ay = ax * 0.92, ay * 0.92
    px, py = STACK_LEFT + ax, STACK_TOP + ay
    kx, ky = CONTENT_X - 30, 96 + 8
    leader = (f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="1440" height="1200" viewBox="0 0 1440 1200" fill="none">'
              f'<path d="M{px:.0f} {py:.0f} H{kx} V{ky}" stroke="{ACC}" stroke-width="1" opacity="0.55"/>'
              f'<circle cx="{px:.0f}" cy="{py:.0f}" r="3.5" fill="{ACC}"/><circle cx="{kx}" cy="{ky}" r="2.5" fill="{ACC}"/></svg>')
    parts = "".join(row("28px 200px minmax(0,1fr) 16px", [mono(i), title(n), text(f), chev()], "12px 0") for i, n, f in PIC_PARTS)
    cos = "".join(row("120px 120px 70px 60px minmax(0,1fr)", [title(n), mono(t, size=11), text("行业图示", 12), sig(r, 13), mono(last, T["ink2"], 11)], "12px 0")
                  for (n, t, _), r, last in zip(PIC_COMPANIES, ["−0.4%", "+0.6%", "+3.1%", "+2.1%"], ["08-28 认证导入", "08-25 供需", "08-29 扩产", "08-27 订单合同"]))
    content = f"""
<div style="position:absolute;left:{CONTENT_X}px;top:96px;width:540px;display:flex;flex-direction:column;gap:44px">
  <div style="display:flex;flex-direction:column;gap:14px">
    {eyebrow("04 / 09 · SIPH-PIC", accent=True)}
    <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">硅光芯片</h1>
    <span style="font-size:15px;color:{T['muted']}">Silicon photonics PIC · 硅光环节 · 篮子 7 天 {sig('+2.4%', 14)} · {link("篮子 →", 14)}</span>
    <p style="margin:10px 0 0;font-size:17px;line-height:1.6;color:{T['ink2']};font-weight:300;text-wrap:pretty">把电信号调制到光载波、按波长复用,并通过片上波导把光耦合进出光纤。它是 CPO 的光学核心,对应产业链中的硅光环节。</p>
  </div>
  {thesis_block()}
  {events_block(EV)}
  <div style="display:flex;flex-direction:column">{head("部件 · 3", '<span style="font-size:13px;color:' + T['muted'] + '">点击进入下一层</span>')}{parts}{rows_end()}</div>
  <div style="display:flex;flex-direction:column">{head("公司 · 硅光环节 · 4 · 最近事件与 T+1", link("全部公司 →"))}{cos}{rows_end()}</div>
</div>"""
    hint = f"""<div style="position:absolute;left:80px;top:1010px;display:flex;align-items:center;gap:14px;font-size:12px;color:{T['muted']}"><span style="font-family:{MONO};font-size:11px;letter-spacing:0.08em;padding:3px 6px;border:1px solid {T['hair2']};border-radius:4px">ESC</span><span>或点击空白处回到整机</span></div>"""
    body = nav2(["CPO 光模块", "硅光芯片"]) + f"""
<section style="position:relative;height:1900px">
  <div style="position:absolute;left:{STACK_LEFT}px;top:{STACK_TOP}px">{svg}</div>
  {leader}{content}{hint}
</section>"""
    return wrap2(body, 1964)

# ---------------------------------------------------------------- 2b. judgement edit
def judgement4():
    sel = "pic"
    svg, anchors = stack_svg(T, selected=sel, transform="scale(0.92)")
    STACK_LEFT, STACK_TOP, CONTENT_X = 120, 150, 820
    field = lambda k, v, ph=False: row("96px minmax(0,1fr)", [mono(k), f'<span style="font-size:14px;color:{T["muted"] if ph else T["ink"]};border-bottom:1px solid {T["hair2"]};padding-bottom:4px;display:block">{v}</span>'], "9px 0")
    editor = f"""
<div style="position:absolute;left:{CONTENT_X}px;top:96px;width:540px;display:flex;flex-direction:column;gap:32px">
  <div style="display:flex;flex-direction:column;gap:14px">
    {eyebrow("04 / 09 · SIPH-PIC · 编辑判断", accent=True)}
    <h1 style="margin:0;font-size:40px;line-height:1.05;font-weight:600;letter-spacing:-0.02em;color:{T['ink']}">硅光芯片 · 我的判断</h1>
    <span style="font-size:13px;color:{T['muted']}">Markdown 笔记 · data/notes/cpo.mod.pic.md · 可直接用 Obsidian 打开 · 上次保存 08-30</span>
  </div>
  <div style="display:flex;flex-direction:column;gap:6px">
    {eyebrow("方向 · 先选,再写")}
    <div style="display:flex;gap:28px;padding:8px 0;border-top:1px solid {T['hair']};border-bottom:1px solid {T['hair']}">
      <span style="font-family:{MONO};font-size:13px;color:{SIG['pos']};border-bottom:2px solid {SIG['pos']};padding-bottom:6px">▲ 偏多</span>
      <span style="font-family:{MONO};font-size:13px;color:{T['muted']}">▼ 偏空</span>
      <span style="font-family:{MONO};font-size:13px;color:{T['muted']}">● 中性 / 观察</span>
      <span style="font-size:12px;color:{T['muted']};margin-left:auto">方向决定这条判断用什么颜色出现在其他页面</span>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:6px">
    {eyebrow("论点")}
    <div style="position:relative;font-size:16px;line-height:1.7;color:{T['ink']};padding:10px 0;border-top:1px solid {T['hair']};border-bottom:1px solid {T['hair']};min-height:190px">
      硅光环节的瓶颈不在 PIC 设计,而在耦合与测试良率;国内厂商在 PIC 代工上仍依赖外部 fab。[[中际旭创]] 的封测产线是往上游走的信号,但产能兑现要看 2027 年;关注 [[源<span style="border-left:1.5px solid {T['ink']};margin-left:1px"></span>
      <div style="position:absolute;left:300px;top:96px;width:220px;background:{T['bg']};border:1px solid {T['hair2']};border-radius:6px;padding:6px 0;box-shadow:0 12px 28px -12px rgba(0,0,0,0.25)">
        <div style="padding:6px 12px;font-size:14px;color:{T['ink']};background:color-mix(in srgb, {ACC} 8%, transparent)">源杰科技 <span style="font-family:{MONO};font-size:11px;color:{T['muted']};margin-left:8px">公司 · 688498</span></div>
        <div style="padding:6px 12px;font-size:14px;color:{T['ink2']}">光源 / 激光器 <span style="font-family:{MONO};font-size:11px;color:{T['muted']};margin-left:8px">环节</span></div>
        <div style="padding:6px 12px;font-size:14px;color:{T['ink2']}">激光器阵列 <span style="font-family:{MONO};font-size:11px;color:{T['muted']};margin-left:8px">层 05</span></div>
      </div>
    </div>
    <span style="font-size:12px;color:{T['muted']}">Markdown · 输入 [[ 链接公司 / 环节 / 层 / 部件 · 链接会出现在对方页面的“被引用”里</span>
  </div>
  <div style="display:flex;flex-direction:column;gap:6px">
    {eyebrow("让它可被证伪 · 数字会被自动跟踪")}
    <div style="display:flex;flex-direction:column">
      {field("窗口", "2 个季度 · 至 2027-Q1 · 到期自动进收件箱回顾")}
      {field("验证指标", "硅光篮子相对整机 ≥ +3% · [[中际旭创]] 毛利率 · 1.6T 出货中硅光占比 ≥ 30%")}
      {field("失效条件", "硅光占比 < 30%,或封测产线投产延后 > 1 季度,或篮子相对整机 < −5%")}
      {field("头寸含义", "触发验证 → 加环节篮子;触发失效 → 减至基准", ph=True)}
      {rows_end()}
    </div>
    <span style="font-size:12px;color:{T['muted']}">带阈值的指标(≥ / <)会每天用行情重算,达到即在收件箱提示;没有阈值的只做记录。</span>
  </div>
  <div style="display:flex;gap:22px;align-items:baseline">
    <span style="font-size:14px;color:{T['bg']};background:{T['ink']};padding:8px 16px;border-radius:6px">保存</span>
    <span style="font-size:14px;color:{T['muted']}">取消</span>
    <span style="font-size:12px;color:{T['muted']};margin-left:auto">⌘S 保存 · Esc 取消</span>
  </div>
</div>"""
    body = nav2(["CPO 光模块", "硅光芯片", "编辑判断"]) + f"""
<section style="position:relative;height:1100px">
  <div style="position:absolute;left:{STACK_LEFT}px;top:{STACK_TOP}px;opacity:{0.5 if T is LIGHT else 0.75}">{svg}</div>
  {editor}
</section>"""
    return wrap2(body, 1164)

# ---------------------------------------------------------------- 3. company page
def company4():
    crowd = f"""
  <div style="display:flex;flex-direction:column;gap:10px">
    {head("拥挤度 · 脆弱性", asof("08-30 收盘", "20 日", "状态量,每日重算,不是信号"))}
    {conclusion("neg", "拥挤:短期获利盘厚、筹码在集中;利好边际递减,小利空会被放大。这与你说的 7 月那种“利好也拉不回”是同一类结构,只是量级不同。")}
    {kv([("20日涨幅分位", "92%", "neg"), ("换手率分位", "88%", "neg"), ("融资余额/流通市值", "4.1%", "neg"), ("股东户数", "↓ 3.2% 集中", None), ("相对篮子偏离", "+1.8σ", "neg")])}
    <span style="font-size:12px;color:{T['muted']}">读数着色规则:高于 80 分位或 +1.5σ 视为脆弱(偏空),低于 20 分位视为出清(偏多),其余中性。阈值可调。</span>
  </div>"""
    reso = f"""
  <div style="display:flex;flex-direction:column;gap:12px">
    {head("共振 · 08-29 扩产", f'<span style="display:flex;gap:16px;align-items:baseline">{asof("08-30 收盘", "事件后 T+1 / T+3", "时效 T+5")}{link("换一个事件")}</span>')}
    {conclusion("pos", "环节级事件而非个股事件:同环节与上游同向,资金用量确认。但换手分位 91% 说明追价者多,若 T+5 前没有二次确认(订单 / 涨价),回吐概率高。")}
    <div style="display:flex;flex-direction:column">
      {row("110px minmax(0,1fr)", [mono("本公司"), inline("T+1 ", sig("+3.1%"), " · T+3 ", sig("+4.8%"), " · 量比 2.4 · 换手 6.8%(60 日分位 91%)")], "10px 0")}
      {row("110px minmax(0,1fr)", [mono("同环节"), inline("源杰科技 ", sig("+2.1%"), " · Broadcom ", sig("+0.6%"), " · Intel ", sig("−0.4%"), " → 3/4 同向,硅光篮子 T+1 超额 ", sig("+1.9%"))], "10px 0")}
      {row("110px minmax(0,1fr)", [mono("上下游层"), inline("上游 光纤阵列 篮子 ", sig("+1.2%"), " · 下游 光引擎/封装 篮子 ", sig("+0.3%"), " · 交换 ASIC 无反应")], "10px 0")}
      {row("110px minmax(0,1fr)", [mono("资金与关注"), inline("融资余额 ", sig("+2.3%"), "(3 日)· 互动易提问 +12 条 · 龙虎榜:无 · 北向:不披露")], "10px 0")}
      {row("110px minmax(0,1fr)", [mono("历史基线"), inline("该公司近 1 年 5 次“扩产”事件,T+1 平均超额 ", sig("+1.2%"), ",命中率 3/5;本次高于基线")], "10px 0")}
      {rows_end()}
    </div>
  </div>"""
    ev_rows = [
        ("08-29", "公告", "关于投资建设硅光芯片封测产线的公告", "扩产", "+3.1%", "2.4", "窗口内 T+2/5"),
        ("08-21", "新闻", "1.6T 光模块批量出货节奏(媒体报道,需回到公告核验)", "供需", "+0.9%", "1.2", "已定价"),
        ("08-12", "互动易", "回复投资者:硅光方案在 800G 产品中的占比持续提升", "认证导入", "+0.2%", "0.8", "过期 · 未反应"),
    ]
    ev_hdr = row("48px 56px minmax(0,1fr) 64px 60px 44px 108px", [mono("日期"), mono("来源"), mono("事件"), mono("类别"), mono("T+1"), mono("量比"), mono("时效")], "6px 0")
    ev_body = "".join(row("48px 56px minmax(0,1fr) 64px 60px 44px 108px", [mono(d), mono(k), text(tt, 14, T["ink"]), mono(cat, ACC), sig(r, 13), mono(q, T["ink2"], 12), freshness(f)], "11px 0") for d, k, tt, cat, r, q, f in ev_rows)
    left = f"""
<div style="display:flex;flex-direction:column;gap:44px">
  <header style="display:flex;flex-direction:column;gap:14px">
    {eyebrow("300308 · 深交所")}
    <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{T['ink']}">中际旭创</h1>
    <span style="font-size:15px;color:{T['muted']}">中际旭创股份有限公司 · 硅光芯片 / 光引擎与封装 · {link("硅光篮子 →", 15)}</span>
    {conclusion("neu", f"事件面偏多(30 天 3 条卡口事件,2 条已见资金反应),结构面偏空(拥挤区)。两者相抵:有新事件才追,没有就等它出清。", 16)}
  </header>
  <div style="display:flex;flex-direction:column;gap:10px">
    {head("价格 · 6 个月 · 指数化 = 100", asof("08-30 收盘", None, "圆点为卡口事件,点开看共振 · 示例数据"))}
    {price_strip()}
    <div style="display:flex;gap:28px;font-size:13px;color:{T['ink2']};margin-top:6px;align-items:baseline">
      <span>{mono("PE TTM")} 28.4</span><span>{mono("5 年分位")} 35%</span><span>{mono("3M")} {sig("+12.6%", 13)}</span><span>{mono("相对篮子")} {sig("+4.1%", 13)}</span><span>{mono("相对整机")} {sig("+6.5%", 13)}</span>
    </div>
  </div>
  {crowd}
  <div style="display:flex;flex-direction:column;gap:10px">
    {head("卡口事件 · 30 天 · 3 条", f'<span style="display:flex;gap:16px;align-items:baseline">{asof("08-30 收盘", "T+1 相对篮子 · 时效 T+5")}{link("全部公告与新闻 →")}</span>')}
    {conclusion("pos", "三条里只有 08-29 那条被资金真正投票(有量、有共振);互动易那条过期未反应,信息已被消化。")}
    <div style="display:flex;flex-direction:column">{ev_hdr}{ev_body}{rows_end()}</div>
  </div>
  {reso}
  {thesis_block()}
  <div style="display:flex;flex-direction:column">
    {head("在产业链中的位置 · 2")}
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
    <dt style="color:{T['muted']}">在整机中</dt><dd style="margin:0;color:{T['ink']}">{link("04 硅光芯片", 14)}</dd>
    <dt style="color:{T['muted']}">被引用</dt><dd style="margin:0;color:{T['ink']}">{link("硅光芯片 · 判断", 14)} · {link("Q1", 14)}</dd>
  </dl>
  <div style="display:flex;flex-direction:column;gap:10px">
    {eyebrow("待核验 · 1")}
    <div style="display:flex;flex-direction:column;gap:8px;padding:12px 0;border-top:1px solid {T['hair']};border-bottom:1px solid {T['hair']}">
      <span style="font-size:14px;color:{T['ink']}">硅光芯片环节 · 行业图示 → 候选</span>
      <span style="font-size:13px;color:{T['ink2']}">08-29 公告提到硅光芯片封测产线,可作为来源升级这条关系。</span>
      <div style="display:flex;gap:18px;margin-top:4px">{link("以此公告升级为候选")}<span style="font-size:13px;color:{T['muted']}">忽略</span></div>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:8px">
    {eyebrow("颜色怎么读")}
    <p style="margin:0;font-size:12px;line-height:1.7;color:{T['muted']}">{tag("pos")} 对资金方向是正向 · {tag("neg")} 负向 · {tag("neu")} 中性或状态量。A 股习惯:红涨绿跌;可在设置里切换为绿涨红跌。颜色只用在数字、方向标记和结论行,正文保持墨色。</p>
  </div>
</aside>"""
    body = nav2(["公司", "中际旭创"], active="公司") + f"""
<main style="max-width:1440px;margin:0 auto;padding:56px 80px 0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:96px;align-items:start">
  {left}{aside}
</main>""" + footer("价格、估值、反应与拥挤读数为样式示例;接入公告、新闻、行情与东财资金面数据后替换,每条事件保留原文链接。")
    return wrap2(body, 2320)

# ---------------------------------------------------------------- 4. inbox
def inbox4():
    t = T
    def decide(kind, d, txt, actions):
        return row("90px 52px minmax(0,1fr) 220px", [mono(kind), tag(d, LABEL[d], 11), text(txt, 14, t["ink"]), f'<span style="display:flex;gap:16px">{actions}</span>'], "12px 0")
    decide_rows = "".join([
        decide("篮子偏离", "neg", "硅光芯片篮子相对整机 +2.1σ(20 日),拥挤度进入高位 —— 环节级仓位此时加,买到的是被投票过的那一半", f'{link("看篮子")}<span style="font-size:13px;color:{t["muted"]}">知道了</span>'),
        decide("判断到期", "neu", "激光器阵列 · “外置光源不改变颗数需求” · 窗口 08-31 到期 · 自判断起篮子 +1.1%,未达 ±3% 阈值", f'{link("回顾")}<span style="font-size:13px;color:{t["muted"]}">延长一季</span>'),
        decide("待核验", "pos", "中际旭创 → 硅光芯片 · 08-29 公告可作为来源,行业图示 → 候选", f'{link("升级为候选")}<span style="font-size:13px;color:{t["muted"]}">忽略</span>'),
        decide("待核验", "neu", "Broadcom → 交换 ASIC · 官网交换产品线(既有候选)· 候选 → 已核验", f'{link("审核")}<span style="font-size:13px;color:{t["muted"]}">驳回</span>'),
    ])
    ev = [
        ("08-29", "中际旭创", "公告", "关于投资建设硅光芯片封测产线的公告", "扩产", "+3.1%", "窗口内 T+2/5"),
        ("08-29", "高速主板", "新闻", "高层数 PCB 涨价函流传(需回到公告核验)", "涨价", "−0.6%", "未反应"),
        ("08-28", "Intel", "新闻", "Integrated photonics 产品线路线图更新", "认证导入", "−0.4%", "未反应"),
        ("08-27", "源杰科技", "互动易", "CW 激光器送样进展", "订单合同", "+2.1%", "窗口内 T+4/5"),
        ("08-26", "长光华芯", "公告", "关于股份回购进展的公告", "—", "+0.3%", "已定价"),
        ("08-25", "Broadcom", "新闻", "CPO 交换机平台出货节奏说明", "供需", "+0.6%", "已定价"),
    ]
    ev_hdr = row("48px 100px 52px minmax(0,1fr) 64px 60px 100px", [mono("日期"), mono("对象"), mono("来源"), mono("事件"), mono("类别"), mono("T+1"), mono("时效")], "6px 0")
    ev_body = "".join(row("48px 100px 52px minmax(0,1fr) 64px 60px 100px", [mono(d), link(o, 13), mono(k), text(tt, 14, t["ink"]), mono(cat, ACC), sig(r, 13), freshness(f)], "10px 0") for d, o, k, tt, cat, r, f in ev)
    def q(i, qtext, obj, status, date):
        return row("28px minmax(0,1fr) 150px 80px 60px", [mono(i), text(qtext, 15, t["ink"]), link(obj, 13), mono(status), mono(date)], "13px 0")
    open_q = "".join([q("Q1", "1.6T 世代硅光 PIC 的国产代工份额是多少?", "硅光芯片", "待验证", "08-30"), q("Q3", "封测产线投产后硅光 PIC 是否自供?", "中际旭创", "待验证", "08-30"), q("Q2", "外置光源架构对激光器颗数需求的影响方向?", "激光器阵列", "待验证", "08-26")])
    notes = "".join([
        row("56px 110px minmax(0,1fr) 60px", [tag("pos", "", 11), link("硅光芯片", 13), text("硅光环节的瓶颈不在 PIC 设计,而在耦合与测试良率……", 14), mono("08-30")], "11px 0"),
        row("56px 110px minmax(0,1fr) 60px", [tag("neu", "", 11), link("中际旭创", 13), text("事件面偏多、结构面偏空;有新事件才追……", 14), mono("08-30")], "11px 0"),
        row("56px 110px minmax(0,1fr) 60px", [tag("neu", "", 11), link("激光器阵列", 13), text("外置光源是可维护性与成本的权衡,不是技术路线之争……", 14), mono("08-24")], "11px 0"),
    ])
    rail_layers = [("01", "散热与上盖", 0, "—", None), ("02", "交换 ASIC", 1, "+0.4%", "pos"), ("03", "电处理层", 0, "—", None), ("04", "硅光芯片", 4, "+2.4%", "pos"), ("05", "激光器阵列", 2, "+1.1%", "pos"), ("06", "光电探测阵列", 0, "—", None), ("07", "光纤阵列", 0, "+1.2%", "pos"), ("08", "共封装基板", 0, "—", None), ("09", "高速主板", 1, "−0.6%", "neg")]
    rail = "".join(
        f'<div style="display:grid;grid-template-columns:28px minmax(0,1fr) 24px 56px;gap:10px;align-items:baseline;padding:9px 0;border-top:1px solid {t["hair"]}">'
        f'{mono(i, (SIG[d] if d else t["muted"]))}<span style="font-size:14px;color:{t["ink"] if n else t["ink2"]}">{nm}</span>'
        f'<span style="font-family:{MONO};font-size:12px;color:{t["ink2"] if n else t["faint"]};text-align:right">{n if n else "·"}</span>'
        f'<span style="text-align:right">{sig(p, 12) if d else mono("—", t["faint"])}</span></div>'
        for i, nm, n, p, d in rail_layers)
    body = nav2(["研究"], active="研究") + f"""
<main style="max-width:1440px;margin:0 auto;padding:56px 80px 0;display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:96px;align-items:start">
  <div style="display:flex;flex-direction:column;gap:52px">
    <header style="display:flex;flex-direction:column;gap:14px">
      {eyebrow("Research · this week")}
      <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{t['ink']}">研究</h1>
      {conclusion("neu", "4 件事要决定,最紧急的是硅光篮子的拥挤告警;6 条事件里只有两条国内侧事件还在窗口内,其余 2 条已定价、2 条未反应。", 16)}
      {asof("08-30 收盘", "本周", "每日收盘后重算")}
    </header>
    <div style="display:flex;flex-direction:column">{head("要决定 · 4", '<span style="font-size:13px;color:' + t['muted'] + '">按紧急程度 · 方向标记 = 对你现有判断的含义</span>')}{decide_rows}{rows_end()}</div>
    <div style="display:flex;flex-direction:column">{head("卡口事件 · 7 天 · 6 条", asof("08-30 收盘", "T+1 相对篮子 · 时效 T+5"))}{ev_hdr}{ev_body}{rows_end()}</div>
    <div style="display:flex;flex-direction:column">{head("未决问题 · 3", link("+ 新问题"))}{open_q}{rows_end()}</div>
    <div style="display:flex;flex-direction:column">{head("最近笔记 · 3", '<span style="font-size:13px;color:' + t['muted'] + '">标记 = 判断方向</span>')}{notes}{rows_end()}</div>
  </div>
  <aside style="display:flex;flex-direction:column;gap:14px;padding-top:120px">
    {head("整机 · 本周", asof("08-30", "7 天"))}
    <div style="display:grid;grid-template-columns:28px minmax(0,1fr) 24px 56px;gap:10px;padding:0 0 4px">{mono("")}{mono("层")}{mono("事件", size=11)}<span style="text-align:right">{mono("篮子", size=11)}</span></div>
    <div style="display:flex;flex-direction:column">{rail}{rows_end()}</div>
    <span style="font-size:12px;color:{t['muted']};line-height:1.6">点层回到整机对应位置。判断与问题以 Markdown 保存在 data/notes/,可直接用 Obsidian 打开。</span>
  </aside>
</main>""" + footer("事件、反应与偏离读数为样式示例。")
    return wrap2(body, 1640)

# ---------------------------------------------------------------- 5. basket
def basket4():
    t = T
    legend = (f'<div style="display:flex;gap:22px;font-size:13px;color:{t["ink2"]};align-items:center">'
              f'<span style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:2px;background:{ACC};display:inline-block"></span>硅光芯片篮子 · 4 家 · 等权</span>'
              f'<span style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:2px;background:{t["faint"]};display:inline-block"></span>整机篮子 · 32 家 · 等权</span>'
              f'{asof("08-30 收盘", "6 个月", "指数化 = 100 · 各自本币 · 示例数据")}</div>')
    cols = "150px 140px 64px 64px 80px 90px minmax(0,1fr) 90px"
    hdr = row(cols, [mono("公司"), mono("市场"), mono("3M"), mono("6M"), mono("估值分位"), mono("拥挤"), mono("最近卡口事件 · T+1"), mono("证据级")], "8px 0")
    def r(n, m, m3, m6, pct, crowd, cd, ev, evr, lvl):
        return row(cols, [title(n), mono(m, size=11), sig(m3, 14), sig(m6, 14), text(pct, 14), f'<span style="font-family:{MONO};font-size:12px;color:{SIG[cd]}">{crowd}</span>', inline(ev, " ", sig(evr, 13), size=13), text(lvl, 13)], "13px 0")
    table = hdr + "".join([
        r("中际旭创", "300308 · 深交所", "+12.6%", "+31.2%", "35%", "高 92%", "neg", "08-29 扩产", "+3.1%", "行业图示"),
        r("源杰科技", "688498 · 上交所", "+8.1%", "+19.4%", "62%", "中 61%", "neu", "08-27 订单合同", "+2.1%", "行业图示"),
        r("Intel", "INTC · NASDAQ", "−3.4%", "+2.0%", "18%", "低 22%", "pos", "08-28 认证导入", "−0.4%", "行业图示"),
        r("Broadcom", "AVGO · NASDAQ", "+6.9%", "+24.8%", "88%", "高 85%", "neg", "08-25 供需", "+0.6%", "候选 · 待核验"),
    ]) + rows_end()
    efficacy = f"""
  <div style="display:flex;flex-direction:column;gap:12px">
    {head("事件效力 · 该环节", asof("08-30", "滚动 90 天", "每周重算"))}
    {conclusion("pos", "这一环节的卡口事件“有效但短”:当交易信号看 T+5,当研究信号看是否出现二次确认(订单 → 扩产 → 涨价)。")}
    <div style="display:flex;flex-direction:column">
      {row("110px minmax(0,1fr)", [mono("样本"), text("14 条卡口事件(扩产 5 · 订单合同 4 · 认证导入 3 · 供需 2)", 14, t["ink"])], "10px 0")}
      {row("110px minmax(0,1fr)", [mono("平均反应"), inline("T+1 ", sig("+1.8%"), " · T+5 ", sig("+2.6%"), " · T+20 ", sig("+1.1%"), "(相对整机篮子)")], "10px 0")}
      {row("110px minmax(0,1fr)", [mono("命中率"), text("64%(9/14 同向)· 扩产类最高 4/5 · 认证导入类最低 1/3", 14, t["ink"])], "10px 0")}
      {row("110px minmax(0,1fr)", [mono("半衰期"), inline("T+5 到 T+20 回吐 58% → 事件信号的有效期约 ", f'<span style="color:{t["ink"]};font-weight:500">5–8 个交易日</span>', ";过期后的价格里已经没有这条事件了")], "10px 0")}
      {rows_end()}
    </div>
  </div>"""
    crowd = f"""
  <div style="display:flex;flex-direction:column;gap:10px">
    {head("篮子拥挤度", asof("08-30 收盘", "20 日", "状态量,每日重算"))}
    {conclusion("neg", "篮子整体进入拥挤区,但分化明显:资金集中在国内两家,美股两家没跟。环节级仓位此时加,买到的是“已被投票过的”那一半。")}
    {kv([("20日涨幅分位", "89%", "neg"), ("成交额占整机", "31%(均值 18%)", "neg"), ("换手率分位", "84%", "neg"), ("相对整机偏离", "+2.1σ", "neg"), ("成分内分化", "2 高 1 中 1 低", None)])}
  </div>"""
    others = "".join(row("40px 220px 70px 80px minmax(0,1fr)", [mono(i), title(n, 15), sig(v, 14), f'<span style="font-family:{MONO};font-size:12px;color:{SIG[cd]}">{cr}</span>', text(k, 13)], "10px 0") for i, n, v, cr, cd, k in [
        ("04", "光源 / 激光器", "+15.2%", "高 90%", "neg", "4 家 · 最近 08-27 订单合同 · +2.1%"), ("02", "交换芯片 / ASIC", "+9.8%", "中 55%", "neu", "3 家 · 最近 08-25 供需 · +0.6%"), ("06", "基板与互连", "+7.4%", "中 48%", "neu", "3 家 · 最近 08-29 涨价 · 未反应"), ("07", "散热与结构件", "+4.1%", "低 30%", "pos", "3 家 · —")])
    body = nav2(["公司", "硅光芯片", "篮子"], active="公司") + f"""
<main style="max-width:1440px;margin:0 auto;padding:56px 80px 0;display:flex;flex-direction:column;gap:48px">
  <header style="display:flex;flex-direction:column;gap:14px;max-width:820px">
    {eyebrow("Basket · 03 / 10 · 硅光芯片")}
    <h1 style="margin:0;font-size:56px;line-height:1.02;font-weight:600;letter-spacing:-0.025em;color:{t['ink']}">硅光芯片篮子</h1>
    {conclusion("neu", f"环节相对整机 6 个月 {sig('+3.5%', 16)},趋势偏多;但当前拥挤(+2.1σ)且事件效力只有 5–8 天。结论:不追,等回到 +1σ 以内或出现二次确认再加。", 16)}
    <p style="margin:0;font-size:15px;line-height:1.6;color:{t['ink2']};font-weight:300;text-wrap:pretty">这一环节的 4 家公司等权组成一个篮子,与整机全部公司的篮子比较;卡口事件标在篮子曲线上。公司页看的是单一标的,这里看的是整个环节被资金对待的方式。</p>
  </header>
  <div style="display:flex;flex-direction:column;gap:14px">{legend}{basket_chart()}</div>
  <div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:96px;align-items:start">{efficacy}{crowd}</div>
  <div style="display:flex;flex-direction:column">{head("成分 · 4 家", link("编辑权重"))}{table}</div>
  <div style="display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:96px;align-items:start">
    <div style="display:flex;flex-direction:column">{head("其他环节 · 3M · 拥挤", link("全部环节 →"))}{others}{rows_end()}</div>
    <p style="margin:0;font-size:13px;line-height:1.7;color:{t['ink2']}">篮子回答两个问题:这一环节作为整体相对整机在走强还是走弱、拐点是否和卡口事件对得上;以及资金给这个环节的事件投的是长票还是短票。跨市场成分按各自本币指数化;权重默认等权,可手动调整并记录理由。</p>
  </div>
</main>""" + footer("行情、反应与拥挤读数为样式示例;接入免费行情源(A 股:腾讯/新浪/东财;美股:Yahoo)后替换。")
    return wrap2(body, 1780)

# ---------------------------------------------------------------- write both themes
PAGES = [("Main", overview4, 1340), ("Selected", selected4, 1964), ("Judgement", judgement4, 1164), ("Company", company4, 2320), ("Inbox", inbox4, 1640), ("Basket", basket4, 1780)]
TITLES = {"Main": "总览:资金在给谁投票", "Selected": "选中一层:结论先行", "Judgement": "编辑判断", "Company": "公司:拥挤 · 事件 · 共振", "Inbox": "研究:先决定", "Basket": "环节篮子:效力 · 拥挤"}
NOTES = {
    "Main": "看:1) 第一行结论(红 ▲)是不是你想第一眼看到的;2) 层上的呼吸点颜色 = 篮子方向;3) 第二行的 截至/窗口。",
    "Selected": "看:1) 每段第一行都是结论,方向色只出现在标记与数字;2) “判断”的阈值(≥ +3% / < 30%)会被自动跟踪;3) 事件表新增 T+1 / 量比 / 时效。",
    "Judgement": "看:方向先选;带阈值的验证指标会每天重算并在收件箱提示。",
    "Company": "看:1) 页首一句话把事件面(偏多)和结构面(偏空)相抵;2) 拥挤度读数按阈值着色;3) 共振五行的数字全部带方向色;4) 右下角是颜色规则。",
    "Inbox": "看:“要决定”每条带方向标记 = 对你现有判断的含义;事件表带时效列。",
    "Basket": "看:1) 页首结论把趋势、拥挤、效力三者合成一句;2) 事件效力里的“半衰期”= 这类事件的时效;3) 成分表拥挤列着色。",
}
files = []
artboards, annotations = [], []
ROW_GAP = 160
x = 0
xs = {}
for name, fn, h in PAGES:
    xs[name] = x
    x += 1440 + 140
y_light, y_dark = 0, 2440
for theme in ("light", "dark"):
    set_theme(theme)
    for name, fn, h in PAGES:
        fname = f"{name}{'' if theme == 'light' else 'Dark'}.dc.html"
        with open(os.path.join(HERE, fname), "w", encoding="utf-8") as f:
            f.write(fn())
        files.append(fname)
        yy = y_light if theme == "light" else y_dark
        artboards.append({"file": fname, "title": f"{TITLES[name]} · {'浅' if theme == 'light' else '深'}", "x": xs[name], "y": yy, "w": 1440, "h": h})
        if theme == "light":
            annotations.append({"id": f"note-{name.lower()}", "x": xs[name], "y": -150, "w": 440, "text": NOTES[name]})
set_theme("light")
annotations.insert(0, {"id": "brief", "x": -520, "y": 0, "w": 460,
    "text": "Teardown · 方向稿 v3\n\n三条改动:\n① 每个分析段第一行是结论,带方向标记 ▲偏多 / ▼偏空 / ●中性;A 股习惯红涨绿跌,可切换。颜色只落在标记、数字、结论行,正文保持墨色。\n② 每个读数都带“截至 + 窗口”。事件反应 = T+1 / T+5 相对篮子;事件时效默认 T+5(由事件效力里的半衰期校准);拥挤度是状态量,每日重算,不是信号。\n③ 六页全部有深色版(下一行)。\n\n所有事件、价格、读数仍为样式示例。"})
canvas = {"artboards": artboards, "annotations": annotations, "launch": {"view": "canvas"}}
with open(os.path.join(HERE, "canvas.json"), "w", encoding="utf-8") as f:
    json.dump(canvas, f, ensure_ascii=False, indent=2)
print("ok", files)
