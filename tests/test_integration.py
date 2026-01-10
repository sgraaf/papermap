"""End-to-end integration tests for PaperMap.

These tests verify the complete workflow from initialization to PDF output,
using mocked HTTP responses to avoid network dependencies.
"""

import io
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from papermap.papermap import PaperMap


def create_mock_tile_response(color: str = "green", size: int = 256) -> MagicMock:
    """Create a mock HTTP response with a tile image."""
    img = Image.new("RGBA", (size, size), color=color)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    response = MagicMock()
    response.ok = True
    response.content = buffer.getvalue()
    return response


def create_mock_session(response: MagicMock) -> MagicMock:
    """Create a mock session that returns the given response."""
    mock_session = MagicMock()
    mock_session.get.return_value = response
    mock_session.headers = {}
    return mock_session


@pytest.fixture
def mock_tile_download() -> Generator[MagicMock, None, None]:
    """Mock the tile download process."""
    response = create_mock_tile_response()

    with patch("papermap.papermap.Session") as mock_session_class:
        mock_session = create_mock_session(response)
        mock_session_class.return_value.__enter__.return_value = mock_session
        yield mock_session


@pytest.mark.usefixtures("mock_tile_download")
class TestFullPipeline:
    """End-to-end tests for the complete map generation pipeline."""

    def test_basic_map_generation(self, tmp_path: Path) -> None:
        """Test generating a basic map with default settings."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.render()

        output_file = tmp_path / "test_map.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_map_with_grid(self, tmp_path: Path) -> None:
        """Test generating a map with UTM grid overlay."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=1000)
        pm.render()

        output_file = tmp_path / "test_map_grid.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_map_landscape(self, tmp_path: Path) -> None:
        """Test generating a map in landscape orientation."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, use_landscape=True)
        pm.render()

        output_file = tmp_path / "test_map_landscape.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert pm.width > pm.height

    def test_map_different_sizes(self, tmp_path: Path) -> None:
        """Test generating maps with different paper sizes."""
        for size in ["a3", "a4", "a5", "letter"]:
            pm = PaperMap(lat=40.7128, lon=-74.0060, size=size)
            pm.render()

            output_file = tmp_path / f"test_map_{size}.pdf"
            pm.save(output_file)

            assert output_file.exists()

    def test_map_different_scales(self, tmp_path: Path) -> None:
        """Test generating maps with different scales."""
        for scale in [10000, 25000, 50000]:
            pm = PaperMap(lat=40.7128, lon=-74.0060, scale=scale)
            pm.render()

            output_file = tmp_path / f"test_map_scale_{scale}.pdf"
            pm.save(output_file)

            assert output_file.exists()

    def test_map_custom_margins(self, tmp_path: Path) -> None:
        """Test generating a map with custom margins."""
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            margin_top=20,
            margin_right=15,
            margin_bottom=25,
            margin_left=10,
        )
        pm.render()

        output_file = tmp_path / "test_map_margins.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert pm.image_width == pm.width - 10 - 15
        assert pm.image_height == pm.height - 20 - 25

    def test_map_with_metadata(self, tmp_path: Path) -> None:
        """Test generating a map with custom PDF metadata."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.render()

        output_file = tmp_path / "test_map_metadata.pdf"
        pm.save(output_file, title="NYC Map", author="Test Author")

        assert output_file.exists()


@pytest.mark.usefixtures("mock_tile_download")
class TestDifferentLocations:
    """Tests for map generation at various global locations."""

    @pytest.mark.parametrize(
        ("lat", "lon", "name"),
        [
            (40.7128, -74.0060, "new_york"),
            (51.5074, -0.1278, "london"),
            (35.6762, 139.6503, "tokyo"),
            (-33.8688, 151.2093, "sydney"),
            (0.0, 0.0, "null_island"),
            (60.0, 10.0, "norway"),
            (-45.0, 170.0, "new_zealand"),
        ],
    )
    def test_map_at_location(
        self, tmp_path: Path, lat: float, lon: float, name: str
    ) -> None:
        """Test generating maps at various global locations."""
        pm = PaperMap(lat=lat, lon=lon)
        pm.render()

        output_file = tmp_path / f"test_map_{name}.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_map_near_date_line_east(self, tmp_path: Path) -> None:
        """Test generating a map near the date line (east side)."""
        pm = PaperMap(lat=0.0, lon=179.5)
        pm.render()

        output_file = tmp_path / "test_map_dateline_east.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_map_near_date_line_west(self, tmp_path: Path) -> None:
        """Test generating a map near the date line (west side)."""
        pm = PaperMap(lat=0.0, lon=-179.5)
        pm.render()

        output_file = tmp_path / "test_map_dateline_west.pdf"
        pm.save(output_file)

        assert output_file.exists()


