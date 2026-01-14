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


TILE_SERVERS: dict[str, TileServer] = {
    "BasemapAT": _basemap_at_server("basemapat", "BasemapAT", "geolandbasemap"),
    "BasemapAT Grau": _basemap_at_server(
        "basemapat-grau", "BasemapAT Grau", "bmapgrau"
    ),
    "BasemapAT Overlay": _basemap_at_server(
        "basemapat-overlay", "BasemapAT Overlay", "bmapoverlay"
    ),
    "BasemapAT Terrain": _basemap_at_server(
        "basemapat-terrain", "BasemapAT Terrain", "bmapgelaende", ext="jpeg"
    ),
    "BasemapAT Surface": _basemap_at_server(
        "basemapat-surface", "BasemapAT Surface", "bmapoberflaeche", ext="jpeg"
    ),
    "BasemapAT Highdpi": _basemap_at_server(
        "basemapat-highdpi", "BasemapAT Highdpi", "bmaphidpi", zoom_max=19
    ),
    "BasemapAT Orthofoto": _basemap_at_server(
        "basemapat-orthofoto", "BasemapAT Orthofoto", "bmaporthofoto30cm", ext="jpeg"
    ),
}
"""Basemap.at tile servers."""
