# CLAUDE.md - AI Assistant Guide for PaperMap

## Project Overview

**PaperMap** is a Python package and CLI tool for creating ready-to-print paper maps from various tile servers (OpenStreetMap, Google Maps, ESRI, etc.). The project generates PDF maps at customizable scales, sizes (A0-A7, letter, legal), and orientations with optional UTM grid overlays.

-   **Current Version:** 0.3.0
-   **License:** GNU General Public License v3+
-   **Python Support:** 3.10+
-   **Package Manager:** flit
-   **Documentation:** https://papermap.readthedocs.io/

## Repository Structure

```
papermap/
├── src/papermap/          # Main source code
│   ├── __init__.py        # Package initialization, version
│   ├── __main__.py        # Entry point for CLI
│   ├── cli.py             # Click-based CLI implementation
│   ├── papermap.py        # Core PaperMap class (main logic)
│   ├── tile_server.py     # TileServer dataclass
│   ├── tile.py            # Tile dataclass for map tiles
│   ├── defaults.py        # Default values and tile server configs
│   ├── constants.py       # Mathematical and geographical constants
│   ├── utils.py           # Utility functions (coordinate conversions, etc.)
│   ├── typing.py          # Type aliases
│   └── py.typed           # PEP 561 marker for type information
├── docs/                  # Sphinx documentation
│   ├── conf.py            # Sphinx configuration
│   ├── index.md           # Documentation index
│   ├── api.md             # API reference
│   ├── cli.md             # CLI reference
│   ├── usage.md           # Usage guide
│   └── _static/           # Static assets (example PDFs)
├── .github/workflows/     # GitHub Actions
│   └── publish.yml        # PyPI publishing workflow
├── pyproject.toml         # Project metadata and dependencies
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── .editorconfig          # Editor configuration
├── .gitignore             # Git ignore patterns
└── README.md              # Project README
```

## Development Environment and Tools

### Build System

-   **Build Backend:** flit_core (>=3.2, <4)
-   **Installation:** `pip install flit` or `pipx install flit`
-   **Local Development:** `flit install` (installs in editable mode)

### Code Quality Tools

#### Pre-commit Hooks (runs on every commit)

1. **Basic Checks:** JSON, TOML, XML, YAML validation, EOF fixer, trailing whitespace
2. **pyproject.toml validation:** Validates project configuration
3. **GitHub workflows validation:** Validates .github/workflows/\*.yml
4. **ReadTheDocs validation:** Validates .readthedocs.yaml
5. **Ruff:** Python linter (replaces flake8, isort) with auto-fix
6. **Black:** Code formatter (opinionated, no configuration)
7. **mypy:** Static type checker with types-requests
8. **Codespell:** Spell checker for code and docs
9. **Prettier:** Formatter for YAML, Markdown, JSON

#### Ruff Configuration (pyproject.toml)

```toml
select = ["B", "C90", "E", "F", "I", "UP", "RUF100", "W"]
ignore = ["E501"]  # Line length ignored (Black handles it)
target-version = "py38"
```

-   **B:** flake8-bugbear (likely bugs and design problems)
-   **C90:** mccabe (complexity)
-   **E/W:** pycodestyle errors and warnings
-   **F:** Pyflakes (Python errors)
-   **I:** isort (import sorting)
-   **UP:** pyupgrade (Python version upgrades)
-   **RUF100:** Ruff-specific rules

#### Special Configurations

-   `__init__.py` files ignore F401 (unused imports) - allows re-exports

### Editor Configuration

-   **Indent:** 4 spaces (Python), 2 spaces (YAML), tabs (Makefile)
-   **Line Endings:** LF
-   **Charset:** UTF-8
-   **Final Newline:** Yes
-   **Trailing Whitespace:** Trimmed (except Markdown)

## Code Architecture

### Core Components

#### 1. PaperMap Class (`papermap.py`)

The main class that orchestrates map generation.

**Key Methods:**

