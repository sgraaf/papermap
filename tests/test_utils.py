from typing import Callable

import pytest

from papermap import utils


def test_clip():
    assert utils.clip(5, 1, 10) == 5
    assert utils.clip(1, 5, 10) == 5
    assert utils.clip(11, 5, 10) == 10
    with pytest.raises(ValueError):
        utils.clip(11, 15, 10)


@pytest.mark.parametrize(
    "input,expected",
    (
        ((45, 135), 45),
        ((225, 135), -45),
        ((300, 135), 30),
    ),
)
def test_wrap(input, expected):
    assert utils.wrap(*input) == expected


@pytest.mark.parametrize(
    "input,expected",
    (
        (45, 45),
        (135, -45),
        (210, 30),
    ),
)
def test_wrap90(input, expected):
    assert utils.wrap90(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    (
        (45, 45),
        (225, -135),
        (405, 45),
    ),
)
def test_wrap180(input, expected):
    assert utils.wrap180(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    (
        (45, 45),
        (405, 45),
        (750, 30),
    ),
)
def test_wrap360(input, expected):
    assert utils.wrap360(input) == expected


def lon_lat_x_y_zoom(func: Callable) -> Callable:
    return pytest.mark.parametrize(
        "lat,lon,x,y,zoom",
        (
            (13.736717, 100.523186, 24.93539, 14.76709, 5),  # Bangkok
            (40.416775, -3.703790, 62.68310, 48.26409, 7),  # Madrid
            (19.432608, -99.133209, 0.22463, 0.44495, 0),  # Mexico City
            (49.246292, -123.116226, 2588.84376, 5609.50009, 14),  # Vancouver
        ),
    )(func)


@lon_lat_x_y_zoom
def test_lon_to_x(lat, lon, x, y, zoom):
    assert utils.lon_to_x(lon, zoom) == pytest.approx(x)


@lon_lat_x_y_zoom
def test_x_to_lon(lat, lon, x, y, zoom):
    assert utils.x_to_lon(x, zoom) == pytest.approx(lon)


@lon_lat_x_y_zoom
def test_lat_to_y(lat, lon, x, y, zoom):
    assert utils.lat_to_y(lat, zoom) == pytest.approx(y)


@lon_lat_x_y_zoom
def test_y_to_lat(lat, lon, x, y, zoom):
    assert utils.y_to_lat(y, zoom) == pytest.approx(lat)
