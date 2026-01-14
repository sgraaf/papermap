"""MapTiler tile server configurations.

MapTiler provides high-quality vector and raster map tiles
with various styles. Requires an API key.

See: https://www.maptiler.com/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

MAPTILER_ATTRIBUTION = "© MapTiler, © OpenStreetMap contributors"
MAPTILER_HTML_ATTRIBUTION = (
    '© <a href="https://www.maptiler.com/copyright/">MapTiler</a>, '
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
)


def _maptiler_server(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 21,
    ext: str = "png",
) -> TileServer:
    """Create a MapTiler tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=MAPTILER_ATTRIBUTION,
        html_attribution=MAPTILER_HTML_ATTRIBUTION,
        url_template=f"https://api.maptiler.com/maps/{variant}/{{z}}/{{x}}/{{y}}.{ext}?key={{a}}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: list[TileServer] = [
    _maptiler_server("maptiler-streets", "MapTiler Streets", "streets-v2"),
    _maptiler_server("maptiler-basic", "MapTiler Basic", "basic-v2"),
    _maptiler_server("maptiler-bright", "MapTiler Bright", "bright-v2"),
    _maptiler_server("maptiler-pastel", "MapTiler Pastel", "pastel"),
    _maptiler_server("maptiler-positron", "MapTiler Positron", "positron"),
    _maptiler_server("maptiler-hybrid", "MapTiler Hybrid", "hybrid", ext="jpg"),
    _maptiler_server(
        "maptiler-satellite", "MapTiler Satellite", "satellite-v2", ext="jpg"
    ),
    _maptiler_server("maptiler-toner", "MapTiler Toner", "toner-v2"),
    _maptiler_server("maptiler-topo", "MapTiler Topo", "topo-v2"),
    _maptiler_server("maptiler-winter", "MapTiler Winter", "winter-v2"),
    _maptiler_server("maptiler-outdoor", "MapTiler Outdoor", "outdoor-v2"),
]
"""MapTiler tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
