"""Unit tests for papermap.utils module."""

from decimal import Decimal
from math import isclose

import pytest

from papermap.utils import (
    clip,
    dd_to_dms,
    dms_to_dd,
    drange,
    get_string_formatting_arguments,
    is_out_of_bounds,
    lat_to_y,
    lon_to_x,
    mm_to_pt,
    mm_to_px,
    pt_to_mm,
    px_to_mm,
    scale_to_zoom,
    x_to_lon,
    x_to_px,
    y_to_lat,
    y_to_px,
    zoom_to_scale,
)


class TestClip:
    """Tests for the clip function."""

    def test_clip_value_within_range(self) -> None:
        assert clip(5, 0, 10) == 5

    def test_clip_value_below_range(self) -> None:
        assert clip(-5, 0, 10) == 0

    def test_clip_value_above_range(self) -> None:
        assert clip(15, 0, 10) == 10

    def test_clip_value_at_lower_bound(self) -> None:
        assert clip(0, 0, 10) == 0

    def test_clip_value_at_upper_bound(self) -> None:
        assert clip(10, 0, 10) == 10

    def test_clip_with_negative_range(self) -> None:
        assert clip(0, -10, -5) == -5

    def test_clip_with_floats(self) -> None:
        assert clip(5.5, 0.0, 10.0) == 5.5


class TestLonToX:
    """Tests for lon_to_x conversion."""

    def test_lon_to_x_at_origin(self) -> None:
        # At zoom 0, x should be 0.5 for lon=0 (center of single tile)
        assert isclose(lon_to_x(0, 0), 0.5, abs_tol=1e-9)

    def test_lon_to_x_at_minus_180(self) -> None:
        # At zoom 0, x should be 0 for lon=-180
        assert isclose(lon_to_x(-180, 0), 0, abs_tol=1e-9)

    def test_lon_to_x_at_plus_180(self) -> None:
        # At zoom 0, x should be 1 for lon=180
        assert isclose(lon_to_x(180, 0), 1, abs_tol=1e-9)

    def test_lon_to_x_at_zoom_1(self) -> None:
        # At zoom 1, there are 2 tiles, so lon=0 should give x=1
        assert isclose(lon_to_x(0, 1), 1, abs_tol=1e-9)

    def test_lon_to_x_wraps_longitude(self) -> None:
        # lon=200 should wrap to lon=-160
        result = lon_to_x(200, 0)
        expected = lon_to_x(-160, 0)
        assert isclose(result, expected, abs_tol=1e-9)


class TestXToLon:
    """Tests for x_to_lon conversion."""

    def test_x_to_lon_at_center(self) -> None:
        assert isclose(x_to_lon(0.5, 0), 0, abs_tol=1e-9)

    def test_x_to_lon_at_left_edge(self) -> None:
        assert isclose(x_to_lon(0, 0), -180, abs_tol=1e-9)

    def test_x_to_lon_at_right_edge(self) -> None:
        assert isclose(x_to_lon(1, 0), 180, abs_tol=1e-9)


class TestLonXRoundtrip:
    """Tests for lon_to_x and x_to_lon roundtrip conversion."""

    @pytest.mark.parametrize("lon", [-180, -90, -45, 0, 45, 90, 179])
    def test_lon_x_roundtrip(self, lon: float) -> None:
        for zoom in [0, 5, 10, 15]:
            x = lon_to_x(lon, zoom)
            result = x_to_lon(x, zoom)
            assert isclose(result, lon, abs_tol=1e-6)


class TestLatToY:
    """Tests for lat_to_y conversion."""

    def test_lat_to_y_at_equator(self) -> None:
        # At zoom 0, y should be 0.5 for lat=0 (center of single tile)
        assert isclose(lat_to_y(0, 0), 0.5, abs_tol=1e-9)

    def test_lat_to_y_at_zoom_1(self) -> None:
        # At zoom 1, there are 2 tiles, so lat=0 should give y=1
        assert isclose(lat_to_y(0, 1), 1, abs_tol=1e-9)

    def test_lat_to_y_north_is_smaller(self) -> None:
        # Northern latitudes should have smaller y values (top of map)
        assert lat_to_y(45, 10) < lat_to_y(0, 10)

    def test_lat_to_y_south_is_larger(self) -> None:
        # Southern latitudes should have larger y values (bottom of map)
        assert lat_to_y(-45, 10) > lat_to_y(0, 10)


