# Starter Governance Update 工作日志

## 日期

2026-08-28

## 结果

`pass_with_existing_untracked_data`

项目本地 Harness/Pi governance surface 已手工对齐当时的 `Harness_Workspace` starter baseline。官方 updater 的 fail-closed recognition 与 clean-worktree checks 未被削弱或绕过。

## 变更

- 刷新 root `AGENTS.md` 为 current external-first、PI-first project contract。
- 增加 root `Harness_manual.md`。
- 更新 `.pi/settings.json`，保留既有 project-specific keys。
- 更新 `.pi/agents/README.md` 与既有 baseline skills/prompts。
- 增加 project-local `harness-flow` extension。
- 增加 optional `domain-modeling` skill 与 supporting files。
- 增加 `/project-kickoff` 与 `/session-handoff` prompt templates。

## 边界

- Project `README.md` 作为 business-owned documentation 保留。
- 既有 intake、plans、reviews、work logs、source 与 runtime configuration 未由本次 reconciliation 修改。
- 既有 untracked `data/seeds/cpo/cpo-research-seed.json` 被显式忽略，未修改、stage、删除或 commit。
- 未 commit、未 push。

## 验证

- `update.sh <project-root> --check`：全部 managed `.pi` entries 报告 `OK`。`<project-root>` 表示当前仓库根目录，不记录宿主机绝对路径。
- Root project-owned status：`AGENTS.md` 与 `Harness_manual.md` 匹配当时 rendered starter；business `README.md` 有意保持项目版本。
- Resource counts：1 extension、5 skills、3 prompt templates。
- Unresolved `__PROJECT_NAME__` placeholders：none。
- `git diff --check`：passed。
- Data file hash before/after：`f30b9e9b7aae5e5ba95163e8868c87cbad4bde28` unchanged。

## 当前治理解释

本记录属于 governance maintenance history，不是 R1 product-audit candidate。`.pi/extensions/harness-flow` 后续如需修复，应按 `operations/orchestration/independent-review-and-round-scope-standard.md` 作为单独 governance maintenance 处理。

## Remaining Gate

Review Git diff。Owner 需要单独决定 governance update 与既有 untracked `data/` seed 是否提交，以及是否分开提交。
