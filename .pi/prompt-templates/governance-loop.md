---
description: Route an existing-baseline task through the minimal governance loop
argument-hint: "<bounded task>"
---

# Governance Loop

Use this template for a later task in a project with an approved baseline. Greenfield/no-baseline work must use `/project-kickoff` and remain planning-only until Plan confirmation.

Task:

```text
$ARGUMENTS
```

## Gate

- Project: infer from current repository/intake
- Goal:
- Source of truth:
- Entry points:
- Constraints:
- Outputs:
- Candidate scope: actual task/Round delivery submitted for acceptance; only this receives P0/P1/P2
- Context scope: read-only contracts, Plan/spec, source, tests, baseline, and evidence needed for judgment
- Environment / dirty-worktree scope: changed/untracked, pre-existing local files, tooling dirs, and residue for transparency/immutability only
- Governance-layer status: `.pi/` / harness is a product non-goal unless separately authorized by the Owner
- Existing approved baseline:
- Route: `direct-execute` | `plan` | `review-only` | `needs-extension`

Use repository evidence before asking questions. If the route remains unclear, use the applicable grilling skill with the shared bounded interview contract: at most 3 rounds, 3–5 blocking decisions per round, recommended defaults, and explicit Owner opt-in before `deep-discovery`.

## Direct Execute

For a clear bounded task:

- Execute:
- Verify:
- Result:
- Next step:

Do not manufacture durable evidence for a trivial task.

## Plan

When contract, portability, cross-file risk, handoff, or validation needs justify a Plan:

- Scope:
- Files expected to change:
- Validation:
- Assumptions/backlog:
- Human control gate:

If the work is additionally complex, cross-session, high-risk, or requires formal acceptance, explicitly route to `fixed-round-plan`. Then `Round` is the only acceptance-bearing unit and every Round must declare its Round ID, one primary implementation session name, independently reviewable delivery boundary, non-goals, dependencies/Definition of Ready, expected change surfaces, exact validation strategy, Independent Review mode and role-specific artifact paths, acceptance evidence, next gate, blockers/assumptions, and blocked/rebaseline conditions in a matching `## R<n> — ...` owning section. Plan metadata uniquely records approval, Git baseline, and accepted-effective Round IDs. Continuations remain in the same Round; do not create Phase acceptance or letter-suffixed Rounds.

## Review Only

- Candidate/contract:
- Review mode:
- Findings/decision:
- No candidate edits by reviewer:

## Needs Extension

- Missing capability:
- Why the starter boundary is reached:
- Suggested next action:

## Fixed-Round Closeout

When and only when `fixed-round-plan` is active:

- use `harness_update_round_progress` to show truthful control stages (Scope/DoR, Implementation, Verification, Review, Fix/Verify/Re-review, Owner/Commit Gate) without project writes or fabricated percentages
- after automated verification, the current Builder automatically calls `harness_run_independent_review` for this Round with explicit `deliveryClass`, `candidatePaths`, and optional `contextPaths`/`environmentPaths`; require distinct PID, non-interactive `--no-session`, strict `read,grep,find,ls`, captured provider/model/exit/stdout/stderr, phase history, attempt run ID, and unchanged pre/post candidate hash
- P0/P1 remains in this Round through automatic Fix/Verify/Re-review; record every P2 disposition
- after all planned delivery is complete, run a separate Final Integrated Independent Review before the last Round's pre-commit gate
- Review/Fix/integrated review do not create a hidden Round
- the child never writes candidate or durable artifact; the Builder records the tool result in the declared review path
- all Review attempts remain evidence; same-hash blocking/pass inconsistency is `review_inconsistency` and blocks last-pass-wins
- capability/auth/read-only isolation failure is `automated_review_capability_blocked`; stop automatic Harness repair/reload loops and report candidate/gate impact to the Owner
- the Owner chooses a recorded limitation, approved distinct-human fallback, separate governance maintenance, review mode/Plan adjustment, or pause; if Independent Review remains required, limitation is not a pass

Entering a review bundle does not make a path candidate. Git changed/untracked paths do not automatically enter the product task/Round acceptance scope. `.pi/`, harness-flow, extensions, skills, prompts, settings, and handoff/review tooling are governance-layer surfaces; record problems as `governance maintenance issue` / `review limitation` rather than editing them from a product task. Default Independent Review does not require OS-level sandbox / bwrap.

## Closeout

- Files changed:
- Checks/results:
- Evidence written only if required:
- Portability notes:
- Next bounded step:

For the `direct-execute` simple path, keep this lightweight and do not manufacture fixed Rounds or formal Review.
