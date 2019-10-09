#!/usr/bin/env python3
# -*- coding: utf-8 -*-
NAME = 'papermap'
DESCRIPTION = 'papermap is a CLI application for creating paper maps based on open map data and styles'  # description of papermap
VERSION =  '0.1'  # current version of papermap
HEADERS = {'User-Agent': f'{NAME}v{VERSION}', 'Accept': 'image/png,image/*;q=0.9,*/*;q=0.8'}  # headers used for requests
TILE_SIZE = 256  # size (width/height) of tiles
GRID_SIZE = 1000_000  # grid size (in mm)
SERVERS = ['a', 'b', 'c']  # tile server subdomains
C = 40_075_017  # circumference of the equator
X0 = 155_000  # RD coordinates of Amersfoort
Y0 = 463_000
LAT0 = 52.15517440  # WGS84 coordinates of Amersfoort
LON0 = 5.38720621
