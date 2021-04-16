#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from math import (acos, asin, atan, atan2, cos, degrees, hypot, isclose, log,
                  radians, sin, sinh, sqrt, tan)
from string import Formatter
from typing import Dict, Tuple

from PIL import Image, ImageColor

from .constants import E_, K0, LAT0, LON0, X0, Y0, C, E, R, π


def clip(val: float, lower: float, upper: float) -> float:
    """
    Clips a value to [lower, upper] range.

    Args:
        val (float): value
        lower (float): lower bound
        upper (float): upper bound

    Returns:
        The value clipped to [lower, upper] range.
    """
    return min(max(val, lower), upper)


def wrap(angle: float, limit: float) -> float:
    """
    Wraps an angle (either in dd or rad) to [-limit, limit] range.

    Args:
        angle (float): angle (in dd/rad)
        limit (float): limit (in dd/rad)

    Returns:
        The angle wrapped to [-limit, limit] range.
    """
    if -limit <= angle <= limit:  # angle already in [-limit, limit] range
        return angle
    # angle %= limit
    return (angle + limit) % (2 * limit) - limit


def wrap90(angle: float) -> float:
    """
    Wraps an angle to [-90, 90] range

    Args:
        angle (float): angle (in dd)

    Returns:
        The angle wrapped to [-90, 90] range.
    """
    return wrap(angle, 90)


def wrap180(angle: float) -> float:
    """
    Wraps an angle to [-180, 180] range

    Args:
        angle (float): angle (in dd)

    Returns:
        The angle wrapped to [-180, 180] range.
    """
    return wrap(angle, 180)


def wrap360(angle: float) -> float:
    """
    Wraps an angle to [0, 360) range

    Args:
        angle (float): angle (in dd)

    Returns:
        The angle wrapped to [0, 360) range.
    """
    if 0 <= angle < 360:  # angle already in [0, 360) range
        return angle
    return angle % 360


def lon_to_x(lon: float, zoom: int) -> float:
    """
    Converts longitude to x (tile number) given zoom level

    Args:
        lon (float): longitude (in dd)
        zoom (int): zoom level
    """
    # constrain lon to [-180, 180] range
    lon = wrap180(lon)

    # convert lon to [0, 1] range
    x = ((lon + 180.0) / 360) * 2**zoom

    return x


def x_to_lon(x: float, zoom: int) -> float:
    """
    Converts x (tile number) to longitude given zoom level

    Args:
        x (float / int): tile number
        zoom (int): zoom level
    """
    lon = x / (2**zoom) * 360 - 180
    return lon


def lat_to_y(lat: float, zoom: int) -> float:
    """
    Converts latitude to y (tile number) given zoom

    Args:
        lat (float): latitude (in dd)
        zoom (int): zoom level
    """
    # constrain lat to [-90, 90] range
    lat = wrap90(lat)

    # convert lat to radians
    φ = radians(lat)

    # convert lat to [0, 1] range
    y = ((1 - log(tan(φ) + 1 / cos(φ)) / π) / 2) * 2**zoom

    return y


def y_to_lat(y: float, zoom: int) -> float:
    """
    Converts y (tile number) to latitude given zoom level

    Args:
        y (float / int): tile number
        zoom (int): zoom level
    """
    lat = atan(sinh(π * (1 - 2 * y / (2**zoom)))) / π * 180
    return lat


def x_to_px(x: int, x_center: int, width: int, tile_size: int = 256) -> int:
    """
    Convert x (tile number) to pixel

    Args:
        x (int): tile number
        x_center (int): tile number of center tile
        width (int): image width in pixels
        tile_size (int): tile size in pixels
    """
    return round(width / 2 - (x_center - x) * tile_size)


def y_to_px(y: int, y_center: int, height: int, tile_size: int = 256) -> int:
    """
    Convert y (tile number) to pixel

    Args:
        y (int): tile number
        y_center (int): tile number of center tile
        height (int): image height in pixels
        tile_size (int): tile size in pixels
    """
    return round(height / 2 - (y_center - y) * tile_size)


