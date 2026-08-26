# Phase 1 MVP Plan — CPO Research Workstation

## Status

- Route: `plan`
- Baseline: confirmed through an against-docs `grill-with-docs` session
- Implementation status: P3 complete and independently reviewed (`approved with minor findings`); P4 not started
- Scope status: frozen for Phase 1; additions require an explicit plan update

## P0 Progress — 2026-08-24

- Status: completed; deliverables are explicit and reviewable
- Taxonomy/glossary: `docs/research-baseline/cpo-taxonomy.md`
- Company seed universe: `docs/research-baseline/company-universe.md`
- Evidence/review/publication contract and image-risk record: `docs/research-baseline/evidence-contract.md`
- Serenity template/version and P1 bootstrap contract: `operations/planning/serenity-bootstrap.md`
- P1 implementation was not started during P0; it was completed in the subsequent authorized P1 round
- JPEG provenance and public reuse rights remain unresolved; copied artwork remains prohibited

## P1 Progress — 2026-08-24

- Status: completed; P2 not started
- Community Serene `10.3.7` application and .NET 10/Node 24 toolchain are operational
- SQLite migrations implement the frozen research objects, recursive parts, many-to-many links, audit fields, evidence/conclusion/report version relationships, and minimum permissions
- Idempotent seed import loads 9 modules, 21 parts, 10 chain nodes, 20 companies, and one candidate/draft complete chain
- `PartResearchService` queries part → chain/technology → company exposure → evidence without diagram parsing
- Evidence transition and conclusion publication policies enforce the P0 contract baseline
- Verification: build has 0 warnings/errors; 12 tests pass; `sergen doctor`, HTTP login smoke, fresh migration, seed counts, and complete-chain SQL query pass
- Work log: `operations/work_logs/phase-1-p1.md`

## P2 Progress — 2026-08-24

- Status: completed and independently reviewed (`approved with minor findings`); P3 not started
- Added an original service-driven 3×3 CPO system composition; no JPEG pixels, traced geometry, or hotspot map are shipped
- All 21 seeded parts are listed by `PartResearchService`, bound to generated SVG groups through stable `data-part-id` values, and selectable through both SVG and tree/table paths
- Hover/focus highlighting, unrelated-module dimming, click/Enter/Space lock, Escape/clear behavior, research drawer, and part-detail navigation are implemented
- Drawer/detail content queries physical module, chain nodes, technology links, candidate company verification states, evidence review states, warnings, and unresolved questions from the research service
- Independent review initially returned `changes requested`; H-01 and M-01 through M-03 were remediated without entering P3
- Fresh-context focused re-review resolved H-01, M-01 through M-03, and L-01/L-02; final decision is `approved with minor findings`
- Remaining L-03 is bounded browser-test assertion hardening, not a current contract or interaction failure
- Verification: build has 0 warnings/errors; 13 .NET tests, 5 UI state/request tests, and fresh Kestrel + Firefox browser wiring tests pass; frontend build passes
- Work log: `operations/work_logs/phase-1-p2.md`
- Review record: `operations/reviews/phase-1-p2-independent-review.md`

## P3 Progress — 2026-08-25

- Status: completed and independently reviewed (`approved with minor findings`); P4 not started
- Added `CompanyUniverseService` with stable-ID retrieval, explicit relationship aggregation, all frozen filters, coverage/freshness indicators, company detail, chain-node cross-navigation, and review-permitted audited exposure updates
- Added a Serenity 10.3.7 SleekGrid-first company universe with three frozen identity/selection columns, sorting, bounded five-company comparison, stable detail navigation, and an always-available native table fallback
- Added the seven frozen accessible company-detail tabs; existing records render directly and missing typed financial/Capex/event/conclusion/source records render explicit research gaps
- Added part → company, company → part/chain, chain → company/part, and grid/comparison → company cross-navigation using stable IDs only
- Server policy rejects machine state changes and rejects `verified` unless supporting reviewed Level A/B evidence exists; candidate/discovery/draft/in-review/rejected/stale semantics remain explicit and auditable
- Broadcom remains `candidate`; `EVD-2026-0001@v1` remains `draft` / `contextualizes`
- Initial independent review found non-functional frozen columns, non-derived human identity, unstructured policy failures, and a universal freshness threshold; the original `changes requested` decision is preserved
- Remediation uses real Serenity `FrozenLayout`, persisted server-trusted `Users.ActorType`, human-reviewed evidence identity checks, stable HTTP 400 policy codes, and category-aware/unknown freshness without entering P4
- Verification after remediation: build has 0 warnings/errors; 51 .NET tests, 10 UI state tests, TypeScript no-emit, frontend build, fresh SQLite/Kestrel HTTP smoke, and fresh Firefox real-page browser smoke pass
- Work log: `operations/work_logs/phase-1-p3.md`
- Independent-review record/history: `operations/reviews/phase-1-p3-independent-review.md`; original `changes requested` preserved and focused decision is `approved with minor findings`
- Remaining Low findings: L-01R (future typed/period freshness semantics and neutral labels) and L-02 (handled ValidationError fail-level logging noise); neither blocks the P3 gate

