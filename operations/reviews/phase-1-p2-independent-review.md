# Phase 1 P2 Independent Review

## Gate / Route

- Gate: independent review
- Route: review-only
- P3: out of scope and not entered
- Date: 2026-08-24
- Reviewer stance: fresh-context verification; implementation and work-log claims were not accepted without source/runtime evidence

## Scope

Reviewed the frozen P2 contract and implementation for:

- diagram/artwork and phase boundaries;
- `PartResearchService` catalog, drawer, and detail data;
- all 9 modules and 21 seeded parts;
- pointer, keyboard, fallback, drawer, detail, async, empty/error, responsive, and reduced-motion behavior;
- .NET and UI test quality;
- generated ServerTypes/MVC/ESM, navigation, project/package files, and portability.

P3 company comparison/detail implementation, trading/market/account/backtest functionality, and business-code changes were excluded.

## Verification

### Required commands

| Check | Result |
|---|---|
| `dotnet build SerenityQuantResearch.slnx --no-restore` | Passed; 0 warnings, 0 errors. Generated MVC/ServerTypes and TypeScript/ESM steps completed. |
| `dotnet test SerenityQuantResearch.slnx --no-build` | Passed; 13/13 tests. |
| `cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui` | Passed; 3/3 tests. Test-quality limitation is Finding M-03. |
| `cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build` | Passed; generated output reported no changed files. |

An initial npm invocation from the repository root failed because there is no root `package.json`; the required command was then run from the web project and passed.

### Data and contract checks

- Taxonomy-to-seed comparison: exact match for 9 unique `cpo.mod.*` IDs and 21 unique `cpo.part.*` IDs.
- Fresh-database service/runtime catalog: 9 modules, 21 parts, 21 unique part IDs; per-module counts were `3,2,3,3,2,1,2,2,3`.
- The .NET integration test independently retrieved every catalog part and confirmed its module, chain mapping, warnings, and unresolved questions.
- `cpo.part.host-asic.switch-die` resolved to `cpo.mod.host-asic`, one chain node, and one technology link.
- Broadcom remained `candidate` with `low` confidence and a scope note that denies a verified CPO product/supply relationship.
- `EVD-2026-0001@v1` remained `draft` and `contextualizes`; the UI/service warning correctly states that unreviewed evidence cannot support verified facts.
- Parts without company/evidence mappings rendered explicit research gaps rather than inferred relationships.
- No CPO JPEG/image asset, runtime JPEG reference, `<image>`, hotspot/image-map implementation, or CPO image file was found under project source/tests/data. The two reference JPEGs were visually inspected; the implementation is a materially different abstract 3×3 board/grid composition, not their exploded/product artwork.
- SVG source contains only generated geometry, labels, stable module/part IDs, and visual state. Company, chain, technology, and evidence records are queried from `PartResearchService`, not parsed from SVG.
- No P3 company universe/comparison UI and no trading, market-data, brokerage/live-account, backtest, portfolio-execution, or chat-only research module was found.

### HTTP and rendered-browser smoke

A separate post-build Kestrel process was started from this working tree on `127.0.0.1:5017` with a temporary SQLite database, then stopped and cleaned up.

- Anonymous `/Research/Cpo`: `302` to `/Account/Login`.
- Development login: `200`.
- Authenticated `/Research/Cpo`: `200`.
- Authenticated `/Research/Parts/cpo.part.host-asic.switch-die`: `200`.
- Generated diagram JS/CSS: `200`.
- Authenticated `ListParts`: `200`, 9 modules / 21 unique parts.
- Authenticated `RetrieveCompleteChain`: `200`, with Broadcom `candidate` and `EVD-2026-0001@v1` `draft`.
- Unknown part service request: expected `400 PartNotFound`; detail page rendered an error state.

Firefox 140 ESR was exercised headlessly through its built-in WebDriver BiDi endpoint without installing browser packages. The software-rendered browser verified:

