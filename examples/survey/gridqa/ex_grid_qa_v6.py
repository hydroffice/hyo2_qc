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
logger = logging.getLogger(__name__)

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add a CSAR file
# csar_files = testing.input_test_files(".csar")
# print("- CSAR files: %d" % len(csar_files))

# add a BAG file
bag_files = testing.input_test_files(".bag")
print("- BAG files: %d" % len(bag_files))

kluster_file = r"C:\code\kluster\kluster\test_data\srgrid_mean_auto_depth_20211127_201258"
prj.add_to_grid_list(kluster_file)

# prj.add_to_grid_list(csar_files[0])
# prj.add_to_grid_list(csar_files[1])
# prj.add_to_grid_list(bag_files[0])
# prj.add_to_grid_list(bag_files[1])
# prj.add_to_grid_list(bag_files[2])
# prj.add_to_grid_list(csar_file)
print("%s" % (prj.grid_list,))

four_gb = 4294967296
one_mb = 1048576

force_tvu_qc = True

calc_object_detection = False
calc_full_coverage = True

hist_depth = True
hist_density = True
hist_tvu_qc = True
hist_pct_res = True

depth_vs_density = True
depth_vs_tvu_qc = True


for grid_path in prj.grid_list:

    prj.clear_survey_label()
    prj.set_cur_grid(path=grid_path)
    prj.open_to_read_cur_grid(chunk_size=four_gb)

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
    print("passed? %s" % ret)

# print project info
logger.debug(prj)
