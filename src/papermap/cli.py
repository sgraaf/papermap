from collections.abc import Callable
from functools import wraps
from importlib import metadata
from pathlib import Path
from typing import Any

import click
from click_default_group import DefaultGroup

from .geodesy import ECEFCoordinate, MGRSCoordinate, UTMCoordinate
from .papermap import (
    DEFAULT_DPI,
    DEFAULT_GRID_SIZE,
    DEFAULT_MARGIN,
    DEFAULT_PAPER_SIZE,
    DEFAULT_SCALE,
    PAPER_SIZES,
    PaperMap,
)
from .tile_providers import DEFAULT_TILE_PROVIDER_KEY, TILE_PROVIDER_KEYS

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


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
        "--tile-provider",
        "tile_provider_key",
        type=click.Choice(TILE_PROVIDER_KEYS),
        default=DEFAULT_TILE_PROVIDER_KEY,
        help="Tile provider to serve as the base of the paper map.",
    )
    @click.option(
        "--api-key",
        type=str,
        metavar="KEY",
        help="API key for the chosen tile provider (if applicable).",
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
    @click.option(
        "--strict",
        "strict_download",
        default=False,
        is_flag=True,
        help="Fail if any tiles cannot be downloaded.",
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
    """PaperMap is a Python library and CLI tool for creating ready-to-print paper maps.

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
    *,
    tile_provider_key: str = DEFAULT_TILE_PROVIDER_KEY,
    api_key: str | None = None,
    paper_size: str = DEFAULT_PAPER_SIZE,
    use_landscape: bool = False,
    margin_top: int = DEFAULT_MARGIN,
    margin_right: int = DEFAULT_MARGIN,
    margin_bottom: int = DEFAULT_MARGIN,
    margin_left: int = DEFAULT_MARGIN,
    scale: int = DEFAULT_SCALE,
    dpi: int = DEFAULT_DPI,
    add_grid: bool = False,
    grid_size: int = DEFAULT_GRID_SIZE,
    strict_download: bool = False,
) -> None:
    """Generates a paper map for the given geographic coordinates (i.e. lat, lon) and outputs it to file."""
    pm = PaperMap(
        lat,
        lon,
        tile_provider_key=tile_provider_key,
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
        strict_download=strict_download,
    )
    pm.render()
    pm.save(file)


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
    *,
    tile_provider_key: str = DEFAULT_TILE_PROVIDER_KEY,
    api_key: str | None = None,
    paper_size: str = DEFAULT_PAPER_SIZE,
    use_landscape: bool = False,
    margin_top: int = DEFAULT_MARGIN,
    margin_right: int = DEFAULT_MARGIN,
    margin_bottom: int = DEFAULT_MARGIN,
    margin_left: int = DEFAULT_MARGIN,
    scale: int = DEFAULT_SCALE,
    dpi: int = DEFAULT_DPI,
    add_grid: bool = False,
    grid_size: int = DEFAULT_GRID_SIZE,
    strict_download: bool = False,
) -> None:
    """Generates a paper map for the given UTM (Universal Transverse Mercator) coordinates and outputs it to file."""
    pm = PaperMap.from_utm(
        UTMCoordinate(easting, northing, zone, hemisphere),
        tile_provider_key=tile_provider_key,
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
        strict_download=strict_download,
    )
    pm.render()
    pm.save(file)


@cli.command()
@click.argument("zone", type=int, metavar="ZONE-NUMBER")
@click.argument("band", type=str, metavar="BAND")
@click.argument("square", type=str, metavar="SQUARE")
@click.argument("easting", type=float, metavar="EASTING")
@click.argument("northing", type=float, metavar="NORTHING")
@common_parameters
def mgrs(  # noqa: PLR0913
    zone: int,
    band: str,
    square: str,
    easting: float,
    northing: float,
    file: Path,
    *,
    tile_provider_key: str = DEFAULT_TILE_PROVIDER_KEY,
    api_key: str | None = None,
    paper_size: str = DEFAULT_PAPER_SIZE,
    use_landscape: bool = False,
    margin_top: int = DEFAULT_MARGIN,
    margin_right: int = DEFAULT_MARGIN,
    margin_bottom: int = DEFAULT_MARGIN,
    margin_left: int = DEFAULT_MARGIN,
    scale: int = DEFAULT_SCALE,
    dpi: int = DEFAULT_DPI,
    add_grid: bool = False,
    grid_size: int = DEFAULT_GRID_SIZE,
    strict_download: bool = False,
) -> None:
    """Generates a paper map for the given MGRS (Military Grid Reference System) coordinates and outputs it to file."""
    pm = PaperMap.from_mgrs(
        MGRSCoordinate(zone, band, square, easting, northing),
        tile_provider_key=tile_provider_key,
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
        strict_download=strict_download,
    )
    pm.render()
    pm.save(file)


@cli.command()
@click.argument("x", type=float, metavar="X")
@click.argument("y", type=float, metavar="Y")
@click.argument("z", type=float, metavar="Z")
@common_parameters
def ecef(  # noqa: PLR0913
    x: float,
    y: float,
    z: float,
    file: Path,
    *,
    tile_provider_key: str = DEFAULT_TILE_PROVIDER_KEY,
    api_key: str | None = None,
    paper_size: str = DEFAULT_PAPER_SIZE,
    use_landscape: bool = False,
    margin_top: int = DEFAULT_MARGIN,
    margin_right: int = DEFAULT_MARGIN,
    margin_bottom: int = DEFAULT_MARGIN,
    margin_left: int = DEFAULT_MARGIN,
    scale: int = DEFAULT_SCALE,
    dpi: int = DEFAULT_DPI,
    add_grid: bool = False,
    grid_size: int = DEFAULT_GRID_SIZE,
    strict_download: bool = False,
) -> None:
    """Generates a paper map for the given ECEF (Earth-Centered, Earth-Fixed) Cartesian coordinates and outputs it to file."""
    pm = PaperMap.from_ecef(
        ECEFCoordinate(x, y, z),
        tile_provider_key=tile_provider_key,
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
        strict_download=strict_download,
    )
    pm.render()
    pm.save(file)
