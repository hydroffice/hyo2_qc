from PySide2 import QtWidgets

from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing
from hyo2.qc.survey.scan.base_scan import survey_areas

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add a S57 file
s57_files = testing.input_test_files(".000")
print("- S57 files: %d" % len(s57_files))
prj.add_to_s57_list(s57_files[3])
# prj.add_to_s57_list("C:/Users/gmasetti/Google Drive/QC Tools/data/survey/feature_scan/H12971_FFF_Field_2018.000")
# prj.add_to_s57_list("C:/Users/gmasetti/Google Drive/QC Tools/test data/2018_HSSD_Test/H12971_FFF_Office_2018Test.000")
print("%s" % (prj.s57_list,))
logger.debug(prj)

prj.feature_scan(version=10, specs_version='2020', use_mhw=True, mhw_value=4.0,
                 survey_area=survey_areas["Pacific Coast"])
