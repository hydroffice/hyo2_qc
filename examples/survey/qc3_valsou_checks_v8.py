import sys
import logging

from PySide2 import QtWidgets
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.abc.lib.logging import set_logging

from hyo2.qc.common import testing
from hyo2.qc.survey.project import SurveyProject

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication()
wid = QtWidgets.QWidget(parent=None)

# options
use_internal_test_files = False
use_internal_csar = True
with_laser = True
specs_version = "2021"
is_target_detection = False

prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add a S57 file
if use_internal_test_files:
    s57_idx = 0
    s57_files = testing.input_test_files(".000")
    logger.debug("- test S57 files: %d" % len(s57_files))
    logger.debug("- adding test S57 file #%d" % s57_idx)
    prj.add_to_s57_list(s57_path=s57_files[s57_idx])

    # add a grid file
    grid_idx = 0
    if use_internal_csar:
        grid_files = testing.input_test_files(".csar")
        logger.debug("- test CSAR files: %d" % len(grid_files))
    else:
        grid_files = testing.input_test_files(".bag")
        logger.debug("- test BAG files: %d" % len(grid_files))
    logger.debug("- adding test grid file #%d" % grid_idx)
    prj.add_to_grid_list(path=grid_files[grid_idx])

else:
    prj.add_to_s57_list(r"D:\google_drive\_ccom\QC Tools\data\survey\QC Tools 4\VALSOU_Checks\F00879\F00879_FFF.000")
    prj.add_to_grid_list(r"D:\google_drive\_ccom\QC Tools\data\survey\QC Tools 4\VALSOU_Checks\F00879\F00879_MB_50cm_MLLW_Final.csar")


for s57_file in prj.s57_list:

    logger.debug("s57: %s" % s57_file)
    prj.clear_survey_label()
    prj.read_feature_file(feature_path=s57_file)

    for grid_path in prj.grid_list:
        logger.debug("grid: %s" % grid_path)
        prj.open_grid(path=grid_path)
        prj.valsou_check_v8(with_laser=with_laser, specs_version=specs_version, is_target_detection=is_target_detection)
        prj.valsou_check_deconflict()
        saved_s57 = prj.save_valsou_features()
        if saved_s57:
            prj.open_valsou_output_folder()
