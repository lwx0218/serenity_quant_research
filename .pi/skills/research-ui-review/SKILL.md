---
name: research-ui-review
description: 主动审阅 Serenity research-facing Web UI/UX。使用 pi-frontend-check 驱动 Chromium，跨 viewport 和交互状态检查视觉层级、布局几何、drawer/selection 同步、响应式、console/network 与产品合同；将 findings 按根因归并为 bounded 修复计划并有限复验。用于“review UI/UX”“检查前端页面”“主动找视觉/交互问题”“规划前端修复”等请求。
compatibility: Requires the project-local pi-frontend-check package and a running local Serenity Web URL.
license: Project-local
---

# Research UI Review

## 目的

主动发现问题，而不是等待 Owner 逐个指出。把浏览器观察、产品合同、精确几何断言和视觉判断合并成一次有边界的 review。

默认行为是 **review-only**：不修改业务代码，不写 Markdown review bundle，不创建 Fleet Session。只有 Owner 明确要求修复时才进入 bounded fix。

## Capability check

开始前确认以下工具已出现在当前 Pi Session：

- `frontend_open`
- `frontend_act`
- `frontend_screenshot`
- `frontend_console`
- `frontend_eval`

若缺失，说明项目 package 已安装但当前 Session 需要 `/reload` 或重启 Pi。不要退回到让 Owner 人工逐项找 bug，也不要自动安装其他浏览器 package。

## Source of truth

审阅 research-facing 页面时按项目合同读取：

1. 根 `AGENTS.md` 与适用 scoped `AGENTS.md`
2. `docs/product/README.md`
3. `docs/product/experience-map.md`
4. task-specific page spec
5. approved/directional prototype（仅作交互/视觉参考）
6. `docs/product/visual-language.md`
7. `docs/product/acceptance-contract.md`
8. current implementation

Prototype mock data 不是 research facts。Review 不得建议新增未批准 primary navigation、permanent sidebar、schema、research claims 或 persistent writing。

## Invocation contract

解析用户输入：

- URL：显式 URL 优先；否则使用已运行的 `http://127.0.0.1:5000`。
- 页面：默认只审当前页面；“全站”才扩到最多 3 个 primary research routes。
- 模式：
  - `standard`：默认。
  - `thorough`：补充 keyboard、focus、reset、loading/empty/error、long content。
  - `fix`：仅 Owner 明确要求时；先完成独立 review，再改代码。

CPO 默认 viewport：

- `1440 × 980`
- `1920 × 1080`
- `2504 × 1178`

项目 acceptance 最低要求 1440/1920；2504 用于发现超宽屏内容小岛、标题/画布漂移和异常 gutters。

## Standard workflow

### 1. Read and open

读取适用产品文件与页面实现。调用 `frontend_open`，等待页面 ready selector（CPO 使用 `#cpo-explorer-app[data-ready="true"]`）。同时检查首屏截图和 console health。

### 2. Establish idle geometry

在每个 viewport：

1. `frontend_screenshot` 调整 viewport 并捕获 idle。
2. 读取 `scripts/generic-layout-probe.js`，把完整 IIFE 作为 `frontend_eval.expression` 执行。
3. 对 CPO 再读取并执行 `scripts/cpo-baseline-probe.js`；它把当前 workbench/canvas/stage/title 几何保存到页面内 `window.__researchUiReview.cpoBaseline`。
4. 视觉检查标题、内容边界、左右 gutters、空白、主画布占比、文字层级和 control alignment。

不要仅凭 screenshot 猜尺寸；几何结论必须引用 probe 数值。

### 3. Exercise state matrix

CPO 至少覆盖：

| View | State | Required observation |
|---|---|---|
| Flat | idle | whole system、all callouts、drawer hidden |
| Flat | hover | component ↔ callout 同步、moderate de-emphasis |
| Flat | selected | drawer open、selected context 同步、canvas invariant |
| 3D | idle | exploded composition readable |
| 3D | hover | linked focus |
| 3D | selected | drawer open、canvas invariant |
| switch | selected Flat ↔ 3D | stable ID 与 drawer context 保留 |
| reset | Esc / close / blank / same object | overview restored |

优先通过稳定 ID 定位，例如：

```text
.cpo-component[data-component-id="cpo.mod.thermal"]
.cpo-callout[data-component-id="cpo.mod.thermal"]
```

SVG callout group 的 bounding box 包含 connector，中心点可能落在未绘制区域。真实 pointer 验证应点击可见 `.cpo-callout-card` 或 component geometry，不要把自动化工具点击 group 中心失败误报为产品 defect。

