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
from typing import TYPE_CHECKING, Any, Protocol, TypeAlias, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from PIL import Image


@runtime_checkable
class SupportsGeoInterface(Protocol):
    """Protocol for objects exposing the ``__geo_interface__`` attribute."""

    __geo_interface__: dict[str, Any]


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


_SIMPLESTYLE_KEYS: dict[str, str] = {
    "stroke": "stroke_color",
    "stroke-width": "stroke_width",
    "stroke-opacity": "stroke_opacity",
    "fill": "fill_color",
    "fill-opacity": "fill_opacity",
}


def _swap(coord: Sequence[float]) -> tuple[float, float]:
    """Swap GeoJSON ``[lon, lat]`` to internal ``(lat, lon)``."""
    lon, lat = coord[0], coord[1]
    return (lat, lon)


def _swap_ring(ring: Sequence[Sequence[float]]) -> list[tuple[float, float]]:
    return [_swap(c) for c in ring]


def _apply_simplestyle(
    properties: dict[str, Any] | None, base_style: dict[str, Any]
) -> dict[str, Any]:
    """Merge GeoJSON ``simplestyle-spec`` keys from ``properties`` into ``base_style``.

    Properties take precedence over ``base_style``; unknown keys are ignored.
    """
    merged = dict(base_style)
    if properties:
        for src_key, dst_key in _SIMPLESTYLE_KEYS.items():
            if src_key in properties:
                merged[dst_key] = properties[src_key]
    return merged


def _filter_style(style: dict[str, Any], allowed: tuple[str, ...]) -> dict[str, Any]:
    """Return only the entries in ``style`` whose keys appear in ``allowed``."""
    return {k: v for k, v in style.items() if k in allowed}


_POINT_STYLE_KEYS = (
    "radius",
    "stroke_color",
    "stroke_width",
    "fill_color",
    "opacity",
    "stroke_opacity",
    "fill_opacity",
)
_LINE_STYLE_KEYS = ("stroke_color", "stroke_width", "opacity", "stroke_opacity")
_POLYGON_STYLE_KEYS = (
    "stroke_color",
    "stroke_width",
    "fill_color",
    "opacity",
    "stroke_opacity",
    "fill_opacity",
)


def geojson_to_features(  # noqa: C901, PLR0911, PLR0912
    obj: dict[str, Any] | SupportsGeoInterface,
    style: dict[str, Any] | None = None,
) -> list[MapFeature]:
    """Convert a GeoJSON object into a list of :data:`MapFeature` instances.

    Accepts a GeoJSON-shaped ``dict`` or any object implementing the
    `__geo_interface__ <https://gist.github.com/sgillies/2217756>`_
    protocol. Geometries are recursively flattened so that ``MultiPoint``,
    ``MultiLineString``, ``MultiPolygon``, ``GeometryCollection``, and
    ``FeatureCollection`` each yield one feature per child geometry.

    When parsing a ``Feature`` whose ``properties`` contain
    `simplestyle-spec <https://github.com/mapbox/simplestyle-spec>`_ keys
    (``stroke``, ``stroke-width``, ``stroke-opacity``, ``fill``,
    ``fill-opacity``), those properties take precedence over ``style``.

    Args:
        obj: A GeoJSON dict or an object with ``__geo_interface__``.
        style: Default styling applied to every parsed feature. Keys must
            match the corresponding dataclass fields (e.g.
            ``stroke_color``, ``fill_color``, ``stroke_width``,
            ``opacity``).

    Returns:
        A flat list of feature dataclasses. Points become
        :class:`CircleMarker`, line strings become :class:`Line`, and
        polygons become :class:`Polygon`.

    Raises:
        TypeError: If the input is neither a dict nor an object exposing
            ``__geo_interface__``.
        ValueError: If the object's ``type`` field is missing or
            unrecognised.
    """
    if isinstance(obj, SupportsGeoInterface):
        geo_obj: dict[str, Any] = obj.__geo_interface__
    elif isinstance(obj, dict):
        geo_obj = obj
    else:
        msg = (
            "Expected a GeoJSON dict or __geo_interface__ object, "
            f"got {type(obj).__name__}"
        )
        raise TypeError(msg)
    base_style = style or {}
    geo_type = geo_obj.get("type")

    if geo_type == "FeatureCollection":
        features: list[MapFeature] = []
        for child in geo_obj.get("features", []):
            features.extend(geojson_to_features(child, base_style))
        return features

    if geo_type == "Feature":
        merged = _apply_simplestyle(geo_obj.get("properties"), base_style)
        geometry = geo_obj.get("geometry")
        if geometry is None:
            return []
        return geojson_to_features(geometry, merged)

    if geo_type == "GeometryCollection":
        features = []
        for child in geo_obj.get("geometries", []):
            features.extend(geojson_to_features(child, base_style))
        return features

    if geo_type == "Point":
        lat, lon = _swap(geo_obj["coordinates"])
        return [CircleMarker(lat, lon, **_filter_style(base_style, _POINT_STYLE_KEYS))]

    if geo_type == "MultiPoint":
        kw = _filter_style(base_style, _POINT_STYLE_KEYS)
        return [CircleMarker(*_swap(c), **kw) for c in geo_obj["coordinates"]]

    if geo_type == "LineString":
        kw = _filter_style(base_style, _LINE_STYLE_KEYS)
        return [Line(_swap_ring(geo_obj["coordinates"]), **kw)]

    if geo_type == "MultiLineString":
        kw = _filter_style(base_style, _LINE_STYLE_KEYS)
        return [Line(_swap_ring(line), **kw) for line in geo_obj["coordinates"]]

    if geo_type == "Polygon":
        kw = _filter_style(base_style, _POLYGON_STYLE_KEYS)
        rings = [_swap_ring(ring) for ring in geo_obj["coordinates"]]
        return [Polygon(rings, **kw)]

    if geo_type == "MultiPolygon":
        kw = _filter_style(base_style, _POLYGON_STYLE_KEYS)
        return [
            Polygon([_swap_ring(ring) for ring in poly], **kw)
            for poly in geo_obj["coordinates"]
        ]

    msg = f"Unsupported or missing GeoJSON type: {geo_type!r}"
    raise ValueError(msg)
