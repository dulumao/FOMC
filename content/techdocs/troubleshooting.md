---
slug: troubleshooting
title: 运行与排错（Runbook）
order: 90
summary: 最短启动路径、数据/LLM 缺失时的降级策略、产物落盘位置与常见问题定位。
---

# 运行与排错（Runbook）

> 目标：把运行风险降到最低；使用时建议优先复用**已缓存产物**，避免把体验押在实时生成上。

## 1) 最短启动路径

```bash
pip install -r requirements.txt
pip install -e .
uvicorn fomc.apps.web.main:app --app-dir src --reload --port 9000
```

打开：`http://127.0.0.1:9000/`

## 2) 两个关键环境变量（以及无 Key 的口径）

在仓库根目录 `.env`：

- `DEEPSEEK_API_KEY`：用于讨论/决议、摘要类文本生成
  - 无 Key：页面仍可打开，部分内容会使用本地 fallback 文本；讨论/决议等内容可能缺失或降级
- `FRED_API_KEY`：用于同步经济指标（没有它也能启动门户）
  - 无 Key：图表/模型可能缺数据（取决于本地指标库是否已同步）

## 3) 建议的自测与理解路径

1. `/history` → 选择一个 `meeting_id`
2. `/history/<meeting_id>/overview` → 看会议上下文与 materials 步骤
3. 依次打开：`macro → nfp → cpi → model → discussion → decision`
4. 再去 `/fed101`：对照学习章节理解每一步的输入/输出与假设

## 4) 产物落盘在哪里（遇到问题先看这里）

- 会议产物：`data/meeting_runs/<meeting_id>/`
  - `manifest.json`（清单与更新时间）
  - `macro.md` / `nfp.md` / `cpi.md` / `taylor.md`
  - `discussion.md` / `statement.md` / `minutes_summary.md`
- Prompt 运行日志：`data/prompt_runs/`
- 指标库：`data/fomc_data.db`
- 宏观事件库：`data/macro_events.db`
- 研报缓存：`data/reports.db`

## 5) 最常见的 4 类故障与定位顺序

1. 页面打不开 / 500：先看 `uvicorn` 控制台报错；再从 `src/fomc/apps/web/main.py` 定位路由
2. 历史会议提示不可模拟：检查 `history_cutoff`（见 `src/fomc/apps/web/backend.py`）
3. 某一步内容为空：先看 `data/meeting_runs/<meeting_id>/manifest.json` 是否有对应 artifact
4. LLM 报错：确认 `.env` 的 `DEEPSEEK_API_KEY`，并查看 `data/prompt_runs/` 里的错误记录

补充：若你看到“Job 一直转圈但刷新后消失”，大概率是进程重启或 reload 导致 Job Registry 丢失（见 `/techdocs/dev/concepts` 的 Jobs 说明）。

## 6) 典型错误长什么样（以及对应处理）

### `DEEPSEEK_API_KEY is missing`

- 触发点：任一调用 `LLMClient()` 的链路（`src/fomc/infra/llm.py`）
- 处理：
  - 在根目录 `.env` 填写 `DEEPSEEK_API_KEY`
  - 重启 `uvicorn`（确保进程重新加载环境变量）

### 会议讨论报 “No JSON object found” 或 JSON parse error

- 触发点：会议讨论阶段会要求 LLM 输出 JSON，并做 best-effort 抽取（`src/fomc/data/meetings/discussion_service.py:_extract_json_object`）
- 处理建议：
  - 查看 `data/prompt_runs/meetings/<meeting_id>.jsonl` 找到对应阶段的原始输出
  - 适当降低生成温度、提高 JSON 约束（通常通过 prompt 模板修正，而不是在代码里硬修）
  - `refresh=true` 做一次回归，确认缓存没有遮蔽修复

### 宏观事件为空或 DDG 报 warn

- 触发点：`src/fomc/data/macro_events/month_service.py` 会打印 `[warn] DDG search failed ...`
- 处理：
  - 先确认网络可用、月份参数合法（`YYYY-MM`）
  - 若只想复用已有缓存：不要 `refresh`，直接读 DB 月份记录

### PDF 导出失败（Playwright）

- 触发点：调用 `/api/reports/*.pdf` 或宏观月报 PDF 导出
- 处理：
  - 安装：`playwright install chromium`
  - 若环境不支持 PDF：仍可使用 HTML/Markdown 版本（这不影响会议模拟落盘）
