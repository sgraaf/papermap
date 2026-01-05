"""Type information used throughout `papermap`."""

from typing import Tuple, Union

Degree = float
"""Angle in degrees."""

Radian = float
"""Angle in radians."""

Angle = Union[Degree, Radian]
"""Angle in either degrees or radians."""

Pixel = int
"""Number of pixels."""

DMS = Tuple[int, int, float]
"""Degrees, Minutes, and Seconds (DMS)."""

Cartesian_2D = Tuple[float, float]
"""Two-dimensional Cartesian (x, y) coordinates."""

Cartesian_3D = Tuple[float, float, float]
"""Thee-dimensional Cartesian (x, y, z) coordinates."""

Spherical_2D = Tuple[Angle, Angle]
"""Two-dimensional Spherical (lat, lon) coordinates."""

Spherical_3D = Tuple[Angle, Angle, Angle]
"""Thee-dimensional Spherical (lat, lon, height) coordinates."""

UTM_Coordinate = Tuple[float, float, int, str]
"""UTM coordinate (easting, northing, zone, hemisphere)."""
