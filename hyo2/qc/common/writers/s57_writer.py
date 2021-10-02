import logging
import os

from hyo2.abc.lib.helper import Helper
from hyo2.s57.s57 import S57

logger = logging.getLogger(__name__)


class S57Writer:

    @classmethod
    def write_soundings(cls, feature_list, path, list_of_list=False):
        """Feature list as list of long, lat, depth"""

        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("the passed path does not exist: %s" % path)

        path = Helper.truncate_too_long(path)

        if not isinstance(feature_list, list):
            raise RuntimeError("the passed parameter as feature_list is not a list: %s" % type(feature_list))

        s57 = S57()
        s57.create_soundings_file(filename=path, geo3s=feature_list, list_of_list=list_of_list)

    @classmethod
    def write_bluenotes(cls, feature_list, path, list_of_list=True):
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("the passed path does not exist: %s" % path)

        path = Helper.truncate_too_long(path)

        if not isinstance(feature_list, list):
            raise RuntimeError("the passed parameter as feature_list is not a list: %s" % type(feature_list))

        s57 = S57()
        s57.create_blue_notes_file(filename=path, geo2notes=feature_list, list_of_list=list_of_list)

    @classmethod
    def write_tin(cls, feature_list_a, feature_list_b, path, list_of_list=True):
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("the passed path does not exist: %s" % path)

        path = Helper.truncate_too_long(path)

        if not isinstance(feature_list_a, list):
            raise RuntimeError("the passed parameter as feature_list_a is not a list: %s" % type(feature_list_a))

        if not isinstance(feature_list_b, list):
            raise RuntimeError("the passed parameter as feature_list_b is not a list: %s" % type(feature_list_b))

        s57 = S57()
        s57.create_tin_file(filename=path, geo2edges_a=feature_list_a, geo2edges_b=feature_list_b,
                            list_of_list=list_of_list)
