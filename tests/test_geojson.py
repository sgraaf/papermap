"""Unit tests for papermap.features module."""

import json
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from papermap.features import CircleMarker, IconMarker, Line, Polygon
from papermap.geojson import SupportsGeoInterface, geojson_to_features


@pytest.fixture
def sample_geojson_string() -> str:
    """A small GeoJSON string with Points, a LineString, and a MultiLineString."""
    return """\
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.9857, 40.7484]
      },
      "properties": {
        "name": "Empire State"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-74.006, 40.7128]
      },
      "properties": {
        "name": "City Hall"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[-73.9857, 40.7484], [-74.006, 40.7128]],
        "bbox": [-74.006, 40.7128, -73.9857, 40.7484]
      },
      "properties": {
        "name": "RouteA"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "MultiLineString",
        "coordinates": [
          [
            [-73.9857, 40.7484],
            [-73.996, 40.73],
            [-74.006, 40.7128]
          ],
          [
            [-74.01, 40.7],
            [-74.02, 40.69]
          ]
        ],
        "bbox": [-74.02, 40.69, -73.9857, 40.7484]
      },
      "properties": {
        "name": "TrackA"
      }
    }
  ]
}
"""


@pytest.fixture
def sample_geojson_file(tmp_path: Path, sample_geojson_string: str) -> Path:
    """A small GeoJSON file with waypoints, a route, and a multi-segment track."""
    sample_geojson_file = tmp_path / "sample.geojson"
    sample_geojson_file.write_text(sample_geojson_string, encoding="utf-8")
    return sample_geojson_file


@pytest.fixture
def sample_geojson_object(sample_geojson_string: str) -> dict[str, Any]:
    """A GeoJSON object with waypoints, a route, and a multi-segment track."""
    return json.loads(sample_geojson_string)


