# 服务器上跑起来（数据接入版）

目标：页面上每个数字都有来路。行情 / 融资 / 股东户数 / 估值走免费接口（东财、Yahoo、stooq，
都是 akshare / yfinance 底下那几个 HTTP 接口，这里用标准库直接调，不装第三方包），事件走
巨潮公告 / 互动易 / RSS 进候选池，系统按规则自动入账（拿不准的交给 AI 判，人只对入账的事件说「不算」）。接口取不到的，自动记成待办，让 AI（PI + web-access）
去网页端取，再 POST 回来。

## 第一次

```bash
git checkout physical-first && git pull
cd web && npm install && npm run build && cd ..          # 前端
cd api && pip install -e ".[dev]"                         # fastapi / uvicorn（原来就有；接入层不加新依赖）
python -m app.seed --rebuild --no-sample                  # 建库；--no-sample 不装样式示例的市场层
python -m app.ingest probe                                # 每条路各试一家：东财 K 线 / 融资 / 股东户数 / 估值、Yahoo、stooq、RSS
python -m app.ingest daily --full                         # 首次全量：两年多日线 → 融资 / 股东户数 → 估值 → 重算 series / 反应 / 拥挤度
python -m app.ingest news                                 # 候选池（跑完自动按规则入账）
python -m app.ingest triage                               # 对库里还没判过的候选跑一遍入账规则（上线时对现有候选跑一次）
python -m app.ingest backfill --since 2025-10-01 --until 2026-09-29   # 巨潮公告历史回填（实物层上的 A 股公司 × 按月 × 翻页到空）
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
`valuation`（date, pe_ttm, pb, market_cap）、`candidates`（date, title, url, summary, source, tier, category, company_id, origin）——最后这个是让 AI 从
讯石 / 光纤在线 / 财联社这类 RSS 打不开的站点把新闻直接喂进候选池；进池后立刻按入账规则分流。
媒体回填（DIGITIMES / 讯石 / C114 / 光纤在线近 6 个月的光模块栏目）每行带 `"origin": "backfill"`、`"tier": 1`。

## 页面上怎么体现

- 研究页头部一行「行情截至 · 有行情 x / 可取 y / 公司 z · 事件 真 / 示例 · 交给 AI 补」。
- 「候选」是一行状态：入账（规则 / AI）· 交给 AI 判 · 例行 · 不算。规则 v2.2 在 `api/app/ingest/accounting.py::classify`
  （规格 `docs/claude/teardown-accounting-v2.md` §1，v2.2 见 `docs/claude/teardown-review-2026-09-29-real-data.md` §4）：**规则只挡与归位，判定交 AI**。
  读正文：第 0 层巨潮公告标题像事件（类别动词，或套话标题「对外投资 / 重大合同 / 签订 / 中标 / 项目 / 自愿性信息披露 / 进展 …」，或活动记录表）
  → 入账前读 PDF 正文前 1500 字写进 `candidates.summary`（`accounting.read_bodies`，要 `pypdf`；取不到也记 `body_at`，不每轮重抓，照旧交 AI 读原文）。
  挡：例行正则分硬 / 软两组（`news.py::ROUTINE_HARD` / `ROUTINE_SOFT`，英文源另有 `ROUTINE_EN`）。硬组（发行上市 / 定期报告 / 盘面汇总 / 募资置换 …）
  命中就不算；软组（使用募集资金 / 增资 / 借款 / 投资进展 / 土地使用权 / 出让合同 / 调研）在标题同时有产品词与类别动词时不挡；
  归位：公司不在这只模块的任何部件上（Meta / 微软 / 需求侧）→ 不算，否则给一个部件初判（`candidates.part_id`）；
  强命中（公告 / 互动易 + **标题**里有部件词或强产品词 + 标题有类别动词 + 类别与日期）→ 入账（decided_by=rule，confidence=3，类别取动词的）；
  正文里的产品词不算强命中（「公司主营光模块」是公司简介），只决定交不交 AI；
  其余 → `ingest_todo`（kind=`candidate_triage`，company_id 列放候选 id）交给 AI；综合媒体标题没有部件 / 产品词的、
  第 0 层公告标题没有类别动词且标题 + 正文都没有部件 / 产品词的直接不算。
  交给 AI 7 天没判的待办作废（`news` 作业末尾），候选保持 pending。
- 规则换版后第一次 `triage` 会把上一版规则判过的候选（自动入账的与判成例行的）重开重判（人判过的、AI 判过的不动），
  版本记在 `settings.accounting_rules`（当前 v2.3）。
- 归位底线：事件只能落在公司已有映射的部件上（`/judge`、`/confirm` 校验，读的时候也不认映射以外的 `part_id`）；
  AI 认为公司该站在别的部件上，开 `mapping_candidate` 待办附来源（`POST /api/mapping/candidates`），走证据流程进 physical JSON，事件不改研究事实。
- 互动问答（`source_type=cninfo_irm`：互动易接口，或上证 e 互动网页端上传）：标题是问题、摘要是回答；不自动入账，
  回答里有事件、问答提到部件 / 产品的交 AI，其余例行。
- 人工只剩「不算」：研究页卡口事件行悬停出现，`POST /api/events/{id}/dismiss`，可撤回（`/restore`）。
- `seed --rebuild` 不倒回事件表，按已入账的候选重新写出来（人判的「不算」不会回来；部件 / thesis / confidence 跟着回来）。

给 PI 的候选判定：读 `GET /api/ingest/todo?status=open`，kind=`candidate_triage` 的每条 hint 是一个结构化任务
（「判断这条候选是不是『公司 在 部件 上的卡口事件』…」），打开原文判断后**批量**交回（一批最多 200 条，每条各自成败）：

```bash
curl -X POST http://localhost:8000/api/candidates/judge -H 'content-type: application/json' -d '{"by": "ai", "items": [
  {"id": "cand.xxxx", "is_chokepoint": true, "part_id": "part.cw-laser", "category": "qualification", "date": "2026-09-21",
   "thesis": "一句话：这件事对这个部件意味着什么", "confidence": 4, "reason": "原文依据"},
  {"id": "cand.yyyy", "is_chokepoint": false, "reason": "募集资金用途变更，与产线无关"}]}'
