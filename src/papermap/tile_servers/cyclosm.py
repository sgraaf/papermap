"""CyclOSM tile server configuration.

CyclOSM is a bicycle-oriented map built on top of OpenStreetMap data.
It aims to provide a beautiful and practical map for cyclists.

See: https://www.cyclosm.org/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

TILE_SERVERS: list[TileServer] = [
    TileServer(
        key="cyclosm",
        name="CyclOSM",
        attribution="Map data: © OpenStreetMap contributors. Map style: © CyclOSM (hosted by OpenStreetMap France)",
        html_attribution=(
            'Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. '
            'Map style: © <a href="https://www.cyclosm.org/">CyclOSM</a> '
            '(hosted by <a href="https://openstreetmap.fr/">OpenStreetMap France</a>)'
        ),
        url_template="https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=20,
    ),
]
"""CyclOSM tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
