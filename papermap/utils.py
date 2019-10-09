#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from math import atan, cos, degrees, floor, log, pi, radians, sinh, tan
from pathlib import Path
from typing import List, Tuple, Union

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .constants import LAT0, LON0, NAME, X0, Y0, C


def lon_to_x(lon: float, zoom: int) -> float:
    """
    Transforms longitude to x (tile number) given zoom level

    Args:
        lon (float): longitude (in dd)
        zoom (int): zoom level
    """
    # convert lon to [-180, 180] range
    lon = (lon + 180) % 360 - 180

    # convert lon to [0, 1] range
    x = ((lon + 180.) / 360) * 2 ** zoom

    return x


def x_to_lon(x: Union[float, int], zoom: int) -> float:
    """
    Transforms x (tile number) to longitude given zoom level

    Args:
        x (float / int): tile number
        zoom (int): zoom level
    """
    lon = x / (2 ** zoom) * 360 - 180
    return lon


def lat_to_y(lat: float, zoom: int) -> float:
    """
    Transforms latitude to y (tile number) given zoom

    Args:
        lat (float): latitude (in dd)
        zoom (int): zoom level
    """
    # convert lat to [-90, 90] range
    lat = (lat + 90) % 180 - 90

    # convert lat to radians
    lat_rad = radians(lat)

    # convert lat to [0, 1] range
    y = ((1 - log(tan(lat_rad) + 1 / cos(lat_rad)) / pi) / 2) * 2 ** zoom

    return y


def y_to_lat(y: Union[float, int], zoom: int) -> float:
    """
    Transforms y (tile number) to latitude given zoom level

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
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees
    return int(degrees), int(minutes), round(seconds, 6)


def dms_to_dd(dms: Tuple[int, int, float]) -> float:
    """
    Convert a quantity in dms to dd

    Args:
        dms (tuple): quantity to be converted to dd
    """
    d, m, s = dms
    return d + m/60 + s/3600


def wgs84_to_rd(lat: float, lon: float) -> Tuple[float, float]:
    """
    Convert WGS84 coordinate into RD coordinate
    Adapted from: https://github.com/djvanderlaan/rijksdriehoek/blob/master/Python/rijksdriehoek.py

    Args:
        lat (float): latitude (in dd)
        lon (float): longitude (in dd)
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
    Adapted from: https://github.com/djvanderlaan/rijksdriehoek/blob/master/Python/rijksdriehoek.py

    Args:
        x (float)
        y (float)
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


def compute_grid_coordinates(image: Image, grid_size: int, lat: float, lon: float, scale: int, dpi: int = 300) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    """
    Computes the coordinates (and labels) for the RD grid

    Args:
    image (PIL.Image): image to compute the grid coordinates (and labels) for
    grid_size (int): size of the grid (in px)
    lat (float): latitude
    lon (float): longitude
    scale (int): scale of the map
    dpi (int): dots per inch. Default: 300
    """
    # convert WGS84 coordinate (lat, lon) into RD coordinate (x, y)
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
    y_labels = [y_label_start - i for i in range(1, len(y_grid_cs) + 1)]

    return list(zip(x_grid_cs, map(str, x_labels))), list(zip(y_grid_cs, map(str, y_labels)))


def add_grid(image: Image, grid_size: int, lat: float, lon: float, scale: int, dpi: int = 300, font: ImageFont = ImageFont.truetype('arial.ttf', 35), color: str = 'black') -> None:
    """
    Adds a grid to the image

    Args:
        image (PIL.Image): image to add a grid to
        grid_size (int): grid size (in px)
        lat (float): latitude (in dd)
        lon (float): longitude (in dd)
        scale (int): image scale (in cm)
        dpi (int): dots per inch. Default: 300
        font (PIL.ImageFont): the font to use for the grid labels. Default: Arial, size 35
        color (str): color of the grid lines. Default: 'black'
    """
    # get grid coordinates
    x_grid, y_grid = compute_grid_coordinates(image, grid_size, lat, lon, scale, dpi)

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


def add_attribution_scale(image: Image, attribution: str, scale: int, font: ImageFont = ImageFont.truetype('arial.ttf', 35), color: str = 'black') -> None:
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
    text = f'{attribution}. Scale: 1:{scale}'
    text_size = draw.textsize(text, font=font)
    if text_size[0] <= image.width:
        draw.rectangle([(image.width - text_size[0], image.height - text_size[1]), (image.width, image.height)], fill='white')
        draw.text((image.width - text_size[0], image.height - text_size[1]), text, font=font, fill=color)
    del draw
