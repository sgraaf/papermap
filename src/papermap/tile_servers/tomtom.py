"""TomTom tile server configurations.

TomTom provides high-quality map tiles with various styles
including basic, hybrid, and labels layers. Requires an API key.

See: https://developer.tomtom.com/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

TOMTOM_ATTRIBUTION = "© TomTom"
TOMTOM_HTML_ATTRIBUTION = '© <a href="https://tomtom.com/">TomTom</a>'


def _tomtom_server(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 22,
) -> TileServer:
    """Create a TomTom tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=TOMTOM_ATTRIBUTION,
        html_attribution=TOMTOM_HTML_ATTRIBUTION,
        url_template=f"https://{{s}}.api.tomtom.com/map/1/tile/{variant}/{{z}}/{{x}}/{{y}}.png?key={{a}}",
        subdomains=["a", "b", "c", "d"],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: dict[str, TileServer] = {
    "TomTom Basic": _tomtom_server("tomtom-basic", "TomTom Basic", "basic/main"),
    "TomTom Hybrid": _tomtom_server("tomtom-hybrid", "TomTom Hybrid", "hybrid/main"),
    "TomTom Labels": _tomtom_server("tomtom-labels", "TomTom Labels", "labels/main"),
}
"""TomTom tile servers."""
