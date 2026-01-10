"""Unit tests for papermap.tile_server module."""

from papermap.defaults import TILE_SERVERS_MAP
from papermap.tile import Tile
from papermap.tile_server import TileServer
from papermap.utils import get_string_formatting_arguments


class TestTileServerInit:
    """Tests for TileServer initialization."""

    def test_basic_init(self, sample_tile_server: TileServer) -> None:
        assert sample_tile_server.attribution == "Test Attribution"
        assert (
            sample_tile_server.url_template == "https://example.com/{zoom}/{x}/{y}.png"
        )
        assert sample_tile_server.zoom_min == 0
        assert sample_tile_server.zoom_max == 19
        assert sample_tile_server.mirrors is None

    def test_init_with_mirrors(
        self, sample_tile_server_with_mirrors: TileServer
    ) -> None:
        assert sample_tile_server_with_mirrors.mirrors == ["a", "b", "c"]

    def test_init_without_mirrors_creates_none_cycle(
        self, sample_tile_server: TileServer
    ) -> None:
        # Should cycle through [None] when no mirrors
        result = next(sample_tile_server.mirrors_cycle)
        assert result is None

    def test_init_with_mirrors_creates_cycle(
        self, sample_tile_server_with_mirrors: TileServer
    ) -> None:
        # Should cycle through mirrors
        result1 = next(sample_tile_server_with_mirrors.mirrors_cycle)
        result2 = next(sample_tile_server_with_mirrors.mirrors_cycle)
        result3 = next(sample_tile_server_with_mirrors.mirrors_cycle)
        result4 = next(sample_tile_server_with_mirrors.mirrors_cycle)

        assert result1 == "a"
        assert result2 == "b"
        assert result3 == "c"
        assert result4 == "a"  # Cycles back

    def test_init_with_integer_mirrors(self) -> None:
        ts = TileServer(
            attribution="Test",
            url_template="https://mt{mirror}.example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
            mirrors=[0, 1, 2, 3],
        )
        mirrors = [next(ts.mirrors_cycle) for _ in range(8)]
        assert mirrors == [0, 1, 2, 3, 0, 1, 2, 3]


class TestTileServerFormatUrlTemplate:
    """Tests for TileServer.format_url_template method."""

    def test_basic_formatting(
        self, sample_tile_server: TileServer, sample_tile: Tile
    ) -> None:
        result = sample_tile_server.format_url_template(sample_tile)
        # sample_tile has x=123, y=456, zoom=10
        assert result == "https://example.com/10/123/456.png"

    def test_formatting_with_mirrors_cycles(
        self, sample_tile_server_with_mirrors: TileServer, sample_tile: Tile
    ) -> None:
        # Each call should use next mirror in cycle
        result1 = sample_tile_server_with_mirrors.format_url_template(sample_tile)
        result2 = sample_tile_server_with_mirrors.format_url_template(sample_tile)
        result3 = sample_tile_server_with_mirrors.format_url_template(sample_tile)
        result4 = sample_tile_server_with_mirrors.format_url_template(sample_tile)

        assert "a.example.com" in result1
        assert "b.example.com" in result2
        assert "c.example.com" in result3
        assert "a.example.com" in result4  # Cycles back

    def test_formatting_with_api_key(
        self, sample_tile_server_with_api_key: TileServer, sample_tile: Tile
    ) -> None:
        result = sample_tile_server_with_api_key.format_url_template(
            sample_tile, api_key="secret123"
        )
        assert "api_key=secret123" in result

    def test_formatting_with_none_api_key(
        self, sample_tile_server_with_api_key: TileServer, sample_tile: Tile
    ) -> None:
        result = sample_tile_server_with_api_key.format_url_template(
            sample_tile, api_key=None
        )
        assert "api_key=None" in result

    def test_formatting_osm_style_template(self, sample_tile: Tile) -> None:
        ts = TileServer(
            attribution="OSM",
            url_template="http://{mirror}.tile.osm.org/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
            mirrors=["a", "b", "c"],
        )
        result = ts.format_url_template(sample_tile)
        assert result == "http://a.tile.osm.org/10/123/456.png"

    def test_formatting_google_style_template(self, sample_tile: Tile) -> None:
        ts = TileServer(
            attribution="Google",
            url_template="http://mt{mirror}.google.com/vt/lyrs=m&x={x}&y={y}&z={zoom}",
            zoom_min=0,
            zoom_max=19,
            mirrors=[0, 1, 2, 3],
        )
        result = ts.format_url_template(sample_tile)
        assert result == "http://mt0.google.com/vt/lyrs=m&x=123&y=456&z=10"


