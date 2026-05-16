"""Unit tests for papermap.features module."""

from typing import Any

import pytest
from PIL import Image

from papermap.features import (
    CircleMarker,
    IconMarker,
    Line,
    MapFeature,
    Polygon,
    SupportsGeoInterface,
    geojson_to_features,
    iter_feature_coordinates,
)


class TestDataclassDefaults:
    """Tests for default values of feature dataclasses."""

    def test_circle_marker_defaults(self) -> None:
        m = CircleMarker(40.0, -74.0)
        assert m.lat == 40.0
        assert m.lon == -74.0
        assert m.radius == 2.0
        assert m.stroke_color == "#000"
        assert m.stroke_width == 0.5
        assert m.fill_color == "#fff"
        assert m.opacity == 1.0
        assert m.stroke_opacity is None
        assert m.fill_opacity is None

    def test_icon_marker_defaults(self) -> None:
        m = IconMarker(40.0, -74.0, icon="path/to/icon.png")
        assert m.icon == "path/to/icon.png"
        assert m.width == 5.0
        assert m.height is None
        assert m.anchor == (0.5, 1.0)
        assert m.opacity == 1.0

    def test_line_defaults(self) -> None:
        line = Line([(40.0, -74.0), (41.0, -74.0)])
        assert line.coordinates == [(40.0, -74.0), (41.0, -74.0)]
        assert line.stroke_color == "#000"
        assert line.stroke_width == 0.5
        assert line.opacity == 1.0
        assert line.stroke_opacity is None

    def test_polygon_defaults(self) -> None:
        rings = [[(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]]
        p = Polygon(rings)
        assert p.coordinates == rings
        assert p.stroke_color == "#000"
        assert p.stroke_width == 0.5
        assert p.fill_color is None
        assert p.opacity == 1.0

    @pytest.mark.parametrize(
        "cls",
        [CircleMarker, IconMarker, Line, Polygon],
    )
    def test_dataclasses_use_slots(self, cls: type) -> None:
        assert hasattr(cls, "__slots__")


class TestGeojsonParsing:
    """Tests for parsing each GeoJSON geometry type."""

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


class TestMapFeatureUnion:
    """Tests for the MapFeature type alias."""

    def test_union_includes_all_dataclasses(self) -> None:
        # Type alias is satisfied by isinstance checks against the underlying types
        marker: MapFeature = CircleMarker(0.0, 0.0)
        line: MapFeature = Line([(0.0, 0.0), (1.0, 1.0)])
        poly: MapFeature = Polygon([[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)]])
        icon: MapFeature = IconMarker(0.0, 0.0, icon="x.png")
        for f in (marker, line, poly, icon):
            assert isinstance(f, (CircleMarker, IconMarker, Line, Polygon))


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


class TestIterFeatureCoordinates:
    """Tests for the iter_feature_coordinates helper."""

    def test_circle_marker_yields_single_coordinate(self) -> None:
        marker = CircleMarker(40.7128, -74.0060)
        assert list(iter_feature_coordinates(marker)) == [(40.7128, -74.0060)]

    def test_icon_marker_yields_single_coordinate(self) -> None:
        marker = IconMarker(40.7128, -74.0060, icon="path/to/icon.png")
        assert list(iter_feature_coordinates(marker)) == [(40.7128, -74.0060)]

    def test_line_yields_every_vertex_in_order(self) -> None:
        line = Line([(40.0, -75.0), (41.0, -74.0), (42.0, -73.0)])
        assert list(iter_feature_coordinates(line)) == [
            (40.0, -75.0),
            (41.0, -74.0),
            (42.0, -73.0),
        ]

    def test_polygon_yields_outer_then_holes(self) -> None:
        outer = [(40.0, -75.0), (42.0, -75.0), (42.0, -73.0), (40.0, -75.0)]
        hole = [(40.5, -74.5), (41.5, -74.5), (41.5, -73.5), (40.5, -74.5)]
        polygon = Polygon([outer, hole])
        assert list(iter_feature_coordinates(polygon)) == [*outer, *hole]

    def test_empty_polygon_yields_nothing(self) -> None:
        assert list(iter_feature_coordinates(Polygon([]))) == []

    def test_empty_line_yields_nothing(self) -> None:
        assert list(iter_feature_coordinates(Line([]))) == []


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
