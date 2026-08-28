# Starter Governance Update Plan

## 状态

- Approved: 2026-08-28
- Route: `plan`
- Authorization：Owner 要求忽略既有 untracked `data/`，并补齐缺失治理内容。
- 当前状态：该计划属于治理维护历史，不是 Research Experience Reboot 的产品 Round candidate。

## 目标

将 project-local Harness/Pi governance surface 对齐当时的 `Harness_Workspace` starter baseline，同时不改变业务代码或业务 owned 文档。

## Scope

- 从 canonical starter 更新 starter-managed `.pi/` surface。
- 保留 `.pi/settings.json` 中已有 project-specific declarations，并补充当前 canonical settings。
- 增加缺失的 project-root `Harness_manual.md`。
- 刷新旧 starter-derived `AGENTS.md` 为 external-first、PI-first contract。
- 在本项目中记录治理更新与验证结果。

## Non-goals

- 不读取、修改、stage、删除或 commit 既有 untracked `data/` 内容。
- 不修改业务 source、runtime configuration、项目 `README.md`、intake 或既有 operations evidence。
- 不 commit、不 push。
- 不把 `.pi/extensions/harness-flow` 维护混入 R1 产品审计 candidate。

## Expected Change Surfaces

- `AGENTS.md`
- `Harness_manual.md`
- `.pi/settings.json`
- `.pi/agents/`
- `.pi/extensions/`
- `.pi/skills/`
- `.pi/prompt-templates/`
- `operations/planning/2026-08-28-starter-governance-update.md`
- `operations/work_logs/2026-08-28-starter-governance-update.md`

## Validation

1. Run Workspace `update.sh <project> --check`，全部 managed `.pi` 文件应报告 `OK`。
2. 确认 project name placeholders 已完全渲染。
3. 确认项目有 1 extension、5 skills、3 prompt templates。
4. 确认 `data/` 保持 untracked 且 unchanged。
5. 检查 `git diff --check` 与最终项目状态。

## Risks And Controls

- 官方 updater 对旧 starter fingerprint 和 dirty worktree fail-closed；本计划使用显式 manual merge，而不是削弱 updater 检查。
- Canonical `.pi` 文件从当前 starter 替换；不相关项目文件和额外 `.pi` declarations 保留。
- 不自动 commit 或 push。
- 若后续发现 harness-flow bug，按 `operations/orchestration/independent-review-and-round-scope-standard.md` 作为单独 governance maintenance 处理。