## Gate

- Project: `serenity_quant_research`
- Goal: deliver a usable CPO research workstation that closes the loop from an interactive physical-part diagram to companies, reviewed evidence, versioned conclusions, and a report
- Source of truth:
  - `AGENTS.md`
  - `docs/project-intake/serenity-quant-research.md`
  - `docs/serenity_finance_research_summary.md`
  - `docs/CPO_3D.jpeg`
  - `docs/CPO_FUll.jpeg`
- Entry points: CPO exploded diagram, industry-chain map, company universe, NVIDIA and company primary-source evidence
- Constraints: finance-first semantics; actual `serenity-is/Serenity` technical base; project-local evidence; no trading features; no chat-only shell; no unreviewed conclusions
- Outputs: interactive CPO diagram, part research flow, company comparison and details, evidence timeline and review, versioned conclusions, print-ready report
- Route: `plan`

## Frozen Product Decisions

1. Use `serenity-is/Serenity` as the implementation base, not only as an architectural metaphor.
2. Use the two JPEG files as seed references and rebuild the product view as original, data-driven SVG layers.
3. Use two-level physical decomposition for the MVP:
   - physical module
   - independently researchable part/component
4. Keep the domain hierarchy recursive so deeper BOM levels can be added later without a schema redesign.
5. Use two-stage part interaction:
   - hover: highlight, identify, summarize function, show company count
   - click: lock selection, open the research drawer, and allow navigation to a full part detail page
6. Use a dual-layer company universe:
   - global industry anchors for demand, technology, ecosystem, and supply-chain context
   - A-share-focused companies for full research coverage, with selected HK/overseas additions only when necessary
7. Use machine-assisted drafts with mandatory human review. Reports may cite only reviewed evidence and published conclusions.

## In Scope

- One theme: optical modules / CPO
- One data-driven CPO exploded diagram
- 9 top-level physical modules seeded from `docs/CPO_3D.jpeg`
- Approximately 15–25 independently researchable part/component nodes
- Approximately 12–20 companies across the two company-universe layers
- Approximately 30–50 reviewed evidence records
- Approximately 5–10 published, versioned research conclusions
- One thematic report template with browser-print/PDF output
- Research home, industry-chain decomposition, company comparison, company detail, evidence timeline, and report output pages
- Source level, publication time, capture time, review state, staleness, and citation back-links

## Out of Scope

- K-lines, market tape, real-time quotes, order books, and technical indicators
- Brokerage or live-account integration
- Trading, order execution, portfolio execution, and position management
- Backtesting and strategy signals
- Full engineering BOM or CAD system
- Rotatable 3D, assembly simulation, and complex WebGL
- Fully automated crawling or real-time news pipelines
- Automatically publishing evidence, conclusions, or reports without review
- DCF/WACC/VaR and broad valuation engines
- Multi-theme production operations and complex organization-wide permissions
- Chat as the only product interface

## Domain Model Boundary

### Research domain objects

- `Theme`
- `IndustryChain`
- `IndustryChainNode`
- `PhysicalModule`
- `PhysicalPart` with recursive parent-child relationships
- `TechnologyLink`
- `Company`
- `CompanyExposure`
- `SourceDocument`
- `Event`
- `Evidence`
- `ResearchConclusion`
- `ResearchReport`

### Required relationship semantics

- A physical part may map to multiple technology links and industry-chain nodes.
- An industry-chain node may map to multiple physical parts.
- `CompanyExposure` records company, related node/part, role, relevance, confidence, and supporting evidence.
- Evidence may support, contradict, or contextualize a proposition.
- A published conclusion must cite reviewed evidence and record confidence, horizon, risks, and invalidation conditions.
- A generated report must lock the versions of cited conclusions and evidence.

### Diagram presentation boundary

SVG geometry is presentation data, not the research domain model. Each interactive SVG group must bind to a stable domain identifier, for example:

```html
<g data-part-id="..."></g>
```

The diagram layer may store path geometry, transform, z-order, labels, and default visual state. Business relationships must remain queryable without parsing SVG markup.

## Initial CPO Taxonomy

The first taxonomy pass starts from these top-level modules in `docs/CPO_3D.jpeg`:

