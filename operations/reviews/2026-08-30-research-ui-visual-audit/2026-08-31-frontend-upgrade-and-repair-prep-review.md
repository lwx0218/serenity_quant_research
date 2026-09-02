# Frontend Upgrade And Repair Preparation

## Metadata

- Project: serenity_quant_research
- Task: Research UI frontend upgrade recommendation and repair-session preparation
- Timestamp (UTC): 2026-08-31T07:49:56Z
- Owner: project owner
- Route: review-only
- Source of truth: operations/reviews/2026-08-30-research-ui-visual-audit/2026-08-30-research-ui-visual-audit-review.md

## Purpose

本文补充记录 Owner 确认的前端升级方向：

> research-facing 前端渐进迁移到 React + Vite；复用 Vibe-Research 的架构经验，但重新实现符合本项目产品合同的视觉系统。

本文件是视觉巡检 bundle 的 repair-preparation addendum，不是 business-code implementation，不改变 canonical Plan、accepted Round、research facts、evidence/review/audit semantics，也不自动启用 formal fixed-Round。

## Recommendation

建议采用 **Serenity 后端保留 + research-facing 前端渐进升级**。

目标架构：

```text
ASP.NET Core / Serenity
├── services
├── permissions / audit
├── migrations / seed
├── admin maintenance
└── research API
        ↓
React + Vite Research App
├── ResearchShell
├── CPO Explorer
├── Company Pool / Company Detail
├── Research Workspace
└── later Evidence / Review / Conclusion / Report
```

## Why Upgrade Is Justified

当前 research-facing UI 主要是：

```text
Razor .cshtml
+ page-local TypeScript DOM orchestration
+ page-local CSS
+ inline SVG for CPO Explorer
```

这已足够交付 vertical slice，但视觉巡检暴露了长期扩展风险：

1. CPO Flat / 3D / callout / selected drawer 状态强耦合，布局逻辑分散在 SVG 坐标、CSS 固定值和 TypeScript DOM class 中。
2. CPO、Company、Workspace 各自定义 max-width、drawer、card、badge、radius、shadow、semantic color，跨页面像三个不同产品。
3. Drawer 使用 full-height fixed overlay，不参与 shell layout，导致 topbar 覆盖、主图偏心和背景层级不清。
4. 响应式主要靠固定高度、固定 viewBox、max-width 和少量 media query，未形成 viewport/layout primitives。
5. 后续 Evidence → Review → Conclusion → Report 若继续堆在 page-local DOM/CSS 上，状态和视觉一致性成本会继续上升。

因此，若目标只是修十个视觉问题，现有栈可以修；若目标是完整研究工作台，前端需要升级。

## What To Learn From Vibe-Research

可借鉴：

- React + Vite 的独立前端开发与构建边界；
- `Layout` / Router / page-level shell 的组织方式；
- component primitives，如 PageHeader、Drawer、Card、ErrorBoundary、AI Dock；
- page context / shared state 的登记机制；
- Tailwind + CSS variables 的 design-token 方法；
- local browser UI 与 backend API 分离的工程体验。

不可照搬：

- 暗色暖橙玻璃视觉；
- 永久左侧 heavy sidebar；
- 十几个一级导航入口；
- glow-heavy / dashboard-home 风格；
- `max-w-6xl` 中央小岛式超宽屏行为；
- Vibe-Research 的金融 agent IA。

本项目仍以 `docs/product/` product contract 为准：primary navigation 仅 `CPO Explorer`、`Company Pool`、`Research Workspace`；CPO Explorer 不得新增永久 research sidebar。

## Migration Strategy

采用渐进式，不做 big-bang rewrite。

### Step 1 — Shared visual/layout contract

- 建立 research-facing design tokens：color、spacing、radius、shadow、typography、badge、semantic states。
- 建立 `ResearchShell` / `PageFrame` / `ContextDrawer` / `ViewportCanvas` 等 primitives。
- 先修 CSS/layout contract，避免 React migration 复制旧问题。

### Step 2 — CPO Explorer pilot

优先迁移或重构 CPO，因为 V-001～V-005 均集中在这里。

目标：

- responsive viewport stage；
- explicit annotation gutters；
- Flat / 3D shared selection store；
- drawer-aware re-centering；
- accessible focus 不再用 SVG group 大包围框；
- selected state 保留空间关系而非过度 blur。

