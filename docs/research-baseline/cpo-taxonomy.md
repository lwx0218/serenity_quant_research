# CPO 两级 Taxonomy 与术语表

## 1. 状态与边界

- 状态：Phase 1 P0 研究基线
- 核验日期：2026-08-24
- 范围：CPO 研究工作台的“两级物理拆解”，不是工程 BOM、CAD 或某一量产产品的逆向拆解
- 输入图片：`docs/references/cpo-3d-components.jpeg`、`docs/references/cpo-industry-chain.jpeg`
- 核验原则：图片只提供候选命名和研究线索；分类边界以 OIF 官方 co-packaging 文档为主要技术校验来源
- 稳定标识：以下 `module_id` / `part_id` 一经进入 P1 seed，不因展示文案调整而改变

本基线保留 9 个一级物理模块，并拆成 21 个可独立研究、可关联公司与证据的二级 part。数据模型仍须支持 `PhysicalPart.parent_id` 递归，以便未来增加第三级及更深 BOM。

## 2. 一级模块核验结果

| module_id | 标准名称（中文 / English） | 核验结论 | 边界说明 |
|---|---|---|---|
| `cpo.mod.thermal` | 散热与上盖 / Thermal solution and lid | 保留 | OIF 明确把 thermal/mechanical 作为 CPO 设计边界；图片中的冷板、热管只是实现候选。 |
| `cpo.mod.host-asic` | 主机交换 ASIC / Host switch ASIC | 保留 | CPO 的核心定义是光引擎与 host ASIC 在共同封装装配基板上近距离互连。 |
| `cpo.mod.eic` | 电接口处理层 / Electrical IC (EIC) layer | 保留并改名 | Driver、TIA、retimer/CDR/DSP 的组合依架构而异，不能假设每个设计同时具备全部器件。 |
| `cpo.mod.pic` | 硅光 PIC / Silicon-photonics PIC | 保留 | PIC 可包含波导、分合波、调制器和光电探测结构；“PIC”和完整“optical engine”不得同义使用。 |
| `cpo.mod.laser` | 光源 / Laser source | 保留并泛化 | 可能是集成光源，也可能是可维护的外置连续波光源（ELS）；图片的 EML/DFB 阵列不是唯一方案。 |
| `cpo.mod.receiver` | 光接收阵列 / Photodetector receive array | 保留为研究视图 | PD 功能成立，但实体可能集成于 PIC/光引擎，并不必然是图片中的独立板层。 |
| `cpo.mod.fiber-interface` | 光纤耦合与连接 / Fiber attach and optical connector | 保留 | 可采用 pigtail、mid-board connector、MPO 或其他高密度连接；MPO 不是所有 CPO 的必选项。 |
| `cpo.mod.cpa-substrate` | 共封装装配基板 / Co-packaged assembly substrate | 保留并规范命名 | OIF 使用 CPA substrate；organic substrate、RDL/interposer/bridge 是不同实现，不应混成同一材料结论。 |
| `cpo.mod.host-board` | 主机板与板级互连 / Host board and board-level interconnect | 保留但标为系统边界 | PCB 属于系统承载层，不等同于 CPA substrate；“金手指”是产品形态候选，不是 CPO 定义要件。 |

## 3. 二级 part 基线（21 个）

