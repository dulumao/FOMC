---
slug: modules/economic-data
title: 经济数据
order: 31
summary: 指标库（元数据 + 时间序列）、同步管线与门户查询。
---

# 经济数据模块

## 职责边界

这个模块负责两件事：

1. **把宏观指标时间序列落到本地数据库**（统一查询、绘图、建模）
2. **提供门户侧可复用的查询接口**（工具箱、历史会议、FOMC101）

它刻意不做的事情：

- 不在运行时“边查边算”复杂派生指标（优先把输入序列稳定落库）
- 不在门户层硬编码 series id（指标清单集中维护，便于扩展与审计）

## 关键入口

- ORM 模型：`src/fomc/data/database/models.py`
  - `EconomicIndicator`：指标元信息
  - `EconomicDataPoint`：时间序列点（date/value）
  - `IndicatorCategory`：指标分类（用于树状目录）
- DB 连接：`src/fomc/data/database/connection.py`
- 同步管线：`src/fomc/data/indicators/`
  - `indicator_sync_pipeline.py`
  - `data_updater.py`
- 门户查询：`src/fomc/apps/web/backend.py`

## 指标清单从哪里来

当前实现采用“外部定义 + 同步入库”的方式维护指标清单：

- 指标定义表：`docs/US Economic Indicators with FRED Codes.xlsx`

这样做的好处是：指标覆盖与口径变化可以通过表格审阅与版本管理完成，不需要改代码。

## 同步流程（当前实现）

1. 读取 Excel 定义（`docs/US Economic Indicators with FRED Codes.xlsx`）
2. 同步分类与指标元数据
3. 增量拉取 FRED 数据
4. 写入 `fomc_data.db`（避免重复日期）

更细一点（代码级）：

- 同步编排：`src/fomc/data/indicators/indicator_sync_pipeline.py`
  - 会把 Excel 的“板块/指标名/FRED 代码”映射成 `IndicatorCategory` + `EconomicIndicator`
  - Excel 里有一类“空 FRED 代码行”会被当作子分类标记行（不是错误）
- 增量更新：`src/fomc/data/indicators/data_updater.py:IndicatorDataUpdater`
  - 默认只补齐缺口区间（起止边界由 DB 现有最小/最大日期推断）
  - `full_refresh=true` 会先删除该指标已有数据再重拉（用于修复口径或脏数据）
  - 会做重复日期清理（历史遗留重复写入的兜底）

## 数据落点

- 主库：`data/fomc_data.db`

## 数据模型（概念层）

- `EconomicIndicator`：描述“这条序列是什么”（名称、代码、单位、频率、分类等）
- `EconomicDataPoint`：描述“这条序列在某天是多少”（date/value）
- `IndicatorCategory`：描述“这条序列属于哪个目录”（用于门户展示与搜索）

你可以把它理解为：一个“字典表（元信息）” + 一个“事实表（时间序列）”。

## 门户接口（常用）

- `GET /api/indicators`：返回指标树（分类 + 指标元信息）
- `GET /api/indicator-data?code=<series_code>&date_range=5Y`：返回序列绘图数据
- `POST /api/db/jobs/sync-indicators`：启动同步任务
- `GET /api/db/indicator-health`：查看缺口/健康状态（哪些指标缺数据）

## 影响范围（谁会用到这套数据）

- 工具箱：指标浏览、单序列绘图
- 研报：NFP/CPI 的图表与摘要（`apps/flaskapp/`）
- 规则模型：Taylor 系列（`/techdocs/modules/rules`）
- FOMC101：学习章节里的图表 cell（`/techdocs/web/fed101`）

## 常见问题定位

- 图表无数据：检查是否已执行 init/sync
- 指标名称或单位异常：检查 `EconomicIndicator` 元数据
- 某指标缺口：查看 `indicator_health` 接口结果
