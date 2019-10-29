#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from math import atan, cos, degrees, floor, log, pi, radians, sin, sinh, sqrt, tan
from pathlib import Path
from typing import List, Tuple, Union

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .constants import E_, K0, LAT0, LON0, X0, Y0, C, E, R


def constrain_lon(lon: float):
    """
    Constrains longitude to [-180, 180] range

    Args:
        lon (float): longitude (in dd)
    """
    return (lon + 180) % 360 - 180


def constrain_lat(lat: float):
    """
    Constrains latitude to [-90, 90] range

    Args:
        lat (float): latitude (in dd)
    """
    return (lat + 90) % 180 - 90


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
    x = ((lon + 180.0) / 360) * 2 ** zoom

    return x


def x_to_lon(x: Union[float, int], zoom: int) -> float:
    """
    Converts x (tile number) to longitude given zoom level

    Args:
        x (float / int): tile number
        zoom (int): zoom level
    """
    lon = x / (2 ** zoom) * 360 - 180
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
    lat_rad = radians(lat)

    # convert lat to [0, 1] range
    y = ((1 - log(tan(lat_rad) + 1 / cos(lat_rad)) / pi) / 2) * 2 ** zoom

    return y


def y_to_lat(y: Union[float, int], zoom: int) -> float:
    """
    Converts y (tile number) to latitude given zoom level

    Args:
        y (float / int): tile number
        zoom (int): zoom level
    """
    lat = atan(sinh(pi * (1 - 2 * y / (2 ** zoom)))) / pi * 180
    return lat


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
        x += r * dlat ** p * dlon ** q

    for p, q, s in pqs:
        y += s * dlat ** p * dlon ** q

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
        lat += k * dx ** p * dy ** q / 3600

    for p, q, l in pql:
        lon += l * dx ** p * dy ** q / 3600

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
        raise ValueError(f'Latitude out of range [-80.0, 84.0] for UTM conversion: {lat}')

    # get the zone number and letter
    z = wgs84_to_zone_number(lat, lon)
    l = 'CDEFGHJKLMNPQRSTUVWXX'[int((lat + 80) / 8)]

    # convert lat and lon to radians
    lat_rad = radians(lat)
    lon_rad = radians(lon)

    # compute sin, cos and tan of lat to be used in further computations
    lat_sin = sin(lat_rad)
    lat_cos = cos(lat_rad)
    lat_tan = tan(lat_rad)

    # compute the lon of the central meridian
    central_lon_rad = radians(compute_central_lon(z))

    # compute some quantities to be used in further computations
    N = R / sqrt(1 - E * lat_sin ** 2)
    T = lat_tan ** 2
    C = E_ * lat_cos ** 2
    A = (lon_rad - central_lon_rad) * lat_cos

    # compute the true distance to from the equator
    M = R * ((1 - E / 4 - 3 * E ** 2 / 64 - 5 * E ** 3 / 256) * lat_rad - (3 * E / 8 + 3 * E ** 2 / 32 + 45 * E ** 3 / 1024) *
             sin(2 * lat_rad) + (15 * E ** 2 / 256 + 45 * E ** 3 / 1024) * sin(4 * lat_rad) - (35 * E ** 3 / 3072) * sin(6 * lat_rad))

    # compute the easting (x) and northing (y)
    x = K0 * N * (A + (1 - T + C) * A ** 3 / 6 + (5 - 18 * T + T ** 2 + 72 * C - 58 * E_) * A ** 5 / 120) + 500000
    y = K0 * (M + N * lat_tan * (A ** 2 / 2 + (5 - T + 9 * C + 4 * C ** 2) * A **
                                 4 / 24 + (61 - 58 * T + T ** 2 + 600 * C - 330 * E_) * A ** 6 / 720))

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
        raise ValueError(f'Easting (x) out of range [160e3, 840e3] for WGS84 conversion: {x}')
    if not 0 <= y <= 10000000:
        raise ValueError(f'Northing (y) out of range [0, 10e6] for WGS84 conversion: {y}')

    x -= 500000
    if l < 'N':
        y -= 10000000

    # compute some quantities to be used in further computations
    E1 = (1 - sqrt(1 - E)) / (1 + sqrt(1 - E))
    M0 = 0
    M = M0 + y / K0
    M1 = (1 - E / 4 - 3 * E**2 / 64 - 5 * E**3 / 256)
    mu = M / (R * M1)

    LON0 = compute_central_lon(z)
    LAT1 = mu + (3 * E1 / 2 - 27 * E1 ** 3 / 32 + 269 * E1 ** 5 / 512) * sin(2 * mu) + (21 * E1 ** 2 / 16 - 55 * E1 ** 4 / 32) * \
        sin(4 * mu) + (151 * E1 ** 3 / 96 - 417 * E1 ** 5 / 128) * sin(6 * mu) + (1097 * E1 ** 4 / 512) * sin(8 * mu)

    C1 = E1 * cos(LAT1) ** 2
    T1 = tan(LAT1) ** 2
    N1 = R / sqrt(1 - E * sin(LAT1) ** 2)
    R1 = R * (1 - E) / (1 - E * sin(LAT1) ** 2) ** (3 / 2)
    D = x / (N1 * K0)

    lat = degrees(LAT1 - (N1 * tan(LAT1) / R1) * (D ** 2 / 2 - (5 + 3 * T1 + 10 * C1 - 4 * C1 ** 2 - 9 * E_)
                                                  * D ** 4 / 24 + (61 + 90 * T1 + 298 * C1 + 45 * T1 ** 2 - 252 * E_ - 3 * C1 ** 2) * D ** 6 / 720))
    lon = LON0 + degrees((D - (1 + 2 * T1 + C1) * D ** 3 / 6 + (5 - 2 * C1 + 28 * T1 -
                                                                3 * C1 ** 2 + 8 * E_ + 24 * T1 ** 2) * D ** 5 / 120) / cos(LAT1))

    return lat, lon


def compute_zoom(lat: float, scale: int, dpi: int = 300) -> float:
    """
    Compute the zoom level, given the latitude, scale and dpi

    Args:
        lat (float): latitude (in dd)
        scale (int): the scale (in cm)
        dpi (int): dots per inch. Default: 300
    """
    scale_px = scale * 25.4 / (1000 * dpi)
    zoom = log(C * cos(radians(lat)) / scale_px, 2) - 8
    return zoom, floor(zoom)


def compute_scale(lat: float, zoom: int, dpi: int = 300) -> float:
    """
    Compute the scale, given the latitude, zoom level and dpi

    Args:
        lat (float): latitude (in dd)
        zoom (int): the zoom level
        dpi (int): dots per inch. Default: 300
    """
    scale_px = C * cos(radians(lat)) / 2 ** (zoom + 8)
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
    resize_factor = 2 ** zoom_scaled / 2 ** zoom

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
    if grid == 'UTM':
        x, y, z, l = wgs84_to_utm(lat, lon)
    elif grid == 'RD':
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
    if grid == 'UTM':
        y_labels = [y_label_start - i for i in range(len(y_grid_cs))]
    elif grid == 'RD':
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
        draw.rectangle([(image.width - text_size[0], image.height - text_size[1]),
                        (image.width, image.height)], fill='white')
        draw.text((image.width - text_size[0], image.height - text_size[1]), text, font=font, fill=color)
    del draw
