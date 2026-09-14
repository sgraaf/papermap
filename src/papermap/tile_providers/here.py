"""HERE Maps tile provider configurations.

HERE provides high-quality map tiles including various base maps,
satellite imagery, and terrain data. Requires an API key.

The tile providers use the HERE Raster Tile API v3. The styles of the tile
providers that originate from the retired HERE Map Tile API v2 follow the
official migration guide.

See: https://docs.here.com/map-rendering/docs/migration-guide-raster-tile-api
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

HERE_ATTRIBUTION = "Map data: © HERE"
HERE_HTML_ATTRIBUTION = 'Map data: © <a href="https://www.here.com/">HERE</a>'


def _here_provider(  # noqa: PLR0913
    key: str,
    name: str,
    style: str,
    *,
    resource: str = "base",
    ext: str = "png8",
    public_transit: bool = False,
    large_labels: bool = False,
) -> TileProvider:
    """Create a HERE Raster Tile API v3 tile provider configuration.

    Args:
        key: The key of the tile provider.
        name: The name of the tile provider.
        style: The style of the map tiles (e.g. `explore.day`).
        resource: The type of map tiles (`base`, `background` or `label`).
        ext: The image format of the map tiles.
        public_transit: Show public transit (formerly the `*.transit` schemes).
        large_labels: Show large labels and icons (formerly the `*.mobile` schemes).
    """
    query = f"style={style}"
    if public_transit:
        query += "&features=public_transit:all_systems"
    if large_labels:
        query += "&ppi=400"
    return TileProvider(
        key=key,
        name=name,
        attribution=HERE_ATTRIBUTION,
        html_attribution=HERE_HTML_ATTRIBUTION,
        url_template=f"https://maps.hereapi.com/v3/{resource}/mc/{{z}}/{{x}}/{{y}}/{ext}?{query}&apiKey={{a}}",
        subdomains=None,
        zoom_min=0,
        zoom_max=20,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _here_provider("here-normalday", "HERE normalDay", "explore.day"),
    _here_provider("here-normaldaygrey", "HERE normalDayGrey", "lite.day"),
    _here_provider(
        "here-normaldaymobile", "HERE normalDayMobile", "explore.day", large_labels=True
    ),
    _here_provider(
        "here-normaldaygreymobile",
        "HERE normalDayGreyMobile",
        "lite.day",
        large_labels=True,
    ),
    _here_provider(
        "here-normaldaytransit",
        "HERE normalDayTransit",
        "explore.day",
        public_transit=True,
    ),
    _here_provider(
        "here-normaldaytransitmobile",
        "HERE normalDayTransitMobile",
        "explore.day",
        public_transit=True,
        large_labels=True,
    ),
    _here_provider("here-normalnight", "HERE normalNight", "explore.night"),
    _here_provider(
        "here-normalnightmobile",
        "HERE normalNightMobile",
        "explore.night",
        large_labels=True,
    ),
    _here_provider("here-normalnightgrey", "HERE normalNightGrey", "lite.night"),
    _here_provider(
        "here-normalnightgreymobile",
        "HERE normalNightGreyMobile",
        "lite.night",
        large_labels=True,
    ),
    _here_provider(
        "here-normalnighttransit",
        "HERE normalNightTransit",
        "explore.night",
        public_transit=True,
    ),
    _here_provider(
        "here-normalnighttransitmobile",
        "HERE normalNightTransitMobile",
        "explore.night",
        public_transit=True,
        large_labels=True,
    ),
    _here_provider(
        "here-basicmap", "HERE basicMap", "explore.day", resource="background"
    ),
    _here_provider(
        "here-maplabels", "HERE mapLabels", "explore.day", resource="label", ext="png"
    ),
    TileProvider(
        key="here-trafficflow",
        name="HERE trafficFlow",
        attribution=HERE_ATTRIBUTION,
        html_attribution=HERE_HTML_ATTRIBUTION,
        url_template="https://traffic.maps.hereapi.com/v3/flow/mc/{z}/{x}/{y}/png?apiKey={a}",
        subdomains=None,
        zoom_min=0,
        zoom_max=20,
    ),
    _here_provider(
        "here-hybridday", "HERE hybridDay", "explore.satellite.day", ext="jpeg"
    ),
    _here_provider(
        "here-hybriddaymobile",
        "HERE hybridDayMobile",
        "explore.satellite.day",
        ext="jpeg",
        large_labels=True,
    ),
    _here_provider(
        "here-hybriddaytransit",
        "HERE hybridDayTransit",
        "explore.satellite.day",
        ext="jpeg",
        public_transit=True,
    ),
    _here_provider(
        "here-hybriddaygrey", "HERE hybridDayGrey", "lite.satellite.day", ext="jpeg"
    ),
    _here_provider("here-pedestrianday", "HERE pedestrianDay", "explore.day"),
    _here_provider("here-pedestriannight", "HERE pedestrianNight", "explore.night"),
    _here_provider(
        "here-satelliteday", "HERE satelliteDay", "satellite.day", ext="jpeg"
    ),
    _here_provider("here-terrainday", "HERE terrainDay", "topo.day"),
    _here_provider(
        "here-terraindaymobile", "HERE terrainDayMobile", "topo.day", large_labels=True
    ),
    # Styles that were introduced in the HERE Raster Tile API v3
    _here_provider("here-toponight", "HERE topoNight", "topo.night"),
    _here_provider("here-logisticsday", "HERE logisticsDay", "logistics.day"),
    _here_provider("here-logisticsnight", "HERE logisticsNight", "logistics.night"),
    _here_provider(
        "here-logisticssatelliteday",
        "HERE logisticsSatelliteDay",
        "logistics.satellite.day",
        ext="jpeg",
    ),
]
"""HERE tile providers."""
