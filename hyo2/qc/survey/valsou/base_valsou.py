import logging

from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper
from hyo2.abc.app.report import Report

logger = logging.getLogger(__name__)

valsou_algos = {
    "BASE": 0,
    "VALSOU_CHECK_v6": 1,
    "VALSOU_CHECK_v7": 2,
}

specs_vers = {
    "BASE": 0,
    "2015": 1,
    "2016": 2,
    "2017": 3,
    "2018": 4,
}


class BaseValsou:
    def __init__(self, s57, grids):
        self.type = valsou_algos["BASE"]
        self.version = specs_vers["BASE"]
        # inputs
        self.s57 = s57
        # inputs
        self.grids = grids
        # outputs
        self.flagged_features = list()
        # report
        self.report = Report(lib_name=lib_info.lib_name, lib_version=lib_info.lib_version)

    def __repr__(self):
        msg = "  <BaseValsou>\n"

        msg += "    <type: %s>\n" % Helper.first_match(valsou_algos, self.type)
        msg += "    <s57: %s>\n" % bool(self.s57)
        msg += "    <grids: %s>\n" % bool(self.grids)
        msg += "    <flagged features: %s>\n" % len(self.flagged_features)

        return msg