def mm_to_px(mm: float, dpi: int = 300) -> int:
    """
    Convert millimeters to pixels, given the dpi

    Args:
        mm (float): quantity in millimeters
        dpi (int): dots per inch. Default: 300
    """
    return round(mm * dpi / 25.4)


def px_to_mm(px: int, dpi: int = 300) -> float:
    """
    Convert pixels to millimeters, given the dpi

    Args:
        px (int): quantity in pixels
        dpi (int): dots per inch. Default: 300
    """
    return px * 25.4 / dpi


def dd_to_dms(dd: float) -> Tuple[int, int, float]:
    """
    Convert a quantity in dd to dms

    Args:
        dd (float): quantity to be converted to dms
    """
    is_positive = dd >= 0
    dd = abs(dd)
    m, s = divmod(dd * 3600, 60)
    d, m = divmod(m, 60)
    d = d if is_positive else -d
    return round(d), round(m), round(s, 6)


def dms_to_dd(dms: Tuple[int, int, float]) -> float:
    """
    Convert a quantity in dms to dd

    Args:
        dms (tuple): quantity to be converted to dd
    """
    d, m, s = dms
    is_positive = d >= 0
    d = d if is_positive else -d
    return round((d + m / 60 + s / 3600) * (1 if is_positive else -1), 6)


def spherical_to_cartesian(lat: float, lon: float, r: float = R) -> Tuple[float, float, float]:
    """
    Convert spherical coordinates (i.e. point; lat, lon) to cartesian coordinates (x, y, z)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat (float): the latitude (in dd)
        lon (float): the longitude (in dd)
        r (float): the radius of the sphere. Default: 6378137 (equatorial Earth radius)

    Returns:
        The cartesian coordinates (x, y, z).
    """
    # convert lat and lon (in dd) to radians
    φ = radians(lat)
    λ = radians(lon)

    x = r * cos(φ) * cos(λ)
    y = r * cos(φ) * sin(λ)
    z = r * sin(φ)

    return x, y, z


def cartesian_to_spherical(x: float, y: float, z: float) -> Tuple[float, float]:
    """
    Convert cartesian coordinates (x, y, z) to spherical coordinates (i.e. point; lat, lon)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        x (float): x
        y (float): y
        z (float): z

    Returns:
        The spherical coordinates (i.e. point; lat, lon).
    """
    # compute the spherical coordinates in radians
    φ = atan2(z, hypot(x, y))
    λ = atan2(y, x)

    # convert radians to degrees
    lat = degrees(φ)
    lon = degrees(λ)

    return lat, lon


def scale_to_zoom(scale: int, lat: float, dpi: int = 300) -> float:
    """
    Compute the zoom level, given the latitude, scale and dpi

    Args:
        scale (int): the scale (in cm)
        lat (float): latitude (in dd)
        dpi (int): dots per inch. Default: 300
    """
    # convert lat to radians
    φ = radians(lat)

    # compute the zoom level
    scale_px = scale * 25.4 / (1000 * dpi)
    zoom = log(C * cos(φ) / scale_px, 2) - 8
    return zoom


def zoom_to_scale(zoom: int, lat: float, dpi: int = 300) -> float:
    """
    Compute the scale, given the latitude, zoom level and dpi

    Args:
        zoom (int): the zoom level
        lat (float): latitude (in dd)
        dpi (int): dots per inch. Default: 300
    """
    # convert lat to radians
    φ = radians(lat)

    # compute the scale
    scale_px = C * cos(φ) / 2**(zoom + 8)
    scale = scale_px * dpi * 1000 / 25.4
    return scale


