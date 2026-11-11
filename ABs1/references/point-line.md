> 以下代码、API 与配置仅为参考，可替换实现；全局绘图规范以 SKILL.md 为准。

# 点、线、点线图

接口：`plot_point_line / plot_points / plot_line / plot_pointline`，统一从 `abs1.api` 导入。配置：[configs/point-line.json](../configs/point-line.json)。全局字体、字号、线宽、尺寸只见 [SKILL.md](../SKILL.md)。

```python
plot_point_line(ax, x, y, mode="point")     # 散点，保留输入顺序
plot_point_line(ax, x, y, mode="line")      # 折线
plot_point_line(ax, x, y, mode="pointline") # 点线
```

`x/y` 为等长一维数组，每次调用一条序列。多组数据重复传入同一个 ax，可以独立设置颜色、标记、线型和标签，也可以在同一 ax 混合不同图型：

```python
plot_points(ax, x_a, y_a, label="A", zorder=3)
plot_line(ax, x_b, y_b, label="B", zorder=2)
plot_pointline(ax, x_c, y_c, label="C", zorder=2)
ax.legend()  # 由调用方统一管理图例
```

三组的 x 长度可以不同；每组内部 x/y 等长即可。所有函数追加到已有 ax、返回该 ax，不创建画布、不清空、不设置布局或保存。坐标范围由调用方覆盖所有叠加数据。完整示例见 [example_overlay.py](../example_overlay.py)。

点图不连接；线与点线复用项目函数并按 x 排序，不应用于需要保留路径顺序的轨迹。配置 `mode`、`color`、`marker`、`markers`、`ls`、`alpha`。默认 `marker="auto"`，同一个 ax 上的散点和点线共用形状轮换，圆形排最后；纯线和填充不推进轮换。`markers` 可自定义轮换列表，`marker="D"` 等可固定单次形状。同组跨面板保持颜色与标记一致。

配置优先级：默认 JSON < `config` 字典或 JSON 路径 < 显式关键字参数。绘图函数仅绘制到传入的 ax，不设置范围、刻度或画布尺寸；返回 ax。完整组图见 [example_categories.py](../example_categories.py)。

默认从标准配色顺序取色，每个新 ax 和清空后的 ax 均从头开始。配色与点型规则统一见 [SKILL.md](../SKILL.md)。