class TestTileDownloadBehavior:
    """Tests for tile download behavior and error handling."""

    def test_successful_tile_download(self) -> None:
        """Test that tiles are downloaded and marked as successful."""
        response = create_mock_tile_response()

        with patch("papermap.papermap.Session") as mock_session_class:
            mock_session = create_mock_session(response)
            mock_session_class.return_value.__enter__.return_value = mock_session

            pm = PaperMap(lat=40.7128, lon=-74.0060)
            pm.download_tiles()

            # All tiles should be marked as successful
            for tile in pm.tiles:
                assert tile.success

    def test_tile_download_retry_on_failure(self) -> None:
        """Test that tile downloads are retried on failure."""
        call_count = [0]
        total_tiles = [0]

        def get_response(*_args: object, **_kwargs: object) -> MagicMock:
            call_count[0] += 1
            response = MagicMock()
            if call_count[0] <= total_tiles[0]:
                # First attempt fails
                response.ok = False
            else:
                # Subsequent attempts succeed
                img = Image.new("RGBA", (256, 256), color="green")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                response.ok = True
                response.content = buffer.getvalue()
            return response

        with patch("papermap.papermap.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.headers = {}
            mock_session.get.side_effect = get_response
            mock_session_class.return_value.__enter__.return_value = mock_session

            pm = PaperMap(lat=40.7128, lon=-74.0060)
            total_tiles[0] = len(pm.tiles)

            pm.download_tiles(num_retries=3)

            # All tiles should eventually be successful
            for tile in pm.tiles:
                assert tile.success

    def test_tile_download_max_retries_exceeded(self) -> None:
        """Test that an error is raised when max retries are exceeded."""
        response = MagicMock()
        response.ok = False

        with patch("papermap.papermap.Session") as mock_session_class:
            mock_session = create_mock_session(response)
            mock_session_class.return_value.__enter__.return_value = mock_session

            pm = PaperMap(lat=40.7128, lon=-74.0060)

            with pytest.raises(RuntimeError, match="Could not download"):
                pm.download_tiles(num_retries=2)


@pytest.mark.usefixtures("mock_tile_download")
class TestRenderMethods:
    """Tests for individual render methods."""

    def test_render_base_layer_creates_image(self) -> None:
        """Test that render_base_layer creates the map image."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.render_base_layer()

        assert hasattr(pm, "map_image")
        assert pm.map_image is not None
        assert pm.map_image.size == (pm.image_width_px, pm.image_height_px)

    def test_render_base_layer_uses_background_color(self) -> None:
        """Test that render_base_layer uses the specified background color."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, background_color="#ff0000")
        pm.render_base_layer()

        assert hasattr(pm, "map_image_scaled")

    def test_render_grid_only_when_enabled(self) -> None:
        """Test that grid is only rendered when add_grid ."""
        pm_no_grid = PaperMap(lat=40.7128, lon=-74.0060, add_grid=False)
        pm_with_grid = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True)

        pm_no_grid.render_base_layer()
        pm_with_grid.render_base_layer()

        # Both should work without error
        pm_no_grid.render_grid()
        pm_with_grid.render_grid()

    def test_render_attribution_and_scale(self) -> None:
        """Test that attribution and scale are rendered."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.render_base_layer()

        # Should not raise any errors
        pm.render_attribution_and_scale()


@pytest.mark.usefixtures("mock_tile_download")
class TestImageProcessing:
    """Tests for image processing in the pipeline."""

    def test_tiles_are_composited(self) -> None:
        """Test that tiles are composited into the final image."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.render_base_layer()

        # The scaled map image should exist
        assert hasattr(pm, "map_image_scaled")
        assert pm.map_image_scaled is not None

        # The final map image should be resized
        assert pm.map_image.size == (pm.image_width_px, pm.image_height_px)

    def test_resize_factor_applied(self) -> None:
        """Test that the resize factor is applied correctly."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # The resize factor compensates for discrete zoom levels
        assert 0 < pm.resize_factor <= 1

        pm.render_base_layer()

        # Scaled image dimensions should match calculated values
        assert pm.map_image_scaled.size == (
            pm.image_width_scaled_px,
            pm.image_height_scaled_px,
        )


@pytest.mark.usefixtures("mock_tile_download")
class TestPdfOutput:
    """Tests for PDF output characteristics."""

    def test_pdf_has_correct_dimensions(self, tmp_path: Path) -> None:
        """Test that the PDF has correct page dimensions."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, size="a4")
        pm.render()

        output_file = tmp_path / "test_dimensions.pdf"
        pm.save(output_file)

        # A4 is 210x297mm
        assert pm.width == 210
        assert pm.height == 297

    def test_pdf_content_is_valid(self, tmp_path: Path) -> None:
        """Test that the PDF content is valid."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.render()

        output_file = tmp_path / "test_valid.pdf"
        pm.save(output_file)

        # Check PDF magic bytes
        with output_file.open("rb") as f:
            header = f.read(8)
            assert header.startswith(b"%PDF-")


@pytest.mark.usefixtures("mock_tile_download")
class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_small_map(self, tmp_path: Path) -> None:
        """Test generating a very small map (A7)."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, size="a7")
        pm.render()

        output_file = tmp_path / "test_small.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_large_margins(self, tmp_path: Path) -> None:
        """Test generating a map with large margins."""
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            margin_top=50,
            margin_right=50,
            margin_bottom=50,
            margin_left=50,
        )
        pm.render()

        output_file = tmp_path / "test_large_margins.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_zero_margins(self, tmp_path: Path) -> None:
        """Test generating a map with zero margins."""
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            margin_top=0,
            margin_right=0,
            margin_bottom=0,
            margin_left=0,
        )
        pm.render()

        output_file = tmp_path / "test_zero_margins.pdf"
        pm.save(output_file)

        assert output_file.exists()


