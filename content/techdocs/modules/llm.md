---
slug: modules/llm
title: LLM 基础设施
order: 35
summary: 统一调用封装、Prompt 模板组织、运行日志与可追溯性。
---

# LLM 基础设施

本项目把 LLM 当作一种“外部依赖服务”。工程目标不是堆框架，而是做到：调用入口统一、模板可迭代、输出可追溯、失败可降级。

## 职责边界

- 提供统一的 LLM 调用客户端（模型/URL/超时/重试等策略集中管理）
- 提供 Prompt 模板的组织方式（把 prompt 从代码里外置）
- 提供运行日志落盘（可回放输入与输出）

它不做的事情：

- 不引入复杂的链式编排框架（例如 LangChain）作为硬依赖
- 不提供长期记忆/向量检索统一层（当前需求不强）

## 关键入口

- 统一客户端：`src/fomc/infra/llm.py`
  - 典型调用：`LLMClient.chat([...])`
  - 兼容别名：`DeepSeekClient`（历史代码仍使用 `.generate`）
- 会议模拟的 prompt 与日志：`src/fomc/data/meetings/discussion_service.py`
- 研报的 prompt 与日志：`src/fomc/reports/`、`src/fomc/apps/flaskapp/`（以及 `content/prompts/reports/`）

## 配置（.env）

核心：

- `DEEPSEEK_API_KEY`

可选（用于兼容不同部署/模型）：

- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `DEEPSEEK_TIMEOUT`
- `DEEPSEEK_RETRIES`

## Prompt 模板组织

模板采用 Markdown 文件并携带 frontmatter：

- 研报：`content/prompts/reports/`
- 会议模拟：`content/prompts/meetings/`

约定：

- frontmatter 中存 `prompt_id` / `prompt_version` / `system_prompt`
- 文件正文为 user prompt（通常会注入结构化数据）
- 研报模板使用 `str.format`（变量语法 `{var}`），会议模板使用 `string.Template`（变量语法 `$var`）

这套组织方式的好处是：prompt 可以像代码一样版本化、对比与回滚。

## 运行日志（可追溯性）

所有关键调用都会写入 `data/prompt_runs/`（按模块分子目录）：

- `data/prompt_runs/macro/`
- `data/prompt_runs/nfp/`
- `data/prompt_runs/cpi/`
- `data/prompt_runs/meetings/`

日志通常包含：

- system/user prompt 原文
- 模型参数（model/temperature/max_tokens 等）
- 输出文本
- 时间戳与关联标识（如 `meeting_id`）

### JSONL 字段（当前实现的共同子集）

不同模块的记录字段略有差异，但一般会包含：

- `prompt_id` / `prompt_version`
- `agent_role`（研报审阅链、会议阶段会使用）
- `model` / `temperature` / `max_tokens`
- `timestamp`
- `system_prompt` / `user_prompt` / `output_text`

研报与宏观月报的日志文件通常按 “run_id + month” 命名；会议讨论的日志文件按 `meeting_id` 固定命名并持续 append（见 `discussion_service.py:_log_prompt_run`）。

## 输出约束（一致性与可用性）

为了减少“看起来像但不可复盘”的输出，项目在 prompt 层采用强约束：

- 明确禁止编造：不得引入输入中不存在的数据与事件
- 输入缺失时必须显式声明
- 需要结构化数据时使用 JSON schema（便于渲染与落盘）
