"""Unit tests for papermap.papermap module."""

from decimal import Decimal
from math import isclose
from pathlib import Path

import pytest
from PIL import UnidentifiedImageError
from pytest_httpx import HTTPXMock

from papermap.papermap import (
    DEFAULT_DPI,
    DEFAULT_SCALE,
    SIZE_TO_DIMENSIONS_MAP,
    SIZES,
    PaperMap,
)


class TestPaperMapInit:
    """Tests for PaperMap initialization."""

    def test_basic_init(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        assert pm.lat == 40.7128
        assert pm.lon == -74.0060
        assert pm.scale == DEFAULT_SCALE
        assert pm.dpi == DEFAULT_DPI

    def test_init_with_custom_scale(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060, scale=10000)
        assert pm.scale == 10000

    def test_init_with_custom_dpi(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060, dpi=150)
        assert pm.dpi == 150

    def test_init_with_landscape(self) -> None:
        pm_portrait = PaperMap(lat=40.7128, lon=-74.0060, use_landscape=False)
        pm_landscape = PaperMap(lat=40.7128, lon=-74.0060, use_landscape=True)

        # Landscape should swap width and height
        assert pm_portrait.width == pm_landscape.height
        assert pm_portrait.height == pm_landscape.width

    def test_init_with_custom_margins(self) -> None:
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            margin_top=20,
            margin_right=15,
            margin_bottom=25,
            margin_left=10,
        )
        assert pm.margin_top == 20
        assert pm.margin_right == 15
        assert pm.margin_bottom == 25
        assert pm.margin_left == 10

    def test_init_with_grid(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=500)
        assert pm.add_grid
        assert pm.grid_size == 500

    def test_init_stores_api_key(self) -> None:
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            tile_server="Thunderforest Landscape",
            api_key="test_key",
        )
        assert pm.api_key == "test_key"

    def test_init_computes_zoom(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        assert pm.zoom > 0
        assert pm.zoom_scaled >= 0
        assert isinstance(pm.zoom_scaled, int)

    def test_init_computes_image_dimensions(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        # Image dimensions should be paper size minus margins
        expected_width = pm.width - pm.margin_left - pm.margin_right
        expected_height = pm.height - pm.margin_top - pm.margin_bottom
        assert pm.image_width == expected_width
        assert pm.image_height == expected_height

    def test_init_creates_tiles(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        assert len(pm.tiles) > 0
        for tile in pm.tiles:
            assert tile.zoom == pm.zoom_scaled

    def test_init_creates_pdf(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        assert pm.pdf is not None


class TestPaperMapValidation:
    """Tests for PaperMap input validation."""

    def test_invalid_tile_server_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid tile server"):
            PaperMap(lat=40.7128, lon=-74.0060, tile_server="NonexistentServer")

    def test_valid_tile_servers(self) -> None:
        # Test a few valid tile servers
        for ts in ["OpenStreetMap", "Google Maps", "ESRI Standard"]:
            pm = PaperMap(lat=40.7128, lon=-74.0060, tile_server=ts)
            assert pm.tile_server is not None

    def test_api_key_stored_correctly(self) -> None:
        # API key should be stored when provided
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            tile_server="Thunderforest Landscape",
            api_key="test_key",
        )
        assert pm.api_key == "test_key"

    def test_thunderforest_works_without_api_key(self) -> None:
        with pytest.raises(ValueError, match="No API key specified"):
            PaperMap(
                lat=40.7128,
                lon=-74.0060,
                tile_server="Thunderforest Landscape",
            )

    def test_invalid_paper_size_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid paper size"):
            PaperMap(lat=40.7128, lon=-74.0060, size="nonexistent_size")

    def test_valid_paper_sizes(self) -> None:
        for size in SIZES:
            pm = PaperMap(lat=40.7128, lon=-74.0060, size=size)
            expected_width, expected_height = SIZE_TO_DIMENSIONS_MAP[size]
            assert pm.width == expected_width
            assert pm.height == expected_height

    def test_scale_out_of_bounds_raises_error_too_detailed(self) -> None:
        # Very small scale (very detailed) may exceed max zoom
        with pytest.raises(ValueError, match="Scale out of bounds"):
            PaperMap(lat=40.7128, lon=-74.0060, scale=100)

    def test_very_coarse_scale_works(self) -> None:
        # Very large scale (very coarse) - zoom level is computed but not below min
        # OpenStreetMap has zoom_min=0, so even very coarse scales work
        pm = PaperMap(lat=40.7128, lon=-74.0060, scale=100_000_000)
        assert pm.zoom_scaled >= 0


class TestPaperMapEdgeCases:
    """Tests for edge cases and boundary conditions."""

    # Coordinate edge cases
    def test_latitude_at_90_degrees(self) -> None:
        """Test latitude at exact north pole causes error in Web Mercator."""
        # Web Mercator cannot handle exactly ±90° (math domain error in log(tan()))
        # Could raise either ValueError or ZeroDivisionError depending on implementation
        try:
            PaperMap(lat=90.0, lon=0.0)
            msg = "Expected ValueError or ZeroDivisionError for latitude=90"
            raise AssertionError(msg)
        except (ValueError, ZeroDivisionError):
            pass  # Expected

    def test_latitude_at_minus_90_degrees(self) -> None:
        """Test latitude at exact south pole causes error in Web Mercator."""
        try:
            PaperMap(lat=-90.0, lon=0.0)
            msg = "Expected ValueError or ZeroDivisionError for latitude=-90"
            raise AssertionError(msg)
        except (ValueError, ZeroDivisionError):
            pass  # Expected

    def test_latitude_near_web_mercator_limit(self) -> None:
        """Test latitude near Web Mercator projection limits (~85.05°)."""
        pm_north = PaperMap(lat=85.05, lon=0.0)
        pm_south = PaperMap(lat=-85.05, lon=0.0)
        assert pm_north.lat == 85.05
        assert pm_south.lat == -85.05

    def test_longitude_at_180_degrees(self) -> None:
        """Test longitude at international date line."""
        pm_pos = PaperMap(lat=0.0, lon=180.0)
        pm_neg = PaperMap(lat=0.0, lon=-180.0)
        assert pm_pos.lon == 180.0
        assert pm_neg.lon == -180.0

    def test_coordinates_at_equator_prime_meridian(self) -> None:
        """Test coordinates at (0, 0)."""
        pm = PaperMap(lat=0.0, lon=0.0)
        assert pm.lat == 0.0
        assert pm.lon == 0.0

    # Scale edge cases
    def test_scale_of_one(self) -> None:
        """Test scale of 1:1 (extremely detailed, likely invalid)."""
        with pytest.raises(ValueError, match="Scale out of bounds"):
            PaperMap(lat=40.7128, lon=-74.0060, scale=1)

    def test_very_large_scale(self) -> None:
        """Test extremely coarse scale."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, scale=1_000_000_000)
        assert pm.scale == 1_000_000_000
        assert pm.zoom_scaled >= 0

    # DPI edge cases
    def test_dpi_minimum_value(self) -> None:
        """Test DPI at minimum reasonable value."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, dpi=1)
        assert pm.dpi == 1

    def test_very_high_dpi(self) -> None:
        """Test very high DPI value."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, dpi=2400)
        assert pm.dpi == 2400

    # Margin edge cases
    def test_zero_margins(self) -> None:
        """Test with all margins set to zero."""
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            margin_top=0,
            margin_right=0,
            margin_bottom=0,
            margin_left=0,
        )
        assert pm.margin_top == 0
        assert pm.image_width == pm.width
        assert pm.image_height == pm.height

    def test_asymmetric_margins(self) -> None:
        """Test with highly asymmetric margins."""
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            margin_top=50,
            margin_right=5,
            margin_bottom=10,
            margin_left=30,
        )
        assert pm.margin_top == 50
        assert pm.margin_right == 5
        assert pm.margin_bottom == 10
        assert pm.margin_left == 30

    def test_very_large_margins_on_small_paper(self) -> None:
        """Test large margins on A7 (smallest paper size)."""
        # A7 is 74x105mm, leaving very little space with large margins
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            size="a7",
            margin_top=20,
            margin_right=20,
            margin_bottom=20,
            margin_left=20,
        )
        # Should still have positive image area
        assert pm.image_width > 0
        assert pm.image_height > 0

    # Grid size edge cases
    def test_grid_size_very_small(self) -> None:
        """Test very small grid size."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=100)
        assert pm.grid_size == 100

    def test_grid_size_very_large(self) -> None:
        """Test very large grid size."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=100000)
        assert pm.grid_size == 100000

    # Tile server and API key edge cases
    def test_api_key_empty_string(self) -> None:
        """Test behavior with empty string API key."""
        # Empty string is stored as-is (not validated as missing)
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            tile_server="Thunderforest Landscape",
            api_key="",
        )
        assert pm.api_key == ""

    def test_api_key_with_special_characters(self) -> None:
        """Test API key with special characters."""
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            tile_server="Thunderforest Landscape",
            api_key="test-key_123.456/abc",
        )
        assert pm.api_key == "test-key_123.456/abc"

    # Combination edge cases
    def test_extreme_combination_a0_landscape_normal_scale(self) -> None:
        """Test A0 paper in landscape with normal scale."""
        pm = PaperMap(
            lat=40.7128, lon=-74.0060, size="a0", use_landscape=True, scale=25000
        )
        # A0 dimensions: 841x1189mm, swapped for landscape
        expected_width, expected_height = SIZE_TO_DIMENSIONS_MAP["a0"]
        assert pm.width == expected_height  # Swapped for landscape
        assert pm.height == expected_width
        assert pm.use_landscape
        assert pm.width > pm.height  # Landscape orientation

    def test_extreme_combination_a7_portrait_coarse_scale(self) -> None:
        """Test A7 paper in portrait with coarse scale."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, size="a7", scale=100_000)
        # A7 dimensions: 74x105mm
        expected_width, expected_height = SIZE_TO_DIMENSIONS_MAP["a7"]
        assert pm.width == expected_width
        assert pm.height == expected_height
        assert not pm.use_landscape
        assert pm.width < pm.height  # Portrait orientation


class TestPaperMapPaperSizes:
    """Tests for different paper sizes."""

    @pytest.mark.parametrize("size", ["a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7"])
    def test_a_series_sizes(self, size: str) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060, size=size)
        expected_width, expected_height = SIZE_TO_DIMENSIONS_MAP[size]
        assert pm.width == expected_width
        assert pm.height == expected_height

    def test_letter_size(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060, size="letter")
        assert pm.width == 216
        assert pm.height == 279

    def test_legal_size(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060, size="legal")
        assert pm.width == 216
        assert pm.height == 356


class TestPaperMapLandscape:
    """Tests for landscape orientation."""

    def test_landscape_swaps_dimensions(self) -> None:
        pm_portrait = PaperMap(
            lat=40.7128, lon=-74.0060, size="a4", use_landscape=False
        )
        pm_landscape = PaperMap(
            lat=40.7128, lon=-74.0060, size="a4", use_landscape=True
        )

        assert pm_portrait.width == 210
        assert pm_portrait.height == 297
        assert pm_landscape.width == 297
        assert pm_landscape.height == 210

    def test_landscape_with_different_sizes(self) -> None:
        for size in ["a3", "a4", "a5", "letter"]:
            pm = PaperMap(lat=40.7128, lon=-74.0060, size=size, use_landscape=True)
            # In landscape, width should be greater than height
            assert pm.width > pm.height


class TestPaperMapCoordinates:
    """Tests for different coordinate locations."""

    def test_equator_prime_meridian(self) -> None:
        pm = PaperMap(lat=0, lon=0)
        assert pm.lat == 0
        assert pm.lon == 0

    def test_northern_hemisphere(self) -> None:
        pm = PaperMap(lat=60, lon=10)
        assert pm.lat == 60

    def test_southern_hemisphere(self) -> None:
        pm = PaperMap(lat=-33, lon=151)
        assert pm.lat == -33

    def test_near_date_line_east(self) -> None:
        pm = PaperMap(lat=35, lon=179)
        assert pm.lon == 179

    def test_near_date_line_west(self) -> None:
        pm = PaperMap(lat=35, lon=-179)
        assert pm.lon == -179


class TestPaperMapComputeGridCoordinates:
    """Tests for compute_grid_coordinates method."""

    def test_compute_grid_coordinates_returns_tuples(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True)
        x_coords, y_coords = pm.compute_grid_coordinates()

        assert isinstance(x_coords, list)
        assert isinstance(y_coords, list)

        # Each item should be a tuple of (Decimal, str)
        for x, label in x_coords:
            assert isinstance(x, Decimal)
            assert isinstance(label, str)

        for y, label in y_coords:
            assert isinstance(y, Decimal)
            assert isinstance(label, str)

    def test_compute_grid_coordinates_in_range(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True)
        x_coords, y_coords = pm.compute_grid_coordinates()

        # All x coordinates should be within image width
        for x, _ in x_coords:
            assert 0 <= float(x) <= pm.image_width

        # All y coordinates should be within image height
        for y, _ in y_coords:
            assert 0 <= float(y) <= pm.image_height

    def test_compute_grid_coordinates_spacing(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=1000)
        x_coords, _y_coords = pm.compute_grid_coordinates()

        # Check that grid spacing is consistent
        if len(x_coords) > 1:
            spacing = float(x_coords[1][0] - x_coords[0][0])
            assert isclose(spacing, float(pm.grid_size_scaled), rel_tol=0.01)


class TestPaperMapRepr:
    """Tests for PaperMap string representation."""

    def test_repr(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        result = repr(pm)
        assert "PaperMap" in result
        assert "40.7128" in result
        assert "-74.006" in result

    def test_repr_with_different_coordinates(self) -> None:
        pm = PaperMap(lat=-33.8688, lon=151.2093)
        result = repr(pm)
        assert "-33.8688" in result
        assert "151.2093" in result


class TestPaperMapTileCalculations:
    """Tests for tile calculation logic."""

    def test_tiles_cover_image_area(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Should have tiles in a grid pattern
        x_values = sorted({t.x for t in pm.tiles})
        y_values = sorted({t.y for t in pm.tiles})

        # Should be contiguous
        for i in range(len(x_values) - 1):
            assert x_values[i + 1] - x_values[i] == 1

        for i in range(len(y_values) - 1):
            assert y_values[i + 1] - y_values[i] == 1

    def test_tile_zoom_matches_computed_zoom(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        for tile in pm.tiles:
            assert tile.zoom == pm.zoom_scaled

    def test_more_tiles_at_higher_resolution(self) -> None:
        pm_low = PaperMap(lat=40.7128, lon=-74.0060, scale=50000)
        pm_high = PaperMap(lat=40.7128, lon=-74.0060, scale=10000)

        # Higher resolution (smaller scale number) should have more tiles
        assert len(pm_high.tiles) >= len(pm_low.tiles)


class TestPaperMapZoomCalculations:
    """Tests for zoom level calculations."""

    def test_zoom_increases_with_detail(self) -> None:
        pm_low = PaperMap(lat=40.7128, lon=-74.0060, scale=100000)
        pm_high = PaperMap(lat=40.7128, lon=-74.0060, scale=10000)

        # Smaller scale number = more detail = higher zoom
        assert pm_high.zoom > pm_low.zoom

    def test_zoom_scaled_is_floor_of_zoom(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        assert pm.zoom_scaled == int(pm.zoom)
        assert pm.zoom_scaled <= pm.zoom

    def test_resize_factor_compensates_for_zoom_rounding(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        # The resize factor equals 2^zoom_scaled divided by 2^zoom
        expected = 2**pm.zoom_scaled / 2**pm.zoom
        assert isclose(pm.resize_factor, expected, rel_tol=1e-6)


class TestPaperMapDownloadTiles:
    """Tests for download_tiles method."""

    def test_download_tiles_with_mocked_client(
        self,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Mock all tile download requests (add one response per tile)
        for _ in pm.tiles:
            httpx_mock.add_response(content=tile_image_content)

        pm.download_tiles()

        # All tiles should have images now
        for tile in pm.tiles:
            assert tile.success

    def test_download_tiles_retry_on_failure(
        self,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        num_tiles = len(pm.tiles)

        # First attempt: all tiles fail (404 error)
        for _ in range(num_tiles):
            httpx_mock.add_response(status_code=404)

        # Second attempt: all tiles succeed
        for _ in range(num_tiles):
            httpx_mock.add_response(content=tile_image_content)

        pm.download_tiles(num_retries=3)

        # All tiles should eventually be successful
        for tile in pm.tiles:
            assert tile.success

    def test_download_tiles_raises_after_max_retries(
        self, httpx_mock: HTTPXMock
    ) -> None:
        # Disable unused response assertion
        httpx_mock._options.assert_all_responses_were_requested = False  # noqa: SLF001

        pm = PaperMap(lat=40.7128, lon=-74.0060)

        num_tiles = len(pm.tiles)
        num_retries = 2

        # All attempts fail
        for _ in range(num_tiles * (num_retries + 1)):
            httpx_mock.add_response(status_code=500)

        with pytest.raises(RuntimeError, match="Could not download"):
            pm.download_tiles(num_retries=num_retries)

    def test_download_tiles_retry_with_sleep(
        self,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that retry logic sleeps between retries when sleep_between_retries is set."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        num_tiles = len(pm.tiles)

        # Track sleep calls
        sleep_calls = []

        def mock_sleep(duration: float) -> None:
            sleep_calls.append(duration)

        monkeypatch.setattr("papermap.papermap.time.sleep", mock_sleep)

        # First attempt: all tiles fail
        for _ in range(num_tiles):
            httpx_mock.add_response(status_code=500)

        # Second attempt: all tiles succeed
        for _ in range(num_tiles):
            httpx_mock.add_response(content=tile_image_content)

        pm.download_tiles(num_retries=3, sleep_between_retries=1)

        # Verify that sleep was called with the correct duration
        assert len(sleep_calls) >= 1
        assert all(duration == 1 for duration in sleep_calls)


class TestPaperMapHttpErrors:
    """Tests for HTTP error handling in tile downloads."""

    def test_download_tiles_404_error(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of HTTP 404 Not Found errors."""
        # Disable unused response assertion
        httpx_mock._options.assert_all_responses_were_requested = False  # noqa: SLF001

        pm = PaperMap(lat=40.7128, lon=-74.0060)

        num_tiles = len(pm.tiles)

        # All attempts return 404
        for _ in range(num_tiles * 2):
            httpx_mock.add_response(status_code=404)

        with pytest.raises(RuntimeError, match="Could not download"):
            pm.download_tiles(num_retries=1)

    def test_download_tiles_500_error(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of HTTP 500 Server Error."""
        # Disable unused response assertion
        httpx_mock._options.assert_all_responses_were_requested = False  # noqa: SLF001

        pm = PaperMap(lat=40.7128, lon=-74.0060)

        num_tiles = len(pm.tiles)

        # All attempts return 500
        for _ in range(num_tiles * 2):
            httpx_mock.add_response(status_code=500)

        with pytest.raises(RuntimeError, match="Could not download"):
            pm.download_tiles(num_retries=1)

    def test_download_tiles_403_forbidden(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of HTTP 403 Forbidden errors (invalid API key)."""
        # Disable unused response assertion
        httpx_mock._options.assert_all_responses_were_requested = False  # noqa: SLF001

        pm = PaperMap(lat=40.7128, lon=-74.0060)

        num_tiles = len(pm.tiles)

        # All attempts return 403
        for _ in range(num_tiles * 2):
            httpx_mock.add_response(status_code=403)

        with pytest.raises(RuntimeError, match="Could not download"):
            pm.download_tiles(num_retries=1)

    def test_download_tiles_empty_response(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of empty response body."""
        # Disable unused response assertion in case exception prevents all downloads
        httpx_mock._options.assert_all_responses_were_requested = False  # noqa: SLF001

        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Return empty content (one per tile)
        for _ in pm.tiles:
            httpx_mock.add_response(content=b"")

        # Should raise UnidentifiedImageError when trying to parse empty content
        with pytest.raises(UnidentifiedImageError):
            pm.download_tiles(num_retries=1)

    def test_download_tiles_invalid_image_data(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of invalid/corrupted image data."""
        # Disable unused response assertion in case exception prevents all downloads
        httpx_mock._options.assert_all_responses_were_requested = False  # noqa: SLF001

        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Return invalid image data (one per tile)
        for _ in pm.tiles:
            httpx_mock.add_response(content=b"This is not a valid PNG image")

        # Should raise UnidentifiedImageError when PIL tries to open invalid image
        with pytest.raises(UnidentifiedImageError):
            pm.download_tiles(num_retries=1)

    def test_download_tiles_partial_success(
        self,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        """Test when some tiles succeed and some fail."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        num_tiles = len(pm.tiles)

        # First attempt: half succeed, half fail
        for i in range(num_tiles):
            if i < num_tiles // 2:
                # First half succeeds
                httpx_mock.add_response(content=tile_image_content)
            else:
                # Second half fails
                httpx_mock.add_response(status_code=500)

        # Second attempt: previously failed tiles now succeed
        for _ in range(num_tiles - num_tiles // 2):
            httpx_mock.add_response(content=tile_image_content)

        pm.download_tiles(num_retries=2)

        # All tiles should eventually succeed
        for tile in pm.tiles:
            assert tile.success


class TestPaperMapRenderBaseLayer:
    """Tests for render_base_layer method."""

    def test_render_base_layer_creates_map_image(
        self,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Mock tile downloads (add one response per tile)
        for _ in pm.tiles:
            httpx_mock.add_response(content=tile_image_content)

        pm.render_base_layer()

        assert hasattr(pm, "map_image")
        assert pm.map_image.size == (pm.image_width_px, pm.image_height_px)


class TestPaperMapSave:
    """Tests for save method."""

    def test_save_creates_file(
        self,
        tmp_path: Path,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Mock tile downloads (add one response per tile)
        for _ in pm.tiles:
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_map.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_save_with_custom_metadata(
        self,
        tmp_path: Path,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Mock tile downloads (add one response per tile)
        for _ in pm.tiles:
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_map.pdf"
        pm.save(output_file, title="Test Map", author="Test Author")

        assert output_file.exists()
