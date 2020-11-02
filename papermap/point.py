#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import isclose, radians

from .utils import destination as _destination
from .utils import distance
from .utils import final_brng as _final_brng
from .utils import initial_brng as _initial_brng
from .utils import intermediate_point as _intermediate_point
from .utils import midpoint as _midpoint
from .utils import wrap90, wrap180


class Point(object):

    def __init__(self, lat: float, lon: float) -> None:
        self._lat = wrap90(lat)
        self._lon = wrap180(lon)

        # convert to radians
        self.φ = radians(self._lat)
        self.λ = radians(self._lon)

    @property
    def lat(self) -> float:
        return self._lat

    @lat.setter
    def lat(self, val: float) -> None:
        self._lat = wrap90(val)
        self.φ = radians(self._lat)

    @property
    def lon(self) -> float:
        return self._lon

    @lon.setter
    def lon(self, val: float) -> None:
        self._lon = wrap180(val)
        self.λ = radians(self._lon)

    def __repr__(self) -> str:
        return f'Point({self.lat:.5f}, {self.lon:.5f})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return False
        return isclose(self._lat, other.lat, rel_tol=1e-6) and isclose(self._lon, other.lon, rel_tol=1e-6)

    def __ne__(self, other: object) -> bool:
        return not self == other

    def destination(self, d: int, brng: float) -> Point:
        return Point(*_destination(self._lat, self._lon, d, brng))

    def distance(self, other: object) -> float:
        if not isinstance(other, Point):
            raise ValueError(
                f'Object of type `Point` expected, but got {type(other)} instead.')
        return distance(self._lat, self._lon, other._lat, other._lon)

    def initial_brng(self, other: object) -> float:
        if not isinstance(other, Point):
            raise ValueError(
                f'Object of type `Point` expected, but got {type(other)} instead.')
        return _initial_brng(self._lat, self._lon, other._lat, other._lon)

    def final_brng(self, other: object) -> float:
        if not isinstance(other, Point):
            raise ValueError(
                f'Object of type `Point` expected, but got {type(other)} instead.')
        return _final_brng(self._lat, self._lon, other._lat, other._lon)

    def midpoint(self, other: object) -> float:
        if not isinstance(other, Point):
            raise ValueError(
                f'Object of type `Point` expected, but got {type(other)} instead.')
        return Point(*_midpoint(self._lat, self._lon, other._lat, other._lon))

    def intermediate_point(self, other: object, frac: float) -> float:
        if not isinstance(other, Point):
            raise ValueError(
                f'Object of type `Point` expected, but got {type(other)} instead.')
        return Point(*_intermediate_point(self._lat, self._lon, other._lat, other._lon, frac))
