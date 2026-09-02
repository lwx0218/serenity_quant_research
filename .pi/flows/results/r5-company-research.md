## Flow: r5-company-research
Duration: 10m 24s | Agents: 5

### Results
✓ scope-context-scout: Read-only R5 scouting complete.

R5 DoR / dependencies:
- Canonical Plan says Accepted-effective Rounds: R1, R2, R3, R4; Active Round: none; next R5 requires separate Owner start decision.
- R5 DoR: R4 accepted-effective; Explorer context contract stable; R1 disposition identifies reusable Company services/routes/policies.
- Based on the Plan, R4 appears accepted-effective enough as a prerequisite, but R5 must still be explicitly started/accepted by Owner. Current HEAD: bfa1357d2ef51269b97c4cc6f6f4e6498ebb912d.

R5 candidate surfaces, if Owner starts R5:
- src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/
- Narrow CompanyUniverse service/view-model adaptation
- Company service/policy tests
- tests-ui/
- Expected product: default Card View, List View with shared filters/context, Quick Drawer with close/Esc/outside dismiss, expand to entity-centric Full Company Detail, Explorer source path preserved/understandable.

Context sources, not candidate by default:
- AGENTS.md; src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md
- operations/planning/research-experience-reboot.md R5 + global gates
- operations/orchestration/research-experience-reboot.md
- docs/product/acceptance-contract.md
- docs/research-baseline/evidence-contract.md
- R1/R4 evidence and current P3 code/services/tests are context unless explicitly declared candidate.

Environment / dirty-worktree items not automatically candidate:
- Dirty/untracked paths exist and must be protected/classified, not assumed candidate merely because present.
- Notable dirty items include .pi/settings.json, .pi/flows/, .pi/npm/, .pi/skills/manage-flows/, governance backlog, R3 review, many R4 screenshot files, and current modified Company/R5-looking files plus package.json/test-ui script.
- Even paths overlapping expected R5 surfaces must be explicitly declared as R5 candidate by the active Builder/Owner; otherwise treat as dirty environment/context.

Protected surfaces / hard stops:
- Stop on schema/migration/stable ID changes; seed fact changes; evidence/review/publication/audit semantics changes; candidate/verified or draft/reviewed policy changes.
- Stop on Company Comparison, Workspace implementation, persistent writing, ResearchNote/OpenQuestion/Backlink/Graph/New Note/editor endpoints.
- Stop if prototype/mock facts become seed/database/research copy/company exposure/conclusion/report, or if candidate/draft/unknown state is visually upgraded to verified/reviewed.
- Stop if Card/List → Quick Drawer → Full Detail path must change, persistent schema is required, evidence/audit semantics must change, or new persistent writing is introduced.

Reminder:
- This scouting does not implement product code, does not replace Plan/review/Owner gates, must not auto-commit/push, and must not start R6 after R5 acceptance.
✓ product-contract-scout: R5 product contract is clear.

Company Pool acceptance:
- Default browse mode is Card View, not SleekGrid/table-first.
- List View is optional compact mode; it must show the same company universe and retain the same active filters and research context.
- Shared filters should be lightweight/high-value research controls (search, component/material group, chain role, market/region or exposure state only when needed), not admin-style long forms.
- Explorer source path/context must remain visible/understandable, e.g. CPO → SiPh PIC → Modulator, and may drive initial filter/order/rationale/drawer/detail content.
- Card/list views should preserve filters, context, and scroll position when opening a company.

Quick Drawer acceptance:
- Clicking a company card or list row opens the same Quick Company Drawer; first click must not navigate directly to Full Detail.
- Company Pool remains visible behind the drawer.
- Drawer must retain source research context.
- Drawer closes without navigation via close icon, outside click, and Esc.
- Drawer must include an explicit expand icon/action to Full Company Detail.
- Minimum drawer content: identity, short research summary, exposure tags, exposure verification state, evidence coverage, open-question count, quick links/sections, expand action.

Full Company Detail acceptance:
- Opened only through Quick Drawer expand in the accepted path: Card/List → Quick Drawer → Expand → Full Company Detail.
- Entity-centric page answering what is known about the company and its industry-chain exposure.
- Selected company and Explorer/source context must remain consistent/visible.
- Continuous or lightly segmented layout is preferred; do not default to seven tabs.
- Expected sections: overview, industry-chain exposure, current research context, key evidence, open questions, relevant events/financial evidence only when material, and link to Research Workspace.

