from __future__ import annotations

from dataclasses import dataclass, field
from itertools import cycle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tile import Tile


@dataclass
class TileServer:
    """A tile server.

    Args:
        key: The key of the tile server (fully lowercase with dashes instead of spaces).
        name: The name of the tile server.
        attribution: The attribution of the tile server.
        html_attribution: The HTML-version of the attribution (with hyperlinks).
        url_template: The URL template of the tile server. Allowed placeholders
            are `{x}`, `{y}`, `{z}`, `{s}` and `{a}`, where `{x}`
            refers to the x coordinate of the tile, `{y}` refers to the y
            coordinate of the tile, `{z}` to the zoom level, `{s}` to
            the subdomain (optional) and `{a}` to the API key (optional). See
            `<https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_servers>`_
            for more information.
        zoom_min: The minimum zoom level of the tile server.
        zoom_max: The maximum zoom level of the tile server.
        bounds: The geographic bounds of the tile server (min_lon, min_lat, max_lon, max_lat).
            Defaults to `None`.
        subdomains: The subdomains of the tile server. Defaults to `None`.
    """

    key: str
    name: str
    attribution: str
    html_attribution: str
    url_template: str
    zoom_min: int
    zoom_max: int
    bounds: tuple[float, float, float, float] | None = None
    subdomains: list[str | int | None] | None = None
    subdomains_cycle: cycle = field(init=False)

    def __post_init__(self) -> None:
        self.subdomains_cycle = cycle(self.subdomains or [None])

    def format_url_template(self, tile: Tile, api_key: str | None = None) -> str:
        """Format the URL template with the tile's coordinates and zoom level.

        Args:
            tile: The tile to format the URL template with.
            api_key: The API key to use. Defaults to `None`.

        Returns:
            The formatted URL template.
        """
        return self.url_template.format(
            s=next(self.subdomains_cycle),
            x=tile.x,
            y=tile.y,
            z=tile.zoom,
            a=api_key,
        )


# Re-export from tile_servers package for backward compatibility
# Import must be after TileServer class to avoid circular import
from papermap.tile_servers import (  # noqa: E402
    DEFAULT_TILE_SERVER,
    TILE_SERVERS,
    TILE_SERVERS_MAP,
)

__all__ = [
    "DEFAULT_TILE_SERVER",
    "TILE_SERVERS",
    "TILE_SERVERS_MAP",
    "TileServer",
]
