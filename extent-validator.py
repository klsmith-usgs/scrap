from dbconnect import DBConnect
from osgeo import osr


class ExtentValidator(object):
    def __init__(self, xmin, xmax, ymin, ymax, srid=0, wkt='', *args, **kwargs):
        pass

    def validate_frame(self):
        pass

    def validate_scenes(self):
        pass

    def db_scenes(self):
        pass

    def comp_scenes(self):
        pass

    def build_tmpsrid(self):
        pass

    def wkt_to_proj4(self):
        pass
