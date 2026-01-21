# CLAUDE.md - AI Assistant Guide for PaperMap

## Project Overview

**PaperMap** is a Python package and CLI tool for creating ready-to-print paper maps from various tile providers (OpenStreetMap, Google Maps, ESRI, etc.). The project generates PDF maps at customizable scales, sizes (A0-A7, letter, legal), and orientations with optional UTM grid overlays.

- **Current Version:** 2026.1.0 (CalVer: YYYY.N.N)
- **License:** GNU General Public License v3+
- **Python Support:** 3.11, 3.12, 3.13, 3.14
- **Package Manager:** uv
- **Documentation:** https://papermap.readthedocs.io/

## Repository Structure

```
papermap/
├── src/papermap/          # Main source code
│   ├── __init__.py        # Package initialization, exports PaperMap
│   ├── __main__.py        # Entry point for CLI
│   ├── cli.py             # Click-based CLI implementation
│   ├── papermap.py        # Core PaperMap class (main logic)
│   ├── tile_provider.py   # TileProvider dataclass
│   ├── tile_providers/    # Tile provider configurations for various map providers
│   ├── tile.py            # Tile dataclass for map tiles
│   ├── geodesy.py         # Geodetic coordinate conversions (UTM, MGRS, ECEF)
│   ├── utils.py           # Utility functions (coordinate conversions, etc.)
│   └── py.typed           # PEP 561 marker for type information
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Shared fixtures
│   ├── smoke_test.py      # Smoke tests for package installation
│   ├── test_cli.py        # CLI tests
│   ├── test_integration.py # Integration tests
│   ├── test_papermap.py   # PaperMap class tests
│   ├── test_tile.py       # Tile tests
│   ├── test_tile_provider.py # TileProvider tests
│   └── test_utils.py      # Utility function tests
├── docs/                  # Sphinx documentation
│   ├── conf.py            # Sphinx configuration
│   ├── index.md           # Documentation index
│   ├── api.md             # API reference
│   ├── cli.md             # CLI reference (auto-generated with cog)
│   ├── usage.md           # Usage guide
│   ├── changelog.md       # Includes CHANGELOG.md
│   └── _static/           # Static assets (example PDFs)
├── .github/workflows/     # GitHub Actions
│   ├── ci.yml             # CI workflow (pre-commit hooks)
│   ├── test.yml           # Test workflow (pytest across Python versions)
│   └── publish.yml        # PyPI publishing workflow
├── pyproject.toml         # Project metadata and dependencies
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── CHANGELOG.md           # Changelog (Keep a Changelog format)
├── README.md              # Project README
├── uv.lock                # uv lockfile
├── .editorconfig          # Editor configuration
└── .gitignore             # Git ignore patterns
```

## Recent Major Changes (Unreleased)

**Important architectural changes to be aware of:**

1. **Geodesy Module Addition:**

   - New `geodesy.py` module providing comprehensive coordinate conversions
   - Implements Karney (2011) high-precision UTM ↔ lat/lon conversions (sub-millimeter accuracy)
   - Adds MGRS (Military Grid Reference System) support
   - Adds ECEF (Earth-Centered, Earth-Fixed) coordinate support
   - Provides `LatLonCoordinate`, `UTMCoordinate`, `MGRSCoordinate`, `ECEFCoordinate` types
   - Replaces some utility functions in `utils.py` with more accurate implementations
   - Per-file ruff ignores configured for mathematical code (Greek letters, math symbols)

1. **HTTP Client Migration:** Migrated from `requests` to `httpx` for modern async-capable HTTP client

   - Test mocking now uses `pytest-httpx` instead of manual response mocking
   - Connection pooling and timeout handling improved

1. **Package Restructuring:**

   - Tile providers moved from `defaults.py` to new `tile_providers/` subpackage
   - Provider configurations organized by vendor in separate modules
   - 100+ tile providers now available (up from 20+)

