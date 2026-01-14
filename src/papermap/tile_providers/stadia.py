"""Stadia Maps tile provider configurations.

Stadia Maps provides high-quality vector and raster map tiles,
including the classic Stamen map styles (Toner, Terrain, Watercolor).

See: https://stadiamaps.com/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

STADIA_ATTRIBUTION = "© Stadia Maps, © OpenMapTiles, © OpenStreetMap contributors"
STADIA_HTML_ATTRIBUTION = (
    '© <a href="https://stadiamaps.com/">Stadia Maps</a>, '
    '© <a href="https://openmaptiles.org/">OpenMapTiles</a>, '
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
)

STAMEN_ATTRIBUTION = (
    "Map tiles by Stamen Design, under CC BY 4.0. Data by OpenStreetMap, under ODbL"
)
STAMEN_HTML_ATTRIBUTION = (
    'Map tiles by <a href="https://stamen.com/">Stamen Design</a>, '
    'under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. '
    'Data by <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, '
    'under <a href="https://opendatacommons.org/licenses/odbl/">ODbL</a>'
)


def _stadia_provider(  # noqa: PLR0913
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 20,
    ext: str = "png",
    use_stamen_attribution: bool = False,  # noqa: FBT001, FBT002
) -> TileProvider:
    """Create a Stadia Maps tile provider configuration."""
    if use_stamen_attribution:
        attribution = STAMEN_ATTRIBUTION
        html_attribution = STAMEN_HTML_ATTRIBUTION
    else:
        attribution = STADIA_ATTRIBUTION
        html_attribution = STADIA_HTML_ATTRIBUTION

    return TileProvider(
        key=key,
        name=name,
        attribution=attribution,
        html_attribution=html_attribution,
        url_template=f"https://tiles.stadiamaps.com/tiles/{variant}/{{z}}/{{x}}/{{y}}.{ext}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    # Stadia native styles
    _stadia_provider("stadia-alidadesmooth", "Stadia AlidadeSmooth", "alidade_smooth"),
    _stadia_provider(
        "stadia-alidasesmoothdark", "Stadia AlidadeSmoothDark", "alidade_smooth_dark"
    ),
    _stadia_provider(
        "stadia-alidasesatellite",
        "Stadia AlidadeSatellite",
        "alidade_satellite",
        zoom_max=20,
        ext="jpg",
    ),
    _stadia_provider("stadia-osmbright", "Stadia OSMBright", "osm_bright"),
    _stadia_provider("stadia-outdoors", "Stadia Outdoors", "outdoors"),
    # Stamen styles (now hosted by Stadia)
    _stadia_provider(
        "stadia-stamentoner",
        "Stadia StamenToner",
        "stamen_toner",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_provider(
        "stadia-stamentonerbackground",
        "Stadia StamenTonerBackground",
        "stamen_toner_background",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_provider(
        "stadia-stamentonerlines",
        "Stadia StamenTonerLines",
        "stamen_toner_lines",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_provider(
        "stadia-stamentonerlabels",
        "Stadia StamenTonerLabels",
        "stamen_toner_labels",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_provider(
        "stadia-stamentonerlite",
        "Stadia StamenTonerLite",
        "stamen_toner_lite",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_provider(
        "stadia-stamenwatercolor",
        "Stadia StamenWatercolor",
        "stamen_watercolor",
        zoom_max=16,
        ext="jpg",
        use_stamen_attribution=True,
    ),
    _stadia_provider(
        "stadia-stamenterrain",
        "Stadia StamenTerrain",
        "stamen_terrain",
        zoom_max=18,
        use_stamen_attribution=True,
    ),
    _stadia_provider(
        "stadia-stamenterrainbackground",
        "Stadia StamenTerrainBackground",
        "stamen_terrain_background",
        zoom_max=18,
        use_stamen_attribution=True,
    ),
    _stadia_provider(
        "stadia-stamenterrainlabels",
        "Stadia StamenTerrainLabels",
        "stamen_terrain_labels",
        zoom_max=18,
        use_stamen_attribution=True,
    ),
    _stadia_provider(
        "stadia-stamenterrainlines",
        "Stadia StamenTerrainLines",
        "stamen_terrain_lines",
        zoom_max=18,
        use_stamen_attribution=True,
    ),
]
"""Stadia Maps tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
