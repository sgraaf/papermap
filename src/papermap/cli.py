from collections.abc import Callable
from functools import wraps
from importlib import metadata
from pathlib import Path
from typing import Any, TypedDict, Unpack

import click
from click_default_group import DefaultGroup

from .geodesy import ECEFCoordinate, MGRSCoordinate, UTMCoordinate
from .papermap import (
    DEFAULT_AUTO_SCALE_PADDING,
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


class CommonParameters(TypedDict):
    """Common parameters shared by every CLI sub-command.

    These mirror the keyword arguments installed by the
    `common_parameters` decorator and ultimately forwarded to the
    `PaperMap` constructor or one of its `from_*` classmethods.
    """

    tile_provider_key: str
    api_key: str | None
    paper_size: str
    use_landscape: bool
    margin_top: int
    margin_right: int
    margin_bottom: int
    margin_left: int
    scale: int
    dpi: int
    add_grid: bool
    grid_size: int
    strict_download: bool


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


def _render_and_save(pm: PaperMap, file: Path) -> None:
    """Render the map and write it to *file*."""
    pm.render()
    pm.save(file)


@click.group(
    cls=DefaultGroup,
    default="latlon",
    default_if_no_args=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option(metadata.version("papermap"), "-v", "--version")
def cli() -> None:
    """papermap is a Python library and CLI tool for creating ready-to-print paper maps.

    Documentation: https://papermap.readthedocs.io/en/stable/
    """  # noqa: D403


@cli.command()
@click.argument("lat", type=float, metavar="LATITUDE")
@click.argument("lon", type=float, metavar="LONGITUDE")
@common_parameters
def latlon(
    lat: float, lon: float, file: Path, **kwargs: Unpack[CommonParameters]
) -> None:
    """Generates a paper map for the given geographic coordinates (i.e. lat, lon) and outputs it to file."""
    _render_and_save(PaperMap(lat, lon, **kwargs), file)


@cli.command()
@click.argument("easting", type=float, metavar="EASTING")
@click.argument("northing", type=float, metavar="NORTHING")
@click.argument("zone", type=int, metavar="ZONE-NUMBER")
@click.argument("hemisphere", type=str, metavar="HEMISPHERE")
@common_parameters
def utm(
    easting: float,
    northing: float,
    zone: int,
    hemisphere: str,
    file: Path,
    **kwargs: Unpack[CommonParameters],
) -> None:
    """Generates a paper map for the given UTM (Universal Transverse Mercator) coordinates and outputs it to file."""
    _render_and_save(
        PaperMap.from_utm(UTMCoordinate(easting, northing, zone, hemisphere), **kwargs),
        file,
    )


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
    **kwargs: Unpack[CommonParameters],
) -> None:
    """Generates a paper map for the given MGRS (Military Grid Reference System) coordinates and outputs it to file."""
    _render_and_save(
        PaperMap.from_mgrs(
            MGRSCoordinate(zone, band, square, easting, northing), **kwargs
        ),
        file,
    )


@cli.command()
@click.argument("x", type=float, metavar="X")
@click.argument("y", type=float, metavar="Y")
@click.argument("z", type=float, metavar="Z")
@common_parameters
def ecef(
    x: float, y: float, z: float, file: Path, **kwargs: Unpack[CommonParameters]
) -> None:
    """Generates a paper map for the given ECEF (Earth-Centered, Earth-Fixed) Cartesian coordinates and outputs it to file."""
    _render_and_save(PaperMap.from_ecef(ECEFCoordinate(x, y, z), **kwargs), file)


@cli.command()
@click.argument(
    "geojson_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--auto-scale",
    "auto_scale",
    default=False,
    is_flag=True,
    help="Compute the scale automatically to fit the GeoJSON geometries.",
)
@click.option(
    "--padding",
    type=float,
    default=DEFAULT_AUTO_SCALE_PADDING,
    metavar="MILLIMETERS",
    help="Padding between the GeoJSON geometries and the image edge (per side). Only used with --auto-scale.",
)
@common_parameters
def geojson(
    geojson_file: Path,
    auto_scale: bool,  # noqa: FBT001
    padding: float,
    file: Path,
    **kwargs: Unpack[CommonParameters],
) -> None:
    """Generates a paper map for the given GeoJSON file and outputs it to file."""
    forwarded: dict[str, Any] = dict(**kwargs)
    if auto_scale:
        forwarded.pop("scale", None)
    _render_and_save(
        PaperMap.from_geojson(
            geojson_file, auto_scale=auto_scale, padding=padding, **forwarded
        ),
        file,
    )


@cli.command()
@click.argument(
    "gpx_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--auto-scale",
    "auto_scale",
    default=False,
    is_flag=True,
    help="Compute the scale automatically to fit the GPX geometries.",
)
@click.option(
    "--padding",
    type=float,
    default=DEFAULT_AUTO_SCALE_PADDING,
    metavar="MILLIMETERS",
    help="Padding between the GPX geometries and the image edge (per side). Only used with --auto-scale.",
)
@common_parameters
def gpx(
    gpx_file: Path,
    auto_scale: bool,  # noqa: FBT001
    padding: float,
    file: Path,
    **kwargs: Unpack[CommonParameters],
) -> None:
    """Generates a paper map for the given GPX file and outputs it to file.

    Requires the optional 'gpx' package; install with 'pip install papermap[gpx]'.
    """
    forwarded: dict[str, Any] = dict(**kwargs)
    if auto_scale:
        forwarded.pop("scale", None)
    _render_and_save(
        PaperMap.from_gpx(
            gpx_file, auto_scale=auto_scale, padding=padding, **forwarded
        ),
        file,
    )