```

`is_chokepoint=true` 要给 `thesis` 与 `confidence`（1–5）；`category` / `date` / `part_id` 不给就用候选上的；候选命中多家公司时要给 `company_id`。
规则判过的以 AI 为准（会重开再判）；人判过的不改。单条 `/confirm`、`/reject` 仍可用，也接收 `part_id / thesis / confidence`。
公告正文：装了 `pypdf` 时入账前读正文前 1500 字进摘要（抓取时不读）；没装就在 hint 里的原文链接读。

**入账 v2.1 上线步骤**（给 PI，已执行，见 `ops/reports/2026-09-29-accounting-v2.1.md`）：
1. `git pull` → `cd web && npm run build` → 重启 uvicorn
2. `pip install pypdf`（可选：活动记录表正文补进摘要；不装就交 AI 读原文）
3. `python -m app.ingest triage`（第一次会把 v1 入账的 12 条和规则判成例行的重开，按 v2.1 重判）
4. `python -m app.ingest backfill --since 2025-10-01 --until 2026-09-29`
5. 读 `GET /api/ingest/todo?status=open`（kind=`candidate_triage`）判候选，`POST /api/candidates/judge` 交回
6. `python -m app.ingest recompute`
7. 出快照（`python3 tools/snapshot/build.py --api http://127.0.0.1:8000`）推上来，执行记录写 `ops/reports/YYYY-MM-DD-*.md`

**入账 v2.2 上线步骤**（给 PI；规格 `docs/claude/teardown-review-2026-09-29-real-data.md` §5）：
0. **先量回填漏了多少**（评审 §3，必须在第 3 步 `triage` 之前跑：`triage` 会把这些规则例行的重开），数字写进报告：
   ```sql
   SELECT COUNT(*) FROM candidates
    WHERE origin='backfill' AND status='rejected' AND decided_by='rule'
      AND title NOT LIKE '%股东大会%' AND title NOT LIKE '%减持%' AND title NOT LIKE '%质押%' AND title NOT LIKE '%回购%'
      AND title NOT LIKE '%激励%' AND title NOT LIKE '%审计%' AND title NOT LIKE '%问询%' AND title NOT LIKE '%年度报告%'
      AND title NOT LIKE '%季度报告%' AND title NOT LIKE '%半年度报告%' AND title NOT LIKE '%业绩%'
      AND (title LIKE '%对外投资%' OR title LIKE '%重大合同%' OR title LIKE '%签订%' OR title LIKE '%中标%'
           OR title LIKE '%投资建设%' OR title LIKE '%项目%' OR title LIKE '%自愿性%' OR title LIKE '%产线%'
           OR title LIKE '%投产%' OR title LIKE '%扩产%' OR title LIKE '%出货%');
   ```
