# 入账 v2.2 剩余候选有界补核 · 2026-10-02

## Metadata

- Project: serenity_quant_research
- Task: 原9条待核验候选单次补核
- Timestamp (UTC): 2026-10-02T14:43:28+00:00
- Owner: Faye
- Route: direct-execute
- Source of truth: Owner 本会话授权；2026-10-01-accounting-v2.2.md
- Status: 本次补核完成，原9条中4条判不算、5条继续待核验；不是全部清零

## 结果

- `/api/candidates/judge`：本次提交4条，算0、不算4、错误0；回读全部rejected/ai。
- 当前真事件仍 **27**（AI26、规则1、示例0），部件分布不变。
- 原9条剩5条；另有本轮范围外新Qualcomm候选1条，故生产待判合计 **6**，不要误称原9条只处理3条。
- v2.2两次交付累计AI提交60条：算23、不算37，不含9月30日的旧5条重判。
- run84 recompute成功，行情截至2026-09-30；快照875个内嵌响应，无skip。Chromium打开console clean，嵌入status核对27事件、6待判、run84一致。
- 本次不重跑triage，不改正文缓存、不重开已判候选、不改实物映射或业务代码。旧stash未恢复。数据库备份及请求回执保存在 `artifacts/runtime/accounting-v2.2-followup/`。

## 本次判定及依据

### cand.4a48b04c390b：不算

补核公司2025-004投关原文全3页，第2页于2025-06-11已明确1.6T光引擎持续起量、平稳交付。2026-04-08候选是2025年度回顾，不是4月新增量产/认证节点；不将旧事实重记新催化。本次不擅以6月11日为首次量产日，若回填原始里程碑须另核首次可知日。来源：https://file.finance.sina.com.cn/211.154.219.97:9494/MRGG/CNSESZ_STOCK/2025/2025-6/2025-06-11/11827203.PDF

### cand.ef60584f9572：不算

本次完整下载26,884,321字节89页扫描PDF，直接渲染读PDF第4–5页（声明与摘要）；摘要明确评估目的是追溯武汉普赛斯全部权益市场价值，以验证2026-04-24收购39%股权价格合理性。判定所述事项为股权估值，不是部件扩产/订单/认证；未声称阅读89页全文，正文若有独立经营新事实需另核日期，不从本条估值推出。原文：https://static.cninfo.com.cn/finalpage/2026-07-22/1225434649.PDF

### cand.2943453dbe7a：不算

补读CHOSUNBIZ同题报道全文（9月29日，引用台湾联合报/经济日报），明确Texas/Dallas与6厂只是设备产业预期及评估，TSMC has not officially announced any related plans。没有可确认投资决定、产线建设或具体DSP/PIC产品族供给变化。本次候选的评估传闻不算已成立卡口，未来正式建设公告可另核。DIGITIMES全文仍不可读，不声称已读。来源：https://biz.chosun.com/en/en-it/2026/09/29/VLJD5FS2PFAS7GW2CIYKXYJLBA/

### cand.a32c938ea7ef：不算

补读CHOSUNBIZ 2026-09-30对Counterpoint同一期Q2 Foundry2.0统计的全文，核对966亿美元、同比25%、TSMC42%等同题统计；正文是通用代工/封装收入与CoWoS供需预测，没有本模块DSP/PIC具体新增产能/订单/认证。按该行业统计事项判不算，不把HBM/CoWoS约束移植为硅光卡口。Counterpoint抓取只得到标题/作者元信息，DIGITIMES全文未读，不宣称读完两者。来源：https://biz.chosun.com/en/en-it/2026/09/30/JCFCXDE3GVG7NCN6KYJVJSMK5A/

## 仍待核验的5条与本次尝试

|候选|本次结果与阻塞|
|---|---|
|cand.c1af7046eca3 中天MPO订单|既有公告证明MPO跳线订单，但公司物理映射仅整模块。本次不改映射、不错误归位；需补MPO来源映射决策，不能由UI/事件需求篡改研究事实。|
|cand.7b717ddd7e68 GMI采访|检索仍指向2025-11-17台湾AI工厂公告和融资报道，未获得本次采访增量。既有Quantum关联不能让旧项目变2026年9月新订单。|
|cand.6764c74eb530 Keysight|找到官方design-to-deployment峰会博客，但实际请求403；另一官方链接为OFC2025视频，不能替代当前事件。未依据搜索生成回答直接判定。|
|cand.de9bb5e0d45d Broadcom审计|搜索线索指向FT/Reuters报道，但未取得可核验原文与已生效采购替换措施。未访问付费墙绕过存档，不把搜索摘要当官方文件。|
|cand.a707e16ab12a GF扩张|尝试另一原站URL，仅得到付费墙前公开导语；官方结果仍为2025年AMF收购与既有能力说明，无法确认2026年9月新增事实。|

本轮范围外：`cand.aea530d1a6e7`（Qualcomm Snapdragon Summit 2026），保持新待办，不把它计入原9条。

## 获取范围说明

