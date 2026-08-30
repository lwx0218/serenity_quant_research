# CPO 公司候选池

## Metadata

- Project: serenity_quant_research
- Document type: research-baseline
- Status: active
- Owner: project owner
- Last updated: 2026-08-30
- Source of truth: docs/research-baseline/evidence-contract.md

## 1. 状态与用途

- 状态：Phase 1 P0 seed candidate baseline
- 建立日期：2026-08-24
- 规模：20 家（8 家全球产业锚点 + 12 家 A 股重点研究候选）
- 用途：为 P1 建立 `Company` 与候选 `CompanyExposure` seed；不是投资建议、推荐名单或已验证供应链名单
- 关键约束：公司身份和证券代码可视为基础资料；技术能力、客户关系、订单、收入暴露和 CPO 映射均须逐条引用证据

## 2. 入池与状态规则

### 两层公司池

1. **全球产业锚点**：用于需求、交换 ASIC、技术路线、生态和供应链语境；默认只做上下文覆盖。
2. **A 股重点研究候选**：用于完整公司研究流程；优先验证公司公开披露的产品能力，再判断是否能建立 CPO 暴露。

### `CompanyExposure` 最小状态

| 状态 | 含义 | UI/报告规则 |
|---|---|---|
| `discovery` | 来自图片、聚合资料或关键词发现 | 仅研究队列，不得作为报告事实 |
| `candidate` | 公司身份和相关业务类别有官方材料，但 CPO/part 映射尚未充分核验 | 显示“候选”，不得写成确定供应关系 |
| `verified` | 映射有经审核的 Level A/B 证据，且角色、对象和时间范围明确 | 可进入比较页和结论引用 |
| `rejected` | 核验后不支持原映射 | 保留否定原因和审计记录 |
| `stale` | 原验证证据超过有效期或已被新披露改变 | 不得静默沿用，需复核 |

图片中出现公司名称只足以产生 `discovery`。同一公司可以对不同 part/chain node 分别拥有不同状态。

## 3. 全球产业锚点（8 家）

| company_id | 公司 | 市场/地区 | 候选研究角色 | 首要核验入口 | seed 状态 |
|---|---|---|---|---|---|
| `global.nvidia` | NVIDIA Corporation | NASDAQ / 美国 | AI 网络需求、交换平台、官方 photonics/CPO 信号 | NVIDIA Networking、官方发布、SEC filings | `candidate` |
| `global.broadcom` | Broadcom Inc. | NASDAQ / 美国 | 交换 ASIC、SerDes、CPO/光互连生态 | Broadcom switching 产品页、investor materials、SEC filings | `candidate` |
| `global.cisco` | Cisco Systems, Inc. | NASDAQ / 美国 | 网络系统、交换机、Acacia 光互连与开放生态 | Cisco 官方技术文章、产品资料、SEC filings | `candidate` |
| `global.intel` | Intel Corporation | NASDAQ / 美国 | 硅光平台、集成光学与封装路线 | Intel Silicon Photonics、官方发布、SEC filings | `candidate` |
| `global.marvell` | Marvell Technology, Inc. | NASDAQ / 美国 | 数据基础设施 ASIC、SerDes/光 DSP 与互连 | Marvell optical/DSP 产品资料、SEC filings | `candidate` |
| `global.coherent` | Coherent Corp. | NYSE / 美国 | 激光器、光器件、收发模块和制造生态 | Coherent networking 产品资料、SEC filings | `candidate` |
| `global.lumentum` | Lumentum Holdings Inc. | NASDAQ / 美国 | 激光器与光通信器件 | Lumentum optical communications 资料、SEC filings | `candidate` |
| `global.arista` | Arista Networks, Inc. | NYSE / 美国 | AI 数据中心交换系统与需求侧技术路线 | Arista 产品/白皮书、SEC filings | `candidate` |

全球锚点不等于供应商名单。例如，NVIDIA 的官方技术表述首先是 event/evidence，不能自动推出某家 A 股公司的供应关系。

## 4. A 股重点研究候选（12 家）

### 4.1 核心覆盖（优先完成公司详情，8 家）

| company_id | 公司（证券代码） | 候选业务类别 | 首批待核验 part/chain node | seed 状态 |
|---|---|---|---|---|
| `cn.300308` | 中际旭创股份有限公司（300308.SZ） | 高速光模块/光通信设备 | `optical-engine-package`、`systems-switches`；是否有明确 CPO 产品/收入 | `candidate` |
| `cn.300502` | 成都新易盛通信技术股份有限公司（300502.SZ） | 高速光模块 | `optical-engine-package`、`systems-switches`；CPO 与 pluggable 边界 | `candidate` |
| `cn.002281` | 武汉光迅科技股份有限公司（002281.SZ） | 光电子器件、模块及系统 | PIC/laser/receiver/optical connection 的实际产品边界 | `candidate` |
| `cn.300394` | 苏州天孚光通信股份有限公司（300394.SZ） | 光器件、精密耦合与封装 | `fiber.fau`、connector、source coupling；CPO 量产阶段 | `candidate` |
| `cn.000988` | 华工科技产业股份有限公司（000988.SZ） | 光电子器件与光模块 | laser/receiver/module 的产品和客户暴露 | `candidate` |
| `cn.603083` | 上海剑桥科技股份有限公司（603083.SH） | 高速光模块与网络设备 | optical engine/module；CPO 与传统模块的区分 | `candidate` |
| `cn.688498` | 陕西源杰半导体科技股份有限公司（688498.SH） | 光通信激光器芯片 | `laser.cw-array`/其他激光路线；是否适配 ELS/CPO | `candidate` |
| `cn.688048` | 苏州长光华芯光电技术股份有限公司（688048.SH） | 半导体激光芯片及器件 | laser source；数据通信/CPO 的产品适配与验证状态 | `candidate` |

