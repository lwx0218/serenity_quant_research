# 入账 v2.1 服务器执行记录

## Metadata

- Project: serenity_quant_research
- Task: 入账 v2.1 上线、历史回填与 AI 原文判定
- Timestamp (UTC): 2026-09-29T15:24:31.989708+00:00
- Owner: Faye
- Route: direct-execute
- Source of truth: ops/README.md、docs/claude/teardown-accounting-v2.md
- Status: 回填与重算完成；AI 已判 16 / 21，5 条证据不足仍待核验

## 结果与边界

- 事件表 `is_sample=0`：**7 条**；这是数据库真实事件标识计数，不代表全部经过本轮原文审计。
- 本轮 AI 已实际交回 **16 条：入账 1、不算 15、接口错误 0**；两批分别 2 / 14 条，均小于 200。
- 原 21 条待办全部访问过原链接并补核，5 条仍证据不足，保留 open。未把无法访问或缺失关键段落伪装成拒绝，未宣称 AI 待办全部完成。
- 新入账 TSMC COUPE 200G 微环调制器生产与后续 400G 路线，归位 part.pic 而非 hint 的 DSP；未证明供货 NVIDIA 本型号。
- 行情截至 2026-09-29，144 / 144 家可取公司有行情；当前真事件远未达到 50 条目标。候选多不等于真事件多。

## 部署与异常处置

1. physical-first 从 56cb689 fast-forward 到 8b1c79d；Web build 通过；API venv 安装 pypdf 6.19.0。
2. 上线前执行全套 unittest 时暴露测试导入顺序隔离缺陷，误用生产 DB，events 从 18 变 39。已停止并经 Owner 明确许可恢复；恢复前验证 candidates/bars/ingest_runs/ingest_todo/margin/holders/valuation_daily 与备份无差异，保存误触后副本，持接入锁暂停本项目 systemd 服务后恢复、重启。显式临时 DB 验证 84 tests OK。此事故不能省略。
3. triage run47：**重开 391**（13 条规则入账 + 378 条规则例行），非旧说明中的 12；auto **0** / routine **396** / triage **19** / failed **0**。保留原有 AI 入账 5 条。
4. 原 backfill run48 在 1200 秒工具超时后中断，未写入回填候选，finished_at/ok 仍 NULL；没有虚构 fetched 或停在哪家公司。
5. 经 Owner 授权修复逐页持久化等问题，代码本地提交 de76110，95 项测试和 Web build 通过。后续回填固定使用归档隔离目录 de76110-run，不执行工作区未审代码。使用生产 SQR_DB_PATH 与现有 ingest.lock，开始前再次 SQLite backup。
6. 当前工作区其他可靠性修复及治理修改均不纳入本报告/快照的交付提交，不推代码。后续代码审查另行跟进。

## 回填计数

| 作业 | fetched | tagged | new | 完成情况 |
|---|---:|---:|---:|---|
| run50 全年 72 家 × 12 月 | 9299 | 9299 | 8938 | 1447 页；863/864 月段完成；22:17:55 结束，ok=0 |
| run51 太辰光 2025-10 补抓 | 35 | 35 | 5 | 4 页、1/1 月段，ok=1 |

- run50 唯一缺口：cn.300570 太辰光 2025-10 第4页 IncompleteRead；没有熔断，最后处理到 cn.920821 则成电子 2026-09 第1页。
- Owner 确认后 run51 仅重扫失败月份，前30条幂等去重，新增5条，失败月份已补齐。保留 run50 的失败事实，不改写成成功。
- 两轮请求计数合计9334（含重复扫描30）；跨两轮去重抓取/标记9304，新增候选合计 **8943**。
- 回填新增候选在 AI 判定前：规则入账1、例行8940、待AI2；不是8943条事件。

## AI 判定明细

已提交项如下。公开摘要判断与全文判断在 reason 中明确区分；不是对未读全文作绝对否定。

### cand.d8be3da8cdf5 — 入账

已读Semiconductor Engineering全文及Fig.6。TSMC投影片原文：World's first 200Gbps micro-ring modulator (MRM) with COUPE technology is in production；Continue scaling with 400Gbps modulator, multiple wavelengths, and multi-row Fiber Array Unit (FAU) to enable 4Tbps/mm by 2030。对应200G/lane硅光调制器及PIC路线，而非hint初判DSP；physical映射TSMC COUPE→part.pic为verified。日期取网页meta核验的报道披露日2026-09-29，不代表量产开始日；媒体转载投影片，未披露本模块客户、订单或产能规模。来源：https://semiengineering.com/tsmc-oip-chip-industry-growth-blows-past-forecast/

