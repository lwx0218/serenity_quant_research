# Research Experience Reboot — R2 独立评审

Round: R2
Review role: per_round
Decision: pass
Unresolved P0: 0
Unresolved P1: 0

## Status

- Round：`R2 — Research Shell`
- Required mode：`spawned_pi_process`
- Final state：**pass with one P2 disposition**
- Artifact author：Builder；review child 未写项目文件。
- Product candidate status：implementation、automated validation、screenshots、Independent Review gate、Owner R2 acceptance 与 acceptance commit authorization 已完成；下一门禁是 commit/post-commit verification。

## Candidate scope reviewed

本次请求评审的 R2 candidate：

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_Layout.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPage.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/ResearchNavigation.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspacePage.cs`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspacePlaceholder.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/wwwroot/Content/site/site.css`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Imports/MVC/MVC.cs`（generated MVC constant）
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh`
- `operations/work_logs/research-experience-reboot-r2.md`
- `operations/reviews/research-experience-reboot-r2-screenshots/*.png`

Context scope 与 dirty-worktree classification 见 `operations/work_logs/research-experience-reboot-r2.md`。`.pi/` / harness 不属于 R2 product candidate。

## Automated validation evidence supplied to reviewer

```text
git diff --check
PASS

cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run build
PASS — esbuild checked 34 output files, none changed

dotnet build SerenityQuantResearch.slnx --no-restore
PASS — 0 warnings, 0 errors

dotnet test SerenityQuantResearch.slnx --no-build
PASS — 54 passed, 0 failed, 0 skipped

cd src/SerenityQuantResearch/SerenityQuantResearch.Web && npm run test:ui
PASS — node UI unit 10 passed; R2 browser shell smoke passed
```

Browser smoke supplied screenshot evidence：

- `operations/reviews/research-experience-reboot-r2-screenshots/root-cpo-shell-1440.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/root-cpo-shell-1920.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/company-pool-shell-1440.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/company-pool-shell-1920.png`
- `operations/reviews/research-experience-reboot-r2-screenshots/secondary-admin-route-1440.png`

## Automated wrapper attempts before successful spawned review

### Attempt 1 — blocked by Builder input error

Builder first invoked `harness_run_independent_review` with screenshot directory as a `scopePaths` entry. The harness rejected the request because `scopePaths` must be regular non-symlink files.

```text
Review decision: blocked
Reason: Path must be a regular non-symlink file: operations/reviews/research-experience-reboot-r2-screenshots
```

Disposition：input packaging error, not product finding. Builder corrected the review bundle to enumerate screenshot files individually.

### Attempt 2 — automated wrapper child capability blocked

Builder invoked `harness_run_independent_review` again with regular files only. The harness returned:

```text
Review decision: blocked
Reason: review child failed, timed out, was aborted, or produced truncated evidence
```

Disposition：`automated_review_capability_blocked` / review limitation, not R2 product candidate P0/P1/P2。

### Attempt 3 — blocked by Plan mode metadata pollution

After an Owner-requested retry, harness returned:

```text
Review decision: blocked
Reason: Independent Review mode must be spawned_pi_process or human_review
```

Disposition：治理元数据错误。Plan 的 `Independent Review mode` 字段曾被扩写为解释性正文，已恢复为精确 `spawned_pi_process`，fallback 说明移至独立字段。该问题记录为 `GOV-003`。

### Attempt 4 — metadata fixed, automated wrapper still blocked

修复 metadata 后再次调用 `harness_run_independent_review`，mode gate 已通过，但 wrapper 仍返回：

```text
Review decision: blocked
Reason: review child failed, timed out, was aborted, or produced truncated evidence
```

Disposition：确认问题在 automated wrapper / child execution capability 层，不是 R2 product candidate failure。记录为 `GOV-002`。

## Successful Independent Review — manual spawned Pi process

Owner 要求本 session 必须解决 Independent Review 且不使用 human review 或 `/new`。Builder 因此启动一个 distinct manual spawned Pi process，在临时 copied review root 中执行 R2 review。该路径不依赖 blocked harness wrapper，但满足 `spawned_pi_process` 的核心要求：独立进程、no-session、non-interactive、strict read-only tools、reviewer 不写 artifact。

### Process / boundary evidence

| 项目 | 结果 |
|---|---|
| Builder session | `governance-standards-reset` / current Builder |
| Reviewer PID | `3579826` |
| Distinct process | yes |
| Invocation | `pi --no-session --no-approve --no-extensions --no-skills --no-prompt-templates --no-themes --no-context-files --tools read,grep,find,ls --provider openai-codex --model gpt-5.6-sol -p <R2 review prompt>` |
| Working root | temporary copied review root `/tmp/sqr-r2-manual-spawn-review-CF1PLR` |
| Tool boundary | `read,grep,find,ls` only；no shell/write tools |
| Project resources | extensions / skills / prompt templates / themes / context files disabled |
| Session boundary | `--no-session`；不是 `/new`，不是 same-session self-check |
| Exit | `0` |
| stderr | empty |
| Structured marker | `HARNESS_REVIEW_RESULT` present and parsed |

