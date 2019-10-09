#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Optional

from PIL import Image


class Tile(object):

    def __init__(self, x: int, y: int, z: int, box: Optional[List[int]] = None) -> None:
        self._x = x
        self._y = y
        self._z = z
        self._box = box
        self._image = None
        self._success = False

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, x: int) -> None:
        self._x = x

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, y: int) -> None:
        self._y = y

    @property
    def z(self) -> int:
        return self._z

    @z.setter
    def z(self, z: int) -> None:
        self._z = z

    @property
    def box(self) -> List[int]:
        return self._box

    @box.setter
    def box(self, box: List[int]) -> None:
        self._box = box

    @property
    def image(self) -> Image:
        return self._image

    @image.setter
    def image(self, image: Image) -> None:
        self._image = image

    @property
    def success(self) -> bool:
        return self._success

    @success.setter
    def success(self, success: bool) -> None:
        self._success = success

    def __repr__(self):
        return f'Tile({self._x}, {self._y}, {self._z})'
