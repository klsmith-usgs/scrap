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
        err_msg = {1: 'OGRERR_NOT_ENOUGH_DATA',
                   2: 'OGRERR_NOT_ENOUGH_MEMORY',
                   3: 'OGRERR_UNSUPPORTED_GEOMETRY_TYPE',
                   4: 'OGRERR_UNSUPPORTED_OPERATION',
                   5: 'OGRERR_CORRUPT_DATA',
                   6: 'OGRERR_FAILURE',
                   7: 'OGRERR_UNSUPPORTED_SRS',
                   8: 'OGRERR_INVALID_HANDLE',
                   9: 'OGRERR_NON_EXISTING_FEATURE'}

        if num in err_msg.keys():
            return err_msg[num]
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
