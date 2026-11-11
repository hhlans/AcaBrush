# ABs1 · 学术绘图 Skill

[![Skill First](https://img.shields.io/badge/Skill-First-13A4BD.svg)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)

ABs1 是 [AcaBrush](../README.md) 的绘图规范入口，覆盖统一字体、线宽、图幅、配色、点型及组图布局。

**首先阅读 [SKILL.md](SKILL.md)。附带 Python 代码只供参考，可替换为自己的绘图函数，不是 skill 的使用前提。**

## 核心规则

| 项目 | 默认规范 |
|---|---|
| 文字 / 子图编号 | 14 pt / 22 pt 加粗 |
| 数据线、轴线与刻度线 | 0.9 pt |
| 初始单图参考 | 完整图幅可参考 3×2.8 inch，先明确内部绘图区尺寸 |
| 总图幅 | 按实际内容、间隙和外边距确定，不取整、不整体缩放 |
| 组图间隙 | 同行真实间隙相等，水平默认至少 0.18 inch、行间至少 0.20 inch |
| 跨行对齐 | 仅同图数的行建立列锚点，不同图数独立排布；图例不计数 |
| 配色 / 点型 | 按既定顺序选取，每个新 ax 从头开始，圆形最后 |
| 输出 | PDF 图像，保留实际尺寸与可编辑文字 |

## 图型说明

- [点、线、点线](references/point-line.md)
- [线下填充](references/fill.md)
- [柱状图](references/bar.md)
- [热力图](references/heatmap.md)
- [小提琴图](references/violin.md)

[测量布局接口](references/layout.md) 说明固定绘图区、真实间隙和编号的联合排布。

图元函数接收已有 `ax`，同一 ax 可叠加多个图型；范围、刻度、图例、布局及导出由调用方统一管理。配色及蓝粉六锚点渐变见 [ABsCol](../ABsCol/README.md)。

## 示例与参考代码

[综合图元展示](Figure/showcase_reference12.pdf) · [复杂测量布局](Figure/showcase_complex_measured.pdf) · [蓝粉色卡](../ABsCol/Figure/reference12_heat.pdf) · [同轴叠加代码](example_overlay.py)

`abs1/api.py`、`configs/` 和 `example_*.py` 展示一种 Python 实现；运行参考代码时可按自身工程对接底层绘图函数。示例均为模拟数据，不构成实验结论。

[返回项目首页](../README.md) · [反馈问题](https://github.com/hhlans/AcaBrush/issues)
