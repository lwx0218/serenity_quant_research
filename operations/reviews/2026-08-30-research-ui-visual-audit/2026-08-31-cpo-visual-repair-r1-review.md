# CPO Visual Repair R1

## Metadata

- Project: serenity_quant_research
- Task: CPO Explorer-only visual repair R1
- Timestamp (UTC): 2026-08-31T08:06:26Z
- Owner: project owner
- Route: direct-execute
- Source of truth: operations/reviews/2026-08-30-research-ui-visual-audit/2026-08-30-research-ui-visual-audit-review.md

## Scope

本次只处理 CPO Explorer 的最高优先级视觉止血项：V-001～V-005。不启动 fixed Round，不修改 research facts、seed、schema、migration、primary navigation、Workspace writing 或 Company/Workspace 页面。

## Changed Files

- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramIndex.cshtml`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/Modules/Research/Diagram/CpoDiagramPage.css`
- `src/SerenityQuantResearch/SerenityQuantResearch.Web/tests-ui/run-browser-smoke.sh`
- `operations/reviews/2026-08-30-research-ui-visual-audit/repair-r1-cpo-screenshots/**`

## Repair Summary

- V-001：移除 CPO workbench 的 1640px 增长平台；CPO app 在 research shell 中按 viewport 宽度扩展，stage 高度改为 `clamp(620px, 48vw, 980px)`，并将 SVG viewBox 扩展到 `1240×720` 以容纳 annotation gutters。
- V-002：将 Flat/3D 右侧 callout 统一移入右 annotation gutter（card 起点 `x=950`），主几何保持在中间 safe area；connector line 可跨区但 card 不再压住主要组件。
- V-003：research drawer 从 full-height fixed overlay 改为 CPO app grid 的第二列 sticky dossier；打开后主图按剩余列宽重排/居中，不再固定 `scale(.94)`，也不覆盖 topbar。
- V-004：移除 `.cpo-callout:focus-visible` 作用于 SVG `<g>` 的大 outline；键盘 focus 改落在 callout card stroke/shadow，component focus 使用真实几何 stroke。
- V-005：selected/hover de-emphasis 降低为轻量 opacity/saturation 差异，context assembly 保持可读，不再强 blur 到空间关系消失。

## Screenshot Evidence

- Directory: `operations/reviews/2026-08-30-research-ui-visual-audit/repair-r1-cpo-screenshots/`
- Contact sheet: `operations/reviews/2026-08-30-research-ui-visual-audit/repair-r1-cpo-screenshots/contact-sheet-cpo-repair-r1.png`
- States covered at `1440×980`、`1920×1080`、`2504×1178`:
  - idle flat / hover flat / callout focus flat / selected flat
  - view-switch selected state
  - idle 3D / hover 3D / selected 3D
  - blank reset

## Verification

Commands run from repository root unless noted:

```bash
cd src/SerenityQuantResearch/SerenityQuantResearch.Web
npm run build
npm run test:ui:unit
UI_SCREENSHOT_DIR=/project/data_science/serenity_quant_research/operations/reviews/2026-08-30-research-ui-visual-audit/repair-r1-cpo-screenshots npm run test:ui:browser:r4
cd /project/data_science/serenity_quant_research
git diff --check
python3 scripts/check-document-governance.py --check
```

Results:

- `npm run build`: pass
- `npm run test:ui:unit`: pass, 19 tests
- `npm run test:ui:browser:r4`: pass, 27 CPO screenshots plus contact sheet generated
- `git diff --check`: pass
- `scripts/check-document-governance.py --check`: pass

## Remaining / Deferred

- 本轮没有处理 V-006～V-010（Company Pool、Quick Drawer、Company Detail、Workspace、跨页面视觉系统）。
- 本轮没有做 React/Vite 迁移或 shared drawer primitives；只做 CPO-only CSS/SVG layout repair。
- 仍需人工 product visual review 截图，不能据此声明全项目视觉完成。
