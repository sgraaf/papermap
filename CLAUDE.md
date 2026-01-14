# CLAUDE.md - AI Assistant Guide for PaperMap

## Project Overview

**PaperMap** is a Python package and CLI tool for creating ready-to-print paper maps from various tile providers (OpenStreetMap, Google Maps, ESRI, etc.). The project generates PDF maps at customizable scales, sizes (A0-A7, letter, legal), and orientations with optional UTM grid overlays.

- **Current Version:** 2026.1.0 (CalVer: YYYY.N.N)
- **License:** GNU General Public License v3+
- **Python Support:** 3.10, 3.11, 3.12, 3.13, 3.14
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
- `render()` - Main rendering pipeline (base layer → grid → attribution)
- `render_base_layer()` - Downloads tiles and assembles map image
- `download_tiles()` - Parallel tile downloading with retries
- `render_grid()` - Adds UTM coordinate grid overlay
- `render_attribution_and_scale()` - Adds attribution and scale text
- `compute_grid_coordinates()` - Calculates UTM grid lines
- `save()` - Exports to PDF file

**Key Attributes:**

- Coordinate system conversions (lat/lon to tile coordinates)
- Zoom level calculations based on scale and DPI
- Tile boundary calculations
- PDF document (FPDF instance)

#### 2. TileProvider Class (`tile_provider.py`)

Dataclass representing a tile provider configuration.

**Fields:**

- `attribution: str` - Attribution text
- `url_template: str` - URL with placeholders: \{x}, \{y}, \{zoom}, \{mirror}, \{api_key}
- `zoom_min: int` - Minimum zoom level
- `zoom_max: int` - Maximum zoom level
- `mirrors: Optional[List]` - Load balancing mirrors
- `mirrors_cycle: cycle` - Iterator for round-robin mirror selection

**Method:**

- `format_url_template()` - Formats URL with tile coordinates and API key

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

#### 6. Defaults (`defaults.py`)

Configuration for:

- **20+ Tile Providers:** OpenStreetMap, Google Maps, ESRI, Thunderforest, Stamen, etc.
- **Paper Sizes:** A-series (A0-A7), letter, legal
- **Default Values:** Scale (25000), DPI (300), margins (10mm), grid size (1000m)

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
- `sample_tile_provider_with_mirrors` - TileProvider with mirror support
- `sample_tile_provider_with_api_key` - TileProvider requiring API key
- `mock_tile_image` - A mock PIL Image
- `mock_response` - A mock HTTP response for tile downloads
- `coordinate_test_cases` - Well-known coordinate test cases (NYC, London, Tokyo, etc.)

### Writing Tests

Follow these conventions:

1. Group related tests in classes (e.g., `class TestClip:`)
1. Use descriptive test names (e.g., `test_clip_value_within_range`)
1. Use pytest fixtures for common setup
1. Use `@pytest.mark.parametrize` for testing multiple inputs
1. Use `math.isclose()` for floating-point comparisons
1. Test edge cases and boundary conditions

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

1. Add entry to `TILE_PROVIDERS_MAP` in `defaults.py`
1. Include attribution, URL template, zoom range, mirrors (if applicable)
1. CLI choices will auto-populate
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

### Code Patterns to Follow

#### Concurrent Tile Downloads

```python
with ThreadPoolExecutor(min(32, os.cpu_count() or 1 + 4)) as executor:
    responses = executor.map(session.get, urls)
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

1. **No Error Recovery:** Tile download failures raise exceptions
1. **Memory Usage:** Large maps load all tiles into memory
1. **Single-page PDFs:** No multi-page map support
1. **Fixed Font:** Uses Helvetica (built-in PDF font)

### Dependencies to Be Aware Of

- **click:** CLI framework (decorators, commands, options)
- **click_default_group:** Allows default command (`latlon`)
- **fpdf2:** PDF generation (successor to PyFPDF)
- **Pillow:** Image manipulation (downloading, resizing, compositing)
- **requests:** HTTP client for tile downloads

### When to Consult Documentation

- **Tile Providers:** Check OSM wiki for URL template format
- **UTM Conversions:** Karney (2011) paper for algorithm details
- **FPDF:** Official FPDF2 docs for PDF drawing operations
- **Click:** Click documentation for CLI patterns

### Debugging Tips

1. **Tile Download Issues:**

   - Check tile provider URL template formatting
   - Verify API key if required
   - Check zoom level is within provider's zoom_min/zoom_max

1. **Coordinate Conversion Issues:**

   - Verify lat/lon are in valid ranges (-90 to 90, -180 to 180)
   - Check UTM zone calculation for edge cases
   - Verify hemisphere detection

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
