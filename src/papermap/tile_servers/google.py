"""Google Maps tile server configurations.

Google Maps provides various map styles including roadmap, satellite,
terrain, and hybrid views.

Note: Use of Google Maps tiles may be subject to Google's Terms of Service.
See: https://www.google.com/intl/en_us/help/terms_maps/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

GOOGLE_ATTRIBUTION = "Map data: © Google"
GOOGLE_HTML_ATTRIBUTION = 'Map data: © <a href="https://www.google.com/maps">Google</a>'


def _google_server(
    key: str,
    name: str,
    lyrs: str,
    zoom_max: int = 20,
) -> TileServer:
    """Create a Google Maps tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=GOOGLE_ATTRIBUTION,
        html_attribution=GOOGLE_HTML_ATTRIBUTION,
        url_template=f"https://mt{{s}}.google.com/vt/lyrs={lyrs}&x={{x}}&y={{y}}&z={{z}}",
        subdomains=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: list[TileServer] = [
    _google_server("google-maps", "Google Maps", "m"),
    _google_server("google-maps-satellite", "Google Maps Satellite", "s"),
    _google_server("google-maps-satellite-hybrid", "Google Maps Satellite Hybrid", "y"),
    _google_server("google-maps-terrain", "Google Maps Terrain", "t"),
    _google_server("google-maps-terrain-hybrid", "Google Maps Terrain Hybrid", "p"),
    _google_server("google-maps-roads", "Google Maps Roads", "h"),
]
"""Google Maps tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
