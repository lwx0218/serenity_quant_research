# Phase 1 P3 Independent Review

## Gate / Route

- Gate: fresh independent P3 review
- Route: `review-only`
- Date: 2026-08-25
- Reviewer stance: non-inherited; work-log claims were treated as claims only
- Write boundary: this review record is the only intentional repository change
- P4/P5/P6: not entered; P4 remains unstarted

## Scope

Reviewed the frozen P3 contract and the existing P2 cross-navigation change across:

- the complete required planning, P0/P1/P2 evidence, P3 claims, taxonomy, company, evidence, bootstrap, seed, summary, and README documents;
- `CompanyUniverseService`, exposure policy/endpoint, entity relationships, migrations, permissions, page controllers/views, company UI/state/CSS, P2 part service/UI, navigation, startup registration, generated ServerTypes and generated ESM/CSS;
- all five .NET test source files, both Node test files, and the complete Kestrel/Firefox browser runner;
- fresh SQLite, authenticated/anonymous HTTP behavior, actual Firefox rendering, policy attempts, exact seed identity sets, and prohibited-scope/portability scans.

No `.git` metadata exists in this repository. Therefore no independent baseline diff, tracked/untracked determination, or authoritative proof of when a file was introduced was possible; review used complete file inventory, source tracing, generated-output checks, temporary runtime databases, tests, and browser/HTTP evidence.

## Verification Evidence

### Required build and test commands

| Check | Result |
|---|---|
| `dotnet build SerenityQuantResearch.slnx --no-restore` | Passed; 0 warnings, 0 errors. MVC/ServerTypes and ESM generation completed; 34 frontend outputs checked, none changed. |
| `dotnet test SerenityQuantResearch.slnx --no-build` | Passed; 40/40 tests. Test implementations and assertions were inspected, not just the final line. |
| Web project: `npm run test:ui` | Passed; 10/10 Node tests and committed fresh SQLite/Kestrel/Firefox smoke. See H-01/H-02 for assertion/control gaps hidden by this success. |
| Web project: `npm run build` | Passed; 34 generated outputs checked, none changed. |
| Microsoft.TypeScript.MSBuild 6.0.3 compiler: `tsc.js --noEmit --project tsconfig.json` | Passed without diagnostics. |

An initial accidental `npm run test:ui` from repository root returned `ENOENT` because there is no root `package.json`; it was rerun from the required web project and passed.

### Source, data, and generated-contract tracing

- `CompanyUniverseService` reads explicit `Company`, `CompanyExposure`, `PhysicalPart`, `IndustryChainNode`, `CompanyExposureEvidence`, `Evidence`, `SourceDocument`, `Event`, and `ConclusionEvidence`/`ResearchConclusion` rows. Search is restricted to company identity fields. No SVG/JPEG/name/category/keyword relationship inference was found.
- The service returns identity, market, geography, universe layer, coverage priority, explicit role/relevance/confidence/state/scope, separated support/contradict/context evidence, audit metadata, coverage, and freshness fields. Generated TypeScript contracts match these C# response/request types.
- Exact seed/runtime counts on a fresh temporary database were 9 modules, 21 parts, 10 chain nodes, 20 companies, 1 exposure, and 1 evidence record.
- The exact set of all 20 frozen company IDs matched `data/seeds/cpo/cpo-research-seed.json`; every ID resolved through `CompanyUniverse/Retrieve` and its company page.
- All 14 server filter checks passed independently: part, chain node, role, exchange, geography, universe layer, priority, candidate/unmapped verification, unreviewed/none coverage, fresh/unknown freshness, and identity search.
- The seven detail tabs are exact and ordered correctly. Existing explicit records render through typed relationships; absent financial/Capex/event/conclusion/source data renders research-gap text rather than invented customer/order/supplier/product/finance claims.
- Part → company, company → part/chain, chain → company/part, fallback/grid/comparison → company URLs use stable IDs. Every currently materialized exposure target resolved through both service and page routes.
- Broadcom remained `candidate`; `EVD-2026-0001@v1` remained `draft` and `contextualizes` after rejected policy attempts.
- Existing P1 `EvidenceWorkflowService`/endpoint remains present, but no P4 evidence timeline, ingestion UI, P4 transition UI, source-capture workflow, or new evidence-review page was found. No P5 conclusion/report workflow was found; company tabs only read existing publication metadata/gaps.

