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
papermap 13.75889 100.49722 Bangkok.pdf
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
pm = PaperMap(lat, lon, tile_server, scale, size, dpi, margin_top, margin_bottom, margin_left, margin_right, nb_workers, nb_retries, landscape, grid, quiet)
```

#### Arguments
    lat (float):            latitude (in DD)
    lon (float):            longitude (in DD)
    tile_server (str):      tile server to serve as the base of the paper map. Default: OpenStreetMap
    scale (int):            scale of the paper map (in cm). Default: 25000
    size (str):             size of the paper map. Default: A4
    margin_top (int):       top margin (in mm), Default: 12
    margin_bottom (int):    bottom margin (in mm), Default: 12
    margin_left (int):      left margin (in mm), Default: 12
    margin_right (int):     right margin (in mm), Default: 12
    dpi (int):              dots per inch. Default: 300
    nb_workers (int):       number of workers (for parallelization). Default: 4
    nb_retries (int):       number of retries (for failed tiles). Default: 3
    landscape (bool):       use landscape orientation. Default: False
    grid (bool):            use a coordinate grid. Default: False
    quiet (bool):           activate quiet mode. Default: False
    
### CLI
```bash
papermap [OPTIONS] LAT LON PATH
```

#### Options
    -t, --tile_server {OpenStreetMap,
    OpenTopoMap,
    Thunderforest Landscape,
    Thunderforest Outdoors,
    Thunderforest Transport,
    ESRI Aerial,
    ESRI Topo,
    Stamen Terrain,
    Stamen Toner,
    Komoot,
    Wikimedia,
    Hike & Bike}                        Tile server to serve as the base of the paper map
    -sz, --size {A0,A1,A2,A3,
    A4,A5,A6,A7,Letter,Legal}           Size of the paper map
    -sc, --scale CENTIMETERS            Scale of the paper map
    -mt, --margin_top MILLIMETERS       Top margin
    -mb, --margin_bottom MILLIMETERS    Bottom margin
    -ml, --margin_left MILLIMETERS      Left margin
    -mr, --margin_right MILLIMETERS     Right margin
    -d, --dpi NUMBER                    Dots per inch
    -w, --nb_workers NUMBER             Number of workers (for parallelization)
    -r, --nb_retries NUMBER             Number of retries (for failed tiles)
    -o, --open                          Open paper map after generating
    -l, --landscape                     Use landscape orientation
    -g, --grid                          Use a coordinate grid
    -q, --quiet                         Activate quiet mode
    -v, --version                       Display the current version of PaperMap
    
### Licence
PaperMap is open-source and licensed under GNU GPL, Version 3.