class TestYToLat:
    """Tests for y_to_lat conversion."""

    def test_y_to_lat_at_center(self) -> None:
        assert isclose(y_to_lat(0.5, 0), 0, abs_tol=1e-9)


class TestLatYRoundtrip:
    """Tests for lat_to_y and y_to_lat roundtrip conversion."""

    @pytest.mark.parametrize("lat", [-85, -45, -10, 0, 10, 45, 85])
    def test_lat_y_roundtrip(self, lat: float) -> None:
        for zoom in [0, 5, 10, 15]:
            y = lat_to_y(lat, zoom)
            result = y_to_lat(y, zoom)
            assert isclose(result, lat, abs_tol=1e-6)


class TestXToPx:
    """Tests for x_to_px conversion."""

    def test_x_to_px_at_center(self) -> None:
        # When x equals x_center, pixel should be width/2
        result = x_to_px(5, 5, 1000, 256)
        assert result == 500

    def test_x_to_px_left_of_center(self) -> None:
        # When x < x_center (tile to the left), pixel is on left side
        # Formula: width/2 - (x_center - x) * tile_size = 500 - 256 = 244
        result = x_to_px(4, 5, 1000, 256)
        assert result == 244

    def test_x_to_px_right_of_center(self) -> None:
        # When x > x_center (tile to the right), pixel is on right side
        # Formula: width/2 - (x_center - x) * tile_size = 500 - (-256) = 756
        result = x_to_px(6, 5, 1000, 256)
        assert result == 756


class TestYToPx:
    """Tests for y_to_px conversion."""

    def test_y_to_px_at_center(self) -> None:
        # When y equals y_center, pixel should be height/2
        result = y_to_px(5, 5, 1000, 256)
        assert result == 500

    def test_y_to_px_above_center(self) -> None:
        # When y < y_center (tile above), pixel is on top side
        # Formula: height/2 - (y_center - y) * tile_size = 500 - 256 = 244
        result = y_to_px(4, 5, 1000, 256)
        assert result == 244

    def test_y_to_px_below_center(self) -> None:
        # When y > y_center (tile below), pixel is on bottom side
        # Formula: height/2 - (y_center - y) * tile_size = 500 - (-256) = 756
        result = y_to_px(6, 5, 1000, 256)
        assert result == 756


class TestMmToPx:
    """Tests for mm_to_px conversion."""

    def test_mm_to_px_at_300_dpi(self) -> None:
        # 25.4mm = 1 inch = 300 pixels at 300 DPI
        assert mm_to_px(25.4, 300) == 300

    def test_mm_to_px_at_72_dpi(self) -> None:
        # 25.4mm = 1 inch = 72 pixels at 72 DPI
        assert mm_to_px(25.4, 72) == 72

    def test_mm_to_px_rounds_result(self) -> None:
        # Should round to nearest integer
        result = mm_to_px(10, 300)
        assert isinstance(result, int)


class TestPxToMm:
    """Tests for px_to_mm conversion."""

    def test_px_to_mm_at_300_dpi(self) -> None:
        # 300 pixels = 1 inch = 25.4mm at 300 DPI
        assert isclose(px_to_mm(300, 300), 25.4, abs_tol=1e-9)

    def test_px_to_mm_roundtrip(self) -> None:
        # Roundtrip (with rounding)
        mm = 50.0
        px = mm_to_px(mm, 300)
        result = px_to_mm(px, 300)
        assert isclose(result, mm, abs_tol=0.1)


class TestMmToPt:
    """Tests for mm_to_pt conversion."""

    def test_mm_to_pt_one_inch(self) -> None:
        # 25.4mm = 1 inch = 72 points
        assert isclose(mm_to_pt(25.4), 72, abs_tol=1e-9)

    def test_mm_to_pt_10mm(self) -> None:
        # 10mm = 10 * 72 / 25.4 points
        expected = 10 * 72 / 25.4
        assert isclose(mm_to_pt(10), expected, abs_tol=1e-9)


class TestPtToMm:
    """Tests for pt_to_mm conversion."""

    def test_pt_to_mm_72_points(self) -> None:
        # 72 points = 1 inch = 25.4mm
        assert isclose(pt_to_mm(72), 25.4, abs_tol=1e-9)

    def test_mm_pt_roundtrip(self) -> None:
        mm = 50.0
        pt = mm_to_pt(mm)
        result = pt_to_mm(pt)
        assert isclose(result, mm, abs_tol=1e-9)


