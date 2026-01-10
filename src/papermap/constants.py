from importlib import metadata

NAME: str = "PaperMap"

# headers used for requests
HEADERS: dict[str, str] = {
    "User-Agent": f"{NAME}v{metadata.version('papermap')}",
    "Accept": "image/png,image/*;q=0.9,*/*;q=0.8",
}

# size (width / height) of map tiles
TILE_SIZE: int = 256

# properties of the WGS 84 datum
WGS84_ELLIPSOID = (6_378_137, 1 / 298.257223563)  # equatorial radius, flattening
R: float = WGS84_ELLIPSOID[0]
C: int = 40_075_017  # equatorial circumference

FALSE_EASTING = 500_000
FALSE_NORTHING = 10_000_000
