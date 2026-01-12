"""Integration tests for papermap CLI."""

import runpy
import subprocess
import sys
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from importlib import import_module, metadata
from os import PathLike
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from papermap.cli import cli
from papermap.defaults import DEFAULT_DPI, DEFAULT_SCALE, SIZES

# copied from `typeshed`
StrOrBytesPath = str | bytes | PathLike
Command = StrOrBytesPath | Sequence[StrOrBytesPath]


@dataclass
class CommandResult:
    """Holds the captured result of an invoked command.

    Inspired by `click.testing.Result`.
    """

    exit_code: int
    stdout: str
    stderr: str


def run_command_in_shell(command: Command, **kwargs: Any) -> CommandResult:  # noqa: ANN401
    """Execute a command through the shell, capturing the exit code and output."""
    result = subprocess.run(  # noqa: S602
        command,
        shell=True,
        capture_output=True,
        check=False,
        **kwargs,
    )
    return CommandResult(
        result.returncode,
        result.stdout.decode().replace("\r\n", "\n"),
        result.stderr.decode().replace("\r\n", "\n"),
    )


# Use London coordinates (positive values) for most tests to avoid
# Click interpreting negative longitude as an option
TEST_LAT = 51.5074
TEST_LON = 0.1278


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_papermap() -> Generator[tuple[MagicMock, MagicMock], None, None]:
    """Mock PaperMap class to avoid actual tile downloads."""
    with patch("papermap.cli.PaperMap") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield mock, instance


def test_main_module() -> None:
    """Exercise (most of) the code in the `__main__` module."""
    import_module("papermap.__main__")


def test_main_module_execution() -> None:
    """Test that __main__.py can be executed directly."""
    # This simulates running the module with __name__ == "__main__"
    # We use runpy to properly execute the module with imports
    with patch("papermap.cli.PaperMap"):
        # Capture sys.argv to prevent test arguments from interfering
        original_argv = sys.argv
        try:
            # Set argv to just show help (avoids needing actual arguments)
            sys.argv = ["papermap", "--help"]
            # Run the module - this will execute the if __name__ == "__main__" block
            with pytest.raises(SystemExit) as exc_info:
                runpy.run_module("papermap.__main__", run_name="__main__")
            # --help causes exit code 0
            assert exc_info.value.code == 0
        finally:
            sys.argv = original_argv


def test_run_as_module() -> None:
    """Is the script runnable as a Python module?"""
    result = run_command_in_shell("python -m papermap --help")
    assert result.exit_code == 0


def test_run_as_executable() -> None:
    """Is the script installed (as a `console_script`) and runnable as an executable?"""
    result = run_command_in_shell("papermap --help")
    assert result.exit_code == 0


def test_version_runner(runner: CliRunner) -> None:
    """Does `--version` display the correct version?"""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"cli, version {metadata.version('papermap')}\n"


