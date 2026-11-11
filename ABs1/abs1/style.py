"""Fixed physical typography; canvas size never scales styles."""
from dataclasses import dataclass
from contextlib import contextmanager
import matplotlib as mpl
from .palette import get_palette

@dataclass(frozen=True)
class Style:
    font: float = 14
    label: float = 22
    line: float = 0.9
    axes: float = 0.9
    tick: float = 0.9
    tick_length: float = 5
    marker: float = 4
    marker_edge: float = 0.9
    grid: float = 0.6
    reference: float = 0.9

DEFAULT = Style()
COLORS = get_palette("reference12")

@contextmanager
def style_context(style=DEFAULT):
    """Apply local rcParams, restoring caller settings on exit."""
    with mpl.rc_context({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.prop_cycle": mpl.cycler(color=COLORS),
        "font.size": style.font, "axes.labelsize": style.font,
        "xtick.labelsize": style.font, "ytick.labelsize": style.font,
        "legend.fontsize": style.font, "axes.linewidth": style.axes,
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.width": style.tick, "ytick.major.width": style.tick,
        "xtick.major.size": style.tick_length, "ytick.major.size": style.tick_length,
        "xtick.minor.width": style.tick, "ytick.minor.width": style.tick,
        "scatter.marker": "s",
        "lines.linewidth": style.line, "lines.markersize": style.marker,
        "lines.markeredgewidth": style.marker_edge,
        "patch.linewidth": style.line, "grid.linewidth": style.grid,
        "legend.frameon": False, "pdf.fonttype": 42, "text.usetex": False,
        "axes.formatter.useoffset": False,
    }):
        yield
