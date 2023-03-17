from decimal import Decimal
from math import (
    asinh,
    atan,
    atan2,
    atanh,
    cos,
    cosh,
    degrees,
    hypot,
    log,
    radians,
    sin,
    sinh,
    sqrt,
    tan,
)
from math import pi as π
from string import Formatter
from typing import Dict, Iterator, List, Union

from .constants import FALSE_EASTING, FALSE_NORTHING, TILE_SIZE, WGS84_ELLIPSOID, C, R
from .defaults import DEFAULT_DPI
from .typing import (
    DMS,
    Angle,
    Cartesian_3D,
    Degree,
    Pixel,
    Spherical_2D,
    UTM_Coordinate,
)


def clip(val: float, lower: float, upper: float) -> float:
    """Clips a value to [lower, upper] range.

    Args:
        val: The value.
        lower: The lower bound.
        upper: The upper bound.

    Returns:
        The value clipped to [lower, upper] range.

    Raises:
        ValueError: If lower > upper.
    """
    if lower > upper:
        raise ValueError(
            f"Lower bound must be less than or equal to upper bound: {lower} > {upper}"
        )
    return min(max(val, lower), upper)


def wrap(angle: Angle, limit: Angle) -> Angle:
    """Wraps an angle to [-limit, limit] range.

    Args:
        angle: The angle.
        limit: The lower and upper limit.

    Returns:
        The angle wrapped to [-limit, limit] range.
    """
    if -limit <= angle <= limit:  # angle already in [-limit, limit] range
        return angle
    return (angle + limit) % (2 * limit) - limit


def wrap90(angle: Degree) -> Degree:
    """Wraps an angle to [-90, 90] range.

    Args:
        angle: The angle.

    Returns:
        The angle wrapped to [-90, 90] range.
    """
    return wrap(angle, 90)


def wrap180(angle: Degree) -> Degree:
    """Wraps an angle to [-180, 180] range

    Args:
        angle: The angle.

    Returns:
        The angle wrapped to [-180, 180] range.
    """
    return wrap(angle, 180)


def wrap360(angle: Degree) -> Degree:
    """Wraps an angle to [0, 360) range

    Args:
        angle: The angle.

    Returns:
        The angle wrapped to [0, 360) range.
    """
    if 0 <= angle < 360:  # angle already in [0, 360) range
        return angle
    return angle % 360


def lon_to_x(lon: Degree, zoom: int) -> float:
    """Converts longitude to x (tile coordinate), given a zoom level.

    Args:
        lon: The longitude.
        zoom: The zoom level.

    Returns:
        The x (tile coordinate).
    """
    # constrain lon to [-180, 180] range
    lon = wrap180(lon)

    # convert lon to [0, 1] range
    x = ((lon + 180.0) / 360) * 2**zoom

    return x


def x_to_lon(x: Union[int, float], zoom: int) -> Degree:
    """Converts x (tile coordinate) to longitude, given a zoom level.

    Args:
        x: The tile coordinate.
        zoom: The zoom level.

    Returns:
        The longitude.
    """
    lon = x / (2**zoom) * 360 - 180
    return lon


def lat_to_y(lat: Degree, zoom: int) -> float:
    """Converts latitude to y (tile coordinate), given a zoom level.

    Args:
        lat: The latitude.
        zoom: The zoom level.

    Returns:
        The y (tile coordinate).
    """
    # constrain lat to [-90, 90] range
    lat = wrap90(lat)

    # convert lat to radians
    φ = radians(lat)

    # convert lat to [0, 1] range
    y = ((1 - log(tan(φ) + 1 / cos(φ)) / π) / 2) * 2**zoom

    return y


def y_to_lat(y: Union[int, float], zoom: int) -> Degree:
    """Converts y (tile coordinate) to latitude, given a zoom level.

    Args:
        y: The tile coordinate.
        zoom: The zoom level.

    Returns:
        The latitude.
    """
    lat = atan(sinh(π * (1 - 2 * y / (2**zoom)))) / π * 180
    return lat


