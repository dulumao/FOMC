---
slug: dev/workflows
title: 开发者工作流
order: 4
summary: 常见修改点与排查路径：指标、研报、会议模拟、Prompt 迭代与落盘复盘。
---

# 开发者工作流

本页聚焦“最常改什么、改完怎么验证、出问题先看哪”，尽量把路径写短。

## 1) 新增/修改经济指标

目标：让指标出现在工具箱目录里，并能被研报/规则模型复用。

1. 编辑指标清单：`docs/US Economic Indicators with FRED Codes.xlsx`
2. 重新同步（全量或增量）：
   - CLI：`python -m fomc.apps.cli.process_all_indicators --start-date 2010-01-01`
   - 或门户异步任务：`POST /api/db/jobs/sync-indicators`
3. 验证：
   - `GET /api/indicators` 是否出现新 code
   - `GET /api/indicator-data?code=<series_code>&date_range=5Y` 是否有数据

排查顺序：

- 指标元信息是否入库：`data/fomc_data.db`（表结构见 `src/fomc/data/database/models.py`）
- 是否缺数据：`GET /api/db/indicator-health`

## 2) 迭代研报文本（NFP/CPI）

研报链路的核心分工：

- 图表与结构化摘要：`src/fomc/apps/flaskapp/app.py`
- LLM 文本：`src/fomc/reports/report_generator.py`
- Prompt 模板：`content/prompts/reports/`
- 缓存：`data/reports.db`
- 运行日志：`data/prompt_runs/nfp/`、`data/prompt_runs/cpi/`

验证建议：

- 先用工具箱跑单月：`/toolbox`（更快）
- 再用历史会议让它进入 `meeting_runs`：`/history/<meeting_id>/overview`

如果调整了 prompt，建议配合 `refresh=true` 做一次回归，确保缓存没有遮蔽变化（见 `/techdocs/dev/concepts`）。

## 3) 迭代会议讨论/决议（meetings）

会议讨论包入口：

- `src/fomc/apps/web/backend.py:ensure_meeting_discussion_pack`
- `src/fomc/data/meetings/discussion_service.py`

工件落盘：

- `data/meeting_runs/<meeting_id>/`（`blackboard.json`、`stance_cards.json`、`discussion.md`、`votes.json`、`statement.md` 等）

建议的验证方式：

1. 选定一个 `meeting_id`
2. 先生成材料：`POST /api/history/{meeting_id}/materials/all?refresh=false`
3. 再生成讨论：`POST /api/history/{meeting_id}/discussion?refresh=true`
4. 打开目录对比产物：
   - `manifest.json` 的更新时间
   - `discussion.md` 是否符合阶段组织
   - `data/prompt_runs/meetings/<meeting_id>.jsonl` 是否记录了各阶段输入输出

## 4) 修改 Web 页面/交互

最短路径：

- 路由与 API：`src/fomc/apps/web/main.py`
- 页面编排与数据组装：`src/fomc/apps/web/backend.py`
- 模板：`src/fomc/apps/web/templates/`
- JS：`src/fomc/apps/web/static/`

历史会议页面的交互通常通过“启动 job → 轮询状态 → 渲染日志/结果”实现；轮询协议见 `/techdocs/web/api`，实现见模板内的脚本片段（`templates/history_*.html`）。
