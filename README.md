# Serenity Quant Research

Finance-first 产业链投研工作台，基于 `serenity-is/Serenity`。首个主题为光模块 / CPO。

## Current Status — Research Experience Reboot

P0–P3 的 domain、service、data、policy、tests 与 review 历史继续保留；其 framework/admin/grid-first research-facing UI / UX 已被新的 approved product baseline supersede。旧 P4 暂停。

当前交付边界：

```text
CPO Explorer
→ Component / Material / Technology
→ Company Pool
→ Quick Drawer
→ Full Company Detail
→ Read-only Research Workspace
```

完整长期产品目标仍然是：

```text
Physical Product / Explorer
→ Component / Material / Technology
→ Company
→ Research Workspace
→ Evidence
→ Review
→ Conclusion
→ Report
```

Evidence Timeline/Review、Conclusion publishing 和 Report generation 没有被取消，但不属于当前 Research Experience Reboot 的验收范围。

## Canonical Baseline

- 文档索引：`docs/README.md`
- Product：`docs/product/`
- Research facts/evidence：`docs/research-baseline/`
- Plan：`operations/planning/research-experience-reboot.md`
- Orchestration：`operations/orchestration/research-experience-reboot.md`
- Legacy plan：`operations/archive/phase-1-mvp-p0-p3.md`

当前第一个实现 Round 是只读审计：`R1 — P0–P3 Code Disposition And Domain Audit`。不要自动进入 Research Shell。

## Product Areas

1. **CPO Explorer** — Flat / 3D Exploded、shared component state、callout、contextual drawer。
2. **Company Pool + Company Detail** — Card/List → Quick Drawer → Expand → entity-centric Full Detail。
3. **Research Workspace v1** — read-only、linked-object-first；无 Graph、New Note 或持久化编辑。

Serenity 继续作为 host、service/data、permission、audit、migration 和 admin maintenance 基础，但不定义 research-facing 产品设计。

## Research-data Boundary

Prototype 和 Gemini design reference 中的 BOM%、国产化率、market share、supplier/customer relationship、company tier、investment thesis、production/sampling status、technology-barrier score 都不是 research fact。没有 evidence contract 支持时使用 `Unknown`、`Not reviewed`、`Candidate`、system-derived status 或省略。

## Toolchain

- .NET SDK `10.0.400`（`global.json`）
- Node.js `>=24.10.0 <25`
- npm `>=11.6.2 <12`
- Firefox（UI browser regression）
- Serenity / Serene / sergen `10.3.7`

## Restore And Build

```bash
dotnet restore SerenityQuantResearch.slnx

cd src/SerenityQuantResearch/SerenityQuantResearch.Web
dotnet tool restore
npm ci
npm run build
cd ../../..

dotnet build SerenityQuantResearch.slnx --no-restore
dotnet test SerenityQuantResearch.slnx --no-build

cd src/SerenityQuantResearch/SerenityQuantResearch.Web
npm run test:ui
```

## Run

```bash
dotnet run \
  --project src/SerenityQuantResearch/SerenityQuantResearch.Web/SerenityQuantResearch.Web.csproj
```

当前本地 runtime 使用 `OpenAccess:Enabled = true`：任何可访问请求都映射为 admin，只适合受信任、隔离环境。任何新增 persistent research writing 前，必须先决定 identity、author attribution 和 audit ownership。

当前主要入口：

- 公司研究池：`http://localhost:5000/Research/Companies`
- CPO：`http://localhost:5000/Research/Cpo`

这些页面仍可能显示 P2/P3 legacy presentation，直到对应 reboot Round 被接受。

## Existing Engineering Baseline

优先复用：

- 9 个 `PhysicalModule`、21 个递归 `PhysicalPart`、10 个 `IndustryChainNode`
- 20 家双层公司候选池、stable IDs、company exposure
- part ↔ technology / chain relationships
- source/event/evidence、review states、audit/permission policy
- versioned conclusion/report model、SQLite migrations、seed importer
- `PartResearchService`、`CompanyUniverseService` 与现有回归测试

Seed 中的 candidate/draft 状态不得因 UI 或 prototype 升级。
