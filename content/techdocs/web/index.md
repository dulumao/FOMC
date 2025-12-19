---
slug: web
title: Web 门户
order: 10
summary: FastAPI + Jinja 的单页式门户：FOMC101 / 历史会议模拟 / 工具箱都从这里出入口。
---

# Web 门户

如果你只想快速定位“这个页面背后是谁在干活”，基本路线是：

`src/fomc/apps/web/main.py`（路由）→ `src/fomc/apps/web/backend.py`（集成层）→ 各功能模块（data/reports/rules/...）

## 入口文件

- 路由与页面：`src/fomc/apps/web/main.py`
- 静态资源：`src/fomc/apps/web/static/`
- 模板：`src/fomc/apps/web/templates/`

## 页面是怎么拼出来的

门户并不是一个“前后端分离 SPA”，而是：

- 后端渲染页面骨架（Jinja 模板）
- 前端用少量 JS 给图表、滚动目录、cell 执行补上交互

## 三个入口对应什么

- FOMC101：`/fed101` 与 `src/fomc/apps/web/fed101.py`
- 历史会议模拟：`/history/...`，主要逻辑在 `src/fomc/apps/web/backend.py`
- 工具箱：`/toolbox`，同样通过 `src/fomc/apps/web/backend.py` 暴露数据与研报/模型接口
