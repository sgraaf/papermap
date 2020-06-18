#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Tuple

from lxml import etree
from PIL import Image, ImageDraw

from .defaults import (MAP_MARKER_FILE, TRACK_COLOR_DEFAULT,
                       WAYPOINT_COLOR_DEFAULT)
from .utils import convert_color, lat_to_y, lon_to_x, x_to_px, y_to_px


class Waypoint(object):

    def __init__(self, wpt: etree.Element, NSMAP: dict) -> None:
        self.lat = float(wpt.xpath('@lat')[0])
        self.lon = float(wpt.xpath('@lon')[0])

        try:
            self.name = wpt.xpath('gpx:name/text()', namespaces=NSMAP)[0]
        except IndexError:
            self.name = None

    def __repr__(self):
        return f'Waypoint({self.lat:.5f}, {self.lon:.5f})'


class Track(object):

    def __init__(self, trk: etree.Element, NSMAP: dict) -> None:
        self.points = [(float(point.xpath('@lat')[0]), float(point.xpath('@lon')[0]))
                       for point in trk.xpath('gpx:trkseg/gpx:trkpt', namespaces=NSMAP)]
        self.bounds = {
            'lat_min': min(point[0] for point in self.points),
            'lon_min': min(point[1] for point in self.points),
            'lat_max': max(point[0] for point in self.points),
            'lon_max': max(point[1] for point in self.points)
        }

        try:
            self.name = trk.xpath('gpx:name/text()', namespaces=NSMAP)[0]
        except IndexError:
            self.name = None

    def __repr__(self):
        return f'Track(({self.bounds["lat_min"]:.5f}, {self.bounds["lon_min"]:.5f}), ({self.bounds["lat_max"]:.5f}, {self.bounds["lon_max"]:.5f}))'


class GPX(object):

    def __init__(self, gpx_file: str, track_color: str = TRACK_COLOR_DEFAULT, waypoint_color: str = WAYPOINT_COLOR_DEFAULT) -> None:
        self._gpx_file = Path(gpx_file)
        self._track_color = track_color
        self._waypoint_color = waypoint_color

        self.name = self._gpx_file.stem
        self.waypoints = []
        self.tracks = []
        self.bounds = None
        self.center = None

        self._parse()

    def _parse(self) -> None:
        # parse the gpx file
        tree = etree.parse(str(self._gpx_file))  # lxml doesn't support pathlib.Path objects (yet)
        root = tree.getroot()

        # get the NSMAP
        NSMAP = {'gpx': v for k, v in root.nsmap.items() if not k}

        # get the waypoints
        wpts = root.xpath('//gpx:wpt', namespaces=NSMAP)
        for wpt in wpts:
            self.waypoints.append(Waypoint(wpt, NSMAP))

        # get the tracks
        trks = root.xpath('//gpx:trk', namespaces=NSMAP)
        for trk in trks:
            self.tracks.append(Track(trk, NSMAP))

        # compute the bounds
        self.bounds = {
            'lat_min': min([trk.bounds['lat_min'] for trk in self.tracks] + [wpt.lat for wpt in self.waypoints]),
            'lon_min': min([trk.bounds['lon_min'] for trk in self.tracks] + [wpt.lon for wpt in self.waypoints]),
            'lat_max': max([trk.bounds['lat_max'] for trk in self.tracks] + [wpt.lat for wpt in self.waypoints]),
            'lon_max': max([trk.bounds['lon_max'] for trk in self.tracks] + [wpt.lon for wpt in self.waypoints])
        }

        # compute the center coordinates
        self.center = (
            (self.bounds['lat_max'] - self.bounds['lat_min']) / 2 + self.bounds['lat_min'],
            (self.bounds['lon_max'] - self.bounds['lon_min']) / 2 + self.bounds['lon_min']
        )

    def render_tracks(self, image: Image, center_coord: Tuple[int, int], zoom: int, dpi: int = 300, tile_size: int = 256, antialias: int = 4, width: int = 5):
        im_width, im_height = image.size
        antialias_width = im_width * antialias
        antialias_height = im_height * antialias
        im_x_center, im_y_center = center_coord

        lines_image = Image.new('RGBA', (antialias_width, antialias_height), (255, 0, 0, 0))
        draw = ImageDraw.Draw(lines_image)

        # render the tracks
        for track in self.tracks:
            points_px = [(x_to_px(lon_to_x(point[1], zoom), im_x_center, image.width, tile_size) * antialias, y_to_px(
                lat_to_y(point[0], zoom), im_y_center, image.height, tile_size) * antialias) for point in track.points]
            draw.line(points_px, fill=self._track_color, width=width * antialias, joint='curve')

        # resize the lines_image
        del draw
        lines_image = lines_image.resize((im_width, im_height), Image.ANTIALIAS)

        # paste the lines_image onto the base image
        image.paste(lines_image, (0, 0), lines_image)

    def render_waypoints(self, image: Image, center_coord: Tuple[int, int], zoom: int, dpi: int = 300, tile_size: int = 256, antialias: int = 4, width: int = 50):
        im_x_center, im_y_center = center_coord

        map_marker_im = Image.open(MAP_MARKER_FILE)
        convert_color(map_marker_im, self._waypoint_color)
        map_marker_im = map_marker_im.resize(
            (width, round(map_marker_im.height * width / map_marker_im.width)), Image.ANTIALIAS)

        # render the waypoints
        for waypoint in self.waypoints:
            point_px = (x_to_px(lon_to_x(waypoint.lon, zoom), im_x_center, image.width, tile_size),
                        y_to_px(lat_to_y(waypoint.lat, zoom), im_y_center, image.height, tile_size))
            box = (
                round(point_px[0] - map_marker_im.width / 2),
                round(point_px[1] - map_marker_im.height)
            )

            # paste the map_marker_im onto the base image
            image.paste(map_marker_im, box, map_marker_im)

    def __repr__(self):
        return f'GPX({self.name})'
