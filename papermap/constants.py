#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from math import pi as π

NAME = 'papermap'
DESCRIPTION = 'A python package and CLI for creating paper maps'  # description of papermap
VERSION = '0.2.2'  # current version of papermap
HEADERS = {  # headers used for requests
    'User-Agent': f'{NAME}v{VERSION}',
    'Accept': 'image/png,image/*;q=0.9,*/*;q=0.8'
}
TILE_SIZE = 256  # size (width/height) of tiles
GRID_SIZE = 1_000_000  # grid size (in mm)
R = 6_378_137  # equatorial Earth radius
R_P = 6_356_752.3142  # polar Earth radius
R_M = 6_371_009  # mean Earth radius
C = 40_075_017  # equatorial circumference
X0 = 155_000  # RD coordinates of Amersfoort
Y0 = 463_000
LAT0 = 52.15517440  # WGS84 coordinates of Amersfoort
LON0 = 5.38720621
K0 = 0.9996  # scale factor
E = 0.00669438  # eccentricity (squared)
E_ = E / (1.0 - E)
