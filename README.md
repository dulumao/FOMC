# FOMC 宏观数据情报工作台

面向 FOMC 场景的本地化数据与研报工作台：抓取/清洗经济数据，提供指标浏览、可视化，以及基于 DeepSeek 的自动研报。

## 你能做什么？
- 浏览经济数据库：按分类选择指标，查看趋势图/数据表，附带 FRED 链接。
- 一键生成非农专题研报：自动绘制图1~图4，生成结构化解读，可导出 PDF（当前无书签大纲）。
- 数据更新：脚本化增量抓取与预处理，SQLite 持久化。

## 快速开始
1) 安装依赖
```bash
pip install -r requirements.txt
```
2) 配置环境变量 `.env`
```
FRED_API_KEY=your_key          # 申请自 https://fred.stlouisfed.org/docs/api/api_key.html
DEEPSEEK_API_KEY=your_key      # 如需生成研报
```
3) 初始化/更新数据
```bash
python init_database.py                     # 初始化空库
python process_all_indicators.py            # 一键全量/增量处理（默认从 2010 抓取）
# 或指定历史区间
python process_all_indicators.py --start-date 2015-01-01
```
4) 启动 Web 工作台
```bash
cd webapp
python app.py
# 打开 http://localhost:5000
```

## 目录导航（精简）
```
data/                 数据摄取与清洗
├─ charts/            图1~图4数据管道（非农、行业贡献、失业率比较）
├─ collect_economic_data_from_excel.py   冷启动抓取 + 分类层级生成
├─ data_updater.py    增量更新调度
├─ preprocessing.py   单位/频率标准化
└─ rate_limited_fred_api.py 等 FRED 客户端

database/             SQLAlchemy Base 与模型定义
reports/              DeepSeek 研报生成（prompt 与文本后处理）
webapp/               Flask 前端与 API（templates/index.html 为主要页面）
requirements.txt      运行依赖
```

## Web 工作台速览
- 经济数据浏览：左侧分类树 + 时间范围/排序过滤；右侧 Chart.js 趋势图 + 数据表。
- 研报工作台：选择月份后生成非农研报，包含四张图与正文；侧栏提供导航与关键经济指标摘要（含 FRED 快捷链接）；支持 PDF 导出（当前无书签）。

## 常用脚本
- `init_database.py`：创建数据库表。
- `process_all_indicators.py`：同步分类、抓取、预处理并写库（推荐入口）。
- `update_fred_urls.py`：修正数据库中的 FRED 链接。
- `data/data_updater.py`：面向生产的增量更新循环。

## 注意事项 / 限制
- PDF 导出当前未含书签/大纲；如需书签需额外的 PDF 后处理。
- DeepSeek 生成研报需要设置 `DEEPSEEK_API_KEY`，否则仅呈现图表和占位文本。
- 本项目使用本地 SQLite，生产环境可根据 SQLAlchemy 链接改为其他数据库。
