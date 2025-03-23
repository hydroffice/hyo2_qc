import logging

from PySide2 import QtWidgets
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.abc.lib.logging import set_logging

from hyo2.qc.common import testing
from hyo2.qc.common.grid_callback.qt_grid_callback import QtGridCallback
from hyo2.qc.survey.project import SurveyProject

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication()
wid = QtWidgets.QWidget(parent=None)

# options
use_internal_test_files = True
neighborhood = True
specs = "2016"
survey_scale = 20000

prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))
prj.set_callback(QtGridCallback(progress=prj.progress))

if use_internal_test_files:
    # add a S57 file
    s57_files = testing.input_test_files(".000")
    prj.add_to_s57_list(s57_files[0])
    # add a BAG file
    bag_files = testing.input_test_files(".bag")
    prj.add_to_grid_list(bag_files[0])
else:
    prj.add_to_s57_list(r"")
    prj.add_to_grid_list(r"")

prj.clear_survey_label()
prj.read_feature_file(feature_path=prj.s57_list[0])
prj.open_grid(path=prj.grid_list[0])
prj.designated_scan_v2(survey_scale=survey_scale, neighborhood=neighborhood, specs=specs)
saved = prj.save_designated()
if saved:
    prj.open_designated_output_folder()
