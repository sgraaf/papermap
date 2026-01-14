"""USGS (United States Geological Survey) tile server configurations.

USGS provides various map layers through the National Map,
including topographic maps and satellite imagery.

See: https://basemap.nationalmap.gov/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

USGS_ATTRIBUTION = "Tiles courtesy of the U.S. Geological Survey"
USGS_HTML_ATTRIBUTION = (
    'Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>'
)


def _usgs_server(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 20,
) -> TileServer:
    """Create a USGS tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=USGS_ATTRIBUTION,
        html_attribution=USGS_HTML_ATTRIBUTION,
        url_template=f"https://basemap.nationalmap.gov/arcgis/rest/services/{variant}/MapServer/tile/{{z}}/{{y}}/{{x}}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: dict[str, TileServer] = {
    "USGS USTopo": _usgs_server("usgs-ustopo", "USGS USTopo", "USGSTopo"),
    "USGS USImagery": _usgs_server("usgs-usimagery", "USGS USImagery", "USGSImageryOnly"),
    "USGS USImageryTopo": _usgs_server(
        "usgs-usimagerytopo", "USGS USImageryTopo", "USGSImageryTopo"
    ),
}
"""USGS tile servers."""
