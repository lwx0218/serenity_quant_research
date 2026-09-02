# Research Experience Reboot — R6 工作日志

Round: R6 — Read-only Linked Research Workspace
Plan: operations/planning/research-experience-reboot.md
Git baseline: 19392d9d2ba73cbd26949e36651ec402bb6795f0

## Metadata

- Project: serenity_quant_research
- Document type: other
- Status: approved
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: operations/planning/research-experience-reboot.md

## Status

- Round：`R6 — Read-only Linked Research Workspace`
- Primary implementation session：`R6-readonly-research-workspace`（当前 Pi session `01a0526a-f33c-72f3-8f89-50442f4f61c5`）。
- Owner start decision：Owner 已明确正式启动且仅启动 canonical fixed Round `R6-readonly-research-workspace`；批准本 Round 使用 formal workflow、pi-subagents 开发编排、开发期 fresh review，以及最终单独 Formal Independent Review。
- 当前状态：Owner 已验收 R6（带已记录 formal review limitation），并在监督复核与 evidence-P2 修复通过后单独授权 acceptance commit；本日志随该 commit 入库，最终以 post-commit verification 结果确认 accepted-effective。
- 前序状态：R1–R5 accepted-effective；R7 未启动且不得自动启动。
- Commit / push：Owner 已授权一次 R6 acceptance commit；不 push。

## Round-Start Baseline

```text
HEAD: 19392d9d2ba73cbd26949e36651ec402bb6795f0
Branch: product-reboot
```

Round start `git status --short` snapshot：

```text
 M .pi/settings.json
 M AGENTS.md
 M operations/orchestration/governance-maintenance-backlog.md
 M operations/reviews/research-experience-reboot-r3-independent-review.md
 M operations/reviews/research-experience-reboot-r4-screenshots/hover-3d-laser-1440.png
 M operations/reviews/research-experience-reboot-r4-screenshots/hover-3d-laser-1920.png
 M operations/reviews/research-experience-reboot-r4-screenshots/hover-flat-pic-1440.png
 M operations/reviews/research-experience-reboot-r4-screenshots/hover-flat-pic-1920.png
 M operations/reviews/research-experience-reboot-r4-screenshots/idle-3d-1440.png
 M operations/reviews/research-experience-reboot-r4-screenshots/idle-3d-1920.png
 M operations/reviews/research-experience-reboot-r4-screenshots/idle-flat-1440.png
 M operations/reviews/research-experience-reboot-r4-screenshots/idle-flat-1920.png
 M operations/reviews/research-experience-reboot-r4-screenshots/reset-blank-1440.png
 M operations/reviews/research-experience-reboot-r4-screenshots/reset-blank-1920.png
 M operations/reviews/research-experience-reboot-r4-screenshots/selected-3d-fiber-interface-1440.png
 M operations/reviews/research-experience-reboot-r4-screenshots/selected-3d-fiber-interface-1920.png
 M operations/reviews/research-experience-reboot-r4-screenshots/selected-flat-host-asic-1440.png
 M operations/reviews/research-experience-reboot-r4-screenshots/selected-flat-host-asic-1920.png
 M operations/reviews/research-experience-reboot-r4-screenshots/view-switch-host-asic-1440.png
 M operations/reviews/research-experience-reboot-r4-screenshots/view-switch-host-asic-1920.png
?? .pi/flows/
?? .pi/npm/
?? .pi/skills/manage-flows/
```

Round-start hashes / immutability aids：

```text
git status --short hash: e01e42667f1a5d1c0f888df0d43e0245a05d9b864e2fa10ce43c5555d15800fe
pre-existing protected text diff hash (.pi/settings, AGENTS, governance backlog, R3 review): 7b50c0b36543ef0ccb615f2bdef2edd5e759f123f725f17e45a3aef199a462cd
pre-existing R4 screenshot hash bundle: 2d328ae7fb60de83298654919ab6d4129d9e90c648ac150cd44adf3550c701e2
migration tracked-file hash bundle: 2cc7fdd58d1d8cbc032809a9d6e2238f3be5b08268958617071ffce5071bf9b0
staged files at start: none
```

## Scope Classification

### Candidate scope（R6 允许请求验收的变更）

