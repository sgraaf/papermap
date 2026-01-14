"""Swiss Federal Geoportal tile server configurations.

SwissFederalGeoportal (geo.admin.ch) provides official Swiss government
map data including topographic maps, satellite imagery, and historical maps.

See: https://www.geo.admin.ch/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

SWISS_ATTRIBUTION = "© swisstopo"
SWISS_HTML_ATTRIBUTION = '© <a href="https://www.swisstopo.admin.ch/">swisstopo</a>'
SWISS_BOUNDS = (5.140242, 45.398181, 11.47757, 48.230651)


def _swiss_server(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 18,
    ext: str = "jpeg",
) -> TileServer:
    """Create a Swiss Federal Geoportal tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=SWISS_ATTRIBUTION,
        html_attribution=SWISS_HTML_ATTRIBUTION,
        url_template=f"https://wmts.geo.admin.ch/1.0.0/{variant}/default/current/3857/{{z}}/{{x}}/{{y}}.{ext}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
        bounds=SWISS_BOUNDS,
    )


TILE_SERVERS: list[TileServer] = [
    _swiss_server(
        "swissfederalgeoportal-nationalmapcolor",
        "SwissFederalGeoportal NationalMapColor",
        "ch.swisstopo.pixelkarte-farbe",
    ),
    _swiss_server(
        "swissfederalgeoportal-nationalmapgrey",
        "SwissFederalGeoportal NationalMapGrey",
        "ch.swisstopo.pixelkarte-grau",
    ),
    _swiss_server(
        "swissfederalgeoportal-swissimage",
        "SwissFederalGeoportal SWISSIMAGE",
        "ch.swisstopo.swissimage",
        zoom_max=20,
    ),
]
"""Swiss Federal Geoportal tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
