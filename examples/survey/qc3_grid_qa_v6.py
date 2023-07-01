import pyximport
pyximport.install()
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

from PySide2 import QtWidgets

import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication()
wid = QtWidgets.QWidget(parent=None)

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# options
use_internal_test_files = True
use_internal_csar = True
chunk_size = 4294967296
force_tvu_qc = True
calc_object_detection = False
calc_full_coverage = True
hist_depth = True
hist_density = True
hist_tvu_qc = True
hist_pct_res = True
depth_vs_density = True
depth_vs_tvu_qc = True

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


for grid_path in prj.grid_list:

    prj.clear_survey_label()
    prj.set_cur_grid(path=grid_path)
    prj.open_to_read_cur_grid(chunk_size=chunk_size)

    tvu_qc_layers = prj.cur_grid_tvu_qc_layers()
    if len(tvu_qc_layers) > 0:
        prj.set_cur_grid_tvu_qc_name(tvu_qc_layers[0])

    ret = prj.grid_qa_v6(
        force_tvu_qc=force_tvu_qc,
        calc_object_detection=calc_object_detection, calc_full_coverage=calc_full_coverage,
        hist_depth=hist_depth, hist_density=hist_density, hist_tvu_qc=hist_tvu_qc, hist_pct_res=hist_pct_res,
        depth_vs_density=depth_vs_density, depth_vs_tvu_qc=depth_vs_tvu_qc
    )
    prj.open_gridqa_output_folder()
    logger.info("passed? %s" % ret)
