from osgeo import osr

class GDALValidator(osr.SpatialReference):
    """
    Validates a well-known-text(WKT), proj4 string, or EPSG code
    with GDAL's OSR module

    :param wkt: WKT string
    :type wkt: string
    :param proj4: proj4 string
    :type proj4: string
    :param epsg: EPSG code
    :type epsg: int
    """
    def __init__(self, wkt=None, proj4=None, epsg=None):
        super(GDALValidator, self).__init__()

        self.valid = False

        if wkt:
            try:
                self.ImportFromWkt(wkt)
            except Exception:
                pass  # Probably print to some logger or outward messaging
        elif proj4:
            try:
                self.ImportFromProj4(proj4)
            except Exception:
                pass
        elif epsg:
            try:
                self.ImportFromEPSG(epsg)
            except Exception:
                pass

        # This is to catch invalid or no args passed in, the ImportFrom
        # calls also give the OGRERR code
        self.err_num = self.Validate()
        self.err_msg = self._ogrerr_msg(self.err_num)

        if not self.err_num:
            self.valid = True

    def __nonzero__(self):
        return self.valid

    @staticmethod
    def _ogrerr_msg(num):
        """
        Pair OGRERR code with the message defined in the
        GDAL source code, made static for portability

        When validating projection information, usually the only
        values that come up are 0, 5, or 7

        :param num: OGRERR/GDAL error code
        :type num: int
        :return: associated error message
        """
        if num == 0:
            return None
        elif num == 1:
            return 'OGRERR_NOT_ENOUGH_DATA'
        elif num == 2:
            return 'OGRERR_NOT_ENOUGH_MEMORY'
        elif num == 3:
            return 'OGRERR_UNSUPPORTED_GEOMETRY_TYPE'
        elif num == 4:
            return 'OGRERR_UNSUPPORTED_OPERATION'
        elif num == 5:
            return 'OGRERR_CORRUPT_DATA'
        elif num == 6:
            return 'OGRERR_FAILURE'
        elif num == 7:
            return 'OGRERR_UNSUPPORTED_SRS'
        elif num == 8:
            return 'OGRERR_INVALID_HANDLE'
        elif num == 9:
            return 'OGRERR_NON_EXISTING_FEATURE'
        else:
            return 'Unknown GDAL/OGR Error'