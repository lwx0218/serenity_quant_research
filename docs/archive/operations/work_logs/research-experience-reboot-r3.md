# Research Experience Reboot — R3 工作日志

Round: R3 — CPO Explorer Vertical Slice
Plan: `operations/planning/research-experience-reboot.md`
Git baseline: `67e9aed979a6c246504b4a97e5cc70300e6c6e49`

## Status

- Round：`R3 — CPO Explorer Vertical Slice`
- Primary session：`R3-cpo-explorer-vertical-slice`
- Start：Owner 在 R2 accepted-effective 后启动 R3。
- 当前状态：`accepted_effective`
- 前序状态：R1、R2 accepted-effective。

## Boundary

R3 目标是交付一个 production-quality SiPh PIC Flat/3D Explorer vertical slice。

### In scope delivered

- 同一 SiPh PIC stable ID：`cpo.mod.pic` 在 Flat / 3D 间保持 selected。
- component / callout hover 与 click 等价；hover state 明确显示 `hover preview`，不再误报 selected。
- Flat SiPh hit region 由真实可见几何承担；browser test 断言 `getBBox < 220×110`，无 board-sized invisible region。
- 3D selected state 中 callout card 不被 drawer 覆盖；browser test 用 `elementFromPoint` 验证 callout 是 top-most pointer target；3D callout geometry 已左移，drawer-open stage transform 从过度 `translateX(-440px) scale(.92)` 收敛为 `translateX(-250px) scale(.94)`。
- same-object、blank canvas、Esc、close reset 均通过 browser assertion，并生成 reset sequence screenshots。
- keyboard selection：Tab-focusable component/callout + Enter / Space 选择，通过 unit/browser assertion，并生成 keyboard sequence screenshots。
- drawer 展示真实 child parts：`cpo.part.pic.modulator`、`cpo.part.pic.wdm`、`cpo.part.pic.waveguide-coupler`。
- technology context 只展示现有 explicit part→technology link：`硅光集成`。
- material 显式显示 `暂无已核验材料数据`；未渲染 `Silicon`、`SiN`、`LNOI` 等示例 material chip。
- company preview 使用安全空状态：当前 SiPh PIC 子部件没有显式 company exposure，未从类别、图形位置或 design reference 推导供应关系。
- 若任何子部件研究链读取失败，UI 明确显示 `unknown`/读取失败，不把服务失败折叠为“尚无技术链接 / Related Companies (0) / 无 evidence”。
- 1440px / 1920px Flat / 3D idle、hover、selected、view-switch preserved、reset 与 keyboard sequence screenshots 已生成。
- Manual spawned Independent Review 曾完成 pass；随后外部 wrapper certification review 对当前 R3 candidate 打出 P1=2/P2=2，Builder 复核后确认 P1 属实并在同一 R3 中修复。
- 最新 Fix/Verify：服务失败不再显示成 confirmed empty；R2 browser regression 覆盖已恢复；3D recenter 视觉过度已收敛；治理 dirty state 已在本日志分类。
- 最新 automated validation：PASS；更新后的 `harness_run_independent_review` wrapper 已生效并返回 `pass`，P0=0、P1=0、P2=1；P2 已处置。

### Non-goals maintained

- 未实现 full component coverage；其他器件仅为空间上下文，不作为 R3 验收交互对象。
- 未 redesign Company Pool；仅提供带 context query 的 Company Pool link。
- 未新增 WebGL、schema、migration、seed、persistent data 或大型前端框架。
- 未复制 prototype/Gemini research claims、BOM、国产化率、tier、thesis、supplier/customer claims。
- 未改 PartResearch service；R3 使用既有 `ListParts` 与 child `RetrieveCompleteChain` read projection。

## Candidate scope

### Product/runtime candidate paths

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramIndex.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.css`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/PartSelectionState.ts`

