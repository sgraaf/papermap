"""Esri (ArcGIS) tile server configurations.

Esri provides a wide variety of basemaps through their ArcGIS Online service,
including street maps, satellite imagery, topographic maps, and more.

See: https://www.esri.com/en-us/arcgis/products/arcgis-online/overview
"""

from __future__ import annotations

from papermap.tile_server import TileServer

ESRI_ATTRIBUTION = "Tiles © Esri"
ESRI_HTML_ATTRIBUTION = 'Tiles © <a href="https://www.esri.com/">Esri</a>'


def _esri_server(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 18,
    extra_attribution: str = "",
) -> TileServer:
    """Create an Esri tile server configuration."""
    attribution = f"{ESRI_ATTRIBUTION}{extra_attribution}"
    html_attribution = f"{ESRI_HTML_ATTRIBUTION}{extra_attribution}"
    return TileServer(
        key=key,
        name=name,
        attribution=attribution,
        html_attribution=html_attribution,
        url_template=f"https://server.arcgisonline.com/ArcGIS/rest/services/{variant}/MapServer/tile/{{z}}/{{y}}/{{x}}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: dict[str, TileServer] = {
    "Esri WorldStreetMap": _esri_server(
        "esri-worldstreetmap",
        "Esri WorldStreetMap",
        "World_Street_Map",
        zoom_max=17,
    ),
    "Esri DeLorme": _esri_server(
        "esri-delorme",
        "Esri DeLorme",
        "Specialty/DeLorme_World_Base_Map",
        zoom_max=11,
        extra_attribution=" — DeLorme",
    ),
    "Esri WorldTopoMap": _esri_server(
        "esri-worldtopomap",
        "Esri WorldTopoMap",
        "World_Topo_Map",
        zoom_max=19,
    ),
    "Esri WorldImagery": _esri_server(
        "esri-worldimagery",
        "Esri WorldImagery",
        "World_Imagery",
        zoom_max=19,
        extra_attribution=" — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
    ),
    "Esri WorldTerrain": _esri_server(
        "esri-worldterrain",
        "Esri WorldTerrain",
        "World_Terrain_Base",
        zoom_max=13,
        extra_attribution=" — Source: USGS, Esri, TANA, DeLorme, and NPS",
    ),
    "Esri WorldShadedRelief": _esri_server(
        "esri-worldshadedrelief",
        "Esri WorldShadedRelief",
        "World_Shaded_Relief",
        zoom_max=13,
        extra_attribution=" — Source: Esri",
    ),
    "Esri WorldPhysical": _esri_server(
        "esri-worldphysical",
        "Esri WorldPhysical",
        "World_Physical_Map",
        zoom_max=8,
        extra_attribution=" — Source: US National Park Service",
    ),
    "Esri OceanBasemap": _esri_server(
        "esri-oceanbasemap",
        "Esri OceanBasemap",
        "Ocean/World_Ocean_Base",
        zoom_max=13,
        extra_attribution=" — Source: Esri, GEBCO, NOAA, National Geographic, DeLorme, HERE, Geonames.org, and other contributors",
    ),
    "Esri NatGeoWorldMap": _esri_server(
        "esri-natgeoworldmap",
        "Esri NatGeoWorldMap",
        "NatGeo_World_Map",
        zoom_max=16,
        extra_attribution=" — Source: National Geographic, Esri, DeLorme, HERE, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, increment P Corp.",
    ),
    "Esri WorldGrayCanvas": _esri_server(
        "esri-worldgraycanvas",
        "Esri WorldGrayCanvas",
        "Canvas/World_Light_Gray_Base",
        zoom_max=16,
    ),
}
"""Esri tile servers."""
