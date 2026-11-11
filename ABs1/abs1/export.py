"""Export without tight cropping so the requested physical size is preserved."""
from pathlib import Path
from .layout import _panel_units

def save_pdf(fig, name, *, output_dir):
    """Save only PDF to an explicit directory; return the absolute path."""
    if Path(name).name != name or not name:
        raise ValueError("name must be a filename without directory components")
    _panel_units(fig.get_size_inches())  # Enforce fixed units even for caller-created figures.
    layout = getattr(fig, "_abs_unit_layout", None)
    if layout is not None and any(abs(float(a)-b)>1e-9 for a,b in
                                  zip(fig.get_size_inches(),layout["canvas_inches"])):
        raise ValueError("Canvas size must follow the unit layout; change its mosaic")
    directory = Path(output_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (name if name.endswith(".pdf") else name + ".pdf")
    fig.savefig(target, format="pdf", facecolor="white")
    return target
