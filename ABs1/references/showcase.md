> 以下代码、API 与配置仅为参考，可替换实现；全局绘图规范以 SKILL.md 为准。

# 十二组综合示例

脚本：[example_showcase.py](../example_showcase.py)。输出：`Figure/showcase_reference12.pdf`、`Figure/showcase_bluepink_gradient.pdf`。

全部数据均为固定随机种子生成的模拟数据，用于演示绘图功能，不表示真实实验结论。G01–G12 在每个面板中按标准色库顺序取色并保持一致；四批分别为蓝、绿、暖黄橙棕、粉紫。字号 16 pt、线宽 1.2 pt。固定单元为 3×2.8 inch。a/e 各占 2×2 格（6×5.6），b/c 各占 1×1 格（3×2.8），d/f 各占 2×1 格（6×2.8）；共享图例占 2×1 格。图幅按 4×4 个单元自动得到 12×11.2 inch。

| 面板 | 内容 | 展示能力 |
|---|---|---|
| a | 12 条模拟动态轨迹 | 12 色及 12 种点型；全曲线保留，仅以 markevery 控制符号密度 |
| b | 12 组、共 576 个特征散点 | 同轴多次叠加，独立颜色与形状轮换 |
| c | 12 层合成组分占比，总和恒为 100% | 顺序填充、累计边界、全套色系共同展示 |
| d | 12 组 × 3 条件，共 36 根柱 | 按组保持颜色，A/B/C 以 1、0.66、0.34 的透明度区分；误差线是模拟 SD 示意值，不是推断性置信区间 |
| e | 12×36 响应偏差矩阵 | 同时融合 6 个标准色锚点的蓝粉连续渐变，范围 −1 到 1 |
| f | 12 组分布，每组 36 次模拟观测 | 核密度、中位数及全部原始点叠加；无观测删减 |

图例共用颜色和点型，对应 G01–G12。色条仅占热力图本面板的一部分，局部宽度例外写入对齐报告，其他面板按统一布局检查。源数据为日志目录中的 `synthetic_data.npz` 及 CSV；示例函数拆为数据生成、各类图绘制、整体布局和检查，绘制函数仍只接收 ax 与数据。

运行检查：

```bash
python AcaBrush/ABs1/example_showcase.py --qa-dir /path/to/nature-figure/scripts
```

启用后保存绘图区对齐、PDF 字体与碰撞报告。默认不改变整个绘图库的字体、线宽或尺寸设置。

## 实际绘图调用

示例统一通过 `from abs1 import api as brush` 调用 `brush.plot_*`，再由 `abs1/plots.py` 分派给项目 `figure_plot.py`。六个面板及蓝粉连续色带的数据图元都走这条调用链；不在示例里直接调用 `ax.plot/scatter/fill_between/bar/pcolormesh/violinplot/imshow`。调用方只管理画布、坐标轴、文字、图例、色条与导出。

## 可核查的图幅机制

占格配置在 [showcase-layout.json](../configs/showcase-layout.json)：

```text
a a b c
a a d d
e e f f
e e legend legend
```

修改占格由 `create_layout` 自动更新总宽高；正常子图不会被放大的相邻子图拉伸。日志 `showcase.layout.json` 同时记录所有子图的完整分配区域和内部数据绘图区（英寸），二者不可混淆。`run.json` 的画布尺寸从布局接口读取，不再写死尺寸；导出拒绝与占格不符的人工缩放。