### Fresh HTTP, migration, permission, and policy evidence

A separately started Kestrel instance used a new `/tmp` SQLite database and was cleaned up afterward.

- Anonymous `/Research/Companies`: `302` to login.
- Anonymous service call: rejected before business data access.
- Authenticated universe/detail/chain/part/CPO pages and company/part/chain services: resolved.
- A synthetic authenticated user with `Research:General` but no `Research:Review` could list companies but could not call exposure update; state remained `candidate`.
- Real candidate + draft/contextual-only evidence → `verified`: rejected without mutation.
- Existing P1 forbidden evidence `draft` → `reviewed` shortcut: rejected without mutation; evidence remained draft.
- Temporary valid updates to `rejected` and then `stale` remained visible through retrieval with `UpdateUserId` and `UpdateDate`, confirming audit visibility.
- Expected policy rejections returned HTTP 500 and logged endpoint failures rather than structured validation responses; see M-01.
- A synthetic Review-authorized account designated as a machine was treated as human by the endpoint. With an otherwise eligible human-reviewed Level A supporting fixture in the temporary database, it promoted the exposure to `verified`; see H-02. No repository seed was changed.

### Firefox and accessibility/runtime behavior

Firefox 140.10 ESR ran headlessly against fresh Kestrel/SQLite instances.

- The committed runner passed its P2 9-module/21-part flow and P3 exact 20-company, real-grid render, exchange filter, keyboard comparison, seven tabs, ArrowRight tab navigation, policy rejection, cross-navigation, and explicit `?view=table` fallback checks.
- An additional independent Firefox run tightened assertions and passed actual Ticker-header sorting (first fallback row became `cn.000988`) and exact P2 fallback focus restoration inside `#cpo-part-tree`.
- A separate tightened frozen-column assertion found zero frozen/pinned start headers. The page text said “前 3 列冻结,” but the real grid used SleekGrid's default `BasicLayout`; see H-01.
- Native labels/controls, roving tab `tabindex`, ARIA tab/panel relationships, visible `:focus-visible` rules, Space comparison, Arrow/Home/End tab logic, native links, and an always-rendered table path were source-verified. Explicit table mode passed.

### Boundary and portability scans

- No runtime CPO JPEG/image, image map, hotspot, SVG relationship parsing, or JPEG/name/category/keyword inference was found.
- No trading, K-line, quote/tape, brokerage/account, execution, portfolio, backtest, short-term price ranking, inferred customer/order/supplier/revenue-share/mass-production, P4 timeline/ingestion, or P5 publication UI was found in authored P3/P2 research surfaces.
- No current-host `/project/...`, `/home/...`, `computer:///...`, or workspace-upload path leak was found in authored/generated P3 source, tests, seed, or README. The plan contains only a prohibition against such runtime links.
- No runtime/test/data image asset was found. JPEG provenance/public reuse rights remain unresolved, but P3 does not use the JPEGs.

## Findings

### Critical

None.

### High

#### H-01 — The three identity columns are not actually frozen in real SleekGrid

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniversePage.ts:150-177`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh:170-176`
- **Evidence/problem:** The page marks three columns `frozen` and supplies `frozenColumns: 3`, but it does not select SleekGrid's `FrozenLayout`. Serenity SleekGrid 10.3.7 defaults to `BasicLayout`; real Firefox produced zero pinned/frozen start headers. The committed browser test calculates `leftHeaders` using an obsolete `.slick-pane-left` selector, never asserts it, and instead accepts self-authored status text containing “前 3 列冻结.”
- **Impact:** A frozen core P3 interaction is absent even though the UI and passing test claim it exists. Identity/selection columns scroll away in the high-density comparison grid.
- **Recommended fix:** Use Serenity 10.3.7's `FrozenLayout` through `layoutEngine`, retain the three intended start columns, and add a real-browser assertion for exactly three `.sg-start .slick-header-column` elements plus horizontal-scroll position/persistence. Do not accept status text as proof.

