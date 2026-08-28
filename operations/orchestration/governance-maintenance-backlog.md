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

## Open Issues

### GOV-001 — R1 automated review / harness-flow scope 漂移

- 发现时间：2026-08-28
- 触发场景：R1 Independent Review 为让 automated review 通过，Builder 将 Plan、AGENTS、product docs、work log、review artifact 与 `.pi/extensions/harness-flow/index.ts` 纳入修复循环；Git dirty worktree 自动进入 review bundle 后，Reviewer 开始 review harness tool implementation。
- 影响范围：R1 review automation、read confinement、provider auth handoff、Round gate metadata；不影响 R1 产品审计本身对 P0–P3 code/domain disposition 的判断。
- 是否阻断当前产品 Round：不应阻断产品审计内容；只影响 automated review capability。R1 可转为 scope-bounded review 或 Owner-approved distinct human review fallback。
- 当前处理：停止在 R1 中修 bwrap、provider auth、harness-flow；将该问题从 R1 product-audit candidate 中移出。
- 推荐处理：如未来确需自动 review sandbox/auth hardening，单开 governance maintenance task，明确 owner、scope、validation 与 rollback；不得混入产品 Round。
- Owner 决策状态：Owner 已明确要求后续 `.pi/` / harness 问题默认单独记录，除严重恶性 bug 且明确授权外不得修改治理层。

## Closed / Deferred

暂无。
