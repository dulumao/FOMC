---
slug: web/techdocs
title: TechDocs（本文档）
order: 12
summary: 与 Fed101 类似的内容系统：Markdown + 文档树 + 本页目录，但不含 cell 与会议上下文。
---

# TechDocs（本文档）

## 内容与路由

- 内容目录：`content/techdocs/`
- 读取与渲染：`src/fomc/apps/web/techdocs.py`
- 路由：`/techdocs`（见 `src/fomc/apps/web/main.py`）

## UI 复用点

TechDocs 直接复用 Fed101 的文档式布局（左侧文档树、中间正文、右侧本页目录）：

- 模板：`src/fomc/apps/web/templates/techdocs_index.html`、`src/fomc/apps/web/templates/techdocs_chapter.html`
- 目录/滚动状态：`src/fomc/apps/web/static/techdocs.js`
- 样式：`src/fomc/apps/web/static/style.css`（复用 `.learning-*` + `docs-*` overlay）

