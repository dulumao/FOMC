---
slug: modules/rules
title: 规则建模
order: 19
summary: Taylor 系列规则：输入指标、参数假设、输出路径，以及门户/学习模式如何调用。
---

# 规则建模模块（Taylor 系列）

## 职责边界

规则模型在本项目里只做一件事：给出一个**可复现的基准线**（baseline）。

它不是预测器，而是坐标系：把“通胀偏离/就业缺口”翻译成一条利率建议路径，便于讨论“偏离来自哪里”。

## 关键入口

- 模型定义：`src/fomc/rules/taylor_rule.py`
  - `ModelType`：不同预设/变体
- 数据准备与计算服务：`src/fomc/data/modeling/taylor_service.py`
  - `build_taylor_series_from_db(...)`
- 门户 API：`POST /api/models/taylor`（见 `src/fomc/apps/web/main.py`）
- FOMC101 cell：`src/fomc/apps/web/fed101.py`（`taylor_model`）

## 输入与默认值（常用）

- 通胀：默认 `PCEPILFE`
- 失业率：默认 `UNRATE`
- NAIRU：默认 `NROU`
- 政策利率（对照）：默认 `EFFR`

## 常见问题定位

- 结果为一条水平线/全空：优先检查指标 DB 是否已同步、code 是否存在
- 与会议窗口对不齐：检查是否使用了 `use_meeting_end`（FOMC101 会用示例会议对齐）

