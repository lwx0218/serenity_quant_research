# Research Experience Reboot — Canonical Fixed-Round Plan

Plan approval: approved
Git baseline: 7cf1b95d23a5da3dd53766049557a67ed18fae73
Accepted-effective Rounds: R1, R2, R3
Active Round: none — R4 requires separate Owner start decision
Branch: product-reboot
Approval authority: Owner structured approval after complete Plan Preview
Approval scope: persist this baseline and hand off R1; no implementation, commit, push, or automatic multi-Round progression

## Metadata

- Route: `fixed-round-plan`
- Product state: Research Experience Reboot
- Legacy engineering state: P0–P3 implemented and reviewed
- Current delivery boundary: CPO Explorer → Company Pool / Company Detail → read-only Research Workspace
- Long-term product loop: Physical Product / Explorer → Component / Material / Technology → Company → Research Workspace → Evidence → Review → Conclusion → Report
- Canonical Plan: `operations/planning/research-experience-reboot.md`
- Canonical orchestration: `operations/orchestration/research-experience-reboot.md`
- Independent Review / Round scope standard: `operations/orchestration/independent-review-and-round-scope-standard.md`
- Final integrated review: `operations/reviews/research-experience-reboot-final-integrated-review.md`

本 Plan 的 machine-readable metadata、Round ledger 与字段标签保留英文，以兼容 handoff/review 工具解析；正文、目标、边界和状态说明使用中文。Round ID 从 R1 开始，因为 project-local handoff/review validator 接受 `R[1-9][0-9]*` 形式。早期 fractional audit 已规范化为 R1；这是编号规范化，不新增或删除已批准交付边界。

## Goal

用连续的投研工作流替代 framework/admin/grid-first 的 research-facing experience，同时尽量保留 P0–P3 已稳定的 domain、service、evidence、audit、permission、migration、seed 与 test 资产。

当前 reboot 交付：

```text
CPO Explorer
→ Component / Material / Technology
→ Company Pool
→ Quick Drawer
→ Full Company Detail
→ Read-only Research Workspace
```

本 Plan 不取消长期 Evidence → Review → Conclusion → Report 闭环，但该闭环不属于当前验收范围。

## Authority And Mandatory Read Order

Governance authority:

1. root `AGENTS.md`
2. `operations/orchestration/independent-review-and-round-scope-standard.md`
3. scoped `src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md`
4. this approved Plan and active Round evidence

Research-facing product authority:

1. `docs/product/README.md`
2. `docs/product/experience-map.md`
3. task-specific product spec
4. approved/directional prototype
5. `docs/product/visual-language.md`
6. `docs/product/acceptance-contract.md`
7. this Plan
8. `operations/orchestration/research-experience-reboot.md`
9. current implementation
10. legacy P0–P3 product plans and logs

研究事实、evidence state、review transitions、publication rules 与 audit semantics 仍由 `docs/research-baseline/evidence-contract.md` 和已评审 repository evidence 管理。Prototype content 绝不覆盖这些合同。

## Architecture And Ownership Decisions

- Serenity/.NET/SQLite 继续作为 application host，负责 services、data、permissions、audit、migrations 与 admin maintenance。
- Serenity defaults 不定义 research-facing navigation、IA、interaction 或 visual design。
- 使用既有 Razor/TypeScript/CSS architecture；不新增大型 frontend framework。
- Stable server-side domain IDs 与 relationships 是权威。URL/query context 承载可恢复研究上下文；hover/drawer 等临时状态保留在 client side。
- Workspace v1 是 read-only，并从既有 objects/relationships 派生；不新增 ResearchNote、OpenQuestion、Backlink、Graph 或 editing persistence。
- R1 只判断 child/material → related company 是否可由 query/service adaptation 支持。若需要 persistent schema change，必须 rebaseline 并取得 Owner approval。
- `OpenAccess:Enabled = true` 仅适用于受信任隔离环境。任何新增 persistent research writing 前必须先决策 identity、attribution 与 audit ownership。

## Independent Review / Scope Governance

- 每个 Review 必须区分 `candidate scope`、`context scope` 与 `environment / dirty-worktree scope`。
- Git changed/untracked paths 可以进入 review bundle 以证明透明性与 immutability，但不自动成为 candidate。
- `.pi/` / harness 是治理层，不属于产品 runtime；项目开发过程中不得擅自修改。发现问题时默认单独记录为 governance maintenance issue / review limitation；只要不直接阻断产品开发或验收判断，就继续当前产品 Round。
- `.pi/extensions/harness-flow` 是 governance tooling，不默认属于产品 Round scope。
- Independent Review 是验收义务；spawned Pi / `harness_run_independent_review` 只是自动化执行能力。child failed/timed out/aborted/truncated 且未返回有效 P0/P1/P2 时，记录为 `automated_review_capability_blocked`，不是产品 candidate P1。
- automated review capability/auth/isolation 不稳定时，允许纠正一次明显调用打包错误；随后停止重复 reload/re-review/harness 修复；不自动修改 `.pi/` / harness；向 Owner 报告问题与影响，并请求 Owner-approved distinct human review fallback、继续产品验收并记录 limitation、另开 governance maintenance 或调整 review mode。
- 本项目默认不要求 OS-level sandbox / bwrap；默认要求是 distinct no-session reviewer、strict read-only tools 与 Git immutability evidence。

