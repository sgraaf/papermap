"""CartoDB (Carto) tile provider configurations.

Carto provides beautiful, high-performance basemaps including
Positron (light), Dark Matter (dark), and Voyager styles.

See: https://carto.com/basemaps/
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

CARTO_ATTRIBUTION = "© OpenStreetMap contributors, © CARTO"
CARTO_HTML_ATTRIBUTION = (
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>, '
    '© <a href="https://carto.com/attributions">CARTO</a>'
)


def _carto_provider(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 20,
) -> TileProvider:
    """Create a CartoDB tile provider configuration."""
    return TileProvider(
        key=key,
        name=name,
        attribution=CARTO_ATTRIBUTION,
        html_attribution=CARTO_HTML_ATTRIBUTION,
        url_template=f"https://{{s}}.basemaps.cartocdn.com/{variant}/{{z}}/{{x}}/{{y}}.png",
        subdomains=["a", "b", "c", "d"],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _carto_provider("cartodb-positron", "CartoDB Positron", "light_all"),
    _carto_provider(
        "cartodb-positronnolabels", "CartoDB PositronNoLabels", "light_nolabels"
    ),
    _carto_provider(
        "cartodb-positrononlylabels", "CartoDB PositronOnlyLabels", "light_only_labels"
    ),
    _carto_provider("cartodb-darkmatter", "CartoDB DarkMatter", "dark_all"),
    _carto_provider(
        "cartodb-darkmatter-nolabels",
        "CartoDB DarkMatterNoLabels",
        "dark_nolabels",
    ),
    _carto_provider(
        "cartodb-darkmatter-onlylabels",
        "CartoDB DarkMatterOnlyLabels",
        "dark_only_labels",
    ),
    _carto_provider("cartodb-voyager", "CartoDB Voyager", "rastertiles/voyager"),
    _carto_provider(
        "cartodb-voyager-nolabels",
        "CartoDB VoyagerNoLabels",
        "rastertiles/voyager_nolabels",
    ),
    _carto_provider(
        "cartodb-voyager-onlylabels",
        "CartoDB VoyagerOnlyLabels",
        "rastertiles/voyager_only_labels",
    ),
    _carto_provider(
        "cartodb-voyager-labelsunder",
        "CartoDB VoyagerLabelsUnder",
        "rastertiles/voyager_labels_under",
    ),
]
"""CartoDB tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
