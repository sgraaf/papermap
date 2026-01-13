"""Smoke tests for papermap.PaperMap package.

These are basic sanity checks to ensure the package is minimally functional.
They should be fast and catch major breakages without extensive coverage.
"""

from pathlib import Path

from click.testing import CliRunner
from pytest_httpx import HTTPXMock

import papermap
from papermap.cli import cli


class TestSmokeTests:
    """Basic smoke tests for papermap.PaperMap."""

    def test_package_imports(self) -> None:
        """Test that the package can be imported."""
        assert hasattr(papermap, "PaperMap")

    def test_basic_workflow(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test the basic create -> render -> save workflow."""
        # Create a PaperMap instance
        pm = papermap.PaperMap(lat=40.7128, lon=-74.0060)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        # Render the map
        pm.render()

        # Save to PDF
        output_file = tmp_path / "smoke_test.pdf"
        pm.save(output_file)

        # Verify output exists and is not empty
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_cli_latlon_command(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test the CLI latlon command works."""
        runner = CliRunner()
        output_file = tmp_path / "cli_test.pdf"

        for _ in range(70):
            httpx_mock.add_response(content=tile_image_content)

        # Use London coordinates (positive values) to avoid Click
        # interpreting negative longitude as an option
        result = runner.invoke(
            cli,
            ["latlon", "51.5074", "0.1278", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_map_with_grid(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that grid overlay functionality works."""
        pm = papermap.PaperMap(lat=40.7128, lon=-74.0060, add_grid=True)

        for _ in range(len(pm.tiles)):
            httpx_mock.add_response(content=tile_image_content)

        pm.render()

        output_file = tmp_path / "grid_test.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_different_paper_sizes(
        self, tmp_path: Path, httpx_mock: HTTPXMock, tile_image_content: bytes
    ) -> None:
        """Test that different paper sizes work."""
        for size in ["a4", "letter"]:
            pm = papermap.PaperMap(lat=40.7128, lon=-74.0060, paper_size=size)

            for _ in range(len(pm.tiles)):
                httpx_mock.add_response(content=tile_image_content)

            pm.render()

            output_file = tmp_path / f"size_{size}.pdf"
            pm.save(output_file)

            assert output_file.exists()
