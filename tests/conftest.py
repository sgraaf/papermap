"""Shared fixtures for PaperMap tests."""

import io
from collections.abc import Callable

import pytest
from PIL import Image
from pytest_httpx import HTTPXMock

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
def create_tile_image_content() -> Callable:
    """Factory fixture to create tile image content as bytes.

    Returns:
        A function that creates PNG image bytes with specified color and size.
    """

    def _create(color: str = "green", size: int = 256) -> bytes:
        """Create PNG image content as bytes.

        Args:
            color: Color of the tile image.
            size: Size of the tile image in pixels.

        Returns:
            PNG image content as bytes.
        """
        img = Image.new("RGBA", (size, size), color=color)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()

    return _create


@pytest.fixture
def mock_tile_download(
    httpx_mock: HTTPXMock,
    create_tile_image_content: Callable,
) -> HTTPXMock:
    """Mock all tile download requests to return a green tile image.

    This fixture automatically mocks all HTTP GET requests to return
    a valid PNG tile image, allowing tests to run without network calls.

    Args:
        httpx_mock: The pytest-httpx mock fixture.
        create_tile_image_content: Factory to create tile image content.

    Returns:
        The configured HTTPXMock instance.
    """
    # Disable assertion for unused responses since we add more than needed
    httpx_mock._options.assert_all_responses_were_requested = False  # noqa: SLF001

    # Add enough responses for typical tests (500 tiles for tests with multiple maps)
    tile_content = create_tile_image_content()
    for _ in range(500):
        httpx_mock.add_response(content=tile_content)

    return httpx_mock
