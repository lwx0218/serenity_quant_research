# Product Acceptance Contract

## 状态

- State：**mandatory reboot gate**
- Applies to：research-facing UI and UX
- Implementation agent：Pi
- Product approval owner：Product Owner

## 1. 目的

本合同用于防止 P0–P3 的 product drift 重演。

Build 与 automated tests 通过并不足够。Research-facing implementation 必须证明：

- product direction 正确；
- information architecture 正确；
- interaction 符合 approved contract；
- visual hierarchy 符合 approved direction；
- 没有新增未批准 scope；
- research data safety 没有被 prototype/mock/model claims 破坏。

## 2. Source-of-Truth Order

Product-facing work 读取顺序：

```text
1. docs/product/README.md
2. docs/product/experience-map.md
3. page-specific product spec
4. approved HTML prototype
5. docs/product/visual-language.md
6. docs/product/acceptance-contract.md
7. operations/planning/research-experience-reboot.md
8. operations/orchestration/research-experience-reboot.md
9. current implementation
10. legacy P0–P3 plans / work logs
```

Current code 不覆盖 approved reboot product contract。

## 3. Prototype Gate

Pi 实现 research-facing page 或 major interaction 前，必须确认：

1. 已有 approved product spec；
2. 当 visual / interaction ambiguity material 时，已有 approved 或 directional prototype；
3. Product Owner 已明确接受 interaction direction；
4. Pi 已区分 prototype 中哪些 behavior 是 mandatory，哪些只是 visual reference。

除非 Owner 明确要求，Pi 不得独立重设计产品。

## 4. No Silent Scope Expansion

除非当前 task 明确授权，Pi 不得新增：

- new primary pages；
- new top-level navigation；
- research UI 中的 new admin-facing concepts；
- new permanent sidebars；
- new filter dimensions；
- new tabs；
- new metric strips；
- new comparison workflows。

若 implementation 暴露 product ambiguity，Pi 应停止并报告，而不是猜测。

## 5. Research-Data Safety Gate

Prototype content 与 model-generated content 不自动成为 research facts。

除非 evidence contract 支持，Pi 不得把以下 unsourced claims 推入 production data 或 research copy：

- supplier relationships；
- customer relationships；
- production status；
- market share；
- BOM value share；
- localization rate；
- technology-barrier score；
- company tier；
- investment thesis。

Candidate research state 必须与 verified state 清楚区分。

## 6. Explorer Acceptance

Production CPO Explorer 必须证明：

- Flat View；
- 3D Exploded View；
- shared component identity；
- shared selection state；
- component ↔ callout hover equivalence；
- component ↔ callout click equivalence；
- unrelated objects de-emphasis；
- no strong blue component outline；
- empty-area reset；
- same-object reset；
- Esc reset；
- contextual drawer；
- view switch 时 selection preserved；
- Flat View segmentation 正确；
- drawer open 时可选 cinematic re-centering。

## 7. Company Pool Acceptance

Production Company Pool 必须证明：

- Card View；
- List View；
- 两种 view 共享 filters；
- 两种 view 共享 research context；
- click 打开 Quick Drawer；
- Quick Drawer 可关闭且不导航；
- Quick Drawer 有 expand icon；
- expand icon 打开 Full Company Detail；
- Full Company Detail 保留 company 与 source research context；
- Company Pool 不默认成为 SleekGrid-first 产品。

## 8. Research Workspace Acceptance

Production Workspace v1 必须证明：

- knowledge-centric read-only layout；
- research-object navigation；
- main reading area 显示 current research object；
- linked objects；
- derived/read-only backlinks 或等价 relationship context；
- evidence / status context；
- existing/read-only open questions 与 conclusions 区分；
- component 与 company research objects 都能打开；
- no new persistent schema or writing endpoint。

Workspace 不得退化为另一个 dashboard。Graph、New Note、note editing、persistent ResearchNote/OpenQuestion/Backlink entities 不是 v1 acceptance requirements。

## 9. Visual Review Deliverables

最低 review evidence：

### Explorer

- Idle Flat
- Hover Flat
- Selected Flat
- Idle 3D
- Hover 3D
- Selected 3D
- Drawer open
- view-switch state preservation

### Company Pool

- Card View
- List View
- Quick Drawer open
- Full Company Detail
- context preserved from Explorer

### Research Workspace

- component object open
- company object open
- linked-object / backlink context visible

## 10. Required Viewport Checks

最低 viewport：

- 1440px desktop width
- 1920px desktop width

当前产品是 desktop-research-first。

## 11. Product Review Order

按以下顺序 review：

1. Product objective
2. Information architecture
3. Interaction behavior
4. Visual hierarchy
5. Data correctness
6. Accessibility / keyboard behavior
7. Automated tests
8. Build / regression status

绿色 test suite 不能弥补错误 product direction。

## 12. Screenshot Review Questions

每张 screenshot 询问：

1. 当前 research object 是什么？
2. 当前 research context 是什么？
3. 下一步最可能 action 是什么？
4. 是否显示了属于更深 information level 的内容？
5. 页面是否像 admin system？
6. 用户是否被迫解析过多 filters / badges / containers？
7. 该 view 是否保持 research journey？

## 13. Stop Conditions

只有当 resolution 会导致以下情况时，Pi 才必须停止并升级给 Product Owner：

- add/remove primary product area；
- change core user path；
- add or materially change persistent domain/schema；
- change research evidence or audit semantics；
- require clearly irreversible/high-cost architecture investment。

普通 prototype defects、layout/spacing choices、hit-region repair、component organization、CSS、test harness、screenshot mechanics 使用安全工程默认，并在 review 中展示。不存在的 factual data 必须保持 `Unknown`、`Not reviewed`、`Candidate`、system-derived 或 omitted，绝不能发明。

## 14. Engineering Preservation

Reboot 不意味着重写稳定 backend work。

Pi 应尽量保留：

- stable domain IDs；
- database migrations；
- domain relationships；
- services；
- evidence semantics；
- audit behavior；
- permission logic；
- validated backend tests。

Acceptance contract 主要治理 research-facing product behavior。

## 15. Review Decision Vocabulary

使用以下 decision：

- `approved`
- `approved with minor findings`
- `changes requested`
- `blocked by product ambiguity`

Review 应区分：

- product issue；
- visual issue；
- interaction issue；
- data issue；
- engineering issue。

不得把所有失败合并成泛化的 “UI polish”。
