# AGENTS.md

## Purpose

`serenity_quant_research` 采用 external-first、PI-first 的最小治理模式。本仓库持有自己的源码、配置、运行入口和 durable evidence；`Harness_Workspace` 只是 starter 来源或治理参考。

## Audience And Local Paths

- `README.md`：项目 landing page
- `Harness_manual.md`：人类 step-by-step manual
- 本文件：Pi/模型执行合同；冲突时优先
- `.pi/`：project-local skills、prompts、settings
- `docs/project-intake/`、`operations/`：project-local durable evidence

人类从 `README.md -> Harness_manual.md` 进入。模型先读本文件，再读 README、human manual 和适用 `.pi/` 资源。

## Owner-Facing Language

- 面向 Owner 的聊天总结、交付说明和状态报告默认使用中文。
- 后续新增或实质更新的项目文档正文默认使用中文；文件名、代码标识、命令、协议字段及必要的原文引用可保留英文。
- 已批准的英文基线不因本规则自动批量翻译；修改其正文时应优先补充或改写为中文，除非 Owner 明确要求英文。
- 代码注释、运行时文案和对外产品语言仍按各自任务合同决定，不从本规则静默推导。

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

## First-Session Applicability

### Greenfield Or No Approved Baseline

从项目根使用：

```bash
pi --name "00-orchestration"
```

该 session 只负责 discovery、Plan Preview、Owner confirmation 和 handoff。在 Owner 明确确认 Plan 前，只能读取/推断/讨论并在 chat 展示 Preview。

确认前禁止：

- 修改业务代码或配置
- 创建/更新 formal Plan、intake、`CONTEXT.md`、ADR、work log、review 或其他项目 artifact
- 安装依赖或执行 destructive/system-level action
- 开始 implementation 或宣称开发进度

bootstrap 预先创建的 scaffold 不等于 orchestration conversation 获得写权限。

### Existing Approved Baseline

已有稳定 approved baseline 后，后续 bounded task 继续使用 `Gate -> Route`。不要强制每个任务进入 kickoff、Plan、Spec、fixed rounds 或 domain modeling。

## Bounded Discovery Contract

默认 question budget：

- 最多 3 个 discovery rounds
- 每轮 3–5 个相关 blocking decisions
- 目标总上限 12–15 个 blocking decisions
- 每个 decision 都给 recommended default
- Owner 可回复 `accept recommended defaults`
- repository 已能回答的事实不再询问
- 只问会改变 scope/acceptance、architecture/data ownership 或 hard-to-reverse/high-risk choice 的问题
- non-blocking uncertainty 写成 assumption 或 backlog
- 预算耗尽仍有 blocker 时，必须询问 Owner 是否 opt in `deep-discovery`；不能自动继续

每轮总结：Resolved、Assumed、Blocking、Deferred、Question budget remaining。

Stop condition：blocking scope、architecture、acceptance decisions 已解决；其余明确 assumed/deferred；validation 与 control gates 清楚。

## Plan Preview Terminal States

Greenfield/no-baseline orchestration turn 只能结束于：

1. `blocking-decisions`：只给 bounded decisions 和剩余 question budget
2. `ready-for-approval`：展示完整 Plan Preview，并主动询问可行性、修改点和显式批准
3. `approved-and-persisted`：仅在 Owner 明确批准后写 approved evidence，并生成 durable-source-based handoff

`ready-for-approval` 必须以等价问题结束：

```text
以上 Plan 是否可行？是否还有需要继续确认或修改的地方？

- 如需修改：直接说明修改点
- 如无其他问题：回复“确认计划”
- 确认后我将持久化 Plan，并生成下一开发 session 的名称和交接内容
```

`accept recommended defaults` 只解决 discovery decisions，不等于 durable Plan approval。完整 Preview 后优先调用 `harness_request_plan_approval`；只有结构化结果 `approved` 才可持久化 project-local Plan/intake、批准的 domain language 或 sparse ADR。`changes_requested` 返回 Preview，`cancelled` 不写。extension unavailable 时 Owner 回复 `确认计划` 或同等清晰批准是 manual fallback。`00-orchestration` 不执行业务实现。

持久化后优先调用 `harness_offer_session_handoff`：验证 Plan/Round/session，展示 proposed session、bounded target 与 summary，请求一次 Owner UI confirmation；confirm 后创建 parent-linked session、命名并提交 prompt 一次。cancel/capability failure 留在当前 session 并返回 copyable fallback。

manual fallback 是 `/session-handoff <declared-session-name>`，再执行：

```text
/session
/new
/name <declared-session-name>
```

非 fixed work 使用 `/name build-<task-slug>`。automatic/manual handoff 都必须以 durable evidence 为 authority；不得把 local `harness-flow` 描述成公开 package。`/new` 不是 Independent Review。

## Default Routing

- `direct-execute`：已有 baseline 的 clear bounded task
- `plan`：cross-file、contract、portability、handoff、risk 或 validation 需要 durable planning
- `review-only`：只要 findings，不实现
- `needs-extension`：真实 package/extension/specialist gap

simple path 优先；固定 round、多角色、subagent、package/extension 都是按需升级。

## Optional Skills

- `grill-me`：无稳定文档 baseline 的 fuzzy request
- `grill-with-docs`：对 substantive approved Plan/Spec/architecture/domain evidence 或 explicit contract conflict 做 bounded stress-test；bootstrap-only scaffold 不触发
- `grilling`：决定 route
- `domain-modeling`：仅在 domain terminology、state、ownership 或 bounded-context ambiguity materially blocks design 时启用

四者都不是默认必经关卡。`domain-modeling` 在 Plan approval 前只能 no-write discovery，临时 glossary/scenarios 留在 chat；approval 后才可进入 record mode。

## Optional Fixed-Round Contract

