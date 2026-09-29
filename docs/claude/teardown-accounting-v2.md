# 事件入账 v2：规则只挡与归位，判定交 AI；历史回填；效力到部件级

- 项目：serenity_quant_research · 分支 physical-first
- 文档类型：实现规格（给 Claude Code 执行）
- 日期：2026-09-29 · 作者：Cowork（Faye 授权）
- 依据：09-29 真数据快照（56cb689）的评审；Faye 09-28 定的分工原则
- 放置：`docs/claude/teardown-accounting-v2.md`，提交进仓库；后续状态以仓库 `docs/claude/` 为准

## 0. 为什么改

真数据上规则自动入账的 12 条，没有一条是这只模块的卡口事件：6 条 A 股公告是募集资金置换 / 增资 / 借款 / 开专户 / 土地出让合同（「募投」被当扩产、「合同」被当订单）；5 条 DIGITIMES 是 Meta 眼镜、微软液冷、TSMC 新加坡厂、NVIDIA 回购（标题里有公司名 + 一个类别词；Meta / 微软不在任何部件上）。真正像卡口事件的三条（铭普 800G LPO 小批量出货、汇绿 3.09 亿光模块产线、亨通 66 亿定增算力底座）都在「交给 AI」的 46 条里。

结论：**关键词判不了「这条事件是不是关于这个部件」**。规则只负责挡掉例行、把事件归到部件；算不算、值不值，交给 AI（PI，服务器上有 web-access）。AI 是系统的一部分，这不违反「人不逐条确认」。现阶段准确率比召回率重要——噪声事件会污染效力统计。

## 1. 规则 v2（`api/app/ingest/accounting.py::classify` 重写）

输入一条候选 `c`（candidates 行 + `companies` JSON），输出三路之一：`routine`（不算）/ `auto`（入账）/ `triage`（交 AI）。顺序如下，前一步命中即返回。

### 1.1 挡：例行与噪声 → `routine`

- `relevance = 0` → routine（现有）。
- 标题命中扩充后的例行正则 → routine。`news.py::ROUTINE_ANNOUNCEMENT` 在现有基础上追加：
  `募集资金置换|募集资金专户|募集资金存放|使用部分募集资金|使用募集资金|自筹资金|增资|借款|担保|土地使用权|出让合同|投资进展|中签|发行价|IPO|上市公告书|招股|询价|三季报|半年报|年报|预约披露|财经早餐|利好消息一览|公告最新快递|重大事项公告|晚间公告|涨停|跌停|市值|回购|调研|机构密集|一览|名单|早盘|午盘|收评`
  英文（对 rss / upload）：`buyback|share price|market cap|glasses|VR|smartphone|earnings call|dividend|layoff|lawsuit`
  例外保留：标题含「投资者关系活动记录」的不挡（现有），但它没有类别，走 triage（见 1.4）。
- 「投资者关系活动记录表」标题本身没信息：在入 triage 前把 `summary` 补成公告正文前 600 字（news.py 抓取时对该类公告多取一次正文；取不到就照旧交 AI 读原文）。

### 1.2 归位：公司必须站在某个部件上

- `ids = _companies(c)`；`len(ids) != 1` → triage（现有，理由「命中 N 家」/「没命中」）。
- `part = physical.part_for_event(conn, company_id, category)`；**`part is None`（公司不在任何实物部件上，如 Meta / Microsoft / 需求侧）→ routine**，理由「公司不在这只模块的任何部件上」。需求侧事件以后另开一桶，本轮不做。
- 部件初判：`news.match_entities` 命中的 `part_ids` 里如果有这家公司站着的部件，取它；否则取 `part_for_event` 的结果。写进 `candidates.part_id`（新列）。

### 1.3 强命中 → `auto`

同时满足才自动入账，否则进 triage：

1. 来源 tier 0（巨潮公告 / 互动易，或 upload 且 `tier=0`）。
2. 标题或摘要含部件词表（`match_entities` 的 parts 命中）**或**强产品词：`1\.6T|3\.2T|800G|硅光|光模块|CW\s*光源|CW\s*激光|EML|DR8|OSFP|光引擎|FAU|MPO|MT\s*插芯|高多层|M8|光芯片|InP|TIA|DSP`（DSP / TIA 只在与光模块词同现时算）。
3. 标题含类别动词：`投资建设|新建|扩建|产线|投产|签订.*合同|中标|框架协议|供货协议|批量出货|小批量|送样|通过.*认证|导入|涨价|提价|调价`。
4. 类别 ∈ 六类，且有日期。

