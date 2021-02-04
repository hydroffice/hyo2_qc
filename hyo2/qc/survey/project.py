from collections import defaultdict
from datetime import datetime
import time
import os
import traceback
import logging
from typing import Optional

import numpy as np
from osgeo import osr

from hyo2.abc.lib.progress.cli_progress import CliProgress
from hyo2.abc.lib.gdal_aux import GdalAux
from hyo2.abc.lib.helper import Helper
from hyo2.abc.app.report import Report
from hyo2.qc.common.project import BaseProject
from hyo2.qc.common.writers.s57_writer import S57Writer
from hyo2.qc.common.writers.kml_writer import KmlWriter
from hyo2.qc.common.writers.shp_writer import ShpWriter
from hyo2.qc.survey.fliers.find_fliers_v8 import FindFliersV8
# noinspection PyProtectedMember
from hyo2.grids import _gappy
from hyo2.qc.survey.gridqa.grid_qa_v6 import GridQAV6
from hyo2.grids.grids_manager import layer_types
from hyo2.qc.survey.scan.base_scan import scan_algos
from hyo2.qc.survey.scan.base_scan import survey_areas
from hyo2.qc.survey.scan.feature_scan_v10 import FeatureScanV10
from hyo2.qc.survey.designated.base_designated import designated_algos
from hyo2.qc.survey.designated.designated_scan_v2 import DesignatedScanV2
from hyo2.qc.survey.valsou.base_valsou import valsou_algos
from hyo2.qc.survey.valsou.valsou_check_v7 import ValsouCheckV7
from hyo2.qc.survey.sbdare.base_sbdare import sbdare_algos
from hyo2.qc.survey.sbdare.sbdare_export_v3 import SbdareExportV3
from hyo2.qc.survey.sbdare.sbdare_export_v4 import SbdareExportV4
from hyo2.qc.survey.submission.base_submission import BaseSubmission, submission_algos
from hyo2.qc.survey.submission.submission_checks_v3 import SubmissionChecksV3
# noinspection PyProtectedMember
from hyo2.grids._grids import FLOAT as GRIDS_FLOAT, DOUBLE as GRIDS_DOUBLE
from hyo2.qc import name as lib_name, __version__ as lib_version

from hyo2.bag import bag
from hyo2.bag.meta import Meta

logger = logging.getLogger(__name__)


