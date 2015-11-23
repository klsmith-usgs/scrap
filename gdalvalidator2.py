from osgeo import osr

class GDALValidator(osr.SpatialReference):
    """
    Used for validating a spatial reference against GDAL's library
    to make sure it is compatible
    """
    def __init__(self):
        super(GDALValidator, self).__init__()

        self.valid = False
        self.err_num = 5
        self.err_msg = self.ogrerr_msg(self.err_num)

    def __nonzero__(self):
        return self.valid

    def check_valid(self):
        self.err_num = self.Validate()
        self.err_msg = self.ogrerr_msg(self.err_num)

        if not self.err_num:
            self.valid = True

    @staticmethod
    def ogrerr_msg(num):
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


class WKTValidate(GDALValidator):
    """
    GDALValidator subclass for checking well-known-texts
    """
    def __init__(self, wkt=''):
        super(WKTValidate, self).__init__()

        try:
            self.ImportFromWkt(wkt)
        except Exception:
            pass

        self.check_valid()


class Proj4Validate(GDALValidator):
    """
    GDALValidator subclass for checking proj4 strings
    """
    def __init__(self, proj4=''):
        super(Proj4Validate, self).__init__()

        try:
            self.ImportFromProj4(proj4)
        except Exception:
            pass

        self.check_valid()

class EPSGValidate(GDALValidator):
    """
    GDALValidator subclass for checking EPSG codes
    """
    def __init__(self, epsg=None):
        super(EPSGValidate, self).__init__()

        try:
            self.ImportFromEPSG(epsg)
        except Exception:
            pass

        self.check_valid()
