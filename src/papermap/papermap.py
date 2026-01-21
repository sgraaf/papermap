import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from dataclasses import KW_ONLY, InitVar, dataclass, field
from decimal import Decimal
from importlib import metadata
from io import BytesIO
from itertools import count
from math import ceil, floor, radians
from pathlib import Path
from typing import Any, Self

import httpx
from fpdf import FPDF
from PIL import Image

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
    drange,
    get_string_formatting_arguments,
    lat_to_y,
    lon_to_x,
    mm_to_px,
    pt_to_mm,
    scale_to_zoom,
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

DEFAULT_DPI: int = 300
"""Default dots per inch."""

DEFAULT_BACKGROUND_COLOR: str = "#fff"
"""Default background color."""

DEFAULT_GRID_SIZE: int = 1_000
"""Default grid size in meters."""


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
        ValueError: If the scale is "out of bounds".
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
    map_image_scaled: Image.Image = field(init=False)
    map_image: Image.Image = field(init=False)
    file: Path = field(init=False)

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

    def _validate_coordinates(self) -> None:
        """Validate latitude and longitude are within valid ranges.

        Args:
            lat: Latitude to validate.
            lon: Longitude to validate.

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
        """Validate paper size and set width and height.

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
            ValueError: If computed zoom is out of bounds for the tile provider.
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
            raise ValueError(msg)

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

        # Compute the scaled grid size (in mm)
        self.grid_size_scaled = Decimal(self.grid_size * 1_000 / self.scale)

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

    def compute_grid_coordinates(
        self,
    ) -> tuple[list[tuple[Decimal, str]], list[tuple[Decimal, str]]]:
        # convert Lat/Lon coordinate into UTM coordinate (easting, northing, zone, hemisphere)
        easting, northing, _, _ = latlon_to_utm(self.lat, self.lon)

        # round easting/northing to nearest thousand
        easting_rnd = round(easting, -3)
        northing_rnd = round(northing, -3)

        # compute distance between x/y and x/y_rnd in mm
        d_easting = Decimal((easting - easting_rnd) / self.scale * 1000)
        d_northing = Decimal((northing - northing_rnd) / self.scale * 1000)

        # determine center grid coordinate (in mm)
        easting_grid_center = Decimal(self.image_width / 2) - d_easting
        northing_grid_center = Decimal(self.image_height / 2) - d_northing

        # determine start grid coordinate (in mm)
        easting_grid_start = easting_grid_center % self.grid_size_scaled
        northing_grid_start = northing_grid_center % self.grid_size_scaled

        # determine the start grid coordinate label
        easting_label_start = int(
            Decimal(easting_rnd / 1000) - easting_grid_center // self.grid_size_scaled
        )
        northing_label_start = int(
            Decimal(northing_rnd / 1000) + northing_grid_center // self.grid_size_scaled
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

    def render_attribution_and_scale(self) -> None:
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
        """Render the paper map, consisting of the map image, grid (if applicable), attribution and scale."""
        # render the base layer
        self.render_base_layer()

        # paste the map image onto the paper map
        self.pdf.image(self.map_image, w=self.image_width, h=self.image_height)

        # possibly render a coordinate grid
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
