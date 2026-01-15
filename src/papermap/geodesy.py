"""Geodesy module for coordinate conversions.

This module provides comprehensive coordinate conversion functions for working with
different geographic coordinate systems including:
- Latitude/Longitude (WGS84 spherical coordinates)
- UTM (Universal Transverse Mercator)
- MGRS (Military Grid Reference System)
- Cartesian (3D Earth-Centered Earth-Fixed coordinates)

Adapted from Chris Veness' geodesy libraries:
https://github.com/chrisveness/geodesy
"""

from math import floor

from .constants import R
from .typing import Cartesian_3D, Degree, Spherical_2D, UTM_Coordinate
from .utils import (
    cartesian_to_spherical,
    compute_central_lon,
    spherical_to_cartesian,
    spherical_to_utm,
    utm_to_spherical,
)


def latlon_to_utm(lat: Degree, lon: Degree) -> UTM_Coordinate:
    """Convert latitude/longitude coordinates to UTM coordinates.

    This function converts geographic coordinates (latitude and longitude) in the
    WGS84 datum to Universal Transverse Mercator (UTM) coordinates. UTM is a
    coordinate system that divides the Earth into 60 north-south zones, each 6°
    wide in longitude.

    The conversion uses the Transverse Mercator projection with high precision
    formulas from Karney (2011), which provide accuracy within a few nanometers.

    Args:
        lat: Latitude in decimal degrees. Must be in range [-80.0, 84.0] for
            valid UTM conversion. Positive values are North, negative are South.
        lon: Longitude in decimal degrees. Range [-180.0, 180.0].
            Positive values are East, negative are West.

    Returns:
        A tuple containing (easting, northing, zone, hemisphere):
            - easting (float): East-West position in meters within the zone.
              Range [0, ~834000] with false easting of 500000m at central meridian.
            - northing (float): North-South position in meters.
              For Northern hemisphere: meters from equator [0, ~9400000].
              For Southern hemisphere: meters from false origin (10000000m south
              of equator) [~1100000, 10000000].
            - zone (int): UTM zone number [1-60]. Each zone spans 6° of longitude.
            - hemisphere (str): Either 'N' (Northern) or 'S' (Southern hemisphere).

    Raises:
        ValueError: If latitude is outside the valid UTM range [-80.0, 84.0].

    Example:
        >>> # Convert coordinates for the Eiffel Tower
        >>> easting, northing, zone, hemisphere = latlon_to_utm(48.8584, 2.2945)
        >>> print(f"{zone}{hemisphere} {easting:.0f}m E {northing:.0f}m N")
        31N 448252m E 5411932m N

    References:
        Karney, C. F. (2011). Transverse Mercator with an accuracy of a few
        nanometers. Journal of Geodesy, 85(8), 475-485.
        https://arxiv.org/abs/1002.1417v3
    """
    # Delegate to the existing implementation in utils.py
    # This wrapper provides a more intuitive function name
    return spherical_to_utm(lat, lon)


def utm_to_latlon(
    easting: float, northing: float, zone: int, hemisphere: str
) -> Spherical_2D:
    """Convert UTM coordinates to latitude/longitude coordinates.

    This function converts Universal Transverse Mercator (UTM) coordinates back to
    geographic coordinates (latitude and longitude) in the WGS84 datum.

    The conversion uses the inverse Transverse Mercator projection with high
    precision formulas from Karney (2011).

    Args:
        easting: East-West position in meters within the UTM zone.
            Typically in range [0, ~834000], with 500000m representing the
            central meridian of the zone.
        northing: North-South position in meters.
            For Northern hemisphere: distance from equator in meters.
            For Southern hemisphere: distance from false origin (10000000m
            south of equator).
        zone: UTM zone number [1-60]. Determines which 6° longitude slice
            of the Earth this coordinate refers to.
        hemisphere: Either 'N' (Northern) or 'S' (Southern hemisphere).
            This is needed because northing values can be ambiguous without it.

    Returns:
        A tuple containing (latitude, longitude):
            - latitude (float): Latitude in decimal degrees [-80.0, 84.0].
              Positive values are North, negative are South.
            - longitude (float): Longitude in decimal degrees [-180.0, 180.0].
              Positive values are East, negative are West.

    Example:
        >>> # Convert UTM coordinates back to lat/lon
        >>> lat, lon = utm_to_latlon(448252, 5411932, 31, 'N')
        >>> print(f"Latitude: {lat:.4f}°, Longitude: {lon:.4f}°")
        Latitude: 48.8584°, Longitude: 2.2945°

    References:
        Karney, C. F. (2011). Transverse Mercator with an accuracy of a few
        nanometers. Journal of Geodesy, 85(8), 475-485.
        https://arxiv.org/abs/1002.1417v3
    """
    # Delegate to the existing implementation in utils.py
    # This wrapper provides a more intuitive function name
    return utm_to_spherical(easting, northing, zone, hemisphere)


