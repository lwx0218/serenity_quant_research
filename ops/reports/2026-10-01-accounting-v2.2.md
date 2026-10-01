# 入账 v2.2 执行报告（10-01任务，跨日交付）

## Metadata

- Project: serenity_quant_research
- Task: v2.2 部署、正文重判、AI核验、重算与真数据快照
- Timestamp (UTC): 2026-10-01T16:30:30+00:00
- Owner: Faye
- Route: direct-execute
- Source of truth: Owner 本会话指令；docs/claude/teardown-review-2026-09-29-real-data.md §4–§5
- Status: 已完成本批可核验候选入账、重算与快照；**9条待核验仍未闭环，不宣称全部完成**

## 1. 结果

- 真事件总数 **27**（AI **26** + 规则 **1**；示例0），本次新增 **23**，之前4条保留。历史回填事件 **24**。
- AI本次实际提交 **56条**：**算23、不算33、接口错误0**，分3批（52 / 2 / 2），均≤200。回读状态及正例part_id、thesis、confidence已核对。
- triage run72 交AI **62条**：本轮处理其中53条（算22、不算31），尚余9条；另补原始公告候选1条算（中瓷）以及并发news新增2条不算。因此不要把56条提交当作62条已全部处理。
- 正文读取：run72 **尝试313，取到306，未取到7**，基线body_at=0。取到指取得前1500字进入summary，不等于AI全文核验。后续news run73另取正文2条；截至快照全库body_at=315、摘要非空308、空7。
- 最新重算 run75 成功，168条序列、89,158点、100条反应记录；行情截至 **2026-09-30**，不能写成10-02行情。
- n≥5的部件目前为PCB（12）与整模块（5），**仅表示事件数量达到门槛，不代表部件效力已算出或因果验收通过**；距离50条真事件目标尚差23。

## 2. 同步与保护

- 拉取并部署 `309531a`（v2.2）；此前 `de76110` 已经CC合并。
- Owner 明确批准先备份暂存冲突工作区。旧修改保存在 `stash@{0}`（pre-v2.2-owner-approved-2026-10-01），**未恢复、未混入部署或提交**。
- 原补丁、同名旧报告、部署前生产SQLite备份在 `artifacts/runtime/accounting-v2.2/`。提交前另留 `before-ai-judge.sqlite`。
- `ops/reports/2026-10-01-backfill-rule-rejected-title-screen.md` 已以 **4e7da18** 提交推送：命中239，样本30。
- `cd web && npm run build` 成功；`teardown-api.service` 已重启；运行venv确认 `pypdf 6.19.0`。
- `POST /api/ingest/run/triage` 后台run72，自10-01 22:45:22至23:06:35，**21分13秒**，没有同步长工具超时中断。
- 旧5条（微软/A14/HBM5拒绝、亨通FAU/汇绿整模块保留）已回读，9月30日重判字段完整，本次不重复判。
- 最初四组核验未落盘且无法查询，随后恢复任务并复用已下载证据；本报告只计已实际提交与回读的数据，不把启动子任务当完成。

## 3. 判定与父会话复核

以原文与产品族为准，不要求点名NVIDIA本型号；混合用途或未拆分产能给予2–3分，不将总投资全部当该部件产能。计划、已投产、试样研发分别写明。

- 核对同项目：沪利微电55亿元8月改址为既有项目跟踪，不重复入账；腾景子公司登记也不重复扩产。东山12→17亿美元为同项目新增5亿美元的实质变更，记录增量而不是新17亿美元。
- 中瓷：8月回顾不能用4/29董事会日充当公开日。补查原巨潮公告2026-037第25–27页及发布路径，以 **4/30原候选 cand.03076632549b** 入账；8月回顾 cand.396605f72a15 判不算（重复），避免同一事实计两次。
- 天孚：已找到2025-11-27投关原文表明早已量产交付；4/8回顾不是新催化，首次公开日仍需追溯，留待核验。
- GF：撤回仅凭9/30扩张导语的低置信正例建议，2025官方源只能证明产品族，不能证明9月新事件；留待核验。
- 部分付费媒体只读到公开导语；判断限于可见的HBM、PC、人事等明确无关对象，不声称全文访问。关键事实或时点不足的保留待核验。
- 华盛昌评估报告为扫描件，已渲染核对封面与摘要，确认股权价值评估目的；不声称读完51页。其他评估类同样在理由中注明实际阅读范围。
- 同期新候选：致尚5亿美元MPO需求预测备忘录明确无强制约束、待正式订单，本次不当确定订单入账；EE Times通用制程营收历史比较也不算模块卡口。

## 4. 按部件的真事件分布

统计：`events.is_sample=0 AND status!='ignored'`，按显式 `part_id` 汇总，无未归位事件；这是全历史入账数，不是365天可计算效力样本数。

