"""Miscellaneous tile provider configurations.

This module contains tile providers that don't fit into other categories
or are standalone providers without multiple variants.
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

OSM_ATTRIBUTION = "© OpenStreetMap contributors"
OSM_HTML_ATTRIBUTION = (
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
)

TILE_PROVIDERS: list[TileProvider] = [
    TileProvider(
        key="opnvkarte",
        name="OPNVKarte",
        attribution="Map data: © OpenStreetMap contributors. Map style: © ÖPNVKarte",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Map style: © <a href="https://www.opnvkarte.de/">ÖPNVKarte</a>'
        ),
        url_template="https://tileprovider.memomaps.de/tilegen/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileProvider(
        key="mtbmap",
        name="MtbMap",
        attribution="Map data: © OpenStreetMap contributors, USGS. Map style: © mtbmap.cz",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION} & USGS. "
            'Map style: © <a href="https://mtbmap.cz/">mtbmap.cz</a>'
        ),
        url_template="http://tile.mtbmap.cz/mtbmap_tiles/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileProvider(
        key="hikebike",
        name="HikeBike",
        attribution=f"Map data: {OSM_ATTRIBUTION}",
        html_attribution=f"Map data: {OSM_HTML_ATTRIBUTION}",
        url_template="https://tiles.wmflabs.org/hikebike/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=19,
    ),
    TileProvider(
        key="safecast",
        name="SafeCast",
        attribution="Map data: © OpenStreetMap contributors. Map style: © SafeCast",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Map style: © <a href="https://safecast.org/">SafeCast</a>'
        ),
        url_template="https://s3.amazonaws.com/te512.safecast.org/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=16,
    ),
    TileProvider(
        key="geofabrik-topo",
        name="Geofabrik Topo",
        attribution=f"Map data: {OSM_ATTRIBUTION}",
        html_attribution=f"Map data: {OSM_HTML_ATTRIBUTION}",
        url_template="http://{s}.tile.geofabrik.de/15173cf79060ee4a66573954f6017ab0/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    TileProvider(
        key="mapy-cz",
        name="Mapy.cz",
        attribution="Map data: © OpenStreetMap contributors. Map style: © Seznam.cz",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Map style: © <a href="https://www.seznam.cz/">Seznam.cz</a>'
        ),
        url_template="https://m{s}.mapprovider.mapy.cz/turist-m/{z}-{x}-{y}.png",
        subdomains=[1, 2, 3, 4],
        zoom_min=0,
        zoom_max=19,
    ),
    TileProvider(
        key="komoot",
        name="Komoot",
        attribution=f"Map data: {OSM_ATTRIBUTION}",
        html_attribution=f"Map data: {OSM_HTML_ATTRIBUTION}",
        url_template="http://{s}.tile.komoot.de/komoot-2/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    TileProvider(
        key="alltrails",
        name="AllTrails",
        attribution=f"Map data: {OSM_ATTRIBUTION}",
        html_attribution=f"Map data: {OSM_HTML_ATTRIBUTION}",
        url_template="https://alltrails.com/tiles/alltrailsOutdoors/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=20,
    ),
    TileProvider(
        key="waymarkedtrails-hiking",
        name="Waymarked Trails Hiking",
        attribution="Map data: © OpenStreetMap contributors. Overlay: © Waymarked Trails",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Overlay: © <a href="https://hiking.waymarkedtrails.org/">Waymarked Trails</a>'
        ),
        url_template="https://tile.waymarkedtrails.org/hiking/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileProvider(
        key="waymarkedtrails-cycling",
        name="Waymarked Trails Cycling",
        attribution="Map data: © OpenStreetMap contributors. Overlay: © Waymarked Trails",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Overlay: © <a href="https://cycling.waymarkedtrails.org/">Waymarked Trails</a>'
        ),
        url_template="https://tile.waymarkedtrails.org/cycling/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileProvider(
        key="waymarkedtrails-mtb",
        name="Waymarked Trails MTB",
        attribution="Map data: © OpenStreetMap contributors. Overlay: © Waymarked Trails",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Overlay: © <a href="https://mtb.waymarkedtrails.org/">Waymarked Trails</a>'
        ),
        url_template="https://tile.waymarkedtrails.org/mtb/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileProvider(
        key="waymarkedtrails-slopes",
        name="Waymarked Trails Slopes",
        attribution="Map data: © OpenStreetMap contributors. Overlay: © Waymarked Trails",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Overlay: © <a href="https://slopes.waymarkedtrails.org/">Waymarked Trails</a>'
        ),
        url_template="https://tile.waymarkedtrails.org/slopes/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileProvider(
        key="waymarkedtrails-riding",
        name="Waymarked Trails Riding",
        attribution="Map data: © OpenStreetMap contributors. Overlay: © Waymarked Trails",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Overlay: © <a href="https://riding.waymarkedtrails.org/">Waymarked Trails</a>'
        ),
        url_template="https://tile.waymarkedtrails.org/riding/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileProvider(
        key="waymarkedtrails-skating",
        name="Waymarked Trails Skating",
        attribution="Map data: © OpenStreetMap contributors. Overlay: © Waymarked Trails",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Overlay: © <a href="https://skating.waymarkedtrails.org/">Waymarked Trails</a>'
        ),
        url_template="https://tile.waymarkedtrails.org/skating/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileProvider(
        key="openaip",
        name="OpenAIP",
        attribution="© OpenAIP",
        html_attribution='© <a href="https://www.openaip.net/">OpenAIP</a>',
        url_template="https://api.tiles.openaip.net/api/data/openaip/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=4,
        zoom_max=14,
    ),
    TileProvider(
        key="opensnowmap",
        name="OpenSnowMap",
        attribution="Map data: © OpenStreetMap contributors. Overlay: © OpenSnowMap",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Overlay: © <a href="https://www.opensnowmap.org/">OpenSnowMap</a>'
        ),
        url_template="https://tiles.opensnowmap.org/pistes/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=18,
    ),
    TileProvider(
        key="openrailwaymap",
        name="OpenRailwayMap",
        attribution="Map data: © OpenStreetMap contributors. Map style: © OpenRailwayMap (CC-BY-SA)",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Map style: © <a href="https://www.openrailwaymap.org/">OpenRailwayMap</a> '
            '(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
        ),
        url_template="https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png",
        subdomains=["a", "b", "c"],
        zoom_min=0,
        zoom_max=19,
    ),
    TileProvider(
        key="openfiremap",
        name="OpenFireMap",
        attribution="Map data: © OpenStreetMap contributors. Map style: © OpenFireMap (CC-BY-SA)",
        html_attribution=(
            f"Map data: {OSM_HTML_ATTRIBUTION}. "
            'Map style: © <a href="http://www.openfiremap.org/">OpenFireMap</a> '
            '(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
        ),
        url_template="http://openfiremap.org/hytiles/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=19,
    ),
]
"""Miscellaneous tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
