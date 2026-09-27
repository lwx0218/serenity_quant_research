# 服务器部署与真实数据抓取执行记录

记录日期：2026-09-27；时区：Asia/Shanghai。

本记录按 Owner 要求提交 Git，汇总 2026-09-25—2026-09-27 的部署、只读排查及授权重算。第 1—8 节保留截至 09-27 19:10 的历史记录；后续部署和重算见第 9 节，不将历史状态作为当前状态。它不是新增数据源、修改解析器或后续补数的授权。原始证据仍保存在服务器本地，未随本提交上传。

## 1. 代码与部署

执行基线为 `physical-first` 分支、提交 `047e4b5`：

- `f80fd3c`：真实行情、拥挤度、估值接入及候选事件功能。
- `5e85eb1`：pi-web-ui 配置。
- `047e4b5`：公司目录测试适配实物种子公司。

上述代码已推送。此后部署及排查没有修改 `api/app/ingest/`、`physical/data/` 或 `data/seeds/`。

已完成：

1. 安装前端依赖并构建 `web/dist`，在 `api/.venv` 安装 API 及开发依赖；40 项 API unittest 通过。
2. 停止占用端口的旧服务及原 5000 API。
3. 备份重建前数据库，备份完整性检查通过。重建前只有 21 条示例事件，没有真实行情或真实事件。
4. 执行授权命令 `python -m app.seed --rebuild --no-sample`。
5. 执行 probe、首轮 `daily --full` 和 news；未手工 SQL 写业务库。
6. 部署 `teardown-api.service`，监听 `0.0.0.0:8000`，同时提供 API 与构建后的前端；启用开机自启和失败重启。
7. 浏览器检查首页与 `/research`，当时控制台无错误。

2026-09-27 19:10 再次检查：`teardown-api.service` 和 `crond` 均为 active/enabled。安装 AKShare 后 `/api/health` 检查亦通过。

## 2. 定时运行

用户 crontab 使用 `CRON_TZ=Asia/Shanghai`：

| 任务 | 表达式 | 含义 |
|---|---|---|
| daily | `35 15 * * 1-5` | 周一至周五 15:35 |
| news | `15 */3 * * *` | 每天每三小时的第 15 分钟 |

两者使用绝对虚拟环境 Python 路径，并共用 `flock -n` 锁，避免定时作业重叠；锁被占用时该次启动会跳过。星期过滤不是交易所节假日日历。

- 锁：`artifacts/runtime/ingest.lock`。
- 连续运行日志：`artifacts/runtime/teardown-ingest.log`。
- 服务和 cron 的网络环境来自服务器权限受限的私密环境文件；配置值不纳入本记录或 Git。

已确认实际执行的部分批次（北京时间）：

| run ID | 任务 | 开始—结束 | 结果 |
|---|---|---|---|
| 2 | daily --full | 09-25 13:48:56—14:27:21 | 139 家成功、5 家失败；写入 73,030 条行情 |
| 3 | news | 09-25 14:27:21—14:36:36 | 原始 441 条，新增 306 条候选 |
| 4 | cron news | 09-25 15:15:02—15:24:00 | 新增 2 条、合并 290 条 |
| 5 | cron daily | 09-25 15:35:02—16:14:05 | 行情写入/更新 1,194 条；仍有 5 家失败 |
| 22 | cron news | 09-27 18:15:02—18:24:01 | 新增 4 条、合并 1 条 |

这些批次作业层 `ok=1`、`error=null`，不代表所有数据源成功。部分源错误被记录在日志后仍正常返回；例如 09-27 09:15、12:15 的 news 批次 `seen=0`，不能据此认定资讯源健康。

## 3. 数据状态快照

2026-09-27 19:10 获取 `/api/ingest/status`，以下摘录不含作业历史字段：

