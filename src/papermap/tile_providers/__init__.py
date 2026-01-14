"""Tile provider configurations for various map providers.

This subpackage contains tile provider configurations organized by provider.
All tile providers are aggregated and exported through this module.

Example:
    >>> from papermap.tile_providers import KEY_TO_TILE_PROVIDER, TILE_PROVIDERS
    >>> osm = KEY_TO_TILE_PROVIDER["openstreetmap"]
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
    from papermap.tile_provider import TileProvider

# Aggregate all tile providers from provider modules
TILE_PROVIDERS: list[TileProvider] = [
    *openstreetmap.TILE_PROVIDERS,
    *opentopomap.TILE_PROVIDERS,
    *openseamap.TILE_PROVIDERS,
    *thunderforest.TILE_PROVIDERS,
    *esri.TILE_PROVIDERS,
    *stadia.TILE_PROVIDERS,
    *cartodb.TILE_PROVIDERS,
    *google.TILE_PROVIDERS,
    *here.TILE_PROVIDERS,
    *usgs.TILE_PROVIDERS,
    *nasagibs.TILE_PROVIDERS,
    *wikimedia.TILE_PROVIDERS,
    *cyclosm.TILE_PROVIDERS,
    *jawg.TILE_PROVIDERS,
    *maptiler.TILE_PROVIDERS,
    *tomtom.TILE_PROVIDERS,
    *basemap_at.TILE_PROVIDERS,
    *nlmaps.TILE_PROVIDERS,
    *swiss.TILE_PROVIDERS,
    *misc.TILE_PROVIDERS,
]
"""List of all available `TileProvider` instances."""

# Mapping from tile provider key to TileProvider instance
KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {
    **openstreetmap.KEY_TO_TILE_PROVIDER,
    **opentopomap.KEY_TO_TILE_PROVIDER,
    **openseamap.KEY_TO_TILE_PROVIDER,
    **thunderforest.KEY_TO_TILE_PROVIDER,
    **esri.KEY_TO_TILE_PROVIDER,
    **stadia.KEY_TO_TILE_PROVIDER,
    **cartodb.KEY_TO_TILE_PROVIDER,
    **google.KEY_TO_TILE_PROVIDER,
    **here.KEY_TO_TILE_PROVIDER,
    **usgs.KEY_TO_TILE_PROVIDER,
    **nasagibs.KEY_TO_TILE_PROVIDER,
    **wikimedia.KEY_TO_TILE_PROVIDER,
    **cyclosm.KEY_TO_TILE_PROVIDER,
    **jawg.KEY_TO_TILE_PROVIDER,
    **maptiler.KEY_TO_TILE_PROVIDER,
    **tomtom.KEY_TO_TILE_PROVIDER,
    **basemap_at.KEY_TO_TILE_PROVIDER,
    **nlmaps.KEY_TO_TILE_PROVIDER,
    **swiss.KEY_TO_TILE_PROVIDER,
    **misc.KEY_TO_TILE_PROVIDER,
}
"""Map of tile provider keys to `TileProvider` instances."""

TILE_PROVIDER_KEYS = sorted(KEY_TO_TILE_PROVIDER.keys())
"""List of tile provider keys."""

DEFAULT_TILE_PROVIDER_KEY: str = "openstreetmap"
"""Default tile provider key."""

__all__ = [
    "DEFAULT_TILE_PROVIDER_KEY",
    "KEY_TO_TILE_PROVIDER",
    "TILE_PROVIDERS",
    "TILE_PROVIDER_KEYS",
]
