# AGENTS.md

<!-- HARNESS:MANAGED:START -->
## Harness Managed Execution Contract

本仓库采用 PI-first `simple` 默认模式。本分区由 Harness starter/updater 管理；项目产品、领域、安全和运行时规则请写在 `PROJECT:OWNED` 分区。

### Authority

- 本文件是模型执行合同；冲突时优先于 README、human manual、`.pi/` 和历史 evidence。
- `.pi/` 只是 capability layer，不是 policy authority。
- extension、skills、prompt templates 默认 passive；不会因为存在而自动启用 formal workflow。

### Default Mode: simple

默认永远是 `simple`：理解请求、必要时少量澄清、执行 bounded change、运行相称验证、用中文总结。复杂、跨文件、跨 session 或已有历史 Plan/evidence 不会自动升级为 fixed Round、handoff、Independent Review 或 formal gate。

Plan 只用于澄清目标、范围、风险和验证；除非 Owner 明确批准 formal mode，否则 Plan 不自动创建 Round 或 review 义务。

### Formal Mode Is Opt-In

只有 Owner 明确要求并批准时，才启用 fixed Round、Independent Review、session handoff、formal acceptance gate 或其他重治理能力。simple mode 下：

- 不创建 Round、Round ledger 或 Round handoff；
- 不自动调用 Independent Review；
- 不显示或恢复 Round progress widget；
- 历史 fixed-Round/review/handoff 条款只作为历史证据。

### First Session

Greenfield 或无 approved baseline 的项目，首次建议从项目根运行：

```bash
pi --name "00-orchestration"
```

Owner 批准 Plan 前只允许 read/infer/discuss 和 chat Plan Preview；不得修改业务 code/config、创建 durable evidence、安装依赖或执行破坏性操作。接受 recommended defaults 不等于批准 durable Plan。

### Routing

- `direct-execute`：清楚 bounded task。
- `plan`：目标、范围、风险、验证或交接需要 durable clarification。
- `review-only`：只要 findings。
- `needs-extension`：确有能力缺口。

skills、domain modeling、subagent 和 reviewer 均为按需能力，不是默认关卡。

### Evidence And Safety

项目 evidence 默认保存在项目本地 `docs/project-intake/` 与 `operations/`。只有 Plan、交接、合同/bootstrap/portability 或正式 review 需要时才写 durable evidence。

高风险、破坏性、外部授权、scope/acceptance 改变或验证失败时 fail closed 并询问 Owner。不自动 push。
<!-- HARNESS:MANAGED:END -->

<!-- PROJECT:OWNED:START -->
## 愿景（一切工作的准绳，2026-09-29 起）

**从物理出发去覆盖投研，根据事件与 evidence 去指导投资。**
一只真实在用的实物（现在是 NVIDIA Quantum-X800 上的 1.6T OSFP DR8 硅光模块）→ 每个部件背后的公司（每条映射带来源、带证据级）→ 落在部件上的卡口事件与资金反应 → 指导投资的判断。先物理，后投研（Owner：Faye）。页面上每个数字都要有来路。

### 产品要回答的唯一问题（验收标准）

> **这只模块的十七段里，此刻资金在为哪一段投票；有没有一条可核实的事实在推动它；这一段里谁最纯。**

首页上任何元素、任何新增的数据或页面，不服务这句话就折叠或不做。三段各有归属：「哪一段」= 部件篮子相对整机（`api/app/market.py`）；「可核实的事实」= 入账的卡口事件与它的 T+N 反应（`api/app/ingest/accounting.py`、`candidates.py`）；「谁最纯」= 部件上的公司按证据级 × 关联度排序（`physical/`）。

### 分工原则

- **事件的入账与价值判定是系统的事（规则 + AI），不是用户的事。** 规则只挡与归位，判定交服务器上的 AI（PI），人只剩事后「不算」。
- Owner 在这个系统里只做一件事：读首页结论，点进原文，回答「事件 → 二级市场变化」够不够直接、够不够支撑投资决策。任何把确认、分类、归位推给用户的设计都是错的。
- 宁可无结论，不要错结论。没有数据就写「暂无」，不拿默认值（时效 5 天、示例序列）冒充读数；错的因果会让 Owner 对整个系统失去信任，信任是这个产品唯一的资产。

### 进度只用三个数衡量

1. **真事件数**：入账且经得起读原文的卡口事件（目标 ≥ 50，靠历史回填 + AI 判定）。
2. **算得出效力的部件数**：命中率与半衰期在部件级成立的部件（`teardown-accounting-v2.md` §4）。
3. **首页结论的可信比例**：Owner 读原文后同意结论因果的比例——这就是「够不够直接」。

不用公司数、候选数、页面数、代码量衡量进度。多 60 家公司不如多 1 条真事件。

### 「刚刚好」

- 每个屏幕只回答一个问题：一句结论、产生它的读数不超过三个、一个反例，其余按需展开。
- 每个数字过一道检验：它变号，结论会变吗？不会就折叠。
- 每次改动前自问：这个改动让哪一段链更直接——实物 → 公司、公司 → 事件、事件 → 反应、反应 → 结论？答不上来就不做。加数据先问：它能改变某个结论吗？
- 一行只允许一个方向色；图例放在读数旁（列头），不放页脚；阈值在 `api/app/analytics.py`，措辞在 `api/app/insights.py`，两处必须一致。

### 顺序（在事件层闭环之前，不加第二只实物、不扩公司池、不加新页面）

