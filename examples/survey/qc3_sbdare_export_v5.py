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
use_internal_test_files = True
do_exif = True
images_folder = None

prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

if use_internal_test_files:
    # add a S57 file
    s57_files = testing.input_test_files(".000")
    prj.add_to_s57_list(s57_files[0])
else:
    prj.add_to_grid_list(r"")

for s57_file in prj.s57_list:

    prj.clear_survey_label()
    prj.read_feature_file(feature_path=s57_file)
    prj.sbdare_export_v5(exif=do_exif, images_folder=images_folder)
    saved_ascii = prj.save_sbdare()
    if saved_ascii:
        prj.open_sbdare_output_folder()

    warnings = prj.sbdare_warnings()
    logger.debug("warnings: %d" % len(warnings))
    for warning in warnings:
        logger.info("- %s" % warning)

