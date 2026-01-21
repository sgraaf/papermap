"""Tests for the geodesy module."""

import math

import pytest

from papermap.geodesy import (
    WGS_84_ELLIPSOID,
    ECEFCoordinate,
    Ellipsoid,
    LatLonCoordinate,
    MGRSCoordinate,
    UTMCoordinate,
    _parse_utm_string,
    ecef_to_latlon,
    format_ecef,
    format_mgrs,
    format_utm,
    latlon_to_ecef,
    latlon_to_mgrs,
    latlon_to_utm,
    mgrs_to_latlon,
    utm_to_latlon,
    wrap_angle,
    wrap_lat,
    wrap_lon,
)


class TestEllipsoid:
    def test_wgs84_semi_major_axis(self) -> None:
        assert WGS_84_ELLIPSOID.semi_major_axis == 6_378_137.0

    def test_wgs84_flattening(self) -> None:
        assert math.isclose(WGS_84_ELLIPSOID.flattening, 1 / 298.257223563)

    def test_wgs84_semi_minor_axis(self) -> None:
        # Semi-minor axis should be calculated from semi-major axis and flattening
        expected = 6_378_137.0 * (1 - 1 / 298.257223563)
        assert math.isclose(WGS_84_ELLIPSOID.semi_minor_axis, expected)
        assert math.isclose(WGS_84_ELLIPSOID.semi_minor_axis, 6356752.314245, abs_tol=1)

    def test_custom_ellipsoid(self) -> None:
        # Create a custom ellipsoid (GRS80)
        grs80 = Ellipsoid(semi_major_axis=6_378_137.0, flattening=1 / 298.257222101)
        assert grs80.semi_major_axis == 6_378_137.0
        assert math.isclose(grs80.flattening, 1 / 298.257222101)
        assert math.isclose(grs80.semi_minor_axis, 6356752.314140, abs_tol=1)

    def test_sphere(self) -> None:
        # Test with a perfect sphere (flattening = 0)
        sphere = Ellipsoid(semi_major_axis=6_371_000.0, flattening=0.0)
        assert sphere.semi_major_axis == 6_371_000.0
        assert sphere.flattening == 0.0
        assert sphere.semi_minor_axis == 6_371_000.0  # Same as semi-major for a sphere

    def test_ellipsoid_immutable(self) -> None:
        # Ellipsoid should be frozen (immutable)
        with pytest.raises(AttributeError):
            WGS_84_ELLIPSOID.semi_major_axis = 1000  # type: ignore[misc]


