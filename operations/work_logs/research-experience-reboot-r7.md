# Research Experience Reboot — R7 工作日志

Round: R7 — Integrated Journey, Regression, And Legacy Cleanup
Plan: operations/planning/research-experience-reboot.md
Git baseline: 2c10022af1ca13a41acc362a9994062fe684a45e

## Metadata

- Project: serenity_quant_research
- Document type: other
- Status: active
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: operations/planning/research-experience-reboot.md

## Status

- Round：`R7 — Integrated Journey, Regression, And Legacy Cleanup`
- Primary session：`R7-reboot-integration-cleanup`
- Owner start decision：Owner 已明确正式启动且仅启动 canonical final Round R7。
- 当前状态：`owner_accepted_commit_authorized`；R7 candidate、full validation、development review/fix/re-review 均已完成；Owner 已明确修改/豁免 R7 formal review gate with limitation，并已验收 R7、授权 acceptance commit（不 push）。
- 前序状态：R1–R6 accepted-effective；acceptance commit HEAD 为 `2c10022af1ca13a41acc362a9994062fe684a45e`。
- Commit / push：未授权；不得自动 commit 或 push。
- Progression：R7 完成后停止；Evidence/Conclusion/Report UI 必须使用后续新 Plan，当前不得启动。

## Round-start baseline

```text
Timestamp (UTC): 2026-08-30T13:03:56Z
HEAD: 2c10022af1ca13a41acc362a9994062fe684a45e
Branch: product-reboot
Staged files: none
Status hash: 1c5846afd0cdab23acb1a60217a27ce458e100dc539114f5f7d65c32aafff939
```

