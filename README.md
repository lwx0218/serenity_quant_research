# Teardown / 拆解 · from part to position

以**实物部件**为入口、落到**资金怎么投票**的产业链量化投研工作台。第一个主题:光模块 / CPO。
(仓库名沿用 serenity_quant_research;产品名 Teardown。)

```text
实物产品(CPO 光模块)· 首页第一行:资金本周在给哪一层投票
  → 九个模块,点一个
    → 我的判断(可证伪,Markdown)· 最近卡口事件与反应 · 子部件 · 谁在做(公司 + 最近事件)
      → 公司页:价格与事件 · 拥挤度 · 事件 30 天 · 共振 · 判断 · 证据级与来源
      → 环节篮子:环节相对整机 · 事件效力(时效)· 拥挤度 · 成分
  研究(收件箱):今天要决定什么 · 本周事件 · 未决问题 · 最近笔记
```

三层内容,分别回答三个问题:

| 层 | 回答 | 在哪 |
|---|---|---|
| 事件 | 发生了什么、资金买没买(T+1 / T+5 相对篮子)、还能管多久(时效) | 每层、每家公司、收件箱 |
| 判断 | 我怎么看、什么能证伪它、到期怎么回顾 | `data/notes/*.md`(Obsidian 可开) |
| 量化 v1 | 环节篮子相对整机、事件效力(命中率、半衰期 → 有效期)、拥挤度 / 脆弱性(状态量) | 篮子页、公司页 |

这是第一层(产业层)。宏观、筹码与资金博弈是之后的层。

长期目标是从机柜(如 GPU / 交换机整机)一层层拆到光模块、再到部件;
Explorer 是同一种视图的递归,加新产品是加数据,不是加页面。

## 分支状态

`reboot-v2`(2026-09):从 .NET / Serenity 推倒重来。旧实现与流程记录见 `docs/archive/`,git 历史完整保留。

已完成:六页(整机 / 选中一层 / 编辑判断 / 公司 / 研究收件箱 / 环节篮子),浅深两色,红涨绿跌可切换。
**当前市场层是样式示例**(`data/seeds/cpo/cpo-sample-market.json`,每条记录 `is_sample=1`,页脚标「示例」):事件、行情序列、拥挤度读数都是编的,反应与效力是从这些序列**算**出来的,规则与真实数据接入后一致。
下一轮:数据源适配器(巨潮公告 / 互动易 / 新闻 RSS / 免费行情),写入同一组表;`python -m app.seed --rebuild --no-sample` 建一个不含示例的库。

## 技术栈

| 层 | 选择 | 位置 |
|---|---|---|
| 前端 | Vite + React 19 + TypeScript,纯 CSS 变量,无 UI 框架 | `web/` |
| 后端 | FastAPI + SQLite(标准库 `sqlite3`) | `api/` |
| 数据 | JSON seed → SQLite,随时可重建 | `data/seeds/cpo/` |
| 判断笔记 | Markdown + 小 front matter,API 读写,Obsidian 直接打开 | `data/notes/` |
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
重建数据库:`cd api && python -m app.seed --rebuild`(加 `--no-sample` 不导入示例市场层)。

## 目录

```text
api/      FastAPI 应用:app/{main,db,seed,market_seed,repo,market,analytics,insights,notes,research,routers/}、tests/
web/      Vite 应用:src/{pages,components,lib,styles}
data/     seeds/cpo/*.json(研究事实 · 展示文案 · 参考企业 · 示例市场层)· notes/*.md(判断)
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
- 分层是**研究分层,不是物理拆解**:九个模块来自公开图示命名、经 OIF 术语核验(`docs/research-baseline/cpo-taxonomy.md`);光接收多集成在 PIC 内,光源可外置,主板属系统边界。做到交换机 / 机柜一级再换物理保真视图。
- 时间语义:每个读数带 `截至 + 窗口`。事件反应 = T+1/T+3/T+5/T+20 相对篮子;事件时效默认 T+5,由该层「事件效力」的半衰期校准;拥挤度是状态量(20 日,每日重算),不是信号;判断有自己的窗口,到期进收件箱回顾。交易日按工作日近似,尚未接交易所日历。

## 设计

规则只有一页:`docs/product/design-rules.md`。数值以 `web/src/styles/tokens.css` 为准。