def latlon_to_mgrs(lat: Degree, lon: Degree, precision: int = 5) -> str:
    """Convert latitude/longitude coordinates to MGRS (Military Grid Reference System) string.

    MGRS is a geocoordinate standard used by NATO militaries for locating points
    on Earth. It's an alternative way of representing UTM coordinates that uses
    a combination of letters and numbers for more compact representation.

    MGRS format: ZZ[B] [A][A] [XXXXX] [YYYYY]
    - ZZ: Grid zone (01-60, representing 6° longitude bands)
    - B: Latitude band letter (C-X, representing 8° latitude bands)
    - AA: 100km grid square identifier (two letters)
    - XXXXX: Easting within 100km square (0-5 digits based on precision)
    - YYYYY: Northing within 100km square (0-5 digits based on precision)

    Args:
        lat: Latitude in decimal degrees [-80.0, 84.0].
            Must be within valid UTM range.
        lon: Longitude in decimal degrees [-180.0, 180.0].
        precision: Number of digits for easting and northing (0-5).
            Determines the precision of the coordinate:
            - 0: 100 km precision (grid square only)
            - 1: 10 km precision
            - 2: 1 km precision
            - 3: 100 m precision
            - 4: 10 m precision
            - 5: 1 m precision (default)

    Returns:
        MGRS coordinate string with spaces between components.
        Example: "31U DQ 48251 11932" (representing a point in Paris)

    Raises:
        ValueError: If latitude is outside valid UTM/MGRS range [-80.0, 84.0],
                    or if precision is not in range [0, 5].

    Example:
        >>> # Convert Eiffel Tower coordinates to MGRS
        >>> mgrs = latlon_to_mgrs(48.8584, 2.2945)
        >>> print(mgrs)
        31U DQ 48251 11932

        >>> # Lower precision (100m)
        >>> mgrs_low = latlon_to_mgrs(48.8584, 2.2945, precision=3)
        >>> print(mgrs_low)
        31U DQ 482 119

    References:
        NGA.SIG.0012_2.0.0_UTMUPS (2014). Universal Grids and Grid Reference Systems.
        National Geospatial-Intelligence Agency.
    """
    # Validate precision (MGRS supports 0-5 digits)
    if not 0 <= precision <= 5:  # noqa: PLR2004
        msg = f"Precision must be in range [0, 5], got {precision}"
        raise ValueError(msg)

    # Step 1: Convert lat/lon to UTM coordinates
    # This gives us easting, northing, zone number, and hemisphere
    easting, northing, zone, hemisphere = latlon_to_utm(lat, lon)

    # Step 2: Determine the latitude band letter (C through X, skipping I and O)
    # Each band covers 8° of latitude, starting from 80°S
    # Special case: Band X extends to 84°N (12° instead of 8°)
    lat_bands = "CDEFGHJKLMNPQRSTUVWXX"  # X appears twice for the extended band
    # Calculate band index: 80°S is index 0, equator is index 10
    band_index = floor(lat / 8 + 10)
    # Clamp to valid range
    band_index = max(0, min(band_index, 19))
    lat_band = lat_bands[band_index]

    # Step 3: Calculate the 100km grid square identifier (two letters)
    # The grid square letters help identify position within the UTM zone

    # Column letter (East-West): cycles through the alphabet every 3 zones
    # Uses sets: A-H, J-N, P-Z (skipping I and O)
    # The pattern repeats based on zone number
    col_letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # 24 letters (no I, O)

    # Calculate column: which 100km square east-west (0-7 in most zones)
    # Remove false easting (500000m) and divide by 100km
    col = floor((easting - 500000) / 100000)

    # Column letter cycles based on zone number (starts different for each zone group)
    # Zones 1,4,7,10... start at A, zones 2,5,8,11... start at J, zones 3,6,9,12... start at S
    col_offset = ((zone - 1) % 3) * 8
    col_letter = col_letters[(col_offset + col + 8) % 24]

    # Row letter (North-South): cycles through the alphabet every 2 zones
    # Two different patterns alternate: ABCDEFGHJKLMNPQRSTUV (zones 1,3,5...)
    # and FGHJKLMNPQRSTUVABCDE (zones 2,4,6...)
    row_letters = "ABCDEFGHJKLMNPQRSTUV"  # 20 letters (no I, O)

    # Calculate row: which 100km square north-south
    # For northern hemisphere: use northing directly
    # For southern hemisphere: remove false northing (10000000m) first
    if hemisphere == "N":
        row = floor(northing / 100000) % 20
    else:
        # Southern hemisphere has false northing of 10,000,000m
        row = floor((northing - 10000000) / 100000) % 20

    # Row letter offset alternates every zone (even zones shift by 5 letters)
    row_offset = ((zone - 1) % 2) * 5
    row_letter = row_letters[(row_offset + row) % 20]

    # Step 4: Calculate the numerical position within the 100km grid square
    # The precision parameter determines how many digits we keep

    # Easting within the grid square (0-99999m)
    grid_easting = easting % 100000
    # Northing within the grid square (0-99999m)
    grid_northing = northing % 100000

    # Scale to the desired precision
    # precision=5: 1m (5 digits: 0-99999)
    # precision=4: 10m (4 digits: 0-9999)
    # precision=3: 100m (3 digits: 0-999)
    # precision=2: 1km (2 digits: 0-99)
    # precision=1: 10km (1 digit: 0-9)
    # precision=0: 100km (no digits, grid square only)
    scale = 10 ** (5 - precision)
    easting_scaled = floor(grid_easting / scale)
    northing_scaled = floor(grid_northing / scale)

    # Step 5: Format the MGRS string
    # String structure: zone(2) + band(1) + space + col(1) + row(1) + space + easting + space + northing
    if precision == 0:
        # Grid square only, no numerical coordinates
        return f"{zone:02d}{lat_band} {col_letter}{row_letter}"

    # Include numerical coordinates with the specified precision
    # Use zero-padding to maintain consistent digit count
    return (
        f"{zone:02d}{lat_band} {col_letter}{row_letter} "
        f"{easting_scaled:0{precision}d} {northing_scaled:0{precision}d}"
    )


