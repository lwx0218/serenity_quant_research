# Research Experience Reboot — R1 独立评审

Round: R1
Review role: per_round
Decision: owner_accepted_with_review_capability_limitation
Unresolved P0: 0
Unresolved P1: 0 product-audit candidate P1 confirmed after scope reset; automated review capability blocker accepted as documented governance limitation

## Status

- Round: `R1`
- Review role: `per_round`
- Required mode: `spawned_pi_process`
- 首次调用时间：`2026-08-28T07:24:06Z`
- 最新有效评审记录时间：`2026-08-28T08:35:25Z`
- 当前决定：**Owner accepted with documented automated review capability limitation；按新标准停止 R1 sandbox/auth/harness 修复循环**
- 候选验收：**Owner 于 2026-08-28 确认验收 R1；review capability blocker 留档为 governance limitation，不作为 R1 product-audit finding**
- Artifact 作者：Builder（review child 不写项目文件）

## Candidate

- Audit: `operations/reviews/reboot-p3-code-disposition.md`
- Work log: `operations/work_logs/research-experience-reboot-r1.md`
- Candidate HEAD: `7cf1b95d23a5da3dd53766049557a67ed18fae73`
- Candidate scope: R1 product-audit durable evidence only; production paths protected
- Context scope: governance/product/research contracts needed to judge the audit
- Environment/governance dirty state: `.pi/extensions/harness-flow`、starter update、docs references 整理；不作为 R1 product-audit candidate

## Invocation Evidence

The Builder automatically called `harness_run_independent_review` after automated verification with:

- `reviewRole`: `per_round`
- `roundId`: `R1`
- `planPath`: `operations/planning/research-experience-reboot.md`
- scope including product/evidence contracts, canonical Plan/orchestration, audit/work log, P0–P3 source, migrations, seed, generated contracts, tests, and legacy review evidence
- timeout: 900 seconds

Tool result:

```text
Review decision: blocked
Reason: Round R1 must be declared uniquely as in_progress for Review

Use an Owner-approved human distinct from the Builder to review the declared Round read-only and record P0/P1/P2 plus candidate immutability.
```

## Process / Model / Tool-Boundary Evidence

No Independent Review child was spawned because durable Plan validation failed before process creation.

| Evidence | Result |
|---|---|
| distinct child PID | none; process not spawned |
| child provider/model | none; process not spawned |
| child exit/stdout/stderr | none; validation returned the structured blocked result above |
| requested child boundary | non-interactive, no-session, strict `read,grep,find,ls` |
| effective child boundary | not established because no child existed |
| Builder session | `01a04739-196e-7a38-ba8f-cc17df99fc67` |
| Builder provider/model | `openai-codex` / `gpt-5.6-sol` |

The Builder session is recorded only to distinguish it from the absent reviewer; it is not an Independent Review substitute.

## Durable Status Mismatch

The canonical Plan contains both:

```text
Active Round: R1
```

and a Round Ledger R1 status of:

```text
pending
```

The review validator requires exactly one matching Round to be declared `in_progress`. R1 expected change surfaces permit only the three audit/work-log/review artifacts, so the Builder did not silently modify the approved canonical Plan.

## Candidate Immutability

Before the review attempt:

- HEAD: `7cf1b95d23a5da3dd53766049557a67ed18fae73`
- `git diff --exit-code -- src tests data`: exit `0`
- protected status: pre-existing untracked `data/` and pre-existing untracked scoped `AGENTS.md`

After the blocked review attempt:

- HEAD: `7cf1b95d23a5da3dd53766049557a67ed18fae73`
- `git diff --exit-code -- src tests data`: exit `0`
- protected status: unchanged

No reviewer process or review attempt modified the candidate or protected production paths.

## Findings

The Independent Review did not execute, so it produced no valid P0/P1/P2 candidate findings.

- P0: not assessed
- P1: not assessed
- P2: not assessed

Absence of findings is not a pass.

## 第二次调用记录：工作日志元数据阻塞

Owner 授权后，Builder 将唯一 R1 Ledger 状态修正为 `in_progress`，重新验证通过并再次调用自动评审。工具在 child spawn 前返回：

```text
Review decision: blocked
Reason: declared review work log lacks unique authoritative Round/Plan metadata
```

