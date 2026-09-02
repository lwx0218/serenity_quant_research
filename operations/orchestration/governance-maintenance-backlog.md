# Governance Maintenance Backlog

## Metadata

- Project: serenity_quant_research
- Document type: orchestration
- Status: active
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: operations/orchestration/independent-review-and-round-scope-standard.md

## 状态

- 状态：active governance backlog
- 创建时间：2026-08-28
- 上级标准：`operations/orchestration/independent-review-and-round-scope-standard.md`
- 适用范围：`.pi/`、harness-flow、skills、prompts、settings、handoff/review tooling 与治理脚本

## 规则

项目开发过程中，`.pi/` / harness 治理层问题不得被擅自修改。

- 默认单独记录为 governance maintenance issue 或 review limitation。
- 不进入当前产品 candidate。
- 不阻塞产品验收，除非它让必要门禁完全无法成立。
- 只要不直接阻断产品开发/验收判断，就继续当前产品 Round。
- 不自动修 harness，不重复 reload。
- 只有严重恶性 bug 导致项目无法继续，并且 Owner 明确授权后，才允许修改 `.pi/` / harness 相关文件。

## Issue 模板

每个 issue 至少记录：

- ID
- 发现时间
- 发现位置 / 触发场景
- 影响范围
- 是否阻断当前产品 Round
- 推荐处理
- Owner 决策状态
- 后续维护任务 / 验证需求

## Capability Status

- `spawned_pi_process` Independent Review：**harness wrapper certified in fresh non-session Pi run**；manual spawned Pi path 也已 certified for R2。
- 最近失败：修复 Plan `Independent Review mode` metadata 后，旧 runtime 中的 R2/R3 wrapper 调用仍返回 `review child failed, timed out, was aborted, or produced truncated evidence`。
- 最近成功：本 governance session 使用 fresh `pi --no-session --approve --extension .pi/extensions/harness-flow/index.ts` 加载更新后的 wrapper，调用 `harness_run_independent_review` 审查 active R3，返回有效 `changes_required`，P0=0，P1=2，P2=2，Candidate immutable=yes，未 blocked。
- 默认处理：后续产品 Round 可使用更新后的 `harness_run_independent_review` wrapper；若当前交互 session 已加载旧 extension，需要 reload/新 session 才会使用新 wrapper code。
- 恢复条件：已满足 wrapper 返回有效 decision/P0/P1/P2 evidence；R3 产品 P1 需在 R3 Round 修复，不属于 wrapper blocker。

## Open Issues

### GOV-001 — R1 automated review / harness-flow scope 漂移

- 发现时间：2026-08-28
- 触发场景：R1 Independent Review 为让 automated review 通过，Builder 将 Plan、AGENTS、product docs、work log、review artifact 与 `.pi/extensions/harness-flow/index.ts` 纳入修复循环；Git dirty worktree 自动进入 review bundle 后，Reviewer 开始 review harness tool implementation。
- 影响范围：R1 review automation、read confinement、provider auth handoff、Round gate metadata；不影响 R1 产品审计本身对 P0–P3 code/domain disposition 的判断。
- 是否阻断当前产品 Round：不应阻断产品审计内容；只影响 automated review capability。R1 可转为 scope-bounded review 或 Owner-approved distinct human review fallback。
- 当前处理：停止在 R1 中修 bwrap、provider auth、harness-flow；将该问题从 R1 product-audit candidate 中移出。
- 推荐处理：如未来确需自动 review sandbox/auth hardening，单开 governance maintenance task，明确 owner、scope、validation 与 rollback；不得混入产品 Round。
- Owner 决策状态：Owner 已明确要求后续 `.pi/` / harness 问题默认单独记录，除严重恶性 bug 且明确授权外不得修改治理层。

### GOV-002 — R2 spawned Independent Review capability failed / truncated evidence

