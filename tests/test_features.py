"""Unit tests for papermap.features module."""

import pytest

from papermap.features import (
    CircleMarker,
    IconMarker,
    Line,
    MapFeature,
    Polygon,
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