- 9 module layers, 21 SVG part nodes, and 21 fallback buttons;
- pointer hover, one active/eight dimmed layers, click lock, and lock persistence after pointer leave;
- empty company/evidence messages plus warnings/questions;
- Enter and Space selection, Escape close, pointer close button, and fallback Enter selection;
- Broadcom `candidate` and evidence `draft` text in drawer and detail;
- 600px responsive rules (`column` heading, 780px scrollable SVG);
- successful 600×800 PNG capture from the rendered detail page;
- unknown-detail error rendering.

The same run exposed the stale clear/ARIA state in Finding M-02.

### Generated/source and portability checks

- Generated `PartResearchService` and response typings match the current C# service contract.
- Generated MVC includes both P2 views; ESM includes `CpoDiagramPage`; navigation points to `CpoResearchPage.Diagram`.
- Frontend output source map contains the current P2 TypeScript, and rebuild reported no generated changes.
- No current-host `/project/...`, `/home/...`, or `computer:///...` leak was found in project source/config/generated files.
- Runtime SQLite and temporary browser/Kestrel artifacts were cleaned or covered by ignore patterns.
- The repository has no `.git` metadata, so tracked/untracked status and a clean generated-file diff cannot be independently established.

## Findings

### Critical

None.

### High

#### H-01 — Drawer/detail omit mandatory P2 research sections

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Services/PartResearchService.cs:11-19`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts:355-381`
- **Problem:** The frozen page contract requires function, boundaries, upstream/downstream, key specifications, technology links, companies, evidence, conclusions, risks, and unresolved questions. The service/UI expose function/module, undifferentiated chain nodes, technologies, companies, evidence, warnings, and questions only. There are no explicit boundaries, upstream/downstream, key-specification, conclusion, or risk sections, even as empty/research-gap states.
- **Impact/evidence:** Both the drawer and “full detail” page use the same incomplete renderer. Headless rendering confirmed the omitted sections. P2 therefore does not satisfy drawer completeness, and the detail link does not provide additional completeness. Omitting a section also hides the distinction between “no reviewed conclusion/risk/specification exists” and “the product does not support that concept.”
- **Recommended fix:** Extend the service response and both render paths with all frozen sections. Preserve domain separation and represent unavailable/unverified content explicitly as empty gaps; do not infer product specifications, relationships, conclusions, or risks. Add contract tests for every required section.

### Medium

#### M-01 — Drawer requests have stale-result/error and retry races

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts:126-132`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts:188-209`
- **Problem:** Success rendering checks `state.selectedId`, but `catch` and `finally` do not. An older failed request can overwrite a newer selection with the old error, and an older completion can remove `aria-busy` while the current request is pending. Rejected promises remain permanently cached, preventing an in-page retry. `aria-expanded` is also updated after the asynchronous request rather than as part of guarded selection state.
- **Impact/evidence:** Rapid A→B selection under latency/failure can show an A error for selected part B or report the drawer as no longer busy. None of the current UI tests exercises page requests, ordering, rejection, or retries.
- **Recommended fix:** Use a drawer request generation/token or `AbortController`; guard success, error, and finalization with the current token; evict rejected cache entries; and derive ARIA state synchronously from the selected part.

#### M-02 — Clear/close leaves stale expanded and visual state and may restore focus to the wrong access path

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts:135-153`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts:209-224`
- **Problem:** Clear resets `aria-pressed` but never resets `aria-expanded`. It restores focus with the first document-wide matching selector, which is normally the SVG node even when selection originated in the fallback table. The focus handler immediately creates a hover state again.
- **Impact/evidence:** After browser-executed clear, the drawer was hidden and lock removed, but the activating SVG still had `aria-expanded="true"` and eight layers were dimmed again; this conflicts with the closeout acceptance statement that dimming is removed. Fallback users can be moved unexpectedly from the table back to the SVG. Assistive technology receives stale expansion state.
- **Recommended fix:** Track the exact initiating element, reset `aria-expanded` for all representations on clear, keep mirrored SVG/table ARIA state consistent, restore focus to the initiator, and reconcile focus highlighting with the documented requirement that close/clear removes dimming.

