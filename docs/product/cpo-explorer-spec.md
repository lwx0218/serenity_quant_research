# CPO Explorer Product & Interaction Specification

## Status

- Spec state: **interaction baseline**
- Approved prototype reference: `docs/product/prototypes/cpo-explorer-v0.4.html`
- Approval scope: interaction model and product behavior
- Not yet approved: final illustration quality, final typography, final colors, final spacing, final industrial artwork

## 1. Purpose

CPO Explorer is the primary research entry point for the CPO theme.

It should let a research user:

1. understand the system as a whole
2. identify major physical components
3. understand where a component is located
4. understand how the system decomposes physically
5. select a component
6. inspect subcomponents / materials
7. identify related companies
8. continue into company research without losing context

The Explorer is a research surface, not a diagram viewer and not an admin page.

## 2. View Model

CPO Explorer contains two visual representations of the same component graph.

### 2.1 Flat View

Purpose:

- system-level orientation
- functional location
- component-to-system mapping
- whole-device context

The Flat View should visually resemble a complete device / board / system composition.

Each researchable component must have an independent interaction region.

A single large invisible overlay that captures most of the device is prohibited.

### 2.2 3D Exploded View

Purpose:

- layered decomposition
- physical relationships
- assembly intuition
- component hierarchy

The production implementation does not require true 3D rendering.

An original, layered SVG / vector representation is acceptable and currently preferred for the MVP.

### 2.3 Shared state

Flat and 3D views must share:

- stable component ID
- hovered component
- selected component
- active callout
- research context
- drawer content

Switching view must preserve a locked selection.

## 3. Interaction Object

The canonical interaction object is:

```text
Component
+
Callout
+
Connector
```

All three refer to one domain component.

A callout is not independent UI state.

A component is not considered fully represented if the callout points to a different state or behaves differently.

## 4. Idle State

### Visible

- complete system / exploded device
- all major callouts
- Flat / 3D view control
- minimal research navigation

### Hidden

- research side panel

### Appearance

- all major components readable
- all callouts readable
- no selected-state accent
- no unnecessary glow
- no permanent research metadata panel

## 5. Hover State

Hover can begin from either:

- component body
- corresponding callout card

Both inputs must produce the same state.

### Active component

On hover:

- remains sharp
- may move upward / outward slightly
- may receive a subtle scale increase
- may receive natural shadow / depth enhancement

The component body must **not** receive a strong blue outline.

### Active callout

On hover:

- remains sharp
- may receive restrained accent border / shadow
- connector line may use the accent color
- endpoint may use the accent color

### Unrelated objects

On hover:

- unrelated components reduce opacity
- unrelated components receive moderate blur / desaturation
- unrelated callouts reduce opacity
- unrelated callouts receive moderate blur / de-emphasis

The result should feel like visual focus, not a warning/error state.

### Hover exit

If no component is locked:

- return to Idle

If another component is locked:

- selection remains authoritative

## 6. Selected State

Selection begins by clicking:

- component body, or
- corresponding callout

Both are equivalent.

### On selection

- component locks in focus state
- callout locks in focus state
- connector locks in focus state
- unrelated objects remain de-emphasized
- research panel slides in from the right
- research context becomes persistent until reset

### Select another component

Clicking another component / callout:

- replaces current selection
- updates the panel
- does not require manual reset first

### Click selected object again

Clicking the currently selected component / callout:

- unlocks
- closes research panel
- returns to overview

## 7. Reset Behavior

The following actions reset the current selection:

1. click selected component again
2. click selected callout again
3. click empty canvas area
4. press `Esc`
5. close the research panel

After reset:

- no component is selected
- no callout is selected
- research panel is closed
- full device returns to normal clarity

A dedicated “Return to full device” button inside the panel is not required.

## 8. Empty Canvas Definition

The implementation must distinguish:

- real component interaction regions
- empty canvas

This is especially important in Flat View.

Do not use one board-sized interaction zone that prevents empty-area reset or causes the same component to remain active across most of the device.

## 9. Flat View Segmentation

Each major component must have its own explicit visual or geometric interaction region.

Example component set from the current CPO baseline:

- top cover / heatsink
- switch ASIC
- Driver / TIA / Retimer
- SiPh PIC / optical engine
- laser array
- PD / receive array
- FAU / fiber array / MPO
- co-packaged substrate / interposer
- high-speed PCB / gold fingers

Interaction regions may be:

- SVG groups
- paths
- polygons
- grouped primitives
- carefully bounded transparent hit areas

They must not materially overlap in a way that causes incorrect hover ownership. Interaction regions must correspond to real visible geometry; broad invisible zones are prohibited.

When geometric overlap cannot be avoided, interaction priority must be explicit and reflect the visible top-most component, not DOM accident. Known prototype overlap or detached hit-zone behavior is a prototype limitation that production must correct.

## 10. Callout Specification

Each major component has a callout.

Recommended information:

```text
[number]
component name
short functional description
```

Example:

```text
04
SiPh PIC
调制 / 波导 / 耦合
```

### Callout behavior

Hover callout:

- focus component
- focus callout
- focus connector
- de-emphasize unrelated objects

Click callout:

- select component
- open research panel

Callout interaction must be equivalent to direct component interaction.

## 11. View Switching

The Explorer provides a visible view switch.

Current model:

```text
Flat View
3D Exploded
```

The control should behave as a view toggle, not global navigation.

### Required behavior

When component `X` is selected:

```text
3D View: X selected
↓ switch view
Flat View: X remains selected
```

The research panel remains synchronized.