## Scope

In scope:

- 合并 Product Reboot constraints，且不削弱当前治理；
- P0–P3 code/domain disposition audit；
- 独立 research shell；
- Flat/3D Explorer、shared stable-ID state、callout、drawer、keyboard access；
- Card/List Company Pool、Quick Drawer、entity-centric Full Detail；
- read-only linked-object Workspace；
- 1440px 与 1920px product-visible evidence；
- replacement proven 后的 bounded legacy frontend cleanup。

Out of scope:

- Evidence Timeline/Review UI、Conclusion publishing UI、Report generation UI；
- Company Comparison；
- Workspace writing、Graph、New Note、Markdown、collaboration、plugin ecosystem；
- ResearchNote/OpenQuestion/Backlink persistent entities；
- identity-system redesign；
- 新大型 frontend framework、WebGL、复杂 3D/CAD；
- trading、market data、backtesting；
- prototype claims 进入 seed/database/research copy；
- automatic commit 或 push。

## Round Ledger

| Round ID | Primary implementation session | Independently reviewable delivery boundary | Acceptance evidence | Status |
|---|---|---|---|---|
| R1 | R1-code-disposition-audit | 完成只读 P0–P3 code/domain disposition audit 与 child/material-to-company capability finding；只写 durable audit/review evidence。 | 完整 disposition matrix；child/material relationship capability/gap finding；production-path unchanged evidence；validation record；Independent Review/fallback evidence 与 P2 dispositions | accepted |
| R2 | R2-research-shell | 交付 root research entry、minimal research top navigation、research layout，并把 primary research navigation 与 secondary admin routes 分离。 | 1440px/1920px shell screenshots；root/navigation/admin-route assertions；full validation；Independent Review evidence 与 P2 dispositions | accepted |
| R3 | R3-cpo-explorer-vertical-slice | 交付一个 production-quality SiPh PIC Flat/3D Explorer vertical slice。 | 1440px/1920px Flat/3D evidence；view-switch/reset/keyboard sequence；focused/full validation；Independent Review evidence 与 P2 dispositions | accepted |
| R4 | R4-full-cpo-explorer | 将已接受的 Explorer interaction 扩展到完整 approved CPO taxonomy。 | Full component coverage matrix；1440px/1920px Explorer evidence；interaction recording；full validation；Independent Review evidence 与 P2 dispositions | pending |
| R5 | R5-company-research-experience | 交付 Card/List Company Pool、context-preserving Quick Drawer 与 entity-centric Full Company Detail。 | 1440px/1920px Card/List/Drawer/Detail evidence；context/filter/scroll sequence；policy regression；full validation；Independent Review evidence 与 P2 dispositions | pending |
| R6 | R6-readonly-research-workspace | 使用既有 relationships 交付 read-only linked-object Workspace。 | Schema-unchanged evidence；1440px/1920px component/company Workspace evidence；navigation/context sequence；full validation；Independent Review evidence 与 P2 dispositions | pending |
| R7 | R7-reboot-integration-cleanup | 验证 Explorer-to-Company-to-Workspace journey，修复 Evidence review endpoint 的 human actor enforcement，并只删除 proven-unreferenced legacy frontend。 | End-to-end journey evidence；machine-reviewer rejection test；cleanup map；full regression/portability；per-Round 与 Final Integrated Independent Review evidence | pending |

## R1 — P0–P3 Code Disposition And Domain Audit

