#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from io import BytesIO
from itertools import count
from math import ceil, floor
from pathlib import Path
from random import choice
from subprocess import Popen
from typing import Dict

import requests
from cachecontrol import CacheControl
from PIL import Image

from .constants import *
from .defaults import *
from .tile import Tile
from .utils import (add_attribution_scale, add_grid, compute_scale,
                   compute_scaled_size, compute_zoom, lat_to_y, lon_to_x,
                   mm_to_px)


class PaperMap(object):

    def __init__(
        self, 
        lat: float, 
        lon: float,
        tile_server: str = TILE_SERVER_DEFAULT, 
        scale: int = SCALE_DEFAULT, 
        size: str = SIZE_DEFAULT,
        dpi: int = DPI_DEFAULT,
        margin_top: int = MARGIN_DEFAULT,
        margin_bottom: int = MARGIN_DEFAULT, 
        margin_left: int = MARGIN_DEFAULT, 
        margin_right: int = MARGIN_DEFAULT, 
        nb_workers: int = NB_WORKERS_DEFAULT, 
        nb_retries: int = NB_RETRIES_DEFAULT,
        landscape: bool = False,
        grid: bool = False,
        quiet: bool = False,
        **kwargs
    ) -> None:
        """
        Initialize the papermap

        Args:
            lat (float): latitude
            lon (float): longitude
            scale (int): scale of the paper map (in cm). Default: 25000
            size (str): size of the paper map. Default: A4
            margin_top (int): top margin (in mm), Default: 12
            margin_bottom (int): bottm margin (in mm), Default: 12
            margin_left (int): left margin (in mm), Default: 12
            margin_right (int): bottom margin (in mm), Default: 12
            dpi (int): dots per inch. Default: 300
            nb_workers (int): = Number of workers (for parallelization). Default: 4
            nb_retries (int):  = Number of retries (for failed tiles). Default: 3
            landscape (bool): Use landscape orientation. Default: False
            grid (bool): Use a coordinate grid. Default: False
            open (bool): Open paper map after generating. Default: False
            quiet (bool): Activate quiet mode. Default: False
        """
        self.lat = lat
        self.lon = lon
        self.scale = scale
        self.dpi = dpi
        self.margin_top = mm_to_px(margin_top, self.dpi)
        self.margin_bottom = mm_to_px(margin_bottom, self.dpi)
        self.margin_left = mm_to_px(margin_left, self.dpi)
        self.margin_right = mm_to_px(margin_right, self.dpi)
        self.nb_workers = nb_workers
        self.nb_retries = nb_retries
        self.use_landscape = landscape
        self.use_grid = grid
        self.quiet_mode = quiet

        # get the right tile server
        try:
            self.tile_server = TILE_SERVERS_DICT[tile_server]
        except KeyError:
            if not self.quiet_mode:
                raise ValueError(f'Invalid tile server. Please choose one of {TILE_SERVER_CHOICES}')
            sys.exit()

        # get the paper size
        try:
            self.size = SIZES_DICT[size]
        except KeyError:
            if not self.quiet_mode:
                raise ValueError(f'Invalid paper size. Please choose one of {SIZES_DICT}')
            sys.exit()

        # compute the zoom
        self.zoom, self.zoom_scaled = compute_zoom(self.lat, self.scale, self.dpi)

        # make sure the zoom is not out of bounds
        if self.zoom_scaled < self.tile_server['zoom_min'] or self.zoom_scaled > self.tile_server['zoom_max']:
            if not self.quiet_mode:
                raise ValueError('Scale out of bounds')
            sys.exit()

        # compute the proper grid size (in px)
        self.grid_size = mm_to_px(GRID_SIZE / self.scale, self.dpi)

        # get the width and height of the paper (incl. margins, in px)
        self.width = mm_to_px(self.size['h'] if self.use_landscape else self.size['w'], self.dpi)
        self.height = mm_to_px(self.size['w'] if self.use_landscape else self.size['h'], self.dpi)

        # compute the width and  of the image (in px)
        self.im_width = self.width - self.margin_left - self.margin_right
        self.im_height = self.height - self.margin_top - self.margin_bottom

        # compute the scaled width and height of the image
        self.im_width_scaled, self.im_height_scaled = compute_scaled_size((self.im_width, self.im_height), self.zoom, self.zoom_scaled)

        # determine the center tile
        self.x_center = lon_to_x(self.lon, self.zoom_scaled)
        self.y_center = lat_to_y(self.lat, self.zoom_scaled)

        # determine the tiles required to produce the map image
        self.x_min = floor(self.x_center - (0.5 * self.im_width_scaled / TILE_SIZE))
        self.y_min = floor(self.y_center - (0.5 * self.im_height_scaled / TILE_SIZE))
        self.x_max = ceil(self.x_center + (0.5 * self.im_width_scaled / TILE_SIZE))
        self.y_max = ceil(self.y_center + (0.5 * self.im_height_scaled / TILE_SIZE))

        self.tiles = []

        for x in range(self.x_min, self.x_max):
            for y in range(self.y_min, self.y_max):
                # x and y may have crossed the date line
                max_tile = 2 ** self.zoom_scaled
                x_tile = (x + max_tile) % max_tile
                y_tile = (y + max_tile) % max_tile

                box = (
                    round((x_tile - self.x_center) * TILE_SIZE + self.im_width_scaled / 2),
                    round((y_tile - self.y_center) * TILE_SIZE + self.im_height_scaled / 2),
                    round((x_tile + 1 - self.x_center) * TILE_SIZE + self.im_width_scaled / 2),
                    round((y_tile + 1 - self.y_center) * TILE_SIZE + self.im_height_scaled / 2),
                )

                self.tiles.append(Tile(x_tile, y_tile, self.zoom_scaled, box))

        # initialize paper map and svaled map image
        self.paper_map = Image.new('RGB', (self.width, self.height), '#fff')
        self.map_image_scaled = Image.new('RGB', (self.im_width_scaled, self.im_height_scaled), '#fff')

        # initialize a cache-controlled requests Session object and set the headers
        self.session = CacheControl(requests.Session())
        self.session.headers = HEADERS

    def download_tiles(self):
        for nb_retry in count(1):
            # get the unsuccessful tiles
            tiles = [tile for tile in self.tiles if not tile.success]
            
            # break if all tiles successful
            if not tiles:
                break

            # break if max number of retries exceeded
            if nb_retry > self.nb_retries:
                if not self.quiet_mode:
                    raise RuntimeError(f'Could not download {len(tiles)} tiles after {self.nb_retries} retries.')
                sys.exit()
            
            # download the tiles (parallelalized)
            with ThreadPoolExecutor(max_workers=self.nb_workers) as executor:
                futures = [executor.submit(self.session.get, self.tile_server['url'].format(s=choice(SERVERS), x=tile.x, y=tile.y, z=tile.z)) for tile in tiles if not tile.success]

                for tile, future in zip(tiles, futures):
                    try:
                        r = future.result()

                        if r.status_code == 200:
                            # open the tile image and mark it a success
                            tile.image = Image.open(BytesIO(r.content)).convert('RGBA')                            
                            tile.success = True
                        else:
                            if not self.quiet_mode:
                                print(f'Request failed [{r.status_code}]: {r.url}')
                    except ConnectionError as e:
                        if not self.quiet_mode:
                            print(str(e))

    def render(self):
        # download all the required tiles
        self.download_tiles()

        # paste all the tiles in the scaled map image
        for tile in self.tiles:
            self.map_image_scaled.paste(tile.image, tile.box, tile.image)

        # resize the scaled map image
        self.map_image = self.map_image_scaled.resize((self.im_width, self.im_height), Image.LANCZOS)

        # add the coordinate grid
        if self.use_grid:
            add_grid(self.map_image, GRID_SIZE, self.lat, self.lon, self.scale, self.dpi)

        # add the attribution and scale to the map
        add_attribution_scale(self.map_image, self.tile_server['attribution'], self.scale)

        # paste the map image onto the paper map
        self.paper_map.paste(self.map_image, (self.margin_left, self.margin_top))

    def show(self):
        self.paper_map.show()

    def save(self, file: Path, title: str = NAME, author: str = NAME):
        self.file = file
        self.paper_map.save(self.file, resolution=self.dpi, title=title, author=author)

    def open(self):
        Popen([str(self.file)], shell=True)


