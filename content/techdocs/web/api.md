---
slug: web/api
title: HTTP API
order: 12
summary: 门户对外 API 端点清单、参数与缓存语义（以当前实现为准）。
---

# HTTP API

本文档按用途列出门户的主要 API，并解释常见参数与缓存语义。路由定义集中在 `src/fomc/apps/web/main.py`，具体编排逻辑集中在 `src/fomc/apps/web/backend.py`。

> 约定：多数“生成类”接口都支持 `refresh`。`refresh=false` 会尽量复用已有缓存/落盘产物；`refresh=true` 会强制重算并覆盖落盘。

## 通用语义（refresh / cached / 产物落盘）

对“历史会议材料、讨论包、宏观月报、研报”等生成类能力，一般同时具备：

- `refresh`：是否强制重算（语义见 `/techdocs/dev/concepts`）
- `cached`：是否命中已有缓存（具体字段名以返回为准）
- 产物落盘：会议级产物落在 `data/meeting_runs/<meeting_id>/`；LLM 运行日志落在 `data/prompt_runs/`

## 会议日历与上下文

- `GET /api/meetings?refresh=false`
  - 返回会议列表（历史会议 + 标签等）
- `GET /api/meetings/{meeting_id}?refresh=false`
  - 返回单个会议元信息
- `GET /api/history/{meeting_id}/context?refresh_calendar=false`
  - 返回会议上下文（含 `report_months`）
- `GET /api/history/{meeting_id}/run?refresh_calendar=false`
  - 确保 `data/meeting_runs/<meeting_id>/manifest.json` 存在并写入 context

## 宏观事件（月报）

- `GET /api/macro-events?month=YYYY-MM&refresh=false`
  - 返回月度事件与月报摘要
- `GET /api/macro-events/months?order=desc`
  - 返回已有月份列表
- `POST /api/macro-events/refresh?month=YYYY-MM`
  - 强制刷新某月事件与摘要

## 研报（NFP/CPI）

- `GET /api/reports/labor?month=YYYY-MM&refresh=false`
  - 返回非农研报的结构化数据（图表数据 + 摘要/文本）
- `GET /api/reports/cpi?month=YYYY-MM&refresh=false`
  - 返回 CPI 研报的结构化数据
- `GET /api/reports/labor.pdf?month=YYYY-MM&refresh=false`
- `GET /api/reports/cpi.pdf?month=YYYY-MM&refresh=false`
  - 导出 PDF（若启用 Playwright）

## 指标库（经济数据）

- `GET /api/indicators`
  - 返回指标分类树与元信息
- `GET /api/indicator-data?code=<series_code>&date_range=5Y`
  - 返回单条序列的绘图数据
- `GET /api/db/indicator-health`
  - 返回指标同步与缺口健康状态
- `POST /api/db/jobs/sync-indicators`
- `POST /api/db/jobs/refresh-indicator?code=<series_code>`
  - 启动同步/刷新任务（异步 job）

## 规则模型（Taylor）

- `POST /api/models/taylor`
  - 计算 Taylor 系列规则（参数在 JSON body 中；默认会从指标库读取必要序列）

## 历史会议：材料生成与读取

- `GET /api/history/{meeting_id}/materials/{kind}`
  - `kind`：`macro|nfp|cpi|taylor`
  - 返回落盘缓存（若存在）与渲染后的 HTML
- `POST /api/history/{meeting_id}/materials/{kind}?refresh=false`
  - 生成并落盘某类材料；`kind=all` 可一次生成全部材料
- `POST /api/history/{meeting_id}/jobs/materials/{kind}?refresh=false`
  - 异步生成（返回 `job_id`，用于轮询）

## 历史会议：讨论与决议

- `GET /api/history/{meeting_id}/discussion`
  - 返回 `discussion.md`（以及 blackboard/stance_cards 等 JSON 工件）
- `POST /api/history/{meeting_id}/discussion?refresh=false`
  - 生成讨论包并落盘（见 `/techdocs/modules/meetings`）
- `POST /api/history/{meeting_id}/jobs/discussion?refresh=false`
  - 异步生成讨论包
- `GET /api/history/{meeting_id}/decision`
  - 返回 statement/minutes_summary/votes 等决议工件

## Job 轮询

- `GET /api/jobs/{job_id}`
  - 返回任务状态与日志片段（用于前端轮询显示进度）
- `GET /api/db/jobs/{job_id}`
  - 同上（指标同步任务也使用该接口轮询）

Job 的字段形状（当前实现）：

- `status`：`queued|running|success|error`
- `logs`：日志行数组（会截断）
- `error`：错误字符串（若失败）

注意：Job 目前保存在进程内存里（`backend.py` 的 `_JOBS`），进程重启会丢失；因此它是“前端体验优化”，不是持久化任务系统。
