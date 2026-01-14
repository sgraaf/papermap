"""OpenTopoMap tile provider configuration.

OpenTopoMap is a topographic map based on OpenStreetMap data with
contour lines and hillshading.

See: https://opentopomap.org/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

TILE_PROVIDERS: list[TileProvider] = [
    TileProvider(
        key="opentopomap",
        name="OpenTopoMap",
        attribution=(
            "Map data: © OpenStreetMap contributors, SRTM. "
            "Map style: © OpenTopoMap (CC-BY-SA)"
        ),
        html_attribution=(
            'Map data: © <a href="https://www.openstreetmap.org/copyright">'
            "OpenStreetMap contributors</a>, "
            '<a href="https://www2.jpl.nasa.gov/srtm/">SRTM</a>. '
            'Map style: © <a href="https://opentopomap.org/">OpenTopoMap</a> '
            '(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
        ),
        url_template="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=17,
    ),
]
"""OpenTopoMap tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
