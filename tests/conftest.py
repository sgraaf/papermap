"""Shared fixtures for PaperMap tests."""

import io
from collections.abc import Callable, Generator
from unittest.mock import MagicMock, patch

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
    response.is_success = True
    response.content = buffer.getvalue()
    return response


@pytest.fixture
def create_mock_tile_response() -> Callable[..., MagicMock]:
    """Factory fixture to create mock HTTP responses with tile images."""

    def _create(color: str = "green", size: int = 256) -> MagicMock:
        """Create a mock HTTP response with a tile image.

        Args:
            color: Color of the tile image.
            size: Size of the tile image in pixels.

        Returns:
            MagicMock HTTP response with tile image content.
        """
        img = Image.new("RGBA", (size, size), color=color)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        response = MagicMock()
        response.is_success = True
        response.content = buffer.getvalue()
        return response

    return _create


@pytest.fixture
def create_mock_client() -> Callable[..., MagicMock]:
    """Factory fixture to create mock httpx clients."""

    def _create(response: MagicMock) -> MagicMock:
        """Create a mock httpx client that returns the given response.

        Args:
            response: Mock response to return from client.get.

        Returns:
            MagicMock client configured to return the response.
        """
        mock_client = MagicMock()
        mock_client.get.return_value = response
        return mock_client

    return _create


@pytest.fixture
def mock_tile_download(
    create_mock_tile_response: Callable[..., MagicMock],
    create_mock_client: Callable[..., MagicMock],
) -> Generator[MagicMock, None, None]:
    """Mock the tile download process to avoid network calls.

    Yields:
        MagicMock client configured for tile downloads.
    """
    response = create_mock_tile_response()

    with patch("papermap.papermap.httpx.Client") as mock_client_class:
        mock_client = create_mock_client(response)
        mock_client_class.return_value.__enter__.return_value = mock_client
        yield mock_client
