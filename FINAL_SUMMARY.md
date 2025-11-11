# FOMC经济数据分析项目最终总结报告

## 项目概述
本项目旨在收集、存储和分析与美联储公开市场委员会(FOMC)决策相关的经济数据。项目包含数据收集、存储和可视化组件，为用户提供了一个完整的数据浏览和分析平台。

## 已完成的工作

### 1. 数据库设计与实现
- 成功设计并实现了两个核心数据表：
  - `economic_indicators`: 存储经济指标定义信息
  - `economic_data_points`: 存储具体的经济数据点
- 使用SQLAlchemy ORM实现数据库操作，确保数据一致性和完整性
- 创建了数据库初始化脚本，方便快速部署

### 2. 数据收集功能
- 实现了从FRED API自动收集经济数据的功能
- 成功收集了18个关键经济指标，包括：
  - 失业率 (UNRATE)
  - 自然失业率 (NROU)
  - 非农就业人数 (PAYEMS)
  - 消费者价格指数 (CPIAUCSL)
  - 个人消费支出价格指数 (PCEPI)
  - 联邦基金利率 (FEDFUNDS)
  - 10年期国债收益率 (DGS10)
  - 2年期国债收益率 (DGS2)
  - 10年期与2年期国债收益率差 (T10Y2Y)
  - 密歇根大学消费者信心指数 (UMCSENT)
  - 基础货币 (BOGMBASE)
  - M2货币供应量 (M2SL)
  - Case-Shiller房价指数 (CSUSHPINSA)
  - 工业生产指数 (INDPRO)
  - 制造业采购经理人指数 (NAPM)
  - 零售销售 (RSXFS)
  - 耐用品订单 (DGORDER)
  - 商业库存 (BUSINV)
- 实现了数据预处理功能，确保数据质量和一致性

### 3. Web数据浏览器
项目成功开发了一个功能完整的Web界面，用于直观地浏览和分析FOMC相关经济数据。

#### 功能特性
1. **响应式设计**：适配桌面和移动设备，提供良好的用户体验
2. **指标选择**：支持从18个关键经济指标中选择查看
3. **时间范围筛选**：支持1年、3年、5年、10年和全部数据的时间范围筛选
4. **数据排序**：支持按日期或数值进行升序/降序排列
5. **可视化图表**：使用Chart.js实现交互式折线图和柱状图展示
6. **数据表格**：以表格形式展示详细数据点，支持滚动查看
7. **实时刷新**：支持手动刷新获取最新数据
8. **数据摘要**：在首页显示关键指标的最新值和趋势信息
9. **用户反馈**：提供加载状态和错误信息提示，提升用户体验

#### 技术实现
- **后端**：Python Flask框架，使用SQLAlchemy ORM进行数据库操作
- **前端**：HTML5, CSS3, JavaScript，采用Bootstrap 5实现现代化UI
- **可视化**：Chart.js库实现动态数据图表
- **交互性**：通过Fetch API实现前后端异步通信

#### 使用方法
```bash
cd webapp
python app.py
```

访问 http://localhost:5000 查看数据浏览器。

## 项目文件结构
```
FOMC/
├── config/                 # 配置文件
├── data/                   # 数据处理相关模块
│   ├── collect_economic_data.py  # 经济数据收集脚本
│   ├── fred_api.py         # FRED API接口
│   ├── preprocessing.py    # 数据预处理
│   └── visualization.py    # 数据可视化
├── database/               # 数据库相关模块
│   ├── base.py            # 共享Base对象
│   ├── connection.py      # 数据库连接
│   └── models.py          # 数据模型
├── webapp/                 # Web应用
│   ├── app.py             # Flask应用
│   └── templates/         # HTML模板
│       └── index.html     # 主页面
├── .env                   # 环境变量配置
├── init_database.py       # 数据库初始化脚本
├── main.py                # 主程序入口
├── requirements.txt       # Python依赖包
├── SUMMARY.md             # 项目总结报告
├── FINAL_SUMMARY.md       # 最终总结报告
├── view_data.py           # 查看数据脚本
└── view_schema.py         # 查看数据库结构脚本
```

## 技术亮点
1. **模块化设计**：项目采用模块化设计，便于维护和扩展
2. **ORM使用**：使用SQLAlchemy ORM简化数据库操作，提高代码可读性和可维护性
3. **响应式UI**：采用Bootstrap 5实现现代化、响应式的用户界面
4. **异步通信**：使用Fetch API实现前后端异步通信，提升用户体验
5. **错误处理**：完善的错误处理机制，确保系统稳定运行
6. **用户体验**：提供加载状态、错误提示和用户反馈，提升交互体验

## 使用说明

### 环境配置
1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 在FRED网站注册账户并获取API密钥: https://fred.stlouisfed.org/docs/api/api_key.html
3. 将API密钥添加到.env文件中:
```
FRED_API_KEY=your_api_key_here
```

### 初始化数据库
```bash
python init_database.py
```

### 收集经济数据
```bash
python data/collect_economic_data.py
```

### 启动Web服务器
```bash
cd webapp
python app.py
```

访问 http://localhost:5000 查看数据浏览器。

## 项目成果
本项目成功实现了从数据收集到可视化展示的完整流程，为用户提供了一个直观、易用的经济数据分析平台。通过该项目，用户可以：
- 快速查看关键经济指标的历史数据
- 通过图表直观了解经济趋势
- 通过筛选和排序功能深入分析数据
- 实时获取最新的经济数据

## 下一步建议
1. 实现定期自动数据收集功能
2. 添加更多经济指标到收集列表
3. 增强数据可视化功能，提供更多图表类型
4. 实现用户认证和个性化功能
5. 添加数据导出功能，支持CSV、Excel等格式