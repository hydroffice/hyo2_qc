import logging
import os
import time
import traceback
from datetime import datetime
from typing import Optional, List

import numpy as np
from hyo2.abc.app.report import Report
from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.abc.lib.progress.cli_progress import CliProgress
from hyo2.bag import bag
from hyo2.qc import name as lib_name, __version__ as lib_version
from hyo2.qc.common.project import BaseProject
from osgeo import osr

logger = logging.getLogger(__name__)


class BagChecksV2:

    def __init__(self, grid_list: List[str], output_folder: str,
                 output_project_folder: bool, output_subfolders: bool,
                 use_nooa_nbs_profile: bool = False, check_structure: bool = False,
                 check_metadata: bool = False, check_elevation: bool = False,
                 check_uncertainty: bool = False, check_tracking_list: bool = False,
                 check_gdal_compatibility: bool = False,
                 progress: AbstractProgress = CliProgress(), open_output_folder: bool = True):

        self.grid_list = grid_list
        self.output_folder = output_folder
        self.output_project_folder = output_project_folder
        self.output_subfolders = output_subfolders
        self.open_output_folder = open_output_folder

        self._noaa_nbs_profile = use_nooa_nbs_profile
        self._structure = check_structure
        self._metadata = check_metadata
        self._elevation = check_elevation
        self._uncertainty = check_uncertainty
        self._tracking_list = check_tracking_list
        self._gdal_compatibility = check_gdal_compatibility

        self._msg = str()
        self._bc_structure_errors = 0  # type: int
        self._bc_structure_warnings = 0  # type: int
        self._bc_metadata_errors = 0  # type: int
        self._bc_metadata_warnings = 0  # type: int
        self._bc_elevation_errors = 0  # type: int
        self._bc_elevation_warnings = 0  # type: int
        self._bc_uncertainty_errors = 0  # type: int
        self._bc_uncertainty_warnings = 0  # type: int
        self._bc_tracking_list_errors = 0  # type: int
        self._bc_tracking_list_warnings = 0  # type: int
        self._bc_gdal_compatibility_errors = 0  # type: int
        self._bc_gdal_compatibility_warnings = 0  # type: int
        self._bc_report = None
        self._bc_pdf = str()
        self._cur_min_depth = None  # type: Optional[float]
        self._cur_max_depth = None  # type: Optional[float]
        self._cur_vr_min_depth = None  # type: Optional[float]
        self._cur_vr_max_depth = None  # type: Optional[float]

        self.progress = progress

        self._is_vr = False
        self._survey = str()
        self._grid_basename = str()

    @property
    def msg(self) -> str:
        return self._msg

    def run(self):
        self.progress.start(title="BAG Checks v2", text="Loading")

        if not self._structure and not self._metadata and not self._elevation and not self._uncertainty \
                and not self._tracking_list:
            raise RuntimeError('At least one check needs to be selected')

        logger.info('BAG Checks v2 -> Structure: %s, Metadata: %s, Elevation: %s, Uncertainty: %s, Tracking List: %s'
                    % (self._structure, self._metadata, self._elevation, self._uncertainty,
                       self._tracking_list))

        if self._noaa_nbs_profile:
            logger.info('Using the NOAA NBS profile')
        else:
            logger.info('Using the general profile')

        # Check if the grid list is empty
        if len(self.grid_list) == 0:
            raise RuntimeError("The grid list is empty")

        try:
            start_time = time.time()

            # for each file in the project grid list
            self._msg = "Checks results per input:\n"
            opened_folders = list()

            nr_of_files = len(self.grid_list)
            for i, grid_file in enumerate(self.grid_list):

                self._cur_min_depth = None
                self._cur_max_depth = None
                self._cur_vr_min_depth = None
                self._cur_vr_max_depth = None
                success = self._bag_checks_v2(grid_file=grid_file, idx=i, total=nr_of_files)

                if success:
                    if self.cur_bag_checks_passed:
                        self._msg += "- %s: pass\n" % self._grid_basename
                    else:
                        self._msg += "- %s: fail\n" % self._grid_basename

                    if self.open_output_folder:
                        # open the output folder (if not already open)
                        if self.bagchecks_output_folder not in opened_folders:
                            self.open_bagchecks_output_folder()
                            opened_folders.append(self.bagchecks_output_folder)
                else:
                    self._msg += "- %s: skip\n" % self._grid_basename

            logger.info("BAG Checks v2 -> execution time: %.3f s" % (time.time() - start_time))

        except Exception as e:
            traceback.print_exc()
            self._msg = None
            self.progress.end()
            raise e

        self.progress.end()

    def _bag_checks_v2(self, grid_file: str, idx: int, total: int) -> bool:

        quantum = 100.0 / total
        cur_quantum = quantum * idx

        self.progress.update(value=cur_quantum + quantum * 0.05, text="[%d/%d] File opening" % (idx + 1, total))

        # we want to be sure that the label is based on the name of the new file input
        self._survey = BaseProject.make_survey_label_from_path(grid_file)
        self._grid_basename = os.path.splitext(os.path.basename(grid_file))[0]

        # skip CSAR
        if not bag.BAGFile.is_bag(bag_path=grid_file):  # skip CSAR
            logger.debug('not a BAG file: %s' % grid_file)
            return False

        self._is_vr = bag.BAGFile.is_vr(bag_path=grid_file)
        if self._is_vr:
            logger.debug('detected VR BAG')

        self._bc_report = Report(lib_name=lib_name, lib_version=lib_version)

        self.progress.update(value=cur_quantum + quantum * 0.15, text="[%d/%d] Structure checking" % (idx + 1, total))

        self._bag_checks_v2_structure(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.3, text="[%d/%d] Metadata checking" % (idx + 1, total))

        self._bag_checks_v2_metadata(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.5, text="[%d/%d] Elevation checking" % (idx + 1, total))

        self._bag_checks_v2_elevation(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.7, text="[%d/%d] Uncertainty checking" % (idx + 1, total))

        self._bag_checks_v2_uncertainty(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.85,
                             text="[%d/%d] Tracking list checking" % (idx + 1, total))

        self._bag_checks_v2_tracking_list(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.90,
                             text="[%d/%d] GDAL compatibility checking" % (idx + 1, total))

        self._bag_checks_v2_gdal_compatibility(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.95,
                             text="[%d/%d] Summary" % (idx + 1, total))

        self._bag_checks_v2_summary()

        output_pdf = os.path.join(self.bagchecks_output_folder, "%s.BCv2.%s.pdf"
                                  % (self._grid_basename, datetime.now().strftime("%Y%m%d.%H%M%S")))
        if self._noaa_nbs_profile:
            title_pdf = "BAG Checks v2 - Tests against NOAA OCS Profile"
        else:
            title_pdf = "BAG Checks v2 - Tests against General Profile"
        if self._bc_report.generate_pdf(output_pdf, title_pdf, use_colors=True):
            self._bc_pdf = output_pdf

        return True

    def _bag_checks_v2_structure(self, grid_file: str) -> None:
        if self._structure is False:
            self._bc_report += "Structure [SKIP_SEC]"
            self._bc_report += "All structure-related checks are deactivated. [SKIP_REP]"
            return

        self._bc_report += "Structure [SECTION]"

        self._bc_structure_errors = 0
        self._bc_structure_warnings = 0

        try:
            bf = bag.BAGFile(grid_file)
            # logger.debug('BAG version: %s' % bf.bag_version())

            # CHK: presence of root
            self._bc_report += "Check the presence of the BAG Root group [CHECK]"
            if not bf.has_bag_root():
                self._bc_structure_errors += 1
                self._bc_report += "[ERROR] Missing the BAG Root group"
            else:
                self._bc_report += "OK"

            # CHK: presence of version
            self._bc_report += "Check the presence of the BAG Version attribute [CHECK]"
            if not bf.has_bag_version():
                self._bc_structure_errors += 1
                self._bc_report += "[ERROR] Missing the BAG Version attribute"
            else:
                self._bc_report += "OK"

            # CHK: presence of metadata
            self._bc_report += "Check the presence of the Metadata dataset [CHECK]"
            if not bf.has_metadata():
                self._bc_structure_errors += 1
                self._bc_report += "[ERROR] Missing the Metadata dataset"
            else:
                self._bc_report += "OK"

            # CHK: presence of elevation
            self._bc_report += "Check the presence of the Elevation dataset [CHECK]"
            if not bf.has_elevation():
                self._bc_structure_errors += 1
                self._bc_report += "[ERROR] Missing the Elevation dataset"
            else:
                self._bc_report += "OK"

            # CHK: presence of uncertainty
            self._bc_report += "Check the presence of the Uncertainty dataset [CHECK]"
            if not bf.has_uncertainty():
                self._bc_structure_errors += 1
                self._bc_report += "[ERROR] Missing the Uncertainty dataset"
            else:
                self._bc_report += "OK"

            # CHK: presence of tracking list
            self._bc_report += "Check the presence of the Tracking List dataset [CHECK]"
            if not bf.has_tracking_list():
                self._bc_structure_errors += 1
                self._bc_report += "[ERROR] Missing the Tracking List dataset"
            else:
                self._bc_report += "OK"

            if self._is_vr:
                # CHK: presence of VR Metadata
                self._bc_report += "Check the presence of the VR Metadata dataset [CHECK]"
                if not bf.has_varres_metadata():
                    self._bc_structure_errors += 1
                    self._bc_report += "[ERROR] Missing the VR Metadata dataset"
                else:
                    self._bc_report += "OK"

                # CHK: presence of VR Refinements
                self._bc_report += "Check the presence of the VR Refinements dataset [CHECK]"
                if not bf.has_varres_refinements():
                    self._bc_structure_errors += 1
                    self._bc_report += "[ERROR] Missing the VR Refinements dataset"
                else:
                    self._bc_report += "OK"

                # CHK: presence of VR Tracking List
                self._bc_report += "Check the presence of the VR Tracking List dataset [CHECK]"
                if not bf.has_varres_tracking_list():
                    self._bc_structure_errors += 1
                    self._bc_report += "[ERROR] Missing the VR Tracking List dataset"
                else:
                    self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_structure_errors += 1
            self._bc_report += "[ERROR] %s" % e

    def _bag_checks_v2_metadata(self, grid_file: str) -> None:
        if self._metadata is False:
            self._bc_report += "Metadata [SKIP_SEC]"
            self._bc_report += "All metadata-related checks are deactivated. [SKIP_REP]"
            return

        self._bc_report += "Metadata [SECTION]"

        self._bc_metadata_errors = 0
        self._bc_metadata_warnings = 0

        try:
            bf = bag.BAGFile(grid_file)

            # CHK: presence of metadata
            self._bc_report += "Check the presence of the Metadata dataset [CHECK]"
            if not bf.has_metadata():
                self._bc_metadata_errors += 1
                self._bc_report += "[ERROR] Missing the Metadata dataset"
                return
            else:
                self._bc_report += "OK"

            bf.populate_metadata()
            # bf.extract_metadata('test.xml')

            if self._noaa_nbs_profile and not self._is_vr:

                # CHK: check resolution in metadata matches filename
                self._bc_report += "Check that the resolution in metadata matches the filename (SR only) [CHECK]"
                if bf.meta.res_x is None:
                    self._bc_report += "[WARNING] The resolution entry might be NOT present"
                    self._bc_metadata_warnings += 1
                else:
                    res_token_m = "%.0fm" % bf.meta.res_x
                    res_token_cm = "%.0fcm" % (bf.meta.res_x*100)

                    if res_token_m in self._grid_basename:

                        self._bc_report += "OK"

                    elif res_token_cm in self._grid_basename:

                        self._bc_report += "OK"

                    else:

                        self._bc_report += "[ERROR] The resolution entry [%s m] might NOT match " \
                                           "the filename [%s]" % (bf.meta.res_x, self._grid_basename)
                        self._bc_metadata_warnings += 1

            if self._noaa_nbs_profile:

                # CHK: use of projected spatial reference system
                self._bc_report += "Check that the spatial reference system is projected [CHECK]"
                if bf.meta.wkt_srs is None:
                    if b"UTM" not in bf.meta.xml_srs:
                        self._bc_report += "[WARNING] The spatial reference system might be NOT projected [%s...]" \
                                           % bf.meta.xml_srs[:20]
                        self._bc_metadata_warnings += 1
                    else:
                        self._bc_report += "OK"
                else:
                    srs = osr.SpatialReference()
                    srs.ImportFromWkt(bf.meta.wkt_srs)
                    srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
                    # check if projected coordinates
                    if not srs.IsProjected:
                        self._bc_report += "[WARNING] The spatial reference system does is NOT projected [%s...]" \
                                           % bf.meta.wkt_srs[:20]
                        self._bc_metadata_warnings += 1
                    else:
                        self._bc_report += "OK"

            # TODO: additional checks on SRS

            if self._noaa_nbs_profile:

                # CHK: definition of vertical datum
                self._bc_report += "Check that the vertical datum is defined [CHECK]"
                if bf.meta.wkt_vertical_datum is None:
                    if b"Unknown" in bf.meta.xml_vertical_datum:
                        self._bc_report += "[WARNING] The vertical datum might be unknown [%s...]" \
                                           % bf.meta.xml_vertical_datum[:20]
                        self._bc_metadata_warnings += 1
                    else:
                        self._bc_report += "OK"
                else:
                    if "unknown" in bf.meta.wkt_vertical_datum.lower():
                        self._bc_report += "[WARNING] The vertical datum is unknown [%s...]" \
                                           % bf.meta.wkt_vertical_datum[:20]
                        self._bc_metadata_warnings += 1
                    else:
                        self._bc_report += "OK"

            if self._noaa_nbs_profile:
                # CHK: presence of creation date
                self._bc_report += "Check the presence of the creation date [CHECK]"
                if bf.meta.date is None:
                    self._bc_report += "[WARNING] Unable to retrieve the creation date."
                    self._bc_metadata_warnings += 1
                else:
                    self._bc_report += "OK"

                # CHK: presence of survey start date
                self._bc_report += "Check the presence of the survey start date [CHECK]"
                if bf.meta.survey_start_date is None:
                    self._bc_report += "[WARNING] Unable to retrieve the survey start date."
                    self._bc_metadata_warnings += 1
                else:
                    self._bc_report += "OK"

                # CHK: presence of survey end date
                self._bc_report += "Check the presence of the survey end date [CHECK]"
                if bf.meta.survey_end_date is None:
                    self._bc_report += "[WARNING] Unable to retrieve the survey end date."
                    self._bc_metadata_warnings += 1
                else:
                    self._bc_report += "OK"

            if self._noaa_nbs_profile:
                # CHK: use of product uncertainty
                self._bc_report += "Check the selection of Product Uncertainty [CHECK]"
                if not bf.has_product_uncertainty():
                    self._bc_metadata_warnings += 1
                    self._bc_report += "[WARNING] The Uncertainty layer does not contain Product Uncertainty: %s" \
                                       % bf.meta.unc_type
                else:
                    self._bc_report += "OK"

            if self._is_vr:
                # CHK: presence of VR Metadata
                self._bc_report += "Check the presence of the VR Metadata dataset [CHECK]"
                if not bf.has_varres_metadata():
                    self._bc_metadata_errors += 1
                    self._bc_report += "[ERROR] Missing the VR Metadata dataset"
                else:
                    self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_metadata_errors += 1
            self._bc_report += "[ERROR] Unexpected issue: %s" % e

    def _bag_checks_v2_elevation(self, grid_file: str) -> None:
        if self._elevation is False:
            self._bc_report += "Elevation [SKIP_SEC]"
            self._bc_report += "All elevation-related checks are deactivated. [SKIP_REP]"
            return

        self._bc_report += "Elevation [SECTION]"

        self._bc_elevation_errors = 0
        self._bc_elevation_warnings = 0

        try:
            bf = bag.BAGFile(grid_file)

            # CHK: presence of elevation
            self._bc_report += "Check the presence of the Elevation dataset [CHECK]"
            if not bf.has_elevation():
                self._bc_elevation_errors += 1
                self._bc_report += "[ERROR] Missing the Elevation dataset"
                return
            else:
                self._bc_report += "OK"

            self._cur_min_depth, self._cur_max_depth = bf.depth_min_max()
            logger.debug('min/max depth: %.2f/%.2f' % (self._cur_min_depth, self._cur_max_depth))

            # CHK: all NaN
            self._bc_report += "Check that all the values are not NaN [CHECK]"
            if np.isnan(self._cur_min_depth):  # all NaN case
                self._bc_elevation_warnings += 1
                self._bc_report += "[WARNING] All elevation values are NaN"
            else:
                self._bc_report += "OK"

            if self._is_vr:
                # CHK: presence of VR Refinements
                self._bc_report += "Check the presence of the VR Refinements dataset [CHECK]"
                if not bf.has_varres_refinements():
                    self._bc_elevation_errors += 1
                    self._bc_report += "[ERROR] Missing the VR Refinements dataset"
                else:
                    self._bc_report += "OK"

                self._cur_vr_min_depth, self._cur_vr_max_depth = bf.vr_depth_min_max()
                logger.debug('VR min/max depth: %.2f/%.2f' % (self._cur_vr_min_depth, self._cur_vr_max_depth))

                # CHK: VR depth all NaN
                self._bc_report += "Check that all the VR depth values are not NaN [CHECK]"
                if np.isnan(self._cur_vr_min_depth):  # all NaN case
                    self._bc_elevation_warnings += 1
                    self._bc_report += "[WARNING] All VR elevation values are NaN"
                else:
                    self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_elevation_errors += 1
            self._bc_report += "[ERROR] Unknown issue: %s" % e

    def _bag_checks_v2_uncertainty(self, grid_file: str) -> None:
        if self._uncertainty is False:
            self._bc_report += "Uncertainty [SKIP_SEC]"
            self._bc_report += "All uncertainty-related checks are deactivated. [SKIP_REP]"
            return

        self._bc_report += "Uncertainty [SECTION]"

        self._bc_uncertainty_errors = 0
        self._bc_uncertainty_warnings = 0

        try:
            bf = bag.BAGFile(grid_file)

            # CHK: presence of uncertainty
            self._bc_report += "Check the presence of the Uncertainty dataset [CHECK]"
            if not bf.has_uncertainty():
                self._bc_uncertainty_errors += 1
                self._bc_report += "[ERROR] Missing the Uncertainty dataset"
                return
            else:
                self._bc_report += "OK"

            if self._cur_max_depth is None:
                self._cur_min_depth, self._cur_max_depth = bf.depth_min_max()
            # logger.debug('min/max depth: %.2f/%.2f'
            #              % (self._cur_min_depth, self._cur_max_depth))
            if np.isnan(self._cur_max_depth) or (self._cur_max_depth < 0.0):
                max_depth = 0.0
            else:
                max_depth = self._cur_max_depth
            high_unc_threshold = 4.0 + 0.1 * max_depth
            logger.debug('max uncertainty threshold: %.2f m (max: %.2f m)' % (high_unc_threshold, self._cur_max_depth))

            min_uncertainty, max_uncertainty = bf.uncertainty_min_max()
            logger.debug('min/max uncertainty: %.2f/%.2f' % (min_uncertainty, max_uncertainty))

            if self._noaa_nbs_profile:
                # CHK: all NaN
                self._bc_report += "Check that all the values are not NaN [CHECK]"
                if np.isnan(min_uncertainty):  # all NaN case
                    self._bc_uncertainty_warnings += 1
                    self._bc_report += "[WARNING] All uncertainty values are NaN"
                    return
                else:
                    self._bc_report += "OK"

            # CHK: negative uncertainty
            self._bc_report += "Check that uncertainty values are only positive [CHECK]"
            if min_uncertainty <= 0.0:
                self._bc_uncertainty_errors += 1
                self._bc_report += "[ERROR] At least one negative or zero value of uncertainty is present (%.3f)" \
                                   % min_uncertainty
            else:
                self._bc_report += "OK"

            if self._noaa_nbs_profile:

                # CHK: too high uncertainty
                if "ellipsoid" in self._grid_basename.lower():
                    self._bc_report += \
                        "Check that uncertainty values are not too high (detected Ellipsoid Depths) [SKIP_CHK]"
                    logger.debug("Ellipsoid Depths: skipping check for too high uncertainty values")
                else:
                    self._bc_report += "Check that uncertainty values are not too high (<%.2fm) [CHECK]" \
                                       % high_unc_threshold
                    if max_uncertainty >= high_unc_threshold:
                        self._bc_uncertainty_warnings += 1
                        self._bc_report += "[WARNING] Too high value for maximum uncertainty: %.2f" % max_uncertainty
                    else:
                        self._bc_report += "OK"

            if self._is_vr:
                # CHK: presence of VR Refinements
                self._bc_report += "Check the presence of the VR Refinements dataset [CHECK]"
                if not bf.has_varres_refinements():
                    self._bc_uncertainty_errors += 1
                    self._bc_report += "[ERROR] Missing the VR Refinements dataset"
                else:
                    self._bc_report += "OK"

                if self._cur_vr_max_depth is None:
                    self._cur_vr_min_depth, self._cur_vr_max_depth = bf.vr_depth_min_max()
                logger.debug('min/max elevation: %.2f/%.2f'
                             % (self._cur_vr_min_depth, self._cur_vr_max_depth))
                if np.isnan(self._cur_vr_max_depth) or (self._cur_vr_max_depth < 0.0):
                    vr_max_depth = 0.0
                else:
                    vr_max_depth = self._cur_vr_max_depth
                vr_high_unc_threshold = 4.0 + 0.1 * vr_max_depth
                logger.debug('max VR uncertainty threshold: %.2f m (max: %.2f m)'
                             % (vr_high_unc_threshold, self._cur_vr_max_depth))

                vr_min_uncertainty, vr_max_uncertainty = bf.vr_uncertainty_min_max()
                logger.debug('VR min/max uncertainty: %.2f/%.2f' % (vr_min_uncertainty, vr_max_uncertainty))

                if self._noaa_nbs_profile:
                    # CHK: all NaN
                    self._bc_report += "Check that all the VR values are not NaN [CHECK]"
                    if np.isnan(vr_min_uncertainty):  # all NaN case
                        self._bc_uncertainty_warnings += 1
                        self._bc_report += "[WARNING] All uncertainty values are NaN"
                        return
                    else:
                        self._bc_report += "OK"

                # CHK: negative uncertainty
                self._bc_report += "Check that VR uncertainty values are only positive [CHECK]"
                if vr_min_uncertainty <= 0.0:
                    self._bc_uncertainty_errors += 1
                    self._bc_report += "[ERROR] At least one negative or zero value of uncertainty is present (%.3f)" \
                                       % min_uncertainty
                else:
                    self._bc_report += "OK"

                if self._noaa_nbs_profile:
                    # CHK: too high uncertainty
                    if "ellipsoid" in self._grid_basename.lower():
                        self._bc_report += \
                            "Check that VR uncertainty values are not too high (detected Ellipsoid Depths) [SKIP_CHK]"
                        logger.debug("Ellipsoid Depths: skipping check for too high uncertainty values")
                    else:
                        self._bc_report += "Check that VR uncertainty values are not too high (<%.2fm) [CHECK]" \
                                           % vr_high_unc_threshold
                        if vr_max_uncertainty >= vr_high_unc_threshold:
                            self._bc_uncertainty_warnings += 1
                            self._bc_report += "[WARNING] Too high value for maximum uncertainty: %.2f" % vr_max_uncertainty
                        else:
                            self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_uncertainty_errors += 1
            self._bc_report += "[ERROR] Unuspected issue: %s" % e

    def _bag_checks_v2_tracking_list(self, grid_file: str) -> None:
        if self._tracking_list is False:
            self._bc_report += "Tracking List [SKIP_SEC]"
            self._bc_report += "All tracking-list-related checks are deactivated. [SKIP_REP]"
            return

        self._bc_report += "Tracking List [SECTION]"

        self._bc_tracking_list_errors = 0
        self._bc_tracking_list_warnings = 0

        try:
            bf = bag.BAGFile(grid_file)

            # CHK: presence of tracking list
            self._bc_report += "Check the presence of the Tracking List dataset [CHECK]"
            if not bf.has_tracking_list():
                self._bc_tracking_list_errors += 1
                self._bc_report += "[ERROR] Missing the Tracking List dataset"
                return
            else:
                self._bc_report += "OK"

            # CHK validity of row columns
            self._bc_report += "Check the validity of 'row' columns [CHECK]"
            if not bf.has_valid_row_in_tracking_list():
                self._bc_tracking_list_errors += 1
                self._bc_report += "[ERROR] At least 1 invalid value in 'row' columns"
            else:
                self._bc_report += "OK"

            # CHK validity of col columns
            self._bc_report += "Check the validity of 'col' columns [CHECK]"
            if not bf.has_valid_col_in_tracking_list():
                self._bc_tracking_list_errors += 1
                self._bc_report += "[ERROR] At least 1 invalid value in 'col' columns"
            else:
                self._bc_report += "OK"

            if self._is_vr:
                # CHK: presence of VR Tracking List
                self._bc_report += "Check the presence of the VR Tracking List dataset [CHECK]"
                if not bf.has_varres_tracking_list():
                    self._bc_tracking_list_errors += 1
                    self._bc_report += "[ERROR] Missing the VR Tracking List dataset"
                else:
                    self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_tracking_list_errors += 1
            self._bc_report += "[ERROR] Unexpected issue: %s" % e

    def _bag_checks_v2_gdal_compatibility(self, grid_file: str) -> None:
        if self._gdal_compatibility is False:
            self._bc_report += "GDAL Compatibility [SKIP_SEC]"
            self._bc_report += "All GDAL-compatibility-related checks are deactivated. [SKIP_REP]"
            return

        self._bc_report += "GDAL Compatibility [SECTION]"

        self._bc_gdal_compatibility_errors = 0
        self._bc_gdal_compatibility_warnings = 0

        try:
            bf = bag.BAGFile(grid_file)

            # CHK: Too many refinement grids
            self._bc_report += "Check for 'Too many refinement grids' GDAL error [CHECK]"
            bf_rows, bf_cols = bf.elevation_shape()
            if self._is_vr and ((bf_rows * bf_cols) > 10000000):
                self._bc_gdal_compatibility_warnings += 1
                self._bc_report += "[WARNING] Too big super-grid: %d, %d" % (bf_rows, bf_cols)
                return
            else:
                self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_gdal_compatibility_errors += 1
            self._bc_report += "[ERROR] Unexpected issue: %s" % e

    def _bag_checks_v2_summary(self) -> None:
        self._bc_report += "Summary [SECTION]"
        if self._structure:
            self._bc_report += "Structure [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_structure_errors
            self._bc_report += "Warnings: %d" % self._bc_structure_warnings
        if self._metadata:
            self._bc_report += "Metadata [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_metadata_errors
            self._bc_report += "Warnings: %d" % self._bc_metadata_warnings
        if self._elevation:
            self._bc_report += "Elevation [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_elevation_errors
            self._bc_report += "Warnings: %d" % self._bc_elevation_warnings
        if self._uncertainty:
            self._bc_report += "Uncertainty [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_uncertainty_errors
            self._bc_report += "Warnings: %d" % self._bc_uncertainty_warnings
        if self._tracking_list:
            self._bc_report += "Tracking List [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_tracking_list_errors
            self._bc_report += "Warnings: %d" % self._bc_tracking_list_warnings
        if self._gdal_compatibility:
            self._bc_report += "GDAL Compatibility [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_gdal_compatibility_errors
            self._bc_report += "Warnings: %d" % self._bc_gdal_compatibility_warnings

    @property
    def cur_bag_checks_passed(self) -> bool:

        if self._structure:
            if (self._bc_structure_errors > 0) or (self._bc_structure_warnings > 0):
                return False

        if self._metadata:
            if (self._bc_metadata_errors > 0) or (self._bc_metadata_warnings > 0):
                return False

        if self._elevation:
            if (self._bc_elevation_errors > 0) or (self._bc_elevation_warnings > 0):
                return False

        if self._uncertainty:
            if (self._bc_uncertainty_errors > 0) or (self._bc_uncertainty_warnings > 0):
                return False

        if self._tracking_list:
            if (self._bc_tracking_list_errors > 0) or (self._bc_tracking_list_warnings > 0):
                return False

        if self._gdal_compatibility:
            if (self._bc_gdal_compatibility_errors > 0) or (self._bc_gdal_compatibility_warnings > 0):
                return False

        return True

    def open_bagchecks_output_folder(self):
        logger.info("open %s" % self.bagchecks_output_folder)
        Helper.explore_folder(self.bagchecks_output_folder)

    @property
    def bagchecks_output_folder(self):
        # make up the output folder (creating it if it does not exist)
        if self.output_project_folder:
            output_folder = os.path.join(self.output_folder, self._survey)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            output_folder = os.path.join(output_folder, "bag_checks")
        else:
            output_folder = os.path.join(output_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        return output_folder