def mgrs_to_latlon(mgrs: str) -> Spherical_2D:  # noqa: C901, PLR0912, PLR0915
    """Convert MGRS (Military Grid Reference System) string to latitude/longitude.

    Parses an MGRS coordinate string and converts it to geographic coordinates
    (latitude and longitude) in the WGS84 datum.

    MGRS strings can be in various formats:
    - With spaces: "31U DQ 48251 11932"
    - Without spaces: "31UDQ4825111932"
    - Partial precision: "31U DQ 482 119" (100m precision)
    - Grid square only: "31U DQ" (100km precision)

    Args:
        mgrs: MGRS coordinate string. Can include or omit spaces.
              Format: ZZ[Band][Col][Row][Easting][Northing]
              where easting and northing have 0-5 digits each.

    Returns:
        A tuple containing (latitude, longitude):
            - latitude (float): Latitude in decimal degrees [-80.0, 84.0].
            - longitude (float): Longitude in decimal degrees [-180.0, 180.0].

    Raises:
        ValueError: If the MGRS string is malformed or contains invalid values.

    Example:
        >>> # Parse various MGRS formats
        >>> lat, lon = mgrs_to_latlon("31U DQ 48251 11932")
        >>> print(f"Lat: {lat:.4f}°, Lon: {lon:.4f}°")
        Lat: 48.8584°, Lon: 2.2945°

        >>> # Parse without spaces
        >>> lat2, lon2 = mgrs_to_latlon("31UDQ4825111932")

        >>> # Parse lower precision (100km grid square only)
        >>> lat3, lon3 = mgrs_to_latlon("31U DQ")

    References:
        NGA.SIG.0012_2.0.0_UTMUPS (2014). Universal Grids and Grid Reference Systems.
    """
    # Step 1: Parse the MGRS string
    # Remove all spaces for easier parsing
    mgrs_clean = mgrs.replace(" ", "").strip().upper()

    # Minimum length: 5 characters (zone + band + grid square)
    if len(mgrs_clean) < 5:  # noqa: PLR2004
        msg = f"MGRS string too short: {mgrs}"
        raise ValueError(msg)

    # Extract zone number (first 2 characters, should be digits)
    try:
        zone = int(mgrs_clean[0:2])
    except ValueError:
        msg = f"Invalid zone in MGRS string: {mgrs_clean[0:2]}"
        raise ValueError(msg) from None

    # UTM has 60 zones
    if not 1 <= zone <= 60:  # noqa: PLR2004
        msg = f"Zone must be in range [1, 60], got {zone}"
        raise ValueError(msg)

    # Extract latitude band (3rd character, should be C-X, excluding I and O)
    lat_band = mgrs_clean[2]
    valid_bands = "CDEFGHJKLMNPQRSTUVWX"
    if lat_band not in valid_bands:
        msg = f"Invalid latitude band: {lat_band}"
        raise ValueError(msg)

    # Extract 100km grid square identifier (4th and 5th characters)
    if len(mgrs_clean) < 5:  # noqa: PLR2004
        msg = "MGRS string must include 100km grid square letters"
        raise ValueError(msg)

    col_letter = mgrs_clean[3]
    row_letter = mgrs_clean[4]

    # Extract numerical easting and northing (remaining digits)
    # These must be equal length (0-5 digits each)
    numerical = mgrs_clean[5:]
    num_len = len(numerical)

    # Must have even number of digits (or zero for grid square only)
    if num_len % 2 != 0:
        msg = f"Easting and northing must have equal length, got {numerical}"
        raise ValueError(msg)

    precision = num_len // 2  # Number of digits for each coordinate

    # MGRS supports maximum 5 digits precision (1 meter)
    if precision > 5:  # noqa: PLR2004
        msg = f"Precision cannot exceed 5 digits, got {precision}"
        raise ValueError(msg)

    # Step 2: Calculate easting within the 100km grid square
    # Parse the easting digits (first half)
    if precision > 0:
        easting_str = numerical[:precision]
        # Pad with zeros to get meter precision (5 digits total)
        easting_str_padded = easting_str.ljust(5, "0")
        grid_easting = float(easting_str_padded)
    else:
        # No numerical coordinates: use center of grid square (50km)
        grid_easting = 50000.0

    # Step 3: Calculate northing within the 100km grid square
    # Parse the northing digits (second half)
    if precision > 0:
        northing_str = numerical[precision:]
        # Pad with zeros to get meter precision (5 digits total)
        northing_str_padded = northing_str.ljust(5, "0")
        grid_northing = float(northing_str_padded)
    else:
        # No numerical coordinates: use center of grid square (50km)
        grid_northing = 50000.0

    # Step 4: Decode the 100km grid square identifier to get base easting/northing

    # Column letter decoding
    col_letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    try:
        col_index = col_letters.index(col_letter)
    except ValueError:
        msg = f"Invalid column letter: {col_letter}"
        raise ValueError(msg) from None

    # Account for zone offset in column letters
    col_offset = ((zone - 1) % 3) * 8
    col = (col_index - col_offset - 8) % 24

    # Row letter decoding
    row_letters = "ABCDEFGHJKLMNPQRSTUV"
    try:
        row_index = row_letters.index(row_letter)
    except ValueError:
        msg = f"Invalid row letter: {row_letter}"
        raise ValueError(msg) from None

    # Account for zone offset in row letters
    row_offset = ((zone - 1) % 2) * 5
    row = (row_index - row_offset) % 20

    # Step 5: Calculate absolute UTM coordinates

    # Base easting from 100km column + fine position within square
    # Add false easting (500000m for all UTM zones)
    easting = col * 100000 + grid_easting + 500000

    # Base northing from 100km row + fine position within square
    base_northing = row * 100000 + grid_northing

    # Step 6: Determine hemisphere and adjust northing
    # Approximate latitude from band letter to determine hemisphere
    lat_bands = "CDEFGHJKLMNPQRSTUVWXX"
    band_index = lat_bands.index(lat_band)

    # Calculate approximate latitude for the band
    # Each band is 8° wide, starting at 80°S
    approx_lat = (band_index * 8) - 80

    # Determine hemisphere from approximate latitude
    hemisphere = "N" if approx_lat >= 0 else "S"

    # Adjust northing based on hemisphere
    # Southern hemisphere uses false northing of 10,000,000m
    northing = base_northing if hemisphere == "N" else base_northing + 10000000

    # We need to handle the case where the computed northing might be in the wrong
    # 2,000,000m band. MGRS row letters repeat every 2,000,000m.
    # Adjust northing to be in the correct latitude band

    # Calculate the southern edge of the latitude band
    # Special case: band X goes from 72°N to 84°N, normal case: 8° bands
    band_south = 72 if lat_band == "X" else (band_index * 8) - 80

    # Get the central longitude of the zone
    central_lon = compute_central_lon(zone)

    # Convert the southern edge of the band to UTM to get the minimum northing
    _, min_northing, _, _ = latlon_to_utm(band_south, central_lon)

    # Adjust northing to be within the correct 2,000,000m band
    # This is necessary because row letters repeat every 2,000,000m
    while northing < min_northing - 1000000:  # Allow some margin
        northing += 2000000

    # Ensure we're not too far north either
    max_lat = band_south + (12 if lat_band == "X" else 8)
    _, max_northing, _, _ = latlon_to_utm(max_lat - 0.001, central_lon)
    while northing > max_northing + 1000000:  # Allow some margin
        northing -= 2000000

    # Step 7: Convert UTM to lat/lon
    lat, lon = utm_to_latlon(easting, northing, zone, hemisphere)

    return lat, lon