def x_to_px(x: int, x_center: int, width: Pixel, tile_size: Pixel = TILE_SIZE) -> Pixel:
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


def y_to_px(
    y: int, y_center: int, height: Pixel, tile_size: Pixel = TILE_SIZE
) -> Pixel:
    """Convert y (tile coordinate) to pixel

    Args:
        y: The tile coordinate.
        y_center: Tile coordinate of the center tile.
        height: The image height.
        tile_size: The tile size. Defaults to `256`.

    Returns:
        The pixels.
    """
    return round(height / 2 - (y_center - y) * tile_size)


def mm_to_px(mm: float, dpi: int = DEFAULT_DPI) -> Pixel:
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


def dd_to_dms(dd: Degree) -> DMS:
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


def dms_to_dd(dms: DMS) -> Degree:
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


def spherical_to_cartesian(lat: Degree, lon: Degree, r: float = R) -> Cartesian_3D:
    """Convert spherical coordinates (i.e. lat, lon) to cartesian coordinates (i.e. x, y, z).

    Adapted from: `<https://github.com/chrisveness/geodesy>`_

    Args:
        lat: The latitude.
        lon: The longitude.
        r: The radius of the sphere. Defaults to `6378137`
        (equatorial Earth radius).

    Returns:
        The cartesian coordinates (x, y, z).
    """
    # convert lat and lon (in deg) to radians
    φ = radians(lat)
    λ = radians(lon)

    x = r * cos(φ) * cos(λ)
    y = r * cos(φ) * sin(λ)
    z = r * sin(φ)

    return x, y, z


def cartesian_to_spherical(x: float, y: float, z: float) -> Spherical_2D:
    """Convert cartesian coordinates (i.e. x, y, z) to spherical coordinates (i.e. lat, lon).

    Adapted from: `<https://github.com/chrisveness/geodesy>`_

    Args:
        x: The x coordinate.
        y: The y coordinate.
        z: The z coordinate.

    Returns:
        The spherical coordinates (i.e. lat, lon).
    """
    # compute the spherical coordinates in radians
    φ = atan2(z, hypot(x, y))
    λ = atan2(y, x)

    # convert radians to degrees
    lat = degrees(φ)
    lon = degrees(λ)

    return lat, lon


def scale_to_zoom(scale: int, lat: Degree, dpi: int = DEFAULT_DPI) -> float:
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
    zoom = log(C * cos(φ) / scale_px, 2) - 8
    return zoom


