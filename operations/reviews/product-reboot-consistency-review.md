# Product Reboot — Package-supplied Consistency Review

> Provenance：本记录来自 `docs/serenity-product-reboot-package.zip` 导入前的 package 内容。它是 package consistency input，不是 repository fixed-Round Independent Review，也不是 R1–R7 acceptance evidence。

## Package Decision

- Package author recorded result：**approved**
- Scope：product docs、prototypes、reboot plan、orchestration、repository-entry reset drafts
- Production application code：package 未 review 或修改

## 检查项

- [x] **No Codex references**：implementation agent 术语统一为 Pi。
- [x] **P4 paused / historical only**：reboot 文档不授权 legacy P4。
- [x] **Company Pool hierarchy defined**：canonical product docs 中存在三层 company research flow。
- [x] **Research Workspace knowledge-centric**：Workspace 与 entity-centric Company Detail 分离。
- [x] **Prototype data safety gate**：design mock data 明确禁止成为 research facts。
- [x] **Serenity UI authority limited**：framework 是 infrastructure，不是 research-facing product authority。
- [x] **Legacy plan tombstoned**：旧 Plan 不再授权 P4/P5/P6。
- [x] **Web-local AGENTS exists**：research-facing frontend 有 scoped guardrails。
- [x] **Gemini prototype design-only**：Gemini visual ideas 可作为设计参考，但不导入 unsourced research claims。

## 已解决跨文档决策

1. Primary research areas 为 `CPO Explorer`、`Company Pool`、`Research Workspace`。
2. `Company Detail` 不是 primary nav item；路径是 `Company Pool → Quick Drawer → Expand`。
3. Research Workspace 是独立 knowledge-centric product area，不是更大的 Company Detail。
4. Explorer prototype v0.4 是 interaction baseline；Gemini prototype 仅是 visual / UX design reference。
5. P0–P3 engineering work 继续作为历史/可复用工程证据；research-facing P2/P3 presentation 已 supersede。
6. Legacy P4 paused。下一 Pi action 被 canonical Plan 规范化为 `R1 — P0–P3 Code Disposition And Domain Audit`。

## Bootstrap Handling

`operations/planning/serenity-bootstrap.md` 保持技术 bootstrap 记录。Research Experience Reboot 后，它不再定义 research-facing IA、navigation、interaction、page composition 或 visual design。

## Legacy Plan Handling

`operations/planning/phase-1-mvp.md` 是短的 superseded pointer。`operations/archive/phase-1-mvp-p0-p3.md` 保存历史过渡。旧 long-form plan 可通过 archive 与 Git 历史恢复。

## 当前边界

当前权威是 `operations/planning/research-experience-reboot.md` 与 `operations/orchestration/independent-review-and-round-scope-standard.md`。R1 停在 disposition audit、scope-bounded review/fallback 与 Product Owner gate，不自动进入 R2。