#### M-03 — UI tests are helper-only and can produce false confidence about the core flow

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs:1-32`
- **Problem:** The three tests import only `PartSelectionState.ts`. They never instantiate `CpoDiagramPage`, render SVG/table/drawer/detail DOM, call the service, or exercise actual event/ARIA/focus/error/async wiring.
- **Impact/evidence:** The suite passes despite H-01, M-01, and M-02. It does not prove that all 21 parts are rendered, Enter/Space/Escape are wired, fallback navigation works, drawer sections are complete, errors are recoverable, or stale requests are suppressed. The .NET test provides strong service coverage but cannot close these UI gaps.
- **Recommended fix:** Add DOM/browser-level tests around the real page initializer and service stubs, including all 21 bindings, pointer/focus/click/Enter/Space/Escape, close/clear focus and ARIA, drawer/detail navigation, out-of-order success/failure, retry, empty/error states, responsive layout, and reduced motion.

### Low

#### L-01 — P2 duplicates generated service contracts instead of consuming them

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts:13-60`; generated counterpart `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/PartResearchService.ts:1-24`
- **Problem:** The page hand-defines every service DTO and hard-codes the service base despite matching generated ServerTypes being available.
- **Impact/evidence:** Current source/generated output is consistent, but future server contract changes can compile against permissive local optional interfaces while the page silently drifts.
- **Recommended fix:** Import the generated service namespace and generated response/request interfaces; retain only presentation-specific local types.

