# Serenity Quant Research — Product Reboot Baseline

## Metadata

- Project: serenity_quant_research
- Document type: index
- Status: superseded
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: AGENTS.md

## Status

- Product state: **Approved Research Experience Reboot baseline**
- Current engineering state: R1–R5 accepted-effective; Active Round none; R6 remains pending and requires a separate Owner start decision
- Current product/UI state: **P0–P3 research-facing UI baseline is superseded**
- Legacy P4: **paused**
- Current reboot acceptance boundary: Explorer → Company → read-only Workspace
- Long-term product loop retains: Workspace → Evidence → Review → Conclusion → Report
- Approved CPO Explorer interaction reference: `prototypes/cpo-explorer-v0.4.html`
- Approval meaning: **interaction direction approved; final visual design is not yet approved and is not an R1–R5 blocker**

This document is the highest-level product source of truth for the rebooted research experience.

## 1. Product North Star

`serenity_quant_research` is a finance-first industrial-chain research workstation.

Its purpose is to let an investor or analyst begin with a **real physical product or system**, understand what it is made of, move from physical components into materials and technologies, and then identify and research the companies exposed to those components.

The core exploration loop is:

```text
Physical Product
    ↓
Component
    ↓
Subcomponent / Material / Technology
    ↓
Related Companies
    ↓
Research
```

The product should feel like an **interactive research atlas / technical research workstation**, not like an administration system.

## 2. What This Product Is Not

The research-facing product is not:

- an ERP
- a CRM
- an admin dashboard
- a generic BI dashboard
- a CRUD management console
- a market-data terminal
- a trading system
- a spreadsheet-first database browser

The following patterns must not define the main research experience:

- Serenity default dashboard layout
- persistent administration sidebar
- SleekGrid-first primary research pages
- large sets of CRUD filters
- language / role / permission management in primary navigation
- generic metric-card dashboards
- duplicated grid + fallback table as simultaneous default content
- technology-demo visualizations with no clear research workflow

## 3. Relationship to Serenity Framework

Serenity remains useful as infrastructure.

It may continue to provide:

- ASP.NET Core application host
- service layer
- database access
- permissions
- audit
- migrations
- administrative maintenance tools
- internal data-management workflows

However:

> **Serenity is an implementation base, not the product design system.**

The research-facing UI must have its own interaction model and visual language.

Existing administration capabilities may remain available through secondary or hidden routes, but they must not shape the primary research experience.

## 4. MVP Product Structure

The rebooted MVP should contain only the minimum number of primary product areas required to close the research loop.

### 4.1 CPO Explorer

Primary entry point.

Purpose:

- understand the physical composition of a CPO system
- switch between a flat system view and a 3D exploded view
- explore components through hover and selection
- drill down into subcomponents and materials
- discover related companies

### 4.2 Company Research Pool

Card-first company exploration.

Purpose:

- browse companies in the context of components / materials / chain roles
- preserve the research context coming from CPO Explorer
- filter without turning the page into a database-admin form
- review one company at a time through Card/List → Quick Drawer → Full Detail；Company Comparison 已延期，不属于当前 MVP

### 4.3 Research Workspace

Research Workspace is now accepted as a separate primary product area.

It is **knowledge-centric**, not company-detail-centric.

Purpose:

- maintain linked research objects
- navigate components, technologies, companies, evidence, and research notes
- preserve backlinks and research context
- keep open questions distinct from verified conclusions

Its current directional reference is:

`docs/product/prototypes/research-workspace-v0.1.html`

Workspace v1 is `read-only + linked-object-first`. It may project existing component, technology/material, company, evidence, relationship, derived backlink, status, and unresolved-question data. It does not add ResearchNote, OpenQuestion, Backlink, Graph, or editor persistence. Prototype `Graph` and `New note` controls are deferred placeholders, not v1 acceptance requirements.

## 5. Primary Navigation Principle

Current working model:

```text
CPO Explorer
Company Pool
Research Workspace
```

`Company Detail` is reached from Company Pool and is not a top-level navigation item.

Primary research navigation must not expose:

- Administration
- Language management
- Users
- Roles
- Permissions
- generic Dashboard
- unrelated template modules

## 6. CPO Explorer Product Principle

CPO Explorer is not a static diagram page.

It is the main research entry surface.

The same domain component must be represented consistently across:

- Flat View
- 3D Exploded View
- callout annotation
- research side panel
- related-company context

These are different representations of one research object, not separate pieces of UI.

The approved interaction baseline is defined in:

`docs/product/cpo-explorer-spec.md`

