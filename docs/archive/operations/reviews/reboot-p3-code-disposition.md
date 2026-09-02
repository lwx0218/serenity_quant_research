# Research Experience Reboot — P0–P3 Code / Domain Disposition Audit

## Status

- Round: `R1`
- Session: `R1-code-disposition-audit`
- Audit time: 2026-08-28 UTC
- Git baseline: `7cf1b95d23a5da3dd53766049557a67ed18fae73`
- Decision: **ready for Product Owner disposition review after scope-bounded review/fallback; not accepted-effective**
- Write boundary: R1 product-audit durable evidence only; no application, schema, migration, seed, runtime-config, or test change
- Review scope rule: `.pi/extensions/harness-flow`、starter update、docs references 整理属于 governance/context/environment，不属于本审计的 product-audit candidate
- Product authority: `docs/product/README.md`, `docs/product/experience-map.md`, the three page specs/prototypes, `docs/product/visual-language.md`, and `docs/product/acceptance-contract.md`
- Research/evidence authority: `docs/research-baseline/evidence-contract.md`, `docs/research-baseline/cpo-taxonomy.md`, and `docs/research-baseline/company-universe.md`

## Executive Finding / 执行结论

P0–P3 可作为工程基础复用，但不能作为 Research Experience Reboot 的产品呈现继续沿用。

- **KEEP:** stable IDs, rows/relationships, migrations, seed safety, evidence/exposure/publication policy、权限/审计、符合合同的 service internals、request-race helper 和 backend policy tests；不代表所有 endpoints 原样保留。
- **ADAPT:** root/shell routing、research navigation、page controllers、part/company aggregation services 与相关 endpoints/generated contracts、需要可信 actor-type 校验的 `EvidenceWorkflowEndpoint`、stable URL context、selection state 和 service/endpoint tests。
- **REPLACE:** the legacy admin-framed 3×3 Explorer presentation and the SleekGrid/comparison/seven-tab Company presentation.
- **HIDE:** the Serenity sidebar/admin navigation, chain-node maintenance-style page, and legacy standalone part-detail path from the primary research journey while retaining secondary routes until replacement is proven.
- **DELETE LATER:** only the demo Dashboard view/model and any later proven-unreferenced legacy research-facing frontend. No deletion is authorized before R7 reference proof.

No large frontend/backend replacement is necessary. Existing Razor/TypeScript/CSS and Serenity service/data infrastructure can support the reboot.

## Disposition Vocabulary

| Disposition | Meaning in this audit |
|---|---|
| `KEEP` | Preserve behavior and contract; ordinary maintenance or generated refresh does not change the disposition. |
| `ADAPT` | Preserve the stable route/domain/service responsibility but change its projection, query, state, or shell integration. |
| `REPLACE` | Current research-facing IA/interaction/presentation is superseded; implement the approved behavior at the same bounded product surface. |
| `HIDE` | Retain as secondary/admin-compatible capability, but remove it from primary research navigation/journey. |
| `DELETE LATER` | Candidate only after accepted replacement plus no-reference proof in R7; not authorized for deletion now. |

## Disposition Profiles

The file manifest below is file-level. This profile table supplies the required reason, dependency, governing contract, migration risk, and backend reuse finding without duplicating identical text on every row.

