"""Canvas, explicit ticks and renderer-based panel labels."""
import string
import copy
import operator
import numpy as np
import matplotlib.pyplot as plt
from .style import DEFAULT

BASE_PANEL_SIZE = (3.0, 2.8)


def _positive_integer(value, name):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be a positive integer")
    try:
        value = operator.index(value)
    except TypeError as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _panel_units(panel_size):
    size = np.asarray(panel_size, dtype=float)
    if size.shape != (2,) or not np.isfinite(size).all():
        raise ValueError("panel_size must be a finite (width, height) pair")
    units = size / BASE_PANEL_SIZE
    if np.any(units < 1) or not np.allclose(units, np.round(units), rtol=0, atol=1e-9):
        raise ValueError("panel_size must be integer multiples of (3, 2.8) inches")
    return tuple(int(x) for x in np.round(units))


def create_layout(mosaic):
    """Create exact physical slots from a rectangular matrix of panel names.

    Each cell is 3 x 2.8 inches. Repeated names must fill a rectangle; '.' is
    an explicitly empty cell. Figure size follows occupied grid dimensions.
    Returns (Figure, dict[name, Axes]). Ordinary cells never grow with a peer.
    """
    rows = [list(row) for row in mosaic]
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("mosaic must be a nonempty rectangular matrix")
    cells = {}
    for row_index, row in enumerate(rows):
        for col_index, name in enumerate(row):
            if not isinstance(name, str) or not name:
                raise ValueError("Use nonempty string panel names and '.' for empty cells")
            if name != '.':
                cells.setdefault(name, []).append((row_index, col_index))
    if not cells:
        raise ValueError("mosaic must contain at least one panel")
    specifications = {}
    for name, locations in cells.items():
        r0 = min(r for r, c in locations); r1 = max(r for r, c in locations)+1
        c0 = min(c for r, c in locations); c1 = max(c for r, c in locations)+1
        if len(locations) != (r1-r0)*(c1-c0):
            raise ValueError(f"Panel {name!r} must occupy one solid rectangle")
        specifications[name] = dict(row=r0, column=c0, width_units=c1-c0, height_units=r1-r0)
    nrows, ncols = len(rows), len(rows[0])
    width, height = ncols*BASE_PANEL_SIZE[0], nrows*BASE_PANEL_SIZE[1]
    fig = plt.figure(figsize=(width, height))
    grid = fig.add_gridspec(nrows, ncols, left=0, right=1, bottom=0, top=1,
                           wspace=0, hspace=0)
    axes = {}
    for name, spec in specifications.items():
        row, col = spec['row'], spec['column']
        w, h = spec['width_units'], spec['height_units']
        ax = fig.add_subplot(grid[row:row+h, col:col+w])
        spec['box_inches'] = [col*3., height-(row+h)*2.8, w*3., h*2.8]
        ax._abs_unit_name = name
        axes[name] = ax
    fig._abs_unit_layout = dict(base_inches=list(BASE_PANEL_SIZE),
        grid_rows=nrows, grid_columns=ncols, canvas_inches=[width,height],
        mosaic=rows, panels=specifications)
    return fig, axes


def create_figure(nrows=1, ncols=1, *, panel_size=BASE_PANEL_SIZE):
    """Uniform grid using the same unit engine; return Figure and 2-D Axes.

    panel_size must be positive INTEGER multiples of the fixed base dimensions.
    For mixed sizes use create_layout instead of enlarging every panel.
    """
    nrows = _positive_integer(nrows, "nrows")
    ncols = _positive_integer(ncols, "ncols")
    width_units, height_units = _panel_units(panel_size)
    mosaic = [[f"p{row//height_units}_{col//width_units}"
               for col in range(ncols*width_units)]
              for row in range(nrows*height_units)]
    fig, panels = create_layout(mosaic)
    axes = np.array([[panels[f'p{row}_{col}'] for col in range(ncols)]
                     for row in range(nrows)], dtype=object)
    return fig, axes


def get_layout_spec(fig):
    """Return allocated physical slots and final plot rectangles, in inches."""
    if not hasattr(fig, '_abs_unit_layout'):
        raise ValueError("Figure was not created with the ABs unit-layout API")
    result = copy.deepcopy(fig._abs_unit_layout)
    for ax in fig.axes:
        name = getattr(ax, '_abs_unit_name', None)
        if name in result['panels']:
            box = ax.get_position()
            result['panels'][name]['plot_box_inches'] = [
                box.x0*fig.get_figwidth(), box.y0*fig.get_figheight(),
                box.width*fig.get_figwidth(), box.height*fig.get_figheight()]
    return result


