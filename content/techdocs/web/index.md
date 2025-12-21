---
slug: web
title: Web 门户
order: 10
summary: FastAPI + Jinja 的统一入口，路由与集成层的分工。
---

# Web 门户

Web 门户负责两件事：页面路由 + 轻量交互。它不是 SPA，而是服务端渲染（Jinja）+ 少量 JS 的组合。

如果你想快速定位“这个页面背后是谁在干活”，最短路径是：

`main.py`（路由） -> `backend.py`（集成层） -> 各模块（data/reports/rules）

## 入口文件

- 路由与页面：`src/fomc/apps/web/main.py`
- 静态资源：`src/fomc/apps/web/static/`
- 模板：`src/fomc/apps/web/templates/`

## 集成层的职责

`src/fomc/apps/web/backend.py` 负责把数据、研报、模型、LLM 拼成对外接口：

- 会议上下文与会议材料生成
- 研报生成与缓存读取
- 指标查询、健康检查、同步任务
- 会议讨论与决议模拟

## 页面与模板对应

- 首页：`/` → `templates/index.html`
- 历史会议：`/history` 与 `/history/<meeting_id>/*` → `templates/history_*.html`
- 工具箱：`/toolbox` → `templates/toolbox.html`
- FOMC101：`/fed101/*` → `templates/fed101_*.html`
- TechDocs：`/techdocs/*` → `templates/techdocs_*.html`

## 核心页面与接口

- FOMC101：`/fed101` + `/api/fed101/*`
- 历史会议：`/history` + `/api/history/*`
- 工具箱：`/toolbox` + `/api/reports/*`、`/api/indicators`

## 页面渲染方式

门户不是前后端分离 SPA，而是：

- 后端渲染页面骨架（Jinja）
- 前端用少量 JS 完成交互与图表渲染

## API 导航

API 端点清单与参数说明见：`/techdocs/web/api`