def zoom_to_scale(zoom: int, lat: Degree, dpi: int = DEFAULT_DPI) -> float:
    """Compute the scale, given the latitude, zoom level and dpi

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
    scale = scale_px * dpi * 1000 / 25.4
    return scale


def spherical_to_zone(lat: Degree, lon: Degree) -> int:
    """Compute the UTM zone number of a given spherical coordinate (i.e. lat, lon).

    Args:
        lat: The latitude.
        lon: The longitude.

    Returns:
        The UTM zone number.
    """
    if 56 <= lat < 64 and 3 <= lon < 12:
        return 32

    if 72 <= lat <= 84 and lon >= 0:
        if lon < 9:
            return 31
        elif lon < 21:
            return 33
        elif lon < 33:
            return 35
        elif lon < 42:
            return 37

    return int((lon + 180) / 6) + 1


def compute_central_lon(zone: int) -> Degree:
    """Compute the central longitude of a given UTM zone number.

    Args:
        zone: The UTM zone number.

    Returns:
        The central longitude.
    """
    return (zone - 1) * 6 - 180 + 3


def spherical_to_utm(lat: Degree, lon: Degree) -> UTM_Coordinate:
    """Convert a spherical coordinate (i.e. lat, lon) to a UTM coordinate.

    Based on formulas from (Karney, 2011).

    Adapted from: `<https://github.com/chrisveness/geodesy/blob/master/utm.js>`_

    Args:
        lat: The latitude.
        lon: The longitude.

    References:
        `Karney, C. F. (2011). Transverse Mercator with an accuracy of a few nanometers. Journal of Geodesy, 85(8), 475-485. <https://arxiv.org/abs/1002.1417v3>`_
    """
    # constrain lat to [-90.0, 90.0] range, lon to [-180.0, 180.0] range
    lat = wrap90(lat)
    lon = wrap180(lon)

    # ensure lat is not out of range for conversion
    if not -80.0 <= lat <= 84.0:
        raise ValueError(
            f"Latitude out of range [-80.0, 84.0] for UTM conversion: {lat}"
        )

    # get the zone number and letter
    zone = spherical_to_zone(lat, lon)

    # compute the lon of the central meridian
    λ0 = radians(compute_central_lon(zone))

    # convert lat and lon to radians
    φ = radians(lat)
    λ = radians(lon) - λ0

    # compute some quantities used throughout the equations below
    a, f = WGS84_ELLIPSOID
    e = sqrt(f * (2 - f))  # eccentricity
    n = f / (2 - f)  # third flattening
    n2 = n**2
    n3 = n**3
    n4 = n**4
    n5 = n**5
    n6 = n**6
    k0 = 0.9996  # scale factor on central meridian
    λ_cos = cos(λ)
    λ_sin = sin(λ)

    # (Karney, 2011, Eqs. (7-9))
    τ = tan(φ)
    σ = sinh(e * atanh(e * τ / sqrt(1 + τ**2)))
    τʹ = τ * sqrt(1 + σ**2) - σ * sqrt(1 + τ**2)

    # (Karney, 2011, Eq. (10))
    ξʹ = atan2(τʹ, λ_cos)
    ηʹ = asinh(λ_sin / sqrt(τʹ**2 + λ_cos**2))

    # (Karney, 2011, Eq. (35))
    α = [
        1,
        n / 2
        - 2 * n2 / 3
        + 5 * n3 / 16
        + 41 * n4 / 180
        - 127 * n5 / 288
        + 7891 * n6 / 37800,
        13 * n2 / 48
        - 3 * n3 / 5
        + 557 * n4 / 1440
        + 281 * n5 / 630
        - 1983433 * n6 / 1935360,
        61 * n3 / 240 - 103 * n4 / 140 + 15061 * n5 / 26880 + 167603 * n6 / 181440,
        49561 * n4 / 161280 - 179 * n5 / 168 + 6601661 * n6 / 7257600,
        34729 * n5 / 80640 - 3418889 * n6 / 1995840,
        212378941 * n6 / 319334400,
    ]

    # (Karney, 2011, Eq. (11))
    ξ = ξʹ
    for j in range(1, 7):
        ξ += α[j] * sin(2 * j * ξʹ) * cosh(2 * j * ηʹ)
    η = ηʹ
    for j in range(1, 7):
        η += α[j] * cos(2 * j * ξʹ) * sinh(2 * j * ηʹ)

    # 2πA is the circumference of a meridian
    # (Karney, 2011, Eq. (14))
    A = a / (1 + n) * (1 + n2 / 4 + n4 / 64 + n6 / 256)

    # compute the x (easting) and y (northing)
    # (Karney, 2011, Eq. (13))
    x = k0 * A * η
    y = k0 * A * ξ

    # shift easting and northing to false origins
    x += FALSE_EASTING
    if y < 0:
        y += FALSE_NORTHING

    # get the hemisphere
    hemisphere = "N" if lat >= 0 else "S"

    return x, y, zone, hemisphere


def utm_to_spherical(x: float, y: float, zone: int, hemisphere: str) -> Spherical_2D:
    """Convert a UTM coordinate to a spherical coordinate (i.e. lat, lon).

    Based on formulas from (Karney, 2011).

    Adapted from: `<https://github.com/chrisveness/geodesy/blob/master/utm.js>`_

    Args:
        x: The easting.
        y: The northing.
        z: The zone number.
        l: The hemisphere.

    References:
        `Karney, C. F. (2011). Transverse Mercator with an accuracy of a few nanometers. Journal of Geodesy, 85(8), 475-485. <https://arxiv.org/abs/1002.1417v3>`_
    """
    # shift easting and northing from false origins
    x -= FALSE_EASTING
    if hemisphere == "S":
        y -= FALSE_NORTHING

    # compute some quantities used throughout the equations below
    a, f = WGS84_ELLIPSOID
    e = sqrt(f * (2 - f))  # eccentricity
    n = f / (2 - f)  # third flattening
    n2 = n**2
    n3 = n**3
    n4 = n**4
    n5 = n**5
    n6 = n**6
    k0 = 0.9996  # scale factor on central meridian

    # 2πA is the circumference of a meridian
    # (Karney, 2011, Eq. (14))
    A = a / (1 + n) * (1 + n2 / 4 + n4 / 64 + n6 / 256)

    # (Karney, 2011, Eq. (15))
    ξ = y / (k0 * A)
    η = x / (k0 * A)

    # (Karney, 2011, Eq. (36))
    β = [
        1,
        n / 2
        - 2 * n2 / 3
        + 37 * n3 / 96
        - n4 / 360
        - 81 * n5 / 512
        + 96199 * n6 / 604800,
        n2 / 48 + n3 / 15 - 437 * n4 / 1440 + 46 * n5 / 105 - 1118711 * n6 / 3870720,
        17 * n3 / 480 - 37 * n4 / 840 - 209 * n5 / 4480 + 5569 * n6 / 90720,
        4397 * n4 / 161280 - 11 * n5 / 504 - 830251 * n6 / 7257600,
        4583 * n5 / 161280 - 108847 * n6 / 3991680,
        20648693 * n6 / 638668800,
    ]

    # (Karney, 2011, Eq. (11))
    ξʹ = ξ
    for j in range(1, 7):
        ξʹ -= β[j] * sin(2 * j * ξ) * cosh(2 * j * η)
    ηʹ = η
    for j in range(1, 7):
        ηʹ -= β[j] * cos(2 * j * ξ) * sinh(2 * j * η)

    ηʹ_sinh = sinh(ηʹ)
    ξʹ_cos = cos(ξʹ)

    # (Karney, 2011, Eq. (18))
    τʹ = sin(ξʹ) / sqrt(ηʹ_sinh**2 + ξʹ_cos**2)
    λ = atan2(ηʹ_sinh, ξʹ_cos)

    # (Karney, 2011, Eqs. (19-21))
    δτi = 1.0
    τi = τʹ
    while abs(δτi) > 1e-12:
        σi = sinh(e * atanh(e * τi / sqrt(1 + τi**2)))
        τiʹ = τi * sqrt(1 + σi**2) - σi * sqrt(1 + τi**2)
        δτi = (
            (τʹ - τiʹ)
            / sqrt(1 + τiʹ**2)
            * (1 + (1 - e**2) * τi**2)
            / ((1 - e**2) * sqrt(1 + τi**2))
        )
        τi += δτi
    τ = τi

    # (Karney, 2011, Eq. (22))
    φ = atan(τ)

    # convert to degrees
    lat = degrees(φ)
    lon = degrees(λ)

    return lat, lon


def get_string_formatting_arguments(s: str) -> List[str]:
    return [t[1] for t in Formatter().parse(s) if t[1] is not None]


def is_out_of_bounds(test: Dict[str, float], bounds: Dict[str, float]) -> bool:
    if test["lat_min"] < bounds["lat_min"]:
        return True
    elif test["lon_min"] < bounds["lon_min"]:
        return True
    elif test["lat_max"] > bounds["lat_max"]:
        return True
    elif test["lon_max"] > bounds["lat_max"]:
        return True
    return False


def drange(start: Decimal, stop: Decimal, step: Decimal) -> Iterator[Decimal]:
    while start < stop:
        yield start
        start += step
