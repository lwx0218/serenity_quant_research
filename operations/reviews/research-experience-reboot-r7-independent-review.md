# Research Experience Reboot — R7 独立评审

Round: R7
Review role: per_round
Decision: owner_modified_review_gate_with_limitation
Unresolved P0: 0 (not formally assessed; formal child did not run)
Unresolved P1: 0 (not formally assessed; formal child did not run)
Unresolved P2: 0 (not formally assessed; formal child did not run)

## Metadata

- Project: serenity_quant_research
- Document type: other
- Status: approved
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: operations/planning/research-experience-reboot.md

## Status

- Candidate：R7 integrated journey, Evidence endpoint actor enforcement, and proven DELETE LATER cleanup.
- Required mode：formal `harness_run_independent_review` per canonical Plan and Owner R7 start decision.
- Current decision：`owner_modified_review_gate_with_limitation`；formal review child did not run, formal P0/P1/P2 are not assessed, and development subagent reviews are not being used as substitutes.
- Reason：R6 twice observed current Pi/harness runtime returning `not_applicable/simple-passive` for formal review helpers. After R7 candidate stabilization, Owner selected the option asserting formal harness was restored; Builder invoked the formal per-Round helper once, but the current runtime again returned `not_applicable/simple-passive`. Owner then explicitly selected option 2：modify/waive the R7 formal review gate with this limitation and enter Owner acceptance judgment. This does not create a formal review pass and does not itself authorize commit/push.
- Next gate：R7 acceptance commit `730eeee50c9e07997828f2bb7e6017a955092caa` completed；post-commit verification passed；not pushed；R7 is accepted-effective and Active Round is none.

## Candidate Reviewed / Review Packet

Formal review did not execute. The prepared read-only packet for a valid per-Round reviewer is:

### Candidate paths

- `operations/planning/research-experience-reboot.md`（R7 active status only）
- `operations/work_logs/research-experience-reboot-r7.md`
- `operations/reviews/research-experience-reboot-r7-independent-review.md`
- `operations/reviews/research-experience-reboot-r7-screenshots/*.png`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Imports/MVC/MVC.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPage.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardIndex.cshtml`（tracked deletion）
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPageModel.cs`（tracked deletion）
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Endpoints/EvidenceWorkflowEndpoint.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/package.json`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-r7-integrated-journey-browser-smoke.sh`
- `tests/SerenityQuantResearch.Tests/EvidenceWorkflowEndpointPolicyTests.cs`
- `tests/SerenityQuantResearch.Tests/OpenAccessIntegrationTests.cs`

### Candidate summary

- `/` remains the canonical research entry and renders CPO Explorer.
- `/Dashboard` no longer renders demo dashboard content; it redirects to `/` while admin maintenance routes remain available.
- R1 `DELETE LATER` demo files `DashboardIndex.cshtml` and `DashboardPageModel.cs` were removed only after redirect replacement, MVC regeneration, source/test no-reference scans, build, and route assertions. `PartDetail.cshtml` remains present and referenced.
- `EvidenceWorkflowEndpoint` now loads authenticated `UserRow`, derives `actorIsHumanReviewer` from `UserActorTypes.Human`, returns typed `MachineEvidenceReviewDenied` for non-human finalization to `reviewed` / `rejected`, and passes the trusted actor-type boolean into the unchanged workflow service.
- Endpoint tests prove a machine principal with `Research:Review` is rejected without evidence/audit mutation, and a human reviewer can finalize evidence with review audit fields.
- R7 browser smoke proves Explorer → selected Host ASIC switch-die → Company Pool → Quick Drawer → Company Detail → read-only Workspace at 1440 and 1920, with source context preserved and no Graph/writing/Evidence/Conclusion/Report UI.

### Context paths

