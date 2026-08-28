# Research Experience Reboot — R2 工作日志

Round: R2 — Research Shell
Plan: `operations/planning/research-experience-reboot.md`
Git baseline: `28ec224ac6070245f51b22f02aff18b815f3d745`

## Status

- Round：`R2 — Research Shell`
- Primary session：`R2-research-shell`
- Start time：`2026-08-28T13:30:43Z`
- 当前状态：`acceptance_commit_authorized_pending_post_commit_verify`
- 治理解释：`harness_run_independent_review` wrapper 仍存在 automated capability blocker；但本 session 已用 distinct manual spawned Pi process 完成 R2 Independent Review 义务。该 process 是 no-session、read-only tools、非 `/new`、非 human review。
- R1 状态：accepted-effective；Owner 已明确启动 R2。
- Owner R2 acceptance：2026-08-28T15:34:02Z，Owner 回复 `accept`。
- Owner 授权 acceptance commit：2026-08-28，Owner 回复“可以，验收吧，commit吧”。
- accepted-effective closeout 需在 commit 后 post-commit verification 通过后确认。

## Boundary

R2 交付 root research entry、minimal independent research-facing top navigation、research layout，并把 primary research navigation 与 secondary admin routes 分离。

### In scope

- `/` 使用 research shell 打开 CPO Explorer 作为 root research entry。
- `/Research/*` 使用轻量 research shell；不渲染 Serenity sidebar。
- primary research navigation 固定为：`CPO Explorer`、`Company Pool`、`Research Workspace`。
- `Dashboard` / `Administration` / `Language` / `Users` / `Roles` / `Permissions` 不出现在 primary research navigation。
- secondary admin route `/Administration/User` 与 admin service `/Services/Administration/User/List` 仍可达。
- 新增 `Research Workspace` 的 R2 placeholder route，只证明 primary nav target 存在；明确不提供 writing、Graph、New Note 或 persistence。
- 更新 focused browser shell smoke，保存 1440px / 1920px product-visible screenshots。

### Non-goals maintained

- 未 redesign Explorer 或 Company 页面内容。
- 未实现 Workspace content；placeholder 明确指向 R6。
- 未删除 admin services/routes 或 Dashboard 文件。
- 未新增 schema、migration、seed、entity、evidence workflow 或 verification policy。
- 未新增大型 frontend framework。

## Candidate scope

### Product/runtime candidate paths

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_Layout.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPage.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/ResearchNavigation.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspacePage.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspacePlaceholder.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/wwwroot/Content/site/site.css`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Imports/MVC/MVC.cs`（sergen generated MVC view constant）

### Test / evidence candidate paths

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh`
- `operations/reviews/research-experience-reboot-r2-screenshots/root-cpo-shell-1440.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/root-cpo-shell-1920.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/company-pool-shell-1440.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/company-pool-shell-1920.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/secondary-admin-route-1440.png`
- `operations/work_logs/research-experience-reboot-r2.md`
- `operations/reviews/research-experience-reboot-r2-independent-review.md`

## Context scope

- `AGENTS.md`
- `operations/orchestration/independent-review-and-round-scope-standard.md`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md`
- `docs/product/README.md`
- `docs/product/experience-map.md`
- `docs/product/visual-language.md`
- `docs/product/acceptance-contract.md`
- `operations/planning/research-experience-reboot.md`
- `operations/orchestration/research-experience-reboot.md`
- `operations/reviews/reboot-p3-code-disposition.md`

## Environment / dirty-worktree scope

R2 start 已记录 protected status：

```text
HEAD: 28ec224ac6070245f51b22f02aff18b815f3d745
?? data/
?? src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md
```

Review 前 `git status --short` 还包含 pre-existing governance / context dirty state：

