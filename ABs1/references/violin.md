> 以下代码、API 与配置仅为参考，可替换实现；全局绘图规范以 SKILL.md 为准。

# 小提琴图

接口：`plot_violin`，统一从 `abs1.api` 导入。配置：[configs/violin.json](../configs/violin.json)。全局字体、字号、线宽、尺寸只见 [SKILL.md](../SKILL.md)。

```python
plot_violin(ax, [group_a, group_b], positions=[1, 2])
ax.set_xticks([1, 2], ["A", "B"])
```

输入为各组原始观测数组，不接收均值列表。每组至少 2 个有限且非恒定的观测，否则报错，不静默删值。配置 `widths`、`alpha`、`color`、`showmedians`、`showextrema`、`points`、`bw_method`。默认显示中位数，不显示极值线；核密度只表示分布估计，不等同置信区间。分类轴由调用方设标签，y 范围覆盖全部观测；小样本建议叠加原始点并报告 n。

配置优先级：默认 JSON < `config` 字典或 JSON 路径 < 显式关键字参数。绘图函数仅绘制到传入的 ax，不设置范围、刻度或画布尺寸；返回 ax。完整组图见 [example_categories.py](../example_categories.py)。

默认从标准配色顺序取色，每个新 ax 和清空后的 ax 均从头开始。每个分布依次取一种颜色。配色与点型规则统一见 [SKILL.md](../SKILL.md)。
