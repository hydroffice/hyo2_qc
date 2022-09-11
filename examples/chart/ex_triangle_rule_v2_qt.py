import sys
import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.chart.project import ChartProject
from hyo2.qc.chart.triangle.base_triangle import sounding_units
from hyo2.qc.common import testing
from PySide2 import QtWidgets
from hyo2.qc.qctools.qt_progress import QtProgress

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

prj = ChartProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add S57 files

# s57_files = testing.input_test_files(".000")
# logger.info("S57 files: %d" % len(s57_files))
# for s57_file in s57_files:
#
#     if "S57" in s57_file:
#         prj.add_to_s57_list(s57_file)
#     elif "SS" in s57_file:
#         prj.add_to_ss_list(s57_file)
#     else:
#         pass

prj.add_to_s57_list("C:/Users/gmasetti/Google Drive/QC Tools/test data/H12761/Chart_Tab_testing/H12761_H12762_H12763_H12764_H12765_CS.000")
prj.add_to_ss_list("C:/Users/gmasetti/Google Drive/QC Tools/test data/H12761/Chart_Tab_testing/H12761_H12762_H12763_H12764_H12765_SS.000")

use_valsous = True
use_depcnt = True
detect_deeps = False
sounding_units = sounding_units['feet']

prj.triangle_rule(version=2, use_valsou=use_valsous, use_depcnt=use_depcnt, detect_deeps=detect_deeps,
                  sounding_unit=sounding_units)

logger.debug(prj)

sys.exit(app.exec_())