Round-start `git status --short`：

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
?? operations/reviews/2026-08-30-research-ui-visual-audit/
```

Round-start protected/hash evidence：

```text
pre-existing protected text diff hash: 7b50c0b36543ef0ccb615f2bdef2edd5e759f123f725f17e45a3aef199a462cd
pre-existing R4 screenshot hash bundle: 2d328ae7fb60de83298654919ab6d4129d9e90c648ac150cd44adf3550c701e2
non-candidate visual-audit residue hash bundle: 965442f31b7c0bc6ff1bf2e8c8d663ff1098f30920008affce9e1f29f95039ca
migration tracked-file hash bundle: 2cc7fdd58d1d8cbc032809a9d6e2238f3be5b08268958617071ffce5071bf9b0
seed tracked-file hash bundle: 17a236f1629ca4b2fed69a58db2e9079fcec7a014e64c59a47c3dcaab91ce116
```

## Scope classification

### Candidate scope

仅允许 R7 integration/security/cleanup 实现与证据：

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Endpoints/EvidenceWorkflowEndpoint.cs`
- endpoint-level machine rejection / human acceptance tests under `tests/SerenityQuantResearch.Tests/**`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPage.cs` 的安全 secondary-route redirect
- 仅当 replacement + exhaustive no-reference proof 成立时删除 R1 `DELETE LATER`：`DashboardIndex.cshtml`、`DashboardPageModel.cs`
- build/sergen 因上述删除产生的 generated MVC/types change
- bounded route/integration/browser journey assertions and R7 1440/1920 evidence
- `operations/planning/research-experience-reboot.md` 的 R7 status-only update
- 本 work log、R7 per-Round review packet/artifact、Final Integrated review packet/artifact

### Context scope

适用 AGENTS、Independent Review scope standard、完整 product baseline/spec/prototypes、visual/acceptance/evidence contracts、canonical Plan/orchestration、R1–R6 work logs/reviews、P3 disposition、current source/tests。

### Environment / pre-existing dirty state

- `.pi/**`
- pre-existing `AGENTS.md` hunk
- `operations/orchestration/governance-maintenance-backlog.md`
- `operations/reviews/research-experience-reboot-r3-independent-review.md`
- `operations/reviews/research-experience-reboot-r4-screenshots/**`
- `operations/reviews/2026-08-30-research-ui-visual-audit/**`

以上不属于 R7 candidate；不得 reset、stash、clean、覆盖、误暂存或纳入候选。

## Protected / forbidden surfaces

- migrations、schema、seed、persistent domain、identity schema/config
- research evidence/review/publication/audit semantics
- Evidence/Conclusion/Report product UI
- history、domain services、evidence policy、admin backend、HIDE-only `Modules/Research/Diagram/PartDetail.cshtml`
- `.pi/**`、harness、runtime settings
- new product area、Graph/writing、prototype mock facts

## Definition of Ready / read-only audit

- [x] Owner R7 start decision and final-Round boundary received via Pi Fleet.
- [x] Mandatory governance/product/research/Plan/R1–R6 evidence read.
- [x] HEAD、full dirty status、no-staged baseline 与 protected hashes recorded.
- [x] Candidate/context/environment/protected surfaces classified.
- [x] `subagent({ action: "list", capabilities: true })` run; only executable/non-disabled agents will be used.
- [x] Root replacement proof established：`DashboardPage.Index` renders `CpoDiagramIndex.cshtml`; root browser/regression evidence exists from accepted R2–R6.
- [x] Current DELETE LATER references audited；deletion is not yet authorized.
- [x] `/Dashboard` redirect/secondary-route behavior implemented and regression-tested.
- [x] Generated MVC/types refreshed and exhaustive no-reference proof established.
- [x] DELETE LATER disposition finalized without deleting any HIDE-only path.

DELETE LATER disposition after implementation：

```text
/Dashboard -> 302 Location: / via DashboardPage.Dashboard()
R1 DELETE LATER files removed: DashboardIndex.cshtml, DashboardPageModel.cs
Generated MVC refreshed: Common.Dashboard view constant removed; PartDetail constant preserved
No source/test references remain for legacy dashboard view/model/action symbols
```

R7 implementation plan：

1. Keep root `/` on CPO Explorer and adapt `/Dashboard` to an explicit redirect to the canonical research route without touching admin maintenance routes.
2. Add route regression assertions for root, `/Dashboard`, research primary nav, and `/Administration/User` reachability.
3. Make `EvidenceWorkflowEndpoint` load authenticated `UserRow`, compare `ActorType` to `UserActorTypes.Human`, and pass the trusted result into the unchanged domain service.
4. Add endpoint tests proving a review-permitted machine principal is rejected without mutation and a human reviewer is accepted.
5. Regenerate MVC/server types through the normal build pipeline; run exhaustive `rg`/build/test proof. Delete only the two R1 DELETE LATER files if all references are gone. Preserve `PartDetail.cshtml`.
6. Add reproducible Explorer → Company Pool/Drawer/Detail → Workspace journey assertions and 1440/1920 screenshot sequence without introducing new product behavior.
7. Run focused/full validation, development fresh review/fix/re-review, then stop at the separately required formal per-Round + Final Integrated review gate if the known formal capability remains unavailable.

## Validation plan

- exact-head `npm run build`
- `dotnet build SerenityQuantResearch.slnx --no-restore`
- full `dotnet test SerenityQuantResearch.slnx --no-build`
- full UI unit/browser suites with protected screenshot output redirected where required
- canonical R7 integrated journey screenshots at 1440/1920
- machine reviewer rejection + human reviewer acceptance endpoint tests
- migration/schema/seed unchanged scans
- DELETE LATER replacement/no-reference cleanup map
- route/dead-link/exhaustive reference proof
- portability scan
- candidate manifest/hash、protected hash recheck、`git diff --check`、no-staged guard

## Running evidence

- 2026-08-30 R7 implementation updated `EvidenceWorkflowEndpoint` to load `UserRow` and pass `ActorType == human` into the existing review policy; no domain/service/schema changes were made.
- Added endpoint regression tests for machine reviewer rejection without mutation and human reviewer acceptance/audit fields.
- Adapted `/Dashboard` to redirect to `/`, added route/admin-maintenance assertions, regenerated MVC via normal `dotnet build`, and deleted only `DashboardIndex.cshtml` / `DashboardPageModel.cs`; `PartDetail.cshtml` remains present and generated.
- Added R7 integrated browser smoke for Explorer → selected Host ASIC switch-die → Company Pool → Quick Drawer → Company Detail → read-only Workspace at 1440 and 1920, with screenshots under `operations/reviews/research-experience-reboot-r7-screenshots/`.
- Validation run so far: focused endpoint/route tests passed (6/6), `npm run build` passed, `dotnet build SerenityQuantResearch.slnx --no-restore` passed, `dotnet test SerenityQuantResearch.slnx --no-build` passed (66/66), `npm run test:ui` passed with protected screenshot output redirected, and R7 screenshot generation passed to the canonical R7 screenshot directory.
- Development review fix-pass disposition: product review found no issues; security and cleanup reviews reported the same P2 endpoint-test gap where machine evidence finalization could pass with HTTP 500 instead of a typed 4xx. Applied the bounded fix in `EvidenceWorkflowEndpoint` to return `MachineEvidenceReviewDenied` as a `ValidationError` before calling the unchanged workflow service, and tightened endpoint coverage to assert `BadRequest` plus that code for both `reviewed` and `rejected` final states.
- Development review fix-pass validation: `dotnet test SerenityQuantResearch.slnx --filter EvidenceWorkflowEndpointPolicyTests` passed (3/3), `git diff --check` passed, no staged files, and migration/schema/seed/domain entity path scans stayed clean.
- Development re-review: product/security/cleanup fresh read-only re-reviews all returned OK / no blockers.
- Pre-commit validation exposed a reproducible R5 Company browser-smoke scroll-preservation failure when opening Quick Drawer in a short viewport. Applied a bounded UI stability fix to `CompanyUniversePage.ts` by extending the existing scroll restoration window; this preserves accepted R5 behavior and avoids changing schema/domain/evidence semantics. Focused R5 smoke then passed, and the full UI suite passed with `UI_SCREENSHOT_DIR` redirected to `/tmp/r7-ui-precommit2-screenshots`.

## Full Validation Evidence — primary session after fix-pass

```text
HEAD: 2c10022af1ca13a41acc362a9994062fe684a45e
PASS: git diff --check -- . ':(exclude).pi/**'
PASS: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build
PASS: dotnet build SerenityQuantResearch.slnx --no-restore (0 warnings, 0 errors)
PASS: dotnet test SerenityQuantResearch.slnx --no-build (67/67)
PASS: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && UI_SCREENSHOT_DIR=/tmp/serenity-r7-full-ui-screenshots npm run test:ui
      - 19/19 UI unit tests
      - R4 Explorer, R5 Company, R6 Workspace, and R7 integrated browser smokes passed
PASS: pre-commit rerun after R5 scroll-stability fix:
      - python3 scripts/check-document-governance.py --check
      - git diff --check -- . ':(exclude).pi/**'
      - npm --prefix src/SerenityQuantResearch/SerenityQuantResearch.Web run build
      - dotnet build SerenityQuantResearch.slnx --no-restore (0 warnings, 0 errors)
      - dotnet test SerenityQuantResearch.slnx --no-build (67/67)
      - UI_SCREENSHOT_DIR=/tmp/r7-ui-precommit2-screenshots npm --prefix src/SerenityQuantResearch/SerenityQuantResearch.Web run test:ui (19/19 unit; R4/R5/R6/R7 browser smokes passed)
PASS: python3 scripts/check-document-governance.py --check
PASS: git diff --exit-code -- src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations data/seeds
PASS: git diff --cached --name-only (no staged files)
```

R7 canonical screenshot evidence remains under `operations/reviews/research-experience-reboot-r7-screenshots/` and contains 10 PNGs：Explorer selected, Company Pool, Company Drawer, Company Detail, and Workspace Company at both 1440×980 and 1920×1080. The full UI regression run redirected R4/R5/R6/R7 screenshot output to `/tmp/serenity-r7-full-ui-screenshots` to avoid modifying protected pre-existing R4 screenshot files while preserving canonical R7 evidence from the focused R7 smoke.

## Cleanup / no-reference / protected proof

```text
Source/test no-reference proof:
rg -n --hidden --glob '!.git/**' --glob '!.pi/**' 'DashboardIndex|DashboardPageModel|LegacyDashboard|MVC\.Views\.Common\.Dashboard|DashboardPage\.LegacyDashboard' src tests
=> no matches

PartDetail protection proof:
src/SerenityQuantResearch/SerenityQuantResearch.Web/Imports/MVC/MVC.cs -> PartDetail constant remains
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoResearchPage.cs -> PartDetail route remains
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts -> render path remains
```

Protected hash recheck after candidate stabilization：

```text
status hash including environment: eebff04467794c9528bc489d3c55733bbdf1831d69a19f4d3dcba571e455fee2
pre-existing protected text diff hash: 7b50c0b36543ef0ccb615f2bdef2edd5e759f123f725f17e45a3aef199a462cd
current non-candidate R4 screenshot hash bundle: 5527a738b525afe88c84d7d151c8320f51c308838a4ae75d3c3d6f3fbb569a13
current non-candidate R6 screenshot hash bundle: 751a21e6e7e3e895ff5b9ae6ae1176cb1d9aaa8e9c94b04d6ea2b4328382da4e
non-candidate visual-audit residue hash bundle: 965442f31b7c0bc6ff1bf2e8c8d663ff1098f30920008affce9e1f29f95039ca
migration tracked-file hash bundle: 2cc7fdd58d1d8cbc032809a9d6e2238f3be5b08268958617071ffce5071bf9b0
seed tracked-file hash bundle: 17a236f1629ca4b2fed69a58db2e9079fcec7a014e64c59a47c3dcaab91ce116
```

Portability scan over live candidate files found no `/home/`、`/project/data_science`、`/tmp/pi-subagents`、`computer://`、provider key/secret strings.

## Final candidate manifest

Manifest algorithm:

```bash
{ git diff --name-only --diff-filter=ACMRTUXB; git diff --name-only --diff-filter=D; git ls-files --others --exclude-standard; } | sort -u \
  | grep -v '^\.pi/' \
  | grep -v '^AGENTS.md$' \
  | grep -v '^operations/orchestration/governance-maintenance-backlog.md$' \
  | grep -v '^operations/reviews/research-experience-reboot-r3-independent-review.md$' \
  | grep -v '^operations/reviews/research-experience-reboot-r4-screenshots/' \
  | grep -v '^operations/reviews/research-experience-reboot-r6-screenshots/' \
  | grep -v '^operations/reviews/2026-08-30-research-ui-visual-audit/'
```

```text
final R7 candidate path count: 24
final R7 manifest-file hash: 1690c828bd24bf2e3d16067345910c408ee3c07efc796c0b208d4fea0c846740
final R7 hashable-content path count: 21
final R7 hashable-content bundle hash: 258edb287096fa4b962f81f590c51266dd840a2880add3403555f7a8c3038ef3
```

Self-referential evidence rule: content bundle excludes `operations/work_logs/research-experience-reboot-r7.md`, `operations/reviews/research-experience-reboot-r7-independent-review.md`, and `operations/reviews/2026-08-30-research-experience-reboot-final-integrated-review.md`; tracked deletions are represented as `DELETED  <path>` lines.

Final 24-path manifest:

```text
operations/planning/research-experience-reboot.md
operations/reviews/2026-08-30-research-experience-reboot-final-integrated-review.md
operations/reviews/research-experience-reboot-r7-independent-review.md
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-company-detail-1440.png
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-company-detail-1920.png
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-company-drawer-1440.png
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-company-drawer-1920.png
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-company-pool-1440.png
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-company-pool-1920.png
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-explorer-selected-1440.png
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-explorer-selected-1920.png
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-workspace-company-1440.png
operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-workspace-company-1920.png
operations/work_logs/research-experience-reboot-r7.md
src/SerenityQuantResearch/SerenityQuantResearch.Web/Imports/MVC/MVC.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardIndex.cshtml
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPage.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPageModel.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniversePage.ts
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Endpoints/EvidenceWorkflowEndpoint.cs
src/SerenityQuantResearch/SerenityQuantResearch.Web/package.json
src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-r7-integrated-journey-browser-smoke.sh
tests/SerenityQuantResearch.Tests/EvidenceWorkflowEndpointPolicyTests.cs
tests/SerenityQuantResearch.Tests/OpenAccessIntegrationTests.cs
```

## Formal review readiness / blocker

Prepared formal review packets:

- Per-Round R7 packet/artifact：`operations/reviews/research-experience-reboot-r7-independent-review.md`
- Final Integrated packet/artifact：`operations/reviews/2026-08-30-research-experience-reboot-final-integrated-review.md`

State: `owner_accepted_commit_authorized`. Owner first selected the “formal harness restored” path, so Builder invoked `harness_run_independent_review` once for `reviewRole=per_round`, `roundId=R7`. The tool returned:

```text
harness_run_independent_review: not_applicable
Reason: Harness is in simple/passive mode. Formal Round, handoff, review, and widget capabilities require explicit Owner-approved formal activation.
```

No formal child was created and no formal P0/P1/P2 exist. This direct R7 invocation disproved restored formal capability in the current runtime; Builder did not proceed to a redundant Final Integrated helper call in the same capability state. Owner then explicitly selected option 2：modify/waive the R7 formal review gate with this limitation and enter Owner acceptance judgment. Owner subsequently accepted R7 with this visible limitation and authorized an acceptance commit without push.

## Formal review boundary

R7 originally required two distinct formal obligations：per-Round Independent Review and Final Integrated Independent Review. Development subagent reviewers are supplemental only. Current runtime returned `not_applicable/simple-passive` again when Owner selected the formal-harness-restored path. Owner then explicitly modified/waived the R7 formal review gate with limitation and allowed the candidate to enter Owner acceptance judgment. Owner accepted R7 with this limitation and authorized an acceptance commit without push. No silent waiver or substitution occurred; the limitation remains visible in the R7 and Final Integrated review artifacts.