def wgs84_to_rd(lat: float, lon: float) -> Tuple[float, float]:
    """
    Convert a WGS84 point to an RD coordinate
    Based on formulas from (Schreutelkamp & Van hees, 2001)
    Adapted from: https://github.com/djvanderlaan/rijksdriehoek/blob/master/Python/rijksdriehoek.py

    Args:
        lat (float): latitude (in dd)
        lon (float): longitude (in dd)

    References:
        Schreutelkamp, F. H., & van Hees, G. S. (2001). Benaderingsformules voor de transformatie 
            tussen RD-en WGS84-kaartcoördinaten. NGT Geodesia, februari, 64-69.
    """

    # transformation
    pqr = [
        (0, 1, 190094.945),
        (1, 1, -11832.228),
        (2, 1, -114.221),
        (0, 3, -32.391),
        (1, 0, -0.705),
        (3, 1, -2.34),
        (1, 3, -0.608),
        (0, 2, -0.008),
        (2, 3, 0.148)
    ]

    pqs = [
        (1, 0, 309056.544),
        (0, 2, 3638.893),
        (2, 0, 73.077),
        (1, 2, -157.984),
        (3, 0, 59.788),
        (0, 1, 0.433),
        (2, 2, -6.439),
        (1, 1, -0.032),
        (0, 4, 0.092),
        (1, 4, -0.054)
    ]

    # compute the RD coordinates
    dlat = 0.36 * (lat - LAT0)
    dlon = 0.36 * (lon - LON0)
    x = X0
    y = Y0

    for p, q, r in pqr:
        x += r * dlat**p * dlon**q

    for p, q, s in pqs:
        y += s * dlat**p * dlon**q

    return x, y


def rd_to_wgs84(x, y):
    """
    Convert an RD coordinate to a WGS84 point
    Based on formulas from (Schreutelkamp & Van hees, 2001)
    Adapted from: https://github.com/djvanderlaan/rijksdriehoek/blob/master/Python/rijksdriehoek.py

    Args:
        x (float)
        y (float)

    References:
        Schreutelkamp, F. H., & van Hees, G. S. (2001). Benaderingsformules voor de transformatie 
            tussen RD-en WGS84-kaartcoördinaten. NGT Geodesia, februari, 64-69.
    """

    # transformation coefficients
    pqk = [
        (0, 1, 3235.65389),
        (2, 0, -32.58297),
        (0, 2, -0.24750),
        (2, 1, -0.84978),
        (0, 3, -0.06550),
        (2, 2, -0.01709),
        (1, 0, -0.00738),
        (4, 0, 0.00530),
        (2, 3, -0.00039),
        (4, 1, 0.00033),
        (1, 1, -0.00012)
    ]

    pql = [
        (1, 0, 5260.52916),
        (1, 1, 105.94684),
        (1, 2, 2.45656),
        (3, 0, -0.81885),
        (1, 3, 0.05594),
        (3, 1, -0.05607),
        (0, 1, 0.01199),
        (3, 2, -0.00256),
        (1, 4, 0.00128),
        (0, 2, 0.00022),
        (2, 0, -0.00022),
        (5, 0, 0.00026)
    ]

    # compute the WGS84 coordinates
    dx = 1e-5 * (x - X0)
    dy = 1e-5 * (y - Y0)
    lat = LAT0
    lon = LON0

    for p, q, k in pqk:
        lat += k * dx**p * dy**q / 3600

    for p, q, l in pql:
        lon += l * dx**p * dy**q / 3600

    return lat, lon


