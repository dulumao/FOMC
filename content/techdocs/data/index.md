---
slug: data
title: 数据与存储
order: 20
summary: 数据库、缓存与落盘目录的清单与用途。
---

# 数据与存储

本项目的数据落点分为三类：**SQLite 数据库（结构化数据）、会议级产物目录（可复盘工件）、LLM 运行日志（可追溯输入输出）**。

## 一览表

| 类别 | 位置 | 用途 | 主要读写模块 |
| --- | --- | --- | --- |
| 指标库 | `data/fomc_data.db` | 经济指标元数据 + 时间序列 | `data/database/`、`data/indicators/` |
| 宏观事件库 | `data/macro_events.db` | 月度事件、摘要、原始文章 | `data/macro_events/` |
| 研报缓存库 | `data/reports.db` | LLM 研报文本缓存 | `apps/flaskapp/app.py` |
| 会议材料 | `data/meeting_runs/<meeting_id>/` | 会议级产物与清单 | `data/meetings/run_store.py` |
| Prompt 运行日志 | `data/prompt_runs/` | LLM 输入输出追溯 | `reports/`、`data/macro_events/`、`data/meetings/` |

## 1) 指标时间序列（`fomc_data.db`）

- ORM 模型：`src/fomc/data/database/models.py`
- DB 连接：`src/fomc/data/database/connection.py`
- 同步/刷新：`src/fomc/data/indicators/`
- 门户接口：`src/fomc/apps/web/backend.py`

详细说明：`/techdocs/modules/economic-data`

## 2) 宏观事件（月报，`macro_events.db`）

- 事件库：`src/fomc/data/macro_events/db.py`
- 生成逻辑：`src/fomc/data/macro_events/month_service.py`
- 门户调用：`src/fomc/apps/web/backend.py`

详细说明：`/techdocs/modules/macro-events`

## 3) 研报缓存（`reports.db`）

研报模块会将部分文本与中间结果缓存到 `reports.db`，以避免重复生成，并支撑工具箱/历史会议复用同一份研报产物。

详细说明：`/techdocs/modules/reports`

## 4) 会议运行缓存（`meeting_runs/<meeting_id>/`）

- 路径：`data/meeting_runs/<meeting_id>/`
- 清单文件：`manifest.json`
- 读写封装：`src/fomc/data/meetings/run_store.py`

详细说明：`/techdocs/data/meetings`

## 5) Prompt 运行日志（`prompt_runs/`）

所有关键 LLM 调用都会落盘到 `data/prompt_runs/`，用于复盘与排查。日志按功能分子目录：

- `macro/`：宏观事件月报与摘要
- `nfp/`、`cpi/`：研报生成链路
- `meetings/`：会议讨论与决议生成链路

详细说明：`/techdocs/modules/llm`

### 命名与查询习惯

- 宏观/研报日志通常是“时间戳 run_id + 月份”的 JSONL 文件，便于按运行批次归档
- 会议日志固定为 `data/prompt_runs/meetings/<meeting_id>.jsonl` 并持续 append，便于按会议复盘全链路

排查时推荐从 `prompt_runs` 入手的场景：

- 输出里出现“编造/口径不一致”：对比 prompt 输入与输出
- refresh 后仍无变化：确认是否真正走到了 LLM 调用（日志是否新增）
