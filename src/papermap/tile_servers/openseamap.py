"""OpenSeaMap tile server configuration.

OpenSeaMap is a nautical chart based on OpenStreetMap data,
designed for sailors and maritime navigation.

See: https://openseamap.org/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

TILE_SERVERS: list[TileServer] = [
    TileServer(
        key="openseamap",
        name="OpenSeaMap",
        attribution="Map data: © OpenSeaMap contributors",
        html_attribution=(
            'Map data: © <a href="https://www.openseamap.org/">OpenSeaMap contributors</a>'
        ),
        url_template="https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
]
"""OpenSeaMap tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
