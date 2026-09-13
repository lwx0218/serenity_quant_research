# physical/ · 从物理出发

`main`（原 reboot-v2）上的 Teardown 是从投研出发去找物理：首页是「资金本周在给哪一层投票」，CPO 九个模块其实是一条产业链的分类，而不是一只正在出货的模块。

这个目录反过来：**先拿一只真实在用的模块，画横截面，让信号从主机金手指走到光纤，穿过的每一个部件挂上它背后的公司**。投研是从物理长出来的，不是反过来去找物理。

第一只模块：**1.6T OSFP DR8 硅光 + 3nm DSP**——Quantum-X800 / Spectrum-X800 / ConnectX-9（Rubin 世代 scale-out）正在用的形态。

## 文件

```text
physical/
  data/module-1.6t-dr8-siph.json     唯一的数据源：模块 → 部件 → 信号顺序 → 公司（按产业阶段、证据级）
  design/gen_physical.py             方向稿画板（Claude Design 画布用 .dc.html，浅深两版）；等距揭盖图的几何在这里
  design/build_prototype.py          可交互原型：→ dist/teardown-1.6t-prototype.html（单文件，双击即开）
  design/reference-intel-1.6t-opened.png  部件摆位参考（Intel 1.6T 拆解图）
  dist/teardown-1.6t-prototype.html  当前的原型（选中部件 / 发收切换 / 浅深 / Esc 回整机）
  index.html · build.py · dist/teardown-1.6t-dr8-siph.html  第一版横截面页（风格不合，已被原型取代，待删）
```

改了 JSON 或几何之后：`python3 physical/design/gen_physical.py && python3 physical/design/build_prototype.py`。
画布：`Teardown 实物剖面 · 1.6T 光模块`（Claude Design）。原型的 UX 预审记录见提交历史（ux-preflight）。

## 接缝（物理 → 投研）

`physical/seam.py` 给每条公司映射写 `companyId`（与 `data/seeds/cpo` 同一套 id：A 股 `cn.<代码>`，海外 `global.<slug>`，未上市 `private.<slug>`），main 没有主数据的公司补在 `data/seeds/physical/companies.json`（61 家）。占位条目（如「国产 DSP（暂无成熟量产者）」）`companyId` 为 null。
下一步在 web/ 上落：公司页加一节「在实物里的位置」，研究收件箱事件表加「→ 部件」列（方向稿见画布第二页）。

## 数据模型（schema 0.2）

| 字段 | 含义 |
|---|---|
| `module` | 一只具体模块：形态、规格、它插在哪台英伟达机器的哪个位置（`hostContext`） |
| `layers` | 横截面从上到下的分层（顶盖 / 光引擎 / 主 PCB / 壳体），只用于讲解 |
| `parts[]` | 部件：功能、关键参数、上游材料、`companies[]` |
| `signalPath.tx / rx` | 信号按顺序经过哪些 part，每一步是电还是光 |
| `stages` | 产业阶段：材料 → 芯片 → 器件/封装 → 引擎/组装 → 连接 → 模块/客户 → 设备/测试 |
| `companies[].evidence` | `verified` 公开披露可查 · `consensus` 券商/行业媒体一致 · `candidate` 方向对但供货关系待核验 |
| `companies[].market` | `A` / `US` / `JP` / `TW` / `HK` / `私有` … 页面上按此上色和筛选 |
| `companies[].companyId` | main 侧公司 id（`seam.py` 生成）；占位条目为 null |

同一家公司可以出现在多个 part 下（旭创同时是 PIC 自研、引擎组装、整模块），页面底部的「Multi-part exposure」就是数这个。

## 页面三块

1. **横截面 · 信号怎么走**：侧视图，发 / 收 / 同时三种路径，电信号橙、光信号青，数字站点按 `signalPath` 顺序。点部件或站点，下面出详情。
2. **部件详情**：功能、参数、上游材料，公司按产业阶段分组，市场标签 + 证据级圆点。
3. **全景表 · 谁在哪一层**：行 = 部件（按 TX 顺序），列 = 阶段；可按市场、证据级筛选；点公司名高亮它出现的所有格子。

## 下一步（尚未做）

- 追加第二、第三只实物：存储（HBM / SSD）、PCB（GB300 compute tray）、电源……都围绕一台真实的英伟达机柜展开，`module` 变成 `objects[]`。
- 把 `companies` 的 id 和 `data/seeds/cpo/*.json` 里的公司主数据对上，这样 main 上的事件 / 反应 / 篮子能直接挂到横截面的部件上——这是「物理 → 投研」的接缝。
- 每条 `evidence: candidate` 都需要一条来源（公告 / 互动易 / 招股书）才能升为 `verified`，沿用 `docs/research-baseline/evidence-contract.md`。
- 横截面几何现在写死在 `index.html` 的 `G` 表里；到第二只实物时要把几何也搬进 JSON。