```json
{
  "as_of": "2026-09-25",
  "sample": false,
  "companies": 165,
  "quotable": 144,
  "with_bars": 139,
  "last_bar_date": "2026-09-25",
  "with_margin": 71,
  "with_valuation": 73,
  "events": {"real": 0, "sample": 0},
  "candidates": {"pending": 318},
  "last_news_fetch": "2026-09-27T18:24:01",
  "todo_open": 5
}
```

首轮 daily 已完成篮子、序列、估值及拥挤度重算。没有自动确认候选事件，也没有执行人工补数上传。

首轮行情抓取发生在盘中，日期相同不等于当时已取得最终收盘价；页面现有“收盘”文案未调整。研究页候选列表当时展示上限为 100 条，标题列过窄；这些 UI 问题未在本次修复。

## 4. 五家行情缺口

| 公司 | 稳定 company_id | 首轮查询代码 | 已记录问题 / 后续只读核查 |
|---|---|---|---|
| 则成电子 | `cn.837821` | `837821` / `837821.BJ` | 东财断连、Yahoo 404；北交所官方对照表确认新证券代码为 `920821` |
| 蘅东光 | `cn.920045` | `920045` / `920045.BJ` | 东财断连、Yahoo 404 |
| 万源通 | `cn.920060` | `920060` / `920060.BJ` | 东财断连、Yahoo 404 |
| 凯德石英 | `cn.920179` | `920179` / `920179.BJ` | 东财断连、Yahoo 404 |
| 台燿 TUC | `global.tuc` | `6274.TW` | Yahoo 404；独立测试 `6274.TWO` 返回 HTTP 200、487 条非空收盘价 |

代码核查参考：

- 北交所新旧证券代码对照表：<https://www.bse.cn/service/code_mapping.html>。
- 台燿 Yahoo 标识：<https://finance.yahoo.com/quote/6274.TWO/>。

查询代码变更不应直接改动公司稳定 ID。台燿可取数据只保留了诊断结论，尚未写入业务库；所有五条缺口仍未正式补齐。

## 5. 外部数据源问题

首轮探测及抓取发现：

- 东财 K 线多次在收到 HTTP 响应前断开，错误为 `RemoteDisconnected`；此时没有状态码或响应体。
- stooq 返回 HTTP 200，但正文为浏览器验证页，而非行情数据。
- 互动易对 74 家公司的查询均返回 HTTP 405；当前流程仍逐家公司尝试，没有源级停止机制。
- RSS 失败包括：讯石 TLS EOF；C114、OFweek、Semiconductor Today、Lightwave 404；集微返回 HTML 而非 XML；华尔街见闻非 XML（另一次带 Referer 补证为 404）；经济观察 403；智东西 500。

首轮 daily 耗时 38 分 25 秒、news 耗时 9 分 15 秒，重复尝试失败源是重要耗时因素。任务仍在推进，并非已证实的死锁。

## 6. 北交所直连、分段与 AKShare 排查

### 6.1 复现 AKShare 参数

2026-09-27 18:50，从 AKShare 官方源码核对 `stock_zh_a_hist` 参数，用标准库执行只读请求：

- 四个北交所代码 `920821 / 920045 / 920060 / 920179`，另加深市 `300308` 作对照。
- 短窗口 2026-09-01—2026-09-27，日线、前复权参数。
- 继承服务器代理环境：五个请求均断连。
- 显式直连：五个请求均 HTTP 200，各返回 18 条记录，日期为 09-01—09-24，公司名称与代码匹配。
- 扩大到 2024-07-19 起的长历史窗口：四家公司及则成电子旧代码对照均断连。

这证明东财存在四家北交所的日线数据，但不证明其完整历史可稳定取得。返回截至 09-24 的原因及交易日完整性未核实。不能将长窗口失败唯一归因于窗口长度或限流。

### 6.2 低频分月验证

18:56 再测：服务器直连、串行、请求间隔 5 秒、每次超时 8 秒。则成电子、蘅东光的短窗口均断连；达到预设连续两次失败阈值后停止，未继续请求剩余公司或月份。

