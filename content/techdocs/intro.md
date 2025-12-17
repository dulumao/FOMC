---
slug: intro
title: 导读
order: 1
summary: 项目技术总览：架构、模块、三种模式入口。
---

# 技术总览

本项目是一个面向 FOMC 决策流程的交互式系统：**同一套底层能力**，提供三种入口：

- **美联储 101（学习）**：用文档 + 可运行小组件讲清楚“每一步为什么存在、怎么看输出”
- **历史会议模拟（流程）**：按 `meeting_id` 重放一次会议，生成并缓存材料，强调可复现
- **工具箱（工具）**：把研报、模型、数据浏览拆成独立工具，随时调用

这份技术文档的定位是：**解释它怎么实现**（模块边界、关键入口、数据流、缓存落点）。

## 快速索引（先看这三页就够）

- 架构总览：`/techdocs/architecture`
- 模块细节：`/techdocs/modules`
- Web 门户入口：`/techdocs/web`

## 代码组织（当前实现）

- Web 门户：`src/fomc/apps/web/`
- 指标数据库与同步：`src/fomc/data/database/`、`src/fomc/data/indicators/`
- 宏观事件（月报）：`src/fomc/data/macro_events/`
- 会议日历与流程产物落盘：`src/fomc/data/meetings/`、`data/meeting_runs/`
- 研报生成：`src/fomc/reports/`
- 规则模型（Taylor 系列）：`src/fomc/rules/`、`src/fomc/data/modeling/`

后续的“理想架构蓝图”在 `docs/development.md`（那是目标形态；本文档以当前实现为准）。