选中后等待约 360ms 让 major transition 完成，截图，再读取并执行 `scripts/cpo-selected-probe.js`。

### 4. CPO owner invariants

除 approved product spec 外，当前 Owner 明确要求以下 layout/interaction invariants：

1. **标题动态跟随页面边界**：`.cpo-page-heading` 与 `.cpo-explorer-app` 主左边界保持一致；超宽屏不得出现标题滞留在旧 content container 而画布向外扩展。
2. **空闲画布利用可用宽度**：左右 outer gutters 视觉平衡；2504 下不得因硬 `max-width` 形成明显单侧空白或“内容小岛”。
3. **选中不压缩画布**：drawer 打开前后 `.cpo-explorer-workbench`、`#cpo-canvas-frame` 与 `.cpo-viewport-stage` 的最终 rect 不应改变超过 2px。画布只随 browser viewport 动态调整。
4. **drawer overlay slide-in**：drawer 从右侧滑入/滑出，不通过新增 grid column 挤压 workbench；最终应贴合 workbench 的 top/right/bottom（建议误差 ≤ 8px）。
5. **同步**：`data-selected`、active component、active callout、state line、drawer title 和 view switch 共享同一 stable component identity。
6. **非空打开**：点击后 drawer 首个可见 frame 至少显示 selected component identity 或明确 loading context，不得先弹出无身份空白面板。

如果 product spec 的“may temporarily reduce usable canvas space”与本次 Owner 明确偏好冲突，以本次 Owner 的固定画布 + overlay drawer 决策为当前 review expectation；不要静默改回压缩布局。

### 5. Visual inspection

每张关键截图必须由 vision-capable model 实际判断：

- objective / IA / current context / next action 是否清楚；
- 标题、workbench、state line、canvas 与 drawer 是否在同一几何系统；
- 是否存在异常空白、内容小岛、偏心、裁切、重叠、drawer 上下错位；
- unrelated dim/blur 是否适中；
- focus/selected 是否清楚但没有强蓝 component outline；
- drawer 是否像 contextual dossier，而不是 permanent admin sidebar；
- 是否出现 mock/research-fact 泄漏。

自动 probe 不能替代视觉判断；视觉判断也不能替代精确 geometry/state assertions。

### 6. Console and network

调用 `frontend_console`：

- errors；
- warnings；
- failed requests；
- HTTP 4xx/5xx。

清洁 console 只证明没有 runtime error，不代表 UX 正确。

### 7. Source mapping and root-cause grouping

把每个 confirmed finding 映射到 source file/selector。相同根因只保留一条，例如：

- `grid-template-columns` 同时造成 drawer 挤压、画布缩放、callout 漂移 → 一个 interaction-layout 根因；
- page heading 和 app 使用不同 max-width/gutter system → 一个 shell-alignment 根因。

不得把一个根因在 3 个 viewport、6 个状态下复制成 18 条 bug。

## Findings and plan output

默认只在聊天输出，不写 durable report：

```text
Decision: changes requested | approved with minor findings | approved

Root-cause findings
1. [P0/P1/P2] category — observed evidence — affected states/viewports — source

Bounded repair batch
- objective
- files likely touched
- acceptance assertions
- verification matrix
- explicitly out of scope
```

优先级：

- `P0`：核心路径不可用、错误 research context、critical accessibility。
- `P1`：主要 interaction/layout 违约，广泛影响使用。
- `P2`：明显但不阻塞的视觉层级或 polish。

## Bounded fix loop

仅当 Owner 明确要求修复：

1. 选择一个 root-cause batch，通常最多 1–3 个高度相关根因。
2. 修改最小必要文件；不扩大到 Company/Workspace、schema、research data 或全量迁移。
3. 重跑失败断言和相同 state/viewport screenshot。
4. 最多进行 2 次 fix → verify 循环。
5. 第二次仍失败、出现 product ambiguity 或修复引发新 P0/P1 时停止，向 Owner 汇报证据与阻塞点。

禁止无限 polish、自动连续开 Session、自动扩大 scope 或用新增截图数量代替验收质量。

## Existing automated tests

现有 `tests-ui/run-browser-smoke.sh` 是重要 engineering evidence，但不是完整视觉审阅。它通过时仍需检查：

- heading/workbench dynamic alignment；
- idle 与 selected 的 canvas rect invariant；
- drawer overlay positioning 和 top/right/bottom alignment；
- 超宽屏 whitespace balance；
- screenshot visual hierarchy。

可复用 smoke 中稳定 ID、state matrix 和 reset assertions，不要把旧截图当当前 live 页面证据。