-   `__init__()` - Initialize map with coordinates, size, scale, tile server
-   `render()` - Main rendering pipeline (base layer → grid → attribution)
-   `render_base_layer()` - Downloads tiles and assembles map image
-   `download_tiles()` - Parallel tile downloading with retries
-   `render_grid()` - Adds UTM coordinate grid overlay
-   `render_attribution_and_scale()` - Adds attribution and scale text
-   `compute_grid_coordinates()` - Calculates UTM grid lines
-   `save()` - Exports to PDF file

**Key Attributes:**

-   Coordinate system conversions (lat/lon to tile coordinates)
-   Zoom level calculations based on scale and DPI
-   Tile boundary calculations
-   PDF document (FPDF instance)

#### 2. TileServer Class (`tile_server.py`)

Dataclass representing a tile server configuration.

**Fields:**

-   `attribution: str` - Attribution text
-   `url_template: str` - URL with placeholders: {x}, {y}, {zoom}, {mirror}, {api_key}
-   `zoom_min: int` - Minimum zoom level
-   `zoom_max: int` - Maximum zoom level
-   `mirrors: Optional[List]` - Load balancing mirrors
-   `mirrors_cycle: cycle` - Iterator for round-robin mirror selection

**Method:**

-   `format_url_template()` - Formats URL with tile coordinates and API key

#### 3. Tile Class (`tile.py`)

Dataclass for individual map tiles.

#### 4. CLI (`cli.py`)

Click-based command-line interface.

**Commands:**

-   `latlon` - Generate map from latitude/longitude (default)
-   `utm` - Generate map from UTM coordinates

**Common Options:**

-   `--tile-server` - Choose from 20+ tile servers
-   `--size` - Paper size (a0-a7, letter, legal)
-   `--landscape` - Landscape orientation
-   `--scale` - Map scale (default: 25000)
-   `--dpi` - Resolution (default: 300)
-   `--grid` - Add UTM grid overlay
-   `--api-key` - API key for commercial tile servers

#### 5. Utilities (`utils.py`)

Comprehensive utility functions for:

-   **Coordinate Conversions:** lat/lon ↔ tile coordinates, spherical ↔ UTM, spherical ↔ cartesian
-   **Unit Conversions:** mm ↔ px, mm ↔ pt, degrees ↔ DMS
-   **Angle Operations:** wrap(), wrap90(), wrap180(), wrap360()
-   **Scale/Zoom:** scale_to_zoom(), zoom_to_scale()
-   **UTM Functions:** spherical_to_zone(), spherical_to_utm(), utm_to_spherical()

Mathematical implementations follow Karney (2011) paper on Transverse Mercator projection.

#### 6. Defaults (`defaults.py`)

Configuration for:

-   **20+ Tile Servers:** OpenStreetMap, Google Maps, ESRI, Thunderforest, Stamen, etc.
-   **Paper Sizes:** A-series (A0-A7), letter, legal
-   **Default Values:** Scale (25000), DPI (300), margins (10mm), grid size (1000m)

## Development Workflows

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/sgraaf/papermap.git
cd papermap

# Install flit
pip install flit

# Install in development mode with all dependencies
flit install --deps develop --symlink

