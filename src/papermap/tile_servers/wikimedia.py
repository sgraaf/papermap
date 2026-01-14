"""Wikimedia Maps tile server configuration.

Wikimedia provides map tiles based on OpenStreetMap data
for use in Wikipedia and other Wikimedia projects.

See: https://maps.wikimedia.org/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

TILE_SERVERS: dict[str, TileServer] = {
    "Wikimedia": TileServer(
        key="wikimedia",
        name="Wikimedia",
        attribution="Map data: © OpenStreetMap contributors. Map style: © Wikimedia Foundation",
        html_attribution=(
            'Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. '
            'Map style: © <a href="https://foundation.wikimedia.org/">Wikimedia Foundation</a>'
        ),
        url_template="https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=19,
    ),
}
"""Wikimedia tile servers."""
