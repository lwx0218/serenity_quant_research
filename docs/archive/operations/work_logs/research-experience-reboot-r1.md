# Research Experience Reboot — R1 工作日志

Round: R1 — P0–P3 Code Disposition And Domain Audit
Plan: operations/planning/research-experience-reboot.md
Git baseline: 7cf1b95d23a5da3dd53766049557a67ed18fae73

## Status

- Round: `R1 — P0–P3 Code Disposition And Domain Audit`
- Primary session: `R1-code-disposition-audit`
- Date: 2026-08-28 UTC
- 候选状态：审计已完成，自动验证通过；R1 candidate/context/environment scope 已按新治理标准界定
- 验收状态：**accepted-effective**
- 当前治理决定：不再在 R1 中继续修 bwrap、provider auth 或 `.pi/extensions/harness-flow`；automated review capability blocker 已作为 governance maintenance / review limitation 留档
- 下一门禁：R1 停止；R2 需要 Owner 另行 start decision，不得自动启动

## Boundary

Completed a read-only inspection of P0–P3 product/frontend, routes, services, entities, migrations, seed, generated contracts, and tests. R1 原始预期写入面仅包括：

- `operations/reviews/reboot-p3-code-disposition.md`
- `operations/work_logs/research-experience-reboot-r1.md`
- `operations/reviews/research-experience-reboot-r1-independent-review.md`

Owner 后续授权 Plan 状态修正与本项目持续 Independent Review；但 2026-08-28 的治理复盘重新明确：R1 产品 candidate 不应因 automated review bundle 或 dirty worktree 扩张到治理工具实现。

按新标准，R1 scope 分类如下：

- **R1 product-audit candidate**：`operations/reviews/reboot-p3-code-disposition.md`、`operations/work_logs/research-experience-reboot-r1.md`、`operations/reviews/research-experience-reboot-r1-independent-review.md` 中与产品审计/验证/评审直接相关的内容。
- **Context scope**：`AGENTS.md`、`operations/planning/research-experience-reboot.md`、`operations/orchestration/research-experience-reboot.md`、`operations/orchestration/independent-review-and-round-scope-standard.md`、`docs/product/`、`docs/research-baseline/`、当前 P0–P3 source/test baseline。
- **Governance maintenance / dirty state**：`.pi/extensions/harness-flow/index.ts`、starter governance update、docs references 整理、harness sandbox/auth 实验性修复。

结论：`.pi/extensions/harness-flow` 与 bwrap/provider-auth 修复不再作为 R1 产品审计 candidate；若继续处理，必须作为单独 governance maintenance。任何 application code、schema、migration、seed、runtime configuration 或 test 均未修改。

Owner 进一步固定规则：产品开发过程中不得擅自修改 `.pi/` / harness 治理层。发现问题默认记录到 `operations/orchestration/governance-maintenance-backlog.md` 或 review limitation；只要不直接阻断产品开发或验收判断，就继续当前产品 Round。只有严重恶性 bug 导致项目无法继续，并经 Owner 明确授权，才允许单开治理维护修改 `.pi/` / harness 文件。本次 scope 漂移已记录为 `GOV-001`。

## Round-Start Evidence

```text
HEAD: 7cf1b95d23a5da3dd53766049557a67ed18fae73
```

Round start 时 worktree 已包含大量与 R1 无关的 governance/data 变更。以下是当时完整的 `git status --short` durable snapshot：

```text
 M .pi/agents/README.md
 M .pi/prompt-templates/governance-loop.md
 M .pi/settings.json
 M .pi/skills/governance-loop-entry/SKILL.md
 M .pi/skills/grill-me/SKILL.md
 M .pi/skills/grill-with-docs/SKILL.md
 M .pi/skills/grilling/SKILL.md
 M AGENTS.md
 M README.md
 M docs/project-intake/serenity-quant-research.md
 M operations/planning/phase-1-mvp.md
 M operations/planning/serenity-bootstrap.md
?? .pi/extensions/
?? .pi/prompt-templates/project-kickoff.md
?? .pi/prompt-templates/session-handoff.md
?? .pi/skills/domain-modeling/
?? Harness_manual.md
?? data/
?? docs/PI_HANDOFF.md
?? docs/product/
?? docs/serenity-product-reboot-package.zip
?? operations/archive/
?? operations/orchestration/
?? operations/planning/2026-08-28-starter-governance-update.md
?? operations/planning/reboot-mvp.md
?? operations/planning/research-experience-reboot.md
?? operations/reviews/product-reboot-consistency-review.md
?? operations/work_logs/2026-08-28-starter-governance-update.md
?? src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md
```

