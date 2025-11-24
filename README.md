# FOMC 宏观数据情报工作台

面向非技术用户的本地化宏观数据小工具：自动抓取清洗经济数据，提供可视化浏览，一键生成非农/CPI 研报，并可导出 PDF。

## 核心功能
- 经济指标浏览：按分类挑选指标，查看趋势图和数据表，附带 FRED 链接。
- 研报生成：输入月份即可生成专题研报  
  - 非农：自动绘制新增就业、行业贡献、失业率等图表，生成解读。  
  - CPI：自动绘制同比/环比图表，生成分项拉动表。
- PDF 导出：非农与 CPI 研报均可一键导出（包含图表和表格）。
- 数据更新：脚本化抓取与增量更新，数据存储在本地 SQLite。

## 简明架构
- 数据层：从 FRED 抓取并清洗，存入本地 SQLite；`process_all_indicators.py` 负责一键更新。
- 服务层：Flask 提供 API 和页面渲染；`webapp/app.py` 同时渲染图表、生成 PDF。
- 前端层：单页式界面（`webapp/templates/index.html`），显示图表、表格并触发研报/PDF 导出。
- AI 生成（可选）：如配置 DeepSeek API，可自动写研报正文；未配置时仍可生成图表和表格。

## 快速上手
1) 安装依赖  
```bash
pip install -r requirements.txt
```
2) 配置 `.env`（文本文件即可）  
```
FRED_API_KEY=你的FRED密钥       # https://fred.stlouisfed.org
DEEPSEEK_API_KEY=可选，用于自动写研报
```
3) 初始化并更新数据  
```bash
python init_database.py
python process_all_indicators.py            # 默认从 2010 年开始抓取
# 如需指定起点：python process_all_indicators.py --start-date 2015-01-01
```
4) 启动 Web 工作台  
```bash
cd webapp
python app.py
# 浏览器打开 http://localhost:5000
```

## 如何生成研报
- 非农研报：在页面选择月份，点击“生成非农研报”→ 可查看并导出 PDF。
- CPI 研报：在页面选择月份，点击“生成CPI图表与研判”→ 可查看并导出 PDF（含分项拉动表、可视化条形+数值）。
- 若未设置 DEEPSEEK_API_KEY，仍可生成图表和表格，正文会使用简短占位描述。

## 目录速览
```
data/          数据抓取与清洗；charts/ 内含各类图表的数据管道
database/      SQLAlchemy 模型定义
reports/       研报生成与提示词（DeepSeek）
webapp/        Flask 后端与前端模板（index.html 为主要页面）
requirements.txt  依赖列表
```

## 注意事项
- PDF 导出默认无书签/大纲；如需书签可在导出后自行处理。
- 本地默认使用 SQLite，生产可替换为其他数据库（调整 SQLAlchemy 连接字符串）。
