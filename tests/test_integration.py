"""End-to-end integration tests for PaperMap.

These tests verify the complete workflow from initialization to PDF output,
using mocked HTTP responses to avoid network dependencies.
"""

from pathlib import Path

import pytest
from PIL import Image
from pytest_httpx import HTTPXMock

from papermap.papermap import PaperMap


class TestFullPipeline:
    """End-to-end tests for the complete map generation pipeline."""

    def test_basic_map_generation(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a basic map with default settings."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_map.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_map_with_grid(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a map with UTM grid overlay."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=1000)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_map_grid.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_map_landscape(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a map in landscape orientation."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, use_landscape=True)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_map_landscape.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert pm.width > pm.height

    def test_map_different_sizes(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating maps with different paper sizes."""
        for size in ["a3", "a4", "a5", "letter"]:
            pm = PaperMap(lat=40.7128, lon=-74.0060, paper_size=size)

            for _ in range(len(pm.tiles)):
                httpx_mock.add_response(content=tile_image_content)

            pm.render()

            output_file = tmp_path / f"test_map_{size}.pdf"
            pm.save(output_file)

            assert output_file.exists()

    def test_map_different_scales(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating maps with different scales."""
        for scale in [10000, 25000, 50000]:
            pm = PaperMap(lat=40.7128, lon=-74.0060, scale=scale)

            for _ in range(len(pm.tiles)):
                httpx_mock.add_response(content=tile_image_content)

            pm.render()

            output_file = tmp_path / f"test_map_scale_{scale}.pdf"
            pm.save(output_file)

            assert output_file.exists()

    def test_map_custom_margins(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a map with custom margins."""
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            margin_top=20,
            margin_right=15,
            margin_bottom=25,
            margin_left=10,
        )

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_map_margins.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert pm.image_width == pm.width - 10 - 15
        assert pm.image_height == pm.height - 20 - 25

    def test_map_with_metadata(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a map with custom PDF metadata."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_map_metadata.pdf"
        pm.save(output_file, title="NYC Map", author="Test Author")

        assert output_file.exists()


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
    def test_map_at_location(  # noqa: PLR0913
        self,
        tmp_path: Path,
        lat: float,
        lon: float,
        name: str,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        """Test generating maps at various global locations."""
        pm = PaperMap(lat=lat, lon=lon)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / f"test_map_{name}.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_map_near_date_line_east(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a map near the date line (east side)."""
        pm = PaperMap(lat=0.0, lon=179.5)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_map_dateline_east.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_map_near_date_line_west(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a map near the date line (west side)."""
        pm = PaperMap(lat=0.0, lon=-179.5)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_map_dateline_west.pdf"
        pm.save(output_file)

        assert output_file.exists()


class TestTileDownloadBehavior:
    """Tests for tile download behavior and error handling."""

    def test_successful_tile_download(
        self,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        """Test that tiles are downloaded and marked as successful."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # Mock all tile downloads (add one response per tile)
        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.download_tiles()

        # All tiles should be marked as successful
        for tile in pm.tiles:
            assert tile.success

    def test_tile_download_retry_on_failure(
        self,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        """Test that tile downloads are retried on failure."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        num_tiles = len(pm.tiles)

        # First attempt: all tiles fail
        for _ in range(num_tiles):
            httpx_mock.add_response(status_code=500)

        # Second attempt: all tiles succeed
        for _ in range(num_tiles):
            httpx_mock.add_response(content=tile_image_content)

        pm.download_tiles(num_retries=3)

        # All tiles should eventually be successful
        for tile in pm.tiles:
            assert tile.success

    @pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
    def test_tile_download_max_retries_exceeded(self, httpx_mock: HTTPXMock) -> None:
        """Test that an error is raised when max retries are exceeded with strict=True."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        # All attempts fail
        for _ in range(len(pm.tiles) * 3):
            httpx_mock.add_response(status_code=500)

        with pytest.raises(RuntimeError, match="Could not download"):
            pm.download_tiles(num_retries=2, strict=True)


class TestRenderMethods:
    """Tests for individual render methods."""

    def test_render_base_layer_creates_image(
        self, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that render_base_layer creates the map image."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render_base_layer()

        assert hasattr(pm, "map_image")
        assert pm.map_image is not None
        assert pm.map_image.size == (pm.image_width_px, pm.image_height_px)

    def test_render_base_layer_uses_background_color(
        self, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that render_base_layer uses the specified background color."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, background_color="#ff0000")

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render_base_layer()

        assert hasattr(pm, "map_image_scaled")

    def test_render_grid_only_when_enabled(
        self, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that grid is only rendered when add_grid ."""
        pm_no_grid = PaperMap(lat=40.7128, lon=-74.0060, add_grid=False)
        pm_with_grid = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True)

        for _ in range(len(pm_no_grid.tiles) + len(pm_with_grid.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm_no_grid.render_base_layer()
        pm_with_grid.render_base_layer()

        # Both should work without error
        pm_no_grid.render_grid()
        pm_with_grid.render_grid()

    def test_render_attribution_and_scale(
        self, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that attribution and scale are rendered."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render_base_layer()

        # Should not raise any errors
        pm.render_attribution_and_scale()


class TestImageProcessing:
    """Tests for image processing in the pipeline."""

    def test_tiles_are_composited(
        self, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that tiles are composited into the final image."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render_base_layer()

        # The scaled map image should exist
        assert hasattr(pm, "map_image_scaled")
        assert pm.map_image_scaled is not None

        # The final map image should be resized
        assert pm.map_image.size == (pm.image_width_px, pm.image_height_px)

    def test_resize_factor_applied(
        self, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that the resize factor is applied correctly."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        # The resize factor compensates for discrete zoom levels
        assert 0 < pm.resize_factor <= 1

        pm.render_base_layer()

        # Scaled image dimensions should match calculated values
        assert pm.map_image_scaled.size == (
            pm.image_width_scaled_px,
            pm.image_height_scaled_px,
        )


class TestPdfOutput:
    """Tests for PDF output characteristics."""

    def test_pdf_has_correct_dimensions(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that the PDF has correct page dimensions."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, paper_size="a4")

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_dimensions.pdf"
        pm.save(output_file)

        # A4 is 210x297mm
        assert pm.width == 210
        assert pm.height == 297

    def test_pdf_content_is_valid(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that the PDF content is valid."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_valid.pdf"
        pm.save(output_file)

        # Check PDF magic bytes
        with output_file.open("rb") as f:
            header = f.read(8)
            assert header.startswith(b"%PDF-")


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_small_map(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a very small map (A7)."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, paper_size="a7")

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_small.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_large_margins(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a map with large margins."""
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            margin_top=50,
            margin_right=50,
            margin_bottom=50,
            margin_left=50,
        )

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_large_margins.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_zero_margins(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test generating a map with zero margins."""
        pm = PaperMap(
            lat=40.7128,
            lon=-74.0060,
            margin_top=0,
            margin_right=0,
            margin_bottom=0,
            margin_left=0,
        )

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "test_zero_margins.pdf"
        pm.save(output_file)

        assert output_file.exists()


class TestTileProviderConfiguration:
    """Tests for different tile provider configurations."""

    @pytest.mark.parametrize(
        "tile_provider",
        ["openstreetmap", "google-maps", "esri-worldstreetmap"],
    )
    def test_different_tile_providers(
        self,
        tmp_path: Path,
        tile_provider: str,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
    ) -> None:
        """Test generating maps with different tile providers."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, tile_provider_key=tile_provider)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / f"test_{tile_provider.replace('-', '_')}.pdf"
        pm.save(output_file)

        assert output_file.exists()

    def test_tile_provider_attribution_in_output(
        self, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that tile provider attribution is included in output."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, tile_provider_key="openstreetmap")

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        # Attribution should be part of the tile provider
        assert "OpenStreetMap" in pm.tile_provider.attribution


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


class TestFeatureRendering:
    """End-to-end tests for rendering GeoJSON-style features over the base map."""

    def test_render_circle_marker(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.add_circle_marker(40.7128, -74.0060, radius=4, fill_color="#f00")

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "circle.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_icon_marker_from_path(
        self,
        tmp_path: Path,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
        icon_image_path: Path,
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.add_icon_marker(40.7128, -74.0060, icon=icon_image_path, width=8.0)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "icon_path.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_icon_marker_from_pil_image(
        self,
        tmp_path: Path,
        httpx_mock: HTTPXMock,
        tile_image_content: bytes,
        icon_image: Image.Image,
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.add_icon_marker(40.7128, -74.0060, icon=icon_image, width=6.0)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "icon_pil.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_line(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.add_line(
            [(40.71, -74.01), (40.715, -74.005), (40.72, -74.0)],
            stroke_color="#00f",
            stroke_width=1.0,
        )

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "line.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_polygon_no_holes(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.add_polygon(
            [
                [
                    (40.71, -74.012),
                    (40.71, -74.002),
                    (40.72, -74.002),
                    (40.72, -74.012),
                    (40.71, -74.012),
                ]
            ],
            fill_color="#0f0",
            opacity=0.3,
        )

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "polygon.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_polygon_with_hole(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.add_polygon(
            [
                [
                    (40.705, -74.020),
                    (40.705, -73.990),
                    (40.725, -73.990),
                    (40.725, -74.020),
                    (40.705, -74.020),
                ],
                [
                    (40.710, -74.010),
                    (40.710, -74.005),
                    (40.720, -74.005),
                    (40.720, -74.010),
                    (40.710, -74.010),
                ],
            ],
            stroke_color="#800",
            fill_color="#fa0",
            opacity=0.4,
        )

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "polygon_hole.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_geojson_feature_collection(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.add_geojson(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-74.0060, 40.7128],
                        },
                        "properties": {"fill": "#f0f"},
                    },
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [
                                [-74.01, 40.71],
                                [-74.0, 40.72],
                            ],
                        },
                        "properties": {"stroke": "#0ff", "stroke-width": 1.5},
                    },
                ],
            }
        )

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "geojson.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_out_of_bounds_feature_does_not_crash(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        # Feature on the other side of the planet -- must be silently clipped.
        pm.add_circle_marker(0.0, 100.0, radius=5)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "oob.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_with_opacity(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        pm.add_circle_marker(
            40.7128, -74.0060, radius=4, fill_color="#f00", opacity=0.5
        )
        pm.add_polygon(
            [
                [
                    (40.71, -74.012),
                    (40.71, -74.002),
                    (40.72, -74.002),
                    (40.72, -74.012),
                    (40.71, -74.012),
                ]
            ],
            fill_color="#00f",
            stroke_color="#000",
            opacity=0.5,
        )

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "opacity.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_features_with_grid(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Features must coexist with the grid (drawn below it)."""
        pm = PaperMap(lat=40.7128, lon=-74.0060, add_grid=True, grid_size=1000)
        pm.add_circle_marker(40.7128, -74.0060, radius=4, fill_color="#f00")

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "features_grid.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_render_features_skipped_when_empty(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Existing maps without features must continue to render unchanged."""
        pm = PaperMap(lat=40.7128, lon=-74.0060)
        assert pm.features == []

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)
        pm.render()

        output_file = tmp_path / "no_features.pdf"
        pm.save(output_file)
        assert output_file.exists()
        assert output_file.stat().st_size > 0
