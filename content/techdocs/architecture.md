---
slug: architecture
title: 架构
order: 5
summary: 用一张“数据流 + 模块边界”的地图，把三种模式入口串起来。
---

# 架构

## 总体结构：一套能力，三种入口

三种入口共享同一套底层模块：

- 学习：`/fed101`（解释 + 可运行演示）
- 流程：`/history`（按会议串联跑完并落盘）
- 工具：`/toolbox`（把能力拆成独立工具）

## 数据流（从输入到落盘）

1) **数据与上下文**

- 指标时间序列：DB（见 `src/fomc/data/database/`）
- 宏观事件：macro events DB（见 `src/fomc/data/macro_events/`）
- 会议上下文：`meeting_id → report_months`（见 `src/fomc/apps/web/backend.py:get_meeting_context`）

2) **生成与计算**

- NFP/CPI 研报：`src/fomc/apps/web/backend.py`（调用研报生成逻辑）
- 规则模型：`src/fomc/data/modeling/taylor_service.py` + `src/fomc/rules/taylor_rule.py`
- 讨论与决议（LLM）：`src/fomc/data/meetings/discussion_service.py`

3) **缓存与复盘**

- 历史会议产物落盘：`data/meeting_runs/<meeting_id>/`
- 读写封装：`src/fomc/data/meetings/run_store.py`

## Web 门户：薄路由 + 集成层

- 路由与模板：`src/fomc/apps/web/main.py`
- “集成层”（把数据/研报/模型/LLM 串起来）：`src/fomc/apps/web/backend.py`

如果你想定位“一个页面背后到底调用了哪些模块”，从 `main.py` 找路由，再跳到 `backend.py` 基本就能跟完主链路。

