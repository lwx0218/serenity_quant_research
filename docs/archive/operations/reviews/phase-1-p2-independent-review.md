# Phase 1 P2 Independent Review

## 状态

- Gate：independent review
- Route：review-only
- Date：2026-08-24
- Scope：P2 interactive SVG / Part Research UI
- P3：out of scope，未进入
- 当前解释：这是 P2 历史 Independent Review；P2 工程证据继续有效，但 research-facing presentation 已被 Research Experience Reboot supersede。

## Review 范围

Reviewer 检查了 frozen P2 contract 与实现，覆盖：

- diagram/artwork 与 phase boundary；
- `PartResearchService` catalog、drawer、detail data；
- 9 modules 与 21 seeded parts；
- pointer、keyboard、fallback、drawer、detail、async、empty/error、responsive、reduced-motion behavior；
- .NET 与 UI test quality；
- generated ServerTypes/MVC/ESM、navigation、project/package files、portability。

明确排除：P3 company comparison/detail、trading/market/account/backtest，以及任何 P3 business-code changes。

## 首轮验证结论

通过的命令/检查：

- `dotnet build SerenityQuantResearch.slnx --no-restore`：0 warnings，0 errors。
- `dotnet test SerenityQuantResearch.slnx --no-build`：13/13 tests passed。
- web project `npm run test:ui`：3/3 tests passed，但 test quality 存在 finding。
- web project `npm run build`：passed，generated output 无变化。

Fresh Kestrel + temporary SQLite + Firefox headless smoke 验证了：anonymous redirect、authenticated `/Research/Cpo`、part detail、generated assets、`ListParts`、`RetrieveCompleteChain`、Broadcom `candidate` 与 `EVD-2026-0001@v1` `draft` 状态、安全 gap rendering、keyboard/pointer selection、fallback navigation、unknown-detail error rendering。

## 首轮 Findings

### Critical

无。

### High

- **H-01 — Drawer/detail 缺少 mandatory P2 research sections。** 影响：drawer/detail 不满足 frozen contract；需补齐 function、boundaries、upstream/downstream、key specs、technology、companies、evidence、conclusions、risks、questions 等 section，即使无事实也要显示 gap。

### Medium

- **M-01 — Drawer requests 存在 stale result/error/retry race。** 需加入 generation/token 或 abort guard，并允许 rejected cache retry。
- **M-02 — Clear/close 后残留 stale `aria-expanded`、visual state，focus 可能回到错误 access path。** 需同步 SVG/table ARIA，记录 exact initiator，并防止 close 后重新 dimming。
- **M-03 — UI tests 只测 helper，无法证明 real page wiring。** 需增加 DOM/browser-level tests。

### Low

- **L-01 — P2 duplicate generated service contracts。** 建议改用 generated ServerTypes。
- **L-02 — Catalog failure/empty states 与 page-level status 矛盾。** 建议统一 error/empty/retry 状态。

首轮 decision：**changes requested**。P2 不可标记 independently reviewed，P3 不可启动。

## Focused Re-review — 2026-08-24

Remediation 后进行 fresh-context focused re-review，范围只覆盖原 H/M/L findings 与当前 P2 gate；P3 未进入，reviewer 不写 business code。

### 原 Findings 处置

| Finding | 处置 | 证据摘要 |
|---|---|---|
| H-01 | resolved | service 与 shared drawer/detail path 暴露并渲染全部 frozen sections；缺失事实显示 gap，不推断 claims。 |
| M-01 | resolved | request generation guards 与 rejected-cache eviction 已加入；stale completion 不再更新 active drawer。 |
| M-02 | resolved | SVG/table `aria-pressed`/`aria-expanded` 同步 reset；exact initiator focus restoration；close 后无 dimmed layers。 |
| M-03 | resolved with minor L-03 | suite 改为 fresh SQLite/Kestrel/Firefox real-page smoke，覆盖 9 modules/21 bindings、pointer/keyboard/drawer/detail/error。 |
| L-01 | resolved | page 使用 generated service namespace 与 DTO interfaces。 |
| L-02 | resolved | empty/failed catalog 走统一 status renderer，SVG/fallback/coverage/preview/retry 一致。 |

### Focused 验证

通过：

- `dotnet build SerenityQuantResearch.slnx --no-restore`
- `dotnet test SerenityQuantResearch.slnx --no-build`
- web `npm run test:ui`
- web `npm run build`
- TypeScript `tsc --noEmit --project tsconfig.json`
- additional exact-focus Firefox run
- taxonomy/seed exact ID check
- boundary/image/portability scans

### 新 Low Finding

- **L-03 — Browser smoke 仍有 assertion blind spots。** 它证明 real page 可运行，但 exact frozen ID set、function/module rendering、exact representation focus、fault-injected async/catalog cases 还可加强。该 finding 不表示当前功能缺陷，不阻塞 P2。

## 最终 Decision

**approved with minor findings**

无 Critical/High/Medium finding 残留。P2 service/UI contract、21 part bindings、pointer/keyboard/fallback/drawer/detail interactions、async guards、reset/focus、generated contracts、status handling、phase/artwork/evidence boundaries 均通过。L-03 作为后续 test hardening，不阻塞 P2 gate。

## 当前影响

- P2 independently reviewed：Yes。
- P3 gate at the time：可在单独授权 session 中打开。
- 当前 Research Experience Reboot：P2 的 domain/service/test 价值保留；legacy 3×3 research-facing UI 不再是产品事实源。
