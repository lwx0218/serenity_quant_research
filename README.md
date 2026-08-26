# Serenity Quant Research

Finance-first 产业链投研工作台，基于 `serenity-is/Serenity`。Phase 1 首个主题为光模块 / CPO。

当前实现到 **P3：公司研究池、比较与详情**，并已通过独立复审（`approved with minor findings`，原始 `changes requested` 历史保留）；P2 同样已独立复审通过。不包含行情、K 线、账户、交易、回测或浏览器抓取功能；P4 尚未开始。

## Toolchain

- .NET SDK `10.0.400`（见 `global.json`）
- Node.js `>=24.10.0 <25`
- npm `>=11.6.2 <12`
- Firefox（仅用于 `npm run test:ui` 的无头浏览器回归）
- `Serene.Templates` / Serenity packages / `sergen` `10.3.7`

## Restore and build

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
npm run test:ui       # unit state tests + fresh Kestrel/Firefox browser smoke
```

## Run

```bash
dotnet run \
  --project src/SerenityQuantResearch/SerenityQuantResearch.Web/SerenityQuantResearch.Web.csproj
```

默认开发地址由 `Properties/launchSettings.json` 定义。当前按项目要求启用免登录开放模式，直接打开：

- 公司研究池：`http://localhost:5000/Research/Companies`
- Broadcom 公司详情：`http://localhost:5000/Research/Companies/global.broadcom`
- CPO 部件研究图：`http://localhost:5000/Research/Cpo`
- 部件详情示例：`http://localhost:5000/Research/Parts/cpo.part.host-asic.switch-die`

> **安全警告：** `appsettings.json` 当前设置 `OpenAccess:Enabled = true`。任何可访问应用的人都会被映射为内置 `admin`（user ID 1），可使用研究写入、审核和 Administration 管理能力；审计记录也会统一归属 admin。此模式仅适合受信任、隔离的本地环境。要恢复登录和 Serenity 权限边界，将该配置改为 `false`。

首次启动会：

1. 在应用的 `App_Data/` 下创建本地 SQLite 数据库；
2. 执行 FluentMigrator migrations；
3. 幂等导入 `data/seeds/cpo/cpo-research-seed.json`。

数据库、上传文件和 machine-local settings 已被 `.gitignore` 排除。

## P3 company research baseline

- `CompanyUniverseService` 返回 20 家稳定公司 ID、显式 exposure/evidence 关系、研究缺口、覆盖与新鲜度
- SleekGrid-first 高密度列表、冻结身份列、服务端筛选、排序和最多五家公司比较
- 原生表格 fallback、键盘比较选择和稳定公司详情导航
- 七个冻结公司详情 tabs，以及 part / chain node / company 双向 cross-navigation
- `Research:Review` exposure 编辑与审计；没有 reviewed Level A/B supporting evidence 时服务端拒绝 `verified`
- 当前 runtime 为全开放模式：无需登录，所有请求以 `admin` 身份运行；底层 protected-mode 权限/人机策略测试仍保留
- Broadcom 保持 `candidate`，`EVD-2026-0001@v1` 保持 `draft`

## P2 interaction baseline

- 原创 3×3 二维系统构成 SVG；未复制、描摹或发布两张 seed JPEG
- SVG group 只保存 presentation geometry 与稳定 `data-part-id`
- 21 个 seed part 均由 `PartResearchService` 目录解析并可选择
- hover/focus 高亮、无关模块 dim、click/Enter/Space 锁定、Escape/按钮清除
- 部件研究 drawer、完整部件详情导航，以及 tree/table 非指针 fallback
- 公司 verification state 与 evidence review state 原样显示；candidate/draft 不升级

## P1 domain baseline

- 9 个 `PhysicalModule`
- 21 个递归可扩展的 `PhysicalPart`
- 10 个独立 `IndustryChainNode`
- 20 家双层公司候选池
- part ↔ technology / industry-chain 多对多关系
- company exposure、source document、event、evidence
- versioned conclusion/report 与锁定引用关系
- evidence review 状态与人工审核权限边界
- 一条可查询的 part → company exposure → draft evidence 示例链

研究 seed 中的公司映射保持 `candidate`，示例 evidence 保持 `draft`；不得视为已审核事实。

## Key paths

- `docs/research-baseline/`：taxonomy、公司池和 evidence contract
- `data/seeds/cpo/`：版本化研究 seed
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/`：研究对象、服务与审核策略
- `tests/SerenityQuantResearch.Tests/`：seed、递归关系、审核状态和集成测试
- `operations/planning/phase-1-mvp.md`：冻结范围与执行阶段
