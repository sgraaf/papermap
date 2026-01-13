# Changelog

## [Unreleased]

### Changed

- Migrated from `requests` to `httpx` for HTTP client functionality, utilizing modern features such as improved connection pooling and timeout handling
- Refactored tests to use `pytest-httpx` for cleaner and more maintainable HTTP mocking
- Reorganized package structure by consolidating `defaults.py`, `constants.py`, and `typing.py` into their logical homes:
  - Tile server configurations moved to `tile_server.py`
  - Paper sizes and default values moved to `papermap.py`
  - Geographic constants and type aliases moved to `utils.py`
- Enhanced `TileServer` dataclass with new properties:
  - Added `key` property for tile server key (lowercase with dashes)
  - Added `name` property for tile server display name
  - Added `html_attribution` property for HTML-formatted attribution with hyperlinks
  - Added `bounds` property for geographic bounds (optional)
  - Renamed `mirrors` to `subdomains` for better clarity
  - Renamed `mirrors_cycle` to `subdomains_cycle`
  - Updated URL template placeholders: `{zoom}` → `{z}`, `{mirror}` → `{s}`, `{api_key}` → `{a}`

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
