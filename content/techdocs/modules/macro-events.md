---
slug: modules/macro-events
title: 宏观事件
order: 16
summary: 新闻 → 事件 → 月报：抓取、清洗、打分、总结，并在会议窗口内复用。
---

# 宏观经济事件模块

## 职责边界

这个模块解决的是：**把一整个月的宏观新闻压缩成“可用于会议讨论”的事件与摘要**。

输出形态有两类：

- 月度摘要（Markdown）
- 事件列表（带类型、重要度、摘要、来源）

## 关键入口

- 生成/确保某月事件与摘要：`src/fomc/data/macro_events/month_service.py`
- DB 读写：`src/fomc/data/macro_events/db.py`
- 门户调用（会议页/宏观事件页）：`src/fomc/apps/web/backend.py`（相关接口会组合月度材料与会议窗口摘要）

## 数据与落点

- 宏观事件库：SQLite（路径由配置决定；入口常见于 `src/fomc/data/macro_events/db.py`）
- 会议级宏观摘要落盘：`data/meeting_runs/<meeting_id>/`（见 `src/fomc/data/meetings/run_store.py`）

## 调试建议

- 如果页面显示“无摘要/无事件”，先确认宏观事件库是否有当月记录，再看是否触发了 refresh。

