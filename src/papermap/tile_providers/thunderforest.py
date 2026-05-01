"""Thunderforest tile provider configurations.

Thunderforest provides high-quality map tiles including outdoor,
cycle, transport, and landscape maps. Requires an API key.

See: https://www.thunderforest.com/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider
from papermap.tile_providers._attribution import OSM_ATTRIBUTION, OSM_HTML_ATTRIBUTION

TF_ATTRIBUTION = f"Maps © Thunderforest, Data {OSM_ATTRIBUTION}"
TF_HTML_ATTRIBUTION = (
    'Maps © <a href="https://www.thunderforest.com/">Thunderforest</a>, '
    f"Data {OSM_HTML_ATTRIBUTION}"
)


def _thunderforest_provider(
    key: str, name: str, variant: str, zoom_max: int = 22
) -> TileProvider:
    """Create a Thunderforest tile provider configuration."""
    return TileProvider(
        key=key,
        name=name,
        attribution=TF_ATTRIBUTION,
        html_attribution=TF_HTML_ATTRIBUTION,
        url_template=f"https://{{s}}.tile.thunderforest.com/{variant}/{{z}}/{{x}}/{{y}}.png?apikey={{a}}",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _thunderforest_provider(
        "thunderforest-opencyclemap", "Thunderforest OpenCycleMap", "cycle"
    ),
    _thunderforest_provider(
        "thunderforest-transport", "Thunderforest Transport", "transport"
    ),
    _thunderforest_provider(
        "thunderforest-transport-dark", "Thunderforest Transport Dark", "transport-dark"
    ),
    _thunderforest_provider(
        "thunderforest-spinalmap", "Thunderforest SpinalMap", "spinal-map"
    ),
    _thunderforest_provider(
        "thunderforest-landscape", "Thunderforest Landscape", "landscape"
    ),
    _thunderforest_provider(
        "thunderforest-outdoors", "Thunderforest Outdoors", "outdoors"
    ),
    _thunderforest_provider(
        "thunderforest-pioneer", "Thunderforest Pioneer", "pioneer"
    ),
    _thunderforest_provider(
        "thunderforest-mobileatlas", "Thunderforest MobileAtlas", "mobile-atlas"
    ),
    _thunderforest_provider(
        "thunderforest-neighbourhood", "Thunderforest Neighbourhood", "neighbourhood"
    ),
    _thunderforest_provider("thunderforest-atlas", "Thunderforest Atlas", "atlas"),
]
"""Thunderforest tile providers."""
