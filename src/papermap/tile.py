from dataclasses import dataclass
from typing import Optional, Tuple

from PIL.Image import Image


@dataclass
class Tile:
    """A tile from a tile server.

    Args:
        x: The x coordinate of the tile.
        y: The y coordinate of the tile.
        zoom: The zoom level of the tile.
        bbox: The bounding box of the tile.
        image: The image of the tile. Defaults to `None`.
        success: Whether the tile was successfully downloaded or not. Defaults
            to `False`.
    """

    x: int
    y: int
    zoom: int
    bbox: Tuple[int, int, int, int]
    image: Optional[Image] = None
    success: bool = False
