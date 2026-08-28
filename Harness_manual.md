# serenity_quant_research Harness Manual

这份文件是 `serenity_quant_research` 项目根的人类操作手册。它随项目一起移动，不依赖 `Harness_Workspace` 的 `operations/` 或宿主机路径。

## Read This Project In This Order

1. `README.md`：项目/starter 概览
2. `Harness_manual.md`：人类下一步操作
3. `AGENTS.md`：Pi 和其他模型必须遵守的项目合同
4. `.pi/`：project-local skills、prompts 和 settings
5. `docs/project-intake/`、`operations/`：项目本地 durable evidence

如果人类说明与 `AGENTS.md` 冲突，以 `AGENTS.md` 为模型执行合同。

## What Was Initialized

bootstrap 已为本项目提供：

- `Harness_manual.md`
- `README.md`
- `AGENTS.md`
- `.pi/`
- `docs/project-intake/<project-slug>.md`
- `operations/planning/`
- `operations/work_logs/`
- `operations/reviews/`

这些目录属于当前项目。日常 Plan、work log 和 review 默认保存在这里，而不是外部 Workspace。

## Bootstrap-Ready Versus Runtime-Ready

- `bootstrap-ready`
  - 上述 scaffold、manual、intake 和 evidence 路径已存在
- `runtime-ready`
  - 除 bootstrap-ready 外，本机还可执行 `pi`，并已完成 provider/auth

bootstrap 不安装 Pi，也不配置 API key 或 OAuth。若运行前置条件未满足，先安装 Pi，并在需要时通过 `/login` 配置 provider；不要把 `bootstrap-ready` 当作模型调用已就绪。

## Start The First Session

从当前项目根按顺序执行：

```text
1. cd <project>
2. read Harness_manual.md
3. pi --name "00-orchestration"
4. enter the project request and complete kickoff before implementation
```

首次使用 project-local resources 时，先检查项目内容；Pi 如提示 trust，可按需 `/trust` 后重启。进入后运行 `/project-kickoff <project request>`。

session 名称用于识别和恢复，不会自动创建权限边界或 plan mode。实际 kickoff boundary 来自 `AGENTS.md` 与 `/project-kickoff`；Pi 没有内建 sandbox，人类仍需观察控制门。

## What `00-orchestration` Does

对于 greenfield 项目或没有 approved baseline Plan 的项目，把 `00-orchestration` 保持为 planning-only kickoff。

它应当：

- 读取 `README.md`、`AGENTS.md`、intake 和已有 evidence
- 澄清 goal、scope、constraints、acceptance、assumptions 和 risks
- 在聊天中展示 Plan Preview
- 说明 durable Plan 路径和下一个 control gate

在人类确认 Plan 前，只允许 read/infer/discuss 和 chat Plan Preview；不得执行任何 project write，包括：

- 修改业务代码、配置或其他既有文件
- 创建/更新 formal Plan、intake 或任意 durable evidence
- 创建/更新 `CONTEXT.md`、`CONTEXT-MAP.md` 或 ADR
- 创建 work log、review、其他 project artifact 或 acceptance commit
- 安装依赖或执行破坏性/system-level 操作
- 开始 implementation 或宣称开发进度

默认 discovery budget 是最多 3 rounds、每轮 3–5 个 related blocking decisions、目标总上限 12–15；每个 decision 给 recommended default。Owner 可回复 `accept recommended defaults`。预算耗尽仍有 blocker 时，必须显式选择是否进入 `deep-discovery`。

每轮检查 Resolved、Assumed、Blocking、Deferred、Question budget remaining。只有 domain language/state/ownership/context ambiguity material 时才启用 `domain-modeling`；approval 前不写 `CONTEXT.md` 或 ADR。

这是人类控制门；`00-orchestration` 这个名字本身不提供技术强制。

已有 approved baseline 后，后续清晰的小任务仍可使用 `Gate -> Route` simple path，不需要强制 fixed rounds。

## Confirm The Plan

Pi 给出完整 Plan Preview 后，必须主动询问：

```text
以上 Plan 是否可行？是否还有需要继续确认或修改的地方？

- 如需修改：直接说明修改点
- 如无其他问题：回复“确认计划”
- 确认后我将持久化 Plan，并生成下一开发 session 的名称和交接内容
```

人类至少检查：

