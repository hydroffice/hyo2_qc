import logging
from typing import List, Optional

from hyo2.qc.common import lib_info
from hyo2.qc.survey.scan.flags import Flags
from hyo2.qc.survey.scan.checks import Checks
from hyo2.abc.lib.helper import Helper
from hyo2.abc.app.report import Report
from hyo2.s57.s57 import S57File

logger = logging.getLogger(__name__)


class FeatureScanV11:

    def __init__(self, s57: S57File, profile: int = 0, version: str = "2021",
                 survey_area: int = Checks.survey_areas["Pacific Coast"], use_mhw: bool = False, mhw_value: float = 0.0,
                 sorind: Optional[str] = None, sordat: Optional[str] = None, multimedia_folder: Optional[str] = None,
                 check_image_names: bool = False):
        self.type = 'FEATURE_SCAN_v11'
        self.s57 = s57
        
        self.flags = Flags()
        self.report = Report(lib_name=lib_info.lib_name, lib_version=lib_info.lib_version)
        self.checks = Checks(flags=self.flags, report=self.report, all_features=self.s57.rec10s,
                             survey_area=survey_area, version=version,
                             sorind=sorind, sordat=sordat, profile=profile,
                             use_mhw=use_mhw, mhw_value=mhw_value, check_image_names=check_image_names, multimedia_folder=multimedia_folder)

    @property
    def version(self) -> str:
        return self.checks.version

    @property
    def flagged_features(self) -> List[list]:
        return self.flags.features

    def info_settings(self) -> None:
        msg = "Feature Scan settings:\n"
        msg += "- HSSD version: %s\n" % self.checks.version
        msg += "- nr. on features in the S57 file: %d\n" % len(self.checks.all_fts)
        msg += "- profile: %s\n" % ("field" if (self.checks.profile == 1) else "office")
        msg += "- survey area: %s\n" % Helper.first_match(Checks.survey_areas, self.checks.survey_area)
        msg += "- use MHW: %s [%s]\n" % (self.checks.use_mhw, self.checks.mhw_value)
        msg += "- check SORIND: %s\n" % (self.checks.sorind,)
        msg += "- check SORDAT: %s\n" % (self.checks.sordat,)
        msg += "- use HTD: %s \n" % (self.checks.check_image_names,)
        logger.info(msg)

    def run(self) -> None:
        """Execute the set of check of the feature scan algorithm"""
        if self.checks.version not in ["2019", "2020", "2021"]:
            raise RuntimeError("unsupported specs version: %s" % self.checks.version)

        self.info_settings()

        self.checks.file_consistency()
        self.checks.assigned_features()
        self.checks.new_or_updated_features()
        self.checks.new_or_deleted_features()
        self.checks.images()

        self.checks.soundings()
        self.checks.dtons()
        self.checks.wrecks()
        self.checks.rocks()
        self.checks.obstructions()
        self.checks.platforms()
        self.checks.sbdares()
        self.checks.moorings()
        self.checks.coastlines()
        self.checks.lands()
        self.checks.coverages()

        self.checks.office_only()

        self.checks.finalize_summary()