#### H-02 — The server does not derive or enforce human-reviewer identity

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Endpoints/CompanyUniverseEndpoint.cs:36-49`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Domain/ResearchWorkflowPolicy.cs:51-64`; `tests/SerenityQuantResearch.Tests/ResearchWorkflowPolicyTests.cs:19-35`
- **Evidence/problem:** Every principal with `Research:Review` is passed to the policy as `actorIsHumanReviewer: true`. The user/account model has no machine/service-account marker or trusted reviewer claim from which the server derives this fact. The policy's machine-denial branch is exercised only by direct unit calls. In a temporary runtime fixture, a Review-authorized account designated as a machine changed candidate state; with otherwise eligible human-reviewed Level A supporting evidence it received HTTP 200 and promoted the exposure to `verified`.
- **Impact:** “Machines cannot silently promote” is not an enforceable server property. It is only an external permission-provisioning convention, while audit records merely show a user ID and cannot prove the actor was an allowed human reviewer.
- **Recommended fix:** Add a server-trusted human-reviewer/account-type claim or equivalent controlled identity attribute, prohibit machine/service principals from `Research:Review` state changes, derive the policy argument exclusively from that server identity, and test a Review-capable machine principal over the real endpoint. Preserve the evidence workflow as read-only in P3; do not add P4 transitions.

### Medium

#### M-01 — Expected exposure-policy rejection is surfaced as an HTTP 500 endpoint failure

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Domain/ResearchWorkflowPolicy.cs:55-64`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Services/CompanyUniverseService.cs:284-289`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh:211-214`
- **Evidence/problem:** Policy denials throw `InvalidOperationException`. Fresh authenticated HTTP candidate/draft → verified correctly preserved state, but returned 500 and emitted a `fail: Serenity.Services.ServiceEndpoint` log. The browser test passes on any nonempty UI error and does not assert a stable status/error code.
- **Impact:** Normal invalid user actions are reported as internal server failures, pollute operational error logs, and provide no stable client contract distinguishing policy denial from an actual outage.
- **Recommended fix:** Translate P3 exposure-policy denials to a structured `ValidationError`/4xx response with stable codes, preserve rollback, and assert exact endpoint status/code, no mutation, and no unexpected server-failure log.

### Low

#### L-01 — Freshness uses one universal capture-age rule instead of the frozen type-dependent contract

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Services/CompanyUniverseService.cs:399-426`
- **Evidence/problem:** Every source is `fresh` through 180 days, `review_due` through 365, then `stale`. The evidence contract specifies 90 days for news/events/outlooks, 180 for product/industry material, report-period rules for quarterly/annual reports, and no automatic expiry for labelled historical financial facts.
- **Impact:** The current single product-page seed is not mislabelled, but future explicit records can be incorrectly filtered or presented as fresh/stale.
- **Recommended fix:** Keep P3 read-only, but derive freshness from an explicit source/evidence category and its contract threshold when available; otherwise return an explicit unknown/review-policy gap. Add boundary tests without implementing P4 ingestion or transitions.

## Unverified Items

- No physical desktop, screen reader/accessibility-tree audit, contrast/high-contrast/zoom assessment, reduced-motion emulation, or cross-browser run was performed. Firefox headless keyboard/pointer/render behavior passed except H-01.
- Actual SleekGrid constructor failure was not fault-injected in-browser. Source catch handling and explicit native table mode passed, and the native table remains present after normal initialization.
- No organically created reviewed supporting evidence exists in the seed, so positive verified promotion was tested only with a controlled temporary evidence fixture; the repository seed remained candidate/draft.
- JPEG legal provenance/public reuse rights remain unresolved.
- Without `.git` metadata, tracked-file cleanliness, authoritative phase attribution, and a pre-P3 diff remain unverified.

