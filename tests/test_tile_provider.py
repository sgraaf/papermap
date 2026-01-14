"""Unit tests for papermap.tile_provider module."""

from papermap.tile import Tile
from papermap.tile_provider import TileProvider
from papermap.tile_providers import KEY_TO_TILE_PROVIDER
from papermap.utils import get_string_formatting_arguments


class TestTileProviderInit:
    """Tests for TileProvider initialization."""

    def test_basic_init(self, tile_provider: TileProvider) -> None:
        assert tile_provider.key == "test-provider"
        assert tile_provider.name == "Test Provider"
        assert tile_provider.attribution == "Test Attribution"
        assert tile_provider.html_attribution == "Test Attribution"
        assert tile_provider.url_template == "https://example.com/{z}/{x}/{y}.png"
        assert tile_provider.zoom_min == 0
        assert tile_provider.zoom_max == 19
        assert tile_provider.bounds is None
        assert tile_provider.subdomains is None

    def test_init_with_subdomains(
        self, tile_provider_with_mirrors: TileProvider
    ) -> None:
        assert tile_provider_with_mirrors.subdomains == ["a", "b", "c"]

    def test_init_without_subdomains_creates_none_cycle(
        self, tile_provider: TileProvider
    ) -> None:
        # Should cycle through [None] when no subdomains
        result = next(tile_provider.subdomains_cycle)
        assert result is None

    def test_init_with_subdomains_creates_cycle(
        self, tile_provider_with_mirrors: TileProvider
    ) -> None:
        # Should cycle through subdomains
        result1 = next(tile_provider_with_mirrors.subdomains_cycle)
        result2 = next(tile_provider_with_mirrors.subdomains_cycle)
        result3 = next(tile_provider_with_mirrors.subdomains_cycle)
        result4 = next(tile_provider_with_mirrors.subdomains_cycle)

        assert result1 == "a"
        assert result2 == "b"
        assert result3 == "c"
        assert result4 == "a"  # Cycles back

    def test_init_with_integer_subdomains(self) -> None:
        ts = TileProvider(
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


class TestTileProviderFormatUrlTemplate:
    """Tests for TileProvider.format_url_template method."""

    def test_basic_formatting(self, tile_provider: TileProvider, tile: Tile) -> None:
        result = tile_provider.format_url_template(tile)
        # sample_tile has x=123, y=456, zoom=10
        assert result == "https://example.com/10/123/456.png"

    def test_formatting_with_subdomains_cycles(
        self, tile_provider_with_mirrors: TileProvider, tile: Tile
    ) -> None:
        # Each call should use next subdomain in cycle
        result1 = tile_provider_with_mirrors.format_url_template(tile)
        result2 = tile_provider_with_mirrors.format_url_template(tile)
        result3 = tile_provider_with_mirrors.format_url_template(tile)
        result4 = tile_provider_with_mirrors.format_url_template(tile)

        assert "a.example.com" in result1
        assert "b.example.com" in result2
        assert "c.example.com" in result3
        assert "a.example.com" in result4  # Cycles back

    def test_formatting_with_api_key(
        self, tile_provider_with_api_key: TileProvider, tile: Tile
    ) -> None:
        result = tile_provider_with_api_key.format_url_template(
            tile, api_key="secret123"
        )
        assert "api_key=secret123" in result

    def test_formatting_with_none_api_key(
        self, tile_provider_with_api_key: TileProvider, tile: Tile
    ) -> None:
        result = tile_provider_with_api_key.format_url_template(tile, api_key=None)
        assert "api_key=None" in result

    def test_formatting_osm_style_template(self, tile: Tile) -> None:
        ts = TileProvider(
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
        ts = TileProvider(
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


class TestTileProviderSubdomainsCycle:
    """Tests for TileProvider subdomains cycling behavior."""

    def test_subdomains_cycle_is_infinite(
        self, tile_provider_with_mirrors: TileProvider
    ) -> None:
        # Should be able to get many values without error
        for _ in range(100):
            next(tile_provider_with_mirrors.subdomains_cycle)

    def test_single_subdomain_cycles(self) -> None:
        ts = TileProvider(
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
        ts = TileProvider(
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


class TestTileProviderEquality:
    """Tests for TileProvider equality comparisons."""

    def test_equal_tile_providers(self) -> None:
        ts1 = TileProvider(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        ts2 = TileProvider(
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
        ts1 = TileProvider(
            key="test1",
            name="Test1",
            attribution="Test1",
            html_attribution="Test1",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        ts2 = TileProvider(
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
        ts1 = TileProvider(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=19,
        )
        ts2 = TileProvider(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=0,
            zoom_max=17,
        )
        assert ts1.zoom_max != ts2.zoom_max


class TestTileProviderValidation:
    """Tests for TileProvider attribute validation."""

    def test_zoom_min_less_than_max(self) -> None:
        # This should work
        ts = TileProvider(
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
        ts = TileProvider(
            key="test",
            name="Test",
            attribution="Test",
            html_attribution="Test",
            url_template="https://example.com/{z}/{x}/{y}.png",
            zoom_min=10,
            zoom_max=10,
        )
        assert ts.zoom_min == ts.zoom_max == 10


class TestRealTileProviders:
    """Tests using real tile provider configurations from defaults."""

    def test_openstreetmap_config(self) -> None:
        osm = KEY_TO_TILE_PROVIDER["openstreetmap"]
        assert osm.key == "openstreetmap"
        assert osm.name == "OpenStreetMap"
        assert osm.zoom_min == 0
        assert osm.zoom_max == 19
        # Note: subdomains changed to None in new architecture (direct URL)
        assert "OpenStreetMap" in osm.attribution

    def test_google_maps_config(self) -> None:
        google = KEY_TO_TILE_PROVIDER["google-maps"]
        assert google.key == "google-maps"
        assert google.name == "Google Maps"
        assert google.zoom_min == 0
        assert google.zoom_max == 20  # Updated to match new config
        assert google.subdomains == [0, 1, 2, 3]
        assert "Google" in google.attribution

    def test_esri_config(self) -> None:
        # Test the canonical key lookup
        esri = KEY_TO_TILE_PROVIDER["esri-worldstreetmap"]
        assert esri.key == "esri-worldstreetmap"
        assert esri.name == "Esri WorldStreetMap"
        assert esri.zoom_min == 0
        assert esri.zoom_max == 17
        assert esri.subdomains is None
        assert "Esri" in esri.attribution

    def test_thunderforest_requires_api_key(self) -> None:
        tf = KEY_TO_TILE_PROVIDER["thunderforest-landscape"]
        args = get_string_formatting_arguments(tf.url_template)
        assert "a" in args

    def test_all_tile_providers_have_required_fields(self) -> None:
        for key, ts in KEY_TO_TILE_PROVIDER.items():
            assert ts.key, f"{key} missing key"
            assert ts.name, f"{key} missing name"
            assert ts.attribution, f"{key} missing attribution"
            assert ts.html_attribution, f"{key} missing html_attribution"
            assert ts.url_template, f"{key} missing url_template"
            assert ts.zoom_min >= 0, f"{key} has invalid zoom_min"
            assert ts.zoom_max >= ts.zoom_min, f"{key} has invalid zoom range"
