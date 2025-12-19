---
slug: data/nfp
title: 就业（NFP）
order: 41
summary: 关注“再平衡路径”，而不是单月强弱。
---

# 就业（NFP）

本节用于建立就业数据的最小读法框架。

## 核心问题

- 降温是否在发生
- 降温来自需求、供给还是口径噪声

## 图1：就业 + 失业率

```fomc-cell
{
  "id": "nfp-fig1",
  "title": "图1：就业 + 失业率",
  "type": "labor_figure",
  "note": "默认用示例会议推断月份。",
  "params": { "figure": "fig1", "use_meeting_month": true }
}
```

读法要点：

- 先看 6–12 个月趋势，再看当月值。
- 失业率作为趋势确认信号。

## 图2：行业贡献（%）

```fomc-cell
{
  "id": "nfp-industry",
  "title": "图2：行业贡献（%）",
  "type": "labor_figure",
  "note": "最近 12 个月的分行业贡献率。",
  "params": { "figure": "industry_contribution", "use_meeting_month": true }
}
```

读法要点：

- 关注集中度与连续性。
- 识别结构变化而非单月噪声。

## 图3：U1~U6

```fomc-cell
{
  "id": "nfp-u-rates",
  "title": "图3：U1~U6",
  "type": "labor_figure",
  "note": "条形图对比本月 vs 上月。",
  "params": { "figure": "unemployment_types", "use_meeting_month": true }
}
```

读法要点：

- 宽口径先变化通常代表边缘劳动力调整。

## 图4：就业率 & 参与率

```fomc-cell
{
  "id": "nfp-emp-part",
  "title": "图4：就业率 & 参与率",
  "type": "labor_figure",
  "note": "近 24 个月就业率与参与率走势。",
  "params": { "figure": "employment_participation", "use_meeting_month": true }
}
```

读法要点：

- 参与率与就业率共同判断“供给侧变化”。

## 结论模板

- 本期就业变化来自：____
- 结构证据：____
- 风险提示：____
