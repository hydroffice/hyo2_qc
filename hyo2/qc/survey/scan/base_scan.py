import logging
from typing import Optional

from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper
from hyo2.abc.app.report import Report
from hyo2.s57.s57 import S57File

logger = logging.getLogger(__name__)

scan_algos = {
    "BASE": 0,
    "FEATURE_SCAN_v7": 7,
    "FEATURE_SCAN_v8": 8,
    "FEATURE_SCAN_v9": 9,
    "FEATURE_SCAN_v10": 10,

}

survey_areas = {
    "Great Lakes": 0,
    "Pacific Coast": 1,
    "Atlantic Coast": 2,
}


class BaseScan:

    def __init__(self, s57: Optional[S57File]) -> None:

        self.type = scan_algos["BASE"]

        # inputs
        self.s57 = s57
        # outputs
        self.flagged_features = [[], [], []]
        # report
        self.report = Report(lib_name=lib_info.lib_name, lib_version=lib_info.lib_version)

    def __repr__(self) -> str:
        msg = "  <BaseScan>\n"

        msg += "    <type: %s>\n" % Helper.first_match(scan_algos, self.type)
        msg += "    <s57: %s>\n" % bool(self.s57)
        msg += "    <flagged features: %s>\n" % len(self.flagged_features)

        return msg