### cand.2d6d2965c91e — 当前不算

已读2页全文。本次进展为取得地契后变更泰国子公司注册地址，其他登记事项不变；没有PCB产线建设/投产、订单、认证、价格或技术路线的新事实，属土地及工商登记手续，非主PCB卡口事件。 原文第1—2页记载取得地契及注册地址变更。来源：http://static.cninfo.com.cn/finalpage/2026-09-21/1225575507.PDF

### cand.1721b4971aae — 当前不算

已读本公告8页全文，明确是尚待具体协议的初步合作意向，产品只到自主芯片/超低功耗光模块和AI算力场景；未给能够连接当前1.6T硅光部件链的速率、光源/PIC路线或确定建设内容。依据当前证据作“不算”，不等于否认光模块投资意向或未来事件；不要求点名NVIDIA客户/本型号。公司后续产品矩阵不倒灌本公告。 候选原文可见引文：本次签署的《光芯片、光模块研发和生产建设项目合作协议书》为双方投资合作达成的初步意向（原访问范围：full_pdf；http://static.cninfo.com.cn/finalpage/2025-12-17/1224883577.PDF） 补核引文：本次签署的《光芯片、光模块研发和生产建设项目合作协议书》为双方投资合作达成的初步意向（访问范围：full_pdf_already_read；http://static.cninfo.com.cn/finalpage/2025-12-17/1224883577.PDF）

### cand.fef1dde9ef66 — 当前不算

已读本公告3页全文，12.65亿元/2年建设期是具体扩产规划，不是因自筹资金而排除。但对象横跨无源/有源光芯片与器件，无CW激光器或本模块其他明确部件产品拆分。按当前证据不作为CW部件卡口入账；不是否认扩产存在，不要求点名NVIDIA。以后取得同项目产品拆分可重新判定，不能用不同金额的后续CW项目替代。 候选原文可见引文：项目主要内容：高速光芯片与器件的土地厂房及生产线建设、设备购置（原访问范围：full_pdf；http://static.cninfo.com.cn/finalpage/2026-04-18/1225122540.PDF） 补核引文：项目主要内容：高速光芯片与器件的土地厂房及生产线建设、设备购置（访问范围：full_pdf_already_read；http://static.cninfo.com.cn/finalpage/2026-04-18/1225122540.PDF）

### cand.0225c312086c — 当前不算

原媒体摘要明确VSMC新加坡厂开幕；中央社同日同厂完整报道将工艺界定为40—130nm特色工艺、汽车工业模拟/电源及先进封装interposer。不是hint中TSMC为1.6T光模块提供的3nm DSP逻辑代工；未见该项目与本模块电源等其他部件的特定供需关系，不能把所有电源芯片泛归模块电源。本次不算并非否认建厂。 候选原文可见引文：VSMC, the joint venture between Vanguard International Semiconductor (VIS) and NXP Semiconductors, officially opened its first 12-inch wafer fab in Singapore on September 28, completing construction in just 22 months.（原访问范围：summary_only_registration_wall；https://www.digitimes.com/news/a20260929PD212/fab-tsmc-joint-venture-12-inch-vis.html） 补核引文：The fab will manufacture chips using mature specialty processes ranging from 40nm to 130nm, including embedded flash memory, power management and analog chips for automotive and industrial applications, VSMC said.（访问范围：full_same_event_news；https://focustaiwan.tw/business/202609280015）

### cand.ba47fb5095c4 — 当前不算

补读三星电机同投资公告全文，扩产对象为AI加速器/GPU/CPU封装用FCBGA基板；不是NVIDIA OSFP笼子/连接器，也未提供本光模块主PCB或其他部件的项目关系。供给变动真实，但原hint公司与部件归位不成立。 候选原文可见引文：Samsung Electro-Mechanics said it will invest KRW6.78 trillion (about US$5 billion) in South Korea and Vietnam to expand ABF substrate production for AI servers and high-performance computing (HPC) markets...（原访问范围：summary_only_registration_wall；https://www.digitimes.com/news/a20260929PD231/semco-abf-substrate-nvidia-capacity-production.html） 补核引文：FCBGA is a highly integrated semiconductor substrate that connects high-performance semiconductors such as AI accelerators, GPUs, and CPUs to the mainboard, supplying electrical signals and power.（访问范围：full_official_same_event；https://www.samsungsem.com/global/newsroom/news/view.do?id=10562）

