# Research Experience Reboot — Final Integrated Independent Review

Round: Final Integrated after R7
Review role: final_integrated
Decision: owner_modified_review_gate_with_limitation
Unresolved P0: 0 (not formally assessed; formal child did not run)
Unresolved P1: 0 (not formally assessed; formal child did not run)
Unresolved P2: 0 (not formally assessed; formal child did not run)

## Metadata

- Project: serenity_quant_research
- Task: R7 final integrated independent review readiness
- Timestamp (UTC): 2026-08-30T13:43:32Z
- Owner: project owner
- Route: review-only
- Source of truth: operations/planning/research-experience-reboot.md

## Status

- Scope：Final integrated review for Research Experience Reboot through R7.
- Required mode：formal `harness_run_independent_review` with `reviewRole = final_integrated` after R7 candidate stabilization.
- Current decision：`owner_modified_review_gate_with_limitation`；no formal final-integrated child has run and formal P0/P1/P2 are not assessed.
- Reason：No independent governance-maintenance evidence shows current formal harness runtime capability has recovered from the R6 `not_applicable/simple-passive` blocker. After R7 candidate stabilization, Owner selected the “formal harness restored” path; the per-Round R7 helper invocation again returned `not_applicable/simple-passive`. Builder therefore did not make a redundant Final Integrated helper invocation in the same blocked capability state. Owner then explicitly selected option 2：modify/waive the R7 formal review gate with this limitation and enter Owner acceptance judgment. Development subagent reviews remain supplemental and do not become formal review.
- Next gate：R7 acceptance commit `730eeee50c9e07997828f2bb7e6017a955092caa` completed；post-commit verification passed；not pushed；R7 and current Research Experience Reboot boundary are accepted-effective; Active Round none.

## Integrated Candidate Packet

### Candidate delivery boundary

Research Experience Reboot current accepted/in-progress delivery boundary:

```text
CPO Explorer
→ Component / Material / Technology
→ Company Pool
→ Quick Drawer
→ Full Company Detail
→ Read-only Research Workspace
```

R7 candidate closes this boundary by proving the end-to-end journey, enforcing human-only evidence review endpoint behavior, and removing only proven-dead demo Dashboard frontend.

### R1–R6 status context

- R1：accepted-effective P0–P3 code/domain disposition audit.
- R2：accepted-effective research shell/root/nav/admin separation.
- R3：accepted-effective CPO Explorer vertical slice.
- R4：accepted-effective full CPO Explorer with documented R4-only review limitation.
- R5：accepted-effective Company Pool / Quick Drawer / Full Detail.
- R6：accepted-effective read-only linked Research Workspace with documented R6-only formal review limitation.
- R7：accepted-effective after Owner-modified formal review limitation, acceptance commit `730eeee50c9e07997828f2bb7e6017a955092caa`, and successful post-commit verification without push.

### R7 candidate paths

Use `operations/reviews/research-experience-reboot-r7-independent-review.md` and `operations/work_logs/research-experience-reboot-r7.md` as the R7 detailed packet. Key paths:

- `operations/planning/research-experience-reboot.md`
- `operations/work_logs/research-experience-reboot-r7.md`
- `operations/reviews/research-experience-reboot-r7-independent-review.md`
- `operations/reviews/2026-08-30-research-experience-reboot-final-integrated-review.md`
- `operations/reviews/research-experience-reboot-r7-screenshots/*.png`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPage.cs`
- tracked deletions: `DashboardIndex.cshtml`, `DashboardPageModel.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Endpoints/EvidenceWorkflowEndpoint.cs`
- `tests/SerenityQuantResearch.Tests/EvidenceWorkflowEndpointPolicyTests.cs`
- `tests/SerenityQuantResearch.Tests/OpenAccessIntegrationTests.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-r7-integrated-journey-browser-smoke.sh`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/package.json`
- generated MVC update: `src/SerenityQuantResearch/SerenityQuantResearch.Web/Imports/MVC/MVC.cs`