| part_id | parent module | 名称（中文 / English） | 独立研究问题 | 状态 |
|---|---|---|---|---|
| `cpo.part.thermal.lid-spreader` | `cpo.mod.thermal` | 上盖/均热盖 / Lid or heat spreader | 材料、平整度、热阻、封装应力 | 已核验类别 |
| `cpo.part.thermal.cooling-assembly` | `cpo.mod.thermal` | 冷板/散热器组件 / Cold plate or heatsink assembly | 风冷/液冷、流道、系统热预算 | 已核验类别，形态待产品核验 |
| `cpo.part.thermal.tim` | `cpo.mod.thermal` | 热界面材料 / Thermal interface material (TIM) | 导热率、厚度、可靠性、可维修性 | 已核验类别 |
| `cpo.part.host-asic.switch-die` | `cpo.mod.host-asic` | 交换 ASIC 裸片/封装 / Switch ASIC die or package | 交换容量、radix、功耗、封装方式 | 已核验类别 |
| `cpo.part.host-asic.serdes-io` | `cpo.mod.host-asic` | SerDes 与高速 I/O / SerDes and high-speed I/O | lane rate、XSR 链路预算、功耗 | 已核验类别 |
| `cpo.part.eic.driver` | `cpo.mod.eic` | 调制器驱动器 / Modulator driver | 摆幅、线性、带宽、每比特功耗 | 已核验类别 |
| `cpo.part.eic.tia` | `cpo.mod.eic` | 跨阻放大器 / Transimpedance amplifier (TIA) | 灵敏度、噪声、带宽、集成方式 | 已核验类别 |
| `cpo.part.eic.retimer-cdr-dsp` | `cpo.mod.eic` | Retimer/CDR/DSP 功能块 | retimed/linear/直驱架构取舍 | 架构可选项 |
| `cpo.part.pic.modulator` | `cpo.mod.pic` | 光调制器 / Optical modulator | MZM/环形等路线、带宽、损耗、驱动需求 | 已核验类别 |
| `cpo.part.pic.wdm` | `cpo.mod.pic` | WDM 复用/解复用 / WDM mux/demux | 波长数、通道间隔、温漂、插损 | 已核验类别 |
| `cpo.part.pic.waveguide-coupler` | `cpo.mod.pic` | 波导与片上耦合结构 / Waveguide and on-chip coupler | waveguide、splitter/combiner、耦合损耗 | 已核验类别 |
| `cpo.part.laser.cw-array` | `cpo.mod.laser` | 连续波激光器/阵列 / CW laser or laser array | 集成式与 ELS、功率、波长、可靠性 | 已核验类别 |
| `cpo.part.laser.source-interface` | `cpo.mod.laser` | 光源耦合与供光接口 / Source coupling and delivery interface | laser attach、外置供光、eye safety、可维护性 | 已核验类别 |
| `cpo.part.receiver.pd-array` | `cpo.mod.receiver` | 光电探测器阵列 / Photodiode array | responsivity、带宽、暗电流、PIC 集成 | 已核验功能；物理边界待产品核验 |
| `cpo.part.fiber.fau` | `cpo.mod.fiber-interface` | 光纤阵列单元 / Fiber array unit (FAU) | 通道数、对准、端面、耦合损耗、良率 | 已核验类别 |
| `cpo.part.fiber.connector` | `cpo.mod.fiber-interface` | 高密度光连接器 / High-density optical connector | MPO/EBO/其他路线、密度、插损、清洁维护 | 已核验类别；具体制式待核验 |
| `cpo.part.cpa.package-substrate` | `cpo.mod.cpa-substrate` | 高密度封装基板 / High-density package substrate | 材料、布线密度、翘曲、供电与热路径 | 已核验类别 |
| `cpo.part.cpa.interposer-bridge` | `cpo.mod.cpa-substrate` | 中介层/RDL/桥接 / Interposer, RDL or bridge | 互连距离、带宽密度、封装良率、成本 | 实现可选项 |
| `cpo.part.board.high-speed-pcb` | `cpo.mod.host-board` | 高速主机 PCB / High-speed host PCB | 低损耗材料、层叠、供电、散热与信号完整性 | 已核验系统类别 |
| `cpo.part.board.edge-connector` | `cpo.mod.host-board` | 板级连接器/金手指 / Board connector or edge fingers | 系统接口、可靠性、带宽边界 | 产品形态候选 |
| `cpo.part.board.power-management` | `cpo.mod.host-board` | 板级供电与电源管理 / Board power delivery and management | 多电压轨、瞬态、效率、监控 | 已核验系统类别 |

### P1 seed 约束

1. 一级模块与二级 part 分表/分类型保存，但二级实体使用递归 `parent_id`。
2. `optical engine` 是由 PIC、EIC、光源/接收和光纤接口等构成的装配/功能边界，不新增为与这些部件并列且重复计数的物理层。
3. `module_id`/`part_id` 与 SVG 的 `<g data-part-id="...">` 绑定；SVG 几何不承载业务关系。
4. 公司暴露关系默认 `candidate`，没有 Level A/B 证据不得标成 `verified`。
5. 图片中的 `1.6T/3.2T`、`112G/224G PAM4`、`8×200G/16×100G` 不进入固定 taxonomy 字段，只能进入带来源和时间的 specification/evidence。

## 4. 物理 taxonomy 与产业链视图的分离

`docs/references/cpo-industry-chain.jpeg` 给出的十个区域可作为产业链候选入口，但不能作为物理 BOM：

| chain_node_id | 产业链视图 | 与物理 taxonomy 的关系 |
|---|---|---|
| `cpo.chain.demand` | 需求与算力网络 | 需求/事件上下文，不是物理 part |
| `cpo.chain.asic` | 交换 ASIC | 主要关联 host ASIC 与 SerDes |
| `cpo.chain.silicon-photonics` | 硅光 | 主要关联 PIC、modulator、WDM、waveguide |
| `cpo.chain.light-source` | 光源/激光器 | 主要关联 CW laser 与 source interface |
| `cpo.chain.optical-engine-package` | 光引擎与封装 | 跨 PIC、EIC、光源/接收、CPA substrate |
| `cpo.chain.substrate-interconnect` | 基板与互连 | 关联 package substrate、interposer、host PCB |
| `cpo.chain.thermal-structure` | 散热与结构 | 关联 lid、cooling assembly、TIM |
| `cpo.chain.test-equipment` | 测试与设备 | 横跨晶圆、封装、光电和系统测试，不对应单一 part |
| `cpo.chain.optical-connection` | 光器件与连接 | 关联 FAU、connector、PD、部分光源部件 |
| `cpo.chain.systems-switches` | 下游系统与交换机 | 系统/需求上下文，不是物理 part |