class TestEllipsoidParameter:
    def test_latlon_to_utm_with_custom_ellipsoid(self) -> None:
        # Use GRS80 ellipsoid (very similar to WGS84, but slightly different)
        grs80 = Ellipsoid(semi_major_axis=6_378_137.0, flattening=1 / 298.257222101)

        # Convert using both ellipsoids
        lat, lon = 40.7128, -74.0060
        utm_wgs84 = latlon_to_utm(lat, lon)  # Default WGS84
        utm_grs80 = latlon_to_utm(lat, lon, ellipsoid=grs80)

        # Both should have same zone and hemisphere
        assert utm_wgs84.zone == utm_grs80.zone
        assert utm_wgs84.hemisphere == utm_grs80.hemisphere

        # Coordinates should be very close but not identical
        assert math.isclose(utm_wgs84.easting, utm_grs80.easting, abs_tol=1)
        assert math.isclose(utm_wgs84.northing, utm_grs80.northing, abs_tol=1)

    def test_utm_to_latlon_with_custom_ellipsoid(self) -> None:
        # Test roundtrip with custom ellipsoid
        grs80 = Ellipsoid(semi_major_axis=6_378_137.0, flattening=1 / 298.257222101)
        lat, lon = 40.7128, -74.0060

        utm = latlon_to_utm(lat, lon, ellipsoid=grs80)
        lat2, lon2, _ = utm_to_latlon(utm, ellipsoid=grs80)

        assert math.isclose(lat, lat2, abs_tol=1e-6)
        assert math.isclose(lon, lon2, abs_tol=1e-6)

    def test_latlon_to_mgrs_with_custom_ellipsoid(self) -> None:
        # Test MGRS with custom ellipsoid
        grs80 = Ellipsoid(semi_major_axis=6_378_137.0, flattening=1 / 298.257222101)
        lat, lon = 40.7128, -74.0060

        mgrs_wgs84 = latlon_to_mgrs(lat, lon)
        mgrs_grs80 = latlon_to_mgrs(lat, lon, ellipsoid=grs80)

        # Zone and band should be the same
        assert mgrs_wgs84.zone == mgrs_grs80.zone
        assert mgrs_wgs84.band == mgrs_grs80.band
        assert mgrs_wgs84.square == mgrs_grs80.square

    def test_latlon_to_ecef_with_custom_ellipsoid(self) -> None:
        # Test ECEF conversion with a noticeably different ellipsoid
        # Use a sphere for easier verification
        sphere = Ellipsoid(semi_major_axis=6_371_000.0, flattening=0.0)

        # At equator, prime meridian on a sphere
        ecef = latlon_to_ecef(0, 0, ellipsoid=sphere)
        assert math.isclose(ecef.x, 6_371_000.0, abs_tol=1)
        assert math.isclose(ecef.y, 0, abs_tol=1)
        assert math.isclose(ecef.z, 0, abs_tol=1)

    def test_ecef_to_latlon_with_custom_ellipsoid(self) -> None:
        # Test ECEF roundtrip with custom ellipsoid
        sphere = Ellipsoid(semi_major_axis=6_371_000.0, flattening=0.0)

        lat, lon, height = 45, 45, 0
        ecef = latlon_to_ecef(lat, lon, height=height, ellipsoid=sphere)
        lat2, lon2, h2 = ecef_to_latlon(ecef, ellipsoid=sphere)

        assert math.isclose(lat, lat2, abs_tol=1e-6)
        assert math.isclose(lon, lon2, abs_tol=1e-6)
        assert h2 is not None
        assert math.isclose(height, h2, abs_tol=0.01)

    def test_mgrs_to_latlon_with_custom_ellipsoid(self) -> None:
        # Test MGRS roundtrip with custom ellipsoid
        grs80 = Ellipsoid(semi_major_axis=6_378_137.0, flattening=1 / 298.257222101)
        lat, lon = 40.7128, -74.0060

        mgrs = latlon_to_mgrs(lat, lon, ellipsoid=grs80)
        lat2, lon2, _ = mgrs_to_latlon(mgrs, ellipsoid=grs80)

        # MGRS has 1-meter precision
        assert math.isclose(lat, lat2, abs_tol=0.0001)
        assert math.isclose(lon, lon2, abs_tol=0.0001)


class TestWrapAngle:
    """Tests for the wrap function."""

    def test_wrap_angle_value_within_range(self) -> None:
        assert wrap_angle(45, 90) == 45

    def test_wrap_angle_value_at_positive_limit(self) -> None:
        assert wrap_angle(90, 90) == 90

    def test_wrap_angle_value_at_negative_limit(self) -> None:
        assert wrap_angle(-90, 90) == -90

    def test_wrap_angle_value_exceeds_positive_limit(self) -> None:
        assert wrap_angle(100, 90) == -80

    def test_wrap_angle_value_exceeds_negative_limit(self) -> None:
        assert wrap_angle(-100, 90) == 80

    def test_wrap_angle_full_rotation(self) -> None:
        assert wrap_angle(270, 90) == -90

    def test_wrap_angle_multiple_rotations(self) -> None:
        assert math.isclose(wrap_angle(450, 90), -90, abs_tol=1e-9)


class TestWrapLat:
    """Tests for the wrap_lat function."""

    def test_wrap_lat_within_range(self) -> None:
        assert wrap_lat(45) == 45

    def test_wrap_lat_at_boundary(self) -> None:
        assert wrap_lat(90) == 90
        assert wrap_lat(-90) == -90

    def test_wrap_lat_exceeds_range(self) -> None:
        assert wrap_lat(100) == -80

    def test_wrap_lat_negative_exceeds_range(self) -> None:
        assert wrap_lat(-100) == 80


class TestWrapLon:
    """Tests for the wrap_lon function."""

    def test_wrap_lon_within_range(self) -> None:
        assert wrap_lon(90) == 90

    def test_wrap_lon_at_boundary(self) -> None:
        assert wrap_lon(180) == 180
        assert wrap_lon(-180) == -180

    def test_wrap_lon_exceeds_range(self) -> None:
        assert wrap_lon(200) == -160

    def test_wrap_lon_negative_exceeds_range(self) -> None:
        assert wrap_lon(-200) == 160

    def test_wrap_lon_full_rotation(self) -> None:
        assert wrap_lon(360) == 0