- `.pi/agents/README.md`
- `.pi/prompt-templates/governance-loop.md`
- `.pi/settings.json`
- `.pi/skills/governance-loop-entry/SKILL.md`
- `.pi/skills/grill-me/SKILL.md`
- `.pi/skills/grill-with-docs/SKILL.md`
- `.pi/skills/grilling/SKILL.md`
- `.pi/extensions/`
- `.pi/prompt-templates/project-kickoff.md`
- `.pi/prompt-templates/session-handoff.md`
- `.pi/skills/domain-modeling/`
- `data/`
- `operations/planning/research-experience-reboot.md`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md`

这些不属于 R2 product candidate；`.pi/` / harness 不修改、不评审为产品 candidate。

## Implementation notes

1. `_Layout.cshtml` 增加 research-shell branch：root 与 `/Research/*` 渲染独立 topbar + centered research main；其他 routes 继续使用 `_Sidebar`。
2. Root `/` 从 demo Dashboard 改为直接渲染 CPO Explorer view；`/Dashboard` 继续保留 legacy dashboard secondary route。
3. `ResearchNavigation.cs` 从中文 CPO submenu 替换为三项 primary research nav metadata：CPO Explorer / Company Pool / Research Workspace。
4. `ResearchWorkspacePage` 与 placeholder view 只作为 R2 shell/nav target；文案声明 R6 才交付 read-only Workspace，并禁止 writing/Graph/New Note/persistence。
5. `site.css` 增加 light / restrained / technical research shell tokens、topbar、pill nav、main container 与 placeholder style。
6. `run-browser-smoke.sh` 改为 R2 focused assertions，并生成截图 evidence。

## Automated validation

最终验证结果：

```text
git diff --check
PASS

cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build
PASS — esbuild checked 34 output files, none changed

dotnet build SerenityQuantResearch.slnx --no-restore
PASS — 0 warnings, 0 errors

dotnet test SerenityQuantResearch.slnx --no-build
PASS — 54 passed, 0 failed, 0 skipped

cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui
PASS — node UI unit 10 passed; R2 browser shell smoke passed
```

R2 browser smoke assertions covered：

- root `/` renders research shell and CPO Explorer at 1440px / 1920px。
- `/Research/Companies` renders research shell and active Company Pool at 1440px / 1920px。
- primary nav labels/hrefs exactly equal `CPO Explorer`、`Company Pool`、`Research Workspace`。
- banned primary-nav labels absent：Dashboard、Administration、Language、Users、Roles、Permissions。
- Serenity sidebar absent from research shell。
- `/Research/Workspace` placeholder route exists, active nav is Research Workspace, and no deferred writing controls leak into R2。
- `/Administration/User` remains directly available outside research shell; admin service `/Services/Administration/User/List` returns 200 in Open Access maintenance mode。

## Product-visible evidence

Screenshots generated by `npm run test:ui:browser`：

- `operations/reviews/research-experience-reboot-r2-screenshots/root-cpo-shell-1440.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/root-cpo-shell-1920.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/company-pool-shell-1440.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/company-pool-shell-1920.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/secondary-admin-route-1440.png`

## Protected surface check

- No migration/entity/seed/evidence workflow/policy edits were made by R2 candidate.
- Existing `data/` untracked state preserved.
- Existing `.pi/` governance dirty state preserved and not modified by this implementation session.

## Independent Review status

Builder completed the required automated-review call after automated validation, then this governance maintenance session completed a manual spawned Pi Independent Review because Owner did not accept human review or `/new` review.

- Attempt 1：blocked because Builder passed screenshot directory as `scopePaths`; harness requires regular files. Disposition：input packaging error, corrected by enumerating screenshot files.
- Attempt 2：blocked by harness result `review child failed, timed out, was aborted, or produced truncated evidence`.
- Attempt 3：Owner 要求“执行一次 Independent review”后进行一次额外 retry；blocked by harness result `Independent Review mode must be spawned_pi_process or human_review`。
- Attempt 4：Owner 说明 governance 已改并要求启动独立 review 后再次 retry；mode 字段解析 blocker 消失，但 harness 仍返回 `review child failed, timed out, was aborted, or produced truncated evidence`。
- Successful Review：本 session 用 distinct manual spawned Pi process 完成 read-only review：PID `3579826`，`--no-session`，`--no-extensions`，`--no-skills`，`--no-prompt-templates`，`--no-themes`，`--no-context-files`，`--tools read,grep,find,ls`，working root 为 temporary copied review root。Child exit `0`，stderr empty，返回 `HARNESS_REVIEW_RESULT`。

Durable review artifact：`operations/reviews/research-experience-reboot-r2-independent-review.md`。

Review decision：`pass`，P0=0，P1=0，P2=1。

P2 disposition：截图脚本在部分截图中未等待异步研究内容加载稳定，导致个别 screenshot 仍显示 loading / empty content。Builder 接受为 non-blocking：R2 acceptance 重点是 shell/nav/admin separation/placeholder boundary，browser DOM assertions 已覆盖这些合同；该项作为 screenshot stability hardening backlog，不阻塞 Owner R2 acceptance。

`harness_run_independent_review` wrapper capability blocker 仍记录为 `operations/orchestration/governance-maintenance-backlog.md` 的 `GOV-002`；manual spawned Pi capability certification 与 wrapper 修复状态分开记录。

## Owner acceptance

- Acceptance time：`2026-08-28T15:34:02Z`
- Owner response：`accept`
- Accepted scope：R2 Research Shell candidate as documented above, including P2 non-blocking disposition.
- Remaining gates before accepted-effective：Builder commits；post-commit verification passes。
- Commit authorization：Owner replied “可以，验收吧，commit吧”。

Required next gate：执行 acceptance commit 与 post-commit verify。R3 不得自动启动；仅在 R2 accepted-effective 后准备 R3 handoff。
