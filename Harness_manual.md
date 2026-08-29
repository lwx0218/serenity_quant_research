# serenity_quant_research Harness Manual

这份文件是项目本地的人类操作入口。模型执行合同以 `AGENTS.md` 为准。

## 默认路径

1. 读 `README.md`、`Harness_manual.md` 和 `AGENTS.md`。
2. 从项目根启动 Pi。
3. 对清楚的小任务直接走 native Pi simple path。
4. 只有目标、范围、风险、验证或交接需要时，才要求轻量 Plan。
5. 只有 Owner 明确批准时，才启用 fixed Round、Independent Review、handoff 或 formal gate。

## 新项目第一次 session

```bash
pi --name "00-orchestration"
```

在 Owner 明确批准 Plan 前，保持 no-write：只读取、推断、讨论和展示 Plan Preview；不改业务文件、不写 durable evidence、不安装依赖、不执行破坏性操作。

Plan Preview 必须让 Owner 能检查 goal、scope、non-goals、assumptions、risks、validation 和是否需要 formal mode。接受 recommended defaults 不等于批准 Plan。

## 已有 baseline 后

后续清楚 bounded task 默认直接执行并验证。不要因为仓库里有 `.pi/`、历史 Plan、旧 review 或 operations 目录，就自动创建 Round 或 formal review。

## Evidence

项目 evidence 默认保存在：

- `docs/project-intake/`
- `operations/planning/`
- `operations/work_logs/`
- `operations/reviews/`

普通 simple task 不强制写 evidence。需要记录时写最小、可复验内容。

## Update Governance Surface

从 `Harness_Workspace` 根可执行：

```bash
./update.sh <target-dir> --check
./update.sh <target-dir> --apply
```

updater 会显示 manifest 和备份路径；它只管理 Harness 分区与 `.pi` capability surface，必须保留项目 owned 内容，不会自动 commit 或 push。

## Safety

遇到破坏性操作、外部授权、scope/acceptance 改变、无法验证或 managed/project 分区不清时停下来让 Owner 决策。Harness 不自动 push。
