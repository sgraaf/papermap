"""NL Maps (Dutch/Netherlands) tile provider configurations.

NL Maps provides official Dutch government map data
from PDOK (Publieke Dienstverlening Op de Kaart).

See: https://www.pdok.nl/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

NLMAPS_ATTRIBUTION = "Kaartgegevens © Kadaster"
NLMAPS_HTML_ATTRIBUTION = (
    'Kaartgegevens © <a href="https://www.kadaster.nl/">Kadaster</a>'
)
NLMAPS_BOUNDS = (3.37, 50.75, 7.21, 53.47)


def _nlmaps_provider(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 19,
) -> TileProvider:
    """Create a NL Maps tile provider configuration."""
    return TileProvider(
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


TILE_PROVIDERS: list[TileProvider] = [
    _nlmaps_provider("nlmaps-standaard", "NLMaps Standaard", "standaard"),
    _nlmaps_provider("nlmaps-pastel", "NLMaps Pastel", "pastel"),
    _nlmaps_provider("nlmaps-grijs", "NLMaps Grijs", "grijs"),
    _nlmaps_provider("nlmaps-water", "NLMaps Water", "water"),
    TileProvider(
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
"""NL Maps tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
