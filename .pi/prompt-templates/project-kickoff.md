---
description: Establish an approved baseline Plan before greenfield implementation
argument-hint: "<project request>"
---

# Project Kickoff

Use this kickoff for a greenfield project or a project without an approved baseline Plan.

Project request:

```text
$ARGUMENTS
```

If the repository already has an approved, stable baseline and the request is a later bounded task, say so and route through the normal `Gate -> Route` simple path instead of forcing this kickoff.

## Orchestration-Only Boundary

Before the Owner confirms the Plan, you may:

- read repository contracts and existing evidence
- infer facts from the repository instead of asking the user
- classify the request and select relevant discovery lenses
- discuss scope, domain, constraints, acceptance, assumptions, and risks
- present a Plan Preview in chat

Before confirmation, you must not:

- modify business code or configuration
- create or update a formal Plan, `CONTEXT.md`, ADR, work log, review, or other project artifact
- install dependencies or run destructive/system-level actions
- begin implementation or claim development progress

Files created by bootstrap before this conversation are pre-existing scaffold, not writes authorized by this kickoff.

## Bounded Decision Interview

- maximum 3 discovery rounds by default
- each round groups 3–5 related blocking decisions
- target maximum 12–15 blocking decisions total
- every decision includes a recommended default and why it is safe enough
- the Owner may answer `accept recommended defaults`
- infer repository facts rather than asking about them
- ask only when the answer changes scope/acceptance, architecture/data ownership, or a hard-to-reverse/high-risk choice
- record non-blocking uncertainty as an assumption or backlog item
- if blockers remain when the budget is exhausted, ask whether the Owner opts into `deep-discovery`; do not continue automatically

End every discovery response with:

- Resolved
- Assumed
- Blocking
- Deferred
- Question budget remaining

Optional `domain-modeling` is selected only when terminology, actors/entities, state transitions, ownership, or bounded contexts are materially ambiguous. Before Plan approval it stays in no-write discovery mode and keeps temporary glossary/scenarios in chat.

## Terminal States

Every greenfield/no-baseline orchestration turn must end in exactly one state:

1. `blocking-decisions`
   - present only bounded decisions and the discovery budget state
2. `ready-for-approval`
   - use only when all blocking scope, architecture, and acceptance decisions are resolved, non-blocking uncertainty is assumed/deferred, and validation/control gates are clear
   - present one complete Plan Preview in chat containing:
     - Goal and source of truth
     - in-scope / out-of-scope
     - architecture and data/domain ownership decisions
     - files or surfaces expected to change
     - `candidate scope`, `context scope`, and `environment / dirty-worktree scope`; bundle membership and Git changed/untracked paths do not define candidate scope
     - governance-layer status: `.pi/` / harness is a product non-goal unless the Owner explicitly approves a separate governance maintenance task
     - acceptance criteria and exact validation strategy
     - assumptions, risks, and backlog
     - delivery route/rounds and review mode when justified
     - for each fixed Round: Round ID, one primary implementation session name, independently reviewable delivery boundary, non-goals, dependencies/Definition of Ready, expected change surfaces, exact validation strategy, distinct per-Round and final-integrated Review artifact paths when applicable, Independent Review mode, acceptance evidence, exact next gate, blockers/assumptions, and blocked/rebaseline conditions; keep these fields in the owning Round section for runtime grounding
     - durable evidence paths
     - next human control gate
   - end with exactly:

```text
以上 Plan 是否可行？是否还有需要继续确认或修改的地方？

- 如需修改：直接说明修改点
- 如无其他问题：回复“确认计划”
- 确认后我将持久化 Plan，并生成下一开发 session 的名称和交接内容
```

3. `approved-and-persisted`
   - use only after explicit Owner Plan confirmation and approved evidence persistence
   - propose the declared next session name and a durable-source-based copyable handoff

Accepting recommended discovery defaults is not durable Plan approval. After the complete Preview, call `harness_request_plan_approval`; only its `approved` result grants persistence authority. `changes_requested` returns to Preview revision and `cancelled` authorizes no write. If `harness-flow` is unavailable, require `确认计划` or an equally explicit confirmation as the manual fallback.

## After Confirmation Only

After explicit confirmation, you may:

- create/update the project-local Plan and intake; the Plan must record explicit `Plan approval: approved` metadata for durable handoff validation
- record approved domain language or sparse ADRs when justified
- generate a New Session Handoff Prompt

Do not start business implementation in `00-orchestration`. For a fixed Round, read its declared primary implementation session name and call `harness_offer_session_handoff` only after approved evidence exists. It validates the Plan/Round/session, displays the proposed session/target/summary, asks one Owner confirmation, then creates a parent-linked session, names it, and submits the durable-source prompt once.

On cancellation/capability failure—or when the extension is unavailable—generate `/session-handoff <declared-session-name>` and give the human:

```text
/session
/new
/name <declared-session-name>
```

For non-fixed work use `/name build-<task-slug>`. The copyable manual handoff remains supported. Do not claim that local `harness-flow` is a public package, and never use mutable chat history as durable authority.

`/new` is not Independent Review. A fixed-round Plan requires every Round's current Builder to automatically call `harness_run_independent_review` after verification. It must establish a distinct non-interactive/no-session/strict read-only child and Git immutability evidence, or mark `automated_review_capability_blocked` and report candidate/gate impact to the Owner. The Owner chooses a review limitation, approved distinct `human_review`, separate governance maintenance, review mode/Plan adjustment, or pause; if Independent Review remains required, a limitation is not a pass.

Independent Review grades only `candidate scope`. `context scope` is read-only judgment input; `environment / dirty-worktree scope` is transparency/immutability evidence. 进入 review bundle 不等于进入 candidate scope。Git changed/untracked paths 不自动进入当前产品 Round / task 的验收范围。项目开发过程中，`.pi/` / harness 治理层问题不得被擅自修改；do not automatically repair Harness or repeat reload/re-review to fix tooling. Default Review does not require OS-level sandbox / bwrap.

P0/P1 candidate findings stay in the same Round through Fix/Verify/Re-review, and the last Round also requires a separate `final_integrated` Review before its pre-commit gate.
