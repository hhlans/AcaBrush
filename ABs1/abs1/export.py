"""Export without tight cropping so the requested physical size is preserved."""
from pathlib import Path
from math import isfinite

def save_pdf(fig, name, *, output_dir):
    """Save only PDF to an explicit directory; return the absolute path."""
    if Path(name).name != name or not name:
        raise ValueError("name must be a filename without directory components")
    if any(not isfinite(float(v)) or v<=0 for v in fig.get_size_inches()):
        raise ValueError("Canvas dimensions must be finite and positive")
    measured = getattr(fig, "_abs_measured_layout", None)
    if measured is not None and any(abs(float(a)-b)>1e-9 for a,b in
                                   zip(fig.get_size_inches(),measured["canvas_inches"])):
        raise ValueError("Canvas changed after measured layout; re-run the layout solver")
    layout = getattr(fig, "_abs_unit_layout", None)
    if layout is not None and any(abs(float(a)-b)>1e-9 for a,b in
                                  zip(fig.get_size_inches(),layout["canvas_inches"])):
        raise ValueError("Canvas size must follow the unit layout; change its mosaic")
    directory = Path(output_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (name if name.endswith(".pdf") else name + ".pdf")
    fig.savefig(target, format="pdf", facecolor="white")
    return target
