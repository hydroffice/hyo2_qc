from PySide import QtGui

from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.qctools.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing

app = QtGui.QApplication([])
wid = QtGui.QWidget()

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add a S57 file
s57_files = testing.input_test_files(".000")
print("- S57 files: %d" % len(s57_files))
# prj.add_to_s57_list(s57_files[3])
prj.add_to_s57_list("C:/Users/gmasetti/Google Drive/QC Tools/test data\H12679/testing_feature_scan_v5/feature_testfile_10212016.000")
print("%s" % (prj.s57_list,))
logger.debug(prj)

prj.prf_check(version=1, specs_version='2018')
