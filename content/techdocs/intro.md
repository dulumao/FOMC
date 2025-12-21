---
slug: intro
title: 导读
order: 1
summary: 当前实现的技术总览与阅读路径。
---

# 技术导读

TechDocs 面向“要读代码、要定位问题、要解释系统怎么跑”的读者。它只描述**当前实现**（What is），不讨论理想蓝图（见 `docs/development.md`）。

这个项目的核心目标很简单：用一套底层能力，撑起三种入口与一条可复盘的会议流程。

## 适用人群

- 想在 10 分钟内建立全局：先读 `/techdocs/architecture` + `/techdocs/data`
- 想定位“某个页面背后是谁在干活”：读 `/techdocs/web`
- 想理解“历史会议模拟怎么生成/怎么缓存/落盘长什么样”：读 `/techdocs/pipelines` + `/techdocs/data/meetings`
- 想理解某个能力模块的边界：读 `/techdocs/modules/*`
- 想把项目跑起来并能自测：先读 `/techdocs/dev/setup` + `/techdocs/dev/workflows`

## 最短启动（开发者）

```bash
pip install -r requirements.txt
pip install -e .
uvicorn fomc.apps.web.main:app --app-dir src --reload --port 9000
```

打开：`http://127.0.0.1:9000/`

完整的环境变量、数据初始化、PDF 导出等见：`/techdocs/dev/setup`

## 一句话架构心智模型

你可以把系统理解为三层：

第一层是 Web 门户（FastAPI + Jinja），负责路由与页面；第二层是集成层 `src/fomc/apps/web/backend.py`，负责把数据/研报/规则/LLM 串起来；第三层是各功能模块（指标库、宏观事件、研报、规则模型、会议讨论）与数据落盘（SQLite + `data/meeting_runs/` + `data/prompt_runs/`）。

## 两个关键概念

- `meeting_id`：会议索引（以会议结束日期/声明发布日表示），也是会议产物的落盘目录名
- 可复盘落盘：会议级产物统一写入 `data/meeting_runs/<meeting_id>/`，并由 `manifest.json` 维护清单与元信息

## 系统分层（当前实现）

1. **Web 门户**：FastAPI + Jinja，负责路由与页面渲染
2. **集成层**：`src/fomc/apps/web/backend.py`，统一串联数据/研报/模型/LLM
3. **功能模块**：经济数据、宏观事件、研报生成、规则模型、会议讨论
4. **数据与缓存**：多个 SQLite + `data/meeting_runs` + `data/prompt_runs`

你可以把这个项目理解为：

- 一个“门户”统一入口
- 一组可组合的底层模块
- 一套强调可复盘的落盘策略

如果你只记住一个实现细节：多数“生成类能力”都同时具备 **refresh 语义**与**落盘产物**，这也是排查问题时最省时的切入点（见 `/techdocs/dev/concepts`）。
