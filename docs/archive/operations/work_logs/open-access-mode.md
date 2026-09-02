# Runtime Open-Access Mode 工作日志

## 状态

- Date: 2026-08-25
- Result: completed
- Scope：仅 runtime access/authentication override
- Phase implementation：P4/P5/P6 未启动
- 当前产品边界：该记录是历史 runtime 决策证据；Research Experience Reboot 的 research-facing 产品事实仍以 `docs/product/` 为准。

## 决策

操作者明确选择无需登录即可访问完整应用，包括 research writes、review actions 和 Administration capabilities。

因此 `appsettings.json` 中 `OpenAccess:Enabled` 默认是 `true`。cookie authentication 执行后，middleware 会把 request principal 替换为 authenticated `OpenAccess` principal，并映射到 persisted `admin` / user ID 1。现有 `PageAuthorize`、`ServiceAuthorize`、row permissions 和 audit code 继续执行，但解析为 admin superuser。

## 后果

- `/`、research pages 和 Administration pages 不再跳转到 login；
- read/write services 可在无 login session 下调用，browser writes 仍受 CSRF 保护；
- `/Account/Login` 与 `/Account/Signout` 在 open mode 下跳转到 `/`；
- sidebar 显示 open-lock indicator，而不是 login/profile/logout controls；
- anonymous visitor actions 都被 audit 为 admin user ID 1；
- open mode 下没有 individual visitor identity、human/machine identity 或 per-user accountability；
- 将 `OpenAccess:Enabled` 设为 `false` 可恢复 cookie-login 与 Serenity permission path。

该模式不适合 Internet-facing 或其他不受信任部署。当前安全边界是 network/process isolation。

## 文件

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Initialization/Startup.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/appsettings.json`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Membership/Account/AccountPage.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_Sidebar.cshtml`
- `tests/SerenityQuantResearch.Tests/OpenAccessIntegrationTests.cs`
- 已调整的既有 integration/browser tests
- `README.md`
- `operations/planning/phase-1-mvp.md`

## 验证

已通过：

- build：0 warnings，0 errors；
- 54/54 .NET tests；
- 10/10 UI state tests；
- fresh SQLite/Kestrel/Firefox browser smoke；
- anonymous root、CPO、company universe、Administration user page access；
- anonymous Administration user-list service access；
- anonymous audited CompanyExposure write attributed to admin user ID 1；
- login page bypass；
- protected mode endpoint policy tests with `OpenAccess:Enabled=false`；
- Broadcom 仍为 `candidate`；`EVD-2026-0001@v1` 仍为 `draft`。

## Preview

- `http://localhost:5000/Research/Companies`

## 当前限制

Research Experience Reboot 的 Workspace v1 是 read-only。任何新增 persistent research writing 之前，必须重新取得 Owner 对 identity、author attribution、audit ownership 和 all-admin Open Access 影响的决策。
