from __future__ import print_function, absolute_import

import os
import subprocess

try:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtWidgets import QFileDialog, QApplication
except ImportError:
    from PySide import QtCore, QtGui
    from PySide.QtGui import QFileDialog, QApplication

ask_for_input_file = False

# create a Qt application (required to get the dialog to select folders)

app = QApplication([])
app.setApplicationName('run_bag_uncertainty_check')
app.setOrganizationName("HydrOffice")
app.setOrganizationDomain("hydroffice.org")

# manage the input folder by asking to user OR using the hand-written path

if ask_for_input_file:
    # noinspection PyArgumentList
    input_file, _ = QFileDialog.getOpenFileName(parent=None, caption="Select input grid file",
                                                dir=QtCore.QSettings().value("ex_qc_scripts"),
                                                filter="BAG (*.bag *.BAG);;CSAR (*.csar *.CSAR);;All files (*.*)")

    if input_file == str():
        print("input file not selected")
        exit(-1)

    QtCore.QSettings().setValue("ex_qc_scripts", os.path.dirname(input_file))

else:
    input_file = r"C:\Users\gmasetti\Google Drive\QC Tools\data\survey\QuickTest.bag"

    if not os.path.exists(input_file):
        print("input file does not exist: %s" % input_file)
        exit(-1)

    if os.path.isdir(input_file):
        print("input file is actually a folder: %s" % input_file)
        exit(-1)

print("input file: %s" % input_file)

flier_finder = "1"
flier_finder_height = "None"
holiday_finder = "1"
holiday_finder_mode = "OBJECT_DETECTION"  # "FULL_COVERAGE"
grid_qa = "1"
survey_name = "TEST001"

# helper function to retrieve the path to the NOAA folder in PydroXL
def retrieve_noaa_folder_path():

    from HSTB import __file__
    folder_path = os.path.realpath(os.path.dirname(__file__))
    if not os.path.exists(folder_path):
        raise RuntimeError("the folder does not exist: %s" % folder_path)
    print("NOAA folder: %s" % folder_path)
    return folder_path


# helper function to retrieve the install prefix path for PydroXL
def retrieve_install_prefix():

    noaa_folder = retrieve_noaa_folder_path()
    folder_path = os.path.realpath(os.path.join(noaa_folder, os.pardir, os.pardir, os.pardir, os.pardir))
    if not os.path.exists(folder_path):
        raise RuntimeError("the folder does not exist: %s" % folder_path)
    print("install prefix: %s" % folder_path)
    return folder_path


# helper function to retrieve the path to the "Scripts" folder in PydroXL
def retrieve_scripts_folder():

    install_prefix = retrieve_install_prefix()
    folder_path = os.path.realpath(os.path.join(install_prefix, "Scripts"))
    if not os.path.exists(folder_path):
        raise RuntimeError("the folder does not exist: %s" % folder_path)
    print("scripts folder: %s" % folder_path)
    return folder_path


# helper function to retrieve the path to the "activate.bat" batch file in PydroXL
def retrieve_activate_batch():

    scripts_prefix = retrieve_scripts_folder()
    file_path = os.path.realpath(os.path.join(scripts_prefix, "activate.bat"))
    if not os.path.exists(file_path):
        raise RuntimeError("the file does not exist: %s" % file_path)
    print("activate batch file: %s" % file_path)
    return file_path

# retrieve the path to the "activate.bat"
activate_file = retrieve_activate_batch()

qc_scripts_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "qc_scripts.py"))
if not os.path.exists(qc_scripts_path):
    raise RuntimeError("this path does not exist: %s" % qc_scripts_path)

args = ["cmd.exe", "/K", "set pythonpath=", "&&",  # run shell (/K: leave open (debugging), /C close the shell)
        activate_file, "Pydro367", "&&",  # activate the Pydro367 virtual environment
        "python", qc_scripts_path,  # call the script with a few arguments
        '"' + input_file.replace("&", "^&") + '"',  # surface path
        flier_finder, flier_finder_height,  # flier finder arguments
        holiday_finder, holiday_finder_mode,  # holiday finder arguments
        grid_qa,  # grid QA arguments
        survey_name  # survey name used for output folder (if not None)
       ]

print("args: %s" % (args, ))

qc_env = os.environ.copy()
valid_paths = list()
# print(qc_env['PATH'])
for token in qc_env['PATH'].split(";"):
    if "Pydro27" not in token:
        valid_paths.append(token)
qc_env['PATH'] = ";".join(valid_paths)
print(qc_env['PATH'])

subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE, env=qc_env)
