---
slug: modules
title: 模块
order: 30
summary: 模块边界、入口函数、输入输出与落盘位置。
---

# 模块

本节按功能模块拆解，每页回答四个问题：

1. 它做什么（职责边界）
2. 入口在哪（关键文件/函数）
3. 输入/输出是什么
4. 产物落在哪里（缓存/落盘）

如果你要“改模块并验证改动”，建议搭配阅读：`/techdocs/dev/workflows`（常见修改点与验证路径）。

## 模块列表

- 宏观经济事件：`/techdocs/modules/macro-events`
- 经济数据（指标库）：`/techdocs/modules/economic-data`
- 研报（NFP/CPI）：`/techdocs/modules/reports`
- 规则建模（Taylor 系列）：`/techdocs/modules/rules`
- 会议模拟（讨论/决议/落盘）：`/techdocs/modules/meetings`
- LLM 基础设施（统一调用与日志）：`/techdocs/modules/llm`
