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


TILE_SERVERS: list[TileServer] = [
    _thunderforest_server(
        "thunderforest-opencyclemap", "Thunderforest OpenCycleMap", "cycle"
    ),
    _thunderforest_server(
        "thunderforest-transport", "Thunderforest Transport", "transport"
    ),
    _thunderforest_server(
        "thunderforest-transport-dark", "Thunderforest Transport Dark", "transport-dark"
    ),
    _thunderforest_server(
        "thunderforest-spinalmap", "Thunderforest SpinalMap", "spinal-map"
    ),
    _thunderforest_server(
        "thunderforest-landscape", "Thunderforest Landscape", "landscape"
    ),
    _thunderforest_server(
        "thunderforest-outdoors", "Thunderforest Outdoors", "outdoors"
    ),
    _thunderforest_server("thunderforest-pioneer", "Thunderforest Pioneer", "pioneer"),
    _thunderforest_server(
        "thunderforest-mobileatlas", "Thunderforest MobileAtlas", "mobile-atlas"
    ),
    _thunderforest_server(
        "thunderforest-neighbourhood", "Thunderforest Neighbourhood", "neighbourhood"
    ),
    _thunderforest_server("thunderforest-atlas", "Thunderforest Atlas", "atlas"),
]
"""Thunderforest tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
