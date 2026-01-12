"""Smoke tests for papermap.PaperMap package.

These are basic sanity checks to ensure the package is minimally functional.
They should be fast and catch major breakages without extensive coverage.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

import papermap
from papermap.cli import cli


class TestSmokeTests:
    """Basic smoke tests for papermap.PaperMap."""

    def test_package_imports(self) -> None:
        """Test that the package can be imported."""
        assert hasattr(papermap, "PaperMap")

    @pytest.mark.usefixtures("mock_tile_download")
    def test_basic_workflow(self, tmp_path: Path) -> None:
        """Test the basic create -> render -> save workflow."""
        # Create a PaperMap instance
        pm = papermap.PaperMap(lat=40.7128, lon=-74.0060)

        # Render the map
        pm.render()

        # Save to PDF
        output_file = tmp_path / "smoke_test.pdf"
        pm.save(output_file)

        # Verify output exists and is not empty
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    @pytest.mark.usefixtures("mock_tile_download")
    def test_cli_latlon_command(self, tmp_path: Path) -> None:
        """Test the CLI latlon command works."""
        runner = CliRunner()
        output_file = tmp_path / "cli_test.pdf"

        # Use London coordinates (positive values) to avoid Click
        # interpreting negative longitude as an option
        result = runner.invoke(
            cli,
            ["latlon", "51.5074", "0.1278", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    @pytest.mark.usefixtures("mock_tile_download")
    def test_map_with_grid(self, tmp_path: Path) -> None:
        """Test that grid overlay functionality works."""
        pm = papermap.PaperMap(lat=40.7128, lon=-74.0060, add_grid=True)
        pm.render()

        output_file = tmp_path / "grid_test.pdf"
        pm.save(output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    @pytest.mark.usefixtures("mock_tile_download")
    def test_different_paper_sizes(self, tmp_path: Path) -> None:
        """Test that different paper sizes work."""
        for size in ["a4", "letter"]:
            pm = papermap.PaperMap(lat=40.7128, lon=-74.0060, size=size)
            pm.render()

            output_file = tmp_path / f"size_{size}.pdf"
            pm.save(output_file)

            assert output_file.exists()
