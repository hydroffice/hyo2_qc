import logging

from hyo2.qc.common import lib_info
from hyo2.qc.common.helper import Helper
from hyo2.qc.common.report import Report

logger = logging.getLogger(__name__)

triangle_algos = {
    "BASE": 0,
    "TRIANGLE_RULE_v2": 1,
}

sounding_units = {
    "feet": 0,
    "meters": 1,
    "fathoms": 2,
}


class BaseTriangle:
    def __init__(self, ss, s57, cs, sounding_unit, progress=None):
        self.type = triangle_algos["BASE"]
        # inputs
        self.ss = ss
        self.cs = cs
        self.s57 = s57
        # criteria
        self.csu = sounding_unit
        # outputs
        self.flagged_features = [[], [], []]
        # report
        self.report = Report(lib_name=lib_info.lib_name, lib_version=lib_info.lib_version)
        # progress bar
        self.progress = progress

    def __repr__(self):
        msg = "  <ChartBaseTriangle>\n"

        msg += "    <type: %s>\n" % Helper.first_match(triangle_algos, self.type)
        msg += "    <ss: %s>\n" % bool(self.ss)
        msg += "    <s57: %s>\n" % bool(self.s57)
        msg += "    <cs: %s>\n" % bool(self.cs)
        msg += "    <flagged features: %s>\n" % len(self.flagged_features)

        return msg
