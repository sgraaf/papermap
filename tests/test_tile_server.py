"""Unit tests for papermap.tile_server module."""

from papermap.tile import Tile
from papermap.tile_server import TILE_SERVERS_MAP, TileServer
from papermap.utils import get_string_formatting_arguments


class TestTileServerInit:
    """Tests for TileServer initialization."""

    def test_basic_init(self, tile_server: TileServer) -> None:
        assert tile_server.key == "test-server"
        assert tile_server.name == "Test Server"
        assert tile_server.attribution == "Test Attribution"
        assert tile_server.html_attribution == "Test Attribution"
        assert tile_server.url_template == "https://example.com/{z}/{x}/{y}.png"
        assert tile_server.zoom_min == 0
        assert tile_server.zoom_max == 19
        assert tile_server.bounds is None
        assert tile_server.subdomains is None

    def test_init_with_subdomains(self, tile_server_with_mirrors: TileServer) -> None:
        assert tile_server_with_mirrors.subdomains == ["a", "b", "c"]

    def test_init_without_subdomains_creates_none_cycle(
        self, tile_server: TileServer
    ) -> None:
        # Should cycle through [None] when no subdomains
        result = next(tile_server.subdomains_cycle)
        assert result is None

    def test_init_with_subdomains_creates_cycle(
        self, tile_server_with_mirrors: TileServer
    ) -> None:
        # Should cycle through subdomains
        result1 = next(tile_server_with_mirrors.subdomains_cycle)
        result2 = next(tile_server_with_mirrors.subdomains_cycle)
        result3 = next(tile_server_with_mirrors.subdomains_cycle)
        result4 = next(tile_server_with_mirrors.subdomains_cycle)

        assert result1 == "a"
        assert result2 == "b"
        assert result3 == "c"
        assert result4 == "a"  # Cycles back

    def test_init_with_integer_subdomains(self) -> None:
        ts = TileServer(
            key="test-int-subdomains",
            name="Test Integer Subdomains",
            attribution="Test",
            html_attribution="Test",
            url_template="https://mt{s}.example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
            subdomains=[0, 1, 2, 3],
        )
        subdomains = [next(ts.subdomains_cycle) for _ in range(8)]
        assert subdomains == [0, 1, 2, 3, 0, 1, 2, 3]


class TestTileServerFormatUrlTemplate:
    """Tests for TileServer.format_url_template method."""

    def test_basic_formatting(self, tile_server: TileServer, tile: Tile) -> None:
        result = tile_server.format_url_template(tile)
        # sample_tile has x=123, y=456, zoom=10
        assert result == "https://example.com/10/123/456.png"

    def test_formatting_with_subdomains_cycles(
        self, tile_server_with_mirrors: TileServer, tile: Tile
    ) -> None:
        # Each call should use next subdomain in cycle
        result1 = tile_server_with_mirrors.format_url_template(tile)
        result2 = tile_server_with_mirrors.format_url_template(tile)
        result3 = tile_server_with_mirrors.format_url_template(tile)
        result4 = tile_server_with_mirrors.format_url_template(tile)

        assert "a.example.com" in result1
        assert "b.example.com" in result2
        assert "c.example.com" in result3
        assert "a.example.com" in result4  # Cycles back

    def test_formatting_with_api_key(
        self, tile_server_with_api_key: TileServer, tile: Tile
    ) -> None:
        result = tile_server_with_api_key.format_url_template(tile, api_key="secret123")
        assert "api_key=secret123" in result

    def test_formatting_with_none_api_key(
        self, tile_server_with_api_key: TileServer, tile: Tile
    ) -> None:
        result = tile_server_with_api_key.format_url_template(tile, api_key=None)
        assert "api_key=None" in result

    def test_formatting_osm_style_template(self, tile: Tile) -> None:
        ts = TileServer(
            key="osm-test",
            name="OSM Test",
            attribution="OSM",
            html_attribution="OSM",
            url_template="http://{s}.tile.osm.org/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
            subdomains=["a", "b", "c"],
        )
        result = ts.format_url_template(tile)
        assert result == "http://a.tile.osm.org/10/123/456.png"

    def test_formatting_google_style_template(self, tile: Tile) -> None:
        ts = TileServer(
            key="google-test",
            name="Google Test",
            attribution="Google",
            html_attribution="Google",
            url_template="http://mt{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            zoom_min=0,
            zoom_max=19,
            subdomains=[0, 1, 2, 3],
        )
        result = ts.format_url_template(tile)
        assert result == "http://mt0.google.com/vt/lyrs=m&x=123&y=456&z=10"


