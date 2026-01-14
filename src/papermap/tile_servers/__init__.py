"""Tile server configurations for various map providers.

This package contains tile server configurations organized by provider.
All tile servers are aggregated and exported through this module.

Example:
    >>> from papermap.tile_servers import KEY_TO_TILE_SERVER, TILE_SERVERS
    >>> osm = KEY_TO_TILE_SERVER["openstreetmap"]
    >>> print(osm.name)
    OpenStreetMap

Available providers:
    - OpenStreetMap (and regional variants)
    - OpenTopoMap
    - OpenSeaMap
    - Thunderforest (requires API key)
    - Esri
    - Stadia (including Stamen styles)
    - CartoDB (Carto)
    - Google Maps
    - HERE (requires API key)
    - USGS
    - NASA GIBS
    - Wikimedia
    - CyclOSM
    - Jawg (requires API key)
    - MapTiler (requires API key)
    - TomTom (requires API key)
    - BasemapAT (Austrian)
    - NLMaps (Dutch)
    - SwissFederalGeoportal
    - And many more miscellaneous providers
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import (
    basemap_at,
    cartodb,
    cyclosm,
    esri,
    google,
    here,
    jawg,
    maptiler,
    misc,
    nasagibs,
    nlmaps,
    openseamap,
    openstreetmap,
    opentopomap,
    stadia,
    swiss,
    thunderforest,
    tomtom,
    usgs,
    wikimedia,
)

if TYPE_CHECKING:
    from papermap.tile_server import TileServer

# Aggregate all tile servers from provider modules
TILE_SERVERS: list[TileServer] = [
    *openstreetmap.TILE_SERVERS,
    *opentopomap.TILE_SERVERS,
    *openseamap.TILE_SERVERS,
    *thunderforest.TILE_SERVERS,
    *esri.TILE_SERVERS,
    *stadia.TILE_SERVERS,
    *cartodb.TILE_SERVERS,
    *google.TILE_SERVERS,
    *here.TILE_SERVERS,
    *usgs.TILE_SERVERS,
    *nasagibs.TILE_SERVERS,
    *wikimedia.TILE_SERVERS,
    *cyclosm.TILE_SERVERS,
    *jawg.TILE_SERVERS,
    *maptiler.TILE_SERVERS,
    *tomtom.TILE_SERVERS,
    *basemap_at.TILE_SERVERS,
    *nlmaps.TILE_SERVERS,
    *swiss.TILE_SERVERS,
    *misc.TILE_SERVERS,
]
"""List of all available `TileServer` instances."""

# Mapping from tile server key to TileServer instance
KEY_TO_TILE_SERVER: dict[str, TileServer] = {
    **openstreetmap.KEY_TO_TILE_SERVER,
    **opentopomap.KEY_TO_TILE_SERVER,
    **openseamap.KEY_TO_TILE_SERVER,
    **thunderforest.KEY_TO_TILE_SERVER,
    **esri.KEY_TO_TILE_SERVER,
    **stadia.KEY_TO_TILE_SERVER,
    **cartodb.KEY_TO_TILE_SERVER,
    **google.KEY_TO_TILE_SERVER,
    **here.KEY_TO_TILE_SERVER,
    **usgs.KEY_TO_TILE_SERVER,
    **nasagibs.KEY_TO_TILE_SERVER,
    **wikimedia.KEY_TO_TILE_SERVER,
    **cyclosm.KEY_TO_TILE_SERVER,
    **jawg.KEY_TO_TILE_SERVER,
    **maptiler.KEY_TO_TILE_SERVER,
    **tomtom.KEY_TO_TILE_SERVER,
    **basemap_at.KEY_TO_TILE_SERVER,
    **nlmaps.KEY_TO_TILE_SERVER,
    **swiss.KEY_TO_TILE_SERVER,
    **misc.KEY_TO_TILE_SERVER,
}
"""Map of tile server keys to `TileServer` instances."""

DEFAULT_TILE_SERVER: str = "openstreetmap"
"""Default tile server key."""

__all__ = [
    "DEFAULT_TILE_SERVER",
    "KEY_TO_TILE_SERVER",
    "TILE_SERVERS",
]
