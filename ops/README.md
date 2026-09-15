# 服务器上跑起来（数据接入版）

目标：页面上每个数字都有来路。行情 / 融资 / 股东户数 / 估值走免费接口（东财、Yahoo、stooq，
都是 akshare / yfinance 底下那几个 HTTP 接口，这里用标准库直接调，不装第三方包），事件走
巨潮公告 / 互动易 / RSS 进候选池，人在收件箱确认。接口取不到的，自动记成待办，让 AI（PI + web-access）
去网页端取，再 POST 回来。

## 第一次

```bash
git checkout physical-first && git pull
cd web && npm install && npm run build && cd ..          # 前端
cd api && pip install -e ".[dev]"                         # fastapi / uvicorn（原来就有；接入层不加新依赖）
python -m app.seed --rebuild --no-sample                  # 建库；--no-sample 不装样式示例的市场层
python -m app.ingest probe                                # 每条路各试一家：东财 K 线 / 融资 / 股东户数 / 估值、Yahoo、stooq、RSS
python -m app.ingest daily --full                         # 首次全量：两年多日线 → 融资 / 股东户数 → 估值 → 重算 series / 反应 / 拥挤度
python -m app.ingest news                                 # 候选池
uvicorn app.main:app --host 0.0.0.0 --port 8000           # web/dist 存在时同时提供前端
```

`probe` 里 ERR 的那条路会在 `daily` 时自动退到下一条（A 股：东财 → Yahoo；海外：Yahoo → stooq）；
三条都不通的公司进 `GET /api/ingest/todo`。RSS 地址没在本机验证过：`--probe` 打不开的，改 `data/sources/news_sources.json` 或删。

以后改了 seed / physical JSON 再 `python -m app.seed --rebuild --no-sample`：抓过的 bars / 候选 / 运行记录会原样保留并自动重算，不用重抓。

## 定时（cron，服务器时区 Asia/Shanghai）

```cron
# A 股 15:00 收盘，东财 K 线 15:30 后稳定；美股在次日早上补进来
35 15 * * 1-5  cd /path/to/serenity_quant_research/api && python -m app.ingest daily  >> /var/log/teardown-ingest.log 2>&1
# 公告 / 互动易 / 新闻：每 3 小时一次候选池
15 */3 * * *   cd /path/to/serenity_quant_research/api && python -m app.ingest news   >> /var/log/teardown-ingest.log 2>&1
```

也可以不进服务器，直接打接口（后台线程跑，立即返回）：

```bash
curl -X POST http://localhost:8000/api/ingest/run/daily
curl -X POST http://localhost:8000/api/ingest/run/news
curl http://localhost:8000/api/ingest/runs          # 每次的计数 / 错误
curl http://localhost:8000/api/ingest/status        # 行情截至、多少家有行情、候选池、待办
```

`daily` 只增量拉（从上次最后一天往前 10 天覆盖），几分钟跑完；`quotes --full` 才重拉全量。

## 让 AI 补接口拿不到的

`GET /api/ingest/todo` 每条带 `hint`（去哪个网页取什么、按什么格式交回）。给 PI 的任务写法：

> 读 http://localhost:8000/api/ingest/todo，逐条按 hint 用浏览器去取，整理成 rows 后
> `POST /api/ingest/upload {"kind": "bars", "company_id": "...", "rows": [{"date","open","high","low","close","volume","amount","turnover_pct"}]}`；
> 全部传完 `POST /api/ingest/run/recompute`。取不到的 `PATCH /api/ingest/todo/{id} {"status":"dropped"}` 并说明原因。

`kind` 还可以是 `margin`（date, rz_balance, rq_balance, rz_to_float_pct）、`holders`（end_date, holder_num, change_pct, avg_cap）、
`valuation`（date, pe_ttm, pb, market_cap）、`candidates`（date, title, url, summary, source, tier, category, company_id）——最后这个是让 AI 从
讯石 / 光纤在线 / 财联社这类 RSS 打不开的站点把新闻直接喂进候选池。

## 页面上怎么体现

- 研究页头部一行「行情截至 · 有行情 x / 可取 y / 公司 z · 事件 真 / 示例 · 候选待确认 · 交给 AI 补」。
- 「候选」块：确认 → 写 events（is_sample=0，status=reviewed，来源即原文），反应按收盘重算；驳回只记状态。类别 / 公司缺的在行内补。
- 建库不带 `--no-sample` 时，样例事件仍在但标着示例；真行情一进来 series / 拥挤度 / 估值就全换成真的（`sample=0`），页脚「示例」自动消失。

## 表

`bars`（日线原始事实）→ `series`（公司指数 + 篮子指数，既有分析代码读这个）→ `reactions`。
`margin` / `holders` / `valuation_daily` → `crowding` / `valuation`。`candidates` → `events`。
`ingest_runs`（每次作业）、`ingest_todo`（交给 AI 的）。篮子：main 的层篮子照旧；实物部件篮子 `basket:part.*`（≥2 家有行情的已核验 / 行业图示公司）；
整机篮子 = main exposures 成员 ∪ 站在芯片 / 器件 / 引擎 / 模块阶段且已核验的实物公司。
拥挤度分位 = 当前值在过去 250 个交易日同类值里的百分位；偏离 = 相对参照篮子 20 日收益差的 σ 数（参照：所在层 → 主要部件篮子 → 整机）。
