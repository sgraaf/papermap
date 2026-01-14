"""HERE Maps tile provider configurations.

HERE provides high-quality map tiles including various base maps,
satellite imagery, and terrain data. Requires an API key.

See: https://developer.here.com/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

HERE_ATTRIBUTION = "Map data: © HERE"
HERE_HTML_ATTRIBUTION = 'Map data: © <a href="https://www.here.com/">HERE</a>'


def _here_provider(
    key: str,
    name: str,
    scheme: str,
    base: str = "base",
    zoom_max: int = 20,
) -> TileProvider:
    """Create a HERE Maps tile provider configuration."""
    return TileProvider(
        key=key,
        name=name,
        attribution=HERE_ATTRIBUTION,
        html_attribution=HERE_HTML_ATTRIBUTION,
        url_template=f"https://{{s}}.{base}.maps.ls.hereapi.com/maptile/2.1/maptile/newest/{scheme}/{{z}}/{{x}}/{{y}}/256/png8?apiKey={{a}}",
        subdomains=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _here_provider("here-normalday", "HERE normalDay", "normal.day"),
    _here_provider("here-normaldaycustom", "HERE normalDayCustom", "normal.day.custom"),
    _here_provider("here-normaldaygrey", "HERE normalDayGrey", "normal.day.grey"),
    _here_provider("here-normaldaymobile", "HERE normalDayMobile", "normal.day.mobile"),
    _here_provider(
        "here-normaldaygreymobile", "HERE normalDayGreyMobile", "normal.day.grey.mobile"
    ),
    _here_provider(
        "here-normaldaytransit", "HERE normalDayTransit", "normal.day.transit"
    ),
    _here_provider(
        "here-normaldaytransitmobile",
        "HERE normalDayTransitMobile",
        "normal.day.transit.mobile",
    ),
    _here_provider("here-normalnight", "HERE normalNight", "normal.night"),
    _here_provider(
        "here-normalnightmobile", "HERE normalNightMobile", "normal.night.mobile"
    ),
    _here_provider("here-normalnightgrey", "HERE normalNightGrey", "normal.night.grey"),
    _here_provider(
        "here-normalnightgreymobile",
        "HERE normalNightGreyMobile",
        "normal.night.grey.mobile",
    ),
    _here_provider(
        "here-normalnighttransit", "HERE normalNightTransit", "normal.night.transit"
    ),
    _here_provider(
        "here-normalnighttransitmobile",
        "HERE normalNightTransitMobile",
        "normal.night.transit.mobile",
    ),
    _here_provider("here-reducedday", "HERE reducedDay", "reduced.day"),
    _here_provider("here-reducednight", "HERE reducedNight", "reduced.night"),
    _here_provider("here-basicmap", "HERE basicMap", "normal.day", base="base"),
    _here_provider("here-maplabels", "HERE mapLabels", "normal.day", base="base"),
    _here_provider(
        "here-trafficflow", "HERE trafficFlow", "normal.day", base="traffic"
    ),
    _here_provider("here-carnavdaygrey", "HERE carnavDayGrey", "carnav.day.grey"),
    _here_provider("here-hybridday", "HERE hybridDay", "hybrid.day", base="aerial"),
    _here_provider(
        "here-hybriddaymobile",
        "HERE hybridDayMobile",
        "hybrid.day.mobile",
        base="aerial",
    ),
    _here_provider(
        "here-hybriddaytransit",
        "HERE hybridDayTransit",
        "hybrid.day.transit",
        base="aerial",
    ),
    _here_provider(
        "here-hybriddaygrey", "HERE hybridDayGrey", "hybrid.grey.day", base="aerial"
    ),
    _here_provider("here-pedestrianday", "HERE pedestrianDay", "pedestrian.day"),
    _here_provider("here-pedestriannight", "HERE pedestrianNight", "pedestrian.night"),
    _here_provider(
        "here-satelliteday", "HERE satelliteDay", "satellite.day", base="aerial"
    ),
    _here_provider("here-terrainday", "HERE terrainDay", "terrain.day", base="aerial"),
    _here_provider(
        "here-terraindaymobile",
        "HERE terrainDayMobile",
        "terrain.day.mobile",
        base="aerial",
    ),
]
"""HERE tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
