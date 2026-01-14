"""Tile server configurations for various map providers.

This package contains tile server configurations organized by provider.
All tile servers are aggregated and exported through this module.

Example:
    >>> from papermap.tile_servers import TILE_SERVERS_MAP, TILE_SERVERS
    >>> osm = TILE_SERVERS_MAP["OpenStreetMap"]
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

from papermap.tile_server import TileServer

from . import (
    basemap_at,
    cartodb,
    cyclosm,
    esri,
    google,
    here,
    jawg,
    legacy,
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

# Aggregate all tile servers from provider modules
TILE_SERVERS_MAP: dict[str, TileServer] = {
    **openstreetmap.TILE_SERVERS,
    **opentopomap.TILE_SERVERS,
    **openseamap.TILE_SERVERS,
    **thunderforest.TILE_SERVERS,
    **esri.TILE_SERVERS,
    **stadia.TILE_SERVERS,
    **cartodb.TILE_SERVERS,
    **google.TILE_SERVERS,
    **here.TILE_SERVERS,
    **usgs.TILE_SERVERS,
    **nasagibs.TILE_SERVERS,
    **wikimedia.TILE_SERVERS,
    **cyclosm.TILE_SERVERS,
    **jawg.TILE_SERVERS,
    **maptiler.TILE_SERVERS,
    **tomtom.TILE_SERVERS,
    **basemap_at.TILE_SERVERS,
    **nlmaps.TILE_SERVERS,
    **swiss.TILE_SERVERS,
    **misc.TILE_SERVERS,
    # Legacy aliases for backward compatibility (added last to not override new names)
    **legacy.TILE_SERVERS,
}
"""Map of tile server names to `TileServer` instances."""

TILE_SERVERS: tuple[str, ...] = tuple(TILE_SERVERS_MAP.keys())
"""Tuple of available tile server names."""

DEFAULT_TILE_SERVER: str = "OpenStreetMap"
"""Default tile server name."""

__all__ = [
    "DEFAULT_TILE_SERVER",
    "TILE_SERVERS",
    "TILE_SERVERS_MAP",
]