class TestLatLonToUTM:
    def test_new_york_city(self) -> None:
        # New York City: 40.7128°N, 74.0060°W
        utm = latlon_to_utm(40.7128, -74.0060)
        assert utm.zone == 18
        assert utm.hemisphere == "N"
        # Verify easting is in a reasonable range for NYC
        assert 580_000 < utm.easting < 590_000
        assert 4_500_000 < utm.northing < 4_510_000

    def test_sydney(self) -> None:
        # Sydney: 33.8688°S, 151.2093°E
        utm = latlon_to_utm(-33.8688, 151.2093)
        assert utm.zone == 56
        assert utm.hemisphere == "S"
        # Verify coordinates are in a reasonable range for Sydney
        assert 330_000 < utm.easting < 340_000
        assert 6_245_000 < utm.northing < 6_255_000

    def test_london(self) -> None:
        # London: 51.5074°N, 0.1278°W
        utm = latlon_to_utm(51.5074, -0.1278)
        assert utm.zone == 30
        assert utm.hemisphere == "N"
        # Verify coordinates are in a reasonable range for London
        assert 695_000 < utm.easting < 705_000
        assert 5_705_000 < utm.northing < 5_715_000

    def test_equator_prime_meridian(self) -> None:
        # Origin: Equator at Prime Meridian (Gulf of Guinea)
        utm = latlon_to_utm(0, 0)
        assert utm.zone == 31
        assert utm.hemisphere == "N"
        assert math.isclose(utm.easting, 166021, abs_tol=1)
        assert math.isclose(utm.northing, 0, abs_tol=1)

    def test_southern_hemisphere(self) -> None:
        # Rio de Janeiro: 22.9068°S, 43.1729°W
        utm = latlon_to_utm(-22.9068, -43.1729)
        assert utm.zone == 23
        assert utm.hemisphere == "S"
        # Northing should have false northing applied
        assert utm.northing > 7_000_000

    def test_norway_exception_zone_32(self) -> None:
        # Point in Norway that would normally be zone 31 but is zone 32
        # Oslo: 59.9139°N, 10.7522°E (zone 32)
        utm = latlon_to_utm(59.9139, 10.7522)
        assert utm.zone == 32

    def test_norway_exception_boundary(self) -> None:
        # Point at 60°N, 5°E should be in zone 32 (Norway exception)
        utm = latlon_to_utm(60, 5)
        assert utm.zone == 32

    def test_svalbard_exception(self) -> None:
        # Svalbard: 78.2°N, 15.6°E should be in zone 33
        utm = latlon_to_utm(78.2, 15.6)
        assert utm.zone == 33

    def test_latitude_out_of_range_north(self) -> None:
        with pytest.raises(ValueError, match="outside UTM coverage"):
            latlon_to_utm(85, 0)

    def test_latitude_out_of_range_south(self) -> None:
        with pytest.raises(ValueError, match="outside UTM coverage"):
            latlon_to_utm(-81, 0)

    def test_boundary_latitude_north(self) -> None:
        # 84°N is the northern limit
        utm = latlon_to_utm(84, 0)
        assert utm.hemisphere == "N"

    def test_boundary_latitude_south(self) -> None:
        # 80°S is the southern limit
        utm = latlon_to_utm(-80, 0)
        assert utm.hemisphere == "S"

    def test_utm_coordinate_format(self) -> None:
        utm = UTMCoordinate(583960, 4507523, 18, "N")
        assert format_utm(utm) == "18N 583960E 4507523N"


