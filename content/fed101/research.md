---
slug: research
title: 研究流程与反应函数
order: 30
summary: 研究流程总览、基准线与分歧复盘。
---

# 研究流程与反应函数

本章给出流程总览，并说明基准线与分歧复盘的必要性。

## 流程结构

> 信息集 → 基准线 → 风险权重 → 决议/沟通 → 复盘

- 信息集：数据与事件构成的输入。
- 基准线：规则模型给出的可计算基线。
- 风险权重：对不确定性的偏好与约束。
- 决议/沟通：政策动作与对外口径。
- 复盘：解释偏离发生在哪一步。

## 基准线：规则模型

规则模型的用途是给出可计算的基准线，用来定位分歧来源。

- 模型不提供“答案”，只提供“坐标系”。
- 规则假设透明，便于复盘与对比。

### 示例：Taylor 规则（可运行）

```fomc-cell
{
  "id": "taylor-playground",
  "title": "Taylor（可运行）",
  "type": "taylor_model",
  "note": "建议先在右侧选择示例会议，让窗口对齐决议日。",
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

### 规则变体（同一类假设组合）

```fomc-cell
{
  "id": "taylor-variants",
  "title": "切换预设（可运行）",
  "type": "taylor_model",
  "note": "同一组数据在不同假设下的利率建议对比。",
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

## 分歧来源与复盘

分歧通常来自三类来源：

- **数据**：口径不一致、结构变化与噪声混合、数据修正。
- **假设**：r*、π*、NAIRU 的设定差异。
- **风险权重**：对通胀粘性或增长下行的敏感度不同。

复盘的最低要求：

- 明确数据窗口与口径。
- 明确基准线与参数设定。
- 记录风险权重的判断依据。
