"""Jawg Maps tile server configurations.

Jawg provides customizable vector and raster map tiles.
Requires an API key (access token).

See: https://www.jawg.io/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

JAWG_ATTRIBUTION = "© Jawg Maps, © OpenStreetMap contributors"
JAWG_HTML_ATTRIBUTION = (
    '© <a href="https://www.jawg.io/">Jawg</a> Maps, '
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
)


def _jawg_server(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 22,
) -> TileServer:
    """Create a Jawg Maps tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=JAWG_ATTRIBUTION,
        html_attribution=JAWG_HTML_ATTRIBUTION,
        url_template=f"https://tile.jawg.io/{variant}/{{z}}/{{x}}/{{y}}.png?access-token={{a}}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: dict[str, TileServer] = {
    "Jawg Streets": _jawg_server("jawg-streets", "Jawg Streets", "jawg-streets"),
    "Jawg Terrain": _jawg_server("jawg-terrain", "Jawg Terrain", "jawg-terrain"),
    "Jawg Sunny": _jawg_server("jawg-sunny", "Jawg Sunny", "jawg-sunny"),
    "Jawg Dark": _jawg_server("jawg-dark", "Jawg Dark", "jawg-dark"),
    "Jawg Light": _jawg_server("jawg-light", "Jawg Light", "jawg-light"),
    "Jawg Matrix": _jawg_server("jawg-matrix", "Jawg Matrix", "jawg-matrix"),
}
"""Jawg Maps tile servers."""
