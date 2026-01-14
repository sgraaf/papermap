# CLI Reference

The `papermap` command-line interface (CLI) provides for creating ready-to-print paper maps via the command-line.

<!-- [[[cog
import cog
from click.testing import CliRunner

from papermap.cli import cli

def help_output(args):
    result = CliRunner().invoke(cli, args)
    output = result.output.replace("Usage: cli ", "Usage: papermap ")
    cog.out(f"\nRunning `gpx {' '.join(args)}` or `python -m gpx {' '.join(args)}` shows a list of all of the available options and arguments:\n")
    cog.out(f"\n```sh\n{output}```\n\n")
cog.outl()
]]] -->

<!-- [[[end]]] -->

The `papermap` CLI tool provides two commands to generate papermaps, which boil down to the two different coordinate systems through which you can define the location that the map should cover.

Running `papermap` without specifying a command runs the default command, `papermap latlon`. See [papermap latlon](#papermap-latlon) for the full list of options for that command.

## papermap --help

<!-- [[[cog
help_output(["--help"])
]]] -->

Running `gpx --help` or `python -m gpx --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap [OPTIONS] COMMAND [ARGS]...

  PaperMap is a Python library and CLI tool for creating ready-to-print paper
  maps.

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
help_output(["latlon", "--help"])
]]] -->

Running `gpx latlon --help` or `python -m gpx latlon --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap latlon [OPTIONS] LATITUDE LONGITUDE FILE

  Generates a paper map for the given spherical coordinate (i.e. lat, lon) and
  outputs it to file.

Options:
  --tile-server [alltrails|basemapat|basemapat-grau|basemapat-highdpi|basemapat-orthofoto|basemapat-overlay|basemapat-surface|basemapat-terrain|cartodb-darkmatter|cartodb-darkmatter-nolabels|cartodb-darkmatter-onlylabels|cartodb-positron|cartodb-positronnolabels|cartodb-positrononlylabels|cartodb-voyager|cartodb-voyager-labelsunder|cartodb-voyager-nolabels|cartodb-voyager-onlylabels|cyclosm|esri-delorme|esri-natgeoworldmap|esri-oceanbasemap|esri-worldgraycanvas|esri-worldimagery|esri-worldphysical|esri-worldshadedrelief|esri-worldstreetmap|esri-worldterrain|esri-worldtopomap|geofabrik-topo|google-maps|google-maps-roads|google-maps-satellite|google-maps-satellite-hybrid|google-maps-terrain|google-maps-terrain-hybrid|here-basicmap|here-carnavdaygrey|here-hybridday|here-hybriddaygrey|here-hybriddaymobile|here-hybriddaytransit|here-maplabels|here-normalday|here-normaldaycustom|here-normaldaygrey|here-normaldaygreymobile|here-normaldaymobile|here-normaldaytransit|here-normaldaytransitmobile|here-normalnight|here-normalnightgrey|here-normalnightgreymobile|here-normalnightmobile|here-normalnighttransit|here-normalnighttransitmobile|here-pedestrianday|here-pedestriannight|here-reducedday|here-reducednight|here-satelliteday|here-terrainday|here-terraindaymobile|here-trafficflow|hikebike|jawg-dark|jawg-light|jawg-matrix|jawg-streets|jawg-sunny|jawg-terrain|komoot|maptiler-basic|maptiler-bright|maptiler-hybrid|maptiler-outdoor|maptiler-pastel|maptiler-positron|maptiler-satellite|maptiler-streets|maptiler-toner|maptiler-topo|maptiler-winter|mapy-cz|mtbmap|nasagibs-modisterraaod|nasagibs-modisterrabands367cr|nasagibs-modisterrachlorophyll|nasagibs-modisterralstday|nasagibs-modisterrasnowcover|nasagibs-modisterratruecolorcr|nasagibs-viirsearthatnight2012|nlmaps-grijs|nlmaps-luchtfoto|nlmaps-pastel|nlmaps-standaard|nlmaps-water|openaip|openfiremap|openrailwaymap|openseamap|opensnowmap|openstreetmap|openstreetmap-bzh|openstreetmap-ch|openstreetmap-de|openstreetmap-france|openstreetmap-hot|opentopomap|opnvkarte|safecast|stadia-alidadesmooth|stadia-alidasesatellite|stadia-alidasesmoothdark|stadia-osmbright|stadia-outdoors|stadia-stamenterrain|stadia-stamenterrainbackground|stadia-stamenterrainlabels|stadia-stamenterrainlines|stadia-stamentoner|stadia-stamentonerbackground|stadia-stamentonerlabels|stadia-stamentonerlines|stadia-stamentonerlite|stadia-stamenwatercolor|swissfederalgeoportal-nationalmapcolor|swissfederalgeoportal-nationalmapgrey|swissfederalgeoportal-swissimage|thunderforest-atlas|thunderforest-landscape|thunderforest-mobileatlas|thunderforest-neighbourhood|thunderforest-opencyclemap|thunderforest-outdoors|thunderforest-pioneer|thunderforest-spinalmap|thunderforest-transport|thunderforest-transport-dark|tomtom-basic|tomtom-hybrid|tomtom-labels|usgs-usimagery|usgs-usimagerytopo|usgs-ustopo|waymarkedtrails-cycling|waymarkedtrails-hiking|waymarkedtrails-mtb|waymarkedtrails-riding|waymarkedtrails-skating|waymarkedtrails-slopes|wikimedia]
                                  Tile server to serve as the base of the paper
                                  map.
  --api-key KEY                   API key for the chosen tile server (if
                                  applicable).
  --paper-size [a0|a1|a2|a3|a4|a5|a6|a7|letter|legal]
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
help_output(["utm", "--help"])
]]] -->

