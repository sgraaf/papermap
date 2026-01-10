"""Shared fixtures for PaperMap tests."""

import io
from typing import Any
from unittest.mock import MagicMock

import pytest
from PIL import Image

from papermap.tile import Tile
from papermap.tile_server import TileServer


@pytest.fixture
def sample_tile() -> Tile:
    """Return a sample tile for testing."""
    return Tile(x=123, y=456, zoom=10, bbox=(0, 0, 256, 256))


@pytest.fixture
def sample_tile_with_image() -> Tile:
    """Return a sample tile with an image for testing."""
    tile = Tile(x=123, y=456, zoom=10, bbox=(0, 0, 256, 256))
    tile.image = Image.new("RGBA", (256, 256), color="blue")
    return tile


@pytest.fixture
def sample_tile_server() -> TileServer:
    """Return a sample tile server for testing."""
    return TileServer(
        attribution="Test Attribution",
        url_template="https://example.com/{zoom}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=19,
    )


@pytest.fixture
def sample_tile_server_with_mirrors() -> TileServer:
    """Return a sample tile server with mirrors for testing."""
    return TileServer(
        attribution="Test Attribution",
        url_template="https://{mirror}.example.com/{zoom}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=19,
        mirrors=["a", "b", "c"],
    )


@pytest.fixture
def sample_tile_server_with_api_key() -> TileServer:
    """Return a sample tile server requiring an API key for testing."""
    return TileServer(
        attribution="Test Attribution",
        url_template="https://example.com/{zoom}/{x}/{y}.png?api_key={api_key}",
        zoom_min=0,
        zoom_max=19,
    )


@pytest.fixture
def mock_tile_image() -> Image.Image:
    """Return a mock tile image for testing."""
    return Image.new("RGBA", (256, 256), color="green")


@pytest.fixture
def mock_response(mock_tile_image: Image.Image) -> MagicMock:
    """Return a mock HTTP response for tile downloads."""
    buffer = io.BytesIO()
    mock_tile_image.save(buffer, format="PNG")
    buffer.seek(0)

    response = MagicMock()
    response.ok = True
    response.content = buffer.getvalue()
    return response


# Well-known coordinate test cases
COORDINATE_TEST_CASES: dict[str, dict[str, float]] = {
    "new_york": {"lat": 40.7128, "lon": -74.0060},
    "london": {"lat": 51.5074, "lon": -0.1278},
    "tokyo": {"lat": 35.6762, "lon": 139.6503},
    "sydney": {"lat": -33.8688, "lon": 151.2093},
    "sao_paulo": {"lat": -23.5505, "lon": -46.6333},
    "equator_prime_meridian": {"lat": 0.0, "lon": 0.0},
    "north_pole_edge": {"lat": 84.0, "lon": 0.0},  # Max for UTM
    "south_pole_edge": {"lat": -80.0, "lon": 0.0},  # Min for UTM
    "date_line_east": {"lat": 0.0, "lon": 179.9},
    "date_line_west": {"lat": 0.0, "lon": -179.9},
}


@pytest.fixture
def coordinate_test_cases() -> dict[str, Any]:
    """Return well-known coordinate test cases."""
    return COORDINATE_TEST_CASES