### Step 3 — Shared drawer model

统一 CPO Drawer 与 Company Quick Drawer 的 shell relationship：

- drawer 不覆盖 topbar；
- foreground/background 层级一致；
- 主内容按 available area 调整；
- Esc / outside / close 行为一致；
- mobile / narrow desktop fallback 明确。

### Step 4 — Company pages

- Company Pool filters 降噪；
- gap / candidate / verified 对象建立扫描层级；
- Quick Drawer 保持 triage，不变成窄版 Full Detail；
- Full Detail 减少 boxed section，转向 document-like reading rhythm。

### Step 5 — Workspace

- 中心 current object 优先；
- left/right rails bounded-height / sticky / independent-scroll 策略明确；
- right context 减少 card/pill 噪音；
- 双语长标签、linked object、evidence status 统一密度规则。

### Step 6 — Integrated validation

- 1440、1920、2504 三档截图；
- CPO idle / selected / view switch；
- Company card / list / drawer / detail；
- Workspace component / company top and mid-scroll；
- existing .NET tests、npm build、browser smoke 保持通过。

## Candidate Development Surfaces

后续修复 Session 可能触碰：

```text
src/SerenityQuantResearch/SerenityQuantResearch.Web/package.json
src/SerenityQuantResearch/SerenityQuantResearch.Web/tsconfig.json
src/SerenityQuantResearch/SerenityQuantResearch.Web/tsbuild.js or Vite config if introduced
src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_Layout.cshtml
src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/**
src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/**
```

Protected / avoid by default：

```text
Migrations/**
data/seeds/**
Research evidence semantics
audit / permission policy
admin maintenance routes
primary navigation scope
```

## Suggested Next Session

Recommended session name:

```text
build-research-ui-visual-repair
```

Suggested first implementation boundary:

```text
CPO layout foundation + selected-state repair only.
```

Do first before broader React/Vite migration:

1. Fix CPO responsive canvas sizing and annotation gutters.
2. Fix selected-state drawer layout and re-centering.
3. Fix SVG focus outline and dimming levels.
4. Regenerate CPO screenshot evidence at 1440 / 1920 / 2504.

Non-goals for the first repair pass：

- no research fact / seed / schema changes；
- no new primary navigation；
- no Workspace writing / Graph / New Note；
- no full React rewrite unless a separate implementation plan is accepted during the repair session；
- no copying Vibe-Research visual theme.

## Copyable Handoff Prompt

```text
本 Session 处理 research-facing UI 修复准备。请读取：

1. AGENTS.md
2. src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md
3. docs/product/README.md
4. docs/product/experience-map.md
5. docs/product/cpo-explorer-spec.md
6. docs/product/visual-language.md
7. docs/product/acceptance-contract.md
8. operations/reviews/2026-08-30-research-ui-visual-audit/2026-08-30-research-ui-visual-audit-review.md
9. operations/reviews/2026-08-30-research-ui-visual-audit/2026-08-31-frontend-upgrade-and-repair-prep-review.md

目标：先做 CPO Explorer 视觉修复，不做业务数据/schema/research semantics 改动。

优先修：
- V-001 CPO 主画布响应式增长平台；
- V-002 右侧 callout 覆盖主图、左右不对称；
- V-003 selected state drawer 不参与布局、主图偏心；
- V-004 SVG group focus 大矩形；
- V-005 selected state 弱化过度。

实现原则：可以借鉴 Vibe-Research 的组件化、shell、state、design-token 思路，但不得照搬其暗色玻璃视觉、heavy sidebar 或 IA。Serenity 后端、research service、stable IDs、permissions/audit、seed/migrations 不动。

验证：至少运行 npm build、相关 UI unit/browser smoke；重新生成 CPO Flat/3D idle/selected/view-switch 截图，覆盖 1440、1920、2504。最终用中文总结 changed files、截图 evidence、验证结果和剩余 findings。
```

## Decision

- Direction accepted for preparation: **learn Vibe-Research architecture, not its visual/IA**。
- Implementation start condition: 新 Session 明确接手 repair boundary 后执行。
- Current Session status: 记录 / evidence / preparation only；不修改业务代码。
