"""Small, file-backed color library. No global style changes on import."""
import json
import operator
from pathlib import Path

_PALETTES = Path(__file__).resolve().parent / "palettes"

def list_palettes():
    """Return available palette names, sorted."""
    return tuple(sorted(p.stem for p in _PALETTES.glob("*.json")))

def get_palette(name):
    """Return an immutable tuple of HEX colors in stored order."""
    if name not in list_palettes():
        raise ValueError(f"Unknown palette {name!r}; choose from {list_palettes()}")
    records = json.loads((_PALETTES / (name + ".json")).read_text())["colors"]
    colors = tuple(record["hex"] for record in records)
    if not colors:
        raise ValueError(f"Empty palette: {name}")
    for record, color in zip(records, colors):
        if len(color) != 7 or not color.startswith("#"):
            raise ValueError(f"Invalid HEX color: {color}")
        rgb = [int(color[j:j+2], 16) for j in (1, 3, 5)]
        if record.get("rgb", rgb) != rgb:
            raise ValueError(f"Inconsistent HEX/RGB: {color}")
    return colors

def get_color(name, index=0):
    """Return a zero-based color; nonnegative indices wrap around the palette."""
    index = operator.index(index)
    if index < 0:
        raise ValueError("Color index must be nonnegative")
    colors = get_palette(name)
    return colors[index % len(colors)]

def get_cmap(name, *, indices=None, continuous=False):
    """Default: categorical ListedColormap. Interpolate only if requested.

    Standard/warm palettes declare a derived sequential palette for heatmaps.
    With continuous=True and no explicit indices, use that ordered ramp.
    """
    from matplotlib.colors import ListedColormap, LinearSegmentedColormap
    if continuous and indices is None:
        get_palette(name)  # Validate the name before reading metadata.
        metadata = json.loads((_PALETTES / (name + ".json")).read_text())
        name = metadata.get("sequential_palette", name)
    colors = get_palette(name) if indices is None else tuple(get_color(name, i) for i in indices)
    if not colors or (continuous and len(colors) < 2):
        raise ValueError("Need >=1 categorical color or >=2 continuous colors")
    if continuous:
        return LinearSegmentedColormap.from_list(name + "_continuous", colors)
    return ListedColormap(colors, name=name)
