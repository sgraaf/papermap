"""Geodesy module for coordinate conversions.

This module provides functions for converting between different coordinate systems:
- Geographic coordinates (latitude/longitude in WGS84)
- UTM (Universal Transverse Mercator) coordinates
- MGRS (Military Grid Reference System) coordinates
- ECEF (Earth-Centered, Earth-Fixed) Cartesian coordinates

The implementations are based on well-established geodetic formulas, particularly:
- Karney (2011) for high-accuracy Transverse Mercator projections
- Bowring (1985) for efficient Cartesian to geographic conversions

References:
    Karney, C. F. (2011). Transverse Mercator with an accuracy of a few nanometers.
        Journal of Geodesy, 85(8), 475-485. https://arxiv.org/abs/1002.1417v3

    Bowring, B. R. (1985). The accuracy of geodetic latitude and height equations.
        Survey Review, 28(218), 202-206.

    Veness, C. Geodesy functions. https://github.com/chrisveness/geodesy
"""

from __future__ import annotations

from dataclasses import dataclass
from math import (
    asinh,
    atan,
    atan2,
    atanh,
    cos,
    cosh,
    degrees,
    floor,
    hypot,
    radians,
    sin,
    sinh,
    sqrt,
)
from typing import NamedTuple

# =============================================================================
# Ellipsoid Dataclass
# =============================================================================


@dataclass(frozen=True, slots=True)
class Ellipsoid:
    """A reference ellipsoid for geodetic calculations.

    An ellipsoid is a mathematical model of the Earth's shape, defined by
    its semi-major axis (equatorial radius) and flattening. Different
    ellipsoids are used for different regions and applications.

    Attributes:
        semi_major_axis: Semi-major axis (equatorial radius) in meters.
            This is the distance from the Earth's center to the equator.
        flattening: Flattening factor (dimensionless). This describes how
            much the ellipsoid deviates from a perfect sphere, defined as
            f = (a - b) / a where a is the semi-major axis and b is the
            semi-minor axis. A value of 0 indicates a perfect sphere.
    """

    semi_major_axis: float
    flattening: float

    @property
    def semi_minor_axis(self) -> float:
        """Semi-minor axis (polar radius) in meters.

        This is the distance from the Earth's center to the poles,
        calculated as b = a × (1 - f).

        Returns:
            The semi-minor axis in meters.
        """
        return self.semi_major_axis * (1 - self.flattening)


# =============================================================================
# WGS84 Ellipsoid Constant
# =============================================================================
# The World Geodetic System 1984 (WGS84) is the reference coordinate system
# used by GPS and most modern mapping applications.

WGS_84_ELLIPSOID = Ellipsoid(
    semi_major_axis=6_378_137.0,
    flattening=1 / 298.257223563,
)
"""The WGS84 ellipsoid used by GPS and most modern mapping applications.

This is the default ellipsoid for all coordinate conversion functions.
"""

# =============================================================================
# UTM Constants
# =============================================================================

UTM_SCALE_FACTOR: float = 0.9996
"""UTM central meridian scale factor (dimensionless).

UTM uses a secant cylinder projection, meaning the cylinder intersects
the Earth at two lines parallel to the central meridian. This scale
factor (less than 1) reduces distortion across the zone by making the
scale exact along those secant lines rather than at the central meridian.
"""

UTM_FALSE_EASTING: float = 500_000.0
"""UTM false easting in meters.

All UTM easting values are offset by this amount to ensure they are
always positive. The central meridian of each zone has an easting of
exactly 500,000 meters.
"""

UTM_FALSE_NORTHING: float = 10_000_000.0
"""UTM false northing for the Southern Hemisphere in meters.

In the Southern Hemisphere, northing values are offset by this amount
to avoid negative coordinates. The equator has a northing of 10,000,000
meters in the Southern Hemisphere and 0 meters in the Northern.
"""

# =============================================================================
# MGRS Constants
# =============================================================================

MGRS_LATITUDE_BANDS: str = "CDEFGHJKLMNPQRSTUVWXX"
"""MGRS latitude band letters.

These letters designate 8-degree latitude bands from 80°S to 84°N.
Letters I and O are omitted to avoid confusion with digits 1 and 0.
The band 'X' is repeated because it spans 12 degrees (72°N to 84°N)
instead of the usual 8 degrees.

Band C: 80°S to 72°S
Band D: 72°S to 64°S
...
Band X: 72°N to 84°N
"""

MGRS_COLUMN_LETTERS_SET1: str = "ABCDEFGH"
"""100km column letters for UTM zones where (zone % 3) == 1."""

MGRS_COLUMN_LETTERS_SET2: str = "JKLMNPQR"
"""100km column letters for UTM zones where (zone % 3) == 2."""

MGRS_COLUMN_LETTERS_SET3: str = "STUVWXYZ"
"""100km column letters for UTM zones where (zone % 3) == 0."""

MGRS_ROW_LETTERS_ODD: str = "ABCDEFGHJKLMNPQRSTUV"
"""100km row letters for odd UTM zones (1, 3, 5, ...)."""

MGRS_ROW_LETTERS_EVEN: str = "FGHJKLMNPQRSTUVABCDE"
"""100km row letters for even UTM zones (2, 4, 6, ...).

Note how this is offset by 5 letters from the odd zone pattern.
This offset ensures that adjacent zones don't have the same row
letter at the same northing, reducing ambiguity.
"""


# =============================================================================
# Coordinate Types (NamedTuples)
# =============================================================================


class LatLonCoordinate(NamedTuple):
    """A geographic coordinate in latitude and longitude.

    Attributes:
        lat: Latitude in degrees (-90 to 90). Positive values are north of
            the equator, negative values are south.
        lon: Longitude in degrees (-180 to 180). Positive values are east of
            the Prime Meridian, negative values are west.
        height: Height above the WGS84 ellipsoid in meters. Defaults to None.
    """

    lat: float
    lon: float
    height: float | None = None


class UTMCoordinate(NamedTuple):
    """A Universal Transverse Mercator (UTM) coordinate.

    UTM divides the Earth into 60 longitudinal zones, each 6 degrees wide,
    numbered 1-60 starting from 180°W. Each zone uses a Transverse Mercator
    projection with its own central meridian.

    Attributes:
        easting: Distance east from the zone's central meridian in meters.
            The central meridian has an easting of 500,000m (false easting).
        northing: Distance north from the equator in meters. In the Southern
            Hemisphere, 10,000,000m is added (false northing) so all values
            are positive.
        zone: UTM zone number (1-60).
        hemisphere: 'N' for Northern Hemisphere, 'S' for Southern Hemisphere.
    """

    easting: float
    northing: float
    zone: int
    hemisphere: str


class MGRSCoordinate(NamedTuple):
    """A Military Grid Reference System (MGRS) coordinate.

    MGRS extends UTM by adding a two-letter 100km square identifier and
    providing a way to specify location to varying precision levels.

    Attributes:
        zone: UTM zone number (1-60).
        band: Latitude band letter (C-X, excluding I and O).
        square: Two-letter 100km grid square identifier.
        easting: Easting within the 100km square in meters (0-99999).
        northing: Northing within the 100km square in meters (0-99999).
    """

    zone: int
    band: str
    square: str
    easting: float
    northing: float


