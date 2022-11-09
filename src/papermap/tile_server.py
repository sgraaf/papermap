from dataclasses import dataclass
from typing import List, Optional, Union


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
    mirrors: Optional[List[Optional[Union[str, int]]]] = None
