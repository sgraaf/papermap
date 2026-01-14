"""MapTiler tile provider configurations.

MapTiler provides high-quality vector and raster map tiles
with various styles. Requires an API key.

See: https://www.maptiler.com/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

MAPTILER_ATTRIBUTION = "© MapTiler, © OpenStreetMap contributors"
MAPTILER_HTML_ATTRIBUTION = (
    '© <a href="https://www.maptiler.com/copyright/">MapTiler</a>, '
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
)


def _maptiler_provider(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 21,
    ext: str = "png",
) -> TileProvider:
    """Create a MapTiler tile provider configuration."""
    return TileProvider(
        key=key,
        name=name,
        attribution=MAPTILER_ATTRIBUTION,
        html_attribution=MAPTILER_HTML_ATTRIBUTION,
        url_template=f"https://api.maptiler.com/maps/{variant}/{{z}}/{{x}}/{{y}}.{ext}?key={{a}}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _maptiler_provider("maptiler-streets", "MapTiler Streets", "streets-v2"),
    _maptiler_provider("maptiler-basic", "MapTiler Basic", "basic-v2"),
    _maptiler_provider("maptiler-bright", "MapTiler Bright", "bright-v2"),
    _maptiler_provider("maptiler-pastel", "MapTiler Pastel", "pastel"),
    _maptiler_provider("maptiler-positron", "MapTiler Positron", "positron"),
    _maptiler_provider("maptiler-hybrid", "MapTiler Hybrid", "hybrid", ext="jpg"),
    _maptiler_provider(
        "maptiler-satellite", "MapTiler Satellite", "satellite-v2", ext="jpg"
    ),
    _maptiler_provider("maptiler-toner", "MapTiler Toner", "toner-v2"),
    _maptiler_provider("maptiler-topo", "MapTiler Topo", "topo-v2"),
    _maptiler_provider("maptiler-winter", "MapTiler Winter", "winter-v2"),
    _maptiler_provider("maptiler-outdoor", "MapTiler Outdoor", "outdoor-v2"),
]
"""MapTiler tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