class TestUTMToLatLon:
    def test_new_york_city(self) -> None:
        # First convert lat/lon to UTM, then convert back
        original_lat, original_lon = 40.7128, -74.0060
        utm = latlon_to_utm(original_lat, original_lon)
        lat, lon, _ = utm_to_latlon(utm)
        assert math.isclose(lat, original_lat, abs_tol=0.0001)
        assert math.isclose(lon, original_lon, abs_tol=0.0001)

    def test_sydney(self) -> None:
        # First convert lat/lon to UTM, then convert back
        original_lat, original_lon = -33.8688, 151.2093
        utm = latlon_to_utm(original_lat, original_lon)
        lat, lon, _ = utm_to_latlon(utm)
        assert math.isclose(lat, original_lat, abs_tol=0.0001)
        assert math.isclose(lon, original_lon, abs_tol=0.0001)

    def test_london(self) -> None:
        # First convert lat/lon to UTM, then convert back
        original_lat, original_lon = 51.5074, -0.1278
        utm = latlon_to_utm(original_lat, original_lon)
        lat, lon, _ = utm_to_latlon(utm)
        assert math.isclose(lat, original_lat, abs_tol=0.0001)
        assert math.isclose(lon, original_lon, abs_tol=0.0001)

    def test_equator(self) -> None:
        utm = UTMCoordinate(166021, 0, 31, "N")
        lat, lon, _ = utm_to_latlon(utm)
        assert math.isclose(lat, 0, abs_tol=0.0001)
        assert math.isclose(lon, 0, abs_tol=0.0001)

    def test_roundtrip_accuracy(self) -> None:
        # Test that latlon -> utm -> latlon gives back original coordinates
        test_points = [
            (40.7128, -74.0060),  # New York
            (-33.8688, 151.2093),  # Sydney
            (35.6762, 139.6503),  # Tokyo
            (48.8566, 2.3522),  # Paris
            (-22.9068, -43.1729),  # Rio
            (55.7558, 37.6173),  # Moscow
        ]
        for lat, lon in test_points:
            utm = latlon_to_utm(lat, lon)
            lat2, lon2, _ = utm_to_latlon(utm)
            assert math.isclose(lat, lat2, abs_tol=1e-6)
            assert math.isclose(lon, lon2, abs_tol=1e-6)