| Profile | Disposition | Reason / dependency | Governing contract | Migration risk | Backend reuse finding |
|---|---|---|---|---|---|
| `SH-ADAPT` | ADAPT | Current shared layout/root/navigation is admin-sidebar-first. Depends on R2 shell and secondary admin-route reachability. | Product README §§3–5; experience map §3; visual language §§2,14 | None | Keep Serenity host, navigation discovery, auth, antiforgery, bundles, and admin routes. |
| `SH-HIDE` | HIDE | Admin/sidebar/language controls must not be primary research navigation. Depends on the R2 research shell. | Product README §§2–5; acceptance contract §4 | None | Keep secondary maintenance capability and permissions. |
| `SH-DELETE` | DELETE LATER | Demo dashboard content has no research purpose. Delete only after root replacement and reference proof. | Product README §2; R7 cleanup boundary | None | No research backend value; controller route may first be adapted for root handoff. |
| `ROUTE-ADAPT` | ADAPT | Stable URLs/controllers remain useful, but must carry recoverable source context and render the reboot shell. | Experience map §§3–4; page specs | None | Keep PageAuthorize, stable IDs, MVC routing, and existing service URLs. |
| `UI-REPLACE-CPO` | REPLACE | Legacy generated 3×3 diagram is neither Flat/3D nor component↔callout interaction and lacks same-object/blank/view-switch semantics. | CPO spec §§2–19; acceptance contract §6 | None | Reuse stable IDs, service calls, keyboard/request helpers, and safe gap language. |
| `STATE-ADAPT-CPO` | ADAPT | Existing stable-ID hover/selection foundation is useful; add same-object toggle, Flat/3D shared state, blank reset, callout equivalence, and context state. | CPO spec §§3–11,17–19 | None | Reuse pure state/helper pattern and retry/latest-request guard. |
| `UI-REPLACE-CO` | REPLACE | SleekGrid-first, built-in comparison, dense filters, and seven-tab detail conflict with Card/List → Quick Drawer → continuous/light detail. | Company spec §§2–9,13–14; acceptance contract §7 | None | Reuse service DTOs, stable links, safe labels, explicit gaps, and policy-error handling. |
| `ROUTE-HIDE` | HIDE | Route may remain secondary for compatibility, but it is not an approved primary destination. | Experience map §§2–3; no-silent-scope contract | None | Retain stable cross-link resolution until R7 proves it unnecessary. |
| `SVC-ADAPT-PART` | ADAPT | Current exact-part query is safe but does not aggregate module children/descendants or derived technology/material→company paths. | CPO spec §§12–15; Workspace spec §§5–8 | None for derived v1 path | Reuse rows, exact exposure/evidence semantics, stable IDs, and safe gaps. |
| `SVC-ADAPT-CO` | ADAPT | Existing aggregation/policy is strong; simplify product DTO/query for Card/List/drawer/detail and preserve URL research context. | Company spec §§3–12; evidence contract | None | Reuse filters selectively, exposure/evidence aggregation, policy/audit, stable routes. |
| `ENDPOINT-ADAPT-IDENTITY` | ADAPT | 当前 Evidence workflow endpoint 把任何拥有 `Research:Review` 权限的 principal 硬编码为 human reviewer，无法阻止机器身份执行 review。必须接入可信 actor type 判断并增加端点身份测试，之后才能依赖该写端点。 | Evidence contract §3：禁止机器身份执行 review；acceptance contract §5 | 无 schema 迁移；属于身份校验与端点策略修复 | 复用 `UserRow.ActorType`、`UserActorTypes`、`UserSaveHandler` validation、`EvidenceWorkflowService` 的显式 human flag 与 domain policy；不能复用 endpoint 当前的常量 `true`。 |
| `ACTOR-IDENTITY-KEEP` | KEEP | `UserRow.ActorType`、`UserActorTypes.Human/Machine` 和 User save validation 已提供可信持久身份分类；Evidence endpoint 应复用 Company exposure endpoint 的查询模式。 | Evidence contract §3；P3 actor-type migration | 受保护，无新 migration | 完整复用 actor field/constants/validation；R7 只适配 Evidence endpoint caller。 |
| `BACKEND-KEEP` | KEEP | Stable domain/evidence/audit capability remains authoritative. | Acceptance contract §§5,14; evidence contract | Protected: changing it would trigger rebaseline | Full reuse. |
| `SEED-KEEP` | KEEP | Existing candidate/draft facts and IDs are protected; prototype mock claims cannot enter data. | Acceptance contract §5; evidence contract §§1–10 | Protected | Reuse counts/IDs and explicit gaps; do not infer missing relationships. |
| `GEN-ADAPT` | ADAPT | Generated service/DTO output must follow later C# contract adaptation; never hand-edit. | Plan architecture decision; generated-contract practice | None | Regenerate from retained endpoints/services. |
| `GEN-KEEP` | KEEP | Generated row/policy/publication contracts reflect retained backend. Regenerate only as a build artifact. | Evidence contract; engineering preservation | Protected through source rows | Retain. |
| `TEST-ADAPT` | ADAPT | Preserve current regression intent, but align assertions to reboot interactions and new read-only projections. | Acceptance contract §§6–11; Round validations | None | Reuse fixtures, temporary SQLite/Kestrel/Firefox harness, and policy checks. |
| `TEST-KEEP` | KEEP | Contract/policy/bootstrap tests remain valid and guard protected semantics. | Evidence contract; acceptance contract §§5,14 | None | Full reuse. |

