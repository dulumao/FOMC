---
slug: modules/rules
title: 规则建模
order: 34
summary: Taylor 系列规则：输入、参数、输出与门户调用。
---

# 规则建模模块（Taylor 系列）

## 职责边界

规则模型在本项目里只做一件事：给出**可复现的基准线**。它是坐标系，不是预测器。

## 关键入口

- 模型定义：`src/fomc/rules/taylor_rule.py`
- 计算服务：`src/fomc/data/modeling/taylor_service.py`
- 门户 API：`POST /api/models/taylor`（`src/fomc/apps/web/main.py`）
- FOMC101 cell：`src/fomc/apps/web/fed101.py`（`taylor_model`）

## 输入与默认值

- 通胀：`PCEPILFE`
- 失业率：`UNRATE`
- NAIRU：`NROU`
- 政策利率：`EFFR`

## 数据来源

- 指标数据来自 `data/fomc_data.db`

## 输出形状（门户 API）

`POST /api/models/taylor` 会返回：

- `series[]`：按月的规则利率序列（含 month/date、rule_rate、actual_rate 等）
- `metrics`：末端月份的关键指标快照（用于页面右侧 summary）
- `meta`：本次计算使用的 code、日期窗口、是否做了通胀转换等信息

对应实现：`src/fomc/data/modeling/taylor_service.py:build_taylor_series_from_db`

## 关键实现细节（会影响结果解释）

- 通胀序列既可能是“同比百分比”，也可能是“指数水平”。
  - 当前实现会通过 units 判断（含 `Index`/`percent` 等），必要时将指数转换为 YoY（`pct_change(12)`）
- `EFFR` 这类高频序列会 resample 成月度均值；其他序列会做按月对齐与必要的 forward-fill

## 与历史会议的关系

历史会议模拟会把规则输出写入会议级材料：

- `data/meeting_runs/<meeting_id>/taylor.md`

使得你可以在同一会议窗口里把“宏观事件/研报”与“规则对照”放在一起复盘。

## 常见问题定位

- 结果为水平线或空：检查指标库是否已同步、code 是否存在
- 与会议窗口对不齐：检查是否使用 `use_meeting_end`