Fixed rounds 只用于复杂、跨 session、高风险或 formal acceptance 工作；simple path 不被强制升级。

启用后：

- `Round` 是唯一 acceptance-bearing delivery unit；`Phase` 只能是不带 status、session、acceptance evidence 或 commit gate 的叙事分组
- 每个 Round 声明 Round ID、一个 primary implementation session name、independently reviewable delivery boundary、non-goals、dependencies/Definition of Ready、expected change surfaces、exact validation strategy、Independent Review mode and artifact path、acceptance evidence 和 blocked/rebaseline conditions
- 一个 Round 默认适合一个 primary Builder session；需要 continuation 时命名为 `R1-<slug>-cont-2` 并保留同一 Round、scope、Review lifecycle 和 acceptance gate
- 不得创建 `R2A`、`R2B` 或通过 Phase/session 拆出隐藏 acceptance unit
- Owner 已对本项目 Plan 声明的 Independent Review 提供持续授权；满足 Round 状态、候选验证和隔离条件后，Builder 无需逐轮再次询问即可自动调用，但该授权不等于 Round 验收、Plan 变更授权或 human-review fallback 授权
- Independent Review 是验收义务；`harness_run_independent_review` / spawned Pi 只是自动化执行能力。只有返回有效 decision 与 P0/P1/P2 evidence 才算完成 automated Review；child failed/timed out/aborted/truncated 只表示 capability blocked，不是产品 P1。
- 当前 Builder 在 automated verification 后自动调用 `harness_run_independent_review`，启动 distinct non-interactive/no-session/strict `read,grep,find,ls` child；captured evidence 包含 process/model/exit/stdout/stderr/tool boundary 和 Git immutability，durable artifact 由 Builder 写。若已知 automated capability blocked，纠正一次明显调用错误后不得 reload/retry 循环。
- P0/P1 在原 Round 自动 Fix/Verify/Re-review，P2 在 acceptance 前 disposition
- 全部 planned delivery 完成后，最后 Round 在 pre-commit gate 前执行单独的 Final Integrated Independent Review；它是最后 Round 的 evidence，不是新 Round
- `spawned_pi_process` capability/auth/read-only isolation 不成立时 fail closed，或使用经批准且与 Builder 不同的 `human_review`；`same_session` 与 `/new` 都不满足 Independent Review

## Independent Review Scope Standard

完整标准见 `operations/orchestration/independent-review-and-round-scope-standard.md`。默认规则：

- Independent Review 评审当前 active Round 的 candidate 是否满足批准合同；不默认评审整个仓库、全部 dirty worktree、治理工具实现或下一 Round。
- 每次 Review scope 必须区分 `candidate scope`、`context scope`、`environment / dirty-worktree scope`。进入 review bundle 不等于进入 candidate scope。
- Git changed/untracked paths 必须透明记录并分类为 candidate、context、pre-existing dirty state、governance maintenance 或 unrelated/preserved；dirty 状态不因存在而自动阻塞产品 Round。
- `.pi/` / harness 属于治理层，不属于产品 runtime。项目开发过程中不得擅自修改 `.pi/`、harness-flow、skills、prompts、settings 或治理脚本；除非出现导致项目无法继续的严重恶性 bug，且 Owner 明确授权，否则只能单独记录为 governance maintenance issue。
- `.pi/extensions/harness-flow` 属于 governance tooling。除非当前任务明确是治理工具维护，或 Owner 明确批准纳入 candidate，否则它不属于产品 Round scope。
- Reviewer 发现 harness/tooling bug 时，默认转为 governance maintenance backlog 或 review limitation；只要不直接阻断产品开发/验收判断，就继续当前产品 Round，不扩大产品 candidate。
- 本项目默认不要求 OS-level sandbox / bwrap read confinement；默认要求是 distinct no-session reviewer、strict read-only tools、Builder 记录 process/model/output/tool-boundary 与 Git immutability。
- automated review capability/auth/isolation 不稳定时，不自动修 harness、不重复 reload；记录/更新 governance maintenance issue，向 Owner 报告问题、是否影响产品 Round 判断、是否让 gate 完全无法成立，并给出 distinct human review fallback、继续产品验收并记录 limitation、单开治理修复或调整 review mode 的选项。
- `spawned_pi_process` 或 Owner-approved distinct `human_review` 才能作为 Independent Review；same-session self-check 和单纯 `/new` 都不得冒充 Independent Review。

## Evidence Paths

- `docs/project-intake/`
- `docs/product/`
- `docs/research-baseline/`
- `docs/references/`
- `operations/planning/`
- `operations/orchestration/`
- `operations/work_logs/`
- `operations/reviews/`
- `operations/archive/`

只在 Plan、跨 session/handoff、contract/bootstrap/portability 或 formal review 需要时写入。trivial task 不制造 durable evidence。当前有效治理/交付文档正文默认中文；历史归档证据可保留原文并补中文状态说明。

## Readiness

- `bootstrap-ready`：manual、contract、`.pi/`、intake、evidence directories 已生成
- `runtime-ready`：还具备 `pi` 和 provider/auth

session name 不提供权限隔离或 automatic plan mode。

## Portability And Review

- committed content 使用 relative path/placeholder，不硬编码 host absolute path
- secrets/local overrides 不提交
- heavy runtime residue 不作为 durable evidence
- Independent Review 需要 capability-checked `harness_run_independent_review` / read-only `spawned_pi_process`，或 approved distinct `human_review`
- same session 或 `/new` 不得冒充 Independent Review
- 不自动 push

## Boundary

`.pi/` 只承载治理入口，不承载业务 runtime、多底座适配或默认重闭环。Bug/Fix/Review 留在当前 task/round；scope/acceptance/round-map 变化需要 Owner approval。