#### L-02 — Catalog failure/empty states leave contradictory page-level status

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts:113-124`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts:232-235`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramIndex.cshtml:26-31`
- **Problem:** On catalog failure only the fallback container receives an inline error; the SVG remains blank, coverage remains “loading,” and the initial preview still claims 21 parts. A successful zero-module response produces blank SVG/table content without an explicit empty-state explanation.
- **Impact/evidence:** Users can see mutually inconsistent status and cannot distinguish loading, failed, and empty catalogs. The current tests do not exercise either branch.
- **Recommended fix:** Render one coherent page-level error/empty state, update coverage and preview, clear busy state, and offer a safe retry.

## Unverified Items

- No display server was available. Firefox headless software rendering and real BiDi pointer/keyboard actions passed, but human visual inspection on a physical graphical desktop, pixel fidelity, color contrast, zoom/high-contrast modes, and cross-browser behavior remain unverified.
- No screen reader/accessibility-tree audit was performed. Source/ARIA and keyboard behavior were inspected, and Finding M-02 records the observed state defect.
- `prefers-reduced-motion` CSS exists and removes the relevant transitions, but an OS/browser reduced-motion preference was not emulated in the browser run.
- The reference JPEGs and generated composition were inspected, and no copied/runtime asset or similar geometry was found; legal provenance/public reuse rights for the JPEGs remain unresolved as documented.
- No `.git` metadata exists, so tracked-file cleanliness, ignored runtime artifacts, and an independent diff against the pre-P2 baseline are unverified.

## Decision

**changes requested**

The build, service/data, seeded-state, HTTP, and most rendered interaction checks pass, but H-01 is a High contract gap. P2 must not be marked independently reviewed under the stated gate. The async, ARIA/focus, and test-evidence gaps also need correction and regression coverage.

## P3 Gate Recommendation

- P2 may be marked independently reviewed: **No**.
- P3 may start: **No**.
- Recommendation: remain at the P2 gate, resolve H-01 and the Medium findings, rerun the full required verification plus rendered interaction tests, and obtain a focused independent re-review. Do not use P3 work to conceal or bypass the P2 contract gaps.

## Focused Re-review — 2026-08-24

### Scope and reviewer stance

This was a fresh-context, review-only re-test of the original H-01, M-01 through M-03, and L-01 through L-02 findings after remediation. The plan, work log, original review history, taxonomy, evidence contract, service/UI/state/request sources, .NET and UI tests, browser runner, generated ServerTypes, views/endpoints, package scripts, seed, and reference JPEGs were read or inspected independently. Remediation claims were not accepted without current source and runtime evidence. P3 was not entered, and no business code, tests, plans, README, or work log was changed.

This section supersedes the original `changes requested` gate outcome for the current P2 state while preserving that original decision as review history.

### Original-finding disposition

| Finding | Disposition | Focused re-review evidence |
|---|---|---|
| H-01 | **resolved** | `PartResearchService.cs:11-24,125-166` exposes function/module plus explicit boundaries, upstream/downstream, key specifications, chain nodes, technologies, companies, evidence, conclusions, risks, warnings, and questions. `CpoDiagramPage.ts:340-366` renders them in the shared drawer/detail path. Missing facts are represented as baseline/unresolved/none/warning gaps; no product specification, directional supply relationship, published conclusion, or verified exposure is invented. Real Firefox rendering confirmed the required drawer and detail sections. |
| M-01 | **resolved** | `CpoDiagramPage.ts:157-181,188-202` starts/cancels request generations and guards success, error, and finalization against both the current token and selected part. `ResearchRequestState.ts` evicts rejected promise entries. Unit tests passed for latest-request invalidation and rejected-cache retry. Cancellation is safe UI invalidation rather than transport abort; stale completions cannot update or clear the active drawer state. |
| M-02 | **resolved** | `CpoDiagramPage.ts:96-117,188-202` resets mirrored SVG/table `aria-pressed` and `aria-expanded`, clears active/dimmed/locked state, remembers the exact initiating element, suppresses focus-driven hover during restoration, and restores focus only to that connected initiator. The committed browser test passed; an additional temporary stricter Firefox run asserted that SVG close returned inside `#cpo-diagram` and fallback close returned inside `#cpo-part-tree`, with zero dimmed layers. |
| M-03 | **resolved with minor test-hardening finding L-03** | The committed suite is no longer helper-only: it starts a fresh temporary SQLite/Kestrel application, authenticates, loads the generated page/assets and services in headless Firefox, and exercises 9 modules/21 SVG and fallback bindings, pointer hover/click, Enter/Space/Escape, close/clear, drawer sections, candidate/draft states, fallback selection, detail rendering, and an unknown-detail error. The runner was inspected line by line rather than accepted from its final success message. See L-03 for assertion precision that should still be improved. |
| L-01 | **resolved** | `CpoDiagramPage.ts:1-9,33-39` imports the generated service namespace and generated DTO interfaces. The generated `PartResearchService.ts` methods and generated response fields match the current C# contract; the Microsoft.TypeScript.MSBuild-bundled compiler no-emit check passed. |
| L-02 | **resolved** | `CpoDiagramPage.ts:72-81,211-218,464-478` routes both empty and failed catalogs through one coherent status renderer: SVG is cleared/hidden, coverage and preview are updated, the fallback area shows an info/error alert, busy state is finalized, and retry performs a full reload. The branches were source-inspected; see unverified items for browser fault injection. |

### Verification