Planned candidate paths are limited to R6 read-only Workspace implementation/evidence:

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/**`
- narrowly required read-only aggregation DTO/service/endpoint files under `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Services/**` and `Endpoints/**`
- generated ServerTypes caused by approved read-only service DTO changes only
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyDetail.cshtml` / `CompanyUniversePage.ts` only for source-context-preserving Workspace links
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts` / related view only for Explorer-to-Workspace navigation links
- focused tests under `tests/SerenityQuantResearch.Tests/**` and `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/**`
- `operations/reviews/research-experience-reboot-r6-screenshots/**`
- `operations/reviews/research-experience-reboot-r6-independent-review.md`
- `operations/work_logs/research-experience-reboot-r6.md`
- R6 status-only updates in `operations/planning/research-experience-reboot.md`

### Context scope（只读判断材料）

- `AGENTS.md`
- `operations/orchestration/independent-review-and-round-scope-standard.md`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md`
- `docs/product/README.md`
- `docs/product/experience-map.md`
- `docs/product/research-workspace-spec.md`
- `docs/product/prototypes/research-workspace-v0.1.html`
- `docs/product/visual-language.md`
- `docs/product/acceptance-contract.md`
- `docs/research-baseline/evidence-contract.md`
- `operations/planning/research-experience-reboot.md`
- `operations/orchestration/research-experience-reboot.md`
- `operations/reviews/reboot-p3-code-disposition.md`
- accepted R1/R5 work logs and independent reviews
- current source/tests needed to judge R6 implementation

### Environment / pre-existing dirty state（保护，不纳入 R6 candidate）

- `.pi/settings.json`
- `.pi/flows/**`
- `.pi/npm/**`
- `.pi/skills/manage-flows/**`
- pre-existing `AGENTS.md` hunk
- `operations/orchestration/governance-maintenance-backlog.md`
- `operations/reviews/research-experience-reboot-r3-independent-review.md`
- `operations/reviews/research-experience-reboot-r4-screenshots/**`

## Protected / Forbidden Surfaces

R6 must not modify or introduce:

- database schema or migrations under `src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations/**`
- new persistent entities, ResearchNote, OpenQuestion, Backlink, Graph, Markdown knowledge base, editor persistence, write endpoints, or identity configuration
- evidence/review/publication/audit semantics
- `.pi/**` / harness tooling or governance runtime
- seed facts / prototype mock data as production research facts
- R7 work, including Evidence endpoint actor enforcement or legacy cleanup

## Definition Of Ready Checklist

- [x] Owner R6 start decision received via Pi Fleet kickoff.
- [x] Required governance/product/research contracts read.
- [x] R1/R5 applicable work logs/reviews read.
- [x] Current HEAD and dirty baseline captured.
- [x] Candidate/context/environment/protected surfaces classified.
- [x] `subagent({ action: "list", capabilities: true })` run; executable agents identified.
- [x] Read-only scouts complete.
- [x] Single writer implementation complete.
- [x] Focused/full validation complete.
- [x] Development fresh review complete and findings dispositioned; fresh re-review returned `OK` with no remaining P2.
- [x] Formal Independent Review attempted twice and returned `not_applicable` because harness remained `simple/passive`; Owner explicitly waived/modified the R6 formal gate with limitation.
- [x] Owner gate ready checkpoint sent; Owner accepted R6 with documented limitation and explicitly did not authorize commit.

## Orchestration Contract

R6 uses pi-subagents orchestrator mode with one top-level async workflow. Parallelism is limited to read-only scouting/review/validation. The shared checkout has exactly one writer during implementation/fix phases; no `worktree: true` is used because protected dirty state is present in the current checkout.

Development loop target:

```text
read-only scouts → sole writer implementation + validation → fresh read-only reviewers → parent synthesis → sole writer fixes if needed → affected validation → fresh re-review (max two fix rounds)
```

Development reviewers do not satisfy the final Formal Independent Review obligation. The final review must be invoked separately by the primary/top-level session after candidate stabilization and validation.

## Validation Plan

Required R6 validation/evidence before Owner gate:

- schema-unchanged proof (`git diff --exit-code -- src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations` and migration hash comparison)
- focused read-only Workspace projection tests
- component/company Workspace routes
- linked-object/backlink navigation and source context assertions
- evidence state and read-only gap/open-question separation assertions
- `cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build`
- `dotnet build SerenityQuantResearch.slnx --no-restore`
- `dotnet test SerenityQuantResearch.slnx --no-build`
- `cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui`
- 1440/1920 component Workspace screenshots
- 1440/1920 company Workspace screenshots
- Explorer/Company-to-Workspace navigation sequence evidence

## Running Notes

- 2026-08-30T11:26:40Z — baseline/DoR established; no production source/test changes yet.

## Implementation Evidence — writer pass

- 2026-08-30T12:20Z — Implemented R6 read-only linked-object Workspace candidate without worktree, commit, staging, schema, migration, seed, identity, evidence/review/publication/audit semantic, or write-endpoint changes.
- Added read-only `ResearchWorkspaceService` / endpoint projection over existing persistent rows only: physical modules/parts, technology links, chain-node links, company exposures, evidence/source rows, and conclusion-evidence links.
- Replaced `/Research/Workspace` placeholder route with a knowledge-centric Workspace page: lightweight existing-object tree, document-like current-object center, linked objects, derived relationship context, evidence/status context, separated existing conclusions and read-only gaps/unresolved questions.
- Added source-context-preserving Workspace navigation from CPO Explorer selected component/part, Company Pool Quick Drawer, and Full Company Detail. Existing Company Detail source/filter context is carried into `objectType=company&companyId=...` Workspace URLs.
- Added focused .NET projection/route tests and UI state/browser assertions. R6 browser smoke captured component/company 1440/1920 screenshots plus Explorer and Company Detail navigation sequence under `operations/reviews/research-experience-reboot-r6-screenshots/`.

## Validation Evidence — writer pass

Commands run from repo root unless noted:

```text
FAILED then fixed: dotnet test SerenityQuantResearch.slnx --filter ResearchWorkspace --no-restore
- Initial failure: missing `using Serenity.Services;` in new test file.
- After fix: passed, 6/6 ResearchWorkspace tests.

PASSED: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui:unit
- 19/19 UI state tests passed, including R6 Workspace URL/state/forbidden-control assertions.

PASSED: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build
- TypeScript/esbuild completed; Workspace bundle emitted.

PASSED: dotnet build SerenityQuantResearch.slnx --no-restore
- Build succeeded, 0 warnings, 0 errors.

PASSED: dotnet test SerenityQuantResearch.slnx --no-build
- 60/60 .NET tests passed.

FAILED then fixed: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui:browser:r6
- Initial failures were browser-smoke assertion/harness issues (Workspace wait predicate too strict, SVG click helper, seed display-name assumptions), not source behavior failures.
- After fixes: passed; screenshots saved to `operations/reviews/research-experience-reboot-r6-screenshots/`.

PASSED: git diff --exit-code -- src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations
PASSED: git diff --exit-code -- data/seeds
PASSED: git diff --check
PASSED: grep -R "Create.Table(\"ResearchNote\|Create.Table(\"OpenQuestion\|Create.Table(\"Backlink\|class ResearchNote\|class OpenQuestion\|class Backlink" -n src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations/DefaultDB || true
- No migration/seed diff; no persistent ResearchNote/OpenQuestion/Backlink table/entity creation found.
```

Superseded writer limitation:

- Initial writer pass did not run full `npm run test:ui` because default R4/R5 screenshot scripts would touch protected pre-existing R4 screenshot paths. Parent later ran the full command with `UI_SCREENSHOT_DIR=/tmp/serenity-r6-full-ui-4S0PSU`, avoiding protected screenshot churn; see post-review validation below.

Screenshot evidence captured:

- `operations/reviews/research-experience-reboot-r6-screenshots/r6-workspace-component-host-asic-1440.png`
- `operations/reviews/research-experience-reboot-r6-screenshots/r6-workspace-component-host-asic-1920.png`
- `operations/reviews/research-experience-reboot-r6-screenshots/r6-workspace-company-broadcom-1440.png`
- `operations/reviews/research-experience-reboot-r6-screenshots/r6-workspace-company-broadcom-1920.png`
- `operations/reviews/research-experience-reboot-r6-screenshots/r6-nav-explorer-selected-component-1440.png`
- `operations/reviews/research-experience-reboot-r6-screenshots/r6-nav-explorer-to-workspace-1440.png`
- `operations/reviews/research-experience-reboot-r6-screenshots/r6-nav-company-detail-source-1440.png`
- `operations/reviews/research-experience-reboot-r6-screenshots/r6-nav-company-detail-to-workspace-1440.png`

Residual risks / limitations:

- Existing generated MVC/ServerTypes outputs changed as build/codegen artifacts of the R6 read-only endpoint/page; no migration, seed, schema, write endpoint, or persistent research-writing entity was introduced.

## Development Review Evidence

Development fresh review after the worker pass used two distinct read-only reviewers:

- `product-data-safety-review` (`f57112e1-18e5-4ac4-9caf-defa38152fb3`) returned `BLOCK` with two P1 findings.
- `correctness-tests-maintainability-review` (`0b94ae78-7bdb-4c90-bfe1-61126202afe9`) returned `OK with notes` with one P2 finding.

Findings and disposition:

1. **P1 — full UI validation was stale / older smoke expected Workspace placeholder.** Accepted. Updated `tests-ui/run-browser-smoke.sh` to assert the new read-only Workspace surface (`#research-workspace-app`, read-only state, default component object, no edit/deferred controls) instead of `.research-placeholder`.
2. **P1 — evidence-derived backlinks rendered as `href="#"` dead links.** Accepted. Updated `ResearchWorkspacePage.ts` so evidence backlinks render as non-clickable read-only context cards with explicit dataset/ARIA context; object backlinks remain navigable.
3. **P2 — service request aliases did not infer object type before stable-ID fallback.** Accepted. Updated `ResearchWorkspaceService.Retrieve` to infer `objectType` before resolving `CompanyId` / `PartId` / `ChainNodeId`; added alias regression tests.

## Post-review Fix Validation

Commands run after development-review fixes:

```text
PASSED: git diff --exit-code -- src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations
PASSED: git diff --exit-code -- data/seeds
PASSED: dotnet test SerenityQuantResearch.slnx --filter ResearchWorkspace --no-restore
- 9/9 focused ResearchWorkspace tests passed; no warnings after analyzer cleanup.
PASSED: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui:unit
- 19/19 UI state tests passed.
PASSED: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build
PASSED: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui:browser:r6
- R6 canonical screenshots regenerated under `operations/reviews/research-experience-reboot-r6-screenshots/`.
PASSED: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && UI_SCREENSHOT_DIR=/tmp/serenity-r6-full-ui-4S0PSU npm run test:ui
- R4 Explorer, R5 Company, and R6 Workspace browser suites passed without touching protected screenshot paths.
PASSED: dotnet build SerenityQuantResearch.slnx --no-restore
- Build succeeded, 0 warnings, 0 errors.
PASSED: dotnet test SerenityQuantResearch.slnx --no-build
- 63/63 .NET tests passed.
PASSED: git diff --check
PASSED: git diff --cached --name-only
- no staged files.
```

## Development Re-review Evidence

Fresh read-only re-review after the fix pass:

- Reviewer run ID：`9c9a7bde-a202-49bc-9c7f-1f5e7d97d508`
- Output artifact：`/home/levi_luo/.pi/agent/sessions/--project-data_science-serenity_quant_research--/subagent-artifacts/outputs/9c9a7bde-a202-49bc-9c7f-1f5e7d97d508/reviews/r6-fix-rereview.md`
- Decision：`OK`
- Findings：No issues found；no remaining P2 notes；`BLOCKING_FINDINGS: no`。

Reviewer confirmed:

1. Prior P1 stale full UI smoke fixed by `tests-ui/run-browser-smoke.sh` assertions against the new read-only Workspace surface.
2. Prior P1 dead evidence backlinks fixed by rendering evidence backlinks as non-clickable read-only context, not `href="#"` navigation.
3. Prior P2 request alias inference fixed by inferring object type before stable-ID fallback, with focused test coverage.

Development reviewers are supplemental and do not satisfy the final Formal Independent Review gate. Candidate proceeded to separate formal `harness_run_independent_review` invocation.

## Formal Independent Review Attempt

- Invocation time：2026-08-30T12:10:00Z
- Tool：`harness_run_independent_review`
- Result：`not_applicable`
- Reason：Harness is in `simple/passive` mode; formal Round, handoff, review, and widget capabilities require explicit Owner-approved formal activation.
- Review artifact：`operations/reviews/research-experience-reboot-r6-independent-review.md`

No formal reviewer child was created and no valid formal P0/P1/P2 findings exist. This is a formal review capability/gate blocker, not a product candidate failure.

Owner then selected `启用/激活 formal harness 后重新调用 harness_run_independent_review`. Builder retried once with candidate hash bundle `6a4f85dfe7968f98b7b317b6b9027443b1df481841e8c866487706fe98c5781b`; the tool again returned `not_applicable` for the same simple/passive-mode reason. Current runtime therefore still has not activated formal harness capability. Per scope standard, Builder will not repeat the same capability retry loop or modify `.pi/**` / harness inside R6 product scope.

Owner selected `明确修改/豁免 formal review gate，带 limitation 进入 Owner 验收判断`. Decision effect for R6 only: no valid Formal Independent Review child ran and formal P0/P1/P2 are not assessed, but Owner allows R6 to proceed to Product Owner acceptance judgment with this visible review limitation.

Owner then selected `验收 R6（带已记录 formal review limitation；不授权 commit）`. R6 Product Owner acceptance gate is passed with the documented limitation. R6 is not accepted-effective because acceptance commit/post-commit verification are not authorized or performed; no commit or push is authorized; R7 remains not started.

## Final Candidate Manifest / Environment Snapshot

Final commit-readiness evidence correction recorded after Owner acceptance-with-limitation. This is evidence-only; no product source/test/screenshot file is modified by this correction.

```text
Timestamp: 2026-08-30T12:10Z
HEAD: 19392d9d2ba73cbd26949e36651ec402bb6795f0
status hash including environment: 6c3ab7ba17580f6099f00521f68b1c7cba467c60065800940457855782630c58
corrected R6 candidate path count: 36
corrected R6 manifest-file hash: 43eda903b428540e0c89c247e57ccf6d1c0e79bfa0f5c41ba885983f1fcfa9f6
corrected R6 hashable-content path count: 34
corrected R6 hashable-content bundle hash: 255682f709766e549b217816f47c87b09066300df29a056aeaa9aef1a33e5e4e
protected text diff hash: 7b50c0b36543ef0ccb615f2bdef2edd5e759f123f725f17e45a3aef199a462cd
protected R4 screenshot hash bundle: 2d328ae7fb60de83298654919ab6d4129d9e90c648ac150cd44adf3550c701e2
non-candidate visual-audit residue hash bundle: 965442f31b7c0bc6ff1bf2e8c8d663ff1098f30920008affce9e1f29f95039ca
```

Manifest generation algorithm:

```bash
{ git diff --name-only; git ls-files --others --exclude-standard; } | sort -u \
  | grep -v '^\.pi/' \
  | grep -v '^AGENTS.md$' \
  | grep -v '^operations/orchestration/governance-maintenance-backlog.md$' \
  | grep -v '^operations/reviews/research-experience-reboot-r3-independent-review.md$' \
  | grep -v '^operations/reviews/research-experience-reboot-r4-screenshots/' \
  | grep -v '^operations/reviews/2026-08-30-research-ui-visual-audit/' \
  > /tmp/r6-candidate-manifest-corrected.txt
sha256sum /tmp/r6-candidate-manifest-corrected.txt
```

Self-referential evidence rule for content hash:

- The 36-path manifest includes R6 evidence files `operations/work_logs/research-experience-reboot-r6.md` and `operations/reviews/research-experience-reboot-r6-independent-review.md` because they are R6 durable candidate evidence.
- The reproducible content hash intentionally excludes those two self-referential evidence files, because writing the hash into either file changes its own bytes.
- Therefore the content bundle hashes 34 non-self-referential candidate paths with:

```bash
grep -v '^operations/work_logs/research-experience-reboot-r6.md$' /tmp/r6-candidate-manifest-corrected.txt \
  | grep -v '^operations/reviews/research-experience-reboot-r6-independent-review.md$' \
  > /tmp/r6-candidate-hashable-subset.txt
while IFS= read -r path; do sha256sum "$path"; done < /tmp/r6-candidate-hashable-subset.txt \
  > /tmp/r6-candidate-hashable-sha256.txt
sha256sum /tmp/r6-candidate-hashable-sha256.txt
```

Corrected 36-path R6 candidate manifest:

```text
operations/planning/research-experience-reboot.md
operations/reviews/research-experience-reboot-r6-independent-review.md
operations/reviews/research-experience-reboot-r6-screenshots/r6-nav-company-detail-source-1440.png
operations/reviews/research-experience-reboot-r6-screenshots/r6-nav-company-detail-to-workspace-1440.png
operations/reviews/research-experience-reboot-r6-screenshots/r6-nav-explorer-selected-component-1440.png
operations/reviews/research-experience-reboot-r6-screenshots/r6-nav-explorer-to-workspace-1440.png
operations/reviews/research-experience-reboot-r6-screenshots/r6-workspace-company-broadcom-1440.png
operations/reviews/research-experience-reboot-r6-screenshots/r6-workspace-company-broadcom-1920.png
operations/reviews/research-experience-reboot-r6-screenshots/r6-workspace-component-host-asic-1440.png
operations/reviews/research-experience-reboot-r6-screenshots/r6-workspace-component-host-asic-1920.png
operations/work_logs/research-experience-reboot-r6.md
src/SerenityQuantResearch/SerenityQuantResearch.Web/Imports/MVC/ESM.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/Imports/MVC/MVC.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/Initialization/Startup.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniversePage.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Endpoints/ResearchWorkspaceEndpoint.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Services/ResearchWorkspaceService.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspace.cshtml
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspacePage.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspacePage.css
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspacePage.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspaceState.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/ResearchWorkspaceService.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.ResearchWorkspaceRequest.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.ResearchWorkspaceResponse.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.WorkspaceBacklink.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.WorkspaceEvidenceContext.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.WorkspaceObjectSummary.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.WorkspaceTreeGroup.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/package.json
src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/ResearchWorkspaceState.test.mjs
src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh
src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-r6-workspace-browser-smoke.sh
tests/SerenityQuantResearch.Tests/ResearchWorkspaceServiceTests.cs
```

Excluded environment/protected surfaces:

- `.pi/**`
- `AGENTS.md`
- `operations/orchestration/governance-maintenance-backlog.md`
- `operations/reviews/research-experience-reboot-r3-independent-review.md`
- `operations/reviews/research-experience-reboot-r4-screenshots/**`
- `operations/reviews/2026-08-30-research-ui-visual-audit/**`（non-candidate visual-audit residue）

All excluded paths remain unreset, unstashed, uncleaned, unstaged, and outside R6 candidate.

## Commit-readiness Evidence P2 Correction

Owner authorized the R6 primary Session to fix a commit-readiness evidence P2 after supervision review found the final corrected candidate count/hash and DoR closeout were not durable enough. Scope was limited to durable evidence only.

Changed paths in this evidence-only correction:

- `operations/work_logs/research-experience-reboot-r6.md`
- `operations/reviews/research-experience-reboot-r6-independent-review.md`

No product source, tests, screenshots, schema, seed, `.pi/**`, protected dirty state, commit, push, or R7 scope was modified by this correction.

Validation after the evidence-only correction:

```text
PASS: python3 scripts/check-document-governance.py --check
PASS: git diff --check
PASS: git diff --exit-code -- src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations
PASS: git diff --exit-code -- data/seeds
PASS: git diff --cached --name-only  (no staged files)
protected text diff hash: 7b50c0b36543ef0ccb615f2bdef2edd5e759f123f725f17e45a3aef199a462cd
protected R4 screenshot hash bundle: 2d328ae7fb60de83298654919ab6d4129d9e90c648ac150cd44adf3550c701e2
non-candidate visual-audit residue hash bundle: 965442f31b7c0bc6ff1bf2e8c8d663ff1098f30920008affce9e1f29f95039ca
status hash including environment: 6c3ab7ba17580f6099f00521f68b1c7cba467c60065800940457855782630c58
corrected candidate path count: 36
corrected manifest-file hash: 43eda903b428540e0c89c247e57ccf6d1c0e79bfa0f5c41ba885983f1fcfa9f6
corrected hashable-content path count: 34
corrected hashable-content bundle hash: 255682f709766e549b217816f47c87b09066300df29a056aeaa9aef1a33e5e4e
```

## Acceptance Commit Authorization

- Owner 在 evidence-P2 修复和监督 Session 独立复核通过后，单独授权创建 R6 acceptance commit；不授权 push，不启动 R7。
- Acceptance commit candidate 仍严格使用上述 36-path manifest；所有 pre-existing dirty state 与 `operations/reviews/2026-08-30-research-ui-visual-audit/**` 继续排除。
- Plan closeout 状态已更新为 R1–R6 accepted-effective、Active Round none；该状态须由 acceptance commit 和随后成功的 post-commit verification 共同确认。
- Formal Independent Review limitation 保持原样：没有 formal child、formal P0/P1/P2 未评估、Owner 仅对 R6 修改/豁免该 gate，后续 Round 不继承。
- Post-authorization manifest-file hash：`43eda903b428540e0c89c247e57ccf6d1c0e79bfa0f5c41ba885983f1fcfa9f6`（36 paths）。
- Post-authorization hashable-content bundle hash：`fcf363001cc99b1ad0db8151e4261ed9079e8b8f52c3e96f1b6872a58708fdb3`（34 non-self-referential paths；排除本 work log 与 R6 review artifact）。
