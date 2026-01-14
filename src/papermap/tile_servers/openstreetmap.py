"""OpenStreetMap tile server configurations.

OpenStreetMap is the free, editable map of the world. This module contains
the main OSM tile servers and regional/specialized variants.

See: https://wiki.openstreetmap.org/wiki/Tiles
"""

from __future__ import annotations

from papermap.tile_server import TileServer

OSM_ATTRIBUTION = "© OpenStreetMap contributors"
OSM_HTML_ATTRIBUTION = (
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
)

TILE_SERVERS: list[TileServer] = [
    TileServer(
        key="openstreetmap",
        name="OpenStreetMap",
        attribution=f"Map data: {OSM_ATTRIBUTION}",
        html_attribution=f"Map data: {OSM_HTML_ATTRIBUTION}",
        url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=19,
    ),
    TileServer(
        key="openstreetmap-de",
        name="OpenStreetMap DE",
        attribution=f"Map data: {OSM_ATTRIBUTION}",
        html_attribution=f"Map data: {OSM_HTML_ATTRIBUTION}",
        url_template="https://tile.openstreetmap.de/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileServer(
        key="openstreetmap-ch",
        name="OpenStreetMap CH",
        attribution=f"Map data: {OSM_ATTRIBUTION}",
        html_attribution=f"Map data: {OSM_HTML_ATTRIBUTION}",
        url_template="https://tile.osm.ch/switzerland/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
        bounds=(5.140242, 45.398181, 11.47757, 48.230651),
    ),
    TileServer(
        key="openstreetmap-france",
        name="OpenStreetMap France",
        attribution=f"Map data: {OSM_ATTRIBUTION}",
        html_attribution=f"Map data: {OSM_HTML_ATTRIBUTION}",
        url_template="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=20,
    ),
    TileServer(
        key="openstreetmap-hot",
        name="OpenStreetMap HOT",
        attribution=f"Map data: {OSM_ATTRIBUTION}. Tiles style: © Humanitarian OpenStreetMap Team",
        html_attribution=f'Map data: {OSM_HTML_ATTRIBUTION}. Tiles style: © <a href="https://www.hotosm.org/">Humanitarian OpenStreetMap Team</a>',
        url_template="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    TileServer(
        key="openstreetmap-bzh",
        name="OpenStreetMap BZH",
        attribution=f"Map data: {OSM_ATTRIBUTION}. Tiles: © Breton OpenStreetMap Team",
        html_attribution=f'Map data: {OSM_HTML_ATTRIBUTION}. Tiles: © <a href="https://www.openstreetmap.bzh/">Breton OpenStreetMap Team</a>',
        url_template="https://tile.openstreetmap.bzh/br/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=19,
        bounds=(-5.4, 46.2, -0.7, 48.9),
    ),
]
"""OpenStreetMap tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