1. top cover / heatsink
2. high-speed switch ASIC
3. Driver / TIA / Retimer electrical-processing layer
4. SiPh PIC / optical engine
5. laser array
6. PD / receive array
7. FAU / fiber array / MPO interface
8. co-packaged substrate / interposer
9. high-speed PCB / gold fingers

Second-level nodes must be independently researchable and company-mappable. The taxonomy is a candidate baseline until technical and primary-source verification is complete.

The industry-chain view starts from the ten areas in `docs/CPO_FUll.jpeg`: demand, ASIC, silicon photonics, light source/laser, optical engine/package, substrate/interconnect, thermal/structure, test/equipment, optical components/connection, and downstream systems/switches.

## Page and Interaction Contract

### Research Home

- Active theme and research coverage
- Recently reviewed evidence and published conclusions
- Stale evidence and uncovered parts/companies
- Direct entry to the CPO diagram, company universe, evidence review, and current report
- No market-tape or trading widgets

### Industry-chain Decomposition

- Default CPO exploded SVG view with a table/tree fallback
- Hover one part to highlight it and dim unrelated layers
- Click to lock selection and open a part research drawer
- Drawer sections: function, boundaries, upstream/downstream, key specifications, technology links, companies, evidence, conclusions, risks, and unresolved questions
- Navigation from the drawer to the full part detail page
- A separate industry-chain perspective linked to, but not conflated with, the physical BOM

### Company Universe and Comparison

- SleekGrid-first high-density comparison
- Filters for physical part, chain node, company role, market, geography, evidence coverage, and freshness
- Frozen identity columns, sorting, comparison, saved filters, and export
- No default ranking by short-term share-price movement

### Company Research Detail

Tabs:

1. Overview
2. Industry-chain Exposure
3. Earnings & Financial Evidence
4. Capex & Investment
5. Events
6. Research Conclusions
7. Sources & Audit

### Evidence / Event Timeline

- Timeline and table views
- Filters by source level, evidence type, company, part, chain node, and technology link
- Separate event time, publication time, and capture time
- Original quotation or video timestamp, source back-link, review status, and analyst annotation
- Action to create or update a conclusion draft

### Report Output

Minimum structure:

1. scope and methodology
2. CPO physical and industry-chain structure
3. key technologies and parts
4. company universe and comparison
5. NVIDIA and industry signals
6. earnings, Capex, and investment evidence
7. current conclusions
8. risks, counter-evidence, and invalidation conditions
9. citation appendix

## Serenity Service Boundary

- `DiagramQueryService`: diagram composition, layer state, and domain bindings
- `PartResearchService`: part details and linked technology/company/evidence queries
- `IndustryChainService`: chain structure and physical-to-industry relationships
- `CompanyUniverseService`: company filtering, comparison, and exposure maintenance
- `EvidenceReviewService`: evidence drafts, review transitions, source metadata, and citations
- `ConclusionService`: conclusion drafts, publication, versions, confidence, and invalidation
- `ReportService`: report composition, citation-version locking, and print output

Authorization and audit should use Serenity conventions. Complex organization-wide role design is deferred; Phase 1 needs only the minimum distinction between maintaining drafts and publishing reviewed research.

## Evidence Contract

### Manual-first MVP

Manually curate and verify:

- physical and industry-chain taxonomy
- company exposure and role
- source level
- original quotation or timestamp
- object associations
- whether evidence supports, contradicts, or only contextualizes a proposition
- conclusion text, confidence, horizon, risks, and invalidation conditions

### Source levels

- Level A: regulatory filings, exchange disclosures, company reports/calls, and NVIDIA official materials
- Level B: company releases, credible industry institutions, and specialist media
- Level C: aggregations, reposts, and social material used only as discovery leads

### NVIDIA signal chain

NVIDIA official event/material → quoted evidence or video timestamp → signal classification → technology/part mapping → company-exposure mapping → cross-check against earnings/Capex/investment evidence → reviewed conclusion → report.

An NVIDIA statement is evidence or an event; it is not automatically a conclusion about a listed company.

## Execution Backlog

### P0 — Research and implementation baseline

- Verify provenance and permitted use of both JPEG seed references.
- Produce a reviewed two-level CPO taxonomy and glossary.
- Produce the initial global-anchor and A-share-focused company lists.
- Define minimum review states and citation rules.
- Select and lock the supported Serenity project template/version during bootstrap.

Exit: taxonomy, company seed, evidence states, and technical bootstrap choice are reviewable and no longer implicit.

### P1 — Serenity bootstrap and core objects

- Create the minimal Serenity application structure.
- Implement core domain objects and relationships.
- Add audit fields, review states, and seed import support.
- Seed one complete part-to-company-to-evidence example.

Exit: domain relationships are queryable and one complete chain works without the diagram.

### P2 — Interactive SVG and part research

