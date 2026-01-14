"""TomTom tile provider configurations.

TomTom provides high-quality map tiles with various styles
including basic, hybrid, and labels layers. Requires an API key.

See: https://developer.tomtom.com/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

TOMTOM_ATTRIBUTION = "© TomTom"
TOMTOM_HTML_ATTRIBUTION = '© <a href="https://tomtom.com/">TomTom</a>'


def _tomtom_provider(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 22,
) -> TileProvider:
    """Create a TomTom tile provider configuration."""
    return TileProvider(
        key=key,
        name=name,
        attribution=TOMTOM_ATTRIBUTION,
        html_attribution=TOMTOM_HTML_ATTRIBUTION,
        url_template=f"https://{{s}}.api.tomtom.com/map/1/tile/{variant}/{{z}}/{{x}}/{{y}}.png?key={{a}}",
        subdomains=["a", "b", "c", "d"],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _tomtom_provider("tomtom-basic", "TomTom Basic", "basic/main"),
    _tomtom_provider("tomtom-hybrid", "TomTom Hybrid", "hybrid/main"),
    _tomtom_provider("tomtom-labels", "TomTom Labels", "labels/main"),
]
"""TomTom tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
