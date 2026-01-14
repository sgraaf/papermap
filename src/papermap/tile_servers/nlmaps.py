"""NL Maps (Dutch/Netherlands) tile server configurations.

NL Maps provides official Dutch government map data
from PDOK (Publieke Dienstverlening Op de Kaart).

See: https://www.pdok.nl/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

NLMAPS_ATTRIBUTION = "Kaartgegevens © Kadaster"
NLMAPS_HTML_ATTRIBUTION = (
    'Kaartgegevens © <a href="https://www.kadaster.nl/">Kadaster</a>'
)
NLMAPS_BOUNDS = (3.37, 50.75, 7.21, 53.47)


def _nlmaps_server(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 19,
) -> TileServer:
    """Create a NL Maps tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=NLMAPS_ATTRIBUTION,
        html_attribution=NLMAPS_HTML_ATTRIBUTION,
        url_template=f"https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{variant}/EPSG:3857/{{z}}/{{x}}/{{y}}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
        bounds=NLMAPS_BOUNDS,
    )


TILE_SERVERS: list[TileServer] = [
    _nlmaps_server("nlmaps-standaard", "NLMaps Standaard", "standaard"),
    _nlmaps_server("nlmaps-pastel", "NLMaps Pastel", "pastel"),
    _nlmaps_server("nlmaps-grijs", "NLMaps Grijs", "grijs"),
    _nlmaps_server("nlmaps-water", "NLMaps Water", "water"),
    TileServer(
        key="nlmaps-luchtfoto",
        name="NLMaps Luchtfoto",
        attribution=NLMAPS_ATTRIBUTION,
        html_attribution=NLMAPS_HTML_ATTRIBUTION,
        url_template="https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0/Actueel_orthoHR/EPSG:3857/{z}/{x}/{y}.jpeg",
        subdomains=None,
        zoom_min=0,
        zoom_max=19,
        bounds=NLMAPS_BOUNDS,
    ),
]
"""NL Maps tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