根因：工作日志的 Round 字段位于首个 `##` 标题之后，且缺少工具要求的唯一 `Plan` 与 `Git baseline` 权威元数据。此次同样未创建 child process，因此没有 P0/P1/P2；HEAD、受保护路径状态及 production tracked diff 均未变化。

Builder 已在工作日志首个二级标题前补充：

```text
Round: R1 — P0–P3 Code Disposition And Domain Audit
Plan: operations/planning/research-experience-reboot.md
Git baseline: 7cf1b95d23a5da3dd53766049557a67ed18fae73
```

## 第三次调用记录：scope path 类型阻塞

补齐工作日志元数据并重新验证后，工具继续在 child spawn 前返回：

```text
Review decision: blocked
Reason: Path must be a regular non-symlink file: docs/product
```

根因是 Builder 将目录传入 `scopePaths`，而该工具要求每一项都是普通非符号链接文件。此次仍未创建 child process，没有 P0/P1/P2，候选与受保护路径保持不变。

## 第四次调用：有效 Independent Review

本次成功创建 distinct read-only child，并返回 `changes_required`：P0=0、P1=2、P2=1；候选在评审前后保持不变。

### Process / model / isolation evidence

| 项目 | 结果 |
|---|---|
| Builder PID | `240660` |
| Reviewer PID | `698109`，与 Builder 不同 |
| Provider / model | `openai-codex` / `gpt-5.6-sol` |
| Thinking level | `high` |
| 模式 | print、`--no-session`、`--no-approve` |
| Project resources | extensions / skills / prompt templates / themes / context files 均禁用 |
| Tool boundary | 仅 `read,grep,find,ls`；无 shell、无写工具 |
| Exit / timeout / truncation | exit `0`；未超时；未中止；输出未截断；stderr 为空 |
| Duration | `352760 ms` |
| Git immutability | before/after HEAD、status hash、candidate hash 完全一致 |

### Findings 与 Builder disposition

1. **P1 — Evidence workflow endpoint 将机器身份误判为 human reviewer。**
   - 证据：`EvidenceWorkflowEndpoint.cs` 对任何拥有 `Research:Review` 的 principal 传入 `actorIsHumanReviewer: true`，违反 evidence contract 的“禁止机器身份执行 review”。
   - 处置：**接受并修正审计。** `EvidenceWorkflowEndpoint.cs` 从 KEEP 改为 `ADAPT / ENDPOINT-ADAPT-IDENTITY`；保留 service 的显式 human flag 与 domain policy；新增可信 actor-type 校验和 endpoint-level machine-principal 拒绝测试作为后续必需修复。R1 仍不修改 production endpoint 或 tests。
2. **P1 — Final Integrated Review 对 per-Round role 的校验值与工具枚举不一致。**
   - 证据：`.pi/extensions/harness-flow/index.ts` 校验 `per-round`，工具参数与 bundle 使用 `per_round`。
   - 处置：**接受并修复。** 将前置校验统一为 `per_round`，并为本 artifact 增加工具可解析的 preamble metadata。
3. **P2 — 工作日志未声明 Owner 授权的 Plan 写入例外。**
   - 处置：**接受并修复。** Boundary 已明确列出 Plan 状态修正、持续评审授权及本轮 P1 extension 修复；另行授权的 `docs/` 整理明确为独立 maintenance。

### Reviewer limitations

- child 遵循只读边界，未运行命令或独立重跑 Git、build、tests；自动验证依据 review bundle 与 durable evidence。
- R1 无 UI 候选，因此未验证外部来源、物理桌面呈现或跨浏览器行为。

## 第五次调用：第一次 Re-review

Re-review child 成功运行并返回 `changes_required`：P0=0、P1=1、P2=2；candidate immutable。

### Process / model / isolation evidence

| 项目 | 结果 |
|---|---|
| Builder / Reviewer PID | `240660` / `771725`，进程不同 |
| Provider / model | `openai-codex` / `gpt-5.6-sol`，thinking `high` |
| Exit / timeout / truncation | exit `0`；未超时、未中止、未截断；stderr 为空 |
| Duration | `443451 ms` |
| Status hash | before/after 均为 `47fba60c56bda1bedc707f362df8b1b097b0a1e7322c0c6053925f5bf9fc8d3e` |
| Candidate hash | before/after 均为 `ccbbd63b6f6c887c85bcafe54419a1a1276fe92b5188bae4aa845f64aeac7148` |
| Immutability | `true` |

