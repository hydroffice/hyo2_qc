from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.chart.project import ChartProject
from hyo2.qc.common import testing
from hyo2.qc.common.grid_callback.cli_grid_callback import CliGridCallback
from hyo2.qc.common.grid_callback.qt_grid_callback import QtGridCallback
from PySide import QtGui
from hyo2.qc.qctools.qt_progress import QtProgress


app = QtGui.QApplication([])
wid = QtGui.QWidget()

prj = ChartProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))
prj.set_callback(QtGridCallback(progress=prj.progress))

# input_bag_file = testing.input_test_files('.bag')[1]
# logger.debug('input: %s' % input_bag_file)
# prj.add_to_grid_list(input_bag_file)
#prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\test data\\H12976\\H12976_MB_1m_MLLW_1of2.bag")
# prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\test data\\H12976\\H12976_MB_2m_MLLW_2of2.bag")
# prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\test data\\H12976\\H12976_VR_Test.bag")
prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\test data\\H12871\\H12871_MB_2m_MLLW_combined.bag")

prj.grid_truncate(version=2, decimal_places=1)

logger.debug(prj)