@pytest.mark.usefixtures("mock_tile_download")
class TestTileServerConfiguration:
    """Tests for different tile server configurations."""

    @pytest.mark.parametrize(
        "tile_server",
        ["OpenStreetMap", "Google Maps", "ESRI Standard"],
    )
    def test_different_tile_servers(self, tmp_path: Path, tile_server: str) -> None:
        """Test generating maps with different tile servers."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, tile_server=tile_server)
        pm.render()

        output_file = tmp_path / f"test_{tile_server.replace(' ', '_')}.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_tile_server_attribution_in_output(self) -> None:
        """Test that tile server attribution is included in output."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, tile_server="OpenStreetMap")
        pm.render()

        # Attribution should be part of the tile server
        assert "OpenStreetMap" in pm.tile_server.attribution


@pytest.mark.usefixtures("mock_tile_download")
class TestGridCoordinates:
    """Tests for UTM grid coordinate calculations."""

    def test_grid_coordinates_calculated(self) -> None:
        """Test that grid coordinates are calculated correctly."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=1000)

        x_coords, y_coords = pm.compute_grid_coordinates()

        # Should have some grid lines
        assert len(x_coords) > 0
        assert len(y_coords) > 0

        # Each coordinate should have a position and label
        for _x, label in x_coords:
            assert isinstance(label, str)

        for _y, label in y_coords:
            assert isinstance(label, str)

    def test_grid_size_affects_coordinate_count(self) -> None:
        """Test that grid size affects the number of grid lines."""
        pm_small = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=500)
        pm_large = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=2000)

        x_small, y_small = pm_small.compute_grid_coordinates()
        x_large, y_large = pm_large.compute_grid_coordinates()

        # Smaller grid size should result in more grid lines
        assert len(x_small) >= len(x_large)
        assert len(y_small) >= len(y_large)