### cand.2438b784b582 — 当前不算

原媒体仅摘要，但明确是CUDA-Q Logical；补读NVIDIA同名产品发布完整正文，系容错量子计算软件编排、算法与基准工具。正文另提NVQLink生态，未给OSFP连接器、1.6T光模块或其部件的产能/订单/认证/价格/路线新事实；不能把量子GPU互联的一般背景等同主机笼子卡口。 候选原文可见引文：Nvidia expanded its open-source CUDA-Q platform with CUDA-Q Logical, an orchestration layer aimed at helping researchers build software for fault-tolerant quantum computers...（原访问范围：summary_only_registration_wall；https://www.digitimes.com/news/a20260929PD211/nvidia-software-hardware-data.html） 补核引文：NVIDIA today announced an expansion of the NVIDIA CUDA-Q™ open source platform with CUDA-Q Logical, an orchestration layer that provides a programmable, verifiable approach to developing useful applications for fault-tolerant quantum computers.（访问范围：full_official_release；https://nvidianews.nvidia.com/news/nvidia-expands-open-source-cuda-q-platform-for-fault-tolerant-quantum-computing）

### cand.e4c39ea7d974 — 当前不算

已读前轮原页公开长片段12041字符，不宣称全文；作者在可见段明确将主题定义为六类表外担保/信贷支持与残值担保的融资分析，供货承诺亦标明主要为存储器。按规格融资安排/泛产业资金支持不作为光模块部件卡口，当前不算；这是对可见候选事件范围的判定，并非宣称全文不存在其他内容或相关需求。 候选原文可见引文：We will now explore how this support could evolve in detail – walking the six off-balance sheet obligation lines in the recent quarter’s disclosure, plus a new one we have created to track residual value guarantees under the capital partnership.（原访问范围：partial_article_completeness_unverified；https://newsletter.semianalysis.com/p/nvidias-backstop-universe-heads-i） 补核引文：We will now explore how this support could evolve in detail – walking the six off-balance sheet obligation lines in the recent quarter’s disclosure, plus a new one we have created to track residual value guarantees under the capital partnership.（访问范围：prior_public_excerpt_12041_chars_not_full；https://newsletter.semianalysis.com/p/nvidias-backstop-universe-heads-i）

### cand.9e4111c0b7c2 — 当前不算

原可见摘要与The Elec完整现场报道均明确这次代工产品是Snapdragon 8 Elite Gen6标准和Extreme手机/平板应用处理器，而非光模块PAM4 DSP。两公司虽在实物映射中，不能把所有2nm代工订单归为该DSP；本事件当前不算。 候选原文可见引文：Qualcomm is sticking with TSMC for both of its newly launched 2nm Snapdragon flagship processors, extending the Taiwan foundry's hold on Qualcomm's top-tier mobile chips even as Samsung Electronics ramps its second-generation 2nm process and steps up efforts...（原访问范围：summary_only_registration_wall；https://www.digitimes.com/news/a20260924VL210/qualcomm-tsmc-snapdragon-samsung-2nm.html） 补核引文：The application processors (APs), which serve as the brains of mobile devices such as smartphones and tablet PCs, are used in flagship devices from major smartphone makers.（访问范围：full_same_event_news；https://www.thelec.net/news/articleView.html?idxno=14172）

### cand.8e67c81691a9 — 当前不算

仅取得原页公开og:description（非完整正文），内容明确为DGX Spark桌面/家庭本地AI计算的定位与趋势讨论；不是光模块、OSFP主机互联或其部件的新产能/订单/认证/价格/技术路线事实。按这条候选公开界定的事件范围当前不算，不将检索出的其他日期DGX发布当作本新闻，也不声称正文无其他内容。 补核引文：Nvidia is positioning its newest personal AI system as more than a developer tool. By putting DGX Spark on desks and, eventually, in homes, the company is signaling that the next phase of AI computing may rely less on remote data centers and more on local machines.（访问范围：public_meta_only_not_article_body；https://www.digitimes.com/news/a20260924PD208/nvidia-data.html）

### cand.1368e65cc8f7 — 当前不算