class ECEFCoordinate(NamedTuple):
    """An Earth-Centered, Earth-Fixed (ECEF) Cartesian coordinate.

    ECEF is a 3D Cartesian coordinate system with:
    - Origin at the Earth's center of mass
    - X-axis pointing towards the intersection of the Prime Meridian and Equator
    - Y-axis pointing towards 90°E longitude on the Equator
    - Z-axis pointing towards the North Pole

    Attributes:
        x: Distance along X-axis in meters.
        y: Distance along Y-axis in meters.
        z: Distance along Z-axis in meters.
    """

    x: float
    y: float
    z: float


# =============================================================================
# Coordinate Formatting Functions
# =============================================================================


def format_latlon(latlon: LatLonCoordinate, *, precision: int = 5) -> str:
    """Format a geographic coordinate in latitude and longitude as a human-readable string.

    Args:
        latlon: The geographic coordinate in latitude and longitude to format.
        precision: Number of digits for latitude/longitude (0-8).
            0=111km, 1 = 11.1km, 2 = 1.11km, 3 = 111m, 4 = 11.1m, 5 = 1.11m,
            6 = 111mm, 7 = 11.1mm, 8 = 1.11mm. Defaults to 5.

    Returns:
        A string in the format "40.7128, -74.0060".
    """
    # Validate precision
    if not 0 <= precision <= 8:
        msg = f"Precision must be between 0 and 8, got {precision}"
        raise ValueError(msg)

    return f"{latlon.lat:.{precision}f}, {latlon.lon:.{precision}f}"


def format_utm(utm: UTMCoordinate) -> str:
    """Format a UTM coordinate as a human-readable string.

    Args:
        utm: The UTM coordinate to format.

    Returns:
        A string in the format "18N 583960E 4507523N".
    """
    return f"{utm.zone}{utm.hemisphere} {utm.easting:.0f}E {utm.northing:.0f}N"