## File-Level Disposition Matrix

### A. Host, Shell, Root, And Navigation

| File | Disposition | Profile | Dependency / note |
|---|---|---|---|
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Initialization/Program.cs` | KEEP | BACKEND-KEEP | Host bootstrap remains. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Initialization/Startup.cs` | ADAPT | SH-ADAPT | Keep registrations/Open Access behavior; later register read-only Workspace aggregation only. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/SerenityQuantResearch.Web.csproj` | KEEP | BACKEND-KEEP | Existing Razor/TS build and relative seed link remain. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Navigation/NavigationModel.cs` | KEEP | BACKEND-KEEP | Reusable Serenity navigation model. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Navigation/NavigationModelFactory.cs` | ADAPT | SH-ADAPT | May need research/admin shell filtering; preserve permission-aware discovery. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Navigation/NavigationItems.cs` | ADAPT | SH-ADAPT | Remove Dashboard from primary research navigation after root reroute. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/ResearchNavigation.cs` | REPLACE | SH-ADAPT | Emit exactly Explorer, Company Pool, Workspace for primary research navigation. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Administration/AdministrationNavigation.cs` | HIDE | SH-HIDE | Keep routes, hide from primary research shell. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPage.cs` | ADAPT | SH-ADAPT | R2 reroutes root to research experience; secondary dashboard route need not define product. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardIndex.cshtml` | DELETE LATER | SH-DELETE | Demo orders/traffic/calendar UI; delete only after R2 replacement and R7 proof. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPageModel.cs` | DELETE LATER | SH-DELETE | Demo-only metrics model; same gate as DashboardIndex. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_Layout.cshtml` | ADAPT | SH-ADAPT | Select/host a lightweight research shell without breaking admin pages. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_LayoutHead.cshtml` | ADAPT | SH-ADAPT | Preserve bundles/CSP/CSRF; avoid research-facing language/admin chrome. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_LayoutNoNavigation.cshtml` | KEEP | BACKEND-KEEP | Useful non-navigation infrastructure layout. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_Sidebar.cshtml` | HIDE | SH-HIDE | Keep for secondary admin routes, not research pages. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/wwwroot/Content/site/site.css` | ADAPT | SH-ADAPT | Shared research-shell tokens/base styling; do not let template styles define product. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/ScriptInit.ts` | ADAPT | SH-ADAPT | Preserve framework initialization; research shell must not depend on permanent sidebar behavior. |

### B. CPO Explorer And Part Routes

| File | Disposition | Profile | Dependency / note |
|---|---|---|---|
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoResearchPage.cs` | ADAPT | ROUTE-ADAPT | Keep `/Research/Cpo`; add reboot shell/context behavior. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramIndex.cshtml` | REPLACE | UI-REPLACE-CPO | New Flat/3D canvas, callouts, hidden-until-selection drawer. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts` | REPLACE | UI-REPLACE-CPO | Preserve safe service wiring patterns, not legacy 3×3 rendering. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.css` | REPLACE | UI-REPLACE-CPO | Current dark/neon/admin-card direction is superseded. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/PartSelectionState.ts` | ADAPT | STATE-ADAPT-CPO | Stable-ID pure state is reusable but incomplete for approved interactions. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/ResearchRequestState.ts` | KEEP | BACKEND-KEEP | Latest-request and retryable-cache behavior remains useful. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/PartDetail.cshtml` | HIDE | ROUTE-HIDE | Keep stable route as secondary compatibility until Explorer/Workspace replacement is proven. |

### C. Company Pool, Drawer, Detail, And Chain Route

