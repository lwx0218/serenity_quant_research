# Teardown 状态与交接 · 2026-09-29

> 放置：`docs/claude/teardown-status.md`。**从现在起以仓库里这份为准**，claude.ai Project 里的同名文档是镜像。Claude Code / PI / Cowork 都从这里读。

## 一句话
从物理出发去覆盖投研：一只真实在用的 1.6T OSFP DR8 硅光模块 → 每个部件背后的公司（带来源的证据级）→ 公司的行情 / 拥挤度 / 事件 → 人的判断。Faye 的定义：先物理，后投研。

## 分工原则（Faye 2026-09-28 定）
**事件的入账与价值判定是系统的事，不是用户的事。** AI（服务器上的 PI）是系统的一部分。Faye 只看结果，判断「事件 → 市场变化」是否足够直接、足够支撑投资决策。人的介入只剩事后「不算」。

## 三个执行者
- **Claude Code（CC）**：改代码，直接 push `physical-first`；每步 `pytest` + `npm run build` 过再推；推完出快照。
- **PI（服务器）**：部署、跑作业、从网页端补数据、AI 判候选、出真数据快照并推上来；执行记录写进 `ops/reports/`。
- **Cowork**：评审（代码、真数据、设计层）、画布方向稿、写规格；不能 push，规格以 `docs/claude/*.md` 交给 CC。

## 当前基线
- GitHub `physical-first`：入账 v2.1（见下）+ 预审 C 剩余 + AGENTS.md 换成 09-29 版（愿景 / 验收标准 / 刚刚好）。main 留着 tag `v1.0-teardown-reboot`，未分叉；合并到 main 要 Faye 点头。
- 服务器（09-29 16:45）：行情 140 / 144 家，截至 09-29；融资 72、估值 73；序列 164 条（含部件篮子）；候选 423 = 规则入账 12 · 例行 365 · 交 AI 46；事件 12（全是噪声，见下）。4 家行情缺口（北交所 920045 / 920060 / 920179 + 台燿 6274.TWO）。
- 证据层：17 部件、211 条映射、158 家公司、244 条来源（verified 158 · consensus 38 · candidate 15）；反向扫描全集 200 家在 `physical/data/coverage-1.6t-dr8-siph.json`。
- 已知问题：互动易 405（源停用）、9 个 RSS 停用（`news_sources.json` enabled:false）、东财长窗口断连（已分段）、run 41 中断未收尾（runner 启动时应把上一条 NULL 的 run 标 failed）。

## 真数据评审结论（Cowork 09-29，快照 56cb689）
后半段通了：部件篮子（5–25 家）、7 天 / 3 个月读数、20 日分位、反应、共振、结论句在真数据上全部算出且内部一致。前半段错了：规则自动入账的 12 条没有一条是这只模块的卡口事件（募资类公告 + Meta / 微软 / TSMC / NVIDIA 泛新闻），真正像卡口事件的在「交 AI」的 46 条里。「够不够直接」现在答不了——事件层还没给出一条真信号。修法是入账规则的设计：**规则只挡与归位，判定交 AI，历史回填凑样本**，规格见 `teardown-accounting-v2.md`。

## 已实现（评审通过）
- 实物层：等距揭盖图、`/physical`（= 首页）、公司页「在实物里的位置」、收件箱「→ 部件」。
- 数据接入 `api/app/ingest/`：行情（东财 → Yahoo → stooq）、融资 / 股东户数 / 估值、候选池、bars → series / 篮子 / 反应；`seed --rebuild` 保留并合并接入数据。
- 「物理页 · 事件 / 资金投票」（→ a0d7ce1）：部件篮子规则（≥ 3 家、module 阶段只在整模块、candidate 不进）、右栏顺序、`/api/physical/{id}/market`、`/parts/{part}/market`。
- 候选自动入账框架（6cb4f58）：`accounting.py::classify`、`candidate_triage` 待办、「不算」override、收件箱状态行、`python -m app.ingest triage`。

