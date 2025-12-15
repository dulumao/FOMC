---
slug: data
title: 数据与存储
order: 20
summary: 三类数据的落点与用途：指标库、宏观事件库、会议产物缓存。
---

# 数据与存储

这个项目的“数据”大致分三类，你排查问题时可以直接对号入座：

## 1) 指标时间序列（Economic Indicators）

- ORM 模型：`src/fomc/data/database/models.py`
- DB 连接：`src/fomc/data/database/connection.py`
- 同步/刷新：`src/fomc/data/indicators/`
- 门户接口：`src/fomc/apps/web/backend.py`（例如指标查询、健康状态）

更详细的模块说明：`/techdocs/modules/economic-data`

## 2) 宏观事件（月报）

- 事件库（SQLite）：见 `src/fomc/data/macro_events/db.py`
- 生成逻辑：`src/fomc/data/macro_events/month_service.py`
- 门户调用：`src/fomc/apps/web/backend.py`（会议页的宏观事件与摘要）

更详细的模块说明：`/techdocs/modules/macro-events`

## 3) 会议运行缓存（meeting_runs）

历史会议模拟会把生成结果落盘，方便复用与复盘：

- 路径：`data/meeting_runs/<meeting_id>/`
- 读写封装：`src/fomc/data/meetings/run_store.py`
- 典型产物：宏观摘要、NFP/CPI 研报文本、规则模型结果、讨论过程、Statement/Minutes 生成稿等
