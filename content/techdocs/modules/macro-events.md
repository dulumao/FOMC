---
slug: modules/macro-events
title: 宏观事件
order: 32
summary: 新闻 -> 事件 -> 月报：抓取、筛选、聚类、摘要、落盘。
---

# 宏观经济事件模块

## 职责边界

把一个月的宏观新闻压缩成“可用于会议讨论”的事件与摘要，输出两类产物：

- **月度摘要**（Markdown）
- **事件列表**（类型、重要度、摘要、来源）

这不是“宏观研究结论模块”。它提供的是可追溯的事实链路与冲击脉络：讨论可以基于事件库形成解释，但事件库本身不替代研报判断。

## 关键入口

- 生成/确保某月事件：`src/fomc/data/macro_events/month_service.py:ensure_month_events`
- DB 读写：`src/fomc/data/macro_events/db.py`
- 门户调用：`src/fomc/apps/web/backend.py`

## 处理流程（当前实现，高层）

1. 构造查询集合（按 report_type）
2. 新闻检索（DDG）
3. 过滤与分类（主题/冲击/渠道）
4. 事件候选聚类
5. 重要度排序与截断
6. LLM 摘要与月报生成
7. 写入 SQLite + 可选落盘

对应实现（更贴近代码）：

- 入口：`src/fomc/data/macro_events/month_service.py:ensure_month_events`
  - 先查 `months` 记录，命中且 `status=completed` 时默认直接复用
  - `force_refresh=true` 才会重新检索/聚类/摘要并覆盖写库
  - 两阶段检索：先用统一 queries 拉一批候选，再用 LLM 提炼关键词做第二轮补检索
  - 可选抓正文：挑选部分 URL 拉取 full text，并落库到 `raw_articles` 便于 UI 展示与复盘

## 数据模型（macro_events.db）

- `months`：月度记录（状态、月报摘要、统计）
- `events`：事件明细（重要度、冲击类型、传导渠道、摘要、来源列表）
- `raw_articles`：原始新闻正文与片段（用于聚类与摘要输入）

## 数据落点

- 事件库：`data/macro_events.db`
- 会议级宏观摘要：`data/meeting_runs/<meeting_id>/macro.md`

## 可追溯日志

- Prompt 运行日志：`data/prompt_runs/macro/`

## 输出形状（门户侧）

- `GET /api/macro-events?month=YYYY-MM`
  - 返回 `events[]`（含 title/summary/shock/channel/importance/source_urls）
  - 返回 `monthly_summary_md`/`monthly_summary_html`

## refresh 语义

- `refresh=false`：若该月 `months` 已生成且摘要存在，直接复用
- `refresh=true`：强制重新检索/聚类/摘要并覆盖写库（用于质量迭代）

## 调试建议

- 页面显示“无事件/无摘要”时：
  - 先检查 `macro_events.db` 是否有该月记录
  - 再看是否启用 refresh 或 LLM 是否可用