|部件 ID|部件|事件数|
|---|---|---:|
|`part.pcb`|主 PCB（高速多层板）|12|
|`part.module-maker`|整模块：组装、测试、客户|5|
|`part.cw-laser`|CW 激光器（外置光源）|3|
|`part.fau`|光纤阵列单元（FAU）|2|
|`part.laser-coupling`|光源耦合：隔离器 / 透镜 / 保偏光纤|1|
|`part.lid-thermal`|顶盖 / 散热与 TIM|1|
|`part.mpo`|MPO 插座与 MT 插芯|1|
|`part.pic`|硅光 PIC（调制器 + 波导 + 分束）|1|
|`part.shell`|OSFP 壳体 / 拉环 / EMI|1|
|`part.driver`|调制器驱动器（Driver）|0|
|`part.dsp`|DSP（重定时芯片）|0|
|`part.edge-fingers`|金手指|0|
|`part.engine-assembly`|光引擎组装（COB / 倒装 / 耦合）|0|
|`part.host-cage`|主机侧 OSFP 笼子 / 连接器|0|
|`part.pd`|Ge 光电探测器（PD）|0|
|`part.power-mgmt`|电源 / MCU / 存储|0|
|`part.tia`|跨阻放大器（TIA）|0|

## 5. 9条待核验（保持pending/open，未伪装拒绝）

