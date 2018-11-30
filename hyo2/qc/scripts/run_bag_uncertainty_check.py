import pyximport
pyximport.install()
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

from PySide import QtGui, QtCore
import os

from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common.helper import Helper

# set settings

ask_for_input_folder = True
ask_for_output_folder = True
write_report_on_disk = True
open_output_folder = True


# create a Qt application (required to get the dialog to select folders)

app = QtGui.QApplication([])
app.setApplicationName('run_bag_uncertainty_check')
app.setOrganizationName("HydrOffice")
app.setOrganizationDomain("hydroffice.org")

# manage the input folder by asking to user OR using the hand-written path

if ask_for_input_folder:
    # noinspection PyArgumentList
    input_folder = QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption="Select input folder with BAGs",
                                                          dir=QtCore.QSettings().value("run_bag_uncertainty_check_folder"))

    if input_folder == str():
        logger.error("input folder not selected")
        exit(-1)

    QtCore.QSettings().setValue("run_bag_uncertainty_check_folder", input_folder)

else:
    input_folder = "U:\\Working\\QCTools\\scripts"

    if not os.path.exists(input_folder):
        logger.error("input folder does not exist: %s" % input_folder)
        exit(-1)

    if not os.path.isdir(input_folder):
        logger.error("input folder is actually not a folder: %s" % input_folder)
        exit(-1)

logger.debug("input folder: %s" % input_folder)


# create a list with all the BAG paths (walking recursively across the sub-folders, if present)

bag_todo_list = list()
try:   # Trapping Exceptions like OSError (File permissions)
    for root, dirs, files in os.walk(input_folder):

        for file in files:

            if file.lower().endswith(".bag"):
                bag_todo_list.append(os.path.join(root, file))

except Exception as e:
    logger.warning("issue in walking through the input folder: %s" % e)

nr_bag_todo = len(bag_todo_list)
if nr_bag_todo == 0:
    logger.error("not BAG files accessible in the input folder: %s" % input_folder)
    exit(-1)

logger.debug("BAG listed: %d" % nr_bag_todo)


# manage the output folder by asking to user OR using the hand-written path (required to instantiate a SurveyProject)

if ask_for_output_folder:
    # noinspection PyArgumentList
    output_folder = QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption="Select output folder",
                                                           dir=QtCore.QSettings().value("run_bag_uncertainty_check_output_folder"))

    if output_folder == str():
        logger.error("output folder not selected")
        exit(-1)

    QtCore.QSettings().setValue("run_bag_uncertainty_check_output_folder", output_folder)

else:
    output_folder = "U:\\Working\\QCTools\\scripts"

    if not os.path.exists(output_folder):
        logger.error("output folder does not exist: %s" % output_folder)
        exit(-1)

    if not os.path.isdir(output_folder):
        logger.error("output folder is actually not a folder: %s" % output_folder)
        exit(-1)

logger.debug("output folder: %s" % output_folder)


# create the project

prj = SurveyProject(output_folder=output_folder)

# add all the BAG files to the project

for bag_path in bag_todo_list:
    prj.add_to_grid_list(bag_path)


# create 3 empty lists: one for the BAGs successfully processed, one for the ones without Uncertainty lauyer, and another for crashes

bag_done_list = list()
bag_without_uncertainty_list = list()
bag_crash_list = list()

# actually processing the BAG files

for i, bag_path in enumerate(prj.grid_list):

    try:  # Trapping Exceptions like OSError (File permissions)

        logger.debug(">>>>>> #%03d (%s): processing ..." % (i, bag_path))

        prj.clear_survey_label()
        prj.open_grid(path=bag_path)
        prj.retrieve_max_uncert(bag_path)

        max_uncert = prj.retrieve_max_uncert(bag_path)
        # manage the two possible cases of BAG without uncertainty (None or 0.0)
        if max_uncert is None:
            bag_without_uncertainty_list.append(bag_path)
        elif max_uncert == 0.0:
            bag_without_uncertainty_list.append(bag_path)

        bag_done_list.append(bag_path)

        logger.debug(">>>>>> #%03d (%s): OK" % (i, bag_path))

    except Exception as e:
        logger.warning("******  #%03d (%s): issue in processing (%s)" % (i, bag_path, e))
        bag_crash_list.append(bag_path)
        continue


# provide a final report (on screen)

report = str()
report += "- successfully processed: %d/%d\n" % (len(bag_done_list), nr_bag_todo)
report += "\n- processed without uncertainty: %d/%d\n" % (len(bag_without_uncertainty_list), len(bag_done_list))
for bag_without_uncertainty in bag_without_uncertainty_list:
    report += "  . %s\n" % bag_without_uncertainty
report += "\n- crashes while processing: %d/%d\n" % (len(bag_crash_list), nr_bag_todo)
for bag_crash in bag_crash_list:
    report += "  . %s\n" % bag_crash

logger.info("\n%s" % report)


# save on disk a final report

if write_report_on_disk:

    report_path = os.path.join(output_folder, "Uncertainty_Scan_Results.txt")
    try:  # Trapping Exceptions like OSError (File permissions)

        with open(report_path, "w") as fod:
            fod.write(report)

    except Exception as e:
        logger.warning("issue in saving report on disk: %s (%s)" % (report_path, e))


# open the output folder

if open_output_folder:

    Helper.explore_folder(output_folder)


logger.debug("DONE!")