原媒体正文仍未取得，但其公开og:description已读，明确说明MIPS完成ARC整合，围绕RISC-V physical AI及处理器IP拓展汽车/数据中心；GF官网完整背景访谈也界定其为RISC-V处理器与边缘系统。此处是处理器IP业务整合与市场定位，不是Fotonix硅光PIC供给/路线事实；仅据公开摘要及范围核对作当前不算，不伪称读到媒体全文。 候选原文可见引文：Sorry, unusual traffic from your computer network.（原访问范围：access_denied；https://www.digitimes.com/news/a20260929PD220/mips-globalfoundries-risc-v-data-ip.html） 补核引文：MIPS, a GlobalFoundries (GF) unit, said it has completed its integration with the ARC unit acquired from Synopsys earlier this year and is using the move to position RISC-V for physical AI, while expanding from AIoT into automotive and data center applications. MIPS said the strategy lowers the barrier for global customers to adopt GF platforms across process technologies and has pushed GF and MIPS to become the world's second-largest processor IP provider.（访问范围：public_meta_only_not_article_body；https://www.digitimes.com/news/a20260929PD220/mips-globalfoundries-risc-v-data-ip.html）

### cand.2068ffa5e930 — 当前不算

仅据原页公开og:description，第二部分是前TSMC高管回顾CoWoS如何由实验室概念变为业界标准，属于历史封装技术发展访谈；没有当前这只硅光模块部件供需/价格/路线的可核验新变化，当前不算。未取得完整采访，不主张全文绝无硅光内容；也不能把新发布访谈日期当历史技术突破发生日。 候选原文可见引文：As chip design enters the AI era, heterogeneous integration is driving foundry giants like TSMC, Samsung, and Intel to bring advanced front-end fab capabilities into back-end packaging.（原访问范围：summary_only_registration_wall；https://www.digitimes.com/news/a20260924PD238/tsmc-packaging-cowos-design-silicon.html） 补核引文：As chip design enters the AI era, heterogeneous integration is driving foundry giants like TSMC, Samsung, and Intel to bring advanced front-end fab capabilities into back-end packaging. In the second part of his interview with , Dr. Shin-Puu Jeng, chairman of IMAPS and a former TSMC executive, shared how TSMC transformed CoWoS from a niche lab concept into an industry standard.（访问范围：public_meta_only_not_article_body；https://www.digitimes.com/news/a20260924PD238/tsmc-packaging-cowos-design-silicon.html）

### cand.22a78d8ac959 — 当前不算

仅据原页公开og:description，第一部分明确回顾CoWoS早期薄中介层危机与TSMC/Xilinx的历史创新。不是当前光模块DSP或PIC的新供给/订单/路线变化，当前不算；未读完整采访，不将零良率历史危机记成2026年当期事件。 候选原文可见引文：In a recent interview on the DIGITIMES podcast, Dr. Shin-Puu Jeng, chairman of the International Microelectronics and Packaging Society (IMAPS) and a former longtime TSMC advanced packaging executive, reflected on the early development of CoWoS...（原访问范围：summary_only_registration_wall；https://www.digitimes.com/news/a20260924PD236/tsmc-xilinx-digitimes-cowos-silicon.html） 补核引文：In a recent interview on the  podcast, Dr. Shin-Puu Jeng, chairman of the International Microelectronics and Packaging Society (IMAPS) and a former longtime TSMC advanced packaging executive, reflected on the early development of CoWoS. In the first of this two-part series, Jeng details how a critical thin-interposer crisis forced TSMC and Xilinx to innovate, laying the foundation for modern advanced packaging.（访问范围：public_meta_only_not_article_body；https://www.digitimes.com/news/a20260924PD236/tsmc-xilinx-digitimes-cowos-silicon.html）

### cand.788df8c595cb — 当前不算

原媒体仅峰会会谈摘要；同场同两方发布的Business Wire公开转载完整正文，明确是Hexagon NPU上的本地个人上下文及端侧Agent软件。产品对象不是1.6T光模块PAM4 DSP，当前不算；不声称取得媒体会谈全文。 候选原文可见引文：Qualcomm Technologies held its Snapdragon Summit 2026 in Maui, Hawaii, from September 22 to 24. During the keynote on the second day, Qualcomm president and CEO Cristiano Amon spoke with co-founder and CEO of Liquid AI Ramin Hasani.（原访问范围：summary_only_registration_wall；https://www.digitimes.com/news/a20260925PD200/qualcomm-snapdragon-on-device-ai-2026-ceo.html） 补核引文：Liquid AI today, at Snapdragon Summit 2026, announced that Liquid Context, an on-device context layer, is now optimized for Snapdragon® processors, specifically using the Qualcomm® Hexagon™ NPU.（访问范围：full_press_release_republication；https://markets.financialcontent.com/ms.intelvalue/article/bizwire-2026-9-23-liquid-ai-in-collaboration-with-qualcomm-technologies-brings-personal-ai-context-to-devices-powered-by-snapdragon）

