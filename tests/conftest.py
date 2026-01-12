"""Shared fixtures for PaperMap tests."""

import io

import pytest
from PIL import Image

from papermap.tile import Tile
from papermap.tile_server import TileServer


@pytest.fixture
def tile() -> Tile:
    """Return a sample tile for testing."""
    return Tile(x=123, y=456, zoom=10, bbox=(0, 0, 256, 256))


@pytest.fixture
def tile_image() -> Image.Image:
    """Return a sample tile image for testing."""
    return Image.new("RGBA", (256, 256), color="blue")


@pytest.fixture
def tile_with_image(tile: Tile, tile_image: Image.Image) -> Tile:
    """Return a sample tile with an image for testing."""
    tile.image = tile_image
    return tile


@pytest.fixture
def tile_image_content(tile_image: Image.Image) -> bytes:
    """Return a sample tile image as bytes for testing."""
    buffer = io.BytesIO()
    tile_image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def tile_server() -> TileServer:
    """Return a sample tile server for testing."""
    return TileServer(
        attribution="Test Attribution",
        url_template="https://example.com/{zoom}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=19,
    )


@pytest.fixture
def tile_server_with_mirrors() -> TileServer:
    """Return a sample tile server with mirrors for testing."""
    return TileServer(
        attribution="Test Attribution",
        url_template="https://{mirror}.example.com/{zoom}/{x}/{y}.png",
        zoom_min=0,
        zoom_max=19,
        mirrors=["a", "b", "c"],
    )


@pytest.fixture
def tile_server_with_api_key() -> TileServer:
    """Return a sample tile server requiring an API key for testing."""
    return TileServer(
        attribution="Test Attribution",
        url_template="https://example.com/{zoom}/{x}/{y}.png?api_key={api_key}",
        zoom_min=0,
        zoom_max=19,
    )
