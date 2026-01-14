from collections.abc import Callable
from functools import wraps
from importlib import metadata
from pathlib import Path
from typing import Any

import click
from click_default_group import DefaultGroup

from .papermap import (
    DEFAULT_DPI,
    DEFAULT_GRID_SIZE,
    DEFAULT_MARGIN,
    DEFAULT_PAPER_SIZE,
    DEFAULT_SCALE,
    PAPER_SIZES,
    PaperMap,
)
from .tile_servers import DEFAULT_TILE_SERVER_KEY, TILE_SERVER_KEYS
from .utils import utm_to_spherical

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def _create_and_save_map(  # noqa: PLR0913
    lat: float,
    lon: float,
    file: Path,
    tile_server_key: str = DEFAULT_TILE_SERVER_KEY,
    api_key: str | None = None,
    paper_size: str = DEFAULT_PAPER_SIZE,
    use_landscape: bool = False,  # noqa: FBT001, FBT002
    margin_top: int = DEFAULT_MARGIN,
    margin_right: int = DEFAULT_MARGIN,
    margin_bottom: int = DEFAULT_MARGIN,
    margin_left: int = DEFAULT_MARGIN,
    scale: int = DEFAULT_SCALE,
    dpi: int = DEFAULT_DPI,
    add_grid: bool = False,  # noqa: FBT001, FBT002
    grid_size: int = DEFAULT_GRID_SIZE,
) -> None:
    """Shared map creation logic for all coordinate input methods."""
    # initialize PaperMap object
    pm = PaperMap(
        lat=lat,
        lon=lon,
        tile_server_key=tile_server_key,
        api_key=api_key,
        paper_size=paper_size,
        use_landscape=use_landscape,
        margin_top=margin_top,
        margin_right=margin_right,
        margin_bottom=margin_bottom,
        margin_left=margin_left,
        scale=scale,
        dpi=dpi,
        add_grid=add_grid,
        grid_size=grid_size,
    )

    # render it
    pm.render()

    # save it
    pm.save(file)


def margin_option(side: str) -> Callable:
    """Attaches a margin option for the given side to the command."""
    return click.option(
        f"--margin-{side}",
        type=int,
        default=DEFAULT_MARGIN,
        metavar="MILLIMETERS",
        help=f"{side.title()} margin.",
    )


def common_parameters(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to add common parameters (arguments and options) to a click command.

    Adapted from: https://github.com/pallets/click/issues/108#issuecomment-280489786
    """

    @click.argument("file", type=click.Path(dir_okay=False, path_type=Path))
    @click.option(
        "--tile-server",
        "tile_server_key",
        type=click.Choice(TILE_SERVER_KEYS),
        default=DEFAULT_TILE_SERVER_KEY,
        help="Tile server to serve as the base of the paper map.",
    )
    @click.option(
        "--api-key",
        type=str,
        metavar="KEY",
        help="API key for the chosen tile server (if applicable).",
    )
    @click.option(
        "--paper-size",
        type=click.Choice(PAPER_SIZES),
        default=DEFAULT_PAPER_SIZE,
        help="Size of the paper map.",
    )
    @click.option(
        "--landscape",
        "use_landscape",
        default=False,
        is_flag=True,
        help="Use landscape orientation.",
    )
    @margin_option("top")
    @margin_option("right")
    @margin_option("bottom")
    @margin_option("left")
    @click.option(
        "--scale",
        type=int,
        default=DEFAULT_SCALE,
        help="Scale of the paper map.",
    )
    @click.option(
        "--dpi",
        type=int,
        default=DEFAULT_DPI,
        help="Dots per inch.",
    )
    @click.option(
        "--grid",
        "add_grid",
        default=False,
        is_flag=True,
        help="Add a coordinate grid overlay to the paper map.",
    )
    @click.option(
        "--grid-size",
        type=int,
        default=DEFAULT_GRID_SIZE,
        metavar="METERS",
        help="Size of the grid squares (if applicable).",
    )
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper


@click.group(
    cls=DefaultGroup,
    default="latlon",
    default_if_no_args=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option(metadata.version("papermap"), "-v", "--version")
def cli() -> None:
    """PaperMap is a Python package and CLI for creating ready-to-print paper maps.

    Documentation: https://papermap.readthedocs.io/en/stable/
    """


@cli.command()
@click.argument("lat", type=float, metavar="LATITUDE")
@click.argument("lon", type=float, metavar="LONGITUDE")
@common_parameters
def latlon(  # noqa: PLR0913
    lat: float,
    lon: float,
    file: Path,
    tile_server_key: str = DEFAULT_TILE_SERVER_KEY,
    api_key: str | None = None,
    paper_size: str = DEFAULT_PAPER_SIZE,
    use_landscape: bool = False,  # noqa: FBT001, FBT002
    margin_top: int = DEFAULT_MARGIN,
    margin_right: int = DEFAULT_MARGIN,
    margin_bottom: int = DEFAULT_MARGIN,
    margin_left: int = DEFAULT_MARGIN,
    scale: int = DEFAULT_SCALE,
    dpi: int = DEFAULT_DPI,
    add_grid: bool = False,  # noqa: FBT001, FBT002
    grid_size: int = DEFAULT_GRID_SIZE,
) -> None:
    """Generates a paper map for the given spherical coordinate (i.e. lat, lon) and outputs it to file."""
    _create_and_save_map(
        lat,
        lon,
        file,
        tile_server_key=tile_server_key,
        api_key=api_key,
        paper_size=paper_size,
        use_landscape=use_landscape,
        margin_top=margin_top,
        margin_right=margin_right,
        margin_bottom=margin_bottom,
        margin_left=margin_left,
        scale=scale,
        dpi=dpi,
        add_grid=add_grid,
        grid_size=grid_size,
    )


@cli.command()
@click.argument("easting", type=float, metavar="EASTING")
@click.argument("northing", type=float, metavar="NORTHING")
@click.argument("zone", type=int, metavar="ZONE-NUMBER")
@click.argument("hemisphere", type=str, metavar="HEMISPHERE")
@common_parameters
def utm(  # noqa: PLR0913
    easting: float,
    northing: float,
    zone: int,
    hemisphere: str,
    file: Path,
    tile_server_key: str = DEFAULT_TILE_SERVER_KEY,
    api_key: str | None = None,
    paper_size: str = DEFAULT_PAPER_SIZE,
    use_landscape: bool = False,  # noqa: FBT001, FBT002
    margin_top: int = DEFAULT_MARGIN,
    margin_right: int = DEFAULT_MARGIN,
    margin_bottom: int = DEFAULT_MARGIN,
    margin_left: int = DEFAULT_MARGIN,
    scale: int = DEFAULT_SCALE,
    dpi: int = DEFAULT_DPI,
    add_grid: bool = False,  # noqa: FBT001, FBT002
    grid_size: int = DEFAULT_GRID_SIZE,
) -> None:
    """Generates a paper map for the given UTM coordinate and outputs it to file."""
    # convert UTM coordinate to spherical (i.e. lat, lon)
    lat, lon = utm_to_spherical(easting, northing, zone, hemisphere)
    _create_and_save_map(
        lat,
        lon,
        file,
        tile_server_key=tile_server_key,
        api_key=api_key,
        paper_size=paper_size,
        use_landscape=use_landscape,
        margin_top=margin_top,
        margin_right=margin_right,
        margin_bottom=margin_bottom,
        margin_left=margin_left,
        scale=scale,
        dpi=dpi,
        add_grid=add_grid,
        grid_size=grid_size,
    )