### cand.c6635a576c4f — 当前不算

补读三星官网同日同金额Helix投资公告完整正文，事件为六家三星公司对Helix合计10亿美元资本投资，NVIDIA仅列为共同创始投资人。Helix覆盖数据中心/电力/光纤网络，但未形成NVIDIA光模块或OSFP部件订单/认证/供给变化；按规格融资股权类不算，不否认基础设施需求背景。 候选原文可见引文：Sorry, unusual traffic from your computer network.（原访问范围：access_denied；https://www.digitimes.com/news/a20260929VL201/samsung-data-center-nvidia-data-investment.html） 补核引文：Samsung Electronics, Samsung C&T, Samsung SDS, Samsung SDI, Samsung Life Insurance and Samsung Fire & Marine Insurance today announced they are investing a combined USD 1 billion in Helix Digital Infrastructure, an AI infrastructure company established by global investment firm KKR.（访问范围：full_official_same_event；https://news.samsung.com/global/samsung-to-invest-usd-1-billion-in-ai-infrastructure-company-helix）

### cand.d4fd8832a9f2 — 当前不算

仅据原报道可见摘要，事件已明确界定为GaN代工扩产/TSMC退出，而非硅光PIC或逻辑DSP；GF官方旧技术许可全文辅助确认GaN为650V/80V功率器件，不能用其替代本次扩产细节。本次证据没有连接到本模块的具体电源部件，因此当前不算；不否认GaN扩产或未来光模块应用。 候选原文可见引文：GlobalFoundries (GF) is preparing a major global capacity expansion as TSMC is set to gradually exit gallium nitride (GaN) foundry services in 2027...（原访问范围：summary_only_registration_wall；https://www.digitimes.com/news/a20260929PD215/globalfoundries-gan-tsmc-expansion-capacity-expansion.html） 补核引文：This strategic move will accelerate GF’s next generation of GaN products for datacenter, industrial and automotive power applications and provide U.S.-based GaN capacity for a global customer base.（访问范围：full_official_background_prior_event；https://gf.com/news-and-events/news/globalfoundries-licenses-gan-technology-from-tsmc-to-accelerate-u-s-manufactured-power-portfolio-for-datacenter-industrial-and-automotive-custo/）

## 剩余 5 条待核验（仍 open，未提交 false）

- **cand.7b717ddd7e68**（todo 99）：原摘要确为同5亿美元台湾项目；公开旧项目公告已提Quantum InfiniBand且超链接指向X800，不能草率判成完全无关。但2025-11项目发布不能冒充2026-09访谈的新订单/新增产能；未取得访谈正文以判断是否有新变化，继续blocked。 下一步：需2026-09访谈完整原文或与访谈同步的项目新增订单/交付进展；2025-11项目公告不能直接定为2026-09新事件。
- **cand.6764c74eb530**（todo 38）：同文标题/同期官方活动/产品发布多角度检索后，当前仅取得原页公开元描述的AI开支与测试背景；两处Keysight官方页面均403。检索结果指向早期不同产品发布及会议，不能替换这篇候选。因为测试厂商可能有1.6T具体进展但本段未揭示，继续blocked。 下一步：取得该采访/文章公开全文或作者同文公开发布，核对是否有新1.6T测试产品/客户导入；其他年度产品不替代。
- **cand.de9bb5e0d45d**（todo 46）：Reuters同事件公开全文已读，证明报道对象是Broadcom交换机使用情况调查，并称可能发布非正式采购指引，Reuters未独立核实。不是确认禁售/订单减少，也未交代涉及的网络代际和模块采购变化；不能因存在高端交换机映射就把未落地调查当成已发生1.6T部件供需变化，保留blocked。 下一步：补Broadcom具体产品范围及实际采购限制/订单变动的可靠原文；目前Reuters明确未独立核实且仅称可能发布指引。
- **cand.92965351a8a3**（todo 64）：原页公开og:description补充完整导语后明确同会讨论还包括optical interconnects，不能只凭HBM标题拒绝。主办方页面仅议程/讲者，不是具体技术结果；未取得报道中光互联与ASMPT关系及是否新变化的细节，继续blocked。 下一步：补同文章光互联段或ASMPT同会议公开讲话原文，核对是否涉及光引擎组装的新设备/工艺/客户。
- **cand.cb3c63e4a584**（todo 68）：检索同题并查主办方同会议资料；可见摘要仅列会议与封装议题，主办方页面是议程/讲者资料而非讲话或报道全文，同会另含硅光议题，不能用HBM标题或泛会议摘要排除正文可能的光引擎进展。未取得足够同文事实，保留blocked。 下一步：补同文章具体技术/人才讨论段或主办方同场完整记录，不能以会议名单判断技术新事件。

