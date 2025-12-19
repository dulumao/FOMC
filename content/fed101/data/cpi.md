---
slug: data/cpi
title: 通胀（CPI/PCE）
order: 42
summary: 重点在结构与动量，而非单一水平。
---

# 通胀（CPI/PCE）

本节用于建立通胀阅读的最小框架。

## 核心问题

- 可逆 vs 粘性
- 扩散 vs 局部

## 图1：同比

```fomc-cell
{
  "id": "cpi-yoy",
  "title": "图1：同比",
  "type": "cpi_figure",
  "note": "默认用示例会议推断月份。",
  "params": { "figure": "yoy", "use_meeting_month": true }
}
```

读法要点：

- 关注趋势斜率，而非单点水平。
- 总 CPI 与核心 CPI 的分化提示驱动来源。

## 图2：环比（季调）

```fomc-cell
{
  "id": "cpi-mom",
  "title": "图2：环比（季调）",
  "type": "cpi_figure",
  "note": "用于确认当月动量变化。",
  "params": { "figure": "mom", "use_meeting_month": true }
}
```

## 表1：同比拆分

```fomc-cell
{
  "id": "cpi-contrib-yoy",
  "title": "表1：同比拆分",
  "type": "cpi_figure",
  "note": "分项权重与拉动贡献。",
  "params": { "figure": "contrib_yoy", "use_meeting_month": true }
}
```

## 表2：环比拆分（季调）

```fomc-cell
{
  "id": "cpi-contrib-mom",
  "title": "表2：环比拆分（季调）",
  "type": "cpi_figure",
  "note": "识别当月动量来源。",
  "params": { "figure": "contrib_mom", "use_meeting_month": true }
}
```

## 结论模板

- 主导分项：____
- 粘性证据：____
- 再通胀/回落风险：____