## Decision

**changes requested**

The explicit service relationships, exact company set, filters, sorting, bounded comparison, detail tabs/gaps, cross-navigation, fallback, candidate/draft rejection, audit visibility, generated contracts, and phase boundaries are substantially present. However, the frozen identity columns do not work in actual SleekGrid, and the human-only promotion guarantee is not enforced from server identity. These High findings block P3 acceptance.

## P3 Independently-Reviewed Status

- Independent review executed: **Yes**.
- P3 accepted as independently reviewed: **No — changes requested**.
- Required route: remain at the P3 gate for bounded P3-only remediation and fresh focused re-review.

## P4 Readiness

- P4 status: **unstarted**.
- P4 may start: **No**.
- Do not use P4 evidence workflows to remediate or conceal the P3 grid/identity-policy findings.

---

# Focused Re-review — 2026-08-25

## Supersession and Fresh Stance

This is the one permitted focused re-review after the bounded P3 remediation cycle. The complete original review above, including its **changes requested** decision, is preserved as review history. This section is non-inherited and supersedes **only the current P3 gate outcome**.

- Review time: 2026-08-25 06:29 UTC
- Route: `review-only`; P4/P5/P6 were not entered
- Stance: remediation claims, work-log summaries, existing tests, and the first review were treated as untrusted claims until source and runtime behavior were checked independently
- Focus: all H-01/H-02/M-01/L-01 findings plus the complete P3 gate
- Write boundary: only this review file was modified; pre-write SHA-256 comparison of 390 repository files (excluding `bin/`, `obj/`, and `node_modules/`) found no content change caused by the review commands
- Repository limitation: `.git` metadata is absent, so authoritative baseline diff, tracked/untracked state, commit attribution, and cleanliness cannot be established

## Original Finding Disposition

| Finding | Focused disposition | Independent basis |
|---|---|---|
| H-01 Frozen identity columns | **Resolved** | Authored and generated code select Serenity 10.3.7 `FrozenLayout`. Fresh actual Firefox found exactly three start headers. A separately authored, grid-scoped probe scrolled the main viewport to 600 px, observed the main header move by -600 px, and observed all three pinned header x positions remain unchanged. |
| H-02 Human-only exposure state changes | **Resolved** | `Users.ActorType` is persisted, migration-backed, constrained on admin save, and security-administered. The exposure endpoint reloads the actor from the database and accepts no actor boolean from the request/UI. Supporting evidence requires reviewed/supporting/Level A or B plus a persisted human `ReviewedBy`. A separately created authenticated Review-authorized machine principal was denied with exact code `MachineExposureStateChangeDenied` and no state mutation despite eligible human-reviewed Level A support. |
| M-01 Structured policy rejection | **Resolved for HTTP/error contract and rollback** | Both independently exercised policy denials returned HTTP 400 with exact stable codes and preserved state; no `InvalidOperationException`, HTTP 500, or unhandled exception occurred. Serenity still logs handled `ValidationError` responses at `fail` severity; that remaining observability concern is recorded as L-02 below. |
| L-01 Freshness | **Partially resolved; residual Low finding** | Missing/unknown category no longer receives a universal age threshold, and historical/90/180/365/450-day helper cases passed. However, materialized evidence is always passed `evidenceCategory: null`, report-period semantics are incomplete, and UI labels still imply one 180-day rule. See L-01R. |

## Independent Verification Evidence

### Source, migration, generated output, and assertion inspection

