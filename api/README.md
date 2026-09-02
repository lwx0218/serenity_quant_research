# api

FastAPI + SQLite。所有研究对象都从 `data/seeds/cpo/` 导入,数据库文件可随时删掉重建。

```bash
cd api
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m app.seed --rebuild        # 生成 data/sqr.sqlite
uvicorn app.main:app --reload --port 8000
```

- `GET /api/products/cpo` — 产品全树(模块 → 部件)+ 信号链路
- `GET /api/nodes/{id}` — 任一节点:祖先、子节点、产业链环节、技术、相关公司
- `GET /api/chain` — 产业链环节与代表企业
- `GET /api/companies?chain=…&node=…&q=…` — 公司列表
- `GET /api/companies/{id}` — 单公司

证据级(`evidence_level`):`reference`(行业公开图示)< `candidate`(候选,待核验)< `reviewed`(已核验)。
