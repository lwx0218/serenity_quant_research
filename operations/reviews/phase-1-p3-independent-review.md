# Phase 1 P3 Independent Review

## 状态

- Gate：fresh independent P3 review
- Route：review-only
- Date：2026-08-25
- Write boundary：review record only
- P4/P5/P6：未进入；P4 remains unstarted
- 当前解释：这是 P3 历史 Independent Review；P3 backend/service/policy/test 继续有效，但其 SleekGrid-first、comparison、seven-tab research-facing presentation 已被 Research Experience Reboot supersede。

## Review 范围

Reviewer fresh-context 检查了：

- P3 planning、P0/P1/P2 evidence、taxonomy、company、evidence、bootstrap、seed、README 等文档；
- `CompanyUniverseService`、exposure policy/endpoint、entities、migrations、permissions、page controllers/views、company UI/state/CSS、P2 part service/UI、navigation、startup、generated ServerTypes/ESM/CSS；
- .NET tests、Node tests、Kestrel/Firefox browser runner；
- fresh SQLite、authenticated/anonymous HTTP、Firefox rendering、policy attempts、seed identity sets、prohibited-scope/portability scans。

当时 repository 无 `.git` metadata，因此无法独立证明 baseline diff、tracked/untracked 或文件引入时间；review 使用完整 file inventory、source tracing、generated-output checks、temporary runtime DB、tests、browser/HTTP evidence。

## 首轮验证结论

通过：

- `dotnet build SerenityQuantResearch.slnx --no-restore`：0 warnings，0 errors。
- `dotnet test SerenityQuantResearch.slnx --no-build`：40/40 tests。
- web `npm run test:ui`：10/10 Node tests 与 fresh SQLite/Kestrel/Firefox smoke，但隐藏了 H-01/H-02。
- web `npm run build`：generated outputs unchanged。
- TypeScript `tsc --noEmit --project tsconfig.json`：passed。

Source/data tracing 证明：20 companies exact set、explicit relationships、candidate/draft 状态、no SVG/JPEG/name/category inference、stable cross-navigation、no P4 evidence timeline/ingestion UI、no P5 publication workflow。

## 首轮 Findings

### Critical

无。

### High

- **H-01 — 三个 identity columns 在 real SleekGrid 中未实际 frozen。** 页面声明 frozen，但未使用 Serenity `FrozenLayout`；Firefox 实际得到 0 pinned headers。需改用 `FrozenLayout` 并增加真实 browser assertion。
- **H-02 — server 未从可信身份派生/强制 human reviewer。** endpoint 把任何 `Research:Review` principal 当作 human；Review-authorized machine principal 可完成 verified promotion。需新增 server-trusted actor type 或等价身份属性，并用 real endpoint test 证明 machine 被拒绝。

### Medium

- **M-01 — exposure-policy rejection 以 HTTP 500 endpoint failure 暴露。** 需改为 structured `ValidationError` / 4xx stable code，并证明 rollback。

### Low

- **L-01 — Freshness 使用 universal capture-age rule，而非 type-dependent contract。** 当前 seed 不误标，但未来 typed records 可能错误。

首轮 decision：**changes requested**。P3 不可标记 independently reviewed，P4 不可启动。

## Focused Re-review — 2026-08-25

一次 bounded P3-only remediation 后执行 focused re-review。原始 changes-requested history 保留；本节只 supersede 当前 P3 gate outcome。

### 原 Findings 处置

| Finding | Focused disposition | 证据摘要 |
|---|---|---|
| H-01 Frozen identity columns | Resolved | Authored/generated code 使用 Serenity 10.3.7 `FrozenLayout`；fresh Firefox 看到 3 个 `.sg-start` headers，横向滚动后 pinned headers x positions unchanged。 |
| H-02 Human-only exposure state changes | Resolved | `Users.ActorType` migration-backed；endpoint 从 DB reload authenticated actor；machine principal 即使有 `Research:Review` 与 eligible human-reviewed Level A support 也被 `MachineExposureStateChangeDenied` 拒绝且无 mutation。 |
| M-01 Structured policy rejection | Resolved for HTTP/error contract and rollback | Policy denials 返回 HTTP 400 与 stable codes；无 `InvalidOperationException` 或 HTTP 500；剩余 Serenity fail-level log noise 记为 Low。 |
| L-01 Freshness | Partially resolved; residual Low | 缺失/unknown category 返回 `unknown`，historical/90/180/365/450 helper cases 通过；report-period semantics 与 UI labels 仍有 Low gap。 |

## Focused 验证

通过：

- full build、.NET tests、web `npm run test:ui`、web `npm run build`、TypeScript no-emit；
- fresh SQLite schema check，确认 `Users.ActorType` non-null default `human`；
- anonymous/authenticated HTTP checks；
- candidate→verified 对 draft/contextual evidence 返回 `VerifiedExposureEvidenceRequired` 且不 mutation；
- Review-authorized machine principal 返回 `MachineExposureStateChangeDenied` 且不 mutation；
- Firefox 验证 20 unique companies、3 pinned headers、main viewport horizontal scroll；
- boundary scans 确认 no runtime JPEG/image、hotspot、SVG-derived relationship inference、trading/K-line/quote/account/portfolio/backtest、P4 timeline/ingestion、P5 publication UI。

## Focused 后剩余 Low Findings

- **L-01R — Freshness remediation 对当前 absent-category data 安全，但未完整实现 type/period contract。** materialized evidence 当前总是 `evidenceCategory: null`，所以返回 `unknown`；quarterly/half-year next-report semantics 与 UI labels 仍需后续单独处理。
- **L-02 — Expected policy denials 仍以 failure severity 记录。** HTTP 400/stable code/rollback 正确，但 Serenity logger 对 handled `ValidationError` 输出 fail-level stack trace，可能造成 observability noise。

## Unverified Items

- 未做 physical-desktop visual inspection、screen-reader/accessibility-tree audit、contrast/high-contrast/zoom、reduced-motion emulation、non-Firefox browser run。
- 未 fault-inject SleekGrid constructor failure。
- Admin UI editing of ActorType 只做 source/generated-contract verification，未通过 browser 手工演练。
- 当前 schema 无 persisted freshness category，因此 category-specific runtime behavior 只能通过 helper probe 验证。
- JPEG provenance/public reuse rights 未解决。
- 无 `.git` metadata，无法权威证明 diff/cleanliness/tracked state。

## 最终 Decision

**approved with minor findings**

H-01/H-02 resolved。M-01 的 HTTP 400/stable-code/rollback contract resolved；剩余 logging 是 operational noise。L-01 对当前 absent-category data 安全但保留 Low gaps。无 Critical/High/Medium finding 阻塞 P3 gate。

## 当前影响

- Focused re-review executed：Yes。
- Current P3 gate outcome at the time：accepted as independently reviewed with minor findings。
- P4 readiness at the time：P3 不再阻塞单独授权的 P4。
- 当前 Research Experience Reboot：P3 的 service/domain/policy/test 作为历史工程资产复用；research-facing UI/UX 不作为当前产品事实源。