- 华兴源创原PDF此次下载完整，89页为扫描件；渲染阅读声明与摘要（PDF第4–5页），没有声称全文核验。截图只用于内部阅读，不作为给Owner的展示产物。
- 天孚6月投关原PDF全文3页已读取，证明4月回顾不是新量产；不把6月11日擅定为最早里程碑。
- TSMC德州使用同题CHOSUNBIZ可读全文，披露仍为产业预期、公司未正式公告，未读取付费DIGITIMES全文。
- Foundry2.0找到Counterpoint正确Q2页面，但提取仅标题/作者，没有统计正文；因此采用CHOSUNBIZ同日同一期统计报道全文，不把错误提取声称为官方全文。统计中的CoWoS缺口仍属通用AI封装，不是本模块部件事件。
- 没有反复请求同样付费墙，也没有修改工具鉴权/抓取配置；本次不自动循环安排后续定时任务。剩余候选在7天期限内仍需补证，但不会为清零假判。

## 真事件部件分布

|部件|数量|
|---|---:|
|主 PCB（高速多层板）|12|
|整模块：组装、测试、客户|5|
|CW 激光器（外置光源）|3|
|光纤阵列单元（FAU）|2|
|光源耦合：隔离器 / 透镜 / 保偏光纤|1|
|顶盖 / 散热与 TIM|1|
|MPO 插座与 MT 插芯|1|
|硅光 PIC（调制器 + 波导 + 分束）|1|
|OSFP 壳体 / 拉环 / EMI|1|
|调制器驱动器（Driver）|0|
|DSP（重定时芯片）|0|
|金手指|0|
|光引擎组装（COB / 倒装 / 耦合）|0|
|主机侧 OSFP 笼子 / 连接器|0|
|Ge 光电探测器（PD）|0|
|电源 / MCU / 存储|0|
|跨阻放大器（TIA）|0|

## `/api/ingest/status` 全文（本次重算后）

