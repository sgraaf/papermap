# PaperMap

A python package and CLI for creating paper maps.

## Example
Below, you'll find two examples on how to use PaperMap. Both of these examples accomplish the exact same thing: creating an A4 map of Bangkok at scale 1:25000.

### Package
```python
from papermap import PaperMap
pm = PaperMap(13.75889, 100.49722)
pm.render()
pm.save('Bangkok.pdf')
```

### CLI
```bash
papermap wgs84 13.75889 100.49722 Bangkok.pdf
```

## Installation
### Using pip
```bash
pip install --upgrade papermap
```

### From source
```bash
git clone https://github.com/sgraaf/papermap.git
cd papermap
python setup.py install
```

## Usage

### Package
#### Create a new PaperMap instance
```python
pm = PaperMap(lat, lon, tile_server, scale, size, dpi, margin_top, margin_bottom, margin_left, margin_right, grid, nb_workers, nb_retries, landscape, quiet, gpx)
```

#### Arguments
    lat (float):            latitude (in DD)
    lon (float):            longitude (in DD)
    tile_server (str):      tile server to serve as the base of the paper map. Default: OpenStreetMap
    api_key (str):          API key for the chosen tile server (if applicable). Default: None
    scale (int):            scale of the paper map (in cm). Default: 25000
    size (str):             size of the paper map. Default: A4
    margin_top (int):       top margin (in mm), Default: 12
    margin_bottom (int):    bottom margin (in mm), Default: 12
    margin_left (int):      left margin (in mm), Default: 12
    margin_right (int):     right margin (in mm), Default: 12
    dpi (int):              dots per inch. Default: 300
    grid (str):             coordinate grid to display on the paper map. Default: None
    nb_workers (int):       number of workers (for parallelization). Default: 4
    nb_retries (int):       number of retries (for failed tiles). Default: 3
    landscape (bool):       use landscape orientation. Default: False
    quiet (bool):           activate quiet mode. Default: False
    gpx (GPX):              GPX object. Default: None
    
### CLI
```bash
papermap [GLOBAL OPTIONS] {wgs84,utm,rd,gpx} [ARGS] PATH
```

#### Global Options
    -t, --tile_server {OpenStreetMap,
    OpenStreetMap Monochrome,
    OpenTopoMap,
    Thunderforest Landscape,
    Thunderforest Outdoors,
    Thunderforest Transport,
    ESRI Standard,
    ESRI Satellite,
    ESRI Topo,
    ESRI Dark Gray,
    ESRI Light Gray,
    ESRI Transportation,
    Google Maps,
    Google Maps Sattelite,
    Google Maps Sattelite Hybrid,
    Google Maps Terrain,
    Google Maps Terrain Hybrid,
    Stamen Terrain,
    Stamen Toner,
    Stamen Toner Lite,
    Komoot,
    Wikimedia,
    Hike & Bike}                        Tile server to serve as the base of the paper map
    -a, --api_key                       API key for the chosen tile server (if applicable)
    -sz, --size {A0,A1,A2,A3,
    A4,A5,A6,A7,Letter,Legal}           Size of the paper map
    -sc, --scale CENTIMETERS            Scale of the paper map
    -mt, --margin_top MILLIMETERS       Top margin
    -mb, --margin_bottom MILLIMETERS    Bottom margin
    -ml, --margin_left MILLIMETERS      Left margin
    -mr, --margin_right MILLIMETERS     Right margin
    -d, --dpi NUMBER                    Dots per inch
    -g, --grid {utm, rd}                Coordinate grid to display on the paper map
    -w, --nb_workers NUMBER             Number of workers (for parallelization)
    -r, --nb_retries NUMBER             Number of retries (for failed tiles)
    -o, --open                          Open paper map after generating
    -l, --landscape                     Use landscape orientation
    -q, --quiet                         Activate quiet mode
    -v, --version                       Display the current version of PaperMap

For a visual reference of the different tile servers at your disposal, please refer to [`example.pdf`](https://github.com/sgraaf/papermap/blob/master/example.pdf).

### Attribution and alternatives
PaperMap (and its functionality) draws inspiration from various sources. You can find some of these listed below:
* [StaticMap](https://github.com/komoot/staticmap), a small, python-based library for creating map images with lines and markers
* [ScoutingTools.nl](https://scoutingtools.nl/), a Dutch website dedicated to useful tools for scouts (e.g. generating maps)
* [rijksdriehoek](https://github.com/djvanderlaan/rijksdriehoek), a collection of functions to convert WGS84 coordinates into RD coordinates in various programming languages
* [Movable Type](https://www.movable-type.co.uk/scripts/latlong.html), a collection of calculations and code relevant to WGS84 coordinates


### License
PaperMap is open-source and licensed under GNU GPL, Version 3.
