#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from collections import OrderedDict
from pathlib import Path

SCALE_DEFAULT = 25000
MARGIN_DEFAULT = 12
DPI_DEFAULT = 300
NB_WORKERS_DEFAULT = os.cpu_count()
NB_RETRIES_DEFAULT = 3
TRACK_COLOR_DEFAULT = 'blue'
WAYPOINT_COLOR_DEFAULT = 'blue'

SIZES_DICT = OrderedDict(
    [
        ('A0', {'w': 841, 'h': 1189}),
        ('A1', {'w': 594, 'h': 841}),
        ('A2', {'w': 420, 'h': 594}),
        ('A3', {'w': 297, 'h': 420}),
        ('A4', {'w': 210, 'h': 297}),
        ('A5', {'w': 148, 'h': 210}),
        ('A6', {'w': 105, 'h': 148}),
        ('A7', {'w': 74, 'h': 105}),
        ('Letter', {'w': 216, 'h': 279}),
        ('Legal', {'w': 216, 'h': 356})
    ]
)
SIZES_CHOICES = list(SIZES_DICT.keys())
SIZE_DEFAULT = 'A4'

TILE_SERVERS_DICT = OrderedDict(
    [
        (
            'OpenStreetMap',
            {
                'attribution': 'Map data: © OpenStreetMap contributors',
                'url': 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 19,
            }
        ),
        (
            'OpenStreetMap Monochrome',
            {
                'attribution': 'Map data: © OpenStreetMap contributors',
                'url': 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 19,
            }
        ),
        (
            'OpenTopoMap',
            {
                'attribution': 'Map data: © OpenStreetMap contributors, SRTM. Map style: © OpenTopoMap (CC-BY-SA)',
                'url': 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 17,
            }
        ),
        (
            'Thunderforest Landscape',
            {
                'attribution': 'Map data: © OpenStreetMap contributors',
                'url': 'https://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 22,
            }
        ),
        (
            'Thunderforest Outdoors',
            {
                'attribution': 'Map data: © OpenStreetMap contributors',
                'url': 'https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 22,
            }
        ),
        (
            'Thunderforest Transport',
            {
                'attribution': 'Map data: © OpenStreetMap contributors',
                'url': 'https://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 22,
            }
        ),
        (
            'ESRI Standard',
            {
                'attribution': 'Map data: © Esri',
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}.png',
                'zoom_min': 0,
                'zoom_max': 17,
            }
        ),
        (
            'ESRI Satellite',
            {
                'attribution': 'Map data: © Esri',
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png',
                'zoom_min': 0,
                'zoom_max': 17,
            }
        ),
        (
            'ESRI Topo',
            {
                'attribution': 'Map data: © Esri',
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png',
                'zoom_min': 0,
                'zoom_max': 20,
            }
        ),
        (
            'ESRI Dark Gray',
            {
                'attribution': 'Map data: © Esri',
                'url': 'https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}.png',
                'zoom_min': 0,
                'zoom_max': 16,
            }
        ),
        (
            'ESRI Light Gray',
            {
                'attribution': 'Map data: © Esri',
                'url': 'https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}.png',
                'zoom_min': 0,
                'zoom_max': 16,
            }
        ),
        (
            'ESRI Transportation',
            {
                'attribution': 'Map data: © Esri',
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}.png',
                'zoom_min': 0,
                'zoom_max': 20,
            }
        ),
        (
            'Stamen Terrain',
            {
                'attribution': 'Map data: © OpenStreetMap contributors. Map style: © Stamen Design (CC-BY-3.0)',
                'url': 'http://{s}.tile.stamen.com/terrain/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 18,
            }
        ),
        (
            'Stamen Toner',
            {
                'attribution': 'Map data: © OpenStreetMap contributors. Map style: © Stamen Design (CC-BY-3.0)',
                'url': 'http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 18,
            }
        ),
        (
            'Stamen Toner Lite',
            {
                'attribution': 'Map data: © OpenStreetMap contributors. Map style: © Stamen Design (CC-BY-3.0)',
                'url': 'http://{s}.tile.stamen.com/toner-lite/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 18,
            }
        ),
        (
            'Komoot',
            {
                'attribution': 'Map data: © OpenStreetMap contributors',
                'url': 'http://{s}.tile.komoot.de/komoot-2/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 19,
            }
        ),
        (
            'Wikimedia',
            {
                'attribution': 'Map data: © OpenStreetMap contributors',
                'url': 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 19,
            }
        ),
        (
            'Hike & Bike',
            {
                'attribution': 'Map data: © OpenStreetMap contributors',
                'url': 'http://{s}.tiles.wmflabs.org/hikebike/{z}/{x}/{y}.png',
                'zoom_min': 0,
                'zoom_max': 20,
            }
        )
    ]
)
TILE_SERVER_CHOICES = list(TILE_SERVERS_DICT.keys())
TILE_SERVER_DEFAULT = 'OpenStreetMap'

GRID_CHOICES = ['utm', 'rd']
GRID_DEFAULT = None

MAP_MARKER_FILE = Path(__file__).resolve().parent / 'icons' / 'map_marker.png'