- Round name: P0–P3 Code Disposition And Domain Audit
- Primary Pi implementation session: R1-code-disposition-audit
- Goal: 将相关 frontend、routes、view-models、services 与 tests 分类为 KEEP、ADAPT、REPLACE、HIDE 或 DELETE LATER，并确认既有 child/material-to-company relationship capability。
- Handoff contracts: AGENTS.md; operations/orchestration/independent-review-and-round-scope-standard.md; src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md; docs/product/README.md; docs/product/experience-map.md; docs/product/cpo-explorer-spec.md; docs/product/company-research-spec.md; docs/product/research-workspace-spec.md; docs/product/acceptance-contract.md; docs/research-baseline/evidence-contract.md; operations/planning/research-experience-reboot.md; operations/orchestration/research-experience-reboot.md
- Latest work log: operations/work_logs/research-experience-reboot-r1.md
- Latest review: operations/reviews/research-experience-reboot-r1-independent-review.md
- Review work log: operations/work_logs/research-experience-reboot-r1.md
- Non-goals: Do not modify production application code; do not modify schema, migrations, seed, runtime config, or tests; do not start the Research Shell; do not infer research facts from prototypes; do not repair bwrap/provider-auth/harness-flow inside R1 product scope
- Dependencies / Definition of Ready: Approved product/governance baseline is present; Git baseline and dirty-worktree status are recorded; P0–P3 source and tests are readable; review scope classification is explicit; package prototype limitations are treated as production acceptance defects rather than product questions
- Mandatory read order: Applicable AGENTS; independent review scope standard; product README and experience map; all page specs and prototypes; visual language and acceptance contract; this Plan and orchestration; research evidence contract; current P0–P3 source and tests
- Governing product spec: docs/product/README.md; docs/product/experience-map.md; all page-specific specs
- Approved / directional prototype: docs/product/prototypes/cpo-explorer-v0.4.html; docs/product/prototypes/company-pool-v0.3.html; docs/product/prototypes/research-workspace-v0.1.html; Gemini reference is design-only
- Expected change surfaces: R1 product-audit candidate is limited to operations/reviews/reboot-p3-code-disposition.md; operations/work_logs/research-experience-reboot-r1.md; operations/reviews/research-experience-reboot-r1-independent-review.md. Governance/document updates such as AGENTS.md, operations/orchestration/independent-review-and-round-scope-standard.md, operations/orchestration/research-experience-reboot.md, docs/README.md, and docs references cleanup are context/governance surfaces, not R1 product-audit candidate surfaces. `.pi/` / harness-flow maintenance must not be modified during product development unless a severe blocking bug prevents continuation and Owner explicitly authorizes a separate governance maintenance task.
- Protected / forbidden surfaces: src/; tests/; data/; migrations; appsettings and runtime config; existing research evidence and seed
- Exact visible outcome: 文件级 disposition matrix；每项说明 reason、dependency、governing spec、migration risk、backend reuse；child/material-to-company finding 明确 current capability、missing capability、query/service adaptation need 与 schema-change need。
- Exact validation strategy: Capture before/after `git rev-parse HEAD` and `git status --short`; run `git diff --exit-code -- src tests data`; compare before/after `git status --short -- src tests data`; use `find` and `rg` to prove all relevant Research UI, routes, services, entities, and tests are classified; verify every cited file and dependency exists; classify dirty paths as candidate/context/environment/governance.
- Product-visible acceptance evidence: Audit matrix 与 migration sequence human-readable；child/material finding 明确说明 current capability、gap、query/service need、schema-change need。
- Screenshot / recording requirements: None because R1 has no UI candidate; durable audit matrix is visible evidence
- Independent Review mode: spawned_pi_process
- Review fallback rule: If automated spawned review capability is blocked, use Owner-approved distinct human_review fallback or explicit Owner review-mode/acceptance change; do not edit `.pi/` / harness inside the product Round.
- Round review: operations/reviews/research-experience-reboot-r1-independent-review.md
- Final integrated review: operations/reviews/research-experience-reboot-final-integrated-review.md
- Acceptance evidence: Complete disposition matrix; child/material relationship capability and gap finding; unchanged production-path evidence; automated validation record; Independent Review/fallback evidence and P2 dispositions
- Product Owner acceptance gate: Owner accepts the disposition map before R2 begins
- Exact next gate: R1 accepted by Owner on 2026-08-28; acceptance commit/post-commit verify is authorized if requested; stop. R2 handoff requires a separate Owner start decision.
- Blockers / assumptions: Existing stable IDs and relationships are expected to be reusable; existing untracked data and governance changes are preserved; no production write is permitted in this Round; automated review sandbox/auth blocker is governance maintenance, not R1 product candidate.
- Blocked / rebaseline conditions: A new or materially changed persistent domain model is required; evidence or audit semantics must change; a large frontend/backend architecture replacement appears necessary; relevant source cannot be classified without modifying it; Owner changes R1 acceptance boundary.

## R2 — Research Shell

