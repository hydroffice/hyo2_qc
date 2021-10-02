import logging
import math

import numpy as np
from pyproj import Geod

logger = logging.getLogger(__name__)


class Geodesy(object):
    """ A class about geodetic methods and conversions """

    geo = Geod(ellps='WGS84')

    @classmethod
    def convert_to_meter(cls, dist, units):
        """ Helper function that converts the distance in various unit of measure """
        if units.lower() == "m":
            return dist
        elif units.lower() == "km":
            return dist * 0.001
        elif units.lower() == "sm":
            return (dist / 1000) * 0.621371192
        elif units.lower() == "nm":
            return (dist / 1000) * 0.539956803
        else:
            raise RuntimeError("Unknown unit: %s" % units)

    @classmethod
    def haversine(cls, long_1, lat_1, long_2, lat_2):
        """ Calculate the great circle distance between two points on a spherical Earth"""
        # convert decimal degrees to radians
        long_1, lat_1, long_2, lat_2 = map(math.radians, [long_1, lat_1, long_2, lat_2])
        dlon = long_2 - long_1
        dlat = lat_2 - lat_1
        a = math.sin(dlat/2)**2 + math.cos(lat_1) * math.cos(lat_2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371000  # Radius of earth in meters. Use 3956 for miles
        return c * r

    @classmethod
    def distance(cls, long_1, lat_1, long_2, lat_2, units="m"):
        """ Returns distance in 'units' (default m) between two Lat Lon point sets"""
        try:
            _, _, dist = cls.geo.inv(lons1=long_1, lats1=lat_1, lons2=long_2, lats2=lat_2, radians=False)

        except ValueError as e:
            dist = cls.haversine(long_1=long_1, lat_1=lat_1, long_2=long_2, lat_2=lat_2)
            logger.info("%s > switch to Haversine: %s" % (e, dist))

        return cls.convert_to_meter(dist=dist, units=units)

    # degree converions

    @classmethod
    def radians(cls, degrees=0.0, minutes=0.0, seconds=0.0):
        """ Conversion of degrees, minutes and seconds to radians

        Args:
            degrees:            Degrees
            minutes:            Minutes
            seconds:            Seconds
        """
        toggle = False
        if degrees < 0.0:
            toggle = True
            degrees *= -1.0

        if minutes:
            degrees += minutes / cls._arc_minutes(degrees=1.0)
        if seconds:
            degrees += seconds / cls._arc_seconds(degrees=1.0)

        if toggle:
            degrees *= -1.0

        return math.radians(degrees)

    @classmethod
    def _arc_minutes(cls, degrees=0.0, radians=0.0, arc_seconds=0.0):

        if radians:
            degrees += math.degrees(radians)

        if arc_seconds:
            degrees += arc_seconds / cls._arc_seconds(degrees=1.)

        return degrees * 60.0

    @classmethod
    def _arc_seconds(cls, degrees=0.0, radians=0.0, arc_minutes=0.0):
        """
        TODO docs.
        """

        if radians:
            degrees += math.degrees(radians)

        if arc_minutes:
            degrees += arc_minutes / cls._arc_minutes(degrees=1.0)

        return degrees * 3600.0

    @classmethod
    def degrees(cls, radians):
        """ Radians to degree

        Args:
            radians:        Radians
        """

        return math.degrees(radians)

    @classmethod
    def dms2dd(cls, degrees=0.0, minutes=0.0, seconds=0.0):
        """ Convert degree format from DMS to DD

        Args:
            degrees:        Degrees
            minutes:        Minutes
            seconds:        Seconds
        """

        return cls.degrees(cls.radians(degrees, minutes, seconds))

    @classmethod
    def dd2dms(cls, dd):
        """ Convert degree format from DD to DMS """
        toggle = False
        if dd < 0.0:
            dd *= -1
            toggle = True

        degrees = np.floor(dd)
        m = (dd - np.floor(dd)) * 60.0
        minutes = np.floor(m)
        s = (m - np.floor(m)) * 60.0

        if toggle:
            degrees *= -1.0

        return degrees, minutes, s
