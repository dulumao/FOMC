---
slug: dev/setup
title: 开发环境与启动
order: 2
summary: 从零跑起来：依赖、环境变量、数据初始化与验证路径。
---

# 开发环境与启动

本页的目标是把“我能跑起来，并且能自测关键路径”这件事变得确定、可复现。

## 1) 前置条件

- Python：3.10+（见 `README.md` 徽标）
- 建议使用虚拟环境（venv/conda 均可）
- 若需要导出 PDF：安装 Playwright（可选）

## 2) 安装依赖与启动门户

```bash
pip install -r requirements.txt
pip install -e .
uvicorn fomc.apps.web.main:app --app-dir src --reload --port 9000
```

打开：`http://127.0.0.1:9000/`

入口文件：

- 路由：`src/fomc/apps/web/main.py`
- 集成层：`src/fomc/apps/web/backend.py`

## 3) 环境变量（.env）

仓库根目录 `.env`（已在仓库中提供示例）：

- `FRED_API_KEY`
  - 用途：同步经济指标（`data/fomc_data.db`）
  - 没有它：门户仍可启动，但图表/模型可能无数据（取决于本地库是否已同步）
- `DEEPSEEK_API_KEY`
  - 用途：宏观摘要、会议讨论/投票、Statement/Minutes 等文本生成
  - 没有它：系统会在部分链路走 fallback 或返回降级结果；但“可复盘落盘”仍成立（会留下空/兜底工件，便于定位）

LLM 可选配置（见 `src/fomc/infra/llm.py`）：

- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `DEEPSEEK_TIMEOUT`
- `DEEPSEEK_RETRIES`

## 4) 首次运行：初始化与同步数据

### 初始化指标数据库（必需一次）

```bash
python -m fomc.apps.cli.init_database
```

生成/更新：`data/fomc_data.db`

### 同步经济指标（可选但强烈建议）

```bash
python -m fomc.apps.cli.process_all_indicators --start-date 2010-01-01
```

指标清单来自：`docs/US Economic Indicators with FRED Codes.xlsx`  
同步实现入口：`src/fomc/data/indicators/indicator_sync_pipeline.py`

## 5) PDF 导出（可选）

研报/宏观月报的 PDF 导出依赖 Playwright：

```bash
playwright install chromium
```

对应实现见：

- `src/fomc/apps/flaskapp/app.py`（研报 PDF）
- `src/fomc/apps/web/backend.py`（宏观月报 PDF）

## 6) 启动后的自测清单（建议按顺序）

1. 首页能打开：`/`
2. 指标浏览器能返回目录：`/toolbox` → 指标树加载成功（或直接 `GET /api/indicators`）
3. 选择一个会议：`/history`（日历列表可加载）
4. 生成会议材料：`/history/<meeting_id>/overview`（会看到 materials 逐步生成）
5. 查看落盘：`data/meeting_runs/<meeting_id>/manifest.json`

如果你在第 2/4 步遇到“内容为空/按钮卡住”，先读 `/techdocs/dev/concepts`（refresh/落盘/jobs 的语义），再看 `/techdocs/troubleshooting`。