### Findings 与 Builder disposition

1. **P1 — handoff/review 的前序 Round 和 Active Round 门禁可被绕过。**
   - 处置：**接受并修复。** `assertEffectiveRoundSet` 现在要求 `Active Round` 唯一等于目标 Round，所有前序 Ledger Round 必须为 `accepted`，且 `Accepted-effective Rounds` 必须精确等于全部前序 Round；handoff 与 review 共用该校验。
2. **P2 — Executive Finding 将 endpoints 统一写入 KEEP，与详细矩阵冲突。**
   - 处置：**接受并修复。** 摘要改为只 KEEP 符合合同的 service internals，并明确 Company/Evidence 等 endpoints 属于 ADAPT。
3. **P2 — starter governance work log 含宿主机绝对路径。**
   - 处置：**接受并修复。** `operations/work_logs/2026-08-28-starter-governance-update.md` 改用 `<project-root>` placeholder，并解释其含义；不再记录真实宿主机项目路径。

## 第六次调用：第二次 Re-review

本次 child 返回 `changes_required`：P0=0、P1=2、P2=2；candidate immutable。

| 项目 | 结果 |
|---|---|
| Builder / Reviewer PID | `240660` / `851705`，进程不同 |
| Provider / model | `openai-codex` / `gpt-5.6-sol`，thinking `high` |
| Exit / timeout / truncation | exit `0`；未超时、未中止、未截断；stderr 为空 |
| Duration | `406074 ms` |
| Status hash | before/after 均为 `47fba60c56bda1bedc707f362df8b1b097b0a1e7322c0c6053925f5bf9fc8d3e` |
| Candidate hash | before/after 均为 `c5c043870f54cc38392d33b8f3e8ca167ebf5aadff2e7e65815957e15ab99868` |
| Immutability | `true` |

### Findings 与 Builder disposition

1. **P1 — Evidence endpoint 身份缺陷没有后续 Round owner。**
   - 处置：**接受并修正 Plan。** R7 delivery boundary、Goal、Expected change surfaces、validation、acceptance evidence 和 blocked conditions 现在明确负责可信 human/machine actor-type enforcement 及 endpoint-level tests；保持 evidence semantics 与 schema 不变。
2. **P1 — 当前无权威离散材料数据，但 R3 仍把材料展示当作 ready。**
   - 处置：**接受并修正 Plan/spec。** R3 DoR 和 visible outcome 明确当前只保证真实 child stable IDs；material 仅在权威现有关系支持时显示，否则使用 `暂无已核验材料数据` 或省略。`cpo-explorer-spec.md` 的 panel 与 acceptance scenario 同步采用安全 gap 语义。
3. **P2 — Workspace 与 Company 文档仍混有 deferred writing/OpenQuestion/Comparison。**
   - 处置：**接受并修正。** Workspace spec 将 v1 入口、tree、center、backlinks、notes 和 questions 统一为 existing-object/read-only/derived，ResearchNote/OpenQuestion/Graph/editing 明确 deferred；Product README 将 Company Comparison 从 current purpose 移除。
4. **P2 — 缺少 durable Round-start 完整 worktree 状态。**
   - 处置：**接受并修正。** R1 work log 已加入 Round start 的完整 `git status --short` snapshot，并单列受保护路径状态。

## 第七次调用：第三次 Re-review

本次 child 返回 `changes_required`：P0=0、P1=3、P2=2；candidate immutable。

| 项目 | 结果 |
|---|---|
| Builder / Reviewer PID | `240660` / `942619`，进程不同 |
| Provider / model | `openai-codex` / `gpt-5.6-sol`，thinking `high` |
| Exit / timeout / truncation | exit `0`；未超时、未中止、未截断；stderr 为空 |
| Duration | `431929 ms` |
| Status hash | before/after 均为 `47fba60c56bda1bedc707f362df8b1b097b0a1e7322c0c6053925f5bf9fc8d3e` |
| Candidate hash | before/after 均为 `ece5ad029eb6677ebbd2376474909125122511dbe90df7a9bfb7083df432dd2e` |
| Immutability | `true` |

### Findings 与 Builder disposition

