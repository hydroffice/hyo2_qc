import pyximport
pyximport.install()
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

import numpy as np
from PySide2 import QtWidgets
import logging
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.common import default_logging
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing

default_logging.load()
logger = logging.getLogger()

four_gb = 4294967296
one_mb = 1048576

height_value = None  # 1.0
check_laplacian = True
check_curv = False
check_adjacent = True
check_slivers = True
check_isolated = True
check_edges = True

filter_designated = False
filter_fff = True

export_proxies = True
export_heights = True
export_curvatures = True

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

csar_files = testing.input_test_files(".csar")
logger.debug("test CSAR files: %d" % len(csar_files))
# bag_files = testing.input_test_files(".bag")
# logger.debug("test BAG files: %d" % len(bag_files))

prj.add_to_grid_list(csar_files[0])
# prj.add_to_grid_list(bag_files[1])
# prj.add_to_grid_list(r"C:\Users\gmasetti\Google Drive\QC Tools\data\survey\Find Fliers\FFv7_filters\
# test_finalized.csar")
# prj.add_to_grid_list(r"C:\Users\gmasetti\Google Drive\QC Tools\data\survey\Find Fliers\FFv7_filters\
# test_finalized.bag")
# prj.add_to_grid_list(r"C:\Users\gmasetti\Google Drive\QC Tools\test_data_vr_do.not.use\
# Test0_H12280_2806_200kHz_DN149_CalderRice.bag")
# prj.add_to_grid_list(r"C:\Users\gmasetti\Google Drive\QC Tools\test_data_vr_do.not.use\
# Test0_H12280_2806_200kHz_DN149_CalderRice.csar")
# prj.add_to_grid_list(r"C:\Users\gmasetti\Google Drive\QC Tools\data\survey\Find Fliers\VR_Test\
# H13015_MB_VR_MLLW_Final_Extracted_8_tiles.csar")
# prj.add_to_s57_list(r"C:\Users\gmasetti\Google Drive\QC Tools\data\survey\Find Fliers\FFv7_filters\FFv7_filters.000")

logger.debug("grid list: %s" % (prj.grid_list,))

prev = None

for j in range(1):
    for i, grid_path in enumerate(prj.grid_list):
        logger.debug(">>> #%d (%s)" % (i, grid_path))

        prj.clear_survey_label()
        prj.set_cur_grid(path=grid_path)
        prj.open_to_read_cur_grid(chunk_size=four_gb)

        prj.detect_anomalies_v1(height=height_value,
                                check_laplacian=check_laplacian,
                                check_curv=check_curv,
                                check_adjacent=check_adjacent,
                                check_slivers=check_slivers,
                                check_isolated=check_isolated,
                                check_edges=check_edges,
                                filter_fff=filter_fff,
                                filter_designated=filter_designated,
                                export_proxies=export_proxies,
                                export_heights=export_heights,
                                export_curvatures=export_curvatures)
        prj.close_cur_grid()

        prj.set_cur_grid(path=grid_path)
        prj.open_to_read_cur_grid(chunk_size=four_gb)
        prj.detect_anomalies_v1_apply_filters()

        # saved = prj.save_anomalies()
        # prj.open_anomalies_output_folder()
        #
        # if prev is not None:
        #     diff = prev - prj._anomaly.ths.median
        #     from matplotlib import pyplot as plt
        #     plt.figure("diff")
        #     m = plt.imshow(diff, interpolation='none')
        #     plt.colorbar(m)
        #     plt.show()
        #
        # if prj._anomaly.ths is not None:
        #     prev = np.copy(prj._anomaly.ths.median)

# print project info
logger.debug(prj)
