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
help_output(["latlon", "--help"])
]]] -->

Running `gpx latlon --help` or `python -m gpx latlon --help` shows a list of all of the available options and arguments:

```sh
Usage: papermap latlon [OPTIONS] LATITUDE LONGITUDE FILE

  Generates a paper map for the given spherical coordinate (i.e. lat, lon) and
  outputs it to file.

Options:
  --tile-server [OpenStreetMap|OpenStreetMap DE|OpenStreetMap CH|OpenStreetMap France|OpenStreetMap HOT|OpenStreetMap BZH|OpenTopoMap|OpenSeaMap|Thunderforest OpenCycleMap|Thunderforest Transport|Thunderforest Transport Dark|Thunderforest SpinalMap|Thunderforest Landscape|Thunderforest Outdoors|Thunderforest Pioneer|Thunderforest MobileAtlas|Thunderforest Neighbourhood|Thunderforest Atlas|Esri WorldStreetMap|Esri DeLorme|Esri WorldTopoMap|Esri WorldImagery|Esri WorldTerrain|Esri WorldShadedRelief|Esri WorldPhysical|Esri OceanBasemap|Esri NatGeoWorldMap|Esri WorldGrayCanvas|Stadia AlidadeSmooth|Stadia AlidadeSmoothDark|Stadia AlidadeSatellite|Stadia OSMBright|Stadia Outdoors|Stadia StamenToner|Stadia StamenTonerBackground|Stadia StamenTonerLines|Stadia StamenTonerLabels|Stadia StamenTonerLite|Stadia StamenWatercolor|Stadia StamenTerrain|Stadia StamenTerrainBackground|Stadia StamenTerrainLabels|Stadia StamenTerrainLines|CartoDB Positron|CartoDB PositronNoLabels|CartoDB PositronOnlyLabels|CartoDB DarkMatter|CartoDB DarkMatterNoLabels|CartoDB DarkMatterOnlyLabels|CartoDB Voyager|CartoDB VoyagerNoLabels|CartoDB VoyagerOnlyLabels|CartoDB VoyagerLabelsUnder|Google Maps|Google Maps Satellite|Google Maps Satellite Hybrid|Google Maps Terrain|Google Maps Terrain Hybrid|Google Maps Roads|HERE normalDay|HERE normalDayCustom|HERE normalDayGrey|HERE normalDayMobile|HERE normalDayGreyMobile|HERE normalDayTransit|HERE normalDayTransitMobile|HERE normalNight|HERE normalNightMobile|HERE normalNightGrey|HERE normalNightGreyMobile|HERE normalNightTransit|HERE normalNightTransitMobile|HERE reducedDay|HERE reducedNight|HERE basicMap|HERE mapLabels|HERE trafficFlow|HERE carnavDayGrey|HERE hybridDay|HERE hybridDayMobile|HERE hybridDayTransit|HERE hybridDayGrey|HERE pedestrianDay|HERE pedestrianNight|HERE satelliteDay|HERE terrainDay|HERE terrainDayMobile|USGS USTopo|USGS USImagery|USGS USImageryTopo|NASAGIBS ModisTerraTrueColorCR|NASAGIBS ModisTerraBands367CR|NASAGIBS ViirsEarthAtNight2012|NASAGIBS ModisTerraLSTDay|NASAGIBS ModisTerraSnowCover|NASAGIBS ModisTerraAOD|NASAGIBS ModisTerraChlorophyll|Wikimedia|CyclOSM|Jawg Streets|Jawg Terrain|Jawg Sunny|Jawg Dark|Jawg Light|Jawg Matrix|MapTiler Streets|MapTiler Basic|MapTiler Bright|MapTiler Pastel|MapTiler Positron|MapTiler Hybrid|MapTiler Satellite|MapTiler Toner|MapTiler Topo|MapTiler Winter|MapTiler Outdoor|TomTom Basic|TomTom Hybrid|TomTom Labels|BasemapAT|BasemapAT Grau|BasemapAT Overlay|BasemapAT Terrain|BasemapAT Surface|BasemapAT Highdpi|BasemapAT Orthofoto|NLMaps Standaard|NLMaps Pastel|NLMaps Grijs|NLMaps Water|NLMaps Luchtfoto|SwissFederalGeoportal NationalMapColor|SwissFederalGeoportal NationalMapGrey|SwissFederalGeoportal SWISSIMAGE|OPNVKarte|MtbMap|HikeBike|SafeCast|Geofabrik Topo|Mapy.cz|Komoot|AllTrails|Waymarked Trails Hiking|Waymarked Trails Cycling|Waymarked Trails MTB|Waymarked Trails Slopes|Waymarked Trails Riding|Waymarked Trails Skating|OpenAIP|OpenSnowMap|OpenRailwayMap|OpenFireMap|OpenStreetMap Monochrome|ESRI Standard|ESRI Satellite|ESRI Topo|ESRI Dark Gray|ESRI Light Gray|ESRI Transportation|HERE Terrain|HERE Satellite|HERE Hybrid|Stamen Terrain|Stamen Toner|Stamen Toner Lite|Hike & Bike]
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
  --tile-server [OpenStreetMap|OpenStreetMap DE|OpenStreetMap CH|OpenStreetMap France|OpenStreetMap HOT|OpenStreetMap BZH|OpenTopoMap|OpenSeaMap|Thunderforest OpenCycleMap|Thunderforest Transport|Thunderforest Transport Dark|Thunderforest SpinalMap|Thunderforest Landscape|Thunderforest Outdoors|Thunderforest Pioneer|Thunderforest MobileAtlas|Thunderforest Neighbourhood|Thunderforest Atlas|Esri WorldStreetMap|Esri DeLorme|Esri WorldTopoMap|Esri WorldImagery|Esri WorldTerrain|Esri WorldShadedRelief|Esri WorldPhysical|Esri OceanBasemap|Esri NatGeoWorldMap|Esri WorldGrayCanvas|Stadia AlidadeSmooth|Stadia AlidadeSmoothDark|Stadia AlidadeSatellite|Stadia OSMBright|Stadia Outdoors|Stadia StamenToner|Stadia StamenTonerBackground|Stadia StamenTonerLines|Stadia StamenTonerLabels|Stadia StamenTonerLite|Stadia StamenWatercolor|Stadia StamenTerrain|Stadia StamenTerrainBackground|Stadia StamenTerrainLabels|Stadia StamenTerrainLines|CartoDB Positron|CartoDB PositronNoLabels|CartoDB PositronOnlyLabels|CartoDB DarkMatter|CartoDB DarkMatterNoLabels|CartoDB DarkMatterOnlyLabels|CartoDB Voyager|CartoDB VoyagerNoLabels|CartoDB VoyagerOnlyLabels|CartoDB VoyagerLabelsUnder|Google Maps|Google Maps Satellite|Google Maps Satellite Hybrid|Google Maps Terrain|Google Maps Terrain Hybrid|Google Maps Roads|HERE normalDay|HERE normalDayCustom|HERE normalDayGrey|HERE normalDayMobile|HERE normalDayGreyMobile|HERE normalDayTransit|HERE normalDayTransitMobile|HERE normalNight|HERE normalNightMobile|HERE normalNightGrey|HERE normalNightGreyMobile|HERE normalNightTransit|HERE normalNightTransitMobile|HERE reducedDay|HERE reducedNight|HERE basicMap|HERE mapLabels|HERE trafficFlow|HERE carnavDayGrey|HERE hybridDay|HERE hybridDayMobile|HERE hybridDayTransit|HERE hybridDayGrey|HERE pedestrianDay|HERE pedestrianNight|HERE satelliteDay|HERE terrainDay|HERE terrainDayMobile|USGS USTopo|USGS USImagery|USGS USImageryTopo|NASAGIBS ModisTerraTrueColorCR|NASAGIBS ModisTerraBands367CR|NASAGIBS ViirsEarthAtNight2012|NASAGIBS ModisTerraLSTDay|NASAGIBS ModisTerraSnowCover|NASAGIBS ModisTerraAOD|NASAGIBS ModisTerraChlorophyll|Wikimedia|CyclOSM|Jawg Streets|Jawg Terrain|Jawg Sunny|Jawg Dark|Jawg Light|Jawg Matrix|MapTiler Streets|MapTiler Basic|MapTiler Bright|MapTiler Pastel|MapTiler Positron|MapTiler Hybrid|MapTiler Satellite|MapTiler Toner|MapTiler Topo|MapTiler Winter|MapTiler Outdoor|TomTom Basic|TomTom Hybrid|TomTom Labels|BasemapAT|BasemapAT Grau|BasemapAT Overlay|BasemapAT Terrain|BasemapAT Surface|BasemapAT Highdpi|BasemapAT Orthofoto|NLMaps Standaard|NLMaps Pastel|NLMaps Grijs|NLMaps Water|NLMaps Luchtfoto|SwissFederalGeoportal NationalMapColor|SwissFederalGeoportal NationalMapGrey|SwissFederalGeoportal SWISSIMAGE|OPNVKarte|MtbMap|HikeBike|SafeCast|Geofabrik Topo|Mapy.cz|Komoot|AllTrails|Waymarked Trails Hiking|Waymarked Trails Cycling|Waymarked Trails MTB|Waymarked Trails Slopes|Waymarked Trails Riding|Waymarked Trails Skating|OpenAIP|OpenSnowMap|OpenRailwayMap|OpenFireMap|OpenStreetMap Monochrome|ESRI Standard|ESRI Satellite|ESRI Topo|ESRI Dark Gray|ESRI Light Gray|ESRI Transportation|HERE Terrain|HERE Satellite|HERE Hybrid|Stamen Terrain|Stamen Toner|Stamen Toner Lite|Hike & Bike]
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