class TestParseUTMString:
    """Tests for _parse_utm_string helper function."""

    def test_parse_standard_format(self) -> None:
        """Test parsing standard UTM format with E/N suffixes."""
        utm = _parse_utm_string("18N 583960E 4507523N")
        assert utm.zone == 18
        assert utm.hemisphere == "N"
        assert utm.easting == 583960
        assert utm.northing == 4507523

    def test_parse_without_suffixes(self) -> None:
        """Test parsing without E/N suffixes."""
        utm = _parse_utm_string("18N 583960 4507523")
        assert utm.zone == 18
        assert utm.hemisphere == "N"
        assert utm.easting == 583960
        assert utm.northing == 4507523

    def test_parse_lowercase(self) -> None:
        """Test that lowercase input is handled correctly."""
        utm = _parse_utm_string("18n 583960e 4507523n")
        assert utm.zone == 18
        assert utm.hemisphere == "N"
        assert utm.easting == 583960
        assert utm.northing == 4507523

    def test_parse_with_extra_spaces(self) -> None:
        """Test parsing with extra whitespace."""
        utm = _parse_utm_string("  18  N  583960  E  4507523  N  ")
        assert utm.zone == 18
        assert utm.hemisphere == "N"
        assert utm.easting == 583960
        assert utm.northing == 4507523

    def test_parse_separate_hemisphere(self) -> None:
        """Test parsing with separate hemisphere letter."""
        utm = _parse_utm_string("18 N 583960E 4507523N")
        assert utm.zone == 18
        assert utm.hemisphere == "N"
        assert utm.easting == 583960
        assert utm.northing == 4507523

    def test_parse_southern_hemisphere(self) -> None:
        """Test parsing Southern Hemisphere coordinates."""
        utm = _parse_utm_string("56S 334786E 6252182N")
        assert utm.zone == 56
        assert utm.hemisphere == "S"
        assert utm.easting == 334786
        assert utm.northing == 6252182

    def test_parse_with_decimals(self) -> None:
        """Test parsing coordinates with decimal values."""
        utm = _parse_utm_string("18N 583960.5E 4507523.7N")
        assert utm.zone == 18
        assert utm.hemisphere == "N"
        assert math.isclose(utm.easting, 583960.5)
        assert math.isclose(utm.northing, 4507523.7)

    def test_parse_single_digit_zone(self) -> None:
        """Test parsing single-digit zone number."""
        utm = _parse_utm_string("5N 500000E 5000000N")
        assert utm.zone == 5
        assert utm.hemisphere == "N"

    def test_parse_two_digit_zone(self) -> None:
        """Test parsing two-digit zone number."""
        utm = _parse_utm_string("32N 500000E 5000000N")
        assert utm.zone == 32
        assert utm.hemisphere == "N"

    def test_parse_invalid_too_short(self) -> None:
        """Test that string with missing parts raises ValueError."""
        with pytest.raises(ValueError, match="Invalid UTM string format"):
            _parse_utm_string("18N 583960")

    def test_parse_invalid_no_hemisphere(self) -> None:
        """Test that missing hemisphere raises ValueError."""
        with pytest.raises(ValueError, match="missing hemisphere"):
            _parse_utm_string("18 583960E 4507523N")

    def test_parse_invalid_zone_too_low(self) -> None:
        """Test that zone < 1 raises ValueError."""
        with pytest.raises(ValueError, match="Zone must be 1-60"):
            _parse_utm_string("0N 583960E 4507523N")

    def test_parse_invalid_zone_too_high(self) -> None:
        """Test that zone > 60 raises ValueError."""
        with pytest.raises(ValueError, match="Zone must be 1-60"):
            _parse_utm_string("61N 583960E 4507523N")

    def test_parse_invalid_zone_non_numeric(self) -> None:
        """Test that non-numeric zone raises ValueError."""
        with pytest.raises(ValueError, match="Invalid zone"):
            _parse_utm_string("XXN 583960E 4507523N")

    def test_parse_invalid_easting_non_numeric(self) -> None:
        """Test that non-numeric easting raises ValueError."""
        with pytest.raises(ValueError, match="Invalid coordinates"):
            _parse_utm_string("18N ABCE 4507523N")

    def test_parse_invalid_northing_non_numeric(self) -> None:
        """Test that non-numeric northing raises ValueError."""
        with pytest.raises(ValueError, match="Invalid coordinates"):
            _parse_utm_string("18N 583960E ABCN")

    def test_parse_invalid_easting_out_of_range(self) -> None:
        """Test that easting out of valid range raises ValueError."""
        with pytest.raises(ValueError, match=r"Easting must be.*northing"):
            _parse_utm_string("18N 1500000E 4507523N")

    def test_parse_invalid_northing_out_of_range(self) -> None:
        """Test that northing out of valid range raises ValueError."""
        with pytest.raises(ValueError, match=r"Easting must be.*northing"):
            _parse_utm_string("18N 583960E 11000000N")

    def test_roundtrip_with_format(self) -> None:
        """Test that format_utm output can be parsed back."""
        original = UTMCoordinate(583960, 4507523, 18, "N")
        formatted = format_utm(original)
        parsed = _parse_utm_string(formatted)
        assert parsed.zone == original.zone
        assert parsed.hemisphere == original.hemisphere
        assert math.isclose(parsed.easting, original.easting)
        assert math.isclose(parsed.northing, original.northing)