### Context packet

- root/scoped `AGENTS.md`
- `operations/orchestration/independent-review-and-round-scope-standard.md`
- `docs/product/README.md`
- `docs/product/experience-map.md`
- `docs/product/cpo-explorer-spec.md`
- `docs/product/company-research-spec.md`
- `docs/product/research-workspace-spec.md`
- `docs/product/visual-language.md`
- `docs/product/acceptance-contract.md`
- `docs/research-baseline/evidence-contract.md`
- `operations/orchestration/research-experience-reboot.md`
- `operations/reviews/reboot-p3-code-disposition.md`
- R1–R6 work logs and review artifacts
- current source/tests for Explorer, Company, Workspace, endpoint, route, and browser smoke behavior

### Environment / excluded dirty state

Final integrated review must treat these as environment/pre-existing and not current product candidate:

- `.pi/**`
- pre-existing `AGENTS.md` hunk
- `operations/orchestration/governance-maintenance-backlog.md`
- `operations/reviews/research-experience-reboot-r3-independent-review.md`
- `operations/reviews/research-experience-reboot-r4-screenshots/**`
- `operations/reviews/2026-08-30-research-ui-visual-audit/**`

## Validation Evidence

Current primary-session validation after the R7 fix/re-review loop:

```text
PASS: git diff --check -- . ':(exclude).pi/**'
PASS: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build
PASS: dotnet build SerenityQuantResearch.slnx --no-restore (0 warnings, 0 errors)
PASS: dotnet test SerenityQuantResearch.slnx --no-build (67/67)
PASS: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && UI_SCREENSHOT_DIR=/tmp/serenity-r7-full-ui-screenshots npm run test:ui
PASS: python3 scripts/check-document-governance.py --check
PASS: git diff --exit-code -- src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations data/seeds
PASS: git diff --cached --name-only (no staged files)
```

R7 canonical product-visible screenshots:

- `operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-explorer-selected-1440.png`
- `operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-company-pool-1440.png`
- `operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-company-drawer-1440.png`
- `operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-company-detail-1440.png`
- `operations/reviews/research-experience-reboot-r7-screenshots/r7-journey-workspace-company-1440.png`
- same five states at 1920px.

## Required Final Integrated Reviewer Questions

A valid final integrated reviewer must answer with P0/P1/P2 findings and a decision:

1. Does the integrated reboot journey satisfy the approved product objective and IA without reverting to admin/dashboard/grid-first framing?
2. Does primary navigation remain exactly CPO Explorer / Company Pool / Research Workspace, with admin routes only secondary?
3. Does Explorer → Company Pool → Quick Drawer → Full Detail → read-only Workspace preserve source research context and object identity?
4. Does Workspace remain read-only + linked-object-first, with no Graph/New Note/ResearchNote/OpenQuestion/Backlink/editor persistence?
5. Does R7 avoid Evidence/Conclusion/Report UI and preserve evidence/review/publication/audit semantics?
6. Does EvidenceWorkflowEndpoint enforce human reviewer identity via persisted `UserRow.ActorType`, rejecting machine principals even with permission?
7. Was legacy cleanup limited to proven-dead R1 DELETE LATER Dashboard view/model, with `PartDetail.cshtml`, admin backend, domain services, migrations, seed, and history preserved?
8. Are validation, screenshot evidence, no-reference proof, schema/seed scans, portability checks, protected hashes, candidate manifest, and no-staged guard sufficient for acceptance judgment?

## Owner Gate

Owner explicitly modified/waived the R7 formal review gate with limitation after the per-Round helper still returned `not_applicable/simple-passive`. This artifact records that no formal Final Integrated review child ran and formal P0/P1/P2 are not assessed. Owner accepted R7 with this limitation；acceptance commit `730eeee50c9e07997828f2bb7e6017a955092caa` and post-commit verification completed without push. R7 and the current Research Experience Reboot boundary are accepted-effective；Active Round none.
