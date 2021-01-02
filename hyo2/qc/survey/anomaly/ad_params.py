import logging
from typing import Optional
from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.abc.lib.progress.cli_progress import CliProgress
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)

anomaly_algos = {
    "BASE": 0,
    "ANOMALY_DETECTOR_v1": 1,
}


class AnomalyDetectionParams:

    def __init__(self):
        self._type = anomaly_algos["ANOMALY_DETECTOR_v1"]
        self._version = 1

        self._visual_debug = False

        self._progress = CliProgress()
        self._progress_span = 100

        self._write_kml = False
        self._write_shp = False

    @property
    def type(self) -> int:
        return self._type

    @type.setter
    def type(self, value: int) -> None:
        self._type = value

    @property
    def algo(self) -> str:
        return Helper.first_match(anomaly_algos, self.type)

    @algo.setter
    def algo(self, value: str) -> None:
        self._type = anomaly_algos[value]

    @property
    def version(self) -> int:
        return self._version

    @version.setter
    def version(self, value: int) -> None:
        self._version = value

    @property
    def visual_debug(self) -> bool:
        return self._visual_debug

    @visual_debug.setter
    def visual_debug(self, value: bool) -> None:
        self._visual_debug = value

    @property
    def progress(self) -> Optional[AbstractProgress]:
        return self._progress

    @progress.setter
    def progress(self, value: AbstractProgress) -> None:
        self._progress = value

    @property
    def progress_span(self) -> float:
        return self._progress_span

    @progress_span.setter
    def progress_span(self, value: float) -> None:
        self._progress_span = value

    @property
    def write_kml(self) -> bool:
        return self._write_kml

    @write_kml.setter
    def write_kml(self, value: bool) -> None:
        self._write_kml = value

    @property
    def write_shp(self) -> bool:
        return self._write_shp

    @write_shp.setter
    def write_shp(self, value: bool) -> None:
        self._write_shp = value

    def __repr__(self):
        msg = "  <%s>\n" % self.__class__.__name__
        msg += "    <type: %s [v.%d]>\n" % (self.algo, self._version)
        msg += "    <visual debug: %s>\n" % self.visual_debug
        msg += "    <progress: %s>\n" % bool(self.progress)
        msg += "    <progress span: %s>\n" % self.progress_span
        msg += "    <write kml: %s>\n" % self.write_kml
        msg += "    <write shp: %s>\n" % self.write_shp
        return msg
