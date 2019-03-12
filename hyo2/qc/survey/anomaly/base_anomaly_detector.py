import logging
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


anomaly_algos = {
    "BASE": 0,
    "ANOMALY_DETECTOR_v1": 1,
}


class BaseAnomalyDetector:

    def __init__(self, grids):
        self.type = anomaly_algos["BASE"]
        # inputs
        self.grids = grids
        # outputs
        self.anomalies = list()
        self.anomalies_xs = list()
        self.anomalies_ys = list()
        self.anomalies_zs = list()
        self.anomalies_cks = list()

    def __repr__(self):
        msg = "  <AnomalyDetector>\n"

        msg += "    <type: %s>\n" % Helper.first_match(anomaly_algos, self.type)
        msg += "    <grids: %s>\n" % bool(self.grids)
        msg += "    <anomalies: %s>\n" % len(self.anomalies)

        return msg
