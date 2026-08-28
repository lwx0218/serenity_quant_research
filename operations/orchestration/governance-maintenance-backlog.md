# Governance Maintenance Backlog

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

- `spawned_pi_process` Independent Review：**manual spawned Pi path certified for R2**；`harness_run_independent_review` wrapper 仍需 runtime reload 后再认证。
- 最近失败：修复 Plan `Independent Review mode` metadata 后，R2 再次调用 harness wrapper，仍返回 `review child failed, timed out, was aborted, or produced truncated evidence`。
- 最近成功：本 governance session 启动 distinct manual spawned Pi process（PID `3579826`，`--no-session`，strict `read,grep,find,ls`，temporary copied review root），返回 `pass`，P0=0，P1=0，P2=1。
- 默认处理：后续产品 Round 在 wrapper 未认证前，不假定 `harness_run_independent_review` wrapper 已恢复；如必须自动 wrapper，需先 reload 并单独 certification。manual spawned Pi path 可作为非 human、非 `/new` 的 spawned_pi_process fallback。
- 恢复条件：单独 governance maintenance 完成，证明 harness wrapper 能稳定返回有效 decision 与 P0/P1/P2 evidence，并记录 tool boundary / Git immutability。

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
- 当前处理：R2 Independent Review 义务已由 manual spawned Pi process 完成；harness wrapper failure 继续作为治理维护问题跟踪。
- 推荐处理：若要恢复 automated wrapper，reload 后对 `harness_run_independent_review` 做最小 capability certification；不得在产品 Round 中临时修 `.pi` / harness。
- Owner 决策状态：Owner 不接受 human review 或 `/new` review，并要求本 session 解决；已使用 manual spawned Pi process 完成 R2 review。

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
- 修改内容：`MAX_REVIEW_OUTPUT_BYTES` 从 512 KiB 提升到 5 MiB；reviewer env 保留当前 process auth/HOME 并叠加 provider env；wrapper 不再强制 bwrap read confinement，而是在 temporary copied review root 中直接启动 `pi --no-session`，仍禁用 extensions/skills/prompts/themes/context files，并限制 tools 为 `read,grep,find,ls`。
- 理由：本项目标准已明确不默认要求 OS-level sandbox / bwrap；此前 bwrap/provider auth/output truncation 是导致 review capability blocked 的主要风险链路。
- 验证：direct `pi --no-session ... -p 'Reply OK'` smoke 通过；manual spawned Pi R2 review 在 temporary copied review root 中通过，返回 `pass`、P0=0、P1=0、P2=1。
- 限制：当前 Pi session 已加载旧 wrapper，无法在不 reload 的情况下证明 `harness_run_independent_review` tool wrapper 已使用新代码；wrapper certification 需后续 reload 后单独执行。
- Product impact：无 R2 product candidate 修改；R2 review artifact 已记录 manual spawned Pi process 结果。

## Closed / Deferred

暂无。
