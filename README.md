# Serenity Quant Research

以**实物部件**为入口的产业链投研工作台。第一个主题:光模块 / CPO。

```text
实物产品(CPO 光模块)
  → 九层结构,点一层
    → 它由什么构成(子部件)· 属于产业链哪一环 · 谁在做(公司)
      → 公司页:证据级与来源
```

长期目标是从机柜(如 GPU / 交换机整机)一层层拆到光模块、再到部件;
Explorer 是同一种视图的递归,加新产品是加数据,不是加页面。

## 分支状态

`reboot-v2`(2026-09):从 .NET / Serenity 推倒重来。旧实现与流程记录见 `docs/archive/`,git 历史完整保留。

本轮范围:Shell(含深浅色切换)+ Explorer(总览 / 选中一层 / 下钻到部件)+ 极简公司页。
研究笔记(Obsidian 式的可写 Workspace)尚未开始,需要先决定作者身份与写入模型。

## 技术栈

| 层 | 选择 | 位置 |
|---|---|---|
| 前端 | Vite + React 19 + TypeScript,纯 CSS 变量,无 UI 框架 | `web/` |
| 后端 | FastAPI + SQLite(标准库 `sqlite3`) | `api/` |
| 数据 | JSON seed → SQLite,随时可重建 | `data/seeds/cpo/` |
| 字体 | Geist / Geist Mono 自托管(OFL);中文用系统字体 | `web/public/fonts/` |

## 运行

后端(端口 8000):

```bash
cd api
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000              # 首次启动自动从 seed 建库
```

前端(端口 5173,`/api` 自动代理到 8000):

```bash
cd web
npm install
npm run dev
```

打开 http://localhost:5173 。

测试与构建:

```bash
cd api && python -m unittest -q          # 或 pytest
cd web && npm run build                  # tsc + vite build → web/dist
```

`web/dist` 存在时,`uvicorn app.main:app` 会直接同时提供前端与 API(单进程部署)。
重建数据库:`cd api && python -m app.seed --rebuild`。

## 目录

```text
api/      FastAPI 应用:app/{main,db,seed,repo,schemas,routers/}、tests/
web/      Vite 应用:src/{pages,components,lib,styles}
data/     seeds/cpo/*.json(研究事实 · 展示文案 · 参考企业)
docs/
  product/            design-rules.md(当前有效的设计规则)+ 旧 spec(标注 superseded)
  research-baseline/  CPO taxonomy、公司候选池、证据合同
  references/         两张参考图示(图财社)
  archive/            旧 operations 记录与模板(只读)
```

## 数据与证据边界

- 研究事实、稳定 ID 与分类来自 `cpo-research-seed.json`,不因界面需要而改动。
- 界面怎么讲(显示名、一句话、分层图视觉类型、信号链路)在 `cpo-presentation.json`。
- 公司与产业链环节的对应关系带**证据级**:`reference`(行业公开图示)< `candidate`(有来源、待核验)< `reviewed`(已核验)。
  详见 `docs/research-baseline/evidence-contract.md` 与 `api/README.md`。
- 图示中的份额、BOM%、国产化率等数字不进入产品。

## 设计

规则只有一页:`docs/product/design-rules.md`。数值以 `web/src/styles/tokens.css` 为准。
