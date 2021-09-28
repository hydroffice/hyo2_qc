import pyximport
pyximport.install()
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

from PySide2 import QtWidgets

from hyo2.qc.common import default_logging
import logging

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing

default_logging.load()
logger = logging.getLogger()

four_gb = 4294967296
one_mb = 1048576

height_value = None
check_laplacian = False
check_curv = False
check_adjacent = True
check_slivers = True
check_isolated = True
check_edges = False

filter_designated = False
filter_fff = False

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# csar_files = testing.input_test_files(".csar")
# logger.debug("test CSAR files: %d" % len(csar_files))
# prj.add_to_grid_list(csar_files[0])

# bag_files = testing.input_test_files(".bag")
# logger.debug("test BAG files: %d" % len(bag_files))
# prj.add_to_grid_list(bag_files[0])

# bag_file = r"C:\Users\gmasetti\Documents\kluster\test\srgrid_mean_auto_20210926_145921\export_8.0_1.bag"
# prj.add_to_grid_list(bag_file)

kluster_file = r"C:\Users\gmasetti\Documents\kluster\test\srgrid_mean_auto_20210926_145921"
prj.add_to_grid_list(kluster_file)

logger.debug("grid list: %s" % (prj.grid_list,))

for i, grid_path in enumerate(prj.grid_list):

    logger.debug(">>> #%d (%s)" % (i, grid_path))

    prj.clear_survey_label()
    prj.set_cur_grid(path=grid_path)
    prj.open_to_read_cur_grid(chunk_size=four_gb)

    prj.find_fliers_v8(height=height_value,
                       check_laplacian=check_laplacian,
                       check_curv=check_curv,
                       check_adjacent=check_adjacent,
                       check_slivers=check_slivers,
                       check_isolated=check_isolated,
                       check_edges=check_edges,
                       filter_fff=filter_fff,
                       filter_designated=filter_designated,
                       export_proxies=False)
    prj.close_cur_grid()

    prj.set_cur_grid(path=grid_path)
    prj.open_to_read_cur_grid(chunk_size=four_gb)
    prj.find_fliers_v8_apply_filters()

    saved = prj.save_fliers()
    if saved:
        prj.open_fliers_output_folder()

# print project info
logger.debug(prj)