- 发现时间：2026-08-28
- 触发场景：R2 implementation、full automated validation 与 screenshots 已完成后，Builder 调用 automated Independent Review。
- Attempt 1：Builder packaging error，把 screenshot directory 传给要求 regular file 的 `scopePaths`；已通过枚举 screenshot files 纠正。该问题不是产品 finding。
- Attempt 2：harness 返回 `review child failed, timed out, was aborted, or produced truncated evidence`，未产出有效 P0/P1/P2，也未形成 `pass` / `changes_required` 判断。
- Attempt 3：修复 GOV-003 的 Plan `Independent Review mode` metadata 后，R2 session 重新调用 spawned review；mode enum gate 已通过，但 child execution 仍返回 `review child failed, timed out, was aborted, or produced truncated evidence`。这确认问题位于 automated spawned reviewer capability 层，而不是 Plan metadata 或 R2 candidate scope。
- 影响范围：automated spawned review capability；不直接证明 R2 产品 candidate 失败。
- 是否阻断当前产品 Round：阻断 formal Independent Review gate；不应触发产品 scope 扩张或 `.pi/` / harness 修复。
- 当前处理：R2 Independent Review 义务已由 manual spawned Pi process 完成；harness wrapper 后续通过 GOV-004 修复并在 fresh non-session Pi run 中认证。
- 推荐处理：后续产品 Round 使用已更新 wrapper；已加载旧 extension 的 session 需要 reload/新 session。
- Owner 决策状态：Owner 不接受 human review 或 `/new` review，并要求本 session 解决；已完成。

### GOV-003 — Plan `Independent Review mode` 字段被解释性正文污染

- 发现时间：2026-08-28
- 触发场景：governance standards reset 中把 `Independent Review mode: spawned_pi_process` 扩写为 `spawned_pi_process; if automated capability is blocked ...`，导致 harness mode gate 报错：`Independent Review mode must be spawned_pi_process or human_review`。
- 影响范围：Plan machine-readable metadata；会阻止 review child 启动。不是 R2 产品 candidate failure。
- 是否阻断当前产品 Round：阻断 automated review gate，直到 Plan 字段恢复精确枚举。
- 当前处理：已将 R1–R7 的 `Independent Review mode` 字段恢复为精确 `spawned_pi_process`，并把 fallback 说明移入独立 `Review fallback rule` 字段。
- 推荐处理：后续所有 Plan 中 machine-readable fields 保持精确 enum/path/status，不在同一字段追加说明；解释写入独立字段或正文。
- Owner 决策状态：已按治理修正执行；无需修改 `.pi/` / harness。

### GOV-004 — harness wrapper 最小修复：取消强制 bwrap 并提高 review output capture

- 发现时间：2026-08-28
- 触发场景：R2 必须完成独立 review，但 Owner 不接受 human review 或 `/new` review；`harness_run_independent_review` wrapper 在 metadata 修复后仍无法产出有效 evidence。
- Owner 授权：Owner 要求该问题必须在 `governance-standards-reset` session 解决；因此本次作为单独 governance maintenance 修改 `.pi/extensions/harness-flow/index.ts`，不混入 R2 product candidate。
- 修改内容：`MAX_REVIEW_OUTPUT_BYTES` 从 512 KiB 提升到 5 MiB；reviewer child 不再传入 `--provider`、`--model` 或 `--thinking`，而是读取 Pi settings 默认 provider/model/thinking；reviewer env 只保留 allowlisted runtime variables 与 HOME auth store；wrapper 不再强制 bwrap read confinement，而是在 temporary copied review root 中直接启动 `pi --no-session`，仍禁用 extensions/skills/prompts/themes/context files，并限制 tools 为 `read,grep,find,ls`。
- 理由：本项目标准已明确不默认要求 OS-level sandbox / bwrap；此前 bwrap/provider auth/output truncation 是导致 review capability blocked 的主要风险链路。
- 验证：direct `pi --no-session ... -p 'Reply OK'` smoke 通过；manual spawned Pi R2 review 在 temporary copied review root 中通过，返回 `pass`、P0=0、P1=0、P2=1；fresh non-session Pi 显式加载更新后的 extension 后调用 `harness_run_independent_review`，返回有效 `changes_required`、P0=0、P1=2、P2=2、Candidate immutable=yes，未 blocked。
- 限制：当前主会话内置 tool 实例仍可能是旧加载版本；需要 reload/新 session 才会使用新 wrapper code。R3 review 返回的 P1 是产品 candidate finding，不是 wrapper failure。
- Product impact：无 R2/R3 product candidate 修改；R3 需回产品 Round 修复 P1 后重新验证并 re-review。

## Closed / Deferred

暂无。