- **Frozen layout:** `CompanyUniversePage.ts:1-2,150-177` imports `FrozenLayout` and passes `layoutEngine: new FrozenLayout()` with three intended frozen columns. The generated ESM contains the constructor and three frozen flags; its source map uses relative sources and its embedded `CompanyUniversePage.ts` exactly matches the authored file.
- **Committed Firefox assertions:** `run-browser-smoke.sh:170-179` checks exact company IDs, real cells/headers, exactly three start headers, nonzero main viewport scroll, and fixed start-pane x position. It no longer relies on status text or `.slick-pane-left`. Its selectors for the start pane are not grid-scoped and it checks the pane rather than every pinned header, but there is only one grid on the page and the separate independent probe removed those possible false-positive paths by scoping to `#company-grid`, comparing all three header positions, and proving the main header moved.
- **Persisted identity:** `DefaultDB_20260825_1000_P3ResearchActorType.cs:5-11` adds non-null `Users.ActorType` with default `human`; `UserRow.cs:19-20` maps it; `UserSaveHandler.cs:71-72,92` constrains new/admin-saved values to `human` or `machine` and defaults creates to human. `UserRow` read/modify access remains `Administration:Security`.
- **Server derivation:** `CompanyUniverseEndpoint.cs:37-52` is `Research:Review` authorized, obtains the authenticated identifier, reloads `UserRow`, and derives humanity only from persisted `ActorType`. `CompanyExposureUpdateRequest` contains no human/machine/reviewer boolean. The client-side ActorType check only hides the editor; it is not trusted by the endpoint.
- **Evidence qualification:** `ResearchWorkflowPolicy.cs:51-67` requires `supports`, `reviewed`, persisted-human reviewer, and Level A/B. `CompanyUniverseService.cs:483-493` resolves `Evidence.ReviewedBy` back to `Users` and checks `ActorType == human`; missing users and machine users do not qualify.
- **Stable denials:** `ResearchWorkflowPolicy.cs:58-67` throws `ValidationError` with `MachineExposureStateChangeDenied` or `VerifiedExposureEvidenceRequired`. `run-browser-smoke.sh:218-219` parses the exact response code/status and checks candidate/draft persistence. The earlier UI-only assertion at lines 214-217 accepts any error text, but the immediately following exact service assertion prevents that path from producing a suite-wide false positive.
- **Endpoint tests:** `CompanyExposureEndpointPolicyTests.cs` uses fresh real application hosting, cookie/CSRF authentication, a persisted machine user with direct `Research:Review`, and eligible Level A supporting evidence reviewed by user 1. Its response-body checks use substring matching, but independent runtime parsing and the committed browser JSON assertion both checked the exact `Error.Code`.
- **Generated identity contracts:** generated `ScriptUserDefinition`, `UserRow`, `UserForm`, `UserColumns`, `Texts`, bundled administration ESM, company ESM, and source map contain the expected ActorType/FrozenLayout changes. `npm run build` reported all 34 outputs current and none changed.

### Required command gate

| Command | Fresh result |
|---|---|
| `dotnet build SerenityQuantResearch.slnx --no-restore` | Passed; 0 warnings, 0 errors; MVC/ServerTypes/frontend generation ran and 34 outputs were unchanged. |
| `dotnet test SerenityQuantResearch.slnx --no-build` | Passed; 51/51, 0 skipped/failed. All authored .NET test files and assertions were inspected. |
| Web `npm run test:ui` | Passed; 10/10 Node tests and fresh SQLite/Kestrel/actual Firefox smoke. Both Node test files and the complete browser runner were inspected. |
| Web `npm run build` | Passed; 34 outputs checked, none changed. |
| Microsoft.TypeScript.MSBuild 6.0.3 `tsc.js --noEmit --project tsconfig.json` | Passed with no diagnostics. |

Toolchain observed: .NET SDK 10.0.400, Node 24.19.0, npm 11.17.0, Firefox 140.10.0 ESR, Serenity 10.3.7.

### Separate fresh SQLite, HTTP, policy, and Firefox probes

A separate Kestrel process used a newly created temporary SQLite database and was removed afterward.

