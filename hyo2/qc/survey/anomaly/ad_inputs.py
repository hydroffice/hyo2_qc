import logging
from typing import Optional
from hyo2.grids.grids_manager import GridsManager

logger = logging.getLogger(__name__)


class AnomalyDetectionInputs:

    def __init__(self):
        self._grid = None

    @property
    def grid(self) -> Optional[GridsManager]:
        return self._grid

    @grid.setter
    def grid(self, value: GridsManager) -> None:
        self._grid = value

    def __repr__(self):
        msg = "  <%s>\n" % self.__class__.__name__
        msg += "    <grid: %s>\n" % (self.grid, )
        return msg
