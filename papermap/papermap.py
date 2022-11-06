#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from io import BytesIO
from itertools import count, cycle
from math import ceil, floor, radians
from pathlib import Path
from subprocess import Popen

import requests
from cachecontrol import CacheControl
from fpdf import FPDF
from PIL import Image

from .constants import *
from .defaults import *
from .gpx import GPX
from .tile import Tile
from .utils import (get_string_formatting_arguments, is_out_of_bounds,
                    lat_to_y, lon_to_x, mm_to_px, rd_to_wgs84, scale_to_zoom,
                    utm_to_wgs84, wgs84_to_rd, wgs84_to_utm, x_to_lon,
                    y_to_lat, pt_to_mm, drange)


class PaperMap(object):

    def __init__(
        self,
        lat: float,
        lon: float,
        tile_server: str = TILE_SERVER_DEFAULT,
        api_key: str = API_KEY_DEFAULT,
        scale: int = SCALE_DEFAULT,
        size: str = SIZE_DEFAULT,
        dpi: int = DPI_DEFAULT,
        margin_top: int = MARGIN_DEFAULT,
        margin_bottom: int = MARGIN_DEFAULT,
        margin_left: int = MARGIN_DEFAULT,
        margin_right: int = MARGIN_DEFAULT,
        grid: str = GRID_DEFAULT,
        nb_workers: int = NB_WORKERS_DEFAULT,
        nb_retries: int = NB_RETRIES_DEFAULT,
        landscape: bool = False,
        quiet: bool = False,
        gpx: GPX = None,
        **kwargs
    ) -> None:
        """
        Initialize the papermap

        Args:
            lat (float): latitude
            lon (float): longitude
            tile_server (str): Tile server to serve as the base of the paper map. Default: OpenStreetMap
            api_key (str): API key for the chosen tile server (if applicable). Default: None
            scale (int): scale of the paper map (in cm). Default: 25000
            size (str): size of the paper map. Default: A4
            dpi (int): dots per inch. Default: 300
            margin_top (int): top margin (in mm), Default: 12
            margin_bottom (int): bottom margin (in mm), Default: 12
            margin_left (int): left margin (in mm), Default: 12
            margin_right (int): right margin (in mm), Default: 12
            grid (str): coordinate grid to display on the paper map. Default: None
            nb_workers (int): number of workers (for parallelization). Default: 4
            nb_retries (int): number of retries (for failed tiles). Default: 3
            landscape (bool): use landscape orientation. Default: False
            quiet (bool): activate quiet mode. Default: False
            gpx (GPX): GPX object. Default: None
        """
        self.lat = lat
        self.lon = lon
        self.api_key = api_key
        self.scale = scale
        self.dpi = dpi
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.nb_workers = nb_workers
        self.nb_retries = nb_retries
        self.use_landscape = landscape
        self.quiet_mode = quiet
        self.gpx = gpx

        # get the right tile server
        try:
            self.tile_server = TILE_SERVERS_DICT[tile_server]
            try:
                self.servers = cycle(self.tile_server['servers'])
            except KeyError:
                self.servers = cycle([None])
        except KeyError:
            if not self.quiet_mode:
                raise ValueError(
                    f'Invalid tile server. Please choose one of {TILE_SERVER_CHOICES}')
            sys.exit()

        # evaluate whether an API key is provided (if needed)
        if 'a' in get_string_formatting_arguments(self.tile_server['url']) and self.api_key is None:
            if not self.quiet_mode:
                raise ValueError(
                    f'No API key specified for {tile_server} tile server')
            sys.exit()

        # get the paper size
        try:
            self.size = SIZES_DICT[size]
        except KeyError:
            if not self.quiet_mode:
                raise ValueError(
                    f'Invalid paper size. Please choose one of {SIZES_DICT}')
            sys.exit()

        # set the grid
        if grid is not None:
            if grid not in GRID_CHOICES:
                raise ValueError(
                    f'Invalid grid. Please choose one of {GRID_CHOICES}')
        self.grid = grid

        # get the width and height of the paper (incl. margins, in mm)
        self.width = self.size['h'] if self.use_landscape else self.size['w']
        self.height = self.size['w'] if self.use_landscape else self.size['h']

        # compute the width and height of the image (in mm)
        self.im_width = self.width - self.margin_left - self.margin_right
        self.im_height = self.height - self.margin_top - self.margin_bottom

         # compute the proper grid size (in mm)
        self.grid_size = Decimal(GRID_SIZE / self.scale)

        # perform conversions
        self.im_width_px = mm_to_px(self.im_width, self.dpi)
        self.im_height_px = mm_to_px(self.im_height, self.dpi)
        self.φ = radians(self.lat)
        self.λ = radians(self.lon)

        # compute the zoom and resize factor
        self.zoom = scale_to_zoom(self.scale, self.lat, self.dpi)
        self.zoom_scaled = floor(self.zoom)
        self.resize_factor = 2**self.zoom_scaled / 2**self.zoom

        # make sure the zoom is not out of bounds
        if self.zoom_scaled < self.tile_server['zoom_min'] or self.zoom_scaled > self.tile_server['zoom_max']:
            if not self.quiet_mode:
                raise ValueError('Scale out of bounds')
            sys.exit()

        # compute the scaled width and height of the image (in px)
        self.im_width_scaled_px = round(self.im_width_px * self.resize_factor)
        self.im_height_scaled_px = round(self.im_height_px * self.resize_factor)

        # determine the center tile
        self.x_center = lon_to_x(self.lon, self.zoom_scaled)
        self.y_center = lat_to_y(self.lat, self.zoom_scaled)

        # determine the tiles required to produce the map image
        self.x_min = floor(
            self.x_center - (0.5 * self.im_width_scaled_px / TILE_SIZE))
        self.y_min = floor(
            self.y_center - (0.5 * self.im_height_scaled_px / TILE_SIZE))
        self.x_max = ceil(
            self.x_center + (0.5 * self.im_width_scaled_px / TILE_SIZE))
        self.y_max = ceil(
            self.y_center + (0.5 * self.im_height_scaled_px / TILE_SIZE))

        # compute the coordinate bounds
        self.bounds = {
            'lat_min': y_to_lat(self.y_max, self.zoom_scaled),
            'lon_min': x_to_lon(self.x_min, self.zoom_scaled),
            'lat_max': y_to_lat(self.y_min, self.zoom_scaled),
            'lon_max': x_to_lon(self.x_max, self.zoom_scaled)
        }

        # make sure the gpx tracks / waypoints are not out of bounds
        if self.gpx is not None:
            if is_out_of_bounds(self.gpx.bounds, self.bounds):
                if not self.quiet_mode:
                    raise ValueError('GPX out of bounds')
                sys.exit()

        # initializa the tiles
        self.tiles = []
        for x in range(self.x_min, self.x_max):
            for y in range(self.y_min, self.y_max):
                # x and y may have crossed the date line
                max_tile = 2 ** self.zoom_scaled
                x_tile = (x + max_tile) % max_tile
                y_tile = (y + max_tile) % max_tile

                bbox = (
                    round((x_tile - self.x_center) *
                          TILE_SIZE + self.im_width_scaled_px / 2),
                    round((y_tile - self.y_center) *
                          TILE_SIZE + self.im_height_scaled_px / 2),
                    round((x_tile + 1 - self.x_center) *
                          TILE_SIZE + self.im_width_scaled_px / 2),
                    round((y_tile + 1 - self.y_center) *
                          TILE_SIZE + self.im_height_scaled_px / 2),
                )

                self.tiles.append(Tile(x_tile, y_tile, self.zoom_scaled, bbox))

        # initialize a cache-controlled requests Session object and set the headers
        self.session = CacheControl(requests.Session())
        self.session.headers = HEADERS

        # initialize scaled map image
        self.map_image_scaled = Image.new(
            'RGB', (self.im_width_scaled_px, self.im_height_scaled_px), '#fff')

        # initialize the pdf document
        self.pdf = FPDF(
            orientation="Landscape" if self.use_landscape else "Portrait",
            unit="mm",
            format=(self.width, self.height)
        )
        self.pdf.set_font('Helvetica')
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_top_margin(self.margin_top)
        self.pdf.set_auto_page_break(True, self.margin_bottom)
        self.pdf.set_left_margin(self.margin_left)
        self.pdf.set_right_margin(self.margin_right)
        self.pdf.add_page()

    def compute_grid_coordinates(self):
        """
        Computes the coordinates (and labels) for the grid
        """
        # convert WGS84 point (lat, lon) into UTM/RD coordinate (x, y)
        if self.grid == 'utm':
            x, y, _, _ = wgs84_to_utm(self.lat, self.lon)
        elif self.grid == 'rd':
            x, y = wgs84_to_rd(self.lat, self.lon)

        # round UTM/RD coordinates to nearest thousand
        x_rnd = round(x, -3)
        y_rnd = round(y, -3)

        # compute distance between x/y and x/y_rnd in mm
        dx = Decimal((x - x_rnd) / self.scale * 1000)
        dy = Decimal((y - y_rnd) / self.scale * 1000)

        # determine center grid coordinate (in mm)
        x_grid_center = Decimal(self.im_width / 2) - dx
        y_grid_center = Decimal(self.im_height / 2) - dy

        # determine start grid coordinate (in mm)
        x_grid_start = x_grid_center % self.grid_size
        y_grid_start = y_grid_center % self.grid_size

        # determine the start grid coordinate label
        x_label_start = int(Decimal(x_rnd / 1000) - x_grid_center // self.grid_size)
        y_label_start = int(Decimal(y_rnd / 1000) + y_grid_center // self.grid_size)

        # determine the grid coordinates (in mm)
        x_grid_cs = list(drange(x_grid_start, Decimal(self.im_width), self.grid_size))
        y_grid_cs = list(drange(y_grid_start, Decimal(self.im_height), self.grid_size))

        # determine the grid coordinates labels
        x_labels = [x_label_start + i for i in range(len(x_grid_cs))]
        if self.grid == 'utm':
            y_labels = [y_label_start - i for i in range(len(y_grid_cs))]
        elif self.grid == 'rd':
            y_labels = [y_label_start -
                        i for i in range(1, len(y_grid_cs) + 1)]

        x_grid_cs_and_labels = list(zip(x_grid_cs, map(str, x_labels)))
        y_grid_cs_and_labels = list(zip(y_grid_cs, map(str, y_labels)))

        return x_grid_cs_and_labels, y_grid_cs_and_labels

    def render_grid(self):
        """
        Adds a grid to the image
        """
        if self.grid is not None:
            self.pdf.set_draw_color(0, 0, 0)
            self.pdf.set_line_width(0.1)
            self.pdf.set_font_size(8)

            # get grid coordinates
            x_grid_cs_and_labels, y_grid_cs_and_labels = self.compute_grid_coordinates()

            # draw vertical grid lines
            for x, label in x_grid_cs_and_labels:
                x = float(x + self.margin_left)
                label_width = self.pdf.get_string_width(label)

                # draw grid line
                self.pdf.line(x, self.margin_top, x, self.margin_top + self.pdf.eph)

                # draw label
                self.pdf.set_xy(x - label_width / 2, self.margin_top)
                self.pdf.cell(w=label_width, txt=label, align='C', fill=True)

            # draw horizontal grid lines
            for y, label in y_grid_cs_and_labels:
                y = float(y + self.margin_top)
                label_width = self.pdf.get_string_width(label)
                label_height = pt_to_mm(self.pdf.font_size)

                # draw grid line
                self.pdf.line(self.margin_left, y, self.margin_left + self.pdf.epw, y)

                # draw label
                self.pdf.set_xy(self.margin_left, y + label_width / 2)
                with self.pdf.rotation(90):
                    self.pdf.cell(w=label_width, txt=label, align='C', fill=True)

            self.pdf.set_font_size(12)

    def render_attribution_and_scale(self):
        """
        Adds the attribution and scale to the image
        """
        text = f'{self.tile_server["attribution"]}. Created with PaperMap. Scale: 1:{self.scale}'
        self.pdf.set_xy(
            self.margin_left + self.pdf.epw - self.pdf.get_string_width(text),
            self.margin_top + self.pdf.eph - pt_to_mm(self.pdf.font_size_pt)
        )
        self.pdf.cell(w=0, txt=text, align='R', fill=True)

    def download_tiles(self):
        # download the tile images
        for nb_retry in count(1):
            # get the unsuccessful tiles
            tiles = [tile for tile in self.tiles if not tile.success]

            # break if all tiles successful
            if not tiles:
                break

            # break if max number of retries exceeded
            if nb_retry > self.nb_retries:
                if not self.quiet_mode:
                    raise RuntimeError(
                        f'Could not download {len(tiles)}/{len(self.tiles)} tiles after {self.nb_retries} retries.')
                sys.exit()

            with ThreadPoolExecutor(max_workers=self.nb_workers) as executor:
                responses = executor.map(
                    self.session.get,
                    [self.tile_server['url'].format(
                        s=s,
                        x=tile.x,
                        y=tile.y,
                        z=tile.z,
                        a=self.api_key
                    ) for tile, s in zip(tiles, self.servers) if not tile.success]
                )

                for tile, r in zip(tiles, responses):
                    try:
                        if r.status_code == 200:
                            # open the tile image and mark it a success
                            tile.image = Image.open(
                                BytesIO(r.content)).convert('RGBA')
                            tile.success = True
                        else:
                            if not self.quiet_mode:
                                print(
                                    f'Request failed [{r.status_code}]: {r.url}')
                    except ConnectionError as e:
                        if not self.quiet_mode:
                            print(f'Connection error for URL: {str(r.url)}')
                            print(str(e))

    def render_base_layer(self):
        # download all the required tiles
        self.download_tiles()

        # paste all the tiles in the scaled map image
        for tile in self.tiles:
            if tile.image is not None:
                self.map_image_scaled.paste(tile.image, tile.bbox, tile.image)

    def render_gpx(self):
        # draw all the features on the scaled map image
        if self.gpx is not None:
            # render the tracks
            self.gpx.render_tracks(
                self.map_image_scaled,
                (self.x_center, self.y_center),
                self.zoom_scaled,
                TILE_SIZE
            )
            # render the waypoints
            self.gpx.render_waypoints(
                self.map_image_scaled,
                (self.x_center, self.y_center),
                self.zoom_scaled,
                TILE_SIZE
            )

    def render(self):
        # render the base layer
        self.render_base_layer()

        # render the GPX (if applicable)
        self.render_gpx()

        # resize the scaled map image
        self.map_image = self.map_image_scaled.resize(
            (self.im_width_px, self.im_height_px), Image.LANCZOS)

        # paste the map image onto the paper map
        self.pdf.image(self.map_image, w=self.im_width, h=self.im_height)

        # add the coordinate grid
        self.render_grid()

        # add the attribution and scale to the map
        self.render_attribution_and_scale()

    def show(self):
        self.map_image.show()

    def save(self, file: Path, title: str = NAME, author: str = NAME):
        self.file = file
        self.pdf.set_title(title)
        self.pdf.set_author(author)
        self.pdf.set_creator(f"{NAME} v{VERSION}")
        self.pdf.output(self.file)

    def open(self):
        Popen([str(self.file)], shell=True)

    def __repr__(self):
        return f'PaperMap({self.lat}, {self.lon})'


def main():
    # cli arguments
    parser = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION)
    subparsers = parser.add_subparsers(
        title='inputs', dest='input', required=True)

    # global arguments
    parser.add_argument('file', type=str, metavar='PATH',
                        help='File path to save the paper map to')
    parser.add_argument('-t', '--tile_server', type=str, default=TILE_SERVER_DEFAULT,
                        choices=TILE_SERVER_CHOICES, help='Tile server to serve as the base of the paper map')
    parser.add_argument('-a', '--api_key', type=str, default=API_KEY_DEFAULT, metavar='KEY',
                        help='API key for the chosen tile server (if applicable)')
    parser.add_argument('-sz', '--size', type=str, default=SIZE_DEFAULT,
                        choices=SIZES_CHOICES, help='Size of the paper map')
    parser.add_argument('-sc', '--scale', type=int, default=SCALE_DEFAULT,
                        metavar='CENTIMETERS', help='Scale of the paper map')
    parser.add_argument('-mt', '--margin_top', type=int, default=MARGIN_DEFAULT,
                        metavar='MILLIMETERS', help='Top margin')
    parser.add_argument('-mb', '--margin_bottom', type=int, default=MARGIN_DEFAULT,
                        metavar='MILLIMETERS', help='Bottom margin')
    parser.add_argument('-ml', '--margin_left', type=int, default=MARGIN_DEFAULT,
                        metavar='MILLIMETERS', help='Left margin')
    parser.add_argument('-mr', '--margin_right', type=int, default=MARGIN_DEFAULT,
                        metavar='MILLIMETERS', help='Right margin')
    parser.add_argument('-d', '--dpi', type=int, default=DPI_DEFAULT,
                        metavar='NUMBER', help='Dots per inch')
    parser.add_argument('-g', '--grid', type=str, default=GRID_DEFAULT, choices=GRID_CHOICES,
                        help='Coordinate grid to display on the paper map')
    parser.add_argument('-w', '--nb_workers', type=int, default=NB_WORKERS_DEFAULT,
                        metavar='NUMBER', help='Number of workers (for parallelization)')
    parser.add_argument('-o', '--open', action='store_true',
                        help='Open paper map after generating')
    parser.add_argument('-l', '--landscape', action='store_true',
                        help='Use landscape orientation')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Activate quiet mode')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s v{VERSION}',
                        help=f'Display the current version of {NAME}')

    # wgs84 subparser arguments
    wgs84_parser = subparsers.add_parser('wgs84')
    wgs84_parser.add_argument(
        'lat', type=float, metavar='LAT', help='Latitude')
    wgs84_parser.add_argument(
        'lon', type=float, metavar='LON', help='Longitude')

    # utm subparser arguments
    utm_parser = subparsers.add_parser('utm')
    utm_parser.add_argument(
        'east', type=float, metavar='EASTING', help='Easting')
    utm_parser.add_argument('north', type=float,
                            metavar='NORTHING', help='Northing')
    utm_parser.add_argument(
        'zone', type=int, metavar='NUMBER', help='Zone number')
    utm_parser.add_argument(
        'letter', type=str, metavar='LETTER', help='Zone letter')

    # rd subparser arguments
    rd_parser = subparsers.add_parser('rd')
    rd_parser.add_argument('x', type=float, metavar='X', help='X')
    rd_parser.add_argument('y', type=float, metavar='Y', help='Y')

    # gpx subparser arguments
    gpx_parser = subparsers.add_parser('gpx')
    gpx_parser.add_argument('gpx_file', type=str,
                            metavar='PATH', help='File path to the GPX file')
    gpx_parser.add_argument('-tc', '--track_color', type=str, default=TRACK_COLOR_DEFAULT,
                            metavar='COLOR', help='Color to render tracks as')
    gpx_parser.add_argument('-wc', '--waypoint_color', type=str, default=WAYPOINT_COLOR_DEFAULT,
                            metavar='COLOR', help='Color to render waypoints as')

    args = parser.parse_args()

    # compute lat, lon from input method
    if args.input == 'wgs84':
        pass
    elif args.input == 'utm':
        args.lat, args.lon = utm_to_wgs84(
            args.east, args.north, args.zone, args.letter)
    elif args.input == 'rd':
        args.lat, args.lon = rd_to_wgs84(args.x, args.y)
    elif args.input == 'gpx':
        args.gpx = GPX(args.gpx_file, args.track_color, args.waypoint_color)
        args.lat, args.lon = args.gpx.center
    else:
        raise ValueError(
            'Invalid input method. Please choose one of: wgs84, utm, rd or gpx')

    # initialize the paper map
    pm = PaperMap(**vars(args))

    # render it
    pm.render()

    # save it
    try:
        pm.save(args.file)
    except PermissionError:
        if not args.quiet:
            raise RuntimeError(
                'Could not save paper map, please make sure you don\'t have it opened elsewhere')
        sys.exit()

    # open it
    if args.open:
        pm.open()


if __name__ == '__main__':
    main()