待办有7天作废机制；没有修改或延长有效期，后续需在有效期内补证，过期不等于事件不存在。

## 重算与快照验证

- 固定 de76110 隔离代码运行 recompute；结果如下。
- 同版本 snapshot/build.py 对 http://127.0.0.1:8000 构建：835 个内嵌响应，约2.5 MB，无 skip。
- Chromium 实际打开交互 HTML 并点击“研究”：页面正常、console clean；页面显示真事件7、待AI5。快照只模拟交互，不写生产库。
- 产物：physical/dist/teardown-web-snapshot.html。

```text
2026-09-29T23:22:39 run 52 recompute 开始
2026-09-29T23:22:39 recompute 开始 series / reactions / valuation
2026-09-29T23:22:41 recompute 开始 crowding
2026-09-29T23:22:42 recompute 完成
2026-09-29T23:22:42 run 52 recompute 完成 ok=True
{
 "run_id": 52,
 "job": "recompute",
 "ok": true,
 "summary": {
  "instruments": 168,
  "points": 88994,
  "product_members": 73,
  "reactions": 12,
  "valuation": 73,
  "as_of": "2026-09-29",
  "crowding": 168
 },
 "error": null
}
```

## /api/ingest/status 全文

以下为重算后的完整响应（含历史未收尾任务，不作隐瞒或篡改）：

