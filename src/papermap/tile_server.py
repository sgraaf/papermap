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


TILE_SERVERS_MAP: dict[str, TileServer] = {
    "OpenStreetMap": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="http://{mirror}.tile.osm.org/{zoom}/{x}/{y}.png",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    "OpenStreetMap Monochrome": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="https://tiles.wmflabs.org/bw-mapnik/{zoom}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=19,
    ),
    "OpenTopoMap": TileServer(
        attribution="Map data: © OpenStreetMap contributors, SRTM. Map style: © OpenTopoMap (CC-BY-SA)",
        url_template="https://{mirror}.tile.opentopomap.org/{zoom}/{x}/{y}.png",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=17,
    ),
    "Thunderforest Landscape": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="https://{mirror}.tile.thunderforest.com/landscape/{zoom}/{x}/{y}.png?apikey={api_key}",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=22,
    ),
    "Thunderforest Outdoors": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="https://{mirror}.tile.thunderforest.com/outdoors/{zoom}/{x}/{y}.png?apikey={api_key}",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=22,
    ),
    "Thunderforest Transport": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="https://{mirror}.tile.thunderforest.com/transport/{zoom}/{x}/{y}.png?apikey={api_key}",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=22,
    ),
    "Thunderforest OpenCycleMap": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="https://{mirror}.tile.thunderforest.com/cycle/{zoom}/{x}/{y}.png?apikey={api_key}",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=22,
    ),
    "ESRI Standard": TileServer(
        attribution="Map data: © Esri",
        url_template="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{zoom}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=17,
    ),
    "ESRI Satellite": TileServer(
        attribution="Map data: © Esri",
        url_template="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=17,
    ),
    "ESRI Topo": TileServer(
        attribution="Map data: © Esri",
        url_template="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{zoom}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=20,
    ),
    "ESRI Dark Gray": TileServer(
        attribution="Map data: © Esri",
        url_template="https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{zoom}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=16,
    ),
    "ESRI Light Gray": TileServer(
        attribution="Map data: © Esri",
        url_template="https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{zoom}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=16,
    ),
    "ESRI Transportation": TileServer(
        attribution="Map data: © Esri",
        url_template="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{zoom}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=20,
    ),
    "Geofabrik Topo": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="http://{mirror}.tile.geofabrik.de/15173cf79060ee4a66573954f6017ab0/{zoom}/{x}/{y}.png",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps": TileServer(
        attribution="Map data: © Google",
        url_template="http://mt{mirror}.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={zoom}",
        mirrors=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps Satellite": TileServer(
        attribution="Map data: © Google",
        url_template="http://mt{mirror}.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={zoom}",
        mirrors=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps Satellite Hybrid": TileServer(
        attribution="Map data: © Google",
        url_template="http://mt{mirror}.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={zoom}",
        mirrors=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps Terrain": TileServer(
        attribution="Map data: © Google",
        url_template="http://mt{mirror}.google.com/vt/lyrs=t&hl=en&x={x}&y={y}&z={zoom}",
        mirrors=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps Terrain Hybrid": TileServer(
        attribution="Map data: © Google",
        url_template="http://mt{mirror}.google.com/vt/lyrs=p&hl=en&x={x}&y={y}&z={zoom}",
        mirrors=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "HERE Terrain": TileServer(
        attribution="Map data: © HERE",
        url_template="https://{mirror}.aerial.maps.ls.hereapi.com/maptile/2.1/maptile/newest/terrain.day/{zoom}/{x}/{y}/256/png8?apiKey={api_key}",
        mirrors=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=20,
    ),
    "HERE Satellite": TileServer(
        attribution="Map data: © HERE",
        url_template="https://{mirror}.aerial.maps.ls.hereapi.com/maptile/2.1/maptile/newest/satellite.day/{zoom}/{x}/{y}/256/png8?apiKey={api_key}",
        mirrors=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=20,
    ),
    "HERE Hybrid": TileServer(
        attribution="Map data: © HERE",
        url_template="https://{mirror}.aerial.maps.ls.hereapi.com/maptile/2.1/maptile/newest/hybrid.day/{zoom}/{x}/{y}/256/png8?apiKey={api_key}",
        mirrors=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=20,
    ),
    "Mapy.cz": TileServer(
        attribution="Map data: © OpenStreetMap contributors. Map style: © Sesznam.cz",
        url_template="https://m{mirror}.mapserver.mapy.cz/turist-m/{zoom}-{x}-{y}.png",
        mirrors=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=19,
    ),
    "Stamen Terrain": TileServer(
        attribution="Map data: © OpenStreetMap contributors. Map style: © Stamen Design (CC-BY-3.0)",
        url_template="http://{mirror}.tile.stamen.com/terrain/{zoom}/{x}/{y}.png",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=18,
    ),
    "Stamen Toner": TileServer(
        attribution="Map data: © OpenStreetMap contributors. Map style: © Stamen Design (CC-BY-3.0)",
        url_template="http://{mirror}.tile.stamen.com/toner/{zoom}/{x}/{y}.png",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=18,
    ),
    "Stamen Toner Lite": TileServer(
        attribution="Map data: © OpenStreetMap contributors. Map style: © Stamen Design (CC-BY-3.0)",
        url_template="http://{mirror}.tile.stamen.com/toner-lite/{zoom}/{x}/{y}.png",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=18,
    ),
    "Komoot": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="http://{mirror}.tile.komoot.de/komoot-2/{zoom}/{x}/{y}.png",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    "Wikimedia": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="https://maps.wikimedia.org/osm-intl/{zoom}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=19,
    ),
    "Hike & Bike": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="http://{mirror}.tiles.wmflabs.org/hikebike/{zoom}/{x}/{y}.png",
        mirrors=["a", "b", "c"],
        zoom_min=0,
        zoom_max=20,
    ),
    "AllTrails": TileServer(
        attribution="Map data: © OpenStreetMap contributors",
        url_template="http://alltrails.com/tiles/alltrailsOutdoors/{zoom}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=20,
    ),
}
"""Map of tile server names to `TileServer` instances."""

TILE_SERVERS = tuple(TILE_SERVERS_MAP.keys())
"""Tuple of available tile server names."""

DEFAULT_TILE_SERVER: str = "OpenStreetMap"
"""Default tile server name."""
