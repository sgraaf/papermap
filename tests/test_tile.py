"""Unit tests for papermap.tile module."""

from PIL import Image

from papermap.tile import Tile


class TestTileInit:
    """Tests for Tile initialization."""

    def test_basic_init(self) -> None:
        tile = Tile(x=10, y=20, zoom=5, bbox=(0, 0, 256, 256))
        assert tile.x == 10
        assert tile.y == 20
        assert tile.zoom == 5
        assert tile.bbox == (0, 0, 256, 256)
        assert tile.image is None

    def test_init_with_different_bbox(self) -> None:
        tile = Tile(x=0, y=0, zoom=0, bbox=(100, 200, 356, 456))
        assert tile.bbox == (100, 200, 356, 456)

    def test_init_with_high_zoom(self) -> None:
        tile = Tile(x=262143, y=262143, zoom=18, bbox=(0, 0, 256, 256))
        assert tile.x == 262143
        assert tile.y == 262143
        assert tile.zoom == 18


class TestTileSuccess:
    """Tests for Tile.success property."""

    def test_success_false_when_no_image(self, tile: Tile) -> None:
        assert not tile.success

    def test_success_true_when_image_present(self, tile_with_image: Tile) -> None:
        assert tile_with_image.success

    def test_success_false_when_image_is_none(self) -> None:
        tile = Tile(x=0, y=0, zoom=0, bbox=(0, 0, 256, 256))
        tile.image = None
        assert not tile.success

    def test_success_true_after_setting_image(self, tile: Tile) -> None:
        assert not tile.success
        tile.image = Image.new("RGBA", (256, 256), color="red")
        assert tile.success


class TestTileEquality:
    """Tests for Tile equality comparisons."""

    def test_tiles_with_same_values_are_equal(self) -> None:
        tile1 = Tile(x=10, y=20, zoom=5, bbox=(0, 0, 256, 256))
        tile2 = Tile(x=10, y=20, zoom=5, bbox=(0, 0, 256, 256))
        assert tile1 == tile2

    def test_tiles_with_different_x_are_not_equal(self) -> None:
        tile1 = Tile(x=10, y=20, zoom=5, bbox=(0, 0, 256, 256))
        tile2 = Tile(x=11, y=20, zoom=5, bbox=(0, 0, 256, 256))
        assert tile1 != tile2

    def test_tiles_with_different_y_are_not_equal(self) -> None:
        tile1 = Tile(x=10, y=20, zoom=5, bbox=(0, 0, 256, 256))
        tile2 = Tile(x=10, y=21, zoom=5, bbox=(0, 0, 256, 256))
        assert tile1 != tile2

    def test_tiles_with_different_zoom_are_not_equal(self) -> None:
        tile1 = Tile(x=10, y=20, zoom=5, bbox=(0, 0, 256, 256))
        tile2 = Tile(x=10, y=20, zoom=6, bbox=(0, 0, 256, 256))
        assert tile1 != tile2

    def test_tiles_with_different_bbox_are_not_equal(self) -> None:
        tile1 = Tile(x=10, y=20, zoom=5, bbox=(0, 0, 256, 256))
        tile2 = Tile(x=10, y=20, zoom=5, bbox=(10, 10, 266, 266))
        assert tile1 != tile2


class TestTileImageHandling:
    """Tests for handling tile images."""

    def test_setting_image(self) -> None:
        tile = Tile(x=0, y=0, zoom=0, bbox=(0, 0, 256, 256))
        img = Image.new("RGBA", (256, 256), color="white")
        tile.image = img
        assert tile.image is img

    def test_replacing_image(self) -> None:
        tile = Tile(x=0, y=0, zoom=0, bbox=(0, 0, 256, 256))
        img1 = Image.new("RGBA", (256, 256), color="red")
        img2 = Image.new("RGBA", (256, 256), color="blue")
        tile.image = img1
        assert tile.image is img1
        tile.image = img2
        assert tile.image is img2

    def test_clearing_image(self, tile_with_image: Tile) -> None:
        assert tile_with_image.success
        tile_with_image.image = None
        assert not tile_with_image.success
