# AGENTS.md

<!-- HARNESS:MANAGED:START -->
## Harness Managed Execution Contract

本仓库采用 PI-first `simple` 默认模式。本分区由 Harness starter/updater 管理；项目产品、领域、安全和运行时规则请写在 `PROJECT:OWNED` 分区。

### Authority

- 本文件是模型执行合同；冲突时优先于 README、human manual、`.pi/` 和历史 evidence。
- `.pi/` 只是 capability layer，不是 policy authority。
- extension、skills、prompt templates 默认 passive；不会因为存在而自动启用 formal workflow。

### Owner-Facing Language

面向 Owner 的聊天总结、交付说明、状态报告和控制门提示默认使用中文。治理文档新增或实质更新默认使用中文；文件名、命令、代码标识、协议字段和必要原文引用可保留英文。

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

### Document And Evidence Governance

新增或实质更新 Markdown 时先判定承载位置：

- `docs/**`：长期说明、manual、reference、project intake 与导航；使用 kebab-case 文件名和最小 Metadata。
- `operations/**`：事件型 durable evidence；使用 `YYYY-MM-DD-<slug>.md` 日期前缀与任务型 Metadata。
- reusable 模板放在 `assets/templates/**`；项目本地没有 reusable 模板目录时，不把模板塞进 `operations/**`。
- `operations/archive/**` 保持历史原貌，不因新格式规则批量重写；默认 active navigation 不读取 archive，也不激活旧 workflow。

项目 evidence 默认保存在项目本地 `docs/project-intake/` 与 `operations/`。只有进入 Plan、跨 session/交接、合同/bootstrap/portability 变更或正式 review trail 时，才默认写 durable evidence。

详细格式见 `docs/manual/document-governance.md`；若该文件不存在，以本 `AGENTS.md` 分区规则为准，并优先创建/补齐该 reference，而不是临时发明新目录规则。

### Evidence And Safety

高风险、破坏性、外部授权、scope/acceptance 改变或验证失败时 fail closed 并询问 Owner。不自动 push。
<!-- HARNESS:MANAGED:END -->

<!-- PROJECT:OWNED:START -->
## Project Document Governance

Project-local Markdown governance is defined in `docs/manual/document-governance.md`. For new or substantively updated governance/evidence documents, prefer project-local paths under `docs/**`, `operations/**`, and `assets/templates/**`; do not depend on external workspace paths or historical archive conventions as active policy.

Canonical product delivery authority remains `operations/planning/research-experience-reboot.md`. Document-format cleanup must not change product authority, research facts, evidence/review/audit semantics, accepted Round state, or R6 start requirements.

## Product Reboot Gate

当前 approved product baseline 是 **Research Experience Reboot**。P0–P3 工程实现、tests、work logs 和 reviews 继续作为有效工程历史；与 `docs/product/` 冲突的 research-facing UI / UX 不再是产品事实源。旧 P4 不得继续；当前交付到 Explorer → Company → read-only Workspace，完整长期闭环仍保留 Workspace → Evidence → Review → Conclusion → Report。

涉及 research-facing UI、UX、navigation、page structure、interaction、frontend shell 或 workflow 的非 trivial 任务，按以下顺序读取：

1. 本文件和适用 scoped `AGENTS.md`
2. `docs/product/README.md`
3. `docs/product/experience-map.md`
4. task-specific page spec
5. approved/directional prototype
6. `docs/product/visual-language.md`
7. `docs/product/acceptance-contract.md`
8. approved active Plan 与 orchestration
9. current implementation
10. legacy product plans/work logs

研究事实、evidence state、review、publication 和 audit 语义仍以 `docs/research-baseline/evidence-contract.md` 与 reviewed repository evidence 为准。Prototype 只定义交互/视觉方向，不得把 mock data 变成 seed、database、research copy、company exposure、conclusion 或 report。

Serenity 继续承载 host、service/data、permission、audit、migration 和 admin maintenance，但不是 research-facing 产品设计依据。不得因为框架已有能力而静默新增 primary page、top-level navigation、permanent research sidebar、tab/filter/metric/comparison family 或 research-facing admin entry。

Product-visible review 必须先验证 objective、IA、interaction、visual hierarchy 和 research-data safety，再看 accessibility、tests 与 build。Prototype 的 hit-zone、overlap、keyboard 或 mock-state 局限是 production acceptance defect，不是默认接受项。

Workspace v1 是 `read-only + linked-object-first`，不得新增 ResearchNote、OpenQuestion、Backlink、Graph 或 editor persistence。受信任隔离环境可保留 `OpenAccess:Enabled = true`；任何新 persistent research writing 开始前，必须就 identity、author attribution、audit ownership 和 all-admin Open Access 影响重新取得 Owner 决策。

只主动升级会改变 primary product area、core user path、persistent domain/schema、research evidence/audit semantics，或造成明显不可逆/高成本架构投入的问题。普通 visual、CSS、component、hit-region、test 和 screenshot 细节使用安全默认并在 review 中展示。

Canonical delivery authority：`operations/planning/research-experience-reboot.md`。不得自动连续推进 fixed Rounds。
<!-- PROJECT:OWNED:END -->