```json
{
  "as_of": "2026-09-30",
  "sample": false,
  "companies": 165,
  "quotable": 144,
  "with_bars": 144,
  "last_bar_date": "2026-09-30",
  "with_margin": 72,
  "with_valuation": 74,
  "events": {
    "real": 27,
    "sample": 0
  },
  "candidates": {
    "confirmed": 27,
    "pending": 6,
    "rejected": 9420,
    "pending_relevant": 6
  },
  "accounting": {
    "total": 9453,
    "accounted": 27,
    "by_rule": 1,
    "by_ai": 26,
    "by_human": 0,
    "to_ai": 6,
    "routine": 9346,
    "not_counted": 74,
    "dismissed_by_human": 0,
    "backfill": 8943,
    "backfill_accounted": 24,
    "expired": 0,
    "unprocessed": 0
  },
  "last_news_fetch": "2026-10-02T03:17:09",
  "todo_open": 286,
  "runs": [
    {
      "id": 84,
      "job": "recompute",
      "started_at": "2026-10-02T22:41:09",
      "finished_at": "2026-10-02T22:41:13",
      "ok": 1,
      "summary": {
        "instruments": 168,
        "points": 89158,
        "product_members": 73,
        "reactions": 100,
        "valuation": 74,
        "as_of": "2026-09-30",
        "crowding": 168
      },
      "error": null
    },
    {
      "id": 83,
      "job": "news",
      "started_at": "2026-10-02T21:15:01",
      "finished_at": "2026-10-02T21:15:31",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 502,
          "routine": 8951
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 10,
          "failed": 0,
          "bodies_read": 0,
          "bodies_missing": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 82,
      "job": "news",
      "started_at": "2026-10-02T18:15:02",
      "finished_at": "2026-10-02T18:15:31",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 502,
          "routine": 8951
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 10,
          "failed": 0,
          "bodies_read": 0,
          "bodies_missing": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 81,
      "job": "daily",
      "started_at": "2026-10-02T15:35:01",
      "finished_at": "2026-10-02T16:44:03",
      "ok": 1,
      "summary": {
        "quotes": {
          "companies_ok": 0,
          "companies_failed": 144,
          "unquotable": 21,
          "rows": 0
        },
        "inputs": {
          "companies_ok": 0,
          "companies_failed": 74
        },
        "valuation": {
          "companies_ok": 0,
          "companies_failed": 74
        },
        "recompute": {
          "instruments": 168,
          "points": 89158,
          "product_members": 73,
          "reactions": 100,
          "valuation": 74,
          "as_of": "2026-09-30",
          "crowding": 168
        }
      },
      "error": null
    },
    {
      "id": 80,
      "job": "news",
      "started_at": "2026-10-02T15:15:01",
      "finished_at": "2026-10-02T15:15:31",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 502,
          "routine": 8951
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 10,
          "failed": 0,
          "bodies_read": 0,
          "bodies_missing": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 79,
      "job": "news",
      "started_at": "2026-10-02T12:15:01",
      "finished_at": "2026-10-02T12:15:31",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 502,
          "routine": 8951
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 10,
          "failed": 0,
          "bodies_read": 0,
          "bodies_missing": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 78,
      "job": "news",
      "started_at": "2026-10-02T09:15:01",
      "finished_at": "2026-10-02T09:15:30",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 502,
          "routine": 8951
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 10,
          "failed": 0,
          "bodies_read": 0,
          "bodies_missing": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 77,
      "job": "news",
      "started_at": "2026-10-02T06:15:01",
      "finished_at": "2026-10-02T06:15:31",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 502,
          "routine": 8951
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 10,
          "failed": 0,
          "bodies_read": 0,
          "bodies_missing": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 76,
      "job": "news",
      "started_at": "2026-10-02T03:15:02",
      "finished_at": "2026-10-02T03:17:17",
      "ok": 1,
      "summary": {
        "new": 1,
        "merged": 0,
        "seen": 297,
        "triage": {
          "relevant": 502,
          "routine": 8951
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 10,
          "failed": 0,
          "bodies_read": 0,
          "bodies_missing": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 75,
      "job": "recompute",
      "started_at": "2026-10-02T00:28:14",
      "finished_at": "2026-10-02T00:28:19",
      "ok": 1,
      "summary": {
        "instruments": 168,
        "points": 89158,
        "product_members": 73,
        "reactions": 100,
        "valuation": 74,
        "as_of": "2026-09-30",
        "crowding": 168
      },
      "error": null
    },
    {
      "id": 74,
      "job": "recompute",
      "started_at": "2026-10-02T00:26:16",
      "finished_at": "2026-10-02T00:26:20",
      "ok": 1,
      "summary": {
        "instruments": 168,
        "points": 89158,
        "product_members": 73,
        "reactions": 100,
        "valuation": 74,
        "as_of": "2026-09-30",
        "crowding": 168
      },
      "error": null
    },
    {
      "id": 73,
      "job": "news",
      "started_at": "2026-10-02T00:15:01",
      "finished_at": "2026-10-02T00:17:35",
      "ok": 1,
      "summary": {
        "new": 33,
        "merged": 0,
        "seen": 296,
        "triage": {
          "relevant": 501,
          "routine": 8951
        },
        "accounting": {
          "auto": 0,
          "routine": 31,
          "triage": 64,
          "failed": 0,
          "bodies_read": 2,
          "bodies_missing": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 72,
      "job": "triage",
      "started_at": "2026-10-01T22:45:22",
      "finished_at": "2026-10-01T23:06:35",
      "ok": 1,
      "summary": {
        "rejudged": 9365,
        "relevance": {
          "relevant": 497,
          "routine": 8922
        },
        "auto": 1,
        "routine": 9316,
        "triage": 62,
        "failed": 0,
        "bodies_read": 306,
        "bodies_missing": 7,
        "reactions": 8,
        "summary": {
          "total": 9419,
          "accounted": 4,
          "by_rule": 1,
          "by_ai": 3,
          "by_human": 0,
          "to_ai": 62,
          "routine": 9316,
          "not_counted": 37,
          "dismissed_by_human": 0,
          "backfill": 8943,
          "backfill_accounted": 1,
          "expired": 0,
          "unprocessed": 0
        }
      },
      "error": null
    },
    {
      "id": 71,
      "job": "news",
      "started_at": "2026-10-01T21:15:01",
      "finished_at": "2026-10-01T21:15:14",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 209,
          "routine": 9210
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 14,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 70,
      "job": "news",
      "started_at": "2026-10-01T18:15:01",
      "finished_at": "2026-10-01T18:15:15",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 209,
          "routine": 9210
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 14,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 69,
      "job": "daily",
      "started_at": "2026-10-01T15:35:01",
      "finished_at": "2026-10-01T16:09:28",
      "ok": 1,
      "summary": {
        "quotes": {
          "companies_ok": 0,
          "companies_failed": 144,
          "unquotable": 21,
          "rows": 0
        },
        "inputs": {
          "companies_ok": 0,
          "companies_failed": 74
        },
        "valuation": {
          "companies_ok": 0,
          "companies_failed": 74
        },
        "recompute": {
          "instruments": 168,
          "points": 89158,
          "product_members": 73,
          "reactions": 8,
          "valuation": 74,
          "as_of": "2026-09-30",
          "crowding": 168
        }
      },
      "error": null
    },
    {
      "id": 68,
      "job": "news",
      "started_at": "2026-10-01T15:15:01",
      "finished_at": "2026-10-01T15:15:15",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 209,
          "routine": 9210
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 14,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 67,
      "job": "news",
      "started_at": "2026-10-01T12:15:02",
      "finished_at": "2026-10-01T12:15:15",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 209,
          "routine": 9210
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 14,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 66,
      "job": "news",
      "started_at": "2026-10-01T09:15:01",
      "finished_at": "2026-10-01T09:15:15",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 209,
          "routine": 9210
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 14,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 65,
      "job": "news",
      "started_at": "2026-10-01T06:15:01",
      "finished_at": "2026-10-01T06:15:15",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 209,
          "routine": 9210
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 14,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    }
  ]
}
```
