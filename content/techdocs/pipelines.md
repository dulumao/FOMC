---
slug: pipelines
title: 历史会议模拟（流程）
order: 30
summary: 一场会议如何被“跑完”：生成/缓存/刷新都在同一条 pipeline 上完成。
---

# 历史会议模拟（流程）

## 页面入口

- 入口页面：`/history`
- 会议页：`/history/<meeting_id>/...`
- 路由：`src/fomc/apps/web/main.py`

## 核心编排在哪里

历史会议模拟的“流程编排”主要集中在：

- `src/fomc/apps/web/backend.py`：作为门户与底层模块之间的集成层
- `src/fomc/data/meetings/run_store.py`：把每一步产物落盘、读取、标记缓存状态

## 一次会议会产出什么

运行目录：`data/meeting_runs/<meeting_id>/`

常见产物包括：

- 宏观事件摘要（会议窗口）
- NFP / CPI 研报（文本 + 图表数据）
- 规则模型结果（时间序列/建议路径）
- 多角色讨论过程与汇总
- Statement / Minutes 生成稿

如果你在页面上看到“cached”，通常意味着对应产物已存在且本次请求未强制 refresh。