其中受保护路径状态为：

```text
?? data/
?? src/SerenityQuantResearch/SerenityQuantResearch.Web/AGENTS.md
```

These pre-existing untracked paths were preserved. `data/seeds/cpo/cpo-research-seed.json` was read but not edited.

## Inspection Performed

1. Read applicable governance, product specs/prototypes, visual/acceptance contracts, evidence contract, canonical Plan/orchestration, and legacy P0–P3 evidence.
2. Enumerated all tracked authored `Modules/Research` files, all generated Research ServerTypes, relevant shell/root/navigation surfaces, both research migrations, seed source, and all .NET/UI test files.
3. Traced route/controller → Razor/TypeScript → generated DTO → endpoint/service → rows/links/migrations → seed/tests using `find`, `git ls-files`, and `rg`.
4. Read every authored Research module and every research test/harness file.
5. Measured seed relationship coverage with `jq`.

Inventory coverage recorded in the audit:

```text
authored Modules/Research files: 30 / 30 classified
generated Research ServerTypes: 47 / 47 classified
research .NET/UI test and harness files: 12 / 12 classified
```

## Delivered Finding

The durable audit is:

- `operations/reviews/reboot-p3-code-disposition.md`

Its conclusions are:

- preserve stable domain/service/evidence/audit assets;
- adapt shell/routes/queries/context;
- replace the legacy Explorer and Company product presentations;
- hide admin/secondary routes from primary research navigation;
- delete only proven-dead frontend in R7;
- use a schema-preserving derived module/part/technology/exposure query for v1;
- do not invent missing materials or company relationships.

## Child / Material Capability Evidence

Read-only seed inspection returned:

```text
modules=9 parts=21 parent_links=0 technologies=4
part_technology_links=10 chain_nodes=10 part_chain_links=21
companies=20 seeded_exposures=1
```

Existing schema supports recursive parts, part↔technology, part↔chain, and company exposure to part/chain. Current services only query an exact part or chain node; they do not aggregate module children/descendants or reverse technology/material→company paths. Current data has no recursive parent links, no discrete reviewed material catalog, and only one candidate exposure.

R1 finding: query/service adaptation is required; no schema migration is required for an explicitly derived read-only v1 path. A required direct material↔company edge or new semantic persistent object would trigger rebaseline.

## Validation Record

### Completed before evidence write

- Start `git rev-parse HEAD`: `7cf1b95d23a5da3dd53766049557a67ed18fae73`
- Start full `git status --short`: captured in session evidence.
- Start `git status --short -- src tests data`: only the two pre-existing untracked paths above.
- Initial `git diff --exit-code -- src tests data`: exit `0`.
- Audit manifest coverage script: 30/30 authored, 47/47 generated, 12/12 tests found in the matrix.
- Cited-path existence check: all repository file citations exist; the only ignored token was the descriptive directory label `Modules/Research/`.

### Final automated gate (passed before Independent Review)

- End candidate `git rev-parse HEAD`: unchanged at `7cf1b95d23a5da3dd53766049557a67ed18fae73`.
- `git diff --exit-code -- src tests data`: exit `0`.
- End candidate `git status --short -- src tests data`: exactly the same two pre-existing untracked paths as Round start (`data/` and scoped `AGENTS.md`).
- Audit manifest coverage: authored Research `30/30`; generated Research ServerTypes `47/47`; research tests/harness `12/12`.
- 初始 disposition profile check：`16/16`；required dispositions：`5/5`。Independent Review 修正后新增 `ENDPOINT-ADAPT-IDENTITY` 与 `ACTOR-IDENTITY-KEEP`，当前为 `18/18`。
- Repository file citations checked: `115`; missing: `0`.
- Seed relationship assertions: passed for counts plus `candidate` / `draft` / `contextualizes` safety states.
- `find`/`rg` source trace confirmed parent-part, part↔technology, part/chain↔company exposure, seed/import/validator, service, and test surfaces.