def main():
    # cli arguments
    parser = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION)
    parser.version = VERSION

    # required arguments
    parser.add_argument('lat', type=float, metavar='LAT', help='Latitude')
    parser.add_argument('lon', type=float, metavar='LON', help='Longitude')
    parser.add_argument('file', type=str, metavar='PATH', help='File path to save the file to')

    # optional arguments
    parser.add_argument('-t', '--tile_server', type=str, default=TILE_SERVER_DEFAULT, choices=TILE_SERVER_CHOICES, help='Tile server to serve as the base of the paper map')
    parser.add_argument('-sz', '--size', type=str, default=SIZE_DEFAULT, choices=SIZES_CHOICES, help='Size of the paper map')
    parser.add_argument('-sc', '--scale', type=int, default=SCALE_DEFAULT, metavar='CENTIMETERS', help='Scale of the paper map')
    parser.add_argument('-mt', '--margin_top', type=int, default=MARGIN_DEFAULT, metavar='MILLIMETERS', help='Top margin')
    parser.add_argument('-mb', '--margin_bottom', type=int, default=MARGIN_DEFAULT, metavar='MILLIMETERS', help='Bottom margin')
    parser.add_argument('-ml', '--margin_left', type=int, default=MARGIN_DEFAULT, metavar='MILLIMETERS', help='Left margin')
    parser.add_argument('-mr', '--margin_right', type=int, default=MARGIN_DEFAULT, metavar='MILLIMETERS', help='Right margin')
    parser.add_argument('-d', '--dpi', type=int, default=DPI_DEFAULT, metavar='NUMBER', help='Dots per inch')
    parser.add_argument('-w', '--nb_workers', type=int, default=NB_WORKERS_DEFAULT, metavar='NUMBER', help='Number of workers (for parallelization)')
    parser.add_argument('-r', '--nb_retries', type=int, default=NB_RETRIES_DEFAULT, metavar='NUMBER', help='Number of retries (for failed tiles)')
    
    # boolean arguments
    parser.add_argument('-o', '--open', action='store_true', help='Open paper map after generating')
    parser.add_argument('-l', '--landscape', action='store_true', help='Use landscape orientation')
    parser.add_argument('-g', '--grid', action='store_true', help='Use a coordinate grid')
    parser.add_argument('-q', '--quiet', action='store_true', help='Activate quiet mode')
    parser.add_argument('-v', '--version', action='version', help=f'Display the current version of {NAME}')
    
    parsed, _ = parser.parse_known_args()
    args = vars(parsed)

    # initialize the paper map
    pm = PaperMap(**args)
    
    # render it
    pm.render()

    # save it
    file = args['file']
    try:
        pm.save(file)
    except PermissionError:
        if not args['quiet']:
            raise RuntimeError('Could not save paper map, please make sure you don\'t have it opened elsewhere')
        sys.exit()

    # open it
    if args['open']:
        pm.open()


if __name__ == '__main__':
    main()