- `AGENTS.md`
- `operations/orchestration/independent-review-and-round-scope-standard.md`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md`
- `docs/product/README.md`
- `docs/product/experience-map.md`
- `docs/product/cpo-explorer-spec.md`
- `docs/product/company-research-spec.md`
- `docs/product/research-workspace-spec.md`
- `docs/product/prototypes/cpo-explorer-v0.4.html`
- `docs/product/prototypes/company-pool-v0.3.html`
- `docs/product/prototypes/research-workspace-v0.1.html`
- `docs/product/visual-language.md`
- `docs/product/acceptance-contract.md`
- `docs/research-baseline/evidence-contract.md`
- `operations/planning/research-experience-reboot.md`
- `operations/orchestration/research-experience-reboot.md`
- `operations/reviews/reboot-p3-code-disposition.md`
- R1–R6 accepted work logs and review artifacts
- Current source/tests needed to judge route, endpoint, and journey behavior

### Environment / excluded dirty state

- `.pi/**`
- pre-existing `AGENTS.md` hunk
- `operations/orchestration/governance-maintenance-backlog.md`
- `operations/reviews/research-experience-reboot-r3-independent-review.md`
- `operations/reviews/research-experience-reboot-r4-screenshots/**`
- `operations/reviews/2026-08-30-research-ui-visual-audit/**`

These paths remain excluded from the R7 product candidate and were not reset, stashed, cleaned, staged, or modified by the R7 fix pass.

## Formal Invocation Evidence

Builder invoked `harness_run_independent_review` for the per-Round R7 review after Owner selected “已恢复 formal harness”. Invocation parameters used `reviewRole=per_round`, `roundId=R7`, `planPath=operations/planning/research-experience-reboot.md`, `deliveryClass=product`, R7 candidate/context/environment paths, and `timeoutSeconds=1200`.

Tool result:

```text
harness_run_independent_review: not_applicable
Reason: Harness is in simple/passive mode. Formal Round, handoff, review, and widget capabilities require explicit Owner-approved formal activation.
```

No formal reviewer child was created; no valid formal P0/P1/P2 findings exist. This is a formal review capability/gate blocker, not a product candidate failure. Because this direct R7 invocation disproved restored capability, Builder did not proceed to a redundant Final Integrated helper call in the same capability state.

## Validation Evidence

Primary session validation after the development review fix pass:

```text
PASS: git diff --check -- . ':(exclude).pi/**'
PASS: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build
PASS: dotnet build SerenityQuantResearch.slnx --no-restore (0 warnings, 0 errors)
PASS: dotnet test SerenityQuantResearch.slnx --no-build (67/67)
PASS: cd src/SerenityQuantResearch/SerenityQuantResearch.Web && UI_SCREENSHOT_DIR=/tmp/serenity-r7-full-ui-screenshots npm run test:ui (19 UI unit tests; R4/R5/R6/R7 browser smokes)
PASS: python3 scripts/check-document-governance.py --check
PASS: git diff --exit-code -- src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations data/seeds
PASS: git diff --cached --name-only (no staged files)
```

Focused/development validation also passed:

```text
PASS: dotnet test SerenityQuantResearch.slnx --filter EvidenceWorkflowEndpointPolicyTests (3/3)
PASS: focused endpoint/route tests before fix-pass (6/6)
PASS: R7 canonical screenshot generation via npm run test:ui:browser:r7
```

## Development Review Evidence (Supplemental Only)

A single `pi-subagents` workflow `6d1d6774-c207-4014-b925-d408cd73d939` ran read-only scouts, one writer, three fresh development reviewers, the same writer fix pass, and three fresh re-reviews.

- Product reviewer：OK with notes / no findings.
- Security reviewer：P2 — machine denial could surface as HTTP 500; fixed with typed `ValidationError("MachineEvidenceReviewDenied")`.
- Cleanup reviewer：same P2; test tightened to `BadRequest` + stable code.
- Product/security/cleanup re-reviews：OK / no blockers.

This evidence helps development quality but does **not** satisfy the formal R7 Independent Review obligation.

## Formal Blocker And Owner Choices

Per `operations/orchestration/independent-review-and-round-scope-standard.md`, automated review capability failure does not equal candidate failure and does not waive the Independent Review obligation.

Owner selected option 2 after the failed R7 helper invocation: explicitly modify/waive the R7 formal review gate with limitation and enter Owner acceptance judgment.

Decision effect:

- no formal per-Round child ran;
- formal P0/P1/P2 are not assessed;
- development subagent review/re-review remains supplemental, not a formal substitute;
- Owner acceptance judgment occurred with this visible limitation;
- Owner accepted R7 with this limitation；acceptance commit `730eeee50c9e07997828f2bb7e6017a955092caa` and post-commit verification completed without push；R7 is accepted-effective.