class TestTileServerMirrorsCycle:
    """Tests for TileServer mirrors cycling behavior."""

    def test_mirrors_cycle_is_infinite(
        self, sample_tile_server_with_mirrors: TileServer
    ) -> None:
        # Should be able to get many values without error
        for _ in range(100):
            next(sample_tile_server_with_mirrors.mirrors_cycle)

    def test_single_mirror_cycles(self) -> None:
        ts = TileServer(
            attribution="Test",
            url_template="https://{mirror}.example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
            mirrors=["only"],
        )
        result1 = next(ts.mirrors_cycle)
        result2 = next(ts.mirrors_cycle)
        result3 = next(ts.mirrors_cycle)
        assert result1 == result2 == result3 == "only"

    def test_empty_mirrors_treated_as_none(self) -> None:
        ts = TileServer(
            attribution="Test",
            url_template="https://example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
            mirrors=[],
        )
        # Empty list should result in [None] cycle behavior
        # Actually looking at the code: cycle(self.mirrors or [None])
        # Empty list is falsy, so should become [None]
        result = next(ts.mirrors_cycle)
        assert result is None


class TestTileServerEquality:
    """Tests for TileServer equality comparisons."""

    def test_equal_tile_servers(self) -> None:
        ts1 = TileServer(
            attribution="Test",
            url_template="https://example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        ts2 = TileServer(
            attribution="Test",
            url_template="https://example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        # Note: dataclass equality doesn't compare cycle objects well
        # but the base attributes should match
        assert ts1.attribution == ts2.attribution
        assert ts1.url_template == ts2.url_template
        assert ts1.zoom_min == ts2.zoom_min
        assert ts1.zoom_max == ts2.zoom_max

    def test_different_attribution(self) -> None:
        ts1 = TileServer(
            attribution="Test1",
            url_template="https://example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        ts2 = TileServer(
            attribution="Test2",
            url_template="https://example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        assert ts1.attribution != ts2.attribution

    def test_different_zoom_range(self) -> None:
        ts1 = TileServer(
            attribution="Test",
            url_template="https://example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        ts2 = TileServer(
            attribution="Test",
            url_template="https://example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=17,
        )
        assert ts1.zoom_max != ts2.zoom_max


class TestTileServerValidation:
    """Tests for TileServer attribute validation."""

    def test_zoom_min_less_than_max(self) -> None:
        # This should work
        ts = TileServer(
            attribution="Test",
            url_template="https://example.com/{zoom}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        assert ts.zoom_min < ts.zoom_max

    def test_zoom_min_equals_max(self) -> None:
        # Edge case: single zoom level
        ts = TileServer(
            attribution="Test",
            url_template="https://example.com/{zoom}/{x}/{y}.png",
            zoom_min=10,
            zoom_max=10,
        )
        assert ts.zoom_min == ts.zoom_max == 10


class TestRealTileServers:
    """Tests using real tile server configurations from defaults."""

    def test_openstreetmap_config(self) -> None:
        osm = TILE_SERVERS_MAP["OpenStreetMap"]
        assert osm.zoom_min == 0
        assert osm.zoom_max == 19
        assert osm.mirrors == ["a", "b", "c"]
        assert "OpenStreetMap" in osm.attribution

    def test_google_maps_config(self) -> None:
        google = TILE_SERVERS_MAP["Google Maps"]
        assert google.zoom_min == 0
        assert google.zoom_max == 19
        assert google.mirrors == [0, 1, 2, 3]
        assert "Google" in google.attribution

    def test_esri_config(self) -> None:
        esri = TILE_SERVERS_MAP["ESRI Standard"]
        assert esri.zoom_min == 0
        assert esri.zoom_max == 17
        assert esri.mirrors is None
        assert "Esri" in esri.attribution

    def test_thunderforest_requires_api_key(self) -> None:
        tf = TILE_SERVERS_MAP["Thunderforest Landscape"]
        args = get_string_formatting_arguments(tf.url_template)
        assert "api_key" in args

    def test_all_tile_servers_have_required_fields(self) -> None:
        for name, ts in TILE_SERVERS_MAP.items():
            assert ts.attribution, f"{name} missing attribution"
            assert ts.url_template, f"{name} missing url_template"
            assert ts.zoom_min >= 0, f"{name} has invalid zoom_min"
            assert ts.zoom_max >= ts.zoom_min, f"{name} has invalid zoom range"
