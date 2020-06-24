#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from math import asin, atan, atan2, cos, degrees, floor, hypot, isclose, log, radians, sin, sinh, sqrt, tan
from math import pi as π
from string import Formatter
from typing import Dict, List, Tuple, Union

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

from .constants import E_, K0, LAT0, LON0, X0, Y0, C, E, R


def constrain_angle(angle: float, limit: float) -> float:
    """
    Constrains an angle (either in dd or rad) to [-limit, limit] range.

    Args:
        angle (int/float): angle (in dd/rad)
        limit (int/float): limit (in dd/rad)

    Returns:
        The angle constrained to [-limit, limit] range.
    """
    if -limit <= angle <= limit:  # angle already in [-limit, limit] range
        return angle
    return (angle + limit) % (2 * limit) - limit


def constrain_lon(lon: float) -> float:
    """
    Constrains longitude to [-180, 180] range

    Args:
        lon (int/float): longitude (in dd)

    Returns:
        The longitude constrained to [-180, 180] range.
    """
    return constrain_angle(lon, 180)


def constrain_lat(lat: float) -> float:
    """
    Constrains latitude to [-90, 90] range

    Args:
        lat (int/float): latitude (in dd)

    Returns:
        The latitude constrained to [-90, 90] range.
    """
    return constrain_angle(lat, 90)


def constrain_brng(brng: float) -> float:
    """
    Constrains bearing to [0, 360] range

    Args:
        bearing (int/float): bearing (in dd)

    Returns:
        The bearing constrained to [0, 360] range.
    """
    if 0 <= brng <= 360:  # bearing already in [0, 360] range
        return brng
    return brng % 360


def lon_to_x(lon: float, zoom: int) -> float:
    """
    Converts longitude to x (tile number) given zoom level

    Args:
        lon (float): longitude (in dd)
        zoom (int): zoom level
    """
    # constrain lon to [-180, 180] range
    lon = constrain_lon(lon)

    # convert lon to [0, 1] range
    x = ((lon + 180.0) / 360) * 2**zoom

    return x


def x_to_lon(x: Union[float, int], zoom: int) -> float:
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
    lat = constrain_lat(lat)

    # convert lat to radians
    φ = radians(lat)

    # convert lat to [0, 1] range
    y = ((1 - log(tan(φ) + 1 / cos(φ)) / π) / 2) * 2**zoom

    return y


def y_to_lat(y: Union[float, int], zoom: int) -> float:
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
    return d + m / 60 + s / 3600


def spherical_to_cartesian(lat: float, lon: float, r: float = R) -> Tuple[float, float, float]:
    """
    Convert spherical coordinates (lat, lon)  to cartesian coordinates (x, y, z)
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
    Convert cartesian coordinates (x, y, z) to spherical coordinates (lat, lon)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        x (float): x
        y (float): y
        z (float): z

    Returns:
        The spherical coordinates (lat, lon).
    """
    # compute the spherical coordinates in radians
    φ = atan2(z, hypot(x, y))
    λ = atan2(y, x)
    
    # convert radians to degrees
    lat = degrees(φ)
    lon = degrees(λ)
    
    return lat, lon


