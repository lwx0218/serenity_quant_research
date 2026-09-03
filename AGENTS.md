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
## 项目规则(reboot-v2,2026-09)

### 是什么

Teardown(拆解):以实物部件为入口、落到资金投票的产业链量化投研工作台。Explorer 是同一种视图的递归:容器 → 模块 → 子部件;当前唯一产品是 CPO 光模块。
三层内容:事件(卡口事件 + T+N 反应 + 时效)、判断(`data/notes/*.md`,可证伪)、量化 v1(环节篮子、事件效力、拥挤度)。
技术栈:`web/`(Vite + React + TS,纯 CSS 变量)与 `api/`(FastAPI + SQLite);数据从 `data/seeds/cpo/*.json` 导入,可随时重建。

### 界面

- 唯一规则文件:`docs/product/design-rules.md`;数值以 `web/src/styles/tokens.css` 为准。改界面前先读它,改完对照「禁区」一节。
- 页面就是背景:不新增卡片、面板、侧边栏、标签页、筛选器家族。需要新组件先问能否用现有五种原语拼出。
- 界面文案中文为主;不出现实现术语、轮次号、边界声明。
- 深浅色都必须成立:只用变量,不写死颜色。
- 方向色只有一条轴(`--sig-pos/neg/neu`),只落在方向标记、带号数字、结论行;正文墨色。每个分析段第一行是结论行,方向由阈值决定(`api/app/analytics.py`),措辞在 `api/app/insights.py`。
- 没有「裸」读数:每段带 `截至 + 窗口`;拥挤度是状态量不是信号;事件时效由事件效力的半衰期校准。
- `docs/product/` 里其余 spec 与 `docs/archive/` 只是历史,不作为实现依据。

### 数据与证据

- `cpo-research-seed.json` 是研究事实与稳定 ID,不因界面需要改动;展示文案在 `cpo-presentation.json`。
- 公司 ↔ 环节关系必须带 `evidence_level`(`reference` < `candidate` < `reviewed`),定义见 `docs/research-baseline/evidence-contract.md` §2a。
- 图示里的份额、BOM%、国产化率等数字不进入产品;没有数据就不放模块,不放 Unknown 徽章。
- 市场层示例数据只在 `cpo-sample-market.json`,写库时 `is_sample=1`;真实适配器写同一组表(events / reactions / series / crowding),不新造并行结构。反应永远从序列算,不手填。
- 判断笔记的 front matter 字段以 `api/app/notes.py` 为准;新增字段要能被 Obsidian 手改后无损读回。

### 尚未决定、动之前先问 Owner

- 接哪些真实数据源、抓取频率与存放(公告 / 互动易 / 新闻 / 行情);交易所日历。
- 篮子权重(默认等权)与跨市场汇率处理。
- 新增产品容器(机柜、交换机)时的层级与 ID 约定,以及是否换成物理保真的分层图。
- 任何对外发布、推送或删除历史。

### 验证

- API:`cd api && python -m unittest -q`
- Web:`cd web && npm run build`(含 `tsc --noEmit`);界面改动附截图(总览、选中、深色各一张)。
<!-- PROJECT:OWNED:END -->
