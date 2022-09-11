import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.chart.project import ChartProject
from hyo2.qc.common import testing
from PySide2 import QtWidgets
from hyo2.qc.qctools.qt_progress import QtProgress

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

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
