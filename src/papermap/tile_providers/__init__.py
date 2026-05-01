"""Tile provider configurations for various map providers.

This subpackage contains tile provider configurations organized by provider.
All tile providers are aggregated and exported through this module.

Each provider module is expected to expose a module-level
``TILE_PROVIDERS: list[TileProvider]`` attribute. Modules are discovered
automatically; adding a new module under ``papermap/tile_providers/`` is
sufficient to register its providers here.

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

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from papermap.tile_provider import TileProvider


def _discover_tile_providers() -> list[TileProvider]:
    """Import every public submodule and collect their ``TILE_PROVIDERS`` lists."""
    providers: list[TileProvider] = []
    for module_info in pkgutil.iter_modules(__path__):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        providers.extend(getattr(module, "TILE_PROVIDERS", []))
    return providers


TILE_PROVIDERS: list[TileProvider] = _discover_tile_providers()
"""List of all available `TileProvider` instances."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {tp.key: tp for tp in TILE_PROVIDERS}
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
