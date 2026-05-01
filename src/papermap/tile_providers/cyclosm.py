"""CyclOSM tile provider configuration.

CyclOSM is a bicycle-oriented map built on top of OpenStreetMap data.
It aims to provide a beautiful and practical map for cyclists.

See: https://www.cyclosm.org/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider
from papermap.tile_providers._attribution import OSM_ATTRIBUTION, OSM_HTML_ATTRIBUTION

TILE_PROVIDERS: list[TileProvider] = [
    TileProvider(
        key="cyclosm",
        name="CyclOSM",
        attribution=(
            f"Map data: {OSM_ATTRIBUTION}. "
            "Map style: © CyclOSM (hosted by OpenStreetMap France)"
        ),
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Map style: © <a href="https://www.cyclosm.org/">CyclOSM</a> '
            '(hosted by <a href="https://openstreetmap.fr/">OpenStreetMap France</a>)'
        ),
        url_template="https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=20,
    ),
]
"""CyclOSM tile providers."""
