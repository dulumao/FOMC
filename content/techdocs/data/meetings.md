---
slug: data/meetings
title: 会议日历与上下文
order: 21
summary: meeting_id 的来源、会议窗口推断、产物落盘结构。
---

# 会议日历与上下文

## meeting_id 从哪里来

- 会议日历抓取与缓存：`src/fomc/data/meetings/calendar_service.py`
- 门户统一入口：`src/fomc/apps/web/backend.py:get_meeting_context`

在门户里，`meeting_id` 等于会议结束日期（声明发布日），既用作会议索引，也用作落盘目录名：`data/meeting_runs/<meeting_id>/`。

## 研报月份窗口怎么推断

历史会议模拟会为每次会议推断 1-2 个“研报月份”：

- 推断逻辑：`src/fomc/apps/web/backend.py:_compute_meeting_report_months`
- 输出字段：`context["report_months"]`

规则：若两次会议间隔 >= 2 个月，会返回两个月的窗口，便于对比趋势。

## meeting_runs 的结构

每个会议的产物落在：`data/meeting_runs/<meeting_id>/`

典型结构：

- `manifest.json`：产物清单（路径、更新时间、元信息）
- `macro.md`：会议窗口宏观事件摘要
- `nfp.md` / `cpi.md`：会议级研报或兜底文本
- `taylor.md`：规则模型简报
- `discussion.md` / `statement.md` / `minutes_summary.md`：LLM 讨论与决议产物

读写封装入口：`src/fomc/data/meetings/run_store.py`

## manifest.json 的意义

`manifest.json` 是会议目录的“索引文件”。它至少包含：

- `context`：会议上下文（会议元信息、`report_months` 等）
- `artifacts`：各产物的元信息（path/bytes/updated_at/meta）

这样做的好处是：前端可以通过 manifest 快速判断“哪些产物已存在”“是否需要刷新”“最近一次更新时间是什么”，而不需要遍历文件系统。

### 一个最小示例（字段级）

```json
{
  "meeting_id": "2025-05-07",
  "created_at": "2025-12-20T12:00:00Z",
  "updated_at": "2025-12-20T12:05:00Z",
  "context": { "report_months": ["2025-03", "2025-04"] },
  "artifacts": {
    "macro": { "path": "data/meeting_runs/2025-05-07/macro.md", "bytes": 1234, "updated_at": "..." }
  }
}
```

注意：`updated_at` 由 `run_store.save_manifest` 统一维护，每次写入 artifact 都会更新 manifest。

## artifact 命名规则（避免路径注入）

`run_store.artifact_path` 会对 artifact 名称做简化过滤：只保留字母数字与 `-`/`_`，并由 `ext` 决定落盘扩展名（`md/json`）。因此：

- 写入工件请使用固定短名（例如 `macro`、`nfp`、`blackboard`）
- 不要把用户输入直接当作 artifact 名

## 为什么要统一 context

同一个会议上下文被两处复用：

- 历史会议模拟：生成并缓存会议材料
- FOMC101：作为示例会议，让 cell 与会议窗口对齐
