from PySide2 import QtCore, QtWidgets

import os
import logging

from hyo2.qc.common import default_logging
from hyo2.qc.survey.project import SurveyProject
from hyo2.abc.lib.helper import Helper

default_logging.load()
logger = logging.getLogger()

# set settings

ask_for_input_folder = True
ask_for_output_folder = True
# If set to False, height_value can be set by user or calculated like when the GUI is left empty.
calc_min_depth_tvu = True
# If None, and calc_min_depth_tvu is set to false, then height will be automatically calculated.
# If set with float (aka number), then the value is used as threshold.
height_value = None
check_laplacian = False
check_curv = True
check_adjacent = True
check_slivers = True
check_isolated = False
check_edges = False
filter_fff = True
filter_designated = True
out_kml = False
out_shp = False
write_report_on_disk = True
open_output_folder = True

# create a Qt application (required to get the dialog to select folders)

app = QtWidgets.QApplication([])
app.setApplicationName('run_find_fliers_v8')
app.setOrganizationName("HydrOffice")
app.setOrganizationDomain("hydroffice.org")

# manage the input folder by asking to user OR using the hand-written path

if ask_for_input_folder:
    # noinspection PyArgumentList
    input_folder = QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption="Select input folder with BAGs",
                                                              dir=QtCore.QSettings().value("run_ff8_input_folder", ""))

    if input_folder == str():
        logger.error("input folder not selected")
        exit(-1)

    QtCore.QSettings().setValue("run_ff8_input_folder", input_folder)

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
try:  # Trapping Exceptions like OSError (File permissions)
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

# create a list with all the FFF paths (walking recursively across the sub-folders, if present)
fff_todo_list = list()
try:  # Trapping Exceptions like OSError (File permissions)
    for root, dirs, files in os.walk(input_folder):

        for file in files:

            if file.lower().endswith(".000"):
                fff_todo_list.append(os.path.join(root, file))

except Exception as e:
    logger.warning("issue in walking through the input folder: %s" % e)

nr_fff_todo = len(fff_todo_list)
if nr_fff_todo == 0:
    logger.debug("no fff files accessible in the input folder: %s" % input_folder)
    # exit(-1)

logger.debug("FFF listed: %d" % nr_fff_todo)

# manage the output folder by asking to user OR using the hand-written path (required to instantiate a SurveyProject)

if ask_for_output_folder:
    # noinspection PyArgumentList
    output_folder = QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption="Select output folder",
                                                               dir=QtCore.QSettings().value("run_ff8_output_folder",
                                                                                            ""))

    if output_folder == str():
        logger.error("output folder not selected")
        exit(-1)

    QtCore.QSettings().setValue("run_ff8_output_folder", output_folder)

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

# set output settings
prj.output_shp = out_shp
prj.output_kml = out_kml

# add all the BAG files to the project

for bag_path in bag_todo_list:
    prj.add_to_grid_list(bag_path)

# add all FFF files to the project
for fff in fff_todo_list:
    prj.add_to_s57_list(fff)

# create 3 empty lists: one for the BAGs successfully processed, one for the ones with fliers, and another for crashes

bag_done_list = list()
bag_with_fliers_list = list()
bag_crash_list = list()

# actually processing the BAG files
nr_fliers_per_bag_dict = dict()
tvu_height_per_bag_dict = dict()
for i, bag_path in enumerate(prj.grid_list):

    try:  # Trapping Exceptions like OSError (File permissions)

        logger.debug(">>>>>> #%03d (%s): processing ..." % (i, bag_path))

        if calc_min_depth_tvu:
            height_value = prj.retrieve_min_depth_tvu(bag_path)

        prj.clear_survey_label()
        prj.open_grid(path=bag_path)

        prj.find_fliers_v8(height=height_value,
                           check_laplacian=check_laplacian,
                           check_curv=check_curv,
                           check_adjacent=check_adjacent,
                           check_slivers=check_slivers,
                           check_isolated=check_isolated,
                           check_edges=check_edges,
                           filter_designated=filter_designated,
                           filter_fff=filter_fff
                           )

        prj.close_cur_grid()

        prj.open_grid(path=bag_path)
        prj.find_fliers_v8_apply_filters()

        saved = prj.save_fliers()
        if saved:
            bag_with_fliers_list.append(bag_path)
            nr_fliers_per_bag_dict[bag_path] = prj.number_of_fliers()
            tvu_height_per_bag_dict[bag_path] = height_value

        bag_done_list.append(bag_path)

        logger.debug(">>>>>> #%03d (%s): OK" % (i, bag_path))

    except Exception as e:
        logger.warning("******  #%03d (%s): issue in processing (%s)" % (i, bag_path, e))
        bag_crash_list.append(bag_path)
        continue

# provide a final report (on screen)

report = str()
report += "- successfully processed: %d/%d\n" % (len(bag_done_list), nr_bag_todo)
report += "- processed with fliers: %d/%d\n" % (len(bag_with_fliers_list), len(bag_done_list))
if calc_min_depth_tvu is True:
    for bag_with_fliers in bag_with_fliers_list:
        report += ("  . %s, %.3f, %s\n" %
                   (bag_with_fliers, tvu_height_per_bag_dict[bag_with_fliers], nr_fliers_per_bag_dict[bag_with_fliers]))
    report += "- crashes while processing: %d/%d\n" % (len(bag_crash_list), nr_bag_todo)
    for bag_crash in bag_crash_list:
        logger.info("  . %s\n" % bag_crash)
else:
    for bag_with_fliers in bag_with_fliers_list:
        report += ("  . %s, %s\n" %
                   (bag_with_fliers, nr_fliers_per_bag_dict[bag_with_fliers]))
    report += "- crashes while processing: %d/%d\n" % (len(bag_crash_list), nr_bag_todo)
    for bag_crash in bag_crash_list:
        logger.info("  . %s\n" % bag_crash)
logger.info("\n%s" % report)

# save on disk a final report

if write_report_on_disk:

    report_path = os.path.join(output_folder, "Batch_Find_Fliers_Results.txt")
    try:  # Trapping Exceptions like OSError (File permissions)

        with open(report_path, "w") as fod:
            fod.write(report)

    except Exception as e:
        logger.warning("issue in saving report on disk: %s (%s)" % (report_path, e))

# open the output folder

if open_output_folder:
    Helper.explore_folder(output_folder)

logger.debug("DONE!")