- **cand.4a48b04c390b** 天孚通信：关于“质量回报双提升”行动方案的进展公告：撤回2026-04-08 qualification判定：原公告只是2025年度量产回顾。补取公司2025-11-27投关记录原文第1页已明确具备800G及1.6T量产能力、第2页已正常交付，足以排除4/8为新催化；未确定首次公开日，不能把11/27擅当首次，暂不入账。需追溯更早正式披露并排除旧事件重复。 [原文](http://static.cninfo.com.cn/finalpage/2026-04-08/1225082727.PDF)
- **cand.c1af7046eca3** 中天科技：江苏中天科技股份有限公司关于中标互联网企业数据中心用耗材项目的公告：第1页确证15.18亿元数据中心MPO跳线及配件订单，事实属于part.mpo而非整模块；mode=ro查physical_part_companies中天只有part.module-maker映射。不能为过接口错归模块，需父代理解决MPO映射/归位合同后再判；不改事实JSON/DB。 [原文](http://static.cninfo.com.cn/finalpage/2026-06-06/1225353680.PDF)
- **cand.ef60584f9572** 华兴源创：华兴源创：公司收购武汉普赛斯电子股份有限公司股权涉及的其股东全部权益价值追溯评估项目资产评估报告：本轮未继续下载26MB评估报告，已补取同日2页原公告1225434650（2026-044）全文：2.0616亿元收购普赛斯39%股权、合计51%，完成付款及工商变更，所载是股权事项而非供给/订单节点。但它并非候选1225434649评估报告全文，不能据替代公告断言评估报告没有独立经营事实，故候选仍unresolved；原大PDF继续标记不完整。 [原文](http://static.cninfo.com.cn/finalpage/2026-07-22/1225434649.PDF)
- **cand.7b717ddd7e68** Interview: GMI Cloud bets on Taiwan as a proving ground for global AI expansion：媒体只开放GMI台湾5亿美元AI工厂导语。已读GMI正式新闻稿（PRNewswire，2025-11-17），确实明确Quantum InfiniBand/Spectrum-X，不只是GPU需求；但该事实是2025年公告，不能伪装成2026-09-25新订单/新产能。需采访全文核对本次增量，或父代理明确将该候选改作2025-11-17历史事实并全库去重后再判。 [原文](https://www.digitimes.com/news/a20260921VL212/taiwan-cloud-infrastructure-data-center-investment.html)
- **cand.6764c74eb530** Keysight pushes design-to-deployment standard for AI cluster validation：DIGITIMES返回Access denied；Keysight官方AI Scale Out及9月9日ECOC公告返回403。搜索提示1.6T端到端测试可能相关，但未读到公告正文且不能确认与9月27日候选是同一产品/新交付事实；保留待核，不以泛集群宣传拒绝，也不用其它日期展示替代该事件。 [原文](https://www.digitimes.com/news/a20260924PD225/ai-applications-testing-keysight-design-communications.html)
- **cand.de9bb5e0d45d** Beijing escalates domestic chip drive with Broadcom audits：原页只开放审计/国产替代导语，产品可能涉及Broadcom主机交换芯片（生产映射有host-cage）。未见审计正式范围、禁令/替代时间或订单变化；检索到二手博客但非官方证据，不能确认实际需求改变，暂不真也不假。 [原文](https://www.digitimes.com/news/a20260924VL220/broadcom-beijing-infrastructure-hardware-technology.html)
- **cand.2943453dbe7a** TSMC reportedly evaluates Texas fabs as US regional competition intensifies：DIGITIMES访问被拒。候选是据报道评估德州晶圆厂，仍缺公司确认、制程/产品范围、决定与时间。官方检索仅返回旧有美国投资/亚利桑那方案，不能拿旧项目替代德州传闻，更不能凭泛先进制程断言DSP产能；留待全文/正式公告。 [原文](https://www.digitimes.com/news/a20260930PD215/tsmc-texas-fab-arizona-ic-manufacturing.html)
- **cand.a32c938ea7ef** Foundry 2.0 revenue hits record as growth spreads beyond TSMC：DIGITIMES访问被拒；RSS与搜索摘要呈现Foundry 2.0市场营收统计，尚未读取原文，无法排除文中具体产能段落。搜索到Counterpoint Q1而非本条Q2原始报告；不用季度错配的旧报告补证，也不仅凭营收标题作假拒。 [原文](https://www.digitimes.com/news/a20260930VL211/revenue-tsmc-growth-market-capacity.html)
- **cand.a707e16ab12a** GlobalFoundries Singapore capacity utilization tops 90% as silicon photonics expansion hits equipment lead-time bottleneck：父复核纠正：仅可见2026-09-30媒体持续扩张导语；已读GF官方支持来源为2025-11-17，能够确认硅光产品族，但不能证明9月30日出现新增扩产事实或确定事件时点。撤回低置信true，不把旧项目叙述当成新事件；90%利用率和设备交期瓶颈亦未核实。 [原文](https://www.digitimes.com/news/a20260929PD228/globalfoundries-silicon-photonics-equipment-capacity.html)

其中中天数据中心MPO订单原文已取到，但公司现有实物映射仅有整模块：不改事实JSON、不把订单错归整模块，也不擅自扩充映射。需要补齐MPO映射的证据与归位后再入账。其余待办继续按7天要求补证；本报告是已核验批次交付，不是待办清零声明。

## 6. 实际提交清单

|候选 ID|判断|部件 / 类别 / confidence|理由及来源|
|---|---|---|---|
|`cand.54cf09807441`|算|part.pcb / capex / 3|第1、3页确认东城四期达到预定可使用状态并已投入使用，第3页设备总数938调整为1230；按投用里程碑计，不把内部资金调整或设备增多等同新增规划产能。具体投产日未披露，日期用公告日。 核验来源：http://static.cninfo.com.cn/finalpage/2025-10-29/1224756270.PDF|
|`cand.ea07153e6fa2`|算|part.pcb / capex / 3|第2—3页明确重庆基地无法满足订单需求，拟新建厂房、设备用房和自动化产线，产品为高多层板；建设周期14个月，尚非投产。产品族覆盖，不将交换机板等同本模块板。 核验来源：http://static.cninfo.com.cn/finalpage/2025-11-08/1224793464.PDF|
|`cand.d1202021deff`|算|part.pcb / capex / 3|第1—2页明确新建高层数、高频高速、高密度互连、高通流PCB，建设期2年；面向服务器和交换机，未拆分光模块板份额。昆山高新区青淞路/东龙路项目不同于3月沪利微电综合保税区项目。 核验来源：http://static.cninfo.com.cn/finalpage/2026-02-13/1224980233.PDF|
|`cand.77a8075ab114`|算|part.pcb / capex / 3|第1、3、4页明确55亿元、三期、生产高层数高频高速高密度互连高通流PCB，主要用于设备及厂房；为建设计划非已投产，与2月33亿元项目主体及地块不同。 核验来源：http://static.cninfo.com.cn/finalpage/2026-03-07/1225000150.PDF|
|`cand.42f9ff26f061`|算|part.pcb / capex / 3|第1、3页明确项目已达到预定可使用状态并已投入使用；内部投资调整不影响产能目标，因此只按投用里程碑计。不同于东城四期；原文未给确切投产日，用公告日。 核验来源：http://static.cninfo.com.cn/finalpage/2026-03-13/1225006734.PDF|
|`cand.ca3cd1cbbe8e`|算|part.pcb / capex / 3|第1—2页明确建设高速高密、高多层电子电路产品项目，主营为PCB制造销售，建设周期规划约12个月；未拆分模块PCB产能，尚非投产。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-24/1225163814.PDF|
|`cand.3e33b92f7c0e`|算|part.pcb / capex / 3|第3—4页明确产品包括5G通信及AI服务器用高频高速材料，规划4800万平方米覆铜板和1亿米商品粘结片，分两期建设，一期预计2028年投产；总量含汽车、封装等用途，不能全归高速板。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-25/1225195378.PDF|
|`cand.8e3e386b1877`|不算|—|第1—2页为2025年度行动方案进展回顾，仅称稳步提升、提速建设、加速泰国基地，未给可定位的新增项目决策、投产、订单或认证里程碑；不能将综合经营宣传作为新的独立扩产事件。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-29/1225231054.PDF|
|`cand.96be58f6c0a4`|不算|—|第3页明确搬迁不涉及产能减少、整体有效产能保持不变，原有生产业务延续；第4页仅提示短期波动风险，非已发生供给中断。不将公司内部搬迁整合误计新增产能或供给冲击。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-29/1225231053.PDF|
|`cand.13bd72097e91`|不算|—|第1、4页建设对象为光纤配套衬管、套管，70吨/年，非PCB用超薄石英电子布；生产映射仅有part.pcb材料角色，不能因同属石英或光通信就将光纤制备材料归入PCB。不是因合资形式而排除。 核验来源：http://static.cninfo.com.cn/finalpage/2026-06-09/1225360502.PDF|
|`cand.1b0b7ec4ff64`|算|part.pcb / capex / 4|第3页明确月增1万平方米、年增12万平方米mSAP基板用于光模块，第6页项目投资200261.60万元；按明确建设项目而非定增融资计。只纳入光模块mSAP项目，不把封装基板三期或补流偿贷合并为该产能；备案环评仍在办理。 核验来源：http://static.cninfo.com.cn/finalpage/2026-06-24/1225383446.PDF|
|`cand.4cbd7485197a`|算|part.pcb / capex / 3|第2—3页明确在赣州现有厂房增加全流程生产设备，主要产品高阶HDI和mSAP，覆盖高端通讯等；预计2027年1月开工，48个月建设，尚待股东会及审批。不同于吉安HDI技改和D1新厂房项目。 核验来源：http://static.cninfo.com.cn/finalpage/2026-07-24/1225439657.PDF|
|`cand.56e0624b8244`|算|part.pcb / capex / 3|第2—4页明确购置机械钻机、激光钻机等扩充HDI产能，覆盖通信等客户，24个月建设；与赣州50亿元mSAP不同地点、不同项目，未拆分模块板份额。 核验来源：http://static.cninfo.com.cn/finalpage/2026-07-24/1225439656.PDF|
|`cand.f4f18eda6d0f`|算|part.pcb / capex / 2|第2—4页明确D1为PCB扩产前置配套基础设施，拟2026年10月开工、24个月建设；产品族用途明确可按capex计，但仅土建载体、产线数量与产能未定，置信度2。50亿元mSAP使用现有厂房，D1为新增建筑；不可重复汇总两项目为已投产规模。 核验来源：http://static.cninfo.com.cn/finalpage/2026-07-24/1225439651.PDF|
|`cand.85a7892c4889`|不算|—|同cand.77a8075ab114的55亿元沪利微电项目后续调整：第1页明确仅二期改址至三期并取消自建污水厂，其他投资内容及总额不变；第2页称不产生重大不利影响。作为原项目跟踪证据，不重复建立扩产事件；并非新55亿元投资。 核验来源：http://static.cninfo.com.cn/finalpage/2026-08-26/1225502255.PDF|
|`cand.469d6ac96759`|算|part.pcb / capex / 3|第2—4页明确新增投资215800万元、总投资225700万元含已有厂房，AI服务器及汽车等HDI、36个月建设，目前筹备；不把总投资全称新增。不同于东城四期及智能算力一期。 核验来源：http://static.cninfo.com.cn/finalpage/2026-08-29/1225524449.PDF|
|`cand.ddd897562f44`|不算|—|原文第1–2页为17.88亿元海缆、海上风电、油田及深海绞车/脐带缆项目，不是高速光模块订单；不得因中天有光模块业务跨业务归因。 核验来源：http://static.cninfo.com.cn/finalpage/2025-10-17/1224715535.PDF|
|`cand.88c9b9d07ed9`|不算|—|第1–2页18.68亿元中标对象是±500kV/66kV海缆、风机施工及船舶租赁；不属于FAU或数据中心光互连产品族。 核验来源：http://static.cninfo.com.cn/finalpage/2025-10-28/1224745919.PDF|
|`cand.fc4bf4ed3de5`|不算|—|第1、5、11页明确仅框架性合作意愿，产品类别、价格、数量、规格均另行协商，不涉及具体金额；无已落实的产线、订单、认证或技术路线变更。不能把潜在收购/进入行业意愿当光模块订单。 核验来源：http://static.cninfo.com.cn/finalpage/2025-12-16/1224882280.PDF|
|`cand.def76f24afb9`|不算|—|第2页列示的高速数据中心电芯片产业化和800G研发是既有IPO项目；本次新增事项只是薪酬、税费、外币设备款的账户支付及等额置换（第2–4页），无新增建设、产能或技术节点。项目本身相关，但不得把每次资金安排重复当扩产；应以原IPO建设披露回填。 核验来源：http://static.cninfo.com.cn/finalpage/2025-12-30/1224904595.PDF|
|`cand.4808872add57`|不算|—|第2–4页沿用cand.def76f24afb9列示的同一批IPO项目；第4页明确投资总额、募集资金投入额、建设内容均未变更。仅增加实施主体/城市，没有独立新增产线、规模或投产里程碑，不再计一次扩产。 核验来源：http://static.cninfo.com.cn/finalpage/2026-01-27/1224951149.PDF|
|`cand.9474bfe9547d`|算|part.cw-laser / capex / 2|第3页明确新建光芯片生产线、厂房及配套，地点开元路1265号、建设期18个月；第3–4页聚焦高速光芯片及数据中心。按产品族覆盖纳入CW，但不推断具体型号或CW份额。 核验来源：http://static.cninfo.com.cn/finalpage/2026-02-10/1224972519.PDF|
|`cand.9e887b0f3e59`|算|part.fau / capex / 2|第2页明确激光器、光学智能装备及光连接器件研发生产，非纯工业激光；第4页新建产线厂房，24个月建设、30个月内投产。10亿元为混合项目总额，不等同FAU专属投资。 核验来源：http://static.cninfo.com.cn/finalpage/2026-03-28/1225048461.PDF|
|`cand.093217b326c7`|不算|—|全文3页中第1页仅概述400G/800G/1.6T核心产品已广泛应用及多形态技术体系，未给出本次新推出、投产、送样、订单或特定硅光PIC路线变化。后续是财务分红及治理；不能把既有业务介绍或MEMS OCS产品错挂硅光PIC。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-24/1225172615.PDF|
|`cand.7ffe590e5ab9`|算|part.module-maker / capex / 3|第1–2页明确常州等地光芯片及光模块扩建、12亿美元自筹资金，现有产能无法满足需求。产品族明确但速率未拆分。 核验来源：http://static.cninfo.com.cn/finalpage/2026-06-17/1225374224.PDF|
|`cand.f9eea6ac18bd`|算|part.mpo / capex / 2|第6–7页具体建设装修42600平方米厂房、购置设备及24个月周期；第9–10页明确扩大主营精密零部件并列举光纤连接器，符合产品族覆盖。不是仅资金转账户；不得将全部预算视为MPO专用。 核验来源：http://static.cninfo.com.cn/finalpage/2026-07-08/1225413565.PDF|
|`cand.190baa98ad18`|算|part.cw-laser / order / 2|第1–3页合同标的是磷化铟晶片（衬底），2026-08-01至2027-12-31分批交付。数据库核验云南锗业在CW部件的角色为InP衬底；按上游产品族归位，不能断言全部流向光模块或具体厂商。 核验来源：http://static.cninfo.com.cn/finalpage/2026-07-24/1225438868.PDF|
|`cand.fac9b0bd6e56`|算|part.cw-laser / capex / 3|第3–4页明确购买约126亩土地建设激光器芯片生产线、厂房及配套，建设期24个月。与2月二期12.51亿元/开元路1265号/18个月不同名称、拿地及规模，原文作为投资新项目披露，计独立决策；未证实两项目产能互不重叠，不把两笔预算相加为新增CW产能。 核验来源：http://static.cninfo.com.cn/finalpage/2026-08-12/1225469034.PDF|
|`cand.543f097e9404`|算|part.module-maker / capex / 4|第3页具体购置设备2650万元、测试调试100万元、12个月建设；第4页明确800G/1.6T需求、高速采集误码分析与精密耦合封装设备。按新建设项目capex，不因来源为剩余超募资金排除。 核验来源：http://static.cninfo.com.cn/finalpage/2026-08-18/1225478530.PDF|
|`cand.f0d0d250a98c`|算|part.module-maker / capex / 3|第1–2页直接引用6月17日项目并新增泰国、盐城实施主体/地点，总投资由12亿美元调增17亿美元。与cand.7ffe590e5ab9同项目，但新增5亿美元是实质变化，独立记变更而非重复原12亿美元。 核验来源：http://static.cninfo.com.cn/finalpage/2026-08-22/1225492197.PDF|
|`cand.e1a84317174a`|不算|—|与cand.def76f24afb9、cand.4808872add57是同一批IPO项目。第3页表明800G及以上项目主体/地点完全不变；第4页再次明确投资总额、投入额、建设内容未变。新增上海参与其他既有项目不足以证明新增供给，不重复计扩产。 核验来源：http://static.cninfo.com.cn/finalpage/2026-08-25/1225497047.PDF|
|`cand.2be9e8a052df`|不算|—|第1–2页18.31亿元订单为海底光电复合缆、海底电缆、风电安装与运维、软管；与FAU/模块光互连不同产品族，不因含光字入账。 核验来源：http://static.cninfo.com.cn/finalpage/2026-08-27/1225513677.PDF|
|`cand.c9519b4b907d`|不算|—|已直接渲染阅读原PDF封面及摘要：第1页为浙联评报字[2026]第253号股权价值评估；第6–7页（印刷第3–4页）明确为拟现金收购伽蓝特股权而评估全部权益，基准日2025-12-31、评估值47200万元。这是收购定价/股权事项，本次所读摘要未披露独立新增产线、订单、认证或技术路线变化，不把股权估值当整模块卡口。仅读封面/声明/摘要，并未宣称已核验51页全文；若后续正文有独立事实，应另核日期。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-18/1225121885.PDF|
|`cand.49859a174243`|算|part.lid-thermal / capex / 3|泰国生产基地明确包含石墨膜和导热界面材料；本次签署2.14亿元EPC工程合同为建设实质进展，而非仅募集资金安排。 核验来源：http://static.cninfo.com.cn/finalpage/2025-10-17/1224718690.PDF|
|`cand.b1f67accbb5c`|不算|—|本次终止的是安全智能光储系统项目；光模块及光器件改建仅为2024年资金用途调整的历史回顾和投入进度，并非本次新的建设决定。 核验来源：http://static.cninfo.com.cn/finalpage/2026-02-11/1224975496.PDF|
|`cand.a69176fd6ed0`|算|part.laser-coupling / capex / 3|公告第2–3页明确拟投3500万元建设光通信无源光学元器件规模化生产线，解决产能瓶颈并匹配高速光模块、OCS、CPO产品需求；按产品族归位。 核验来源：http://static.cninfo.com.cn/finalpage/2026-03-10/1225001280.PDF|
|`cand.588e3b866301`|不算|—|本次新增事实仅为子公司工商登记及取得营业执照，扩产方案重复2026-03-10公告；与cand.a69176fd6ed0同项目，不重复计为扩产。 核验来源：http://static.cninfo.com.cn/finalpage/2026-03-21/1225020460.PDF|
|`cand.0e5e359fac3c`|不算|—|原文PDF第5页（印刷页2）摘要明确：为年度合并财务报表进行商誉减值测试、评估商誉相关资产组可收回金额。这是财务计量，不是新的光引擎组装扩产、订单或认证事件。仅核验目录与摘要，不声称读完27页。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-24/1225165117.PDF|
|`cand.178a418c908d`|不算|—|PDF第5页（印刷页2）摘要明确为了解太芯截至2025-12-31股权价值变动进行评估，给转让行为提供价值参考；属于股权估值更新，不构成模块部件卡口事件。仅核验摘要及声明，不声称全文核验。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-30/1225268673.PDF|
|`cand.b2679ce11797`|不算|—|PDF第5页（印刷页2）摘要明确为拟收购太芯股权的价值参考、更新2025-12-31估值；是股权估值，不是陶瓷封装产线建设。仅核验摘要，不声称全文核验。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-30/1225268674.PDF|
|`cand.b7eb620a135c`|不算|—|PDF第5页（印刷页2）摘要明确评估目的为拟收购太芯股权、提供价值参考，基准日2025-04-30；是股权评估而非新增扩产/订单/认证。仅核验摘要，不声称全文核验。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-30/1225268676.PDF|
|`cand.ef0aec41f6b6`|不算|—|PDF第5页（印刷页2）摘要明确评估目的为十三所拟转让太芯股权提供价值参考，基准日2025-04-30；股权价值评估不算卡口事件。仅核验摘要，不声称全文核验。 核验来源：http://static.cninfo.com.cn/finalpage/2026-04-30/1225268675.PDF|
|`cand.97e5ae49fe24`|不算|—|投资对象为高强高韧粉末钛合金精密构件，应用列为折叠屏手机、5G基站、无人机及机器人；未建立与光模块散热顶盖/TIM产品族的关联，不能将通用MIM业务扩展当该部件扩产。 核验来源：http://static.cninfo.com.cn/finalpage/2026-05-20/1225317704.PDF|
|`cand.ed7c0ff96a94`|不算|—|原文第3页真正结项且达到预定可使用状态的是“光伏储能和片式通信磁性元器件智能制造项目”，不是光模块/光器件改建；第2页光模块改建为2024-09-25资金用途调整历史回顾。磁性器件投产不能误归为OSFP壳体/拉环/EMI供给。 核验来源：http://static.cninfo.com.cn/finalpage/2026-07-17/1225428395.PDF|
|`cand.92965351a8a3`|不算|—|实际访问原页仅见付费墙前导语；公开标题明确为16层以上HBM堆叠，导语为ASM/ASMPT/KLA在会议讨论先进封装及hybrid bonding。判定对象是这条HBM设备议题，非光引擎组装设备的扩产、交付或认证；不能把内存堆叠需求移植为本模块卡口。未声称读过付费全文。 核验来源：https://www.digitimes.com/news/a20260929PD221/packaging-equipment-hbm-2026-materials.html|
|`cand.cb3c63e4a584`|不算|—|实际访问仅公开标题及会议导语：研究机构与设备企业在Innovate Together会议讨论系统集成及人才吸引力。就该候选所陈述的会议/人才议题不算光引擎组装卡口，不把泛先进封装讨论当作光模块新产能；未读付费全文。 核验来源：https://www.digitimes.com/news/a20260929PD225/packaging-talent-2026-equipment-kla.html|
|`cand.0228229fc1d3`|不算|—|媒体仅预览；已读TOPPAN官方2026-09-30正文。实际开设的是AST的FC-BGA封装基板工厂，9月29日开幕、12月计划投产，专用于AI/大型网络交换机用大型高多层基板。不是Broadcom的DSP/PIC或主机交换ASIC产线投产，也非OSFP连接器产线；生产映射中Broadcom没有该FC-BGA基板部件。不能因Broadcom参与或网络设备用途强行映射host-cage。 核验来源：https://www.digitimes.com/news/a20260930VL202/ast-fc-bga-substrate-plant-high-end.html|
|`cand.3d4be9acfb80`|不算|—|DIGITIMES访问被拒；已读CBS直接采访报道正文。黄仁勋关于AI灭绝风险的公开观点（0% chance…end of the world）属于安全/监管话题，无本模块或主机网络产品族的供需、订单、产能或技术路线变化。 核验来源：https://www.digitimes.com/news/a20260930PD208/jensen-huang-nvidia-infrastructure-demand-ceo.html|
|`cand.5be45d4726bb`|不算|—|实际媒体预览明确AT&T与Corning超过30亿美元协议用于expand US fiber networks。Corning/AT&T官方链接实际尝试均403，未声称官方全文。候选可见交易对象为运营商光纤网络，不是硅光FAU或模块MPO器件订单；不把通用光纤需求映射为FAU卡口。 核验来源：https://www.digitimes.com/news/a20260930PR200/corning-demand-manufacturing-infrastructure-wireless.html|
|`cand.8539dcca2c0c`|不算|—|实际原页付费墙前导语说明DeepSeek将AI模型开发软件适配Huawei Ascend 950，以减少对NVIDIA硬件/CUDA依赖。对象是AI处理器软件生态，不是NVIDIA Quantum/Spectrum网络、OSFP连接器或光模块产品族；不能从算力竞争推导本模块订单变化。未读付费全文。 核验来源：https://www.digitimes.com/news/a20260930VL214/deepseek-ascend-software-huawei-nvidia.html|
|`cand.b1c74efc3b61`|不算|—|实际付费墙前导语确认黄仁勋和苏姿丰加入清华经管顾问委员会，属于人事/学术交流，不是主机侧光连接器或模块的供需、订单、认证、价格或路线事件。未读付费全文。 核验来源：https://www.digitimes.com/news/a20260930VL209/jensen-huang-lisa-su-ai-chip-academia-beijing.html|
|`cand.d1cf41ac5ec5`|不算|—|实际媒体预览为Qualcomm在Snapdragon Summit的PC战略，明确unveiled no new PC chips；标题为Googlebook/QwenBook与PC系统层AI。对象为PC/处理器生态，不是Qualcomm Alphawave Dragonfly光DSP产品族；不将所有Qualcomm芯片映射DSP。未读付费全文。 核验来源：https://www.digitimes.com/news/a20260930PD205/google-alibaba-ai-agent-ai-pc-chips.html|
|`cand.03076632549b`|算|part.shell / capex / 2|补查库内原始候选cand.03076632549b及巨潮公告2026-037：候选公告日期为2026-04-30，原PDF发布目录亦为finalpage/2026-04-30；4月29日是董事会/落款日期，不作为公开日。原文第25–27页明确建设高精密电子陶瓷生产线：总投资3.32亿元、新增年产2亿只（混合产品总量）、建设36个月，产品包括通信器件用电子陶瓷外壳、氮化铝薄厚膜基板及精密陶瓷零部件。按既有陶瓷封装角色与产品族归位，不等同于OSFP金属壳体；并非纯股权收购或主营介绍。8月24日公告只作交叉印证，不计为8月新催化；这是4月30日公开扩产事项的历史回填，尚非投产。原候选状态rejected、已有事件无该公司事件，父代理应按原候选/原文归账并避免与本条重复。 父复核改用原始候选入账，8月回顾候选不重复计。原文：https://static.cninfo.com.cn/finalpage/2026-04-30/1225268668.PDF|
|`cand.396605f72a15`|不算|—|已核对8月回顾及4月原公告：扩建是2026-04-30已公开事项，并非本次新事件。以原始候选cand.03076632549b按公开日回填，不将本回顾重复入账；4月29日仅董事会/落款日。原文：https://static.cninfo.com.cn/finalpage/2026-04-30/1225268668.PDF 第25–27页。|
|`cand.e033a5efb2ef`|不算|—|已读EE Times全文；比较10/7/5/3nm前六季度收入占比爬坡，并讨论2nm的未来观察方法。未披露光模块DSP/PIC产品族的新产线、订单、价格或认证，不能把通用晶圆营收曲线当部件卡口。来源：https://www.eetimes.com/tsmcs-3-nm-ramp-looks-different-in-historical-context/|
|`cand.4fe5876e3b92`|不算|—|已读公司2026-076公告全部3页。虽明确MPO产品族及5亿美元2027需求预测，但第1–2页重复说明仅意向性年度预测、无强制约束力、实际供货需后续正式订单；未披露已落实订单、新产线或可执行采购承诺，本次不按5亿美元订单/确定需求入账。未来正式订单另核。来源：https://static.cninfo.com.cn/finalpage/2026-09-30/1225589683.PDF|

## 7. 重算、快照与验证

- 最终CLI `python -m app.ingest recompute` run75 成功，日志在本地 `artifacts/runtime/accounting-v2.2/recompute-final.log`。
- `python3 tools/snapshot/build.py --api http://127.0.0.1:8000` 成功；产物 `physical/dist/teardown-web-snapshot.html`。
- Chromium本地打开及“研究”导航检查无console错误；快照嵌入数据与生产读数逐项核对（27真事件、9待判）。本次不改UI，不声称已有历史首页设计问题被修复。
- 未运行可能改写生产库的测试；本次没有业务代码变更。旧stash、其它未跟踪文件不提交。
- 本地证据含各组PDF/摘要/页码、请求与回执3批、部署前及AI提交前备份、前后status与17部件分布。备份不推送；原文访问范围以逐条理由为准。
- 生产期间news run73新增33条、交AI总池64（非净新增64）；原62之外新入队2条已在第3批处理，不能把全库新增数全算本次回填成果。

## 8. triage run72完整结果

```json
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
}
```

## 9. `/api/ingest/status` 全文（最终重算后）

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
    "pending": 9,
    "rejected": 9416,
    "pending_relevant": 9
  },
  "accounting": {
    "total": 9452,
    "accounted": 27,
    "by_rule": 1,
    "by_ai": 26,
    "by_human": 0,
    "to_ai": 9,
    "routine": 9346,
    "not_counted": 70,
    "dismissed_by_human": 0,
    "backfill": 8943,
    "backfill_accounted": 24,
    "expired": 0,
    "unprocessed": 0
  },
  "last_news_fetch": "2026-10-02T00:17:23",
  "todo_open": 286,
  "runs": [
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
    },
    {
      "id": 64,
      "job": "news",
      "started_at": "2026-10-01T03:15:01",
      "finished_at": "2026-10-01T03:15:15",
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
      "id": 63,
      "job": "news",
      "started_at": "2026-10-01T00:15:01",
      "finished_at": "2026-10-01T00:15:15",
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
      "id": 62,
      "job": "news",
      "started_at": "2026-09-30T21:15:02",
      "finished_at": "2026-09-30T21:15:15",
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
      "id": 61,
      "job": "news",
      "started_at": "2026-09-30T18:15:01",
      "finished_at": "2026-09-30T18:15:15",
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
      "id": 60,
      "job": "daily",
      "started_at": "2026-09-30T15:35:02",
      "finished_at": "2026-09-30T16:05:52",
      "ok": 1,
      "summary": {
        "quotes": {
          "companies_ok": 140,
          "companies_failed": 4,
          "unquotable": 21,
          "rows": 988
        },
        "inputs": {
          "companies_ok": 74,
          "companies_failed": 0
        },
        "valuation": {
          "companies_ok": 74,
          "companies_failed": 0
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
      "id": 59,
      "job": "news",
      "started_at": "2026-09-30T15:15:02",
      "finished_at": "2026-09-30T15:17:37",
      "ok": 1,
      "summary": {
        "new": 2,
        "merged": 0,
        "seen": 310,
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
      "id": 58,
      "job": "news",
      "started_at": "2026-09-30T12:15:01",
      "finished_at": "2026-09-30T12:17:34",
      "ok": 1,
      "summary": {
        "new": 5,
        "merged": 0,
        "seen": 308,
        "triage": {
          "relevant": 207,
          "routine": 9210
        },
        "accounting": {
          "auto": 0,
          "routine": 0,
          "triage": 12,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 57,
      "job": "news",
      "started_at": "2026-09-30T09:15:01",
      "finished_at": "2026-09-30T09:17:23",
      "ok": 1,
      "summary": {
        "new": 6,
        "merged": 0,
        "seen": 307,
        "triage": {
          "relevant": 202,
          "routine": 9210
        },
        "accounting": {
          "auto": 0,
          "routine": 4,
          "triage": 7,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    },
    {
      "id": 56,
      "job": "news",
      "started_at": "2026-09-30T06:15:01",
      "finished_at": "2026-09-30T06:17:10",
      "ok": 1,
      "summary": {
        "new": 1,
        "merged": 0,
        "seen": 314,
        "triage": {
          "relevant": 197,
          "routine": 9209
        },
        "accounting": {
          "auto": 0,
          "routine": 1,
          "triage": 5,
          "failed": 0
        },
        "expired": 0
      },
      "error": null
    }
  ]
}
```
