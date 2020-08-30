import random
import unittest

from papermap import PaperMap
from papermap.utils import (zoom_to_scale, scale_to_zoom, dd_to_dms, destination,
                            dms_to_dd, distance, initial_brng,
                            lat_to_y, lon_to_x, mm_to_px, px_to_mm,
                            rd_to_wgs84, utm_to_wgs84, wgs84_to_rd,
                            wgs84_to_utm, wgs84_to_zone_number, x_to_lon,
                            y_to_lat, wrap90, wrap180)


class TestUtils(unittest.TestCase):
    def test_convert_scale_zoom(self):
        for _ in range(20):
            lat = random.uniform(-90, 90)
            zoom = random.randint(0, 18)
            scale = zoom_to_scale(zoom, lat, dpi=300)
            z = scale_to_zoom(scale, lat, dpi=300)
            self.assertAlmostEqual(zoom, z, places=5)

    def test_constrain_lat(self):
        for _ in range(20):
            lat = random.uniform(-180, 180)
            l = wrap90(lat)
            self.assertTrue(-90 <= l <= 90)

    def test_constrain_lon(self):
        for _ in range(20):
            lon = random.uniform(-360, 360)
            l = wrap180(lon)
            self.assertTrue(-180 <= l <= 180)

    def test_dd_dms_conversion(self):
        for _ in range(20):
            dd = random.uniform(0.0, 180.0)
            dms = dd_to_dms(dd)
            dd_ = dms_to_dd(dms)
            self.assertAlmostEqual(dd, dd_, places=5)

    def test_lat_y_conversion(self):
        for _ in range(20):
            lat = random.uniform(-90, 90)
            zoom = random.randint(0, 18)
            y = lat_to_y(lat, zoom)
            l = y_to_lat(y, zoom)
            self.assertAlmostEqual(lat, l, places=5)

    def test_lon_x_conversion(self):
        for _ in range(20):
            lon = random.uniform(-180, 180)
            zoom = random.randint(0, 18)
            x = lon_to_x(lon, zoom)
            l = x_to_lon(x, zoom)
            self.assertAlmostEqual(lon, l, places=5)

    def test_mm_px_convesion(self):
        for _ in range(20):
            mm = random.randint(0, 1000)
            dpi = random.choice([20, 72, 100, 300])
            px = mm_to_px(mm, dpi)
            mm_ = px_to_mm(px, dpi)
            self.assertAlmostEqual(mm, mm_, places=-1)

    def test_wgs84_rd_conversion(self):
        for _ in range(20):
            lat = random.uniform(50.75, 53.50)
            lon = random.uniform(3.36, 6.09)
            x, y = wgs84_to_rd(lat, lon)
            lat_, lon_ = rd_to_wgs84(x, y)
            self.assertAlmostEqual(lat, lat_, places=5)
            self.assertAlmostEqual(lon, lon_, places=5)

    def test_wgs84_utm_conversion(self):
        for _ in range(20):
            lat = random.uniform(-80, 84)
            lon = random.uniform(-180, 180)
            x, y, z, l = wgs84_to_utm(lat, lon)
            lat_, lon_ = utm_to_wgs84(x, y, z, l)
            self.assertAlmostEqual(lat, lat_, places=4)
            self.assertAlmostEqual(lon, lon_, places=4)

    def test_distance_bearing_destination_conversion(self):
        for _ in range(20):
            lat1 = random.uniform(-80, 84)
            lon1 = random.uniform(-180, 180)
            lat2 = random.uniform(-80, 84)
            lon2 = random.uniform(-180, 180)
            d = distance(lat1, lon1, lat2, lon2)
            brng = initial_brng(lat1, lon1, lat2, lon2)
            lat2_, lon2_ = destination(lat1, lon1, d, brng)
            self.assertAlmostEqual(lat2, lat2_, places=4)
            self.assertAlmostEqual(lon2, lon2_, places=4)


if __name__ == '__main__':
    unittest.main()
