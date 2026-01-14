"""Legacy tile server aliases for backward compatibility.

This module provides aliases for tile servers that were renamed
in the transition to the new provider-based architecture.

These aliases are deprecated and may be removed in a future release.
"""

from __future__ import annotations

from papermap.tile_server import TileServer

from .esri import TILE_SERVERS as ESRI_TILE_SERVERS
from .google import TILE_SERVERS as GOOGLE_TILE_SERVERS
from .here import TILE_SERVERS as HERE_TILE_SERVERS
from .misc import TILE_SERVERS as MISC_TILE_SERVERS
from .openstreetmap import TILE_SERVERS as OSM_TILE_SERVERS
from .stadia import TILE_SERVERS as STADIA_TILE_SERVERS
from .thunderforest import TILE_SERVERS as TF_TILE_SERVERS

# Legacy aliases mapping old names to new TileServer objects
# These are provided for backward compatibility only
TILE_SERVERS: dict[str, TileServer] = {
    # OpenStreetMap legacy aliases
    "OpenStreetMap Monochrome": TileServer(
        key="openstreetmap-monochrome",
        name="OpenStreetMap Monochrome",
        attribution="Map data: © OpenStreetMap contributors",
        html_attribution='Map data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
        url_template="https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png",
        subdomains=None,
        zoom_min=0,
        zoom_max=19,
    ),
    # ESRI legacy aliases (ESRI -> Esri naming)
    "ESRI Standard": ESRI_TILE_SERVERS["Esri WorldStreetMap"],
    "ESRI Satellite": ESRI_TILE_SERVERS["Esri WorldImagery"],
    "ESRI Topo": ESRI_TILE_SERVERS["Esri WorldTopoMap"],
    "ESRI Dark Gray": ESRI_TILE_SERVERS["Esri WorldGrayCanvas"],
    "ESRI Light Gray": ESRI_TILE_SERVERS["Esri WorldGrayCanvas"],
    "ESRI Transportation": TileServer(
        key="esri-transportation",
        name="ESRI Transportation",
        attribution="Tiles © Esri",
        html_attribution='Tiles © <a href="https://www.esri.com/">Esri</a>',
        url_template="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}",
        subdomains=None,
        zoom_min=0,
        zoom_max=20,
    ),
    # HERE legacy aliases
    "HERE Terrain": HERE_TILE_SERVERS["HERE terrainDay"],
    "HERE Satellite": HERE_TILE_SERVERS["HERE satelliteDay"],
    "HERE Hybrid": HERE_TILE_SERVERS["HERE hybridDay"],
    # Stamen legacy aliases (now hosted by Stadia)
    "Stamen Terrain": STADIA_TILE_SERVERS["Stadia StamenTerrain"],
    "Stamen Toner": STADIA_TILE_SERVERS["Stadia StamenToner"],
    "Stamen Toner Lite": STADIA_TILE_SERVERS["Stadia StamenTonerLite"],
    # Hike & Bike legacy alias
    "Hike & Bike": MISC_TILE_SERVERS["HikeBike"],
}
"""Legacy tile server aliases for backward compatibility."""
