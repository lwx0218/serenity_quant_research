# 重建、候选入账与重算执行记录

记录日期：2026-09-29；时区：Asia/Shanghai。执行基线：`physical-first` / `6cb4f58`。

Owner 授权重建、采集、候选入账、重算、服务重启，以及提交本记录和既有 Pi 启动配置变更。以下是本次运行快照，不代表后续定时任务执行后的实时状态。

## 1. 备份与重建

- 本地没有遗留 `data/sqr.ingest-keep*.sqlite`；Owner 确认不以此阻塞重建。
- Web 的 `npm run build` 通过（TypeScript 检查及 Vite 生产构建）。
- 首次重建在表结构升级阶段遇到 `database is locked`，尚未删除主库。同期 cron daily（run 40）于 15:35:01—16:10:26 运行；其后检查未见采集进程或数据库锁。
- 重试及后续采集、入账、重算均使用 cron 共用的 `artifacts/runtime/ingest.lock`，避免与定时采集重叠。未修改 cron 或永久锁策略。
- 以 SQLite backup API 创建一致性备份，完整性检查均为 `ok`：
  - `artifacts/rebuild-20260929-160851/sqr.sqlite`（首次尝试前）。
  - `artifacts/rebuild-20260929-161521/sqr.sqlite`（定时任务结束后、成功重建前）。
- 最新备份含 73,331 条行情、423 条候选。备份只在本机保留，不提交 Git。

成功执行 `cd api && .venv/bin/python -m app.seed --rebuild --no-sample`，关键输出：

```text
ingest_restored_bars: 73331
ingest_renamed: 1
ingest_orphans: 0
ingest_keep_files: 1
ingest_leftover_keep_files: 0
```

`ingest_keep_files=1` 是本次从现有主库创建的临时快照，不是历史遗留文件。恢复完成后检查无剩余 keep 文件。

## 2. 当日采集与中断

- 此前 cron daily（run 40）正常完成，作业层 `ok=1`；行情 139 家成功、5 家失败，估值 73 家成功、1 家失败。作业成功不等于所有数据源成功。
- 本次 daily（run 41）于 16:15:42 开始；日志多次出现东财 `RemoteDisconnected`，随后改用 Yahoo，并报告四个北交所代码取数失败。
- 本次调用后来被中断。16:44 检查已无采集进程、无相关文件锁；数据库中 run 41 的 `finished_at/ok/summary/error` 仍为 NULL，未手工将它改成成功。该记录不代表进程仍在运行。
- 部分采集结果已提交，行情总数变为 73,862 条，截至 2026-09-29。未宣称本轮融资、估值等所有阶段完整跑完。
- Owner 确认不再重跑完整 daily，继续入账、重算和重启。

## 3. 候选入账、重算与重启

| run ID | 作业 | 开始—结束 | 结果 |
|---|---|---|---|
| 42 | triage | 16:45:37—16:45:40 | 成功，失败计数 0 |
| 43 | recompute | 16:45:40—16:45:42 | 成功 |

423 条候选按现有规则处理：12 条自动入账、365 条例行排除、46 条交给 AI，未处理计数 0。没有进行人工候选确认或 AI 原文判定。

重算结果：

```json
{
  "instruments": 164,
  "points": 87359,
  "product_members": 70,
  "reactions": 11,
  "valuation": 73,
  "as_of": "2026-09-29",
  "crowding": 164
}
```

- 数据库 `PRAGMA integrity_check` 为 `ok`，`foreign_key_check` 违规数为 0。
- 16:45:51 重启 `teardown-api.service`，服务为 active，新 PID 为 1349448。
- 重启后 `/api/ingest/status` 请求成功。
- API：`cd api && .venv/bin/python -m unittest -q`，67 项测试通过（7.485 秒）；存在 Starlette/httpx 弃用提示。
- 本次未修改 UI 源码，未另做浏览器视觉验收。

## 4. 重启后的状态快照

以下摘录省略运行历史：

```json
{
  "as_of": "2026-09-29",
  "sample": false,
  "companies": 165,
  "quotable": 144,
  "with_bars": 140,
  "last_bar_date": "2026-09-29",
  "with_margin": 72,
  "with_valuation": 73,
  "events": {"real": 12, "sample": 0},
  "candidates": {
    "confirmed": 12,
    "pending": 46,
    "rejected": 365,
    "pending_relevant": 46
  },
  "accounting": {
    "total": 423,
    "accounted": 12,
    "by_rule": 12,
    "by_ai": 0,
    "by_human": 0,
    "to_ai": 46,
    "routine": 365,
    "not_counted": 0,
    "dismissed_by_human": 0,
    "unprocessed": 0
  },
  "last_news_fetch": "2026-09-29T15:17:34",
  "todo_open": 4
}
```

剩余工作：4 家行情缺口、46 条候选待 AI 判定；run 41 保留中断后的未收尾状态。未新增数据源、修改采集频率或自动补齐这些事项。

## 5. 本次 Git 范围

按 Owner 确认，一并提交此前已有的两个改动：

- `.pi/settings.json`：移除项目内 `pi-web-ui@0.95.0` 包引用。
- `scripts/pi-web-ui.sh`：使用 npm 全局安装的 pi-web-ui，保留项目原会话数据目录；脚本内容未在本次修改。

本次不提交数据库、备份、Web 构建产物、私密运行环境、`api/sqr_api.egg-info/`。Git 推送不等于备份或同步运行数据库。