class SurveyProject(BaseProject):

    def __init__(self, output_folder=None, profile=BaseProject.project_profiles['office'], progress=CliProgress()):

        super().__init__(projects_folder=output_folder, profile=profile, progress=progress)

        self._submission_output_folder = None

        # find fliers
        self._fliers = None
        # find fliers outputs
        self.file_fliers_svp = str()
        self.file_fliers_s57 = str()

        # anomaly detector
        self._anomaly = None
        # anomaly detector outputs
        self.file_anomaly_svp = str()
        self.file_anomaly_s57 = str()

        # find holes
        self._holes = None
        # find holes outputs
        self.file_holes_svp = str()
        self.file_holes_s57 = str()

        # grid qa
        self._qa = None

        # bag checks
        self._bc = None
        self._bc_msg = str()
        self._bc_noaa_nbs_profile = False
        self._bc_structure = False
        self._bc_metadata = False
        self._bc_elevation = False
        self._bc_uncertainty = False
        self._bc_tracking_list = False
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
        self._bc_report = None
        self._bc_pdf = str()
        self._bc_cur_min_elevation = None  # type: Optional[float]
        self._bc_cur_max_elevation = None  # type: Optional[float]

        # scan features
        self._scan = None
        self.file_scan_s57 = str()
        self.file_scan_pdf = str()
        self.scan_msg = str()

        # designated
        self._designated = None
        # outputs
        self.file_designated_svp = str()
        self.file_designated_s57 = str()

        # valsou check
        self._valsou = None
        self.file_valsou_s57 = str()

        # sbdare check
        self._sbdare = None
        self.file_sbdare_ascii = str()
        self.file_sbdare_shp = str()

        # --- submission check stuff

        self._submissions = list()
        self._submission = None
        self.file_submission_pdf = str()

    def clear_data(self):

        super(SurveyProject, self).clear_data()

        # find fliers
        self._fliers = None
        # find fliers outputs
        self.file_fliers_svp = str()
        self.file_fliers_s57 = str()

        # find holes
        self._holes = None
        # find holes outputs
        self.file_holes_svp = str()
        self.file_holes_s57 = str()

        # grid qa
        self._qa = None

        # scan features
        self._scan = None
        self.file_scan_s57 = str()
        self.file_scan_pdf = str()
        self.scan_msg = str()

        # designated
        self._designated = None
        # outputs
        self.file_designated_svp = str()
        self.file_designated_s57 = str()

        # valsou check
        self._valsou = None
        self.file_valsou_s57 = str()

        # sbdare check
        self._sbdare = None
        self.file_sbdare_ascii = str()
        self.file_sbdare_shp = str()

    def clear_submission_data(self):

        self._submission = None
        # inputs
        self._submissions = list()
        # output
        self.file_submission_pdf = str()

    # ________________________________________________________________________________
    # ############################## FLIER-FINDER METHODS ############################

    @property
    def flagged_fliers(self):
        if self.number_of_fliers():
            return self._fliers.flagged_fliers
        else:
            return list()

    def number_of_fliers(self):
        if not self._fliers:
            return 0
        return len(self._fliers.flagged_fliers)

    def make_fliers_output_folder(self) -> str:
        # make up the output folder (creating it if it does not exist)
        if self.output_project_folder:
            output_folder = os.path.join(self.output_folder, self._survey)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            output_folder = os.path.join(output_folder, "flier_finder")
        else:
            output_folder = os.path.join(output_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        return output_folder

    def find_fliers_v8(self, height,
                       check_laplacian=False, check_curv=True, check_adjacent=True,
                       check_slivers=True, check_isolated=True, check_edges=False,
                       edges_distance=3, edges_pct_tvu=0.9,
                       filter_fff=False, filter_designated=False,
                       export_proxies=False, export_heights=False, export_curvatures=False,
                       progress_bar=None):
        """Look for fliers using the passed parameters and the loaded grids"""
        if not self.has_grid():
            logger.warning("first load some grids")
            return

        try:
            self._gr.select_layers_in_current = [self._gr.depth_layer_name(), ]

            self._fliers = FindFliersV8(grids=self._gr,
                                        height=height,  # can be None in case of just gaussian curv or isolated nodes
                                        check_laplacian=check_laplacian,
                                        check_curv=check_curv,
                                        check_adjacent=check_adjacent,
                                        check_slivers=check_slivers,
                                        check_isolated=check_isolated,
                                        check_edges=check_edges,
                                        edges_distance=edges_distance,
                                        edges_pct_tvu=edges_pct_tvu,
                                        filter_fff=filter_fff,
                                        filter_designated=filter_designated,
                                        save_proxies=export_proxies,
                                        save_heights=export_heights,
                                        save_curvatures=export_curvatures,
                                        output_folder=self.make_fliers_output_folder(),
                                        progress_bar=progress_bar)

            start_time = time.time()
            self._fliers.run()
            logger.info("find fliers v8 -> execution time: %.3f s" % (time.time() - start_time))

        except Exception as e:
            traceback.print_exc()
            self._fliers = None
            raise e

    def find_fliers_v8_apply_filters(self, distance=1.0, delta_z=0.01):
        """Look for fliers using the passed parameters and the loaded grids"""
        if not self.has_grid():
            logger.warning("first load some grids")
            return

        try:
            self._gr.select_layers_in_current = [self._gr.depth_layer_name(), ]

            start_time = time.time()

            self._fliers.apply_filters(s57_list=self.s57_list, distance=distance, delta_z=delta_z)

            logger.info("find fliers v8 filters -> execution time: %.3f s" % (time.time() - start_time))

        except Exception as e:
            traceback.print_exc()
            self._fliers = None
            raise e

    # ________________________________________________________________________________
    #                               FLIERS EXPORT METHODS

    def save_fliers(self):
        """Save fliers in S57 format"""
        plot_algos_dict = False  # for visual debugging

        if not self.number_of_fliers():
            logger.warning("no fliers to save")
            return False

        output_folder = self._fliers.output_folder
        basename = self._fliers.basename
        s57_file1 = os.path.join(output_folder, "%s.blue_notes.000" % basename)
        s57_file2 = os.path.join(output_folder, "%s.soundings.000" % basename)

        # converting floats to strings (required by blue notes)
        fliers_for_blue_notes = list()

        algos_dict = defaultdict(int)
        for flagged_flier in self._fliers.flagged_fliers:
            fliers_for_blue_notes.append([flagged_flier[0], flagged_flier[1], "%.0f" % flagged_flier[2]])
            algos_dict[flagged_flier[2]] += 1
        S57Writer.write_bluenotes(feature_list=fliers_for_blue_notes, path=s57_file1, list_of_list=False)
        logger.debug("flagged per algo: %s" % algos_dict)
        if plot_algos_dict:
            from matplotlib import pyplot as plt
            plt.bar(algos_dict.keys(), algos_dict.values(), 1.0, color='g')
            plt.show()

        S57Writer.write_soundings(feature_list=self._fliers.flagged_fliers, path=s57_file2)
        self.file_fliers_s57 = s57_file2

        # noinspection PyBroadException
        try:
            out_file = s57_file2[:-4]
            if self.output_kml:
                KmlWriter().write_soundings(feature_list=self._fliers.flagged_fliers, path=out_file)

            if self.output_shp:
                ShpWriter().write_soundings(feature_list=self._fliers.flagged_fliers, path=out_file)

        except Exception:
            traceback.print_exc()
            logger.info("issue in writing shapefile/kml")

        return True

    def open_fliers_output_folder(self):
        if self.file_fliers_s57:
            Helper.explore_folder(os.path.dirname(self.file_fliers_s57))

        else:
            logger.warning('unable to define the output folder to open')

    @property
    def fliers_output_folder(self):
        if self.file_fliers_s57:
            return os.path.dirname(self.file_fliers_s57)

        else:
            logger.warning('unable to define the output folder to open')
            return str()

    # ________________________________________________________________________________
    # ############################ HOLIDAY-FINDER METHODS ############################

    @property
    def flagged_holes(self):
        GdalAux.check_gdal_data()

        holes = list()

        try:
            osr_csar = osr.SpatialReference()
            osr_csar.ImportFromWkt(self._holes.crs)
            osr_geo = osr.SpatialReference()
            osr_geo.ImportFromEPSG(4326)  # geographic WGS84
            loc2geo = osr.CoordinateTransformation(osr_csar, osr_geo)

        except Exception as e:
            raise IOError("unable to create a valid coords transform: %s" % e)

        # convert certain nodes to geographic coords
        try:
            if self._holes.certain_holes() > 0:
                xs = np.array(list(self._holes.certain_xs))
                ys = np.array(list(self._holes.certain_ys))

                # convert to geographic
                lonlat = np.array(loc2geo.TransformPoints(np.vstack((xs, ys)).transpose()), np.float64)
                # add depths
                lonlat[:, 2] = 1
                # store as list of list
                holes += lonlat.tolist()

        except Exception as e:
            raise RuntimeError("Unable to perform conversion of the certain holes to geographic: %s" % e)

        # convert possible nodes to geographic coords
        try:
            if self._holes.possible_holes() > 0:
                xs = np.array(list(self._holes.possible_xs))
                ys = np.array(list(self._holes.possible_ys))

                # convert to geographic
                lonlat = np.array(loc2geo.TransformPoints(np.vstack((xs, ys)).transpose()), np.float64)
                # add depths
                lonlat[:, 2] = 2
                # store as list of list
                holes += lonlat.tolist()

        except Exception:
            raise RuntimeError("Unable to perform conversion of the possible holes to geographic: {e}")

        logger.info(f"Detected candidate holes: {len(holes)}")
        return holes

    def number_of_certain_holes(self):
        """Return the number of certain holes"""
        if not self._holes:
            return 0
        return len(self._holes.certain_xs)

    def number_of_possible_holes(self):
        """Return the number of possible holes"""
        if not self._holes:
            return 0
        return len(self._holes.possible_xs)

    def find_holes_v4(self, path, mode="FULL_COVERAGE", sizer="THREE_TIMES", max_size=0, pct_min_res=1.0,
                      local_perimeter=True, visual_debug=False, export_ascii=False, brute_force=True, cb=None):
        """Look for fliers using the passed parameters and the loaded grids"""

        try:
            support_path = os.path.dirname(_gappy.__file__).replace("\\", "/")
            logger.debug("support path: %s" % support_path)

            if sizer == "TWO_TIMES":
                hole_sizer = _gappy.GappyHoleSizer_TWO_TIMES
                logger.debug("hole sizer: TWO_TIMES")
            elif sizer == "TWO_TIMES_PLUS_ONE_NODE":
                hole_sizer = _gappy.GappyHoleSizer_TWO_TIMES_PLUS_ONE_NODE
                logger.debug("hole sizer: TWO_TIMES_PLUS_ONE_NODE")
            else:  # if sizer == "THREE_TIMES":
                hole_sizer = _gappy.GappyHoleSizer_THREE_TIMES
                logger.debug("hole sizer: THREE_TIMES")

            if local_perimeter:
                ref_depth = _gappy.GappyHoleReferenceDepth_PERIMETER_MEDIAN
                logger.debug("ref depth: PERIMETER_MEDIAN")
            else:
                ref_depth = _gappy.GappyHoleReferenceDepth_TILE_MEDIAN
                logger.debug("ref depth: TILE_MEDIAN")

            start_time = time.time()
            if mode == "FULL_COVERAGE":
                gappy_mode = _gappy.GappyMode_FULL_COVERAGE
                logger.debug("gappy mode: FULL_COVERAGE")
            elif mode == "OBJECT_DETECTION":
                gappy_mode = _gappy.GappyMode_OBJECT_DETECTION
                logger.debug("gappy mode: OBJECT_DETECTION")
            else:  # if mode == "ALL_HOLES":
                gappy_mode = _gappy.GappyMode_ALL_HOLES
                logger.debug("gappy mode: ALL_HOLES")

            logger.debug("max size: %s" % (max_size if (max_size != 0.0) else "unlimited"))

            self._holes = _gappy.Gappy(support_path, path, gappy_mode, max_size, hole_sizer, ref_depth)
            self._holes.visual_debug = visual_debug
            self._holes.export_ascii = export_ascii
            self._gr.set_current(path)
            self.make_survey_label()

            if cb:
                self._holes.set_progress_callback(cb)

            if brute_force:
                logger.debug("brute force: pct of minimum resolution: %.1f" % (pct_min_res * 100.0,))
                success = self._holes.detect_brute_force(True, pct_min_res)
            else:
                success = self._holes.detect_per_tile()
            if not success:
                raise RuntimeError("Unable to analyze %s !\n"
                                   "Are you processing the input surface in another application?" % path)

            logger.info("find holidays v4 [%s] -> execution time: %.3f s" % (mode, time.time() - start_time))

        except Exception as e:
            # traceback.print_exc()
            self._holes = None
            raise e

    # ________________________________________________________________________________
    #                              HOLES EXPORT METHODS

    def save_holes(self):
        """Save holes"""

        if not self.number_of_certain_holes() and not self.number_of_possible_holes():
            logger.warning("no holes to save")
            return False

        logger.debug(f"holes: certain {self.number_of_certain_holes()}, possible {self.number_of_possible_holes()}")

        # make up the output folder (creating it if it does not exist)
        if self.output_project_folder:
            output_folder = os.path.join(self.output_folder, self._survey)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            output_folder = os.path.join(output_folder, "holiday_finder")
        else:
            output_folder = os.path.join(output_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # make the filename for output

        mode_str = self._holes.mode_str()
        if mode_str == "FULL_COVERAGE":
            mode_type = "cov"
        elif mode_str == "OBJECT_DETECTION":
            mode_type = "obj"
        else:
            mode_type = "all"
        basename = self._gr.current_basename
        upper_limit_sizer_value = self._holes.upper_limit_sizer()
        if self._holes.upper_limit_infinite():
            upper_limit_sizer = "inf"
        else:
            upper_limit_sizer = "%d" % upper_limit_sizer_value
        flagged_holes = self.flagged_holes
        # if self._holes.brute_force():
        #     strategy = "BF"
        # else:
        #     strategy = "PT"

        # pct_min_res = "%d" % (self._holes.pct_min_res() * 100)

        algo_type = "HFv4"
        basename = os.path.join(output_folder, "%s.%s.%s.%s"
                                % (basename, algo_type, mode_type, upper_limit_sizer))
        # svp_file = basename + ".svp"
        s57_file = basename + ".000"

        S57Writer.write_soundings(feature_list=flagged_holes, path=s57_file)
        self.file_holes_s57 = s57_file

        try:
            if self.output_kml:
                KmlWriter().write_soundings(feature_list=flagged_holes, path=basename)

            if self.output_shp:
                ShpWriter().write_soundings(feature_list=flagged_holes, path=basename)

        except Exception as e:
            traceback.print_exc()
            logger.info(f"issue in writing shapefile/kml ({e})")

        # delete Gappy instance
        self._holes = None

        return True

    def open_holes_output_folder(self):
        if self.file_holes_s57:
            Helper.explore_folder(os.path.dirname(self.file_holes_s57))

        elif self.file_holes_svp:
            Helper.explore_folder(os.path.dirname(self.file_holes_svp))

        else:
            logger.warning('unable to define the output folder to open')

    @property
    def holes_output_folder(self):
        if self.file_holes_s57:
            return os.path.dirname(self.file_holes_s57)

        elif self.file_holes_svp:
            return os.path.dirname(self.file_holes_svp)

        else:
            logger.warning('unable to define the output folder to open')
            return str()

    # ________________________________________________________________________________
    #                           GRID-QA  METHODS

    def grid_qa_v6(self, force_tvu_qc=True, calc_object_detection=True, calc_full_coverage=True,
                   hist_depth=True, hist_density=True, hist_tvu_qc=True, hist_pct_res=True,
                   hist_catzoc_a1=True, hist_catzoc_a2b=True, hist_catzoc_c=True,
                   depth_vs_density=False, depth_vs_tvu_qc=False,
                   progress_bar=None):
        """Calculate grid QA using the passed parameters and the loaded grids"""
        if not self.has_grid():
            logger.warning("first load some grids")
            return False

        try:

            # layers selection
            layers = list()
            has_depth = self.cur_grid_has_depth_layer()
            if has_depth:
                layers.append(layer_types["depth"])

            if hist_density or depth_vs_density:
                has_density = self.cur_grid_has_density_layer()
                if has_density:
                    layers.append(layer_types["density"])
            else:
                has_density = False

            if hist_tvu_qc or depth_vs_tvu_qc or hist_catzoc_a1 or hist_catzoc_a2b or hist_catzoc_c:
                has_tvu_qc = self.cur_grid_has_tvu_qc_layer()
                has_product_uncertainty = self.cur_grid_has_product_uncertainty_layer()
                if has_tvu_qc and not force_tvu_qc:
                    layers.append(layer_types["tvu_qc"])

                elif has_product_uncertainty:
                    layers.append(layer_types["product_uncertainty"])
            else:
                has_tvu_qc = False
                has_product_uncertainty = False

            self._gr.selected_layers_in_cur_grid = layers

            # do the QA
            self._qa = GridQAV6(grids=self._gr, force_tvu_qc=force_tvu_qc,
                                has_depth=has_depth, has_product_uncertainty=has_product_uncertainty,
                                has_density=has_density, has_tvu_qc=has_tvu_qc, output_folder=self.gridqa_output_folder,
                                object_detection=calc_object_detection, full_coverage=calc_full_coverage,
                                hist_depth=hist_depth, hist_density=hist_density,
                                hist_tvu_qc=hist_tvu_qc, hist_pct_res=hist_pct_res, hist_catzoc_a1=hist_catzoc_a1,
                                hist_catzoc_a2b=hist_catzoc_a2b, hist_catzoc_c=hist_catzoc_c,
                                depth_vs_density=depth_vs_density, depth_vs_tvu_qc=depth_vs_tvu_qc,
                                progress=progress_bar)

            start_time = time.time()
            passed = self._qa.run()
            logger.info("Grid QA v6 -> execution time: %.3f s" % (time.time() - start_time))

            return passed

        except Exception as e:
            traceback.print_exc()
            self._qa = None
            raise e

    def open_gridqa_output_folder(self):
        logger.info("open %s" % self.gridqa_output_folder)
        Helper.explore_folder(self.gridqa_output_folder)

    @property
    def gridqa_output_folder(self):
        # make up the output folder (creating it if it does not exist)
        if self.output_project_folder:
            output_folder = os.path.join(self.output_folder, self._survey)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            output_folder = os.path.join(output_folder, "grid_qa")
        else:
            output_folder = os.path.join(output_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        return output_folder

    # ________________________________________________________________________________
    # ############################# BAG-CHECKS METHODS ###############################

    def bag_checks_v1(self, use_nooa_nbs_profile: bool = False, check_structure: bool = False,
                      check_metadata: bool = False, check_elevation: bool = False,
                      check_uncertainty: bool = False, check_tracking_list: bool = False):
        """Check the input BAG files"""
        
        self._bc_noaa_nbs_profile = use_nooa_nbs_profile
        self._bc_structure = check_structure
        self._bc_metadata = check_metadata
        self._bc_elevation = check_elevation
        self._bc_uncertainty = check_uncertainty
        self._bc_tracking_list = check_tracking_list

        self.progress.start(title="BAG Checks v1", text="Loading")

        if not self._bc_structure and not self._bc_metadata and not self._bc_elevation and not self._bc_uncertainty \
                and not self._bc_tracking_list:
            raise RuntimeError('At least one check needs to be selected')
            
        logger.info('BAG Checks v1 -> Structure: %s, Metadata: %s, Elevation: %s, Uncertainty: %s, Tracking List: %s'
                    % (self._bc_structure, self._bc_metadata, self._bc_elevation, self._bc_uncertainty,
                       self._bc_tracking_list))

        if self._bc_noaa_nbs_profile:
            logger.info('Using the NOAA OCS profile')
        else:
            logger.info('Using the general profile')

        # Check if the grid list is empty
        if len(self.grid_list) == 0:
            raise RuntimeError("The grid list is empty")

        if not self.has_bag_grid():
            raise RuntimeError("At least one BAG file is required")

        try:
            start_time = time.time()

            # for each file in the project grid list
            self._bc_msg = "Checks results per input:\n"
            opened_folders = list()

            nr_of_files = len(self.grid_list)
            for i, grid_file in enumerate(self.grid_list):

                self._bc_cur_min_elevation = None
                self._bc_cur_max_elevation = None
                success = self._bag_checks_v1(grid_file=grid_file, idx=i, total=nr_of_files)

                if success:
                    if self.cur_bag_checks_passed:
                        self._bc_msg += "- %s: pass\n" % self.cur_grid_basename
                    else:
                        self._bc_msg += "- %s: fail\n" % self.cur_grid_basename
                    # open the output folder (if not already open)
                    if self.bagchecks_output_folder not in opened_folders:
                        self.open_bagchecks_output_folder()
                        opened_folders.append(self.bagchecks_output_folder)
                else:
                    self._bc_msg += "- %s: skip\n" % self.cur_grid_basename

            logger.info("BAG Checks v1 -> execution time: %.3f s" % (time.time() - start_time))

        except Exception as e:
            traceback.print_exc()
            self._bc = None
            self._bc_msg = None
            self.progress.end()
            raise e

        self.progress.end()

    def _bag_checks_v1(self, grid_file: str, idx: int, total: int) -> bool:

        quantum = 100.0 / total
        cur_quantum = quantum * idx

        self.progress.update(value=cur_quantum + quantum * 0.05, text="[%d/%d] File opening" % (idx + 1, total))

        # we want to be sure that the label is based on the name of the new file input
        self.clear_survey_label()
        self.set_cur_grid(path=grid_file)

        # skip CSAR and BAG VR
        if not bag.BAGFile.is_bag(bag_path=grid_file):  # skip CSAR
            logger.debug('not a BAG file: %s' % grid_file)
            return False
        if bag.BAGFile.is_vr(bag_path=grid_file):  # skip VR BAG
            logger.debug('skipping VR BAG file: %s' % grid_file)
            return False

        self._bc_report = Report(lib_name=lib_name, lib_version=lib_version)

        self.progress.update(value=cur_quantum + quantum * 0.15, text="[%d/%d] Structure checking" % (idx + 1, total))

        self._bag_checks_v1_structure(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.3, text="[%d/%d] Metadata checking" % (idx + 1, total))

        self._bag_checks_v1_metadata(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.5, text="[%d/%d] Elevation checking" % (idx + 1, total))

        self._bag_checks_v1_elevation(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.7, text="[%d/%d] Uncertainty checking" % (idx + 1, total))

        self._bag_checks_v1_uncertainty(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.85,
                             text="[%d/%d] Tracking list checking" % (idx + 1, total))

        self._bag_checks_v1_tracking_list(grid_file=grid_file)

        self.progress.update(value=cur_quantum + quantum * 0.95,
                             text="[%d/%d] Summary" % (idx + 1, total))

        self._bag_checks_v1_summary()

        output_pdf = os.path.join(self.bagchecks_output_folder, "%s.BCv1.%s.pdf"
                                  % (self.cur_grid_basename, datetime.now().strftime("%Y%m%d.%H%M%S")))
        if self._bc_noaa_nbs_profile:
            title_pdf = "BAG Checks v1 - Tests against NOAA OCS Profile"
        else:
            title_pdf = "BAG Checks v1 - Tests against General Profile"
        if self._bc_report.generate_pdf(output_pdf, title_pdf, use_colors=True):
            self._bc_pdf = output_pdf

        return True

    def _bag_checks_v1_structure(self, grid_file: str) -> None:
        if self._bc_structure is False:
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

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_structure_errors += 1
            self._bc_report += "[ERROR] %s" % e

    def _bag_checks_v1_metadata(self, grid_file: str) -> None:
        if self._bc_metadata is False:
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

            if self._bc_noaa_nbs_profile:
                # CHK: use of projected spatial reference system
                self._bc_report += "Check that the spatial reference system is projected [CHECK]"
                srs = osr.SpatialReference()
                srs.ImportFromWkt(bf.meta.wkt_srs)
                # check if projected coordinates
                if not srs.IsProjected:
                    self._bc_report += "[WARNING] The spatial reference system does is NOT projected [%s...]" \
                                       % bf.meta.wkt_srs[:20]
                    self._bc_metadata_warnings += 1
                else:
                    self._bc_report += "OK"

            # TODO: additional checks on SRS

            if self._bc_noaa_nbs_profile:
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

            # TODO: add checks to retrieve start/end of survey in the BAG library

            if self._bc_noaa_nbs_profile:
                # CHK: use of product uncertainty
                self._bc_report += "Check the selection of Product Uncertainty [CHECK]"
                if not bf.has_product_uncertainty():
                    self._bc_metadata_warnings += 1
                    self._bc_report += "[WARNING] The Uncertainty layer does not contain Product Uncertainty: %s" \
                                       % bf.meta.unc_type
                else:
                    self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_metadata_errors += 1
            self._bc_report += "[ERROR] Unexpected issue: %s" % e

    def _bag_checks_v1_elevation(self, grid_file: str) -> None:
        if self._bc_elevation is False:
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

            self._bc_cur_min_elevation, self._bc_cur_max_elevation = bf.elevation_min_max()
            logger.debug('min/max elevation: %s/%s' % (self._bc_cur_min_elevation, self._bc_cur_max_elevation))

            # CHK: all NaN
            self._bc_report += "Check that all the values are not NaN [CHECK]"
            if np.isnan(self._bc_cur_min_elevation):  # all NaN case
                self._bc_elevation_warnings += 1
                self._bc_report += "[WARNING] All elevation values are NaN"
            else:
                self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_elevation_errors += 1
            self._bc_report += "[ERROR] Unknown issue: %s" % e

    def _bag_checks_v1_uncertainty(self, grid_file: str) -> None:
        if self._bc_uncertainty is False:
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

            if self._bc_cur_min_elevation is None:
                self._bc_cur_min_elevation, self._bc_cur_max_elevation = bf.elevation_min_max()
            ref_elevation = -(self._bc_cur_min_elevation + self._bc_cur_max_elevation) / 2.0
            logger.debug('ref elevation: %s -> min/max elevation: %s/%s'
                         % (ref_elevation, self._bc_cur_min_elevation, self._bc_cur_max_elevation))
            if np.isnan(ref_elevation):
                high_unc_threshold = 30.0
            elif ref_elevation < 0.0:
                high_unc_threshold = 30.0
            elif ref_elevation > 30.0:
                high_unc_threshold = 30.0
            else:
                high_unc_threshold = ref_elevation
            logger.debug('max uncertainty threshold: %s' % (high_unc_threshold, ))

            # logger.debug('min/max elevation: %s/%s' % (min_elevation, max_elevation))
            min_uncertainty, max_uncertainty = bf.uncertainty_min_max()
            logger.debug('min/max uncertainty: %s/%s' % (min_uncertainty, max_uncertainty))

            if self._bc_noaa_nbs_profile:
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

            if self._bc_noaa_nbs_profile:
                # CHK: negative uncertainty
                self._bc_report += "Check that uncertainty values are not too high [CHECK]"
                if max_uncertainty >= high_unc_threshold:
                    self._bc_uncertainty_warnings += 1
                    self._bc_report += "[WARNING] Too high value for maximum uncertainty: %.2f" % max_uncertainty
                else:
                    self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_uncertainty_errors += 1
            self._bc_report += "[ERROR] Unuspected issue: %s" % e

    def _bag_checks_v1_tracking_list(self, grid_file: str) -> None:
        if self._bc_tracking_list is False:
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
                self._bc_structure_errors += 1
                self._bc_report += "[ERROR] Missing the Tracking List dataset"
                return
            else:
                self._bc_report += "OK"

            # CHK validity of row and col columns
            self._bc_report += "Check the validity of 'row' and 'col' columns [CHECK]"
            if not bf.has_valid_row_and_col_in_tracking_list():
                self._bc_structure_errors += 1
                self._bc_report += "[ERROR] At least 1 invalid value in 'row' and 'col' columns"
            else:
                self._bc_report += "OK"

        except Exception as e:
            traceback.print_exc()
            self._bc_report += "Other potential issues [CHECK]"
            self._bc_tracking_list_errors += 1
            self._bc_report += "[ERROR] Unexpected issue: %s" % e

    def _bag_checks_v1_summary(self) -> None:
        self._bc_report += "Summary [SECTION]"
        if self._bc_structure:
            self._bc_report += "Structure [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_structure_errors
            self._bc_report += "Warnings: %d" % self._bc_structure_warnings
        if self._bc_metadata:
            self._bc_report += "Metadata [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_metadata_errors
            self._bc_report += "Warnings: %d" % self._bc_metadata_warnings
        if self._bc_elevation:
            self._bc_report += "Elevation [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_elevation_errors
            self._bc_report += "Warnings: %d" % self._bc_elevation_warnings
        if self._bc_uncertainty:
            self._bc_report += "Uncertainty [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_uncertainty_errors
            self._bc_report += "Warnings: %d" % self._bc_uncertainty_warnings
        if self._bc_tracking_list:
            self._bc_report += "Tracking List [CHECK]"
            self._bc_report += "Errors: %d" % self._bc_tracking_list_errors
            self._bc_report += "Warnings: %d" % self._bc_tracking_list_warnings

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

    @property
    def bag_checks_message(self) -> str:
        return self._bc_msg

    @property
    def cur_bag_checks_passed(self) -> bool:

        if self._bc_structure:
            if (self._bc_structure_errors > 0) or (self._bc_structure_warnings > 0):
                return False

        if self._bc_metadata:
            if (self._bc_metadata_errors > 0) or (self._bc_metadata_warnings > 0):
                return False

        if self._bc_elevation:
            if (self._bc_elevation_errors > 0) or (self._bc_elevation_warnings > 0):
                return False

        if self._bc_uncertainty:
            if (self._bc_uncertainty_errors > 0) or (self._bc_uncertainty_warnings > 0):
                return False

        if self._bc_tracking_list:
            if (self._bc_tracking_list_errors > 0) or (self._bc_tracking_list_warnings > 0):
                return False

        return True
    # ________________________________________________________________________________
    # ########################### DESIGNATED-SCAN METHODS ############################

    @property
    def flagged_designated(self):
        if self.number_of_designated():
            return self._designated.flagged_designated
        else:
            return list()

    def number_of_designated(self):
        """Return the number of flagged designated"""
        if not self._designated:
            return 0
        return len(self._designated.flagged_designated[0])

    def designated_scan_v2(self, survey_scale, neighborhood=False, specs="2017"):
        """Look for fliers using the passed parameters and the loaded grids"""
        if not self.has_s57():
            logger.warning("first load some features")
            return

        if not self.has_bag_grid():
            logger.warning("first load some BAG grids")
            return

        self.progress.start(text="Data processing")

        try:

            self._gr.selected_layers_in_current = [layer_types["depth"], ]

            self._designated = DesignatedScanV2(s57=self.cur_s57,
                                                grids=self._gr.cur_grids,
                                                survey_scale=survey_scale,
                                                neighborhood=neighborhood,
                                                specs=specs)

            start_time = time.time()
            self._designated.run()
            logger.info("designated scan v2 [ngb: %s] -> execution time: %.3f s"
                        % (neighborhood, time.time() - start_time))

        except Exception as e:
            traceback.print_exc()
            self._designated = None
            self.progress.end()
            raise e

        self.progress.end()

    # ________________________________________________________________________________
    #                            DESIGNATED EXPORT METHODS

    def save_designated(self):
        """Save designated in two formats: S57 and SVP"""

        if not self.number_of_designated():
            logger.warning("no designated to save")
            return False

        # make up the output folder (creating it if it does not exist)
        if self.output_project_folder:
            output_folder = os.path.join(self.output_folder, self._survey)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            output_folder = os.path.join(output_folder, "designated_scan")
        else:
            output_folder = os.path.join(output_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # make the filename for output
        str_grid_res = "%.f" % self._gr.cur_grids.bbox().res_x
        algo_type = Helper.first_match(designated_algos, self._designated.type)

        if self._designated.type == designated_algos['DESIGNATED_SCAN_v2']:
            s57_file = os.path.join(output_folder, "%s.%s.%s_%s.%s.000"
                                    % (self.cur_grid_basename, self.cur_s57_basename,
                                       str_grid_res, algo_type, self._designated.specs))
        else:
            raise RuntimeError("Not implemented find holidays algorithm")

        S57Writer.write_bluenotes(feature_list=self._designated.flagged_designated, path=s57_file)
        self.file_designated_s57 = s57_file
        # noinspection PyBroadException
        try:
            out_file = s57_file[:-4]
            if self.output_kml:
                KmlWriter().write_bluenotes(feature_list=self._designated.flagged_designated, path=out_file)
            if self.output_shp:
                ShpWriter().write_bluenotes(feature_list=self._designated.flagged_designated, path=out_file)
        except Exception:
            logger.info("issue in writing shapefile/kml")

        return True

    def open_designated_output_folder(self):
        if self.file_designated_s57:
            Helper.explore_folder(os.path.dirname(self.file_designated_s57))

        elif self.file_designated_svp:
            Helper.explore_folder(os.path.dirname(self.file_designated_svp))

        else:
            logger.warning('unable to define the output folder to open')

    @property
    def designated_output_folder(self):
        if self.file_designated_s57:
            return os.path.dirname(self.file_designated_s57)

        elif self.file_designated_svp:
            return os.path.dirname(self.file_designated_svp)

        else:
            logger.warning('unable to define the output folder to open')
            return str()

    # ________________________________________________________________________________
    # ############################# SCAN PROCESS METHODS #############################

    @classmethod
    def check_sorind(cls, value):
        return FeatureScanV10.check_sorind(value=value)

    @classmethod
    def check_sordat(cls, value):
        return FeatureScanV10.check_sordat(value=value)

    @property
    def flagged_features(self):
        if self.number_of_flagged_features():
            return self._scan.flagged_features
        else:
            return list()

    def number_of_flagged_features(self):
        """Return the number of flagged fliers"""
        if not self._scan:
            return 0
        return len(self._scan.flagged_features[0])

    def feature_scan(self, version: int, specs_version: str,
                     survey_area: int = survey_areas["Pacific Coast"], use_mhw: bool = False, mhw_value: float = 0.0,
                     sorind: Optional[str] = None, sordat: Optional[str] = None,
                     multimedia_folder: Optional[str] = None, use_htd: bool = False):

        # sanity checks
        # - version
        if version not in [10]:
            raise RuntimeError("passed invalid Feature Scan version: %s" % version)

        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.s57_list) == 0:
            raise RuntimeError("the S57 list is empty")

        # for each file in the project grid list
        self.scan_msg = "Flagged features per input:\n"
        opened_folders = list()

        for i, s57_file in enumerate(self.s57_list):

            # we want to be sure that the label is based on the name of the new file input
            self.clear_survey_label()

            if multimedia_folder is None:
                input_folder = os.path.dirname(s57_file)
                multimedia_folder = os.path.join(input_folder, "Multimedia")
                if not os.path.exists(multimedia_folder):
                    multimedia_folder = None

            # switcher between different versions of feature scan
            if version in [10]:
                self._feature_scan(feature_file=s57_file, version=version, specs_version=specs_version,
                                   survey_area=survey_area, use_mhw=use_mhw, mhw_value=mhw_value,
                                   sorind=sorind, sordat=sordat, multimedia_folder=multimedia_folder, use_htd=use_htd,
                                   idx=(i + 1), total=len(self.s57_list))

            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Feature Scan version: %s" % version)

            # export the flagged features
            saved = self._export_feature_scan()
            self.scan_msg += "- %s: %d\n" % (self.cur_s57_basename, self.number_of_flagged_features())

            # open the output folder (if not already open)
            if saved:

                if self._scan_output_folder not in opened_folders:
                    self._open_scan_output_folder()
                    opened_folders.append(self._scan_output_folder)

    def _feature_scan(self, feature_file: str, version: int, specs_version: str,
                      survey_area: int, use_mhw: bool, mhw_value: float, sorind: Optional[str], sordat: Optional[str],
                      multimedia_folder: Optional[str], use_htd: bool,
                      idx: int, total: int) -> None:
        """ feature scan in the loaded s57 features """
        logger.debug('feature scan v%d ...' % version)

        self.progress.start(title="Feature scan v.%d" % version,
                            text="Data loading [%d/%d]" % (idx, total))

        try:
            self.read_feature_file(feature_path=feature_file)

        except Exception as e:
            traceback.print_exc()
            self.progress.end()
            raise e

        self.progress.update(text="Feature Scan v%d [%d/%d]" % (version, idx, total), value=30)

        try:
            if version == 10:
                self._scan_features_v10(specs_version=specs_version,
                                        survey_area=survey_area, use_mhw=use_mhw, mhw_value=mhw_value,
                                        sorind=sorind, sordat=sordat, multimedia_folder=multimedia_folder,
                                        use_htd=use_htd)

            else:
                RuntimeError("unknown Feature Scan version: %s" % version)

        except Exception as e:
            traceback.print_exc()
            self.progress.end()
            raise e

        self.progress.end()

    def _scan_features_v10(self, specs_version: str, survey_area: int, use_mhw: bool, mhw_value: float,
                           sorind: Optional[str], sordat: Optional[str], multimedia_folder: Optional[str],
                           use_htd: bool):
        """Look for fliers using the passed parameters and the loaded grids"""
        if not self.has_s57():
            return

        try:

            self._scan = FeatureScanV10(s57=self.cur_s57, profile=self.active_profile, version=specs_version,
                                        survey_area=survey_area, use_mhw=use_mhw, mhw_value=mhw_value,
                                        sorind=sorind, sordat=sordat, multimedia_folder=multimedia_folder,
                                        use_htd=use_htd)

            start_time = time.time()
            self._scan.run()
            logger.info("scan features v10 -> execution time: %.3f s" % (time.time() - start_time))

        except Exception as e:
            traceback.print_exc()
            self._scan = None
            raise e

    # ________________________________________________________________________________
    #                               SCAN EXPORT METHODS

    def _export_feature_scan(self):
        """ export flagged features """
        logger.debug('exporting flagged features ...')
        saved_pdf = self._report_scanned_features()
        saved_s57 = self._save_scanned_features()
        logger.debug('exporting flagged features: done')
        return saved_s57 or saved_pdf

    def _report_scanned_features(self):
        """Generate a pdf with the result of the checks"""
        if not self._scan:
            logger.warning('no Feature scan algorithm to access')
            return False

        if len(self._scan.report.records) == 0:
            logger.warning('no Feature scan records to write')
            return False

        # make up the output folder (creating it if it does not exist)
        if self.output_project_folder:
            output_folder = os.path.join(self.output_folder, self._survey)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            output_folder = os.path.join(output_folder, "feature_scan")
        else:
            output_folder = os.path.join(output_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        if self._scan.type == scan_algos['FEATURE_SCAN_v10']:

            if self._scan.version == '2018':
                output_pdf = os.path.join(output_folder, "%s.SFSv10.2018.pdf" % self.cur_s57_basename)
                title_pdf = "Survey Feature Scan v10 - Tests against HSSD 2018"

            elif self._scan.version == '2019':
                output_pdf = os.path.join(output_folder, "%s.SFSv10.2019.pdf" % self.cur_s57_basename)
                title_pdf = "Survey Feature Scan v10 - Tests against HSSD 2019"

            elif self._scan.version == '2020':
                output_pdf = os.path.join(output_folder, "%s.SFSv10.2020.pdf" % self.cur_s57_basename)
                title_pdf = "Survey Feature Scan v10 - Tests against HSSD 2020"

            elif self._scan.version == '2021':
                output_pdf = os.path.join(output_folder, "%s.SFSv10.2021.pdf" % self.cur_s57_basename)
                title_pdf = "Survey Feature Scan v10 - Tests against HSSD 2021"

            else:
                raise RuntimeError("Not implemented version: %s" % self._scan.version)

        else:
            raise RuntimeError("Not implemented feature scan algorithm")

        if self._scan.report.generate_pdf(output_pdf, title_pdf, use_colors=True):
            self.file_scan_pdf = output_pdf

        return True

    def _save_scanned_features(self):
        """Save flagged features in S57"""

        if self.number_of_flagged_features() == 0:
            logger.warning("no flagged features to save")
            return False

        if not os.path.exists(self.file_scan_pdf):
            logger.warning("unable to locate pfd report")
            return False

        s57_file = "%s.000" % self.file_scan_pdf[:-4]

        S57Writer.write_bluenotes(feature_list=self._scan.flagged_features, path=s57_file)
        self.file_scan_s57 = s57_file
        # noinspection PyBroadException
        try:
            out_file = s57_file[:-4]

            if self.output_kml:
                KmlWriter().write_bluenotes(feature_list=self._scan.flagged_features, path=out_file)

            if self.output_shp:
                ShpWriter().write_bluenotes(feature_list=self._scan.flagged_features, path=out_file)

        except Exception:
            traceback.print_exc()
            logger.info("issue in writing shapefile/kml")

        return True

    def _open_scan_output_folder(self):
        if self.file_scan_s57 or self.file_scan_pdf:
            Helper.explore_folder(self._scan_output_folder)
        else:
            logger.warning('unable to define the output folder to open')

    @property
    def _scan_output_folder(self):
        if self.file_scan_s57:
            return os.path.dirname(self.file_scan_s57)

        elif self.file_scan_pdf:
            return os.path.dirname(self.file_scan_pdf)

        else:
            logger.warning('unable to define the output folder to open')
            return str()

    # ________________________________________________________________________________
    # ############################# VALSOU-CHECK METHODS #############################

    @property
    def valsou_features(self):
        if self.number_of_valsou_features():
            return self._valsou.flagged_features
        else:
            return list()

    @property
    def valsou_out_of_bbox(self):
        if self._valsou is None:
            raise RuntimeError("first run VALSOU Check")

        return self._valsou.out_of_bbox

    def number_of_valsou_features(self):
        """Return the number of flagged features"""
        if not self._valsou:
            return 0
        return len(self._valsou.flagged_features)

    def valsou_check_v7(self, specs_version="2018", survey_scale=100000, with_laser=True, is_target_detection=False):

        if not self.has_s57():
            logger.warning("first load some features")
            return

        if not self.has_grid():
            logger.warning("first load some grids")
            return

        self.progress.start(text="Data processing")

        try:

            self._gr.selected_layers_in_current = [layer_types["depth"], ]

            self._valsou = ValsouCheckV7(s57=self.cur_s57, grids=self._gr, version=specs_version,
                                         scale=survey_scale, with_laser=with_laser,
                                         is_target_detection=is_target_detection)

            start_time = time.time()
            self._valsou.run()
            logger.info("VALSOU check v7 -> execution time: %.3f s" % (time.time() - start_time))
            logger.info("flagged features: %d" % self.number_of_valsou_features())

        except Exception as e:
            traceback.print_exc()
            self._valsou = None
            self.progress.end()
            raise e

        self.progress.end()

    def valsou_check_deconflict_v6(self):
        # turn on the deconflicted flag
        self._valsou.deconflicted = True

        if self.number_of_valsou_features() == 0:
            logger.warning("no flagged valsou features to deconflict")
            return

        grid_file = self._gr.current_path

        for i, i_grid_file in enumerate(self.grid_list):

            if i_grid_file == grid_file:
                continue
            logger.debug("de-conflicting %s vs %s" % (os.path.basename(grid_file), os.path.basename(i_grid_file)))

            self.add_to_grid_list2(i_grid_file)
            self.set_cur_grid2(path=i_grid_file)
            self.open_to_read_cur_grid2()
            # self.selected_layers_in_cur_grid2 = [layer_types["depth"], ]

            nr_of_features = len(self._valsou.flagged_features)
            logger.debug("features to test: %d" % nr_of_features)
            if nr_of_features == 0:
                break

            # store the coordinate transform from CSAR CRS to geo (using GDAL)
            try:
                osr_grid = osr.SpatialReference()
                osr_grid.ImportFromWkt(self._gr2.cur_grids.bbox().hrs)
                osr_geo = osr.SpatialReference()
                osr_geo.ImportFromEPSG(4326)  # geographic WGS84
                # self.loc2geo = osr.CoordinateTransformation(osr_bag, osr_geo)
                geo2loc = osr.CoordinateTransformation(osr_geo, osr_grid)

            except Exception as e:
                raise RuntimeError("unable to create a valid coords transform: %s" % e)

            while self._gr2.read_next_tile(layers=[self._gr2.depth_layer_name(), ]):

                temp_flagged_features = self._valsou.flagged_features
                if len(temp_flagged_features) == 0:
                    break
                self._valsou.flagged_features = list()

                # first retrieve [long, lat, depth]
                valsou_geo = list()
                for flagged_feature in temp_flagged_features:
                    lon = flagged_feature[0]
                    lat = flagged_feature[1]
                    # logger.debug("- (%.6f, %.6f)" % (lon, lat))

                    valsou_geo.append([lon, lat, 0])

                # convert s57 features to grid CRS coords
                valsou_array = np.array(geo2loc.TransformPoints(np.array(valsou_geo, np.float64)),
                                        np.float64)

                tile = self._gr2.tiles[0]
                # logger.debug("types: %s" % (list(tile.types),))

                # convert feature to array coords
                valsou_array[:, 0] = (valsou_array[:, 0] - tile.bbox.transform[0]) / tile.bbox.transform[1] - 0.5
                valsou_array[:, 1] = (valsou_array[:, 1] - tile.bbox.transform[3]) / tile.bbox.transform[5] - 0.5

                # convert to the closest array coordinates
                valsou_closest = np.empty_like(valsou_array)
                valsou_closest[:, 0] = np.rint(valsou_array[:, 0])
                valsou_closest[:, 1] = np.rint(valsou_array[:, 1])

                depth_type = tile.type(self._gr2.depth_layer_name())
                depth_idx = tile.band_index(self._gr2.depth_layer_name())
                # logger.debug("depth layer: %s [idx: %s]" % (self.grids.grid_data_type(depth_type), depth_idx))

                # bathy_is_double = None
                # bathy_values = None
                # bathy_nodata = None
                if depth_type == GRIDS_DOUBLE:

                    # bathy_is_double = True
                    bathy_values = tile.doubles[depth_idx]
                    # bathy_nodata = tile.doubles_nodata[depth_idx]
                    bathy_values[tile.doubles[depth_idx] == tile.doubles_nodata[depth_idx]] = np.nan
                    if len(bathy_values) == 0:
                        raise RuntimeError("No bathy values")

                elif depth_type == GRIDS_FLOAT:

                    # bathy_is_double = False
                    bathy_values = tile.floats[depth_idx]
                    # bathy_nodata = tile.floats_nodata[depth_idx]
                    bathy_values[tile.floats[depth_idx] == tile.floats_nodata[depth_idx]] = np.nan
                    if len(bathy_values) == 0:
                        raise RuntimeError("No bathy values")

                else:
                    raise RuntimeError("Unsupported data type for bathy")

                # depth_closest = None
                for idx, closest_node in enumerate(valsou_closest):

                    # if the "[*]" is NOT found (there were data under the flagged feature)
                    if temp_flagged_features[idx][2].find("[*]") == - 1:
                        self._valsou.flagged_features.append(temp_flagged_features[idx])
                        # logger.debug("adding -> %s" % (temp_flagged_features[idx][2], ))
                        continue

                    # retrieve the node position on the current grid
                    c = int(closest_node[0])
                    r = int(closest_node[1])
                    # the node is NOT in this slice, we append
                    if (r < 0) or (r >= tile.bbox.rows) or \
                            (c < 0) or (c >= tile.bbox.cols):
                        self._valsou.flagged_features.append(temp_flagged_features[idx])
                        # logger.debug("adding (%s, %s) -> out of bbox (%s, %s)"
                        #              % (c, r, self._gr2.cur_grids.cur_slice.start,
                        #              self._gr2.cur_grids.cur_slice.stop))
                        continue

                    logger.debug("point (%s, %s) -> (%s, %s) in grid (%s, %s)"
                                 % (valsou_geo[idx][0], valsou_geo[idx][0], r, c, tile.bbox.rows, tile.bbox.cols))
                    # retrieve the depth at the node
                    depth_closest = bathy_values[r, c]
                    # if the depth is NAN, we append
                    if np.isnan(depth_closest):
                        self._valsou.flagged_features.append(temp_flagged_features[idx])
                        # logger.debug("adding (%s, %s) -> dep: %s" % (c, r, depth_closest))
                        continue

                    logger.debug("removing (%s, %s) -> dep: %s" % (c, r, depth_closest))

                self._gr2.clear_tiles()

    def valsou_check_deconflict_v7(self):
        self.valsou_check_deconflict_v6()

    # ________________________________________________________________________________
    # #########################    VALSOU EXPORT METHODS     #########################

    def save_valsou_features(self):
        """Save flagged valsou features in S57"""

        if self.number_of_valsou_features() == 0:
            logger.warning("no flagged valsou features to save")
            return False

        # make up the output folder (creating it if it does not exist)
        if self.output_project_folder:
            output_folder = os.path.join(self.output_folder, self._survey)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            output_folder = os.path.join(output_folder, "valsou_check")
        else:
            output_folder = os.path.join(output_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # make the filename for output
        if self._valsou.type == valsou_algos['VALSOU_CHECK_v6']:

            laser_token = ""
            if self._valsou.with_laser:
                laser_token = ".las"

            deconflict_token = ""
            if self._valsou.deconflicted:
                deconflict_token = ".dec"

            if self._valsou.version in ["2018", ]:
                s57_file = os.path.join(output_folder, "%s.%s.VCv6.%s%s%s.000"
                                        % (self.cur_s57_basename, self.cur_grid_basename, self._valsou.version,
                                           laser_token, deconflict_token))
            else:
                s57_file = os.path.join(output_folder, "%s.%s.VCv6.%s.%s%s%s.000"
                                        % (self.cur_s57_basename, self.cur_grid_basename, self._valsou.version,
                                           self._valsou.scale, laser_token, deconflict_token))

        elif self._valsou.type == valsou_algos['VALSOU_CHECK_v7']:

            laser_token = ""
            if self._valsou.with_laser:
                laser_token = ".las"

            deconflict_token = ""
            if self._valsou.deconflicted:
                deconflict_token = ".dec"

            mode_token = ".fc"
            if self._valsou.is_target_detection:
                mode_token = ".od"

            if self._valsou.version in ["2018", ]:
                s57_file = os.path.join(output_folder, "%s.%s.VCv7.%s%s%s%s.000"
                                        % (self.cur_s57_basename, self.cur_grid_basename, self._valsou.version,
                                           laser_token, deconflict_token, mode_token))
            else:
                s57_file = os.path.join(output_folder, "%s.%s.VCv7.%s.%s%s%s%s.000"
                                        % (self.cur_s57_basename, self.cur_grid_basename, self._valsou.version,
                                           self._valsou.scale, laser_token, deconflict_token, mode_token))

        else:
            raise RuntimeError("Not implemented VALSOU check algorithm")

        logger.debug("output: %s" % s57_file)
        S57Writer.write_bluenotes(feature_list=self._valsou.flagged_features, path=s57_file, list_of_list=False)
        self.file_valsou_s57 = s57_file
        # noinspection PyBroadException
        try:

            out_file = s57_file[:-4]

            if self.output_kml:
                KmlWriter().write_bluenotes(feature_list=self._valsou.flagged_features, path=out_file,
                                            list_of_list=False)

            if self.output_shp:
                ShpWriter().write_bluenotes(feature_list=self._valsou.flagged_features, path=out_file,
                                            list_of_list=False)

        except Exception:
            traceback.print_exc()
            logger.info("issue in writing shapefile/kml")

        return True

    def open_valsou_output_folder(self):
        if self.file_valsou_s57:
            Helper.explore_folder(self.valsou_output_folder)

        else:
            logger.warning('unable to define the output folder to open')

    @property
    def valsou_output_folder(self):
        if self.file_valsou_s57:
            return os.path.dirname(self.file_valsou_s57)

        else:
            logger.warning('unable to define the output folder to open')
            return str()

    # ________________________________________________________________________________
    # ############################# SBDARE-CHECK METHODS #############################

    def number_of_sbdare_features(self):
        """Return the number of seabed features"""
        if not self._sbdare:
            return 0
        return len(self._sbdare.sbdare_features)

    def sbdare_export_v3(self):
        """Export S57 SBDARE values"""
        if not self.has_s57():
            logger.warning("first load some features")
            return

        try:

            self._sbdare = SbdareExportV3(s57=self.cur_s57)

            start_time = time.time()
            self._sbdare.run()
            logger.info("SBDARE export v3 -> execution time: %.3f s" % (time.time() - start_time))

        except Exception as e:
            traceback.print_exc()
            self._sbdare = None
            raise e

    def sbdare_export_v4(self, exif=False, images_folder=None):
        """Export S57 SBDARE values"""
        if not self.has_s57():
            logger.warning("first load some features")
            return

        try:

            self._sbdare = SbdareExportV4(s57=self.cur_s57, s57_path=self.cur_s57_path,
                                          do_exif=exif, images_folder=images_folder)

            self._sbdare.run()

        except Exception as e:
            traceback.print_exc()
            self._sbdare = None
            raise e

    # ________________________________________________________________________________
    #                              SBDARE-EXPORT METHODS

    def save_sbdare(self):
        """All collected SBDARE objects are printed to an ASCII file per HTD 2013-3"""
        if not self._sbdare:
            logger.warning('no SBDARE check algorithm to access')
            return False

        if len(self._sbdare.sbdare_features) == 0:
            logger.warning('no SBDARE features')
            return False

        # make up the output folder (creating it if it does not exist)
        if self.output_project_folder:
            output_folder = os.path.join(self.output_folder, self._survey)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            output_folder = os.path.join(output_folder, "sbdare_export")
        else:
            output_folder = os.path.join(output_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        success = True
        if self._sbdare.type == sbdare_algos['SBDARE_EXPORT_v3']:

            output_ascii = os.path.join(output_folder, "%s_BottomSamples.ascii" % self._survey)
            if self._sbdare.generate_ascii(output_ascii):
                self.file_sbdare_ascii = output_ascii
            else:
                success = False

        elif self._sbdare.type == sbdare_algos['SBDARE_EXPORT_v4']:

            start_time = time.time()

            output_name = "%s_BottomSamples" % self._survey
            success = self._sbdare.generate_output(output_folder, output_name)
            if success:
                self.file_sbdare_ascii = self._sbdare.output_ascii
                self.file_sbdare_shp = self._sbdare.output_shp

            logger.info("SBDARE export v4 -> execution time: %.3f s" % (time.time() - start_time))

        return success

    def open_sbdare_output_folder(self):
        if self.file_sbdare_ascii:
            Helper.explore_folder(self.sbdare_output_folder)

        else:
            logger.warning('unable to define the output folder to open')

    @property
    def sbdare_output_folder(self):
        if self.file_sbdare_ascii:
            return os.path.dirname(self.file_sbdare_ascii)

        else:
            logger.warning('unable to define the output folder to open')
            return str()

    def sbdare_warnings(self):
        if not self._sbdare:
            logger.warning('no SBDARE check algorithm to access')
            return list()
        return self._sbdare.warnings

    # ________________________________________________________________________________
    # ######################  SUBMISSION FOLDER LIST METHODS  ########################

    @property
    def submission_output_folder(self):
        if self._submission is None:
            raise RuntimeError("first run Submission Check")
        logger.debug("current survey label: %s" % self._submission.cur_xnnnnn)
        if self.output_project_folder and (self._submission.cur_xnnnnn is not None):
            output_folder = os.path.join(self.output_folder, self._submission.cur_xnnnnn)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            self._submission_output_folder = os.path.join(output_folder, "submissions")
        else:
            self._submission_output_folder = output_folder
        # self._submission_output_folder = os.path.join(self.output_folder, "submissions")
        if not os.path.exists(self._submission_output_folder):
            os.makedirs(self._submission_output_folder)
        return self._submission_output_folder

    @submission_output_folder.setter
    def submission_output_folder(self, submission_output_folder):
        if not os.path.exists(submission_output_folder):
            raise RuntimeError("the passed output folder does not exist: %s" % submission_output_folder)
        self._submission_output_folder = submission_output_folder

    def open_submission_output_folder(self):
        Helper.explore_folder(self.submission_output_folder)

    @property
    def submission_list(self):
        return self._submissions

    def add_to_submission_list(self, path):

        if not os.path.exists(path):
            logger.warning("the passed path does not exist: %s" % path)
            return

        if not os.path.isdir(path):
            logger.warning("the passed path is not a folder path: %s" % path)
            return

        if path in self._submissions:
            logger.warning("the passed folder path is already present: %s" % path)
            return

        self._submissions.append(path)

    def remove_from_submission_list(self, path):

        if path not in self._submissions:
            logger.warning("the passed folder path is not present: %s" % path)
            return

        self._submissions.remove(path)

    def clear_submission_list(self):
        self._submissions = list()

    @classmethod
    def is_valid_project_folder(cls, path, version="2017", opr=True):
        return BaseSubmission.is_valid_project_folder(path=path, version=version, opr=opr)

    @classmethod
    def is_valid_survey_folder(cls, path, version="2017", opr=True):
        return BaseSubmission.is_valid_survey_folder(path=path, version=version, opr=opr)

    @classmethod
    def is_valid_report_folder(cls, path, version="2017", opr=True):
        return BaseSubmission.is_valid_report_folder(path=path, version=version, opr=opr)

    @property
    def cur_project_name(self):
        if self._submission is None:
            raise RuntimeError("first run Submission Checks")

        return self._submission.project

    @property
    def cur_root_name(self):
        if self._submission is None:
            raise RuntimeError("first run Submission Checks")

        if self._submission.root_is_project:
            return self._submission.project

        if self._submission.root_is_survey:
            return "%s.%s" % (self._submission.project, self._submission.cur_xnnnnn)

        if self._submission.root_is_report:
            return "%s.report" % self._submission.project

        return self._submission.project

    @property
    def cur_submission_hssd(self):
        if self._submission is None:
            raise RuntimeError("first run Submission Checks")

        return self._submission.version

    def number_of_submission_errors(self):
        if not self._submission:
            return 0
        return len(self._submission.errors)

    def number_of_submission_warnings(self):
        if not self._submission:
            return 0
        return len(self._submission.warnings)

    # ________________________________________________________________________________
    #                           SUBMISSION CHECKS METHODS

    def submission_checks_v3(self, path, version, recursive, office, opr, noaa_only=False):

        try:

            self._submission = SubmissionChecksV3(root=path, version=version, recursive=recursive, office=office,
                                                  opr=opr, noaa_only=noaa_only)

            start_time = time.time()
            self._submission.run()
            logger.info("Submission checks v3 -> execution time: %.3f s" % (time.time() - start_time))

            return self._submission_checks_report()

        except Exception as e:
            traceback.print_exc()
            self._submission = None
            raise e

    def _submission_checks_report(self):
        """Generate a pdf with the result of the checks"""
        if not self._submission:
            logger.warning('no Submission Checks algorithm to access')
            return False

        if len(self._submission.report.records) == 0:
            logger.warning('no Submission Checks records to write')
            return False

        if self._submission.type == submission_algos['SUBMISSION_CHECKS_v3']:

            if self._submission.root_is_project:
                level = "project"
            elif self._submission.root_is_survey:
                level = self._submission.cur_xnnnnn
            else:
                level = "report"
            if self._submission.office:
                profile = "office"
            else:
                profile = "field"
            if self._submission.recursive:
                behavior = "recursive"
                beh_file = "rec"
            else:
                behavior = "exhaustive"
                beh_file = "exh"

            output_pdf = os.path.join(self.submission_output_folder, "%s.SCv3.%s.%s.%s.%s.pdf"
                                      % (self.cur_project_name, level, self.cur_submission_hssd, profile, beh_file))
            title_pdf = "Submission Checks v3 - %s [%s, %s, %s]" \
                        % (self.cur_submission_hssd, level, profile, behavior)

        else:
            raise RuntimeError("Not implemented feature scan algorithm")

        if self._submission.report.generate_pdf(output_pdf, title_pdf, use_colors=True, small=True):
            self.file_submission_pdf = output_pdf

        return True

    # _______________________________________________________________________________
    # ############################## AUXILIARY METHODS ##############################

    def retrieve_min_depth_tvu(self, path):
        self.open_grid(path=path)

        min_depth = None
        while self._gr.read_next_tile(layers=[self._gr.depth_layer_name(), ]):
            tile = self._gr.tiles[0]
            # logger.debug("types: %s" % (list(tile.types),))

            depth_type = tile.type(self._gr.depth_layer_name())
            depth_idx = tile.band_index(self._gr.depth_layer_name())
            # logger.debug("depth layer: %s [idx: %s]" % (self.grids.grid_data_type(depth_type), depth_idx))

            if depth_type == GRIDS_DOUBLE:

                bathy_values = tile.doubles[depth_idx]
                bathy_values[tile.doubles[depth_idx] == tile.doubles_nodata[depth_idx]] = np.nan
                if len(bathy_values) == 0:
                    raise RuntimeError("No bathy values")

            elif depth_type == GRIDS_FLOAT:

                bathy_values = tile.floats[depth_idx]
                bathy_values[tile.floats[depth_idx] == tile.floats_nodata[depth_idx]] = np.nan
                if len(bathy_values) == 0:
                    raise RuntimeError("No bathy values")

            else:
                raise RuntimeError("Unsupported data type for bathy")

            min_value = np.nanmin(bathy_values)
            if not np.isnan(min_value):
                if min_depth is None:
                    min_depth = min_value
                else:
                    if min_value < min_depth:
                        min_depth = min_value

            self._gr.clear_tiles()

        self.close_cur_grid()

        if min_depth is None:
            logger.warning("unable to retrieve the minimum depth")
            return None

        if min_depth > -100.0:
            tvu = (0.25 + (0.013 * min_depth) ** 2) ** 0.5
        else:
            tvu = (1. + (0.023 * min_depth) ** 2) ** 0.5
        logger.debug("min depth: %s -> tvu: %s" % (min_depth, tvu))

        return tvu

    def retrieve_max_uncert(self, path):
        self.open_grid(path=path)

        max_uncert = None
        while self._gr.read_next_tile(layers=[self._gr.product_uncertainty_layer_name(), ]):
            tile = self._gr.tiles[0]
            # logger.debug("types: %s" % (list(tile.types),))

            uncert_type = tile.type(self._gr.product_uncertainty_layer_name())
            uncert_idx = tile.band_index(self._gr.product_uncertainty_layer_name())
            # logger.debug("uncert layer: %s [idx: %s]" % (self.grids.grid_data_type(uncert_type), uncert_idx))

            if uncert_type == GRIDS_DOUBLE:

                uncert_values = tile.doubles[uncert_idx]
                uncert_values[tile.doubles[uncert_idx] == tile.doubles_nodata[uncert_idx]] = np.nan
                if len(uncert_values) == 0:
                    raise RuntimeError("No uncertainty values")

            elif uncert_type == GRIDS_FLOAT:

                uncert_values = tile.floats[uncert_idx]
                uncert_values[tile.floats[uncert_idx] == tile.floats_nodata[uncert_idx]] = np.nan
                if len(uncert_values) == 0:
                    raise RuntimeError("No uncertainty values")

            else:
                raise RuntimeError("Unsupported data type for uncertainty")

            max_value = np.nanmax(uncert_values)
            if not np.isnan(max_value):
                if max_uncert is None:
                    max_uncert = max_value
                else:
                    if max_value > max_uncert:
                        max_uncert = max_value
            logger.debug("max uncertainty: %s" % (max_uncert,))

            self._gr.clear_tiles()

        self.close_cur_grid()

        if max_uncert is None:
            logger.warning("unable to retrieve the maximum uncertainty")
            return None

        else:
            return max_uncert

    def retrieve_min_uncert(self, path):
        self.open_grid(path=path)

        min_uncert = None
        while self._gr.read_next_tile(layers=[self._gr.product_uncertainty_layer_name(), ]):
            tile = self._gr.tiles[0]
            # logger.debug("types: %s" % (list(tile.types),))

            uncert_type = tile.type(self._gr.product_uncertainty_layer_name())
            uncert_idx = tile.band_index(self._gr.product_uncertainty_layer_name())
            # logger.debug("uncert layer: %s [idx: %s]" % (self.grids.grid_data_type(uncert_type), uncert_idx))

            if uncert_type == GRIDS_DOUBLE:

                uncert_values = tile.doubles[uncert_idx]
                uncert_values[tile.doubles[uncert_idx] == tile.doubles_nodata[uncert_idx]] = np.nan
                if len(uncert_values) == 0:
                    raise RuntimeError("No uncertainty values")

            elif uncert_type == GRIDS_FLOAT:

                uncert_values = tile.floats[uncert_idx]
                uncert_values[tile.floats[uncert_idx] == tile.floats_nodata[uncert_idx]] = np.nan
                if len(uncert_values) == 0:
                    raise RuntimeError("No uncertainty values")

            else:
                raise RuntimeError("Unsupported data type for uncertainty")

            min_value = np.nanmin(uncert_values)
            if not np.isnan(min_value):
                if min_uncert is None:
                    min_uncert = min_value
                else:
                    if min_value < min_uncert:
                        min_uncert = min_value
            logger.debug("min uncertainty: %s" % (min_uncert,))

            self._gr.clear_tiles()

        self.close_cur_grid()

        if min_uncert is None:
            logger.warning("unable to retrieve the minumum uncertainty")
            return None

        else:
            return min_uncert

    def __repr__(self):
        msg = super().__repr__()
        msg += "  <active profile: %s>\n" % Helper.first_match(self.project_profiles, self.active_profile)
        return msg