def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance (in m) between two coordinates (in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first coordinate (in dd)
        lon1 (float): the longitude of the first coordinate (in dd)
        lat2 (float): the latitude of the second coordinate (in dd)
        lon2 (float): the longitude of the second coordinate (in dd)

    Returns:
        The great-circle distance (in m) between the two coordinates.
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
    Calculate the initial bearing (in dd) between two coordinates (also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first coordinate (in dd)
        lon1 (float): the longitude of the first coordinate (in dd)
        lat2 (float): the latitude of the second coordinate (in dd)
        lon2 (float): the longitude of the second coordinate (in dd)

    Returns:
        The initial bearing (in dd) between the two coordinates.
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

    # convert bearing to [0, 360] range
    brng = constrain_brng(brng)

    return brng


def final_brng(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the final bearing (in dd) between two coordinates (also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first coordinate (in dd)
        lon1 (float): the longitude of the first coordinate (in dd)
        lat2 (float): the latitude of the second coordinate (in dd)
        lon2 (float): the longitude of the second coordinate (in dd)

    Returns:
        The final bearing (in dd) between the two coordinates.
    """
    # get the initial bearing from the second coordinate to the first and reverse it by 180 degrees
    brng = initial_brng(lat2, lon2, lat1, lon1) + 180

    # convert bearing to [0, 360] range
    brng = constrain_brng(brng)

    return brng


def midpoint(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, float]:
    """
    Calculate the midpoint (in dd) of two coordinates (also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first coordinate (in dd)
        lon1 (float): the longitude of the first coordinate (in dd)
        lat2 (float): the latitude of the second coordinate (in dd)
        lon2 (float): the longitude of the second coordinate (in dd)

    Returns:
        The midpoint (in dd) of the two coordinates.
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
    φ3 = atan2(mid_z, hypot(mid_x, mid_y))
    λ3 = λ1 + atan2(mid_y, mid_x)
    
    # convert radians to dd
    lat3 = degrees(φ3)
    lon3 = degrees(λ3)

    # constrain lon to [-180, 180] range
    lon_3 = constrain_lon(lon_3)
    
    return lat3, lon3


def intermediate_point(lat1: float, lon1: float, lat2: float, lon2: float, frac: float) -> Tuple[float, float]:
    """
    Calculate the intermediate point (in dd) at a fraction along the great circle path between two coordinates (also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html
    References: http://www.edwilliams.org/avform.htm#Intermediate

    Args:
        lat1 (float): the latitude of the first coordinate (in dd)
        lon1 (float): the longitude of the first coordinate (in dd)
        lat2 (float): the latitude of the second coordinate (in dd)
        lon2 (float): the longitude of the second coordinate (in dd)
        frac (float): the fraction along the great circle path (in [0, 1])

    Returns:
        The intermediate point (in dd) at a fraction along the great circle path between the two coordinates (also in dd)
    """
    # convert dd to radians
    φ1 = radians(lat1)
    λ1 = radians(lon1)
    φ2 = radians(lat2)
    λ2 = radians(lon2)
    
    # compute the distance between the two coordinates
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
    lat3, lon3 = cartesian_to_spherical_2(x, y, z)

    # constrain lon to [-180, 180] range
    lon_3 = constrain_lon(lon_3)
    
    return lat3, lon3


def destination(lat1: float, lon1: float, d: int, brng: float) -> Tuple[float, float]:
    """
    Calculate the destination coordinate from a given initial coordinate, having travelled the given distance on the 
    given initial bearing.
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the initial coordinate (in dd)
        lon1 (float): the longitude of the initial coordinate (in dd)
        d (int): the distance travelled (in m)
        brng (float): the initial bearing (in dd)

    Returns:
        the coordinates in (lat, lon) of the destination.
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
    lon_2 = constrain_lon(lon_2)

    return lat_2, lon_2


def intersection(lat1: float, lon1: float, brng1: float, lat2: float, lon2: float, brng2: float) -> Tuple[float, float]:
    """
    Calculate the intersection (in dd) of two paths defined by their coordinates and bearings (both also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat1 (float): the latitude of the first coordinate (in dd)
        lon1 (float): the longitude of the first coordinate (in dd)
        brng1 (float): the initial bearing from the first coordinate (in dd)
        lat2 (float): the latitude of the second coordinate (in dd)
        lon2 (float): the longitude of the second coordinate (in dd)
        brng2 (float): the initial bearing from the second coordinate (in dd)

    Returns:
        The intersection (in dd) of the two paths.
    """
    # convert dd to radians
    φ1 = radians(lat1)
    λ1 = radians(lon1)
    φ2 = radians(lat2)
    λ2 = radians(lon2)
    θ13 = radians(brng1)
    θ23 = radians(brng2)
    
    # compute the distance between the two coordinates
    d = distance(lat1, lon1, lat2, lon2)
    
    # compute the angular distance (in radians)
    δ12 = d / R
    
    if isclose(δ12, 0, rel_tol=1e-5):  # coincedence
        return lat1, lon1
    
    # compute initial and final bearings between the two coordinates
    θa = acos((sin(φ2) - sin(φ1) * cos(δ12)) / (sin(δ12) * cos(φ1)))
    θb = acos((sin(φ1) - sin(φ2) * cos(δ12)) / (sin(δ12) * cos(φ2)))
    
    # protect against rounding errors
    θa = min(max(θa, -π), π)
    θb = min(max(θb, -π), π)

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
        raise ValueError(f'Infinite intersections for ({lat1}, {lon1}) @ {brng1} and ({lat2}, {lon2}) @ {brng2}')
    if sin(α1) * sin(α2) < 0:  # ambiguous intersection
        raise ValueError(f'Ambiguous intersection for ({lat1}, {lon1}) @ {brng1} and ({lat2}, {lon2}) @ {brng2}')

    # compute spherical coordinates (lat, lon) of the intersection 
    cosα3 = -cos(α1) * cos(α2) + sin(α1) * sin(α2) * cos(δ12)
    δ13 = atan2(sin(δ12) * sin(α1) * sin(α2), cos(α2) + cos(α1) * cosα3)
    φ3 = asin(sin(φ1) * cos(δ13) + cos(φ1) * sin(δ13) * cos(θ13))
    φ3 = min(max(φ3, -π), π)  # protect against rounding errors
    Δλ13 = atan2(sin(θ13) * sin(δ13) * cos(φ1), cos(δ13) - sin(φ1) * sin(φ3))
    λ3 = λ1 + Δλ13

    # convert to degrees
    lat3 = degrees(φ3)
    lon3 = degrees(λ3)
    
    return lat3, lon3


def intersection2(lat11: float, lon11: float, lat12: float, lon12: float, lat21: float, lon21: float, lat22: float, lon22: float) -> Tuple[float, float]:
    """
    Calculate the intersection (in dd) of two paths defined by their coordinates (both also in dd)
    Adapted from: https://www.movable-type.co.uk/scripts/latlong.html

    Args:
        lat11 (float): the latitude of the first coordinate of the first path (in dd)
        lon11 (float): the longitude of the first coordinate of the first path (in dd)
        lat12 (float): the latitude of the second coordinate of the first path (in dd)
        lon12 (float): the longitude of the second coordinate of the first path (in dd)
        lat21 (float): the latitude of the first coordinate of the second path (in dd)
        lon21 (float): the longitude of the first coordinate of the second path (in dd)
        lat22 (float): the latitude of the second coordinate of the second path (in dd)
        lon22 (float): the longitude of the second coordinate of the second path (in dd)
        
    Returns:
        The intersection (in dd) of the two paths.
    """
    # get initial bearings
    brng1 = initial_brng(lat11, lon11, lat12, lon12)
    brng2 = initial_brng(lat21, lon21, lat22, lon22)
    
    return intersection(lat11, lon11, brng1, lat21, lon21, brng2)


def wgs84_to_rd(lat: float, lon: float) -> Tuple[float, float]:
    """
    Convert WGS84 coordinate into RD coordinate
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
    Convert RD coordinate into WGS84 coordinate
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
    Convert WGS84 coordinate into UTM coordinate
    Based on formulas from (Snyder, 1987)
    Adapted parts from: https://gist.github.com/twpayne/4409500

    Args:
        lat (float): latitude (in dd)
        lon (float): longitude (in dd)

    References:
        Snyder, J. P. (1987). Map projections -- A working manual (Vol. 1395). US Government Printing Office.
    """
    # constrain lat to [-90.0, 90.0] range, lon to [-180.0, 180.0] range
    lat = constrain_lat(lat)
    lon = constrain_lon(lon)

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
    Convert UTM coordinate into WGS84 coordinate
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


def compute_zoom(lat: float, scale: int, dpi: int = 300) -> float:
    """
    Compute the zoom level, given the latitude, scale and dpi

    Args:
        lat (float): latitude (in dd)
        scale (int): the scale (in cm)
        dpi (int): dots per inch. Default: 300
    """
    # convert lat to radians
    φ = radians(lat)

    # compute the zoom level
    scale_px = scale * 25.4 / (1000 * dpi)
    zoom = log(C * cos(φ) / scale_px, 2) - 8
    return zoom, floor(zoom)


def compute_scale(lat: float, zoom: int, dpi: int = 300) -> float:
    """
    Compute the scale, given the latitude, zoom level and dpi

    Args:
        lat (float): latitude (in dd)
        zoom (int): the zoom level
        dpi (int): dots per inch. Default: 300
    """
    # convert lat to radians
    φ = radians(lat)

    # compute the scale
    scale_px = C * cos(φ) / 2**(zoom + 8)
    scale = scale_px * dpi * 1000 / 25.4
    return scale


def compute_scaled_size(size: Tuple[int, int], zoom: float, zoom_scaled: int) -> float:
    """
    Compute the scaled image size, given the zoom level

    Args:
        size (tuple): size (width, height)
        zoom (float): zoom level
        zoom_scaled (int) rounded-down zoom level
    """
    # compute the resize factor
    resize_factor = 2**zoom_scaled / 2**zoom

    # compute the new height and width
    width, height = size
    new_width = round(width * resize_factor)
    new_height = round(height * resize_factor)

    return new_width, new_height


def compute_grid_coordinates(
    image: Image,
    grid: str,
    grid_size: int,
    lat: float,
    lon: float,
    scale: int,
    dpi: int = 300
) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    """
    Computes the coordinates (and labels) for the RD grid

    Args:
        image (PIL.Image): image to compute the grid coordinates (and labels) for
        grid (str): coordinate grid to add to the image
        grid_size (int): size of the grid (in px)
        lat (float): latitude
        lon (float): longitude
        scale (int): scale of the map
        dpi (int): dots per inch. Default: 300
    """
    # convert WGS84 coordinate (lat, lon) into UTM/RD coordinate (x, y)
    if grid == 'utm':
        x, y, z, l = wgs84_to_utm(lat, lon)
    elif grid == 'rd':
        x, y = wgs84_to_rd(lat, lon)

    # round RD coordinate to nearest thousand
    x_rnd = round(x, -3)
    y_rnd = round(y, -3)

    # compute distance between RD and RD_rnd in mm
    dx_mm = (x - x_rnd) / scale * 1000
    dy_mm = (y - y_rnd) / scale * 1000

    # convert distance from mm to px
    dx_px = mm_to_px(dx_mm, dpi)
    dy_px = mm_to_px(dy_mm, dpi)

    # determine center grid coordinate (in px)
    x_grid_center = int(image.width / 2 - dx_px)
    y_grid_center = int(image.height / 2 - dy_px)

    # determine start grid coordinate (in px)
    x_grid_start = x_grid_center % grid_size
    y_grid_start = y_grid_center % grid_size

    # determine the start grid coordinate label (RD coordinate)
    x_label_start = int(x_rnd / 1000 - x_grid_center // grid_size)
    y_label_start = int(y_rnd / 1000 + y_grid_center // grid_size)

    # determine the grid coordinates (in px)
    x_grid_cs = range(x_grid_start, image.width, grid_size)
    y_grid_cs = range(y_grid_start, image.height, grid_size)

    # determine the grid coordinates labels (RD coordinates)
    x_labels = [x_label_start + i for i in range(len(x_grid_cs))]
    if grid == 'utm':
        y_labels = [y_label_start - i for i in range(len(y_grid_cs))]
    elif grid == 'rd':
        y_labels = [y_label_start - i for i in range(1, len(y_grid_cs) + 1)]

    return (list(zip(x_grid_cs, map(str, x_labels))), list(zip(y_grid_cs, map(str, y_labels))))


def add_grid(
    image: Image,
    grid: str,
    grid_size: int,
    lat: float,
    lon: float,
    scale: int,
    dpi: int = 300,
    font: ImageFont = ImageFont.truetype('arial.ttf', 35),
    color: str = 'black'
) -> None:
    """
    Adds a grid to the image

    Args:
        image (PIL.Image): image to add a grid to
        grid (str): coordinate grid to add to the image
        grid_size (int): grid size (in px)
        lat (float): latitude (in dd)
        lon (float): longitude (in dd)
        scale (int): image scale (in cm)
        dpi (int): dots per inch. Default: 300
        font (PIL.ImageFont): the font to use for the grid labels. Default: Arial, size 35
        color (str): color of the grid lines. Default: 'black'
    """
    # get grid coordinates
    x_grid, y_grid = compute_grid_coordinates(image, grid, grid_size, lat, lon, scale, dpi)

    draw = ImageDraw.Draw(image)

    # draw vertical grid lines
    for x, label in x_grid:
        # draw grid line
        draw.line(((x, 0), (x, image.height)), fill=color)

        # draw grid label
        text_size = draw.textsize(label, font=font)
        draw.rectangle([(x - text_size[0] / 2, 0), (x + text_size[0] / 2, text_size[1])], fill='white')
        draw.text((x - text_size[0] / 2, 0), label, font=font, fill=color)

    # draw horizontal grid lines
    for y, label in y_grid:
        # draw grid line
        draw.line(((0, y), (image.width, y)), fill=color)

        # draw grid label
        text_size = draw.textsize(label, font=font)
        text_image = Image.new('RGB', text_size, '#fff')
        text_draw = ImageDraw.Draw(text_image)
        text_draw.text((0, 0), label, font=font, fill=color)
        text_image = text_image.rotate(90, expand=1)
        image.paste(text_image, (0, int(y - text_size[0] / 2)))
        del text_draw
    del draw


def add_attribution_scale(
    image: Image,
    attribution: str,
    scale: int,
    font: ImageFont = ImageFont.truetype('arial.ttf', 35),
    color: str = 'black'
) -> None:
    """
    Adds the attribution and scale to the image

    Args:
        image (PIL.Image): image to add a grid to
        attribution (str):  attribution of tile server
        scale (int): image scale (in cm)
        font (PIL.ImageFont): the font to use for the attribution and scale. Default: Arial, size 35
        color (str): color of the text. Default: 'black'
    """
    draw = ImageDraw.Draw(image)
    text = f'{attribution}. Created with PaperMap. Scale: 1:{scale}'
    text_size = draw.textsize(text, font=font)
    if text_size[0] <= image.width:
        draw.rectangle(
            [(image.width - text_size[0], image.height -
              text_size[1]), (image.width, image.height)],
            fill='white'
        )
        draw.text(
            (image.width - text_size[0], image.height - text_size[1]), text, font=font, fill=color)
    del draw


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
