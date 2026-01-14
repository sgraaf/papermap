"""OpenSeaMap tile provider configuration.

OpenSeaMap is a nautical chart based on OpenStreetMap data,
designed for sailors and maritime navigation.

See: https://openseamap.org/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

TILE_PROVIDERS: list[TileProvider] = [
    TileProvider(
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
"""OpenSeaMap tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
