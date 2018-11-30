import os
import logging

logger = logging.getLogger(__name__)

from hyo2.qc.survey.submission.base_submission import BaseSubmission, submission_algos, specs_vers


class SubmissionChecksV3(BaseSubmission):
    def __init__(self, root, version="2017", recursive=False, office=False, opr=True, noaa_only=True):

        super().__init__(root=root, opr=opr)
        self.type = submission_algos["SUBMISSION_CHECKS_v3"]

        self.recursive = recursive
        self.office = office

        try:
            _ = specs_vers[version]
        except Exception as e:
            RuntimeError("invalid or unsupported version: %s" % version)

        self.version = version

        self.noaa_only = noaa_only

    def run(self):
        """Execute algorithm"""
        logger.info("Submission Checks V3 against HSSD %s [recursive: %s, office: %s]"
                    % (self.version, self.recursive, self.office))
        logger.info("Using root %s" % (self.root,))

        if self.root_is_project:
            self._check_xnnnnns()
            if self.version in ["2016", "2017"]:
                self._check_project_reports()

        elif self.root_is_survey:
            self.xnnnnn_paths.append(self.root)
            self.cur_xnnnnn_path = self.xnnnnn_paths[-1]
            self.xnnnnns.append(os.path.basename(self.root))
            self.cur_xnnnnn = self.xnnnnns[-1]
            self._check_xnnnnn_children()

        else:
            raise RuntimeError("unable to identify the kind of passed folder: %s" % self.root)

        self._check_file_lengths()

        self._finalize_summary()

    # ------- X###### METHODS --------

    def _check_xnnnnns(self):
        # it also populate the list of survey folders
        if not self._check_xnnnnn_valid():
            if self.recursive:
                return

        for i, self.cur_xnnnnn_path in enumerate(self.xnnnnn_paths):

            self.cur_xnnnnn = self.xnnnnns[i]

            # check "X#####"
            tree = "%s" % self.project
            value = self.cur_xnnnnn
            if not self._check_path_value_exists(path=self.project_path, tree=tree, value=value):
                if self.recursive:
                    return

            if self.version in ["2016", "2017"]:
                # check "Data"
                tree = "%s/%s" % (self.project, self.cur_xnnnnn)
                value = "Data"
                if not self._check_path_value_exists(path=self.cur_xnnnnn_path, tree=tree, value=value):
                    if self.recursive:
                        return
            else:
                # check "Raw"
                tree = "%s/%s" % (self.project, self.cur_xnnnnn)
                value = "Raw"
                if not self._check_path_value_exists(path=self.cur_xnnnnn_path, tree=tree, value=value):
                    if self.recursive:
                        return
            self._check_xnnnnn_children()

    def _check_xnnnnn_children(self):

        if self.version in ["2016", "2017"]:
            self._check_xnnnnn_data_preprocess()
            self._check_xnnnnn_data_processed()
            self._check_xnnnnn_data_separates()
            self._check_xnnnnn_data_dr()
            self._check_xnnnnn_data_pr_and_cp()
        else:
            self._check_xnnnnn_raw()
            self._check_xnnnnn_processed()

    def _check_xnnnnn_valid(self):
        if self.cur_xnnnnn is None:
            self.report += "Check for %s [CHECK]" % (self.project, )
        else:
            self.report += "Check for %s/%s [CHECK]" % (self.project, self.cur_xnnnnn)

        found = False

        for root, dirs, files in os.walk(self.root):

            for d in dirs:

                cur_path = os.path.join(root, d)
                valid, reason = self.is_valid_survey_folder(path=cur_path, opr=self.opr)
                if valid:
                    found = True
                    self.xnnnnns.append(d)
                    self.xnnnnn_paths.append(cur_path)
                    continue

            break  # stop at the first level

        if not found:

            msg = "Unable to identify a valid X##### folder in %s" % self.root
            self.report += msg
            self.errors.append(msg)
            self.xnnnnn_paths.append(os.path.join(self.root, "X#####"))
            self.xnnnnns.append(os.path.basename(self.xnnnnn_paths[-1]))
            return False

        logger.debug('survey folders: %d' % len(self.xnnnnn_paths))
        self.report += "OK"
        return True

    def _check_xnnnnn_subfolder_valid(self, subpath, subtree):
        self.report += "Check for HXXXXX under %s [CHECK]" % subtree

        found = False

        for root, dirs, _ in os.walk(subpath):

            for d in dirs:

                cur_path = os.path.join(root, d)
                valid, reason = self.is_valid_survey_folder(path=cur_path, opr=self.opr, check_parent=False)
                if valid:
                    found = True
                    continue

                # logger.info("invalid: %s [%s]" % (cur_path, reason))

            break  # stop at the first level

        if not found:
            msg = "Unable to identify a valid X##### folder in %s" % subpath
            self.report += msg
            self.errors.append(msg)
            return False

        self.report += "OK"
        return True

    # 2016 and 2017

    def _check_xnnnnn_data_preprocess(self):
        # check "Data/Preprocess"
        path = os.path.join(self.cur_xnnnnn_path, "Data")
        tree = "%s/%s/Data" % (self.project, self.cur_xnnnnn)

        value = "Preprocess"
        if not self._check_path_value_exists(path=path, tree=tree, value=value):
            if self.recursive:
                return

        if self.version == "2016":

            subs = [
                ["Backscatter", ],
                ["Bathymetry", ],
                ["Bathymetry", "MBES"],
                ["Bathymetry", "SBES"],
                ["Features", ],
                ["Positioning", ],
                ["SSS", ],
                ["SVP", ],
            ]

        else:  # 2017

            subs = [
                ["Features", ],
                ["MBES"],
                ["SBES"],
                ["SSS", ],
                ["SVP", ],
            ]

        for sub in subs:
            sub_path = os.path.join(path, value, *sub)
            sub_tree = "%s/%s/%s" % (tree, value, "/".join(sub))
            self._check_path_exists(path=sub_path, tree=sub_tree)

    def _check_xnnnnn_data_processed(self):
        # check "Data/Processed"
        path = os.path.join(self.cur_xnnnnn_path, "Data")
        tree = "%s/%s/Data" % (self.project, self.cur_xnnnnn)

        value = "Processed"
        if not self._check_path_value_exists(path=path, tree=tree, value=value):
            if self.recursive:
                return

        is_caris_user = False
        if self.version == "2016":

            subs = [
                ["Bathymetry_&_SSS", ],
                ["GNSS_Data", ],
                ["GNSS_Data", "SBET"],
                ["Multimedia", ],
                ["S-57 Files", ],
                ["S-57 Files", "Final_Feature_File"],
                ["S-57 Files", "Side_Scan_Sonar_Contacts"],
                ["SVP", ],
                ["Tide", ],
            ]

        else:  # 2017

            subs = [
                ["GNSS_Data", ],
                ["GNSS_Data", "SBET"],
                ["Multimedia", ],
                ["S-57_Files", ],
                ["S-57_Files", "Final_Feature_File"],
                ["S-57_Files", "Side_Scan_Sonar_Contacts"],
                ["Sonar_Data", ],
                ["Sonar_Data", "Surfaces_&_Mosaics"],
                ["SVP", ],
                ["Water_Levels", ],
            ]

            is_caris_user = os.path.exists(os.path.join(path, value, "Sonar_Data", "HDCS_Data"))
            logger.debug("is CARIS user: %s" % is_caris_user)

            if is_caris_user:

                subs.append(["Sonar_Data", "HDCS_Data", "VesselConfig"])

            else:

                subs.append(["Sonar_Data", "VesselConfig"])

        for sub in subs:
            sub_path = os.path.join(path, value, *sub)
            sub_tree = "%s/%s/%s" % (tree, value, "/".join(sub))
            self._check_path_exists(path=sub_path, tree=sub_tree)

        if self.version == "2017":

            # logger.debug("checking for HXXXXX under Processed: %s" % path)

            if is_caris_user:

                sub_path = os.path.join(path, value, "Sonar_Data", "HDCS_Data")
                sub_tree = "%s/%s/%s" % (tree, value, "/".join(["Sonar_Data", "HDCS_Data"]))

            else:

                sub_path = os.path.join(path, value, "Sonar_Data")
                sub_tree = "%s/%s/%s" % (tree, value, "/".join(["Sonar_Data", ]))

            self._check_xnnnnn_subfolder_valid(subpath=sub_path, subtree=sub_tree)

    def _check_xnnnnn_data_separates(self):
        # check "Data/Separates"
        path = os.path.join(self.cur_xnnnnn_path, "Data")
        tree = "%s/%s/Data" % (self.project, self.cur_xnnnnn)

        value = "Separates"
        if not self._check_path_value_exists(path=path, tree=tree, value=value):
            if self.recursive:
                return

        subs = [
            ["I_Acquisition_&_Processing_Logs", ],
            ["I_Acquisition_&_Processing_Logs", "Acquisition_Logs"],
            ["I_Acquisition_&_Processing_Logs", "Detached_Positions"],
            ["I_Acquisition_&_Processing_Logs", "Processing_Logs"],
            ["II_Digital_Data", ],
            ["II_Digital_Data", "Checkpoint_Summary_&_Crossline_Comparisons"],
            ["II_Digital_Data", "Sound_Speed_Data_Summary"],
        ]

        for sub in subs:
            sub_path = os.path.join(path, value, *sub)
            sub_tree = "%s/%s/%s" % (tree, value, "/".join(sub))
            self._check_path_exists(path=sub_path, tree=sub_tree)

    def _check_xnnnnn_data_dr(self):
        # check "Data/Descriptive_Report"
        path = os.path.join(self.cur_xnnnnn_path, "Data")
        tree = "%s/%s/Data" % (self.project, self.cur_xnnnnn)

        value = "Descriptive_Report"
        if not self._check_path_value_exists(path=path, tree=tree, value=value):
            if self.recursive:
                return

        if self.version == "2016":

            subs = [
                ["Report", ],
                ["Appendices", ],
                ["Appendices", "I_Tides_&_Water_Levels"],
                ["Appendices", "II_Supplemental_Survey_Records_&_Correspondence"],
            ]

        else:  # 2017

            subs = [
                ["Report", ],
                ["Appendices", ],
                ["Appendices", "I_Water_Levels"],
                ["Appendices", "II_Supplemental_Survey_Records_&_Correspondence"],
            ]

        for sub in subs:
            sub_path = os.path.join(path, value, *sub)
            sub_tree = "%s/%s/%s" % (tree, value, "/".join(sub))
            self._check_path_exists(path=sub_path, tree=sub_tree)

    def _check_xnnnnn_data_pr_and_cp(self):
        # check "Data/Public_Relations_&_Constituent_Products"
        path = os.path.join(self.cur_xnnnnn_path, "Data")
        tree = "%s/%s/Data" % (self.project, self.cur_xnnnnn)

        value = "Public_Relations_&_Constituent_Products"
        if not self._check_path_value_exists(path=path, tree=tree, value=value):
            if self.recursive:
                return

    #2018

    def _check_xnnnnn_raw(self):

        # check "Raw"
        path = os.path.join(self.cur_xnnnnn_path, "Raw")
        tree = "%s/%s/Raw" % (self.project, self.cur_xnnnnn)

        subs = [
            ["Features", ],
            ["MBES"],
            ["Positioning", ],
            ["SBES"],
            ["SSS", ],
            ["SVP", ],
            ["WC", ],
        ]

        for sub in subs:
            sub_path = os.path.join(path, *sub)
            sub_tree = "%s/%s" % (tree, "/".join(sub))
            self._check_path_exists(path=sub_path, tree=sub_tree)

    def _check_xnnnnn_processed(self):

        # check "Processed"
        path = os.path.join(self.cur_xnnnnn_path, "Processed")
        tree = "%s/%s/Processed" % (self.project, self.cur_xnnnnn)

        subs = [
            ["GNSS_Data", ],
            ["SBET", ],
            ["Multimedia", ],
            ["Reports", "Project", "DAPR", "Report", ],
            ["Reports", "Project", "DAPR", "Appendices", ],
            ["Reports", "Project", "HVCR", "Digital_A-Vertical_Control_Report", ],
            ["Reports", "Project", "HVCR", "Digital_B-Horizontal_Control_Data", "ATON_Data", ],
            ["Reports", "Project", "HVCR", "Digital_B-Horizontal_Control_Data", "Base_Station_Data", ],
            ["Reports", "Project", "Project_Correspondence", ],
            ["Reports", "Survey", "Descriptive_Report", "Appendices", "I_Water_Levels", ],
            ["Reports", "Survey", "Descriptive_Report", "Appendices", "II_Supplemental_Survey_Records_Correspondence", ],
            ["Reports", "Survey", "Descriptive_Report", "Report", ],
            ["Reports", "Survey", "Public_Relations_Constituent_Products", ],
            ["Reports", "Survey", "Separates", "I_Acquisition_Processing_Logs", "Detached_Positions", ],
            ["Reports", "Survey", "Separates", "II_Digital_Data", "Crossline_Comparisons", ],
            ["Reports", "Survey", "Separates", "II_Digital_Data", "Sound_Speed_Data_Summary", ],
            ["S-57_Files", "Final_Feature_File", ],
            ["S-57_Files", "Side_Scan_Sonar_Contacts", ],
            ["Surfaces_Mosaics", ],
            ["SVP", ],
            ["Water_Levels", ],
        ]

        if self.noaa_only:
            subs.append(["Sonar_Data", "%s_GSF" %(self.cur_xnnnnn)])

        is_caris_user = os.path.exists(os.path.join(path, "Sonar_Data", "HDCS_Data"))
        logger.debug("is CARIS user: %s" % is_caris_user)

        if is_caris_user:
            subs += [
                ["Sonar_Data", "HDCS_Data", "%s_MB" %(self.cur_xnnnnn), ],
                ["Sonar_Data", "HDCS_Data", "%s_SB" %(self.cur_xnnnnn), ],
                ["Sonar_Data", "HDCS_Data", "%s_SSS" %(self.cur_xnnnnn), ],
                ["Sonar_Data", "HDCS_Data", "%s_WC" %self.cur_xnnnnn, ],
                ["Sonar_Data", "HDCS_Data", "VesselConfig", ],
            ]

        else:
            subs += [
                ["Sonar_Data", "%s_MB" %(self.cur_xnnnnn), ],
                ["Sonar_Data", "%s_SB" %(self.cur_xnnnnn), ],
                ["Sonar_Data", "%s_SSS" %(self.cur_xnnnnn), ],
                ["Sonar_Data", "%s_WC" %(self.cur_xnnnnn), ],
                ["Sonar_Data", "VesselConfig", ],
            ]

        for sub in subs:
            sub_path = os.path.join(path, *sub)
            sub_tree = "%s/%s" % (tree, "/".join(sub))
            self._check_path_exists(path=sub_path, tree=sub_tree)


    # ------- PROJECT_REPORTS METHODS --------

    def _check_project_reports(self):

        if not self._check_project_reports_valid():
            if self.recursive:
                return

        self._check_project_reports_children()

    def _check_project_reports_valid(self):
        self.report += "Check for %s/%s [CHECK]" % (self.project, self.pr)

        found = False

        for root, dirs, files in os.walk(self.root):

            for d in dirs:

                if d == self.pr:
                    found = True
                    self.pr_path = os.path.join(root, d)
                    break

            break  # stop at the first level

        if not found:
            msg = "Unable to identify a valid '%s' folder in %s" % (self.pr, self.root)
            self.report += msg
            self.errors.append(msg)
            self.pr_path = os.path.join(self.root, self.pr)
            return False

        if not os.listdir(self.pr_path):
            msg = "Intentionally empty folder must have a Readme.txt file: %s " % self.pr_path
            self.report += msg
            self.errors.append(msg)
            return False

        self.report += "OK"
        return True

    def _check_project_reports_children(self):

        # check "Data/Preprocess"

        tree = "%s/Project_Reports" % self.project

        subs = [
            ["Data_Acquisition_&_Processing_Report", ],
            ["Data_Acquisition_&_Processing_Report", "Report"],
            ["Data_Acquisition_&_Processing_Report", "Appendices"],
            ["Horizontal_&_Vertical_Control_Report", ],
            ["Horizontal_&_Vertical_Control_Report", "Digital_A-Vertical_Control_Report"],
            ["Horizontal_&_Vertical_Control_Report", "Digital_B-Horizontal_Control_Data"],
            ["Horizontal_&_Vertical_Control_Report", "Digital_B-Horizontal_Control_Data", "ATON_Data"],
            ["Horizontal_&_Vertical_Control_Report", "Digital_B-Horizontal_Control_Data", "Base_Station_Data"],
            ["Project_Correspondence", ],
        ]

        for sub in subs:
            sub_path = os.path.abspath(os.path.join(self.pr_path, *sub))
            sub_tree = "%s/%s" % (tree, "/".join(sub))
            self._check_path_exists(path=sub_path, tree=sub_tree)

    def _check_file_lengths(self):
        if self.office:
            max_len = 260
        else:
            max_len = 200

        issues = False

        self.report += "Check all path lengths < %s characters [CHECK]" % max_len

        for root, dirs, files in os.walk(self.root):

            for f in files:

                file_path = os.path.join(root, f)
                # logger.debug("file: %s" % file_path)
                if len(file_path) >= max_len:
                    issues = True
                    msg = "Too long [%d]: %s" % (len(file_path), file_path)
                    self.report += msg
                    self.errors.append(msg)

            for d in dirs:

                dir_path = os.path.join(root, d)
                # logger.debug("dir: %s" % dir_path)
                if len(dir_path) >= max_len:
                    issues = True
                    msg = "Too long [%d]: %s" % (len(dir_path), dir_path)
                    self.report += msg
                    self.errors.append(msg)

            if self.recursive and issues:
                break

        if not issues:
            self.report += "OK"

    # ------- COMMON METHODS --------

    def _check_path_value_exists(self, path, tree, value):
        self.report += "Check for %s/%s [CHECK]" % (tree, value)

        # this happens only with not-recursive mode
        if path is None:
            return False
        if not os.path.exists(path):
            msg = "Unable to identify a valid '%s' folder in %s" % (value, path)
            self.report += msg
            self.errors.append(msg)
            return False

        found = False

        for root, dirs, files in os.walk(path):

            for d in dirs:

                if d == value:
                    found = True
                    break

            break  # to stop at the first level

        if not found:
            msg = "Unable to identify a valid '%s' folder in %s" % (value, path)
            self.report += msg
            self.errors.append(msg)
            return False

        path_value = os.path.join(path, value)
        if not os.listdir(path_value):
            msg = "Intentionally empty folder must have a Readme.txt file: %s " % path_value
            self.report += msg
            self.errors.append(msg)
            return False

        self.report += "OK"
        return True

    def _check_path_exists(self, path, tree):
        self.report += "Check for %s [CHECK]" % (tree,)

        # this happens only with not-recursive mode
        if path is None:
            return False

        found = True

        if not os.path.exists(path):

            # special cases
            if "S-57 File" in path:
                _path = path.replace("S-57 File", "S-57_File")

                if os.path.exists(_path):
                    msg = "!WARNING! HSSD Appendix J prescribes 'S-57 File' (without '_'), " \
                          "but the folder is named %s" \
                          % (_path,)
                    self.report += msg
                    self.warnings.append(msg)
                    return False

                else:
                    found = False

            else:
                # print(path)
                found = False

        if not found:
            msg = "Unable to locate %s" % (path,)
            self.report += msg
            self.errors.append(msg)
            return False

        if not os.listdir(path):
            msg = "Intentionally empty folder must have a Readme.txt file: %s " % path
            self.report += msg
            self.errors.append(msg)
            return False

        self.report += "OK"
        return True

    def _finalize_summary(self):
        """Add a summary to the report"""

        # Add a summary to the report
        self.report += 'SUMMARY [TOTAL]'

        self.report += 'Identified errors: %s' % len(self.errors)
        self.report += 'Identified warnings: %s' % len(self.warnings)
