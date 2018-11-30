import logging
logger = logging.getLogger(__name__)

from hyo2.qc.common.helper import Helper


fliers_algos = {
    "BASE": 0,
    "FIND_FLIERS_v7": 7,
    "FIND_FLIERS_v8": 8,
}


class BaseFliers:

    def __init__(self, grids):
        self.type = fliers_algos["BASE"]
        # inputs
        self.grids = grids
        # outputs
        self.flagged_fliers = list()
        self.flagged_xs = list()
        self.flagged_ys = list()
        self.flagged_zs = list()
        self.flagged_cks = list()

    def __repr__(self):
        msg = "  <FlierDetector>\n"

        msg += "    <type: %s>\n" % Helper.first_match(fliers_algos, self.type)
        msg += "    <grids: %s>\n" % bool(self.grids)
        msg += "    <possible fliers: %s>\n" % len(self.flagged_fliers)

        return msg