| Check | Result |
|---|---|
| `dotnet build SerenityQuantResearch.slnx --no-restore` | Passed; 0 warnings, 0 errors; generated MVC/ServerTypes and ESM steps completed with no generated output changes. |
| `dotnet test SerenityQuantResearch.slnx --no-build` | Passed; 13/13 tests. |
| `cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui` | Passed; 5/5 Node tests plus fresh temporary Kestrel/SQLite and headless Firefox browser smoke. The test itself, setup, assertions, and cleanup paths were inspected. |
| `cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build` | Passed; 30 generated outputs checked, none changed. |
| Microsoft.TypeScript.MSBuild-bundled TypeScript 6.0.3: `tsc.js --noEmit --project tsconfig.json` | Passed with no diagnostics. |
| Additional exact-focus Firefox run | Passed; exact SVG and exact fallback initiator restoration were asserted, not merely the shared `data-part-id`. |
| Taxonomy/seed check | Passed; exact sets of 9 module IDs and 21 part IDs match the frozen taxonomy; IDs are unique; per-module counts are `3,2,3,3,2,1,2,2,3`. |
| State/contract check | Passed; Broadcom remains `candidate`/`low`; `EVD-2026-0001@v1` remains `draft`/`contextualizes`; generated frontend contracts match the service response. |
| Boundary scan and image inspection | Passed; no CPO JPEG copy, matching hash, runtime JPEG reference, authored image asset, `<image>`, hotspot/map, or traced exploded geometry was found. The implementation remains an original abstract 3×3 composition. SVG carries presentation geometry/IDs/state only; business links come from the service. No P3 company comparison/detail, prohibited trading/market/account/backtest/chat-only scope, or candidate/draft promotion was found. |
| Change-boundary hash check | Passed; authored source/evidence hashes were unchanged by verification before this review-record update. The repository still has no `.git` metadata. |

### New findings

#### Critical

None.

#### High

None.

#### Medium

None.

#### Low

##### L-03 — Browser smoke has assertion blind spots despite exercising the real page

- **File:line:** `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh:115-117,127-129,134-156`; `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs:38-59`
- **Evidence/problem:** The browser suite proves a real 21-node render but checks counts rather than the exact frozen ID set/uniqueness. Its drawer section list does not explicitly assert the function summary or physical-module badge. Most importantly, both SVG and fallback focus assertions compare only `document.activeElement.dataset.partId`; because both representations share that value, the fallback assertion would also pass if focus incorrectly returned to the SVG representation. Out-of-order page success/error/finally behavior and catalog empty/error retry remain covered by helper tests/source review rather than browser fault injection.
- **Impact:** This does not indicate a current functional defect: source inspection and the stricter independent Firefox run confirmed the exact initiators and current request guards. It does leave avoidable regression-test false-positive paths in areas that previously failed.
- **Recommendation:** Harden the committed browser test in a future P2 maintenance change by asserting the exact frozen ID set and uniqueness in both representations, function/module rendering, `activeElement.closest('#cpo-diagram')` versus `activeElement.closest('#cpo-part-tree')`, and fault-injected out-of-order/rejected/catalog empty/error scenarios. Do not fold this work into P3 behavior.

### Unverified items

- Catalog empty/error responses and out-of-order drawer responses were not fault-injected through the committed real-browser suite; the current branches were verified by complete source tracing, helper tests, and the successful real-page baseline flow.
- Firefox headless software rendering passed, but physical-desktop visual fidelity, cross-browser behavior, screen-reader/accessibility-tree output, contrast, zoom/high-contrast, and reduced-motion emulation remain unverified.
- JPEG provenance/public reuse rights remain unresolved. No copy, trace, or runtime use was found, so this does not block the current original composition.
- Without `.git` metadata, tracked/untracked status and a baseline diff remain independently unavailable; pre/post verification hashes confirmed no authored-file changes before this review update.

### Decision

**approved with minor findings**

No Critical, High, or Medium finding remains. The frozen P2 service/UI contract, all 21 part bindings, core pointer/keyboard/fallback/drawer/detail interactions, async guards, reset/focus behavior, generated contract use, status handling, and strict phase/artwork/evidence boundaries pass. L-03 is a regression-assertion precision issue, not a current core-contract failure, and the combined automated, rendered-browser, source, and additional focused evidence is sufficient for the P2 gate.

### Independently-reviewed status and P3 recommendation

- P2 independently reviewed: **Yes**.
- P3 gate may open: **Yes**, only in a separately authorized session.
- P3 started by this review: **No**.
- Recommendation: preserve candidate/draft controls and the service/SVG boundary when P3 is authorized; address L-03 as bounded P2 test hardening rather than concealing it inside P3 functionality.
