---
slug: modules/reports
title: 研报（NFP/CPI）
order: 33
summary: 图表生成、LLM 撰写、多智能体校对与落盘缓存。
---

# 研报模块（NFP/CPI）

## 职责边界

把一堆指标时间序列压缩成少数图表与要点，输出“可用于讨论”的材料：

- NFP（就业）
- CPI（通胀）

研报模块输出两类东西：

- 面向页面展示的结构化数据（图表数据、关键指标、摘要）
- 面向会议复盘的会议级材料（按 `meeting_id` 落盘的 markdown 简报）

## 关键入口

- 研报生成（图表 + 文本）：`src/fomc/apps/flaskapp/app.py`
- LLM 研报生成器：`src/fomc/reports/report_generator.py`
- 门户封装：`src/fomc/apps/web/backend.py`

## 生成流程（当前实现）

1. 从指标库拉取所需序列
2. 生成图表与摘要数据
3. 构造 LLM 输入（含宏观事件上下文）
4. 多智能体审阅（Consistency/Completeness/Logic/Editor）
5. 结果写入 `reports.db` 并返回门户

多智能体开关：

- 环境变量：`FOMC_REPORT_MULTI_AGENT`
  - `1`/未设置：启用多智能体审阅
  - `0`：只生成草稿，不做审阅链路

## 缓存与落盘

- 研报文本缓存：`data/reports.db`（避免重复生成）
- 会议级落盘：`data/meeting_runs/<meeting_id>/nfp.md`、`data/meeting_runs/<meeting_id>/cpi.md`

## 模板与 Prompt

- Prompt 模板目录：`content/prompts/reports/`
  - 主研报：`nfp_report.md`、`cpi_report.md`
  - 审阅链：`report_consistency.md`、`report_completeness.md`、`report_logic.md`、`report_editor.md`
- Prompt 运行日志：`data/prompt_runs/<report_type>/`
  - 命名：`<run_id>_<YYYY-MM>.jsonl`（见 `report_generator.py:_record_prompt`）

## 复用方式

三处复用同一份研报结果：

- 工具箱：完整研报与图表
- 历史会议：会议窗口内生成并缓存研报
- FOMC101：把研报图表拆成 cell 逐张讲解

## PDF 导出（可选）

若启用 Playwright，可通过：

- `GET /api/reports/labor.pdf`
- `GET /api/reports/cpi.pdf`

导出 PDF（用于保存或分享）。

## 输出形状（门户侧）

- `GET /api/reports/labor?month=YYYY-MM&refresh=false`
- `GET /api/reports/cpi?month=YYYY-MM&refresh=false`

门户侧的 `refresh=true` 会透传到 Flask 研报服务的 `refresh_llm=true`（见 `src/fomc/apps/web/backend.py:generate_*_report`），用于绕开文本缓存做回归验证。
