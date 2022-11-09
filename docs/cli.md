# CLI Reference

<!-- [[[cog
from papermap import cli
from click.testing import CliRunner
import textwrap
def help(args):
    cog.out("\n```shell\n")
    result = CliRunner().invoke(cli.cli, args)
    output = result.output.replace("Usage: cli ", "Usage: papermap ")
    cog.out(output)
    cog.out("```\n\n")
]]] -->
<!-- [[[end]]] -->

The `papermap` CLI tool provides two commands to generate papermaps, which boil down to the two different coordinate systems through which you can define the location that the map should cover.

Running `papermap` without specifying a command runs the default command, `papermap latlon`. See [papermap latlon](#papermap-latlon) for the full list of options for that command.

## papermap --help

<!-- [[[cog
help(["--help"])
]]] -->

```shell
Usage: papermap [OPTIONS] COMMAND [ARGS]...

  PaperMap is a Python package and CLI for creating ready-to-print paper maps.

  Documentation: https://papermap.readthedocs.io/en/stable/

Options:
  -v, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  latlon*  Generates a paper map for the given spherical coordinate (i.e.
  utm      Generates a paper map for the given UTM coordinate and outputs it...
```

<!-- [[[end]]] -->

(cli_help_latlon)=

## papermap latlon

This command generates a paper map for the given spherical coordinate (i.e. lat, lon) and outputs it to file.

<!-- [[[cog
help(["latlon", "--help"])
]]] -->

```shell
Usage: papermap latlon [OPTIONS] LATITUDE LONGITUDE FILE

  Generates a paper map for the given spherical coordinate (i.e. lat, lon) and
  outputs it to file.

Options:
  --tile-server [OpenStreetMap|OpenStreetMap Monochrome|OpenTopoMap|Thunderforest Landscape|Thunderforest Outdoors|Thunderforest Transport|Thunderforest OpenCycleMap|ESRI Standard|ESRI Satellite|ESRI Topo|ESRI Dark Gray|ESRI Light Gray|ESRI Transportation|Geofabrik Topo|Google Maps|Google Maps Satellite|Google Maps Satellite Hybrid|Google Maps Terrain|Google Maps Terrain Hybrid|HERE Terrain|HERE Satellite|HERE Hybrid|Mapy.cz|Stamen Terrain|Stamen Toner|Stamen Toner Lite|Komoot|Wikimedia|Hike & Bike|AllTrails]
                                  Tile server to serve as the base of the paper
                                  map.
  --api-key KEY                   API key for the chosen tile server (if
                                  applicable).
  --size [a0|a1|a2|a3|a4|a5|a6|a7|letter|legal]
                                  Size of the paper map.
  --landscape                     Use landscape orientation.
  --margin-top MILLIMETERS        Top margin.
  --margin-right MILLIMETERS      Right margin.
  --margin-bottom MILLIMETERS     Bottom margin.
  --margin-left MILLIMETERS       Left margin.
  --scale INTEGER                 Scale of the paper map.
  --dpi INTEGER                   Dots per inch.
  --grid                          Add a coordinate grid overlay to the paper
                                  map.
  --grid-size METERS              Size of the grid squares (if applicable).
  -h, --help                      Show this message and exit.
```

<!-- [[[end]]] -->

## papermap utm

This command generates a paper map for the given UTM coordinate (i.e. easting, northing, zone) and outputs it to file.

<!-- [[[cog
help(["utm", "--help"])
]]] -->

```shell
Usage: papermap utm [OPTIONS] EASTING NORTHING ZONE-NUMBER HEMISPHERE FILE

  Generates a paper map for the given UTM coordinate and outputs it to file.

Options:
  --tile-server [OpenStreetMap|OpenStreetMap Monochrome|OpenTopoMap|Thunderforest Landscape|Thunderforest Outdoors|Thunderforest Transport|Thunderforest OpenCycleMap|ESRI Standard|ESRI Satellite|ESRI Topo|ESRI Dark Gray|ESRI Light Gray|ESRI Transportation|Geofabrik Topo|Google Maps|Google Maps Satellite|Google Maps Satellite Hybrid|Google Maps Terrain|Google Maps Terrain Hybrid|HERE Terrain|HERE Satellite|HERE Hybrid|Mapy.cz|Stamen Terrain|Stamen Toner|Stamen Toner Lite|Komoot|Wikimedia|Hike & Bike|AllTrails]
                                  Tile server to serve as the base of the paper
                                  map.
  --api-key KEY                   API key for the chosen tile server (if
                                  applicable).
  --size [a0|a1|a2|a3|a4|a5|a6|a7|letter|legal]
                                  Size of the paper map.
  --landscape                     Use landscape orientation.
  --margin-top MILLIMETERS        Top margin.
  --margin-right MILLIMETERS      Right margin.
  --margin-bottom MILLIMETERS     Bottom margin.
  --margin-left MILLIMETERS       Left margin.
  --scale INTEGER                 Scale of the paper map.
  --dpi INTEGER                   Dots per inch.
  --grid                          Add a coordinate grid overlay to the paper
                                  map.
  --grid-size METERS              Size of the grid squares (if applicable).
  -h, --help                      Show this message and exit.
```

<!-- [[[end]]] -->
