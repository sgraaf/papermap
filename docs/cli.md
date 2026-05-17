# CLI Reference

The `papermap` command-line interface (CLI) provides for creating ready-to-print paper maps via the command-line.

<!-- [[[cog
import cog
from click.testing import CliRunner

from papermap.cli import cli

def help_output(args):
    result = CliRunner().invoke(cli, args)
    output = result.output.replace("Usage: cli ", "Usage: papermap ")
    cog.out(f"\nRunning `papermap {' '.join(args)}` or `python -m papermap {' '.join(args)}` shows a list of all of the available options and arguments:\n")
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

Running `papermap --help` or `python -m papermap --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap [OPTIONS] COMMAND [ARGS]...

  papermap is a Python library and CLI tool for creating ready-to-print paper
  maps.

  Documentation: https://papermap.readthedocs.io/en/stable/

Options:
  -v, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  latlon*  Generates a paper map for the given geographic coordinates (i.e.
  ecef     Generates a paper map for the given ECEF (Earth-Centered,...
  geojson  Generates a paper map for the given GeoJSON file and outputs it...
  gpx      Generates a paper map for the given GPX file and outputs it to...
  mgrs     Generates a paper map for the given MGRS (Military Grid...
  utm      Generates a paper map for the given UTM (Universal Transverse...
```

<!-- [[[end]]] -->

(cli_help_latlon)=

## papermap latlon

This command generates a paper map for the given spherical coordinate (i.e. lat, lon) and outputs it to file.

<!-- [[[cog
help_output(["latlon", "--help"])
]]] -->

Running `papermap latlon --help` or `python -m papermap latlon --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap latlon [OPTIONS] LATITUDE LONGITUDE FILE

  Generates a paper map for the given geographic coordinates (i.e. lat, lon) and
  outputs it to file.

Options:
  --tile-provider [alltrails|basemapat|basemapat-grau|basemapat-highdpi|basemapat-orthofoto|basemapat-overlay|basemapat-surface|basemapat-terrain|cartodb-darkmatter|cartodb-darkmatter-nolabels|cartodb-darkmatter-onlylabels|cartodb-positron|cartodb-positronnolabels|cartodb-positrononlylabels|cartodb-voyager|cartodb-voyager-labelsunder|cartodb-voyager-nolabels|cartodb-voyager-onlylabels|cyclosm|esri-delorme|esri-natgeoworldmap|esri-oceanbasemap|esri-worldgraycanvas|esri-worldimagery|esri-worldphysical|esri-worldshadedrelief|esri-worldstreetmap|esri-worldterrain|esri-worldtopomap|geofabrik-topo|google-maps|google-maps-roads|google-maps-satellite|google-maps-satellite-hybrid|google-maps-terrain|google-maps-terrain-hybrid|here-basicmap|here-carnavdaygrey|here-hybridday|here-hybriddaygrey|here-hybriddaymobile|here-hybriddaytransit|here-maplabels|here-normalday|here-normaldaycustom|here-normaldaygrey|here-normaldaygreymobile|here-normaldaymobile|here-normaldaytransit|here-normaldaytransitmobile|here-normalnight|here-normalnightgrey|here-normalnightgreymobile|here-normalnightmobile|here-normalnighttransit|here-normalnighttransitmobile|here-pedestrianday|here-pedestriannight|here-reducedday|here-reducednight|here-satelliteday|here-terrainday|here-terraindaymobile|here-trafficflow|hikebike|jawg-dark|jawg-light|jawg-matrix|jawg-streets|jawg-sunny|jawg-terrain|komoot|maptiler-basic|maptiler-bright|maptiler-hybrid|maptiler-outdoor|maptiler-pastel|maptiler-positron|maptiler-satellite|maptiler-streets|maptiler-toner|maptiler-topo|maptiler-winter|mapy-cz|mtbmap|nasagibs-modisterraaod|nasagibs-modisterrabands367cr|nasagibs-modisterrachlorophyll|nasagibs-modisterralstday|nasagibs-modisterrasnowcover|nasagibs-modisterratruecolorcr|nasagibs-viirsearthatnight2012|nlmaps-grijs|nlmaps-luchtfoto|nlmaps-pastel|nlmaps-standaard|nlmaps-water|openaip|openfiremap|openrailwaymap|openseamap|opensnowmap|openstreetmap|openstreetmap-bzh|openstreetmap-ch|openstreetmap-de|openstreetmap-france|openstreetmap-hot|opentopomap|opnvkarte|safecast|stadia-alidadesmooth|stadia-alidasesatellite|stadia-alidasesmoothdark|stadia-osmbright|stadia-outdoors|stadia-stamenterrain|stadia-stamenterrainbackground|stadia-stamenterrainlabels|stadia-stamenterrainlines|stadia-stamentoner|stadia-stamentonerbackground|stadia-stamentonerlabels|stadia-stamentonerlines|stadia-stamentonerlite|stadia-stamenwatercolor|swissfederalgeoportal-nationalmapcolor|swissfederalgeoportal-nationalmapgrey|swissfederalgeoportal-swissimage|thunderforest-atlas|thunderforest-landscape|thunderforest-mobileatlas|thunderforest-neighbourhood|thunderforest-opencyclemap|thunderforest-outdoors|thunderforest-pioneer|thunderforest-spinalmap|thunderforest-transport|thunderforest-transport-dark|tomtom-basic|tomtom-hybrid|tomtom-labels|usgs-usimagery|usgs-usimagerytopo|usgs-ustopo|waymarkedtrails-cycling|waymarkedtrails-hiking|waymarkedtrails-mtb|waymarkedtrails-riding|waymarkedtrails-skating|waymarkedtrails-slopes|wikimedia]
                                  Tile provider to serve as the base of the
                                  paper map.
  --api-key KEY                   API key for the chosen tile provider (if
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
  --strict                        Fail if any tiles cannot be downloaded.
  -h, --help                      Show this message and exit.
```

<!-- [[[end]]] -->

## papermap utm

This command generates a paper map for the given UTM coordinate (i.e. easting, northing, zone) and outputs it to file.

<!-- [[[cog
help_output(["utm", "--help"])
]]] -->

Running `papermap utm --help` or `python -m papermap utm --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap utm [OPTIONS] EASTING NORTHING ZONE-NUMBER HEMISPHERE FILE

  Generates a paper map for the given UTM (Universal Transverse Mercator)
  coordinates and outputs it to file.

Options:
  --tile-provider [alltrails|basemapat|basemapat-grau|basemapat-highdpi|basemapat-orthofoto|basemapat-overlay|basemapat-surface|basemapat-terrain|cartodb-darkmatter|cartodb-darkmatter-nolabels|cartodb-darkmatter-onlylabels|cartodb-positron|cartodb-positronnolabels|cartodb-positrononlylabels|cartodb-voyager|cartodb-voyager-labelsunder|cartodb-voyager-nolabels|cartodb-voyager-onlylabels|cyclosm|esri-delorme|esri-natgeoworldmap|esri-oceanbasemap|esri-worldgraycanvas|esri-worldimagery|esri-worldphysical|esri-worldshadedrelief|esri-worldstreetmap|esri-worldterrain|esri-worldtopomap|geofabrik-topo|google-maps|google-maps-roads|google-maps-satellite|google-maps-satellite-hybrid|google-maps-terrain|google-maps-terrain-hybrid|here-basicmap|here-carnavdaygrey|here-hybridday|here-hybriddaygrey|here-hybriddaymobile|here-hybriddaytransit|here-maplabels|here-normalday|here-normaldaycustom|here-normaldaygrey|here-normaldaygreymobile|here-normaldaymobile|here-normaldaytransit|here-normaldaytransitmobile|here-normalnight|here-normalnightgrey|here-normalnightgreymobile|here-normalnightmobile|here-normalnighttransit|here-normalnighttransitmobile|here-pedestrianday|here-pedestriannight|here-reducedday|here-reducednight|here-satelliteday|here-terrainday|here-terraindaymobile|here-trafficflow|hikebike|jawg-dark|jawg-light|jawg-matrix|jawg-streets|jawg-sunny|jawg-terrain|komoot|maptiler-basic|maptiler-bright|maptiler-hybrid|maptiler-outdoor|maptiler-pastel|maptiler-positron|maptiler-satellite|maptiler-streets|maptiler-toner|maptiler-topo|maptiler-winter|mapy-cz|mtbmap|nasagibs-modisterraaod|nasagibs-modisterrabands367cr|nasagibs-modisterrachlorophyll|nasagibs-modisterralstday|nasagibs-modisterrasnowcover|nasagibs-modisterratruecolorcr|nasagibs-viirsearthatnight2012|nlmaps-grijs|nlmaps-luchtfoto|nlmaps-pastel|nlmaps-standaard|nlmaps-water|openaip|openfiremap|openrailwaymap|openseamap|opensnowmap|openstreetmap|openstreetmap-bzh|openstreetmap-ch|openstreetmap-de|openstreetmap-france|openstreetmap-hot|opentopomap|opnvkarte|safecast|stadia-alidadesmooth|stadia-alidasesatellite|stadia-alidasesmoothdark|stadia-osmbright|stadia-outdoors|stadia-stamenterrain|stadia-stamenterrainbackground|stadia-stamenterrainlabels|stadia-stamenterrainlines|stadia-stamentoner|stadia-stamentonerbackground|stadia-stamentonerlabels|stadia-stamentonerlines|stadia-stamentonerlite|stadia-stamenwatercolor|swissfederalgeoportal-nationalmapcolor|swissfederalgeoportal-nationalmapgrey|swissfederalgeoportal-swissimage|thunderforest-atlas|thunderforest-landscape|thunderforest-mobileatlas|thunderforest-neighbourhood|thunderforest-opencyclemap|thunderforest-outdoors|thunderforest-pioneer|thunderforest-spinalmap|thunderforest-transport|thunderforest-transport-dark|tomtom-basic|tomtom-hybrid|tomtom-labels|usgs-usimagery|usgs-usimagerytopo|usgs-ustopo|waymarkedtrails-cycling|waymarkedtrails-hiking|waymarkedtrails-mtb|waymarkedtrails-riding|waymarkedtrails-skating|waymarkedtrails-slopes|wikimedia]
                                  Tile provider to serve as the base of the
                                  paper map.
  --api-key KEY                   API key for the chosen tile provider (if
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
  --strict                        Fail if any tiles cannot be downloaded.
  -h, --help                      Show this message and exit.
```

<!-- [[[end]]] -->

## papermap mgrs

<!-- [[[cog
help_output(["mgrs", "--help"])
]]] -->

Running `papermap mgrs --help` or `python -m papermap mgrs --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap mgrs [OPTIONS] ZONE-NUMBER BAND SQUARE EASTING NORTHING FILE

  Generates a paper map for the given MGRS (Military Grid Reference System)
  coordinates and outputs it to file.

Options:
  --tile-provider [alltrails|basemapat|basemapat-grau|basemapat-highdpi|basemapat-orthofoto|basemapat-overlay|basemapat-surface|basemapat-terrain|cartodb-darkmatter|cartodb-darkmatter-nolabels|cartodb-darkmatter-onlylabels|cartodb-positron|cartodb-positronnolabels|cartodb-positrononlylabels|cartodb-voyager|cartodb-voyager-labelsunder|cartodb-voyager-nolabels|cartodb-voyager-onlylabels|cyclosm|esri-delorme|esri-natgeoworldmap|esri-oceanbasemap|esri-worldgraycanvas|esri-worldimagery|esri-worldphysical|esri-worldshadedrelief|esri-worldstreetmap|esri-worldterrain|esri-worldtopomap|geofabrik-topo|google-maps|google-maps-roads|google-maps-satellite|google-maps-satellite-hybrid|google-maps-terrain|google-maps-terrain-hybrid|here-basicmap|here-carnavdaygrey|here-hybridday|here-hybriddaygrey|here-hybriddaymobile|here-hybriddaytransit|here-maplabels|here-normalday|here-normaldaycustom|here-normaldaygrey|here-normaldaygreymobile|here-normaldaymobile|here-normaldaytransit|here-normaldaytransitmobile|here-normalnight|here-normalnightgrey|here-normalnightgreymobile|here-normalnightmobile|here-normalnighttransit|here-normalnighttransitmobile|here-pedestrianday|here-pedestriannight|here-reducedday|here-reducednight|here-satelliteday|here-terrainday|here-terraindaymobile|here-trafficflow|hikebike|jawg-dark|jawg-light|jawg-matrix|jawg-streets|jawg-sunny|jawg-terrain|komoot|maptiler-basic|maptiler-bright|maptiler-hybrid|maptiler-outdoor|maptiler-pastel|maptiler-positron|maptiler-satellite|maptiler-streets|maptiler-toner|maptiler-topo|maptiler-winter|mapy-cz|mtbmap|nasagibs-modisterraaod|nasagibs-modisterrabands367cr|nasagibs-modisterrachlorophyll|nasagibs-modisterralstday|nasagibs-modisterrasnowcover|nasagibs-modisterratruecolorcr|nasagibs-viirsearthatnight2012|nlmaps-grijs|nlmaps-luchtfoto|nlmaps-pastel|nlmaps-standaard|nlmaps-water|openaip|openfiremap|openrailwaymap|openseamap|opensnowmap|openstreetmap|openstreetmap-bzh|openstreetmap-ch|openstreetmap-de|openstreetmap-france|openstreetmap-hot|opentopomap|opnvkarte|safecast|stadia-alidadesmooth|stadia-alidasesatellite|stadia-alidasesmoothdark|stadia-osmbright|stadia-outdoors|stadia-stamenterrain|stadia-stamenterrainbackground|stadia-stamenterrainlabels|stadia-stamenterrainlines|stadia-stamentoner|stadia-stamentonerbackground|stadia-stamentonerlabels|stadia-stamentonerlines|stadia-stamentonerlite|stadia-stamenwatercolor|swissfederalgeoportal-nationalmapcolor|swissfederalgeoportal-nationalmapgrey|swissfederalgeoportal-swissimage|thunderforest-atlas|thunderforest-landscape|thunderforest-mobileatlas|thunderforest-neighbourhood|thunderforest-opencyclemap|thunderforest-outdoors|thunderforest-pioneer|thunderforest-spinalmap|thunderforest-transport|thunderforest-transport-dark|tomtom-basic|tomtom-hybrid|tomtom-labels|usgs-usimagery|usgs-usimagerytopo|usgs-ustopo|waymarkedtrails-cycling|waymarkedtrails-hiking|waymarkedtrails-mtb|waymarkedtrails-riding|waymarkedtrails-skating|waymarkedtrails-slopes|wikimedia]
                                  Tile provider to serve as the base of the
                                  paper map.
  --api-key KEY                   API key for the chosen tile provider (if
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
  --strict                        Fail if any tiles cannot be downloaded.
  -h, --help                      Show this message and exit.
```

<!-- [[[end]]] -->

## papermap ecef

<!-- [[[cog
help_output(["ecef", "--help"])
]]] -->

Running `papermap ecef --help` or `python -m papermap ecef --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap ecef [OPTIONS] X Y Z FILE

  Generates a paper map for the given ECEF (Earth-Centered, Earth-Fixed)
  Cartesian coordinates and outputs it to file.

Options:
  --tile-provider [alltrails|basemapat|basemapat-grau|basemapat-highdpi|basemapat-orthofoto|basemapat-overlay|basemapat-surface|basemapat-terrain|cartodb-darkmatter|cartodb-darkmatter-nolabels|cartodb-darkmatter-onlylabels|cartodb-positron|cartodb-positronnolabels|cartodb-positrononlylabels|cartodb-voyager|cartodb-voyager-labelsunder|cartodb-voyager-nolabels|cartodb-voyager-onlylabels|cyclosm|esri-delorme|esri-natgeoworldmap|esri-oceanbasemap|esri-worldgraycanvas|esri-worldimagery|esri-worldphysical|esri-worldshadedrelief|esri-worldstreetmap|esri-worldterrain|esri-worldtopomap|geofabrik-topo|google-maps|google-maps-roads|google-maps-satellite|google-maps-satellite-hybrid|google-maps-terrain|google-maps-terrain-hybrid|here-basicmap|here-carnavdaygrey|here-hybridday|here-hybriddaygrey|here-hybriddaymobile|here-hybriddaytransit|here-maplabels|here-normalday|here-normaldaycustom|here-normaldaygrey|here-normaldaygreymobile|here-normaldaymobile|here-normaldaytransit|here-normaldaytransitmobile|here-normalnight|here-normalnightgrey|here-normalnightgreymobile|here-normalnightmobile|here-normalnighttransit|here-normalnighttransitmobile|here-pedestrianday|here-pedestriannight|here-reducedday|here-reducednight|here-satelliteday|here-terrainday|here-terraindaymobile|here-trafficflow|hikebike|jawg-dark|jawg-light|jawg-matrix|jawg-streets|jawg-sunny|jawg-terrain|komoot|maptiler-basic|maptiler-bright|maptiler-hybrid|maptiler-outdoor|maptiler-pastel|maptiler-positron|maptiler-satellite|maptiler-streets|maptiler-toner|maptiler-topo|maptiler-winter|mapy-cz|mtbmap|nasagibs-modisterraaod|nasagibs-modisterrabands367cr|nasagibs-modisterrachlorophyll|nasagibs-modisterralstday|nasagibs-modisterrasnowcover|nasagibs-modisterratruecolorcr|nasagibs-viirsearthatnight2012|nlmaps-grijs|nlmaps-luchtfoto|nlmaps-pastel|nlmaps-standaard|nlmaps-water|openaip|openfiremap|openrailwaymap|openseamap|opensnowmap|openstreetmap|openstreetmap-bzh|openstreetmap-ch|openstreetmap-de|openstreetmap-france|openstreetmap-hot|opentopomap|opnvkarte|safecast|stadia-alidadesmooth|stadia-alidasesatellite|stadia-alidasesmoothdark|stadia-osmbright|stadia-outdoors|stadia-stamenterrain|stadia-stamenterrainbackground|stadia-stamenterrainlabels|stadia-stamenterrainlines|stadia-stamentoner|stadia-stamentonerbackground|stadia-stamentonerlabels|stadia-stamentonerlines|stadia-stamentonerlite|stadia-stamenwatercolor|swissfederalgeoportal-nationalmapcolor|swissfederalgeoportal-nationalmapgrey|swissfederalgeoportal-swissimage|thunderforest-atlas|thunderforest-landscape|thunderforest-mobileatlas|thunderforest-neighbourhood|thunderforest-opencyclemap|thunderforest-outdoors|thunderforest-pioneer|thunderforest-spinalmap|thunderforest-transport|thunderforest-transport-dark|tomtom-basic|tomtom-hybrid|tomtom-labels|usgs-usimagery|usgs-usimagerytopo|usgs-ustopo|waymarkedtrails-cycling|waymarkedtrails-hiking|waymarkedtrails-mtb|waymarkedtrails-riding|waymarkedtrails-skating|waymarkedtrails-slopes|wikimedia]
                                  Tile provider to serve as the base of the
                                  paper map.
  --api-key KEY                   API key for the chosen tile provider (if
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
  --strict                        Fail if any tiles cannot be downloaded.
  -h, --help                      Show this message and exit.
```

<!-- [[[end]]] -->

## papermap geojson

This command generates a paper map for the given GeoJSON file and outputs it to file.

<!-- [[[cog
help_output(["geojson", "--help"])
]]] -->

Running `papermap geojson --help` or `python -m papermap geojson --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap geojson [OPTIONS] GEOJSON_FILE FILE

  Generates a paper map for the given GeoJSON file and outputs it to file.

Options:
  --auto-scale                    Compute the scale automatically to fit the
                                  GeoJSON geometries.
  --padding MILLIMETERS           Padding between the GeoJSON geometries and the
                                  image edge (per side). Only used with --auto-
                                  scale.
  --stroke COLOR                  Outline colour (CSS-style hex) for markers,
                                  lines and polygons.
  --stroke-width MILLIMETERS      Outline width on paper for markers, lines and
                                  polygons.
  --stroke-opacity FLOAT          Outline opacity, in [0, 1], for markers, lines
                                  and polygons.  [0.0<=x<=1.0]
  --fill COLOR                    Fill colour (CSS-style hex) for markers and
                                  polygons.
  --fill-opacity FLOAT            Fill opacity, in [0, 1], for markers and
                                  polygons.  [0.0<=x<=1.0]
  --opacity FLOAT                 Overall opacity, in [0, 1], for all features.
                                  [0.0<=x<=1.0]
  --marker-radius MILLIMETERS     Circle marker radius on paper.
  --tile-provider [alltrails|basemapat|basemapat-grau|basemapat-highdpi|basemapat-orthofoto|basemapat-overlay|basemapat-surface|basemapat-terrain|cartodb-darkmatter|cartodb-darkmatter-nolabels|cartodb-darkmatter-onlylabels|cartodb-positron|cartodb-positronnolabels|cartodb-positrononlylabels|cartodb-voyager|cartodb-voyager-labelsunder|cartodb-voyager-nolabels|cartodb-voyager-onlylabels|cyclosm|esri-delorme|esri-natgeoworldmap|esri-oceanbasemap|esri-worldgraycanvas|esri-worldimagery|esri-worldphysical|esri-worldshadedrelief|esri-worldstreetmap|esri-worldterrain|esri-worldtopomap|geofabrik-topo|google-maps|google-maps-roads|google-maps-satellite|google-maps-satellite-hybrid|google-maps-terrain|google-maps-terrain-hybrid|here-basicmap|here-carnavdaygrey|here-hybridday|here-hybriddaygrey|here-hybriddaymobile|here-hybriddaytransit|here-maplabels|here-normalday|here-normaldaycustom|here-normaldaygrey|here-normaldaygreymobile|here-normaldaymobile|here-normaldaytransit|here-normaldaytransitmobile|here-normalnight|here-normalnightgrey|here-normalnightgreymobile|here-normalnightmobile|here-normalnighttransit|here-normalnighttransitmobile|here-pedestrianday|here-pedestriannight|here-reducedday|here-reducednight|here-satelliteday|here-terrainday|here-terraindaymobile|here-trafficflow|hikebike|jawg-dark|jawg-light|jawg-matrix|jawg-streets|jawg-sunny|jawg-terrain|komoot|maptiler-basic|maptiler-bright|maptiler-hybrid|maptiler-outdoor|maptiler-pastel|maptiler-positron|maptiler-satellite|maptiler-streets|maptiler-toner|maptiler-topo|maptiler-winter|mapy-cz|mtbmap|nasagibs-modisterraaod|nasagibs-modisterrabands367cr|nasagibs-modisterrachlorophyll|nasagibs-modisterralstday|nasagibs-modisterrasnowcover|nasagibs-modisterratruecolorcr|nasagibs-viirsearthatnight2012|nlmaps-grijs|nlmaps-luchtfoto|nlmaps-pastel|nlmaps-standaard|nlmaps-water|openaip|openfiremap|openrailwaymap|openseamap|opensnowmap|openstreetmap|openstreetmap-bzh|openstreetmap-ch|openstreetmap-de|openstreetmap-france|openstreetmap-hot|opentopomap|opnvkarte|safecast|stadia-alidadesmooth|stadia-alidasesatellite|stadia-alidasesmoothdark|stadia-osmbright|stadia-outdoors|stadia-stamenterrain|stadia-stamenterrainbackground|stadia-stamenterrainlabels|stadia-stamenterrainlines|stadia-stamentoner|stadia-stamentonerbackground|stadia-stamentonerlabels|stadia-stamentonerlines|stadia-stamentonerlite|stadia-stamenwatercolor|swissfederalgeoportal-nationalmapcolor|swissfederalgeoportal-nationalmapgrey|swissfederalgeoportal-swissimage|thunderforest-atlas|thunderforest-landscape|thunderforest-mobileatlas|thunderforest-neighbourhood|thunderforest-opencyclemap|thunderforest-outdoors|thunderforest-pioneer|thunderforest-spinalmap|thunderforest-transport|thunderforest-transport-dark|tomtom-basic|tomtom-hybrid|tomtom-labels|usgs-usimagery|usgs-usimagerytopo|usgs-ustopo|waymarkedtrails-cycling|waymarkedtrails-hiking|waymarkedtrails-mtb|waymarkedtrails-riding|waymarkedtrails-skating|waymarkedtrails-slopes|wikimedia]
                                  Tile provider to serve as the base of the
                                  paper map.
  --api-key KEY                   API key for the chosen tile provider (if
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
  --strict                        Fail if any tiles cannot be downloaded.
  -h, --help                      Show this message and exit.
```

<!-- [[[end]]] -->

## papermap gpx

This command generates a paper map for the given GPX file and outputs it to file.

<!-- [[[cog
help_output(["gpx", "--help"])
]]] -->

Running `papermap gpx --help` or `python -m papermap gpx --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap gpx [OPTIONS] GPX_FILE FILE

  Generates a paper map for the given GPX file and outputs it to file.

  Requires the optional 'gpx' package; install with 'pip install papermap[gpx]'.

Options:
  --auto-scale                    Compute the scale automatically to fit the GPX
                                  geometries.
  --padding MILLIMETERS           Padding between the GPX geometries and the
                                  image edge (per side). Only used with --auto-
                                  scale.
  --stroke COLOR                  Outline colour (CSS-style hex) for markers,
                                  lines and polygons.
  --stroke-width MILLIMETERS      Outline width on paper for markers, lines and
                                  polygons.
  --stroke-opacity FLOAT          Outline opacity, in [0, 1], for markers, lines
                                  and polygons.  [0.0<=x<=1.0]
  --fill COLOR                    Fill colour (CSS-style hex) for markers and
                                  polygons.
  --fill-opacity FLOAT            Fill opacity, in [0, 1], for markers and
                                  polygons.  [0.0<=x<=1.0]
  --opacity FLOAT                 Overall opacity, in [0, 1], for all features.
                                  [0.0<=x<=1.0]
  --marker-radius MILLIMETERS     Circle marker radius on paper.
  --tile-provider [alltrails|basemapat|basemapat-grau|basemapat-highdpi|basemapat-orthofoto|basemapat-overlay|basemapat-surface|basemapat-terrain|cartodb-darkmatter|cartodb-darkmatter-nolabels|cartodb-darkmatter-onlylabels|cartodb-positron|cartodb-positronnolabels|cartodb-positrononlylabels|cartodb-voyager|cartodb-voyager-labelsunder|cartodb-voyager-nolabels|cartodb-voyager-onlylabels|cyclosm|esri-delorme|esri-natgeoworldmap|esri-oceanbasemap|esri-worldgraycanvas|esri-worldimagery|esri-worldphysical|esri-worldshadedrelief|esri-worldstreetmap|esri-worldterrain|esri-worldtopomap|geofabrik-topo|google-maps|google-maps-roads|google-maps-satellite|google-maps-satellite-hybrid|google-maps-terrain|google-maps-terrain-hybrid|here-basicmap|here-carnavdaygrey|here-hybridday|here-hybriddaygrey|here-hybriddaymobile|here-hybriddaytransit|here-maplabels|here-normalday|here-normaldaycustom|here-normaldaygrey|here-normaldaygreymobile|here-normaldaymobile|here-normaldaytransit|here-normaldaytransitmobile|here-normalnight|here-normalnightgrey|here-normalnightgreymobile|here-normalnightmobile|here-normalnighttransit|here-normalnighttransitmobile|here-pedestrianday|here-pedestriannight|here-reducedday|here-reducednight|here-satelliteday|here-terrainday|here-terraindaymobile|here-trafficflow|hikebike|jawg-dark|jawg-light|jawg-matrix|jawg-streets|jawg-sunny|jawg-terrain|komoot|maptiler-basic|maptiler-bright|maptiler-hybrid|maptiler-outdoor|maptiler-pastel|maptiler-positron|maptiler-satellite|maptiler-streets|maptiler-toner|maptiler-topo|maptiler-winter|mapy-cz|mtbmap|nasagibs-modisterraaod|nasagibs-modisterrabands367cr|nasagibs-modisterrachlorophyll|nasagibs-modisterralstday|nasagibs-modisterrasnowcover|nasagibs-modisterratruecolorcr|nasagibs-viirsearthatnight2012|nlmaps-grijs|nlmaps-luchtfoto|nlmaps-pastel|nlmaps-standaard|nlmaps-water|openaip|openfiremap|openrailwaymap|openseamap|opensnowmap|openstreetmap|openstreetmap-bzh|openstreetmap-ch|openstreetmap-de|openstreetmap-france|openstreetmap-hot|opentopomap|opnvkarte|safecast|stadia-alidadesmooth|stadia-alidasesatellite|stadia-alidasesmoothdark|stadia-osmbright|stadia-outdoors|stadia-stamenterrain|stadia-stamenterrainbackground|stadia-stamenterrainlabels|stadia-stamenterrainlines|stadia-stamentoner|stadia-stamentonerbackground|stadia-stamentonerlabels|stadia-stamentonerlines|stadia-stamentonerlite|stadia-stamenwatercolor|swissfederalgeoportal-nationalmapcolor|swissfederalgeoportal-nationalmapgrey|swissfederalgeoportal-swissimage|thunderforest-atlas|thunderforest-landscape|thunderforest-mobileatlas|thunderforest-neighbourhood|thunderforest-opencyclemap|thunderforest-outdoors|thunderforest-pioneer|thunderforest-spinalmap|thunderforest-transport|thunderforest-transport-dark|tomtom-basic|tomtom-hybrid|tomtom-labels|usgs-usimagery|usgs-usimagerytopo|usgs-ustopo|waymarkedtrails-cycling|waymarkedtrails-hiking|waymarkedtrails-mtb|waymarkedtrails-riding|waymarkedtrails-skating|waymarkedtrails-slopes|wikimedia]
                                  Tile provider to serve as the base of the
                                  paper map.
  --api-key KEY                   API key for the chosen tile provider (if
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
  --strict                        Fail if any tiles cannot be downloaded.
  -h, --help                      Show this message and exit.
```

<!-- [[[end]]] -->
