from __future__ import print_function, absolute_import
import subprocess
import os


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

# retrive the path to the "activate.bat"
activate_file = retrieve_activate_batch()

# script's input variables
grid_path = "C:\\Users\\gmasetti\\Desktop\\test_vr\\Test0_H12280_2806_200kHz_DN149_CalderRice.csar"  # VR
# grid_path = "C:\\Users\\gmasetti\\Desktop\\test_vr\\H12880_MB_1m_MLLW_Final.csar"  # SR
if not os.path.exists(grid_path):
    raise RuntimeError("this path does not exist: %s" % grid_path)
is_vr = "1"
flier_finder = "1"
flier_finder_height = "None"
holiday_finder = "1"
holiday_finder_mode = "OBJECT_DETECTION"  # "FULL_COVERAGE"
grid_qa = "1"
survey_name = "TEST001"

qc_scripts_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "qc_scripts.py"))
if not os.path.exists(qc_scripts_path):
    raise RuntimeError("this path does not exist: %s" % qc_scripts_path)

args = ["cmd.exe", "/K", "set pythonpath=", "&&",  # run shell (/K: leave open (debugging), /C close the shell)
        activate_file, "Pydro36", "&&",  # activate the Pydro36 virtual environment
        "python", qc_scripts_path,  # call the script with a few arguments
            grid_path,  # surface path
            is_vr,  # flag to identify VR vs. SR surfaces
            flier_finder, flier_finder_height,  # flier finder arguments
            holiday_finder, holiday_finder_mode,  # holiday finder arguments
            grid_qa,  # grid QA arguments
            survey_name  # survey name used for output folder (if not None)
        ]

subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