class TestLatLonToMGRS:
    def test_new_york_city(self) -> None:
        # New York City
        mgrs = latlon_to_mgrs(40.7128, -74.0060)
        assert mgrs.zone == 18
        assert mgrs.band == "T"
        assert len(mgrs.square) == 2

    def test_sydney(self) -> None:
        # Sydney (Southern Hemisphere)
        mgrs = latlon_to_mgrs(-33.8688, 151.2093)
        assert mgrs.zone == 56
        assert mgrs.band == "H"  # H band is in Southern Hemisphere

    def test_precision_levels(self) -> None:
        mgrs = latlon_to_mgrs(40.7128, -74.0060)

        # Test different precision levels
        s1 = format_mgrs(mgrs, precision=1)  # 10km
        s2 = format_mgrs(mgrs, precision=2)  # 1km
        s3 = format_mgrs(mgrs, precision=3)  # 100m
        s4 = format_mgrs(mgrs, precision=4)  # 10m
        s5 = format_mgrs(mgrs, precision=5)  # 1m

        # Each precision adds 2 digits (1 for easting, 1 for northing)
        assert len(s1) < len(s2) < len(s3) < len(s4) < len(s5)

    def test_invalid_precision_too_low(self) -> None:
        mgrs = latlon_to_mgrs(40.7128, -74.0060)
        with pytest.raises(ValueError, match="Precision must be between 1 and 5"):
            format_mgrs(mgrs, precision=0)

    def test_invalid_precision_too_high(self) -> None:
        mgrs = latlon_to_mgrs(40.7128, -74.0060)
        with pytest.raises(ValueError, match="Precision must be between 1 and 5"):
            format_mgrs(mgrs, precision=6)

    def test_mgrs_coordinate_str(self) -> None:
        mgrs = MGRSCoordinate(18, "T", "WK", 83959, 7523)
        s = format_mgrs(mgrs)
        assert s.startswith("18T")
        assert "WK" in s

    def test_latitude_bands(self) -> None:
        # Test various latitude bands
        # Band letters are assigned based on 8-degree intervals:
        # C: -80 to -72, D: -72 to -64, ..., L: -16 to -8, M: -8 to 0
        # N: 0 to 8, P: 8 to 16, ..., T: 40 to 48, ..., X: 72 to 84
        test_cases = [
            (-75, 0, "C"),  # -80 to -72 band
            (-45, 0, "G"),  # -48 to -40 band
            (-10, 0, "L"),  # -16 to -8 band
            (10, 0, "P"),  # 8 to 16 band
            (45, 0, "T"),  # 40 to 48 band
            (75, 0, "X"),  # 72 to 84 band
        ]
        for lat, lon, expected_band in test_cases:
            mgrs = latlon_to_mgrs(lat, lon)
            assert mgrs.band == expected_band, (
                f"Expected band {expected_band} for lat {lat}"
            )


class TestMGRSToLatLon:
    def test_parse_and_convert(self) -> None:
        # Parse an MGRS string and convert to lat/lon
        lat, lon, _ = mgrs_to_latlon("18TWK8395907523")
        # Should return valid coordinates in the right general area
        assert 39 < lat < 41
        assert -75 < lon < -73

    def test_parse_with_spaces(self) -> None:
        # MGRS string with spaces should also work
        lat, _lon, _ = mgrs_to_latlon("18T WK 83959 07523")
        assert 39 < lat < 41

    def test_parse_low_precision(self) -> None:
        # Low precision MGRS
        lat, lon, _ = mgrs_to_latlon("18TWK89")
        # Should still return valid coordinates
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180

    def test_roundtrip_accuracy(self) -> None:
        # Test that latlon -> mgrs -> latlon gives back original coordinates
        test_points = [
            (40.7128, -74.0060),  # New York
            (48.8566, 2.3522),  # Paris
            (35.6762, 139.6503),  # Tokyo
        ]
        for lat, lon in test_points:
            mgrs = latlon_to_mgrs(lat, lon)
            lat2, lon2, _ = mgrs_to_latlon(mgrs)
            # MGRS has 1-meter precision at best
            assert math.isclose(lat, lat2, abs_tol=0.0001)
            assert math.isclose(lon, lon2, abs_tol=0.0001)

    def test_parse_invalid_too_short(self) -> None:
        with pytest.raises(ValueError, match="too short"):
            mgrs_to_latlon("18T")

    def test_parse_invalid_zone(self) -> None:
        with pytest.raises(ValueError, match="Zone must be"):
            mgrs_to_latlon("99TWK12345")

    def test_parse_invalid_band(self) -> None:
        with pytest.raises(ValueError, match="Invalid latitude band"):
            mgrs_to_latlon("18AWK12345")  # 'A' is not a valid band

    def test_parse_odd_digit_coords(self) -> None:
        with pytest.raises(ValueError, match="equal length"):
            mgrs_to_latlon("18TWK123")  # Odd number of coordinate digits


