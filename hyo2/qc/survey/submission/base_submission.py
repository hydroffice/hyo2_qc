import logging
import os

from hyo2.abc.app.report import Report
from hyo2.abc.lib.helper import Helper
from hyo2.qc.common import lib_info

logger = logging.getLogger(__name__)

submission_algos = {
    "BASE": 0,
    "SUBMISSION_CHECKS_v4": 4,
}

specs_vers = {
    "BASE": 0,
    "2020": 1,
    "2021": 2,
}


class BaseSubmission:

    pr = "Project_Reports"

    def __init__(self, root, opr):

        self.type = submission_algos["BASE"]
        self.version = specs_vers["BASE"]
        self.opr = opr

        # inputs
        if not os.path.exists(root):
            raise RuntimeError("The passed root path does not exist: %s" % root)
        self.root = os.path.abspath(root)
        self.root_is_project = False
        self.root_is_survey = False
        self.root_is_report = False

        # identify project folder
        if self.is_valid_project_folder(self.root, opr=self.opr)[0]:
            self.project = os.path.basename(self.root)
            self.project_path = self.root
            self.root_is_project = True

        elif self.is_valid_survey_folder(self.root, opr=self.opr)[0]:
            self.project_path = os.path.abspath(os.path.join(self.root, os.pardir))
            self.project = os.path.basename(self.project_path)
            self.root_is_survey = True

        elif self.is_valid_report_folder(self.root, opr=self.opr)[0]:
            self.project_path = os.path.abspath(os.path.join(self.root, os.pardir))
            self.project = os.path.basename(self.project_path)
            self.root_is_report = True

        else:
            raise RuntimeError("Unable to identify the kind of root folder: %s" % self.root)

        logger.debug("project folder: %s" % self.project_path)

        self.xnnnnns = list()
        self.xnnnnn_paths = list()

        self.cur_xnnnnn = None
        self.cur_xnnnnn_path = None

        self.pr_path = None

        # outputs
        self.errors = list()
        self.warnings = list()

        # report
        self.report = Report(lib_name=lib_info.lib_name, lib_version=lib_info.lib_version)

    @classmethod
    def is_valid_project_folder(cls, path, version="2020", opr=True):
        if version not in specs_vers.keys():
            return False, "passed invalid or unsupported version: %s" % version

        if not os.path.exists(path=path):
            return False, "the passed root path does not exist: %s" % path

        basename = os.path.basename(path)
        if opr:
            if len(basename) < 14:
                return False, "invalid number of characters in %s: %d" % (basename, len(basename))

        tokens = basename.split("-")
        if len(tokens) < 4:
            return False, "invalid number of '-' characters: %s" % path

        # part 1: OPR-
        p = 0

        if opr:
            if tokens[p] not in ["OPR", ]:
                return False, "invalid part #1 '%s': %s" % (tokens[p], path)

        # part 2: -X###-
        p = 1
        if len(tokens[p]) < 4:
            return False, "invalid number of characters in X###: %s" % tokens[p]

        c = 0
        if not tokens[p][c].isalpha():
            return False, "part #%d, char #%d '%s' is not alphabetic: %s" % (p, c, tokens[p][c], path)
        if not tokens[p][c].isupper():
            return False, "part #%d, char #%d '%s' is not upper case: %s" % (p, c, tokens[p][c], path)

        c = 1
        if not tokens[p][c].isdigit():
            return False, "part #%d, char #%d '%s' is not a digit: %s" % (p, c, tokens[p][c], path)
        c = 2
        if not tokens[p][c].isdigit():
            return False, "part #%d, char #%d '%s' is not a digit: %s" % (p, c, tokens[p][c], path)
        c = 3
        if not tokens[p][c].isdigit():
            return False, "part #%d, char #%d '%s' is not a digit: %s" % (p, c, tokens[p][c], path)

        # part 3: -XX-
        p = 2
        if len(tokens[p]) < 2:
            return False, "invalid number of characters in XX: %s" % tokens[p]

        c = 0
        if not tokens[p][c].isalpha():
            return False, "part #%d, char #%d '%s' is not alphabetic: %s" % (p, c, tokens[p][c], path)
        if not tokens[p][c].isupper():
            return False, "part #%d, char #%d '%s' is not upper case: %s" % (p, c, tokens[p][c], path)

        c = 1
        if not tokens[p][c].isalpha():
            return False, "part #%d, char #%d '%s' is not alphabetic: %s" % (p, c, tokens[p][c], path)
        if not tokens[p][c].isupper():
            return False, "part #%d, char #%d '%s' is not upper case: %s" % (p, c, tokens[p][c], path)

        # part 4: -##
        p = 3

        c = 0
        if not tokens[p][c].isdigit():
            return False, "part #%d, char #%d '%s' is not a digit: %s" % (p, c, tokens[p][c], path)
        c = 1
        if not tokens[p][c].isdigit():
            return False, "part #%d, char #%d '%s' is not a digit: %s" % (p, c, tokens[p][c], path)

        return True, str()

    @classmethod
    def is_valid_survey_folder(cls, path, version="2020", check_parent=True, opr=True):
        if version not in specs_vers.keys():
            return False, "passed invalid or unsupported version: %s" % version

        if not os.path.exists(path=path):
            return False, "the passed root path does not exist: %s" % path

        basename = os.path.basename(path)
        if len(basename) < 6:
            return False, "invalid number of characters in %s: %d" % (basename, len(basename))

        if not basename[0].isalpha():
            return False, "invalid first character for survey folder: %s" % basename[0]

        if not basename[1:6].isdigit():
            return False, "invalid digit characters for survey folder: %s" % basename[1:6]

        if check_parent:

            parent_folder = os.path.abspath(os.path.join(path, os.pardir))
            valid, reason = BaseSubmission.is_valid_project_folder(path=parent_folder, version=version, opr=opr)
            if not valid:
                return False, "the parent folder is not a valid project folder: %s" % parent_folder

        return True, str()

    @classmethod
    def is_valid_report_folder(cls, path, version="2020", opr=True):
        if version not in specs_vers.keys():
            return False, "passed invalid or unsupported version: %s" % version

        if not os.path.exists(path=path):
            return False, "the passed root path does not exist: %s" % path

        basename = os.path.basename(path)
        if basename != cls.pr:
            return False, "invalid %s name : %s" % (cls.pr, basename)

        parent_folder = os.path.abspath(os.path.join(path, os.pardir))
        valid, reason = BaseSubmission.is_valid_project_folder(path=parent_folder, version=version, opr=opr)
        if not valid:
            return False, "the parent folder is not a valid project folder: %s" % parent_folder

        return True, str()

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "    <type: %s>\n" % Helper.first_match(submission_algos, self.type)
        msg += "    <version: %s>\n" % Helper.first_match(specs_vers, self.version)
        msg += "    <root: %s>\n" % self.root
        msg += "    <name: %s>\n" % self.project
        msg += "    <errors: %d>\n" % len(self.errors)
        msg += "    <warnings: %d>\n" % len(self.warnings)

        return msg
