"""Wikimedia Maps tile provider configuration.

Wikimedia provides map tiles based on OpenStreetMap data
for use in Wikipedia and other Wikimedia projects.

See: https://maps.wikimedia.org/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider
from papermap.tile_providers._attribution import OSM_ATTRIBUTION, OSM_HTML_ATTRIBUTION

TILE_PROVIDERS: list[TileProvider] = [
    TileProvider(
        key="wikimedia",
        name="Wikimedia",
        attribution=(f"Map data: {OSM_ATTRIBUTION}. Map style: © Wikimedia Foundation"),
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Map style: © <a href="https://foundation.wikimedia.org/">Wikimedia Foundation</a>'
        ),
        url_template="https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=19,
    ),
]
"""Wikimedia tile providers."""
