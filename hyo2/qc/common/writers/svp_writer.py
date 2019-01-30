import os
from datetime import datetime
import logging

from hyo2.qc.common.geodesy import Geodesy as Gd
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class SvpWriter:

    @classmethod
    def write(cls, feature_list, path):
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("the passed path does not exist: %s" % path)

        path = Helper.truncate_too_long(path)

        if not isinstance(feature_list, list):
            raise RuntimeError("the passed parameter as feature_list is not a list: %s" % type(feature_list))

        # generating header
        header = str()
        header += "[SVP_VERSION_2]\n"
        header += "%s\n" % path

        # generating body
        body = str()
        date_string = "%s" % datetime.now().strftime("%Y-%j %H:%M:%S")
        for m, ft in enumerate(feature_list):

            dd_lon = ft[0]
            dd_lat = ft[1]
            lon_d, lon_m, lon_s = Gd.dd2dms(dd_lon)
            lat_d, lat_m, lat_s = Gd.dd2dms(dd_lat)

            position_string = "{0:02d}:{1:02d}:{2:05.2f} {3:02d}:{4:02d}:{5:05.2f}".format(int(lat_d), int(lat_m),
                                                                                           lat_s, int(lon_d),
                                                                                           int(lon_m), lon_s)

            body += "Section " + date_string + " " + position_string + " Created by hyo2.qc\n"
            body += "    1.00    1500.00\n"
            body += "    15.00   1500.00\n"

        # open the file for writing
        with open(path, 'w') as fid:
            fid.write(header + body)