1. **P1 — Review child 携带 provider auth，但没有 read confinement。**
   - 处置：**接受并修复 extension source。** Linux review 现在 fail-closed 要求 `/usr/bin/bwrap`，把全部 review/changed/scope 文件复制到临时 review root，以只读 mount 暴露为 `/workspace`；host project、host HOME 与 procfs 均不在 sandbox 内，仅保留 runtime、CA/DNS、network 和空临时 HOME。process evidence 将 `readConfinement` 记录为 `true`。
   - 当前 Pi runtime 仍加载修复前 extension；必须执行 `/reload` 后才能用新代码生成有效 confined re-review evidence。
2. **P1 — R1 ownership metadata 未包含实质 Plan/product corrections。**
   - 处置：**接受并修正。** Canonical Plan 的 R1 Expected change surfaces 与 work-log Boundary 已逐项列出 review-authorized Plan、AGENTS、extension、product contract 和 portability 修正面；另行 docs 目录整理仍单独标识。
3. **P1 — disposition matrix 漏掉 trusted actor-type implementation dependencies。**
   - 处置：**接受并修正。** 新增 `ACTOR-IDENTITY-KEEP` profile，并逐文件分类 `UserActorTypes.cs`、`UserRow.cs`、`UserSaveHandler.cs`；Company exposure endpoint/test pattern 明确作为 R7 复用基础，Plan change surface 显式引用 `UserRow.ActorType` / `UserActorTypes`。
4. **P2 — 高优先级文档仍残留 Comparison/ResearchNote 入口与 acceptance。**
   - 处置：**接受并修正。** Experience Map 与 Workspace acceptance 均改为 one-company/read-only existing object/derived backlink/gap，ResearchNote/OpenQuestion/Comparison 保持 deferred。
5. **P2 — 历史参考总结含 `computer:///` host links。**
   - 处置：**接受并修正。** 五个不可移植上传链接替换为“历史上传材料，未纳入当前仓库”，不伪造新的来源路径。

## 第八次调用：confined child runtime path 阻塞

Owner 继续 R1 评审后，新的 read confinement 路径已被当前 runtime 使用，但 child 在启动阶段失败：

```text
Review decision: blocked
Reason: review child failed, timed out, was aborted, or produced truncated evidence
stderr: bwrap: execvp /home/.../.local/share/node-v24.19.0/bin/node: No such file or directory
```

| 项目 | 结果 |
|---|---|
| Builder / Reviewer PID | `1063513` / `1091463`，进程不同 |
| Provider / model | `openai-codex` / `gpt-5.5`，thinking `high` |
| Isolation | `readConfinement: true`；host project / host HOME / procfs 不暴露 |
| Exit | exit `1`，44ms；未超时、未中止、未截断 |
| Candidate immutability | before/after unchanged |

根因：sandbox 正确隐藏 host HOME，但 `getPiInvocation` 在当前 runtime 中选择了 host HOME 下的 Node 二进制。Builder 已修复 `confinedReviewerInvocation`：当 reviewer command 指向 host HOME 下的 Node runtime 时，改用已在 sandbox 中只读暴露的 `/opt/module/nodejs/node/bin/node`；不会暴露 host HOME。

## 第九次调用：confined child provider auth 阻塞

修复 Node runtime path 后，child 在 read-confined sandbox 内启动，但 provider auth 未传入 sandbox，返回：

```text
Review decision: blocked
Reason: review child failed, timed out, was aborted, or produced truncated evidence
stderr: Warning: Invalid settings file /workspace/.pi/settings.json: EROFS ...
stderr: No API key found for openai-codex.
```

| 项目 | 结果 |
|---|---|
| Builder / Reviewer PID | `1063513` / `1125963`，进程不同 |
| Isolation | `readConfinement: true` |
| Exit | exit `1`，476ms；未超时、未中止、未截断 |
| Candidate immutability | before/after unchanged |

根因：sandbox 不暴露 host HOME 和 auth store，且当前 child 未通过 CLI 获得 provider credential。Builder 已验证：在 bwrap 内使用 bundled Node + `--api-key <bearer>` 可通过 openai-codex auth smoke，且不需要暴露 host HOME。Extension 已改为在 reviewer args 中注入 `--api-key`，并在 process evidence 中将其记录为 `<redacted-provider-auth>`。

## 第十次调用：confined provider auth 仍阻塞

Owner 表示这是最后一次 reload 后，Builder 再次验证并调用自动 Independent Review。结果仍为 `blocked`：

