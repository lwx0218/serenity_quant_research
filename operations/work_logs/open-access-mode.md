# Runtime Open-Access Mode Work Log

## Status

- Date: 2026-08-25
- Result: completed
- Scope: runtime access/authentication override only
- Phase implementation: P4/P5/P6 not started

## Decision

The operator explicitly selected full application access without login, including research writes, review actions, and Administration capabilities.

`OpenAccess:Enabled` therefore defaults to `true` in `appsettings.json`. After cookie authentication runs, middleware replaces the request principal with an authenticated `OpenAccess` principal mapped to persisted `admin` / user ID 1. Existing `PageAuthorize`, `ServiceAuthorize`, row permissions, and audit code continue to execute, but resolve through the admin superuser.

Consequences:

- `/`, research pages, and Administration pages no longer redirect to login;
- read and write services are callable without a login session, subject only to CSRF protection for browser writes;
- `/Account/Login` and `/Account/Signout` redirect to `/` while open mode is enabled;
- the sidebar shows an open-lock indicator instead of login/profile/logout controls;
- all anonymous visitor actions are audited as admin user ID 1;
- individual visitor identity, human/machine identity, and per-user accountability are not available in open mode;
- setting `OpenAccess:Enabled` to `false` restores the existing cookie-login and Serenity permission path.

This is not safe for an Internet-facing or otherwise untrusted deployment. Network/process isolation is the active security boundary.

## Files

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Initialization/Startup.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/appsettings.json`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Membership/Account/AccountPage.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_Sidebar.cshtml`
- `tests/SerenityQuantResearch.Tests/OpenAccessIntegrationTests.cs`
- existing integration/browser tests adjusted for the new runtime access contract
- `README.md`
- `operations/planning/phase-1-mvp.md`

## Verification

Passed:

- build: 0 warnings, 0 errors;
- 54/54 .NET tests;
- 10/10 UI state tests;
- fresh SQLite/Kestrel/Firefox browser smoke;
- anonymous root, CPO, company universe, and Administration user page access;
- anonymous Administration user-list service access;
- anonymous audited CompanyExposure write attributed to admin user ID 1;
- login page bypass;
- protected mode endpoint policy tests still pass with `OpenAccess:Enabled=false`;
- Broadcom remains `candidate` and `EVD-2026-0001@v1` remains `draft`.

## Preview

- `http://localhost:5000/Research/Companies`
