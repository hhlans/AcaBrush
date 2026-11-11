> 以下代码、API 与配置仅为参考，可替换实现；全局绘图规范以 SKILL.md 为准。

# 线下填充图

接口：`plot_fill`，统一从 `abs1.api` 导入。配置：[configs/fill.json](../configs/fill.json)。全局字体、字号、线宽、尺寸只见 [SKILL.md](../SKILL.md)。

```python
plot_fill(ax, x, y)              # y 与 0 之间
plot_fill(ax, x, lower, upper)   # 两条边界之间
```

`x` 单调递增；边界与 x 等长，允许一个边界为标量。配置 `color`、`alpha`、`boundary`；`boundary=True` 显示非标量边界线。置信带必须由调用方计算，并注明是 SD、SEM 还是 CI；填充本身不计算统计量。轴范围覆盖两条边界。

配置优先级：默认 JSON < `config` 字典或 JSON 路径 < 显式关键字参数。绘图函数仅绘制到传入的 ax，不设置范围、刻度或画布尺寸；返回 ax。完整组图见 [example_categories.py](../example_categories.py)。

默认从标准配色顺序取色，每个新 ax 和清空后的 ax 均从头开始。配色与点型规则统一见 [SKILL.md](../SKILL.md)。
