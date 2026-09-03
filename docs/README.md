# 文档目录

## Metadata

- Project: serenity_quant_research(产品名 Teardown)
- Document type: index
- Status: active
- Owner: project owner
- Last updated: 2026-09-03
- Source of truth: AGENTS.md

| 路径 | 用途 | 状态 |
|---|---|---|
| `product/design-rules.md` | 研究界面的全部视觉与文案规则(一页) | **当前有效** |
| `product/*.md`(其余) | .NET 时期的产品规格与体验地图 | superseded,思路可参考,条款不再约束 |
| `product/prototypes/teardown-v3/` | Teardown 方向稿 v3 的静态导出与生成脚本(六页 × 浅深) | **当前有效**,实现以它为准 |
| `product/prototypes/*.html`(其余) | .NET 时期的 HTML 原型 | 历史参考 |
| `research-baseline/` | CPO taxonomy、公司候选池、证据合同 | 当前有效(证据级见 evidence-contract §2a) |
| `references/` | 两张公开产业链图示(图财社) | 长期参考输入;它们是 `reference` 级证据的来源 |
| `project-intake/` | 项目入口与边界 | 部分过期,待随 v2 更新 |
| `archive/` | 旧 operations 记录与模板 | 只读历史 |

## 阅读顺序

做界面:`README.md`(根)→ `product/design-rules.md` → `web/src/styles/tokens.css` → 对应页面代码。
做数据 / 研究事实:`research-baseline/evidence-contract.md` → `data/seeds/cpo/*.json` → `api/app/seed.py`。
做市场层 / 量化:`product/design-rules.md` §5–§7(方向色、结论先行、时间语义)→ `api/app/analytics.py` → `api/app/insights.py`。
判断笔记:`data/notes/*.md`(front matter 字段见 `api/app/notes.py` 顶部)。

## 约定

- 面向 Owner 的总结与文档正文默认中文;代码标识、命令、协议字段保留英文。
- 不在 `docs/` 顶层堆放临时文件、运行产物或一次性交接材料。
- 移动文档时同步更新引用;`archive/` 内容保持原样。
