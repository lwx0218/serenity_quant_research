# Serenity P1 Bootstrap Decision

> **Authority boundary after Research Experience Reboot**
>
> This document remains authoritative for the Serenity/.NET/Node/SQLite technical bootstrap, supported versions, build commands, and portability decisions. It is not authoritative for research-facing information architecture, navigation, interaction, page composition, or visual design. For those decisions use `docs/product/` and `operations/planning/research-experience-reboot.md`.
>
> Historical statements such as “不另建 SPA 壳” prohibit an unnecessary new application framework; they do not require Serenity default research UI to remain the product shell.

## 1. 决策状态

- 状态：Phase 1 P1 已按本决策执行
- 决策日期：2026-08-24
- 执行日期：2026-08-24
- 实现位置：`src/SerenityQuantResearch/SerenityQuantResearch.Web/`

| 决策项 | 锁定选择 |
|---|---|
| 技术底座 | `serenity-is/Serenity` Community 生态 |
| 项目模板 | 截至决策日的稳定版 NuGet `Serene.Templates@10.3.7`，template short name `serene` |
| Demo modules | `false`，不引入 Northwind/Basic Samples |
| Serenity packages | `Serenity.*`、`sergen`、`@serenity-is/tsbuild` 全部对齐 `10.3.7` |
| .NET | .NET 10 LTS，SDK `10.0.400`（`global.json` 锁定 feature band/patch 策略） |
| Node/npm | Node 24 LTS，最低 Node `24.10.0`；npm 最低 `11.6.2` |
| 初始数据库 | SQLite，本地相对路径；生产数据库选择延后 |
| UI | 模板自带 TypeScript/Preact、Serenity Corelib 与 SleekGrid；不另建 SPA 壳 |
| 商业模板 | 不选 StartSharp；当前没有许可证需求，也不需要其高级样例完成 MVP |

## 2. 选择依据

1. Serenity 官方文档将 Serene 定义为免费开源 starter，适合 Serenity data-centric business application。
2. 独立 `serenity-is/Serene` 仓库已归档并声明内容并入 `serenity-is/Serenity/tree/master/serene`；不得从旧仓库复制 8.x 模板。
3. NuGet `Serene.Templates` 当前锁定版本 `10.3.7` 与 Serenity Git tag/package 版本一致。
4. 模板目标框架为 `net10.0`，并将 `Serenity.Corelib`、`Serenity.Net.Web`、`Serenity.Extensions` 和 `sergen` 锁到 `10.3.7`。
5. Serenity 10.3.7 `sergen doctor` 推荐 Node `24.10.0+`、npm `11.6.2+`；本计划按该要求，不用“构建可能侥幸通过”替代受支持版本。
6. Community Serene 已提供 service/data/list/dialog/auth/audit 基础和 SleekGrid 依赖，符合冻结的技术母本；StartSharp 的商业特性不构成 P1 前置条件。

### 官方/权威入口

- Serenity repository/tag：https://github.com/serenity-is/Serenity/tree/10.3.7
- Serene source in monorepo：https://github.com/serenity-is/Serenity/tree/10.3.7/serene
- NuGet template：https://www.nuget.org/packages/Serene.Templates/10.3.7
- Serenity guide：https://serenity.is/docs/
- .NET 10 lifecycle：https://dotnet.microsoft.com/platform/support/policy/dotnet-core

## 3. P0 技术验证记录

在仓库外的临时目录完成：

- 安装 .NET SDK `10.0.400`；
- 安装 `Serene.Templates@10.3.7`；
- 使用 `--DemoModules false` 生成 `SerenityQuantResearch.Web`；
- 确认目标框架 `net10.0`，Serenity 与 sergen 均为 `10.3.7`；
- 使用 Node `v24.19.0` / npm `11.17.0`；
- `dotnet tool restore`、`dotnet restore`、`dotnet build --no-restore`、`npm run build` 全部通过；
- `dotnet sergen doctor` 通过版本一致性检查；
- 生成项目不包含 Northwind/Basic Samples。

P1 执行时已在用户目录持久化安装 .NET SDK `10.0.400`、Node `v24.19.0` 和 npm `11.17.0`，并通过 shell profile 将用户本地工具目录置于 PATH 前部。Docker daemon 权限不再构成路径依赖。

## 4. P1 目录约定

P1 bootstrap 后的目标结构：

```text
.
├── global.json
├── SerenityQuantResearch.slnx
├── data/
│   └── seeds/
│       └── cpo/                 # taxonomy/company/example evidence 的版本化 JSON seed
├── docs/
│   └── research-baseline/       # P0 合同和研究基线
├── src/
│   └── SerenityQuantResearch/
│       └── SerenityQuantResearch.Web/
│           ├── .config/dotnet-tools.json
│           ├── Initialization/
│           ├── Migrations/DefaultDB/
│           ├── Modules/
│           │   ├── Administration/   # Serene 必要基础
│           │   ├── Common/
│           │   └── Research/         # P1 业务对象与服务；不放进 .pi/
│           ├── wwwroot/
│           ├── package.json
│           ├── package-lock.json
│           ├── sergen.json
│           └── SerenityQuantResearch.Web.csproj
└── tests/
    └── SerenityQuantResearch.Tests/
```

约束：

