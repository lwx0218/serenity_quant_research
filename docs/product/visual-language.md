# Visual Language

## Status

- State: **product visual direction**
- Applies to CPO Explorer, Company Pool, Company Detail, and Research Workspace
- Final brand system is not yet frozen

## 1. Visual Goal

The product should feel:

- light
- restrained
- technical
- calm
- precise
- research-oriented
- premium without being decorative
- information-dense only where hierarchy remains obvious

Useful mental references:

- technical publication
- research atlas
- precision engineering annotation
- professional knowledge workstation

Avoid:

- generic SaaS dashboard
- admin template
- BI dashboard
- neon science-fiction interface
- crypto / cyberpunk visual language
- excessive cards
- excessive badges
- excessive gradients
- excessive shadows
- every section boxed into a rounded rectangle

## 2. Serenity Boundary

Serenity default research-facing UI must not define the visual language.

Serenity may remain underneath as infrastructure.

Research-facing pages should use an independent shell and product styling.

## 3. Typography

### Sans-serif

Use for primary text, navigation, company names, section headings, and research prose.

Characteristics:

- neutral
- highly readable
- modern
- compact enough for professional data work

### Monospace

Use selectively for:

- component codes
- callout indexes
- stable IDs
- node references
- technical micro-labels

Example:

```text
04 // OPTIC-PIC
```

Monospace should add technical precision, not become the dominant font.

## 4. Precision Blueprint Annotation

CPO Explorer may adopt a blueprint-like annotation language:

- thin connector lines
- small anchor dots
- compact callout cards
- mono node code
- high-contrast component title
- restrained functional subtitle

Example:

```text
04 // OPTIC-PIC
SiPh PIC
调制 / 波导 / 耦合
```

Hover may accent the callout border, connector line, endpoint, and mono index.

Do not add strong blue outlines to component geometry.

## 5. Cinematic Re-centering

When an Explorer drawer opens, the main visual may:

- translate slightly away from the drawer
- scale down slightly
- preserve the selected component near the visual center

Purpose:

- avoid drawer overlap
- maintain spatial context
- create a natural transition into deeper research

Do not hard-code prototype values as product requirements.

## 6. Progressive Disclosure

The visual system should reinforce information depth.

### Level 0 — Overview

- large primary canvas / research surface
- minimal navigation
- minimal metadata

### Level 1 — Hover

- focus
- subtle elevation
- de-emphasize unrelated content

### Level 2 — Selection

- contextual drawer
- focused component or company

### Level 3 — Full Detail / Workspace

- complete research content
- evidence
- notes
- backlinks
- deeper structure

The product should not show Level 3 information at Level 0.

## 7. Cards

Cards are allowed when they represent meaningful research entities.

Good uses:

- company cards
- evidence cards
- subcomponent accordion items
- linked-object previews

Avoid nested decorative cards and card-heavy dashboard composition.

## 8. Drawer Language

Drawers should feel like contextual dossiers.

Recommended:

- clear identity header
- restrained dividers
- compact sections
- progressive disclosure
- no unnecessary dashboard metrics

Drawer widths are not globally fixed.

## 9. Metric Strips

Metric strips can be visually useful but are data-sensitive.

Do not use unverified claims such as:

- BOM value share
- localization rate
- market share
- technology-barrier score
- supplier tier

unless supported by reviewed evidence.

Safer system-derived metrics include:

- evidence coverage
- exposure state
- open-question count
- company coverage
- last reviewed
- research maturity

Prototype metrics must never be mistaken for verified product facts.

## 10. Company Tier / Thesis Language

Avoid presenting model-generated labels such as:

- Global Leader
- Domestic Leader
- Core Supplier
- Domestic Pioneer
- investment thesis

as verified facts.

If introduced later, they must be sourced, reviewed, auditable, and clearly separated from machine-generated suggestions.

## 11. Color

Preferred approach:

- neutral light background
- white / near-white surfaces
- dark neutral text
- restrained accent
- semantic colors only when they encode meaningful state

Accent is appropriate for active callouts, selected context, interactive links, and important navigation state.

## 12. Depth and Shadow

Use depth primarily to explain interaction.

Good uses:

- hovered component elevation
- active drawer
- hovered company card

Avoid permanent heavy shadows and glowing containers.

## 13. Spacing

Prefer generous outer whitespace and compact internal research density.

Principle:

> large-scale breathing room, small-scale information precision

## 14. Navigation

Current expected top-level items:

```text
CPO Explorer
Company Pool
Research Workspace
```

Company Detail is reached from Company Pool and does not require a top-level nav item.

## 15. Interaction Timing

Recommended:

- hover: ~120–220ms
- drawer / major transition: ~240–360ms

Use controlled, non-bouncy easing.

## 16. Research Workspace

Workspace may borrow from knowledge tools:

- quiet left tree
- document-like center
- restrained context rail

It should still feel like the same product.

## 17. Design Reference Policy

External or model-generated prototypes may be used as visual references.

They are not source-of-truth for:

- company relationships
- investment theses
- supplier claims
- BOM shares
- localization rates
- market shares
- technology-barrier ratings

Design reference and research evidence are separate concerns.
