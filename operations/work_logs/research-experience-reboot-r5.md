# Research Experience Reboot — R5 工作日志

Round: R5 — Company Research Experience
Plan: `operations/planning/research-experience-reboot.md`
Git baseline: `bfa1357d2ef51269b97c4cc6f6f4e6498ebb912d`

## Status

- Round：`R5 — Company Pool, Quick Drawer, And Full Detail`
- Primary implementation history：`r5-company-research` flow，后由主 session 使用 `pi-subagents` 完成 blocker 修复、最终验证与只读 reviewer。
- 当前状态：Owner 于 2026-08-30 确认 acceptance；本日志随 authorized acceptance commit 入库。
- 前序状态：R1–R4 accepted-effective。
- 下一步：完成 acceptance commit/post-commit verification 后停止；不得自动启动 R6。

## Delivered boundary

- Company Pool 默认使用 Card View，并提供共享同一 company universe、filter 与 source context 的 List View。
- accepted path 为 `Card/List → Quick Company Drawer → Expand → Full Company Detail`；第一次点击 company 不直接导航到详情页。
- Quick Drawer 保留 Company Pool 背景，支持 close icon、Esc 与 outside click dismiss。
- card/list activation 使用 pointer-down handling，避免 focus 导致 scroll drift；browser smoke 验证 drawer 打开时 scroll position 保持。
- Drawer expand URL、Full Detail source path 与 Back link 保留 view、filter、Explorer、part 和 chain-node context。
- Full Detail 使用 entity-centric continuous/lightly segmented layout，不恢复旧七标签页。
- candidate、discovery、draft、unknown 等状态明确保持未核验/未审核语义，不视觉升级为 verified/reviewed。

## Non-goals and protected surfaces maintained

- 未实现 Company Comparison。
- 未实现 Research Workspace 写入、ResearchNote、OpenQuestion、Backlink、Graph、New Note 或 editor persistence。
- 未新增或修改 schema、migration、seed facts、stable company IDs、evidence/review/publication/audit semantics。
- 未把 prototype/mock claims 变为研究事实、company exposure、conclusion 或 report claim。
- Open Access 仍只按既有受信任隔离环境约束使用。

## Candidate scope

### Product/runtime

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyDetail.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniverse.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniversePage.css`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniversePage.ts`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniverseState.ts`

### Tests and evidence

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/package.json`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/CompanyUniverseState.test.mjs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-r5-company-browser-smoke.sh`
- `operations/reviews/research-experience-reboot-r5-screenshots/*.png`
- `operations/reviews/research-experience-reboot-r5-independent-review.md`
- `operations/work_logs/research-experience-reboot-r5.md`
- R5 status updates in `operations/planning/research-experience-reboot.md`

## Product-visible evidence

`operations/reviews/research-experience-reboot-r5-screenshots/` contains:

- Card View at 1440×980 and 1920×1080.
- List View at 1440×980 and 1920×1080.
- Quick Drawer at 1440×480 and 1920×480.
- Full Company Detail at 1440×980 and 1920×1080.
- Full Detail part+chain context state at 1920×1080.

The browser smoke asserts Card default, shared Card/List universe, filter/source context, first-click Drawer behavior, close/Esc/outside dismiss, scroll preservation, expand-only Full Detail path, Back-link context, part+chain context, and absence of out-of-scope comparison/persistent-writing UI.

## Validation history

The original `r5-company-research` flow result contains an intermediate validation blocker:

```text
scroll position changed after opening drawer: 45 vs 12
```

That result is historical, not the final R5 disposition. A later worker fixed the activation/focus scroll drift and strengthened the smoke measurement. The following final validation sequence then passed:

```text
cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build
PASS

cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui:browser:r5
PASS — R5 browser smoke and required screenshots generated

dotnet test SerenityQuantResearch.slnx --filter CompanyUniverseServiceTests
PASS — 26 passed

dotnet test SerenityQuantResearch.slnx --filter CompanyExposureEndpointPolicyTests
PASS — 2 passed

cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui
PASS — 14 UI unit tests; R4 and R5 browser smoke passed

dotnet build SerenityQuantResearch.slnx --no-restore
PASS — 0 warnings, 0 errors

dotnet test SerenityQuantResearch.slnx --no-build
PASS — 54 passed, 0 failed, 0 skipped

git diff --check
PASS
```

## Independent review and acceptance

- Reviewer run ID：`a718a769-10f3-4445-a666-86457fa16ea1`。
- Reviewer transcript：`~/.pi/agent/sessions/--project-data_science-serenity_quant_research--/subagent-artifacts/a718a769-10f3-4445-a666-86457fa16ea1_reviewer_transcript.jsonl`。
- Reviewer decision：`OK`。
- Finding：`No issues found`；no blockers。
- Reviewer limitation：reviewer was read-only and did not execute git/tests; it reviewed source, scripts, screenshots and parent-attested final validation. Parent session executed the final command suite and checked no staged changes before the Owner gate。
- Owner acceptance：confirmed on 2026-08-30；acceptance commit authorized。

## Environment / excluded dirty scope

The acceptance commit deliberately excludes pre-existing or tooling-only dirty state:

- `.pi/settings.json` and `.pi/flows/**` / `.pi/npm/**` / `.pi/skills/**`。
- R4 screenshots regenerated by the combined browser smoke。
- `operations/orchestration/governance-maintenance-backlog.md`。
- `operations/reviews/research-experience-reboot-r3-independent-review.md`。

No push is authorized. R6 remains gated by a separate Owner start decision.
