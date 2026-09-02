# Phase 1 P1 工作日志 — Serenity Bootstrap 与核心对象

## 状态

- Date: 2026-08-24
- Route: `plan`
- Result: completed
- P2 status at the time: not started
- 当前解释：P1 是有效工程历史；Research Experience Reboot 的 research-facing UI/UX 由 `docs/product/` 与 canonical Plan 接管。

## 已实现

### Runtime 与项目结构

- 安装 user-local .NET SDK `10.0.400`、Node `24.19.0`、npm `11.17.0`。
- 使用 Community `Serene.Templates@10.3.7` 生成项目，未引入 demo modules。
- 增加 `global.json`、`SerenityQuantResearch.slnx`、web project、xUnit project、root ignore rules，并处理 `PLATFORM=linux` 主机兼容。
- 本地数据库从 LocalDB 改为 repository-relative SQLite，位于 web application 的 `App_Data/`。
- 禁用非必要 local background jobs、ClamAV 与 automatic Node watch startup。

### Research domain

FluentMigrator 与 Serenity Row models 覆盖：

- `Theme`
- `IndustryChain` / recursive `IndustryChainNode`
- `PhysicalModule` / recursive `PhysicalPart`
- `TechnologyLink`
- part ↔ technology、part ↔ industry-chain links
- `Company` / `CompanyExposure`
- `SourceDocument` / `Event` / versioned `Evidence`
- versioned `ResearchConclusion` / `ResearchReport`
- exposure/evidence、conclusion/evidence、report/conclusion、report/evidence locked-version links

主要实体使用 Serenity logging rows 与 insert/update audit fields。权限最小区分 general maintenance、evidence review、publication。

### Seed 与 services

- 增加 `data/seeds/cpo/cpo-research-seed.json`。
- 增加 duplicate/missing IDs、recursive cycles、broken references、source levels、machine-assisted seed evidence 必须 draft 的校验。
- 增加 idempotent startup importer。
- Seed 结果：9 modules、21 parts、10 chain nodes、4 technology links、20 companies。
- 增加一个刻意受限样例：`cpo.part.host-asic.switch-die` ↔ `global.broadcom`，exposure state `candidate`，evidence `EVD-2026-0001@v1` state `draft`。
- 增加 `PartResearchService` / endpoint 与 evidence workflow service/endpoint、conclusion publication policy baseline。

该样例只证明 data relationships，不声明 verified CPO product、supplier relationship 或 investment conclusion。

## 验证

通过：

```text
dotnet restore SerenityQuantResearch.slnx
dotnet build SerenityQuantResearch.slnx --no-restore
dotnet test SerenityQuantResearch.slnx --no-build
npm ci
npm run build
dotnet sergen doctor
```

结果：build 0 warnings/0 errors；tests 12 passed；fresh startup、login HTTP smoke、SQLite migration、seed idempotency、complete part → company exposure → evidence query 均通过。未加入 P2 SVG、copied JPEG layer、trading module、market data、account integration、backtest 或 browser runtime。

## Known gaps at the time

- 尚无 P2 research diagram、drawer、part page 或 table/tree UI。
- 公司 mappings 仍是 candidate/discovery；未提升为 `verified`。
- Seed evidence 仍是 `draft`；没有 conclusion/report publication。
- JPEG provenance 与 public reuse rights 未解决。
- 默认 Serene authentication/bootstrap 行为仍需生产加固。
- 当时 repository 无 `.git` metadata，因此 review 使用 file inventory 与 automated validation，而非 git diff。

## P2 readiness at the time

P2 可在不重新设计 schema 的前提下启动：stable `part_id`、physical/industry-chain 分离模型、recursive expansion、SVG geometry 到 domain IDs 的绑定路径、candidate/draft 状态保护均已存在。进入 P2 前应确认 original SVG visual composition 与 accessibility acceptance criteria。