1. **TileProvider Enhancements:**

   - Renamed from `TileServer` to `TileProvider`
   - Added `key`, `name`, `html_attribution`, and `bounds` properties
   - Renamed `mirrors` → `subdomains`, `mirrors_cycle` → `subdomains_cycle`
   - Updated URL placeholders: `{zoom}` → `{z}`, `{mirror}` → `{s}`, `{api_key}` → `{a}`

1. **Graceful Tile Download Failures:**

   - New `strict_download` parameter (defaults to `False`)
   - Failed tiles render as background color with warning when `strict_download=False`
   - Set `strict_download=True` for previous behavior (raise exception on failure)

1. **Code Organization:**

   - `PaperMap.__init__` refactored into focused private methods for better testability
   - Constants consolidated into logical homes (papermap.py, utils.py)

## Requirements for Every Change

**IMPORTANT:** For every change made to the codebase, the following conditions MUST be met:

1. **Tests:** Any missing tests are added to the test suite.
1. **Tests Pass:** All tests must pass:
   ```bash
   uv run pytest
   ```
1. **Pre-commit Hooks Pass:** All checks in the pre-commit hooks must pass:
   ```bash
   uv run prek run --all-files
   ```
1. **API Documentation:** Any new modules are added to the API reference in `docs/api.md`.
1. **CLI Documentation:** Any new CLI sub-commands are added to the CLI reference in `docs/cli.md`.
1. **Changelog:** An entry (based on the Keep a Changelog format) is added to `CHANGELOG.md`.
1. **README:** Any user-facing changes are reflected in the readme in `README.md`.

## Development Environment and Tools

### Build System

- **Build Backend:** uv_build (>=0.9.11, \<0.10.0)
- **Package Manager:** uv
- **Installation:** Install uv from https://docs.astral.sh/uv/
- **HTTP Client:** httpx (replaced requests in recent versions)

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/sgraaf/papermap.git
cd papermap

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (including dev dependencies)
uv sync --dev

