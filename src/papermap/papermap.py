import time
import warnings
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import KW_ONLY, InitVar, dataclass, field
from decimal import Decimal
from importlib import metadata
from io import BytesIO
from itertools import count
from math import ceil, floor, log2, radians
from pathlib import Path
from typing import Any, Self

import httpx
from fpdf import FPDF
from PIL import Image

from .features import (
    CircleMarker,
    IconMarker,
    Line,
    MapFeature,
    Polygon,
    SupportsGeoInterface,
    geojson_to_features,
    iter_feature_coordinates,
)
from .geodesy import (
    ECEFCoordinate,
    MGRSCoordinate,
    UTMCoordinate,
    ecef_to_latlon,
    latlon_to_utm,
    mgrs_to_latlon,
    utm_to_latlon,
)
from .tile import TILE_SIZE, Tile
from .tile_provider import TileProvider
from .tile_providers import (
    DEFAULT_TILE_PROVIDER_KEY,
    KEY_TO_TILE_PROVIDER,
    TILE_PROVIDER_KEYS,
)
from .utils import (
    DEFAULT_DPI,
    drange,
    get_string_formatting_arguments,
    lat_to_y,
    lon_to_x,
    mm_to_px,
    pt_to_mm,
    px_to_mm,
    scale_to_zoom,
    zoom_to_scale,
)

NAME: str = "papermap"
"""Name of the application."""

PAPER_SIZE_TO_DIMENSIONS_MAP: dict[str, tuple[int, int]] = {
    "a0": (841, 1189),
    "a1": (594, 841),
    "a2": (420, 594),
    "a3": (297, 420),
    "a4": (210, 297),
    "a5": (148, 210),
    "a6": (105, 148),
    "a7": (74, 105),
    "letter": (216, 279),
    "legal": (216, 356),
}
"""Map of paper size names to dimensions (width, height) in mm."""

PAPER_SIZES = tuple(PAPER_SIZE_TO_DIMENSIONS_MAP.keys())
"""Tuple of available paper size names."""

DEFAULT_PAPER_SIZE: str = "a4"
"""Default paper size."""

DEFAULT_SCALE: int = 25_000
"""Default map scale."""

DEFAULT_MARGIN: int = 10
"""Default margin in mm."""

DEFAULT_BACKGROUND_COLOR: str = "#fff"
"""Default background color."""

DEFAULT_GRID_SIZE: int = 1_000
"""Default grid size in meters."""

DEFAULT_AUTO_SCALE_PADDING: float = 5.0
"""Default padding (in mm, per side) between features and the image edge when ``auto_scale`` is enabled."""


class ScaleOutOfBoundsError(ValueError):
    """Raised when the resolved zoom level is outside the tile provider's bounds."""


COMMON_SCALES: tuple[int, ...] = (
    500,
    1_000,
    2_500,
    5_000,
    10_000,
    25_000,
    50_000,
    100_000,
    250_000,
    500_000,
    1_000_000,
    2_500_000,
    5_000_000,
    10_000_000,
    25_000_000,
    50_000_000,
)
"""Common cartographic scales that ``auto_scale`` snaps up to."""


def _compute_auto_scale(  # noqa: PLR0913
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    *,
    paper_size: str,
    use_landscape: bool,
    margin_top: int,
    margin_right: int,
    margin_bottom: int,
    margin_left: int,
    dpi: int,
    padding: float,
) -> int:
    """Compute the smallest common-cartographic scale that fits a bbox on paper.

    Given a geographic bounding box and the paper-area parameters, computes
    the most zoomed-in scale at which the bounding box still fits within
    the printable image area (paper size minus margins minus padding), then
    snaps up to the nearest entry in :data:`COMMON_SCALES`.

    Args:
        lat_min: Minimum latitude of the bounding box.
        lat_max: Maximum latitude of the bounding box.
        lon_min: Minimum longitude of the bounding box.
        lon_max: Maximum longitude of the bounding box.
        paper_size: Paper size name (e.g. ``"a4"``).
        use_landscape: Whether the paper is in landscape orientation.
        margin_top: Top margin, in mm.
        margin_right: Right margin, in mm.
        margin_bottom: Bottom margin, in mm.
        margin_left: Left margin, in mm.
        dpi: Dots per inch.
        padding: Padding between the features and the image edge, in mm per side.

    Returns:
        The auto-computed scale (e.g. ``25_000`` for 1:25 000), snapped up
        to a common cartographic scale.

    Raises:
        ValueError: If the paper size is invalid.
        ValueError: If padding/margins leave no printable area.
        ValueError: If the bounding box has zero extent on either axis.
    """
    if paper_size not in PAPER_SIZE_TO_DIMENSIONS_MAP:
        msg = f"Invalid paper size. Please choose one of {', '.join(PAPER_SIZES)}"
        raise ValueError(msg)
    width_mm, height_mm = PAPER_SIZE_TO_DIMENSIONS_MAP[paper_size]
    if use_landscape:
        width_mm, height_mm = height_mm, width_mm

    image_w_mm = width_mm - margin_left - margin_right - 2 * padding
    image_h_mm = height_mm - margin_top - margin_bottom - 2 * padding
    if image_w_mm <= 0 or image_h_mm <= 0:
        msg = "Padding and margins leave no printable area"
        raise ValueError(msg)

    image_w_px = mm_to_px(image_w_mm, dpi)
    image_h_px = mm_to_px(image_h_mm, dpi)

    # Longitude maps linearly to x, so the lon midpoint is also the x midpoint
    # and the symmetric extent is simply (x_max - x_min).
    ex0 = lon_to_x(lon_max, 0) - lon_to_x(lon_min, 0)

    # Latitude maps non-linearly to y (Web Mercator), so the page-y position of
    # the lat midpoint is NOT the midpoint of y_top/y_bottom. To guarantee the
    # bbox fits when centred on the lat midpoint, use twice the larger of the
    # two half-extents about that y-centre as the effective height extent.
    center_lat = (lat_min + lat_max) / 2
    y_top = lat_to_y(lat_max, 0)
    y_bottom = lat_to_y(lat_min, 0)
    y_center = lat_to_y(center_lat, 0)
    ey0 = 2 * max(y_bottom - y_center, y_center - y_top)

    if ex0 <= 0 or ey0 <= 0:
        msg = (
            "Cannot auto-scale: features have zero geographic extent along "
            "at least one axis; provide an explicit 'scale' instead"
        )
        raise ValueError(msg)

    zoom_x = log2(image_w_px / (ex0 * TILE_SIZE))
    zoom_y = log2(image_h_px / (ey0 * TILE_SIZE))
    zoom = min(zoom_x, zoom_y)

    raw_scale = zoom_to_scale(zoom, center_lat, dpi)

    # Snap up to the smallest common scale >= raw_scale.
    for s in COMMON_SCALES:
        if s >= raw_scale:
            return s
    # Bbox is so large no common scale fits; fall back to the next multiple
    # of 1 000 000.
    return ceil(raw_scale / 1_000_000) * 1_000_000


