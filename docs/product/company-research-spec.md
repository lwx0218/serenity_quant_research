# Company Research Product & Interaction Specification

## Metadata

- Project: serenity_quant_research
- Document type: product-spec
- Status: superseded
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: docs/product/README.md

## 状态

- Spec state：**interaction baseline**
- Approved interaction reference：`docs/product/prototypes/company-pool-v0.3.html`
- Approval scope：Company Pool information architecture；Card/List dual browsing model；Quick Drawer → Full Detail hierarchy；Explorer research-context preservation
- Not yet frozen：final typography、spacing、card density、comparison layout、full-detail visual design

## 1. 目的

Company Research 是 CPO Explorer 之后的第二个主要 product area。

它帮助 research user 从：

```text
Component / Material / Technology
→ related companies
→ quick company understanding
→ full company research
```

自然前进，同时不丢失原始 research context。

Company Pool 不是 generic company database，也不是 CRUD table。

## 2. Product Layers

Company experience 有三层 interaction depth。

### Layer 1 — Browse

两个等价 browse views：

- Card View
- List View

两者展示同一个 research universe，并使用同一组 filters/context。

### Layer 2 — Quick Company Drawer

点击 Card 或 List 中的 company 打开右侧 drawer。

Drawer 回答：

- 为什么这家公司出现在这里？
- 当前 exposure state 是什么？
- evidence coverage 如何？
- immediate open questions 是什么？
- 是否值得深入研究？

### Layer 3 — Full Company Detail

Drawer 右上角有显式 expand action。Expand 打开完整 company research page。该页面是 structured company entity page。

## 3. Card / List Dual View

### Card View

默认 browse mode。优化目标：visual scanning、discovery、role recognition，以及理解公司为什么出现在当前 context。

Recommended fields：

- company name；
- ticker / market；
- primary exposure tags；
- exposure state；
- evidence coverage summary；
- concise “Why it appears here” statement。

不要把 card 变成 mini company report。

### List View

可选 compact mode。优化目标：fast scanning、larger universes、stable fields comparison、efficient navigation。

Recommended columns：

- company；
- primary exposure；
- exposure state；
- evidence coverage；
- navigation affordance。

List View 不得成为 primary product default。

## 4. Research Context Preservation

从 Explorer 打开 Company Pool 时，source path 应保持可见。

示例：

```text
CPO → SiPh PIC → Modulator
```

Context 可影响 initial filter state、company ordering、“Why it appears here”、quick-drawer content 与 full-detail exposure sections。用户不应手工重建同一 research context。

## 5. Filtering

Filtering 应保持轻量。

Default visible controls 限于高价值 research dimensions，例如：

- search；
- component / material group；
- chain role；
- market / region only when needed；
- exposure state only when needed。

避免一次暴露所有 backend filter dimensions。优先使用 chips、compact selectors 与 contextual filtering，而不是 long admin forms。

## 6. Company Card Interaction

Hover：

- subtle elevation；
- no strong glow；
- no dashboard-style emphasis。

Click：

- opens Quick Company Drawer；
- keeps Company Pool visible in background；
- preserves current scroll position and filters。

Company card 首次 click 不应直接导航到 Full Detail。

## 7. Quick Company Drawer

Drawer 是 fast research-triage surface，让用户不用离开 Company Pool 就能回答：

> “Should I go deeper into this company?”

Drawer 可由 card click 或 list-row click 打开，通过 close icon、outside click 或 Esc 关闭。

Minimum content：

- company identity；
- short research summary；
- primary exposure tags；
- exposure verification state；
- evidence coverage；
- open-question count；
- quick links to major research sections；
- expand icon to Full Company Detail。

Expand action transition：

```text
Quick Company Drawer
→ Full Company Detail
```

## 8. Full Company Detail

Full Company Detail 是 **entity-centric** page。

它回答：

- 公司是什么？
- 它如何参与当前 industry chain？
- 哪些 product / component relationships 重要？
- 哪些 evidence 支持或反驳这些关系？
- 还有哪些 uncertainty？

不要默认七个 tabs。

优先使用 continuous 或 lightly segmented page：

1. Company Overview
2. Industry-chain Exposure
3. Current Research Context
4. Key Evidence
5. Open Questions
6. Events / Financial Evidence when materially relevant
7. Link to Research Workspace

只有当 content scale 证明必要时，后续才可引入 tabs。

## 9. Comparison

Company Comparison 已延期，不属于 Company Pool v1 acceptance。当前批准的首个 delivery 是：

```text
Card / List
→ Quick Drawer
→ Expand
→ Full Company Detail
```

任何后续 comparison workflow 都需要单独 product decision。Short-term share-price ranking 不属于默认 research experience。

## 10. Exposure State Semantics

既有 research semantics 必须保留：

- `discovery`
- `candidate`
- `verified`
- `rejected`
- `stale`

UI 不得让 `candidate` 看起来等同于 `verified`。

## 11. Evidence Language

Company UI 应区分：

- verified fact；
- candidate mapping；
- research hypothesis；
- unresolved question。

公司关系不会因为出现在 prototype 中，或因为 model 生成 thesis，就变成 `verified`。

## 12. Company Detail vs Research Workspace

Company Detail 是：

> **entity-centric**

Research Workspace 是：

> **knowledge-centric**

Company Detail 回答：

> “What do we know about this company?”

Research Workspace 回答：

> “What do we currently know about this research object or topic, and how are related objects connected?”

## 13. Acceptance Scenarios

### Card browse

1. Card View is default。
2. Cards show identity、exposure、state、concise research rationale。
3. Page remains readable without table density。

### List browse

1. Switch to List View。
2. Same company set and filters remain active。
3. Clicking a row opens the same Quick Drawer as Card View。

### Drawer

1. Click a company。
2. Drawer opens while Company Pool stays visible。
3. Source research context remains visible。
4. Esc / outside click / close icon closes drawer。

### Full Detail

1. Open Quick Drawer。
2. Click expand icon。
3. Full Company Detail opens。
4. Selected company and source context remain consistent。

## 14. Prototype vs Production

`company-pool-v0.3.html` 是 interaction reference。

Pi 可调整 markup、CSS implementation、component library、exact drawer width、card dimensions。

Pi 必须保留：

```text
Card / List
→ Quick Drawer
→ Expand
→ Full Company Detail
```
