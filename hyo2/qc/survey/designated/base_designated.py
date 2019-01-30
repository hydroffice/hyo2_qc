import logging

from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)

designated_algos = {
    "BASE": 0,
    "DESIGNATED_SCAN_v2": 1,
}


class BaseDesignated:

    def __init__(self, s57, grids):
        self.type = designated_algos["BASE"]
        # inputs
        self.s57 = s57
        self.grids = grids
        # outputs
        self.flagged_designated = [[], [], []]

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "    <type: %s>\n" % Helper.first_match(designated_algos, self.type)
        msg += "    <grids: %s>\n" % bool(self.grids)
        msg += "    <flagged designated: %s>\n" % len(self.flagged_designated)

        return msg