- Goal、in-scope、out-of-scope
- source of truth 和预期修改文件
- acceptance criteria 和验证方法
- assumptions、risks、backlog
- 是否需要 fixed rounds 或 Independent Review
- fixed Round 是否按 `AGENTS.md` 的完整 canonical field set 逐 Round 声明 Round/session/delivery/validation/review/acceptance/stop contract，并为最后 Round 声明 integrated Review gate

`accept recommended defaults` 只解决 discovery decisions，不等于批准 durable Plan。优先让 Pi 调用 `harness_request_plan_approval`。Owner UI 返回 `approved`、`changes_requested` 或 `cancelled`，且请求本身不写 project files；只有 `approved` 授权持久化。extension unavailable 时，人类回复 `确认计划` 或其他同等明确批准是 manual fallback。若关键 scope、architecture 或 acceptance 仍未解决，不要确认。

## Create The Implementation Session

Plan 已确认并持久化后，优先让 Pi 调用 `harness_offer_session_handoff`。它验证 approved Plan、Round 与 declared name，展示 proposed session/target/summary，并请求一次确认；confirm 后创建 parent-linked session、命名并提交 prompt 一次。cancel/capability failure 保持当前 session 并提供 fallback。

manual fallback：先使用 `/session-handoff <declared-session-name>` 生成 handoff，再在 Pi 中执行：

```text
/session
/new
/name <declared-session-name>
```

固定 Round 使用 Plan 为该 Round 声明的 primary implementation session name，例如 `R1-<delivery-slug>`。同一 Round 需要 continuation 时使用 `R1-<delivery-slug>-cont-2`；Round ID、delivery boundary、Review lifecycle 和 acceptance gate 不变。普通非固定任务使用：

```text
/name build-<task-slug>
```

把 `AGENTS.md`、approved Plan、最新 work log/review、当前 bounded target、验证命令和下一 control gate 放入新 session handoff。聊天记录不是 durable source of truth。automatic 和 manual path 都遵守同一字段；local `harness-flow` 不是公开 package。

## Request Or Observe Review

普通 simple task 不强制 formal review。若 approved Plan 启用 fixed rounds，每个 Round 都要求 Independent Review，并由当前 Builder 在 automated verification 后自动发起：

- 调用 `harness_run_independent_review`，由它 capability-check 并启动 distinct、non-interactive、`--no-session`、strict `read,grep,find,ls` child；或
- 使用经批准且与 Builder 不同的 `human_review`

`/new` 本身不是 Independent Review。child 不写 candidate 或 durable artifact；Builder 应记录 P0/P1/P2 findings、decision、invocation/PID/provider/model、exit/stdout/stderr、effective tool boundary 和前后 Git status/hash。

P0/P1 在原 Round 自动修复、复验并重新 Review；P2 必须记录 disposition。所有 planned delivery 完成后，最后 Round 在 pre-commit gate 前还要通过单独的 Final Integrated Independent Review；它不创建隐藏 Round。查看 `operations/reviews/` 了解当前 decisions。

## Inspect Evidence, Session, And Git

在项目根：

```bash
find docs/project-intake operations -maxdepth 2 -type f -print
git status --short --branch
git log -1 --oneline
```

在 Pi 中：

```text
/session
/resume
```

证据位置：

- intake：`docs/project-intake/<project-slug>.md`
- Plan：`operations/planning/`
- work log：`operations/work_logs/`
- review：`operations/reviews/`
- session file / ID：`/session`
- commit / worktree：`git log`、`git status`

## Human Control Gates

以下情况必须停下来由人决定或授权：

1. provider/auth 或 project trust 未就绪
2. Plan 尚未确认
3. Goal、scope、acceptance 或 round map 要改变
4. destructive/system-level action 或外部授权
5. Review 仍有 P0/P1
6. acceptance commit、push 或发布

Harness 不自动 push。若项目采用 fixed rounds，只有每 Round Review（以及最后 Round 的 Final Integrated Independent Review）、pre-commit gate、accepted-candidate evidence、acceptance commit 和 post-commit verify 都通过后，才能称为 accepted effective。

## Portability Rules

- 使用项目相对路径或 `<placeholder>`
- secrets 和机器本地 override 不提交
- 项目 evidence 保持 project-local
- 不依赖外部 Workspace 的 historical operations records
- 不把大体积 runtime residue 当作 durable evidence