class TestLatLonToECEF:
    def test_equator_prime_meridian(self) -> None:
        # Point on equator at prime meridian
        ecef = latlon_to_ecef(0, 0)
        # Should be at (a, 0, 0) where a is semi-major axis
        assert math.isclose(ecef.x, 6378137, abs_tol=1)
        assert math.isclose(ecef.y, 0, abs_tol=1)
        assert math.isclose(ecef.z, 0, abs_tol=1)

    def test_equator_90_east(self) -> None:
        # Point on equator at 90°E
        ecef = latlon_to_ecef(0, 90)
        assert math.isclose(ecef.x, 0, abs_tol=1)
        assert math.isclose(ecef.y, 6378137, abs_tol=1)
        assert math.isclose(ecef.z, 0, abs_tol=1)

    def test_north_pole(self) -> None:
        # North pole
        ecef = latlon_to_ecef(90, 0)
        assert math.isclose(ecef.x, 0, abs_tol=1)
        assert math.isclose(ecef.y, 0, abs_tol=1)
        # Z should be semi-minor axis
        assert math.isclose(ecef.z, 6356752, abs_tol=1)

    def test_south_pole(self) -> None:
        # South pole
        ecef = latlon_to_ecef(-90, 0)
        assert math.isclose(ecef.x, 0, abs_tol=1)
        assert math.isclose(ecef.y, 0, abs_tol=1)
        assert math.isclose(ecef.z, -6356752, abs_tol=1)

    def test_with_height(self) -> None:
        # Point with height above ellipsoid
        ecef_ground = latlon_to_ecef(0, 0, height=0)
        ecef_elevated = latlon_to_ecef(0, 0, height=1000)
        # X should increase by approximately 1000m at equator
        assert math.isclose(ecef_elevated.x - ecef_ground.x, 1000, abs_tol=1)

    def test_negative_longitude(self) -> None:
        # Western hemisphere
        ecef = latlon_to_ecef(0, -90)
        assert math.isclose(ecef.x, 0, abs_tol=1)
        assert math.isclose(ecef.y, -6378137, abs_tol=1)

    def test_ecef_coordinate_format(self) -> None:
        ecef = ECEFCoordinate(1000.123, 2000.456, 3000.789)
        s = format_ecef(ecef)
        assert "1000.123" in s
        assert "2000.456" in s
        assert "3000.789" in s


class TestECEFToLatLon:
    def test_equator_prime_meridian(self) -> None:
        ecef = ECEFCoordinate(6378137, 0, 0)
        lat, lon, h = ecef_to_latlon(ecef)
        assert math.isclose(lat, 0, abs_tol=0.0001)
        assert math.isclose(lon, 0, abs_tol=0.0001)
        assert h is not None
        assert math.isclose(h, 0, abs_tol=1)

    def test_north_pole(self) -> None:
        ecef = ECEFCoordinate(0, 0, 6356752)
        lat, lon, _h = ecef_to_latlon(ecef)
        assert math.isclose(lat, 90, abs_tol=0.0001)
        # Longitude is undefined at pole, but should be valid
        assert -180 <= lon <= 180

    def test_south_pole(self) -> None:
        ecef = ECEFCoordinate(0, 0, -6356752)
        lat, _lon, _h = ecef_to_latlon(ecef)
        assert math.isclose(lat, -90, abs_tol=0.0001)

    def test_equator_90_east(self) -> None:
        ecef = ECEFCoordinate(0, 6378137, 0)
        lat, lon, _h = ecef_to_latlon(ecef)
        assert math.isclose(lat, 0, abs_tol=0.0001)
        assert math.isclose(lon, 90, abs_tol=0.0001)

    def test_roundtrip_accuracy(self) -> None:
        # Test that latlon -> ecef -> latlon gives back original coordinates
        test_points = [
            (0, 0, 0),
            (45, 45, 0),
            (-45, -45, 0),
            (80, 120, 1000),
            (-80, -120, 5000),
            (0, 180, 0),
            (0, -180, 0),
        ]
        for lat, lon, height in test_points:
            ecef = latlon_to_ecef(lat, lon, height=height)
            lat2, lon2, h2 = ecef_to_latlon(ecef)
            assert math.isclose(lat, lat2, abs_tol=1e-6)
            # Handle ±180° longitude equivalence
            lon_diff = abs(lon - lon2)
            assert lon_diff < 1e-6 or math.isclose(lon_diff, 360, abs_tol=1e-6)
            assert h2 is not None
            assert math.isclose(height, h2, abs_tol=0.001)

    def test_known_city_coordinates(self) -> None:
        # Test with actual city coordinates for a sanity check
        # New York City: approximately 40.7128°N, 74.0060°W
        ecef = latlon_to_ecef(40.7128, -74.0060, height=0)
        lat, lon, _h = ecef_to_latlon(ecef)
        assert math.isclose(lat, 40.7128, abs_tol=1e-4)
        assert math.isclose(lon, -74.0060, abs_tol=1e-4)


