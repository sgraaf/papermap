"""Unit tests for papermap.gpx module."""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

import pytest
from gpx import GPX, from_string

from papermap.features import CircleMarker, Line
from papermap.gpx import gpx_to_features

if TYPE_CHECKING:
    import types
    from collections.abc import Mapping, Sequence
    from pathlib import Path


@pytest.fixture
def sample_gpx_string() -> str:
    """A small GPX string with waypoints, a route, and a multi-segment track."""
    return """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="papermap-test" xmlns="http://www.topografix.com/GPX/1/1">
  <wpt lat="40.7484" lon="-73.9857"><name>Empire State</name></wpt>
  <wpt lat="40.7128" lon="-74.0060"><name>City Hall</name></wpt>
  <rte><name>RouteA</name>
    <rtept lat="40.7484" lon="-73.9857"/>
    <rtept lat="40.7128" lon="-74.0060"/>
  </rte>
  <trk><name>TrackA</name>
    <trkseg>
      <trkpt lat="40.7484" lon="-73.9857"/>
      <trkpt lat="40.7300" lon="-73.9960"/>
      <trkpt lat="40.7128" lon="-74.0060"/>
    </trkseg>
    <trkseg>
      <trkpt lat="40.7000" lon="-74.0100"/>
      <trkpt lat="40.6900" lon="-74.0200"/>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture
def sample_gpx_file(tmp_path: Path, sample_gpx_string: str) -> Path:
    """A small GPX file with waypoints, a route, and a multi-segment track."""
    sample_gpx_file = tmp_path / "sample.gpx"
    sample_gpx_file.write_text(sample_gpx_string, encoding="utf-8")
    return sample_gpx_file


@pytest.fixture
def sample_gpx_object(sample_gpx_string: str) -> GPX:
    """A GPX object with waypoints, a route, and a multi-segment track."""
    return from_string(sample_gpx_string)


@pytest.fixture
def no_gpx(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def mocked_import(
        name: str,
        globals: Mapping[str, object] | None = None,  # noqa: A002
        locals: Mapping[str, object] | None = None,  # noqa: A002
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> types.ModuleType:
        if name == "gpx":
            msg = "No module named 'gpx'"
            raise ImportError(msg)
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", mocked_import)


class TestGpxParsing:
    """Tests for parsing GPX sources via gpx_to_features."""

    def test_parses_geo_interface_object(self, sample_gpx_object: GPX) -> None:
        features = gpx_to_features(sample_gpx_object)

        # 2 waypoints + 1 route + 2 track segments = 5 features
        assert len(features) == 5
        waypoints = [f for f in features if isinstance(f, CircleMarker)]
        lines = [f for f in features if isinstance(f, Line)]
        assert len(waypoints) == 2
        assert len(lines) == 3  # 1 route + 2 track segments

    def test_parses_file_path(self, sample_gpx_file: Path) -> None:
        features = gpx_to_features(sample_gpx_file)

        assert len(features) == 5
        assert sum(isinstance(f, CircleMarker) for f in features) == 2
        assert sum(isinstance(f, Line) for f in features) == 3

    def test_parses_file_path_as_string(self, sample_gpx_file: Path) -> None:
        features = gpx_to_features(str(sample_gpx_file))
        assert len(features) == 5

    def test_waypoint_coordinate_ordering(self, sample_gpx_object: GPX) -> None:
        # GPX library emits GeoJSON [lon, lat]; internal storage is (lat, lon).
        features = gpx_to_features(sample_gpx_object)
        waypoints = [f for f in features if isinstance(f, CircleMarker)]
        assert waypoints[0].lat == pytest.approx(40.7484)
        assert waypoints[0].lon == pytest.approx(-73.9857)
        assert waypoints[1].lat == pytest.approx(40.7128)
        assert waypoints[1].lon == pytest.approx(-74.0060)

    def test_route_becomes_line(self, sample_gpx_object: GPX) -> None:
        features = gpx_to_features(sample_gpx_object)
        # The route should be the first Line feature (waypoints come first,
        # then the route LineString, then the track MultiLineString segments).
        lines = [f for f in features if isinstance(f, Line)]
        route_line = lines[0]
        assert len(route_line.coordinates) == 2
        assert route_line.coordinates[0] == pytest.approx((40.7484, -73.9857))
        assert route_line.coordinates[1] == pytest.approx((40.7128, -74.0060))

    def test_track_segments_become_separate_lines(self, sample_gpx_object: GPX) -> None:
        features = gpx_to_features(sample_gpx_object)
        lines = [f for f in features if isinstance(f, Line)]
        # Index 0 is the route; indices 1 and 2 are the two track segments.
        seg1, seg2 = lines[1], lines[2]
        assert len(seg1.coordinates) == 3
        assert len(seg2.coordinates) == 2
        assert seg1.coordinates[0] == pytest.approx((40.7484, -73.9857))
        assert seg2.coordinates[0] == pytest.approx((40.7000, -74.0100))

    def test_style_applies_to_all_features(self, sample_gpx_object: GPX) -> None:
        features = gpx_to_features(
            sample_gpx_object,
            style={"stroke_color": "#f00", "stroke_width": 1.5, "fill_color": "#0f0"},
        )
        for f in features:
            if isinstance(f, CircleMarker):
                assert f.stroke_color == "#f00"
                assert f.fill_color == "#0f0"
                assert f.stroke_width == 1.5
            elif isinstance(f, Line):
                assert f.stroke_color == "#f00"
                assert f.stroke_width == 1.5

    def test_empty_gpx_returns_empty_list(self) -> None:
        assert gpx_to_features(GPX()) == []

    def test_nonexistent_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises((FileNotFoundError, OSError)):
            gpx_to_features(tmp_path / "does-not-exist.gpx")

    def test_unsupported_type_raises_typeerror(self) -> None:
        with pytest.raises(TypeError, match="GPX file path"):
            gpx_to_features(12345)  # type: ignore[arg-type, ty:invalid-argument-type]  # pyrefly: ignore[invalid-argument-type]


class TestGpxImportErrorOnMissingExtra:
    """The lazy import should surface a helpful ImportError when gpx is missing."""

    @pytest.mark.usefixtures("no_gpx")
    def test_import_error_when_gpx_unavailable(self, sample_gpx_string: str) -> None:
        with pytest.raises(ImportError, match=r"pip install papermap\[gpx\]"):
            gpx_to_features(sample_gpx_string)
