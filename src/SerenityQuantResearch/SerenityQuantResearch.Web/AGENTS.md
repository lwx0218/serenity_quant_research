# SerenityQuantResearch.Web — AGENTS.md

## Scope

本文件约束：

`src/SerenityQuantResearch/SerenityQuantResearch.Web/`

尤其约束 research-facing UI / UX。

根 `AGENTS.md` 仍然适用；发生冲突时，research-facing product contract 以根 `AGENTS.md` 指定的 `docs/product/` 优先级为准。

## Mandatory Product Read

修改以下内容前必须阅读：

- research shell
- navigation
- CPO Explorer
- Company Pool
- Company Detail
- Research Workspace
- research-facing CSS / layout / interaction

阅读顺序：

1. `/AGENTS.md`
2. `/docs/product/README.md`
3. `/docs/product/experience-map.md`
4. task-specific page spec
5. approved / directional prototype
6. `/docs/product/visual-language.md`
7. `/docs/product/acceptance-contract.md`
8. `/operations/planning/research-experience-reboot.md`
9. `/operations/orchestration/research-experience-reboot.md`

## Research Shell Boundary

Research-facing shell 必须是轻量、独立的研究产品体验。

禁止把以下内容作为 primary research navigation：

- Dashboard
- Administration
- Language
- Users
- Roles
- Permissions
- template/demo navigation

这些能力可以继续作为 secondary admin routes 存在。

## CPO Explorer

不要把当前 legacy 3×3 SVG 当作批准的产品形态。

产品合同：

`/docs/product/cpo-explorer-spec.md`

必须保留的核心语义包括：

- Flat / 3D shared state
- component ↔ callout linked hover
- click selection
- same-object reset
- blank-area reset
- Esc reset
- contextual drawer
- correct Flat segmentation
- view-switch state preservation

## Company Research

不要把 SleekGrid-first 作为默认 Company Pool。

产品合同：

`/docs/product/company-research-spec.md`

批准层级：

```text
Card / List
→ Quick Drawer
→ Expand
→ Full Company Detail
```

Grid / table 可以作为后续专家能力或后台维护工具，但不能反向定义默认 research UX。

## Research Workspace

Workspace 是 knowledge-centric，而非新的 dashboard。

产品合同：

`/docs/product/research-workspace-spec.md`

v1 固定为 `read-only + linked-object-first`。只允许基于现有 component、technology/material、company、evidence 和 relationship 做只读 projection、derived backlinks、status 与 unresolved-question 展示。禁止新增 ResearchNote、OpenQuestion、Backlink、Graph、New Note、editor 或其他 persistence。Prototype 中的 Graph/New Note 是 deferred placeholder。

任何 persistent research writing 开始前，必须停止并就 identity、author attribution、audit ownership 和 all-admin Open Access 影响取得 Owner 决策。

## Visual Boundary

视觉规范：

`/docs/product/visual-language.md`

重点：

- light
- restrained
- technical
- calm
- precision annotation
- progressive disclosure
- minimal primary navigation

避免：

- generic admin dashboard
- neon / cyberpunk
- excessive cards
- excessive badges
- heavy permanent sidebars
- strong component outline highlights

## Prototype Boundary

Prototype 用于：

- interaction reference
- visual direction
- information architecture

Prototype 不等于 production code。

Pi 不应机械复制 prototype DOM / CSS。

Prototype 中任何 research mock data 都不自动成为正式数据。

## Research-data Safety

不得从 prototype 直接复制为正式事实：

- BOM %
- localization %
- supplier / customer claims
- market share
- company tier
- investment thesis
- technology-barrier score
- production / sampling status

没有 evidence contract 支持时使用 neutral state 或不展示。

## Backend Preservation

Research reboot 不意味着重写：

- migrations
- stable IDs
- domain relationships
- services
- evidence semantics
- audit / permission policies
- backend tests

优先 ADAPT，而不是无理由重建。

## Review Requirement

任何 research-facing UI phase 完成后必须提供：

- product-visible screenshots
- required viewport states
- interaction evidence
- automated-test result
- build result

先做 product review，再做 engineering completeness closeout。

具体见：

`/docs/product/acceptance-contract.md`

Canonical fixed-Round authority：`/operations/planning/research-experience-reboot.md`。不得自动连续推进多个 Round。
