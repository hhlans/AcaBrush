> 以下代码、API 与配置仅为参考，可替换实现；全局绘图规范以 SKILL.md 为准。

# 柱状图

接口：`plot_bar`，统一从 `abs1.api` 导入。配置：[configs/bar.json](../configs/bar.json)。全局字体、字号、线宽、尺寸只见 [SKILL.md](../SKILL.md)。

```python
plot_bar(ax, [1, 2, 3], means, yerr=errors)
# 分组柱：调用方给每组 x 加偏移，分别调用；堆叠柱传 bottom。
```

`x/height` 等长；`yerr` 为长度 n 或 (2,n) 的非负误差。配置 `width`、`color`、`alpha`、`capsize`。分类标签由调用方 `ax.set_xticks(positions, labels)` 设置；分类轴无需遵守连续轴两端刻度规则。通常保留零基线；完整覆盖误差端点，标明 n 与误差定义。

配置优先级：默认 JSON < `config` 字典或 JSON 路径 < 显式关键字参数。绘图函数仅绘制到传入的 ax，不设置范围、刻度或画布尺寸；返回 ax。完整组图见 [example_categories.py](../example_categories.py)。

默认从标准配色顺序取色，每个新 ax 和清空后的 ax 均从头开始。每根柱依次取一种颜色，不再整组固定为一种颜色。配色与点型规则统一见 [SKILL.md](../SKILL.md)。