# Install pre-commit hooks
pre-commit install
```

### Code Style Conventions

#### Python Style

1. **Formatting:** Black (uncompromising, no configuration)
2. **Line Length:** E501 ignored in Ruff (Black determines line breaks)
3. **Type Hints:** Fully typed (py.typed marker present)
4. **Imports:** Sorted by Ruff (isort rules)
5. **Docstrings:** Google-style docstrings with Args, Returns, Raises sections

#### Example Docstring Format:

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

#### Naming Conventions

-   **Classes:** PascalCase (e.g., `PaperMap`, `TileServer`)
-   **Functions/Methods:** snake_case (e.g., `render_grid`, `download_tiles`)
-   **Constants:** UPPER_SNAKE_CASE (e.g., `DEFAULT_SCALE`, `TILE_SIZE`)
-   **Private:** Prefix with `_` (not commonly used in this codebase)
-   **Greek Letters:** Used in mathematical code (e.g., `φ` for phi/latitude, `λ` for lambda/longitude, `π` for pi)

#### Import Order (enforced by Ruff)

1. Standard library imports
2. Third-party imports (click, fpdf, PIL, requests)
3. Local imports (relative imports from current package)

### Testing Strategy

**Current State:** No test suite exists in the repository.

**Observations:**

-   `pyproject.toml` includes a `[project.optional-dependencies]` section for tests with `pytest` and `cog`
-   No `tests/` directory or test files present
-   Pre-commit hooks validate code quality but don't run tests

**Recommendations for Future Development:**

-   Add unit tests for utility functions (coordinate conversions, scale calculations)
-   Add integration tests for tile downloading (with mocked HTTP responses)
-   Add end-to-end tests for PDF generation
-   Set up CI/CD with pytest in GitHub Actions

### Documentation

#### Documentation System

-   **Tool:** Sphinx with MyST parser (Markdown support)
-   **Theme:** Furo
-   **Hosting:** ReadTheDocs (https://papermap.readthedocs.io/)
-   **Configuration:** `.readthedocs.yaml` and `docs/conf.py`

#### Documentation Structure

-   `index.md` - Landing page
-   `installation.md` - Installation instructions
-   `usage.md` - User guide with examples
-   `cli.md` - CLI reference
-   `api.md` - API reference
-   `changelog.md` - Version history

#### Extensions

-   `sphinx-copybutton` - Copy button for code blocks
-   `sphinxext-opengraph` - Open Graph metadata for social sharing
-   `myst-parser` - Markdown support

### Release and Publishing

#### Publishing Workflow (GitHub Actions)

**Trigger:** On GitHub release creation

**Steps:**

1. Checkout repository
2. Set up Python 3.10
3. Install Flit
4. Install production dependencies
5. Publish to PyPI using `PYPI_TOKEN` secret

#### Version Management

-   Version defined in `src/papermap/__init__.py` as `__version__`
-   Flit reads version dynamically from module
-   Follow semantic versioning (MAJOR.MINOR.PATCH)

#### Release Checklist

1. Update `__version__` in `__init__.py`
2. Update `docs/changelog.md`
3. Commit changes with message format: `:emoji: Description`
4. Create GitHub release with tag `vX.Y.Z`
5. GitHub Actions automatically publishes to PyPI

### Commit Message Conventions

The project uses **Gitmoji** for commit messages:

-   `:sparkles:` - New features
-   `:bug:` - Bug fixes
-   `:recycle:` - Refactoring
-   `:art:` - Code formatting/style
-   `:memo:` or `:pencil2:` - Documentation updates
-   `:arrow_up:` - Dependency upgrades
-   `:pushpin:` - Pin/version management
-   `:white_check_mark:` - Tests
-   `:construction_worker:` - CI/CD changes

Example: `:sparkles: Add support for custom tile servers`

## Key Conventions for AI Assistants

### When Making Changes

1. **Always run pre-commit hooks:** Code must pass all checks before committing

    ```bash
    pre-commit run --all-files
    ```

2. **Type hints are mandatory:** All functions must have type annotations

3. **Preserve mathematical accuracy:** The coordinate conversion code is based on academic papers (Karney 2011). Don't modify algorithms without understanding the mathematics.

4. **Maintain backwards compatibility:** This is a published library. API changes affect users.

5. **Update documentation:** Changes to public API require documentation updates in `docs/`

### Common Tasks

#### Adding a New Tile Server

1. Add entry to `TILE_SERVERS_MAP` in `defaults.py`
2. Include attribution, URL template, zoom range, mirrors (if applicable)
3. Update CLI choices will auto-populate
4. Test with and without API key (if applicable)

#### Modifying Coordinate Conversions

1. Reference the Karney (2011) paper or other source
2. Add citation in docstring
3. Test with known coordinate pairs
4. Verify edge cases (poles, dateline, UTM zone boundaries)

#### Adding CLI Options

1. Add to `common_parameters` decorator in `cli.py`
2. Add corresponding parameter to `PaperMap.__init__()`
3. Update `cli.md` documentation
4. Test with various combinations

#### Updating Dependencies

1. Modify `dependencies` in `pyproject.toml`
2. Update `additional_dependencies` in `.pre-commit-config.yaml` if needed
3. Test locally with `flit install`
4. Update documentation if user-facing

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
self.pdf.cell(w=width, txt=text, align="C", fill=True)
```

