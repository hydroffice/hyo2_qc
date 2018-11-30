from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.chart.project import ChartProject
from hyo2.qc.common import testing
from PySide import QtGui
from hyo2.qc.qctools.qt_progress import QtProgress


app = QtGui.QApplication([])
wid = QtGui.QWidget()

prj = ChartProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add S57 files
s57_files = testing.input_test_files(".000")
logger.info("S57 files: %d" % len(s57_files))
for s57_file in s57_files:

    if "SS" in s57_file:
        prj.add_to_ss_list(s57_file)
    elif "CS" in s57_file:
        pass
    else:
        prj.add_to_s57_list(s57_file)

prj.feature_scan(version=3, specs_version='2016')

logger.debug(prj)