def latlon_to_cartesian(lat: Degree, lon: Degree, height: float = 0.0) -> Cartesian_3D:
    """Convert latitude/longitude coordinates to 3D Cartesian coordinates.

    Converts geographic coordinates (latitude and longitude) on the WGS84 ellipsoid
    to Earth-Centered Earth-Fixed (ECEF) Cartesian coordinates. This is useful for
    3D calculations such as computing distances, vectors, and rotations in space.

    The coordinate system places the origin at Earth's center of mass:
    - X-axis: passes through the equator at the prime meridian (0°N, 0°E)
    - Y-axis: passes through the equator at 90°E
    - Z-axis: passes through the North Pole

    Note: This is a simplified spherical Earth model. For high-precision geodetic
    applications requiring ellipsoidal calculations, a more sophisticated conversion
    would be needed that accounts for Earth's flattening.

    Args:
        lat: Latitude in decimal degrees [-90.0, 90.0].
            Positive values are North, negative are South.
        lon: Longitude in decimal degrees [-180.0, 180.0].
            Positive values are East, negative are West.
        height: Height above the ellipsoid in meters. Default is 0.0 (sea level).
            Positive values are above the ellipsoid, negative below.

    Returns:
        A tuple containing (x, y, z) coordinates in meters:
            - x (float): X-coordinate in ECEF system (meters)
            - y (float): Y-coordinate in ECEF system (meters)
            - z (float): Z-coordinate in ECEF system (meters)

    Example:
        >>> # Convert coordinates for the Eiffel Tower
        >>> x, y, z = latlon_to_cartesian(48.8584, 2.2945)
        >>> print(f"X: {x:.0f}m, Y: {y:.0f}m, Z: {z:.0f}m")
        X: 4201925m, Y: 171490m, Z: 4778880m

        >>> # With elevation (Eiffel Tower is 300m tall)
        >>> x2, y2, z2 = latlon_to_cartesian(48.8584, 2.2945, height=300)

    References:
        Adapted from Chris Veness' geodesy library:
        https://github.com/chrisveness/geodesy
    """
    # For spherical model, add height to the Earth radius
    # For a true ellipsoidal model, more complex calculations are needed
    # that account for the ellipsoid's flattening and local radius of curvature
    # WGS84 equatorial radius is imported at module level

    # Use the spherical approximation with adjusted radius
    radius = R + height

    # Delegate to the spherical conversion function
    return spherical_to_cartesian(lat, lon, r=radius)


