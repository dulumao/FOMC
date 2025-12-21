---
slug: dev/concepts
title: 核心概念与约定
order: 3
summary: meeting_id、refresh、落盘工件、prompt_runs 与 job 机制。
---

# 核心概念与约定

这页集中解释 TechDocs 里会反复出现的几个“工程约定”。理解它们能显著降低阅读代码与排障成本。

## 1) meeting_id：会议索引，也是落盘目录名

- 来源：`src/fomc/data/meetings/calendar_service.py`
- 门户入口：`src/fomc/apps/web/backend.py:get_meeting_context`

在门户里，`meeting_id` 采用“会议结束日期/声明发布日”作为索引，并同时作为落盘目录名：

`data/meeting_runs/<meeting_id>/`

这保证了：同一个会议的所有材料都能被聚合在一个目录下复盘。

## 2) refresh / cached：生成接口的缓存语义

多数“生成类”接口都遵循同一语义（见 `src/fomc/apps/web/main.py` 路由）：

- `refresh=false`：尽量复用已有缓存/落盘产物（稳定、快、可重复调用）
- `refresh=true`：强制重算并覆盖缓存/落盘产物（用于迭代 prompt 或修复数据后回归）

UI 里常见的 `cached=true/false` 字段通常表示“本次请求是否命中了已有产物”。

## 3) meeting_runs：会议级工件目录（可复盘）

会议模拟的输出不是“只返回给前端就结束”，而是写入会议目录并维护清单：

- 目录：`data/meeting_runs/<meeting_id>/`
- 清单：`manifest.json`
- 读写封装：`src/fomc/data/meetings/run_store.py`

工程取舍：

- 页面展示依赖这些工件，从而允许“先生成、后浏览、可重放”
- 即使 LLM/网络不可用，也能通过已有工件维持基础体验

典型工件见 `/techdocs/pipelines` 与 `/techdocs/modules/meetings`。

## 4) prompt_runs：LLM 的可追溯运行日志

所有关键 LLM 调用都会写入 `data/prompt_runs/`（JSONL）。目的不是“统计”，而是：

- 定位某一步为什么生成了某句话（输入是什么、模型参数是什么）
- 对比 prompt 版本的迭代效果
- 让 bug/质量问题具备复现条件

目录示例：

- `data/prompt_runs/macro/`
- `data/prompt_runs/nfp/`、`data/prompt_runs/cpi/`
- `data/prompt_runs/meetings/`

更多见：`/techdocs/modules/llm`

## 5) Jobs：异步生成的实现方式与限制

门户提供了部分异步接口用于前端轮询进度（materials/discussion、指标同步等）。当前实现采用**进程内 Job Registry + 后台线程**：

- 实现：`src/fomc/apps/web/backend.py`（`DbJob`、`_JOBS`、`_run_job`）
- 查询：`GET /api/jobs/{job_id}`、`GET /api/db/jobs/{job_id}`

重要限制（读代码时要记住）：

- Job 状态与日志存在于内存里：进程重启后会丢失
- 日志会做截断（见 `DbJob.as_dict` 的 `logs[-800:]`）

对开发者来说，这个实现足够简单且可用；如果要做长期运行/多进程部署，需要把 Job 与日志外置（不属于当前实现范围）。
