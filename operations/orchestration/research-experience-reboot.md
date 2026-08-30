# Research Experience Reboot — 编排合同

## Metadata

- Project: serenity_quant_research
- Document type: orchestration
- Status: approved
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: operations/planning/research-experience-reboot.md

## 状态

- Plan approval: approved
- Canonical Plan: `operations/planning/research-experience-reboot.md`
- Product Owner: Owner/user
- Implementation agent: Pi Builder in the Plan-declared primary session
- Independent Reviewer: distinct read-only Pi spawned through `harness_run_independent_review`，或 Owner 明确批准的 distinct human fallback
- Scope standard: `operations/orchestration/independent-review-and-round-scope-standard.md`

## 目的

本编排合同用于避免再次出现：

```text
错误产品合同
→ 看似正确的实现
→ tests 通过
→ research-facing 产品漂移
```

Builder 必须按以下优先级验证：产品目标、信息架构、交互、视觉层级、研究数据安全、可访问性、tests、build。

## 权威顺序

- Governance：适用 `AGENTS.md`
- Review/scope：`operations/orchestration/independent-review-and-round-scope-standard.md`
- Product behavior：`docs/product/` 中 Plan 声明的顺序
- Research facts / evidence / audit：`docs/research-baseline/evidence-contract.md` 与已评审 repository evidence
- Delivery / acceptance：`operations/planning/research-experience-reboot.md`

当前代码是实现证据，不是产品事实源。

## Per-Round Loop

```text
读取 durable contracts
→ 陈述当前 bounded understanding
→ 检查 current code/evidence
→ 只实现 active Round
→ 捕获 product-visible evidence
→ 运行 exact automated validation
→ 执行 Independent Review 或批准的 fallback
→ 在同一 Round 处理 P0/P1
→ 处置 P2
→ Product Owner gate
→ 经明确授权后 acceptance commit / post-commit verify
→ 停止
```

不得自动进入下一 Round。Continuation 保持同一 Round，使用 `<declared-session>-cont-2` 命名，不改变 scope 或 acceptance。

## Review Scope 三层模型

每次 Review 都必须明确：

1. `candidate scope`：本 Round 请求验收的交付物；可产生当前产品阻塞。
2. `context scope`：只读合同、Plan、spec、source、tests、baseline；用于判断 candidate，不自动成为 candidate。
3. `environment / dirty-worktree scope`：Git dirty/untracked、pre-existing local files、工具目录或残留；用于透明度和 immutability，不自动进入验收。

进入 review bundle 不等于进入 candidate scope。

## Product And Data Gates

- Serenity 是 infrastructure，不是 research-facing design authority。
- 不得静默新增 primary page、primary navigation item、permanent sidebar、tab/filter/metric/comparison family、Graph 或 research-facing admin capability。
- Prototype behavior/visual direction 可指导交互；prototype claims 绝不成为 research facts。
- Unsupported values 使用 `Unknown`、`Not reviewed`、`Candidate`、system-derived state 或 omission。
- Candidate/draft 状态不得通过 UI 呈现升级为 verified/reviewed。
- Prototype 的 hit-zone、overlap、keyboard 或 mock-state 局限是 production acceptance defect，不是默认接受项。

## Workspace And Open Access Gates

Workspace v1 是 read-only + linked-object-first。它不引入 persistent ResearchNote、OpenQuestion、Backlink、Graph 或 editor。

`OpenAccess:Enabled = true` 仅允许在受信任隔离环境中使用。任何新增 persistent research writing 之前，必须先取得 identity、author attribution、audit ownership 以及 all-admin Open Access 影响的 Owner 决策。

## Owner Escalation Boundary

只在以下情况主动升级给 Owner：

1. primary product area 变化；
2. core user path 变化；
3. 新增或实质改变 persistent domain/schema；
4. 改变 research evidence/audit semantics；
5. 明显不可逆或高成本 architecture 投入。

普通 visual、CSS、component、hit-region、test、screenshot 细节使用安全工程默认，并在 review 中展示。

## Independent Review

- 每个 fixed Round 在 automated validation 通过后必须完成 Independent Review 义务；spawned Pi 只是自动化执行方式之一。
- 默认 reviewer 要求：distinct、non-interactive、no-session、strict read-only tools。
- automated child 如果 failed、timed out、aborted 或 produced truncated evidence，且未返回有效 P0/P1/P2，不算完成 Review；该状态是 `automated_review_capability_blocked`，不是产品 candidate P1。
- 本项目默认不要求 OS-level sandbox / bwrap；bwrap/provider-auth/harness 修复属于单独 governance maintenance，不应拖入产品 Round。
- 项目开发过程中不得擅自修改 `.pi/` / harness。发现治理层问题时默认记录为 governance maintenance issue / review limitation；只要不直接阻断产品开发或验收判断，就继续当前产品 Round。只有严重恶性 bug 导致项目无法继续，且 Owner 明确授权后，才允许修改治理层文件。
- Child 不写 artifact；Builder 记录 process/model/output/tool-boundary/Git immutability。
- P0/P1：在同一 Round Fix → Verify → Re-review。
- P2：验收前必须 durable disposition。
- 最后一个 planned Round 还需要单独 Final Integrated Independent Review，且不创建隐藏 Round。
- Capability/auth/isolation failure 标记为 blocked；允许纠正一次明显 Builder packaging error，但不自动修 harness、不重复 reload；默认向 Owner 报告影响并请求 distinct human fallback、继续产品验收并记录 limitation、另开治理维护或调整 review mode，不能静默降级。
- same-session self-check 和 `/new` 都不是 Independent Review。

## Commit And Stop Rules

- 保护 unrelated dirty-worktree changes。
- 不自动 push。
- 未完成 required review、Owner acceptance、authorized acceptance commit 和 post-commit verify 前，不得宣称 accepted-effective。
- Bug/Fix/Review 留在 active Round；scope、acceptance、persistent model、evidence semantics 或 Round map 变化需要 Owner approval。
- 一个 Round accepted-effective 后停止；下一 Round 需要 Owner 明确启动和 Plan-declared handoff。

## R1 收口规则

R1 是 P0–P3 code/domain disposition audit。R1 不再继续修 sandbox、provider auth 或 `.pi/extensions/harness-flow`。

- R1 candidate：`operations/reviews/reboot-p3-code-disposition.md` 与直接相关 R1 work/review evidence。
- R1 context：`AGENTS.md`、canonical Plan、product/research contracts、当前 source/test baseline。
- R1 environment/governance dirty state：`.pi/extensions/harness-flow/index.ts`、starter update、docs references 整理。

R1 后续如需 review，使用明确 scope 的 spawned reviewer 或 Owner-approved distinct human review fallback；不得把 harness implementation 作为 R1 产品审计 candidate。

## Long-term Product Boundary

当前 reboot acceptance 到 read-only Research Workspace 为止。长期产品仍保留：

```text
Explorer → Company → Workspace → Evidence → Review → Conclusion → Report
```

Evidence/Conclusion/Report UI 需要后续单独 Plan，不会从当前编排自动启动。
