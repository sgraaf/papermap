# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Calendar Versioning](https://calver.org/).

The **first number** of the version is the year.
The **second number** is incremented with each release, starting at 1 for each year.
The **third number** is for emergencies when we need to start branches for older releases.

## [Unreleased]

### Added

- Added new `papermap.features` module with public dataclasses for overlaying markers, lines and polygons (i.e., features), and a `geojson_to_features()` parser that accepts GeoJSON dicts or any object implementing the `__geo_interface__` protocol (with optional `simplestyle-spec` properties). Features render above the base map but below the grid, and are clipped to the map area.

- Added convenience builder methods on `PaperMap` for adding features:

  - `add_circle_marker()`
  - `add_icon_marker()`
  - `add_line()`
  - `add_polygon()`
  - `add_feature()`
  - `add_geojson()`.

  Features render above the base map but below the grid, and are clipped to the map area.

- Added `PaperMap.from_features()` and `PaperMap.from_geojson()` classmethods to create a `PaperMap` centred on the geographic centre (bounding box midpoint) of one or more features (or geometries parsed from a GeoJSON object, or any object exposing `__geo_interface__`). The provided/parsed features are also added to the new map so they will be drawn when `render()` is called. Both classmethods accept `auto_scale` and `padding` keyword arguments: when `auto_scale=True`, the map scale is computed automatically so that the supplied features fit within the printable image area (paper size minus margins minus `padding`), then snapped up to the nearest common cartographic scale (1:1 000, 1:2 500, …, 1:50 000 000). Passing both `auto_scale=True` and an explicit `scale` raises `ValueError`.

- Added new `papermap.gpx` module with a `gpx_to_features()` parser that turns a `.gpx` file path (or any `__geo_interface__` object, such as a `gpx.GPX` instance) into map features. Waypoints become circle markers, routes become lines, and each segment of each track becomes its own line. Reading GPX files from disk requires the optional `gpx` package; install it with `pip install papermap[gpx]`.

- Added `PaperMap.from_gpx()` classmethod and `PaperMap.add_gpx()` instance method, mirroring the GeoJSON counterparts. `from_gpx()` accepts `auto_scale` and `padding` keyword arguments.

- Added a `gpx` CLI sub-command: `papermap gpx hike.gpx Hike.pdf --auto-scale`. Supports `--auto-scale` and `--padding` options in addition to the common CLI options.

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
