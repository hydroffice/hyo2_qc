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
use_internal_csar = True
sizer = "THREE_TIMES"
mode = "FULL_COVERAGE"  # "ALL_HOLES" "OBJECT_DETECTION"
local_perimeter = True
max_size = 0
pct_min_res = 1.0
visual_debug = True

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

if use_internal_test_files:
    # add a grid file
    grid_idx = 0
    if use_internal_csar:
        grid_files = testing.input_test_files(".csar")
    else:
        grid_files = testing.input_test_files(".bag")
    prj.add_to_grid_list(path=grid_files[grid_idx])
    logger.debug("adding test grid file #%d: %s" % (grid_idx, grid_files[grid_idx]))
else:
    prj.add_to_grid_list(r"")

for grid_path in prj.grid_list:
    prj.clear_survey_label()

    prj.find_holes_v4(path=grid_path, sizer=sizer, mode=mode, local_perimeter=local_perimeter,
                      max_size=max_size, pct_min_res=pct_min_res, visual_debug=visual_debug)
    saved = prj.save_holes()
    if saved:
        prj.open_holes_output_folder()