### Important Implementation Details

1. **Tile Coordinate System:**

    - Origin (0,0) at top-left
    - X increases eastward, Y increases southward
    - Tiles are 256×256 pixels (TILE_SIZE constant)
    - Web Mercator projection (EPSG:3857)

2. **Zoom Level Calculations:**

    - Fractional zoom computed from scale, latitude, DPI
    - Floored to integer for tile downloads
    - Resize factor applied to achieve exact scale

3. **Grid Overlay:**

    - Uses UTM projection (EPSG:326XX for north, EPSG:327XX for south)
    - Grid size in meters, converted to mm based on scale
    - Labels show UTM coordinates in kilometers

4. **PDF Generation:**
    - FPDF2 library (Python port of PHP FPDF)
    - Units in millimeters
    - Images resized to exact scale before embedding
    - Coordinate system: origin at top-left of page

### Known Limitations

1. **No Tests:** Test suite doesn't exist yet
2. **No Error Recovery:** Tile download failures raise exceptions
3. **Memory Usage:** Large maps load all tiles into memory
4. **Single-page PDFs:** No multi-page map support
5. **Fixed Font:** Uses Helvetica (built-in PDF font)

### Dependencies to Be Aware Of

-   **click:** CLI framework (decorators, commands, options)
-   **click_default_group:** Allows default command (`latlon`)
-   **fpdf2:** PDF generation (successor to PyFPDF)
-   **Pillow:** Image manipulation (downloading, resizing, compositing)
-   **requests:** HTTP client for tile downloads

### When to Consult Documentation

-   **Tile Servers:** Check OSM wiki for URL template format
-   **UTM Conversions:** Karney (2011) paper for algorithm details
-   **FPDF:** Official FPDF2 docs for PDF drawing operations
-   **Click:** Click documentation for CLI patterns

### Debugging Tips

1. **Tile Download Issues:**

    - Check tile server URL template formatting
    - Verify API key if required
    - Check zoom level is within server's zoom_min/zoom_max

2. **Coordinate Conversion Issues:**

    - Verify lat/lon are in valid ranges (-90 to 90, -180 to 180)
    - Check UTM zone calculation for edge cases
    - Verify hemisphere detection

3. **PDF Layout Issues:**

    - Margins are in mm, convert to PDF units
    - Check coordinate calculations (mm vs px vs pt)
    - Verify image dimensions match paper size

4. **Scale Issues:**
    - Scale depends on latitude (Mercator distortion)
    - Zoom calculation is non-linear
    - Resize factor compensates for discrete zoom levels

### Pre-commit Hook Failures

Common issues and fixes:

1. **Ruff errors:** Run `ruff check --fix .` to auto-fix
2. **Black formatting:** Run `black .` to reformat
3. **mypy errors:** Add type hints or use `# type: ignore` comments (sparingly)
4. **Trailing whitespace:** Editor issue, configure to trim on save
5. **Codespell:** Real typos, fix them; false positives, add to `.codespellrc`

### Performance Considerations

1. **Tile Downloads:** Parallelized with ThreadPoolExecutor, uses connection pooling
2. **Image Processing:** Pillow operations are CPU-bound, consider memory for large maps
3. **PDF Generation:** FPDF is relatively fast, bottleneck is image embedding
4. **Coordinate Conversions:** Pure Python math, negligible performance impact

---

## Quick Reference

**Install for development:**

```bash
flit install --deps develop --symlink
pre-commit install
```

**Run code quality checks:**

```bash
pre-commit run --all-files
```

**Build documentation locally:**

```bash
cd docs
make html
```

**Test CLI locally:**

```bash
python -m papermap latlon 40.7128 -74.0060 test.pdf
```

**Publish new version:**

1. Update `__version__` in `src/papermap/__init__.py`
2. Update `docs/changelog.md`
3. Commit and push
4. Create GitHub release
5. GitHub Actions publishes to PyPI automatically

---

_This document is intended for AI assistants (like Claude) to understand the PaperMap codebase structure, development workflows, and conventions. Keep it updated as the project evolves._
