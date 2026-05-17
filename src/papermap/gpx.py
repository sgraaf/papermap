"""GPX parsing — turn ``.gpx`` files (or ``gpx.GPX`` objects) into map features.

The :func:`gpx_to_features` function accepts either a path to a GPX file
or any object exposing the ``__geo_interface__`` protocol (e.g.
an instance from the `gpx <https://pypi.org/project/gpx/>`_ library) and
returns a flat list of :data:`~papermap.features.MapFeature` instances by
delegating to :func:`~papermap.features.geojson_to_features`.

GPX objects from the upstream ``gpx`` library expose a
``FeatureCollection`` via ``__geo_interface__``:

- Waypoints become ``Point`` features → :class:`~papermap.features.CircleMarker`.
- Routes become ``LineString`` features → :class:`~papermap.features.Line`.
- Tracks become ``MultiLineString`` features → one :class:`~papermap.features.Line`
  per track segment.

Reading GPX files and/or parsing GPX objects requires the optional ``gpx``
package. Install it with ``uv add --extra gpx papermap``.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .geojson import geojson_to_features

if TYPE_CHECKING:
    from gpx import GeoGPXModel

    from .features import MapFeature


def gpx_to_features(
    gpx_source: str | Path | GeoGPXModel,
    style: dict[str, Any] | None = None,
) -> list[MapFeature]:
    """Convert a GPX file path or GPX object to map features.

    Args:
        gpx_source: A path to a ``.gpx`` file (``str`` or
            :class:`pathlib.Path`), or a GPX object with geometric data.
        style: Default styling forwarded to
            :func:`~papermap.features.geojson_to_features`. See that
            function for the supported keys.

    Returns:
        A flat list of feature dataclasses. Waypoints become
        :class:`~papermap.features.CircleMarker`, routes become
        :class:`~papermap.features.Line`, and each segment of each track
        becomes its own :class:`~papermap.features.Line`.

    Raises:
        ImportError: If the optional ``gpx`` package is not installed.
        TypeError: If ``gpx_source`` is neither a path-like nor a GPX object
            with geometric data.
    """
    try:
        from gpx import GeoGPXModel, read_gpx  # noqa: PLC0415
    except ImportError as e:
        msg = (
            "Reading GPX files and/or parsing GPX objects requires the "
            "optional 'gpx' package. Install it with `pip install "
            "papermap[gpx]`."
        )
        raise ImportError(msg) from e

    if isinstance(gpx_source, GeoGPXModel):  # implements `__geo_interface__`
        gpx_obj = gpx_source
    elif isinstance(gpx_source, (str, Path)):
        gpx_obj = read_gpx(gpx_source)
    else:
        msg = (
            "Expected a GPX file path or a GPX object with geometric data, "
            f"got {type(gpx_source).__name__}"
        )
        raise TypeError(msg)

    return geojson_to_features(gpx_obj, style)
