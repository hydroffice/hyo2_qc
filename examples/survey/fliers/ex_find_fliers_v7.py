import pyximport
pyximport.install()
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

from PySide import QtGui

from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.qctools.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing


four_gb = 4294967296
one_mb = 1048576

height_value = 0.5
check_laplacian = True
check_curv = True
check_adjacent = True
check_slivers = True
check_isolated = True
check_edges = True

filter_designated = True
filter_fff = True

app = QtGui.QApplication([])
wid = QtGui.QWidget()

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

csar_files = testing.input_test_files(".csar")
logger.debug("test CSAR files: %d" % len(csar_files))
bag_files = testing.input_test_files(".bag")
logger.debug("test BAG files: %d" % len(bag_files))

# prj.add_to_grid_list(csar_files[0])
# prj.add_to_grid_list(bag_files[0])
# prj.add_to_grid_list(r"C:\Users\gmasetti\Google Drive\QC Tools\data\survey\Find Fliers\FFv7_filters\test_finalized.csar")
prj.add_to_grid_list(r"C:\Users\gmasetti\Google Drive\QC Tools\data\survey\Find Fliers\FFv7_filters\test_finalized.bag")
prj.add_to_s57_list(r"C:\Users\gmasetti\Google Drive\QC Tools\data\survey\Find Fliers\FFv7_filters\FFv7_filters.000")

logger.debug("grid list: %s" % (prj.grid_list,))

for i, grid_path in enumerate(prj.grid_list):

    logger.debug(">>> #%d (%s)" % (i, grid_path))

    prj.clear_survey_label()
    prj.set_cur_grid(path=grid_path)
    prj.open_to_read_cur_grid(chunk_size=four_gb)

    prj.find_fliers_v7(height=height_value,
                       check_laplacian=check_laplacian,
                       check_curv=check_curv,
                       check_adjacent=check_adjacent,
                       check_slivers=check_slivers,
                       check_isolated=check_isolated,
                       check_edges=check_edges,
                       filter_fff=filter_fff,
                       filter_designated=filter_designated)
    prj.close_cur_grid()

    prj.set_cur_grid(path=grid_path)
    prj.open_to_read_cur_grid(chunk_size=four_gb)
    prj.find_fliers_v7_apply_filters()

    saved = prj.save_fliers()
    if saved:
        prj.open_fliers_output_folder()

# print project info
logger.debug(prj)