# Install pre-commit hooks
uv run prek install
```

### Code Quality Tools

#### Pre-commit Hooks (runs on every commit)

The project uses `prek` (a pre-commit alternative) for running hooks. Hooks are defined in `.pre-commit-config.yaml`:

1. **Basic Checks:** JSON, TOML, XML, YAML validation, EOF fixer, trailing whitespace
1. **pyproject.toml validation:** Validates project configuration
1. **GitHub workflows validation:** Validates .github/workflows/\*.yml
1. **ReadTheDocs validation:** Validates .readthedocs.yaml
1. **Ruff:** Python linter and formatter (replaces flake8, isort, Black)
   - `ruff-check`: Linting with auto-fix and unsafe fixes
   - `ruff-format`: Code formatting
1. **Type Checkers:**
   - `mypy`: Static type checker
   - `pyrefly`: Facebook's Python type checker
   - `ty`: Extremely fast Python type checking
1. **Codespell:** Spell checker for code and docs
1. **Cog:** Auto-generates CLI documentation in `docs/cli.md`
1. **mdformat:** Markdown formatter (with myst and ruff plugins)
1. **Prettier:** YAML formatter

#### Ruff Configuration (pyproject.toml)

```toml
[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "COM812",  # missing-trailing-comma, handled by formatter
    "D100",    # undocumented-public-module
    "D102",    # undocumented-public-method
    "D105",    # undocumented-magic-method
    "D107",    # undocumented-public-init
    "E501",    # line-too-long, handled by formatter
    "PLC2401", # non-ascii-name (allows Greek letters in math code)
]
pydocstyle.convention = "google"
```

#### Per-file Ignores

- `__init__.py`: F401 (unused imports) - allows re-exports
- `docs/conf.py`: INP001 (implicit namespace package)
- `src/papermap/cli.py`: ANN401 (any-type)
- `src/papermap/utils.py`: N806, PLR2004 (for mathematical code)
- `tests/**/test_*.py`: D (docstrings), PLR2004, S101 (assert)
- `tests/conftest.py`: D401 (non-imperative mood)
- `tests/smoke_test.py`: PLR2004, S101

### Editor Configuration

- **Indent:** 4 spaces (Python), 2 spaces (YAML), tabs (Makefile)
- **Line Endings:** LF
- **Charset:** UTF-8
- **Final Newline:** Yes
- **Trailing Whitespace:** Trimmed (except Markdown)

## Code Architecture

### Core Components

#### 1. PaperMap Class (`papermap.py`)

The main class that orchestrates map generation.

**Key Methods:**

- `__init__()` - Initialize map with coordinates, size, scale, tile provider
  - Delegates to private initialization methods for better organization:
  - `_validate_coordinates()` - Validates lat/lon ranges
  - `_validate_and_set_tile_provider()` - Sets up tile provider
  - `_validate_and_set_paper_size()` - Configures paper dimensions
  - `_compute_zoom_and_resize_factor()` - Calculates zoom level
  - `_compute_image_dimensions()` - Determines image size
  - `_initialize_tiles()` - Creates tile grid
  - `_initialize_pdf()` - Sets up PDF document
- `render()` - Main rendering pipeline (base layer → grid → attribution)
- `render_base_layer()` - Downloads tiles and assembles map image
- `download_tiles()` - Parallel tile downloading with retries and optional graceful failure
- `render_grid()` - Adds UTM coordinate grid overlay
- `render_attribution_and_scale()` - Adds attribution and scale text
- `compute_grid_coordinates()` - Calculates UTM grid lines
- `save()` - Exports to PDF file
- `from_utm()` - Class method to create PaperMap from UTM coordinates

**Key Attributes:**

- Coordinate system conversions (lat/lon to tile coordinates)
- Zoom level calculations based on scale and DPI
- Tile boundary calculations
- PDF document (FPDF instance)

#### 2. TileProvider Class (`tile_provider.py`)

Dataclass representing a tile provider configuration.

**Fields:**

- `key: str` - Tile provider key (lowercase with dashes)
- `name: str` - Tile provider display name
- `attribution: str` - Attribution text
- `html_attribution: str` - HTML-formatted attribution with hyperlinks
- `url_template: str` - URL with placeholders: \{x}, \{y}, \{z}, \{s}, \{a}
  - `{x}` - Tile x coordinate
  - `{y}` - Tile y coordinate
  - `{z}` - Zoom level
  - `{s}` - Subdomain (optional, for load balancing)
  - `{a}` - API key (optional)
- `zoom_min: int` - Minimum zoom level
- `zoom_max: int` - Maximum zoom level
- `bounds: Optional[tuple]` - Geographic bounds (min_lon, min_lat, max_lon, max_lat)
- `subdomains: Optional[List]` - Load balancing subdomains
- `subdomains_cycle: cycle` - Iterator for round-robin subdomain selection

**Method:**

- `format_url_template(tile, api_key)` - Formats URL with tile coordinates and API key

#### 3. Tile Class (`tile.py`)

Dataclass for individual map tiles.

#### 4. CLI (`cli.py`)

Click-based command-line interface.

**Commands:**

- `latlon` - Generate map from latitude/longitude (default)
- `utm` - Generate map from UTM coordinates

**Common Options:**

- `--tile-provider` - Choose from 20+ tile providers
- `--paper-size` - Paper size (a0-a7, letter, legal)
- `--landscape` - Landscape orientation
- `--scale` - Map scale (default: 25000)
- `--dpi` - Resolution (default: 300)
- `--grid` - Add UTM grid overlay
- `--api-key` - API key for commercial tile providers

#### 5. Utilities (`utils.py`)

Comprehensive utility functions for:

- **Coordinate Conversions:** lat/lon ↔ tile coordinates, spherical ↔ UTM, spherical ↔ cartesian
- **Unit Conversions:** mm ↔ px, mm ↔ pt, degrees ↔ DMS
- **Angle Operations:** wrap(), wrap90(), wrap180(), wrap360()
- **Scale/Zoom:** scale_to_zoom(), zoom_to_scale()
- **UTM Functions:** spherical_to_zone(), spherical_to_utm(), utm_to_spherical()

Mathematical implementations follow Karney (2011) paper on Transverse Mercator projection.

#### 6. Tile Providers (`tile_providers/`)

Subpackage containing 100+ tile provider configurations organized by provider:

- **`__init__.py`** - Exports `KEY_TO_TILE_PROVIDER`, `TILE_PROVIDER_KEYS`, `DEFAULT_TILE_PROVIDER_KEY`
- **Provider modules:** `openstreetmap.py`, `google.py`, `esri.py`, `stadia.py`, `thunderforest.py`, `cartodb.py`, `here.py`, `maptiler.py`, `jawg.py`, `tomtom.py`, `cyclosm.py`, `openseamap.py`, `usgs.py`, `nasagibs.py`, `wikimedia.py`, `swiss.py`, `nlmaps.py`, `basemap_at.py`, `misc.py`
- Each module contains TileProvider configurations for that provider's tile services

#### 7. Geodesy Module (`geodesy.py`)

Comprehensive geodetic coordinate conversion module based on Karney (2011) and Bowring (1985).

**Coordinate Types (NamedTuples):**

- `LatLonCoordinate` - Geographic coordinates (lat, lon, optional height)
- `UTMCoordinate` - Universal Transverse Mercator (easting, northing, zone, hemisphere)
- `MGRSCoordinate` - Military Grid Reference System (zone, band, square, easting, northing)
- `ECEFCoordinate` - Earth-Centered, Earth-Fixed Cartesian (x, y, z)

**Conversion Functions:**

- `latlon_to_utm()` / `utm_to_latlon()` - High-precision WGS84 ↔ UTM using Karney's Krüger series
- `latlon_to_mgrs()` / `mgrs_to_latlon()` - Geographic ↔ MGRS with alphanumeric grid references
- `latlon_to_ecef()` / `ecef_to_latlon()` - Geographic ↔ ECEF using Bowring's iterative method

**Formatting Functions:**

- `format_latlon()`, `format_utm()`, `format_mgrs()`, `format_ecef()` - Human-readable string formatting

**Helper Functions:**

- `wrap_lat()`, `wrap_lon()` - Normalize angles to valid ranges

**Important Implementation Details:**

- Uses Karney (2011) 6th-order Krüger series for sub-millimeter accuracy in UTM conversions
- Handles Norway and Svalbard UTM zone exceptions (zones 31V, 32V, 31X, 33X, 35X, 37X)
- MGRS latitude bands span 8° (C-W) with band X spanning 12° (72°N to 84°N)
- ECEF uses Bowring's method for efficient lat/lon recovery (converges in 2-3 iterations)
- All functions default to WGS84 ellipsoid but support custom ellipsoids via parameter

**Ellipsoid Class:**

- `Ellipsoid` dataclass with `semi_major_axis` and `flattening` parameters
- `WGS_84_ELLIPSOID` constant provided for GPS/mapping applications

**Constants:**

- `UTM_SCALE_FACTOR` (0.9996), `UTM_FALSE_EASTING` (500,000m), `UTM_FALSE_NORTHING` (10,000,000m)
- MGRS grid letter sets for 100km square identifiers

#### 8. Constants and Defaults (`papermap.py`)

Configuration constants:

- **Paper Sizes:** A-series (A0-A7), letter, legal in `PAPER_SIZE_TO_DIMENSIONS_MAP`
- **Default Values:**
  - Scale: 25000 (`DEFAULT_SCALE`)
  - DPI: 300 (`DEFAULT_DPI`)
  - Margins: 10mm (`DEFAULT_MARGIN`)
  - Grid size: 1000m (`DEFAULT_GRID_SIZE`)
  - Background color: #fff (`DEFAULT_BACKGROUND_COLOR`)

## Testing

### Test Structure

Tests are located in the `tests/` directory and use pytest:

- `conftest.py` - Shared fixtures (sample tiles, tile providers, coordinates)
- `smoke_test.py` - Basic smoke tests for package installation
- `test_utils.py` - Comprehensive unit tests for utility functions
- `test_tile.py` - Tile dataclass tests
- `test_tile_provider.py` - TileProvider tests
- `test_papermap.py` - PaperMap class tests
- `test_cli.py` - CLI tests
- `test_geodesy.py` - Geodesy module tests (coordinate conversions)
- `test_integration.py` - Integration tests

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_utils.py

# Run specific test class or function
uv run pytest tests/test_utils.py::TestClip
uv run pytest tests/test_utils.py::TestClip::test_clip_value_within_range
```

