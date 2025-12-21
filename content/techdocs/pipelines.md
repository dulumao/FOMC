---
slug: pipelines
title: 历史会议模拟（流程）
order: 40
summary: 一场会议如何被跑完：生成、缓存、刷新与落盘。
---

# 历史会议模拟（流程）

历史会议模拟是本项目的“主流程入口”。它做的事情是：给定一个 `meeting_id`，把会前材料组织出来（宏观事件、研报、规则对照），再生成讨论与决议相关文本，并把所有产物落盘到 `data/meeting_runs/<meeting_id>/`，使得整场会议可以被重放与复盘。

阅读建议：

- 先读 `/techdocs/dev/concepts`（理解 refresh/落盘/jobs）
- 再读本页（理解调用顺序与工件依赖）

## 页面入口（UI）

- 入口页面：`/history`
- 会议页：`/history/<meeting_id>/...`
- 路由：`src/fomc/apps/web/main.py`

## 核心编排在哪里

历史会议的流程编排集中在：

- `src/fomc/apps/web/backend.py`：作为门户与底层模块的集成层
- `src/fomc/data/meetings/run_store.py`：会议产物的读写与清单维护

## 一次会议的产出

落盘目录：`data/meeting_runs/<meeting_id>/`

- `macro.md`：会议窗口宏观摘要
- `nfp.md` / `cpi.md`：会议级研报
- `taylor.md`：规则模型简报
- `discussion.md`：委员讨论逐字记录
- `statement.md` / `minutes_summary.md`：决议与纪要
- `manifest.json`：产物清单（更新时间/大小/元信息）

## 运行步骤（按真实调用顺序）

1. **获取会议上下文（context）**
   - 日历抓取与缓存：`calendar_service.py`
   - 推断 `report_months`：`backend.py:_compute_meeting_report_months`
   - 写入 `manifest.json` 的 `context`：`run_store.set_context`

2. **生成会前材料（materials）**
   - `macro`：宏观事件月报 → 会议窗口摘要（写 `macro.md`）
   - `nfp`：按 `report_months` 生成月度研报 → 会议级简报（写 `nfp.md`）
   - `cpi`：同上（写 `cpi.md`）
   - `taylor`：从指标库计算规则对照（写 `taylor.md`）

3. **会议讨论与决议（discussion/decision）**
   - Blackboard：从 `macro/nfp/cpi/taylor` 抽取事实与不确定性
   - Stance Cards：为角色生成立场卡
   - Statements：第一轮发言
   - Chair Q&A：主席提问与定向发言
   - Packages + Vote：提出政策包并投票
   - Drafts：生成 Statement/Minutes 摘要

4. **落盘与缓存**
   - 写入 `meeting_runs` 的 markdown/json 工件
   - 更新 `manifest.json`（路径、字节数、updated_at、meta）

## 工件依赖关系（为什么要按这个顺序）

历史会议的“讨论/决议”不是凭空生成，而是依赖会前材料包：

- `blackboard` 依赖：`macro/nfp/cpi/taylor`
- `stance_cards` 依赖：`blackboard`
- `opening_statements` 依赖：`stance_cards`
- `chair_qna` 依赖：`opening_statements`
- `packages/votes` 依赖：`chair_qna`
- `statement/minutes` 依赖：`votes` + `round_summaries`

这也是为什么排查“讨论质量/决议不一致”时，通常要先确认会前材料是否与会议窗口对齐。

## cached / refresh 的含义

- `cached=true`：对应产物已存在，未强制刷新
- `refresh=true`：强制重新生成并覆盖落盘产物

## API 对照（UI 背后调用什么）

材料读取与生成：

- `GET /api/history/{meeting_id}/materials/{kind}`：读取落盘缓存（macro/nfp/cpi/taylor）
- `POST /api/history/{meeting_id}/materials/{kind}?refresh=false`：生成并落盘
- `POST /api/history/{meeting_id}/materials/all?refresh=false`：一次生成全部材料

讨论与决议：

- `POST /api/history/{meeting_id}/discussion?refresh=false`：生成讨论包并落盘
- `GET /api/history/{meeting_id}/discussion`：读取讨论工件
- `GET /api/history/{meeting_id}/decision`：读取决议工件

异步任务（前端轮询）：

- `POST /api/history/{meeting_id}/jobs/materials/{kind}`、`POST /api/history/{meeting_id}/jobs/discussion`
- `GET /api/jobs/{job_id}`

## 常见问题定位

- 产物为空：先看 `manifest.json` 是否存在对应 artifact
- 会议不可模拟：检查是否超过 `history_cutoff`