- Round name: Research Shell
- Primary Pi implementation session: R2-research-shell
- Goal: 用 minimal independent research-facing shell 替换 admin-template research framing。
- Handoff contracts: AGENTS.md; operations/orchestration/independent-review-and-round-scope-standard.md; src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md; docs/product/README.md; docs/product/experience-map.md; docs/product/visual-language.md; docs/product/acceptance-contract.md; operations/planning/research-experience-reboot.md; operations/orchestration/research-experience-reboot.md; operations/reviews/reboot-p3-code-disposition.md
- Latest work log: operations/work_logs/research-experience-reboot-r2.md
- Latest review: operations/reviews/research-experience-reboot-r2-independent-review.md
- Review work log: operations/work_logs/research-experience-reboot-r2.md
- Non-goals: Do not redesign Explorer or Company pages; do not implement Workspace content; do not delete admin services or routes; do not add a new primary product area
- Dependencies / Definition of Ready: R1 is accepted-effective; shell KEEP/ADAPT/HIDE disposition is approved; current admin routes remain available for maintenance; Owner explicitly starts R2
- Mandatory read order: Applicable AGENTS; independent review scope standard; product README; experience map; shared shell/header direction in prototypes; visual language; acceptance contract; this Plan and orchestration; R1 audit; current layouts and navigation
- Governing product spec: docs/product/README.md; docs/product/experience-map.md; docs/product/visual-language.md
- Approved / directional prototype: Shared navigation and shell direction from all three canonical prototypes
- Expected change surfaces: src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/; src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/; src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/ResearchNavigation.cs; research shell TypeScript/CSS; tests-ui/
- Protected / forbidden surfaces: Migrations and entities; evidence workflow and verification policy; seed data; admin service endpoints and maintenance routes
- Exact visible outcome: Root opens research experience; primary navigation 只包含 CPO Explorer、Company Pool、Research Workspace；Dashboard/Administration/Language/Users/Roles/Permissions 不出现在 primary research navigation，但 secondary admin routes 可达。
- Exact validation strategy: Run `npm run build`; run `dotnet build SerenityQuantResearch.slnx --no-restore`; run `dotnet test SerenityQuantResearch.slnx --no-build`; add focused shell route/navigation assertions; run `npm run test:ui`; verify 1440px and 1920px rendered states
- Product-visible acceptance evidence: Root/research-shell screenshots at both viewports; primary-nav assertions; secondary admin route reachability; no generic Dashboard framing
- Screenshot / recording requirements: Root and one research page at 1440px and 1920px; secondary admin route proof without primary-nav exposure
- Independent Review mode: spawned_pi_process
- Review fallback rule: If automated spawned review capability is blocked, use Owner-approved distinct human_review fallback or explicit Owner review-mode/acceptance change; do not edit `.pi/` / harness inside the product Round.
- Round review: operations/reviews/research-experience-reboot-r2-independent-review.md
- Final integrated review: operations/reviews/research-experience-reboot-final-integrated-review.md
- Acceptance evidence: 1440px/1920px shell screenshots；root/navigation/admin-route assertions；full validation；Independent Review evidence 与 P2 dispositions
- Product Owner acceptance gate: Owner accepts shell objective, IA, visual hierarchy, and admin separation before R3
- Exact next gate: R2 accepted-effective after Owner acceptance, authorized acceptance commit, and post-commit verification on 2026-08-28; stop. R3 requires separate Owner start decision.
- Blockers / assumptions: Existing Razor/TypeScript/CSS can host shell; Open Access remains local-only; admin capability hidden from primary research navigation rather than deleted
- Blocked / rebaseline conditions: A new primary product area is needed; admin maintenance would be destroyed; a new large frontend framework is required; root-route behavior conflicts with approved product contract

## R3 — CPO Explorer Vertical Slice

