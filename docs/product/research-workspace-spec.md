# Research Workspace Product & Interaction Specification

## Metadata

- Project: serenity_quant_research
- Document type: product-spec
- Status: superseded
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: docs/product/README.md

## Status

- Spec state: **approved v1 direction baseline**
- Prototype reference: `docs/product/prototypes/research-workspace-v0.1.html`
- Product direction: **knowledge-centric linked research mental model**
- v1 boundary: **read-only + linked-object-first**
- Exact layout remains directional; persistent editing is deferred

## 1. Purpose

Research Workspace 是产品的 **knowledge-centric** 阅读与关联层，不是 Company Detail 页面。

长期方向可以承载研究对象、证据、链接、结论、笔记与未解决问题，但 **v1 只读取现有持久对象和可派生关系**，不创建或编辑 ResearchNote、OpenQuestion、Backlink 或 Graph。

v1 心智模型：

```text
Existing Research Object
↔ Existing Linked Objects
↔ Existing Evidence / Status
↔ Derived Read-only Backlinks
↔ Read-only Gap / Unresolved-question View
```

## 2. V1 Persistence Boundary

Workspace v1 reuses existing persistent domain objects and relationships. It may display component, technology/material context, company, evidence reference, research status, derived/read-only backlinks, and existing unresolved questions.

It does not add:

- `ResearchNote`
- independent `OpenQuestion`
- independent `Backlink`
- Graph persistence or editing
- New Note / note editor
- Markdown knowledge base
- collaborative editing
- plugin-like systems

The prototype's `Graph` and `New note` controls are placeholders/deferred capabilities, not v1 acceptance requirements. If persistent research writing is proposed later, identity, author attribution, audit ownership, and Open Access effects require a separate Owner decision first.

## 3. Supported Research Objects

Workspace is not limited to companies.

v1 可打开的对象来自现有持久模型，包括：

- CPO component / physical part
- SiPh PIC、Modulator、Laser Array、FAU、ELS 等已有 taxonomy 对象
- a company
- a technology route
- an industry-chain node

Research thesis 与 research note 属于长期方向，不是 v1 可新建、编辑或持久化的对象。

## 3. Layout Direction

### Left — Research Tree / Navigation

用于浏览现有对象：

- Physical Components
- Technologies
- Companies
- Evidence / Status（只读）
- Themes（仅在现有对象支持时）

The tree should remain lightweight and must not become an Administration sidebar.

### Center — Current Research Object

中心区域是主要只读阅读面，不是 editor。

可展示：

- current understanding（仅限已有、可追溯内容）
- structured read-only sections
- evidence links / status
- linked companies
- subcomponents / authoritative material context
- 派生的只读 gap / unresolved-question 提示
- existing working conclusions（如果已有且状态明确）

视觉上可以接近研究文档，但 v1 不提供编辑、New Note 或持久化写入。

### Right — Context / Backlinks

提供：

- linked objects
- derived read-only backlinks
- evidence state
- research status
- current path

`related notes` 仅属于未来 writing capability；v1 不创建或假设 ResearchNote。

This area supplies context without competing with the main note.

## 4. “Obsidian-like” Means Mental Model, Not Visual Copy

v1 可以借鉴：

- linked knowledge objects
- derived read-only backlinks
- object-centric exploration
- lightweight object tree
- context preservation

Research graph 与 note-centric editing 属于 deferred capability。

It should not blindly copy Obsidian visual chrome, every plugin pattern, or generic note-taking behaviors that do not help investment research.

## 5. Workspace Entry Paths

Workspace v1 可从以下现有对象入口打开：

- CPO Explorer
- Company Detail
- Company Pool
- a technology / component object

The source path should be preserved.

Examples:

```text
CPO → SiPh PIC → Modulator → Research Workspace
```

```text
Company Pool → 光迅科技 → Research Workspace
```

## 6. Current Understanding

A Workspace object should make current research state visible.

Recommended content:

- concise current understanding
- confidence / maturity where supported
- supporting evidence links
- contradicting evidence links
- invalidation conditions when available
- last reviewed timestamp

Generated text must not be presented as a verified conclusion.

## 7. Linked Objects

Workspace should make relationships easy to traverse.

Example:

```text
SiPh PIC
→ Modulator
→ Silicon
→ 光迅科技
→ Evidence EVD-...
```

These are research links, not merely decorative tags.

## 8. Backlinks

Backlinks answer:

> “Where else is this object referenced?”

v1 只展示可由现有关系派生的 backlinks，例如：

- company pages
- component pages
- evidence records
- existing conclusions / reports（仅在现有关系与状态支持时）

不得为了 backlinks 新增 persistent entity。

## 9. Research Notes（Deferred）

ResearchNote、note editor、meeting note、evidence summary writing 和 technology-map update 均不属于 v1。未来若增加 persistent research writing，必须重新取得 identity、author attribution、audit ownership 和 Open Access 影响的 Owner 决策。

## 10. Read-only Unresolved Questions / Gaps

v1 可以根据现有对象、状态和缺失关系展示只读问题或 gap，例如：

- 该 exposure 仍是 sampling 还是已进入 production？
- 当前关系是否只有 candidate evidence？
- 哪项关键证据仍缺失？

这些内容不是独立 `OpenQuestion` entity，不能在 v1 中创建、编辑、分派或标记解决。

## 11. Graph View

A graph view may be added later only if it helps reveal:

- object relationships
- research clusters
- missing links
- evidence gaps

Graph View is not required for the first reboot implementation.

## 13. Editing Boundary

The first implementation supports reading, linked-object navigation, relationship context, evidence/status context, and read-only unresolved questions. It does not support lightweight note editing or any persistent research writing.

Editing, advanced collaboration, plugins, markdown extensions, and full knowledge-management features are deferred and require a later Plan.

## 14. Company Detail Relationship

Company Detail and Research Workspace should link to each other.

Example:

```text
Company Detail
→ Open in Research Workspace
```

Workspace may open the same company as a linked research object, but the layout and purpose remain different.

## 15. Acceptance Scenarios

### Component Workspace

1. open Workspace for SiPh PIC
2. center shows current understanding
3. left tree shows related research objects
4. right panel shows linked objects / backlinks
5. linked companies are reachable

### Company Workspace

1. open Workspace from Company Detail
2. company context is preserved
3. company appears as a research object
4. existing evidence / status / linked components remain accessible；不要求或假设 ResearchNote

### Backlink navigation

1. click a derived backlink
2. related existing object opens
3. relationship to the previous object remains understandable
4. 不创建或依赖 ResearchNote / Backlink persistent entity

### Read-only unresolved questions / gaps

1. open a research object
2. 可由现有状态派生的 unresolved question / gap 可见
3. 它们与 verified conclusions 明确分离
4. 不提供创建、编辑、分派或解决 OpenQuestion 的能力

## 16. Prototype vs Production

`research-workspace-v0.1.html` is directional.

Pi may change exact column widths, tree styling, note layout, and context-panel presentation.

Pi must preserve:

> Research Workspace is a knowledge-centric linked research environment, not another company dashboard.