class TestGeojsonParsing:
    """Tests for parsing each GeoJSON geometry type."""

    def test_parses_geo_interface_object(
        self, sample_geojson_object: dict[str, Any]
    ) -> None:
        features = geojson_to_features(sample_geojson_object)

        # 2 waypoints + 1 route + 2 track segments = 5 features
        assert len(features) == 5
        waypoints = [f for f in features if isinstance(f, CircleMarker)]
        lines = [f for f in features if isinstance(f, Line)]
        assert len(waypoints) == 2
        assert len(lines) == 3  # 1 route + 2 track segments

    def test_parses_file_path(self, sample_geojson_file: Path) -> None:
        features = geojson_to_features(sample_geojson_file)

        assert len(features) == 5
        assert sum(isinstance(f, CircleMarker) for f in features) == 2
        assert sum(isinstance(f, Line) for f in features) == 3

    def test_parses_file_path_as_string(self, sample_geojson_file: Path) -> None:
        features = geojson_to_features(str(sample_geojson_file))
        assert len(features) == 5

    def test_waypoint_coordinate_ordering(
        self, sample_geojson_object: dict[str, Any]
    ) -> None:
        # GeoJSON library emits GeoJSON [lon, lat]; internal storage is (lat, lon).
        features = geojson_to_features(sample_geojson_object)
        waypoints = [f for f in features if isinstance(f, CircleMarker)]
        assert waypoints[0].lat == pytest.approx(40.7484)
        assert waypoints[0].lon == pytest.approx(-73.9857)
        assert waypoints[1].lat == pytest.approx(40.7128)
        assert waypoints[1].lon == pytest.approx(-74.0060)

    def test_route_becomes_line(self, sample_geojson_object: dict[str, Any]) -> None:
        features = geojson_to_features(sample_geojson_object)
        # The route should be the first Line feature (waypoints come first,
        # then the route LineString, then the track MultiLineString segments).
        lines = [f for f in features if isinstance(f, Line)]
        route_line = lines[0]
        assert len(route_line.coordinates) == 2
        assert route_line.coordinates[0] == pytest.approx((40.7484, -73.9857))
        assert route_line.coordinates[1] == pytest.approx((40.7128, -74.0060))

    def test_track_segments_become_separate_lines(
        self, sample_geojson_object: dict[str, Any]
    ) -> None:
        features = geojson_to_features(sample_geojson_object)
        lines = [f for f in features if isinstance(f, Line)]
        # Index 0 is the route; indices 1 and 2 are the two track segments.
        seg1, seg2 = lines[1], lines[2]
        assert len(seg1.coordinates) == 3
        assert len(seg2.coordinates) == 2
        assert seg1.coordinates[0] == pytest.approx((40.7484, -73.9857))
        assert seg2.coordinates[0] == pytest.approx((40.7000, -74.0100))

    def test_style_applies_to_all_features(
        self, sample_geojson_object: dict[str, Any]
    ) -> None:
        features = geojson_to_features(
            sample_geojson_object,
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

    def test_empty_geojson_returns_empty_list(self) -> None:
        assert geojson_to_features({}) == []

    def test_nonexistent_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises((FileNotFoundError, OSError)):
            geojson_to_features(tmp_path / "does-not-exist.geojson")

    def test_unsupported_type_raises_typeerror(self) -> None:
        with pytest.raises(TypeError, match="Expected a GeoJSON dict"):
            geojson_to_features(12345)  # type: ignore[arg-type, ty:invalid-argument-type]  # pyrefly: ignore[invalid-argument-type]

    def test_point(self) -> None:
        features = geojson_to_features({"type": "Point", "coordinates": [100.0, 0.0]})
        assert len(features) == 1
        assert isinstance(features[0], CircleMarker)
        assert features[0].lat == 0.0
        assert features[0].lon == 100.0

    def test_multipoint(self) -> None:
        features = geojson_to_features(
            {
                "type": "MultiPoint",
                "coordinates": [[100.0, 0.0], [101.0, 1.0]],
            }
        )
        assert len(features) == 2
        first, second = features
        assert isinstance(first, CircleMarker)
        assert isinstance(second, CircleMarker)
        assert first.lat == 0.0
        assert second.lat == 1.0

    def test_linestring(self) -> None:
        features = geojson_to_features(
            {
                "type": "LineString",
                "coordinates": [[100.0, 0.0], [101.0, 1.0], [102.0, 2.0]],
            }
        )
        assert len(features) == 1
        assert isinstance(features[0], Line)
        assert features[0].coordinates == [(0.0, 100.0), (1.0, 101.0), (2.0, 102.0)]

    def test_multilinestring(self) -> None:
        features = geojson_to_features(
            {
                "type": "MultiLineString",
                "coordinates": [
                    [[100.0, 0.0], [101.0, 1.0]],
                    [[102.0, 2.0], [103.0, 3.0]],
                ],
            }
        )
        assert len(features) == 2
        assert all(isinstance(f, Line) for f in features)

    def test_polygon_without_holes(self) -> None:
        features = geojson_to_features(
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [100.0, 0.0],
                        [101.0, 0.0],
                        [101.0, 1.0],
                        [100.0, 1.0],
                        [100.0, 0.0],
                    ]
                ],
            }
        )
        assert len(features) == 1
        assert isinstance(features[0], Polygon)
        assert len(features[0].coordinates) == 1
        assert features[0].coordinates[0][0] == (0.0, 100.0)

    def test_polygon_with_hole(self) -> None:
        features = geojson_to_features(
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [100.0, 0.0],
                        [103.0, 0.0],
                        [103.0, 3.0],
                        [100.0, 3.0],
                        [100.0, 0.0],
                    ],
                    [
                        [101.0, 1.0],
                        [102.0, 1.0],
                        [102.0, 2.0],
                        [101.0, 2.0],
                        [101.0, 1.0],
                    ],
                ],
            }
        )
        assert len(features) == 1
        poly = features[0]
        assert isinstance(poly, Polygon)
        assert len(poly.coordinates) == 2

    def test_multipolygon(self) -> None:
        features = geojson_to_features(
            {
                "type": "MultiPolygon",
                "coordinates": [
                    [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 0.0]]],
                    [[[200.0, 2.0], [201.0, 2.0], [201.0, 3.0], [200.0, 2.0]]],
                ],
            }
        )
        assert len(features) == 2
        assert all(isinstance(f, Polygon) for f in features)

    def test_geometrycollection(self) -> None:
        features = geojson_to_features(
            {
                "type": "GeometryCollection",
                "geometries": [
                    {"type": "Point", "coordinates": [100.0, 0.0]},
                    {
                        "type": "LineString",
                        "coordinates": [[100.0, 0.0], [101.0, 1.0]],
                    },
                ],
            }
        )
        assert len(features) == 2
        assert isinstance(features[0], CircleMarker)
        assert isinstance(features[1], Line)

    def test_feature_unwraps_geometry(self) -> None:
        features = geojson_to_features(
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Point", "coordinates": [100.0, 0.0]},
            }
        )
        assert len(features) == 1
        assert isinstance(features[0], CircleMarker)

    def test_feature_with_null_geometry(self) -> None:
        features = geojson_to_features(
            {"type": "Feature", "properties": {}, "geometry": None}
        )
        assert features == []

    def test_feature_collection(self) -> None:
        features = geojson_to_features(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [10, 20]},
                        "properties": {},
                    },
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[1, 2], [3, 4]],
                        },
                        "properties": {},
                    },
                ],
            }
        )
        assert len(features) == 2
        assert isinstance(features[0], CircleMarker)
        assert isinstance(features[1], Line)

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported"):
            geojson_to_features({"type": "Banana", "coordinates": []})

    def test_non_dict_raises(self) -> None:
        with pytest.raises(TypeError):
            geojson_to_features(42)  # type: ignore[arg-type, ty:invalid-argument-type]


