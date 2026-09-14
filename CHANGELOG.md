# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Calendar Versioning](https://calver.org/).

The **first number** of the version is the year.
The **second number** is incremented with each release, starting at 1 for each year.
The **third number** is for emergencies when we need to start branches for older releases.

## [2026.3.0](https://github.com/sgraaf/papermap/compare/2026.2.0...2026.3.0) (2026-09-14)

This third release in the year 2026 focuses on correctness and robustness. It fixes a number of bugs that silently produced wrong maps: grid lines are no longer drawn mirrored about the map centre and are labelled correctly for any `grid_size`, maps crossing the ±180° meridian render both sides, and MGRS coordinates just north of 64°N are no longer placed about 2,000km too far north. Tile downloads are more resilient, retrying network errors and invalid images instead of aborting the whole map, while raising an error rather than producing a blank map when no tile can be downloaded at all (e.g. due to an invalid API key). Invalid input is now validated up front, before any tiles are downloaded, and the CLI reports errors as concise messages instead of tracebacks. The `geojson` and `gpx` CLI sub-commands gain styling options such as `--stroke` and `--fill`. Finally, `httpx` has been replaced by `httpx2`, the minimum version of the optional `gpx` dependency has been bumped (parsing already-loaded GPX objects now also requires it), and the defunct `komoot` and `openfiremap` tile providers have been removed.

### Added

- Added shared styling options to the `geojson` and `gpx` CLI sub-commands: `--stroke`, `--stroke-width`, `--stroke-opacity`, `--fill`, `--fill-opacity`, `--opacity` and `--marker-radius`. These apply as defaults to every parsed feature; per-feature GeoJSON `simplestyle-spec` properties still take precedence.
- Added `IconMarker.load_icon()`, which returns the icon image, reading it from disk (once) if the icon is a path.

### Changed

- Bumped the minimum version of the optional `gpx` dependency to `2026.3.0`, and narrowed the accepted `gpx_source` type on `PaperMap.from_gpx()`, `PaperMap.add_gpx()` and `gpx_to_features()` from any object exposing `__geo_interface__` to a path-like or a `gpx.GeoGPXModel` instance. As a consequence, parsing an already-loaded GPX object now also requires the optional `gpx` package (previously only reading from disk did); install it with `uv add --extra gpx papermap`.
- `PaperMap.render()` and `PaperMap.download_tiles()` now raise a `RuntimeError` when no tile at all can be downloaded (e.g. due to an invalid API key), even with `strict_download=False`, instead of producing a blank map with only a warning. Tiles failing with a client error that will not succeed on retry (HTTP 4xx other than 408 and 429) are no longer retried.
- `PaperMap` now raises a `ValueError` on construction when a grid is added outside the UTM coverage area (80°S to 84°N), or when the background color is invalid. Previously, these errors were only raised by `render()`, after all tiles had been downloaded.
- Tile requests now identify themselves with a well-formed `User-Agent` header (`papermap/<version> (+https://github.com/sgraaf/papermap)`), as requested by the usage policies of tile providers such as OpenStreetMap.
- The CLI now reports invalid input (e.g. an out-of-range latitude or a malformed MGRS coordinate), tile download failures, a missing optional `gpx` package, and unreadable or unwritable files as a concise `Error: ...` message with exit code 1, instead of a Python traceback.
- Improved the help of the CLI options: `--scale` and `--dpi` now show descriptive `DENOMINATOR` and `DOTS-PER-INCH` placeholders, and the allowed ranges of numeric options (e.g. `[x>=1]`) are no longer shown.
- Replaced the `httpx` dependency with `httpx2`, which is now used to download tiles.

### Removed

- Removed the `komoot` and `openfiremap` tile providers, whose tile servers no longer exist: the Komoot tile domain no longer resolves, and OpenFireMap no longer serves its raster tiles.

### Fixed

