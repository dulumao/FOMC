---
slug: rules
title: 规则篇
order: 20
summary: 规则不是答案，是讨论的坐标系。你不需要相信它，只需要知道它在假设什么、敏感于什么。
---

# 规则篇

规则模型的正确用法只有一个：**当基准线**。

你可以不同意它，但你不能说它没说清楚——因为它把“我觉得”翻译成了“在这些假设下，公式会给出什么”。

## 研究问题

如果规则不是答案，为什么研究里反而“必须有它”？

## 如果跳过，会发生什么

- 分歧会失焦：你会在“更鹰/更鸽”的形容词里打转，最后只剩情绪。
- 讨论会不可复现：换一场会议、换一份数据，你找不到“为什么结论变了”。

## 在反应函数中的角色

规则模型在流程里扮演的是**坐标系**：

- 它压缩分歧：先把大家拉到同一条基准线附近。
- 它暴露假设：分歧来自数据、参数、目标，还是风险偏好（风险管理）？

## 工具：把基准线跑出来

你可以把 Taylor 规则当成一个“可计算的直觉”：

- 通胀高于目标 → 更紧
- 失业率低于 NAIRU（劳动力市场偏紧） → 更紧

项目里的简化表达式（只要读懂每一项在干什么就行）：

> `i = r* + π + α(π-π*) + β·okun·(u*-u) + output_gap + intercept`
>
> `i_adj = ρ·i_prev + (1-ρ)·i`

```fomc-cell
{
  "id": "taylor-playground",
  "title": "Taylor（可运行）",
  "type": "taylor_model",
  "note": "建议先在右侧选择示例会议，让窗口右端对齐会议决议日。",
  "params": {
    "model": "taylor",
    "rho": 0.00,
    "inflation_code": "PCEPILFE",
    "unemployment_code": "UNRATE",
    "nairu_code": "NROU",
    "fed_effective_code": "EFFR",
    "use_meeting_end": true
  },
  "controls": [
    {"key": "rho", "label": "ρ（惯性）", "type": "number", "min": 0, "max": 1, "step": 0.05}
  ]
}
```

## ρ（惯性）

`ρ` 不是“更科学”，它是“更像现实”：现实政策更平滑、调整更慢，常见理由包括滞后性、风险管理、金融条件的非线性等。

务实用法：把 `ρ` 当作一个“现实世界阻尼器”。你不需要为它辩护，只需要观察它会把建议路径变得多平。

## 变体

在本项目里，这些变体不是一套套全新的理论，更像**同一类规则的不同参数组合**。你应该关注的不是名字，而是它改了哪些假设：

- **通胀权重**（更敏感 → 更“鹰”）
- **就业缺口权重**（更敏感 → 更看重“松紧”）
- **长期假设**（`r*`、`π*`、NAIRU：最强硬、也最容易引发分歧的输入）

用一句话记每个预设就够了：

- **Extended**：更“激进”的权重组合（练敏感度）。
- **Rudebusch**：另一套常见参数组（当作另一份研究假设）。
- **Mankiw**：改目标/权重的直觉练习（看结论怎么跳）。
- **Evans**：练“假设一变，结论就变”（别选边站）。
- **Stone**：做稳健性检查（多个假设是否同向）。

```fomc-cell
{
  "id": "taylor-variants",
  "title": "切换预设（可运行）",
  "type": "taylor_model",
  "note": "把它当成实验：同一组数据，在不同研究假设下会给出怎样的利率建议？",
  "params": {
    "model": "taylor",
    "rho": 0.00,
    "inflation_code": "PCEPILFE",
    "unemployment_code": "UNRATE",
    "nairu_code": "NROU",
    "fed_effective_code": "EFFR",
    "use_meeting_end": true
  },
  "controls": [
    {
      "key": "model",
      "label": "预设",
      "type": "select",
      "options": [
        {"value": "taylor", "label": "Taylor"},
        {"value": "extended", "label": "Extended"},
        {"value": "rudebusch", "label": "Rudebusch"},
        {"value": "mankiw", "label": "Mankiw"},
        {"value": "evans", "label": "Evans"},
        {"value": "stone", "label": "Stone"}
      ]
    },
    {"key": "rho", "label": "ρ（惯性）", "type": "number", "min": 0, "max": 1, "step": 0.05}
  ]
}
```

## 别用错

1. **别把单点当路径**：规则给的是“这一刻的建议”，不是未来 12 个月的承诺。
2. **别忘了假设**：`r*`、`π*`、NAIRU 都是强假设；你要讨论它们，而不是把它们当自然常数。
3. **别把偏离当错误**：现实政策会考虑风险管理、金融稳定、金融条件等（现实世界比公式更爱反例）。

## 下一步

有了基准线，你才知道“分歧”到底长什么样：去历史会议页看讨论/决议/沟通材料，把它们当作对基准线的风险管理回答。
