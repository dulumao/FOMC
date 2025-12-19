---
slug: modules/economic-data
title: 经济数据
order: 17
summary: 指标库（EconomicIndicator/EconomicDataPoint）、同步管线、以及门户侧查询与健康检查。
---

# 经济数据模块

## 职责边界

这个模块负责两件事：

1) **把宏观指标时间序列落到本地数据库**（便于统一查询、绘图与模型计算）
2) **提供门户侧可复用的查询接口**（工具箱、历史会议、FOMC101 都会用）

## 关键入口

- ORM 模型：`src/fomc/data/database/models.py`
  - `EconomicIndicator`：指标元信息（代码、单位、名称等）
  - `EconomicDataPoint`：时间序列点（date/value）
- DB 连接：`src/fomc/data/database/connection.py`
- 同步管线：`src/fomc/data/indicators/`
  - `indicator_sync_pipeline.py`
  - `data_updater.py`
- 门户查询：`src/fomc/apps/web/backend.py`（指标查询、分类树、健康状态等）

## 常见问题定位

- 指标图“无数据”：优先检查 DB 是否已初始化/同步（以及指标 code 是否存在）
- 指标名称/单位异常：检查 `EconomicIndicator` 元数据是否完整