Research data safety obligations:
- Existing exposure states must be preserved: discovery, candidate, verified, rejected, stale.
- Candidate/discovery/unknown/draft states must not look verified/reviewed/published.
- Prototype/model/mock content does not become research fact, seed data, database truth, research copy, company exposure, thesis, conclusion, or report claim.
- Unsourced supplier/customer relationships, production status, market share, BOM value share, localization rate, technology-barrier score, company tier, and investment thesis are forbidden as production facts unless supported by the evidence contract.
- Level C/image/prototype leads cannot alone support verified exposure/conclusions; reviewed evidence and audit semantics must not change.

Explicit out of scope for R5:
- Company Comparison.
- Research Workspace implementation.
- Default SleekGrid-first product.
- Default seven-tab company detail.
- Persistent schema changes, new persistent writing, or changes to evidence/audit/review policy.

Required product-visible evidence for R5 review:
- 1440px and 1920px screenshots/states for Card View, List View, Quick Drawer, and Full Company Detail.
- Evidence of Explorer context preservation.
- Sequence proving context/filter/scroll preservation across Card/List → Drawer → Detail.
- Policy regression record plus validation; candidate/draft/unknown semantics must be visible where relevant.
✓ code-scout: Read-only R5 code scouting complete at HEAD bfa1357d2ef51269b97c4cc6f6f4e6498ebb912d.

Company module pages/scripts/styles/state:
- src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyResearchPage.cs: routes /Research/Companies, /Research/Companies/{companyId}, /Research/ChainNodes/{chainNodeId}; all require ResearchPermissionKeys.General.
- CompanyUniverse.cshtml: Company Pool markup; Card View default, List View peer, lightweight filters, source context ribbon, Quick Drawer shell.
- CompanyDetail.cshtml: Full Company Detail route shell; back link preserves query string.
- ChainNodeDetail.cshtml: chain-node cross-navigation page using same TS module in chain mode.
- CompanyUniversePage.ts: main UI implementation entry point; loads CompanyUniverseService.List/Retrieve/RetrieveChainNode; renders cards/list, Quick Drawer, Full Detail, context query preservation, close/Esc/outside dismiss, expand link.
- CompanyUniversePage.css: Company Pool/Drawer/Detail styling and visual trust-state treatments.
- CompanyUniverseState.ts: reusable state helpers; defaultCompanyBrowseView='card', allowed views card/list, filter normalization, state labels/trust tone.