### Independent Review attempt (blocked)

The Builder automatically called `harness_run_independent_review` after the green automated gate. The tool returned:

```text
Review decision: blocked
Reason: Round R1 must be declared uniquely as in_progress for Review
```

No child process was spawned, so no valid P0/P1/P2 findings exist. The Builder wrote the required process/status/immutability record to `operations/reviews/research-experience-reboot-r1-independent-review.md`.

The canonical Plan says `Active Round: R1` but the R1 Ledger row remains `pending`. The Builder did not modify the approved Plan because R1 authorizes writes only to the three declared audit/review evidence surfaces.

Post-attempt HEAD and protected status remained unchanged; `git diff --exit-code -- src tests data` still exited `0`.

### Owner 授权与重新评审

2026-08-28，Owner 已授权：

1. 将 canonical Plan 中唯一的 R1 Ledger 状态从 `pending` 修正为 `in_progress`；
2. 本项目中 Plan 声明的 Independent Review 采用持续授权，满足候选验证和隔离条件后无需逐轮再次询问。

该授权不等于 R1 验收，也不自动授权 human-review fallback、commit、push 或启动 R2。

第一次重新调用在 child spawn 前再次被工具阻塞：

```text
Review decision: blocked
Reason: declared review work log lacks unique authoritative Round/Plan metadata
```

原因是工作日志的 `Round` 位于 `## Status` 之后，工具只从首个二级标题之前读取权威元数据，同时工作日志缺少唯一的 `Plan` 与 `Git baseline` 字段。没有 child process 被创建，也没有有效 P0/P1/P2。

Builder 已在本文件首个二级标题前补充唯一的 `Round`、`Plan` 和 `Git baseline` 元数据。下一次调用通过该门禁，但仍在 child spawn 前因 `scopePaths` 包含目录 `docs/product` 而阻塞；工具要求 scope 中每一项均为普通非符号链接文件。该次同样没有 child process 或有效 finding，候选与受保护路径未变。

Builder 将 review scope 展开为明确文件后重新执行 Verify → Independent Review。

### 有效 Independent Review 与修正

第四次调用成功创建 distinct read-only child，返回：P0=0、P1=2、P2=1，candidate immutable。

- P1（machine principal 可被 endpoint 硬编码为 human reviewer）：审计已将 `EvidenceWorkflowEndpoint.cs` 从 KEEP 改为 ADAPT，声明可信 actor-type 校验及 endpoint-level machine-principal 拒绝测试为后续必需项；R1 不修改 production/test。
- P1（`per-round` 与 `per_round` 不一致）：已修复 `.pi/extensions/harness-flow/index.ts` 的 Final Integrated Review 前置校验，并补齐 review artifact preamble metadata。
- P2（Boundary 未列 Plan 例外）：已接受并更新本日志 Boundary。

第一次 Re-review 返回 P0=0、P1=1、P2=2，candidate immutable：

- P1（后续 Round 可绕过前序 accepted-effective / Active Round 门禁）：已强化 `assertEffectiveRoundSet`，同时约束 Active Round、全部前序 Ledger 状态和 accepted-effective 精确集合。
- P2（Executive Finding 把 endpoints 统一列为 KEEP）：已修正摘要，与详细 ADAPT 矩阵一致。
- P2（starter governance work log 含宿主机绝对路径）：已改为 `<project-root>` placeholder。

第二次 Re-review 返回 P0=0、P1=2、P2=2，candidate immutable：

- P1（Evidence endpoint 身份缺陷无后续 owner）：已明确纳入 R7 的 delivery、change surfaces、tests 和 acceptance evidence。
- P1（R3 material readiness 与权威数据缺口冲突）：已将 R3 Plan/CPO spec 改为真实 children + 权威 material 或明确 gap state。
- P2（Workspace writing/OpenQuestion 与 Company Comparison 延期语义不一致）：相关 product docs 已统一为 read-only/deferred。
- P2（Round-start 全量 dirty status 未 durable）：本日志已补充完整起始 snapshot。