class TestDdToDms:
    """Tests for dd_to_dms conversion."""

    def test_dd_to_dms_positive(self) -> None:
        # 45.5 degrees = 45 degrees, 30 minutes, 0 seconds
        d, m, s = dd_to_dms(45.5)
        assert d == 45
        assert m == 30
        assert isclose(s, 0, abs_tol=1e-3)

    def test_dd_to_dms_negative(self) -> None:
        # -45.5 degrees = -45 degrees, 30 minutes, 0 seconds
        d, m, s = dd_to_dms(-45.5)
        assert d == -45
        assert m == 30
        assert isclose(s, 0, abs_tol=1e-3)

    def test_dd_to_dms_zero(self) -> None:
        d, m, s = dd_to_dms(0)
        assert d == 0
        assert m == 0
        assert s == 0

    def test_dd_to_dms_with_seconds(self) -> None:
        # 45.508333... degrees = 45 degrees, 30 minutes, 30 seconds
        dd = 45 + 30 / 60 + 30 / 3600
        d, m, s = dd_to_dms(dd)
        assert d == 45
        assert m == 30
        assert isclose(s, 30, abs_tol=1e-3)


class TestDmsToDd:
    """Tests for dms_to_dd conversion."""

    def test_dms_to_dd_positive(self) -> None:
        result = dms_to_dd((45, 30, 0))
        assert isclose(result, 45.5, abs_tol=1e-6)

    def test_dms_to_dd_negative(self) -> None:
        result = dms_to_dd((-45, 30, 0))
        assert isclose(result, -45.5, abs_tol=1e-6)

    def test_dms_to_dd_zero(self) -> None:
        result = dms_to_dd((0, 0, 0))
        assert result == 0

    def test_dms_to_dd_with_seconds(self) -> None:
        result = dms_to_dd((45, 30, 30))
        expected = 45 + 30 / 60 + 30 / 3600
        assert isclose(result, expected, abs_tol=1e-6)


class TestDdDmsRoundtrip:
    """Tests for dd_to_dms and dms_to_dd roundtrip conversion."""

    @pytest.mark.parametrize("dd", [-89.999, -45.5, 0, 45.5, 89.999])
    def test_dd_dms_roundtrip(self, dd: float) -> None:
        dms = dd_to_dms(dd)
        result = dms_to_dd(dms)
        assert isclose(result, dd, abs_tol=1e-4)

    def test_dd_dms_roundtrip_small_positive(self) -> None:
        # Very small values have precision issues due to rounding in DMS
        dd = 0.01
        dms = dd_to_dms(dd)
        result = dms_to_dd(dms)
        assert isclose(result, dd, abs_tol=0.01)

    def test_dd_dms_small_negative_loses_sign(self) -> None:
        # Small negative values: dd_to_dms returns (0, m, s) which loses sign
        # This is a known limitation when degrees rounds to 0
        dd = -0.5
        dms = dd_to_dms(dd)
        # The degrees component rounds to 0, losing the negative sign
        assert dms[0] == 0
        assert dms[1] == 30
        # This means the roundtrip gives positive value - documented limitation
        result = dms_to_dd(dms)
        assert result == 0.5  # Sign is lost


class TestScaleToZoom:
    """Tests for scale_to_zoom conversion."""

    def test_scale_to_zoom_at_equator(self) -> None:
        # At equator, higher scale should give lower zoom
        zoom_large_scale = scale_to_zoom(100000, 0, 300)
        zoom_small_scale = scale_to_zoom(10000, 0, 300)
        assert zoom_large_scale < zoom_small_scale

    def test_scale_to_zoom_at_different_latitudes(self) -> None:
        # Same scale at different latitudes should give different zooms
        zoom_equator = scale_to_zoom(25000, 0, 300)
        zoom_high_lat = scale_to_zoom(25000, 60, 300)
        # These should be different due to Mercator distortion
        assert zoom_equator != zoom_high_lat


class TestZoomToScale:
    """Tests for zoom_to_scale conversion."""

    def test_zoom_to_scale_at_equator(self) -> None:
        # Higher zoom should give smaller scale (more detail)
        scale_low_zoom = zoom_to_scale(5, 0, 300)
        scale_high_zoom = zoom_to_scale(15, 0, 300)
        assert scale_low_zoom > scale_high_zoom