## 待做（顺序）
1. ~~**CC**：`teardown-accounting-v2.md` §1–§3（规则 v2、`/api/candidates/judge`、历史回填）→ 预审 C 剩余。~~ 已做（959fe9c、1664645）。
   与规格的出入：NVIDIA 回购那条标题有 buyback，被 §1.1 英文例行词先挡成例行（另一条 NVIDIA 进 triage）；回填对象按「站在任何部件上」算是 72 家 A 股（规格估 42）；
   自动入账的类别取标题动词的类别（「投资建设…产线」→ 扩产）；回填里没取到正文的活动记录表照旧交 AI；活动记录表正文要服务器装 `pypdf`（可选，没装就交 AI 读原文）；
   综合媒体标题门槛会把「亨通光电定增66.36亿，抢滩算力底座」挡成例行（CPO 只在摘要里）。
   **入账 v2.1（09-29，`RULES_VERSION = "v2.1"`）**：例行正则拆成硬 / 软两组，软组（使用募集资金 / 增资 / 借款 / 投资进展 / 土地使用权 / 出让合同 / 调研，
   另把「使用部分募集资金」一并算软组）在标题同时有产品词（强产品词或部件词）与类别动词时不挡——「关于使用募集资金投资建设 1.6T 硅光模块产线的公告」→ 自动入账 · 扩产；
   换版时 `rejudge` 把规则判成例行的（`status='rejected' AND decided_by='rule'`）也重开重跑；`categorize()` 英文关键词按整词匹配（`\b` + ASCII，带可选复数 s），
   fab / order 不再撞 fabric / border。对 09-29 那 46 条交 AI 的真候选分流不变（例行 25 · 交 AI 21）；东财 14 条原先靠英文子串拿到类别的会在下次抓取时失去类别（多为噪声）。
2. **PI**：pull → build → 重启 → `pip install pypdf`（可选）→ `triage`（第一次会把 v1 入账的 12 条重开重判）→ `backfill --since 2025-10-01 --until 2026-09-29`
   → 读 `/api/ingest/todo` 判候选，`POST /api/candidates/judge` 交回 → `recompute` → 出快照、写 `ops/reports/`。（`ops/README.md` 有逐条命令）
3. **CC**：回填出 50 条以上真事件后做 `teardown-accounting-v2.md` §4（效力到部件级 + 部件篮子页）→ 预审 D → 预审 A。
4. **Cowork**：拿到新快照后再做一次真数据评审，回答「够不够直接」。
5. 互动易接口换新；4 家行情缺口（PI 从网页端 upload）。
6. 判断骨架方向稿（thesis / confidence 已由 AI 判定产出，骨架围绕它长）；mandate 再往后。
7. coverage 里 65 条 pending 与 15 条 candidate 逐条补来源；第二只实物（存储 / PCB）。

## 从哪里读起
1. `physical/README.md`（目录、schema 0.3、证据级规则、篮子规则）
2. `ops/README.md`（部署、cron、给 PI 的候选判定与重建步骤）
3. `ops/reports/`（服务器每次执行的记录，最新 `2026-09-29-rebuild-and-accounting.md`）
4. `api/app/ingest/accounting.py`（入账规则）、`news.py::relevance_of`、`api/tests/test_ingest.py`
5. `docs/claude/teardown-accounting-v2.md`、`docs/claude/teardown-design-review-2026-09-29.md`
6. 画布「Teardown 实物剖面 · 1.6T 光模块」（Claude Design，方向稿）

## 工具
- 快照：`python3 tools/snapshot/build.py --api http://127.0.0.1:8000` → `physical/dist/teardown-web-snapshot.html`；真数据快照在服务器上出，提交推上来。给 Faye 的一律是可交互 HTML，不要 png。
- 本地验证：`cd web && npm run build`、`cd api && pytest`。

## 和 Faye 的工作约定
- 中文。先出方向稿再实现；UI 符合 `docs/product/design-rules.md`（v3）；粗糙版本不接受。
- 不每次推送，确认后再动；她定何时合 main。
- 数据源走免费（东财 / Yahoo / stooq / akshare 同款接口）；接口拿不到的让 PI 从网页端取，走 `/api/ingest/upload`。
- 更新节奏：收盘后 daily（15:35），news 每 3 小时；事件由规则 + AI 入账，人只「不算」。