1. `git pull` → `cd web && npm run build` → 重启 uvicorn（`pypdf` 已装；没装的话 `pip install pypdf`，否则读不了正文，套话标题全部交 AI）
2. v2 之前经旧 `/confirm` 入的 5 条按 v2.1 标准重判（评审 §5.2，`POST /api/candidates/judge`，已入账的会先重开）
3. `python -m app.ingest triage`：换版重判（v2.1 规则判过的入账与例行全部重开）+ 读正文 + 分流。**这一步就是「对回填候选重跑读正文」**，
   不用另跑命令；套话标题的公告每条下载一份 PDF，预计几千条、一小时上下，日志每 50 条报一次进度，期间持有 ingest.lock
4. 判新一批 `candidate_triage` 待办（预计几百条，分批 ≤ 200，7 天内判完），`POST /api/candidates/judge` 交回
5. `python -m app.ingest recompute`
6. 出快照推上来，报告写 `ops/reports/YYYY-MM-DD-*.md`，加一行**真事件数（AI 判算的 + 规则入账的）与按部件的分布**：
   ```bash
   cd api && python - <<'PY'
   from collections import Counter
   from app import market
   from app.db import connect
   evs = market.list_events(connect(), limit=100000)          # 已排除人判「不算」的
   real = [e for e in evs if not e["is_sample"]]              # 只算真事件，不算示例
   print(len(real), Counter((e["part"] or {}).get("part_name") for e in real).most_common())
   PY
   ```

**入账 v2.3 上线步骤**（给 PI；Owner 10-02 的决定，见 `docs/claude/teardown-status.md` 待做 1）：
1. `git pull` → `cd web && npm run build` → 重启 uvicorn（`settings.accounting_rules` 换到 v2.3）
2. `python -m app.ingest probe`，看「irm 300308」那一行：`ok … rows=… answered=… keys=[…]` 说明互动易新接口通了（keys 里应有
   `indexId / mainContent / attachedContent / updateDate`，没有就把这一行贴进报告，CC 照着改 `news._irm_item`）；`ERR` 就走第 6 步的上传
3. 按 id 重判 3 条（`POST /api/candidates/judge`，`is_chokepoint: false`，reason 写清楚）：
   `cand.54cf09807441`、`cand.42f9ff26f061`（生益电子 10-29 / 03-13：募投项目结项 / 投用，不是新增产能）；
   `cand.c1af7046eca3`（中天科技 MPO 跳线订单：跳线是机房外部布线，不是模块内的 MPO 插座 / MT 插芯，Owner 定不算）
4. `python -m app.ingest triage`（换版重判：v2.2 规则判过的重开；新挡「结项 / 内部投资结构 / 延期 / 变更或增加实施地点、实施主体」）
5. 互动易回填（深交所、站在部件上的 36 家）：`python -m app.ingest backfill --only cninfo_irm --since 2025-10-01 --until 2026-09-30`；
   只取已回答的问答，标题 = 问题、摘要 = 回答、日期 = 回答日。问题不是事实：互动问答不会自动入账，回答里有事件、问答提到部件 / 产品的交 AI，其余例行
6. 上证 e 互动（上交所 32 家；以及第 2 步不通时的互动易）没有接口，从网页端整理后上传——只传「回答里有扩产 / 订单 / 认证 / 送样 / 出货 / 供需 / 涨价 / 路线、
   问答提到部件或产品」的，别的传了也会被判例行：
   ```bash
   curl -X POST http://localhost:8000/api/ingest/upload -H 'content-type: application/json' -d '{"kind": "candidates", "rows": [
     {"source_type": "cninfo_irm", "source": "上证e互动", "company_id": "cn.688498", "origin": "backfill",
      "date": "2026-07-10", "title": "<问题原文>", "summary": "<回答原文>", "url": "<问答页链接>"}]}'
   ```
7. 判新一批 `candidate_triage` 待办（分批 ≤ 200，7 天内）。**部件只能是公司在实物映射里站着的**（hint 里列出），认为公司该站在别的部件上：
   `POST /api/mapping/candidates {company_id, part_id, stage, role, sources:[{title, url, publisher, date, quote}], reason, candidate_id}`，
   这条候选先不交回；`GET /api/mapping/candidates` 看提议，映射按 `physical/README.md` 证据流程进 physical JSON、重建后自动关掉并把候选重新交 AI
8. `python -m app.ingest recompute` → 出快照 → 报告：真事件数、按部件、**按类别**（这一轮看订单 / 认证 / 出货有没有进来）

