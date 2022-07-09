import logging

from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


fliers_algos = {
    "BASE": 0,
    "FIND_FLIERS_v9": 9,
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