前次短窗口直连成功未能稳定复现，没有取得新的补数记录。

### 6.3 实际安装并运行 AKShare

Owner 随后明确授权安装，覆盖此前“不安装该包”的限制：

- 在 `api/.venv` 安装 **AKShare 1.18.96**，共新增 25 个包（包含依赖）。
- 安装前将已有 31 个包的版本约束固定，安装后确认它们均未改变；`pip check` 通过。
- 没有将 AKShare 加入业务依赖声明；此次安装仅存在于该服务器虚拟环境。
- 19:00 实际调用安装包的 `ak.stock_zh_a_hist`，四个北交所代码及 `300308` 对照均失败：`ConnectionError / RemoteDisconnected`。
- 调用前清除测试子进程所有大小写代理环境变量，设置 `NO_PROXY=*`，并检查实际请求的有效代理配置均为 `{}`。未改变库源码或默认请求头。
- 该测试明确未使用 Python 环境代理，但不能据此排除服务器网络中的 NAT 或透明网关。请求发起地仍是 SSH 服务器，并非用户个人电脑。
- 安装后 40 项 API unittest 通过，运行中 API 健康检查正常。

结论：换库和关闭应用层代理未解决当前服务器访问问题，且深市对照同样失败。具体断连根因未确定，不能断言封 IP、限流或北交所不受支持。没有修改线上服务代理配置或继续无限重试。

## 7. 未执行事项

- 未修改业务解析器、股票种子映射或公司稳定 ID。
- 未执行第二段网页补数、上传或人工候选确认。
- 未将任何补数记录写入业务库；未调用补数后的 recompute。
- 未决定新增长期数据源、交易所日历或永久网络路由策略。
- 未将数据库、私密配置、虚拟环境、`api/sqr_api.egg-info/` 或原始大日志提交 Git。

下一步如恢复处理，需要另行确认方案，例如从用户个人电脑网络做同样测试，或使用有来源的历史日线导出文件，通过现有上传接口导入。

## 8. 服务器本地证据索引

以下路径均为仓库根目录相对路径，受 Git 忽略规则管理，**不会因本提交而出现在其他克隆或远端仓库中**：

| 路径 | 内容 |
|---|---|
| `artifacts/deploy-20260925/phase-one-report.md` | 第一段完整部署记录、probe、状态、失败响应 |
| `artifacts/deploy-20260925/pre-rebuild.sqlite` | 重建前备份，仅服务器本地 |
| `artifacts/deploy-20260925/{daily,news,probe}.log` | 首轮作业原始日志 |
| `artifacts/deploy-20260925/{status,runs,todo}.json` | 第一段结束时的原始接口快照，非当前状态 |
| `artifacts/deploy-20260925/http-diagnostics.json` | 接口探测原始证据 |
| `artifacts/deploy-20260925/http-daily-diagnostics.json` | 五家缺口请求原始证据 |
| `artifacts/runtime/teardown-ingest.log` | 后续 cron 持续日志 |
| `artifacts/bse-probe-20260927/report.md` | 首轮代理/直连与长历史对照 |
| `artifacts/bse-segmented-20260927/20260927T185624/report.md` | 低频分月验证及停止原因 |
| `artifacts/akshare-test-20260927/report.md` | AKShare 安装、直连实测与验证 |
| `artifacts/akshare-test-20260927/20260927T190022/results.json` | 实际 AKShare 请求及代理核验记录 |

本提交只归档上述执行情况，不等同于备份运行数据库或把服务器环境打包到云端。

## 9. 后续部署与重新计算（09-27 23:32 快照）

### 9.1 代码与生产部署

按 Owner 要求再次拉取 `physical-first`，从 `abf3df2` 快进至 `a0d7ce1`，没有本地业务源码修改。此前当晚已经部署 `da223ce`（42 项 API 测试通过）和 `abf3df2`（43 项通过）。

