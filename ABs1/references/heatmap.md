> 以下代码、API 与配置仅为参考，可替换实现；全局绘图规范以 SKILL.md 为准。

# 热力图

接口：`plot_heatmap`，统一从 `abs1.api` 导入。配置：[configs/heatmap.json](../configs/heatmap.json)。全局字体、字号、线宽、尺寸只见 [SKILL.md](../SKILL.md)。

```python
plot_heatmap(ax, x_edges, y_edges, matrix, vmin=0, vmax=1)
mappable = ax.collections[-1]
# 由调用方分配 cax，fig.colorbar(mappable, cax=cax)。
```

矩阵行为 y、列为 x；中心坐标长度对应矩阵维度，边界坐标长度多 1。配置 `palette`、`continuous`、`shading`、`rasterized`、`colorbar`；显式 `cmap` 可覆盖。顺序量默认使用从标准色卡提取的 reference12_heat 蓝粉六锚点连续渐变；正负偏差可显式选择发散色图及对称范围；可比面板共享 vmin/vmax。默认 `colorbar=False`，由布局层在本子图内单独分配色条，避免为一根色条扩大整图尺寸或间距；可用 `make_axes_locatable(ax).append_axes("right", size="5%", pad=0.08)` 局部预留，热力绘图区的局部缩窄须记录为对齐例外；简单单图可显式 `colorbar=True`。栅格化只影响 PDF 内的色块，文字仍可编辑。缺失值不得替换为零，使用掩码并说明。

配置优先级：默认 JSON < `config` 字典或 JSON 路径 < 显式关键字参数。绘图函数仅绘制到传入的 ax，不设置范围、刻度或画布尺寸；返回 ax。完整组图见 [example_categories.py](../example_categories.py)。

默认从标准配色顺序取色，每个新 ax 和清空后的 ax 均从头开始。配色与点型规则统一见 [SKILL.md](../SKILL.md)。
