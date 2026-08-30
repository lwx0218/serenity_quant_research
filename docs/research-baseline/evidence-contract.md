# 研究证据、引用与发布 Contract

## Metadata

- Project: serenity_quant_research
- Document type: research-baseline
- Status: active
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: AGENTS.md

## 1. 目的和强制边界

本 contract 约束 Phase 1 的 `SourceDocument`、`Event`、`Evidence`、`CompanyExposure`、`ResearchConclusion` 和 `ResearchReport`。

核心规则：

1. 机器可以辅助发现、抽取和起草，但机器产物只能进入 `draft`。
2. 报告只能引用 `reviewed` evidence 和 `published` conclusion 的锁定版本。
3. 图片、搜索摘要、聚合页和社交材料只能作为 discovery lead，不能单独支持事实或结论。
4. 任何 NVIDIA 或其他厂商表述首先是 source/event/evidence，不自动构成对上市公司的结论。
5. 支持、反驳和上下文证据必须分开记录，不能把“提及”当成“支持”。

## 2. 来源等级

| level | 定义 | 典型来源 | 可支持内容 | 限制 |
|---|---|---|---|---|
| `A` | 法定、监管或权威一手材料 | 监管/交易所披露，财报与电话会原文，官方标准/实施协议，NVIDIA 等公司的正式产品/技术材料 | 公司身份、财务事实、公司原话、标准定义、正式产品参数 | 仍需记录发布日期、版本和准确定位；管理层展望不等于已实现事实 |
| `B` | 可追责的一手发布或高可信专业二手来源 | 公司新闻稿/博客，行业机构，会议材料，具名专业媒体或研究机构 | 事件、技术解释、交叉验证与上下文 | 涉及订单、客户、收入或量产时应回到 Level A；不得掩盖转载链 |
| `C` | 聚合、转载、搜索摘要、匿名/社交内容 | 聚合新闻、概念股表、论坛、社交媒体、两张 seed JPEG | 关键词、候选公司、待核验问题 | 只能创建 discovery lead；不得单独支持 exposure、conclusion 或 report claim |

若同一内容有更靠近原始发布者的来源，必须引用最接近原始的版本。付费墙、动态页面或视频不降低等级，但必须保存合法可用的定位信息；不得绕过访问控制。

## 3. Evidence 审核状态

### 状态定义

| state | 含义 | 允许动作 |
|---|---|---|
| `draft` | 人工或机器创建，字段可能不完整 | 编辑、补来源、提交审核、删除未引用草稿 |
| `in_review` | 已提交人工审核，内容冻结供 reviewer 检查 | reviewer 退回、通过或拒绝 |
| `reviewed` | 来源、原文、定位、对象关联和 stance 已人工确认 | 可被 conclusion/report 引用；修改内容必须生成新版本 |
| `rejected` | 来源无效、摘录错误、关联不成立或重复 | 不得引用；保留原因与审计记录 |
| `superseded` | 曾经有效，但已由更新版本取代 | 历史引用仍可解析；新结论默认不得引用 |

允许的转换：

```text
draft -> in_review -> reviewed
                  -> rejected
in_review -> draft            (退回修改)
reviewed -> superseded         (只能由新 evidence 版本取代)
```

禁止 `draft -> reviewed` 的无审核跳转，禁止就地修改已审核内容，禁止机器身份执行 review。

### 结论与报告状态

- Conclusion：`draft -> in_review -> published -> superseded | withdrawn`
- Report：`draft -> generated -> reviewed -> published -> superseded`
- 结论或报告被撤回/取代后，旧版本和当时锁定的引用仍须可审计，但默认页面必须显示状态警告。

## 4. Evidence 最小记录

每条 evidence 至少包含：

- 稳定 `evidence_id` 与不可变 `version`
- `source_document_id`、source level、发布者、标题、原始 URL
- publication time、capture time；若是事件，再单列 event time
- 内容指纹（原文/PDF/页面快照的 SHA-256）和合法保存方式
- 精确定位：页码/章节/表格/公告编号，或视频 `HH:MM:SS-HH:MM:SS`
- 最小必要原文 quote；另存 analyst paraphrase，禁止两者混写
- 语言和翻译；翻译必须保留原文
- 关联的 theme/company/part/chain node/technology/event
- stance：`supports` / `contradicts` / `contextualizes`
- 被评估的 proposition；不得只写泛化“利好/利空”
- reviewer、reviewed_at、审核备注
- freshness/staleness 状态和版权/访问限制

网页无法合法留存全文时，只保存最小必要摘录、元数据、指纹和回链；不要把抓取便利性当成使用授权。

## 5. 引用规则

### 引用键和显示

- Evidence 引用键：`EVD-<year>-<sequence>@v<version>`
- Conclusion 引用键：`CON-<year>-<sequence>@v<version>`
- 报告中的每个 material claim 紧邻显示引用键，并可回链到 evidence 详情。
- PDF/打印版引用附录必须包含发布者、标题、日期、locator、URL、capture time、版本与 source level。

### 引用粒度

1. 一条 citation 只能覆盖其来源实际支持的命题，不允许段尾引用覆盖多个无关事实。
2. 财务数字必须记录币种、单位、期间、口径（reported/adjusted）和表格定位。
3. 视频必须有时间戳；电话会必须区分 prepared remarks 与 Q&A。
4. 翻译引用同时显示原文定位；机器翻译不能替代 reviewer 对关键术语的确认。
5. 转载材料应回溯原始发布；找不到原始材料时最多为 Level C discovery。
6. 同一 URL 更新内容时以内容指纹和 capture time 区分版本。
7. 图片中的公司、成本占比、技术参数和产业关系不得作为 citation。

