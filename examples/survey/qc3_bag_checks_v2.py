import logging

from PySide2 import QtWidgets
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.abc.lib.logging import set_logging

from hyo2.qc.common import testing
from hyo2.qc.survey.project import SurveyProject

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication()
wid = QtWidgets.QWidget(parent=None)

# options
use_internal_test_files = True
use_noaa_nbs_profile: bool = True
check_structure: bool = True
check_metadata: bool = True
check_elevation: bool = True
check_uncertainty: bool = True
check_tracking_list: bool = True
check_gdal_compatibility: bool = True

prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

if use_internal_test_files:
    # add a grid file
    grid_idx = 0
    grid_files = testing.input_test_files(".bag")
    logger.debug("- test BAG files: %d" % len(grid_files))
    logger.debug("- adding test grid file #%d" % grid_idx)
    prj.add_to_grid_list(path=grid_files[grid_idx])
else:
    prj.add_to_grid_list(r"")

prj.bag_checks_v2(use_nooa_nbs_profile=use_noaa_nbs_profile,
                  check_structure=check_structure,
                  check_metadata=check_metadata,
                  check_elevation=check_elevation,
                  check_uncertainty=check_uncertainty,
                  check_tracking_list=check_tracking_list,
                  check_gdal_compatibility=check_gdal_compatibility)

logger.debug(prj.bag_checks_message)
