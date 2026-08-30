# Document Governance

## Metadata

- Project: serenity_quant_research
- Document type: manual-reference
- Status: active
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: AGENTS.md

## Purpose

本文定义 `serenity_quant_research` 的项目本地 Markdown 治理标准，用于统一新增或实质更新治理文档、产品/研究 reference、Plan、work log、review 和可复用模板时的承载位置、命名、Metadata、链接和验证方式。

本标准是自包含的项目规则；它不依赖外部 workspace 的运行时继承，也不把历史 archive 约定当作当前 policy。

## Scope

适用范围：

- `README.md`、`Harness_manual.md`、`AGENTS.md` 等根部治理入口；
- `docs/**` 下的长期说明、manual、reference、project intake、product baseline、research baseline 和导航；
- `operations/**` 下的 Plan、orchestration、work log、review、durable evidence 和 archive index；
- `assets/templates/**` 下的项目本地 reusable Markdown 模板。

不适用或仅 warn-only 的范围：

- `operations/archive/**`：历史 evidence，保持原貌；
- 第三方原文、许可证、vendored dependency README、外部引用镜像；
- 代码、配置、测试、schema、seed、database、生成产物、截图和运行时 `.pi/**` 文件。

格式清理不得改变 product authority、research facts、evidence/review/audit semantics、accepted Round state 或 R6 start requirements。

## Directory Meaning

### `docs/**`

`docs/**` 承载相对稳定的说明性文档，回答“项目、产品、研究基线或机制是什么、为什么存在、怎样使用”。稳定文档使用主题命名，不使用事件日期表达生命周期。

常用子目录：

- `docs/manual/**`：项目本地 manual、治理标准、操作 reference；
- `docs/project-intake/**`：项目 intake、边界、当前 baseline 和稳定输入；
- `docs/product/**`：Research Experience Reboot 的产品事实源、体验地图、页面规格、视觉语言和验收合同；
- `docs/research-baseline/**`：研究事实、evidence state、review、publication 和 audit 语义；
- `docs/references/**`：长期参考输入、历史总结和 discovery material；不自动构成已核验证据或当前产品事实。

### `operations/planning/**`

`operations/planning/**` 承载 Plan、approved scope、acceptance boundary、stop conditions 和任务级授权证据。

- canonical Plan 可使用稳定主题名；当前 canonical delivery authority 是 `operations/planning/research-experience-reboot.md`；
- ad-hoc Plan 使用事件日期前缀：`operations/planning/YYYY-MM-DD-<slug>.md`；
- superseded pointer 可保留稳定主题名，但 Metadata 必须标明 `Status: superseded` 并指向当前 source of truth。

### `operations/orchestration/**`

`operations/orchestration/**` 承载 active orchestration contracts、scope standards、governance backlog 和流程边界说明。

- 稳定 operational contract 使用 `operations/orchestration/<kebab-topic>.md`；
- 一次性事件 evidence 才使用 `YYYY-MM-DD-<slug>.md`；
- orchestration 文档不得自动创建 fixed Round、handoff 或 review obligation，除非 Owner 已明确启用 formal mode。

### `operations/work_logs/**`

`operations/work_logs/**` 承载执行记录、验证记录、已交付边界和后续决策。它回答“做了什么、验证了什么、哪些风险/问题留下”。

- fixed-Round work log 使用 `operations/work_logs/research-experience-reboot-rN.md`；
- ad-hoc work log 使用 `operations/work_logs/YYYY-MM-DD-<slug>.md`；
- work log 可保留顶层 parser label：`Round:`、`Plan:`、`Git baseline:`。

### `operations/reviews/**`

`operations/reviews/**` 承载 Independent Review、disposition、finding evidence 和截图 evidence 目录。

- fixed-Round review 使用 `operations/reviews/research-experience-reboot-rN-independent-review.md`；
- ad-hoc review 使用 `operations/reviews/YYYY-MM-DD-<slug>-review.md`；
- review 可保留顶层 parser label：`Round:`、`Review role:`、`Decision:`、`Unresolved P0/P1/P2:`；
- screenshot 或 binary evidence 目录不受 Markdown checker 格式化。

### `operations/archive/**`

`operations/archive/**` 承载历史证据归档。默认 active navigation 不读取 archive，也不激活旧 workflow。归档文件不因新格式规则批量重写；只有在明确触碰该文件并获准修复时，才做最小 link 或 Metadata correction。

### `assets/templates/**`

`assets/templates/**` 承载 reusable Markdown 模板。模板使用占位符，不写虚构批准、虚构 timestamp、pass verdict、research facts 或 Owner 决策。

## Stable Naming Rules