- Migration/startup produced 9 modules, 21 parts, 10 chain nodes, 20 companies, 1 exposure, and 1 evidence row. SQLite schema inspection confirmed `Users.ActorType` is non-null with default `human`; development admin was persisted as `human`.
- Anonymous `/Research/Companies` returned `302` to the login route. An anonymous service POST with a valid anonymous CSRF cookie returned non-success (`400`) and no research data.
- Authenticated universe, Broadcom detail, ASIC chain node, switch-die part, and CPO pages returned `200`; `CompanyUniverse/List`, `Retrieve`, and `RetrieveChainNode` returned `200`.
- The service company set exactly matched all 20 seed IDs, with 20 unique IDs. All 20 authenticated company page targets returned `200`. Every currently materialized part/chain/company cross-navigation target resolved.
- Before adding any positive fixture, the normal persisted-human admin attempted candidate → verified against only `EVD-2026-0001@v1` draft/contextual evidence. The endpoint returned `400` / `VerifiedExposureEvidenceRequired`; Broadcom remained candidate and the seed evidence remained draft/contextualizes.
- A temporary machine user was persisted with `ActorType=machine`, authenticated normally, and granted both `Research:General` and `Research:Review`. A temporary supporting, reviewed, Level A evidence row was linked to Broadcom and had `ReviewedBy=1`, whose persisted ActorType was human. The machine endpoint request returned `400` / `MachineExposureStateChangeDenied`; exposure state did not change.
- A separate authenticated `Research:General` user without `Research:Review` was denied the update and did not mutate state.
- Fresh actual Firefox independently observed 20 unique companies, exactly three `.sg-start .slick-header-column` headers, and a horizontally scrollable main viewport. After setting the main viewport to `scrollLeft=600`, pinned header x positions remained `[317.25, 375.25, 595.25]` while the main header moved by `-600` px.
- Final temporary-database inspection still showed Broadcom `candidate` and `EVD-2026-0001@v1` `draft/contextualizes`. No repository seed or application database was used for the fixtures.

### ValidationError logging distinction

The two expected HTTP 400 denials were serialized and handled correctly. Kestrel contained no `Unhandled exception` or `System.InvalidOperationException`. Serenity's `ServiceEndpoint` nevertheless emitted `fail: Serenity.Services.ServiceEndpoint[0]` entries and stack traces whose exception type was `Serenity.Services.ValidationError` for both expected denials. These are framework-logged handled validation failures, not HTTP 500/internal failures. The committed browser runner at `run-browser-smoke.sh:241-246` correctly rejects unhandled/`InvalidOperationException` paths but does not—and should not currently be read to—prove absence of fail-level framework log entries.

### Freshness probe

A separate temporary .NET probe directly exercised 17 cases against `CalculateFreshness`:

- absent category at 1 and 5,000 days → `unknown`;
- unknown explicit category → `unknown`;
- `historical_financial` at 5,000 days → `historical`;
- news/event/product-roadmap/management-outlook boundaries → 90 days;
- product-page/presentation/industry-material boundaries → 180 days;
- standard boundary → 365 days;
- current annual-report helper boundary → 450 days.

No P4 ingestion, review transition, timeline, or category-persistence surface was added by this review.

### Phase boundary, inference, asset, and portability checks

- No runtime JPEG/image asset, hotspot/image map, copied artwork, SVG-derived business inference, or company/part relationship inference was found. All current P3 relationships remain explicit database links.
- No P3 implementation of an evidence timeline/ingestion/review UI, conclusion/report publication UI, P5 workflow, trading, K-line, quote/tape, brokerage/account, execution, portfolio, backtest, or short-term price ranking was found.
- The pre-existing P1 `EvidenceWorkflowService`/endpoint and policy tests remain present; no new P4 UI or P4 transition workflow was introduced.
- No host `/project/...`, `/home/...`, `computer:///...`, or upload absolute path was found in authored/generated P3 source, tests, or seed. The plan's `computer:///...` occurrence is a prohibition, not a runtime link.
- No `.git` metadata exists; phase attribution and tracked-file cleanliness therefore remain unverified.

## Findings After Focused Re-review

### Critical

None.

### High

None.

### Medium

None.

### Low

