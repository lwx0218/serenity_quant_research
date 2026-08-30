# 文档目录

## Metadata

- Project: serenity_quant_research
- Document type: index
- Status: active
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: AGENTS.md

本目录保存项目级产品合同、研究事实基线、项目入口信息和长期参考材料。交付过程、计划、工作日志与评审证据统一放在 `operations/`，不与本目录混放。

## 目录结构

| 路径 | 用途 | 权威边界 |
|---|---|---|
| `manual/` | 项目本地文档治理、操作 reference 和长期维护标准 | 文档放置、命名、Metadata、legacy exception 与 checker 规则；入口见 `manual/document-governance.md` |
| `product/` | Research Experience Reboot 的产品目标、体验地图、页面规范、视觉语言、验收合同和原型 | research-facing UI / UX 的产品事实源；具体优先级见 `product/README.md` |
| `project-intake/` | 项目入口、边界、当前基线和稳定输入 | 项目概览，不替代产品合同或执行计划 |
| `research-baseline/` | CPO taxonomy、公司候选池、evidence/review/publication 语义 | 研究事实与证据状态的基线；不由 Prototype mock data 覆盖 |
| `references/` | 图片、历史调研总结等长期参考输入 | 仅供 discovery 和溯源，不自动构成已核验证据或产品事实 |

## 与 `operations/` 的分工

| 路径 | 放置内容 |
|---|---|
| `operations/planning/` | 已批准 Plan、rebaseline、治理维护计划、superseded pointer |
| `operations/orchestration/` | 执行流程、handoff/review loop、Independent Review scope 标准 |
| `operations/work_logs/` | factual 工作日志、验证记录、收口状态 |
| `operations/reviews/` | disposition audit、Independent Review、human review artifact |
| `operations/archive/` | 已 supersede 的历史计划与原文证据 |

`docs/` 不存放一次性 handoff、临时压缩包、runtime residue 或验收过程日志。

## 阅读顺序

涉及 research-facing 产品任务时，按根 `AGENTS.md` 声明的顺序读取，核心入口为：

1. `product/README.md`
2. `product/experience-map.md`
3. 对应页面规范
4. approved / directional prototype
5. `product/visual-language.md`
6. `product/acceptance-contract.md`

涉及研究事实、evidence state、review、publication 或 audit 时，优先读取：

1. `research-baseline/evidence-contract.md`
2. 对应 taxonomy / company baseline
3. repository 中已评审的 durable evidence

涉及治理、Round、handoff 或 Independent Review 时，优先读取：

1. 根 `AGENTS.md`
2. `manual/document-governance.md`（仅文档治理/格式维护时）
3. `operations/orchestration/independent-review-and-round-scope-standard.md`
4. 当前 approved Plan
5. 当前 work log / review artifact

## 维护约定

- 面向 Owner 的聊天总结、交付说明和状态报告默认中文。
- 新增或实质更新的文档正文默认中文；代码标识、文件名、命令、协议字段和必要原文引用可保留英文。
- 已批准或已归档的英文历史证据不因本规则自动全文翻译；需要修改时优先补中文状态说明，避免破坏原始审计语境。
- 不在 `docs/` 顶层堆放临时压缩包、一次性交接文件或运行产物。
- 压缩包完成导入并验证后删除，不作为长期事实源。
- 移动长期文档或参考材料时，必须同步更新有效文档中的路径引用。
- `operations/archive/` 中的历史原文保持原样；其中旧路径只代表当时状态。

## 当前整理结论

- `docs/references/` 是长期参考材料的正确位置。
- 原 `docs/CPO_3D.jpeg`、`docs/CPO_FUll.jpeg`、`docs/serenity_finance_research_summary.md` 迁入 references 的方向保留。
- 临时 zip 与一次性 handoff 文件完成导入后删除，不进入长期事实源。
- 上述整理属于文档治理维护，不属于 R1 产品审计 candidate。
