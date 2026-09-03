---
subject: cpo.mod.laser
kind: module
title: 激光器阵列
direction: neu
stance: 外置光源是可维护性与成本的权衡,不是技术路线之争;不因架构之争加减仓
updated: 2026-08-24
since: 2026-06-01
window_until: 2026-08-31
window_label: 一个季度(至 2026-08-31)
threshold_pct: 3
track:
  - basket:cpo.mod.laser
indicators:
  - 外置光源方案在 1.6T 交换机中的占比
  - 激光器篮子相对整机 ≥ +3%
invalidation:
  - 主流交换机厂商明确放弃外置光源
position: 观察;到期回顾后再决定
sample: true
---

外置光源(ELS)把激光器从封装里挪到前面板,换来的是可维护与可替换,代价是耦合损耗与光纤数量。它不改变每个端口需要的连续波功率,所以不改变激光器的颗数需求,只改变谁来封装它。[[源杰科技]] 与 [[长光华芯]] 的差别在于产品是不是已经进到 CW 大功率这一档。

## 问题

- [ ] 外置光源架构对激光器颗数需求的影响方向? (2026-08-24)
