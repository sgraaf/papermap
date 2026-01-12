<!-- start docs-include-index -->

# PaperMap

[![PyPI](https://img.shields.io/pypi/v/papermap)](https://img.shields.io/pypi/v/papermap)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/papermap)](https://pypi.org/project/papermap/)
[![CI](https://github.com/sgraaf/papermap/actions/workflows/ci.yml/badge.svg)](https://github.com/sgraaf/papermap/actions/workflows/ci.yml)
[![Test](https://github.com/sgraaf/papermap/actions/workflows/test.yml/badge.svg)](https://github.com/sgraaf/papermap/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/papermap/badge/?version=latest)](https://papermap.readthedocs.io/en/latest/?badge=latest)
[![PyPI - License](https://img.shields.io/pypi/l/papermap)](https://img.shields.io/pypi/l/papermap)

PaperMap is a Python library and CLI tool for creating ready-to-print paper maps.

<!-- end docs-include-index -->

## Installation

<!-- start docs-include-installation -->

PaperMap is available on [PyPI](https://pypi.org/project/papermap/). Install with [uv](https://docs.astral.sh/uv/) or your package manager of choice:

```sh
uv add papermap
```

<!-- end docs-include-installation -->

## Documentation

Check out the [PaperMap documentation](https://papermap.readthedocs.io/en/stable/) for the [User's Guide](https://papermap.readthedocs.io/en/stable/usage.html), [API Reference](https://papermap.readthedocs.io/en/stable/api.html) and [CLI Reference](https://papermap.readthedocs.io/en/stable/cli.html).

## Usage

<!-- start docs-include-usage -->

PaperMap can be used both in your own applications as a package, as well as a CLI tool.

### As a Library

#### Basic Usage

Create a simple portrait-oriented, A4-sized map at scale 1:25000:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(13.75889, 100.49722)  # Bangkok, Thailand
>>> pm.render()
>>> pm.save("Bangkok.pdf")
```

#### Custom Size and Orientation

Create a landscape-oriented, A3-sized map with grid overlay:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(
...     lat=40.416775,
...     lon=-3.703790,  # Madrid, Spain
...     tile_server="Stamen Terrain",
...     size="a3",
...     landscape=True,
...     scale=50_000,
...     add_grid=True,
... )
>>> pm.render()
>>> pm.save("Madrid.pdf")
```

#### Satellite Imagery

Create a map using satellite imagery:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(
...     lat=51.5074,
...     lon=-0.1278,  # London, UK
...     tile_server="ESRI Satellite",
...     size="a4",
...     scale=10_000,
... )
>>> pm.render()
>>> pm.save("London_Satellite.pdf")
```

#### Topographic Maps

Create a topographic map for hiking:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(
...     lat=46.5197,
...     lon=7.9577,  # Mürren, Switzerland
...     tile_server="OpenTopoMap",
...     size="a3",
...     landscape=True,
...     scale=25_000,
...     add_grid=True,
...     grid_size=500,  # 500m grid for easier navigation
... )
>>> pm.render()
>>> pm.save("Murren_Topo.pdf")
```

#### High-Resolution Printing

Create a high-resolution map for professional printing:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(
...     lat=35.6762,
...     lon=139.6503,  # Tokyo, Japan
...     tile_server="OpenStreetMap",
...     size="a0",  # Large format
...     landscape=True,
...     scale=15_000,
...     dpi=600,  # High resolution
...     add_grid=True,
... )
>>> pm.render()
>>> pm.save("Tokyo_HighRes.pdf")
```

#### Using UTM Coordinates

Create a map using UTM coordinates instead of latitude/longitude:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap.from_utm(
...     easting=500000,
...     northing=4649776,
...     zone=30,
...     hemisphere="N",  # Northern hemisphere
...     tile_server="OpenStreetMap",
...     size="a4",
...     scale=25_000,
...     add_grid=True,
... )
>>> pm.render()
>>> pm.save("UTM_Map.pdf")
```

#### Custom Margins

Create a map with custom margins for binding:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(
...     lat=-33.8688,
...     lon=151.2093,  # Sydney, Australia
...     tile_server="OpenStreetMap",
...     size="letter",
...     margin_left=20,  # Extra margin for binding
...     margin_top=10,
...     margin_right=10,
...     margin_bottom=10,
...     scale=20_000,
... )
>>> pm.render()
>>> pm.save("Sydney_Binding.pdf")
```

#### Monochrome Maps

Create a black-and-white map for printing:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(
...     lat=48.8566,
...     lon=2.3522,  # Paris, France
...     tile_server="OpenStreetMap Monochrome",
...     size="a4",
...     landscape=True,
...     scale=15_000,
...     add_grid=True,
... )
>>> pm.render()
>>> pm.save("Paris_BW.pdf")
```

#### Using API Keys

Some tile servers require API keys. Here's how to use them:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(
...     lat=37.7749,
...     lon=-122.4194,  # San Francisco, USA
...     tile_server="Thunderforest Outdoors",
...     api_key="your_api_key_here",  # Get from thunderforest.com
...     size="a4",
...     landscape=True,
...     scale=25_000,
...     add_grid=True,
... )
>>> pm.render()
>>> pm.save("SF_Outdoors.pdf")
```

For more options and details, see the [API Reference](https://papermap.readthedocs.io/en/stable/api.html#papermap.papermap.PaperMap).

### As a CLI Tool

#### Basic Usage

Create a simple portrait-oriented, A4-sized map:

```shell
$ papermap latlon -- 13.75889 100.49722 Bangkok.pdf
```

#### Custom Size and Orientation

Create a landscape-oriented, A3-sized map with grid overlay:

```shell
$ papermap latlon \
    --tile-server "Stamen Terrain" \
    --size a3 \
    --landscape \
    --scale 50000 \
    --grid \
    -- 40.416775 -3.703790 Madrid.pdf
```

#### Satellite Imagery

Create a map using satellite imagery:

```shell
$ papermap latlon \
    --tile-server "ESRI Satellite" \
    --scale 10000 \
    -- 51.5074 -0.1278 London_Satellite.pdf
```

#### Topographic Maps

Create a topographic map for hiking:

```shell
$ papermap latlon \
    --tile-server OpenTopoMap \
    --size a3 \
    --landscape \
    --scale 25000 \
    --grid \
    --grid-size 500 \
    -- 46.5197 7.9577 Murren_Topo.pdf
```

#### High-Resolution Printing

Create a high-resolution map for professional printing:

```shell
$ papermap latlon \
    --tile-server OpenStreetMap \
    --size a0 \
    --landscape \
    --scale 15000 \
    --dpi 600 \
    --grid \
    -- 35.6762 139.6503 Tokyo_HighRes.pdf
```

#### Using UTM Coordinates

Create a map using UTM coordinates:

```shell
$ papermap utm \
    --tile-server OpenStreetMap \
    --size a4 \
    --scale 25000 \
    --grid \
    -- 500000 4649776 30 N UTM_Map.pdf
```

#### Custom Margins

Create a map with custom margins for binding:

```shell
$ papermap latlon \
    --tile-server OpenStreetMap \
    --size letter \
    --margin-left 20 \
    --margin-top 10 \
    --margin-right 10 \
    --margin-bottom 10 \
    --scale 20000 \
    -- -33.8688 151.2093 Sydney_Binding.pdf
```

#### Monochrome Maps

Create a black-and-white map:

```shell
$ papermap latlon \
    --tile-server "OpenStreetMap Monochrome" \
    --size a4 \
    --landscape \
    --scale 15000 \
    --grid \
    -- 48.8566 2.3522 Paris_BW.pdf
```

#### Using API Keys

Use tile servers that require API keys:

```shell
$ papermap latlon \
    --tile-server "Thunderforest Outdoors" \
    --api-key "your_api_key_here" \
    --size a4 \
    --landscape \
    --scale 25000 \
    --grid \
    -- 37.7749 -122.4194 SF_Outdoors.pdf
```

For more options and details, see the [CLI Reference](https://papermap.readthedocs.io/en/stable/cli.html).

<!-- end docs-include-usage -->