Service/endpoint/view-model files likely reusable/adaptable:
- Modules/Research/Endpoints/CompanyUniverseEndpoint.cs: read endpoints List/Retrieve/RetrieveChainNode at Services/Research/CompanyUniverse/*; also contains CompanyExposureEndpoint.Update protected by ResearchPermissionKeys.Review.
- Modules/Research/Services/CompanyUniverseService.cs: request/response DTOs, CompanyUniverseItem, CompanyExposureDetail, evidence summaries, ICompanyUniverseService, list/filter/retrieve/detail/cross-nav logic, policy-gated UpdateExposure.
- Generated TS DTO/service files: Modules/ServerTypes/Research/CompanyUniverseService.ts and Services.Company*.ts.
- Startup registration found: Initialization/Startup.cs registers ICompanyUniverseService -> CompanyUniverseService.

Existing focused tests / validation:
- tests/SerenityQuantResearch.Tests/CompanyUniverseServiceTests.cs: seeded company universe count/identity, filters, search behavior, freshness contract, candidate/draft not verified, update rejection, cross-navigation stable IDs.
- tests/SerenityQuantResearch.Tests/CompanyExposureEndpointPolicyTests.cs: endpoint policy 4xx/no mutation, machine reviewer denial.
- src/.../tests-ui/CompanyUniverseState.test.mjs: state/helper unit tests for card default, filter dimensions, source defaults, unverified labels, deterministic sorting.
- src/.../tests-ui/run-browser-smoke.sh: existing R4 browser smoke and research shell regression.
- src/.../tests-ui/run-r5-company-browser-smoke.sh: R5 browser smoke exists in worktree as untracked; validates Card/List/Drawer/Detail screenshots and acceptance states if Owner accepts it as candidate.

Likely missing/fragile R5 coverage:
- If untracked/dirty R5 smoke is not accepted as candidate, product-visible R5 browser coverage is missing from committed baseline.
- Current focused service tests do not assert UI-only behaviors: first click opens drawer not navigation, drawer close methods, scroll preservation, expand-only detail path, screenshots at 1440/1920.
- CPO Explorer currently has an existing direct related-company link to /Research/Companies/{id} in Modules/Research/Diagram/CpoDiagramPage.ts; Owner may need to decide whether R5 must preserve/alter this because accepted Company Pool path says Card/List -> Drawer -> Expand for the accepted Full Detail flow.

Build/test/UI commands:
- From repo root: dotnet build SerenityQuantResearch.slnx
- From repo root: dotnet test SerenityQuantResearch.slnx
- Focused service tests: dotnet test SerenityQuantResearch.slnx --filter CompanyUniverseServiceTests
- Focused policy tests: dotnet test SerenityQuantResearch.slnx --filter CompanyExposureEndpointPolicyTests
- From src/SerenityQuantResearch/SerenityQuantResearch.Web: npm run build
- From src/SerenityQuantResearch/SerenityQuantResearch.Web: npm run test:ui:unit
- From src/SerenityQuantResearch/SerenityQuantResearch.Web: npm run test:ui:browser:r5 (requires Firefox; script currently untracked/dirty candidate)
- From src/SerenityQuantResearch/SerenityQuantResearch.Web: npm run test:ui for unit + browser smoke.

Candidate write surfaces if Owner explicitly starts R5:
- Modules/Research/Company/*
- Modules/Research/Endpoints/CompanyUniverseEndpoint.cs only for read endpoint/view-model adjustments; keep UpdateExposure policy semantics protected.
- Modules/Research/Services/CompanyUniverseService.cs for non-schema read model/list/retrieve adaptations only.
- Generated ServerTypes if DTO/service contract changes through normal generation.
- tests-ui/* and package.json scripts for accepted UI validation.
- tests/SerenityQuantResearch.Tests/CompanyUniverseServiceTests.cs and CompanyExposureEndpointPolicyTests.cs for focused regression additions.

Protected surfaces / blockers needing Owner decision:
- No schema/migration/seed/fact/evidence semantics changes without hard stop.
- Do not touch evidence/review/publication/audit semantics or candidate/verified/draft/reviewed policy.
- Do not implement Company Comparison, Research Workspace writing, persistent writing, ResearchNote/OpenQuestion/Backlink/Graph/New Note/editor endpoints.
- Do not promote prototype/mock/unsupported supplier/customer/production/market-share/BOM/localization/technology-barrier/tier/thesis claims into production facts.
- Worktree already contains dirty/untracked R5-looking files and package.json changes; these must be explicitly classified by Owner/Builder before implementation.
✓ implementation: Changed R5 candidate surfaces only: `Modules/Research/Company/CompanyUniversePage.ts` and `tests-ui/run-r5-company-browser-smoke.sh`. Addressed P1 by making outside-click dismiss ignore card/list activation targets, preserving drawer activation. Addressed Full Detail context by rendering part/chain stable IDs in the source path and syncing the Back link from normalized source/filter/view context. Fixed the BiDi generated-script newline hazard by replacing `\n` string joins with `String.fromCharCode(10)`. Updated R5 browser smoke to assert part+chain context preservation and capture the required 1440/1920 Card/List/Drawer/Detail screenshots plus an extra part+chain detail screenshot. No schema, migrations, seed, evidence/audit semantics, Company Comparison, Workspace implementation, commits, or R6 changes. Validation/review were not run because this harness session exposes no command-execution or independent-review tool; rerun `npm run build`, `dotnet build/test`, `npm run test:ui:browser:r5`, full `npm run test:ui`, and R5 review.
⚠ verification: R5 validation blocked by UI product-visible smoke failure. Passed: focused service checks `dotnet test SerenityQuantResearch.slnx --filter CompanyUniverseServiceTests` (26 passed), focused policy checks `dotnet test SerenityQuantResearch.slnx --filter CompanyExposureEndpointPolicyTests` (2 passed), `cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build`, `dotnet build SerenityQuantResearch.slnx --no-restore`, and `dotnet test SerenityQuantResearch.slnx --no-build` (54 passed). Failing command: `cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui`. Failure occurred inside `npm run test:ui:browser` / `bash tests-ui/run-r5-company-browser-smoke.sh`: `Error: scroll position changed after opening drawer: 45 vs 12`. Product-visible evidence is incomplete: R4 smoke passed; R5 produced only `operations/reviews/research-experience-reboot-r5-screenshots/r5-company-card-1440.png` and `r5-company-list-1440.png` before failing, so 1920 Card/List and Quick Drawer/Full Detail screenshots plus context/filter/scroll preservation sequence and candidate/draft/unknown visual evidence remain unverified.
