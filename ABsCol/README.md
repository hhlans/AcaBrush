> 本文件及附带代码为参考材料；主要绘图规范见 ABs1/SKILL.md。

# ABsCol 配色库

标准 `reference12` 的全部 12 色来自参考图标注的 HEX，不修改色值；取色顺序重新按色系分批规划。每个新 ax 和清空后的 ax 均从首色开始，形状也重新开始。每轮包含 12 色与 12 种点型，圆形最后。

| 组 | 色系 | 顺序与 HEX |
|---|---|---|
| G01–G02 | 蓝色 | 雾蓝 `#96C2D6` → 青蓝 `#13A4BD` |
| G03–G04 | 绿色 | 薄荷绿 `#81BFAD` → 深绿 `#3E8043` |
| G05–G08 | 暖黄橙棕 | 浅黄 `#E6DD96` → 杏橙 `#F4BA6E` → 珊瑚橙 `#E2977C` → 暖棕 `#C7A48E` |
| G09–G12 | 粉紫 | 浅粉 `#EAAEBC` → 玫瑰粉 `#D87F98` → 淡紫 `#C5AFD1` → 梅紫 `#B9719E` |

JSON 的 `index` 是新顺序，`source_index` 保留原图位置；派生库的 `parent_index` 指向新标准库索引。颜色不会只因跨面板而继续往下取，而是每个 ax 都重新开始。

## 蓝粉多锚点融合

`reference12_heat` 使用完整 6 色路径：

**青蓝 → 雾蓝 → 淡紫 → 浅粉 → 玫瑰粉 → 梅紫**

`#13A4BD → #96C2D6 → #C5AFD1 → #EAAEBC → #D87F98 → #B9719E`

调用连续色图时，全部 6 个锚点等距参与插值，形成从蓝侧经过浅蓝、紫粉过渡到粉侧的连续色带，不是只在两个端点之间插值。差值热力图应统一数值范围，可把 0 放在中间。`reference12_warm` 提供 4 色暖色分类库；`reference12_warm_heat` 提供浅黄→杏橙→珊瑚橙→玫瑰粉的暖色渐变。

```python
from AcaBrush.ABs1.abs1.api import plot_points, plot_pointline, plot_heatmap, get_cmap

plot_points(ax, x1, y1)       # G01：雾蓝、方形
plot_pointline(ax, x2, y2)    # G02：青蓝、上三角
plot_pointline(ax, x3, y3)    # G03：薄荷绿、菱形
plot_points(ax2, x1, y1)      # 新面板：重新从雾蓝、方形开始
plot_heatmap(ax3, x_edges, y_edges, values, vmin=-1, vmax=1)
# 等价显式选择：cmap=get_cmap("reference12_heat", continuous=True)
```

`list_palettes/get_palette/get_color/get_cmap` 可以从统一接口或 `AcaBrush.ABsCol` 导入。颜色和点型默认自动按顺序轮换；仅为同一数据组复用颜色时指定 `color_index`，不任意跳色。底层支持显式覆盖，但默认示例均由色库驱动。

## 完整展示

在安装所需 Python 依赖后运行：

```bash
python AcaBrush/ABs1/example_showcase.py
python AcaBrush/ABsCol/preview.py reference12
python AcaBrush/ABsCol/preview.py reference12_heat
```

完整 12 组示例为 `ABs1/Figure/showcase_reference12.pdf`，连续蓝粉融合色带为 `ABs1/Figure/showcase_bluepink_gradient.pdf`。色卡保存至 `ABsCol/Figure/`。仅输出 PDF 图像，保留模拟源数据、色库索引和运行检查日志。
