import os
import time
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from functools import partial
from importlib import metadata
from io import BytesIO
from itertools import count
from math import ceil, floor, radians
from pathlib import Path

from fpdf import FPDF
from PIL import Image
from requests import Session

from .constants import HEADERS, NAME, TILE_SIZE
from .defaults import (
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_DPI,
    DEFAULT_GRID_SIZE,
    DEFAULT_MARGIN,
    DEFAULT_SCALE,
    DEFAULT_SIZE,
    DEFAULT_TILE_SERVER,
    SIZE_TO_DIMENSIONS_MAP,
    SIZES,
    TILE_SERVERS,
    TILE_SERVERS_MAP,
)
from .tile import Tile
from .utils import (
    drange,
    get_string_formatting_arguments,
    lat_to_y,
    lon_to_x,
    mm_to_px,
    pt_to_mm,
    scale_to_zoom,
    spherical_to_utm,
)


class PaperMap:
    """A paper map.

        >>> from papermap import PaperMap
        >>> pm = PaperMap(13.75889, 100.49722)
        >>> pm.render()
        >>> pm.save("Bangkok.pdf")

    Args:
        lat: Latitude of the center of the map.
        lon: Longitude of the center of the map
        tile_server: Tile server to serve as the base of the paper map. Defaults to `OpenStreetMap`.
        api_key: API key for the chosen tile server (if applicable). Defaults to `None`.
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

    Raises:
        ValueError: If the tile server is invalid.
        ValueError: If no API key is specified (when applicable).
        ValueError: If the paper size is invalid.
        ValueError: If the scale is "out of bounds".
    """

    def __init__(  # noqa: PLR0913, PLR0915
        self,
        lat: float,
        lon: float,
        tile_server: str = DEFAULT_TILE_SERVER,
        api_key: str | None = None,
        size: str = DEFAULT_SIZE,
        use_landscape: bool = False,  # noqa: FBT001, FBT002
        margin_top: int = DEFAULT_MARGIN,
        margin_right: int = DEFAULT_MARGIN,
        margin_bottom: int = DEFAULT_MARGIN,
        margin_left: int = DEFAULT_MARGIN,
        scale: int = DEFAULT_SCALE,
        dpi: int = DEFAULT_DPI,
        background_color: str = DEFAULT_BACKGROUND_COLOR,
        add_grid: bool = False,  # noqa: FBT001, FBT002
        grid_size: int = DEFAULT_GRID_SIZE,
    ) -> None:
        self.lat = lat
        self.lon = lon
        self.api_key = api_key
        self.use_landscape = use_landscape
        self.margin_top = margin_top
        self.margin_right = margin_right
        self.margin_bottom = margin_bottom
        self.margin_left = margin_left
        self.scale = scale
        self.dpi = dpi
        self.background_color = background_color
        self.add_grid = add_grid
        self.grid_size = grid_size

        # get the tile server
        if tile_server in TILE_SERVERS_MAP:
            self.tile_server = TILE_SERVERS_MAP[tile_server]
        else:
            msg = f"Invalid tile server. Please choose one of {', '.join(TILE_SERVERS)}"
            raise ValueError(msg)

        # get the tile server mirrors
        self.mirrors = self.tile_server.mirrors if self.tile_server.mirrors else []

        # check whether an API key is provided, if it is needed
        if (
            "api_key" in get_string_formatting_arguments(self.tile_server.url_template)
            and self.api_key is None
        ):
            msg = f"No API key specified for {tile_server} tile server"
            raise ValueError(msg)

        # get the paper size (in mm)
        if size in SIZE_TO_DIMENSIONS_MAP:
            self.width, self.height = SIZE_TO_DIMENSIONS_MAP[size]
            if self.use_landscape:
                self.width, self.height = self.height, self.width
        else:
            msg = f"Invalid paper size. Please choose one of {', '.join(SIZES)}"
            raise ValueError(msg)

        # compute the zoom and resize factor
        self.zoom = scale_to_zoom(self.scale, self.lat, self.dpi)
        self.zoom_scaled = floor(self.zoom)
        self.resize_factor = 2**self.zoom_scaled / 2**self.zoom

        # make sure the zoom is not out of bounds
        if (
            self.zoom_scaled < self.tile_server.zoom_min
            or self.zoom_scaled > self.tile_server.zoom_max
        ):
            msg = f"Scale out of bounds for {tile_server} tile server."
            raise ValueError(msg)

        # compute the width and height of the image (in mm)
        self.image_width = self.width - self.margin_left - self.margin_right
        self.image_height = self.height - self.margin_top - self.margin_bottom

        # perform conversions
        self.image_width_px = mm_to_px(self.image_width, self.dpi)
        self.image_height_px = mm_to_px(self.image_height, self.dpi)
        self.φ = radians(self.lat)
        self.λ = radians(self.lon)

        # compute the scaled grid size (in mm)
        self.grid_size_scaled = Decimal(self.grid_size * 1_000 / self.scale)

        # compute the scaled width and height of the image (in px)
        self.image_width_scaled_px = round(self.image_width_px * self.resize_factor)
        self.image_height_scaled_px = round(self.image_height_px * self.resize_factor)

        # determine the center tile
        self.x_center = lon_to_x(self.lon, self.zoom_scaled)
        self.y_center = lat_to_y(self.lat, self.zoom_scaled)

        # determine the tiles required to produce the map image
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

        # initialize the tiles
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

        # initialize the pdf document
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
        # convert WGS 84 point (lat, lon) into UTM coordinate (x, y, zone_number, hemisphere)
        x, y, _, _ = spherical_to_utm(self.lat, self.lon)

        # round UTM/RD coordinates to nearest thousand
        x_rnd = round(x, -3)
        y_rnd = round(y, -3)

        # compute distance between x/y and x/y_rnd in mm
        dx = Decimal((x - x_rnd) / self.scale * 1000)
        dy = Decimal((y - y_rnd) / self.scale * 1000)

        # determine center grid coordinate (in mm)
        x_grid_center = Decimal(self.image_width / 2) - dx
        y_grid_center = Decimal(self.image_height / 2) - dy

        # determine start grid coordinate (in mm)
        x_grid_start = x_grid_center % self.grid_size_scaled
        y_grid_start = y_grid_center % self.grid_size_scaled

        # determine the start grid coordinate label
        x_label_start = int(
            Decimal(x_rnd / 1000) - x_grid_center // self.grid_size_scaled
        )
        y_label_start = int(
            Decimal(y_rnd / 1000) + y_grid_center // self.grid_size_scaled
        )

        # determine the grid coordinates (in mm)
        x_grid_cs = list(
            drange(x_grid_start, Decimal(self.image_width), self.grid_size_scaled)
        )
        y_grid_cs = list(
            drange(y_grid_start, Decimal(self.image_height), self.grid_size_scaled)
        )

        # determine the grid coordinates labels
        x_labels = [x_label_start + i for i in range(len(x_grid_cs))]
        y_labels = [y_label_start - i for i in range(len(y_grid_cs))]

        x_grid_cs_and_labels = list(zip(x_grid_cs, map(str, x_labels), strict=True))
        y_grid_cs_and_labels = list(zip(y_grid_cs, map(str, y_labels), strict=True))

        return x_grid_cs_and_labels, y_grid_cs_and_labels

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
                label_width = self.pdf.get_string_width(label)

                # draw grid line
                self.pdf.line(x_, self.margin_top, x_, self.margin_top + self.pdf.eph)

                # draw label
                if x_ + label_width < self.margin_left + self.pdf.epw:
                    self.pdf.set_xy(x_ - label_width / 2, self.margin_top)
                    self.pdf.cell(w=label_width, text=label, align="C", fill=True)

            # draw horizontal grid lines
            for y, label in y_grid_cs_and_labels:
                y_ = float(y + self.margin_top)
                label_width = self.pdf.get_string_width(label)

                # draw grid line
                self.pdf.line(self.margin_left, y_, self.margin_left + self.pdf.epw, y_)

                # draw label
                if y_ + label_width < self.margin_top + self.pdf.eph:
                    self.pdf.set_xy(self.margin_left, y_ + label_width / 2)
                    with self.pdf.rotation(90):
                        self.pdf.cell(w=label_width, text=label, align="C", fill=True)

            self.pdf.set_font_size(12)

    def render_attribution_and_scale(self) -> None:
        text = f"{self.tile_server.attribution}. Created with {NAME}. Scale: 1:{self.scale}"
        self.pdf.set_xy(
            self.margin_left + self.pdf.epw - self.pdf.get_string_width(text),
            self.margin_top + self.pdf.eph - pt_to_mm(self.pdf.font_size_pt),
        )
        self.pdf.cell(w=0, text=text, align="R", fill=True)

    def download_tiles(
        self, num_retries: int = 3, sleep_between_retries: int | None = None
    ) -> None:
        # download the tile images
        with (
            Session() as session,
            ThreadPoolExecutor(min(32, (os.cpu_count() or 1) + 4)) as executor,
        ):
            session.headers.update(HEADERS)

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
                    raise RuntimeError(msg)

                responses = executor.map(
                    partial(session.get, timeout=30),
                    [
                        self.tile_server.format_url_template(
                            tile=tile, api_key=self.api_key
                        )
                        for tile in tiles
                    ],
                )

                for tile, r in zip(tiles, responses, strict=True):
                    if r.ok:
                        tile.image = Image.open(BytesIO(r.content)).convert("RGBA")

    def render_base_layer(self) -> None:
        # download all the required tiles
        self.download_tiles()

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

    def __repr__(self) -> str:
        return f"PaperMap({self.lat}, {self.lon})"