### 4.2 链条补位（完成暴露核验后再决定是否升级为完整覆盖，4 家）

| company_id | 公司（证券代码） | 候选业务类别 | 首批待核验 part/chain node | seed 状态 |
|---|---|---|---|---|
| `cn.002916` | 深南电路股份有限公司（002916.SZ） | PCB、封装基板 | host PCB 与 CPA/package substrate 必须分别核验 | `discovery` |
| `cn.002463` | 沪士电子股份有限公司（002463.SZ） | 高速/高层 PCB | `board.high-speed-pcb`；不得由“AI PCB”直接推断 CPO | `discovery` |
| `cn.300602` | 深圳市飞荣达科技股份有限公司（300602.SZ） | 散热与电磁屏蔽材料/器件 | thermal/structure；需产品级 CPO 或交换系统证据 | `discovery` |
| `cn.688200` | 北京华峰测控技术股份有限公司（688200.SH） | 半导体测试设备 | test-equipment；需证明设备覆盖相关 PIC/EIC/光电测试环节 | `discovery` |

补位候选保留是为了暴露研究空白，不表示图片映射成立。若 Level A/B 材料不能支持 CPO 相关性，应转为 `rejected`，而不是为了覆盖十个产业链区域强行保留。

## 5. P1 seed 字段与验证队列

### Company seed

- `company_id`
- 法定/官方名称、英文名、证券代码、交易所、国家/地区
- `universe_layer`: `global_anchor` / `a_share_focus`
- `coverage_priority`: `context` / `core` / `gap_fill`
- 官方网站、交易所/监管披露入口
- `identity_verified_at`

### CompanyExposure seed

- `company_id`
- `part_id` 和/或 `chain_node_id`
- `role`: demand owner / platform vendor / chip vendor / component vendor / module vendor / substrate-PCB / thermal-structure / test-equipment / system vendor
- `status`: discovery / candidate / verified / rejected / stale
- `confidence`: low / medium / high
- `scope_note` 与明确时间范围
- supporting / contradicting evidence ids
- reviewer 与 reviewed_at

### 首批核验顺序

1. 用交易所/监管披露确认 12 家 A 股公司的身份、证券代码和最新年报。
2. 从最新年报中摘取“主营产品/业务”原文；不要先搜索“概念股”标签。
3. 对涉及 CPO、硅光、1.6T/3.2T、ELS、FAU、光引擎等具体表述，回到公司公告、业绩说明会或官网产品材料。
4. 分开记录“已有收入”“送样/验证”“研发”“规划/行业判断”，禁止合并成单一确定性暴露。
5. 至少寻找一条反证或边界信息，例如产品仍为 pluggable、客户未披露、尚未量产。
6. 只有通过 `docs/research-baseline/evidence-contract.md` 的审核门槛后，才将 exposure 升级为 `verified`。

## 6. 权威入口

- 巨潮资讯（深交所上市公司法定披露入口）：https://www.cninfo.com.cn/
- 上海证券交易所披露入口：https://www.sse.com.cn/disclosure/listedinfo/announcement/
- SEC EDGAR（美股公司法定披露）：https://www.sec.gov/edgar/search/
- NVIDIA Networking：https://www.nvidia.com/en-us/networking/
- Broadcom Ethernet Switching：https://www.broadcom.com/products/ethernet-connectivity/switching
- Cisco CPO 技术文章：https://blogs.cisco.com/sp/co-packaged-optics-and-an-open-ecosystem
- Intel Silicon Photonics：https://www.intel.com/content/www/us/en/architecture-and-technology/silicon-photonics/
- Marvell Optical DSP：https://www.marvell.com/products/optical-dsp.html
- Coherent Networking：https://www.coherent.com/networking
- Lumentum Datacom Transceivers：https://www.lumentum.com/en/optical-communications/products/datacom-transceivers
- Arista Platforms：https://www.arista.com/en/products/platforms

## 7. 明确排除

- 不按短期股价、涨跌幅或市场热度排名。
- 不把图片、券商聚合表、媒体转载或社交媒体名单当成供应关系证据。
- 不因公司拥有光模块、PCB、散热或测试业务就自动认定其拥有 CPO 暴露。
- 不推断未披露客户、订单、收入占比或量产时间。
- 不在 P0 扩大到港股/海外完整研究覆盖；海外公司仅作为全球锚点。