class TestNamedTuplesImmutable:
    def test_utm_coordinate_immutable(self) -> None:
        utm = UTMCoordinate(500000, 4500000, 18, "N")
        with pytest.raises(AttributeError):
            utm.easting = 600000  # type: ignore[misc]

    def test_mgrs_coordinate_immutable(self) -> None:
        mgrs = MGRSCoordinate(18, "T", "WK", 50000, 50000)
        with pytest.raises(AttributeError):
            mgrs.zone = 19  # type: ignore[misc]

    def test_ecef_coordinate_immutable(self) -> None:
        ecef = ECEFCoordinate(1000, 2000, 3000)
        with pytest.raises(AttributeError):
            ecef.x = 5000  # type: ignore[misc]

    def test_latlon_coordinate_immutable(self) -> None:
        latlon = LatLonCoordinate(40.7128, -74.0060, 0)
        with pytest.raises(AttributeError):
            latlon.lat = 45.0  # type: ignore[misc]


class TestLatLonCoordinate:
    def test_create_with_height(self) -> None:
        coord = LatLonCoordinate(40.7128, -74.0060, 100.0)
        assert coord.lat == 40.7128
        assert coord.lon == -74.0060
        assert coord.height == 100.0

    def test_create_without_height(self) -> None:
        coord = LatLonCoordinate(40.7128, -74.0060)
        assert coord.lat == 40.7128
        assert coord.lon == -74.0060
        assert coord.height is None

    def test_tuple_unpacking(self) -> None:
        coord = LatLonCoordinate(40.7128, -74.0060, 100.0)
        lat, lon, height = coord
        assert lat == 40.7128
        assert lon == -74.0060
        assert height == 100.0


class TestFormatFunctions:
    def test_format_utm(self) -> None:
        utm = UTMCoordinate(583960, 4507523, 18, "N")
        s = format_utm(utm)
        assert s == "18N 583960E 4507523N"

    def test_format_mgrs_default_precision(self) -> None:
        mgrs = MGRSCoordinate(18, "T", "WK", 83959, 7523)
        s = format_mgrs(mgrs)
        assert s == "18TWK8395907523"

    def test_format_mgrs_low_precision(self) -> None:
        mgrs = MGRSCoordinate(18, "T", "WK", 83959, 7523)
        s = format_mgrs(mgrs, precision=2)
        # Precision 2 = 1km: first 2 digits of easting (83) and northing (07)
        assert s == "18TWK8307"

    def test_format_mgrs_invalid_precision(self) -> None:
        mgrs = MGRSCoordinate(18, "T", "WK", 83959, 7523)
        with pytest.raises(ValueError, match="Precision must be between 1 and 5"):
            format_mgrs(mgrs, precision=0)

    def test_format_ecef(self) -> None:
        ecef = ECEFCoordinate(1000.5, 2000.5, 3000.5)
        s = format_ecef(ecef)
        assert s == "(1000.500, 2000.500, 3000.500)"


class TestEdgeCases:
    def test_dateline_crossing_positive(self) -> None:
        # Near the international date line (positive side)
        utm = latlon_to_utm(0, 179.9)
        lat, lon, _ = utm_to_latlon(utm)
        assert math.isclose(lat, 0, abs_tol=0.0001)
        assert math.isclose(lon, 179.9, abs_tol=0.0001)

    def test_dateline_crossing_negative(self) -> None:
        # Near the international date line (negative side)
        utm = latlon_to_utm(0, -179.9)
        lat, lon, _ = utm_to_latlon(utm)
        assert math.isclose(lat, 0, abs_tol=0.0001)
        assert math.isclose(lon, -179.9, abs_tol=0.0001)

    def test_utm_zone_1(self) -> None:
        # Zone 1 (westernmost)
        utm = latlon_to_utm(0, -177)
        assert utm.zone == 1

    def test_utm_zone_60(self) -> None:
        # Zone 60 (easternmost)
        utm = latlon_to_utm(0, 177)
        assert utm.zone == 60

    def test_very_small_height(self) -> None:
        # Test with very small but non-zero height
        ecef = latlon_to_ecef(45, 45, height=0.001)
        _lat, _lon, h = ecef_to_latlon(ecef)
        assert h is not None
        assert math.isclose(h, 0.001, abs_tol=0.01)