def _fit_unit_slots(fig, axes, style, label_pad_pt, w_pad):
    """Fit decorations WITHIN immutable slots; never stretch other panels."""
    spec = fig._abs_unit_layout
    if not np.allclose(fig.get_size_inches(), spec['canvas_inches'], atol=1e-9, rtol=0):
        raise ValueError("Do not resize a unit-layout figure directly; change its mosaic")
    padding = style.font*.7
    for _ in range(3):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        scale = 72/fig.dpi
        margins = []
        for ax in axes:
            original = ax.get_position(original=True)
            bounds = original.transformed(fig.transFigure)
            boxes = [ax.get_tightbbox(renderer)]
            for artist in ax.collections:
                cb = getattr(artist, 'colorbar', None)
                if cb is not None:
                    boxes.append(cb.ax.get_tightbbox(renderer))
            boxes = [b for b in boxes if b is not None]
            if not boxes:
                continue
            left=min(b.x0 for b in boxes);right=max(b.x1 for b in boxes)
            bottom=min(b.y0 for b in boxes);top=max(b.y1 for b in boxes)
            margins.append([max(0,bounds.x0-left)*scale,
                            max(0,right-bounds.x1)*scale,
                            max(0,bounds.y0-bottom)*scale,
                            max(0,top-bounds.y1)*scale])
        decoration = np.max(margins, axis=0) if margins else np.zeros(4)
        left,right,bottom,top = decoration + ([style.font*w_pad/2]*2 + [padding]*2)
        if len(axes)>1:
            top=max(top,style.label+label_pad_pt+padding)
        for ax in axes:
            name=getattr(ax, '_abs_unit_name', None)
            if name not in spec['panels']:
                raise ValueError("Only unit-layout data axes may be finalized together")
            x,y,width,height=spec['panels'][name]['box_inches']
            plot_width=width-(left+right)/72
            plot_height=height-(bottom+top)/72
            if plot_width<=0 or plot_height<=0:
                raise ValueError(f"Panel {name!r} needs more whole units for its labels")
            ax.set_position([(x+left/72)/fig.get_figwidth(),
                             (y+bottom/72)/fig.get_figheight(),
                             plot_width/fig.get_figwidth(),
                             plot_height/fig.get_figheight()])
    fig.canvas.draw()

def set_axis(ax, *, xlim, ylim, xticks, yticks, xlabel, ylabel):
    """Caller-owned equal ticks must seal both limits and cover all data."""
    for limits, ticks in ((xlim, xticks), (ylim, yticks)):
        ticks = np.asarray(ticks, dtype=float)
        if (ticks.ndim != 1 or len(ticks) < 2 or not np.isfinite(ticks).all()
                or not np.all(np.diff(ticks) > 0)
                or not np.allclose(np.diff(ticks), np.diff(ticks)[0])
                or not np.allclose([ticks[0], ticks[-1]], limits)):
            raise ValueError("Use increasing equal ticks with endpoints at limits")
    ax.set(xticks=xticks, yticks=yticks, xlim=xlim, ylim=ylim,
           xlabel=xlabel, ylabel=ylabel)
    return ax

def finalize_layout(fig, axes, *, style=DEFAULT, label_pad_pt=5, w_pad=1.1, top=0.94, bottom=0):
    """Run after plotting; label complete axes bbox, then freeze layout.

    Re-call after any label/legend/layout change. Returns panel Text objects.
    """
    for artist in list(fig.texts):
        if artist.get_gid() == "abs1-panel-label":
            artist.remove()
    axes = np.asarray(list(axes.values()) if isinstance(axes, dict) else axes,
                      dtype=object).ravel()
    if hasattr(fig, '_abs_unit_layout'):
        if top != 0.94 or bottom != 0:
            raise ValueError("Reserve whole mosaic cells for legends; do not crop or rescale the grid")
        _fit_unit_slots(fig, axes, style, label_pad_pt, w_pad)
    else:
        fig.tight_layout(pad=0.7, w_pad=w_pad, h_pad=2.0,
                         rect=(0, bottom, 1, top))
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    if len(axes) > 26:
        raise ValueError("Split figures with more than 26 labelled panels")
    labels = []
    if len(axes) > 1:
        for letter, ax in zip(string.ascii_lowercase, axes):
            full = ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted())
            top = ax.get_position().y1 + label_pad_pt / (72*fig.get_figheight())
            labels.append(fig.text(full.x0, top, letter, ha="left", va="bottom",
                                   fontsize=style.label, fontweight="bold",
                                   gid="abs1-panel-label"))
    fig.canvas.draw()
    for label in labels:
        box = label.get_window_extent(fig.canvas.get_renderer())
        if not fig.bbox.contains(box.x0, box.y0) or not fig.bbox.contains(box.x1, box.y1):
            raise ValueError("Panel label exceeds canvas; adjust layout/panel size")
    return labels
