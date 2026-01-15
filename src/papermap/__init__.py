"""PaperMap is a Python package and CLI for creating ready-to-print paper maps."""

from . import geodesy
from .papermap import PaperMap

__all__ = ["PaperMap", "geodesy"]
