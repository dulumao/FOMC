---
slug: web/techdocs
title: TechDocs（本文档）
order: 13
summary: 技术文档的内容系统与渲染方式。
---

# TechDocs（本文档）

## 内容与路由

- 内容目录：`content/techdocs/`
- 读取与渲染：`src/fomc/apps/web/techdocs.py`
- 路由：`/techdocs`（见 `src/fomc/apps/web/main.py`）

## UI 复用点

TechDocs 复用 FOMC101 的文档式布局：

- 模板：`src/fomc/apps/web/templates/techdocs_index.html`、`src/fomc/apps/web/templates/techdocs_chapter.html`
- 目录/滚动状态：`src/fomc/apps/web/static/techdocs.js`
- 样式：`src/fomc/apps/web/static/style.css`