def format_mgrs(mgrs: MGRSCoordinate, *, precision: int = 5) -> str:
    """Format an MGRS coordinate as a string with specified precision.

    Args:
        mgrs: The MGRS coordinate to format.
        precision: Number of digits for easting/northing (1-5).
            1 = 10km, 2 = 1km, 3 = 100m, 4 = 10m, 5 = 1m. Defaults to 5.

    Returns:
        MGRS coordinate string at the specified precision.

    Raises:
        ValueError: If precision is not between 1 and 5.
    """
    # Validate precision
    if not 1 <= precision <= 5:
        msg = f"Precision must be between 1 and 5, got {precision}"
        raise ValueError(msg)

    # Calculate divisor to reduce precision
    # precision 5 -> divisor 1, precision 4 -> divisor 10, etc.
    divisor = 10 ** (5 - precision)

    # Truncate (not round) to the specified precision
    e = int(mgrs.easting // divisor)
    n = int(mgrs.northing // divisor)

    return f"{mgrs.zone}{mgrs.band}{mgrs.square}{e:0{precision}d}{n:0{precision}d}"


def format_ecef(ecef: ECEFCoordinate) -> str:
    """Format an ECEF coordinate as a string.

    Args:
        ecef: The ECEF coordinate to format.

    Returns:
        A string in the format "(x, y, z)".
    """
    return f"({ecef.x:.3f}, {ecef.y:.3f}, {ecef.z:.3f})"


# =============================================================================
# Helper Functions
# =============================================================================


def wrap_angle(angle: float, limit: float) -> float:
    """Wraps an angle to [-limit, limit] range.

    Args:
        angle: Angle in degrees.
        limit: Lower and upper limit in degrees.

    Returns:
        Angle wrapped to [-limit, limit] degrees range.
    """
    if -limit <= angle <= limit:  # angle already in [-limit, limit] degrees range
        return angle
    return (angle + limit) % (2 * limit) - limit


def wrap_lat(lat: float) -> float:
    """Wraps latitude to [-90, 90] degrees range.

    Args:
        lat: Latitude in degrees.

    Returns:
        Latitude wrapped to [-90, 90] degrees range.
    """
    return wrap_angle(lat, 90)


def wrap_lon(lon: float) -> float:
    """Wraps longitude to [-180, 180] degrees range.

    Args:
        lon: Longitude in degrees.

    Returns:
        Longitude wrapped to [-180, 180] degrees range.
    """
    return wrap_angle(lon, 180)


def _compute_utm_zone(lat: float, lon: float) -> int:
    """Compute the UTM zone number for a given latitude/longitude.

    The standard UTM zone formula is: zone = floor((lon + 180) / 6) + 1

    However, there are several exceptions to accommodate national mapping
    systems:

    1. Norway (zone 32V): Zone 31V is narrowed and zone 32V is widened to
       cover all of southwestern Norway with a single zone.

    2. Svalbard (zones 31X, 33X, 35X, 37X): Zones 32X, 34X, and 36X do not
       exist. The odd-numbered zones are widened to cover the entire area.

    Args:
        lat: Latitude in degrees.
        lon: Longitude in degrees.

    Returns:
        UTM zone number (1-60).
    """
    # Standard zone calculation
    zone = floor((lon + 180) / 6) + 1

    # Norway exception: zone 31V is narrowed, 32V is widened
    # This affects latitudes 56°N to 64°N and longitudes 3°E to 12°E
    if 56 <= lat < 64 and 3 <= lon < 12:
        return 32

    # Svalbard exceptions: zones 32X, 34X, 36X don't exist
    # The area from 72°N to 84°N uses only zones 31X, 33X, 35X, 37X
    if 72 <= lat <= 84 and lon >= 0:
        if lon < 9:
            return 31
        if lon < 21:
            return 33
        if lon < 33:
            return 35
        if lon < 42:
            return 37

    return zone


def _compute_central_meridian(zone: int) -> float:
    """Compute the central meridian longitude for a UTM zone.

    Each UTM zone is 6 degrees wide, and the central meridian is at the
    center of the zone. Zone 1 spans 180°W to 174°W, so its central
    meridian is at 177°W (-177°).

    The formula is: central_meridian = (zone - 1) * 6 - 180 + 3

    Args:
        zone: UTM zone number (1-60).

    Returns:
        Central meridian longitude in degrees.
    """
    return (zone - 1) * 6 - 180 + 3


def _get_latitude_band(lat: float) -> str:
    """Get the MGRS latitude band letter for a given latitude.

    Latitude bands are 8 degrees high, starting with 'C' at 80°S.
    The northernmost band 'X' is 12 degrees high (72°N to 84°N).

    Args:
        lat: Latitude in degrees.

    Returns:
        Single-character latitude band letter (C-X).

    Raises:
        ValueError: If latitude is outside the UTM/MGRS coverage area.
    """
    # Validate latitude is within UTM coverage
    if not -80 <= lat <= 84:
        msg = f"Latitude {lat} is outside UTM/MGRS coverage area [-80, 84]"
        raise ValueError(msg)

    # Special case: exactly 84°N belongs to band X
    if lat == 84:
        return "X"

    # Calculate band index: each band is 8 degrees, starting at -80
    # Band C (index 0) covers [-80, -72)
    band_index = int((lat + 80) / 8)

    return MGRS_LATITUDE_BANDS[band_index]


def _get_100km_square_column(zone: int, easting: float) -> str:
    """Get the MGRS 100km square column letter.

    The column letters cycle through three sets (A-H, J-R, S-Z) based on
    which zone group the coordinate is in (zone % 3). Within each zone,
    the letters repeat every 8 * 100km = 800km.

    Args:
        zone: UTM zone number (1-60).
        easting: UTM easting in meters.

    Returns:
        Single-character column letter.
    """
    # Determine which letter set to use based on zone
    zone_mod = zone % 3
    if zone_mod == 1:
        letters = MGRS_COLUMN_LETTERS_SET1
    elif zone_mod == 2:
        letters = MGRS_COLUMN_LETTERS_SET2
    else:
        letters = MGRS_COLUMN_LETTERS_SET3

    # Calculate column index within the 100km grid
    # Easting of 100km-199km -> index 0, 200km-299km -> index 1, etc.
    # We subtract 1 because UTM eastings start at 100km (the central
    # meridian is at 500km, and the zone edge is about 100km from the edge)
    col_index = int(easting // 100_000) - 1

    # Wrap index to stay within the 8-letter set
    col_index = col_index % 8

    return letters[col_index]


def _get_100km_square_row(zone: int, northing: float) -> str:
    """Get the MGRS 100km square row letter.

    Row letters cycle through 20 letters (A-V, excluding I and O), but
    odd and even zones use different starting points to avoid ambiguity
    at zone boundaries.

    Args:
        zone: UTM zone number (1-60).
        northing: UTM northing in meters.

    Returns:
        Single-character row letter.
    """
    # Use different letter sets for odd and even zones
    letters = MGRS_ROW_LETTERS_ODD if zone % 2 == 1 else MGRS_ROW_LETTERS_EVEN

    # Calculate row index from northing
    # The row letters cycle every 2,000km (20 rows * 100km each)
    row_index = int(northing // 100_000) % 20

    return letters[row_index]


# =============================================================================
# Coordinate Conversion Functions
# =============================================================================


def latlon_to_utm(
    lat: float,
    lon: float,
    *,
    ellipsoid: Ellipsoid = WGS_84_ELLIPSOID,
) -> UTMCoordinate:
    """Convert geographic coordinates to UTM.

    This function uses Karney's (2011) series expansion of the Transverse
    Mercator projection, which achieves sub-millimeter accuracy anywhere
    on Earth. The algorithm uses a conformal mapping via a 6th-order
    Krüger series.

    The conversion process:
    1. Determine the UTM zone (with special cases for Norway/Svalbard)
    2. Calculate the conformal latitude (τ') using the ellipsoid eccentricity
    3. Apply the forward Krüger series to get projected coordinates
    4. Scale and offset to get final UTM easting/northing

    Args:
        lat: Latitude in degrees (-80 to 84 for UTM coverage).
        lon: Longitude in degrees (-180 to 180).
        ellipsoid: Reference ellipsoid for calculations. Defaults to WGS84.

    Returns:
        UTMCoordinate with easting, northing, zone, and hemisphere.

    Raises:
        ValueError: If latitude is outside the UTM coverage area [-80, 84].

    Examples:
        >>> utm = latlon_to_utm(40.7128, -74.0060)  # New York City
        >>> print(utm)
        UTMCoordinate(easting=583959.3723240846, northing=4507350.998243322, zone=18, hemisphere='N')

        >>> utm = latlon_to_utm(-33.8688, 151.2093)  # Sydney
        >>> print(format_utm(utm))
        56S 334369E 6250948N
    """
    # -------------------------------------------------------------------------
    # Step 1: Validate and normalize input coordinates
    # -------------------------------------------------------------------------
    lat = wrap_lat(lat)
    lon = wrap_lon(lon)

    # UTM is only defined between 80°S and 84°N
    # Outside this range, the Universal Polar Stereographic (UPS) system is used
    if not -80 <= lat <= 84:
        msg = f"Latitude {lat}° is outside UTM coverage area [-80°, 84°]"
        raise ValueError(msg)

    # -------------------------------------------------------------------------
    # Step 2: Determine UTM zone and central meridian
    # -------------------------------------------------------------------------
    zone = _compute_utm_zone(lat, lon)
    central_meridian = _compute_central_meridian(zone)

    # -------------------------------------------------------------------------
    # Step 3: Convert coordinates to radians
    # -------------------------------------------------------------------------
    # φ (phi) = latitude in radians
    # λ (lambda) = longitude offset from central meridian in radians
    φ = radians(lat)
    λ = radians(lon - central_meridian)

    # -------------------------------------------------------------------------
    # Step 4: Compute ellipsoid-derived constants
    # -------------------------------------------------------------------------
    # First eccentricity: measures how much the ellipse deviates from a circle
    # e² = (a² - b²) / a² = f(2-f)
    e = sqrt(ellipsoid.flattening * (2 - ellipsoid.flattening))

    # Third flattening: an alternative parameterization useful for series
    # n = (a - b) / (a + b) = f / (2 - f)
    n = ellipsoid.flattening / (2 - ellipsoid.flattening)

    # Pre-compute powers of n for efficiency (used in Krüger series)
    n2 = n * n
    n3 = n2 * n
    n4 = n3 * n
    n5 = n4 * n
    n6 = n5 * n

    # -------------------------------------------------------------------------
    # Step 5: Compute conformal latitude τ' (tau prime)
    # -------------------------------------------------------------------------
    # The conformal latitude transforms the ellipsoidal coordinates to a
    # sphere where angles are preserved (conformal mapping).
    #
    # Karney (2011) Equations (7-9):
    # τ = tan(φ)
    # σ = sinh(e * atanh(e * τ / sqrt(1 + τ²)))
    # τ' = τ * sqrt(1 + σ²) - σ * sqrt(1 + τ²)

    τ = sin(φ) / cos(φ)  # tan(φ), but avoiding tan() for numerical stability

    # σ (sigma) is an intermediate value in the conformal transformation
    σ = sinh(e * atanh(e * τ / sqrt(1 + τ * τ)))

    # τ' (tau prime) is the conformal tangent of latitude
    τ_prime = τ * sqrt(1 + σ * σ) - σ * sqrt(1 + τ * τ)

    # -------------------------------------------------------------------------
    # Step 6: Compute initial conformal coordinates ξ' and η'
    # -------------------------------------------------------------------------
    # Karney (2011) Equation (10):
    # ξ' = atan2(τ', cos(λ))  - conformal northing parameter
    # η' = asinh(sin(λ) / sqrt(τ'² + cos²(λ)))  - conformal easting parameter

    cos_λ = cos(λ)
    sin_λ = sin(λ)

    ξ_prime = atan2(τ_prime, cos_λ)
    η_prime = asinh(sin_λ / sqrt(τ_prime * τ_prime + cos_λ * cos_λ))

    # -------------------------------------------------------------------------
    # Step 7: Compute Krüger series coefficients (α)
    # -------------------------------------------------------------------------
    # The Krüger series transforms conformal coordinates to final projected
    # coordinates. These coefficients are derived from the ellipsoid parameters.
    # Karney (2011) Equation (35):
    # Note: α[0] corresponds to α₁, α[1] to α₂, etc. (0-indexed)
    α = (
        # α₁
        n / 2
        - 2 * n2 / 3
        + 5 * n3 / 16
        + 41 * n4 / 180
        - 127 * n5 / 288
        + 7891 * n6 / 37800,
        # α₂
        13 * n2 / 48
        - 3 * n3 / 5
        + 557 * n4 / 1440
        + 281 * n5 / 630
        - 1983433 * n6 / 1935360,
        # α₃
        61 * n3 / 240 - 103 * n4 / 140 + 15061 * n5 / 26880 + 167603 * n6 / 181440,
        # α₄
        49561 * n4 / 161280 - 179 * n5 / 168 + 6601661 * n6 / 7257600,
        # α₅
        34729 * n5 / 80640 - 3418889 * n6 / 1995840,
        # α₆
        212378941 * n6 / 319334400,
    )

    # -------------------------------------------------------------------------
    # Step 8: Apply forward Krüger series to get ξ and η
    # -------------------------------------------------------------------------
    # Karney (2011) Equation (11):
    # ξ = ξ' + Σⱼ αⱼ sin(2jξ') cosh(2jη')
    # η = η' + Σⱼ αⱼ cos(2jξ') sinh(2jη')

    ξ = ξ_prime
    η = η_prime

    for j in range(1, 7):
        # Each term adds a sinusoidal correction
        # j goes 1-6, but α is 0-indexed, so we use α[j-1]
        ξ += α[j - 1] * sin(2 * j * ξ_prime) * cosh(2 * j * η_prime)
        η += α[j - 1] * cos(2 * j * ξ_prime) * sinh(2 * j * η_prime)

    # -------------------------------------------------------------------------
    # Step 9: Compute the meridian arc parameter A
    # -------------------------------------------------------------------------
    # A relates the meridian arc length to the ellipsoid parameters.
    # 2πA is the meridian arc length from equator to pole.
    # Karney (2011) Equation (14):
    # A = (a / (1 + n)) * (1 + n²/4 + n⁴/64 + n⁶/256 + ...)

    meridian_arc = (ellipsoid.semi_major_axis / (1 + n)) * (
        1 + n2 / 4 + n4 / 64 + n6 / 256
    )

    # -------------------------------------------------------------------------
    # Step 10: Compute final easting and northing
    # -------------------------------------------------------------------------
    # Karney (2011) Equation (13):
    # x = k₀ × A × η
    # y = k₀ × A × ξ
    #
    # Where k₀ = 0.9996 is the UTM scale factor

    easting = UTM_SCALE_FACTOR * meridian_arc * η
    northing = UTM_SCALE_FACTOR * meridian_arc * ξ

    # -------------------------------------------------------------------------
    # Step 11: Apply false origin offsets
    # -------------------------------------------------------------------------
    # UTM uses false origins to ensure all coordinates are positive:
    # - False easting of 500,000m is added to all eastings
    # - False northing of 10,000,000m is added in the Southern Hemisphere

    easting += UTM_FALSE_EASTING

    # Determine hemisphere and adjust northing for Southern Hemisphere
    if lat >= 0:
        hemisphere = "N"
    else:
        hemisphere = "S"
        northing += UTM_FALSE_NORTHING

    return UTMCoordinate(
        easting=easting,
        northing=northing,
        zone=zone,
        hemisphere=hemisphere,
    )


def utm_to_latlon(
    utm: UTMCoordinate,
    *,
    ellipsoid: Ellipsoid = WGS_84_ELLIPSOID,
) -> LatLonCoordinate:
    """Convert UTM coordinates to geographic coordinates.

    This function uses Karney's (2011) inverse Transverse Mercator series
    to convert UTM coordinates back to latitude/longitude with high accuracy.

    The conversion process:
    1. Remove false origins from easting/northing
    2. Compute normalized conformal coordinates
    3. Apply inverse Krüger series
    4. Iteratively solve for geodetic latitude
    5. Compute longitude from the conformal coordinates

    Args:
        utm: UTMCoordinate object containing easting, northing, zone, and hemisphere.
        ellipsoid: Reference ellipsoid for calculations. Defaults to WGS84.

    Returns:
        Tuple of (latitude, longitude) in degrees.

    Examples:
        >>> utm = UTMCoordinate(583960, 4507523, 18, "N")
        >>> latlon = utm_to_latlon(utm)
        >>> print(latlon)
        LatLonCoordinate(lat=40.714349212461954, lon=-74.00596952683831, height=None)
        >>> print(format_latlon(latlon))
        40.71435, -74.00597
    """
    # -------------------------------------------------------------------------
    # Step 1: Remove false origin offsets
    # -------------------------------------------------------------------------
    # Reverse the false origin offsets applied during forward conversion

    easting = utm.easting - UTM_FALSE_EASTING

    northing = utm.northing
    if utm.hemisphere == "S":
        northing -= UTM_FALSE_NORTHING

    # -------------------------------------------------------------------------
    # Step 2: Compute ellipsoid-derived constants
    # -------------------------------------------------------------------------
    e = sqrt(ellipsoid.flattening * (2 - ellipsoid.flattening))  # First eccentricity
    n = ellipsoid.flattening / (2 - ellipsoid.flattening)  # Third flattening

    # Pre-compute powers of n
    n2 = n * n
    n3 = n2 * n
    n4 = n3 * n
    n5 = n4 * n
    n6 = n5 * n

    # -------------------------------------------------------------------------
    # Step 3: Compute meridian arc parameter A
    # -------------------------------------------------------------------------
    # Same as forward transformation
    meridian_arc = (ellipsoid.semi_major_axis / (1 + n)) * (
        1 + n2 / 4 + n4 / 64 + n6 / 256
    )

    # -------------------------------------------------------------------------
    # Step 4: Compute normalized conformal coordinates
    # -------------------------------------------------------------------------
    # Karney (2011) Equation (15):
    # ξ = y / (k₀ × A)
    # η = x / (k₀ × A)

    ξ = northing / (UTM_SCALE_FACTOR * meridian_arc)
    η = easting / (UTM_SCALE_FACTOR * meridian_arc)

    # -------------------------------------------------------------------------
    # Step 5: Compute inverse Krüger series coefficients (β)
    # -------------------------------------------------------------------------
    # These coefficients are used for the inverse transformation.
    # Karney (2011) Equation (36):
    # Note: β[0] corresponds to β₁, β[1] to β₂, etc. (0-indexed)
    β = (
        # β₁
        n / 2
        - 2 * n2 / 3
        + 37 * n3 / 96
        - n4 / 360
        - 81 * n5 / 512
        + 96199 * n6 / 604800,
        # β₂
        n2 / 48 + n3 / 15 - 437 * n4 / 1440 + 46 * n5 / 105 - 1118711 * n6 / 3870720,
        # β₃
        17 * n3 / 480 - 37 * n4 / 840 - 209 * n5 / 4480 + 5569 * n6 / 90720,
        # β₄
        4397 * n4 / 161280 - 11 * n5 / 504 - 830251 * n6 / 7257600,
        # β₅
        4583 * n5 / 161280 - 108847 * n6 / 3991680,
        # β₆
        20648693 * n6 / 638668800,
    )

    # -------------------------------------------------------------------------
    # Step 6: Apply inverse Krüger series to get ξ' and η'
    # -------------------------------------------------------------------------
    # Karney (2011) Equation (11) (inverse form):
    # ξ' = ξ - Σⱼ βⱼ sin(2jξ) cosh(2jη)
    # η' = η - Σⱼ βⱼ cos(2jξ) sinh(2jη)

    ξ_prime = ξ
    η_prime = η

    for j in range(1, 7):
        # j goes 1-6, but β is 0-indexed, so we use β[j-1]
        ξ_prime -= β[j - 1] * sin(2 * j * ξ) * cosh(2 * j * η)
        η_prime -= β[j - 1] * cos(2 * j * ξ) * sinh(2 * j * η)

    # -------------------------------------------------------------------------
    # Step 7: Compute conformal latitude tangent τ'
    # -------------------------------------------------------------------------
    # Karney (2011) Equation (18):
    # τ' = sin(ξ') / sqrt(sinh²(η') + cos²(ξ'))

    sinh_η_prime = sinh(η_prime)
    cos_ξ_prime = cos(ξ_prime)

    τ_prime = sin(ξ_prime) / sqrt(sinh_η_prime**2 + cos_ξ_prime**2)

    # -------------------------------------------------------------------------
    # Step 8: Compute longitude from conformal coordinates
    # -------------------------------------------------------------------------
    # λ = atan2(sinh(η'), cos(ξ'))

    λ = atan2(sinh_η_prime, cos_ξ_prime)

    # -------------------------------------------------------------------------
    # Step 9: Iteratively solve for geodetic latitude τ
    # -------------------------------------------------------------------------
    # The relationship between τ' and τ is implicit, so we must iterate.
    # Karney (2011) Equations (19-21):
    #
    # We seek τ such that:
    # τ' = τ × sqrt(1 + σ²) - σ × sqrt(1 + τ²)
    # where σ = sinh(e × atanh(e × τ / sqrt(1 + τ²)))
    #
    # Newton-Raphson iteration is used with:
    # δτᵢ = (τ' - τᵢ') / sqrt(1 + τᵢ'²) × (1 + (1-e²)τᵢ²) / ((1-e²)sqrt(1 + τᵢ²))

    # Initial guess
    τ = τ_prime

    # Iteration tolerance (approximately 1 micrometer accuracy)
    tolerance = 1e-12
    max_iterations = 10

    e_squared = e * e

    for _ in range(max_iterations):
        # Compute σᵢ for current τᵢ
        sqrt_1_plus_τ_sq = sqrt(1 + τ * τ)
        σ = sinh(e * atanh(e * τ / sqrt_1_plus_τ_sq))

        # Compute τᵢ' (what τ' would be for current τᵢ)
        τ_prime_i = τ * sqrt(1 + σ * σ) - σ * sqrt_1_plus_τ_sq

        # Compute Newton-Raphson correction
        δτ = (
            (τ_prime - τ_prime_i)
            / sqrt(1 + τ_prime_i * τ_prime_i)
            * (1 + (1 - e_squared) * τ * τ)
            / ((1 - e_squared) * sqrt_1_plus_τ_sq)
        )

        τ += δτ

        # Check for convergence
        if abs(δτ) < tolerance:
            break

    # -------------------------------------------------------------------------
    # Step 10: Convert from conformal tangent to latitude
    # -------------------------------------------------------------------------
    # φ = atan(τ)
    φ = atan(τ)

    # -------------------------------------------------------------------------
    # Step 11: Convert to degrees and adjust for zone
    # -------------------------------------------------------------------------
    lat = degrees(φ)

    # Add the central meridian longitude to get the absolute longitude
    central_meridian = _compute_central_meridian(utm.zone)
    lon = degrees(λ) + central_meridian

    # Normalize longitude to [-180, 180]
    lon = wrap_lon(lon)

    return LatLonCoordinate(lat=lat, lon=lon)


def latlon_to_mgrs(
    lat: float,
    lon: float,
    *,
    ellipsoid: Ellipsoid = WGS_84_ELLIPSOID,
) -> MGRSCoordinate:
    """Convert geographic coordinates to MGRS.

    MGRS (Military Grid Reference System) is an alphanumeric version of UTM
    that provides a standardized way to express grid coordinates. It combines:
    - A Grid Zone Designator (e.g., "18T") = UTM zone + latitude band
    - A 100km Square Identifier (e.g., "WK") = two letters
    - Numerical coordinates within the square (e.g., "12345 67890")

    Args:
        lat: Latitude in degrees (-80 to 84).
        lon: Longitude in degrees (-180 to 180).
        ellipsoid: Reference ellipsoid for calculations. Defaults to WGS84.

    Returns:
        MGRSCoordinate object with zone, band, square, easting, and northing.

    Examples:
        >>> mgrs = latlon_to_mgrs(40.7128, -74.0060)
        >>> print(mgrs)
        MGRSCoordinate(zone=18, band='T', square='WL', easting=83959.37232408463, northing=7350.998243321665)

        >>> mgrs = latlon_to_mgrs(40.7128, -74.0060)
        >>> print(format_mgrs(mgrs))
        18TWL8395907350

        >>> mgrs = latlon_to_mgrs(40.7128, -74.0060, precision=3)
        >>> print(format_mgrs(mgrs, precision=3))
        18TWL839073
    """
    # -------------------------------------------------------------------------
    # Step 1: Convert lat/lon to UTM
    # -------------------------------------------------------------------------
    # MGRS is built on top of UTM, so we first need UTM coordinates
    utm = latlon_to_utm(lat, lon, ellipsoid=ellipsoid)

    # -------------------------------------------------------------------------
    # Step 2: Get the latitude band letter
    # -------------------------------------------------------------------------
    # The latitude band subdivides UTM zones into 8° bands
    band = _get_latitude_band(lat)

    # -------------------------------------------------------------------------
    # Step 3: Get the 100km square identifier
    # -------------------------------------------------------------------------
    # The 100km square is identified by a two-letter code
    column_letter = _get_100km_square_column(utm.zone, utm.easting)
    row_letter = _get_100km_square_row(utm.zone, utm.northing)
    square = column_letter + row_letter

    # -------------------------------------------------------------------------
    # Step 4: Compute coordinates within the 100km square
    # -------------------------------------------------------------------------
    # Extract the portion of easting/northing within the 100km square
    # (values 0-99999 meters)
    easting_in_square = utm.easting % 100_000
    northing_in_square = utm.northing % 100_000

    return MGRSCoordinate(
        zone=utm.zone,
        band=band,
        square=square,
        easting=easting_in_square,
        northing=northing_in_square,
    )


def mgrs_to_latlon(
    mgrs: MGRSCoordinate | str,
    *,
    ellipsoid: Ellipsoid = WGS_84_ELLIPSOID,
) -> LatLonCoordinate:
    """Convert MGRS coordinates to geographic coordinates.

    This function converts an MGRS coordinate (either as an MGRSCoordinate
    object or a string) back to latitude/longitude. The conversion involves:
    1. Parsing the MGRS components
    2. Reconstructing UTM coordinates
    3. Converting UTM to lat/lon

    Args:
        mgrs: Either an MGRSCoordinate object or an MGRS string
            (e.g., "18TWK8395907523").
        ellipsoid: Reference ellipsoid for calculations. Defaults to WGS84.

    Returns:
        Tuple of (latitude, longitude) in degrees.

    Raises:
        ValueError: If the MGRS string is malformed.

    Examples:
        >>> latlon = mgrs_to_latlon("18TWK8395907523")
        >>> print(format_latlon(latlon))
        39.81354, -74.01908

        >>> mgrs = MGRSCoordinate(18, "T", "WK", 83959, 7523)
        >>> lat, lon, _ = mgrs_to_latlon(mgrs)
        >>> print(lat, lon)
        39.81354433765199 -74.01908091495618
    """
    # -------------------------------------------------------------------------
    # Step 1: Parse MGRS string if necessary
    # -------------------------------------------------------------------------
    if isinstance(mgrs, str):
        mgrs = _parse_mgrs_string(mgrs)

    # -------------------------------------------------------------------------
    # Step 2: Determine hemisphere from latitude band
    # -------------------------------------------------------------------------
    # Bands C-M are in the Southern Hemisphere
    # Bands N-X are in the Northern Hemisphere
    # (The letter 'N' marks the equator, bands before it are south)
    hemisphere = "N" if mgrs.band >= "N" else "S"

    # -------------------------------------------------------------------------
    # Step 3: Calculate 100km easting from column letter
    # -------------------------------------------------------------------------
    # Determine which letter set is used for this zone
    zone_mod = mgrs.zone % 3
    if zone_mod == 1:
        letters = MGRS_COLUMN_LETTERS_SET1
    elif zone_mod == 2:
        letters = MGRS_COLUMN_LETTERS_SET2
    else:
        letters = MGRS_COLUMN_LETTERS_SET3

    # Find the index of the column letter
    col_index = letters.index(mgrs.square[0])

    # Convert to easting (add 1 because index 0 corresponds to 100km easting)
    easting_100km = (col_index + 1) * 100_000

    # -------------------------------------------------------------------------
    # Step 4: Calculate 100km northing from row letter
    # -------------------------------------------------------------------------
    # Use the appropriate letter set for odd/even zones
    row_letters = MGRS_ROW_LETTERS_ODD if mgrs.zone % 2 == 1 else MGRS_ROW_LETTERS_EVEN

    # Find the index of the row letter
    row_index = row_letters.index(mgrs.square[1])

    # The row letters cycle every 2,000km (20 × 100km)
    northing_100km = row_index * 100_000

    # -------------------------------------------------------------------------
    # Step 5: Determine the correct 2,000km band for the northing
    # -------------------------------------------------------------------------
    # The row letters repeat every 2,000km, so we need to figure out which
    # 2,000km band we're in based on the latitude band.

    # Get the approximate latitude for the center of this band
    band_index = MGRS_LATITUDE_BANDS.index(mgrs.band)
    band_lat_south = -80 + band_index * 8

    # Convert the southern edge of the band to UTM to get approximate northing
    if band_lat_south >= 0:
        # Northern hemisphere
        _, approx_northing, _, _ = _latlon_to_utm_components(
            band_lat_south, 0, ellipsoid=ellipsoid
        )
    else:
        # Southern hemisphere - need to account for false northing
        _, approx_northing, _, _ = _latlon_to_utm_components(
            band_lat_south, 0, ellipsoid=ellipsoid
        )
        approx_northing += UTM_FALSE_NORTHING

    # Determine which 2,000km block we're in
    base_northing = (approx_northing // 2_000_000) * 2_000_000

    # Add the 100km northing within the 2,000km block
    northing = base_northing + northing_100km

    # Adjust if we've crossed into the next 2,000km block
    # This handles cases at the boundary of latitude bands
    while northing < approx_northing - 100_000:
        northing += 2_000_000

    # -------------------------------------------------------------------------
    # Step 6: Add coordinates within 100km square
    # -------------------------------------------------------------------------
    easting = easting_100km + mgrs.easting
    northing = northing + mgrs.northing

    # Adjust for Southern Hemisphere
    if hemisphere == "S":
        northing -= UTM_FALSE_NORTHING

    # -------------------------------------------------------------------------
    # Step 7: Convert UTM to lat/lon
    # -------------------------------------------------------------------------
    utm = UTMCoordinate(
        easting=easting,
        northing=northing if hemisphere == "N" else northing + UTM_FALSE_NORTHING,
        zone=mgrs.zone,
        hemisphere=hemisphere,
    )

    return utm_to_latlon(utm, ellipsoid=ellipsoid)


def _latlon_to_utm_components(
    lat: float,
    lon: float,
    *,
    ellipsoid: Ellipsoid = WGS_84_ELLIPSOID,
) -> tuple[float, float, int, str]:
    """Helper function to get raw UTM components without creating an object.

    This is used internally for MGRS calculations where we need the raw values.

    Args:
        lat: Latitude in degrees.
        lon: Longitude in degrees.
        ellipsoid: Reference ellipsoid for calculations. Defaults to WGS84.

    Returns:
        Tuple of (easting, northing, zone, hemisphere).
    """
    utm = latlon_to_utm(lat, lon, ellipsoid=ellipsoid)
    # For southern hemisphere, remove the false northing to get raw value
    northing = utm.northing
    if utm.hemisphere == "S":
        northing -= UTM_FALSE_NORTHING
    return utm.easting, northing, utm.zone, utm.hemisphere


def _parse_mgrs_string(mgrs_str: str) -> MGRSCoordinate:
    """Parse an MGRS string into its components.

    MGRS format: ZZB SS EEEEE NNNNN
    - ZZ: Zone number (1-60)
    - B: Latitude band (C-X)
    - SS: 100km square identifier (two letters)
    - EEEEE NNNNN: Easting and northing (same length, 1-5 digits each)

    Examples of valid formats:
    - "4QFJ12345678"  (1m precision)
    - "4QFJ1234567890"  (1m precision with 5-digit coords)
    - "4Q FJ 12345 67890"  (with spaces)
    - "4QFJ"  (center of 100km square)

    Args:
        mgrs_str: MGRS string to parse.

    Returns:
        MGRSCoordinate object.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    # Remove spaces
    mgrs_str = mgrs_str.replace(" ", "").upper()

    # Minimum length is 4 (zone + band + 2-letter square)
    if len(mgrs_str) < 4:
        msg = f"MGRS string too short: {mgrs_str}"
        raise ValueError(msg)

    # Find where the numeric zone ends
    # Zone is 1-2 digits (1-60)
    zone_end = 1 if mgrs_str[1].isalpha() else 2

    try:
        zone = int(mgrs_str[:zone_end])
    except ValueError:
        msg = f"Invalid zone in MGRS string: {mgrs_str}"
        raise ValueError(msg) from None

    if not 1 <= zone <= 60:
        msg = f"Zone must be 1-60, got {zone}"
        raise ValueError(msg)

    # Band letter is next
    band = mgrs_str[zone_end]
    if band not in MGRS_LATITUDE_BANDS:
        msg = f"Invalid latitude band '{band}' in MGRS string"
        raise ValueError(msg)

    # 100km square identifier (2 letters)
    square_start = zone_end + 1
    square = mgrs_str[square_start : square_start + 2]

    if len(square) != 2 or not square.isalpha():
        msg = f"Invalid 100km square identifier in MGRS string: {mgrs_str}"
        raise ValueError(msg)

    # Remaining digits are easting and northing (equal length)
    coords = mgrs_str[square_start + 2 :]

    # Handle empty coordinates (center of 100km square)
    if not coords:
        return MGRSCoordinate(zone, band, square, 50_000, 50_000)

    # Coordinates must be even length (equal easting and northing)
    if len(coords) % 2 != 0:
        msg = f"Easting and northing must have equal length in MGRS: {mgrs_str}"
        raise ValueError(msg)

    precision = len(coords) // 2
    if precision > 5:
        msg = f"Precision too high (max 5 digits): {mgrs_str}"
        raise ValueError(msg)

    try:
        easting_digits = int(coords[:precision])
        northing_digits = int(coords[precision:])
    except ValueError:
        msg = f"Invalid coordinates in MGRS string: {mgrs_str}"
        raise ValueError(msg) from None

    # Scale to full 5-digit precision (multiply by 10^(5-precision))
    scale = 10 ** (5 - precision)
    easting = easting_digits * scale
    northing = northing_digits * scale

    return MGRSCoordinate(zone, band, square, easting, northing)


def latlon_to_ecef(
    lat: float,
    lon: float,
    *,
    height: float = 0.0,
    ellipsoid: Ellipsoid = WGS_84_ELLIPSOID,
) -> ECEFCoordinate:
    """Convert geographic coordinates to Earth-Centered, Earth-Fixed (ECEF).

    ECEF coordinates are a 3D Cartesian system with:
    - Origin at Earth's center of mass
    - X-axis pointing to the intersection of Prime Meridian and Equator
    - Y-axis pointing to 90°E on the Equator
    - Z-axis pointing to the North Pole

    The conversion accounts for the ellipsoidal shape of the Earth using
    the specified ellipsoid parameters.

    The formulas used are:
    - x = (N + h) × cos(φ) × cos(λ)
    - y = (N + h) × cos(φ) × sin(λ)
    - z = (N × (1 - e²) + h) × sin(φ)

    where:
    - N = a / sqrt(1 - e² × sin²(φ)) is the radius of curvature in the
    prime vertical (the distance from the surface to the minor axis
    along the normal to the ellipsoid)
    - a = semi-major axis
    - e = first eccentricity
    - h = height above ellipsoid
    - φ = latitude, λ = longitude

    Args:
        lat: Latitude in degrees.
        lon: Longitude in degrees.
        height: Height above the ellipsoid in meters. Defaults to 0.
        ellipsoid: Reference ellipsoid for calculations. Defaults to WGS84.

    Returns:
        ECEFCoordinate with x, y, z in meters.

    Examples:
        >>> ecef = latlon_to_ecef(0, 0)  # On equator at prime meridian
        >>> print(f"x={ecef.x:.0f}")
        x=6378137

        >>> ecef = latlon_to_ecef(90, 0)  # North Pole
        >>> print(f"z={ecef.z:.0f}")
        z=6356752
    """
    # -------------------------------------------------------------------------
    # Step 1: Convert to radians
    # -------------------------------------------------------------------------
    φ = radians(lat)  # φ = latitude
    λ = radians(lon)  # λ = longitude

    # -------------------------------------------------------------------------
    # Step 2: Compute ellipsoid parameters
    # -------------------------------------------------------------------------
    # First eccentricity squared: e² = f(2-f) = (a²-b²)/a²
    # This measures how much the ellipsoid deviates from a sphere
    e_squared = ellipsoid.flattening * (2 - ellipsoid.flattening)

    # -------------------------------------------------------------------------
    # Step 3: Compute the radius of curvature in the prime vertical (N)
    # -------------------------------------------------------------------------
    # N is the distance from a point on the ellipsoid surface to the
    # minor axis, measured along the normal to the ellipsoid.
    #
    # N = a / sqrt(1 - e² × sin²(φ))
    #
    # At the equator (φ=0), N = a (the semi-major axis)
    # At the poles (φ=±90°), N = a/sqrt(1-e²) = a²/b

    sin_φ = sin(φ)
    cos_φ = cos(φ)

    # The denominator sqrt(1 - e²×sin²φ) is always positive and ≤ 1
    prime_vertical_radius = ellipsoid.semi_major_axis / sqrt(
        1 - e_squared * sin_φ * sin_φ
    )

    # -------------------------------------------------------------------------
    # Step 4: Compute Cartesian coordinates
    # -------------------------------------------------------------------------
    # The formulas project the geodetic coordinates onto 3D space:
    #
    # x = (N + h) × cos(φ) × cos(λ)
    #     └─ distance from Z-axis, scaled by cos(λ) for X component
    #
    # y = (N + h) × cos(φ) × sin(λ)
    #     └─ distance from Z-axis, scaled by sin(λ) for Y component
    #
    # z = (N × (1 - e²) + h) × sin(φ)
    #     └─ the factor (1 - e²) accounts for the ellipsoid's flattening
    #        reducing the Z coordinate relative to a sphere

    cos_λ = cos(λ)
    sin_λ = sin(λ)

    # Distance from Z-axis (in the equatorial plane)
    rho = (prime_vertical_radius + height) * cos_φ

    x = rho * cos_λ
    y = rho * sin_λ
    z = (prime_vertical_radius * (1 - e_squared) + height) * sin_φ

    return ECEFCoordinate(x=x, y=y, z=z)


def ecef_to_latlon(
    ecef: ECEFCoordinate,
    *,
    ellipsoid: Ellipsoid = WGS_84_ELLIPSOID,
) -> LatLonCoordinate:
    """Convert ECEF coordinates to geographic coordinates.

    This function uses Bowring's (1985) iterative method, which converges
    to full precision in just 2-3 iterations for typical coordinates.

    The algorithm uses parametric latitude (β) as an intermediate step,
    which simplifies the iteration compared to direct methods.

    The process:
    1. Compute longitude directly from x and y: λ = atan2(y, x)
    2. Iteratively refine parametric latitude β
    3. Compute geodetic latitude from β
    4. Compute height from the final values

    Args:
        ecef: ECEFCoordinate with x, y, z in meters.
        ellipsoid: Reference ellipsoid for calculations. Defaults to WGS84.

    Returns:
        Tuple of (latitude, longitude, height) where:
        - latitude is in degrees (-90 to 90)
        - longitude is in degrees (-180 to 180)
        - height is above the ellipsoid in meters

    Examples:
        >>> ecef = ECEFCoordinate(6378137, 0, 0)
        >>> latlon = ecef_to_latlon(ecef)
        >>> print(latlon)
        LatLonCoordinate(lat=0.0, lon=0.0, height=0.0)
        >>> print(f"{latlon.lat:.1f}, {latlon.lon:.1f}, {latlon.height:.1f}")
        0.0, 0.0, 0.0
    """
    # -------------------------------------------------------------------------
    # Step 1: Extract ECEF components
    # -------------------------------------------------------------------------
    x = ecef.x
    y = ecef.y
    z = ecef.z

    # -------------------------------------------------------------------------
    # Step 2: Compute ellipsoid parameters
    # -------------------------------------------------------------------------
    # First eccentricity squared: e² = (a² - b²) / a²
    e_squared = ellipsoid.flattening * (2 - ellipsoid.flattening)

    # Second eccentricity squared: e'² = (a² - b²) / b²
    # This is useful for formulas involving the minor axis
    e_prime_squared = e_squared / (1 - e_squared)

    # -------------------------------------------------------------------------
    # Step 3: Compute longitude directly
    # -------------------------------------------------------------------------
    # Longitude is independent of the ellipsoid shape and can be computed
    # directly from the x and y coordinates:
    # λ = atan2(y, x)

    λ = atan2(y, x)

    # -------------------------------------------------------------------------
    # Step 4: Compute distance from the Z-axis (in equatorial plane)
    # -------------------------------------------------------------------------
    # p = sqrt(x² + y²) is the distance from the Z-axis
    # This is the "horizontal" distance from Earth's rotation axis

    p = hypot(x, y)

    # -------------------------------------------------------------------------
    # Step 5: Handle special case of points on the Z-axis
    # -------------------------------------------------------------------------
    # When p ≈ 0, we're on or very near the rotation axis (poles)
    if p < 1e-10:
        # At the pole, latitude is ±90° depending on sign of z
        lat = 90.0 if z >= 0 else -90.0
        lon = 0.0  # Longitude is undefined at poles, conventionally 0
        # Height at pole: h = |z| - b
        height = abs(z) - ellipsoid.semi_minor_axis
        return LatLonCoordinate(lat=lat, lon=lon, height=height)

    # -------------------------------------------------------------------------
    # Step 6: Initial estimate of parametric latitude
    # -------------------------------------------------------------------------
    # Parametric (or reduced) latitude β is related to geodetic latitude φ by:
    # tan(β) = (b/a) × tan(φ)
    #
    # Bowring's initial estimate:
    # tan(β₀) = (z/p) × (a/b)
    #
    # This is equivalent to assuming we're on the ellipsoid surface

    # R is the distance from Earth's center
    r = hypot(p, z)

    # Initial estimate using Bowring's approximation
    # tan(β) = (b × z) / (a × p) × (1 + e'² × b / R)
    tan_β = (
        (z / p)
        * (ellipsoid.semi_major_axis / ellipsoid.semi_minor_axis)
        * (1 + e_prime_squared * ellipsoid.semi_minor_axis / r)
    )

    # -------------------------------------------------------------------------
    # Step 7: Iteratively refine latitude using Bowring's method
    # -------------------------------------------------------------------------
    # The geodetic latitude is related to parametric latitude by:
    # tan(φ) = (z + e'² × b × sin³(β)) / (p - e² × a × cos³(β))
    #
    # And parametric latitude is updated from geodetic latitude:
    # tan(β) = (1 - f) × tan(φ) = (b/a) × tan(φ)
    #
    # This iteration converges very quickly (typically 2-3 iterations)

    tolerance = 1e-12  # About 0.006mm at Earth's surface
    max_iterations = 10

    for _ in range(max_iterations):
        # Compute sin³(β) and cos³(β) from tan(β)
        # Using: sin(β) = tan(β) / sqrt(1 + tan²(β))
        #        cos(β) = 1 / sqrt(1 + tan²(β))

        sqrt_1_plus_tan_sq = sqrt(1 + tan_β * tan_β)
        sin_β = tan_β / sqrt_1_plus_tan_sq
        cos_β = 1 / sqrt_1_plus_tan_sq

        sin_β_cubed = sin_β * sin_β * sin_β
        cos_β_cubed = cos_β * cos_β * cos_β

        # Compute geodetic latitude from parametric latitude
        # tan(φ) = (z + e'² × b × sin³β) / (p - e² × a × cos³β)
        tan_φ = (z + e_prime_squared * ellipsoid.semi_minor_axis * sin_β_cubed) / (
            p - e_squared * ellipsoid.semi_major_axis * cos_β_cubed
        )

        # Update parametric latitude
        # tan(β_new) = (b/a) × tan(φ) = (1-f) × tan(φ)
        tan_β_new = (1 - ellipsoid.flattening) * tan_φ

        # Check for convergence
        delta = abs(tan_β_new - tan_β)
        tan_β = tan_β_new

        if delta < tolerance:
            break

    # -------------------------------------------------------------------------
    # Step 8: Compute final geodetic latitude
    # -------------------------------------------------------------------------
    φ = atan(tan_φ)

    # -------------------------------------------------------------------------
    # Step 9: Compute height above ellipsoid
    # -------------------------------------------------------------------------
    # Using: h = p × cos(φ) + z × sin(φ) - a × sqrt(1 - e² × sin²(φ))
    #
    # Or equivalently:
    # h = p / cos(φ) - N
    # where N = a / sqrt(1 - e² × sin²(φ))

    sin_φ = sin(φ)
    cos_φ = cos(φ)

    # Radius of curvature in prime vertical
    prime_vertical_radius = ellipsoid.semi_major_axis / sqrt(
        1 - e_squared * sin_φ * sin_φ
    )

    # Height calculation - use the more numerically stable formula
    # depending on latitude
    if abs(φ) > radians(45):
        # Near poles, use z-based formula (cos_φ is small)
        height = z / sin_φ - prime_vertical_radius * (1 - e_squared)
    else:
        # Near equator, use p-based formula (sin_φ is small)
        height = p / cos_φ - prime_vertical_radius

    # -------------------------------------------------------------------------
    # Step 10: Convert to degrees and return
    # -------------------------------------------------------------------------
    lat = degrees(φ)
    lon = degrees(λ)

    return LatLonCoordinate(lat=lat, lon=lon, height=height)
