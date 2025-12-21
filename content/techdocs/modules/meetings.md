---
slug: modules/meetings
title: 会议模拟（讨论/决议）
order: 36
summary: 讨论编排、产物工件、落盘结构与缓存语义。
---

# 会议模拟（讨论/决议）

“会议模拟”是把会前材料包（宏观事件、研报、规则对照）组织成结构化讨论与决议文本的一段编排逻辑。它的工程目标是可复盘：每一步都有明确的中间产物，并写入 `meeting_runs`。

## 职责边界

- 读取会议级材料（macro/nfp/cpi/taylor）
- 构建共享上下文（blackboard）
- 为不同角色生成立场卡、发言、提问与投票
- 生成会议讨论记录（markdown）与决议相关文本（statement/minutes）
- 将中间工件落盘，便于复盘与迭代 prompt

## 关键入口

- 编排入口：`src/fomc/apps/web/backend.py:ensure_meeting_discussion_pack`
- 讨论服务：`src/fomc/data/meetings/discussion_service.py`
- 落盘封装：`src/fomc/data/meetings/run_store.py`

## 讨论的阶段划分（当前实现）

讨论包生成会按固定阶段组织（每阶段都有产物）：

1. **Blackboard**：从 macro/nfp/cpi/taylor 材料抽取事实与不确定性，形成共享上下文
2. **Stance Cards**：为每个角色生成立场卡（判断/风险/偏好）
3. **Opening Statements**：第一轮发言，并收集候选问题
4. **Chair-directed Q&A**：主席选择问题并定向提问，形成第二轮发言与小结
5. **Packages + Vote**：主席提出政策包，各角色给偏好并投票
6. **Statement/Minutes Drafts**：基于投票与小结生成决议相关文本

这些阶段的实现与 prompt 模板主要在 `discussion_service.py` 中。

## Prompt 模板与角色（当前实现）

- 模板目录：`content/prompts/meetings/`
- 模板加载：`discussion_service.py:_load_prompt_template`
- 模板渲染：使用 `string.Template.safe_substitute`（变量语法是 `$var`，而不是 `{var}`）

角色配置：

- 默认角色：`src/fomc/data/meetings/discussion_service.py:DEFAULT_ROLES`
- 每条 prompt run 会写入 `agent_role`，用于把输出与阶段对齐（见 `data/prompt_runs/meetings/`）

## 工件与落盘（meeting_runs）

生成讨论包后，典型会写入：

- `blackboard.json`
- `stance_cards.json`
- `round_summaries.json`
- `packages.json`
- `votes.json`
- `discussion.md`
- `statement.md`
- `minutes_summary.md`

落盘目录：`data/meeting_runs/<meeting_id>/`，并由 `manifest.json` 维护清单与元信息。

## API 与页面对应

- 页面：`/history/<meeting_id>/discussion`、`/history/<meeting_id>/decision`
- API：
  - `POST /api/history/{meeting_id}/discussion?refresh=false`
  - `GET /api/history/{meeting_id}/discussion`
  - `GET /api/history/{meeting_id}/decision`

## refresh / cached 语义

- `refresh=false`：若讨论包相关工件已存在，直接复用（避免重复调用 LLM）
- `refresh=true`：强制重算并覆盖工件（通常用于 prompt 调整后的回归验证）

## 运行日志（prompt_runs）

会议模拟的 LLM 调用日志集中在：

- `data/prompt_runs/meetings/<meeting_id>.jsonl`

每条记录包含角色（agent_role）、prompt 版本、输入与输出文本等，用于复盘某一步的生成逻辑。