## 7. Product Experience Principles

### 7.1 Explore first, manage later

Primary research workflows should optimize for understanding and discovery.

Data maintenance, administration, review tooling, and governance should remain secondary.

### 7.2 Progressive disclosure

Do not show all available information at once.

Reveal information in layers:

```text
overview
→ hover context
→ selected object
→ subcomponent / material
→ company
→ deeper research
```

### 7.3 Preserve research context

Navigation should answer:

> “What was I researching, and why am I now looking at this company?”

Component, material, company, and comparison transitions should preserve this context whenever possible.

### 7.4 Reduce before adding

A new panel, tab, filter, badge, metric, or page requires a clear research reason.

Completeness is not a sufficient reason to add UI.

### 7.5 Visual hierarchy before information density

Information density is valuable only when hierarchy is obvious.

The interface should feel calm, technical, and deliberate rather than crowded.

## 8. Current Product Decisions

The following decisions are currently accepted:

1. CPO Explorer has **Flat View** and **3D Exploded View**.
2. Both views share the same component identity and selection state.
3. Component and callout are two representations of the same interaction object.
4. Hover creates focus through elevation / clarity and de-emphasizes unrelated objects.
5. Component bodies do not require blue outline highlights.
6. Callout cards and connector lines may use restrained accent highlighting.
7. Clicking a component or callout locks selection.
8. Clicking the same selected object again unlocks it.
9. Clicking empty canvas space unlocks the current selection.
10. `Esc` unlocks the current selection.
11. Research detail is not permanently visible.
12. The research panel slides in only after selection.
13. The panel shows subcomponents, materials, and related companies.
14. Company Research Pool should be **card-first**, not SleekGrid-first.
15. Administration and language management are not part of the current research MVP.

## 9. Explicitly Deferred

The current Research Experience Reboot intentionally pauses or defers the following without cancelling the complete product loop:

- Evidence Timeline / Evidence Review product UI
- conclusion publishing UX
- report-generation UX
- Company Comparison
- Workspace writing, New Note, Graph, and persistent knowledge entities
- multi-language product navigation
- research-facing administration
- heavy permission-management UI
- advanced organization-management UI
- real-time market features
- trading
- backtesting
- CAD / full engineering BOM
- complex WebGL / rotatable 3D

Existing backend work related to evidence, audit, permissions, and domain relationships may remain reusable even when its product UI is deferred.

## 10. Source-of-Truth Priority

For product-facing implementation, use this priority order:

```text
1. docs/product/README.md
2. docs/product/experience-map.md
3. page-specific product spec
4. approved HTML prototype
5. docs/product/visual-language.md
6. docs/product/acceptance-contract.md
7. `operations/planning/research-experience-reboot.md`
8. `operations/orchestration/research-experience-reboot.md`
9. current implementation
10. legacy P0–P3 product plans and work logs
```

When current code conflicts with an approved reboot product document, the current code does not define the requirement.

Legacy P0–P3 documents remain valuable as engineering history and technical evidence, but they are no longer authoritative for research-facing UI direction.

## 11. Prototype Policy

HTML prototypes are part of the product decision process.

They validate:

- information architecture
- interaction
- layout direction
- navigation
- progressive disclosure
- page-to-page continuity

They are **not automatically production code**.

Pi should implement the approved behavior and design intent using the production architecture rather than blindly copying prototype markup.

## 12. Current Reboot Sequence

```text
[✓] identify product drift
[✓] CPO Explorer interaction prototype
[✓] approve CPO Explorer v0.4 as interaction-direction baseline
[✓] freeze Company Research Pool direction
[✓] accept Research Workspace direction
[✓] define visual language
[✓] define product acceptance contract
[✓] write reboot MVP plan
[✓] write reboot orchestration
[✓] update repository entry documents and approve canonical fixed-Round Plan
[✓] accept R1 P0–P3 code disposition audit
[✓] accept R2 research shell
[✓] accept R3 CPO Explorer vertical slice
[✓] accept R4 full CPO Explorer
[✓] accept R5 company research experience
[ ] R6 read-only Research Workspace remains pending; do not start without separate Owner decision
[ ] R7 integration cleanup remains pending after R6 acceptance and separate Owner decision
```

## 13. Decision Owner

The Product Owner approves:

- product direction
- page structure
- prototype interaction
- visual direction
- whether a new primary page is justified
- whether a reboot phase may proceed

Pi is the implementation agent.

Pi must not independently expand research-facing product scope or reinterpret approved prototypes as optional suggestions.
