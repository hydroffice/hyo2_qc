import sys
import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing
from PySide2 import QtWidgets
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.common.grid_callback.qt_grid_callback import QtGridCallback

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))
prj.set_callback(QtGridCallback(progress=prj.progress))

# add BAG files
bag_files = testing.input_test_files(".bag")
# logger.info("S57 files: %d" % len(bag_files))
# prj.add_to_grid_list(bag_files[0])
prj.add_to_grid_list(
    r"D:\google_drive\_ccom\QC Tools\data\survey\Test Data for all Tools\H12976_MB_2m_MLLW_2of2.bag")
prj.add_to_s57_list(
    r"D:\google_drive\_ccom\QC Tools\data\survey\Test Data for all Tools\H12976_FFF_Test.000")

four_gb = 4294967296
one_mb = 1048576
specs = "2016"

prj.clear_survey_label()
prj.read_feature_file(feature_path=prj.s57_list[0])
prj.open_grid(path=prj.grid_list[0], chunk_size=four_gb)
prj.designated_scan_v2(survey_scale=20000, neighborhood=True, specs=specs)
saved = prj.save_designated()
if saved:
    prj.open_designated_output_folder()

logger.debug(prj)

# sys.exit(app.exec_())