### Stable docs

稳定说明文档使用 kebab-case `.md`：

```text
docs/manual/document-governance.md
docs/product/experience-map.md
```

规则：

- 小写英文、数字、连字符；
- 文件名表达稳定主题，不强制日期；
- 避免 `final`、`new`、`temp`、`copy` 等状态词；
- `README.md` 只用于目录导航/index。

### Root and manual exceptions

以下文件是命名例外：

- `README.md`：项目根导航；
- `Harness_manual.md`：人类操作入口，保留现有名称；
- `AGENTS.md`：模型执行合同，保留 managed/project 分区；
- 任意目录下的 `README.md`：仅用于该目录导航或 index；
- `docs/manual/document-governance.md`：本标准自身。

### Operations naming

- canonical fixed-Round Plan：`operations/planning/research-experience-reboot.md`；
- canonical orchestration：`operations/orchestration/research-experience-reboot.md`；
- orchestration/scope standard：`operations/orchestration/<kebab-topic>.md`；
- ad-hoc Plan/evidence：`operations/planning/YYYY-MM-DD-<slug>.md`；
- fixed-Round work log：`operations/work_logs/research-experience-reboot-rN.md`；
- fixed-Round review：`operations/reviews/research-experience-reboot-rN-independent-review.md`；
- ad-hoc work log：`operations/work_logs/YYYY-MM-DD-<slug>.md`；
- ad-hoc review：`operations/reviews/YYYY-MM-DD-<slug>-review.md`。

同一 ad-hoc task 的 plan/work log/review slug 应保持一致。固定 Round 文件名中的 `rN` 必须与正文 `Round: RN` 一致。

## Required Metadata

所有新增或实质重写的 governed Markdown 应包含一个且仅一个 `## Metadata` section。除本节列出的 parser preamble 例外外，`## Metadata` 应是 H1 后第一个 H2。

### Stable document Metadata

用于 `docs/**`、根 `README.md`、`Harness_manual.md`、`assets/templates/**` 和稳定 orchestration pointer：

```markdown
## Metadata

- Project: serenity_quant_research
- Document type: manual-reference | human-manual | intake | product-spec | product-contract | research-baseline | external-reference-summary | guide | index | template | orchestration | plan-pointer | other
- Status: draft | active | approved | superseded | archived | external-reference
- Owner: project owner
- Last updated: YYYY-MM-DD
- Source of truth: AGENTS.md or path/to/source.md
```

字段顺序固定如上。`Last updated` 表示本文件最后一次实质维护或格式标准化日期，不是历史事件日期、批准日期或 research fact date。

### Ad-hoc operations Metadata

用于新增一次性 Plan、work log、review 或 governance evidence：

```markdown
## Metadata

- Project: serenity_quant_research
- Task: <task name>
- Timestamp (UTC): YYYY-MM-DDTHH:MM:SSZ
- Owner: project owner
- Route: direct-execute | plan | review-only | needs-extension
- Source of truth: AGENTS.md or approved Plan path
```

`Timestamp (UTC)` 只能记录真实写入/事件时间；不得为迁移补造历史 timestamp。历史 migration 如无法确定事件时间，使用 legacy exception 或在新 correction section 中说明。

### Canonical Plan Metadata and preamble

`operations/planning/research-experience-reboot.md` 是 parser-sensitive canonical fixed-Round Plan。它允许在 `## Metadata` 前保留顶层 preamble，但必须包含以下 key：

- `Plan approval:`
- `Git baseline:`
- `Accepted-effective Rounds:`
- `Active Round:`
- `Branch:`
- `Approval authority:`
- `Approval scope:`

其 `## Metadata` 必须至少包含：

- `Route: fixed-round-plan`
- `Canonical Plan: operations/planning/research-experience-reboot.md`
- `Canonical orchestration: operations/orchestration/research-experience-reboot.md`

并保留 `## Round Ledger` heading。

### Orchestration Metadata

Active orchestration contract/standard/backlog 使用 stable Metadata，并在正文状态区保留必要字段：

- approval/status；
- applicable canonical Plan link；
- scope standard link（如适用）；
- superseded replacement（如适用）。

### Fixed-Round work-log Metadata and labels

Fixed-Round work log 可用顶层 parser labels 开头，并应保留：

- `Round: RN — <name>` 或 `Round: RN`；
- `Plan: operations/planning/research-experience-reboot.md`；
- `Git baseline:`；
- `## Status`、`## Delivered Boundary`、`## Candidate Scope`、`## Validation` 等 task-specific sections。

Accepted R1–R5 work logs 是 legacy accepted evidence，本轮不强制补写 `## Metadata`。

