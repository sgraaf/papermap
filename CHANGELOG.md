# Changelog

## [Unreleased]

### Added

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

### Changed

- Migrated from `requests` to `httpx` for HTTP client functionality, utilizing modern features such as improved connection pooling and timeout handling
- Refactored tests to use `pytest-httpx` for cleaner and more maintainable HTTP mocking
- Reorganized package structure by consolidating `defaults.py`, `constants.py`, and `typing.py` into their logical homes:
  - Tile provider configurations moved to new `tile_providers` subpackage
  - Paper sizes and default values moved to `papermap.py`
  - Geographic constants and type aliases moved to `utils.py`
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

### Removed

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
