"""NASA GIBS (Global Imagery Browse Services) tile provider configurations.

NASA GIBS provides satellite imagery from various NASA missions,
including MODIS and VIIRS data.

See: https://earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs
"""

from __future__ import annotations

from papermap.tile_provider import TileProvider

NASA_ATTRIBUTION = "Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (ESDIS) with funding provided by NASA/HQ"
NASA_HTML_ATTRIBUTION = (
    "Imagery provided by services from the "
    '<a href="https://earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs">GIBS</a>, '
    "operated by the NASA/GSFC/Earth Science Data and Information System "
    '(<a href="https://earthdata.nasa.gov/">ESDIS</a>) with funding provided by NASA/HQ'
)


def _nasa_provider(  # noqa: PLR0913
    key: str,
    name: str,
    variant: str,
    zoom_max: int = 9,
    time: str = "",
    tilematrixset: str = "GoogleMapsCompatible_Level",
    ext: str = "jpg",
) -> TileProvider:
    """Create a NASA GIBS tile provider configuration."""
    time_param = f"&TIME={time}" if time else ""
    return TileProvider(
        key=key,
        name=name,
        attribution=NASA_ATTRIBUTION,
        html_attribution=NASA_HTML_ATTRIBUTION,
        url_template=f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{variant}/default/{time_param}{tilematrixset}/{{z}}/{{y}}/{{x}}.{ext}",
        subdomains=None,
        zoom_min=0,
        zoom_max=zoom_max,
    )


TILE_PROVIDERS: list[TileProvider] = [
    _nasa_provider(
        "nasagibs-modisterratruecolorcr",
        "NASAGIBS ModisTerraTrueColorCR",
        "MODIS_Terra_CorrectedReflectance_TrueColor",
    ),
    _nasa_provider(
        "nasagibs-modisterrabands367cr",
        "NASAGIBS ModisTerraBands367CR",
        "MODIS_Terra_CorrectedReflectance_Bands367",
    ),
    _nasa_provider(
        "nasagibs-viirsearthatnight2012",
        "NASAGIBS ViirsEarthAtNight2012",
        "VIIRS_CityLights_2012",
        zoom_max=8,
    ),
    _nasa_provider(
        "nasagibs-modisterralstday",
        "NASAGIBS ModisTerraLSTDay",
        "MODIS_Terra_Land_Surface_Temp_Day",
        zoom_max=7,
        tilematrixset="GoogleMapsCompatible_Level",
        ext="png",
    ),
    _nasa_provider(
        "nasagibs-modisterrasnowcover",
        "NASAGIBS ModisTerraSnowCover",
        "MODIS_Terra_NDSI_Snow_Cover",
        zoom_max=8,
        ext="png",
    ),
    _nasa_provider(
        "nasagibs-modisterraaod",
        "NASAGIBS ModisTerraAOD",
        "MODIS_Terra_Aerosol",
        zoom_max=6,
        ext="png",
    ),
    _nasa_provider(
        "nasagibs-modisterrachlorophyll",
        "NASAGIBS ModisTerraChlorophyll",
        "MODIS_Terra_Chlorophyll_A",
        zoom_max=7,
        ext="png",
    ),
]
"""NASA GIBS tile providers."""

KEY_TO_TILE_PROVIDER: dict[str, TileProvider] = {ts.key: ts for ts in TILE_PROVIDERS}
"""Mapping from tile provider key to TileProvider instance."""
