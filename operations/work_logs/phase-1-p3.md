# Phase 1 P3 工作日志 — Company Universe 与 Detail

## 状态

- Date: 2026-08-25
- Route: continue existing `plan`
- Result: completed and independently reviewed (`approved with minor findings`)，保留 initial `changes requested` 历史
- P4 status at the time: not started
- 当前解释：P3 的 domain/service/policy/tests 继续是有效工程历史；其 SleekGrid-first、comparison、seven-tab research-facing presentation 已被 Research Experience Reboot supersede。

## 已实现

### CompanyUniverseService 与 policy

- 基于既有 `Company`、`CompanyExposure`、`PhysicalPart`、`IndustryChainNode`、`Evidence`、source、event、conclusion、audit relationships 增加 `CompanyUniverseService`。
- 20 家 seeded companies 均通过 stable company ID 解析，并返回 identity/market fields、universe layer、coverage priority、explicit exposures、roles、relevance、confidence、verification state、scope note、evidence/review state、audit metadata、coverage、freshness。
- 无 exposure/evidence 的 companies 以 `unmapped` / research-gap 显示。
- Server filters 覆盖 part、chain node、role、exchange、geography、universe layer、priority、verification state、evidence coverage、freshness、identity search。
- 增加 stable chain-node retrieval 支持 company → chain → part/company cross-navigation。
- 增加 `Research:Review` 下的 exposure update policy；更新使用 Serenity logging-row audit fields，且必须针对 existing exposure。
- Promotion to `verified` 要求 authenticated human-review path 与 reviewed Level A/B supporting evidence。Draft、in-review、rejected、Level C、contextual-only evidence 不能满足 policy。Machine state changes 被 policy API 拒绝。

### Company universe、comparison 与 detail

- 增加 `/Research/Companies` 与 CPO research navigation item。
- 当时采用 Serenity 10.3.7 SleekGrid、高密度 layout、server filters 与 bounded five-company comparison。
- 增加 native table fallback 与 `?view=table`。
- 未新增 price movement、quote、market ranking、trading 或 export scope。
- 增加 `/Research/Companies/{companyId}`，包含 7 个 accessible tabs：Overview、Industry-chain Exposure、Earnings & Financial Evidence、Capex & Investment、Events、Research Conclusions、Sources & Audit。
- 缺失 typed records 时显示 explicit gaps，不做 keyword classification 或 fabricated claims。
- 增加 `/Research/ChainNodes/{chainNodeId}`，并完成 part/company/chain stable cross-navigation。

### Independent-review remediation

Initial fresh review 返回 `changes requested`，随后一次 bounded P3-only remediation 解决：

- Frozen identity columns：使用 Serenity `FrozenLayout` 并在 Firefox suite 中断言 3 个 `.sg-start` headers 与横向滚动固定。
- Human-only review：新增 migration-backed `Users.ActorType`，endpoint 从 persisted server identity 派生 reviewer humanity，并用 real endpoint test 证明 Review-authorized machine principal 被拒绝且不 mutation。
- Structured policy rejection：policy denials 使用 stable `ValidationError` codes 与 HTTP 400。
- Freshness：缺失 category 不再用 universal age threshold；剩余 report-period/label 语义作为 Low gap。

## 验证

通过：

```text
dotnet build SerenityQuantResearch.slnx --no-restore
# 0 warnings, 0 errors

dotnet test SerenityQuantResearch.slnx --no-build
# 51 passed, 0 failed

cd src/SerenityQuantResearch/SerenityQuantResearch.Web
npm run test:ui
# 10 Node UI state tests + fresh SQLite/Kestrel/Firefox browser smoke passed
npm run build
# passed; generated frontend output current

tsc --noEmit --project tsconfig.json
# passed with no diagnostics
```

Fresh SQLite / authenticated HTTP verification 证明：20 company IDs 全部解析；seed counts unchanged；Broadcom 仍为 `candidate`；`EVD-2026-0001@v1` 仍为 `draft/contextualizes`；machine identity 即使拥有 `Research:Review` 也不能完成 verified transition。

Boundary scans 未发现 P4 ingestion/timeline/transitions、P5 publication/version workflow、trading/K-line/quote/market/account/portfolio/order/backtest/chat-only scope、runtime JPEG use、image hotspots 或 inferred customer/supplier/order/revenue-share/mass-production claims。

## Known gaps at the time

- Seed 只有一个 candidate exposure 与一个 draft contextual evidence；多数公司/详情 tabs 显示 research gaps。
- Financial/Capex evidence 未做 keyword classification，因为当前 schema 无 reviewed typed relationship。
- Exposure evidence associations 只显示，不编辑；evidence ingestion/review transitions 仍是 P4 scope。
- Low gaps：freshness category/next-report semantics、Serenity 对 handled policy `ValidationError` 的 fail-level logging noise。
- 仅 Firefox headless 自动化；未覆盖 physical desktop、screen reader、contrast/high-contrast/zoom、cross-browser。
- JPEG provenance/public reuse rights 未解决。

## 当前 Reboot 影响

Research Experience Reboot 保留 P3 backend/service/policy/test 价值，但替换 Company research-facing presentation：未来 R5 应交付 Card/List → Quick Drawer → entity-centric continuous/lightly segmented Full Detail，不继续默认 SleekGrid/comparison/seven-tab 产品体验。