最新版本将实物页作为正式首页，集成按部件的资金投票、部件详情和卡口事件；原层视图保留在 `/layers`。此前 `abf3df2` 的独立方向稿不等同于生产集成，本次正式前端已完成集成。

部署验证：

- API：`cd api && .venv/bin/python -m unittest -q`，57 项测试通过，耗时 7.022 秒；存在 Starlette/httpx 弃用提示，不影响通过。
- Web：`cd web && npm run build`，TypeScript 检查及 Vite 生产构建通过。
- 23:32:27 重启 `teardown-api.service`，检查为 active/running，`/api/health` 返回 HTTP 200。
- 浏览器验证正式首页及选中部件详情，资金投票读数可见，控制台无错误或警告。
- 仍发现 1280px 视口选中部件后页面宽度为 1440px，右栏存在横向溢出；本次没有修改布局。

### 9.2 备份与授权重算

使用 cron 共用锁 `artifacts/runtime/ingest.lock` 防止作业重叠。先以 SQLite 只读源连接执行 backup，保存 `pre-recompute.sqlite`，完整性检查为 `ok`；随后在 API 虚拟环境执行 Owner 指定的命令：

```bash
python -m app.ingest recompute
```

运行记录：run ID **24**，09-27 **23:32:13—23:32:15**，`ok=1`、`error=null`。

```json
{
  "instruments": 163,
  "points": 86476,
  "product_members": 70,
  "reactions": 0,
  "valuation": 73,
  "as_of": "2026-09-25",
  "crowding": 163
}
```

重算前后检查以下原始表行数一致：

| 表 | 重算前 | 重算后 |
|---|---:|---:|
| bars | 73,035 | 73,035 |
| companies | 165 | 165 |
| candidates | 324 | 324 |
| events | 0 | 0 |

本次没有执行 seed 重建、抓取新行情、人工上传、候选确认或直接 SQL 写业务库。重算结果由已有真实数据生成；真实事件仍为 0，因此 `reactions=0` 不表示重算失败。新的部件篮子规则要求至少 3 家有行情公司，篮子组成随新版规则重新计算，不能将序列数量变化直接视为原始行情丢失。

### 9.3 重算后的数据快照

以下为 23:32 部署检查时的 `/api/ingest/status` 摘录，不代表后续 cron 执行后的实时状态：

```json
{
  "as_of": "2026-09-25",
  "sample": false,
  "companies": 165,
  "quotable": 144,
  "with_bars": 139,
  "last_bar_date": "2026-09-25",
  "with_margin": 71,
  "with_valuation": 73,
  "events": {"real": 0, "sample": 0},
  "candidates": {"pending": 324, "pending_relevant": 25},
  "last_news_fetch": "2026-09-27T21:17:46",
  "todo_open": 5
}
```

五家行情缺口仍未补齐。远端代码已包含证券映射种子修正及抓取容错更新，但种子变动没有自动迁移到现有业务库，本次未重建数据库或迁移公司 ID。第 5 节描述的是首轮抓取行为，不是对新版数据源健康状况的重新验证。

### 9.4 本地证据与提交范围

原始证据目录为 `artifacts/redeploy-20260927-2331/`：

| 文件 | 内容 |
|---|---|
| `pre-recompute.sqlite` | 重算前数据库备份，仅服务器本地 |
| `counts-before.json` | 原始表重算前行数；运行时另核验重算后相等 |
| `recompute.log` | CLI 完整输出 |
| `recompute-run.json` | run 24 的状态、时间与汇总 |
| `status.json` | 重算后接口状态快照 |
| `tests.log` | 57 项 API 测试结果 |
| `build.log` | TypeScript 检查与生产构建结果 |

此前两次部署证据分别位于 `artifacts/redeploy-20260927-2007/` 和 `artifacts/redeploy-20260927-2051/`。

按 Owner 要求，本次仅将部署和重算结果补入此文档并提交推送；数据库、派生数据、构建产物、私密环境、虚拟环境、安装元数据及原始 artifacts 不随 Git 上传。
