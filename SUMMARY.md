# FOMC项目总结报告

## 项目概述
本项目旨在收集和分析与美联储公开市场委员会(FOMC)决策相关的经济数据。项目包含数据收集、存储和可视化组件。

## 已完成的工作

### 1. 数据库修复
- 修复了数据库表创建问题，确保所有经济指标和数据点能正确存储
- 实现了共享Base对象，解决SQLAlchemy模型注册问题
- 成功创建了两个主要数据表：
  - `economic_indicators`: 存储经济指标定义
  - `economic_data_points`: 存储具体的经济数据点

### 2. 数据收集
- 成功运行数据收集脚本，收集了2025年以来的经济数据
- 收集了18个关键经济指标，包括：
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
  - 等等...

### 3. 数据验证
- 验证了数据库表结构和数据完整性
- 确认数据已成功存储在SQLite数据库中
- 创建了数据查看脚本，方便检查收集到的数据

## 数据库结构

### economic_indicators 表
- id (INTEGER): 主键
- name (VARCHAR(100)): 指标名称
- code (VARCHAR(50)): 指标代码
- description (TEXT): 指标描述
- frequency (VARCHAR(20)): 数据频率
- units (VARCHAR(50)): 单位
- seasonal_adjustment (VARCHAR(50)): 季节性调整信息
- last_updated (DATETIME): 最后更新时间
- data (TEXT): 其他数据

### economic_data_points 表
- id (INTEGER): 主键
- indicator_id (INTEGER): 外键，关联到economic_indicators表
- date (DATETIME): 数据日期
- value (FLOAT): 数据值

## 使用说明

### 初始化数据库
```bash
python init_database.py
```

### 收集经济数据
```bash
python data/collect_economic_data.py
```

### 查看数据结构
```bash
python view_schema.py
```

### 查看收集的数据
```bash
python view_data.py
```

## 下一步建议

1. 开发数据可视化功能，创建经济指标的趋势图表
2. 实现定期自动数据收集功能
3. 添加更多经济指标到收集列表
4. 开发Web界面以更直观地展示数据