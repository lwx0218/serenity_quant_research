# Phase 1 P2 工作日志 — Interactive SVG 与 Part Research UI

## 状态

- Date: 2026-08-24
- Route: continue existing `plan`
- Result: completed and independently reviewed (`approved with minor findings`)
- P3 status at the time: ready but not started
- 当前解释：P2 工程、tests 与 review 是有效历史；其 3×3/admin-framed research-facing presentation 已被 Research Experience Reboot supersede。

## 已实现

### Data-driven CPO composition

- 在 `Modules/Research/Diagram/` 下增加 original abstract 3×3 system-board composition。
- Geometry 只是 presentation data，不包含 company、chain、technology 或 evidence relationship。
- 未 shipping JPEG、extracted pixel、traced geometry、static hotspot map 或 runtime image dependency。
- `PartResearchService.ListParts` 从数据库读取 9 modules 与 21 parts。
- 每个 SVG part group 使用 stable domain key 作为 `data-part-id`。
- tree/table fallback 与 visual path 共用同一 service catalog。

### Selection 与 accessibility

- Hover/focus 高亮 active part 并 dim unrelated modules。
- Click、Enter、Space 锁定 part selection 并打开 research drawer。
- Escape、close button、clear-lock button 释放 selection。
- SVG part groups 暴露 `role=button`、`tabindex=0`、accessible labels、pressed state、focus styling。
- table/tree fallback 让所有 seeded parts 都可通过 native button 访问。

### Drawer 与 detail

- Drawer/detail requests 使用 `PartResearchService.RetrieveCompleteChain`，不从 SVG 解析关系。
- 内容覆盖 function、module、boundaries、upstream/downstream gap、key-specification gap、industry-chain nodes、technology links、candidate companies、evidence/review state、conclusion gap、risks、warnings、unresolved questions。
- Empty/unverified sections 显示 explicit research gaps，不推断事实。
- Broadcom 保持 `candidate`；`EVD-2026-0001@v1` 保持 `draft`。
- 增加 `/Research/Parts/{partId}` 与 `/Research/Cpo` navigation。

### Independent-review remediation

- 修复 drawer/detail 缺失 frozen sections。
- 增加 latest-request generation guards 与 rejected-promise retry cache eviction。
- 修复 `aria-expanded`、pending cancellation、focus restoration 与 dimming reset。
- 增加 fresh SQLite/Kestrel/Firefox WebDriver BiDi browser suite。
- 使用 generated Serenity ServerTypes，移除 local duplicate DTO/service URL。
- 增加 catalog empty/error retry states。
- focused independent re-review 后，P2 获得 `approved with minor findings`；剩余 L-03 为 browser-test assertion precision / fault injection，不阻塞 P2 gate。

## 验证

通过：

```text
dotnet build SerenityQuantResearch.slnx --no-restore
# 0 warnings, 0 errors

dotnet test SerenityQuantResearch.slnx --no-build
# 13 passed, 0 failed

cd src/SerenityQuantResearch/SerenityQuantResearch.Web
npm run test:ui
# 5 Node state/request tests + fresh Kestrel/Firefox browser smoke passed
npm run build
# passed
```

Authenticated Kestrel HTTP/UI smoke 覆盖 `/Research/Cpo`、part detail、generated JS/CSS、`PartResearch/ListParts`、`RetrieveCompleteChain`，并证明 candidate/draft states preserved。

Firefox real-page coverage 覆盖 9 modules、21 SVG/fallback bindings、pointer/keyboard selection、drawer sections、ARIA/focus reset、fallback navigation、detail、error rendering。

## Known gaps at the time

- 只有一个 seed part 有 company/evidence chain；其他 parts 故意显示 missing coverage。
- Browser regression assertions 可继续加强 exact ID-set、exact representation focus、fault-injected async/catalog scenarios。
- 仅 Firefox headless 自动化；未覆盖 physical desktop、screen reader、contrast、zoom/high-contrast、cross-browser。
- JPEG provenance/public reuse rights 未解决。
- 默认 Serene development authentication 不是生产加固。

## P3 readiness at the time

P3 可在不改变 P2 SVG contract 的前提下启动：stable part IDs、service-based part-to-company/evidence navigation、candidate/draft labels 与 stable part detail URLs 已存在。该记录不授权自动启动 P3。