| File | Disposition | Profile | Dependency / note |
|---|---|---|---|
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyResearchPage.cs` | ADAPT | ROUTE-ADAPT | Keep universe/detail stable URLs; carry Explorer source context. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniverse.cshtml` | REPLACE | UI-REPLACE-CO | Card View becomes default; List is equivalent compact mode. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniversePage.ts` | REPLACE | UI-REPLACE-CO | Remove default SleekGrid/comparison/seven-tab flow; preserve safe DTO/policy handling. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniversePage.css` | REPLACE | UI-REPLACE-CO | Rebuild to visual language and contextual drawer hierarchy. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyUniverseState.ts` | REPLACE | UI-REPLACE-CO | Current comparison and seven-tab state are explicitly deferred/superseded. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/CompanyDetail.cshtml` | ADAPT | ROUTE-ADAPT | Retain route scaffold; render continuous/lightly segmented entity detail and Workspace link. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/ChainNodeDetail.cshtml` | HIDE | ROUTE-HIDE | Secondary stable cross-navigation, not a primary product page. |

### D. Services, Endpoints, Domain, Entities, Permissions, And Seed Source

| File | Disposition | Profile | Dependency / note |
|---|---|---|---|
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Services/PartResearchService.cs` | ADAPT | SVC-ADAPT-PART | Add explicit child/derived relationship projection; preserve exact evidence states. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Endpoints/PartResearchEndpoint.cs` | ADAPT | SVC-ADAPT-PART | Keep endpoint; DTO actions may expand read-only. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Services/CompanyUniverseService.cs` | ADAPT | SVC-ADAPT-CO | Reuse aggregation/policy; expose lightweight browse/drawer/detail/context projection. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Endpoints/CompanyUniverseEndpoint.cs` | ADAPT | SVC-ADAPT-CO | Keep read routes and audited exposure endpoint; research v1 UI need not expose editing. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Services/EvidenceWorkflowService.cs` | KEEP | BACKEND-KEEP | 保留显式 `actorIsHumanReviewer` 输入与 domain policy 检查；当前 reboot 不提供写入 UI。 |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Endpoints/EvidenceWorkflowEndpoint.cs` | ADAPT | ENDPOINT-ADAPT-IDENTITY | 当前将所有 `Research:Review` principal 作为 human reviewer 传入；在可信 actor-type 校验和机器身份拒绝测试完成前，不得视为符合 evidence contract，也不得暴露给研究主流程。 |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Domain/ResearchWorkflowPolicy.cs` | KEEP | BACKEND-KEEP | Candidate/review/publication semantics remain authoritative. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Entities/ResearchStructureRows.cs` | KEEP | BACKEND-KEEP | Stable Theme/chain/module/recursive-part/technology model. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Entities/ResearchLinkRows.cs` | KEEP | BACKEND-KEEP | Stable part↔technology, part↔chain, and evidence locking links. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Entities/ResearchEvidenceRows.cs` | KEEP | BACKEND-KEEP | Stable company/exposure/source/event/evidence model. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Entities/ResearchPublicationRows.cs` | KEEP | BACKEND-KEEP | Preserve long-term conclusion/report model; no current product UI. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/ResearchPermissionKeys.cs` | KEEP | BACKEND-KEEP | Preserve General/Review/Publish boundary. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Seed/ResearchSeedContracts.cs` | KEEP | SEED-KEEP | Existing import contract supports parent parts and technology links. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Seed/ResearchSeedImporter.cs` | KEEP | SEED-KEEP | Preserve idempotence/audit and candidate/draft state. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Seed/ResearchSeedValidator.cs` | KEEP | SEED-KEEP | Preserve reference/cycle/source/review safeguards. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Administration/User/UserActorTypes.cs` | KEEP | ACTOR-IDENTITY-KEEP | Human/machine 常量是 endpoint 强制身份边界的事实源。 |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Administration/User/UserRow.cs` | KEEP | ACTOR-IDENTITY-KEEP | `ActorType` 持久字段可由 endpoint 按 authenticated user ID 查询。 |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Administration/User/RequestHandlers/UserSaveHandler.cs` | KEEP | ACTOR-IDENTITY-KEEP | 保留 actor type allowlist validation 和 create-time human default。 |
| `data/seeds/cpo/cpo-research-seed.json` | KEEP | SEED-KEEP | Untracked pre-existing data at R1 start; no R1 write and no prototype-derived enrichment. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations/DefaultDB/DefaultDB_20260824_1000_ResearchDomain.cs` | KEEP | BACKEND-KEEP | Protected stable schema; no migration need found for derived v1 path. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Migrations/DefaultDB/DefaultDB_20260825_1000_P3ResearchActorType.cs` | KEEP | BACKEND-KEEP | Human/machine audit identity remains required for protected writes. |

### E. Generated Research ServerTypes

These files are generated dependencies, not hand-edit surfaces.

#### `GEN-ADAPT` — regenerate after later Part/Company service DTO adaptation

| File | Disposition | Profile |
|---|---|---|
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/PartResearchService.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/CompanyUniverseService.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/CompanyExposureService.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.PartCatalogResponse.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.PartResearchRequest.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.PartResearchResponse.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.ResearchModuleSummary.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.ResearchPartSummary.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.ResearchNamedLink.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.ResearchSectionSummary.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyExposureSummary.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyUniverseRequest.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyUniverseResponse.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyUniverseItem.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyResearchRequest.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyResearchResponse.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyExposureDetail.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyExposureUpdateRequest.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyFilterOptions.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.ChainNodeResearchRequest.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.ChainNodeResearchResponse.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyEvidenceSummary.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyEventSummary.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.CompanyConclusionSummary.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.EvidenceSummary.ts` | ADAPT | GEN-ADAPT |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research.ts` | ADAPT | GEN-ADAPT |

#### `GEN-KEEP` — retained generated backend contracts

| File | Disposition | Profile |
|---|---|---|
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/CompanyExposureEvidenceRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/CompanyExposureRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/CompanyRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/ConclusionEvidenceRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/EventRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/EvidenceRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/EvidenceWorkflowService.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/IndustryChainNodeRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/IndustryChainRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/PhysicalModuleRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/PhysicalPartIndustryChainNodeRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/PhysicalPartRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/PhysicalPartTechnologyLinkRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/ReportConclusionRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/ReportEvidenceRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/ResearchConclusionRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/ResearchReportRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/Services.EvidenceTransitionRequest.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/SourceDocumentRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/TechnologyLinkRow.ts` | KEEP | GEN-KEEP |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/ServerTypes/Research/ThemeRow.ts` | KEEP | GEN-KEEP |

`wwwroot/esm/**` and `Imports/MVC/*.cs` are generated build output rather than authored product source. They must be regenerated/verified by later Round builds, never independently redesigned.

### F. Tests And Validation Harness

| File | Disposition | Profile | Dependency / note |
|---|---|---|---|
| `tests/SerenityQuantResearch.Tests/PartResearchServiceTests.cs` | ADAPT | TEST-ADAPT | Add module-child/derived technology-company and safe-empty assertions. |
| `tests/SerenityQuantResearch.Tests/CompanyUniverseServiceTests.cs` | ADAPT | TEST-ADAPT | Preserve relationship/policy coverage; adapt browse/drawer/context projection tests. |
| `tests/SerenityQuantResearch.Tests/CompanyExposureEndpointPolicyTests.cs` | KEEP | TEST-KEEP | Protect human-only verification and rollback；其 `UserRow.ActorType` fixture/pattern 应复用于 R7 Evidence endpoint 的 human-success / machine-rejection 测试。 |
| `tests/SerenityQuantResearch.Tests/ResearchWorkflowPolicyTests.cs` | KEEP | TEST-KEEP | Protect evidence/exposure/publication semantics. |
| `tests/SerenityQuantResearch.Tests/ResearchSeedValidatorTests.cs` | KEEP | TEST-KEEP | Protect counts, hierarchy safety, and machine-draft rule. |
| `tests/SerenityQuantResearch.Tests/ResearchBootstrapIntegrationTests.cs` | ADAPT | TEST-ADAPT | Preserve migration/seed/idempotence; root expectation changes in R2. |
| `tests/SerenityQuantResearch.Tests/OpenAccessIntegrationTests.cs` | ADAPT | TEST-ADAPT | Preserve trusted-isolation behavior; add read-only Workspace/no-writing checks later. Evidence endpoint 修复时还必须新增或扩展 endpoint-level 测试，证明 machine principal 即使拥有 `Research:Review` 也不能完成 review transition。 |
| `tests/SerenityQuantResearch.Tests/TestAssembly.cs` | KEEP | TEST-KEEP | Serial temporary-database tests remain appropriate. |
| `tests/SerenityQuantResearch.Tests/SerenityQuantResearch.Tests.csproj` | KEEP | TEST-KEEP | Existing fixture and relative seed link remain. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs` | ADAPT | TEST-ADAPT | Assert shared Flat/3D, callout, same-object, blank, Esc, and keyboard behavior. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/CompanyUniverseState.test.mjs` | REPLACE | TEST-ADAPT | Comparison/seven-tab assertions are obsolete; add Card/List/drawer/context state. |
| `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh` | REPLACE | TEST-ADAPT | Preserve fresh SQLite/Kestrel/Firefox harness; replace legacy product assertions Round by Round. |

## Child / Material → Company Capability Finding

### Observed Persistent Capability

1. **Module → child part:** `PhysicalModuleRow` owns many `PhysicalPartRow` records. The CPO seed has 9 modules and 21 stable-ID parts. This already supports treating a product-level Explorer component such as `cpo.mod.pic` as the parent presentation object and its three stable parts (`modulator`, `wdm`, `waveguide-coupler`) as drill-down children.
2. **Recursive part hierarchy:** `PhysicalPartRow.ParentPartId` and the migration foreign key support deeper parent/child parts. Seed/import/validator code supports and cycle-checks `parentPartId`.
3. **Part → technology/material context:** `PhysicalPartTechnologyLinkRow` provides an explicit many-to-many part→`TechnologyLinkRow` path.
4. **Part/chain → company:** `CompanyExposureRow` can explicitly point to a `PhysicalPartId` and/or `IndustryChainNodeId`; exposure state, scope, evidence, and audit semantics are preserved.
5. **Derived read path:** without inventing a direct relationship, a read model can derive `TechnologyLink ← PhysicalPartTechnologyLink → PhysicalPart ← CompanyExposure → Company`. A module child can use its exact `PhysicalPartId` exposure. A chain-node aggregation already exists but is broader and must not be presented as a material-specific supplier claim.

### Observed Materialized Data

Read-only inspection of `data/seeds/cpo/cpo-research-seed.json` found:

```text
modules=9
parts=21
parent_links=0
technology_links=4
part_technology_links=10
chain_nodes=10
part_chain_links=21
companies=20
seeded_company_exposures=1
```

The four technology records are broad technology contexts (`high-speed-switching`, `silicon-photonics`, `external-laser`, `thermal-management`), not a reviewed discrete material catalog. All 21 parts currently have no `ParentPartId`; their practical parent is their module. The sole exposure is `global.broadcom` → `cpo.part.host-asic.switch-die`, `candidate`, with `draft` contextual evidence. No current SiPh child or material has a company exposure.

### Current Service Gap

- `PartResearchService.RetrieveCompleteChain` resolves one exact part and queries exact-part chain links, technologies, exposures, and evidence.
- It does **not** return a module's children, recursive descendants, parent/child breadcrumbs, reverse technology→parts, or derived technology/material→companies.
- `CompanyUniverseService` filters exposures by exact part or chain node. It does not retrieve by `TechnologyLink` and correctly refuses name/category inference.
- No current DTO distinguishes `material` from a broader `technology` record.

### Query / Service Adaptation Need

A schema-preserving read projection can satisfy the approved v1 relationship semantics if it:

1. resolves a selected module/component to its stable child `PhysicalPart` records (and recursive descendants when populated);
2. loads each child's explicit technology links;
3. loads companies only through explicit `CompanyExposure.PhysicalPartId`, or derives a technology/material company set through explicitly linked parts that themselves have explicit exposures;
4. returns the relationship path and verification/evidence state so the UI can explain why a company appears;
5. deduplicates companies without upgrading `discovery`/`candidate` to `verified`;
6. returns `Unknown`, `Not reviewed`, an explicit gap, or omission when no relationship exists.

Likely adaptation surfaces are `PartResearchService.cs`, `CompanyUniverseService.cs`, their endpoints/DTOs/generated ServerTypes, and focused service tests. No large architecture replacement is indicated.

### Schema-Change Finding

- **Required for approved read-only v1 derived relationships:** **No.** Existing module/part, recursive parent, part↔technology, part↔chain, and part/chain↔company-exposure relationships are sufficient for a provenance-preserving derived query.
- **Required to display reviewed discrete materials with current data:** **No migration is proven necessary, but authoritative data is absent.** A material can only be shown if an approved/reviewed record is represented through the existing generic `TechnologyLink` path or omitted. R1 does not authorize adding such records.
- **Would require rebaseline:** a demand for a direct material↔company edge, stored backlink, semantic material subtype that cannot safely use `TechnologyLink`, new persistent note/question/graph entity, or changed exposure/evidence semantics.

This finding does not itself trigger the R1 blocked/rebaseline condition. It does constrain R3: do not render prototype material chips or company claims unless existing authoritative links support them.

## Backend Reuse By Reboot Area

| Reboot area | Reusable base | Required adaptation | Must not drive product |
|---|---|---|---|
| R2 Research Shell | MVC host, bundles, auth, navigation discovery, admin routes | research layout/root/nav filtering | default Dashboard/sidebar/language/admin IA |
| R3–R4 Explorer | stable module/part IDs, PartResearch endpoint/service, request guards, safe states | Flat/3D state, geometry/callouts, module-child aggregation, context handoff | legacy 3×3 boxes, broad hit areas, prototype claims |
| R5 Company | Company routes/service, stable IDs, exposures/evidence/audit/policy, safe labels | Card/List projections, Quick Drawer, context-preserving continuous detail | SleekGrid-first, comparison, seven default tabs, inline editing as primary UX |
| R6 Workspace | parts/technology/company/evidence/relationships and read-only gaps | new read-only aggregation/projection and routes | ResearchNote/OpenQuestion/Backlink/Graph/editor persistence |
| R7 Cleanup | reference scans and full regression harness | delete only proven-dead frontend | migrations, domain/history, services, policy, admin backend |

## Migration / Replacement Sequence

1. **R2:** adapt root/layout/navigation; hide admin sidebar/navigation from research shell; keep secondary admin routes. Do not delete Dashboard files yet.
2. **R3:** adapt stable selection/request/service projection for one SiPh vertical slice; replace only the Explorer presentation needed by the slice.
3. **R4:** scale the accepted Explorer behavior to all stable module/part IDs; continue safe derived queries only.
4. **R5:** replace Company universe/state/CSS with Card/List → Quick Drawer → Full Detail; keep policy/service contracts and stable routes.
5. **R6:** add a read-only Workspace projection over existing entities/relationships; no schema or writing endpoint.
6. **R7:** 先修复 `EvidenceWorkflowEndpoint` 的可信 human/machine actor-type 判断并增加 endpoint-level 拒绝/成功测试，再执行 end-to-end/reference proof；仅删除无引用的 demo Dashboard 和 legacy research-facing frontend。其他 hidden backend/admin routes 与 historical evidence 保留。

## Risks And Control Gates

| Risk | Finding / control |
|---|---|
| Missing materials/company coverage | Data-readiness gap, not permission to infer. Omit or show explicit neutral state. |
| Legacy UI tests resist product reboot | Replace product assertions while preserving backend/policy regression. |
| Generated contract drift | Change C# source first, regenerate, and verify no unexplained output. |
| Admin capability accidentally deleted | R2 hides from primary research shell; R7 deletion proof excludes admin backend. |
| Existing Open Access writes exposed | Keep trusted-isolation warning; Workspace v1 adds no writing. |
| 机器身份被误判为 human reviewer | `EvidenceWorkflowEndpoint` 当前硬编码 `actorIsHumanReviewer: true`，分类为 ADAPT；修复可信 actor type 判断并补齐 endpoint-level machine-principal 拒绝测试前，不得依赖或暴露该写端点。 |
| Company exposure semantics weakened | KEEP policies/entities/tests; new UI is read-only unless a separately authorized maintenance path is used. |
| Prototype defects copied | Production must repair hit ownership, keyboard, overlap, mock state, and research-data safety. |

## Coverage Proof Method

The audit classified:

- all 30 tracked authored files under `Modules/Research/`;
- all 47 tracked generated Research ServerType files (including `Research.ts`);
- relevant root/layout/navigation/dashboard/startup/build surfaces;
- trusted actor identity dependencies：`UserRow`、`UserActorTypes`、`UserSaveHandler`；
- both research migrations and the seed source;
- all 12 tracked .NET/UI research test and harness files.

Inventory was obtained with `find`, `git ls-files`, and `rg` over routes, services, entities, stable relationship fields, generated imports, and tests. Ignored runtime/build trees (`node_modules`, `bin`, `obj`, generated `wwwroot/esm`) were not treated as authored product source.

## R1 Acceptance Recommendation

**Recommend Product Owner approval of this disposition map, subject to Independent Review.**

R1 has not changed production code and has not started R2. R1 is not accepted-effective until Independent Review, P2 dispositions, Owner acceptance, an explicitly authorized acceptance commit, and post-commit verification.
