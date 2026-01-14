"""Stadia Maps tile server configurations.

Stadia Maps provides high-quality vector and raster map tiles,
including the classic Stamen map styles (Toner, Terrain, Watercolor).

See: https://stadiamaps.com/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

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


def _stadia_server(  # noqa: PLR0913
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 20,
    ext: str = "png",
    use_stamen_attribution: bool = False,  # noqa: FBT001, FBT002
) -> TileServer:
    """Create a Stadia Maps tile server configuration."""
    if use_stamen_attribution:
        attribution = STAMEN_ATTRIBUTION
        html_attribution = STAMEN_HTML_ATTRIBUTION
    else:
        attribution = STADIA_ATTRIBUTION
        html_attribution = STADIA_HTML_ATTRIBUTION

    return TileServer(
        key=key,
        name=name,
        attribution=attribution,
        html_attribution=html_attribution,
        url_template=f"https://tiles.stadiamaps.com/tiles/{variant}/{{z}}/{{x}}/{{y}}.{ext}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: list[TileServer] = [
    # Stadia native styles
    _stadia_server("stadia-alidadesmooth", "Stadia AlidadeSmooth", "alidade_smooth"),
    _stadia_server(
        "stadia-alidasesmoothdark", "Stadia AlidadeSmoothDark", "alidade_smooth_dark"
    ),
    _stadia_server(
        "stadia-alidasesatellite",
        "Stadia AlidadeSatellite",
        "alidade_satellite",
        zoom_max=20,
        ext="jpg",
    ),
    _stadia_server("stadia-osmbright", "Stadia OSMBright", "osm_bright"),
    _stadia_server("stadia-outdoors", "Stadia Outdoors", "outdoors"),
    # Stamen styles (now hosted by Stadia)
    _stadia_server(
        "stadia-stamentoner",
        "Stadia StamenToner",
        "stamen_toner",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_server(
        "stadia-stamentonerbackground",
        "Stadia StamenTonerBackground",
        "stamen_toner_background",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_server(
        "stadia-stamentonerlines",
        "Stadia StamenTonerLines",
        "stamen_toner_lines",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_server(
        "stadia-stamentonerlabels",
        "Stadia StamenTonerLabels",
        "stamen_toner_labels",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_server(
        "stadia-stamentonerlite",
        "Stadia StamenTonerLite",
        "stamen_toner_lite",
        zoom_max=20,
        use_stamen_attribution=True,
    ),
    _stadia_server(
        "stadia-stamenwatercolor",
        "Stadia StamenWatercolor",
        "stamen_watercolor",
        zoom_max=16,
        ext="jpg",
        use_stamen_attribution=True,
    ),
    _stadia_server(
        "stadia-stamenterrain",
        "Stadia StamenTerrain",
        "stamen_terrain",
        zoom_max=18,
        use_stamen_attribution=True,
    ),
    _stadia_server(
        "stadia-stamenterrainbackground",
        "Stadia StamenTerrainBackground",
        "stamen_terrain_background",
        zoom_max=18,
        use_stamen_attribution=True,
    ),
    _stadia_server(
        "stadia-stamenterrainlabels",
        "Stadia StamenTerrainLabels",
        "stamen_terrain_labels",
        zoom_max=18,
        use_stamen_attribution=True,
    ),
    _stadia_server(
        "stadia-stamenterrainlines",
        "Stadia StamenTerrainLines",
        "stamen_terrain_lines",
        zoom_max=18,
        use_stamen_attribution=True,
    ),
]
"""Stadia Maps tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
