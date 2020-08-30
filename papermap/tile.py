#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Tuple, Optional


class Tile(object):

    def __init__(self, x: int, y: int, z: int, bbox: Optional[Tuple[int]] = None) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.bbox = bbox
        self.image = None
        self.success = False

    def __repr__(self):
        return f'Tile({self.x}, {self.y}, {self.z})'