## 6. 审核检查单

Reviewer 必须逐项确认：

- 来源身份、URL/文件、发布日期和 source level 正确；
- quote 与原文逐字一致，locator 可复现；
- paraphrase 没有扩大时态、确定性或适用范围；
- company/part/chain/event 关联不是由图片或关键词自动推导；
- stance 与 proposition 匹配；
- “研发/送样/验证/量产/形成收入”被严格区分；
- 客户、订单、供应关系和份额没有越过披露边界推断；
- 已检查更新材料、反证和失效信息；
- 版权、个人信息、付费访问和保密限制有记录；
- 审核者不是仅对自己的机器草稿做形式性批准；Phase 1 至少记录独立人工确认。

## 7. 结论发布门槛

`ResearchConclusion` 只有同时满足以下条件才能进入 `published`：

1. 明确、可证伪的 proposition，不使用无边界的“受益”“龙头”等标签。
2. 至少一条直接相关的 `reviewed` Level A evidence；若只能取得 Level B，必须有两条相互独立的 reviewed B 且显式降低 confidence。
3. Level C 不能计入发布门槛。
4. 已检索并关联合理的 contradicting evidence；没有找到也须记录检索范围，而不是留空。
5. 涉及公司与 part/chain 的 exposure 必须已达到 `verified`，不能从行业趋势直接外推公司订单。
6. 记录 confidence、time horizon、关键假设、风险、反证和 invalidation conditions。
7. 财务/Capex/投资类命题至少有对应期间的法定披露或公司正式材料。
8. 所有 material claim 均能解析到具体 reviewed evidence 版本。
9. 人工 publisher 完成审核；机器身份不能发布。

### Confidence 口径

- `low`：证据仍有限或关键映射依赖 Level B；允许发布的前提是清楚表达不确定性。
- `medium`：一手证据支持核心命题，但规模、时点或客户等关键变量仍不完整。
- `high`：多条独立 Level A 证据覆盖核心事实、边界和反证；不代表预测必然实现。

confidence 不是投资评级，不映射买入/卖出。

## 8. 报告发布门槛与版本锁定

报告从 `generated` 进入 `published` 前必须：

- 所有 conclusion 均为 `published`，并锁定 `conclusion_id + version`；
- 所有直接 citation 均为 `reviewed`，并锁定 `evidence_id + version`；
- 不含 `draft`、`in_review`、`rejected`、`stale` 或仅 Level C 支持的 material claim；
- 风险、counter-evidence 和 invalidation conditions 章节非空；
- 引用附录中的每个引用都可打开原始来源或合法保存的元数据记录；
- 生成后 evidence/conclusion 的新版本不会静默改变旧报告；
- 完成人工 report review，并记录生成时间、reviewer 和发布者。

## 9. Freshness 默认值

默认值只触发复核，不自动判定事实失效：

| source/evidence 类型 | 默认复核阈值 |
|---|---|
| 新闻、事件、产品路线与管理层展望 | 90 天 |
| 公司产品页、演示材料、产业机构材料 | 180 天 |
| 季报/半年报 | 下一报告期发布后 |
| 年报 | 下一年报发布后，最长 450 天 |
| 标准/Implementation Agreement | 365 天检查是否被修订或替代 |
| 已披露历史财务事实 | 不因时间自动失效，但须保持期间标签 |

## 10. 两张 seed JPEG 的来源、使用权和事实风险

| 项目 | `docs/references/cpo-3d-components.jpeg` | `docs/references/cpo-industry-chain.jpeg` |
|---|---|---|
| 文件规格 | JPEG/JFIF 1.01，1080×1440 | JPEG/JFIF 1.01，1080×1440 |
| SHA-256 | `a72409bcbc077beb682117abfa74d499c051a78e2ba3c1f69968fbd5a1e26e76` | `69db333ba0e507aa0a5ec1ab0343290dedec15e6dfa42832380100d2309e572d` |
| 图内署名 | “作者：图财社” | “作者：图财社” |
| 图内数据源 | “公开资料整理 / 行业报告 / 公司公告（2024–2025）” | “公开资料整理 / 行业报告 / 公司公告（2024→2026）” |
| 嵌入元数据 | 未发现可证明作者、创建时间、许可证或来源 URL 的 EXIF/文本元数据 | 同左 |
| 来源链 | 原始发布 URL、取得方式、创作主体法律身份未确认 | 同左 |
| 使用权 | 未发现许可证或书面授权；署名不等于获得复制/改编权 | 同左 |
| P0 结论 | 仅作内部 seed reference 和 discovery lead | 仅作内部 seed reference 和 discovery lead |

### 图片控制措施

1. 正式页面不得复制 JPEG、抠图、描摹其独创画面或实现静态热区图。
2. P2 SVG 必须依据已审核 taxonomy 自主设计几何、布局、文案和视觉语言，并保留创作记录。
3. 若未来需要公开展示原图，必须先取得可验证的原始发布 URL、权利主体和明确许可范围。
4. 图中 9 层、10 个产业链区、公司映射、成本占比、速率、产品形态和时间均为待核验线索。
5. 图像可能是示意拼装，不能据此断言物理位置、尺寸、接口、良率、供应商或量产状态。
6. 在 provenance 未解决前，应用 seed 不保存图片推导的 `verified` exposure/evidence。

## 11. 最小角色

- `ResearchMaintainer`：创建/编辑 draft、提交审核。
- `ResearchReviewer`：review/reject evidence 和 conclusion；不得由机器账号担任。
- `ResearchPublisher`：发布 conclusion/report；Phase 1 可与 reviewer 是同一受控人工账号，但审计动作必须分开记录。

复杂组织权限延后；以上三类能力边界不得省略。
