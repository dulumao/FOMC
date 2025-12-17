---
slug: modules/reports
title: 研报（NFP/CPI）
order: 18
summary: 同一份研报生成结果被工具箱/历史会议/Fed101 三处复用，保证图表一致与可解释。
---

# 研报模块（NFP/CPI）

## 职责边界

研报模块的目标是：把一堆时间序列压缩成少数图表与要点，输出“可用于讨论”的材料。

本项目当前重点覆盖：

- NFP（就业）
- CPI（通胀）

## 入口与复用方式

门户侧封装在：`src/fomc/apps/web/backend.py`

- NFP 研报：`generate_labor_report(...)`
- CPI 研报：`generate_cpi_report(...)`

三处复用同一份结果：

- 工具箱：展示完整研报与图表
- 历史会议：在会议窗口内生成并缓存研报
- Fed101：把研报图表拆成 cell，逐张讲解（但图表数据/顺序与研报一致）

## 图表渲染

- Fed101 cell 运行与数据拼装：`src/fomc/apps/web/fed101.py`
  - `labor_figure` / `cpi_figure`
- 前端渲染：`src/fomc/apps/web/static/fed101.js`
- 表格渲染（分项拉动表）：`src/fomc/apps/web/static/report_render.js`

## 缓存落点

历史会议模拟会把研报文本/产物落到：

- `data/meeting_runs/<meeting_id>/`（见 `src/fomc/data/meetings/run_store.py`）