- `Research` 按 domain/service 组织，不创建交易、行情、账户、回测或 chat-only 模块。
- SVG presentation data 在 P2 再进入应用；P1 只建稳定 domain ids 与关系，不从 JPEG 生成热区。
- seed 使用仓库相对路径并可重复导入；运行时数据库、上传、密钥和本地覆盖不提交。
- 模板默认 LocalDB 配置不适合当前 Linux/portable 开发基线；P1 改为 `Microsoft.Data.Sqlite`，连接串使用相对 `App_Data/serenity-quant-research.sqlite`，并确保数据库文件被忽略。
- 背景任务、ClamAV、SMTP 等非 P1 必需能力在本地配置中默认关闭或保持未配置，不扩大 bootstrap 范围。

## 5. P1 依赖

### 必需

- .NET SDK `10.0.400`（允许同一 10.0.4xx feature band 的安全 patch，最终由 `global.json` 控制）
- Node.js `>=24.10.0 <25`
- npm `>=11.6.2 <12`
- NuGet template `Serene.Templates@10.3.7`
- 本地工具 `sergen@10.3.7`（模板 manifest 自动提供）
- SQLite provider（模板已引用 `Microsoft.Data.Sqlite` 和 FluentMigrator SQLite runner）
- xUnit 测试项目，目标 `net10.0`

### P1 不新增

- 不新增独立 React/Vue/Next.js 前端；
- 不新增行情、券商、交易、回测 SDK；
- 不新增浏览器 extension/crawler runtime；
- 不引入 StartSharp 或其他商业 package；
- 不引入 WebGL/3D/CAD 工具链；
- 不在 `.pi/` 放置应用依赖或业务代码。

## 6. P1 bootstrap 命令（从仓库根执行）

> 以下命令已在 P1 执行，保留为可复现 bootstrap 清单。

### 6.1 前置检查

```bash
dotnet --version          # 期望 10.0.400 / 受 global.json 允许的 10.0.4xx
node --version            # 期望 >= v24.10.0 且 < v25
npm --version             # 期望 >= 11.6.2 且 < 12
```

### 6.2 生成并锁定骨架

```bash
dotnet new globaljson --sdk-version 10.0.400 --roll-forward latestPatch
dotnet new install Serene.Templates@10.3.7
mkdir -p src/SerenityQuantResearch
dotnet new serene \
  -n SerenityQuantResearch \
  --DemoModules false \
  -o src/SerenityQuantResearch

dotnet new sln -n SerenityQuantResearch --format slnx
dotnet sln SerenityQuantResearch.slnx add \
  src/SerenityQuantResearch/SerenityQuantResearch.Web/SerenityQuantResearch.Web.csproj

dotnet new xunit \
  -n SerenityQuantResearch.Tests \
  -o tests/SerenityQuantResearch.Tests \
  --framework net10.0
dotnet sln SerenityQuantResearch.slnx add \
  tests/SerenityQuantResearch.Tests/SerenityQuantResearch.Tests.csproj
dotnet add tests/SerenityQuantResearch.Tests/SerenityQuantResearch.Tests.csproj reference \
  src/SerenityQuantResearch/SerenityQuantResearch.Web/SerenityQuantResearch.Web.csproj
```

生成后立即完成三项小改动再做业务对象：

1. 将开发数据库从模板默认 LocalDB 改为相对路径 SQLite；
2. 补齐根 `.gitignore`（`bin/`、`obj/`、`node_modules/`、`App_Data/*.sqlite*`、uploads、secrets/local overrides）；
3. 创建 `data/seeds/cpo/`，从 P0 baseline 显式转换 seed，不从 JPEG 自动抽取。

## 7. P1 验证命令

```bash
# 先恢复 .NET，再严格按 lockfile 恢复前端依赖
# （npm ci 的 preinstall 会调用 dotnet build -target:RestoreNodeTypes）
dotnet restore SerenityQuantResearch.slnx
cd src/SerenityQuantResearch/SerenityQuantResearch.Web
dotnet tool restore
npm ci
npm run build
dotnet sergen doctor
cd ../../..

# 根目录完整构建与测试
dotnet build SerenityQuantResearch.slnx --no-restore
dotnet test SerenityQuantResearch.slnx --no-build

# 启动后另一个 shell 做 HTTP smoke；端口以 launchSettings 为准
dotnet run \
  --project src/SerenityQuantResearch/SerenityQuantResearch.Web/SerenityQuantResearch.Web.csproj
curl --fail --location http://localhost:5000/
```

P1 还必须增加并通过以下自动化检查：

- `PhysicalPart` 递归父子关系及循环阻止；
- physical part ↔ industry chain 的多对多关系；
- company exposure 状态和证据关联；
- evidence 状态转换禁止跳过人工审核；
- 一条完整的 part → company exposure → reviewed evidence fixture 可查询；
- seed 二次导入幂等；
- solution/build 输出中没有 Northwind/Basic Samples，也没有交易类模块。

## 8. P1 开工门槛

| 门槛 | 当前状态 |
|---|---|
| CPO 两级 taxonomy 与稳定 ids | Ready：`docs/research-baseline/cpo-taxonomy.md` |
| 双层公司候选池 | Ready：`docs/research-baseline/company-universe.md` |
| evidence/review/citation/publication contract | Ready：`docs/research-baseline/evidence-contract.md` |
| Serenity template/version | Ready：`Serene.Templates@10.3.7` 已 smoke 验证 |
| 本机受支持工具链 | Ready：.NET `10.0.400`、Node `24.19.0`、npm `11.17.0` |
| JPEG provenance/public reuse right | Unresolved，但不阻塞 P1 domain bootstrap；禁止公开复用图片 |

结论：P1 bootstrap 已完成并通过 build、test、`sergen doctor`、HTTP/SQLite smoke。后续保持锁定版本，不重新选模板；进入 P2 前先复核 `operations/work_logs/phase-1-p1.md` 的 known gaps。