def wgs84_to_zone_number(lat: float, lon: float):
    """
    Compute the UTM zone number

    Args:
        lat (float): latitude (in dd)
        lon (float): longitude (in dd)
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


def compute_central_lon(z: int):
    return (z - 1) * 6 - 180 + 3


def wgs84_to_utm(lat: float, lon: float):
    """
    Convert a WGS84 coordinate to a UTM coordinate
    Based on formulas from (Snyder, 1987)
    Adapted parts from: https://gist.github.com/twpayne/4409500

    Args:
        lat (float): latitude (in dd)
        lon (float): longitude (in dd)

    References:
        Snyder, J. P. (1987). Map projections -- A working manual (Vol. 1395). US Government Printing Office.
    """
    # constrain lat to [-90.0, 90.0] range, lon to [-180.0, 180.0] range
    lat = wrap90(lat)
    lon = wrap180(lon)

    # ensure lat is not out of range for conversion
    if not -80.0 <= lat <= 84.0:
        raise ValueError(
            f'Latitude out of range [-80.0, 84.0] for UTM conversion: {lat}')

    # get the zone number and letter
    z = wgs84_to_zone_number(lat, lon)
    l = 'CDEFGHJKLMNPQRSTUVWXX'[int((lat + 80) / 8)]

    # convert lat and lon to radians
    φ = radians(lat)
    λ = radians(lon)

    # compute sin, cos and tan of lat to be used in further computations
    φ_sin = sin(φ)
    φ_cos = cos(φ)
    φ_tan = tan(φ)

    # compute the lon of the central meridian
    central_λ = radians(compute_central_lon(z))

    # compute some quantities to be used in further computations
    N = R / sqrt(1 - E * φ_sin**2)
    T = φ_tan**2
    C = E_ * φ_cos**2
    A = (λ - central_λ) * φ_cos

    # compute the true distance to from the equator
    M = R * ((1 - E / 4 - 3 * E**2 / 64 - 5 * E**3 / 256) * φ - (3 * E / 8 + 3 * E**2 / 32 + 45 * E**3 / 1024)
             * sin(2 * φ) + (15 * E**2 / 256 + 45 * E**3 / 1024) * sin(4 * φ) - (35 * E**3 / 3072) * sin(6 * φ))

    # compute the easting (x) and northing (y)
    x = K0 * N * (A + (1 - T + C) * A**3 / 6 + (5 - 18 * T +
                                                T**2 + 72 * C - 58 * E_) * A**5 / 120) + 500000
    y = K0 * (M + N * φ_tan * (A**2 / 2 + (5 - T + 9 * C + 4 * C**2) * A **
                               4 / 24 + (61 - 58 * T + T**2 + 600 * C - 330 * E_) * A**6 / 720))

    if lat < 0:
        y += 10000000

    return x, y, z, l


def utm_to_wgs84(x: float, y: float, z: int, l: str = None):
    """
    Convert a UTM coordinate to a WGS84 coordinate
    Based on formulas from (Snyder, 1987)
    Adapted parts from: https://gist.github.com/twpayne/4409500

    Args:
        x (float): easting
        y (float): northing
        z (int): zone number
        l (str): zone letter. Default: None

    References:
        Snyder, J. P. (1987). Map projections -- A working manual (Vol. 1395). US Government Printing Office.
    """
    # ensure x and y are not out of range for conversion
    if not 160000 <= x <= 840000:
        raise ValueError(
            f'Easting (x) out of range [160e3, 840e3] for WGS84 conversion: {x}')
    if not 0 <= y <= 10000000:
        raise ValueError(
            f'Northing (y) out of range [0, 10e6] for WGS84 conversion: {y}')

    x -= 500000
    if l < 'N':
        y -= 10000000

    # compute some quantities to be used in further computations
    E1 = (1 - sqrt(1 - E)) / (1 + sqrt(1 - E))
    M0 = 0
    M = M0 + y / K0
    M1 = (1 - E / 4 - 3 * E**2 / 64 - 5 * E**3 / 256)
    μ = M / (R * M1)

    λ0 = radians(compute_central_lon(z))
    φ1 = μ + (3 * E1 / 2 - 27 * E1**3 / 32 + 269 * E1**5 / 512) * sin(2 * μ) \
        + (21 * E1**2 / 16 - 55 * E1**4 / 32) * sin(4 * μ) \
        + (151 * E1**3 / 96 - 417 * E1**5 / 128) * sin(6 * μ) \
        + (1097 * E1**4 / 512) * sin(8 * μ)

    C1 = E1 * cos(φ1)**2
    T1 = tan(φ1)**2
    N1 = R / sqrt(1 - E * sin(φ1)**2)
    R1 = R * (1 - E) / (1 - E * sin(φ1)**2)**(3 / 2)
    D = x / (N1 * K0)

    # compute lat and lon in radians
    φ = φ1 - (N1 * tan(φ1) / R1) * (D**2 / 2 - (5 + 3 * T1 + 10 * C1 - 4 * C1**2 - 9 * E_) *
                                    D**4 / 24 + (61 + 90 * T1 + 298 * C1 + 45 * T1**2 - 252 * E_ - 3 * C1**2) * D**6 / 720)
    λ = λ0 + (D - (1 + 2 * T1 + C1) * D**3 / 6 + (5 - 2 * C1 + 28 *
                                                  T1 - 3 * C1**2 + 8 * E_ + 24 * T1**2) * D**5 / 120) / cos(φ1)

    # convert to degrees
    lat = degrees(φ)
    lon = degrees(λ)

    return lat, lon


def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance (in m) between two points (in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first point (in dd)
        lon1 (float): the longitude of the first point (in dd)
        lat2 (float): the latitude of the second point (in dd)
        lon2 (float): the longitude of the second point (in dd)

    Returns:
        The great-circle distance (in m) between the two points.
    """
    # convert dd to radians
    Δλ = radians(lon2 - lon1)
    Δφ = radians(lat2 - lat1)
    φ1 = radians(lat1)
    φ2 = radians(lat2)

    # haversine formula
    a = sin(Δφ / 2)**2 + cos(φ1) * cos(φ2) * sin(Δλ / 2)**2
    c = 2 * asin(sqrt(a))

    # compute the distance (in m)
    d = R * c

    return d


