import logging

from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)

qa_algos = {
    "BASE": 0,
    "GRID_QA_v5": 5,
    "GRID_QA_v6": 6,
}


class BaseGridQA:
    def __init__(self, grids):
        self.type = qa_algos["BASE"]
        # inputs
        self.grids = grids

    def __repr__(self):
        msg = "  <BaseGridQA>\n"

        msg += "    <type: %s>\n" % Helper.first_match(qa_algos, self.type)
        msg += "    <grids: %s>\n" % bool(self.grids)

        return msg

