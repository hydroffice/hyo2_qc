from PySide2 import QtWidgets

from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

# create the project
prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add a CSAR file
csar_files = testing.input_test_files(".csar")
# print("- CSAR files: %d" % len(csar_files))

# add a BAG file
bag_files = testing.input_test_files(".bag")
# print("- BAG files: %d" % len(bag_files))

prj.add_to_grid_list(csar_files[0])
# prj.add_to_grid_list(csar_files[1])
prj.add_to_grid_list(bag_files[0])
prj.add_to_grid_list(bag_files[1])
prj.add_to_grid_list(bag_files[2])
logger.debug("%s" % (prj.grid_list,))

use_nooa_ocs_profile: bool = True
check_structure: bool = True
check_metadata: bool = True
check_elevation: bool = True
check_uncertainty: bool = True
check_tracking_list: bool = True

prj.bag_checks_v1(use_nooa_ocs_profile=use_nooa_ocs_profile,
                  check_structure=check_structure,
                  check_metadata=check_metadata,
                  check_elevation=check_elevation,
                  check_uncertainty=check_uncertainty,
                  check_tracking_list=check_tracking_list)

logger.debug(prj.bag_checks_message)
