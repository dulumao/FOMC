---
slug: data/meetings
title: 会议日历与上下文
order: 21
summary: meeting_id 的来源、会议窗口（月度）怎么推断，以及上下文如何被历史会议/学习模式复用。
---

# 会议日历与上下文

## meeting_id 从哪里来

- 会议日历抓取与缓存：`src/fomc/data/meetings/calendar_service.py`
- 门户侧统一入口：`src/fomc/apps/web/backend.py:get_meeting_context`

在门户里，`meeting_id` 基本等同于“该次会议的结束日期”（用于索引会议与落盘目录）。

## 研报月份窗口怎么推断

历史会议模拟会为每次会议推断一个或两个“研报月份”（用于生成会议窗口内的月度材料）：

- 推断逻辑：`src/fomc/apps/web/backend.py:_compute_meeting_report_months`
- 输出字段：`context["report_months"]`

## 为什么要统一一个 context

同一个 `context` 被两处复用：

- 历史会议模拟：用它生成并缓存会议材料（可复现）
- Fed101：用它作为“示例会议”，把 cell 的窗口与会议对齐

