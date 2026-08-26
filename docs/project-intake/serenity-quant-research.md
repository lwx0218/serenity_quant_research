# Project Intake

This intake template is for projects initialized from the native PI starter. Keep durable project evidence in the project repository by default, and use `Harness_Workspace` as the reusable governance source rather than the daily evidence sink.

## Metadata

- Project: serenity_quant_research
- Project slug: serenity-quant-research
- Source-of-truth location: .
- Governance mode: external-first
- Project root: .
- Main entrypoint: `pi`
- Runtime config root: `.pi/`
- Provider/auth status: active in the current PI session; credentials remain machine-local
- Runtime readiness: runtime-ready

## Project Role

`serenity_quant_research` 是一个基于 `serenity-is/Serenity` 的 finance-first 产业链投研工作台。首个 MVP 以光模块 / CPO 为主题，从可交互的工业分解图进入，将物理部件、技术环节、产业链节点、公司、事件与财务证据、研究结论和报告连接成可审计闭环；产品不包含行情、K 线、账户、交易执行或回测模块，并应能扩展到其他 AI 产业链主题。

## Current Understanding

- Project type: finance-first research workstation built as a Serenity data-centric business application
- Current maturity: requirements baseline frozen; Phase 1 planning; business implementation not started
- Known stable commands: `pi`
- Known stable inputs: `docs/CPO_3D.jpeg`, `docs/CPO_FUll.jpeg`, and `docs/serenity_finance_research_summary.md`
- Known unstable areas: no source SVG/CAD layers; diagram claims and company mappings still require primary-source verification; browser-assisted evidence capture is deferred
- Confirmed first-user flow: interactive CPO part → technology/industry-chain mapping → company exposure → reviewed evidence → versioned conclusion → report

## Portability Notes

- Keep `docs/project-intake/` and `operations/` in this project unless you have an explicit reason to externalize them.
- Avoid hardcoded host-specific absolute paths in committed files.
- Keep secrets and machine-local overrides in untracked local configuration.
- Treat the two CPO JPEG files as project-local seed references, not as verified evidence or reusable public artwork until provenance and usage rights are confirmed.
- The `computer:///workspace/.uploads/...` references in the research summary are non-portable and remain a deferred cleanup item until their source files can be recovered or replaced.

## Next Actions

- Review and execute `operations/planning/phase-1-mvp.md` in its stated order.
- Build and verify the CPO two-level part taxonomy before implementing the interactive diagram.
- Reconstruct the diagram as original, data-bound SVG layers; do not ship the JPEG as an interactive hotspot map.
- Seed and verify the dual-layer company universe: global industry anchors plus A-share-focused research coverage.
- Keep evidence ingestion human-reviewed; evaluate browser tooling only after the manual evidence contract is validated.
