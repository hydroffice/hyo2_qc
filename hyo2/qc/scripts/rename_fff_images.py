import logging
import os

from PySide2 import QtCore, QtWidgets
from hyo2.qc.common import default_logging

from hyo2.abc.lib.helper import Helper

default_logging.load()
logger = logging.getLogger()

# set settings

ask_for_input_folder = True
ask_for_multimedia_folder = True
ask_for_output_folder = True
open_output_folder = True

# create a Qt application (required to get the dialog to select folders)

app = QtWidgets.QApplication([])
app.setApplicationName('run_find_fliers_v6')
app.setOrganizationName("HydrOffice")
app.setOrganizationDomain("hydroffice.org")

# manage the input folder by asking to user OR using the hand-written path

if ask_for_input_folder:
    # noinspection PyArgumentList
    input_folder = QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption="Select input folder with S57 file",
                                                              dir=QtCore.QSettings().value("rename_fff_images_folder"))

    if input_folder == str():
        logger.error("input folder not selected")
        exit(-1)

    QtCore.QSettings().setValue("rename_fff_images_folder", input_folder)

else:
    input_folder = "U:\\Working\\QCTools\\scripts"

    if not os.path.exists(input_folder):
        logger.error("input folder does not exist: %s" % input_folder)
        exit(-1)

    if not os.path.isdir(input_folder):
        logger.error("input folder is actually not a folder: %s" % input_folder)
        exit(-1)

logger.debug("input folder: %s" % input_folder)

# manage the input multimedia folder by asking to user OR using the hand-written path

if ask_for_multimedia_folder:
    # noinspection PyArgumentList
    input_multimedia_folder = QtWidgets.QFileDialog.getExistingDirectory(parent=None,
                                                                         caption="Select input Multimedia folder",
                                                                         dir=QtCore.QSettings().value(
                                                                             "input_multimedia_folder"))

    if input_multimedia_folder == str():
        logger.error("input multimedia folder not selected")
        exit(-1)

    QtCore.QSettings().setValue("input_multimedia_folder", input_multimedia_folder)

else:
    input_multimedia_folder = "U:\\Working\\QCTools\\scripts"

    if not os.path.exists(input_multimedia_folder):
        logger.error("input folder does not exist: %s" % input_multimedia_folder)
        exit(-1)

    if not os.path.isdir(input_multimedia_folder):
        logger.error("input folder is actually not a folder: %s" % input_multimedia_folder)
        exit(-1)

logger.debug("input folder: %s" % input_multimedia_folder)

# manage the output folder by asking to user OR using the hand-written path (required to instantiate a SurveyProject)

if ask_for_output_folder:
    # noinspection PyArgumentList
    output_folder = QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption="Select output folder",
                                                               dir=QtCore.QSettings().value("rename_fff_images_folder"))

    if output_folder == str():
        logger.error("output folder not selected")
        exit(-1)

    QtCore.QSettings().setValue("rename_fff_images_folder", output_folder)

else:
    output_folder = "U:\\Working\\QCTools\\scripts"

    if not os.path.exists(output_folder):
        logger.error("output folder does not exist: %s" % output_folder)
        exit(-1)

    if not os.path.isdir(output_folder):
        logger.error("output folder is actually not a folder: %s" % output_folder)
        exit(-1)

logger.debug("output folder: %s" % output_folder)


# select all features with images
def check_features_for_attribute(objects, attribute):
    """Check if the passed features have the passed attribute"""
    features_with_images = list()
    features_without_images = list()

    for obj in objects:
        # do the test
        has_attribute = False
        for attr in obj.attributes:
            if attr.acronym == attribute:
                has_attribute = True

        # check passed
        if has_attribute:
            return features_with_images
        else:
            return features_without_images


# open the output folder

if open_output_folder:
    Helper.explore_folder(output_folder)

logger.debug("DONE!")