class TestScaleZoomRoundtrip:
    """Tests for scale_to_zoom and zoom_to_scale roundtrip."""

    @pytest.mark.parametrize("scale", [5000, 10000, 25000, 50000, 100000])
    def test_roundtrip_at_equator(self, scale: int) -> None:
        zoom = scale_to_zoom(scale, 0, 300)
        result_scale = zoom_to_scale(int(zoom), 0, 300)
        # Won't be exact due to integer zoom, but should be in ballpark
        assert 0.5 * scale < result_scale < 2 * scale


class TestGetStringFormattingArguments:
    """Tests for get_string_formatting_arguments function."""

    def test_no_placeholders(self) -> None:
        result = get_string_formatting_arguments("no placeholders here")
        assert result == []

    def test_single_placeholder(self) -> None:
        result = get_string_formatting_arguments("Hello {name}!")
        assert result == ["name"]

    def test_multiple_placeholders(self) -> None:
        result = get_string_formatting_arguments("{a} and {b} and {c}")
        assert result == ["a", "b", "c"]

    def test_tile_provider_template(self) -> None:
        template = "https://{mirror}.example.com/{zoom}/{x}/{y}.png?key={api_key}"
        result = get_string_formatting_arguments(template)
        assert result == ["mirror", "zoom", "x", "y", "api_key"]

    def test_empty_string(self) -> None:
        result = get_string_formatting_arguments("")
        assert result == []


class TestIsOutOfBounds:
    """Tests for is_out_of_bounds function."""

    def test_within_bounds(self) -> None:
        test = {"lat_min": 10.0, "lat_max": 20.0, "lon_min": 30.0, "lon_max": 40.0}
        bounds = {"lat_min": 0.0, "lat_max": 90.0, "lon_min": -180.0, "lon_max": 180.0}
        assert not is_out_of_bounds(test, bounds)

    def test_lat_min_out_of_bounds(self) -> None:
        test = {"lat_min": -100.0, "lat_max": 20.0, "lon_min": 30.0, "lon_max": 40.0}
        bounds = {
            "lat_min": -90.0,
            "lat_max": 90.0,
            "lon_min": -180.0,
            "lon_max": 180.0,
        }
        assert is_out_of_bounds(test, bounds)

    def test_lat_max_out_of_bounds(self) -> None:
        test = {"lat_min": 10.0, "lat_max": 100.0, "lon_min": 30.0, "lon_max": 40.0}
        bounds = {
            "lat_min": -90.0,
            "lat_max": 90.0,
            "lon_min": -180.0,
            "lon_max": 180.0,
        }
        assert is_out_of_bounds(test, bounds)

    def test_lon_min_out_of_bounds(self) -> None:
        test = {"lat_min": 10.0, "lat_max": 20.0, "lon_min": -200.0, "lon_max": 40.0}
        bounds = {
            "lat_min": -90.0,
            "lat_max": 90.0,
            "lon_min": -180.0,
            "lon_max": 180.0,
        }
        assert is_out_of_bounds(test, bounds)

    def test_lon_max_out_of_bounds(self) -> None:
        test = {"lat_min": 10.0, "lat_max": 20.0, "lon_min": 30.0, "lon_max": 200.0}
        bounds = {
            "lat_min": -90.0,
            "lat_max": 90.0,
            "lon_min": -180.0,
            "lon_max": 180.0,
        }
        assert is_out_of_bounds(test, bounds)

    def test_exactly_at_bounds(self) -> None:
        test = {"lat_min": -90.0, "lat_max": 90.0, "lon_min": -180.0, "lon_max": 180.0}
        bounds = {
            "lat_min": -90.0,
            "lat_max": 90.0,
            "lon_min": -180.0,
            "lon_max": 180.0,
        }
        assert not is_out_of_bounds(test, bounds)


class TestDrange:
    """Tests for drange function."""

    def test_basic_range(self) -> None:
        result = list(drange(Decimal(0), Decimal(10), Decimal(2)))
        expected = [Decimal(0), Decimal(2), Decimal(4), Decimal(6), Decimal(8)]
        assert result == expected

    def test_decimal_step(self) -> None:
        result = list(drange(Decimal(0), Decimal(1), Decimal("0.25")))
        expected = [
            Decimal(0),
            Decimal("0.25"),
            Decimal("0.50"),
            Decimal("0.75"),
        ]
        assert result == expected

    def test_start_equals_stop(self) -> None:
        result = list(drange(Decimal(5), Decimal(5), Decimal(1)))
        assert result == []

    def test_single_value(self) -> None:
        result = list(drange(Decimal(0), Decimal(1), Decimal(2)))
        assert result == [Decimal(0)]
