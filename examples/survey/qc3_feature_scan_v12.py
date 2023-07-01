import logging

from PySide2 import QtWidgets
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.abc.lib.logging import set_logging

from hyo2.qc.common import testing
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.survey.scan.checks import Checks

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication()
wid = QtWidgets.QWidget(parent=None)

# options
use_internal_test_files = True
specs_version = '2021'
use_mhw = True
mhw_value = 4.0
survey_area = Checks.survey_areas["Pacific Coast"]

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

if use_internal_test_files:
    # add a S57 file
    s57_files = testing.input_test_files(".000")
    prj.add_to_s57_list(s57_files[3])
else:
    prj.add_to_grid_list(r"")

prj.feature_scan(specs_version=specs_version,
                 use_mhw=use_mhw, mhw_value=mhw_value,
                 survey_area=survey_area)
