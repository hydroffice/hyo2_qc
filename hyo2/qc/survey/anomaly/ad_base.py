import logging
from hyo2.abc.lib.helper import Helper
from hyo2.grids.grids_manager import GridsManager
from hyo2.qc.survey.anomaly.ad_params import AnomalyDetectionParams
from hyo2.qc.survey.anomaly.ad_inputs import AnomalyDetectionInputs
from hyo2.qc.survey.anomaly.ad_outputs import AnomalyDetectionOutputs

logger = logging.getLogger(__name__)


anomaly_algos = {
    "BASE": 0,
    "ANOMALY_DETECTOR_v1": 1,
}


class AnomalyDetectorBase:

    def __init__(self, grid: GridsManager):
        # self.type = anomaly_algos["BASE"]
        # # inputs
        # self.grids = grids
        # # outputs
        # self.anomalies = list()
        # self.anomalies_xs = list()
        # self.anomalies_ys = list()
        # self.anomalies_zs = list()
        # self.anomalies_cks = list()

        self._p = AnomalyDetectionParams()
        self._i = AnomalyDetectionInputs()
        self._i.grid = grid
        self._o = AnomalyDetectionOutputs()

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "%s" % (self._p, )
        msg += "%s" % (self._i, )
        msg += "%s" % (self._o, )
        return msg
