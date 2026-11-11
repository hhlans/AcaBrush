# ABs1 · 学术绘图 Skill

[![Skill First](https://img.shields.io/badge/Skill-First-13A4BD.svg)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)

ABs1 是 [AcaBrush](../README.md) 的绘图规范入口，覆盖统一字体、线宽、图幅、配色、点型及组图布局。

**首先阅读 [SKILL.md](SKILL.md)。附带 Python 代码只供参考，可替换为自己的绘图函数，不是 skill 的使用前提。**

## 核心规则

| 项目 | 默认规范 |
|---|---|
| 文字 / 子图编号 | 16 pt / 22 pt 加粗 |
| 数据线、轴线与刻度线 | 1.2 pt |
| 基础单元 | 3×2.8 inch，宽高分别按正整数倍占格 |
| 放大机制 | 仅增加需要放大的子图占格，总图幅相应变化，其余子图保持原尺寸 |
| 配色 / 点型 | 按既定顺序选取，每个新 ax 从头开始，圆形最后 |
| 输出 | PDF 图像，保留实际尺寸与可编辑文字 |

## 图型说明

- [点、线、点线](references/point-line.md)
- [线下填充](references/fill.md)
- [柱状图](references/bar.md)
- [热力图](references/heatmap.md)
- [小提琴图](references/violin.md)

图元函数接收已有 `ax`，同一 ax 可叠加多个图型；范围、刻度、图例、布局及导出由调用方统一管理。配色及蓝粉六锚点渐变见 [ABsCol](../ABsCol/README.md)。

## 示例与参考代码

[12 组数据完整组图](Figure/showcase_reference12.pdf) · [蓝粉融合渐变](Figure/showcase_bluepink_gradient.pdf) · [同轴叠加](Figure/overlay.pdf)

`abs1/api.py`、`configs/` 和 `example_*.py` 展示一种 Python 实现；运行参考代码时可按自身工程对接底层绘图函数。示例均为模拟数据，不构成实验结论。

[返回项目首页](../README.md) · [反馈问题](https://github.com/hhlans/AcaBrush/issues)
