# Research Experience Reboot — R3 独立评审

Round: R3
Review role: per_round
Decision: pass
Unresolved P0: 0
Unresolved P1: 0

## Status

- Round：`R3 — CPO Explorer Vertical Slice`
- Required mode：`spawned_pi_process`
- Final review path：updated `harness_run_independent_review` wrapper。
- Artifact author：Builder；review child 未写项目文件。
- Product candidate status：implementation、full automated validation、Independent Review、P2 disposition、Product Owner acceptance、acceptance commit authorization 已完成。
- R3 accepted-effective closeout will be valid after acceptance commit and post-commit verification complete.

## Candidate scope reviewed

R3 candidate：

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramIndex.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.css`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/PartSelectionState.ts`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh`
- `operations/reviews/research-experience-reboot-r3-screenshots/*.png`
- `operations/work_logs/research-experience-reboot-r3.md`
- `operations/reviews/research-experience-reboot-r3-independent-review.md`

Context scope：product/governance/evidence contracts, approved CPO prototype, design-only Gemini reference, seed JSON, R1/R2 evidence, and canonical Plan.

Environment / governance scope：`operations/orchestration/governance-maintenance-backlog.md` is governance maintenance dirty state from治理层下发/认证记录；not R3 product candidate. `.pi` / harness was not edited by this R3 Builder.

## Candidate summary reviewed

R3 implements a production-quality SiPh PIC Explorer vertical slice only:

- stable shared interaction object：`cpo.mod.pic`。
- Flat / 3D selected and hover state are shared.
- component ↔ callout hover/click are equivalent.
- same-object、blank canvas、close、Esc reset and keyboard Enter / Space selection are implemented.
- drawer is hidden until selection and initially `hidden` + `aria-hidden="true"`.
- drawer uses existing service data for real child parts：`cpo.part.pic.modulator`、`cpo.part.pic.wdm`、`cpo.part.pic.waveguide-coupler`。
- child retrieval failures are preserved as `research_chain_unknown` / unknown state and are not displayed as confirmed-empty technology/company/evidence state.
- material status explicitly states `暂无已核验材料数据`; example/prototype material chips such as Silicon / SiN / LNOI are not rendered.
- related company preview uses safe empty state when no explicit SiPh exposure exists.
- no PartResearch service adaptation, schema, migration, seed, evidence policy, Company redesign, WebGL, or prototype research claim was added.
- R2 browser regression coverage was restored inside `npm run test:ui` for Company Pool, Workspace placeholder/read-only boundary, secondary admin route, and admin service reachability.

## Automated validation evidence

Final validation after all P1/P2 fixes：

```text
git diff --check
PASS

cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build
PASS — esbuild checked 34 output files

dotnet build SerenityQuantResearch.slnx --no-restore
PASS — 0 warnings, 0 errors

dotnet test SerenityQuantResearch.slnx --no-build
PASS — 54 passed, 0 failed, 0 skipped

cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui
PASS — node UI unit 13 passed; R3 Explorer browser smoke passed
```

`npm run test:ui` now covers both R3 interaction and restored R2 regression assertions.

## Review history and final wrapper review

Early in this session, old wrapper attempts were blocked by screenshot snapshot size and child-output/capture failure. Owner then authorized manual spawned Pi review without `.pi` / harness edits. Manual reviews found and drove fixes for 3D callout occlusion, hover-vs-selected wording, missing reset/keyboard evidence, initial drawer focusability, and browser focus evidence.

After治理层下发更新后的 wrapper, Builder ran `harness_run_independent_review` again with candidate/context/environment scope separated. Result：

```text
Review decision: pass
Findings: P0=0 P1=0 P2=1
Candidate immutable: yes
```

Reviewer output preview：

```text
HARNESS_REVIEW_RESULT {"decision":"pass","findings":[{"severity":"P2","summary":"R3 evidence artifacts contain stale/contradictory status and validation metadata that should be reconciled before Owner acceptance.","evidence":"operations/work_logs/research-experience-reboot-r3.md:12 and :222 still say the current state is pending updated wrapper Independent Review, while :229 records final Attempt 3 pass; operations/work_logs/research-experience-reboot-r3.md:156 says UI unit 12 passed but review-bundle.md:16 says UI unit 13 passed; operations/reviews/research-experience-reboot-r3-independent-review.md:177 records screenshot size 1505372 bytes while operations/work_logs/research-experience-reboot-r3.md:203 and review-bundle.md:2631 record 1523255 bytes."}],"limitations":["Read-only review only; per instruction I did not run commands or rerun build/tests.","Representative screenshots and supplied validation evidence were inspected; automated validation results are accepted from the bundle/work logs."]}
```

## Findings

- P0：0
- P1：0
- P2：1

### P2 — R3 evidence artifacts contained stale/contradictory status and validation metadata

- Evidence：Reviewer found stale status lines and inconsistent validation/screenshot metadata across work log and old review artifact.
- Builder disposition：**accepted / fixed**。This artifact and `operations/work_logs/research-experience-reboot-r3.md` now record the current wrapper review pass, UI unit count `13`, screenshot size `1523255` bytes, and final next gate. This was durable evidence reconciliation only; no product code change was required.

## Product-visible evidence reviewed

R3 screenshot evidence under `operations/reviews/research-experience-reboot-r3-screenshots/` includes:

- Idle / Hover / Selected Flat at 1440px and 1920px.
- Idle / Hover / Selected 3D at 1440px and 1920px.
- View-switch-preserved at 1440px and 1920px.
- Reset-blank Flat and Reset-Esc at 1440px and 1920px.
- 1440px sequence screenshots for component selected, same-callout reset, callout selected, close reset, keyboard Enter selected, keyboard Esc reset, keyboard Space selected.

Total optimized screenshot size after final validation：`1523255` bytes.

## Git / candidate immutability evidence

Final review recording HEAD：

```text
67e9aed979a6c246504b4a97e5cc70300e6c6e49
```

Final candidate source/test hashes before wrapper review：

```text
d077276fb7651601e9bbd6d285fd760b922804a0b72d4bbd93c5520c0356fadb  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramIndex.cshtml
713c5affcd2788f43325da14721f6cd0dbf57a900c0ac3c11c3644c1f10b928b  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.css
1540c1137dd108380010d7593c44afa3b99cdf7b86da7172315886dc0e22677f  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts
a1d766d139ac31594fe632cd426a914dc60f2f4b64713f56cb834832bb517ace  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/PartSelectionState.ts
bd870e3823c6af82077b793b19b7b57ad7c4193cc540dcc8184ce6c497dd0513  src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs
a1681d5bb42788216608eeb9e6fca6b1b91a3656d7cbbec7282be0e608a43d5a  src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh
```

Review tool reported `Candidate immutable: yes`.

Current dirty status classification is recorded in `operations/work_logs/research-experience-reboot-r3.md`; `operations/planning/research-experience-reboot.md` and `operations/orchestration/governance-maintenance-backlog.md` are context/governance dirty state, not R3 product candidate.

## Decision

**pass**

R3 Independent Review obligation is satisfied by updated `harness_run_independent_review` wrapper. No P0/P1 remains. One P2 has been dispositioned as fixed evidence reconciliation.

## Required next gate

R3 accepted-effective closeout: Owner acceptance and commit authorization are complete; acceptance commit and post-commit verification are complete for the final closeout. Do not start R4 automatically.