class TestCliHelp:
    """Tests for CLI help output."""

    def test_cli_help(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "PaperMap" in result.output
        assert "latlon" in result.output
        assert "utm" in result.output

    def test_cli_version(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        # Should contain version number
        assert "." in result.output  # Version numbers have dots

    def test_latlon_help(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["latlon", "--help"])
        assert result.exit_code == 0
        assert "LATITUDE" in result.output
        assert "LONGITUDE" in result.output
        assert "--tile-server" in result.output
        assert "--size" in result.output
        assert "--scale" in result.output

    def test_utm_help(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["utm", "--help"])
        assert result.exit_code == 0
        assert "EASTING" in result.output
        assert "NORTHING" in result.output
        assert "ZONE-NUMBER" in result.output
        assert "HEMISPHERE" in result.output


class TestLatLonCommand:
    """Tests for the latlon command."""

    def test_latlon_basic(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli, ["latlon", str(TEST_LAT), str(TEST_LON), str(output_file)]
        )

        assert result.exit_code == 0
        mock_class.assert_called_once()
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["lat"] == TEST_LAT
        assert call_kwargs["lon"] == TEST_LON
        mock_instance.render.assert_called_once()
        mock_instance.save.assert_called_once()

    def test_latlon_with_negative_longitude(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        """Test with negative longitude using -- separator."""
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        # Use -- to prevent negative longitude from being interpreted as an option
        result = runner.invoke(
            cli, ["latlon", "--", "40.7128", "-74.0060", str(output_file)]
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["lat"] == 40.7128
        assert call_kwargs["lon"] == -74.0060

    def test_latlon_with_tile_server(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--tile-server",
                "Google Maps",
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["tile_server"] == "Google Maps"

    def test_latlon_with_size(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            ["latlon", str(TEST_LAT), str(TEST_LON), str(output_file), "--size", "a3"],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["size"] == "a3"

    def test_latlon_with_landscape(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--landscape",
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["use_landscape"]

    def test_latlon_with_scale(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--scale",
                "10000",
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["scale"] == 10000

    def test_latlon_with_dpi(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            ["latlon", str(TEST_LAT), str(TEST_LON), str(output_file), "--dpi", "150"],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["dpi"] == 150

    def test_latlon_with_grid(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--grid",
                "--grid-size",
                "500",
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["add_grid"]
        assert call_kwargs["grid_size"] == 500

    def test_latlon_with_margins(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--margin-top",
                "20",
                "--margin-right",
                "15",
                "--margin-bottom",
                "25",
                "--margin-left",
                "10",
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["margin_top"] == 20
        assert call_kwargs["margin_right"] == 15
        assert call_kwargs["margin_bottom"] == 25
        assert call_kwargs["margin_left"] == 10

    def test_latlon_with_api_key(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--tile-server",
                "Thunderforest Landscape",
                "--api-key",
                "test_key_123",
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["api_key"] == "test_key_123"

    def test_latlon_missing_coordinates(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["latlon"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Error" in result.output

    def test_latlon_missing_file(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["latlon", str(TEST_LAT), str(TEST_LON)])
        assert result.exit_code != 0

    def test_latlon_invalid_tile_server(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        output_file = tmp_path / "test.pdf"
        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--tile-server",
                "InvalidServer",
            ],
        )
        assert result.exit_code != 0

    def test_latlon_invalid_size(self, runner: CliRunner, tmp_path: Path) -> None:
        output_file = tmp_path / "test.pdf"
        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--size",
                "invalid",
            ],
        )
        assert result.exit_code != 0


class TestUtmCommand:
    """Tests for the utm command.

    Note: The UTM command internally calls the latlon command as a Python function,
    which is not the standard Click pattern. This makes mocking difficult because
    Click tries to create a Context with the function arguments.

    These tests verify the CLI argument parsing works correctly. Full integration
    tests for UTM are in test_integration.py.
    """

    def test_utm_help(self, runner: CliRunner) -> None:
        """Test that UTM help displays correctly."""
        result = runner.invoke(cli, ["utm", "--help"])
        assert result.exit_code == 0
        assert "EASTING" in result.output
        assert "NORTHING" in result.output
        assert "ZONE-NUMBER" in result.output
        assert "HEMISPHERE" in result.output

    def test_utm_missing_arguments(self, runner: CliRunner) -> None:
        """Test that UTM command requires all arguments."""
        result = runner.invoke(cli, ["utm", "583960", "4507523"])
        assert result.exit_code != 0

    def test_utm_invalid_zone(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that UTM command validates zone type."""
        output_file = tmp_path / "test.pdf"
        result = runner.invoke(
            cli, ["utm", "583960", "4507523", "invalid", "N", str(output_file)]
        )
        assert result.exit_code != 0

    def test_utm_basic_execution(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test that UTM command converts coordinates and creates map."""
        output_file = tmp_path / "test.pdf"

        # Mock the latlon function to avoid Click context issues
        with patch("papermap.cli._create_and_save_map") as mock_create_and_save_map:
            # UTM coordinates (zone 31N)
            result = runner.invoke(
                cli, ["utm", "430000", "4580000", "31", "N", str(output_file)]
            )

            assert result.exit_code == 0
            mock_create_and_save_map.assert_called_once()
            call_args = mock_create_and_save_map.call_args.args
            # Verify coordinates were converted to valid lat/lon ranges
            assert -90 <= call_args[0] <= 90
            assert -180 <= call_args[1] <= 180
            # Should be in northern hemisphere (zone 31N)
            assert call_args[0] > 0

    def test_utm_southern_hemisphere(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test that UTM command works for southern hemisphere."""
        output_file = tmp_path / "test.pdf"

        with patch(
            "papermap.cli._create_and_save_map"
        ) as mock_create_and_save_mapmock_create_and_save_map:
            # UTM coordinates for Sydney (zone 56S)
            result = runner.invoke(
                cli, ["utm", "334000", "6252000", "56", "S", str(output_file)]
            )

            assert result.exit_code == 0
            call_args = mock_create_and_save_mapmock_create_and_save_map.call_args.args
            # Should be in southern hemisphere (negative latitude)
            assert call_args[0] < 0

    def test_utm_with_options(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Test that UTM command passes through options to latlon."""
        output_file = tmp_path / "test.pdf"

        with patch("papermap.cli._create_and_save_map") as mock_create_and_save_map:
            result = runner.invoke(
                cli,
                [
                    "utm",
                    "430000",
                    "4580000",
                    "31",
                    "N",
                    str(output_file),
                    "--scale",
                    "10000",
                    "--grid",
                    "--size",
                    "a3",
                ],
            )

            assert result.exit_code == 0
            call_kwargs = mock_create_and_save_map.call_args.kwargs
            assert call_kwargs["scale"] == 10000
            assert call_kwargs["add_grid"]
            assert call_kwargs["size"] == "a3"


class TestDefaultCommand:
    """Tests for default command behavior."""

    def test_default_is_latlon(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        # Without specifying a subcommand, should use latlon
        result = runner.invoke(cli, [str(TEST_LAT), str(TEST_LON), str(output_file)])

        assert result.exit_code == 0
        mock_class.assert_called_once()
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["lat"] == TEST_LAT
        assert call_kwargs["lon"] == TEST_LON


class TestTileServerChoices:
    """Tests for tile server option choices."""

    @pytest.mark.parametrize(
        "tile_server",
        ["OpenStreetMap", "Google Maps", "ESRI Standard", "ESRI Satellite"],
    )
    def test_common_tile_servers_work(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
        tile_server: str,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--tile-server",
                tile_server,
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["tile_server"] == tile_server


class TestPaperSizeChoices:
    """Tests for paper size option choices."""

    @pytest.mark.parametrize("size", SIZES)
    def test_all_sizes_work(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
        size: str,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli,
            [
                "latlon",
                str(TEST_LAT),
                str(TEST_LON),
                str(output_file),
                "--size",
                size,
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]
        assert call_kwargs["size"] == size


class TestCliDefaults:
    """Tests for CLI default values."""

    def test_default_values(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli, ["latlon", str(TEST_LAT), str(TEST_LON), str(output_file)]
        )

        assert result.exit_code == 0
        call_kwargs = mock_class.call_args[1]

        # Check defaults
        assert call_kwargs["tile_server"] == "OpenStreetMap"
        assert call_kwargs["size"] == "a4"
        assert not call_kwargs["use_landscape"]
        assert call_kwargs["scale"] == DEFAULT_SCALE
        assert call_kwargs["dpi"] == DEFAULT_DPI
        assert not call_kwargs["add_grid"]
        assert call_kwargs["margin_top"] == 10
        assert call_kwargs["margin_right"] == 10
        assert call_kwargs["margin_bottom"] == 10
        assert call_kwargs["margin_left"] == 10


class TestCliErrorHandling:
    """Tests for CLI error handling."""

    def test_invalid_latitude_type(self, runner: CliRunner, tmp_path: Path) -> None:
        output_file = tmp_path / "test.pdf"
        result = runner.invoke(
            cli, ["latlon", "invalid", str(TEST_LON), str(output_file)]
        )
        assert result.exit_code != 0

    def test_invalid_longitude_type(self, runner: CliRunner, tmp_path: Path) -> None:
        output_file = tmp_path / "test.pdf"
        result = runner.invoke(
            cli, ["latlon", str(TEST_LAT), "invalid", str(output_file)]
        )
        assert result.exit_code != 0

    def test_papermap_error_propagates(
        self,
        runner: CliRunner,
        mock_papermap: tuple[MagicMock, MagicMock],
        tmp_path: Path,
    ) -> None:
        mock_class, _mock_instance = mock_papermap
        mock_class.side_effect = ValueError("Scale out of bounds")
        output_file = tmp_path / "test.pdf"

        result = runner.invoke(
            cli, ["latlon", str(TEST_LAT), str(TEST_LON), str(output_file)]
        )

        assert result.exit_code != 0
