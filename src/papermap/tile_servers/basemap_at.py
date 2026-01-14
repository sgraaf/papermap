"""Basemap.at (Austrian) tile server configurations.

Basemap.at provides official Austrian government map data
including topographic maps, satellite imagery, and more.

See: https://basemap.at/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

BASEMAP_AT_ATTRIBUTION = "Basemap.at"
BASEMAP_AT_HTML_ATTRIBUTION = '<a href="https://basemap.at/">Basemap.at</a>'
BASEMAP_AT_BOUNDS = (8.782379, 46.358770, 17.189532, 49.037872)


def _basemap_at_server(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 19,
    ext: str = "png",
) -> TileServer:
    """Create a Basemap.at tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=BASEMAP_AT_ATTRIBUTION,
        html_attribution=BASEMAP_AT_HTML_ATTRIBUTION,
        url_template=f"https://maps{{s}}.wien.gv.at/basemap/{variant}/normal/google3857/{{z}}/{{y}}/{{x}}.{ext}",
        subdomains=["", "1", "2", "3", "4"],
        zoom_min=0,
        zoom_max=zoom_max,
        bounds=BASEMAP_AT_BOUNDS,
    )


TILE_SERVERS: list[TileServer] = [
    _basemap_at_server("basemapat", "BasemapAT", "geolandbasemap"),
    _basemap_at_server("basemapat-grau", "BasemapAT Grau", "bmapgrau"),
    _basemap_at_server("basemapat-overlay", "BasemapAT Overlay", "bmapoverlay"),
    _basemap_at_server(
        "basemapat-terrain", "BasemapAT Terrain", "bmapgelaende", ext="jpeg"
    ),
    _basemap_at_server(
        "basemapat-surface", "BasemapAT Surface", "bmapoberflaeche", ext="jpeg"
    ),
    _basemap_at_server(
        "basemapat-highdpi", "BasemapAT Highdpi", "bmaphidpi", zoom_max=19
    ),
    _basemap_at_server(
        "basemapat-orthofoto", "BasemapAT Orthofoto", "bmaporthofoto30cm", ext="jpeg"
    ),
]
"""Basemap.at tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
