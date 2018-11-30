from hyo2.qc.common import default_logging
import sys
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing
from PySide import QtGui
from hyo2.qc.qctools.qt_progress import QtProgress


app = QtGui.QApplication([])
wid = QtGui.QWidget()

prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add a S57 file
# s57_files = testing.input_test_files(".000")
# print("- S57 files: %d" % len(s57_files))
# prj.add_to_s57_list(s57_files[0])
# prj.add_to_s57_list(s57_files[1])
# prj.add_to_s57_list(s57_files[2])
# prj.add_to_s57_list(s57_files[3])
prj.add_to_s57_list("C:\\Users\\gmasetti\\Google Drive\\CMECS Crosswalk Automation\\Input\\H12895_FFF.000")
print("%s" % (prj.s57_list,))
logger.debug(prj)

for s57_file in prj.s57_list:
    prj.clear_survey_label()
    prj.read_feature_file(feature_path=s57_file)
    prj.sbdare_export_v3()
    saved_ascii = prj.save_sbdare()
    if saved_ascii:
        prj.open_sbdare_output_folder()
