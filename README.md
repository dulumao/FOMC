# FOMC经济数据分析项目

## 项目概述
本项目旨在收集、存储和分析与美联储公开市场委员会(FOMC)决策相关的经济数据。项目包含数据收集、存储和可视化组件。

## 项目结构
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
├── .env                   # 环境变量配置
├── init_database.py       # 数据库初始化脚本
├── main.py                # 主程序入口
├── requirements.txt       # Python依赖包
├── SUMMARY.md             # 项目总结报告
├── view_data.py           # 查看数据脚本
└── view_schema.py         # 查看数据库结构脚本
```

## 安装依赖
```bash
pip install -r requirements.txt
```

## 环境配置
1. 在FRED网站注册账户并获取API密钥: https://fred.stlouisfed.org/docs/api/api_key.html
2. 将API密钥添加到.env文件中:
```
FRED_API_KEY=your_api_key_here
```

## 使用说明

### 1. 初始化数据库
```bash
python init_database.py
```

### 2. 收集经济数据
```bash
python data/collect_economic_data.py
```

### 3. 查看数据库结构
```bash
python view_schema.py
```

### 4. 查看收集的数据
```bash
python view_data.py
```

## 数据库结构

### economic_indicators 表
存储经济指标的定义信息:
- id: 主键
- name: 指标名称
- code: 指标代码
- description: 指标描述
- frequency: 数据频率
- units: 单位
- seasonal_adjustment: 季节性调整信息

### economic_data_points 表
存储具体的经济数据点:
- id: 主键
- indicator_id: 外键，关联到economic_indicators表
- date: 数据日期
- value: 数据值

## 收集的经济指标
项目当前收集以下18个关键经济指标:
1. 失业率 (UNRATE)
2. 自然失业率 (NROU)
3. 非农就业人数 (PAYEMS)
4. 消费者价格指数 (CPIAUCSL)
5. 个人消费支出价格指数 (PCEPI)
6. 联邦基金利率 (FEDFUNDS)
7. 10年期国债收益率 (DGS10)
8. 2年期国债收益率 (DGS2)
9. 10年期与2年期国债收益率差 (T10Y2Y)
10. 密歇根大学消费者信心指数 (UMCSENT)
11. 基础货币 (BOGMBASE)
12. M2货币供应量 (M2SL)
13. Case-Shiller房价指数 (CSUSHPINSA)
14. 工业生产指数 (INDPRO)
15. 制造业采购经理人指数 (NAPM)
16. 零售销售 (RSXFS)
17. 耐用品订单 (DGORDER)
18. 商业库存 (BUSINV)

## 开发计划
1. 开发数据可视化功能，创建经济指标的趋势图表
2. 实现定期自动数据收集功能
3. 添加更多经济指标到收集列表
4. 开发Web界面以更直观地展示数据