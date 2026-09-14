"""Basemap.at (Austrian) tile provider configurations.

Basemap.at provides official Austrian government map data
including topographic maps, satellite imagery, and more.

See: https://basemap.at/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

BASEMAP_AT_ATTRIBUTION = "Basemap.at"
BASEMAP_AT_HTML_ATTRIBUTION = '<a href="https://basemap.at/">Basemap.at</a>'
BASEMAP_AT_BOUNDS = (8.782379, 46.358770, 17.189532, 49.037872)


def _basemap_at_provider(  # noqa: PLR0913, PLR0917
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 19,
    style: str = "normal",
    ext: str = "png",
) -> TileProvider:
    """Create a Basemap.at tile provider configuration."""
    return TileProvider(
        key=key,
        name=name,
        attribution=BASEMAP_AT_ATTRIBUTION,
        html_attribution=BASEMAP_AT_HTML_ATTRIBUTION,
        url_template=f"https://mapsneu.wien.gv.at/basemap/{variant}/{style}/google3857/{{z}}/{{y}}/{{x}}.{ext}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
        bounds=BASEMAP_AT_BOUNDS,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _basemap_at_provider("basemapat", "BasemapAT", "geolandbasemap", zoom_max=20),
    _basemap_at_provider("basemapat-grau", "BasemapAT Grau", "bmapgrau"),
    _basemap_at_provider("basemapat-overlay", "BasemapAT Overlay", "bmapoverlay"),
    _basemap_at_provider(
        "basemapat-terrain",
        "BasemapAT Terrain",
        "bmapgelaende",
        style="grau",
        ext="jpeg",
    ),
    _basemap_at_provider(
        "basemapat-surface",
        "BasemapAT Surface",
        "bmapoberflaeche",
        style="grau",
        ext="jpeg",
    ),
    _basemap_at_provider(
        "basemapat-highdpi", "BasemapAT Highdpi", "bmaphidpi", ext="jpeg"
    ),
    _basemap_at_provider(
        "basemapat-orthofoto",
        "BasemapAT Orthofoto",
        "bmaporthofoto30cm",
        zoom_max=20,
        ext="jpeg",
    ),
]
"""Basemap.at tile providers."""