### Test Fixtures

The `conftest.py` provides common fixtures:

- `sample_tile` - A basic Tile for testing
- `sample_tile_with_image` - A Tile with an attached image
- `sample_tile_provider` - A basic TileProvider
- `sample_tile_provider_with_subdomains` - TileProvider with subdomain support
- `sample_tile_provider_with_api_key` - TileProvider requiring API key
- `mock_tile_image` - A mock PIL Image
- HTTP mocking via `pytest-httpx` (use `httpx_mock` fixture)
- `coordinate_test_cases` - Well-known coordinate test cases (NYC, London, Tokyo, etc.)

### Writing Tests

Follow these conventions:

1. Group related tests in classes (e.g., `class TestClip:`)
1. Use descriptive test names (e.g., `test_clip_value_within_range`)
1. Use pytest fixtures for common setup
1. Use `@pytest.mark.parametrize` for testing multiple inputs
1. Use `math.isclose()` for floating-point comparisons
1. Test edge cases and boundary conditions
1. For HTTP mocking, use `pytest-httpx`:
   ```python
   def test_tile_download(httpx_mock):
       httpx_mock.add_response(content=b"fake_image_data")
       # test code that makes HTTP requests
   ```

## Code Style Conventions

### Python Style

1. **Formatting:** Ruff (via ruff-format, replacing Black)
1. **Line Length:** E501 ignored (Ruff format determines line breaks)
1. **Type Hints:** Fully typed (py.typed marker present)
1. **Imports:** Sorted by Ruff (isort rules)
1. **Docstrings:** Google-style docstrings with Args, Returns, Raises sections

