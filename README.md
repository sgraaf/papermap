<!-- start docs-include-index -->

# PaperMap

[![PyPI](https://img.shields.io/pypi/v/papermap)](https://img.shields.io/pypi/v/papermap)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/papermap)](https://pypi.org/project/papermap/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sgraaf/papermap/main.svg)](https://results.pre-commit.ci/latest/github/sgraaf/papermap/main)
[![Test](https://github.com/sgraaf/papermap/actions/workflows/test.yml/badge.svg)](https://github.com/sgraaf/papermap/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/papermap/badge/?version=latest)](https://papermap.readthedocs.io/en/latest/?badge=latest)
[![PyPI - License](https://img.shields.io/pypi/l/papermap)](https://img.shields.io/pypi/l/papermap)

PaperMap is a Python package and CLI for creating ready-to-print paper maps.

<!-- end docs-include-index -->

## Installation

<!-- start docs-include-installation -->

### From PyPI

PaperMap is available on [PyPI](https://pypi.org/project/papermap/).

#### As a package

For use as a package, install PaperMap with `pip` or your package manager of choice:

```bash
pip install papermap
```

#### As a CLI tool

For use as a CLI tool, we recommend installing PaperMap with [`pipx`](https://pypa.github.io/pipx/):

```bash
pipx install papermap
```

### From source

If you'd like, you can also install PaperMap from source (with [`flit`](https://flit.readthedocs.io/en/latest/)):

```bash
git clone https://github.com/sgraaf/papermap.git
cd papermap
python3 -m pip install flit
flit install
```

<!-- end docs-include-installation -->

## Documentation

Check out the [PaperMap documentation](https://papermap.readthedocs.io/en/stable/) for the [User's Guide](https://papermap.readthedocs.io/en/stable/usage.html) and [API Reference](https://papermap.readthedocs.io/en/stable/api.html).

## Usage

PaperMap can be used both in your own applications as a package, as well as a CLI tool.

#### As a package

Using the default values, the example below will create an portrait-oriented, A4-sized map of Bangkok at scale 1:25000:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(13.75889, 100.49722)
>>> pm.render()
>>> pm.save("Bangkok.pdf")
```

You can easily customize the generated map by changing the tile server, size, orientation, etc. For an exhaustive list of all available options, please see the [API Reference](https://papermap.readthedocs.io/en/stable/api.html#papermap.papermap.PaperMap).

For example, the example below will create a landscape-oriented, A3-sized map of Madrid using the [Stamen Terrain](https://stamen.com/say-hello-to-global-stamen-terrain-maps-c195b3bb71e0/) tile server, with a UTM grid overlay, at scale 1:50000:

```python
>>> from papermap import PaperMap
>>> pm = PaperMap(
...     lat=40.416775,
...     lon=-3.703790,
...     tile_server="Stamen Terrain",
...     size="a3",
...     landscape=True,
...     scale=50_000,
...     add_grid=True,
>>> )
>>> pm.render()
>>> pm.save("Madrid.pdf")
```

#### As a CLI tool

Similarly, using the default values, the example below will create an portrait-oriented, A4-sized map of Bangkok at scale 1:25000:

```shell
$ papermap latlon -- 13.75889 100.49722 Bangkok.pdf
```

As with the package, maps generated through the CLI are also highly customizable. Please see the [CLI Reference](https://papermap.readthedocs.io/en/stable/cli.html) for an exhaustive list of all available options.

The example below will create a landscape-oriented, A3-sized map of Madrid using the [Stamen Terrain](https://stamen.com/say-hello-to-global-stamen-terrain-maps-c195b3bb71e0/) tile server, with a UTM grid overlay, at scale 1:50000:

```shell
$ papermap latlon \
    --tile-server "Stamen Terrain" \
    --size a3 \
    --landscape \
    --scale 50000 \
    --grid \
    -- 40.416775 -3.703790 Madrid.pdf
```
