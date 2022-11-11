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
    """

    x: int
    y: int
    zoom: int
    bbox: Tuple[int, int, int, int]
    image: Optional[Image] = None

    @property
    def success(self) -> bool:
        """Whether the tile was successfully downloaded or not."""
        return isinstance(self.image, Image)

    def format_url_template(
        self,
        url_template: str,
        mirror: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> str:
        """Format a URL template with the tile's coordinates and zoom level.

        Args:
            url_template: The URL template to format.
            mirror: The mirror to use. Defaults to `None`.
            api_key: The API key to use. Defaults to `None`.

        Returns:
            The formatted URL template.
        """
        return url_template.format(
            mirror=mirror,
            x=self.x,
            y=self.y,
            zoom=self.zoom,
            api_key=api_key,
        )
