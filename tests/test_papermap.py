"""Unit tests for papermap.papermap module."""

from decimal import Decimal
from math import isclose
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from papermap.defaults import (
    DEFAULT_DPI,
    DEFAULT_GRID_SIZE,
    DEFAULT_MARGIN,
    DEFAULT_SCALE,
    DEFAULT_SIZE,
    DEFAULT_TILE_SERVER,
    SIZE_TO_DIMENSIONS_MAP,
    TILE_SERVERS,
)
from papermap.papermap import PaperMap


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
        assert pm.add_grid is True
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
        # Note: The current implementation checks for "a" placeholder, not "api_key"
        # So Thunderforest doesn't actually require API key at init time
        # (it will fail at tile download time instead)
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            tile_server="Thunderforest Landscape",
        )
        assert pm.api_key is None

    def test_invalid_paper_size_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid paper size"):
            PaperMap(lat=40.7128, lon=-74.0060, size="nonexistent_size")

    def test_valid_paper_sizes(self) -> None:
        from papermap.defaults import SIZES

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
        pm_portrait = PaperMap(lat=40.7128, lon=-74.0060, size="a4", use_landscape=False)
        pm_landscape = PaperMap(lat=40.7128, lon=-74.0060, size="a4", use_landscape=True)

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
        x_coords, y_coords = pm.compute_grid_coordinates()

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
        x_values = sorted(set(t.x for t in pm.tiles))
        y_values = sorted(set(t.y for t in pm.tiles))

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
        # resize_factor = 2^zoom_scaled / 2^zoom
        expected = 2 ** pm.zoom_scaled / 2 ** pm.zoom
        assert isclose(pm.resize_factor, expected, rel_tol=1e-6)


class TestPaperMapDownloadTiles:
    """Tests for download_tiles method."""

    def test_download_tiles_with_mocked_session(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Create mock response
        mock_image = Image.new("RGBA", (256, 256), color="green")
        import io

        buffer = io.BytesIO()
        mock_image.save(buffer, format="PNG")
        buffer.seek(0)

        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = buffer.getvalue()

        with patch("papermap.papermap.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session.get.return_value = mock_response

            pm.download_tiles()

            # All tiles should have images now
            for tile in pm.tiles:
                assert tile.success

    def test_download_tiles_retry_on_failure(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = MagicMock()
            if call_count <= len(pm.tiles):
                # First attempt fails
                mock_response.ok = False
            else:
                # Second attempt succeeds
                mock_image = Image.new("RGBA", (256, 256), color="green")
                import io

                buffer = io.BytesIO()
                mock_image.save(buffer, format="PNG")
                buffer.seek(0)
                mock_response.ok = True
                mock_response.content = buffer.getvalue()
            return mock_response

        with patch("papermap.papermap.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session.get.side_effect = side_effect

            pm.download_tiles(num_retries=3)

    def test_download_tiles_raises_after_max_retries(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        mock_response = MagicMock()
        mock_response.ok = False

        with patch("papermap.papermap.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session.get.return_value = mock_response

            with pytest.raises(RuntimeError, match="Could not download"):
                pm.download_tiles(num_retries=2)


class TestPaperMapRenderBaseLayer:
    """Tests for render_base_layer method."""

    def test_render_base_layer_creates_map_image(self) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Mock tile download
        mock_image = Image.new("RGBA", (256, 256), color="green")
        import io

        buffer = io.BytesIO()
        mock_image.save(buffer, format="PNG")
        buffer.seek(0)

        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = buffer.getvalue()

        with patch("papermap.papermap.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session.get.return_value = mock_response

            pm.render_base_layer()

            assert hasattr(pm, "map_image")
            assert pm.map_image.size == (pm.image_width_px, pm.image_height_px)


class TestPaperMapSave:
    """Tests for save method."""

    def test_save_creates_file(self, tmp_path) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Mock tile download
        mock_image = Image.new("RGBA", (256, 256), color="green")
        import io

        buffer = io.BytesIO()
        mock_image.save(buffer, format="PNG")
        buffer.seek(0)

        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = buffer.getvalue()

        with patch("papermap.papermap.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session.get.return_value = mock_response

            pm.render()

            output_file = tmp_path / "test_map.pdf"
            pm.save(output_file)

            assert output_file.exists()
            assert output_file.stat().st_size > 0

    def test_save_with_custom_metadata(self, tmp_path) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Mock tile download
        mock_image = Image.new("RGBA", (256, 256), color="green")
        import io

        buffer = io.BytesIO()
        mock_image.save(buffer, format="PNG")
        buffer.seek(0)

        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = buffer.getvalue()

        with patch("papermap.papermap.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session
            mock_session.get.return_value = mock_response

            pm.render()

            output_file = tmp_path / "test_map.pdf"
            pm.save(output_file, title="Test Map", author="Test Author")

            assert output_file.exists()
