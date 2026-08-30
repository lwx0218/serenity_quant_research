# Project Intake

## Metadata

- Project: serenity_quant_research
- Document type: intake
- Status: active
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: AGENTS.md
- Project slug: serenity-quant-research
- Source-of-truth location: `.`
- Governance mode: external-first, PI-first
- Runtime config root: `.pi/`
- Runtime readiness: runtime-ready
- Product maturity: approved Research Experience Reboot baseline
- Legacy engineering maturity: P0–P3 implemented and reviewed
- Active Round: none; R1–R5 accepted-effective; next Round R6 requires separate Owner start decision
- Legacy P4: paused

## Project Role

Finance-first 产业链研究工作台。首个主题为光模块 / CPO。Serenity 是 host、service/data、permission、audit、migration 和 admin maintenance 基础，不是 research-facing 产品设计系统。

当前 reboot 交付：

```text
CPO Explorer
→ Component / Material / Technology
→ Company Pool / Company Detail
→ Read-only Research Workspace
```

完整长期闭环仍是：

```text
Physical Product / Explorer
→ Component / Material / Technology
→ Company
→ Research Workspace
→ Evidence
→ Review
→ Conclusion
→ Report
```

## Product Areas

1. CPO Explorer：Flat / 3D、shared stable-ID state、callout、contextual drawer。
2. Company Pool：Card/List → Quick Drawer → Expand → entity-centric Full Detail；Comparison deferred。
3. Research Workspace v1：read-only + linked-object-first；Graph、New Note、持久化 writing deferred。

## Canonical Sources

- Governance：root/scoped `AGENTS.md`
- Product：`docs/product/`
- Research evidence：`docs/research-baseline/evidence-contract.md`
- Plan：`operations/planning/research-experience-reboot.md`
- Orchestration：`operations/orchestration/research-experience-reboot.md`

## Stable Engineering Inputs

- P0–P3 source, tests, work logs, and reviews
- `docs/research-baseline/cpo-taxonomy.md`
- `docs/research-baseline/company-universe.md`
- `docs/research-baseline/evidence-contract.md`
- `data/seeds/cpo/`
- `docs/references/cpo-3d-components.jpeg` 和 `docs/references/cpo-industry-chain.jpeg`：仅作为项目本地参考材料

上述 JPEG 不是已核验证据，也不是可自动复用的公共美术素材。Prototype/Gemini 中的 mock claim 不是研究事实。

## Workspace And Open Access Boundary

Workspace v1 adds no ResearchNote, OpenQuestion, Backlink, Graph, or editor persistence. Existing relationships may be projected read-only. Any required persistent schema change returns to the Owner gate.

`OpenAccess:Enabled = true` may remain in the trusted isolated local environment. Before any new persistent research writing, stop and decide user identity, author attribution, audit ownership, and all-admin Open Access effects.

## Portability

- Keep project evidence project-local and use repository-relative paths.
- Do not commit secrets, cookies, credentials, browser profiles, databases, or machine-local overrides.
- Host-local upload references in the historical research summary are non-portable and are not runtime authority.
- `.pi/` remains governance-only; business implementation stays outside it.

## Next Action

No Round is currently active. R1–R5 are accepted-effective; next Round `R6-readonly-research-workspace` remains pending and must not start without a separate Owner start decision. Do not modify production application code, schema, tests, seed, runtime config, research facts, or R6 state in governance-maintenance tasks.