class TestGeoInterface:
    """Tests for parsing objects implementing the __geo_interface__ protocol."""

    def test_geo_interface_object(self) -> None:
        class FakePoint:
            __geo_interface__ = {"type": "Point", "coordinates": [5.0, 6.0]}  # noqa: RUF012

        features = geojson_to_features(FakePoint())
        assert len(features) == 1
        assert isinstance(features[0], CircleMarker)
        assert features[0].lat == 6.0
        assert features[0].lon == 5.0

    def test_geo_interface_inside_feature(self) -> None:
        class FakeShape:
            __geo_interface__ = {  # noqa: RUF012
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1.0, 2.0]},
                "properties": {"stroke": "#abcdef"},
            }

        features = geojson_to_features(FakeShape())
        assert len(features) == 1
        marker = features[0]
        assert isinstance(marker, CircleMarker)
        assert marker.stroke_color == "#abcdef"


class TestSimpleStyle:
    """Tests for simplestyle-spec property handling."""

    def test_properties_override_style_arg(self) -> None:
        feat: dict[str, Any] = {
            "type": "Feature",
            "properties": {"stroke": "#ff0000", "stroke-width": 2.0},
            "geometry": {
                "type": "LineString",
                "coordinates": [[0.0, 0.0], [1.0, 1.0]],
            },
        }
        features = geojson_to_features(
            feat, style={"stroke_color": "#000000", "stroke_width": 0.5}
        )
        line = features[0]
        assert isinstance(line, Line)
        assert line.stroke_color == "#ff0000"
        assert line.stroke_width == 2.0

    def test_style_arg_used_when_no_properties(self) -> None:
        features = geojson_to_features(
            {"type": "Point", "coordinates": [0.0, 0.0]},
            style={"fill_color": "#abc123", "radius": 4.0},
        )
        marker = features[0]
        assert isinstance(marker, CircleMarker)
        assert marker.fill_color == "#abc123"
        assert marker.radius == 4.0

    def test_style_arg_filters_to_relevant_keys(self) -> None:
        # ``radius`` is not a Line field; passing it as default style for
        # mixed FeatureCollections should not crash the parser.
        fc: dict[str, Any] = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[0.0, 0.0], [1.0, 1.0]],
                    },
                    "properties": {},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
                    "properties": {},
                },
            ],
        }
        features = geojson_to_features(
            fc, style={"radius": 5.0, "stroke_color": "#123"}
        )
        assert len(features) == 2
        assert isinstance(features[0], Line)
        assert features[0].stroke_color == "#123"
        assert isinstance(features[1], CircleMarker)
        assert features[1].radius == 5.0
        assert features[1].stroke_color == "#123"


class TestCoordinateOrdering:
    """Tests verifying GeoJSON [lon, lat] is swapped to (lat, lon)."""

    def test_point_ordering(self) -> None:
        features = geojson_to_features({"type": "Point", "coordinates": [100.0, 0.0]})
        marker = features[0]
        assert isinstance(marker, CircleMarker)
        assert marker.lat == 0.0
        assert marker.lon == 100.0

    def test_linestring_ordering(self) -> None:
        features = geojson_to_features(
            {
                "type": "LineString",
                "coordinates": [[100.0, 0.0], [101.0, 1.0]],
            }
        )
        line = features[0]
        assert isinstance(line, Line)
        assert line.coordinates[0] == (0.0, 100.0)
        assert line.coordinates[1] == (1.0, 101.0)


class TestSupportsGeoInterface:
    """Tests for the runtime-checkable SupportsGeoInterface protocol."""

    def test_object_with_geo_interface_is_recognised(self) -> None:
        class Shape:
            __geo_interface__ = {"type": "Point", "coordinates": [0.0, 0.0]}  # noqa: RUF012

        assert isinstance(Shape(), SupportsGeoInterface)

    def test_object_without_geo_interface_is_rejected(self) -> None:
        assert not isinstance(object(), SupportsGeoInterface)
        assert not isinstance({"type": "Point"}, SupportsGeoInterface)


class TestIconMarkerEquality:
    """IconMarker equality must not depend on the lazy-loaded image cache."""

    def test_equality_independent_of_loaded_icon(self) -> None:
        a = IconMarker(0.0, 0.0, icon="path.png")
        b = IconMarker(0.0, 0.0, icon="path.png")
        assert a == b
        # Simulate a render populating the cache on one of the markers.
        a._loaded_icon = Image.new("RGBA", (1, 1))  # noqa: SLF001
        assert a == b


class TestPolygonDegenerateRings:
    """Polygon parsing should not produce degenerate inner-ring artefacts."""

    def test_polygon_with_degenerate_inner_ring_parses(self) -> None:
        # The hole has only two distinct vertices — too few to form a ring.
        features = geojson_to_features(
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [0.0, 0.0],
                        [1.0, 0.0],
                        [1.0, 1.0],
                        [0.0, 1.0],
                        [0.0, 0.0],
                    ],
                    [[0.5, 0.5], [0.5, 0.5]],
                ],
            }
        )
        assert len(features) == 1
        assert isinstance(features[0], Polygon)
