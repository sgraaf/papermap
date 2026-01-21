from collections.abc import Iterator
from decimal import Decimal
from math import (
    atan,
    cos,
    log,
    log2,
    radians,
    sinh,
    tan,
)
from math import pi as π  # noqa: PLC2403
from string import Formatter

from .geodesy import wrap_lat, wrap_lon
from .tile import TILE_SIZE

C: int = 40_075_017
"""Earth's equatorial circumference in meters."""

DEFAULT_DPI: int = 300
"""Default dots per inch."""


def clip(val: float, lower: float, upper: float) -> float:
    """Clips a value to [lower, upper] range.

    Args:
        val: The value.
        lower: The lower bound.
        upper: The upper bound.

    Returns:
        The value clipped to [lower, upper] range.
    """
    return min(max(val, lower), upper)


def lon_to_x(lon: float, zoom: int) -> float:
    """Converts longitude to x (tile coordinate), given a zoom level.

    Args:
        lon: The longitude.
        zoom: The zoom level.

    Returns:
        The x (tile coordinate).
    """
    # constrain lon to [-180, 180] range
    lon = wrap_lon(lon)

    # convert lon to [0, 1] range
    return ((lon + 180.0) / 360) * 2**zoom


def x_to_lon(x: float, zoom: int) -> float:
    """Converts x (tile coordinate) to longitude, given a zoom level.

    Args:
        x: The tile coordinate.
        zoom: The zoom level.

    Returns:
        The longitude.
    """
    return x / (2**zoom) * 360 - 180


def lat_to_y(lat: float, zoom: int) -> float:
    """Converts latitude to y (tile coordinate), given a zoom level.

    Args:
        lat: The latitude.
        zoom: The zoom level.

    Returns:
        The y (tile coordinate).
    """
    # constrain lat to [-90, 90] range
    lat = wrap_lat(lat)

    # convert lat to radians
    φ = radians(lat)

    # convert lat to [0, 1] range
    return ((1 - log(tan(φ) + 1 / cos(φ)) / π) / 2) * 2**zoom


def y_to_lat(y: float, zoom: int) -> float:
    """Converts y (tile coordinate) to latitude, given a zoom level.

    Args:
        y: The tile coordinate.
        zoom: The zoom level.

    Returns:
        The latitude.
    """
    return atan(sinh(π * (1 - 2 * y / (2**zoom)))) / π * 180


def x_to_px(x: int, x_center: int, width: int, tile_size: int = TILE_SIZE) -> int:
    """Convert x (tile coordinate) to pixels.

    Args:
        x: The tile coordinate.
        x_center: Tile coordinate of the center tile.
        width: The image width.
        tile_size: The tile size. Defaults to `256`.

    Returns:
        The pixels.
    """
    return round(width / 2 - (x_center - x) * tile_size)


def y_to_px(y: int, y_center: int, height: int, tile_size: int = TILE_SIZE) -> int:
    """Convert y (tile coordinate) to pixel.

    Args:
        y: The tile coordinate.
        y_center: Tile coordinate of the center tile.
        height: The image height.
        tile_size: The tile size. Defaults to `256`.

    Returns:
        The pixels.
    """
    return round(height / 2 - (y_center - y) * tile_size)


def mm_to_px(mm: float, dpi: int = DEFAULT_DPI) -> int:
    """Convert millimeters to pixels, given the dpi.

    Args:
        mm: The millimeters.
        dpi: Dots per inch. Defaults to `300`.

    Returns:
        The pixels.
    """
    return round(mm * dpi / 25.4)


def px_to_mm(px: int, dpi: int = DEFAULT_DPI) -> float:
    """Convert pixels to millimeters, given the dpi.

    Args:
        px: The pixels.
        dpi: Dots per inch. Defaults to `300`.

    Returns:
        The millimeters.
    """
    return px * 25.4 / dpi


def mm_to_pt(mm: float) -> float:
    """Convert millimeters to points.

    Args:
        mm: The millimeters.

    Returns:
        The points.
    """
    return mm * 72 / 25.4


def pt_to_mm(pt: float) -> float:
    """Convert points to millimeters.

    Args:
        pt: The points.

    Returns:
        The millimeters.
    """
    return pt * 25.4 / 72


def dd_to_dms(dd: float) -> tuple[int, int, float]:
    """Convert Decimal Degrees (DD) to Degrees, Minutes, and Seconds (DMS).

    Args:
        dd: The Decimal Degrees.

    Returns:
        The Degrees, Minutes, and Seconds.
    """
    is_positive = dd >= 0
    dd = abs(dd)
    m, s = divmod(dd * 3600, 60)
    d, m = divmod(m, 60)
    d = d if is_positive else -d
    return round(d), round(m), round(s, 6)


def dms_to_dd(dms: tuple[int, int, float]) -> float:
    """Convert Degrees, Minutes, and Seconds (DMS) to Decimal Degrees (DD).

    Args:
        dms: The Degrees, Minutes, and Seconds.

    Returns:
        The Decimal Degrees.
    """
    d, m, s = dms
    is_positive = d >= 0
    d = d if is_positive else -d
    return round((d + m / 60 + s / 3600) * (1 if is_positive else -1), 6)


def scale_to_zoom(scale: int, lat: float, dpi: int = DEFAULT_DPI) -> float:
    """Compute the zoom level, given the latitude, scale and dpi.

    Args:
        scale: The scale.
        lat: The latitude.
        dpi: Dots per inch. Defaults to `300`.

    Returns:
        The zoom level.
    """
    # convert lat to radians
    φ = radians(lat)

    # compute the zoom level
    scale_px = scale * 25.4 / (1000 * dpi)
    return log2(C * cos(φ) / scale_px) - 8


def zoom_to_scale(zoom: int, lat: float, dpi: int = DEFAULT_DPI) -> float:
    """Compute the scale, given the latitude, zoom level and dpi.

    Args:
        zoom: The zoom level.
        lat: The latitude.
        dpi: Dots per inch. Defaults to `300`.

    Returns:
        The scale.
    """
    # convert lat to radians
    φ = radians(lat)

    # compute the scale
    scale_px = C * cos(φ) / 2 ** (zoom + 8)
    return scale_px * dpi * 1000 / 25.4


def get_string_formatting_arguments(s: str) -> list[str]:
    """Extracts field names from a format string.

    Args:
        s: A format string (e.g., "{name} is {age}").

    Returns:
        List of field names found in the format string.
    """
    return [t[1] for t in Formatter().parse(s) if t[1] is not None]


def is_out_of_bounds(test: dict[str, float], bounds: dict[str, float]) -> bool:
    """Checks if a bounding box exceeds the specified bounds.

    Args:
        test: Bounding box with keys 'lat_min', 'lat_max', 'lon_min', 'lon_max'.
        bounds: Reference bounds with the same keys.

    Returns:
        True if test exceeds bounds in any direction, False otherwise.
    """
    return bool(
        test["lat_min"] < bounds["lat_min"]
        or test["lon_min"] < bounds["lon_min"]
        or test["lat_max"] > bounds["lat_max"]
        or test["lon_max"] > bounds["lon_max"]
    )


def drange(start: Decimal, stop: Decimal, step: Decimal) -> Iterator[Decimal]:
    """Yields `Decimal` values from *start* to *stop* with the given *step* size.

    Args:
        start: The first value to yield.
        stop: The upper bound (exclusive).
        step: The increment applied on each iteration.

    Yields:
        Decimal values in the range *[start, stop)* incremented by *step*.
    """
    while start < stop:
        yield start
        start += step
