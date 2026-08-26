# Phase 1 P3 Work Log — Company Universe and Detail

## Status

- Date: 2026-08-25
- Route: continue existing `plan`
- Result: completed and independently reviewed (`approved with minor findings`); initial `changes requested` history preserved
- P4 status: not started

## Implemented

### CompanyUniverseService and policy

- Added `CompanyUniverseService` over the existing `Company`, `CompanyExposure`, `PhysicalPart`, `IndustryChainNode`, `Evidence`, source, event, conclusion, and audit relationships.
- All 20 seeded companies resolve by stable company ID, including identity/market fields, universe layer, coverage priority, explicit exposures, roles, relevance, confidence, verification state, scope note, evidence/review state, audit metadata, coverage, and category-aware freshness where explicit type data supports it (`unknown` otherwise).
- Companies without exposure/evidence records remain visible with explicit `unmapped` / research-gap indicators.
- Server filters cover physical part, chain node, role, exchange, geography, universe layer, coverage priority, verification state, evidence coverage, freshness, and identity-only search.
- Added stable chain-node retrieval for company → chain → part/company cross-navigation.
- Added server-side exposure update policy under `Research:Review`; updates use Serenity logging-row audit fields and require an explicit existing exposure.
- Exposure promotion to `verified` requires an authenticated human-review path plus supporting `reviewed` Level A/B evidence. Draft, in-review, rejected, Level C, and contextual-only evidence cannot satisfy the policy. Machine state changes are rejected by the policy API.
- Rejected/stale exposures remain valid visible/auditable states; there is no delete or silent promotion path.

### SleekGrid-first company universe and comparison

- Added `/Research/Companies` and a CPO research navigation item.
- Uses the bundled Serenity 10.3.7 SleekGrid with three frozen identity/selection columns, sortable research fields, high-density layout, all required server filters, and bounded five-company comparison.
- Comparison selection is available as native checkboxes in both SleekGrid and the fallback table; comparison rows link to stable company detail URLs.
- A native table fallback is always present and `?view=table` provides an explicit no-grid mode.
- No price-movement, quote, market-performance ranking, trading, or export scope was added.

### Company detail, exposure editing, and cross-navigation

- Added `/Research/Companies/{companyId}` with the seven frozen accessible tabs:
  1. Overview
  2. Industry-chain Exposure
  3. Earnings & Financial Evidence
  4. Capex & Investment
  5. Events
  6. Research Conclusions
  7. Sources & Audit
- Existing records are displayed; unavailable typed financial/Capex/event/conclusion/source records render explicit gaps instead of keyword classification or fabricated claims.
- Existing exposure fields, supporting/contradicting/context evidence states, source/review state, and audit metadata are visible. Review-permitted users receive an inline edit form; evidence workflow remains read-only in P3.
- Added `/Research/ChainNodes/{chainNodeId}` as a bounded stable cross-navigation target.
- Part drawer/detail company records now link to stable company detail URLs.
- Company detail links to existing stable physical-part URLs and stable chain-node URLs; chain-node detail links back to company and part.

### Independent-review remediation

The initial fresh independent review returned `changes requested` with H-01/H-02, M-01, and L-01. One permitted P3-only remediation cycle addressed all four without entering P4:

- H-01: selected Serenity 10.3.7 `FrozenLayout`; the committed Firefox suite now asserts exactly three `.sg-start` headers and verifies their x-position remains fixed during real horizontal scrolling.
- H-02: added a migration-backed, security-administered `Users.ActorType` (`human` / `machine`). The exposure endpoint derives reviewer humanity exclusively from the persisted server identity. A real authenticated endpoint test gives a machine principal `Research:Review` plus eligible human-reviewed Level A supporting evidence and confirms `MachineExposureStateChangeDenied` with no mutation. Supporting evidence also qualifies only when its `ReviewedBy` user is persisted as human.
- M-01: policy denials now use stable `ValidationError` codes and return HTTP 400. Endpoint/browser tests assert `VerifiedExposureEvidenceRequired`, rollback, candidate/draft persistence, and absence of unhandled/`InvalidOperationException` failures.
- L-01: freshness now requires an explicit evidence category and follows the frozen category thresholds; missing category returns `unknown`, while historical financial facts are marked non-expiring instead of being auto-staled.

The original review record and `changes requested` decision remain preserved in `operations/reviews/phase-1-p3-independent-review.md`.

### Accessibility and generated contracts

- Native labels and controls are used for all filters and comparison selection.
- Tabs implement `tablist` / `tab` / `tabpanel`, `aria-selected`, roving tabindex, Arrow keys, Home, and End.
- Visible focus styling covers filters, comparisons, tabs, links, and exposure forms.
- Candidate/discovery/draft/in-review/rejected/stale labels include meaningful human-readable qualification.
- Generated Serenity ServerTypes are consumed by the TypeScript page; no duplicate service URL/DTO contract was introduced.

## Self-verification

