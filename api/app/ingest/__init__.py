"""数据接入：把真实的行情 / 拥挤度输入 / 估值 / 事件候选写进市场层的表。

- 行情：东财 K 线（A 股，同 akshare stock_zh_a_hist 用的接口）→ Yahoo chart → stooq（海外）
- 拥挤度输入：东财数据中心（融资余额、股东户数），加上行情算出来的分位和偏离
- 估值：东财数据中心 PE TTM 历史 → 当前值 + 5 年分位
- 事件候选：RSS / 巨潮公告 / 互动易（scripts/news_fetch.py 的逻辑搬到 news.py），进 candidates 表，人工确认才成事件

每次抓取记在 ingest_runs；抓不到的记在 ingest_todo，让服务器上的 AI（PI + web-access）去网页端取，
再用 POST /api/ingest/upload 交回来。全部标准库，不依赖 akshare 等第三方包。"""