@dataclass(slots=True)
class PaperMap:
    """A paper map.

        >>> from papermap import PaperMap
        >>> pm = PaperMap(13.75889, 100.49722)
        >>> pm.render()
        >>> pm.save("Bangkok.pdf")

    Args:
        lat: Latitude of the center of the map.
        lon: Longitude of the center of the map
        tile_provider_key: Tile provider key to serve as the base of the paper map. Defaults to `openstreetmap`.
        api_key: API key for the chosen tile provider (if applicable). Defaults to `None`.
        size: Size of the paper map. Defaults to `a4`.
        landscape: Use landscape orientation. Defaults to `False`.
        margin_top: Top margin (in mm). Defaults to `10`.
        margin_right: Right margin (in mm). Defaults to `10`.
        margin_bottom: Bottom margin (in mm). Defaults to `10`.
        margin_left: Left margin (in mm). Defaults to `10`.
        scale: Scale of the paper map. Defaults to `25000`.
        dpi: Dots per inch. Defaults to `300`.
        background_color: Background color of the paper map. Defaults to `#fff`.
        add_grid: Add a coordinate grid overlay to the paper map. Defaults to `False`.
        grid_size: Size of the grid squares (if applicable, in meters). Defaults to `1000`.
        strict_download: Fail if any tiles cannot be downloaded. Defaults to `False`.

    Raises:
        ValueError: If the tile provider is invalid.
        ValueError: If no API key is specified (when applicable).
        ValueError: If the paper size is invalid.
        ScaleOutOfBoundsError: If the scale is "out of bounds" for the chosen
            tile provider.
    """

    lat: float
    lon: float
    _: KW_ONLY
    tile_provider_key: InitVar[str] = DEFAULT_TILE_PROVIDER_KEY
    api_key: str | None = None
    paper_size: InitVar[str] = DEFAULT_PAPER_SIZE
    use_landscape: bool = False
    margin_top: int = DEFAULT_MARGIN
    margin_right: int = DEFAULT_MARGIN
    margin_bottom: int = DEFAULT_MARGIN
    margin_left: int = DEFAULT_MARGIN
    scale: int = DEFAULT_SCALE
    dpi: int = DEFAULT_DPI
    background_color: str = DEFAULT_BACKGROUND_COLOR
    add_grid: bool = False
    grid_size: int = DEFAULT_GRID_SIZE
    strict_download: bool = False

    tile_provider: TileProvider = field(init=False)
    width: int = field(init=False)
    height: int = field(init=False)
    zoom: float = field(init=False)
    zoom_scaled: int = field(init=False)
    resize_factor: float = field(init=False)
    image_width: int = field(init=False)
    image_height: int = field(init=False)
    image_width_px: int = field(init=False)
    image_height_px: int = field(init=False)
    φ: float = field(init=False)
    λ: float = field(init=False)
    grid_size_scaled: Decimal = field(init=False)
    image_width_scaled_px: int = field(init=False)
    image_height_scaled_px: int = field(init=False)
    x_center: float = field(init=False)
    y_center: float = field(init=False)
    x_min: int = field(init=False)
    y_min: int = field(init=False)
    x_max: int = field(init=False)
    y_max: int = field(init=False)
    tiles: list[Tile] = field(init=False)
    pdf: FPDF = field(init=False)
    map_image_scaled: Image.Image = field(init=False, repr=False)
    map_image: Image.Image = field(init=False, repr=False)
    file: Path = field(init=False, repr=False)
    features: list[MapFeature] = field(init=False)

    def __post_init__(self, tile_provider_key: str, paper_size: str) -> None:
        # Store basic parameters
        self._validate_coordinates()

        # Validate and initialize tile provider
        self._validate_and_set_tile_provider(tile_provider_key)

        # Validate and set paper dimensions
        self._validate_and_set_paper_size(paper_size)

        # Compute zoom levels and validate bounds
        self._compute_zoom_and_resize_factor(tile_provider_key)

        # Compute image dimensions and conversions
        self._compute_image_dimensions()

        # Initialize tiles
        self._initialize_tiles()

        # Initialize PDF document
        self._initialize_pdf()

        # Initialize the (empty) feature list
        self.features = []

    @classmethod
    def from_utm(
        cls,
        utm: UTMCoordinate | str,
        **kwargs: Any,
    ) -> Self:
        """Create a paper map from Universal Transverse Mercator (UTM) coordinates.

        Args:
            utm: Either an UTMCoordinate object or a UTM string (e.g., "18N 583960E 4507523N").
            **kwargs: Additional keyword arguments to pass to PaperMap constructor.

        Returns:
            A new PaperMap instance centered on the converted coordinates.

        Examples:
            >>> from papermap import PaperMap
            >>> from papermap.geodesy import UTMCoordinate
            >>> utm = UTMCoordinate(583960, 4507523, 18, "N")
            >>> pm = PaperMap.from_utm(utm)
            >>> pm.render()
            >>> pm.save("map_from_utm.pdf")
        """
        lat, lon, _ = utm_to_latlon(utm)
        return cls(lat, lon, **kwargs)

    @classmethod
    def from_mgrs(
        cls,
        mgrs: MGRSCoordinate | str,
        **kwargs: Any,
    ) -> Self:
        """Create a paper map from Military Grid Reference System (MGRS) coordinates.

        Args:
            mgrs: Either an MGRSCoordinate object or an MGRS string
                (e.g., "18TWK8395907523").
            **kwargs: Additional keyword arguments to pass to PaperMap constructor.

        Returns:
            A new PaperMap instance centered on the converted coordinates.

        Raises:
            ValueError: If the MGRS string is malformed.

        Examples:
            >>> from papermap import PaperMap
            >>> pm = PaperMap.from_mgrs("18TWK8395907523")
            >>> pm.render()
            >>> pm.save("map_from_mgrs.pdf")

            >>> from papermap.geodesy import MGRSCoordinate
            >>> mgrs = MGRSCoordinate(18, "T", "WK", 83959, 7523)
            >>> pm = PaperMap.from_mgrs(mgrs)
        """
        lat, lon, _ = mgrs_to_latlon(mgrs)
        return cls(lat, lon, **kwargs)

    @classmethod
    def from_ecef(
        cls,
        ecef: ECEFCoordinate,
        **kwargs: Any,
    ) -> Self:
        """Create a paper map from Earth-Centered, Earth-Fixed (ECEF) Cartesian coordinates.

        Args:
            ecef: ECEFCoordinate with x, y, z in meters.
            **kwargs: Additional keyword arguments to pass to PaperMap constructor.

        Returns:
            A new PaperMap instance centered on the converted coordinates.

        Examples:
            >>> from papermap import PaperMap
            >>> from papermap.geodesy import ECEFCoordinate
            >>> ecef = ECEFCoordinate(1334934, -4655474, 4137498)
            >>> pm = PaperMap.from_ecef(ecef)
            >>> pm.render()
            >>> pm.save("map_from_ecef.pdf")
        """
        lat, lon, _ = ecef_to_latlon(ecef)
        return cls(lat, lon, **kwargs)

    @classmethod
    def from_features(
        cls,
        *features: MapFeature,
        auto_scale: bool = False,
        padding: float = DEFAULT_AUTO_SCALE_PADDING,
        **kwargs: Any,
    ) -> Self:
        """Create a paper map centred on the geographic centre of the given feature(s).

        The centre is the midpoint of the features' bounding box (the
        midpoints of the min/max latitude and longitude across every
        coordinate referenced by the features). The features are also added
        to the new map and will be drawn when :meth:`render` is called.

        When ``auto_scale`` is ``True``, the map ``scale`` is computed
        automatically so that the bounding box fits within the printable
        image area (paper size minus margins minus ``padding``), then
        snapped up to the nearest common cartographic scale (see
        :data:`COMMON_SCALES`). Passing ``auto_scale=True`` together with
        an explicit ``scale`` raises a ``ValueError``.

        Args:
            features: One or more :data:`MapFeature` instances.
            auto_scale: If ``True``, compute the scale automatically to fit
                the features. Defaults to ``False``.
            padding: Padding between the features and the image edge, in mm
                per side. Only consulted when ``auto_scale`` is ``True``.
                Defaults to ``5.0``.
            **kwargs: Additional keyword arguments to pass to PaperMap
                constructor.

        Returns:
            A new PaperMap instance centred on the features' bounding box,
            with the features added.

        Raises:
            ValueError: If no features are given.
            ValueError: If none of the features contain any coordinates.
            ValueError: If both ``auto_scale=True`` and ``scale`` are given.
            ValueError: If ``auto_scale=True`` and the features have zero
                geographic extent along at least one axis.
            ScaleOutOfBoundsError: If ``auto_scale=True`` and the computed
                scale is out of the tile provider's zoom bounds.

        Note:
            Features spanning the ±180° anti-meridian are not handled
            specially; the resulting centre may be on the opposite side of
            the world from where you expect.

        Examples:
            >>> from papermap import PaperMap
            >>> from papermap.features import CircleMarker, Line
            >>> pm = PaperMap.from_features(
            ...     CircleMarker(40.7128, -74.0060),
            ...     Line([(40.71, -74.01), (40.72, -73.99)]),
            ...     auto_scale=True,
            ... )
            >>> pm.render()
            >>> pm.save("map_from_features.pdf")
        """
        if not features:
            msg = "At least one feature must be provided"
            raise ValueError(msg)

        coords = [c for f in features for c in iter_feature_coordinates(f)]
        if not coords:
            msg = "The provided feature(s) contain no coordinates"
            raise ValueError(msg)

        lats = [lat for lat, _ in coords]
        lons = [lon for _, lon in coords]
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2

        if auto_scale:
            if "scale" in kwargs:
                msg = "Cannot specify both 'scale' and 'auto_scale=True'"
                raise ValueError(msg)
            kwargs["scale"] = _compute_auto_scale(
                lat_min,
                lat_max,
                lon_min,
                lon_max,
                paper_size=kwargs.get("paper_size", DEFAULT_PAPER_SIZE),
                use_landscape=kwargs.get("use_landscape", False),
                margin_top=kwargs.get("margin_top", DEFAULT_MARGIN),
                margin_right=kwargs.get("margin_right", DEFAULT_MARGIN),
                margin_bottom=kwargs.get("margin_bottom", DEFAULT_MARGIN),
                margin_left=kwargs.get("margin_left", DEFAULT_MARGIN),
                dpi=kwargs.get("dpi", DEFAULT_DPI),
                padding=padding,
            )

        try:
            pm = cls(center_lat, center_lon, **kwargs)
        except ScaleOutOfBoundsError as e:
            if auto_scale:
                msg = f"{e} (auto-scaled to 1:{kwargs['scale']})"
                raise ScaleOutOfBoundsError(msg) from e
            raise
        pm.features += list(features)
        return pm

    @classmethod
    def from_geojson(
        cls,
        obj: dict[str, Any] | SupportsGeoInterface,
        style: dict[str, Any] | None = None,
        *,
        auto_scale: bool = False,
        padding: float = DEFAULT_AUTO_SCALE_PADDING,
        **kwargs: Any,
    ) -> Self:
        """Create a paper map centred on the geographic centre of GeoJSON geometries.

        Parses the input with :func:`papermap.features.geojson_to_features`
        and then delegates to :meth:`from_features` to compute the centre
        (the midpoint of the parsed features' bounding box) and to add the
        parsed features to the new map.

        When ``auto_scale`` is ``True``, the map ``scale`` is computed
        automatically so that the parsed features fit within the printable
        image area. See :meth:`from_features` for details.

        Args:
            obj: A GeoJSON dict or an object exposing ``__geo_interface__``.
            style: Default styling applied to every parsed feature. See
                :func:`papermap.features.geojson_to_features` for the
                supported keys and the precedence rules with
                ``simplestyle-spec`` properties.
            auto_scale: If ``True``, compute the scale automatically to fit
                the parsed features. Defaults to ``False``.
            padding: Padding between the features and the image edge, in mm
                per side. Only consulted when ``auto_scale`` is ``True``.
                Defaults to ``5.0``.
            **kwargs: Additional keyword arguments to pass to PaperMap
                constructor.

        Returns:
            A new PaperMap instance centred on the parsed features'
            bounding box, with the parsed features added.

        Raises:
            TypeError: If ``obj`` is neither a dict nor exposes
                ``__geo_interface__``.
            ValueError: If ``obj`` parses to no features (e.g. an empty
                ``FeatureCollection``), or if the parsed features contain no
                coordinates.
            ValueError: If both ``auto_scale=True`` and ``scale`` are given.
            ValueError: If ``auto_scale=True`` and the parsed features have
                zero geographic extent along at least one axis.

        Examples:
            >>> from papermap import PaperMap
            >>> geojson = {
            ...     "type": "FeatureCollection",
            ...     "features": [
            ...         {
            ...             "type": "Feature",
            ...             "geometry": {
            ...                 "type": "Point",
            ...                 "coordinates": [-74.0060, 40.7128],
            ...             },
            ...             "properties": {},
            ...         }
            ...     ],
            ... }
            >>> pm = PaperMap.from_geojson(geojson)
            >>> pm.render()
            >>> pm.save("map_from_geojson.pdf")
        """
        features = geojson_to_features(obj, style)
        if not features:
            msg = "The provided GeoJSON object parsed to no features"
            raise ValueError(msg)
        return cls.from_features(
            *features, auto_scale=auto_scale, padding=padding, **kwargs
        )

    def _validate_coordinates(self) -> None:
        """Validate ``self.lat`` and ``self.lon`` are within valid ranges.

        Raises:
            ValueError: If latitude is not in [-90, 90] range.
            ValueError: If longitude is not in [-180, 180] range.
        """
        if not -90 <= self.lat <= 90:  # noqa: PLR2004
            msg = f"Latitude must be in [-90, 90] range, got {self.lat}"
            raise ValueError(msg)
        if not -180 <= self.lon <= 180:  # noqa: PLR2004
            msg = f"Longitude must be in [-180, 180] range, got {self.lon}"
            raise ValueError(msg)

    def _validate_and_set_tile_provider(self, tile_provider_key: str) -> None:
        """Validate tile provider key and check API key requirements.

        Args:
            tile_provider_key: The tile provider key to validate.

        Raises:
            ValueError: If tile provider key is invalid.
            ValueError: If API key is required but not provided.
        """
        if tile_provider_key in KEY_TO_TILE_PROVIDER:
            self.tile_provider = KEY_TO_TILE_PROVIDER[tile_provider_key]
        else:
            available_keys = TILE_PROVIDER_KEYS
            msg = f"Invalid tile provider key '{tile_provider_key}'. Please choose one of {', '.join(available_keys)}"
            raise ValueError(msg)

        # Check whether an API key is provided, if it is needed
        if (
            "a" in get_string_formatting_arguments(self.tile_provider.url_template)
            and self.api_key is None
        ):
            msg = f"No API key specified for {tile_provider_key} tile provider"
            raise ValueError(msg)

    def _validate_and_set_paper_size(self, paper_size: str) -> None:
        """Validate paper size and set ``self.width`` and ``self.height``.

        Args:
            paper_size: The paper size name to validate.

        Raises:
            ValueError: If paper size is invalid.
        """
        if paper_size in PAPER_SIZE_TO_DIMENSIONS_MAP:
            self.width, self.height = PAPER_SIZE_TO_DIMENSIONS_MAP[paper_size]
            if self.use_landscape:
                self.width, self.height = self.height, self.width
        else:
            msg = f"Invalid paper size. Please choose one of {', '.join(PAPER_SIZES)}"
            raise ValueError(msg)

    def _compute_zoom_and_resize_factor(self, tile_provider_key: str) -> None:
        """Compute zoom levels and validate they are within tile provider bounds.

        Args:
            tile_provider_key: The tile provider key for error messages.

        Raises:
            ScaleOutOfBoundsError: If computed zoom is out of bounds for the
                tile provider.
        """
        self.zoom = scale_to_zoom(self.scale, self.lat, self.dpi)
        self.zoom_scaled = floor(self.zoom)
        self.resize_factor = 2**self.zoom_scaled / 2**self.zoom

        # Make sure the zoom is not out of bounds
        if (
            self.zoom_scaled < self.tile_provider.zoom_min
            or self.zoom_scaled > self.tile_provider.zoom_max
        ):
            msg = f"Scale out of bounds for {tile_provider_key} tile provider."
            raise ScaleOutOfBoundsError(msg)

    def _compute_image_dimensions(self) -> None:
        """Compute all image-related dimensions and perform coordinate conversions."""
        # Compute the width and height of the image (in mm)
        self.image_width = self.width - self.margin_left - self.margin_right
        self.image_height = self.height - self.margin_top - self.margin_bottom

        # Perform conversions
        self.image_width_px = mm_to_px(self.image_width, self.dpi)
        self.image_height_px = mm_to_px(self.image_height, self.dpi)
        self.φ = radians(self.lat)
        self.λ = radians(self.lon)

        # Compute the scaled grid size (in mm) using exact Decimal arithmetic
        self.grid_size_scaled = Decimal(self.grid_size * 1_000) / Decimal(self.scale)

        # Compute the scaled width and height of the image (in px)
        self.image_width_scaled_px = round(self.image_width_px * self.resize_factor)
        self.image_height_scaled_px = round(self.image_height_px * self.resize_factor)

        # Determine the center tile
        self.x_center = lon_to_x(self.lon, self.zoom_scaled)
        self.y_center = lat_to_y(self.lat, self.zoom_scaled)

        # Determine the tiles required to produce the map image
        self.x_min = floor(
            self.x_center - (0.5 * self.image_width_scaled_px / TILE_SIZE)
        )
        self.y_min = floor(
            self.y_center - (0.5 * self.image_height_scaled_px / TILE_SIZE)
        )
        self.x_max = ceil(
            self.x_center + (0.5 * self.image_width_scaled_px / TILE_SIZE)
        )
        self.y_max = ceil(
            self.y_center + (0.5 * self.image_height_scaled_px / TILE_SIZE)
        )

    def _initialize_tiles(self) -> None:
        """Initialize the list of tiles required for the map."""
        self.tiles = []
        for x in range(self.x_min, self.x_max):
            for y in range(self.y_min, self.y_max):
                # x and y may have crossed the date line
                max_tile = 2**self.zoom_scaled
                x_tile = (x + max_tile) % max_tile
                y_tile = (y + max_tile) % max_tile

                bbox = (
                    round(
                        (x_tile - self.x_center) * TILE_SIZE
                        + self.image_width_scaled_px / 2
                    ),
                    round(
                        (y_tile - self.y_center) * TILE_SIZE
                        + self.image_height_scaled_px / 2
                    ),
                    round(
                        (x_tile + 1 - self.x_center) * TILE_SIZE
                        + self.image_width_scaled_px / 2
                    ),
                    round(
                        (y_tile + 1 - self.y_center) * TILE_SIZE
                        + self.image_height_scaled_px / 2
                    ),
                )

                self.tiles.append(Tile(x_tile, y_tile, self.zoom_scaled, bbox))

    def _initialize_pdf(self) -> None:
        """Initialize the PDF document with margins and settings."""
        self.pdf = FPDF(
            unit="mm",
            format=(self.width, self.height),
        )
        self.pdf.set_font("Helvetica")
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_top_margin(self.margin_top)
        self.pdf.set_auto_page_break(True, self.margin_bottom)  # noqa: FBT003
        self.pdf.set_left_margin(self.margin_left)
        self.pdf.set_right_margin(self.margin_right)
        self.pdf.add_page()

    def latlon_to_pdf_mm(self, lat: float, lon: float) -> tuple[float, float]:
        """Convert a geographic position to absolute PDF coordinates in mm.

        Args:
            lat: Latitude.
            lon: Longitude.

        Returns:
            ``(x_mm, y_mm)`` measured from the page origin (top-left).
        """
        x_tile = lon_to_x(lon, self.zoom_scaled)
        y_tile = lat_to_y(lat, self.zoom_scaled)
        dx_px = (x_tile - self.x_center) * TILE_SIZE / self.resize_factor
        dy_px = (y_tile - self.y_center) * TILE_SIZE / self.resize_factor
        x_mm = self.margin_left + self.image_width / 2 + px_to_mm(dx_px, self.dpi)
        y_mm = self.margin_top + self.image_height / 2 + px_to_mm(dy_px, self.dpi)
        return x_mm, y_mm

    def add_circle_marker(
        self,
        lat: float,
        lon: float,
        **kwargs: Any,
    ) -> CircleMarker:
        """Add a :class:`CircleMarker` at the given position to the map.

        Args:
            lat: Latitude of the marker centre.
            lon: Longitude of the marker centre.
            **kwargs: Additional keyword arguments forwarded to
                :class:`CircleMarker`.

        Returns:
            The newly added marker.
        """
        marker = CircleMarker(lat, lon, **kwargs)
        self.features.append(marker)
        return marker

    def add_icon_marker(
        self,
        lat: float,
        lon: float,
        icon: str | Path | Image.Image,
        **kwargs: Any,
    ) -> IconMarker:
        """Add an :class:`IconMarker` at the given position to the map.

        Args:
            lat: Latitude of the anchor point.
            lon: Longitude of the anchor point.
            icon: Path to an image file or a :class:`PIL.Image.Image` instance.
            **kwargs: Additional keyword arguments forwarded to
                :class:`IconMarker`.

        Returns:
            The newly added marker.
        """
        marker = IconMarker(lat, lon, icon, **kwargs)
        self.features.append(marker)
        return marker

    def add_line(
        self,
        coordinates: Sequence[tuple[float, float]],
        **kwargs: Any,
    ) -> Line:
        """Add a :class:`Line` (polyline) to the map.

        Args:
            coordinates: Sequence of ``(lat, lon)`` pairs.
            **kwargs: Additional keyword arguments forwarded to :class:`Line`.

        Returns:
            The newly added line.
        """
        line = Line(coordinates, **kwargs)
        self.features.append(line)
        return line

    def add_polygon(
        self,
        coordinates: Sequence[Sequence[tuple[float, float]]],
        **kwargs: Any,
    ) -> Polygon:
        """Add a :class:`Polygon` to the map.

        Args:
            coordinates: Sequence of rings, where each ring is a sequence of
                ``(lat, lon)`` pairs. The first ring is the outer boundary;
                any subsequent rings are interior holes.
            **kwargs: Additional keyword arguments forwarded to
                :class:`Polygon`.

        Returns:
            The newly added polygon.
        """
        polygon = Polygon(coordinates, **kwargs)
        self.features.append(polygon)
        return polygon

    def add_feature(self, feature: MapFeature) -> MapFeature:
        """Add a pre-constructed feature to the map.

        Args:
            feature: A :class:`CircleMarker`, :class:`IconMarker`,
                :class:`Line`, or :class:`Polygon`.

        Returns:
            The same feature, for chaining.
        """
        self.features.append(feature)
        return feature

    def add_geojson(
        self,
        obj: dict[str, Any] | SupportsGeoInterface,
        style: dict[str, Any] | None = None,
    ) -> list[MapFeature]:
        """Add geometries from a GeoJSON object or ``__geo_interface__`` object.

        See :func:`papermap.features.geojson_to_features` for the supported
        GeoJSON types and the precedence rules for styling.

        Args:
            obj: A GeoJSON dict or an object exposing ``__geo_interface__``.
            style: Default styling applied to every parsed feature.

        Returns:
            The list of features that were parsed and added to the map.
        """
        features = geojson_to_features(obj, style)
        self.features.extend(features)
        return features

    def compute_grid_coordinates(
        self,
    ) -> tuple[list[tuple[Decimal, str]], list[tuple[Decimal, str]]]:
        """Compute the UTM grid line positions and labels for the map overlay.

        The map's geographic centre is converted to UTM and snapped to the
        nearest 1km grid intersection. From there, line positions (in mm
        relative to the image's top-left corner) are walked outward at
        ``grid_size_scaled`` intervals, and the matching kilometre labels
        are derived from the rounded UTM coordinates.

        Returns:
            A pair ``(easting_lines, northing_lines)``. Each list holds
            ``(position_mm, label)`` tuples, where ``position_mm`` is a
            ``Decimal`` distance from the top-left of the image area and
            ``label`` is the UTM coordinate in kilometres.
        """
        # convert Lat/Lon coordinate into UTM coordinate (easting, northing, zone, hemisphere)
        easting, northing, _, _ = latlon_to_utm(self.lat, self.lon)

        # round easting/northing to nearest thousand
        easting_rnd = round(easting, -3)
        northing_rnd = round(northing, -3)

        # compute distance between x/y and x/y_rnd in mm using Decimal arithmetic
        d_easting = Decimal(easting - easting_rnd) / Decimal(self.scale) * 1000
        d_northing = Decimal(northing - northing_rnd) / Decimal(self.scale) * 1000

        # determine center grid coordinate (in mm)
        easting_grid_center = Decimal(self.image_width) / 2 - d_easting
        northing_grid_center = Decimal(self.image_height) / 2 - d_northing

        # determine start grid coordinate (in mm)
        easting_grid_start = easting_grid_center % self.grid_size_scaled
        northing_grid_start = northing_grid_center % self.grid_size_scaled

        # determine the start grid coordinate label
        easting_label_start = int(
            Decimal(easting_rnd) / 1000 - easting_grid_center // self.grid_size_scaled
        )
        northing_label_start = int(
            Decimal(northing_rnd) / 1000 + northing_grid_center // self.grid_size_scaled
        )

        # determine the grid coordinates (in mm)
        easting_grid_cs = list(
            drange(easting_grid_start, Decimal(self.image_width), self.grid_size_scaled)
        )
        northing_grid_cs = list(
            drange(
                northing_grid_start, Decimal(self.image_height), self.grid_size_scaled
            )
        )

        # determine the grid coordinates labels
        easting_labels = [easting_label_start + i for i in range(len(easting_grid_cs))]
        northing_labels = [
            northing_label_start - i for i in range(len(northing_grid_cs))
        ]

        easting_grid_cs_and_labels = list(
            zip(easting_grid_cs, map(str, easting_labels), strict=True)
        )
        northing_grid_cs_and_labels = list(
            zip(northing_grid_cs, map(str, northing_labels), strict=True)
        )

        return easting_grid_cs_and_labels, northing_grid_cs_and_labels

    def _draw_grid_line(  # noqa: PLR0913
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        label: str,
        horizontal: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        """Draw a single grid line with label."""
        label_width = self.pdf.get_string_width(label)
        # draw grid line
        self.pdf.line(start_x, start_y, end_x, end_y)
        # draw label
        if not horizontal and start_x + label_width < self.margin_left + self.pdf.epw:
            self.pdf.set_xy(start_x - label_width / 2, start_y)
            self.pdf.cell(w=label_width, text=label, align="C", fill=True)
        elif horizontal and start_y + label_width < self.margin_top + self.pdf.eph:
            self.pdf.set_xy(start_x, start_y + label_width / 2)
            with self.pdf.rotation(90):
                self.pdf.cell(w=label_width, text=label, align="C", fill=True)

    def render_grid(self) -> None:
        """Draw the UTM coordinate grid overlay onto the PDF, if enabled.

        Does nothing when ``self.add_grid`` is ``False``. When enabled, draws
        vertical (easting) and horizontal (northing) grid lines at the
        positions returned by :meth:`compute_grid_coordinates` and labels
        each line with its UTM coordinate in kilometres.
        """
        if self.add_grid:
            self.pdf.set_draw_color(0, 0, 0)
            self.pdf.set_line_width(0.1)
            self.pdf.set_font_size(8)

            # get grid coordinates
            x_grid_cs_and_labels, y_grid_cs_and_labels = self.compute_grid_coordinates()

            # draw vertical grid lines
            for x, label in x_grid_cs_and_labels:
                x_ = float(x + self.margin_left)
                self._draw_grid_line(
                    x_, self.margin_top, x_, self.margin_top + self.pdf.eph, label
                )

            # draw horizontal grid lines
            for y, label in y_grid_cs_and_labels:
                y_ = float(y + self.margin_top)
                self._draw_grid_line(
                    self.margin_left,
                    y_,
                    self.margin_left + self.pdf.epw,
                    y_,
                    label,
                    horizontal=True,
                )

            self.pdf.set_font_size(12)

    @staticmethod
    def _draw_style(stroke_color: str | None, fill_color: str | None) -> str:
        """Return the FPDF style flag for a stroke/fill combination."""
        if stroke_color is not None and fill_color is not None:
            return "DF"
        if fill_color is not None:
            return "F"
        return "D"

    @staticmethod
    def _local_context_kwargs(  # noqa: PLR0913
        stroke_color: str | None,
        stroke_width: float,
        fill_color: str | None,
        opacity: float,
        stroke_opacity: float | None,
        fill_opacity: float | None,
    ) -> dict[str, Any]:
        """Build ``local_context`` kwargs from a feature's stroke/fill style."""
        ctx_kwargs: dict[str, Any] = {"line_width": stroke_width}
        if stroke_color is not None:
            ctx_kwargs["draw_color"] = stroke_color
        if fill_color is not None:
            ctx_kwargs["fill_color"] = fill_color
        ctx_kwargs["stroke_opacity"] = (
            stroke_opacity if stroke_opacity is not None else opacity
        )
        ctx_kwargs["fill_opacity"] = (
            fill_opacity if fill_opacity is not None else opacity
        )
        return ctx_kwargs

    def _render_circle_marker(self, marker: CircleMarker) -> None:
        """Render a single :class:`CircleMarker` to the PDF."""
        if marker.stroke_color is None and marker.fill_color is None:
            return
        cx, cy = self.latlon_to_pdf_mm(marker.lat, marker.lon)
        ctx_kwargs = self._local_context_kwargs(
            marker.stroke_color,
            marker.stroke_width,
            marker.fill_color,
            marker.opacity,
            marker.stroke_opacity,
            marker.fill_opacity,
        )
        style = self._draw_style(marker.stroke_color, marker.fill_color)
        with self.pdf.local_context(**ctx_kwargs):
            self.pdf.circle(cx, cy, marker.radius, style=style)

    def _render_icon_marker(self, marker: IconMarker) -> None:
        """Render a single :class:`IconMarker` to the PDF."""
        if marker._loaded_icon is None:  # noqa: SLF001
            if isinstance(marker.icon, Image.Image):
                marker._loaded_icon = marker.icon  # noqa: SLF001
            else:
                marker._loaded_icon = Image.open(marker.icon)  # noqa: SLF001
        img = marker._loaded_icon  # noqa: SLF001
        width = marker.width
        if marker.height is None:
            height = width * img.height / img.width
        else:
            height = marker.height
        ax, ay = marker.anchor
        cx, cy = self.latlon_to_pdf_mm(marker.lat, marker.lon)
        tlx = cx - ax * width
        tly = cy - ay * height
        if marker.opacity < 1.0:
            with self.pdf.local_context(
                fill_opacity=marker.opacity, stroke_opacity=marker.opacity
            ):
                self.pdf.image(img, x=tlx, y=tly, w=width, h=height)
        else:
            self.pdf.image(img, x=tlx, y=tly, w=width, h=height)

    def _render_line(self, line: Line) -> None:
        """Render a single :class:`Line` to the PDF."""
        points = [self.latlon_to_pdf_mm(lat, lon) for lat, lon in line.coordinates]
        if len(points) < 2:  # noqa: PLR2004
            return
        ctx_kwargs = self._local_context_kwargs(
            line.stroke_color,
            line.stroke_width,
            None,
            line.opacity,
            line.stroke_opacity,
            None,
        )
        with self.pdf.local_context(**ctx_kwargs):
            self.pdf.polyline(points, style="D")

    @staticmethod
    def _polygon_paint_rule(polygon: Polygon) -> str:
        """Return the FPDF ``paint_rule`` for a polygon's stroke/fill combo."""
        if polygon.stroke_color is not None and polygon.fill_color is not None:
            return "stroke_fill_evenodd"
        if polygon.fill_color is not None:
            return "fill_evenodd"
        return "stroke"

    @staticmethod
    def _strip_closing_vertex(
        ring: list[tuple[float, float]],
    ) -> list[tuple[float, float]]:
        """Drop a GeoJSON ring's closing duplicate vertex if present."""
        return ring[:-1] if ring and ring[0] == ring[-1] else ring

    def _render_polygon_path(
        self, rings: list[list[tuple[float, float]]], paint_rule: str
    ) -> None:
        """Render a multi-ring polygon (with holes) via the FPDF path API."""
        first_x, first_y = rings[0][0]
        with self.pdf.new_path(first_x, first_y) as path:
            path.style.paint_rule = paint_rule
            for ring in rings:
                trimmed = self._strip_closing_vertex(ring)
                path.move_to(*trimmed[0])
                for pt in trimmed[1:]:
                    path.line_to(*pt)
                path.close()

    def _render_polygon(self, polygon: Polygon) -> None:
        """Render a single :class:`Polygon` to the PDF, with optional holes."""
        if polygon.stroke_color is None and polygon.fill_color is None:
            return
        rings = [
            [self.latlon_to_pdf_mm(lat, lon) for lat, lon in ring]
            for ring in polygon.coordinates
        ]
        # Drop any ring (outer or hole) that doesn't have enough vertices to
        # form a triangle once the GeoJSON closing duplicate is removed.
        rings = [r for r in rings if len(self._strip_closing_vertex(r)) >= 3]  # noqa: PLR2004
        if not rings:
            return

        ctx_kwargs = self._local_context_kwargs(
            polygon.stroke_color,
            polygon.stroke_width,
            polygon.fill_color,
            polygon.opacity,
            polygon.stroke_opacity,
            polygon.fill_opacity,
        )
        with self.pdf.local_context(**ctx_kwargs):
            if len(rings) == 1:
                ring = self._strip_closing_vertex(rings[0])
                style = self._draw_style(polygon.stroke_color, polygon.fill_color)
                self.pdf.polygon(ring, style=style)
            else:
                self._render_polygon_path(rings, self._polygon_paint_rule(polygon))

    def render_features(self) -> None:
        """Draw all added geometries onto the PDF, clipped to the map area.

        Features are rendered in the order they were added. Anything that
        falls outside the map's image rectangle is clipped via
        :meth:`fpdf.FPDF.rect_clip` so it cannot bleed into the page margins.
        """
        if not self.features:
            return
        with self.pdf.rect_clip(
            self.margin_left, self.margin_top, self.image_width, self.image_height
        ):
            for feature in self.features:
                if isinstance(feature, CircleMarker):
                    self._render_circle_marker(feature)
                elif isinstance(feature, IconMarker):
                    self._render_icon_marker(feature)
                elif isinstance(feature, Line):
                    self._render_line(feature)
                elif isinstance(feature, Polygon):
                    self._render_polygon(feature)

    def render_attribution_and_scale(self) -> None:
        """Draw the tile provider attribution and map scale on the PDF.

        The text is anchored to the bottom-right of the image area.
        """
        text = f"{self.tile_provider.attribution}. Created with {NAME}. Scale: 1:{self.scale}"
        self.pdf.set_xy(
            self.margin_left + self.pdf.epw - self.pdf.get_string_width(text),
            self.margin_top + self.pdf.eph - pt_to_mm(self.pdf.font_size_pt),
        )
        self.pdf.cell(w=0, text=text, align="R", fill=True)

    def download_tiles(
        self,
        num_retries: int = 3,
        sleep_between_retries: int | None = None,
        strict: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        """Download all tile images for the map in parallel, with retries.

        Tiles that have already been downloaded are skipped. Failed tiles
        are retried up to ``num_retries`` times. When ``strict`` is ``False``
        and tiles still fail after all retries, a warning is emitted; when
        ``strict`` is ``True``, a ``RuntimeError`` is raised instead.

        Args:
            num_retries: Maximum number of retry passes before giving up.
            sleep_between_retries: Optional delay (in seconds) between retry
                passes.
            strict: Raise on persistent failures instead of warning.

        Raises:
            RuntimeError: If ``strict`` is ``True`` and one or more tiles
                cannot be downloaded after ``num_retries`` retries.
        """
        # download the tile images
        with (
            ThreadPoolExecutor() as executor,
            httpx.Client(
                headers={
                    "User-Agent": f"{NAME}v{metadata.version('papermap')}",
                    "Accept": "image/png,image/*;q=0.9,*/*;q=0.8",
                },
                timeout=30.0,
                limits=httpx.Limits(
                    max_connections=executor._max_workers,  # noqa: SLF001
                    max_keepalive_connections=executor._max_workers,  # noqa: SLF001
                ),
            ) as client,
        ):
            for num_retry in count():
                # get the unsuccessful tiles
                tiles = [tile for tile in self.tiles if not tile.success]

                # break if all tiles successful
                if not tiles:
                    break

                # possibly sleep between retries
                if num_retry > 0 and sleep_between_retries is not None:
                    time.sleep(sleep_between_retries)

                # break if max number of retries exceeded
                if num_retry >= num_retries:
                    msg = f"Could not download {len(tiles)}/{len(self.tiles)} tiles after {num_retries} retries."
                    if strict:
                        raise RuntimeError(msg)
                    warnings.warn(msg, stacklevel=2)
                    break

                responses = executor.map(
                    client.get,
                    [
                        self.tile_provider.format_url_template(
                            tile=tile, api_key=self.api_key
                        )
                        for tile in tiles
                    ],
                )

                for tile, r in zip(tiles, responses, strict=True):
                    if r.is_success:
                        tile.image = Image.open(BytesIO(r.content)).convert("RGBA")

    def render_base_layer(self) -> None:
        """Download all tiles and assemble the map image.

        Tiles are downloaded in parallel (honouring ``self.strict_download``),
        composited onto a scaled canvas, and then resampled down to the
        target image size in pixels. The result is stored on
        ``self.map_image`` for subsequent embedding in the PDF.
        """
        # download all the required tiles
        self.download_tiles(strict=self.strict_download)

        # initialize scaled map image
        self.map_image_scaled = Image.new(
            "RGB",
            (self.image_width_scaled_px, self.image_height_scaled_px),
            self.background_color,
        )

        # paste all the tiles in the scaled map image
        for tile in self.tiles:
            if tile.image is not None:
                self.map_image_scaled.paste(tile.image, tile.bbox, tile.image)

        # resize the scaled map image
        self.map_image = self.map_image_scaled.resize(
            (self.image_width_px, self.image_height_px), Image.Resampling.LANCZOS
        )

    def render(self) -> None:
        """Render the paper map, consisting of the map image, features (if any), grid (if applicable), attribution and scale."""
        # render the base layer
        self.render_base_layer()

        # paste the map image onto the paper map
        self.pdf.image(self.map_image, w=self.image_width, h=self.image_height)

        # render any added GeoJSON-style features above the base map
        self.render_features()

        # possibly render a coordinate grid (drawn above features)
        self.render_grid()

        # render the attribution and scale to the map
        self.render_attribution_and_scale()

    def save(self, file: str | Path, title: str = NAME, author: str = NAME) -> None:
        """Save the paper map to a file.

        Args:
            file: The file to save the paper map to.
            title: The title of the PDF document. Defaults to `PaperMap`.
            author: The author of the PDF document. Defaults to `PaperMap`.
        """
        self.file = Path(file)
        self.pdf.set_title(title)
        self.pdf.set_author(author)
        self.pdf.set_creator(f"{NAME} v{metadata.version('papermap')}")
        self.pdf.output(self.file)  # pyrefly: ignore