物理 part 与产业链节点使用显式多对多映射；禁止由 SVG 分组或产业链栏位推导事实关系。

## 5. 术语表

| 术语 | 本项目定义 | 禁止的混用 |
|---|---|---|
| CPO | 光学引擎与 host ASIC 在共同封装装配基板上近距离共封装的体系 | 不等于普通板载光学或所有集成光学 |
| Host ASIC | 交换/处理主芯片 | 不等于 optical engine 内的 EIC |
| Optical Engine / OE | 完成电到光、光到电转换的高密度光学装配 | 不等于单颗 SiPh PIC |
| PIC | Photonic Integrated Circuit，承载波导、调制/分合波/探测等光子功能 | 不默认包含完整驱动、TIA、连接器与散热 |
| SiPh | Silicon Photonics，硅光技术/平台 | 不代表激光器一定单片集成在硅上 |
| EIC | Optical engine 的 electrical IC 部分 | 不等于 host switch ASIC |
| Driver | 驱动光调制器的电路 | 不等于 SerDes/retimer |
| TIA | 将 PD 电流转换并放大的接收前端 | 不等于完整接收 DSP |
| Retimer/CDR/DSP | 重定时、时钟恢复、数字信号处理功能 | 不是所有 CPO 电接口的必选组合 |
| SerDes | 串行化/解串器及高速 I/O | 不等于外部光链路 |
| XSR | 面向封装/短距芯片间的超短距电接口类别 | 不表示任意 PCB 长距电链路 |
| Modulator | 将电信号调制到光载波的器件 | 不等于激光器 |
| WDM | 波分复用/解复用 | 不等于简单并行多纤 |
| CW Laser | 连续波光源 | 不默认等于 EML；EML 自带电吸收调制功能 |
| ELS | External Laser Source，可从可维护位置向 optical engine 供光 | 不默认是 CPO 内部独立“激光板层” |
| PD | Photodiode，光电探测器 | 不默认是独立于 PIC 的板卡 |
| FAU | Fiber Array Unit，用于多通道光纤对准和耦合 | 不等于 MPO 连接器 |
| MPO | 多芯推拉式光连接器家族 | 不是 CPO 唯一或必选连接器 |
| CPA substrate | 承载 host ASIC 与 co-packaged engine 的共同装配基板 | 不等于系统主 PCB |
| Interposer/RDL/bridge | 高密度封装互连的可选实现 | 三者不可无证据互换 |
| TIM | 热源与冷却结构间的热界面材料 | 不等于 heatsink/cold plate |
| PAM4 | 四电平脉冲幅度调制 | lane rate、baud rate 与总带宽必须分别记录 |

## 6. 核验来源与未决项

### 主要核验来源

1. OIF, *Co-Packaging Framework Document*, OIF-Co-Packaging-FD-01.0  
   https://www.oiforum.com/wp-content/uploads/OIF-Co-Packaging-FD-01.0.pdf
2. OIF, *Implementation Agreement for a 3.2Tb/s Co-Packaged (CPO) Module*, OIF-Co-Packaging-3.2T-Module-01.0  
   https://www.oiforum.com/wp-content/uploads/OIF-Co-Packaging-3.2T-Module-01.0.pdf
3. OIF, *Management of External Light Sources and Co-Packaged Optics*  
   https://www.oiforum.com/wp-content/uploads/OIF-MGT-Co-Packaging-ELSFP-01.0-1.pdf
4. Cisco, *Co-Packaged Optics and an Open Ecosystem*（厂商观点，仅作架构交叉检查）  
   https://blogs.cisco.com/sp/co-packaged-optics-and-an-open-ecosystem

### 进入 P1 前不阻塞、但必须保留为 unresolved questions 的事项

- 两张 JPEG 不能证明 9 层结构对应任何真实产品。
- Driver/TIA/retimer/DSP 的具体组合、PD 是否独立、激光器集成/外置方案必须按产品证据建模。
- MPO、金手指、冷板/热管和明确速率均为候选实现，不能写成 CPO 定义。
- 需要由具备光模块/硅光封装经验的人工 reviewer 对 21 个 part 做一次术语签核；签核前状态为“技术文档交叉核验完成，产品事实未核验”。
