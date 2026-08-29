# Research Experience Reboot — R4 工作日志

Round: R4 — Full CPO Explorer
Plan: `operations/planning/research-experience-reboot.md`
Git baseline: `a24d5ab28780c8ce0975cea023708231334ee339`

## Status

- Round：`R4 — Full CPO Explorer`
- Primary session：`R4-full-cpo-explorer`
- Start：Owner 在 R3 accepted-effective 后启动 R4。
- 当前状态：`accepted_effective`
- 前序状态：R1、R2、R3 accepted-effective。

## Boundary

R4 目标是将 R3 已接受的 Explorer interaction 扩展到完整 approved CPO taxonomy。

### In scope delivered

- Flat / 3D Explorer 均绑定 9 个 approved 一级 module stable IDs：
  - `cpo.mod.thermal`
  - `cpo.mod.host-asic`
  - `cpo.mod.eic`
  - `cpo.mod.pic`
  - `cpo.mod.laser`
  - `cpo.mod.receiver`
  - `cpo.mod.fiber-interface`
  - `cpo.mod.cpa-substrate`
  - `cpo.mod.host-board`
- 研究服务目录验证 9 个一级 module / 21 个真实 child parts，并由 browser assertion 验证每个 module 在 Flat 与 3D 中都有 component geometry 与 callout。
- component / callout hover 与 click 等价；unrelated components/callouts dimmed；hover 状态明确显示 `hover preview`，不误报 selected。
- Flat / 3D selected state 共享 stable ID；view switch 不重置 selection。
- same-object component click、same-object callout click、blank canvas、Esc、close drawer reset 保持 R3 行为。
- Keyboard Enter / Space selection 保持 R3 行为，并覆盖 full Explorer component set 中代表对象。
- Drawer 对任一 module 展示现有 `PhysicalPart` child records；child count 按 taxonomy 验证为 3/2/3/3/2/1/2/2/3，总计 21。
- Drawer 聚合选中 module 的 child `RetrieveCompleteChain` 结果，只展示现有 explicit part→chain-node、part→technology、company exposure、evidence；不从图形位置或 taxonomy 类别推导供应关系。
- 材料状态统一保持 `暂无已核验材料数据` 或 retrieval-failure unknown 语义；未渲染 Prototype material chip。
- Original layered SVG / vector geometry 由 R4 自主绘制；未复制、描摹或 shipping 两张 JPEG artwork；未新增 WebGL/CAD。
- R2 shell/admin regression 继续由 UI browser smoke 覆盖。

### Non-goals maintained

- 未实现 Company Pool R5 体验；Explorer 仅保留 context-preserving Company Pool link。
- 未新增 schema、migration、seed factual state、persistent data、evidence policy 或 audit semantics。
- 未新增 CAD、WebGL、unapproved metrics、BOM/localization/market-share/company-tier/investment-thesis 等事实展示。
- 未修改 `.pi/` / harness governance tooling。

## Full component coverage matrix

| module_id | Approved module | child parts | Flat geometry | Flat callout | 3D geometry | 3D callout | Drawer source |
|---|---:|---:|---|---|---|---|---|
| `cpo.mod.thermal` | 散热与上盖 / Thermal solution and lid | 3 | yes | yes | yes | yes | `PhysicalModule` + child `PhysicalPart` service projection |
| `cpo.mod.host-asic` | 主机交换 ASIC / Host switch ASIC | 2 | yes | yes | yes | yes | same |
| `cpo.mod.eic` | 电接口处理层 / Electrical IC layer | 3 | yes | yes | yes | yes | same |
| `cpo.mod.pic` | 硅光 PIC / Silicon-photonics PIC | 3 | yes | yes | yes | yes | same |
| `cpo.mod.laser` | 光源 / Laser source | 2 | yes | yes | yes | yes | same |
| `cpo.mod.receiver` | 光接收阵列 / Photodetector receive array | 1 | yes | yes | yes | yes | same |
| `cpo.mod.fiber-interface` | 光纤耦合与连接 / Fiber attach and optical connector | 2 | yes | yes | yes | yes | same |
| `cpo.mod.cpa-substrate` | 共封装装配基板 / Co-packaged assembly substrate | 2 | yes | yes | yes | yes | same |
| `cpo.mod.host-board` | 主机板与板级互连 / Host board and board-level interconnect | 3 | yes | yes | yes | yes | same |

Browser smoke assertions verify:

- `#cpo-explorer-app[data-catalog-module-count="9"][data-catalog-part-count="21"][data-coverage-complete="true"]`。
- 每个 view 的 `.cpo-component[data-component-id]` set 与 `.cpo-callout[data-component-id]` set 均等于上述 9 个 stable IDs。
- 每个 module 在 Flat component hover、Flat callout hover、Flat component click/select/reset、3D callout click/select、view-switch preserve、Esc reset 中通过。
- 每个 selected drawer 的 `.cpo-child-card` 数量与 approved child part count 一致。

## Candidate scope

### Product/runtime candidate paths

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramIndex.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.css`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/PartSelectionState.ts`

### Test / evidence candidate paths

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh`
- `operations/reviews/research-experience-reboot-r4-screenshots/*.png`
- `operations/work_logs/research-experience-reboot-r4.md`
- `operations/reviews/research-experience-reboot-r4-independent-review.md`（pending Builder write after Independent Review）

## Context scope

- `AGENTS.md`
- `operations/orchestration/independent-review-and-round-scope-standard.md`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md`
- `docs/product/README.md`
- `docs/product/experience-map.md`
- `docs/product/cpo-explorer-spec.md`
- `docs/product/visual-language.md`
- `docs/product/acceptance-contract.md`
- `docs/research-baseline/cpo-taxonomy.md`
- `docs/research-baseline/evidence-contract.md`
- `operations/planning/research-experience-reboot.md`
- `operations/reviews/research-experience-reboot-r3-independent-review.md`
- `operations/work_logs/research-experience-reboot-r3.md`

## Environment / dirty-worktree scope

R4 start snapshot：

```text
HEAD: a24d5ab28780c8ce0975cea023708231334ee339
 M operations/orchestration/governance-maintenance-backlog.md
 M operations/planning/research-experience-reboot.md
 M operations/reviews/research-experience-reboot-r3-independent-review.md
```

Current classification：

- Candidate product/runtime：`src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/*` listed above。
- Candidate tests/evidence：`tests-ui/PartSelectionState.test.mjs`、`tests-ui/run-browser-smoke.sh`、R4 screenshot directory、this work log、R4 review artifact。
- Context/pre-existing dirty state：`operations/planning/research-experience-reboot.md`、`operations/reviews/research-experience-reboot-r3-independent-review.md`。
- Governance maintenance dirty state：`operations/orchestration/governance-maintenance-backlog.md`。
- Protected surfaces preserved：migrations、seed factual state、evidence policy、Company UX、admin capability、`.pi/` / harness governance tooling。

No schema/seed/evidence entity/service changes were made in R4.

## Implementation notes

1. `CpoDiagramIndex.cshtml` replaces the single SiPh PIC vertical slice drawing with original Flat and 3D SVG scenes containing all 9 approved modules and matching callouts. Geometry uses visible primitives only, no broad invisible overlay.
2. `CpoDiagramPage.ts` generalizes selected component state from fixed `cpo.mod.pic` to any approved module stable ID. It validates service catalog coverage before setting `data-ready="true"` and exposes module/part coverage datasets for browser assertions.
3. Drawer rendering now receives the selected `ResearchModuleSummary`, retrieves each child part through existing `PartResearchService.RetrieveCompleteChain`, and aggregates explicit chain-node, technology, company exposure, evidence, warnings, and unknown retrieval state.
4. `PartSelectionState.ts` adds approved CPO module IDs, approved part count, and a coverage helper used by UI unit tests and page initialization.
5. `CpoDiagramPage.css` keeps the R3 light/restrained visual language, adds explicit dimming for unrelated objects, supports full taxonomy geometry, and keeps drawer width bounded so selected callouts remain visible at 1440px.
6. `run-browser-smoke.sh` is updated from R3 to R4: screenshot output moved to `operations/reviews/research-experience-reboot-r4-screenshots`; browser assertions cover full module/callout coverage, child counts, hover/click equivalence, reset, view persistence, geometry ownership, material/company safety, keyboard behavior, and R2 regression.

## Product-visible evidence

Screenshots generated by `npm run test:ui:browser`:

- `operations/reviews/research-experience-reboot-r4-screenshots/idle-flat-1440.png`
- `operations/reviews/research-experience-reboot-r4-screenshots/hover-flat-pic-1440.png`
- `operations/reviews/research-experience-reboot-r4-screenshots/selected-flat-host-asic-1440.png`
- `operations/reviews/research-experience-reboot-r4-screenshots/view-switch-host-asic-1440.png`
- `operations/reviews/research-experience-reboot-r4-screenshots/idle-3d-1440.png`
- `operations/reviews/research-experience-reboot-r4-screenshots/hover-3d-laser-1440.png`
- `operations/reviews/research-experience-reboot-r4-screenshots/selected-3d-fiber-interface-1440.png`
- `operations/reviews/research-experience-reboot-r4-screenshots/reset-blank-1440.png`
- same 8 states at 1920px.

Total screenshot directory size after post-commit browser run and lossless-dimension palette optimization：`757311` bytes. PNG dimensions remain 1440×980 or 1920×1080.

Manual Builder visual inspection：

- `idle-flat-1440.png` shows all 9 callouts and the original flat board/system geometry without Serenity admin sidebar.
- `selected-3d-fiber-interface-1440.png` shows unrelated components/callouts de-emphasized, selected callout visible left of drawer, drawer with 2真实 child parts, material gap, explicit chain context, and safe empty company state.

## Automated validation evidence

Corrected final validation sequence：

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
PASS — node UI unit 14 passed; R4 Explorer browser smoke passed
```

After Independent Review P1 cleanup fix, the same full validation sequence was rerun and passed:

```text
git diff --check
PASS
npm run build
PASS
dotnet build SerenityQuantResearch.slnx --no-restore
PASS — 0 warnings, 0 errors
dotnet test SerenityQuantResearch.slnx --no-build
PASS — 54 passed, 0 failed, 0 skipped
npm run test:ui
PASS — node UI unit 14 passed; R4 Explorer browser smoke passed
```

Note：一次 validation command 使用错误相对路径从 Web 目录 `cd ../../../..` 回到 `src/`，导致 `MSBUILD : error MSB1009: Project file does not exist. Switch: SerenityQuantResearch.slnx`；随后用 repository absolute path 重新运行完整 sequence 并通过。该错误是 Builder command packaging error，不是 product failure。

## Candidate hashes before Independent Review

```text
e74cbaec2e802bd6200daccb2c409910702204a5c9cec8186b3cad0e9b081ca1  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramIndex.cshtml
d4158c5b781073d838132b6b8966007817f8d114a6c9e670d8054db2f7e27df7  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.css
a32cb41957638e45e67b769ceb4942bb130c11acb2916009850376ece9f0adc3  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts
95fb313fdf02fd8cb5703bbdb58dcbca5732b16e63cb874fd209c6760f590253  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/PartSelectionState.ts
d9e7fa2d55f96c13e0eb711c3006e20ac22706d79af633a734176c00633e6bc4  src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs
353e2f5eb3b646440a287212cfffc76475f39329d80aeac9d276dcdaf116e291  src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh
```

## Independent Review status

- Required mode：`spawned_pi_process`
- Artifact：`operations/reviews/research-experience-reboot-r4-independent-review.md`
- Current state：P1 fixed and verified; automated wrapper re-review capability blocked pending Owner fallback decision.
- Attempt 1：blocked by Builder packaging error because screenshot directory was passed as a candidate path instead of regular files.
- Attempt 2：blocked by untracked review evidence snapshot size > 2 MiB. Builder reduced screenshot artifact size by PNG palette optimization while preserving viewport dimensions; no product code/schema/data change was made for this optimization.
- Attempt 3：valid spawned review returned `changes_required`, P0=0, P1=1, P2=0. P1 was `run-browser-smoke.sh` cleanup using `${FIREFOX_PID:-0}` before `FIREFOX_PID` assignment, risking `kill 0` on early failure. Builder fixed cleanup to kill/wait only when PID variables are non-empty.
- Attempt 4：automated wrapper re-review returned `blocked` because review output did not contain the required structured result. Per independent review scope standard, this is automated review capability blockage, not a product candidate P1. Builder does not retry/reload or modify `.pi` / harness.
- Owner decision：Owner chose review artifact option 2 for R4 only: no distinct human reviewer is available; formal requirement for an effective post-fix Independent Re-review decision is explicitly modified/waived; Attempt 4 is not a review pass; Owner accepts the residual risk that no effective post-fix Independent Re-review decision exists. R4 closeout decision vocabulary is `owner_accepted_with_review_limitation`, not Independent Review `pass`.

## Owner acceptance gate

Owner has explicitly resolved the blocked re-review gate by accepting the documented limitation for R4 only. Owner accepted R4 product delivery and authorized acceptance commit on `2026-08-29T11:26:24Z`. Acceptance commit was created and post-commit verification passed. R4 is accepted-effective. Stop; do not start R5 automatically.