```json
{
  "as_of": "2026-09-29",
  "sample": false,
  "companies": 165,
  "quotable": 144,
  "with_bars": 144,
  "last_bar_date": "2026-09-29",
  "with_margin": 72,
  "with_valuation": 73,
  "events": {
    "real": 7,
    "sample": 0
  },
  "candidates": {
    "confirmed": 7,
    "pending": 5,
    "rejected": 9370,
    "pending_relevant": 5
  },
  "accounting": {
    "total": 9382,
    "accounted": 7,
    "by_rule": 1,
    "by_ai": 6,
    "by_human": 0,
    "to_ai": 5,
    "routine": 9336,
    "not_counted": 34,
    "dismissed_by_human": 0,
    "backfill": 8943,
    "backfill_accounted": 1,
    "expired": 0,
    "unprocessed": 0
  },
  "last_news_fetch": "2026-09-29T22:40:51",
  "todo_open": 0,
  "runs": [
    {
      "id": 52,
      "job": "recompute",
      "started_at": "2026-09-29T23:22:39",
      "finished_at": "2026-09-29T23:22:42",
      "ok": 1,
      "summary": {
        "instruments": 168,
        "points": 88994,
        "product_members": 73,
        "reactions": 12,
        "valuation": 73,
        "as_of": "2026-09-29",
        "crowding": 168
      },
      "error": null
    },
    {
      "id": 51,
      "job": "backfill",
      "started_at": "2026-09-29T22:40:42",
      "finished_at": "2026-09-29T22:40:57",
      "ok": 1,
      "summary": {
        "fetch": {
          "new": 5,
          "merged": 0,
          "seen": 35,
          "fetched": 35,
          "tagged": 35,
          "pages": 4,
          "segments_ok": 1,
          "segments_failed": 0,
          "last_position": {
            "company_id": "cn.300570",
            "company": "太辰光",
            "since": "2025-10-01",
            "until": "2025-10-31",
            "page": 4
          },
          "failures": [],
          "since": "2025-10-01",
          "until": "2025-10-31",
          "companies": 1,
          "segments": 1,
          "companies_ok": 1,
          "companies_failed": 0,
          "stopped": false,
          "complete": true
        },
        "relevance": {
          "relevant": 196,
          "routine": 9186
        },
        "accounting": {
          "auto": 0,
          "routine": 5,
          "triage": 21,
          "failed": 0
        },
        "backfill": {
          "confirmed": 1,
          "pending": 2,
          "rejected": 8940
        },
        "summary": {
          "total": 9382,
          "accounted": 6,
          "by_rule": 1,
          "by_ai": 5,
          "by_human": 0,
          "to_ai": 21,
          "routine": 9336,
          "not_counted": 19,
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
      "id": 50,
      "job": "backfill",
      "started_at": "2026-09-29T21:18:05",
      "finished_at": "2026-09-29T22:17:55",
      "ok": 0,
      "summary": {
        "fetch": {
          "new": 8938,
          "merged": 0,
          "seen": 9299,
          "fetched": 9299,
          "tagged": 9299,
          "pages": 1447,
          "segments_ok": 863,
          "segments_failed": 1,
          "last_position": {
            "company_id": "cn.920821",
            "company": "则成电子",
            "since": "2026-09-01",
            "until": "2026-09-29",
            "page": 1
          },
          "failures": [
            {
              "company_id": "cn.300570",
              "company": "太辰光",
              "since": "2025-10-01",
              "until": "2025-10-31",
              "page": 4,
              "error": "IncompleteRead: IncompleteRead(597 bytes read)"
            }
          ],
          "since": "2025-10-01",
          "until": "2026-09-29",
          "companies": 72,
          "segments": 12,
          "companies_ok": 71,
          "companies_failed": 1,
          "stopped": false,
          "complete": false
        },
        "relevance": {
          "relevant": 196,
          "routine": 9181
        },
        "accounting": {
          "auto": 1,
          "routine": 8935,
          "triage": 21,
          "failed": 0,
          "reactions": 12
        },
        "backfill": {
          "confirmed": 1,
          "pending": 2,
          "rejected": 8935
        },
        "summary": {
          "total": 9377,
          "accounted": 6,
          "by_rule": 1,
          "by_ai": 5,
          "by_human": 0,
          "to_ai": 21,
          "routine": 9331,
          "not_counted": 19,
          "dismissed_by_human": 0,
          "backfill": 8938,
          "backfill_accounted": 1,
          "expired": 0,
          "unprocessed": 0
        }
      },
      "error": "回填不完整；已提交页保留，请查看 summary.fetch 和日志后重跑"
    },
    {
      "id": 49,
      "job": "news",
      "started_at": "2026-09-29T21:15:01",
      "finished_at": "2026-09-29T21:15:02",
      "ok": 1,
      "summary": {
        "new": 0,
        "merged": 0,
        "seen": 0,
        "triage": {
          "relevant": 56,
          "routine": 383
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 19,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 48,
      "job": "backfill",
      "started_at": "2026-09-29T20:07:12",
      "finished_at": null,
      "ok": null,
      "summary": null,
      "error": null
    },
    {
      "id": 47,
      "job": "triage",
      "started_at": "2026-09-29T20:06:46",
      "finished_at": "2026-09-29T20:06:46",
      "ok": 1,
      "summary": {
        "rejudged": 391,
        "relevance": {
          "relevant": 56,
          "routine": 383
        },
        "auto": 0,
        "routine": 396,
        "triage": 19,
        "failed": 0,
        "summary": {
          "total": 439,
          "accounted": 5,
          "by_rule": 0,
          "by_ai": 5,
          "by_human": 0,
          "to_ai": 19,
          "routine": 396,
          "not_counted": 19,
          "dismissed_by_human": 0,
          "backfill": 0,
          "backfill_accounted": 0,
          "expired": 0,
          "unprocessed": 0
        }
      },
      "error": null
    },
    {
      "id": 46,
      "job": "news",
      "started_at": "2026-09-29T18:15:01",
      "finished_at": "2026-09-29T18:17:19",
      "ok": 1,
      "summary": {
        "new": 16,
        "merged": 1,
        "seen": 311,
        "triage": {
          "relevant": 61,
          "routine": 378
        },
        "accounting": {
          "auto": 1,
          "routine": 13,
          "triage": 24,
          "failed": 0,
          "reactions": 22
        }
      },
      "error": null
    },
    {
      "id": 45,
      "job": "recompute",
      "started_at": "2026-09-29T17:22:17",
      "finished_at": "2026-09-29T17:22:20",
      "ok": 1,
      "summary": {
        "instruments": 168,
        "points": 88994,
        "product_members": 73,
        "reactions": 22,
        "valuation": 73,
        "as_of": "2026-09-29",
        "crowding": 168
      },
      "error": null
    },
    {
      "id": 44,
      "job": "recompute",
      "started_at": "2026-09-29T17:21:43",
      "finished_at": "2026-09-29T17:21:45",
      "ok": 1,
      "summary": {
        "instruments": 164,
        "points": 87359,
        "product_members": 70,
        "reactions": 19,
        "valuation": 73,
        "as_of": "2026-09-29",
        "crowding": 164
      },
      "error": null
    },
    {
      "id": 43,
      "job": "recompute",
      "started_at": "2026-09-29T16:45:40",
      "finished_at": "2026-09-29T16:45:42",
      "ok": 1,
      "summary": {
        "instruments": 164,
        "points": 87359,
        "product_members": 70,
        "reactions": 11,
        "valuation": 73,
        "as_of": "2026-09-29",
        "crowding": 164
      },
      "error": null
    },
    {
      "id": 42,
      "job": "triage",
      "started_at": "2026-09-29T16:45:37",
      "finished_at": "2026-09-29T16:45:40",
      "ok": 1,
      "summary": {
        "relevance": {
          "relevant": 58,
          "routine": 365
        },
        "auto": 12,
        "routine": 365,
        "triage": 46,
        "failed": 0,
        "reactions": 11,
        "summary": {
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
        }
      },
      "error": null
    },
    {
      "id": 41,
      "job": "daily",
      "started_at": "2026-09-29T16:15:42",
      "finished_at": null,
      "ok": null,
      "summary": null,
      "error": null
    },
    {
      "id": 40,
      "job": "daily",
      "started_at": "2026-09-29T15:35:01",
      "finished_at": "2026-09-29T16:10:26",
      "ok": 1,
      "summary": {
        "quotes": {
          "companies_ok": 139,
          "companies_failed": 5,
          "unquotable": 21,
          "rows": 1104
        },
        "inputs": {
          "companies_ok": 74,
          "companies_failed": 0
        },
        "valuation": {
          "companies_ok": 73,
          "companies_failed": 1
        },
        "recompute": {
          "instruments": 163,
          "points": 86828,
          "product_members": 70,
          "reactions": 0,
          "valuation": 73,
          "as_of": "2026-09-29",
          "crowding": 163
        }
      },
      "error": null
    },
    {
      "id": 39,
      "job": "news",
      "started_at": "2026-09-29T15:15:01",
      "finished_at": "2026-09-29T15:17:34",
      "ok": 1,
      "summary": {
        "new": 3,
        "merged": 11,
        "seen": 299,
        "triage": {
          "relevant": 58,
          "routine": 365
        }
      },
      "error": null
    },
    {
      "id": 38,
      "job": "news",
      "started_at": "2026-09-29T12:15:01",
      "finished_at": "2026-09-29T12:17:15",
      "ok": 1,
      "summary": {
        "new": 12,
        "merged": 3,
        "seen": 300,
        "triage": {
          "relevant": 55,
          "routine": 365
        }
      },
      "error": null
    },
    {
      "id": 37,
      "job": "news",
      "started_at": "2026-09-29T09:15:01",
      "finished_at": "2026-09-29T09:17:23",
      "ok": 1,
      "summary": {
        "new": 8,
        "merged": 0,
        "seen": 293,
        "triage": {
          "relevant": 43,
          "routine": 365
        }
      },
      "error": null
    },
    {
      "id": 36,
      "job": "news",
      "started_at": "2026-09-29T06:15:01",
      "finished_at": "2026-09-29T06:16:56",
      "ok": 1,
      "summary": {
        "new": 1,
        "merged": 0,
        "seen": 286,
        "triage": {
          "relevant": 35,
          "routine": 365
        }
      },
      "error": null
    },
    {
      "id": 35,
      "job": "news",
      "started_at": "2026-09-29T03:15:01",
      "finished_at": "2026-09-29T03:16:56",
      "ok": 1,
      "summary": {
        "new": 2,
        "merged": 2,
        "seen": 287,
        "triage": {
          "relevant": 34,
          "routine": 365
        }
      },
      "error": null
    },
    {
      "id": 34,
      "job": "news",
      "started_at": "2026-09-29T00:15:01",
      "finished_at": "2026-09-29T00:17:32",
      "ok": 1,
      "summary": {
        "new": 2,
        "merged": 38,
        "seen": 285,
        "triage": {
          "relevant": 32,
          "routine": 365
        }
      },
      "error": null
    },
    {
      "id": 33,
      "job": "news",
      "started_at": "2026-09-28T21:15:01",
      "finished_at": "2026-09-28T21:17:45",
      "ok": 1,
      "summary": {
        "new": 42,
        "merged": 11,
        "seen": 294,
        "triage": {
          "relevant": 32,
          "routine": 363
        }
      },
      "error": null
    }
  ]
}
```
