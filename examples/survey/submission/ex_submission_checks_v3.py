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

# submission folders
sub_folders = testing.input_submission_folders()
logger.debug("testing > submission folders: %d" % len(sub_folders))

# # add folders
# for i, sf in enumerate(sub_folders):
#
#     logger.debug("- %d: %s" % (i, sf))
#
#     try:
#         if prj.is_valid_project_folder(path=sf):
#             prj.add_to_submission_list(sf)
#
#     except Exception as e:
#         logger.warning("Invalid submission folder, %s" % e)

# add 2017 test folder
if prj.is_valid_project_folder(path=sub_folders[-1]):
    prj.add_to_submission_list(sub_folders[-1])

# check folders
logger.debug("project > submission folders: %d" % len(prj.submission_list))

version = "2017"
for i, sf in enumerate(prj.submission_list):
    prj.submission_checks_v3(path=sf, version=version, recursive=True, office=True)
prj.open_submission_output_folder()
