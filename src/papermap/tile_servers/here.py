"""HERE Maps tile server configurations.

HERE provides high-quality map tiles including various base maps,
satellite imagery, and terrain data. Requires an API key.

See: https://developer.here.com/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

HERE_ATTRIBUTION = "Map data: © HERE"
HERE_HTML_ATTRIBUTION = 'Map data: © <a href="https://www.here.com/">HERE</a>'


def _here_server(
    key: str,
    name: str,
    scheme: str,
    base: str = "base",
    zoom_max: int = 20,
) -> TileServer:
    """Create a HERE Maps tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=HERE_ATTRIBUTION,
        html_attribution=HERE_HTML_ATTRIBUTION,
        url_template=f"https://{{s}}.{base}.maps.ls.hereapi.com/maptile/2.1/maptile/newest/{scheme}/{{z}}/{{x}}/{{y}}/256/png8?apiKey={{a}}",
        subdomains=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: dict[str, TileServer] = {
    "HERE normalDay": _here_server(
        "here-normalday", "HERE normalDay", "normal.day"
    ),
    "HERE normalDayCustom": _here_server(
        "here-normaldaycustom", "HERE normalDayCustom", "normal.day.custom"
    ),
    "HERE normalDayGrey": _here_server(
        "here-normaldaygrey", "HERE normalDayGrey", "normal.day.grey"
    ),
    "HERE normalDayMobile": _here_server(
        "here-normaldaymobile", "HERE normalDayMobile", "normal.day.mobile"
    ),
    "HERE normalDayGreyMobile": _here_server(
        "here-normaldaygreymobile", "HERE normalDayGreyMobile", "normal.day.grey.mobile"
    ),
    "HERE normalDayTransit": _here_server(
        "here-normaldaytransit", "HERE normalDayTransit", "normal.day.transit"
    ),
    "HERE normalDayTransitMobile": _here_server(
        "here-normaldaytransitmobile",
        "HERE normalDayTransitMobile",
        "normal.day.transit.mobile",
    ),
    "HERE normalNight": _here_server(
        "here-normalnight", "HERE normalNight", "normal.night"
    ),
    "HERE normalNightMobile": _here_server(
        "here-normalnightmobile", "HERE normalNightMobile", "normal.night.mobile"
    ),
    "HERE normalNightGrey": _here_server(
        "here-normalnightgrey", "HERE normalNightGrey", "normal.night.grey"
    ),
    "HERE normalNightGreyMobile": _here_server(
        "here-normalnightgreymobile",
        "HERE normalNightGreyMobile",
        "normal.night.grey.mobile",
    ),
    "HERE normalNightTransit": _here_server(
        "here-normalnighttransit", "HERE normalNightTransit", "normal.night.transit"
    ),
    "HERE normalNightTransitMobile": _here_server(
        "here-normalnighttransitmobile",
        "HERE normalNightTransitMobile",
        "normal.night.transit.mobile",
    ),
    "HERE reducedDay": _here_server(
        "here-reducedday", "HERE reducedDay", "reduced.day"
    ),
    "HERE reducedNight": _here_server(
        "here-reducednight", "HERE reducedNight", "reduced.night"
    ),
    "HERE basicMap": _here_server(
        "here-basicmap", "HERE basicMap", "normal.day", base="base"
    ),
    "HERE mapLabels": _here_server(
        "here-maplabels", "HERE mapLabels", "normal.day", base="base"
    ),
    "HERE trafficFlow": _here_server(
        "here-trafficflow", "HERE trafficFlow", "normal.day", base="traffic"
    ),
    "HERE carnavDayGrey": _here_server(
        "here-carnavdaygrey", "HERE carnavDayGrey", "carnav.day.grey"
    ),
    "HERE hybridDay": _here_server(
        "here-hybridday", "HERE hybridDay", "hybrid.day", base="aerial"
    ),
    "HERE hybridDayMobile": _here_server(
        "here-hybriddaymobile", "HERE hybridDayMobile", "hybrid.day.mobile", base="aerial"
    ),
    "HERE hybridDayTransit": _here_server(
        "here-hybriddaytransit",
        "HERE hybridDayTransit",
        "hybrid.day.transit",
        base="aerial",
    ),
    "HERE hybridDayGrey": _here_server(
        "here-hybriddaygrey", "HERE hybridDayGrey", "hybrid.grey.day", base="aerial"
    ),
    "HERE pedestrianDay": _here_server(
        "here-pedestrianday", "HERE pedestrianDay", "pedestrian.day"
    ),
    "HERE pedestrianNight": _here_server(
        "here-pedestriannight", "HERE pedestrianNight", "pedestrian.night"
    ),
    "HERE satelliteDay": _here_server(
        "here-satelliteday", "HERE satelliteDay", "satellite.day", base="aerial"
    ),
    "HERE terrainDay": _here_server(
        "here-terrainday", "HERE terrainDay", "terrain.day", base="aerial"
    ),
    "HERE terrainDayMobile": _here_server(
        "here-terraindaymobile",
        "HERE terrainDayMobile",
        "terrain.day.mobile",
        base="aerial",
    ),
}
"""HERE tile servers."""
