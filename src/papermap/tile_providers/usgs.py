"""USGS (United States Geological Survey) tile provider configurations.

USGS provides various map layers through the National Map,
including topographic maps and satellite imagery.

See: https://basemap.nationalmap.gov/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

USGS_ATTRIBUTION = "Tiles courtesy of the U.S. Geological Survey"
USGS_HTML_ATTRIBUTION = (
    'Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>'
)


def _usgs_provider(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 20,
) -> TileProvider:
    """Create a USGS tile provider configuration."""
    return TileProvider(
        key=key,
        name=name,
        attribution=USGS_ATTRIBUTION,
        html_attribution=USGS_HTML_ATTRIBUTION,
        url_template=f"https://basemap.nationalmap.gov/arcgis/rest/services/{variant}/MapProvider/tile/{{z}}/{{y}}/{{x}}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _usgs_provider("usgs-ustopo", "USGS USTopo", "USGSTopo"),
    _usgs_provider("usgs-usimagery", "USGS USImagery", "USGSImageryOnly"),
    _usgs_provider("usgs-usimagerytopo", "USGS USImageryTopo", "USGSImageryTopo"),
]
"""USGS tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
