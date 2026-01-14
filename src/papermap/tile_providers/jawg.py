"""Jawg Maps tile provider configurations.

Jawg provides customizable vector and raster map tiles.
Requires an API key (access token).

See: https://www.jawg.io/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

JAWG_ATTRIBUTION = "© Jawg Maps, © OpenStreetMap contributors"
JAWG_HTML_ATTRIBUTION = (
    '© <a href="https://www.jawg.io/">Jawg</a> Maps, '
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
)


def _jawg_provider(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 22,
) -> TileProvider:
    """Create a Jawg Maps tile provider configuration."""
    return TileProvider(
        key=key,
        name=name,
        attribution=JAWG_ATTRIBUTION,
        html_attribution=JAWG_HTML_ATTRIBUTION,
        url_template=f"https://tile.jawg.io/{variant}/{{z}}/{{x}}/{{y}}.png?access-token={{a}}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _jawg_provider("jawg-streets", "Jawg Streets", "jawg-streets"),
    _jawg_provider("jawg-terrain", "Jawg Terrain", "jawg-terrain"),
    _jawg_provider("jawg-sunny", "Jawg Sunny", "jawg-sunny"),
    _jawg_provider("jawg-dark", "Jawg Dark", "jawg-dark"),
    _jawg_provider("jawg-light", "Jawg Light", "jawg-light"),
    _jawg_provider("jawg-matrix", "Jawg Matrix", "jawg-matrix"),
]
"""Jawg Maps tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
