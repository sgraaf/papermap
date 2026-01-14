"""Google Maps tile provider configurations.

Google Maps provides various map styles including roadmap, satellite,
terrain, and hybrid views.

Note: Use of Google Maps tiles may be subject to Google's Terms of Service.
See: https://www.google.com/intl/en_us/help/terms_maps/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

GOOGLE_ATTRIBUTION = "Map data: © Google"
GOOGLE_HTML_ATTRIBUTION = 'Map data: © <a href="https://www.google.com/maps">Google</a>'


def _google_provider(
    key: str,
    name: str,
    lyrs: str,
    zoom_max: int = 20,
) -> TileProvider:
    """Create a Google Maps tile provider configuration."""
    return TileProvider(
        key=key,
        name=name,
        attribution=GOOGLE_ATTRIBUTION,
        html_attribution=GOOGLE_HTML_ATTRIBUTION,
        url_template=f"https://mt{{s}}.google.com/vt/lyrs={lyrs}&x={{x}}&y={{y}}&z={{z}}",
        subdomains=[0, 1, 2, 3],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _google_provider("google-maps", "Google Maps", "m"),
    _google_provider("google-maps-satellite", "Google Maps Satellite", "s"),
    _google_provider(
        "google-maps-satellite-hybrid", "Google Maps Satellite Hybrid", "y"
    ),
    _google_provider("google-maps-terrain", "Google Maps Terrain", "t"),
    _google_provider("google-maps-terrain-hybrid", "Google Maps Terrain Hybrid", "p"),
    _google_provider("google-maps-roads", "Google Maps Roads", "h"),
]
"""Google Maps tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
