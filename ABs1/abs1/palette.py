"""Load the sibling ABsCol library for both package imports and standalone demos."""
import importlib.util
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def _library():
    source = Path(__file__).resolve().parents[2] / "ABsCol" / "palette.py"
    spec = importlib.util.spec_from_file_location("_abs1_color_library", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def list_palettes():
    return _library().list_palettes()

def get_palette(name):
    return _library().get_palette(name)

def get_color(name, index=0):
    return _library().get_color(name, index)

def get_cmap(name, *, indices=None, continuous=False):
    return _library().get_cmap(name, indices=indices, continuous=continuous)