- Round name: CPO Explorer Vertical Slice
- Primary Pi implementation session: R3-cpo-explorer-vertical-slice
- Goal: 交付一个 production-quality SiPh PIC Flat/3D Explorer vertical slice。
- Handoff contracts: AGENTS.md; operations/orchestration/independent-review-and-round-scope-standard.md; src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md; docs/product/README.md; docs/product/experience-map.md; docs/product/cpo-explorer-spec.md; docs/product/visual-language.md; docs/product/acceptance-contract.md; docs/research-baseline/evidence-contract.md; operations/planning/research-experience-reboot.md; operations/reviews/reboot-p3-code-disposition.md
- Latest work log: operations/work_logs/research-experience-reboot-r3.md
- Latest review: operations/reviews/research-experience-reboot-r3-independent-review.md
- Review work log: operations/work_logs/research-experience-reboot-r3.md
- Non-goals: Do not implement full component coverage; do not redesign Company Pool; do not add WebGL or schema; do not copy prototype/Gemini research claims
- Dependencies / Definition of Ready: R2 is accepted-effective; R1 identifies reusable state/service assets; SiPh PIC and children can use stable existing IDs without schema change; current seed lacks reviewed discrete material catalog so material must be authoritative or explicit gap
- Mandatory read order: Applicable AGENTS; independent review scope standard; product README and experience map; CPO spec; CPO v0.4 prototype; Gemini design-only reference; visual language and acceptance contract; evidence contract; this Plan; R1/R2 evidence; current P2 code and tests
- Governing product spec: docs/product/cpo-explorer-spec.md
- Approved / directional prototype: docs/product/prototypes/cpo-explorer-v0.4.html is interaction baseline; docs/product/prototypes/gemini-cpo-explorer-design-reference.html is design-only
- Expected change surfaces: src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/; narrowly required PartResearch service/view-model adaptation; tests/SerenityQuantResearch.Tests/PartResearchServiceTests.cs; tests-ui/
- Protected / forbidden surfaces: Migrations and seed factual state; evidence policy; Company production redesign; prototype mock claims; complex 3D/WebGL dependencies
- Exact visible outcome: 同一 SiPh PIC stable ID 在 Flat/3D 间保持 selected；component/callout hover/click 等价；real geometry owns hit regions；same-object、blank、Esc、close reset；keyboard selection works；drawer 展示真实 children、权威 technology/material context 或 `暂无已核验材料数据`/omission，以及 evidence-safe company preview。
- Exact validation strategy: Add focused selection/view-switch/hit-ownership/keyboard state tests; add service tests only if service adapts; run `npm run build`; run full `dotnet build` and `dotnet test`; run fresh Kestrel/Firefox `npm run test:ui`; inspect 1440px and 1920px states
- Product-visible acceptance evidence: Idle/Hover/Selected Flat and 3D states; open drawer; preserved selection during view switch; reset and keyboard demonstrations
- Screenshot / recording requirements: 1440px and 1920px Flat/3D state screenshots; short recording or sequence for view switching, resets, keyboard selection
- Independent Review mode: spawned_pi_process
- Review fallback rule: If automated spawned review capability is blocked, use Owner-approved distinct human_review fallback or explicit Owner review-mode/acceptance change; do not edit `.pi/` / harness inside the product Round.
- Round review: operations/reviews/research-experience-reboot-r3-independent-review.md
- Final integrated review: operations/reviews/research-experience-reboot-final-integrated-review.md
- Acceptance evidence: 1440px/1920px Flat/3D evidence；view-switch/reset/keyboard sequence；focused/full validation；Independent Review evidence 与 P2 dispositions
- Product Owner acceptance gate: Owner accepts vertical-slice behavior and visual direction before R4
- Exact next gate: R3 accepted-effective closeout; stop. R4 requires separate Owner start decision.
- Blockers / assumptions: SiPh PIC is representative slice; unsupported factual fields are omitted or neutral; child/material company filtering may be deferred when no explicit relationship exists
- Blocked / rebaseline conditions: Persistent schema change is required; complex 3D/WebGL is required; core Explorer path must change; required research data would have to be invented

## R4 — Full CPO Explorer

- Round name: Full CPO Explorer
- Primary Pi implementation session: R4-full-cpo-explorer
- Goal: 将已接受的 vertical-slice behavior 扩展到完整 approved CPO taxonomy。
- Handoff contracts: AGENTS.md; operations/orchestration/independent-review-and-round-scope-standard.md; src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md; docs/product/README.md; docs/product/experience-map.md; docs/product/cpo-explorer-spec.md; docs/product/visual-language.md; docs/product/acceptance-contract.md; docs/research-baseline/cpo-taxonomy.md; docs/research-baseline/evidence-contract.md; operations/planning/research-experience-reboot.md; operations/reviews/research-experience-reboot-r3-independent-review.md
- Latest work log: operations/work_logs/research-experience-reboot-r3.md
- Latest review: operations/reviews/research-experience-reboot-r3-independent-review.md
- Review work log: operations/work_logs/research-experience-reboot-r4.md
- Non-goals: Do not implement Company Pool; do not add schema; do not trace or ship JPEG artwork; do not expand to CAD, WebGL, or unapproved metrics
- Dependencies / Definition of Ready: R3 is accepted-effective; full stable-ID mapping and geometry ownership plan is reviewable; required original presentation can be produced without provenance-risk assets
- Mandatory read order: Applicable AGENTS; independent review scope standard; R3 mandatory contracts and accepted evidence; reviewed CPO taxonomy; current full catalog/service/test implementation
- Governing product spec: docs/product/cpo-explorer-spec.md; docs/product/acceptance-contract.md
- Approved / directional prototype: CPO v0.4 interaction behavior; final production geometry must be original
- Expected change surfaces: Research Diagram Razor/TypeScript/CSS/state; narrowly required query/service adaptation; focused .NET/UI/browser tests
- Protected / forbidden surfaces: Migrations; research/evidence semantics; copied or traced JPEG pixels; Company UX; admin capability
- Exact visible outcome: 所有 approved major components 与 researchable parts 拥有 stable-ID geometry/callout ownership；无 broad invisible hit zone；Flat/3D selection persists；child/material drill-down 与 company context 使用权威关系；keyboard/viewport behavior 通过。
- Exact validation strategy: Run full build and .NET/UI suites; assert component/catalog stable-ID coverage; test component-callout equivalence, overlap ownership, blank reset, view persistence, child/material context, keyboard behavior, and both required viewports
- Product-visible acceptance evidence: Full coverage matrix; representative and edge-case Flat/3D screenshots; interaction recording; prototype-defect remediation evidence
- Screenshot / recording requirements: 1440px and 1920px representative Idle/Hover/Selected Flat and 3D; full-coverage interaction sequence or recording
- Independent Review mode: spawned_pi_process
- Review fallback rule: If automated spawned review capability is blocked, use Owner-approved distinct human_review fallback or explicit Owner review-mode/acceptance change; do not edit `.pi/` / harness inside the product Round.
- Round review: operations/reviews/research-experience-reboot-r4-independent-review.md
- Final integrated review: operations/reviews/research-experience-reboot-final-integrated-review.md
- Acceptance evidence: Full component coverage matrix; 1440px and 1920px Explorer evidence; interaction recording; full automated validation record; Independent Review evidence and P2 dispositions
- Product Owner acceptance gate: Owner accepts full Explorer before R5
- Exact next gate: Product Owner R4 acceptance; authorized acceptance commit/post-commit verify if requested; stop. R5 requires separate Owner start decision.
- Blockers / assumptions: Existing 9-module/21-part taxonomy remains engineering baseline; unsupported factual fields are omitted or neutral
- Blocked / rebaseline conditions: Full coverage needs persistent schema change; artwork rights/provenance block original implementation; accepted R3 interaction must materially change; evidence semantics would be weakened