第三次 Re-review 返回 P0=0、P1=3、P2=2，candidate immutable：

- P1（review child 无 read confinement）：extension source 已增加 bubblewrap OS-level 只读 review root，host project/HOME/procfs 不可见；当前 runtime 需 `/reload` 后才能生效。
- P1（R1 ownership 未覆盖实质 review fixes）：Plan Expected change surfaces 与本日志 Boundary 已完整同步。
- P1（actor-type dependencies 未分类）：审计新增 `ACTOR-IDENTITY-KEEP`，覆盖 `UserActorTypes`、`UserRow`、`UserSaveHandler` 及可复用 endpoint/test pattern。
- P2（Experience Map/Workspace 仍有 deferred scope）：已统一为 read-only existing-object/derived gap，并移除 current Comparison/ResearchNote acceptance。
- P2（历史参考含 `computer:///`）：五个 host-specific link 已替换为不可伪造的历史材料说明。

代码与文档修正完成后，Owner 继续 R1 评审。第八次调用已进入 read-confined path，但 bwrap 内不暴露 host HOME，导致 child 找不到 host HOME 下的 Node runtime 并在启动阶段 blocked；candidate immutable。Builder 已修复 confined invocation：host HOME Node runtime 自动替换为 `/opt/module/nodejs/node/bin/node`。

修复 Node runtime path 后再次调用，child 在 sandbox 内启动但缺少 provider credential，返回 `No API key found for openai-codex`；candidate immutable。Builder 已验证 bwrap 内 bundled Node + `--api-key <bearer>` 可通过 auth smoke，随后修复 extension：reviewer args 注入 provider credential，并在 process evidence 中脱敏为 `<redacted-provider-auth>`。

修正后再次执行完整 R1 automated verification 与 confined Re-review。第十次调用仍在 provider auth handoff 处 blocked：readConfinement 已为 true，child 是独立进程且候选 immutable，但 sandbox 内没有可用 openai-codex credential。Owner 已说明不再重复 reload；该 blocker 后续改按治理标准记录为 review capability limitation，而不是进入 human fallback。

2026-08-28T08:52:33Z，Owner 曾因误解授权 R1 使用 distinct human review fallback；随后明确撤回/不采用该 fallback，要求回到 automated spawned review 的 scope 与 capability 标准。当前 R1 下一步是 scope-bounded `spawned_pi_process` Independent Review；`.pi` / harness 问题不再作为 R1 product-audit candidate。

回到 spawned review 后，工具发现 R1 Plan 的 `Independent Review mode` 字段含说明句，无法被 parser 当作精确枚举值。Builder 已将该字段恢复为 machine-readable `spawned_pi_process`；fallback 说明仍由治理标准承载。

2026-08-28T09:58:32Z，再次按 scope-bounded review 调用 `harness_run_independent_review`。结果仍为 automated capability/auth blocker：distinct child 创建成功、candidate immutable，但 sandbox 内 provider auth 不可用。按新标准，该问题记录为 review capability limitation / governance maintenance，不再作为 R1 product-audit finding，也不继续修 `.pi` / harness。

2026-08-28T10:01:31Z，Owner 确认进入 Owner acceptance gate，并将 automated review capability blocker 作为已留档 limitation / governance maintenance；不再等待有效 spawned review，不采用 human fallback。

2026-08-28T10:01:31Z 后，Owner 明确回复“验收R1”。Builder 已将 canonical Plan 更新为 `Accepted-effective Rounds: R1`、`Active Round: none`、R1 Ledger `accepted`，并将 review artifact decision 更新为 `owner_accepted_with_review_capability_limitation`。R1 停止；R2 需要 Owner 另行 start decision。

## Portability

The audit uses repository-relative paths. No secrets, host absolute paths, external workspace dependencies, runtime residue, dependency installation, commit, or push was introduced.

## Stop Rule

R1 has stopped after Owner acceptance with the automated review capability limitation documented. R2 must not start automatically. Acceptance commit/post-commit verification is authorized only if requested; no push is performed automatically.