自动入账时写 `decided_by='rule'`、`thesis = 标题`、`confidence = 3`。

### 1.4 其余 → `triage`（交 AI）

包括：tier 0 但不是强命中（含投资者关系活动记录表）、tier 1 行业媒体（不再用「另有一家报道」入账）、tier 2 综合财经。
tier 2 的额外门槛：标题不含部件词表或强产品词的，直接 routine（别把「中签率」「财经早餐」喂给 AI）。
每条开一个 `ingest_todo`（kind=`candidate_triage`，company_id 列放候选 id，现有做法），hint 改成结构化任务（见 §2）。**7 天未判的待办自动 `dropped`**，候选保持 pending（`runner.job_news` 末尾清理）。

### 1.5 已入账的 12 条

全部 `candidates.reopen` 后按 v2 重判（多数会变 routine 或 triage）；`replay` 保证事件表随之更新。人工「不算」过的不动（现有约束）。

## 2. AI 判定：结构化交回

### 2.1 待办的 hint（PI 读到的任务）

```
判断这条候选是不是「<公司> 在 <部件初判> 上的卡口事件」：「<标题>」<url>（来源 <source>，<date>）。
卡口事件 = 会改变这家公司在这个部件上的供给 / 需求 / 价格 / 技术路线的事：扩产（新产线、投产）、订单合同、认证导入（送样、批量出货、通过认证）、供需（缺货、交期、分配）、涨价、技术路线（CPO / LPO / 硅光 / 1.6T 路线变化）。
不是：融资安排、股权变动、人事、会议、财报预告、泛行业新闻、与这只 1.6T 光模块无关的业务。
交回：POST /api/candidates/judge，见格式。
```

### 2.2 批量交回接口（新）

`POST /api/candidates/judge`，body：

```json
{"by": "ai", "items": [
  {"id": "cand.xxxx", "is_chokepoint": true, "part_id": "part.cw-laser", "category": "qualification",
   "date": "2026-09-21", "thesis": "源杰 100mW CW 光源通过两家硅光模块客户验证，CW 激光器这一段的国产供给多了一家可用的", "confidence": 4, "reason": "互动易原文明确写…"},
  {"id": "cand.yyyy", "is_chokepoint": false, "reason": "募集资金用途变更，与产线无关"}
]}
```

- `is_chokepoint=true` → `candidates.confirm(..., company_id=候选公司, category, event_date=date, note=reason, by="ai")`，并写 `thesis / confidence / part_id`。
- `is_chokepoint=false` → `candidates.reject(note=reason, by="ai")`。
- `confidence` 1–5（AI 对「这是卡口事件且归位正确」的把握）；`thesis` 一句话：这件事对这个部件意味着什么。这两项就是 Vibe-Trading 那条「可靠性打分」和判断骨架的种子，先存起来，UI 下一轮再用。
- 返回每条的结果与错误；一批最多 200 条；处理完统一 `rebuild_reactions` 一次。
- 单条接口 `/confirm` `/reject` 保留，也接收 `thesis / confidence / part_id`。

### 2.3 存储

`schema.py::MIGRATIONS` 追加：
- `candidates`: `part_id TEXT`、`thesis TEXT`、`confidence INTEGER`、`origin TEXT NOT NULL DEFAULT 'live'`（live / backfill）。
- `events`（main 的表，同样用 ALTER 补列）: `thesis TEXT`、`confidence INTEGER`、`decided_by TEXT`、`part_id TEXT`。
- `_write_event` 写入这四列；`market.event_public` 带出 `thesis / confidence / decided_by`；`part_for_event` 优先用 `events.part_id`（AI 归位过的以它为准）。

## 3. 历史回填

目的：立刻得到 50–100 条真事件，让部件级效力（§4）现在就能算，而不是等半年前向积累。

### 3.1 巨潮公告回填（`python -m app.ingest backfill --since 2025-10-01 --until 2026-09-14`）

- 对象：实物层上的 A 股公司（`companies` 里 exchange ∈ SSE/SZSE/BSE 且站在某个部件上，约 42 家）。
- `news.fetch_cninfo_announcements` 加 `sdate / edate / pageNum` 参数，按月分段、翻页到空；沿用连续 5 家失败即停的熔断；段间歇 0.5 s。
- 入库 `candidates`，`origin='backfill'`，`fetched_at` 记回填时间。
- 回填的候选**先过 §1.1 挡、§1.2 归位**，然后：只有强产品词或部件词命中的进 triage，其余直接 routine（回填量大，AI 只读有可能的）。预期：42 家 × 12 月 × ~15 条 ≈ 7,500 条 → 挡掉 ~90% → 交 AI 300–600 条。
- 强命中的照 §1.3 自动入账。