## R5 — Company Research Experience

- Round name: Company Pool, Quick Drawer, And Full Detail
- Primary Pi implementation session: R5-company-research-experience
- Goal: 交付 approved three-depth company research experience，并保留 Explorer context 与 research states。
- Handoff contracts: AGENTS.md; operations/orchestration/independent-review-and-round-scope-standard.md; src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md; docs/product/README.md; docs/product/experience-map.md; docs/product/company-research-spec.md; docs/product/visual-language.md; docs/product/acceptance-contract.md; docs/research-baseline/evidence-contract.md; operations/planning/research-experience-reboot.md; operations/reviews/reboot-p3-code-disposition.md; operations/reviews/research-experience-reboot-r4-independent-review.md
- Latest work log: operations/work_logs/research-experience-reboot-r4.md
- Latest review: operations/reviews/research-experience-reboot-r4-independent-review.md
- Review work log: operations/work_logs/research-experience-reboot-r5.md
- Non-goals: No Company Comparison; no default SleekGrid-first product; no default seven-tab detail; no change to exposure/evidence verification or audit semantics; no Workspace implementation
- Dependencies / Definition of Ready: R4 is accepted-effective; Explorer context contract is stable; R1 disposition identifies reusable Company services, routes, and policies
- Mandatory read order: Applicable AGENTS; independent review scope standard; product README and experience map; Company spec; company v0.3 prototype; visual language and acceptance contract; evidence contract; this Plan; R1/R4 evidence; current P3 code/services/tests
- Governing product spec: docs/product/company-research-spec.md
- Approved / directional prototype: docs/product/prototypes/company-pool-v0.3.html
- Expected change surfaces: src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Company/; narrowly required CompanyUniverse service/view-model adaptation; Company service/policy tests; tests-ui/
- Protected / forbidden surfaces: Migrations and stable company IDs; candidate/verified and review policy; audit behavior; seed facts; Research Workspace implementation
- Exact visible outcome: Card View 默认；List View 保持 company set/filter/source context；company click 打开 Quick Drawer；Esc/outside/close dismiss；expand 打开 entity-centric continuous/lightly segmented Full Detail；Explorer source path 可理解。
- Exact validation strategy: Run Company service and endpoint policy tests; add Card/List/Drawer/context/filter/scroll browser assertions; run `npm run build`; run full `dotnet build`, `dotnet test`, and `npm run test:ui`; inspect 1440px and 1920px states
- Product-visible acceptance evidence: Card/List/Quick Drawer/Full Detail/Explorer-context screenshots; state-preservation sequence; candidate/draft/unknown semantics visible
- Screenshot / recording requirements: Both viewports for Card/List/Drawer/Detail; sequence proving context/filter/scroll preservation
- Independent Review mode: spawned_pi_process
- Review fallback rule: If automated spawned review capability is blocked, use Owner-approved distinct human_review fallback or explicit Owner review-mode/acceptance change; do not edit `.pi/` / harness inside the product Round.
- Round review: operations/reviews/research-experience-reboot-r5-independent-review.md
- Final integrated review: operations/reviews/research-experience-reboot-final-integrated-review.md
- Acceptance evidence: 1440px and 1920px Card/List/Drawer/Detail evidence; context/filter/scroll sequence; policy regression record; full automated validation record; Independent Review evidence and P2 dispositions
- Product Owner acceptance gate: Owner accepts company experience before R6
- Exact next gate: Product Owner R5 acceptance; authorized acceptance commit/post-commit verify if requested; stop. R6 requires separate Owner start decision.
- Blockers / assumptions: Existing service aggregation and stable IDs are reusable; Open Access remains local-only
- Blocked / rebaseline conditions: Card/List → Quick Drawer → Full Detail path must change; persistent schema is required; evidence/audit semantics must change; new persistent writing is introduced