### Reviewer output

```text
结论：pass。未发现 P0/P1；R2 的 root entry、三项 research nav、独立 shell、admin route 分离及只读 Workspace placeholder 均符合合同。

唯一 P2：截图脚本只等待应用容器挂载，未等待异步内容加载完成，导致部分验收截图仍处于加载状态；不影响本轮 shell 验收，但应增强截图稳定性。
```

Structured result：

```json
{"decision":"pass","findings":[{"severity":"P2","summary":"截图捕获未等待异步研究内容加载完成","evidence":"tests-ui/run-browser-smoke.sh 在检测到 #cpo-research-app 或 #company-research-app 后立即截图；root-cpo-shell-1920.png 和 company-pool-shell-1440.png 仍显示加载状态及空内容区域。"}],"limitations":["只读审查，未执行命令或重新运行构建/测试；验证结果及 protected-surface 状态依据 review bundle、工作日志和提供的截图。"]}
```

## Findings

- P0：0
- P1：0
- P2：1

### P2 — 截图捕获未等待异步研究内容加载完成

- Evidence：`tests-ui/run-browser-smoke.sh` 在检测到 `#cpo-research-app` 或 `#company-research-app` 后立即截图；`root-cpo-shell-1920.png` 和 `company-pool-shell-1440.png` 仍显示加载状态及空内容区域。
- Builder disposition：**accepted / non-blocking**。R2 的验收重点是 shell、root entry、primary nav、admin separation 和 Workspace placeholder。Browser smoke 已通过 DOM assertions 证明 nav labels/hrefs、sidebar absence、admin route/service reachability 与 placeholder no-writing boundary；截图中的异步内容加载状态不改变 R2 shell objective。该项作为 screenshot stability/test-evidence hardening backlog，不阻塞 R2 Owner acceptance。若 Owner 要求更强视觉证据，可在 R2 acceptance 前或后续维护中让 screenshot capture 等待内容加载稳定并重新生成截图。

## Git / candidate immutability evidence

Review-block recording HEAD：

```text
28ec224ac6070245f51b22f02aff18b815f3d745
```

Selected candidate SHA-256 hashes after successful manual spawned review match the previously recorded hashes：

```text
3014a46bc8864087693d87f71ef0a43035d95a155343fce2645620db29321b6f  src/SerenityQuantResearch/SerenityQuantResearch.Web/Views/Shared/_Layout.cshtml
7cea5cf09b7bfa64bc7babf0ae66634335e1eacf45dc275e6ac410a852921297  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Common/Dashboard/DashboardPage.cs
a951e17b36df7ce399235d529858ad2f5a982da43ac77d653edd7b4def89b87d  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/ResearchNavigation.cs
74d1eae23eb72a9f44bbe2c29de00128512e174f8d385ed90ef610a12e10f7e2  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspacePage.cs
52320fdc24070f2fc4612b27ed0644449d46416b5f2e67d0f8a23eb70b9a63b6  src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Workspace/ResearchWorkspacePlaceholder.cshtml
d2e4dcf9d6b208eed0a2570dbddd651679edcd611721ba15c3d5cc8360666c76  src/SerenityQuantResearch/SerenityQuantResearch.Web/wwwroot/Content/site/site.css
cde8a15b40f240279cee2e9b07287524a338151977365fec844eeab93af9e35f  src/SerenityQuantResearch/SerenityQuantResearch.Web/Imports/MVC/MVC.cs
4bc2f150095cc771188d604210e791c790b8c4c227921d9ac872c00941c4b413  src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh
bb41246d41363383fab385b440e966898aac1c92a311864eb6256e8c23fef39b  operations/reviews/research-experience-reboot-r2-screenshots/company-pool-shell-1440.png
883239769070d8ae80e02937266db1b747681155d5c516a1f6219d85310b286c  operations/reviews/research-experience-reboot-r2-screenshots/company-pool-shell-1920.png
8a7c07efa5f40bfc6cd6d3a742180f84a1b3f458b60f1685347a432be8235127  operations/reviews/research-experience-reboot-r2-screenshots/root-cpo-shell-1440.png
57387fb4e426441ebf91944cbb587d5d944e646a506b1afaaa05e83dee0a21c6  operations/reviews/research-experience-reboot-r2-screenshots/root-cpo-shell-1920.png
6491a7f4838d553fc74df7d0af488024d6df439e8ab54173d2436e55539bd441  operations/reviews/research-experience-reboot-r2-screenshots/secondary-admin-route-1440.png
```

The reviewer process operated only on a copied temporary review root and had no write/shell tools. It did not modify project files.

## Decision

**pass**

R2 Independent Review obligation is satisfied via distinct manual spawned Pi process. No P0/P1 remains. One P2 has been dispositioned as non-blocking screenshot stability hardening.

## Owner acceptance and required next gate

Owner accepted R2 on `2026-08-28T15:34:02Z` by replying `accept`.

Owner authorized acceptance commit on `2026-08-28` by replying “可以，验收吧，commit吧”.

R2 is still not accepted-effective until commit and post-commit verification complete. R3 must not start automatically.
