import time
import os
import traceback
import logging

from hyo2.abc.lib.progress.cli_progress import CliProgress
from hyo2.qc.common.project import BaseProject
from hyo2.qc.common.helper import Helper
from hyo2.qc.common.writers.s57_writer import S57Writer
from hyo2.qc.common.writers.kml_writer import KmlWriter
from hyo2.qc.common.writers.shp_writer import ShpWriter
from hyo2.qc.chart.scan.base_scan import scan_algos
from hyo2.qc.chart.scan.feature_scan_v3 import FeatureScanV3
from hyo2.qc.chart.triangle.base_triangle import triangle_algos, sounding_units
from hyo2.qc.chart.triangle.triangle_rule_v2 import TriangleRuleV2

logger = logging.getLogger(__name__)


class ChartProject(BaseProject):

    def __init__(self, output_folder=None, profile=BaseProject.project_profiles['office'], progress=CliProgress()):

        super().__init__(projects_folder=output_folder, profile=profile, progress=progress)

        # scan features
        self._scan = None
        self.file_scan_s57 = str()
        self.file_scan_pdf = str()
        self.scan_msg = str()

        # triangle features
        self._triangle = None
        self.file_triangle_s57 = str()
        self.triangle_msg = str()

    def clear_data(self):
        super().clear_data()

        # scan features
        self._scan = None
        self.file_scan_s57 = str()
        self.file_scan_pdf = str()
        self.scan_msg = str()

        # triangle features
        self._triangle = None
        self.file_triangle_s57 = str()
        self.triangle_msg = str()

    # ________________________________________________________________________________
    # #############################  TRUNCATION METHODS  #############################

    def grid_truncate(self, version=2, decimal_places=1):

        if not self.has_bag_grid():
            logger.warning('No BAG files for truncation')
            return False

        if version not in [2, ] or not isinstance(version, int):
            logger.warning('Invalid version: %s' % version)
            return False

        if (decimal_places < 0) or not isinstance(decimal_places, int):
            logger.warning('Invalid version: %s' % version)
            return False

        opened_folders = list()
        for i, grid_file in enumerate(self.grid_list):

            self.progress.start(text="Data processing [%d/%d]" % (i + 1, len(self.grid_list)))

            self.clear_survey_label()
            survey_label = self.make_survey_label_from_path(grid_file)
            self.progress.update(value=20)

            # output naming
            output_name = str(os.path.basename(grid_file).split(".")[0]) + \
                          ".truncV" + str(version) + "d" + str(decimal_places) + ".bag"
            if self.output_project_folder:
                output_folder = os.path.join(self.output_folder, survey_label)
            else:
                output_folder = self.output_folder
            if self.output_subfolders:
                output_path = os.path.join(output_folder, "grid_truncate", output_name)
            else:
                output_path = os.path.join(output_folder, output_name)
            output_folder = os.path.dirname(output_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            self.progress.update(value=30)

            success = self._gr.truncate(input_file=grid_file, output_file=output_path, decimal_places=decimal_places)
            self.progress.end()
            if (output_folder not in opened_folders) and success:
                Helper.explore_folder(output_folder)
                opened_folders.append(output_folder)

        return True

    def grid_xyz(self, version=1, geographic=True, elevation=False, truncate=False, decimal_places=0):

        if not self.has_bag_grid():
            logger.warning('No BAG files for truncation')
            return False

        if version not in [1, ] or not isinstance(version, int):
            logger.warning('Invalid version: %s' % version)
            return False

        if not isinstance(geographic, bool):
            logger.warning('Invalid geographic parameter: %s' % geographic)
            return False

        logger.debug("geographic: %s, elevation: %s, truncate: %s, decimal places: %s"
                     % (geographic, elevation, truncate, decimal_places))

        opened_folders = list()
        for i, grid_file in enumerate(self.grid_list):

            start_time = time.time()

            self.progress.start(text="Data processing [%d/%d]" % (i + 1, len(self.grid_list)))

            self.clear_survey_label()
            survey_label = self.make_survey_label_from_path(grid_file)
            self.progress.update(value=20)

            # output naming
            output_name = str(os.path.basename(grid_file).split(".")[0]) + ".V" + str(version)
            if elevation:
                output_name += ".elevation"
            else:
                output_name += ".depth"
            if truncate:
                output_name += ".trunc" + str(decimal_places)
            if geographic:
                output_name += ".wgs84"
            output_name += ".xyz"
            if self.output_project_folder:
                output_folder = os.path.join(self.output_folder, survey_label)
            else:
                output_folder = self.output_folder
            if self.output_subfolders:
                output_path = os.path.join(output_folder, "grid_xyz", output_name)
            else:
                output_path = os.path.join(output_folder, output_name)
            output_folder = os.path.dirname(output_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            self.progress.update(value=30)

            success = self._gr.xyz(input_file=grid_file, output_file=output_path,
                                   geographic=geographic, elevation=elevation,
                                   truncate=truncate, decimal_places=decimal_places)
            self.progress.end()
            if (output_folder not in opened_folders) and success:
                Helper.explore_folder(output_folder)
                opened_folders.append(output_folder)

            logger.info("BAG xyz -> execution time: %.3f s" % (time.time() - start_time))

        return True

    def s57_truncate(self, version=2, decimal_places=1):

        if len(self.s57_list) == 0:
            logger.warning('No selected S57 files to use for truncation')
            return

        if version not in [2, ] or not isinstance(version, int):
            logger.warning('Invalid version: %s' % version)
            return False

        if (decimal_places < 0) or not isinstance(decimal_places, int):
            logger.warning('Invalid version: %s' % version)
            return False

        opened_folders = list()
        for i, s57_file in enumerate(self.s57_list):

            start_time = time.time()

            self.progress.start(text="Data processing [%d/%d]" % (i + 1, len(self.grid_list)))

            self.clear_survey_label()
            survey_label = self.make_survey_label_from_path(s57_file)
            self.progress.update(value=20)

            # output naming
            output_name = str(os.path.basename(s57_file).split(".")[0]) + \
                              ".truncV" + str(version) + "d" + str(decimal_places) + ".000"
            if self.output_project_folder:
                output_folder = os.path.join(self.output_folder, survey_label)
            else:
                output_folder = self.output_folder
            if self.output_subfolders:
                output_path = os.path.join(output_folder, "s57_truncate", output_name)
            else:
                output_path = os.path.join(output_folder, output_name)
            output_folder = os.path.dirname(output_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            self.progress.update(text="S57 data loading", value=30)

            self.progress.update(text="S57 data truncating", value=40)

            success = self._ft.truncate(input_file=s57_file, output_file=output_path, decimal_places=decimal_places)
            self.progress.end()
            if (output_folder not in opened_folders) and success:
                Helper.explore_folder(output_folder)
                opened_folders.append(output_folder)

            logger.info("BAG truncate -> execution time: %.3f s" % (time.time() - start_time))

        return True

    # ________________________________________________________________________________
    # ############################# SCAN PROCESS METHODS #############################

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

    def feature_scan(self, version, specs_version):

        # sanity checks
        # - version
        if not isinstance(version, int):
            raise RuntimeError("passed invalid type for version: %s" % type(version))

        if version not in [3, ]:
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

            # retrieve the ss file if present
            if len(self.ss_list) == 0:
                ss_file = None
                logger.info('add SS before the feature scan for extended functionality')
            else:
                ss_file = self.ss_list[0]

            # switcher between different versions of feature scan
            if version == 3:
                self._feature_scan(feature_file=s57_file, ss_file=ss_file,
                                   version=version, specs=specs_version,
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

    def _feature_scan(self, feature_file, ss_file, version, specs, idx, total):
        """ feature scan in the loaded s57 features """
        logger.debug('feature scan v%d ...' % version)

        self.progress.start(title="Feature scan v.%d" % version,
                            text="S57 data loading")  # % (idx, total)) - multi-input currently disabled

        try:
            self.read_feature_file(feature_path=feature_file)

        except Exception as e:
            traceback.print_exc()
            self.progress.end()
            raise e

        if ss_file is not None:
            self.progress.update(text="SS data loading", value=20)

            try:
                self.read_ss_file(ss_path=ss_file)

            except Exception as e:
                traceback.print_exc()
                self.progress.end()
                raise e

        try:

            if version == 3:

                if not self.has_s57():
                    logger.warning("first load some features")
                    return

                self.progress.update(text="Initialize Feature Scan v%d" % version, value=30)
                if self.has_ss():
                    self._scan = FeatureScanV3(s57=self.cur_s57, ss=self.cur_ss, version=specs,
                                               progress=self.progress)
                else:
                    self._scan = FeatureScanV3(s57=self.cur_s57, ss=None, version=specs,
                                               progress=self.progress)

                self.progress.update(text="Run Feature Scan v%d" % version, value=40)
                start_time = time.time()
                self._scan.run()
                logger.info("scan features v3 -> execution time: %.3f s" % (time.time() - start_time))

            else:
                RuntimeError("unknown Feature Scan version: %s" % version)

        except Exception as e:
            traceback.print_exc()
            self._scan = None
            self.progress.end()
            raise e

        self.progress.end()

    # ________________________________________________________________________________
    # ##########################    SCAN EXPORT METHODS     ##########################

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
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        if self._scan.type == scan_algos['FEATURE_SCAN_v3']:

            if self._scan.version == '2014':
                output_pdf = os.path.join(output_folder, "%s.CFSv3.2014.pdf" % self.cur_s57_basename)
                title_pdf = "Chart Feature Scan v3 - Tests against HCell Specs 2014"

            elif self._scan.version == '2016':
                output_pdf = os.path.join(output_folder, "%s.CFSv3.2016.pdf" % self.cur_s57_basename)
                title_pdf = "Chart Feature Scan v3 - Tests against HCell Specs 2016"

            elif self._scan.version == '2018':
                output_pdf = os.path.join(output_folder, "%s.CFSv3.2018.pdf" % self.cur_s57_basename)
                title_pdf = "Chart Feature Scan v3 - Tests against HCell Specs 2018"

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
    # ############################# TRIANGLE RULE METHODS ############################

    @property
    def triangle_features(self):
        if self.number_of_triangle_features():
            return self._triangle.flagged_features

        else:
            return list()

    def number_of_triangle_features(self):
        if not self._triangle:
            return 0

        return len(self._triangle.flagged_features[0])

    def triangle_rule(self, version=2, use_valsous=False, use_depcnts=False, detect_deeps=False,
                      sounding_unit=sounding_units['feet'], meter_th=1.0):

        if len(self.s57_list) == 0:
            logger.warning('No selected S57 CS file to use for triangle rule')
            return

        if len(self.ss_list) == 0:
            logger.warning('No selected S57 SS file to use for triangle rule')
            return

        # for each file in the project grid list
        self.triangle_msg = "Flagged features per input:\n"
        opened_folders = list()

        for i, ss_file in enumerate(self.ss_list):

            # we want to be sure that the label is based on the name of the new file input
            self.clear_survey_label()

            s57_file = self.s57_list[0]

            # switcher between different versions of feature scan
            if version in [2, ]:
                self._triangle_rule(ss_file=ss_file, s57_file=s57_file, cs_file=None,
                                    version=version, use_valsous=use_valsous, use_depcnt=use_depcnts,
                                    detect_deeps=detect_deeps, sounding_unit=sounding_unit, meter_th=meter_th,
                                    idx=(i + 1), total=len(self.ss_list))
            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Triangle Rule version: %s" % version)

            # export the flagged features
            saved = self._export_triangle_rule()
            if self.cur_s57_basename:
                self.triangle_msg += "- %s: %d\n" % (self.cur_s57_basename, self.number_of_triangle_features())

            # open the output folder (if not already open)
            if saved:
                if self._triangle_output_folder not in opened_folders:
                    self._open_triangle_output_folder()
                    opened_folders.append(self._triangle_output_folder)

            self.raise_window()

    def _triangle_rule(self, ss_file, s57_file, cs_file, use_valsous, use_depcnt, sounding_unit, detect_deeps,
                       meter_th, version, idx, total):
        """ triangle rule application"""
        logger.debug('triangle rule v%d ...' % version)

        self.progress.start(text="SS data loading")  # % (idx, total)) - multi-input currently disabled

        try:
            self.read_ss_file(ss_path=ss_file)

        except Exception as e:
            traceback.print_exc()
            self.progress.end()
            raise e

        if s57_file is not None:
            self.progress.update(text="S57 data loading", value=10)

            try:
                self.read_feature_file(feature_path=s57_file)

            except Exception as e:
                traceback.print_exc()
                self.progress.end()
                raise e

        try:

            if version in [2, ]:

                self.progress.update(text="Initialize Triangle Rule v%d" % version, value=30)

                self._triangle = TriangleRuleV2(ss=self.cur_ss, s57=self.cur_s57, cs=None,
                                                use_valsous=use_valsous, use_contours=use_depcnt,
                                                detect_deeps=detect_deeps, sounding_unit=sounding_unit,
                                                multiplier=meter_th,
                                                progress=self.progress)

                self.progress.update(text="Run Triangle Rule v%d" % version, value=40)
                start_time = time.time()
                self._triangle.run()
                logger.info("triangle rule v%d -> execution time: %.3f s" % (version, time.time() - start_time))
                logger.info("nr. of flagged features: %d" % self.number_of_triangle_features())

            else:
                raise RuntimeError("unknown Triangle Rule version: %s" % version)

        except Exception as e:
            traceback.print_exc()
            self._triangle = None
            self.progress.end()
            raise e

        self.progress.end()

    # ________________________________________________________________________________
    # ##########################    TRIANGLE EXPORT METHODS     ##########################

    def _export_triangle_rule(self):
        """ export flagged features """
        logger.debug('exporting flagged features ...')
        saved_s57 = self._save_triangle_features()
        logger.debug('exporting flagged features: done')
        return saved_s57

    def _save_triangle_features(self):
        """Save flagged features in S57"""

        if self.number_of_triangle_features() == 0:
            logger.warning("no flagged features to save")
            return False

        # make up the output folder (creating it if it does not exist)
        if self.output_project_folder:
            output_folder = os.path.join(self.output_folder, self._survey)
        else:
            output_folder = self.output_folder
        if self.output_subfolders:
            output_folder = os.path.join(output_folder, "triangle_rule")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # make the filename for output
        if self._triangle.type == triangle_algos['TRIANGLE_RULE_v2']:

            name = "%s.TRv2" % self.cur_s57_basename

            if self._triangle.use_valsous:
                name += ".valsou"

            if self._triangle.use_contours:
                name += ".contour"

            if self._triangle.detect_deeps:
                name += ".deeps"

            if self._triangle.csu == sounding_units['feet']:
                name += ".feet"
            elif self._triangle.csu == sounding_units['meters']:
                multi_str = "%.3f" % self._triangle.multiplier
                name += ".%s_m" % (multi_str.replace(".", "_"))
            else:
                name += ".fathoms"

            feature_file = os.path.join(output_folder, "%s" % name)
            s57_file1 = os.path.join(output_folder, "%s.blue_notes.000" % name)
            s57_file2 = os.path.join(output_folder, "%s.soundings.000" % name)
            tin_file = os.path.join(output_folder, "%s.TIN.000" % name)

        else:
            raise RuntimeError("Not implemented triangle rule algorithm")

        S57Writer.write_bluenotes(feature_list=self._triangle.flagged_features, path=s57_file1)
        # we need to convert the note back to float for soundings
        float_flagged_features = [self._triangle.flagged_features[0], self._triangle.flagged_features[1], []]
        for ft in self._triangle.flagged_features[2]:
            float_flagged_features[2].append(float(ft))
        S57Writer.write_soundings(feature_list=float_flagged_features, path=s57_file2, list_of_list=True)
        self.file_triangle_s57 = s57_file1
        S57Writer.write_tin(feature_list_a=self._triangle.edges_a, feature_list_b=self._triangle.edges_b, path=tin_file)

        try:
            out_file = feature_file
            if self.output_kml:
                KmlWriter().write_bluenotes(feature_list=self._triangle.flagged_features, path=out_file)
            if self.output_shp:
                ShpWriter().write_bluenotes(feature_list=self._triangle.flagged_features, path=out_file)

            out_file = tin_file[:-4]
            if self.output_kml:
                KmlWriter().write_tin(feature_list_a=self._triangle.edges_a, feature_list_b=self._triangle.edges_b,
                                      path=out_file)
            if self.output_shp:
                ShpWriter().write_tin(feature_list_a=self._triangle.edges_a, feature_list_b=self._triangle.edges_b,
                                      path=out_file)

        except Exception as e:
            traceback.print_exc()
            logger.info("issue in writing shapefile/kml: %s" % e)

        return True

    def _open_triangle_output_folder(self):
        if self.file_triangle_s57:
            Helper.explore_folder(os.path.dirname(self.file_triangle_s57))

        else:
            logger.warning('unable to define the output folder to open')

    @property
    def _triangle_output_folder(self):
        if self.file_triangle_s57:
            return os.path.dirname(self.file_triangle_s57)

        else:
            logger.warning('unable to define the output folder to open')
            return str()