### Test / evidence candidate paths

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh`
- `operations/reviews/research-experience-reboot-r3-screenshots/*.png`
- `operations/work_logs/research-experience-reboot-r3.md`
- `operations/reviews/research-experience-reboot-r3-independent-review.md`

## Context scope

- `AGENTS.md`
- `operations/orchestration/independent-review-and-round-scope-standard.md`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md`
- `docs/product/README.md`
- `docs/product/experience-map.md`
- `docs/product/cpo-explorer-spec.md`
- `docs/product/prototypes/cpo-explorer-v0.4.html`
- `docs/product/prototypes/gemini-cpo-explorer-design-reference.html`（design-only）
- `docs/product/visual-language.md`
- `docs/product/acceptance-contract.md`
- `docs/research-baseline/evidence-contract.md`
- `operations/planning/research-experience-reboot.md`
- `operations/orchestration/research-experience-reboot.md`
- `operations/reviews/reboot-p3-code-disposition.md`
- `operations/work_logs/research-experience-reboot-r2.md`
- `operations/reviews/research-experience-reboot-r2-independent-review.md`

## Environment / dirty-worktree scope

R3 start status from handoff session snapshot：

```text
HEAD: 67e9aed979a6c246504b4a97e5cc70300e6c6e49
 M operations/planning/research-experience-reboot.md
?? operations/reviews/research-experience-reboot-r3-independent-review.md
?? operations/work_logs/research-experience-reboot-r3.md
```

Current classification：

- `operations/planning/research-experience-reboot.md`：pre-existing/context dirty state from R3 handoff; Builder did not edit during R3 implementation.
- `operations/orchestration/governance-maintenance-backlog.md`：governance maintenance dirty state from治理层下发/认证记录；不属于 R3 product candidate。
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/*` listed above：R3 product candidate.
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs` and `run-browser-smoke.sh`：R3 test/evidence candidate.
- `operations/work_logs/research-experience-reboot-r3.md`、`operations/reviews/research-experience-reboot-r3-independent-review.md`、`operations/reviews/research-experience-reboot-r3-screenshots/`：R3 durable evidence.

Protected surfaces preserved：migrations、seed factual state、evidence policy、Company redesign surfaces、`.pi/` / harness governance tooling。

## Implementation notes

1. `CpoDiagramIndex.cshtml` replaced the legacy 3×3 diagram surface with a light technical Explorer shell for the SiPh PIC vertical slice. It contains separate Flat and 3D SVG scenes, a visible view switch, one validated interaction object (`cpo.mod.pic`), and a hidden-until-selection drawer.
2. `CpoDiagramPage.ts` binds component and callout as the same canonical object, keeps shared state across both views, implements same-object / blank / Esc / close reset, and loads real SiPh child parts from `PartResearchService.ListParts` plus child research via existing `RetrieveCompleteChain`.
3. `PartSelectionState.ts` contains `viewMode`, `togglePartSelection`, `switchExplorerView`, and interaction-state helpers so selected state survives view switch and same-object click unlocks.
4. `CpoDiagramPage.css` uses a light, restrained, annotation-led visual style and drawer dossier language; component geometry does not use a strong blue outline. Keyboard focus on component uses a neutral dashed outline; callout/control focus remains visible.
5. The drawer is initially `hidden` + `aria-hidden="true"` so closed off-screen controls are not keyboard-focusable before selection.
6. Retrieval failures from child `RetrieveCompleteChain` calls are preserved as `research_chain_unknown` and rendered as unknown states for technology/company/evidence instead of confirmed-empty language.
7. `run-browser-smoke.sh` writes screenshot evidence to `operations/reviews/research-experience-reboot-r3-screenshots/`, verifies keyboard focus before dispatching Enter / Space, and restores R2 browser regression checks for Company Pool at 1440/1920, Workspace read-only placeholder, secondary admin route, and admin service reachability.
8. No PartResearch service/view-model change was needed; therefore no `.NET` service test was added in R3.

## Manual spawned Pi review cycle

Because `harness_run_independent_review` wrapper was blocked, Owner instructed this session to use a manual spawned Pi process and not to modify `.pi` / harness, not to use human review, and not to use `/new`.

### Manual review attempt 1

- Temporary copied review root：`/tmp/sqr-r3-manual-spawn-review-pbGjI2`
- PID：`4141269`
- Invocation：`pi --no-session --no-approve --no-extensions --no-skills --no-prompt-templates --no-themes --no-context-files --tools read,grep,find,ls --provider openai-codex --model gpt-5.6-sol -p <.review/prompt.txt>`
- Exit：`0`
- stderr：empty
- Structured marker：`HARNESS_REVIEW_RESULT` present
- Decision：`changes_required`
- Findings：P0=0, P1=3, P2=3

P1 findings and Builder fixes：

1. **P1：3D selected callout 被 drawer 覆盖**。Fix：3D drawer-open stage 使用更强 recenter；browser test 增加 `elementFromPoint`，证明 selected 3D callout card 完全在 drawer 左侧且为 top-most pointer target。
2. **P1：hover 被 state line 误报为 selected**。Fix：`updateStateLine` 区分 `selectedId` 与 `hoveredId`；hover 显示 `hover preview`，只有 locked selection 显示 `selected`。
3. **P1：缺少 reset / keyboard product-visible sequence evidence**。Fix：browser smoke 新增 reset 与 keyboard screenshots：blank reset、Esc reset、same-callout reset、close reset、Enter selected、Space selected。

P2 findings and Builder dispositions：

1. **P2：Selected Flat screenshot 在 drawer transition 完成前捕获**。Disposition/fix：browser smoke 在 selected/view-switch screenshots 前等待 CSS transition；截图重新生成。
2. **P2：production UI 暴露 R3/test/seed/mock 语言**。Disposition/fix：移除 user-visible R3/test framing，seed/mock/prototype 文案改为“现有研究目录 / 示例数据不作为事实”。
3. **P2：browser coverage overstates callout hover and Space coverage**。Disposition/fix：browser smoke 增加 callout hover assertion 与 Space keyboard selection assertion。

### Automated validation after fixes

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

R3 browser smoke assertions now cover：

- research shell nav remains exactly `CPO Explorer`、`Company Pool`、`Research Workspace` and no Serenity sidebar leaks into root Explorer.
- Flat / 3D view switch does not reset `cpo.mod.pic` selection.
- component hover and callout hover both focus the paired object in Flat and 3D, and hover is not announced as selected.
- component click, callout click, keyboard Enter, keyboard Space, same-object/callout click, blank canvas click, close button, and Esc reset/selection behavior.
- selected 3D callout is not drawer-covered and remains top-most pointer target.
- drawer contains real child parts and explicit material gap text.
- `硅光集成` appears only as existing part→technology context; example material chips do not appear as badges.
- related companies show safe empty state because no explicit SiPh exposure exists.
- child research-chain failure semantics are covered by unit test helper: failure renders as unknown rather than confirmed empty.
- R2 regression restored: Company Pool shell at 1440/1920, Workspace read-only/no deferred controls, secondary admin route shell separation, and admin service reachability.
- Flat hit region is bounded to real SiPh geometry, and selected component geometry does not use the accent as a strong blue outline.

## Product-visible evidence

Screenshots generated by `npm run test:ui:browser` and PNG palette-optimized with dimensions preserved：

- `operations/reviews/research-experience-reboot-r3-screenshots/idle-flat-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/hover-flat-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/selected-flat-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/reset-blank-flat-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/idle-3d-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/hover-3d-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/selected-3d-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/view-switch-preserved-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/reset-esc-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/sequence-component-selected-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/sequence-same-callout-reset-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/sequence-callout-selected-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/sequence-close-reset-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/sequence-keyboard-enter-selected-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/sequence-keyboard-esc-reset-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/sequence-keyboard-space-selected-1440.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/idle-flat-1920.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/hover-flat-1920.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/selected-flat-1920.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/reset-blank-flat-1920.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/idle-3d-1920.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/hover-3d-1920.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/selected-3d-1920.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/view-switch-preserved-1920.png`
- `operations/reviews/research-experience-reboot-r3-screenshots/reset-esc-1920.png`

Total screenshot size after latest optimization：`1523255` bytes.

Manual visual inspection by Builder：`hover-flat-1440.png` shows hover preview, not selected；`selected-3d-1440.png` shows callout visible left of the drawer；`sequence-keyboard-space-selected-1440.png` shows keyboard selection sequence evidence.

## Candidate hashes before final manual spawned review

```text
d077276fb7651601e9bbd6d285fd760b922804a0b72d4bbd93c5520c0356fadb  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramIndex.cshtml
713c5affcd2788f43325da14721f6cd0dbf57a900c0ac3c11c3644c1f10b928b  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.css
1540c1137dd108380010d7593c44afa3b99cdf7b86da7172315886dc0e22677f  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.ts
a1d766d139ac31594fe632cd426a914dc60f2f4b64713f56cb834832bb517ace  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/PartSelectionState.ts
bd870e3823c6af82077b793b19b7b57ad7c4193cc540dcc8184ce6c497dd0513  src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/PartSelectionState.test.mjs
a1681d5bb42788216608eeb9e6fca6b1b91a3656d7cbbec7282be0e608a43d5a  src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh
```

## Independent Review status

- Required mode：`spawned_pi_process`
- Artifact：`operations/reviews/research-experience-reboot-r3-independent-review.md`
- Current state：updated wrapper Independent Review completed; decision `pass`; P0=0, P1=0, P2=1 dispositioned.

`harness_run_independent_review` wrapper attempts remain recorded in `operations/reviews/research-experience-reboot-r3-independent-review.md` as blocked capability evidence. Per Owner instruction, Builder did not retry wrapper after the approved manual-spawn path, did not modify `.pi` / harness, did not use human review, and did not use `/new`.

### Wrapper Independent Review final result

- Updated wrapper review：decision `pass`; P0=0, P1=0, P2=1; Candidate immutable=yes。
- P2：R3 evidence artifacts contained stale/contradictory status and validation metadata. Disposition/fix：this work log and `operations/reviews/research-experience-reboot-r3-independent-review.md` were reconciled to record latest status, UI unit count `13`, screenshot size `1523255` bytes, and wrapper review pass.
- Manual spawned review history remains recorded as audit trail, but current acceptance-bearing review evidence is the updated wrapper `harness_run_independent_review` pass.

## Owner acceptance gate

- Acceptance time：`2026-08-29T08:59:54Z`
- Owner response：`验收`
- Accepted scope：R3 CPO Explorer Vertical Slice candidate as documented above, including wrapper Independent Review `pass` and fixed P2 evidence reconciliation.
- Commit authorization：Owner replied `授权commit`。
- Acceptance commit：completed by Builder after Owner authorization。
- Post-commit verification：PASS。

R3 is accepted-effective. Required next gate：stop；R4 requires separate Owner start decision and handoff. R4 不得自动启动。