class TestTileServerSubdomainsCycle:
    """Tests for TileServer subdomains cycling behavior."""

    def test_subdomains_cycle_is_infinite(
        self, tile_server_with_mirrors: TileServer
    ) -> None:
        # Should be able to get many values without error
        for _ in range(100):
            next(tile_server_with_mirrors.subdomains_cycle)

    def test_single_subdomain_cycles(self) -> None:
        ts = TileServer(
            key="single-subdomain",
            name="Single Subdomain",
            attribution="Test",
            html_attribution="Test",
            url_template="https://{s}.example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
            subdomains=["only"],
        )
        result1 = next(ts.subdomains_cycle)
        result2 = next(ts.subdomains_cycle)
        result3 = next(ts.subdomains_cycle)
        assert result1 == result2 == result3 == "only"

    def test_empty_subdomains_treated_as_none(self) -> None:
        ts = TileServer(
            key="empty-subdomains",
            name="Empty Subdomains",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
            subdomains=[],
        )
        # Empty list should result in [None] cycle behavior
        # Actually looking at the code: cycle(self.subdomains or [None])
        # Empty list is falsy, so should become [None]
        result = next(ts.subdomains_cycle)
        assert result is None


class TestTileServerEquality:
    """Tests for TileServer equality comparisons."""

    def test_equal_tile_servers(self) -> None:
        ts1 = TileServer(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        ts2 = TileServer(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        assert ts1.key == ts2.key
        assert ts1.name == ts2.name
        assert ts1.attribution == ts2.attribution
        assert ts1.html_attribution == ts2.html_attribution
        assert ts1.url_template == ts2.url_template
        assert ts1.zoom_min == ts2.zoom_min
        assert ts1.zoom_max == ts2.zoom_max
        assert ts1.bounds == ts2.bounds
        assert ts1.subdomains == ts2.subdomains

    def test_different_attribution(self) -> None:
        ts1 = TileServer(
            key="test1",
            name="Test1",
            attribution="Test1",
            html_attribution="Test1",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        ts2 = TileServer(
            key="test2",
            name="Test2",
            attribution="Test2",
            html_attribution="Test2",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        assert ts1.attribution != ts2.attribution

    def test_different_zoom_range(self) -> None:
        ts1 = TileServer(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        ts2 = TileServer(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=17,
        )
        assert ts1.zoom_max != ts2.zoom_max


class TestTileServerValidation:
    """Tests for TileServer attribute validation."""

    def test_zoom_min_less_than_max(self) -> None:
        # This should work
        ts = TileServer(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        assert ts.zoom_min < ts.zoom_max

    def test_zoom_min_equals_max(self) -> None:
        # Edge case: single zoom level
        ts = TileServer(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=10,
            zoom_max=10,
        )
        assert ts.zoom_min == ts.zoom_max == 10


class TestRealTileServers:
    """Tests using real tile server configurations from defaults."""

    def test_openstreetmap_config(self) -> None:
        osm = TILE_SERVERS_MAP["OpenStreetMap"]
        assert osm.key == "openstreetmap"
        assert osm.name == "OpenStreetMap"
        assert osm.zoom_min == 0
        assert osm.zoom_max == 19
        # Note: subdomains changed to None in new architecture (direct URL)
        assert "OpenStreetMap" in osm.attribution

    def test_google_maps_config(self) -> None:
        google = TILE_SERVERS_MAP["Google Maps"]
        assert google.key == "google-maps"
        assert google.name == "Google Maps"
        assert google.zoom_min == 0
        assert google.zoom_max == 20  # Updated to match new config
        assert google.subdomains == [0, 1, 2, 3]
        assert "Google" in google.attribution

    def test_esri_config(self) -> None:
        # Test the new canonical name
        esri = TILE_SERVERS_MAP["Esri WorldStreetMap"]
        assert esri.key == "esri-worldstreetmap"
        assert esri.name == "Esri WorldStreetMap"
        assert esri.zoom_min == 0
        assert esri.zoom_max == 17
        assert esri.subdomains is None
        assert "Esri" in esri.attribution

    def test_esri_legacy_alias(self) -> None:
        # Test that legacy alias still works for backward compatibility
        esri = TILE_SERVERS_MAP["ESRI Standard"]
        assert "Esri" in esri.attribution

    def test_thunderforest_requires_api_key(self) -> None:
        tf = TILE_SERVERS_MAP["Thunderforest Landscape"]
        args = get_string_formatting_arguments(tf.url_template)
        assert "a" in args

    def test_all_tile_servers_have_required_fields(self) -> None:
        for name, ts in TILE_SERVERS_MAP.items():
            assert ts.key, f"{name} missing key"
            assert ts.name, f"{name} missing name"
            assert ts.attribution, f"{name} missing attribution"
            assert ts.html_attribution, f"{name} missing html_attribution"
            assert ts.url_template, f"{name} missing url_template"
            assert ts.zoom_min >= 0, f"{name} has invalid zoom_min"
            assert ts.zoom_max >= ts.zoom_min, f"{name} has invalid zoom range"
