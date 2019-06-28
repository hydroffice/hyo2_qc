import logging
from pathlib import Path
from typing import Optional
import numpy as np
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class AnomalyDetectionOutputs:

    def __init__(self):
        self._output_folder = None

    @property
    def output_folder(self) -> Optional[Path]:
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value: Path) -> None:
        self._output_folder = value

    def open_output_folder(self) -> None:
        if self.output_folder:
            Helper.explore_folder(str(self.output_folder))
        else:
            logger.warning('unable to define the output folder to open')

    def __repr__(self):
        msg = "  <%s>\n" % self.__class__.__name__
        msg += "    <output folder: %s>\n" % self.output_folder
        return msg