- Create original SVG groups for the top-level modules and second-level parts.
- Bind each group to a stable `part_id`.
- Implement hover, selection, dimming, drawer, tree/table fallback, and part detail navigation.
- Verify keyboard focus and non-pointer access for core selection behavior.

Exit: every seeded part can be selected visually and resolved to its research object.

### P3 — Company universe and detail

- Implement SleekGrid comparison and filters.
- Implement company exposure editing and confidence/source display.
- Implement company detail tabs and cross-navigation.

Exit: a user can move from a part to relevant companies and compare their roles and evidence coverage.

### P4 — Evidence review and timeline

- Implement evidence draft creation and review transitions.
- Implement source levels, citations, snapshots/content fingerprints, and timeline filtering.
- Implement support/contradict/context relationships.
- Add staleness and missing-source indicators.

Exit: reviewed evidence is independently searchable and reachable from parts, companies, events, and conclusions.

### P5 — Conclusions and report

- Implement conclusion drafts, publication, versioning, confidence, risks, and invalidation conditions.
- Implement the thematic report structure and locked citations.
- Implement print-friendly HTML and browser PDF output.

Exit: the project can produce one CPO report in which each material conclusion is traceable to reviewed evidence.

### P6 — MVP validation

Run at least these scenarios:

1. Select a physical part from the SVG and reach its company set.
2. Compare at least three companies with different roles in the same chain area.
3. Ingest and review one NVIDIA official signal.
4. Link one earnings, one Capex, and one investment/partnership record.
5. Publish a conclusion with supporting and contradicting evidence.
6. Generate a report and resolve every citation back to a reviewed source.

Exit: all six scenarios pass with no trading feature required and no unreviewed material appearing in the report.

## Browser Capability Boundary

Browser-assisted evidence capture is deferred and does not block the core MVP. Reconsider it only after the manual evidence contract is validated.

A future browser tool may capture a user-opened rendered page, metadata, selected quotation, screenshot/PDF, and content fingerprint into an evidence draft. It must not promise anti-bot bypass, publish research automatically, or commit cookies/browser profiles. Under the current `AGENTS.md` boundary, heavy browser runtime logic must not be placed in `.pi/`; prefer a trusted external/global integration, separate package, and machine-local configuration.

## Risks and Controls

| Risk | Control |
|---|---|
| JPEG cannot supply true layers | Rebuild original SVG groups manually; keep JPEG only as a reference |
| Diagram/company claims may be wrong | Treat all mappings as candidates until primary-source verification |
| Artwork rights are unclear | Do not ship copied artwork; confirm provenance and redraw original assets |
| Physical BOM and industry chain become conflated | Preserve separate objects and explicit many-to-many mappings |
| Scope drifts into a market terminal | Keep trading/market features explicitly out and validate IA language |
| Automated evidence creates unsupported conclusions | Require human review and restrict reports to reviewed/published objects |
| Browser integration expands the runtime boundary | Defer it and keep heavy integration outside `.pi/` |
| Research summary contains non-portable links | Recover or replace source files before treating those links as durable evidence |

## Validation Level

Before implementation closeout:

- automated tests for domain relationships, review transitions, and version locking
- service-level tests for part/company/evidence cross-navigation
- UI tests for SVG hover/click/keyboard behavior and grid filtering
- fixture-driven report citation checks
- manual research walkthrough using the six P6 scenarios

## Portability

- Use repository-relative paths in configuration and documentation.
- Keep credentials, browser profiles, cookies, and machine-specific overrides untracked.
- Do not rely on `computer:///workspace/.uploads/...` links at runtime.
- Keep business implementation outside `.pi/`; `.pi/` remains the minimal governance entry.

## Runtime Access Override — 2026-08-25

- By explicit operator decision, `OpenAccess:Enabled` now defaults to `true`; interactive login is bypassed and every request is mapped server-side to the persisted admin user (ID 1)
- This opens all research write/review endpoints and Administration pages, not only read-only research views
- Existing Serenity permission attributes and human/machine policy code remain in place for protected-mode tests and future restoration, but runtime access isolation is currently the deployment boundary
- All open-mode audit writes are attributed to admin; the application cannot distinguish individual visitors while this override is enabled
- This is intentionally insecure outside a trusted isolated local environment; set `OpenAccess:Enabled` to `false` to restore cookie login and normal permission enforcement
- P4/P5/P6 were not started by this access-mode change
- Work log: `operations/work_logs/open-access-mode.md`

## Next Step

P3 is complete and independently reviewed (`approved with minor findings`). P3 no longer blocks a separately authorized P4 round, but P4 remains unstarted in this session. Preserve L-01R/L-02 as bounded follow-up context and do not retroactively expand P3 or begin P4 without separate authorization.