The view switch must not reset research context unless explicitly requested.

## 12. Research Panel

### Default state

Hidden.

The Explorer should use the full canvas width when no component is selected.

### Open condition

Panel opens only after component selection.

### Presentation

- slides from right
- overlays or temporarily reduces usable canvas space
- does not behave like a permanent application sidebar
- may have a close icon

### Minimum content

#### Component identity

- name
- short functional summary

#### Child research objects

- 具有稳定 ID 的真实 subcomponents
- 仅在现有权威关系支持时显示 materials / technology context；否则显示 `暂无已核验材料数据` 或省略该组，不得使用 Prototype mock material

#### Related companies

- small company cards
- role / relationship summary
- next action toward Company Pool

### Future extension

Possible later additions:

- technology links
- chain-node mapping
- evidence summary
- unresolved research questions

These should not be added to the first production reboot unless they remain visually controlled.

## 13. Subcomponent / Material Behavior

Selecting a main component opens a drill-down list.

Example:

```text
SiPh PIC
├── Modulator
├── Waveguide
└── Coupler
```

子对象只有在 reviewed repository data 与显式关系支持时才可以展示 material / technology context。以下仅说明关系形态，不是可写入生产的事实：

```text
Child part
→ reviewed material or technology context（如果存在）
```

当前 R1 证据表明 seed 中没有已核验的离散材料目录。因此，首个 Explorer vertical slice 必须显示真实子部件，并对材料采用 `暂无已核验材料数据` 或省略策略；不得渲染 `Silicon`、`SiN` 等示例 chip，除非后续已有权威数据支持。

Child selection should refine the current research context and should refine the related-company set when existing authoritative relationships support it.

R1 first records what `PhysicalPart`, `TechnologyLink`, `IndustryChainNode`, `CompanyExposure`, service aggregation, and seed relationships can already express. Query/service adaptation may proceed in the applicable Explorer Round. Any required persistent schema change is a blocked/rebaseline condition requiring Owner approval; material gap presentation itself不需要 schema，也不阻塞 Research Shell 或 initial Explorer vertical slice。

## 14. Related Company Preview

The Explorer should show only a bounded preview of companies related to the selected context.

The panel is not the full company database.

Recommended card-level information:

- company name
- relationship / role
- market or category when useful

The panel should provide a clear action to continue into Company Research Pool.

## 15. Company Pool Transition Contract

Expected transition:

```text
Selected component
→ optional selected subcomponent / material
→ related company preview
→ Company Research Pool
```

The receiving page should preserve enough context to explain why these companies are shown.

Example context:

```text
CPO → SiPh PIC → Modulator
```

The Explorer should not require the user to repeat the same filters manually after navigation.

## 16. Visual Direction

Final visual design is not frozen, but the following constraints are already accepted.

### Preferred

- light
- restrained
- calm
- technical
- precise
- large usable canvas
- strong hierarchy
- editorial / research quality
- subtle depth
- intentional whitespace

### Avoid

- admin-dashboard appearance
- neon sci-fi
- large glow effects
- strong blue component outlines
- cyberpunk aesthetic
- excessive gradient surfaces
- excessive rounded containers
- heavy persistent sidebars
- dense metadata always visible

## 17. Accessibility / Interaction Requirements

Production implementation must preserve:

- keyboard reset via Esc
- visible focus for keyboard navigation
- meaningful component labels
- pointer-independent access to primary component/callout selection
- sufficient contrast for callout text and connectors

Accessibility must not force a duplicate table to remain visible by default.

If a non-visual fallback is required, it should be secondary and unobtrusive.

## 18. Prototype vs Production

`cpo-explorer-v0.4.html` is a behavior reference.

Pi may change:

- DOM structure
- rendering technology
- CSS architecture
- SVG organization
- component geometry
- illustration quality

Pi must preserve the approved interaction semantics unless the Product Owner explicitly changes this spec.

## 19. Acceptance Scenarios

A production CPO Explorer implementation is not ready for product review unless the following scenarios work.

### Scenario A — component hover

1. open Explorer
2. hover one component
3. corresponding callout becomes active
4. unrelated components and callouts de-emphasize
5. component body has no strong blue outline
6. leaving hover returns to overview

### Scenario B — callout hover

1. hover a callout
2. corresponding component becomes active
3. unrelated objects de-emphasize

### Scenario C — selection

1. click component
2. component locks
3. callout locks
4. research panel slides in
5. 真实 subcomponents 可见；materials 仅在权威数据支持时可见，否则明确显示 `暂无已核验材料数据` 或省略
6. related companies 仅在显式关系支持时可见；否则显示安全空状态

### Scenario D — reset

Verify each independently:

- click same selected component
- click same selected callout
- click empty canvas
- press Esc
- close panel

Each must restore overview and close the panel.

### Scenario E — view switch

1. select a component in 3D view
2. switch to Flat View
3. same component remains selected
4. panel remains synchronized
5. switch back
6. selection remains valid

### Scenario F — Flat segmentation

1. hover each major visible component
2. each component activates its own callout
3. no board-sized invisible region incorrectly captures most pointer interactions
4. empty canvas remains available for reset

## 20. Product Review Deliverables

When Pi later implements the production version, product review should include:

- screenshot of Idle — Flat View
- screenshot of Hover — Flat View
- screenshot of Selected — Flat View
- screenshot of Idle — 3D
- screenshot of Hover — 3D
- screenshot of Selected — 3D
- screenshot of open research panel
- short recording or sequential screenshots showing view-switch state preservation

Automated tests are useful, but they do not replace visual product review.
