import sys
import logging

from PySide2 import QtWidgets

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# submission folders
sub_folders = [r"C:\code\hyo2\processing\hyo2_qc\data\download\2021\ALL_OK\CARIS-GSF\OPR-A123-RA-20", ]
logger.debug("testing > submission folders: %d" % len(sub_folders))

# add folders
for i, sf in enumerate(sub_folders):

    logger.debug("- %d: %s" % (i, sf))

    try:
        if prj.is_valid_project_folder(path=sf):
            prj.add_to_submission_list(sf)

    except Exception as e:
        logger.warning("Invalid submission folder, %s" % e)

# check folders
logger.debug("project > submission folders: %d" % len(prj.submission_list))

version = "2021"
is_opr = True
office = False
recursive = False
noaa_only = True
for i, sf in enumerate(prj.submission_list):
    prj.submission_checks_v4(path=sf, version=version, recursive=recursive, office=office, opr=is_opr,
                             noaa_only=noaa_only)
prj.open_submission_output_folder()
