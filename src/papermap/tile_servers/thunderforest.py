"""Thunderforest tile server configurations.

Thunderforest provides high-quality map tiles including outdoor,
cycle, transport, and landscape maps. Requires an API key.

See: https://www.thunderforest.com/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

TF_ATTRIBUTION = "Maps © Thunderforest, Data © OpenStreetMap contributors"
TF_HTML_ATTRIBUTION = (
    'Maps © <a href="https://www.thunderforest.com/">Thunderforest</a>, '
    'Data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
)


def _thunderforest_server(
    key: str, name: str, variant: str, zoom_max: int = 22
) -> TileServer:
    """Create a Thunderforest tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=TF_ATTRIBUTION,
        html_attribution=TF_HTML_ATTRIBUTION,
        url_template=f"https://{{s}}.tile.thunderforest.com/{variant}/{{z}}/{{x}}/{{y}}.png?apikey={{a}}",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: dict[str, TileServer] = {
    "Thunderforest OpenCycleMap": _thunderforest_server(
        "thunderforest-opencyclemap", "Thunderforest OpenCycleMap", "cycle"
    ),
    "Thunderforest Transport": _thunderforest_server(
        "thunderforest-transport", "Thunderforest Transport", "transport"
    ),
    "Thunderforest Transport Dark": _thunderforest_server(
        "thunderforest-transport-dark", "Thunderforest Transport Dark", "transport-dark"
    ),
    "Thunderforest SpinalMap": _thunderforest_server(
        "thunderforest-spinalmap", "Thunderforest SpinalMap", "spinal-map"
    ),
    "Thunderforest Landscape": _thunderforest_server(
        "thunderforest-landscape", "Thunderforest Landscape", "landscape"
    ),
    "Thunderforest Outdoors": _thunderforest_server(
        "thunderforest-outdoors", "Thunderforest Outdoors", "outdoors"
    ),
    "Thunderforest Pioneer": _thunderforest_server(
        "thunderforest-pioneer", "Thunderforest Pioneer", "pioneer"
    ),
    "Thunderforest MobileAtlas": _thunderforest_server(
        "thunderforest-mobileatlas", "Thunderforest MobileAtlas", "mobile-atlas"
    ),
    "Thunderforest Neighbourhood": _thunderforest_server(
        "thunderforest-neighbourhood", "Thunderforest Neighbourhood", "neighbourhood"
    ),
    "Thunderforest Atlas": _thunderforest_server(
        "thunderforest-atlas", "Thunderforest Atlas", "atlas"
    ),
}
"""Thunderforest tile servers."""
