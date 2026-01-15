from dataclasses import dataclass

from PIL import Image

TILE_SIZE: int = 256
"""Size (width/height) of map tiles in pixels."""


@dataclass(slots=True)
class Tile:
    """A tile from a tile provider.

    Args:
        x: The x coordinate of the tile.
        y: The y coordinate of the tile.
        zoom: The zoom level of the tile.
        bbox: The bounding box of the tile.
        image: The image of the tile. Defaults to `None`.
    """

    x: int
    y: int
    zoom: int
    bbox: tuple[int, int, int, int]
    image: Image.Image | None = None

    @property
    def success(self) -> bool:
        """Whether the tile was successfully downloaded or not."""
        return isinstance(self.image, Image.Image)