- Fixed tile downloads aborting the whole map when a single request failed with a network error (e.g. a timeout) or returned data that is not a valid image. Such tiles are now retried and, if they keep failing, reported like any other failed tile (a warning, or a `RuntimeError` with `strict_download=True`). The failure message now also includes the failure reasons.
- Fixed horizontal (northing) grid lines being drawn mirrored about the map centre, placing them up to one grid square away from the northing their label names.
- Fixed wrong grid labels for any `grid_size` other than 1000m: labels always stepped by 1km per line. Grid lines now lie on multiples of `grid_size`, and are labelled with their UTM coordinate in kilometres (e.g. `583.5` for a 500m grid).
- Fixed maps crossing the ±180° meridian rendering the far side of the meridian blank: its tiles were downloaded but pasted outside the map image. Maps extending beyond the latitude limits of the Web Mercator projection (±85.05°) no longer download tiles from the opposite pole.
- Fixed `mgrs_to_latlon()` (and thereby `PaperMap.from_mgrs()` and the `mgrs` CLI sub-command) placing MGRS coordinates in a narrow strip just north of 64°N about 2,000km too far north.
- Fixed `PaperMap.download_tiles(num_retries=n)` retrying failed tiles only `n - 1` times.
- Fixed a non-positive `grid_size` (or `--grid-size`) hanging the process while consuming ever more memory when rendering the grid. It now raises a `ValueError` (or a usage error in the CLI).
- Fixed `utm_to_latlon()` (and thereby `PaperMap.from_utm()`) silently treating any hemisphere other than `S` (e.g. a lowercase `s`) as the northern hemisphere. It now raises a `ValueError` for a hemisphere other than `N` or `S`, or a zone outside 1-60. The `utm` CLI sub-command now accepts a lowercase hemisphere, and rejects invalid hemispheres and zones with a usage error.
- Fixed `mgrs_to_latlon()` (and thereby `PaperMap.from_mgrs()`) not validating `MGRSCoordinate` objects, and not validating the letters of the 100km square identifier of MGRS strings, which crashed with unhelpful errors (e.g. `IndexError: string index out of range`). It now raises a `ValueError` for an invalid zone, latitude band, 100km square identifier, easting or northing. The `mgrs` CLI sub-command now accepts a lowercase band and square, and rejects zones outside 1-60 with a usage error.
- Fixed `latlon_to_utm()` and `latlon_to_mgrs()` returning the non-existent UTM zone 61 for a longitude of exactly 180°; it now lies in zone 1, like 180°W.
- Fixed `latlon_to_utm()` silently converting a latitude beyond the poles (e.g. 100°) to a coordinate in the opposite hemisphere (e.g. -80°); it now raises a `ValueError`.
- Fixed `utils.dd_to_dms()` returning 60 seconds (e.g. `(0, 59, 60.0)` for `0.99999999999`) instead of carrying over into the minutes and degrees.
- Fixed `utils.dd_to_dms()` losing the sign of values between -1° and 0° (e.g. `-0.5` became `(0, 30, 0.0)`, i.e. `+0.5`). The sign of a negative value is now carried by its first non-zero component (e.g. `(0, -30, 0.0)`), and `utils.dms_to_dd()` treats a value as negative if any of its components is negative.
- Fixed two identical `TileProvider` instances comparing unequal, as their internal subdomain cycles were compared by identity. The subdomain cycle is also no longer included in the `repr()`.
- Fixed the `geojson` and `gpx` CLI sub-commands silently ignoring an explicit `--scale` when combined with `--auto-scale`; this combination is now rejected with a usage error, like it is in `PaperMap.from_geojson()` and `PaperMap.from_gpx()`.
- Fixed the CLI accepting a non-positive `--scale` or `--dpi`, or a negative margin or `--padding`, which crashed with a traceback (e.g. a `ZeroDivisionError`); these are now rejected with a usage error.
- Fixed the MtbMap and Geofabrik Topo tile providers downloading tiles over plain HTTP; they now use HTTPS.
- Fixed a missing or invalid icon file of an `IconMarker` only raising an error after all tiles had been downloaded; icons are now loaded before downloading tiles. Icon files are also no longer kept open after rendering.

## [2026.2.0](https://github.com/sgraaf/papermap/compare/2026.1.0...2026.2.0) (2026-05-17)

This second major release in the year 2026 adds the ability to overlay your own geometries on maps — drop in circle or icon markers, lines, and polygons directly, or load them from GeoJSON and GPX files via new `add_*` methods, the `from_features/from_geojson/from_gpx` classmethods (which can auto-fit the scale to your data with optional padding), and matching `geojson` and `gpx` CLI sub-commands. It also fixes broken URL templates for the Esri, USGS, ÖPNVKarte, and Mapy.cz tile providers.

### Added

- Added `papermap.features`, `papermap.geojson` and `papermap.gpx` modules to overlay geometries on the map. `features` exposes `CircleMarker`, `IconMarker`, `Line` and `Polygon` dataclasses; `geojson.geojson_to_features()` parses GeoJSON files, dicts, or any object exposing `__geo_interface__` (honouring `simplestyle-spec` properties); `gpx.gpx_to_features()` does the same for GPX. Features render above the base map but below the grid, and are clipped to the map area.
- Added builder/loader methods on `PaperMap`: `add_circle_marker()`, `add_icon_marker()`, `add_line()`, `add_polygon()`, `add_feature()`, `add_geojson()` and `add_gpx()`.
- Added `PaperMap.from_features()`, `PaperMap.from_geojson()` and `PaperMap.from_gpx()` classmethods that build a `PaperMap` centred on the supplied geometries' bounding box and pre-populate them on the new map. All three accept `auto_scale` and `padding` keyword arguments: when `auto_scale=True`, the scale is computed to fit the geometries within the printable image area (paper size minus margins minus `padding`) and snapped up to the nearest common cartographic scale (1:1 000, 1:2 500, …, 1:50 000 000). Passing both `auto_scale=True` and an explicit `scale` raises `ValueError`.
- Added `geojson` and `gpx` CLI sub-commands (e.g. `papermap gpx hike.gpx Hike.pdf --auto-scale`), with `--auto-scale` and `--padding` options in addition to the common CLI options. Reading GPX files from disk requires the optional `gpx` package; install it with `uv add --extra gpx papermap`.