def cartesian_to_latlon(x: float, y: float, z: float) -> Spherical_2D:
    """Convert 3D Cartesian coordinates to latitude/longitude coordinates.

    Converts Earth-Centered Earth-Fixed (ECEF) Cartesian coordinates back to
    geographic coordinates (latitude and longitude) on the WGS84 ellipsoid.

    The coordinate system has origin at Earth's center:
    - X-axis: passes through equator at prime meridian (0°N, 0°E)
    - Y-axis: passes through equator at 90°E
    - Z-axis: passes through North Pole

    Note: This is a simplified spherical Earth model. The height information is
    not preserved in the conversion (coordinates are projected onto the sphere).
    For applications requiring height, a more sophisticated ellipsoidal
    conversion would be needed.

    Args:
        x: X-coordinate in ECEF system (meters).
        y: Y-coordinate in ECEF system (meters).
        z: Z-coordinate in ECEF system (meters).

    Returns:
        A tuple containing (latitude, longitude):
            - latitude (float): Latitude in decimal degrees [-90.0, 90.0].
              Positive values are North, negative are South.
            - longitude (float): Longitude in decimal degrees [-180.0, 180.0].
              Positive values are East, negative are West.

    Example:
        >>> # Convert ECEF coordinates back to lat/lon
        >>> lat, lon = cartesian_to_latlon(4201925, 171490, 4778880)
        >>> print(f"Latitude: {lat:.4f}°, Longitude: {lon:.4f}°")
        Latitude: 48.8584°, Longitude: 2.2945°

    References:
        Adapted from Chris Veness' geodesy library:
        https://github.com/chrisveness/geodesy
    """
    # Delegate to the spherical conversion function
    # This converts the Cartesian coordinates back to spherical
    # Note: height information is lost in this conversion
    return cartesian_to_spherical(x, y, z)
