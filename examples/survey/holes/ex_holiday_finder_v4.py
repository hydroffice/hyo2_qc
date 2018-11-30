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

# # add a CSAR file
# csar_files = testing.input_test_files(".csar")
# print("- CSAR files: %d" % len(csar_files))
#
# # add a BAG file
# bag_files = testing.input_test_files(".bag")
# print("- BAG files: %d" % len(bag_files))

# prj.add_to_grid_list(csar_files[0])
# prj.add_to_grid_list(bag_files[0])
# prj.add_to_grid_list("V:/CARIS_VR/H12880/Surfaces/H12880_2806_2016DN149_Ranges_CUBE.csar")
# prj.add_to_grid_list("V:/CARIS_VR/H12880/Surfaces/H12880_10_1_0_Ranges_CUBE_Final.csar")
# prj.add_to_grid_list("V:/CARIS_VR/H12880/Surfaces/Test0_H12280_2806_200kHz_DN149_CalderRice.csar")
prj.add_to_grid_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\data\\_issues\\H13034_Holiday_Finder_Issue_4_23_2018\\H13034_MB_2m_MLLW_Final.csar")
print("%s" % (prj.grid_list,))

#four_gb = 4294967296
# one_mb = 1048576
#
for grid_path in prj.grid_list:
    prj.clear_survey_label()

    # v4
    prj.find_holes_v4(path=grid_path, sizer="THREE_TIMES", mode="FULL_COVERAGE", local_perimeter=True,
                      max_size=0, pct_min_res=1.0, visual_debug=False)
    # prj.find_holes_v2(mode="ALL_HOLES")
    # prj.find_holes_v2(mode="OBJECT_DETECTION")
    saved = prj.save_holes()
    if saved:
        prj.open_holes_output_folder()

# print project info
logger.debug(prj)
