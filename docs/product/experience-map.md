# Product Experience Map

## Metadata

- Project: serenity_quant_research
- Document type: product-spec
- Status: approved
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: docs/product/README.md

## Status

- Product state: Reboot
- Scope: research-facing MVP
- Current confirmed primary entry: CPO Explorer
- Company Pool direction: **interaction baseline accepted**
- Research Workspace: **accepted as an independent knowledge-centric product area**

## 1. Core Research Journey

The product should support one simple mental model:

```text
I see a product
→ I understand what it is made of
→ I select one component
→ I see what is inside / what materials or technologies matter
→ I see which companies are exposed
→ I move into company research without losing why I came there
```

Current Research Experience Reboot flow:

```text
CPO Explorer
    ↓
Component / Material / Technology
    ↓
Related Companies
    ↓
Company Research Pool
    ↓
Quick Drawer
    ↓
Full Company Detail
    ↓
Read-only Research Workspace
```

The complete long-term product continues from Workspace into Evidence → Review → Conclusion → Report. Those later product surfaces are deferred, not cancelled.

The interface should optimize this journey before adding secondary workflows.

## 2. Primary Product Areas

### 2.1 CPO Explorer

Role:

- visual entry point
- system understanding
- physical decomposition
- component selection
- contextual drill-down
- company discovery

Contains:

- Flat View
- 3D Exploded View
- callouts
- contextual research drawer after selection

It does **not** contain a permanent research sidebar.

### 2.2 Company Research Pool

Role:

- browse companies relevant to a research context
- scan companies visually
- understand each company’s component / material / chain role
- open deeper research
- review one company at a time；Company Comparison 已延期，不属于 Company Pool v1

Primary presentation:

- card-first

Not primary presentation:

- SleekGrid-first
- spreadsheet-like database table
- long admin-style filter form

### 2.3 Research Workspace

Role（v1）：

- knowledge-centric read-only research environment
- existing linked research objects
- derived read-only backlinks
- evidence / status context
- read-only unresolved-question / gap view

ResearchNote、independent OpenQuestion、Graph 和 editing 属于 deferred capability。

Research Workspace is intentionally separate from Full Company Detail.

```text
Company Detail = entity-centric
Research Workspace = knowledge-centric
```

Workspace may be opened from:

- CPO Explorer
- Company Pool
- Full Company Detail
- existing linked technology / component / company objects

Current directional reference:

`docs/product/prototypes/research-workspace-v0.1.html`

## 3. Navigation

### 3.1 Primary navigation

Current working model:

```text
CPO Explorer
Company Pool
Research Workspace
```

Full Company Detail is reached through Company Pool and does not require a top-level navigation item.

### 3.2 Excluded from primary navigation

Do not show:

- Dashboard
- Administration
- Language
- Users
- Roles
- Permissions
- template/demo modules

These may exist as secondary infrastructure routes if required.

## 4. Research Context Preservation

Context should survive transitions.

Example:

```text
CPO Explorer
Selected:
SiPh PIC
  ↓
Subcomponent:
Modulator
  ↓
Related Companies
  ↓
Company Pool
```

Company Pool should be capable of showing a lightweight context indicator such as:

```text
Researching
CPO → SiPh PIC → Modulator
```

The user should not need to reconstruct why a company appears.

Context preservation may include:

- selected component ID
- selected subcomponent ID
- selected material / technology
- source view
- active filters derived from the research context

The visual presentation should remain lightweight.

## 5. CPO Explorer State Flow

```text
Idle
  ↓ hover component / callout
Hover Focus
  ↓ click
Selected
  ↓ choose subcomponent / material
Drill-down Context
  ↓ company action
Company Pool Context
```

Reset from CPO Explorer:

- click selected object again
- click empty canvas area
- press Esc

Reset returns to the overview state.

## 6. Flat View and 3D Exploded View

These are not separate routes.

They are alternate representations inside CPO Explorer.

### Flat View answers:

> Where is this part in the complete system?

Useful for:

- system-level orientation
- mapping functional zones
- mapping physical regions to chain roles
- understanding where components sit relative to the whole device

### 3D Exploded View answers:

> What is this device physically made of?

Useful for:

- layered physical decomposition
- relative assembly relationships
- component boundaries
- part hierarchy

### Shared behavior

Both views must share:

- domain component IDs
- hover state semantics
- selection state
- callout mapping
- research panel data
- company relationships

Switching view must not discard a locked selection.

## 7. Callout Model

A callout is not merely a label.

It is the annotation representation of the same domain component shown in the device image.

A callout may show:

- sequence / index
- component name
- short functional description
- connector line

Component and callout share:

- hover
- click
- selected state
- reset behavior

Hovering either should focus both.

## 8. Progressive Disclosure

### Level 0 — overview

Visible:

- device
- component callouts
- view switch
- minimal primary navigation

Not visible:

- permanent research drawer
- full company list
- dense research metadata

### Level 1 — hover

Visible emphasis:

- active component
- active callout
- active connector line

De-emphasized:

- unrelated components
- unrelated callouts

No persistent research panel is required.

### Level 2 — selection

On click:

- selection locks
- research panel slides in
- subcomponents / materials appear
- related companies appear

### Level 3 — drill-down

Selecting a subcomponent / material refines the research context.

The UI may then refine:

- related companies
- technology / chain mapping
- evidence summary

This level will be specified further after Company Pool interaction is confirmed.

## 9. Company Transition

The CPO Explorer should not become a complete company research application.

Its job is to provide enough company context to support the next action.

Expected pattern:

```text
Selected component
→ small related-company cards
→ open / view all companies
→ Company Pool with context preserved
```

The transition should feel like continuing the same investigation, not opening an unrelated database module.

## 10. Back / Reset Philosophy

Avoid redundant navigation controls when direct manipulation is more natural.

Within Explorer:

- clicking empty canvas is the primary contextual reset
- clicking the selected object again also resets
- Esc resets for keyboard users

A dedicated “return to full device” button is not required in the side panel.

Page-level navigation may still provide browser-native back behavior when moving between primary product areas.

## 11. Visual Continuity Between Pages

Explorer and Company Pool should feel like parts of one product.

Shared elements should include:

- typography
- top navigation
- spacing system
- card language
- context indicators
- interaction timing
- muted/accent color usage

However, the layout does not need to be identical.

Explorer is visual-first.

Company Pool is entity/card-first.

## 12. UX Guardrails

Do not solve product uncertainty by adding:

- more tabs
- more filters
- more dashboards
- more badges
- more cards
- more permanent panels

When a workflow is unclear, first ask:

1. What is the user trying to understand?
2. What is the minimum information required at this step?
3. What context must remain visible?
4. What can wait until the next interaction?

## 13. Accepted Company Research Flow

Company research now uses three interaction depths:

```text
Card / List Browse
→ Quick Company Drawer
→ Expand
→ Full Company Detail
```

The Quick Drawer preserves Company Pool context and supports rapid triage.

Full Company Detail is an entity-centric research page.

Research Workspace is a separate knowledge-centric environment.

Implementation defaults and deferred items:

1. Company Comparison is deferred and is not Company Pool v1 acceptance.
2. Full Company Detail remains entity-centric and continuous/lightly segmented; exact density is tuned during visual review.
3. Workspace v1 is read-only; writing, Graph, New Note, and persistent knowledge entities are deferred.
4. Final visual polish and brand system are not blockers; the directional visual contract governs implementation review.