### Independent review Metadata and labels

Fixed-Round review 可用顶层 parser labels 开头，并应保留：

- `Round: RN`；
- `Review role:`；
- `Decision:`；
- `Unresolved P0:`、`Unresolved P1:`、`Unresolved P2:`；
- `## Candidate Reviewed`、`## Findings`、`## Limitations And Disposition` 或等价中文 section。

Accepted legacy review 中的 verdict、counts 和 finding labels 不因格式治理被重写。

## First Section Rule

每个 governed Markdown 必须以 H1（`# Title`）开头。H1 后的第一种允许形态为：

1. 立即出现 `## Metadata`；或
2. canonical Plan / fixed-Round work log / fixed-Round review 保留 parser-required top-level preamble labels，然后出现 `## Metadata`、`## Status` 或等价首个 H2；或
3. `AGENTS.md` 保留 managed/project marker 分区；`operations/archive/**` 和 precise legacy exceptions 保留历史结构。

不得把 Metadata 藏在正文后部；不得出现重复 `## Metadata`。

## Update Policy

- 小修只更新相关段落；实质更新时同步刷新 stable doc 的 `Last updated`。
- Event evidence 默认不可变；后续发现错误时追加 correction/disposition，不改写历史结论、verdict、timestamp 或 research facts。
- Metadata normalization date 只能表示格式标准化或维护日期，不是原始批准/事件日期。
- 修改已有 dirty 文件时必须 hunk-aware，保留 unrelated hunks，不 stage 未授权路径。
- Governance cleanup 不得更改 product/research source-of-truth、accepted Round state、review decision、acceptance semantics、截图、schema、seed 或 database。

## Historical Migration Policy

- canonical/current source paths 优先保持稳定；不为样式统一而 rename accepted R1–R5 evidence。
- `operations/archive/**`、第三方/历史原文和 parser-sensitive artifacts 默认通过 legacy exception 或 warn-only 处理。
- 历史文件被后续任务实质修改时，应在该任务 scope 内补齐最小 Metadata 或 correction；不得批量补造历史 approvals、timestamps、owners、pass verdicts 或 research facts。
- Legacy exception 必须精确到 path 和 rule，并写明 reason、lifecycle、review-after 或 permanent reason。新增文件不得通过伪装成 legacy pattern 绕过 active rules。

## Link Update Policy

- rename 或移动 governed Markdown 时，同一变更必须更新 active project Markdown 中的相对链接、canonical Plan reference 和 navigation entry。
- 新增 Markdown link 使用 repo-relative 或当前文件相对路径，避免绝对本机路径。
- URL、mailto 和 anchor-only link 不由本地存在性检查强制。
- Archive link 默认 warn-only；除非任务明确触碰 archive body，否则不批量修历史路径。
- Active docs 指向已移动文件时必须修复；历史 provenance 文本中的旧文件名可保留为原文说明。

## Validation Command

本地验证命令：

```bash
python3 scripts/check-document-governance.py --report
python3 scripts/check-document-governance.py --check
git diff --check
```

`--report` 用于 inventory 和 migration planning，始终返回 0；`--check` 用于 enforcement，遇到 active failure 返回非零，并打印 path 和 exact reason。脚本只读，不自动格式化或写文件。

## CI Enforcement

CI 使用 `.github/workflows/document-governance.yml` 运行：

```bash
python3 scripts/check-document-governance.py --check
```

触发范围为 `pull_request` 和推送到 `main` / `product-reboot`。CI 不运行 formatter，也不生成 migration patch。

## Legacy Exception Policy

Legacy exception baseline 存放在 `docs/manual/document-governance-exceptions.json`。例外必须满足：

- path 为项目相对路径；
- rule 只覆盖明确规则（如 `metadata`、`naming`、`links`），不能 broad-skip `operations/**`；
- reason 说明为什么保留历史原貌；
- lifecycle 使用 `legacy-preserve`、`warn-only`、`superseded-pointer`、`canonical` 或 `permanent`；
- 非永久例外写 `review-after`，永久例外写 `permanent reason`；
- 新增文件不得仅因匹配 legacy 风格文件名而跳过检查。

当前 accepted R1–R5 work logs/reviews、历史 P2/P3 reviews、archive index/body、bootstrap/ad-hoc governance records 由 exceptions 文件精确列出。

## Related Files

- `AGENTS.md`
- `Harness_manual.md`
- `docs/manual/document-governance-exceptions.json`
- `scripts/check-document-governance.py`
- `assets/templates/stable-document.md`
- `assets/templates/operations-plan.md`
- `assets/templates/operations-work-log.md`
- `assets/templates/operations-review.md`
