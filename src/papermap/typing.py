"""Type information used throughout `papermap`."""

Degree = float
"""Angle in degrees."""

Radian = float
"""Angle in radians."""

Angle = Degree | Radian
"""Angle in either degrees or radians."""

Pixel = int
"""Number of pixels."""

DMS = tuple[int, int, float]
"""Degrees, Minutes, and Seconds (DMS)."""

Cartesian_2D = tuple[float, float]
"""Two-dimensional Cartesian (x, y) coordinates."""

Cartesian_3D = tuple[float, float, float]
"""Thee-dimensional Cartesian (x, y, z) coordinates."""

Spherical_2D = tuple[Angle, Angle]
"""Two-dimensional Spherical (lat, lon) coordinates."""

Spherical_3D = tuple[Angle, Angle, Angle]
"""Thee-dimensional Spherical (lat, lon, height) coordinates."""

UTM_Coordinate = tuple[float, float, int, str]
"""UTM coordinate (easting, northing, zone, hemisphere)."""
