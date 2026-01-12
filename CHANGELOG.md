# Changelog

## [Unreleased]

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