#### L-01R — Freshness remediation is safe for current data but does not fully implement the frozen type/period contract

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Services/CompanyUniverseService.cs:418,423-439`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniverseState.ts:37-40`
- **Evidence/problem:** The runtime always invokes freshness with `evidenceCategory: null`, because the current source/evidence schema has no persisted category, so every materialized record safely becomes `unknown`. The helper correctly handles historical, 90-day, 180-day, and standard cases, but quarterly/half-year “next report” behavior is absent and `annual_report` is reduced to capture-age 450 days rather than “next annual report, maximum 450 days.” UI text still labels every `fresh` value as “180 days” and describes `unknown` only as missing time data even when capture time exists but category/policy is absent.
- **Impact:** The current seed is not falsely classified, so this does not block P3. Once explicit categories are authorized, report-period evidence or 90/365/450-day evidence could be described inaccurately.
- **Fix:** Keep P3 read-only and category-neutral in presentation. Change labels to avoid a universal 180-day claim and identify missing category/policy as a reason for `unknown`. When typed category/report-period metadata is authorized, pass it into the calculation and use next-report publication semantics; until then return `unknown` for unsupported report categories rather than approximating them.

#### L-02 — Expected policy denials remain logged at failure severity

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Domain/ResearchWorkflowPolicy.cs:61-67`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh:241-246`
- **Evidence/problem:** Correctly handled `ValidationError` denials return stable HTTP 400 responses, but Serenity's endpoint logger emits `fail: Serenity.Services.ServiceEndpoint` plus a stack trace for each. The browser runner excludes unhandled and `InvalidOperationException` failures but does not expose this expected fail-level noise.
- **Impact:** There is no client failure or rollback defect, but operations may misread expected policy activity as an internal incident and alerting may be noisy.
- **Fix:** Preserve stable `ValidationError`/400 behavior. If supported by the Serenity logging configuration, classify known policy-validation codes below failure severity or filter/route those specific handled entries while retaining metrics/audit counts and all genuine unhandled failures. Add an observability assertion that distinguishes handled policy denials from HTTP 500/internal exceptions rather than asserting a completely clean log.

## Unverified Items

- No physical-desktop visual inspection, screen-reader/accessibility-tree audit, contrast/high-contrast/zoom assessment, reduced-motion emulation, or non-Firefox browser run was performed.
- No fault injection forced the SleekGrid constructor itself to fail; explicit table mode and source fallback handling passed.
- Admin UI editing of ActorType was source/generated-contract verified but not manually exercised through the browser. Endpoint security was exercised with directly persisted, authenticated principals.
- No persisted freshness category exists, so category-specific behavior beyond the direct helper probe cannot be exercised through the current P3 service/UI; quarterly/half-year and next-report timing remain unimplemented as noted in L-01R.
- Positive human promotion used only a temporary eligible fixture as a precondition to machine denial; the repository intentionally has no organically reviewed supporting evidence and no seed promotion was performed.
- Physical desktop, cross-browser, JPEG provenance/public reuse rights, and future P4/P5 behavior remain outside this focused review.
- Without `.git` metadata, authoritative diff/cleanliness, tracked/untracked state, and commit/phase attribution remain unverified.

## Focused Decision

**approved with minor findings**

H-01 and H-02 are independently resolved. M-01's HTTP 400/stable-code/rollback contract is independently resolved; its remaining framework logging behavior is operational noise rather than an unhandled failure. L-01 is safe for current absent-category data but retains the bounded Low issues above. No Critical, High, or Medium finding remains to block the P3 gate.

## Current P3 Independently-Reviewed Status

- Focused re-review executed: **Yes — the one allowed cycle is complete**.
- Current P3 gate outcome: **accepted as independently reviewed with minor findings**.
- Historical outcome: the original **changes requested** decision above remains intact as review history.

## Current P4 Readiness

- P4 readiness: **Yes — P3 no longer blocks a separately authorized P4 round**.
- P4 status in this review: **unstarted**.
- P4/P5/P6 work performed: **None**.
- The Low freshness/observability items should be tracked without retroactively expanding this completed P3 re-review; this review does not start P4.
