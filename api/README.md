# api

FastAPI + SQLite。所有研究对象都从 `data/seeds/cpo/` 导入,数据库文件可随时删掉重建。

```bash
cd api
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m app.seed --rebuild        # 生成 data/sqr.sqlite(--no-sample 跳过示例市场层)
uvicorn app.main:app --reload --port 8000
```

- `GET /api/products/cpo` — 产品全树(模块 → 部件)+ 信号链路
- `GET /api/nodes/{id}` — 任一节点:祖先、子节点、产业链环节、技术、相关公司
- `GET /api/chain` — 产业链环节与代表企业
- `GET /api/companies?chain=…&node=…&q=…` — 公司列表
- `GET /api/companies/{id}` — 单公司

市场层(所有响应带 `as_of`;示例数据时 `sample: true`):

- `GET /api/overview/cpo?days=7` — 首页第一行:结论、计数、每层事件数与篮子 7 天超额
- `GET /api/nodes/{id}/market` — 选中一层:篮子读数、事件与结论、判断(部件继承模块)、公司最近事件
- `GET /api/events?node=&company=&days=` — 卡口事件,含 T+N 反应与时效(窗口内 / 已定价 / 未反应 / 过期)
- `GET /api/events/{id}/resonance` — 一条事件的共振:本公司、同环节、相邻层、资金与关注、历史基线
- `GET /api/baskets` · `GET /api/baskets/{node}` — 环节篮子:序列、事件效力、拥挤度、成分、其他环节
- `GET /api/companies/{id}/market` — 公司页市场部分:价格、指标、拥挤度、事件 30 天、待核验、判断
- `GET/PUT /api/notes/{subject}` · `POST …/questions` · `PATCH …/questions/{i}` · `POST …/extend` — 判断笔记(写 `data/notes/*.md`)
- `GET /api/research/inbox` — 收件箱:要决定的事、事件、未决问题、笔记、整机 rail
- `POST /api/verifications` — 升级 / 忽略 / 审核 / 驳回一条公司↔环节关系
- `GET /api/links/suggest?q=` — `[[` 自动补全

模块:`analytics.py`(纯函数:交易日、反应、时效、拥挤阈值、效力与半衰期)· `market.py`(读)· `insights.py`(结论行的规则与措辞)· `notes.py`(Markdown + front matter)· `research.py`(收件箱与判断跟踪)· `market_seed.py`(示例市场层:合成序列 + 事件冲击,反应由序列计算)。

证据级(`evidence_level`):`reference`(行业公开图示)< `candidate`(候选,待核验)< `reviewed`(已核验)。
