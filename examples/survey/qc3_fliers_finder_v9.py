import pyximport
pyximport.install()
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

import logging
from PySide2 import QtWidgets

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication()
wid = QtWidgets.QWidget(parent=None)

# options
use_internal_test_files = True
use_internal_csar = True
height_value = None
check_laplacian = False
check_curv = False
check_adjacent = False
check_slivers = False
check_isolated = False
check_edges = False
check_margins = True
filter_designated = False
filter_fff = False
export_proxies = False

prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

if use_internal_test_files:
    # add a grid file
    grid_idx = 0
    if use_internal_csar:
        grid_files = testing.input_test_files(".csar")
    else:
        grid_files = testing.input_test_files(".bag")
    prj.add_to_grid_list(path=grid_files[grid_idx])
    logger.debug("adding test grid file #%d: %s" % (grid_idx, grid_files[grid_idx]))
else:
    prj.add_to_grid_list(r"")

logger.debug(prj)

for grid_path in prj.grid_list:

    logger.debug("grid: %s" % grid_path)
    prj.clear_survey_label()
    prj.open_grid(path=grid_path)

    prj.flier_finder_v9(height=height_value,
                        check_laplacian=check_laplacian,
                        check_curv=check_curv,
                        check_adjacent=check_adjacent,
                        check_slivers=check_slivers,
                        check_isolated=check_isolated,
                        check_edges=check_edges,
                        check_margins=check_margins,
                        filter_fff=filter_fff,
                        filter_designated=filter_designated,
                        export_proxies=export_proxies)
    prj.close_cur_grid()

    prj.set_cur_grid(path=grid_path)
    prj.open_to_read_cur_grid()
    prj.find_fliers_v9_apply_filters()

    saved = prj.save_fliers()
    if saved:
        prj.open_fliers_output_folder()