入账 v2（已做）→ PI 回填 + AI 判定 → 部件级效力 → 判断骨架（thesis / confidence 由 AI 判定产出，骨架围绕它长）→ 公司列表带角色与关联度 → 设计预审 D / A → 之后才是 mandate、第二只实物（存储 / PCB）、宏观与筹码层。

## 执行者与交接

- **Claude Code（CC）**：改代码，Owner 已授权直接 push `physical-first`；每步 `pytest` + `npm run build` 过再推；推完出交互 HTML 快照。**CC 读不到 claude.ai Project 里的文档，规格一律以仓库 `docs/claude/*.md` 为准。**
- **PI（服务器）**：部署、跑作业、从网页端补接口拿不到的数据（`POST /api/ingest/upload`）、判候选（`POST /api/candidates/judge`）、出真数据快照并推上来；每次执行记录写 `ops/reports/YYYY-MM-DD-*.md`。PI 不推代码。
- **Cowork**：评审每次推送（代码、真数据、设计层）、画方向稿、写规格；不能 push。
- 交接文档：`docs/claude/teardown-status.md`（先读它）、`teardown-accounting-v2.md`（事件入账规格）、`teardown-design-review-2026-09-29.md`（设计预审 A–D）。每次推送后由 CC 更新 status 的基线与待做，与规格的出入要写明。
- 和 Owner 的约定：中文；UI 改动先出方向稿再实现；不每次推送，确认后再动；合并到 main 要 Owner 点头；给 Owner 看的一律是可交互 HTML，不要 png。

## 是什么（现状）

- `physical/`：实物层。`physical/data/module-1.6t-dr8-siph.json`（schema 0.3：17 部件、211 映射、158 家公司、244 来源；verified / consensus / candidate）是研究事实与稳定 ID；`physical/README.md` 是证据级规则与篮子规则；`coverage-*.json` 是反向扫描全集。
- `api/`：FastAPI + SQLite。`app/ingest/` 是数据接入（行情 东财 → Yahoo → stooq；融资 / 股东户数 / 估值；候选池 巨潮 / 互动易 / RSS；`accounting.py` 入账；`recompute.py` bars → series → 篮子 → 反应）。`app/market.py` 读数，`app/insights.py` 结论句，`app/analytics.py` 阈值与交易日历。
- `web/`：Vite + React 19 + TS，纯 CSS 变量。首页 = 物理页（`/`，`/physical`）：揭盖图 + 十七段部件表 + 事件 / 资金投票；`/layers` 是 main 的九层视图；公司页、研究收件箱、篮子页。
- `tools/snapshot/build.py`：把前端与真 API 数据打成一个可交互 HTML（`physical/dist/teardown-web-snapshot.html`）。
- `ops/`：部署、cron（收盘后 daily 15:35，news 每 3 小时）、给 PI 的步骤与执行记录。
- `data/seeds/cpo/` 是 main 的九层与示例市场层（`is_sample=1`），`data/seeds/physical/companies.json` 是公司主数据；`data/notes/*.md` 是判断笔记。

## 界面

- 唯一规则文件：`docs/product/design-rules.md`（v3）；数值以 `web/src/styles/tokens.css` 为准。改界面前先读它，改完对照「禁区」一节。
- 页面就是背景：不新增卡片、面板、侧边栏、标签页、筛选器家族；只用规则里那几种组件原语。
- 深浅色都必须成立：只用变量，不写死颜色。
- 方向色只有一条轴（`--sig-pos/neg/neu`），只落在方向标记 ▲▼●、带号数字、结论行；正文墨色。
- 结论先行：每个分析段第一行是结论行，方向由阈值决定。没有「裸」读数：每段带 `截至 + 窗口`；拥挤度是状态量不是信号；时效只在部件级效力算出来后才写。
- 证据用词固定：已核验 / 行业图示 / 候选 · 待核验；层 / 环节 / 部件三个词不混用。
- 界面文案中文为主；不出现实现术语、轮次号、边界声明。
- `docs/product/` 里其余 spec 与 `docs/archive/` 只是历史，不作为实现依据。

## 数据与证据

- 实物 JSON 是研究事实，不因界面需要改动；companyId 规则在 `physical/seam.py`（`cn.<code>` / `global.<slug>` / `private.<slug>`），公司改代码走 `data/seeds/physical/company-renames.json`。
- 每条公司 ↔ 部件映射必须带来源与证据级；来源必须打得开且原文确实支持该映射。图示里的份额、BOM%、国产化率不进入产品；没有数据就不放，不放 Unknown 徽章。
- 事件只从候选池经 `accounting.py` 入账（规则 / AI），事件表不手填；反应永远从序列算。人工只剩「不算」（`POST /api/events/{id}/dismiss`）。
- `seed --rebuild` 保留接入数据（bars / 候选 / 运行记录），事件按已入账候选回放；数据源只走免费接口，接口拿不到的由 PI 从网页端 upload。
- 篮子等权、归 100；部件篮子 ≥ 3 家有行情的已核验 / 行业图示公司；整机篮子 = exposures ∪ 核心阶段已核验实物公司。

## 尚未决定、动之前先问 Owner

- 篮子权重是否从等权改为按关联度；跨市场汇率处理。
- 第二只实物（存储 / PCB）的层级与 ID 约定。
- 任何对外发布、合并到 main、删除历史。

## 验证

- API：`cd api && python -m pytest -q`（用例是 unittest 写法，`python -m unittest -q` 亦可）。
- Web：`cd web && npm run build`（含 `tsc --noEmit`）。
- 界面改动附交互快照：`python3 tools/snapshot/build.py --api http://127.0.0.1:8000`；真数据快照在服务器上出。
<!-- PROJECT:OWNED:END -->
