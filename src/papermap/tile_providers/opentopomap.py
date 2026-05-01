"""OpenTopoMap tile provider configuration.

OpenTopoMap is a topographic map based on OpenStreetMap data with
contour lines and hillshading.

See: https://opentopomap.org/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider
from papermap.tile_providers._attribution import OSM_ATTRIBUTION, OSM_HTML_ATTRIBUTION

TILE_PROVIDERS: list[TileProvider] = [
    TileProvider(
        key="opentopomap",
        name="OpenTopoMap",
        attribution=(
            f"Map data: {OSM_ATTRIBUTION}, SRTM. Map style: © OpenTopoMap (CC-BY-SA)"
        ),
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}, "
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