## R6 — Read-only Linked Research Workspace

- Round name: Read-only Linked Research Workspace
- Primary Pi implementation session: R6-readonly-research-workspace
- Goal: 使用既有 persistent objects 与 relationships 验证 knowledge-centric、linked-object-first Workspace。
- Handoff contracts: AGENTS.md; operations/orchestration/independent-review-and-round-scope-standard.md; src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md; docs/product/README.md; docs/product/experience-map.md; docs/product/research-workspace-spec.md; docs/product/visual-language.md; docs/product/acceptance-contract.md; docs/research-baseline/evidence-contract.md; operations/planning/research-experience-reboot.md; operations/reviews/reboot-p3-code-disposition.md; operations/reviews/research-experience-reboot-r5-independent-review.md
- Latest work log: operations/work_logs/research-experience-reboot-r5.md
- Latest review: operations/reviews/research-experience-reboot-r5-independent-review.md
- Review work log: operations/work_logs/research-experience-reboot-r6.md
- Non-goals: No ResearchNote, OpenQuestion, or Backlink persistent entity; no writing; no Graph; no New Note; no Markdown, collaboration, or plugin system
- Dependencies / Definition of Ready: R5 is accepted-effective; R1 proves existing objects can support read-only projection; component/company routes can carry stable source context
- Mandatory read order: Applicable AGENTS; independent review scope standard; product README and experience map; Workspace spec and Owner read-only amendment; workspace v0.1 with Graph/New Note treated as placeholders; visual language and acceptance contract; evidence contract; this Plan; R1/R5 evidence; existing entities and services
- Governing product spec: docs/product/research-workspace-spec.md
- Approved / directional prototype: docs/product/prototypes/research-workspace-v0.1.html is directional; Graph and New Note are deferred placeholders
- Expected change surfaces: New or adapted read-only Research Workspace Razor/TypeScript/CSS; read-only aggregation service/view model; navigation/context; focused .NET/UI/browser tests
- Protected / forbidden surfaces: Migrations; new persistent entities; write endpoints; identity configuration; evidence, review, publication, and audit semantics
- Exact visible outcome: Component 与 company research objects 可在 Workspace 打开；lightweight tree、current object、linked objects、derived backlinks、evidence/status context 与 read-only unresolved questions 可见；source path 可理解；不宣称 writing/Graph/New Note。
- Exact validation strategy: Prove no migration/schema changes; add focused read-only projection tests; test component/company Workspace routes, linked-object/backlink navigation, source context, evidence states, open-question separation; run full build, .NET tests, UI browser suite at both viewports
- Product-visible acceptance evidence: Component object, company object, linked-object/backlink context, evidence/status, and open-question screenshots; Explorer/Company-to-Workspace navigation sequence
- Screenshot / recording requirements: 1440px and 1920px component and company states; navigation sequences from Explorer and Full Company Detail
- Independent Review mode: spawned_pi_process
- Review fallback rule: If automated spawned review capability is blocked, use Owner-approved distinct human_review fallback or explicit Owner review-mode/acceptance change; do not edit `.pi/` / harness inside the product Round.
- Round review: operations/reviews/research-experience-reboot-r6-independent-review.md
- Final integrated review: operations/reviews/research-experience-reboot-final-integrated-review.md
- Acceptance evidence: Schema-unchanged evidence; 1440px and 1920px component/company Workspace evidence; navigation/context sequence; full automated validation record; Independent Review evidence and P2 dispositions
- Product Owner acceptance gate: Owner accepts Workspace v1 before R7
- Exact next gate: Product Owner R6 acceptance; authorized acceptance commit/post-commit verify if requested; stop. R7 requires separate Owner start decision.
- Blockers / assumptions: Existing unresolved questions may be derived read-only; derived backlinks are query/view-model results; unsupported values remain Unknown/Not reviewed/Candidate/omitted
- Blocked / rebaseline conditions: Persistent writing or new entity becomes necessary; identity/author attribution must change; evidence/audit semantics change; graph/knowledge-management backend becomes required

## R7 — Integrated Journey, Regression, And Legacy Cleanup

