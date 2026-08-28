# Independent Review 与 Round Scope 标准

## 状态

- 状态：approved governance standard
- 批准时间：2026-08-28
- 适用范围：本仓库所有 fixed-Round delivery、formal review、handoff 与治理维护
- 上级合同：`AGENTS.md`
- 当前产品计划：`operations/planning/research-experience-reboot.md`

## 目的

本标准用于防止 Independent Review 从当前产品 Round 候选漂移到治理工具实现、环境脏状态或下一 Round。Review 的目标是证明当前 Round candidate 是否满足已批准合同，而不是评审整个仓库或修复 Pi/harness 工具。

## Review 对象

Independent Review 评审三类材料，但只有第一类是验收候选：

1. **Candidate scope**：当前 Round 实际请求验收的变更、证据和交付物。Reviewer 可以对这些内容给出 P0/P1/P2。
2. **Context scope**：判断 candidate 所需的只读合同、Plan、spec、source、tests、baseline。Context 可以作为证据引用，但不因被读取而自动成为 candidate。
3. **Environment / dirty-worktree scope**：Git dirty/untracked 状态、pre-existing local files、工具目录或其他环境残留。它们用于透明记录、immutability 与污染风险判断，不自动成为当前 Round 的交付范围。

结论规则：**进入 review bundle 不等于进入 candidate scope。**

## Scope 设定规则

每次 fixed-Round review 前，Builder 必须在 work log 或 review artifact 中明确：

- Round ID 与当前 active Round；
- candidate paths；
- context paths；
- pre-existing dirty paths；
- governance maintenance / tool paths；
- protected surfaces；
- automated validation summary；
- review capability/fallback 状态。

`scopePaths` 可以包含 reviewer 判断所需的普通文件，但 reviewer finding 必须标明它针对的是 candidate、context、environment，还是 tool/backlog。只有 candidate 不满足当前 Round acceptance 时，才作为产品阻塞处理。

## Git dirty worktree 标准

Dirty worktree 必须透明，不得隐藏：

- Round start 记录 `git status --short` snapshot；
- review 前后记录 HEAD、status/hash、candidate hash；
- 对 changed/untracked paths 分类；
- 对 protected surfaces 执行单独 diff/status 证明。

默认分类：

| 分类 | 含义 | 对当前产品 Round 的影响 |
|---|---|---|
| `candidate` | 本 Round 请求验收的变更 | 可阻塞当前 Round |
| `context` | 只读判断材料 | 不自动阻塞，除非合同冲突导致 candidate 不可验收 |
| `pre-existing dirty state` | Round 开始前已有脏状态 | 记录并保持，不自动纳入 candidate |
| `governance maintenance` | `.pi/`、harness、manual、治理脚本等维护 | 默认转单独治理任务 |
| `unrelated / preserved` | 与当前 Round 无关且被保护 | 不得修改；只记录污染风险 |

## `.pi/` / harness 治理层修改禁令

项目开发过程中，`.pi/` / harness 治理层问题不得被擅自修改。治理层包括 `.pi/extensions/`、harness-flow、skills、prompts、settings、session handoff/review tooling 与相关治理脚本。

默认处理：

- 发现问题时，单独记录为 governance maintenance issue 或 review limitation；
- 不进入当前产品 candidate；
- 不阻塞产品验收，除非它让必要门禁完全无法成立；
- 只要不直接阻断产品开发/验收判断，就继续当前产品 Round；
- 不自动修 harness，不重复 reload；
- 向 Owner 报告问题、影响判断、可选方案。

只有同时满足以下条件，才允许修改 `.pi/` / harness 相关文件：

1. 问题属于严重恶性 bug，导致项目无法继续；例如无法生成任何 review evidence、无法保护候选 immutability、工具会错误修改项目文件、handoff/review gate 完全不可用；
2. Owner 明确授权修改治理层；
3. 修改作为单独 governance maintenance 记录，不能混入产品 Round candidate；
4. 修改后必须证明没有改动 production code、schema、migrations、seed、runtime config 或 tests，除非该治理维护任务本身另有 Owner 授权。

本次 R1 scope 漂移的错误根因正是：把 review automation / harness-flow 问题当成 R1 产品 Round 的 P1 去修。后续不得重复该模式。

## `.pi/extensions` 与 harness-flow 边界

`.pi/extensions/harness-flow` 属于 governance tooling，不属于产品 runtime。

它只有在以下情况下属于 candidate scope：