### Example Docstring Format

```python
def function_name(arg1: Type1, arg2: Type2) -> ReturnType:
    """Brief description of function.

    More detailed description if needed.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When and why this is raised.
    """
```

### Naming Conventions

- **Classes:** PascalCase (e.g., `PaperMap`, `TileProvider`)
- **Functions/Methods:** snake_case (e.g., `render_grid`, `download_tiles`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `DEFAULT_SCALE`, `TILE_SIZE`)
- **Private:** Prefix with `_` (not commonly used in this codebase)
- **Greek Letters:** Used in mathematical code (e.g., `φ` for phi/latitude, `λ` for lambda/longitude, `π` for pi)

### Import Order (enforced by Ruff)

1. Standard library imports
1. Third-party imports (click, fpdf, PIL, requests)
1. Local imports (relative imports from current package)

## Documentation

### Documentation System

- **Tool:** Sphinx with MyST parser (Markdown support)
- **Theme:** Furo
- **Hosting:** ReadTheDocs (https://papermap.readthedocs.io/)
- **Configuration:** `.readthedocs.yaml` and `docs/conf.py`

### Documentation Structure

- `index.md` - Landing page
- `installation.md` - Installation instructions
- `usage.md` - User guide with examples
- `cli.md` - CLI reference (auto-generated via cog)
- `api.md` - API reference
- `changelog.md` - Includes CHANGELOG.md

### CLI Documentation Auto-generation

The CLI reference in `docs/cli.md` uses cog for auto-generation. When CLI commands change, the documentation is automatically updated by running:

```bash
uv run cog -r docs/cli.md
```

This is also checked in pre-commit hooks.

### Adding New Modules to API Reference

When adding a new module, add it to `docs/api.md`:

```markdown
## `papermap.new_module` Module

\`\`\`{eval-rst}
.. automodule:: papermap.new_module
   :members:
\`\`\`
```

### Extensions

- `sphinx-copybutton` - Copy button for code blocks
- `sphinxext-opengraph` - Open Graph metadata for social sharing
- `myst-parser` - Markdown support

## Changelog

### Format

The project uses the [Keep a Changelog](https://keepachangelog.com/) format in `CHANGELOG.md`. Categories include:

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes

### Example Entry

```markdown
## [Unreleased]

### Added

- New tile provider support for XYZ Maps

### Fixed

- Fixed coordinate conversion issue at the date line
```

## Release and Publishing

### Version Management

- Version defined in `pyproject.toml` as `version = "YYYY.N.N"`
- Uses CalVer (Calendar Versioning): YYYY.MINOR.PATCH
- Example: `2026.1.0` = Year 2026, first minor release, no patches

### Publishing Workflow (GitHub Actions)

**Trigger:** On tag push matching `[0-9][0-9][0-9][0-9].[0-9]+.[0-9]+*`

**Steps:**

1. Checkout repository
1. Install uv and Python 3.13
1. Build with `uv build`
1. Smoke test wheel installation
1. Smoke test source distribution
1. Publish to PyPI with `uv publish` (uses trusted publishing)

### Release Checklist

1. Update version in `pyproject.toml`
1. Add entry to `CHANGELOG.md`
1. Commit changes with message format: `:emoji: Description`
1. Create and push tag: `git tag YYYY.N.N && git push origin YYYY.N.N`
1. GitHub Actions automatically publishes to PyPI

### Commit Message Conventions

The project uses **Gitmoji** for commit messages:

- `:sparkles:` - New features
- `:bug:` - Bug fixes
- `:recycle:` - Refactoring
- `:art:` - Code formatting/style
- `:memo:` or `:pencil2:` - Documentation updates
- `:arrow_up:` - Dependency upgrades
- `:pushpin:` - Pin/version management
- `:white_check_mark:` - Tests
- `:construction_worker:` - CI/CD changes

Example: `:sparkles: Add support for custom tile providers`

## Key Conventions for AI Assistants

### When Making Changes

1. **Always run tests:**

   ```bash
   uv run pytest
   ```

1. **Always run pre-commit hooks:**

   ```bash
   uv run prek run --all-files
   ```

1. **Type hints are mandatory:** All functions must have type annotations

1. **Preserve mathematical accuracy:** The coordinate conversion code is based on academic papers (Karney 2011). Don't modify algorithms without understanding the mathematics.

1. **Maintain backwards compatibility:** This is a published library. API changes affect users.

1. **Update documentation:** Changes to public API require documentation updates in `docs/`

1. **Update changelog:** All changes require an entry in `CHANGELOG.md`

1. **Add tests:** All new functionality requires corresponding tests

### Common Tasks

#### Adding a New Tile Provider

1. Identify the appropriate provider module in `src/papermap/tile_providers/` (or create a new one if needed)
1. Create a new `TileProvider` instance with:
   - `key`: lowercase with dashes (e.g., "openstreetmap-de")
   - `name`: display name (e.g., "OpenStreetMap DE")
   - `attribution`: plain text attribution
   - `html_attribution`: HTML attribution with hyperlinks
   - `url_template`: URL with placeholders `{x}`, `{y}`, `{z}`, `{s}` (subdomain), `{a}` (API key)
   - `zoom_min` and `zoom_max`: supported zoom levels
   - `bounds`: optional geographic bounds tuple
   - `subdomains`: optional list for load balancing
1. Add the provider to the module's `__all__` list
1. The provider will auto-populate in `KEY_TO_TILE_PROVIDER` via the `__init__.py`
1. Add tests for the new tile provider
1. Test with and without API key (if applicable)
1. Add changelog entry

#### Modifying Coordinate Conversions

1. Reference the Karney (2011) paper or other source
1. Add citation in docstring
1. Test with known coordinate pairs
1. Verify edge cases (poles, dateline, UTM zone boundaries)
1. Update existing tests if behavior changes

#### Adding CLI Options

1. Add to `common_parameters` decorator in `cli.py`
1. Add corresponding parameter to `PaperMap.__init__()`
1. Run `uv run cog -r docs/cli.md` to update CLI documentation
1. Add tests for the new option
1. Test with various combinations
1. Add changelog entry

#### Adding a New Module

1. Create the module in `src/papermap/`
1. Add to `__init__.py` if it should be publicly exported
1. Add to `docs/api.md` for API documentation
1. Add corresponding test file in `tests/`
1. Add changelog entry

#### Updating Dependencies

1. Modify `dependencies` in `pyproject.toml`
1. Run `uv sync` to update `uv.lock`
1. Test locally with `uv run pytest`
1. Update documentation if user-facing

#### Working with Geodesy Module

When working with coordinate conversions:

1. **Preserve mathematical accuracy:** The geodesy module implements Karney (2011) and Bowring (1985) algorithms with sub-millimeter precision
1. **Test with known coordinates:** Use test cases from `tests/test_geodesy.py` or `conftest.py` fixtures
1. **Handle edge cases:** Test Norway/Svalbard UTM zone exceptions, poles, dateline, equator
1. **Greek letters allowed:** Ruff per-file ignores permit Greek letters (φ, λ, τ) for mathematical clarity
1. **Document formulas:** Include equation references to source papers (Karney, Bowring) in docstrings
1. **Validate conversions:** Round-trip conversions should return original values within tolerance (typically 1e-12)

### Code Patterns to Follow

#### Concurrent Tile Downloads (using httpx)

```python
with ThreadPoolExecutor(min(32, os.cpu_count() or 1 + 4)) as executor:
    with httpx.Client() as client:
        responses = executor.map(client.get, urls)
```

#### Retry Logic

```python
for num_retry in count():
    # ... attempt operation ...
    if success:
        break
    if num_retry >= num_retries:
        raise RuntimeError(...)
    if sleep_between_retries:
        time.sleep(sleep_between_retries)
```

#### PDF Drawing with FPDF

```python
self.pdf.set_xy(x, y)
self.pdf.cell(w=width, text=text, align="C", fill=True)
```

### Important Implementation Details

1. **Tile Coordinate System:**

   - Origin (0,0) at top-left
   - X increases eastward, Y increases southward
   - Tiles are 256×256 pixels (TILE_SIZE constant)
   - Web Mercator projection (EPSG:3857)

1. **Zoom Level Calculations:**

   - Fractional zoom computed from scale, latitude, DPI
   - Floored to integer for tile downloads
   - Resize factor applied to achieve exact scale

1. **Grid Overlay:**

   - Uses UTM projection (EPSG:326XX for north, EPSG:327XX for south)
   - Grid size in meters, converted to mm based on scale
   - Labels show UTM coordinates in kilometers

1. **PDF Generation:**

   - FPDF2 library (Python port of PHP FPDF)
   - Units in millimeters
   - Images resized to exact scale before embedding
   - Coordinate system: origin at top-left of page

### Known Limitations

1. **Tile Download Failures:** By default, failed tiles are rendered as background color with a warning. Use `strict_download=True` to fail on any tile download error.
1. **Memory Usage:** Large maps load all tiles into memory
1. **Single-page PDFs:** No multi-page map support
1. **Fixed Font:** Uses Helvetica (built-in PDF font)

### Dependencies to Be Aware Of

- **click:** CLI framework (decorators, commands, options)
- **click_default_group:** Allows default command (`latlon`)
- **fpdf2:** PDF generation (successor to PyFPDF)
- **Pillow:** Image manipulation (downloading, resizing, compositing)
- **httpx:** Modern HTTP client for tile downloads (replaced `requests`)

### When to Consult Documentation

- **Tile Providers:** Check OSM wiki for URL template format
- **Geodesy/UTM Conversions:**
  - Karney (2011) "Transverse Mercator with an accuracy of a few nanometers" for UTM algorithm details
  - Bowring (1985) for ECEF ↔ lat/lon conversions
  - See extensive inline documentation in `geodesy.py` for implementation details
- **FPDF:** Official FPDF2 docs for PDF drawing operations
- **Click:** Click documentation for CLI patterns
- **httpx:** httpx documentation for HTTP client features and migration from requests

### Debugging Tips

1. **Tile Download Issues:**

   - Check tile provider URL template formatting
   - Verify API key if required
   - Check zoom level is within provider's zoom_min/zoom_max

1. **Coordinate Conversion Issues:**

   - Verify lat/lon are in valid ranges (-90 to 90, -180 to 180)
   - Check UTM zone calculation for edge cases (Norway/Svalbard exceptions)
   - Verify hemisphere detection
   - For geodesy module: test round-trip conversions (lat/lon → UTM → lat/lon should match)
   - MGRS coordinates must have equal-length easting/northing digits (1-5 digits each)
   - UTM only valid from 80°S to 84°N (use UPS for polar regions)

1. **PDF Layout Issues:**

   - Margins are in mm, convert to PDF units
   - Check coordinate calculations (mm vs px vs pt)
   - Verify image dimensions match paper size

1. **Scale Issues:**

   - Scale depends on latitude (Mercator distortion)
   - Zoom calculation is non-linear
   - Resize factor compensates for discrete zoom levels

### Pre-commit Hook Failures

Common issues and fixes:

1. **Ruff errors:** Run `uv run ruff check --fix .` to auto-fix
1. **Ruff formatting:** Run `uv run ruff format .` to reformat
1. **mypy/pyrefly/ty errors:** Add type hints or fix type issues
1. **Trailing whitespace:** Editor issue, configure to trim on save
1. **Codespell:** Real typos, fix them; false positives, add to ignore
1. **Cog errors:** Run `uv run cog -r docs/cli.md` to regenerate

### Performance Considerations

1. **Tile Downloads:** Parallelized with ThreadPoolExecutor, uses connection pooling
1. **Image Processing:** Pillow operations are CPU-bound, consider memory for large maps
1. **PDF Generation:** FPDF is relatively fast, bottleneck is image embedding
1. **Coordinate Conversions:** Pure Python math, negligible performance impact

______________________________________________________________________

## Quick Reference

**Install for development:**

```bash
uv sync --dev
uv run prek install
```

**Run tests:**

```bash
uv run pytest
```

**Run code quality checks:**

```bash
uv run prek run --all-files
```

**Build documentation locally:**

```bash
cd docs
uv run sphinx-build -b html . _build/html
```

**Test CLI locally:**

```bash
uv run papermap latlon 40.7128 -74.0060 test.pdf
```

**Publish new version:**

1. Update version in `pyproject.toml`
1. Update `CHANGELOG.md`
1. Commit and push
1. Create and push tag: `git tag YYYY.N.N && git push origin YYYY.N.N`
1. GitHub Actions publishes to PyPI automatically

______________________________________________________________________

_This document is intended for AI assistants (like Claude) to understand the PaperMap codebase structure, development workflows, and conventions. Keep it updated as the project evolves._