def initial_brng(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the initial bearing (in dd) between two points (also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first point (in dd)
        lon1 (float): the longitude of the first point (in dd)
        lat2 (float): the latitude of the second point (in dd)
        lon2 (float): the longitude of the second point (in dd)

    Returns:
        The initial bearing (in dd) between the two points.
    """
    # convert dd to radians
    Δλ = radians(lon2 - lon1)
    φ1 = radians(lat1)
    φ2 = radians(lat2)

    # forward azimuth (in radians)
    x = cos(φ1) * sin(φ2) - sin(φ1) * cos(φ2) * cos(Δλ)
    y = sin(Δλ) * cos(φ2)
    θ = atan2(y, x)

    # convert radians to dd
    brng = degrees(θ)

    # convert bearing to [0, 360) range
    brng = wrap360(brng)

    return brng


def final_brng(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the final bearing (in dd) between two points (also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first point (in dd)
        lon1 (float): the longitude of the first point (in dd)
        lat2 (float): the latitude of the second point (in dd)
        lon2 (float): the longitude of the second point (in dd)

    Returns:
        The final bearing (in dd) between the two points.
    """
    # get the initial bearing from the second point to the first and reverse it by 180 degrees
    brng = initial_brng(lat2, lon2, lat1, lon1) + 180

    # convert bearing to [0, 360) range
    brng = wrap360(brng)

    return brng


def midpoint(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, float]:
    """
    Calculate the midpoint (in dd) of two points (also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first point (in dd)
        lon1 (float): the longitude of the first point (in dd)
        lat2 (float): the latitude of the second point (in dd)
        lon2 (float): the longitude of the second point (in dd)

    Returns:
        The midpoint (in dd) of the two points.
    """
    # convert dd to radians
    φ1 = radians(lat1)
    λ1 = radians(lon1)
    φ2 = radians(lat2)
    Δλ = radians(lon2 - lon1)

    # compute cartesian coordinates (x, y, z)
    x1 = cos(φ1)
    y1 = 0  # first coordinate in x-z plane, so y = 0
    z1 = sin(φ1)
    x2 = cos(φ2) * cos(Δλ)
    y2 = cos(φ2) * sin(Δλ)
    z2 = sin(φ2)

    # compute cartesian coordinates of the midpoint
    x3 = x1 + x2
    y3 = y1 + y2
    z3 = z1 + z2

    # compute spherical coordinates (lat, lon) of the midpoint in radians
    φ3 = atan2(z3, hypot(x3, y3))
    λ3 = λ1 + atan2(y3, x3)

    # convert radians to dd
    lat3 = degrees(φ3)
    lon3 = degrees(λ3)

    # constrain lon to [-180, 180] range
    lon3 = wrap180(lon3)

    return lat3, lon3


def intermediate_point(lat1: float, lon1: float, lat2: float, lon2: float, frac: float) -> Tuple[float, float]:
    """
    Calculate the intermediate point (in dd) at a fraction along the great circle path between two points (also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html
    References: http://www.edwilliams.org/avform.htm#Intermediate

    Args:
        lat1 (float): the latitude of the first point (in dd)
        lon1 (float): the longitude of the first point (in dd)
        lat2 (float): the latitude of the second point (in dd)
        lon2 (float): the longitude of the second point (in dd)
        frac (float): the fraction along the great circle path (in [0, 1])

    Returns:
        The intermediate point (in dd) at a fraction along the great circle path between the two points (also in dd)
    """
    # convert dd to radians
    φ1 = radians(lat1)
    λ1 = radians(lon1)
    φ2 = radians(lat2)
    λ2 = radians(lon2)

    # compute the distance between the two points
    d = distance(lat1, lon1, lat2, lon2)

    # compute the angular distance (in radians)
    δ = d / R

    a = sin((1 - frac) * δ) / sin(δ)
    b = sin(frac * δ) / sin(δ)

    # compute the cartesian coordinates of the intermediate point
    x = a * cos(φ1) * cos(λ1) + b * cos(φ2) * cos(λ2)
    y = a * cos(φ1) * sin(λ1) + b * cos(φ2) * sin(λ2)
    z = a * sin(φ1) + b * sin(φ2)

    # convert cartesian coordinates to spherical coordinates (in dd)
    lat3, lon3 = cartesian_to_spherical(x, y, z)

    # constrain lon to [-180, 180] range
    lon3 = wrap180(lon3)

    return lat3, lon3


def destination(lat1: float, lon1: float, d: int, brng: float) -> Tuple[float, float]:
    """
    Calculate the destination point from a given initial point, having travelled the given distance on the 
    given initial bearing.
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the initial point (in dd)
        lon1 (float): the longitude of the initial point (in dd)
        d (int): the distance travelled (in m)
        brng (float): the initial bearing (in dd)

    Returns:
        The point (in dd) of the destination.
    """
    # convert latitude, longitude and bearing to radians
    φ1 = radians(lat1)
    λ1 = radians(lon1)
    θ = radians(brng)

    # compute the angular distance (in radians)
    δ = d / R

    # compute the latitude and longitude (in radians)
    φ2 = asin(sin(φ1) * cos(δ) + cos(φ1) * sin(δ) * cos(θ))
    λ2 = λ1 + atan2(sin(θ) * sin(δ) * cos(φ1), cos(δ) - sin(φ1) * sin(φ2))

    # convert radians to dd
    lat_2 = degrees(φ2)
    lon_2 = degrees(λ2)

    # constrain lon to [-180, 180] range
    lon_2 = wrap180(lon_2)

    return lat_2, lon_2


def intersection(lat1: float, lon1: float, brng1: float, lat2: float, lon2: float, brng2: float) -> Tuple[float, float]:
    """
    Calculate the intersection (in dd) of two paths defined by their points and bearings (both also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first point (in dd)
        lon1 (float): the longitude of the first point (in dd)
        brng1 (float): the initial bearing from the first point (in dd)
        lat2 (float): the latitude of the second point (in dd)
        lon2 (float): the longitude of the second point (in dd)
        brng2 (float): the initial bearing from the second point (in dd)

    Returns:
        The intersection point (in dd) of the two paths.
    """
    # convert dd to radians
    φ1 = radians(lat1)
    λ1 = radians(lon1)
    φ2 = radians(lat2)
    λ2 = radians(lon2)
    θ13 = radians(brng1)
    θ23 = radians(brng2)

    # compute the distance between the two points
    d = distance(lat1, lon1, lat2, lon2)

    # compute the angular distance (in radians)
    δ12 = d / R

    if isclose(δ12, 0, rel_tol=1e-5):  # coincedence
        return lat1, lon1

    # compute initial and final bearings between the two points
    θa = acos((sin(φ2) - sin(φ1) * cos(δ12)) / (sin(δ12) * cos(φ1)))
    θb = acos((sin(φ1) - sin(φ2) * cos(δ12)) / (sin(δ12) * cos(φ2)))

    # protect against rounding errors
    θa = clip(θa, -π, π)
    θb = clip(θb, -π, π)

    if sin(λ2 - λ1) > 0:
        θ12 = θa
        θ21 = 2 * π - θb
    else:
        θ12 = 2 * π - θa
        θ21 = θb

    # compute angles
    α1 = θ13 - θ12  # angle 2-1-3
    α2 = θ21 - θ23  # angle 1-2-3

    if sin(α1) == 0 and sin(α2) == 0:  # infinite intersections
        raise ValueError(
            f'Infinite intersections for ({lat1}, {lon1}) @ {brng1} and ({lat2}, {lon2}) @ {brng2}')
    if sin(α1) * sin(α2) < 0:  # ambiguous intersection
        raise ValueError(
            f'Ambiguous intersection for ({lat1}, {lon1}) @ {brng1} and ({lat2}, {lon2}) @ {brng2}')

    # compute spherical coordinates (lat, lon) of the intersection
    cosα3 = -cos(α1) * cos(α2) + sin(α1) * sin(α2) * cos(δ12)
    δ13 = atan2(sin(δ12) * sin(α1) * sin(α2), cos(α2) + cos(α1) * cosα3)
    φ3 = asin(sin(φ1) * cos(δ13) + cos(φ1) * sin(δ13) * cos(θ13))
    φ3 = clip(φ3, -π, π)  # protect against rounding errors
    Δλ13 = atan2(sin(θ13) * sin(δ13) * cos(φ1), cos(δ13) - sin(φ1) * sin(φ3))
    λ3 = λ1 + Δλ13

    # convert to degrees
    lat3 = degrees(φ3)
    lon3 = degrees(λ3)

    return lat3, lon3


def intersection2(
    lat11: float,
    lon11: float,
    lat12: float,
    lon12: float,
    lat21: float,
    lon21: float,
    lat22: float,
    lon22: float
) -> Tuple[float, float]:
    """
    Calculate the intersection (in dd) of two paths defined by their points (both also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat11 (float): the latitude of the first point of the first path (in dd)
        lon11 (float): the longitude of the first point of the first path (in dd)
        lat12 (float): the latitude of the second point of the first path (in dd)
        lon12 (float): the longitude of the second point of the first path (in dd)
        lat21 (float): the latitude of the first point of the second path (in dd)
        lon21 (float): the longitude of the first point of the second path (in dd)
        lat22 (float): the latitude of the second point of the second path (in dd)
        lon22 (float): the longitude of the second point of the second path (in dd)

    Returns:
        The intersection (in dd) of the two paths.
    """
    # get initial bearings
    brng1 = initial_brng(lat11, lon11, lat12, lon12)
    brng2 = initial_brng(lat21, lon21, lat22, lon22)

    return intersection(lat11, lon11, brng1, lat21, lon21, brng2)


def convert_color(image: Image, color: str):
    color_rgb = ImageColor.getrgb(color)
    pixels = image.load()

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if pixels[x, y] != (255, 255, 255, 0):
                pixels[x, y] = color_rgb + (pixels[x, y][3], )


def get_string_formatting_arguments(s: str):
    return [t[1] for t in Formatter().parse(s) if t[1] is not None]


def is_out_of_bounds(test: Dict[str, float], bounds: Dict[str, float]) -> bool:
    if test['lat_min'] < bounds['lat_min']:
        return True
    elif test['lon_min'] < bounds['lon_min']:
        return True
    elif test['lat_max'] > bounds['lat_max']:
        return True
    elif test['lon_max'] > bounds['lat_max']:
        return True
    return False