### Fixed

- Fixed broken URL templates for the Esri, USGS, ÖPNVKarte, and Mapy.cz tile providers, where the upstream `server`/`MapServer` hostnames and paths had been incorrectly renamed to `provider`/`MapProvider`

## [2026.1.0](https://github.com/sgraaf/papermap/compare/0.3.0...2026.1.0) (2026-01-21)

This is a major release featuring comprehensive geodetic coordinate conversion support, a massive expansion of tile providers, and significant architectural improvements. The new `geodesy` module implements high-precision coordinate conversions between geographic (lat/lon), UTM, MGRS, and ECEF coordinate systems using Karney (2011) and Bowring (1985) algorithms. The tile provider ecosystem has grown from 20+ to over 100 providers, including OpenStreetMap variants, Stadia Maps, CartoDB, ESRI, NASA GIBS, and regional providers. The HTTP client has been modernized by migrating from `requests` to `httpx`, and tile downloads now gracefully handle failures by default. This release also drops support for Python 3.7-3.10 and adds support for Python 3.12-3.14.

### Added

- Added new `geodesy` module for comprehensive coordinate conversions between different coordinate systems:
  - Geographic coordinates (latitude/longitude in WGS84)
  - UTM (Universal Transverse Mercator) coordinates
  - MGRS (Military Grid Reference System) coordinates
  - ECEF (Earth-Centered, Earth-Fixed) Cartesian coordinates
- Added public API functions for coordinate conversions (exported from `papermap` package):
  - `latlon_to_utm()` - Convert geographic coordinates to UTM
  - `utm_to_latlon()` - Convert UTM coordinates to geographic
  - `latlon_to_mgrs()` - Convert geographic coordinates to MGRS
  - `mgrs_to_latlon()` - Convert MGRS coordinates to geographic
  - `latlon_to_ecef()` - Convert geographic coordinates to ECEF Cartesian
  - `ecef_to_latlon()` - Convert ECEF Cartesian to geographic
  - `format_latlon()`, `format_utm()`, `format_mgrs()`, `format_ecef()` - Format coordinates as human-readable strings
- Added coordinate type classes: `LatLonCoordinate`, `UTMCoordinate`, `MGRSCoordinate`, `ECEFCoordinate` (NamedTuples)
- Added `Ellipsoid` dataclass for reference ellipsoid parameters with `WGS_84_ELLIPSOID` constant
- Added `PaperMap.from_utm()` classmethod to create a PaperMap instance from UTM coordinates
- Added `PaperMap.from_mgrs()` classmethod to create a PaperMap instance from MGRS coordinates (supports both MGRSCoordinate objects and MGRS strings)
- Added `PaperMap.from_ecef()` classmethod to create a PaperMap instance from ECEF coordinates
- Added `mgrs`, and `ecef` CLI sub-commands to generate paper maps from MGRS and ECEF coordinates, respectively
- Added `--strict` flag to CLI and `strict_download` parameter to `PaperMap` class to control tile download failure behavior. By default (strict=False), PaperMap now allows graceful degradation when some tiles fail to download, rendering failed tiles as background color and issuing a warning. When strict=True, the previous behavior is maintained where any tile download failure raises an exception.
- Added new `tile_providers` subpackage with provider-based organization for improved maintainability
- Added 100+ new tile providers from various providers including:
  - OpenStreetMap regional variants (DE, CH, France, HOT, BZH)
  - Stadia Maps (including Stamen styles: Toner, Terrain, Watercolor)
  - CartoDB/Carto (Positron, Dark Matter, Voyager)
  - Esri (WorldStreetMap, WorldImagery, WorldTopoMap, and more)
  - HERE Maps (requires API key)
  - USGS (USTopo, USImagery)
  - NASA GIBS (satellite imagery)
  - MapTiler (requires API key)
  - Jawg Maps (requires API key)
  - TomTom (requires API key)
  - CyclOSM (bicycle-oriented maps)
  - OpenSeaMap (nautical charts)
  - Waymarked Trails (hiking, cycling, MTB, slopes, riding, skating)
  - Regional providers: BasemapAT (Austria), NLMaps (Netherlands), SwissFederalGeoportal
  - And many more specialty maps