回填可靠性：每页独立提交候选（尚不代表事件入账），日志在请求前和提交后输出公司 / 月份 / 页码 / 耗时，重定向也立即刷新。
后页失败或进程中断不会撤销已提交页；存储失败直接终止，不伪装成网络失败。`fetch.complete=false` 表示某些月份失败、熔断或达到页数上限，
作业 `ok=false`，具体位置在 `fetch.failures` / `last_position`。`fetched` / `tagged` 是本次扫描去重后的计数，`new` 才是新增入库数；重跑可能 fetched 非零而 new 为零。
恢复时用原区间重跑，按 URL 幂等去重并保留既有判定；**这是幂等重扫，不是持久游标断点续传**。异常中断后的候选可先执行 `triage`，再恢复抓取。
单条公告缺 PDF 链接或标题：跳过并计数（`fetch.skipped`，`fetch.failures` 里按条记 `kind: item`），整页照常提交，不影响 `complete`。
CLI 的 Ctrl-C / SIGTERM 会收尾自己的作业记录。SIGKILL、断电、工具超时留下的未完成记录由下一次作业启动时收尾：`finished_at` 为空、
且「同一 job」或「`started_at` 早于 12 小时」的 run 记 `ok=0, error='中断未收尾（进程被杀或超时）'`（作业由 ingest.lock 串行，
同一 job 的新 run 能开始就说明旧的已经死了；别的 job 12 小时内的不动）。
- 建库不带 `--no-sample` 时，样例事件仍在但标着示例；真行情一进来 series / 拥挤度 / 估值就全换成真的（`sample=0`），页脚「示例」自动消失。

## 表

`bars`（日线原始事实）→ `series`（公司指数 + 篮子指数，既有分析代码读这个）→ `reactions`。
`margin` / `holders` / `valuation_daily` → `crowding` / `valuation`。`candidates` → `events`。
`ingest_runs`（每次作业）、`ingest_todo`（交给 AI 的）。篮子：main 的层篮子照旧；实物部件篮子 `basket:part.*`（≥2 家有行情的已核验 / 行业图示公司）；
整机篮子 = main exposures 成员 ∪ 站在芯片 / 器件 / 引擎 / 模块阶段且已核验的实物公司。
拥挤度分位 = 当前值在过去 250 个交易日同类值里的百分位；偏离 = 相对参照篮子 20 日收益差的 σ 数（参照：所在层 → 主要部件篮子 → 整机）。

## 2026-09-27 服务器首轮之后（见 ops/reports/2026-09-27-deployment-and-ingest.md）

跑通了：139 / 144 家有真行情，71 家融资、73 家估值，候选池 318 条，事件 0 条（没人确认）。这轮改动针对它暴露的问题：

- **候选池被例行公告淹了**：巨潮按公司拉回来的减持 / 质押 / 股东大会 / 回购进展全进了池子。现在每条候选带 `relevance`（1 值得看 / 0 例行），
  规则在 `news.py::relevance_of`（例行标题正则 + 强关键词 + 类别 / 部件命中；投资者关系活动记录表永远算相关）；收件箱默认只显示值得看的，
  可切「连例行公告一起看」。已有的池子会在下一次 `news` 作业自动重算，或手动 `POST /api/candidates/retriage`。
- **东财长窗口断连**：K 线改成 120 天一段、段间歇 1.5 秒；某段失败退到 Yahoo。若服务器代理对 push2his 不稳定，`daily --full` 可以多跑几次，只补缺的。
- **逐家查的源加了熔断**：巨潮 / 互动易连续 5 家失败即停，不再把 74 家试一遍（首轮 news 9 分钟大半耗在这）。
- **打不开的源停用**：`news_sources.json` 里 `enabled:false` + 原因（讯石 TLS、C114 / OFweek / Semiconductor Today / Lightwave 404、集微非 XML、
  见闻 404、经观 403、智东西 500、互动易 405）。换到能打开的地址再打开；或让 AI 从这些站的网页端以 `kind=candidates` 上传。
- **五家缺口**：则成电子北交所新代码 920821（公司 id 改为 cn.920821，seed 重建即生效）、台燿 6274 是上櫃（TPEx → Yahoo `6274.TWO`）；
  蘅东光 / 万源通 / 凯德石英 三家北交所 Yahoo 没有，只能靠东财分段拉或 AI 上传。

**为什么页面「看起来没变」**：变的是行情 / 拥挤度 / 估值那一层（公司页价格图、篮子页 3 个月超额、拥挤度读数、PE 分位），
而首页「资金本周在给哪一层投票」、事件面结论、共振、时效全部是**事件驱动**的——事件表现在是空的，候选没人确认就永远是空的。
（2026-09-29 起候选按规则自动入账，见上文「页面上怎么体现」。）
