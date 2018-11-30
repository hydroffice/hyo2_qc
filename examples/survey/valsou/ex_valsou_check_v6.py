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
# prj.add_to_s57_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\testing\\survey\\valsou_check\\test1\\H12976_FFF_clip.000")
# prj.add_to_s57_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\data\\survey\\VALSOU Check\\H12881\\H12881_Final_Feature_File.000")
prj.add_to_s57_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\data\\_issues\\VALSOU_Check_8_27_2018\\H13022_FFF.000")
logger.debug(prj)

# add a grid file
# csar_files = testing.input_test_files(".csar")
# print("- CSAR files: %d" % len(csar_files))
# bag_files = testing.input_test_files(".bag")
# print("- BAG files: %d" % len(bag_files))
# prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\testing\\survey\\valsou_check\\test1\\H12976_1m_clip.csar")
# prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\testing\\survey\\valsou_check\\test1\\H12976_1m_clip.bag")
#prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\testing\\survey\\valsou_check\\test1\\H12976_VR_clip.csar")
#prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\testing\\survey\\valsou_check\\test1\\H12976_VR_clip.bag")
# prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\data\\survey\\VALSOU Check\\H12881\\H12881_MB_1m_MLLW_1of5.bag")
# prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\data\\survey\\VALSOU Check\\H12881\\H12881_MB_2m_MLLW_Final.csar")
prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\data\\_issues\\VALSOU_Check_8_27_2018\\H13022_MB_50cm_MLLW_final.csar")
prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\data\\_issues\\VALSOU_Check_8_27_2018\\H13022_MB_1m_MLLW_final.csar")

four_gb = 4294967296
one_mb = 1048576
with_laser = True
survey_scale = 20000
specs_version = "2017"

for s57_file in prj.s57_list:

    logger.debug("s57: %s" % s57_file)
    prj.clear_survey_label()
    prj.read_feature_file(feature_path=s57_file)

    for grid_path in prj.grid_list:
        logger.debug("grid: %s" % grid_path)
        prj.open_grid(path=grid_path, chunk_size=four_gb)
        prj.valsou_check_v6(with_laser=with_laser, survey_scale=survey_scale, specs_version=specs_version)
        prj.valsou_check_deconflict_v6()
        saved_s57 = prj.save_valsou_features()
        if saved_s57:
            prj.open_valsou_output_folder()