### 3.2 媒体回填（PI 从网页端）

DIGITIMES / 讯石 / C114 / 光纤在线 近 6 个月的光模块栏目，PI 用现有 `POST /api/ingest/upload {kind:"candidates", …}` 交回，每条带 `origin:"backfill"`（upload 接口加此可选字段）、`tier`（行业媒体 1）。进池后走同一套规则 → 大多数进 triage → PI 自己判 → `/judge`。

### 3.3 回填之后

`python -m app.ingest recompute`（反应按事件日算，历史事件 T+20 完整）→ §4 的效力即可计算。回填的事件在页面上与 live 事件无区别，但 `origin` 保留，效力统计可分开看。

## 4. 事件效力到部件级（设计预审 B）

现在 `market.efficacy_for(node_id, days=90)` 只按 main 的层算；部件右栏没有效力块，`insights.basket` 在 `efficacy=None` 时把常量 `DEFAULT_VALIDITY_DAYS` 写成「时效约 5 天」。

- 新增 `market.efficacy_for_part(conn, part_id, days=365, when=None)`：事件 = `part_for_event`（或 `events.part_id`）落在该部件、`status != 'ignored'` 的事件；参照 = 部件篮子（不成篮子时整机）；`A.efficacy(paths)` 不变。窗口用 365 天（回填后才有样本），每周重算并缓存；样本 `n < 5` 返回 `{"n": n, "insufficient": True}`，页面写「样本不足（N 条），不下结论」。
- 部件右栏在「资金投票」之后加「事件效力 · 这个部件」四行：样本（按类别计数）· 平均反应 T+1 / T+5 / T+20 · 命中率 · 半衰期；头部 `截至 · 窗口 365 天 · 每周重算`。样本不足只出一行。
- `insights.basket`：`efficacy=None` 或 `insufficient` 时删去「时效约 N 天」分句。
- `validity_days`（事件时效）改为按部件效力校准，无效力时才用默认 5 天。
- 首页「资金投票 · 按部件」表加一列「命中率」，`n ≥ 5` 才显示，否则「—」。
- 层篮子页 `/baskets/<layer>` 整页改成部件篮子页 `/baskets/part.*`：结构不变（结论 → 走势 → 事件效力 → 篮子拥挤度 → 成分 → 其他部件），层篮子只从 `/layers` 进。

## 5. 收件箱状态行（补充）

现有一行「入账（规则 / AI）· 交给 AI 判 · 例行 · 不算」基础上加：`回填 N 条 · 其中入账 M` 和 `待办超期已作废 K`。运维词汇（可取 / 真 · 示例 / 交给 AI 补）从页头移到页脚一句「行情截至 … · 事件 N 条（其中回填 M）」。

## 6. 验收

1. 单测：09-29 真数据里那 12 条标题作为夹具，v2 规则下 0 条 auto（募资类 routine、Meta / 微软 routine（不在部件上）、TSMC / NVIDIA 进 triage）；铭普「800G LPO 光模块已实现小批量出货」（东财 tier 2）进 triage；一条构造的「关于投资建设硅光光引擎产线的公告」自动入账。
2. `/candidates/judge` 一批 3 条（true / false / 缺字段报错）。
3. 回填在测试里用 mock 的 cninfo 返回跑两个月，候选 `origin='backfill'`，规则分流计数正确。
4. `efficacy_for_part` 在 `tests/scenario_physical.py` 上样本不足与够数各一个断言。
5. pytest + `npm run build` 通过再推；推完服务器：`git pull` → build → 重启 → `python -m app.ingest triage`（重判现有）→ `backfill` → PI 判 → `recompute` → 出快照推上来。

## 7. 顺序

本文 §1–§3（规则 v2 + judge 接口 + 回填）→ 预审 C 剩余（`overview` 无活跃篮子那句的单位；`basket()` 常量时效句）→ 等回填与 AI 判定出 50 条以上真事件 → §4 效力到部件级 → 预审 D（卫生项）→ 预审 A（公司池 / 公司页 / 研究页按实物重排）。A / B / C / D 的全文见 `docs/claude/teardown-design-review-2026-09-29.md`。
