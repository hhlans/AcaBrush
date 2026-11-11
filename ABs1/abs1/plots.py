"""Five chart families. Defaults: JSON config < custom config < explicit kwargs.

Global typography and stroke widths are supplied by Style, never chart configs.
Each call adds artists to the supplied Axes and returns that same Axes.
Reuse one Axes across calls to overlay series and chart types; zorder sets depth.
Limits, ticks, size, legends, layout and saving belong to the caller.
"""
import importlib.util
import json
import operator
from contextlib import contextmanager
from pathlib import Path
import matplotlib as mpl
from .style import DEFAULT
from .palette import get_color, get_cmap

_backend = None
_CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"

def load_config(kind, config=None):
    """Read chart JSON each call; config may be a mapping or a JSON path."""
    kinds = {"point-line", "fill", "bar", "heatmap", "violin"}
    if kind not in kinds:
        raise ValueError(f"Unknown chart family: {kind}")
    result = json.loads((_CONFIG_DIR / f"{kind}.json").read_text())
    if config is not None:
        override = json.loads(Path(config).read_text()) if isinstance(config, (str, Path)) else dict(config)
        result.update(override)
    return result

@contextmanager
def _chart_options(ax, kind, config, kwargs, count=1):
    """Advance color groups only after a successful drawing call.

    Store usage on a newly drawn artist, so each Axes is independent and
    ax.clear() resets the sequence. Multiple artists for one series count once.
    """
    options = load_config(kind, config)
    options.update(kwargs)
    palette = options.pop("palette", None) or "reference12"
    index = options.pop("color_index", "auto")
    continuous = options.pop("continuous", True)
    usage = None
    if kind == "heatmap":
        if "cmap" not in kwargs:
            options["cmap"] = get_cmap(palette, continuous=continuous)
    elif "color" not in kwargs:
        if index is None or (isinstance(index, str) and index == "auto"):
            previous = [getattr(artist, "_abs_palette_usage", None)
                        for artist in ax.get_children()]
            index = max((item[1] for item in previous
                         if item is not None and item[0] == palette), default=0)
        else:
            index = operator.index(index)
        colors = [get_color(palette, index+i) for i in range(count)]
        options["color"] = colors[0] if count == 1 else colors
        usage = (palette, index+count)
    before = set(ax.get_children())
    yield options
    if usage is not None:
        added = [artist for artist in ax.get_children() if artist not in before]
        if added:
            added[0]._abs_palette_usage = usage


def _project_plots():
    global _backend
    if _backend is None:
        source = Path(__file__).resolve().parents[3] / "figure_plot.py"
        spec = importlib.util.spec_from_file_location("_abs1_project_plots", source)
        module = importlib.util.module_from_spec(spec)
        with mpl.rc_context():
            spec.loader.exec_module(module)
        _backend = module
    return _backend

def plot_point_line(ax, x, y, *, mode=None, config=None, style=DEFAULT, **kwargs):
    """One series per call; color and point shapes advance locally on ax."""
    with _chart_options(ax, "point-line", config, kwargs) as options:
        selected_mode = mode or options.pop("mode")
        options.pop("mode", None)
        if selected_mode not in {"point", "line", "pointline"}:
            raise ValueError("mode must be point, line or pointline")
        color = options.pop("color")
        markers = options.pop("markers", None)
        if selected_mode == "line":
            options["marker"] = None
        elif isinstance(options.get("marker"), str) and options["marker"] == "auto":
            options["marker"] = _project_plots().next_marker(ax, markers)
        if selected_mode == "point":
            options.pop("ls", None)
            _project_plots().plot_points(ax, x, y, color=color,
                     size=style.marker, linewidth=style.marker_edge, **options)
        else:
            label = options.pop("label", None)
            options.setdefault("lw", style.line)
            options.setdefault("ms", style.marker)
            options.setdefault("markeredgewidth", style.marker_edge)
            _project_plots().plot_line(ax, x, y, labels=label, colors=[color], **options)
    return ax

def plot_points(ax, x, y, **kwargs):
    return plot_point_line(ax, x, y, mode="point", **kwargs)

def plot_line(ax, x, y, **kwargs):
    return plot_point_line(ax, x, y, mode="line", **kwargs)

def plot_pointline(ax, x, y, **kwargs):
    return plot_point_line(ax, x, y, mode="pointline", **kwargs)

def plot_fill(ax, x, lower, upper=0, *, config=None, style=DEFAULT, **kwargs):
    with _chart_options(ax, "fill", config, kwargs) as options:
        options.setdefault("linewidth", style.line)
        _project_plots().plot_fill(ax, x, lower, upper, **options)
    return ax

def plot_bar(ax, x, height, *, config=None, style=DEFAULT, **kwargs):
    """Each bar gets the next color. Use color_index to reuse a group color."""
    import numpy as np
    count = np.asarray(height).size
    with _chart_options(ax, "bar", config, kwargs, count=count) as options:
        options.setdefault("linewidth", style.line)
        _project_plots().plot_bar(ax, x, height, **options)
    return ax

def plot_heatmap(ax, x, y, values, *, config=None, style=DEFAULT, **kwargs):
    """Use the derived blue-pink ramp by default; continuous=False selects discrete colors."""
    with _chart_options(ax, "heatmap", config, kwargs) as options:
        _project_plots().plot_heatmap(ax, x, y, values, **options)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(style.axes)
    cb = ax.collections[-1].colorbar
    if cb is not None:
        cb.ax.tick_params(labelsize=style.font, width=style.tick)
        cb.outline.set_linewidth(style.axes)
        cb.ax.xaxis.label.set_size(style.font)
        cb.ax.yaxis.label.set_size(style.font)
    return ax

def plot_violin(ax, samples, *, config=None, style=DEFAULT, **kwargs):
    """Each distribution gets the next color in its Axes-local palette."""
    samples = list(samples)
    with _chart_options(ax, "violin", config, kwargs, count=len(samples)) as options:
        options.setdefault("linewidth", style.line)
        _project_plots().plot_violin(ax, samples, **options)
    return ax