```text
Review decision: blocked
Reason: review child failed, timed out, was aborted, or produced truncated evidence
stderr: Warning: Invalid settings file /workspace/.pi/settings.json: EROFS ...
stderr: No API key found for openai-codex.
```

| 项目 | 结果 |
|---|---|
| Builder / Reviewer PID | `1063513` / `1166625`，进程不同 |
| Provider / model | `openai-codex` / `gpt-5.5`，thinking `high` |
| Isolation | `readConfinement: true`；host project / host HOME / procfs 不暴露 |
| Exit | exit `1`，483ms；未超时、未中止、未截断 |
| Candidate immutability | before/after HEAD 均为 `7cf1b95d23a5da3dd53766049557a67ed18fae73`；unchanged=`true` |

结论：自动 review spawn 的 OS-level read confinement 已建立，但当前 runtime/provider credential handoff 仍不能在 sandbox 内完成。按 2026-08-28 新治理标准，本项目默认不再要求 bwrap/OS-level sandbox；R1 不继续修 provider auth 或 harness-flow。该问题改记为 `automated_review_capability_blocked` 与 governance maintenance backlog，不再作为 R1 产品审计 candidate finding。

Owner 进一步确认：产品开发过程中 `.pi/` / harness 治理层问题不得被擅自修改；默认单独记录为 governance maintenance issue / review limitation。只要不直接阻断产品开发或验收判断，就继续当前产品 Round；只有严重恶性 bug 导致项目无法继续并获得 Owner 明确授权后，才允许修改治理层。本次 R1 scope 漂移已记录为 `operations/orchestration/governance-maintenance-backlog.md#gov-001--r1-automated-review--harness-flow-scope-漂移`。

## Human Review Fallback 状态：不采用

- 初始误解授权时间：`2026-08-28T08:52:33Z`
- 后续 Owner 澄清：不采用 Human Review Fallback；需要解决/澄清 automated spawned review 的 scope 与 capability 问题。
- 当前决定：R1 回到 scope-bounded `spawned_pi_process` Independent Review；`.pi/` / harness 问题按新标准作为 governance maintenance / review limitation 处理，不作为 R1 product-audit candidate。
- Builder 边界：只记录 spawned review process evidence、结论、P2 disposition 和 Git immutability。

初始误解授权时的候选状态：

```text
HEAD: 7cf1b95d23a5da3dd53766049557a67ed18fae73
protected status:
?? data/
?? src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md
protected tracked diff: clean (`git diff --exit-code -- src tests data` exit 0)
```

## 第十一次调用：scope-bounded spawned review 仍被 capability 阻塞

- 调用时间：`2026-08-28T09:58:32Z`
- 前置验证：通过；R1 Plan 的 `Independent Review mode` 已恢复为精确 `spawned_pi_process`。
- Review scope：按新标准限定 R1 product-audit candidate；`.pi` / harness 仅为 environment/governance context。
- 工具结果：`blocked`

```text
Reason: review child failed, timed out, was aborted, or produced truncated evidence
stderr: Warning: Invalid settings file /workspace/.pi/settings.json: EROFS ...
stderr: No API key found for openai-codex.
```

| 项目 | 结果 |
|---|---|
| Builder / Reviewer PID | `1063513` / `1666253`，进程不同 |
| Provider / model | `openai-codex` / `gpt-5.5`，thinking `high` |
| Exit | exit `1`；未超时、未中止、未截断 |
| Read confinement | `true`（但本项目新标准默认不要求 bwrap） |
| Candidate immutability | before/after HEAD 均为 `7cf1b95d23a5da3dd53766049557a67ed18fae73`；unchanged=`true` |

Builder disposition：这是 automated review capability/auth limitation，不是 R1 product-audit candidate finding。按新治理标准，不继续修 `.pi` / harness，不要求 reload，不把该问题作为 R1 产品审计 P0/P1。

## 当前解决动作

R1 已由 Owner 于 2026-08-28 验收。R1 Builder candidate 已完成且自动验证通过；automated spawned review capability/auth blocker 已作为 limitation / governance maintenance 留档，不作为 R1 product-audit finding。Plan 已更新为 `Accepted-effective Rounds: R1`、`Active Round: none`、R1 Ledger `accepted`。当前不启动 R2、不 push；acceptance commit/post-commit verify 仅在 Owner 另行要求时执行。
