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


TILE_SERVERS_MAP: dict[str, TileServer] = {
    "OpenStreetMap": TileServer(
        key="openstreetmap",
        name="OpenStreetMap",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="http://{s}.tile.osm.org/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    "OpenStreetMap Monochrome": TileServer(
        key="openstreetmap-monochrome",
        name="OpenStreetMap Monochrome",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=19,
    ),
    "OpenTopoMap": TileServer(
        key="opentopomap",
        name="OpenTopoMap",
        attribution="Map data: © OpenStreetMap contributors, SRTM. Map style: © OpenTopoMap (CC-BY-SA)",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>, <a href="https://www2.jpl.nasa.gov/srtm/">SRTM</a>. Map style: © <a href="https://opentopomap.org/">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
        url_template="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=17,
    ),
    "Thunderforest Landscape": TileServer(
        key="thunderforest-landscape",
        name="Thunderforest Landscape",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="https://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey={a}",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=22,
    ),
    "Thunderforest Outdoors": TileServer(
        key="thunderforest-outdoors",
        name="Thunderforest Outdoors",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey={a}",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=22,
    ),
    "Thunderforest Transport": TileServer(
        key="thunderforest-transport",
        name="Thunderforest Transport",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="https://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey={a}",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=22,
    ),
    "Thunderforest OpenCycleMap": TileServer(
        key="thunderforest-opencyclemap",
        name="Thunderforest OpenCycleMap",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="https://{s}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png?apikey={a}",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=22,
    ),
    "ESRI Standard": TileServer(
        key="esri-standard",
        name="ESRI Standard",
        attribution="Map data: © Esri",
        html_attribution='Map data: © <a href="https://www.esri.com/">Esri</a>',
        url_template="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=17,
    ),
    "ESRI Satellite": TileServer(
        key="esri-satellite",
        name="ESRI Satellite",
        attribution="Map data: © Esri",
        html_attribution='Map data: © <a href="https://www.esri.com/">Esri</a>',
        url_template="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=17,
    ),
    "ESRI Topo": TileServer(
        key="esri-topo",
        name="ESRI Topo",
        attribution="Map data: © Esri",
        html_attribution='Map data: © <a href="https://www.esri.com/">Esri</a>',
        url_template="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=20,
    ),
    "ESRI Dark Gray": TileServer(
        key="esri-dark-gray",
        name="ESRI Dark Gray",
        attribution="Map data: © Esri",
        html_attribution='Map data: © <a href="https://www.esri.com/">Esri</a>',
        url_template="https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=16,
    ),
    "ESRI Light Gray": TileServer(
        key="esri-light-gray",
        name="ESRI Light Gray",
        attribution="Map data: © Esri",
        html_attribution='Map data: © <a href="https://www.esri.com/">Esri</a>',
        url_template="https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=16,
    ),
    "ESRI Transportation": TileServer(
        key="esri-transportation",
        name="ESRI Transportation",
        attribution="Map data: © Esri",
        html_attribution='Map data: © <a href="https://www.esri.com/">Esri</a>',
        url_template="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}.png",
        zoom_min=0,
        zoom_max=20,
    ),
    "Geofabrik Topo": TileServer(
        key="geofabrik-topo",
        name="Geofabrik Topo",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="http://{s}.tile.geofabrik.de/15173cf79060ee4a66573954f6017ab0/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps": TileServer(
        key="google-maps",
        name="Google Maps",
        attribution="Map data: © Google",
        html_attribution='Map data: © <a href="https://www.google.com/maps">Google</a>',
        url_template="http://mt{s}.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}",
        subdomains=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps Satellite": TileServer(
        key="google-maps-satellite",
        name="Google Maps Satellite",
        attribution="Map data: © Google",
        html_attribution='Map data: © <a href="https://www.google.com/maps">Google</a>',
        url_template="http://mt{s}.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}",
        subdomains=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps Satellite Hybrid": TileServer(
        key="google-maps-satellite-hybrid",
        name="Google Maps Satellite Hybrid",
        attribution="Map data: © Google",
        html_attribution='Map data: © <a href="https://www.google.com/maps">Google</a>',
        url_template="http://mt{s}.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}",
        subdomains=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps Terrain": TileServer(
        key="google-maps-terrain",
        name="Google Maps Terrain",
        attribution="Map data: © Google",
        html_attribution='Map data: © <a href="https://www.google.com/maps">Google</a>',
        url_template="http://mt{s}.google.com/vt/lyrs=t&hl=en&x={x}&y={y}&z={z}",
        subdomains=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "Google Maps Terrain Hybrid": TileServer(
        key="google-maps-terrain-hybrid",
        name="Google Maps Terrain Hybrid",
        attribution="Map data: © Google",
        html_attribution='Map data: © <a href="https://www.google.com/maps">Google</a>',
        url_template="http://mt{s}.google.com/vt/lyrs=p&hl=en&x={x}&y={y}&z={z}",
        subdomains=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=19,
    ),
    "HERE Terrain": TileServer(
        key="here-terrain",
        name="HERE Terrain",
        attribution="Map data: © HERE",
        html_attribution='Map data: © <a href="https://www.here.com/">HERE</a>',
        url_template="https://{s}.aerial.maps.ls.hereapi.com/maptile/2.1/maptile/newest/terrain.day/{z}/{x}/{y}/256/png8?apiKey={a}",
        subdomains=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=20,
    ),
    "HERE Satellite": TileServer(
        key="here-satellite",
        name="HERE Satellite",
        attribution="Map data: © HERE",
        html_attribution='Map data: © <a href="https://www.here.com/">HERE</a>',
        url_template="https://{s}.aerial.maps.ls.hereapi.com/maptile/2.1/maptile/newest/satellite.day/{z}/{x}/{y}/256/png8?apiKey={a}",
        subdomains=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=20,
    ),
    "HERE Hybrid": TileServer(
        key="here-hybrid",
        name="HERE Hybrid",
        attribution="Map data: © HERE",
        html_attribution='Map data: © <a href="https://www.here.com/">HERE</a>',
        url_template="https://{s}.aerial.maps.ls.hereapi.com/maptile/2.1/maptile/newest/hybrid.day/{z}/{x}/{y}/256/png8?apiKey={a}",
        subdomains=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=20,
    ),
    "Mapy.cz": TileServer(
        key="mapy-cz",
        name="Mapy.cz",
        attribution="Map data: © OpenStreetMap contributors. Map style: © Sesznam.cz",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. Map style: © <a href="https://www.seznam.cz/">Sesznam.cz</a>',
        url_template="https://m{s}.mapserver.mapy.cz/turist-m/{z}-{x}-{y}.png",
        subdomains=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=19,
    ),
    "Stamen Terrain": TileServer(
        key="stamen-terrain",
        name="Stamen Terrain",
        attribution="Map data: © OpenStreetMap contributors. Map style: © Stamen Design (CC-BY-3.0)",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. Map style: © <a href="http://stamen.com">Stamen Design</a> (<a href="https://creativecommons.org/licenses/by/3.0/">CC-BY-3.0</a>)',
        url_template="http://{s}.tile.stamen.com/terrain/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=18,
    ),
    "Stamen Toner": TileServer(
        key="stamen-toner",
        name="Stamen Toner",
        attribution="Map data: © OpenStreetMap contributors. Map style: © Stamen Design (CC-BY-3.0)",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. Map style: © <a href="http://stamen.com">Stamen Design</a> (<a href="https://creativecommons.org/licenses/by/3.0/">CC-BY-3.0</a>)',
        url_template="http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=18,
    ),
    "Stamen Toner Lite": TileServer(
        key="stamen-toner-lite",
        name="Stamen Toner Lite",
        attribution="Map data: © OpenStreetMap contributors. Map style: © Stamen Design (CC-BY-3.0)",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. Map style: © <a href="http://stamen.com">Stamen Design</a> (<a href="https://creativecommons.org/licenses/by/3.0/">CC-BY-3.0</a>)',
        url_template="http://{s}.tile.stamen.com/toner-lite/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=18,
    ),
    "Komoot": TileServer(
        key="komoot",
        name="Komoot",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="http://{s}.tile.komoot.de/komoot-2/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    "Wikimedia": TileServer(
        key="wikimedia",
        name="Wikimedia",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=19,
    ),
    "Hike & Bike": TileServer(
        key="hike-and-bike",
        name="Hike & Bike",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="http://{s}.tiles.wmflabs.org/hikebike/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=20,
    ),
    "AllTrails": TileServer(
        key="alltrails",
        name="AllTrails",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="http://alltrails.com/tiles/alltrailsOutdoors/{z}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=20,
    ),
}
"""Map of tile server names to `TileServer` instances."""

TILE_SERVERS = tuple(TILE_SERVERS_MAP.keys())
"""Tuple of available tile server names."""

DEFAULT_TILE_SERVER: str = "OpenStreetMap"
"""Default tile server name."""
