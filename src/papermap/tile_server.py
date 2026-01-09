from dataclasses import dataclass, field
from itertools import cycle

from .tile import Tile


@dataclass
class TileServer:
    """A tile server.

    Args:
        attribution: The attribution of the tile server.
        url_template: The URL template of the tile server. Allowed placeholders
            are `{x}`, `{y}`, `{zoom}`, `{mirror}` and `{api_key}`, where `{x}`
            refers to the x coordinate of the tile, `{y}` refers to the y
            coordinate of the tile, `{zoom}` to the zoom level, `{mirror}` to
            the mirror (optional) and `{api_key}` to the API key (optional). See
            `<https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_servers>`_
            for more information.
        zoom_min: The minimum zoom level of the tile server.
        zoom_max: The maximum zoom level of the tile server.
        mirrors: The mirrors of the tile server. Defaults to `None`.
    """

    attribution: str
    url_template: str
    zoom_min: int
    zoom_max: int
    mirrors: list[str | int | None] | None = None
    mirrors_cycle: cycle = field(init=False)

    def __post_init__(self) -> None:
        self.mirrors_cycle = cycle(self.mirrors or [None])

    def format_url_template(self, tile: Tile, api_key: str | None = None) -> str:
        """Format the URL template with the tile's coordinates and zoom level.

        Args:
            tile: The tile to format the URL template with.
            api_key: The API key to use. Defaults to `None`.

        Returns:
            The formatted URL template.
        """
        return self.url_template.format(
            mirror=next(self.mirrors_cycle),
            x=tile.x,
            y=tile.y,
            zoom=tile.zoom,
            api_key=api_key,
        )