- Round name: Integrated Journey, Regression, And Legacy Cleanup
- Primary Pi implementation session: R7-reboot-integration-cleanup
- Goal: 验证完整 Research Experience Reboot，修复 Evidence workflow endpoint 的 human reviewer contract enforcement，并只删除 proven-unreferenced legacy research-facing frontend paths。
- Handoff contracts: AGENTS.md; operations/orchestration/independent-review-and-round-scope-standard.md; src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md; docs/product/README.md; docs/product/experience-map.md; docs/product/cpo-explorer-spec.md; docs/product/company-research-spec.md; docs/product/research-workspace-spec.md; docs/product/visual-language.md; docs/product/acceptance-contract.md; docs/research-baseline/evidence-contract.md; operations/planning/research-experience-reboot.md; operations/reviews/reboot-p3-code-disposition.md; operations/reviews/research-experience-reboot-r6-independent-review.md
- Latest work log: operations/work_logs/research-experience-reboot-r6.md
- Latest review: operations/reviews/research-experience-reboot-r6-independent-review.md
- Review work log: operations/work_logs/research-experience-reboot-r7.md
- Non-goals: Do not implement Evidence, Conclusion, or Report UI; do not delete history, migrations, domain services, evidence policy, or admin backend; do not change review semantics or add product scope; machine principals must never be upgraded to human by permission possession alone
- Dependencies / Definition of Ready: R1–R6 are accepted-effective; every DELETE LATER candidate has proven replacement and no-reference evidence; all product-visible evidence can be reproduced
- Mandatory read order: Applicable AGENTS; independent review scope standard; full product baseline; evidence contract; this Plan; R1–R6 work logs and reviews; current integrated source and tests
- Governing product spec: docs/product/acceptance-contract.md; all page-specific specs
- Approved / directional prototype: All three canonical prototypes for drift comparison only
- Expected change surfaces: Integration/browser tests and harness; bounded dead research-facing frontend files identified by R1; `EvidenceWorkflowEndpoint` using existing `UserRow.ActorType` / `UserActorTypes` lookup pattern to reject machine principals; endpoint policy/integration tests; product status docs; operations/work_logs/research-experience-reboot-r7.md; R7 and final review artifacts
- Protected / forbidden surfaces: Migrations and persistent domain; evidence/audit/publication semantics; historical work logs/reviews; unrelated admin backend; deferred product scope
- Exact visible outcome: Explorer → Company → Workspace journey 可复现；Evidence endpoint 拒绝 machine reviewer；legacy cleanup 有 no-reference proof；无 deferred Evidence/Conclusion/Report UI 被偷带。
- Exact validation strategy: Run full build, .NET tests, UI tests, browser journey, endpoint machine/human reviewer tests, no-schema-change scan, no-reference cleanup scan, portability scan, and Final Integrated Independent Review
- Product-visible acceptance evidence: End-to-end journey screenshots/sequence; machine-reviewer rejection evidence; cleanup map; full regression and portability record
- Screenshot / recording requirements: 1440px and 1920px integrated journey sequence; representative cleanup/no-dead-link evidence
- Independent Review mode: spawned_pi_process
- Review fallback rule: R7 also requires Final Integrated Independent Review before pre-commit gate; if automated spawned review capability is blocked, use Owner-approved distinct human_review fallback or explicit Owner review-mode/acceptance change; do not edit `.pi/` / harness inside the product Round.
- Round review: operations/reviews/research-experience-reboot-r7-independent-review.md
- Final integrated review: operations/reviews/research-experience-reboot-final-integrated-review.md
- Acceptance evidence: End-to-end journey evidence; machine-reviewer rejection test; bounded cleanup map; clean full regression and portability record; per-Round Independent Review evidence; Final Integrated Independent Review evidence and P2 dispositions
- Product Owner acceptance gate: Owner accepts integrated journey, endpoint enforcement, cleanup proof, and final integrated review before accepted-effective
- Exact next gate: Product Owner R7 acceptance; authorized acceptance commit/post-commit verify if requested; stop. Later Evidence/Conclusion/Report UI requires a new Plan.
- Blockers / assumptions: R1–R6 accepted evidence remains reproducible; endpoint identity can reuse P3 actor-type infrastructure; cleanup is limited to proven-dead frontend
- Blocked / rebaseline conditions: Evidence semantics would change; schema/migration is required; cleanup would remove admin/backend/history; deferred UI scope is needed; Final Integrated Review cannot be completed or approved fallback is unavailable

## Commit / Push / Progression Rules

- 不自动 commit，不自动 push。
- 每个 Round 必须在 Owner acceptance、authorized acceptance commit 与 post-commit verify 后才可称为 accepted-effective。
- 一个 Round 完成后停止；后续 Round 需要 Owner 明确启动。
- Review/Fix 不创建隐藏 Round；continuation 仍属于同一 Round。

## Current R1 Closeout Direction

R1 只收口产品审计。不要继续在 R1 中修 bwrap、provider auth 或 `.pi/extensions/harness-flow`。这些属于 governance maintenance dirty state/backlog。R1 后续 review 必须明确 candidate/context/environment scope，并且不得把 review bundle 中的 harness implementation 当作 R1 产品审计 candidate。

后续所有产品 Round 均适用同一规则：`.pi/` / harness 问题默认单独记录，不进产品 candidate；只要不直接阻断产品开发或验收判断，就继续当前产品 Round。只有严重恶性 bug 导致项目无法继续，并经 Owner 明确授权，才允许单开治理维护修改 `.pi/` / harness 文件。
