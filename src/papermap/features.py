"""Map feature dataclasses and a GeoJSON parser.

Features are geometries — circle markers, icon markers, lines, and polygons —
that are overlaid on the map's base layer. They can be constructed directly
from one of the dataclasses in this module, or parsed from a GeoJSON object
(or any object implementing the ``__geo_interface__`` protocol).

Coordinate ordering convention: all dataclass coordinates use ``(lat, lon)``
ordering, matching :class:`PaperMap` and the geodesy helpers. The
:func:`geojson_to_features` parser is the only place that swaps GeoJSON's
``[lon, lat]`` order to the internal ``(lat, lon)`` form.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from pathlib import Path

    from PIL import Image


@dataclass(slots=True)
class CircleMarker:
    """A circular marker at a single geographic position.

    Args:
        lat: Latitude of the marker centre.
        lon: Longitude of the marker centre.
        radius: Marker radius on paper, in mm. Defaults to ``2.0``.
        stroke_color: Outline colour as a CSS-style hex string, or ``None``
            to omit the outline. Defaults to ``"#000"``.
        stroke_width: Outline width on paper, in mm. Defaults to ``0.5``.
        fill_color: Fill colour as a CSS-style hex string, or ``None`` to
            omit the fill. Defaults to ``"#fff"``.
        opacity: Overall opacity, in ``[0, 1]``. Defaults to ``1.0``.
        stroke_opacity: Outline opacity. Defaults to ``opacity`` when ``None``.
        fill_opacity: Fill opacity. Defaults to ``opacity`` when ``None``.
    """

    lat: float
    lon: float
    radius: float = 2.0
    stroke_color: str | None = "#000"
    stroke_width: float = 0.5
    fill_color: str | None = "#fff"
    opacity: float = 1.0
    stroke_opacity: float | None = None
    fill_opacity: float | None = None


@dataclass(slots=True)
class IconMarker:
    """An image marker at a single geographic position.

    The image is anchored to the geographic position via :attr:`anchor`,
    expressed as fractions of the icon width and height. The default
    ``(0.5, 1.0)`` anchors the bottom centre of the icon to the position,
    matching the typical map-pin convention.

    Args:
        lat: Latitude of the anchor point.
        lon: Longitude of the anchor point.
        icon: Path to an image file or a :class:`PIL.Image.Image` instance.
        width: Rendered icon width on paper, in mm. Defaults to ``5.0``.
        height: Rendered icon height on paper, in mm. When ``None``, the
            height is derived from ``width`` and the icon's aspect ratio.
        anchor: Anchor point within the icon as ``(x, y)`` fractions of the
            icon width and height. Defaults to ``(0.5, 1.0)``
            (bottom centre).
        opacity: Opacity of the rendered icon, in ``[0, 1]``. Defaults to
            ``1.0``.
    """

    lat: float
    lon: float
    icon: str | Path | Image.Image
    width: float = 5.0
    height: float | None = None
    anchor: tuple[float, float] = (0.5, 1.0)
    opacity: float = 1.0
    _loaded_icon: Image.Image | None = field(
        init=False, default=None, repr=False, compare=False
    )


@dataclass(slots=True)
class Line:
    """A polyline connecting two or more geographic positions.

    Args:
        coordinates: Sequence of ``(lat, lon)`` pairs. Must contain at
            least two positions.
        stroke_color: Stroke colour as a CSS-style hex string. Defaults to
            ``"#000"``.
        stroke_width: Stroke width on paper, in mm. Defaults to ``0.5``.
        opacity: Stroke opacity, in ``[0, 1]``. Defaults to ``1.0``.
        stroke_opacity: Stroke opacity. Defaults to ``opacity`` when
            ``None``.
    """

    coordinates: Sequence[tuple[float, float]]
    stroke_color: str = "#000"
    stroke_width: float = 0.5
    opacity: float = 1.0
    stroke_opacity: float | None = None


@dataclass(slots=True)
class Polygon:
    """A polygon, optionally with interior holes.

    Args:
        coordinates: Sequence of rings, where each ring is a sequence of
            ``(lat, lon)`` pairs. The first ring is the outer boundary;
            any subsequent rings are interior holes.
        stroke_color: Outline colour as a CSS-style hex string, or ``None``
            to omit the outline. Defaults to ``"#000"``.
        stroke_width: Outline width on paper, in mm. Defaults to ``0.5``.
        fill_color: Fill colour as a CSS-style hex string, or ``None`` for
            an unfilled polygon. Defaults to ``None``.
        opacity: Overall opacity, in ``[0, 1]``. Defaults to ``1.0``.
        stroke_opacity: Outline opacity. Defaults to ``opacity`` when
            ``None``.
        fill_opacity: Fill opacity. Defaults to ``opacity`` when ``None``.

    Note:
        A polygon spanning the ±180° anti-meridian will draw across the
        entire map (the geometry is not auto-split). Pre-split such
        polygons before adding them.
    """

    coordinates: Sequence[Sequence[tuple[float, float]]]
    stroke_color: str | None = "#000"
    stroke_width: float = 0.5
    fill_color: str | None = None
    opacity: float = 1.0
    stroke_opacity: float | None = None
    fill_opacity: float | None = None


MapFeature: TypeAlias = CircleMarker | IconMarker | Line | Polygon
"""Union type alias for any feature that can be rendered on the map."""


def iter_feature_coordinates(feature: MapFeature) -> Iterator[tuple[float, float]]:
    """Yield every ``(lat, lon)`` coordinate referenced by a feature.

    For :class:`CircleMarker` and :class:`IconMarker`, the marker's single
    anchor position is yielded. For :class:`Line`, every vertex is yielded.
    For :class:`Polygon`, every vertex of every ring (outer boundary and
    holes) is yielded.

    Args:
        feature: The feature to iterate over.

    Yields:
        ``(lat, lon)`` pairs, in the order they appear on the feature.
    """
    if isinstance(feature, (CircleMarker, IconMarker)):
        yield (feature.lat, feature.lon)
    elif isinstance(feature, Line):
        yield from feature.coordinates
    elif isinstance(feature, Polygon):
        for ring in feature.coordinates:
            yield from ring