- Added support for Python 3.12, 3.13 and 3.14.

### Changed

- Improved coordinate conversion accuracy by implementing Karney's (2011) series expansion of the Transverse Mercator projection for UTM conversions, achieving sub-millimeter accuracy
- Refactored coordinate conversion functions from `utils.py` into the new `geodesy` module with improved implementations:
  - Replaced `spherical_to_utm()` and `utm_to_spherical()` with `latlon_to_utm()` and `utm_to_latlon()` using high-accuracy Karney (2011) algorithms
  - Replaced `spherical_to_cartesian()` and `cartesian_to_spherical()` with `latlon_to_ecef()` and `ecef_to_latlon()` using Bowring (1985) iterative method
  - Consolidated angle wrapping functions (`wrap()`, `wrap90()`, `wrap180()`, `wrap360()`) into `wrap_angle()`, `wrap_lat()`, and `wrap_lon()`
- Migrated from `requests` to `httpx` for HTTP client functionality, utilizing modern features such as improved connection pooling and timeout handling
- Refactored tests to use `pytest-httpx` for cleaner and more maintainable HTTP mocking
- Reorganized package structure by consolidating `defaults.py`, `constants.py`, and `typing.py` into their logical homes:
  - Tile provider configurations moved to new `tile_providers` subpackage
  - Paper sizes and default values moved to `papermap.py`
  - Geodetic coordinate conversion functions and constants moved to new `geodesy` module
- Renamed `TileServer` class to `TileProvider` and enhanced it with new properties:
  - Added `key` property for tile provider key (lowercase with dashes)
  - Added `name` property for tile provider display name
  - Added `html_attribution` property for HTML-formatted attribution with hyperlinks
  - Added `bounds` property for geographic bounds (optional)
  - Renamed `mirrors` to `subdomains` for better clarity
  - Renamed `mirrors_cycle` to `subdomains_cycle`
  - Updated URL template placeholders: `{zoom}` → `{z}`, `{mirror}` → `{s}`, `{api_key}` → `{a}`
- Renamed some tile providers for consistency
- Refactored `PaperMap.__init__` method into smaller, focused private methods to improve readability and testability:
  - Extracted coordinate validation into `_validate_coordinates`
  - Extracted tile provider setup into `_validate_and_set_tile_provider`
  - Extracted paper size configuration into `_validate_and_set_paper_size`
  - Extracted zoom calculations into `_compute_zoom_and_resize_factor`
  - Extracted image dimension calculations into `_compute_image_dimensions`
  - Extracted tile initialization into `_initialize_tiles`
  - Extracted PDF initialization into `_initialize_pdf`
- Renamed `PaperMap` to `papermap` (purely aesthetically, no changes in installation or usage required).

### Removed

- Removed support for Python 3.7, 3.8, 3.9 and 3.10.
- Removed `papermap.defaults`, `papermap.constants`, and `papermap.typing` modules (contents redistributed to other modules)

## 0.3.0 (2022-11-09)

This is a pretty big release with a completely overhauled codebase. For this, I used my new [cookiecutter-python-package](https://github.com/sgraaf/cookiecutter-python-package) Python package template. As such, this release comes with much higher code quality, documentation, automation and some important changes to the core functionality of PaperMap.

### Changes

- Completely refactored codebase, with:
  - Moved source code from `./papermap` to `./src/papermap`
  - Switched to [fpdf2](https://pyfpdf.github.io/fpdf2/) for the PDF creation
  - Added custom types
  - Fully typed
  - Added class for tile servers
  - Re-implemented spherical-to-UTM conversions
  - Removed GPX support (will come back soon via [PyGPX](https://pypi.org/project/gpx/))
  - Removed tests (will come back soon via [pytest](https://docs.pytest.org/en/stable/contents.html))
- Added documentation via [Read the Docs](https://readthedocs.org/)
- Added CI/CD via GitHub Actions
- Added [pre-commit hooks](https://pre-commit.com) w/ CI-integration
- Switched to [Click](https://click.palletsprojects.com/en/8.1.x/) for the CLI
- Switched to [flit](https://flit.pypa.io/en/stable/) for building & releasing the package

## 0.2.2 (2020-11-26)

### Changes

- Added support for custom fonts

## 0.2.1 (2020-11-03)

### Changes

- Added GPX support
- Added more tile servers
- Added tests
- Refactored the codebase

## 0.1.0 (2019-10-09)

### Changes

- Initial release of PaperMap