Passed:

```text
dotnet build SerenityQuantResearch.slnx --no-restore
  0 warnings, 0 errors

dotnet test SerenityQuantResearch.slnx --no-build
  51 passed, 0 failed

cd src/SerenityQuantResearch/SerenityQuantResearch.Web
npm run test:ui
  10 Node UI state tests passed
  fresh SQLite + Kestrel + Firefox browser smoke passed
npm run build
  passed; generated frontend output current

Microsoft.TypeScript.MSBuild 6.0.3 tsc --noEmit --project tsconfig.json
  passed with no diagnostics
```

Fresh SQLite / authenticated HTTP verification passed:

- anonymous `/Research/Companies`: expected `302` to login;
- authenticated universe/detail/chain-node/part/CPO pages: `200`;
- authenticated `CompanyUniverse/List`, `Retrieve`, and `RetrieveChainNode`: `200`;
- all 20 unique stable company IDs returned and every company service/page target resolved;
- every current company exposure part/chain cross-navigation target resolved;
- fresh seed counts remained 9 modules, 21 parts, 10 chain nodes, 20 companies, 1 exposure, and 1 evidence record;
- Broadcom remained `candidate`;
- `EVD-2026-0001@v1` remained `draft` and `contextualizes`;
- candidate → verified was rejected with structured HTTP 400/code in service, endpoint, unit-policy, and real-browser paths without mutation;
- a Review-authorized machine identity with otherwise eligible supporting evidence was rejected by the real endpoint;
- fresh `Users.ActorType` migration defaulted the development admin to `human`;
- application log contained no failed/unhandled request in the successful HTTP smoke.

Firefox real-page coverage includes:

- exact 20-company stable-ID set and real SleekGrid cell/header rendering;
- exactly three real `FrozenLayout` start headers, horizontal-scroll persistence, and native table fallback;
- server exchange filtering and filter reset;
- keyboard comparison selection and detail navigation;
- all 20 detail page targets;
- all seven tabs and ArrowRight keyboard activation;
- candidate/draft labels, rejected promotion, and state persistence after reload;
- company → part/chain and chain → company/part navigation;
- explicit `?view=table` fallback mode.

Boundary scans found no P3 implementation of P4 ingestion/timeline/transitions, P5 publication/version workflow, trading/K-line/quote/market-tape/account/portfolio/order execution/backtest/chat-only functionality, runtime JPEG use, image hotspots, or inferred customer/supplier/order/revenue-share/mass-production claims. Read-only display of existing evidence/conclusion publication metadata is present as required by the frozen company tabs; no transition or publication action was added.

Toolchain used for final verification:

- .NET SDK `10.0.400`
- Node `24.19.0`
- npm `11.17.0`
- Serenity Community `10.3.7`

## Known gaps

- The seed intentionally contains only one candidate exposure and one draft contextual evidence record. The other 19 companies and most company-detail evidence tabs therefore show explicit research gaps.
- Financial and Capex evidence are not keyword-classified because the current schema has no reviewed typed relationship for those categories; populating/reviewing those records belongs to later authorized work.
- Exposure evidence associations are displayed but not edited; evidence ingestion/review transitions remain P4 scope.
- Independent-review L-01R: the current schema has no persisted freshness category, so materialized records correctly show `unknown`; category-specific next-report semantics and neutralized UI wording remain a future bounded gap.
- Independent-review L-02: handled policy denials return stable HTTP 400/code but Serenity logs `ValidationError` at fail severity, which can create observability noise.
- Only Firefox headless is automated. Physical-desktop visual review, screen reader output, contrast/high-contrast/zoom, and cross-browser behavior remain unverified.
- JPEG provenance/public reuse rights remain unresolved; P3 does not use either JPEG.
- The repository still has no `.git` metadata, so review relies on file inventory, generated-output checks, source tracing, runtime tests, and boundary scans.

## Preview

- Company universe: `http://localhost:5000/Research/Companies`
- Broadcom detail: `http://localhost:5000/Research/Companies/global.broadcom`
- ASIC chain-node detail: `http://localhost:5000/Research/ChainNodes/cpo.chain.asic`

## Independent review closeout

- Initial fresh review decision: `changes requested` (H-01/H-02, M-01, L-01)
- One bounded P3-only remediation cycle: completed
- Fresh focused re-review decision: `approved with minor findings`
- H-01/H-02: resolved
- M-01 HTTP 400/code/rollback contract: resolved
- Remaining Low findings:
  - L-01R: category-specific/next-report freshness semantics and labels remain incomplete; current untyped records safely return `unknown`
  - L-02: Serenity logs handled policy `ValidationError` responses at fail severity despite correct HTTP 400 behavior
- Review history: `operations/reviews/phase-1-p3-independent-review.md`
- P3 independently reviewed: yes
- P4 readiness: P3 no longer blocks a separately authorized P4 round
- P4 status: unstarted; no P4/P5/P6 work was performed