- 当前任务/Round 明确是 governance tool maintenance；
- Owner 明确批准把 `.pi/extensions` 作为当前交付候选；
- review 目标本身是验证 handoff/review 工具。

它不因以下情况自动进入产品 Round：

- Git working tree 中 changed/untracked；
- 被 review bundle 作为 context/环境状态打包；
- automated Independent Review 报告了工具能力问题；
- Builder 为了通过 review 临时修了工具。

## Harness finding 处理

| Finding 类型 | 处理标准 |
|---|---|
| 产品 candidate 不满足 Round 合同 | P0/P1 留在当前 Round，Fix → Verify → Re-review |
| Review evidence 不足以证明 candidate | 阻塞 review gate；补 evidence 或走 fallback，不扩大产品 scope |
| Harness/tooling bug 不影响产品事实判断 | 记录为 governance maintenance backlog / review limitation；继续当前产品 Round |
| Harness capability/auth/isolation 不稳定 | 标记 `automated_review_capability_blocked`；不自动修 harness、不重复 reload；请求 Owner 选择继续产品验收、human fallback、单开治理维护或调整 review mode |
| Harness 本身是已批准 candidate | 仅在单独治理维护任务中按 candidate finding 处理 |

## spawned Pi、human fallback 与 same-session 边界

有效 Independent Review 只能是：

1. `spawned_pi_process`
   - distinct process；
   - non-interactive / no-session；
   - strict read-only tools；
   - child 不写项目文件；
   - Builder 记录 process/model/output/tool-boundary/Git immutability。
2. Owner-approved `human_review`
   - reviewer 与 Builder 不同；
   - reviewer 只读；
   - Builder 记录 reviewer 身份、输入、P0/P1/P2、P2 disposition 与 Git immutability。

以下都不是 Independent Review：

- Builder same-session self-check；
- `/new` 但没有 distinct reviewer 边界；
- child 或 reviewer 直接写 candidate/artifact；
- 未记录 process/human identity 与 immutability 的普通评论。

## OS-level sandbox / bwrap 标准

本项目默认不要求 OS-level sandbox 或 bwrap read confinement。默认要求是：

- distinct no-session reviewer；
- strict read-only tool boundary；
- candidate immutability evidence；
- Builder 不把 reviewer 当作实现者。

如果未来要引入 bwrap/sandbox：

- 必须作为单独 governance maintenance；
- 不挂在产品 Round；
- 不阻塞当前产品审计或产品 UI Round；
- provider credential、runtime path、read root、secret redaction 必须在治理维护任务内单独验收。

## Automated review capability fallback

若 automated review 因 capability/auth/isolation/tool bug 阻塞：

1. 停止重复 reload/re-review/harness 修复循环；
2. 不自动修改 `.pi/` / harness；
3. 标记 `automated_review_capability_blocked`；
4. 不把该 blocker 作为产品 candidate P1；
5. 向 Owner 报告：问题是什么、是否影响产品 Round 判断、是否让必要门禁完全无法成立；
6. 请求 Owner 在以下选项中选择：
   - 继续产品验收并把问题记为 review limitation；
   - 使用 distinct human review fallback；
   - 暂停当前 Round，单开 governance maintenance；
   - 修改 Plan 的 review mode/acceptance；
   - 明确放弃本次 formal review gate。

未获 Owner 批准前，不得静默降级为 same-session review。

## Round acceptance 顺序

Fixed Round 的 accepted-effective 顺序为：

1. Builder 完成当前 Round candidate；
2. automated validation 通过；
3. Independent Review 或 Owner-approved human fallback 完成；
4. P0/P1 清零；
5. P2 disposition 完成；
6. Owner 明确验收当前 Round；
7. Owner 另行授权 acceptance commit；
8. commit；
9. post-commit verify；
10. 标记 accepted-effective；
11. 停止，不自动进入下一 Round。

## R1 当前收口标准

R1 的产品 candidate 是 P0–P3 code/domain disposition audit。R1 不再继续修 bwrap、provider auth 或 harness-flow。

R1 后续只允许：

- 重新界定 candidate/context/environment；
- 使用明确 scope 的 distinct human review fallback 或稳定 spawned review；
- 处置与产品审计相关的 P2；
- 等待 Owner 验收。

`.pi/extensions/harness-flow/index.ts`、starter update、docs references 整理等归入 governance maintenance dirty state/backlog，不再作为 R1 产品审计 candidate。
