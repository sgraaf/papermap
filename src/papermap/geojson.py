"""GeoJSON parsing — turn ``.geojson`` files (or GeoJSON objects) into map features.

The :func:`geojson_to_features` function accepts either a path to a GeoJSON
file or a GeoJSON object (or any object implementing the ``__geo_interface__``
protocol) and returns a flat list of :data:`~papermap.features.MapFeature`
instances.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence


from .features import CircleMarker, Line, MapFeature, Polygon


@runtime_checkable
class SupportsGeoInterface(Protocol):
    """Protocol for objects exposing the ``__geo_interface__`` attribute."""

    @property
    def __geo_interface__(self) -> dict[str, Any]: ...


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
    geojson_source: str | Path | dict[str, Any] | SupportsGeoInterface,
    style: dict[str, Any] | None = None,
) -> list[MapFeature]:
    """Convert a GeoJSON file path or a GeoJSON object to map features.

    When parsing a ``Feature`` whose ``properties`` contain
    `simplestyle-spec <https://github.com/mapbox/simplestyle-spec>`_ keys
    (``stroke``, ``stroke-width``, ``stroke-opacity``, ``fill``,
    ``fill-opacity``), those properties take precedence over ``style``.

    Args:
        geojson_source: A path to a ``.geojson`` file (``str`` or
            :class:`pathlib.Path`), or a GeoJSON dict (or an object exposing
            the ``__geo_interface__`` protocol).
        style: Default styling applied to every parsed feature. Keys must
            match the corresponding dataclass fields (e.g.
            ``stroke_color``, ``fill_color``, ``stroke_width``,
            ``opacity``).

    Returns:
        A flat list of feature dataclasses. Points become
        :class:`CircleMarker`, line strings become :class:`Line`, and
        polygons become :class:`Polygon`.

    Raises:
        TypeError: If the input is neither a path-like, nor a dict nor an
            object exposing n``__geo_interface__``.
        ValueError: If the object's ``type`` field is missing or
            unrecognised.
    """
    if isinstance(geojson_source, SupportsGeoInterface):
        geo_obj: dict[str, Any] = geojson_source.__geo_interface__
    elif isinstance(geojson_source, (str, Path)):
        import json  # noqa: PLC0415

        geo_obj = json.loads(Path(geojson_source).read_text(encoding="utf-8"))
    elif isinstance(geojson_source, dict):
        if not geojson_source:
            return []
        geo_obj = geojson_source
    else:
        msg = (
            "Expected a GeoJSON dict or __geo_interface__ object, "
            f"got {type(geojson_source).__name__}"
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