Running `gpx utm --help` or `python -m gpx utm --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap utm [OPTIONS] EASTING NORTHING ZONE-NUMBER HEMISPHERE FILE

  Generates a paper map for the given UTM coordinate and outputs it to file.

Options:
  --tile-server [alltrails|basemapat|basemapat-grau|basemapat-highdpi|basemapat-orthofoto|basemapat-overlay|basemapat-surface|basemapat-terrain|cartodb-darkmatter|cartodb-darkmatter-nolabels|cartodb-darkmatter-onlylabels|cartodb-positron|cartodb-positronnolabels|cartodb-positrononlylabels|cartodb-voyager|cartodb-voyager-labelsunder|cartodb-voyager-nolabels|cartodb-voyager-onlylabels|cyclosm|esri-delorme|esri-natgeoworldmap|esri-oceanbasemap|esri-worldgraycanvas|esri-worldimagery|esri-worldphysical|esri-worldshadedrelief|esri-worldstreetmap|esri-worldterrain|esri-worldtopomap|geofabrik-topo|google-maps|google-maps-roads|google-maps-satellite|google-maps-satellite-hybrid|google-maps-terrain|google-maps-terrain-hybrid|here-basicmap|here-carnavdaygrey|here-hybridday|here-hybriddaygrey|here-hybriddaymobile|here-hybriddaytransit|here-maplabels|here-normalday|here-normaldaycustom|here-normaldaygrey|here-normaldaygreymobile|here-normaldaymobile|here-normaldaytransit|here-normaldaytransitmobile|here-normalnight|here-normalnightgrey|here-normalnightgreymobile|here-normalnightmobile|here-normalnighttransit|here-normalnighttransitmobile|here-pedestrianday|here-pedestriannight|here-reducedday|here-reducednight|here-satelliteday|here-terrainday|here-terraindaymobile|here-trafficflow|hikebike|jawg-dark|jawg-light|jawg-matrix|jawg-streets|jawg-sunny|jawg-terrain|komoot|maptiler-basic|maptiler-bright|maptiler-hybrid|maptiler-outdoor|maptiler-pastel|maptiler-positron|maptiler-satellite|maptiler-streets|maptiler-toner|maptiler-topo|maptiler-winter|mapy-cz|mtbmap|nasagibs-modisterraaod|nasagibs-modisterrabands367cr|nasagibs-modisterrachlorophyll|nasagibs-modisterralstday|nasagibs-modisterrasnowcover|nasagibs-modisterratruecolorcr|nasagibs-viirsearthatnight2012|nlmaps-grijs|nlmaps-luchtfoto|nlmaps-pastel|nlmaps-standaard|nlmaps-water|openaip|openfiremap|openrailwaymap|openseamap|opensnowmap|openstreetmap|openstreetmap-bzh|openstreetmap-ch|openstreetmap-de|openstreetmap-france|openstreetmap-hot|opentopomap|opnvkarte|safecast|stadia-alidadesmooth|stadia-alidasesatellite|stadia-alidasesmoothdark|stadia-osmbright|stadia-outdoors|stadia-stamenterrain|stadia-stamenterrainbackground|stadia-stamenterrainlabels|stadia-stamenterrainlines|stadia-stamentoner|stadia-stamentonerbackground|stadia-stamentonerlabels|stadia-stamentonerlines|stadia-stamentonerlite|stadia-stamenwatercolor|swissfederalgeoportal-nationalmapcolor|swissfederalgeoportal-nationalmapgrey|swissfederalgeoportal-swissimage|thunderforest-atlas|thunderforest-landscape|thunderforest-mobileatlas|thunderforest-neighbourhood|thunderforest-opencyclemap|thunderforest-outdoors|thunderforest-pioneer|thunderforest-spinalmap|thunderforest-transport|thunderforest-transport-dark|tomtom-basic|tomtom-hybrid|tomtom-labels|usgs-usimagery|usgs-usimagerytopo|usgs-ustopo|waymarkedtrails-cycling|waymarkedtrails-hiking|waymarkedtrails-mtb|waymarkedtrails-riding|waymarkedtrails-skating|waymarkedtrails-slopes|wikimedia]
                                  Tile server to serve as the base of the paper
                                  map.
  --api-key KEY                   API key for the chosen tile server (if
                                  applicable).
  --paper-size [a0|a1|a2|a3|a4|a5|a6|a7|letter|legal]
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
