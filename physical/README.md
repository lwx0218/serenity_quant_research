# physical/ · 从物理出发

`main`（原 reboot-v2）上的 Teardown 是从投研出发去找物理：首页是「资金本周在给哪一层投票」，CPO 九个模块其实是一条产业链的分类，而不是一只正在出货的模块。

这个目录反过来：**先拿一只真实在用的模块，揭盖画出来，让信号从主机金手指走到光纤，穿过的每一个部件挂上它背后的公司**。投研是从物理长出来的，不是反过来去找物理。

第一只模块：**1.6T OSFP DR8 硅光 + 3nm DSP**——Quantum-X800 / Spectrum-X800 / ConnectX-9（Rubin 世代 scale-out）正在用的形态。

## 文件

```text
physical/
  data/module-1.6t-dr8-siph.json     唯一的数据源：模块 → 部件 → 信号顺序 → 公司（产业阶段、证据级、来源、备注）
  seam.py                            物理 → 投研的接缝：写 companyId，补 data/seeds/physical/companies.json
  design/gen_physical.py             方向稿画板（Claude Design 画布用 .dc.html，浅深两版）；等距揭盖图的几何在这里
  design/build_prototype.py          可交互原型 → dist/teardown-1.6t-prototype.html；同时导出 web/public/physical/*.svg|json
  design/reference-intel-1.6t-opened.png  部件摆位参考（Intel 1.6T 拆解图）
  dist/teardown-1.6t-prototype.html  单文件原型（选中部件 / 发收切换 / 浅深 / Esc 回整机）
  dist/teardown-web-snapshot.html    整个 web/ 应用的单文件快照（hash 路由 + 内嵌 API 数据），双击即开，用来验 UX
  index.html · build.py · dist/teardown-1.6t-dr8-siph.html  第一版横截面页（风格不合，已被原型取代，待删）
```

改了 JSON 或几何之后：`python3 physical/design/gen_physical.py && python3 physical/design/build_prototype.py`（后者会把 web/ 用的 SVG 与锚点一起重出）。
画布：`Teardown 实物剖面 · 1.6T 光模块`（Claude Design，两页：实物 / 接缝）。原型的 UX 预审用 `ux-preflight` skill。

## 在 web/ 上落的三处

1. **/physical · /physical/:id**（`web/src/pages/PhysicalPage.tsx`）：等距揭盖图 + 发/收站点 + 部件详情 + 该部件上的公司（按阶段分组，证据级可点开来源）。`?part=` 记住选中。
2. **公司页「在实物里的位置」**（`CompanyPage.tsx`）：这家公司站在哪几个部件上、什么阶段、证据级与来源，缩略图亮着它的部件。
3. **研究收件箱「→ 部件」列**（`Research.tsx`）：事件按类别落到公司最相关的那个部件（`api/app/physical.py::part_for_event`）。

API：`GET /api/physical`、`/api/physical/{id}`、`/api/companies/{id}/physical`；事件对象多一个 `part`。

## 数据模型（schema 0.3）

| 字段 | 含义 |
|---|---|
| `module` | 一只具体模块：形态、规格、它插在哪台英伟达机器的哪个位置（`hostContext`） |
| `parts[]` | 部件：功能、关键参数、上游材料、`companies[]` |
| `signalPath.tx / rx` | 信号按顺序经过哪些 part，每一步是电还是光 |
| `stages` | 产业阶段：材料 → 芯片 → 器件/封装 → 引擎/组装 → 连接 → 模块/客户 → 设备/测试 |
| `companies[].companyId` | main 侧公司 id（`seam.py` 生成：A 股 `cn.<代码>`，海外 `global.<slug>`，未上市 `private.<slug>`）；占位条目为 null |
| `companies[].evidence` | `verified` / `consensus` / `candidate`，由来源决定（见下） |
| `companies[].sources[]` | `{type, title, url, publisher, date, quote}`；type ∈ announcement · irm · filing · official · media · report |
| `companies[].note` | 一句话：这条映射是怎么成立的 / 还差什么 |
| `companies[].market` | `A` / `US` / `JP` / `TW` / `HK` / `私有` … |

**证据级规则**：至少一条公告 / 互动易 / 年报·招股书 / 官网来源直接支持「这家公司在这个部件上」→ `verified`；只有媒体 / 研报 → `consensus`；没有来源 → `candidate`。来源必须打得开且原文确实支持该映射（审计时打不开或答非所问的不算）。
当前：17 个部件、128 条映射（88 家有 companyId，3 条占位）、142 条来源；verified 109 · consensus 4 · candidate 15。

## 新闻源（证据往前走的那条管道）

`data/sources/news_sources.json` 列信息源（tier 0 公告/互动易 → verified；1 行业垂直媒体 → consensus；2 综合财经、3 泛科技 → candidate），`scripts/news_fetch.py` 拉取、按 physical/ 里的公司与部件词表命中、分类（扩产 / 订单 / 认证 / 供需 / 涨价 / 技术路线）、去重，写 `data/events/candidates.json`。
RSS 地址未在本机验证过：先 `python3 scripts/news_fetch.py --probe`，打不开的换地址或删；`--only rss|cninfo_announcement|cninfo_irm` 只跑一类源，`--dry-run` 不写文件。候选进收件箱的 UI 还没做。

## 下一步（尚未做）

- 候选事件（candidates.json）进收件箱：人工确认后才成为事件，来源随事件带进公司页与部件页。
- 判断的骨架加「证伪信号 / 检查点 / 可靠性 1–5」；再往后是 mandate（先出方向稿）。
- 追加第二、第三只实物：存储（HBM / SSD）、PCB（GB300 compute tray）、电源……都围绕一台真实的英伟达机柜展开，`module` 变成 `objects[]`，几何搬进 JSON。
- 15 条 candidate 逐条补来源（沪电 / 深南 / 中芯 / 长飞 / 三环 / 长芯盛 / 天孚 / 铭普 / 精研 / 旭创自研驱动 / Honeywell·Dow / 云南锗业 PD 侧）。
