"""CartoDB (Carto) tile server configurations.

Carto provides beautiful, high-performance basemaps including
Positron (light), Dark Matter (dark), and Voyager styles.

See: https://carto.com/basemaps/
"""

from __future__ import annotations

from papermap.tile_server import TileServer

CARTO_ATTRIBUTION = "© OpenStreetMap contributors, © CARTO"
CARTO_HTML_ATTRIBUTION = (
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>, '
    '© <a href="https://carto.com/attributions">CARTO</a>'
)


def _carto_server(
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 20,
) -> TileServer:
    """Create a CartoDB tile server configuration."""
    return TileServer(
        key=key,
        name=name,
        attribution=CARTO_ATTRIBUTION,
        html_attribution=CARTO_HTML_ATTRIBUTION,
        url_template=f"https://{{s}}.basemaps.cartocdn.com/{variant}/{{z}}/{{x}}/{{y}}.png",
        subdomains=["a", "b", "c", "d"],
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_SERVERS: list[TileServer] = [
    _carto_server("cartodb-positron", "CartoDB Positron", "light_all"),
    _carto_server(
        "cartodb-positronnolabels", "CartoDB PositronNoLabels", "light_nolabels"
    ),
    _carto_server(
        "cartodb-positrononlylabels", "CartoDB PositronOnlyLabels", "light_only_labels"
    ),
    _carto_server("cartodb-darkmatter", "CartoDB DarkMatter", "dark_all"),
    _carto_server(
        "cartodb-darkmatter-nolabels",
        "CartoDB DarkMatterNoLabels",
        "dark_nolabels",
    ),
    _carto_server(
        "cartodb-darkmatter-onlylabels",
        "CartoDB DarkMatterOnlyLabels",
        "dark_only_labels",
    ),
    _carto_server("cartodb-voyager", "CartoDB Voyager", "rastertiles/voyager"),
    _carto_server(
        "cartodb-voyager-nolabels",
        "CartoDB VoyagerNoLabels",
        "rastertiles/voyager_nolabels",
    ),
    _carto_server(
        "cartodb-voyager-onlylabels",
        "CartoDB VoyagerOnlyLabels",
        "rastertiles/voyager_only_labels",
    ),
    _carto_server(
        "cartodb-voyager-labelsunder",
        "CartoDB VoyagerLabelsUnder",
        "rastertiles/voyager_labels_under",
    ),
]
"""CartoDB tile servers."""

KEY_TO_TILE_SERVER: dict[str, TileServer] = {ts.key: ts for ts in TILE_SERVERS}
"""Mapping from tile server key to TileServer instance."""
