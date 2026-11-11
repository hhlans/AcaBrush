# AcaBrush

**面向学术绘图的 skill 规范与配色参考。**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skill First](https://img.shields.io/badge/Skill-First-13A4BD.svg)](ABs1/SKILL.md)
[![Palette: 12 Colors](https://img.shields.io/badge/Palette-12_Colors-D87F98.svg)](ABsCol/README.md)
[![Output: PDF](https://img.shields.io/badge/Output-Vector_PDF-81BFAD.svg)](ABs1/Figure/showcase_reference12.pdf)

[绘图规范](ABs1/SKILL.md) · [ABs1 介绍](ABs1/README.md) · [配色库](ABsCol/README.md) · [示例](#示例) · [反馈](https://github.com/hhlans/AcaBrush/issues)

## 项目定位

AcaBrush 将学术绘图中的字体、线宽、图幅、配色、点型及组图布局整理为可复用的 skill。**`SKILL.md` 是主要交付，Python 代码和示例只用于说明实现方式。** 使用规范不要求安装此项目，也不绑定特定本机路径、运行环境或工程结构；可以复用自己的绘图函数。

## 特性

- **统一样式**：正文、坐标轴及图例 14 pt，子图编号 22 pt；线宽和点大小保持固定。
- **实测布局**：固定绘图区，按完整内容测量真实间隙；同行等距，不同图数的行独立排布，总图幅按内容确定、不取整。
- **顺序配色与点型**：12 色按蓝、绿、暖、粉紫分批；每个子图重新从头取色与点型，圆形排最后。
- **多锚点热力渐变**：蓝、浅蓝、淡紫、浅粉、玫瑰粉和梅紫共同融合，而非仅在两个端点间插值。
- **五类图型**：点/线/点线、线下填充、柱状、热力、小提琴，支持向同一 `ax` 组合绘制。
- **可检查的输出**：仅导出 PDF 图像，检查实际尺寸、文字可读性、重叠和面板对齐。

## 开始使用

1. 阅读 [ABs1/SKILL.md](ABs1/SKILL.md)，将其作为绘图任务的规范，或交给支持 skill 的助手使用。
2. 按需查阅分类说明和 [ABsCol 配色库](ABsCol/README.md)。
3. 使用自己的绘图函数落实规范；需要实现示例时再参考附带 Python 代码，并按自身工程调整函数对接。

> 参考代码不是使用本 skill 的前提，也不承诺直接适配所有环境。示例中的数据均为模拟数据，不表示真实实验结果。

## 示例

| 内容 | PDF |
|---|---|
| 12 组数据综合展示：轨迹、散点、面积、分组柱、热力及小提琴 | [完整组图](ABs1/Figure/showcase_reference12.pdf) |
| 长标签、外置图例和色条的复杂组图 | [测量布局组图](ABs1/Figure/showcase_complex_measured.pdf) |
| 六锚点蓝粉融合配色 | [蓝粉色卡](ABsCol/Figure/reference12_heat.pdf) |
| 标准 12 色 | [标准色卡](ABsCol/Figure/reference12.pdf) |
| 同一 ax 叠加不同图型 | [参考代码](ABs1/example_overlay.py) |

## 目录

```text
AcaBrush/
├── ABs1/
│   ├── SKILL.md          # 核心绘图规范
│   ├── README.md         # 绘图模块介绍
│   ├── references/       # 图型与布局说明
│   ├── configs/          # 参考配置
│   ├── abs1/             # 参考 Python 接口
│   ├── example_*.py      # 参考示例
│   └── Figure/           # PDF 展示
├── ABsCol/
│   ├── README.md         # 色系顺序与渐变说明
│   └── palettes/         # 配色 JSON
├── CONTRIBUTING.md
└── LICENSE
```

## 参与和反馈

欢迎通过 [Issues](https://github.com/hhlans/AcaBrush/issues) 提交规范建议、可读性问题或新的图型需求，也欢迎 Pull Request。提交前请阅读 [贡献说明](CONTRIBUTING.md)，优先改进 skill 的清晰度和可复用性。

## 许可证

本项目采用 [MIT License](LICENSE)。
