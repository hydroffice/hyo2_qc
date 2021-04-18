import logging
from typing import List, Optional

from hyo2.qc.common import lib_info
from hyo2.qc.common.s57_aux import S57Aux
from hyo2.qc.survey.scan.flags import Flags
from hyo2.qc.survey.scan.checks import Checks
from hyo2.abc.lib.helper import Helper
from hyo2.abc.app.report import Report
from hyo2.s57.s57 import S57File, S57Record10

logger = logging.getLogger(__name__)


class FeatureScanV11:

    def __init__(self, s57: S57File, profile: int = 0, version: str = "2021",
                 survey_area: int = Checks.survey_areas["Pacific Coast"], use_mhw: bool = False, mhw_value: float = 0.0,
                 sorind: Optional[str] = None, sordat: Optional[str] = None, multimedia_folder: Optional[str] = None,
                 use_htd: bool = False):
        self.type = 'FEATURE_SCAN_v11'
        self.s57 = s57
        
        self.flags = Flags()
        self.report = Report(lib_name=lib_info.lib_name, lib_version=lib_info.lib_version)
        self.checks = Checks(flags=self.flags, report=self.report, all_features=self.s57.rec10s,
                             survey_area=survey_area, version=version,
                             sorind=sorind, sordat=sordat, profile=profile,
                             use_mhw=use_mhw, mhw_value=mhw_value, use_htd=use_htd, multimedia_folder=multimedia_folder)

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
        msg += "- use HTD: %s \n" % (self.checks.use_htd,)
        logger.info(msg)

    def run(self) -> None:
        """Execute the set of check of the feature scan algorithm"""
        if self.checks.version not in ["2018", "2019", "2020", "2021"]:
            raise RuntimeError("unsupported specs version: %s" % self.checks.version)

        self.info_settings()

        self.checks.all_the_features()
        self.checks.new_or_updated_features()
        self.checks.assigned_features()
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

    def run_2020(self) -> None:
        """HSSD 2020 checks """

        # @ Ensure no feature redundancy
        self.report += "Redundant features [CHECK]"
        self.all_features = self.check_feature_redundancy_and_geometry()
        logger.debug("nr. of features after redundancy and geometry checks: %d" % len(self.all_features))

        # @ Remove carto features
        carto_filter = ['$AREAS', '$LINES', '$CSYMB', '$COMPS', '$TEXTS']
        no_carto_features = S57Aux.filter_by_object(objects=self.all_features, object_filter=carto_filter)

        # @ Isolate only features with descrp = New or Update
        new_update_features = S57Aux.select_by_attribute_value(objects=no_carto_features, attribute='descrp',
                                                               value_filter=['1', '2', ])
        # @ Ensure new or updated features have SORIND
        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORIND [CHECK]"
        self.flagged_sorind = self.check_features_for_attribute(new_update_features, 'SORIND')
        # @ Ensure new or updated features have valid SORIND
        self.report += "New or Updated features (excluding carto notes) with invalid SORIND [CHECK]"
        if self.sorind is None:
            self.flagged_sorind_invalid = self._check_features_for_valid_sorind(new_update_features, check_space=False)
        else:
            self.flagged_sorind_invalid = self._check_features_for_match_sorind(new_update_features)
        # @ Ensure new or updated features have SORDAT
        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORDAT [CHECK]"
        self.flagged_sordat = self.check_features_for_attribute(new_update_features, 'SORDAT')
        # @ Ensure new or updated features have valid SORDAT
        self.report += "New or Updated features (excluding carto notes) with invalid SORDAT [CHECK]"
        if self.sordat is None:
            self.flagged_sordat_invalid = self._check_features_for_valid_sordat(new_update_features)
        else:
            self.flagged_sordat_invalid = self._check_features_for_match_sordat(new_update_features)

        # @ Isolate only features that are assigned
        assigned_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='asgnmt',
                                                             value_filter=['2', ])
        # @ Ensure assigned features have descrp
        self.report += "Assigned features have empty or missing mandatory attribute description [CHECK]"
        self.flagged_description = self.flag_features_with_attribute_value(objects=assigned_features,
                                                                           attribute='descrp',
                                                                           values_to_flag=['', ],
                                                                           check_attrib_existence=True)

        # @ Ensure assigned features have remrks
        self.report += "Assigned features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks = self.check_features_for_attribute(objects=assigned_features, attribute='remrks')

        # @ Isolate features with descrp = New or Delete
        new_delete_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='descrp',
                                                               value_filter=['1', '3'])
        # @ Ensure new or deleted features have remrks
        self.report += "New/Delete features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks_features = self.check_features_for_attribute(
            objects=new_delete_features, attribute='remrks')

        # @ Ensure new or deleted features have recomd
        self.report += "New/Delete features missing mandatory attribute recommendation [CHECK]"
        self.flagged_recommend_features = self.check_features_for_attribute(objects=new_delete_features,
                                                                            attribute='recomd')

        # @ Isolate sounding features
        sounding_features = S57Aux.select_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        # @ Ensure soundings have tecsou
        self.report += "SOUNDG with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_soundings_tecsou = self.flag_features_with_attribute_value(sounding_features, attribute='TECSOU',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)
        # @ Ensure soundings have quasou
        self.report += "SOUNDG with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_soundings_quasou = self.flag_features_with_attribute_value(sounding_features, attribute='QUASOU',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)

        # @ Isolate features that are no-carto, descrp = New or Updated, and sftype = DTON
        dtons = S57Aux.select_by_attribute_value(objects=new_update_features, attribute='sftype', value_filter=['3', ])
        # @ Remove soundings to prevent WRECK and OBSTRN DtoN objects from getting the image flag twice.
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['WRECKS', 'OBSTRN'])
        # @ Ensure DTONs have images
        self.report += "Special feature types (DTONS) missing images [CHECK]"
        self.flagged_dtons = self.check_features_for_attribute(dtons, 'images')

        # @ Isolate new or updated wrecks
        wrecks = S57Aux.select_by_object(objects=new_update_features, object_filter=['WRECKS', ])
        # @ Ensure new or updated wrecks have images
        self.report += "New or Updated WRECKS missing images [CHECK]"
        self.flagged_wrecks_images = self.check_features_for_attribute(wrecks, 'images')
        # @ Ensure new or updated wrecks have catwrk
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute CATWRK [CHECK]"
        self.flagged_wrecks_catwrk = self.flag_features_with_attribute_value(wrecks, attribute='CATWRK',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Filter wrecks if they have a known, undefined, and unknown valsou.
        wrecks_valsou = S57Aux.select_by_attribute(objects=wrecks, attribute='VALSOU')
        logger.debug("Total number of wrecks without undefined VALSOU: %d" % (len(wrecks_valsou)))
        wrecks_undefined_valsou = S57Aux.filter_by_attribute(wrecks, attribute='VALSOU')
        logger.debug("Total number of wrecks with undefined VALSOU: %d" % (len(wrecks_undefined_valsou)))

        # Ensure wrecks with valsou contain watlev
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_watlev = self.flag_features_with_attribute_value(wrecks_valsou,
                                                                             attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure wrecks with unknown valsou have watlev unknown
        self.report += "New or Updated WRECKS with empty VALSOU shall have WATLEV of 'unknown' [CHECK]"
        self.flagged_wrecks_unknown_watlev = self.flag_features_with_attribute_value(wrecks_undefined_valsou,
                                                                                     attribute='WATLEV',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", ],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated wrecks have valsou
        self.report += "New or Updated WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_valsou = self.check_features_for_attribute(wrecks, 'VALSOU')

        # Ensure wrecks with valsou contain tecsou
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_wrecks_tecsou = self.flag_features_with_attribute_value(wrecks_valsou,
                                                                             attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure wrecks with unknown valsou have tecsou "unknown"
        self.report += "New or Updated WRECKS with empty VALSOU shall have TECSOU of 'unknown' [CHECK]"
        self.flagged_wrecks_unknown_tecsou = self.flag_features_with_attribute_value(wrecks_undefined_valsou,
                                                                                     attribute='TECSOU',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", "8", "9",
                                                                                                     "10", "11", "12",
                                                                                                     "13", "14", ],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated wrecks have quasou
        self.report += "New or Updated WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_quasou = self.flag_features_with_attribute_value(wrecks_valsou,
                                                                             attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure wrecks with unknown valsou have quasou "unknown"
        self.report += "New or Updated WRECKS with empty VALSOU shall have QUASOU of 'depth unknown' [CHECK]"
        self.flagged_wrecks_unknown_quasou = self.flag_features_with_attribute_value(wrecks_undefined_valsou,
                                                                                     attribute='QUASOU',
                                                                                     values_to_flag=["1", "3", "4", "5",
                                                                                                     "6", "7", "8", "9",
                                                                                                     "10", "11"],
                                                                                     check_attrib_existence=True)

        # @ Isolate new or updated rocks
        rocks = S57Aux.select_by_object(objects=new_update_features, object_filter=['UWTROC', ])
        # @ Ensure new or updated rocks have valsou
        self.report += "Warning: New or Updated UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_valsou = self.check_features_for_attribute(rocks, 'VALSOU', possible=True)

        # Filter rocks if they have a known, undefined, and unknown valsou.
        rocks_valsou = S57Aux.select_by_attribute(objects=rocks, attribute='VALSOU')
        rocks_undefined_valsou = S57Aux.filter_by_attribute(rocks, attribute='VALSOU')

        # Ensure rocks with valsou contain watlev
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_watlev = self.flag_features_with_attribute_value(rocks_valsou, attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure wrecks with unknown valsou have watlev unknown
        self.report += "New or Updated UWTROC with empty VALSOU shall have WATLEV of 'unknown' [CHECK]"
        self.flagged_uwtroc_unknown_watlev = self.flag_features_with_attribute_value(rocks_undefined_valsou,
                                                                                     attribute='WATLEV',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", ],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated rocks have quasou
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_quasou = self.flag_features_with_attribute_value(rocks_valsou, attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure rocks with unknown valsou have tecsou "unknown"
        self.report += "New or Updated UWTROC with empty VALSOU shall have QUASOU of 'depth unknown' [CHECK]"
        self.flagged_uwtroc_unknown_quasou = self.flag_features_with_attribute_value(rocks_undefined_valsou,
                                                                                     attribute='QUASOU',
                                                                                     values_to_flag=["1", "3", "4", "5",
                                                                                                     "6", "7", "8", "9",
                                                                                                     "10", "11"],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated rocks have tecsou
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_uwtroc_tecsou = self.flag_features_with_attribute_value(rocks_valsou,
                                                                             attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # Ensure rocks with unknown valsou have tecsou "unknown"
        self.report += "New or Updated UWTROC with empty VALSOU shall have TECSOU of 'unknown' [CHECK]"
        self.flagged_uwtroc_unknown_tecsou = self.flag_features_with_attribute_value(rocks_undefined_valsou,
                                                                                     attribute='TECSOU',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", "8", "9",
                                                                                                     "10", "11", "12",
                                                                                                     "13", "14", ],
                                                                                     check_attrib_existence=True)

        # @ Isolate new or updated obstructions
        obstrns = S57Aux.select_by_object(objects=new_update_features, object_filter=['OBSTRN', ])
        # @ Exclude foul area obstructions
        obstrns_no_foul = S57Aux.filter_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])
        # Include only foul obstructions
        obstrns_foul = S57Aux.select_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])
        obstrns_foul_ground = S57Aux.select_by_attribute_value(objects=obstrns, attribute='CATOBS',
                                                               value_filter=['7', ])

        # @ Ensure new or updated obstructions (excluding foul area obstructions) have images
        self.report += "New or Updated OBSTRN (unless foul) missing mandatory attribute images [CHECK]"
        self.flagged_obstrn_images = self.check_features_for_attribute(obstrns_no_foul, 'images')

        # @ Ensure new or updated obstructions have valsou
        # Isolate point obstructions
        obstrn_points = S57Aux.select_only_points(obstrns)
        self.report += "New or Updated OBSTRN point missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_points_valsou = self.check_features_for_attribute(obstrn_points, 'VALSOU')

        # @ Ensure new or updated obstructions have watlev
        self.report += "New or Updated OBSTRN point with invalid WATLEV [CHECK]"
        self.flagged_obstrn_points_watlev = self.flag_features_with_attribute_value(obstrn_points, attribute='WATLEV',
                                                                                    values_to_flag=['', ],
                                                                                    check_attrib_existence=True)

        # @ Ensure new or updated obstructions have watlev
        self.report += "New or Updated OBSTRN lines/areas with valid VALSOU and invalid WATLEV [CHECK]"
        # Isolate line/area obstructions
        obstrn_line_area = S57Aux.select_lines_and_areas(obstrns)
        # Include lines and area obstructions with VALSOU
        obstrn_line_areas_valsou = S57Aux.select_by_attribute(objects=obstrn_line_area, attribute='VALSOU')
        # Include lines and area obstructions with VALSOU
        obstrn_line_area_valsou_known = S57Aux.filter_by_attribute_value(objects=obstrn_line_areas_valsou,
                                                                         attribute='VALSOU', value_filter=['', ], )
        self.flagged_obstrn_lines_areas_watlev = self.flag_features_with_attribute_value(obstrn_line_area_valsou_known,
                                                                                         attribute='WATLEV',
                                                                                         values_to_flag=['', ],
                                                                                         check_attrib_existence=True)

        # Select all lines and area obstructions that have "unknown" and "undefined" VALSOUs and ensure they have an
        # "unknown" WATLEV.
        obstrn_line_areas_undefined_valsou = S57Aux.filter_by_attribute(objects=obstrn_line_area, attribute='VALSOU')
        obstrn_line_areas_unknown_valsou = S57Aux.select_by_attribute_value(objects=obstrn_line_area,
                                                                            attribute='VALSOU', value_filter=['', ])
        self.report += 'New or Update line or area OBSTRN with empty VALSOU with known WATLEV [CHECK]'
        self.flagged_obstrn_watlev_known = self.flag_features_with_attribute_value(obstrn_line_areas_undefined_valsou +
                                                                                   obstrn_line_areas_unknown_valsou,
                                                                                   attribute='WATLEV',
                                                                                   values_to_flag=["1", "2", "3",
                                                                                                   "4", "5", "6",
                                                                                                   "7", ],
                                                                                   check_attrib_existence=True)
        obstrn_valsou = S57Aux.select_by_attribute(objects=obstrns, attribute='VALSOU')
        obstrn_undefined_valsou = S57Aux.filter_by_attribute(obstrns, attribute='VALSOU')

        self.report += "New or Updated OBSTRN with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_quasou = self.flag_features_with_attribute_value(obstrn_valsou,
                                                                             attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # Ensure obstrn with unknown valsou have quasou "unknown"
        self.report += "New or Updated OBSTRN with empty VALSOU shall have QUASOU of 'depth unknown' [CHECK]"
        self.flagged_obstrn_unknown_quasou = self.flag_features_with_attribute_value(obstrn_undefined_valsou,
                                                                                     attribute='QUASOU',
                                                                                     values_to_flag=["1", "6", "7",
                                                                                                     "8", "9", ],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated obstructions with valsou have tecsou
        self.report += "New or Updated OBSTRN missing mandatory attribute TECSOU [CHECK]"
        self.flagged_obstrn_tecsou = self.flag_features_with_attribute_value(obstrn_valsou,
                                                                             attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure obstrn with unknown valsou have tecsou "unknown"
        self.report += "New or Updated OBSTRN with empty VALSOU shall have TECSOU of 'unknown' [CHECK]"
        self.flagged_obstrn_unknown_tecsou = self.flag_features_with_attribute_value(obstrn_undefined_valsou,
                                                                                     attribute='TECSOU',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", "8", "9",
                                                                                                     "10", "11", "12",
                                                                                                     "13"
                                                                                                     "14", ],
                                                                                     check_attrib_existence=True)

        # Isolate line and area foul area obstructions
        obstrns_foul_lines_areas = S57Aux.select_lines_and_areas(obstrns_foul)
        # Check line and area foul area obstructions do not have VALSOU
        self.report += "Foul OBSTRN shall not have VALSOU [CHECK]"
        self.flagged_obstrn_foul_valsou = self.check_features_without_attribute(
            objects=obstrns_foul_lines_areas + obstrns_foul_ground, attribute='VALSOU', possible=False)

        # Isolcate linea and area objects that are not foul
        obstrns_no_foul_foulground = S57Aux.filter_by_attribute_value(objects=obstrns, attribute='CATOBS',
                                                                      value_filter=['6', "7", ])
        obstrns_no_foul_lines_areas = S57Aux.select_lines_and_areas(obstrns_no_foul_foulground)
        # Check line and area obstructions that are not foul: VALSOU shall be left blank if depth not available.
        self.report += "Warning: New or Updated line or area OBSTRN should have VALSOU populated [CHECK]"
        self.flagged_obstrn_unknown_valsou = self.check_features_for_attribute(obstrns_no_foul_lines_areas, 'VALSOU',
                                                                               possible=True)

        # Select all the new features with valsou attribute and check for valid quasou.
        new_valsous = S57Aux.select_by_attribute(objects=new_update_features, attribute='VALSOU')
        self.report += "New or Updated VALSOU features with invalid QUASOU [CHECK]"
        self.flagged_new_valsous_quasou = self._check_features_for_valid_quasou(new_valsous)

        # @ Isolate new or updated offshore platforms
        ofsplf = S57Aux.select_by_object(objects=new_update_features, object_filter=['OFSPLF', ])
        # @ Ensure new or updated offshore platforms have images
        self.report += "New or Updated OFSPLF missing images [CHECK]"
        self.flagged_ofsplf = self.check_features_for_attribute(ofsplf, 'images')

        # @ Isolate new or updated seabed areas
        sbdare = S57Aux.select_by_object(objects=new_update_features, object_filter=['SBDARE', ])

        # Isolate sbdare lines and areas
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)

        # @ Ensure new or updated seabed areas have natsur
        self.report += "New or Updated SBDARE lines and areas with empty/missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_natsur = self.flag_features_with_attribute_value(sbdare_lines_areas, attribute='NATSUR',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # @ Isolate new or updated point seabed areas
        sbdare_points = S57Aux.select_only_points(sbdare)
        # @ Ensure not more natqua than natsur
        self.report += "New or Updated point seabed areas with more NATQUA than NATSUR [CHECK]"
        self.flagged_sbdare_pt_natqua = self.check_attribute_counts(sbdare_points, 'NATSUR', 'NATQUA')
        # @ Ensure not more colour than natsur
        self.report += "New or Updated point seabed areas with more COLOUR than NATSUR [CHECK]"
        self.flagged_sbdare_pt_colour = self.check_attribute_counts(sbdare_points, 'NATSUR', 'COLOUR')
        # @ Ensure no unallowable combinations of natqua and natsur
        self.report += "No unallowable combinations of NATSUR and NATQUA [CHECK]"
        self.flagged_sbdare_pt_allowable_combo = self.allowable_sbdare(sbdare_points)

        # @ Ensure line and area seabed areas have watlev
        self.report += "New or Updated SBDARE lines or areas missing mandatory attribute WATLEV [CHECK]"
        self.flagged_sbdare_watlev = self.check_features_for_attribute(sbdare_lines_areas, 'WATLEV', possible=True)

        # @ Isolate new or updated mooring facilities
        morfac = S57Aux.select_by_object(objects=new_update_features, object_filter=['MORFAC', ])
        # @ Ensure new or updated mooring facilities have catmor
        self.report += "New or Updated MORFAC with empty/missing mandatory attribute CATMOR [CHECK]"
        self.flagged_morfac = self.flag_features_with_attribute_value(morfac, attribute='CATMOR',
                                                                      values_to_flag=['', ],
                                                                      check_attrib_existence=True)

        # @ Isolate new or updated coastline
        coalne = S57Aux.select_by_object(objects=new_update_features, object_filter=['COALNE', ])
        # @ Ensure new or updated coastline has catcoa
        self.report += "New or Updated COALNE with empty/missing mandatory attribute CATCOA [CHECK]"
        self.flagged_coalne = self.flag_features_with_attribute_value(coalne, attribute='CATCOA',
                                                                      values_to_flag=['', ],
                                                                      check_attrib_existence=True)

        # @ Isolate new or updated shoreline construction
        slcons = S57Aux.select_by_object(objects=new_update_features, object_filter=['SLCONS', ])
        # @ Ensure new or updated shoreline construction has catslc
        self.report += "New or Updated SLCONS with empty/missing mandatory attribute CATSLC [CHECK]"
        self.flagged_slcons = self.flag_features_with_attribute_value(slcons, attribute='CATSLC',
                                                                      values_to_flag=['', ],
                                                                      check_attrib_existence=True)
        # @ Isolate new or updated land elevation
        lndelv = S57Aux.select_by_object(objects=new_update_features, object_filter=['LNDELV', ])
        # @ Ensure new or updated land elevation has elevat
        self.report += "New or Updated LNDELV missing mandatory attribute ELEVAT [CHECK]"
        self.flagged_lndelv = self.check_features_for_attribute(lndelv, 'ELEVAT')

        # Select all the new features with VALSOU attribute
        if self.use_mhw:
            new_valsous = S57Aux.select_by_attribute(objects=new_update_features, attribute='VALSOU')
            self.report += "New or Updated VALSOU features with invalid WATLEV [CHECK]"
            self.flagged_new_valsous_watlev = self._check_features_for_valid_watlev(new_valsous)

        new_elevats = S57Aux.select_by_attribute(objects=new_update_features, attribute='ELEVAT')
        self.report += "Invalid New or Updated ELEVAT features [CHECK]"
        self.flagged_new_elevat = self._check_features_for_valid_elevat(new_elevats)

        # @ Isolate M_COVR object
        mcovr = S57Aux.select_by_object(objects=self.all_features, object_filter=['M_COVR', ])
        # @ Ensure M_COVR has catcov
        self.report += "M_COVR with empty/missing mandatory attribute CATCOV [CHECK]"
        self.flagged_m_covr_catcov = self.flag_features_with_attribute_value(mcovr, attribute='CATCOV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure M_COVR has inform
        self.report += "M_COVR missing mandatory attribute INFORM [CHECK]"
        self.flagged_m_covr_inform = self.check_features_for_attribute(mcovr, 'INFORM')
        # @ Ensure M_COVR has ninfom
        self.report += "M_COVR missing mandatory attribute NINFOM [CHECK]"
        self.flagged_m_covr_ninfom = self.check_features_for_attribute(mcovr, 'NINFOM')

        # Ensure all features with images comply with HSSD requirements.
        self.report += "Invalid IMAGES attribute, feature missing image or name check failed per HSSD [CHECK]"
        self.flagged_images_hssd = self._check_features_for_images(self.all_features)

        # New for 2020-- image naming conventions which were tied to HTDs

        # Isolate new or updated seabed areas
        sbdare = S57Aux.select_by_object(objects=new_update_features, object_filter=['SBDARE', ])

        # Isolate new or updated point seabed areas
        sbdare_points = S57Aux.select_only_points(sbdare)

        self.report += "Invalid bottom sample IMAGE name per HSSD [CHECK]"
        self.flagged_images_sbdare_points = self._check_sbdare_images_per_htd(sbdare_points)

        self.report += "Invalid feature IMAGE name per HSSD [CHECK]"
        non_sbdare_features = S57Aux.filter_by_object(objects=self.all_features, object_filter=['SBDARE', ])
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)
        self.flagged_images_features = self._check_nonsbdare_images_per_htd(non_sbdare_features + sbdare_lines_areas)

        if self.profile == 0:  # office
            # For the office profile, ensure all features have onotes
            self.report += "Features missing onotes [CHECK]"
            self.flagged_without_onotes = self.check_features_for_attribute(self.all_features, 'onotes')

            # For the office profile, check for empty hsdrec
            self.report += "Features with empty/unknown attribute hsdrec [CHECK]"
            self.flagged_hsdrec_empty = self.flag_features_with_attribute_value(self.all_features, attribute='hsdrec',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)
            # For the office profile, check for prohibited features by feature type
            self.report += "Features without 'Prohibited feature' keyword [CHECK]"
            prohibited = S57Aux.select_by_object(objects=self.all_features, object_filter=[
                'DRGARE', 'LOGPON', 'PIPARE', 'PIPOHD', 'PIPSOL', 'DMPGRD', 'LIGHTS', 'BOYLAT', 'BOYSAW', 'BOYSPP',
                'DAYMAR', 'FOGSIG', 'CBLSUB', 'CBLARE', 'FAIRWY', 'RTPBCN', 'BOYISD', 'BOYINB', 'BOYCAR', 'CBLOHD',
                'BCNSPP', 'BCNLAT', 'BRIDGE'])
            self.flagged_prohibited_kwds = self.check_for_missing_keywords(prohibited, attr_acronym='onotes',
                                                                           keywords=['Prohibited feature', ])

            # For the office profile, check for prohibited fish haven
            obstrn = S57Aux.select_by_object(objects=self.all_features, object_filter=['OBSTRN', ])
            fish_haven = S57Aux.select_by_attribute_value(objects=obstrn, attribute='CATOBS', value_filter=['5', ])
            self.report += "Fish havens without 'Prohibited feature' keyword [CHECK]"
            self.flagged_fish_haven_kwds = self.check_for_missing_keywords(fish_haven, attr_acronym='onotes',
                                                                           keywords=['Prohibited feature', ])

            # For the office profile, check for prohibited mooring buoys
            morfac = S57Aux.select_by_object(objects=self.all_features, object_filter=['MORFAC', ])
            mooring_buoy = S57Aux.select_by_attribute_value(objects=morfac, attribute='CATMOR', value_filter=['7', ])
            self.report += "Mooring buoy without 'Prohibited feature' keyword [CHECK]"
            self.flagged_mooring_buoy_kwds = self.check_for_missing_keywords(mooring_buoy, attr_acronym='onotes',
                                                                             keywords=['Prohibited feature', ])

            # For office profile, check for M_QUAL attribution
            mqual = S57Aux.select_by_object(objects=self.all_features, object_filter=['M_QUAL', ])
            # Ensure M_QUAL has CATZOC
            self.report += "M_QUAL features with empty/missing mandatory attribute CATZOC [CHECK]"
            self.flagged_m_qual_catzoc = self.flag_features_with_attribute_value(objects=mqual, attribute='CATZOC',
                                                                                 values_to_flag=['', ],
                                                                                 check_attrib_existence=True)
            # Ensure M_QUAL has SURSTA
            self.report += "M_QUAL features missing mandatory attribute SURSTA [CHECK]"
            self.flagged_m_qual_sursta = self.check_features_for_attribute(mqual, 'SURSTA')
            # Ensure M_QUAL has SUREND
            self.report += "M_QUAL features missing mandatory attribute SUREND [CHECK]"
            self.flagged_m_qual_surend = self.check_features_for_attribute(mqual, 'SUREND')
            # Ensure M_QUAL has TECSOU
            self.report += "M_QUAL features empty/missing mandatory attribute TECSOU [CHECK]"
            self.flagged_m_qual_tecsou = self.flag_features_with_attribute_value(objects=mqual, attribute='TECSOU',
                                                                                 values_to_flag=['', ],
                                                                                 check_attrib_existence=True)

            # Ensure all features have descrp (per MCD)
            self.report += "Features have empty or missing mandatory attribute description [CHECK]"
            self.flagged_mcd_description = self.check_features_for_attribute(objects=self.all_features,
                                                                             attribute='descrp')

            # Ensure all features have remrks (per MCD)
            self.report += "Features missing mandatory attribute remarks [CHECK]"
            self.flagged_mcd_remarks = self.check_features_for_attribute(self.all_features, attribute='remrks')

            # New Requirement from mcd in 2020 - character limit for all fields with free text strings
            self.report += "Features with text input fields exceeding %d characters [CHECK]" % self.character_limit
            self.flagged_character_limit = self.check_character_limit(objects=self.all_features,
                                                                      attributes=['images', 'invreq', 'keywrd',
                                                                                  'onotes', 'recomd', 'remrks'],
                                                                      character_limit=self.character_limit)

        # finalize the summary
        self.finalize_summary()

    def run_2021(self) -> None:
        """HSSD 2021 checks """

        # @ Ensure no feature redundancy
        self.report += "Redundant features [CHECK]"
        self.all_features = self.check_feature_redundancy_and_geometry()
        logger.debug("nr. of features after redundancy and geometry checks: %d" % len(self.all_features))

        # @ Remove carto features
        carto_filter = ['$AREAS', '$LINES', '$CSYMB', '$COMPS', '$TEXTS']
        no_carto_features = S57Aux.filter_by_object(objects=self.all_features, object_filter=carto_filter)

        # @ Isolate only features with descrp = New or Update
        new_update_features = S57Aux.select_by_attribute_value(objects=no_carto_features, attribute='descrp',
                                                               value_filter=['1', '2', ])
        # @ Ensure new or updated features have SORIND
        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORIND [CHECK]"
        self.flagged_sorind = self.check_features_for_attribute(new_update_features, 'SORIND')
        # @ Ensure new or updated features have valid SORIND
        self.report += "New or Updated features (excluding carto notes) with invalid SORIND [CHECK]"
        if self.sorind is None:
            self.flagged_sorind_invalid = self._check_features_for_valid_sorind(new_update_features, check_space=False)
        else:
            self.flagged_sorind_invalid = self._check_features_for_match_sorind(new_update_features)
        # @ Ensure new or updated features have SORDAT
        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORDAT [CHECK]"
        self.flagged_sordat = self.check_features_for_attribute(new_update_features, 'SORDAT')
        # @ Ensure new or updated features have valid SORDAT
        self.report += "New or Updated features (excluding carto notes) with invalid SORDAT [CHECK]"
        if self.sordat is None:
            self.flagged_sordat_invalid = self._check_features_for_valid_sordat(new_update_features)
        else:
            self.flagged_sordat_invalid = self._check_features_for_match_sordat(new_update_features)

        # @ Isolate only features that are assigned
        assigned_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='asgnmt',
                                                             value_filter=['2', ])
        # @ Ensure assigned features have descrp
        self.report += "Assigned features have empty or missing mandatory attribute description [CHECK]"
        self.flagged_description = self.flag_features_with_attribute_value(objects=assigned_features,
                                                                           attribute='descrp',
                                                                           values_to_flag=['', ],
                                                                           check_attrib_existence=True)

        # @ Ensure assigned features have remrks
        self.report += "Assigned features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks = self.check_features_for_attribute(objects=assigned_features, attribute='remrks')

        # @ Isolate features with descrp = New or Delete
        new_delete_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='descrp',
                                                               value_filter=['1', '3'])
        # @ Ensure new or deleted features have remrks
        self.report += "New/Delete features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks_features = self.check_features_for_attribute(
            objects=new_delete_features, attribute='remrks')

        # @ Ensure new or deleted features have recomd
        self.report += "New/Delete features missing mandatory attribute recommendation [CHECK]"
        self.flagged_recommend_features = self.check_features_for_attribute(objects=new_delete_features,
                                                                            attribute='recomd')

        # @ Isolate sounding features
        sounding_features = S57Aux.select_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        # @ Ensure soundings have tecsou
        self.report += "SOUNDG with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_soundings_tecsou = self.flag_features_with_attribute_value(sounding_features, attribute='TECSOU',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)
        # @ Ensure soundings have quasou
        self.report += "SOUNDG with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_soundings_quasou = self.flag_features_with_attribute_value(sounding_features, attribute='QUASOU',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)

        # @ Isolate features that are no-carto, descrp = New or Updated, and sftype = DTON
        dtons = S57Aux.select_by_attribute_value(objects=new_update_features, attribute='sftype', value_filter=['3', ])
        # @ Remove soundings to prevent WRECK and OBSTRN DtoN objects from getting the image flag twice.
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['WRECKS', 'OBSTRN'])
        # @ Ensure DTONs have images
        self.report += "Special feature types (DTONS) missing images [CHECK]"
        self.flagged_dtons = self.check_features_for_attribute(dtons, 'images')

        # @ Isolate new or updated wrecks
        wrecks = S57Aux.select_by_object(objects=new_update_features, object_filter=['WRECKS', ])
        # @ Ensure new or updated wrecks have images
        self.report += "New or Updated WRECKS missing images [CHECK]"
        self.flagged_wrecks_images = self.check_features_for_attribute(wrecks, 'images')
        # @ Ensure new or updated wrecks have catwrk
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute CATWRK [CHECK]"
        self.flagged_wrecks_catwrk = self.flag_features_with_attribute_value(wrecks, attribute='CATWRK',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Filter wrecks if they have a known, undefined, and unknown valsou.
        wrecks_valsou = S57Aux.select_by_attribute(objects=wrecks, attribute='VALSOU')
        logger.debug("Total number of wrecks without undefined VALSOU: %d" % (len(wrecks_valsou)))
        wrecks_undefined_valsou = S57Aux.filter_by_attribute(wrecks, attribute='VALSOU')
        logger.debug("Total number of wrecks with undefined VALSOU: %d" % (len(wrecks_undefined_valsou)))

        # Ensure wrecks with valsou contain watlev
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_watlev = self.flag_features_with_attribute_value(wrecks_valsou,
                                                                             attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure wrecks with unknown valsou have watlev unknown
        self.report += "New or Updated WRECKS with empty VALSOU shall have WATLEV of 'unknown' [CHECK]"
        self.flagged_wrecks_unknown_watlev = self.flag_features_with_attribute_value(wrecks_undefined_valsou,
                                                                                     attribute='WATLEV',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", ],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated wrecks have valsou
        self.report += "New or Updated WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_valsou = self.check_features_for_attribute(wrecks, 'VALSOU')

        # Ensure wrecks with valsou contain tecsou
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_wrecks_tecsou = self.flag_features_with_attribute_value(wrecks_valsou,
                                                                             attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure wrecks with unknown valsou have tecsou "unknown"
        self.report += "New or Updated WRECKS with empty VALSOU shall have TECSOU of 'unknown' [CHECK]"
        self.flagged_wrecks_unknown_tecsou = self.flag_features_with_attribute_value(wrecks_undefined_valsou,
                                                                                     attribute='TECSOU',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", "8", "9",
                                                                                                     "10", "11", "12",
                                                                                                     "13", "14", ],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated wrecks have quasou
        self.report += "New or Updated WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_quasou = self.flag_features_with_attribute_value(wrecks_valsou,
                                                                             attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure wrecks with unknown valsou have quasou "unknown"
        self.report += "New or Updated WRECKS with empty VALSOU shall have QUASOU of 'depth unknown' [CHECK]"
        self.flagged_wrecks_unknown_quasou = self.flag_features_with_attribute_value(wrecks_undefined_valsou,
                                                                                     attribute='QUASOU',
                                                                                     values_to_flag=["1", "3", "4", "5",
                                                                                                     "6", "7", "8", "9",
                                                                                                     "10", "11"],
                                                                                     check_attrib_existence=True)

        # @ Isolate new or updated rocks
        rocks = S57Aux.select_by_object(objects=new_update_features, object_filter=['UWTROC', ])
        # @ Ensure new or updated rocks have valsou
        self.report += "Warning: New or Updated UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_valsou = self.check_features_for_attribute(rocks, 'VALSOU', possible=True)

        # Filter rocks if they have a known, undefined, and unknown valsou.
        rocks_valsou = S57Aux.select_by_attribute(objects=rocks, attribute='VALSOU')
        rocks_undefined_valsou = S57Aux.filter_by_attribute(rocks, attribute='VALSOU')

        # Ensure rocks with valsou contain watlev
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_watlev = self.flag_features_with_attribute_value(rocks_valsou, attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure wrecks with unknown valsou have watlev unknown
        self.report += "New or Updated UWTROC with empty VALSOU shall have WATLEV of 'unknown' [CHECK]"
        self.flagged_uwtroc_unknown_watlev = self.flag_features_with_attribute_value(rocks_undefined_valsou,
                                                                                     attribute='WATLEV',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", ],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated rocks have quasou
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_quasou = self.flag_features_with_attribute_value(rocks_valsou, attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure rocks with unknown valsou have tecsou "unknown"
        self.report += "New or Updated UWTROC with empty VALSOU shall have QUASOU of 'depth unknown' [CHECK]"
        self.flagged_uwtroc_unknown_quasou = self.flag_features_with_attribute_value(rocks_undefined_valsou,
                                                                                     attribute='QUASOU',
                                                                                     values_to_flag=["1", "3", "4", "5",
                                                                                                     "6", "7", "8", "9",
                                                                                                     "10", "11"],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated rocks have tecsou
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_uwtroc_tecsou = self.flag_features_with_attribute_value(rocks_valsou,
                                                                             attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # Ensure rocks with unknown valsou have tecsou "unknown"
        self.report += "New or Updated UWTROC with empty VALSOU shall have TECSOU of 'unknown' [CHECK]"
        self.flagged_uwtroc_unknown_tecsou = self.flag_features_with_attribute_value(rocks_undefined_valsou,
                                                                                     attribute='TECSOU',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", "8", "9",
                                                                                                     "10", "11", "12",
                                                                                                     "13", "14", ],
                                                                                     check_attrib_existence=True)

        # @ Isolate new or updated obstructions
        obstrns = S57Aux.select_by_object(objects=new_update_features, object_filter=['OBSTRN', ])
        # @ Exclude foul area obstructions
        obstrns_no_foul = S57Aux.filter_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])
        # Include only foul obstructions
        obstrns_foul = S57Aux.select_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])
        obstrns_foul_ground = S57Aux.select_by_attribute_value(objects=obstrns, attribute='CATOBS',
                                                               value_filter=['7', ])

        # @ Ensure new or updated obstructions (excluding foul area obstructions) have images
        self.report += "New or Updated OBSTRN (unless foul) missing mandatory attribute images [CHECK]"
        self.flagged_obstrn_images = self.check_features_for_attribute(obstrns_no_foul, 'images')

        # @ Ensure new or updated obstructions have valsou
        # Isolate point obstructions
        obstrn_points = S57Aux.select_only_points(obstrns)
        self.report += "New or Updated OBSTRN point missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_points_valsou = self.check_features_for_attribute(obstrn_points, 'VALSOU')

        # @ Ensure new or updated obstructions have watlev
        self.report += "New or Updated OBSTRN point with invalid WATLEV [CHECK]"
        self.flagged_obstrn_points_watlev = self.flag_features_with_attribute_value(obstrn_points, attribute='WATLEV',
                                                                                    values_to_flag=['', ],
                                                                                    check_attrib_existence=True)

        # @ Ensure new or updated obstructions have watlev
        self.report += "New or Updated OBSTRN lines/areas with valid VALSOU and invalid WATLEV [CHECK]"
        # Isolate line/area obstructions
        obstrn_line_area = S57Aux.select_lines_and_areas(obstrns)
        # Include lines and area obstructions with VALSOU
        obstrn_line_areas_valsou = S57Aux.select_by_attribute(objects=obstrn_line_area, attribute='VALSOU')
        # Include lines and area obstructions with VALSOU
        obstrn_line_area_valsou_known = S57Aux.filter_by_attribute_value(objects=obstrn_line_areas_valsou,
                                                                         attribute='VALSOU', value_filter=['', ], )
        self.flagged_obstrn_lines_areas_watlev = self.flag_features_with_attribute_value(obstrn_line_area_valsou_known,
                                                                                         attribute='WATLEV',
                                                                                         values_to_flag=['', ],
                                                                                         check_attrib_existence=True)

        # Select all lines and area obstructions that have "unknown" and "undefined" VALSOUs and ensure they have an
        # "unknown" WATLEV.
        obstrn_line_areas_undefined_valsou = S57Aux.filter_by_attribute(objects=obstrn_line_area, attribute='VALSOU')
        obstrn_line_areas_unknown_valsou = S57Aux.select_by_attribute_value(objects=obstrn_line_area,
                                                                            attribute='VALSOU', value_filter=['', ])
        self.report += 'New or Update line or area OBSTRN with empty VALSOU with known WATLEV [CHECK]'
        self.flagged_obstrn_watlev_known = self.flag_features_with_attribute_value(obstrn_line_areas_undefined_valsou +
                                                                                   obstrn_line_areas_unknown_valsou,
                                                                                   attribute='WATLEV',
                                                                                   values_to_flag=["1", "2", "3",
                                                                                                   "4", "5", "6",
                                                                                                   "7", ],
                                                                                   check_attrib_existence=True)
        obstrn_valsou = S57Aux.select_by_attribute(objects=obstrns, attribute='VALSOU')
        obstrn_undefined_valsou = S57Aux.filter_by_attribute(obstrns, attribute='VALSOU')

        self.report += "New or Updated OBSTRN with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_quasou = self.flag_features_with_attribute_value(obstrn_valsou,
                                                                             attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # Ensure obstrn with unknown valsou have quasou "unknown"
        self.report += "New or Updated OBSTRN with empty VALSOU shall have QUASOU of 'depth unknown' [CHECK]"
        self.flagged_obstrn_unknown_quasou = self.flag_features_with_attribute_value(obstrn_undefined_valsou,
                                                                                     attribute='QUASOU',
                                                                                     values_to_flag=["1", "6", "7",
                                                                                                     "8", "9", ],
                                                                                     check_attrib_existence=True)

        # @ Ensure new or updated obstructions with valsou have tecsou
        self.report += "New or Updated OBSTRN missing mandatory attribute TECSOU [CHECK]"
        self.flagged_obstrn_tecsou = self.flag_features_with_attribute_value(obstrn_valsou,
                                                                             attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure obstrn with unknown valsou have tecsou "unknown"
        self.report += "New or Updated OBSTRN with empty VALSOU shall have TECSOU of 'unknown' [CHECK]"
        self.flagged_obstrn_unknown_tecsou = self.flag_features_with_attribute_value(obstrn_undefined_valsou,
                                                                                     attribute='TECSOU',
                                                                                     values_to_flag=["1", "2", "3",
                                                                                                     "4", "5", "6",
                                                                                                     "7", "8", "9",
                                                                                                     "10", "11", "12",
                                                                                                     "13"
                                                                                                     "14", ],
                                                                                     check_attrib_existence=True)

        # Isolate line and area foul area obstructions
        obstrns_foul_lines_areas = S57Aux.select_lines_and_areas(obstrns_foul)
        # Check line and area foul area obstructions do not have VALSOU
        self.report += "Foul OBSTRN shall not have VALSOU [CHECK]"
        self.flagged_obstrn_foul_valsou = self.check_features_without_attribute(
            objects=obstrns_foul_lines_areas + obstrns_foul_ground, attribute='VALSOU', possible=False)

        # Isolcate linea and area objects that are not foul
        obstrns_no_foul_foulground = S57Aux.filter_by_attribute_value(objects=obstrns, attribute='CATOBS',
                                                                      value_filter=['6', "7", ])
        obstrns_no_foul_lines_areas = S57Aux.select_lines_and_areas(obstrns_no_foul_foulground)
        # Check line and area obstructions that are not foul: VALSOU shall be left blank if depth not available.
        self.report += "Warning: New or Updated line or area OBSTRN should have VALSOU populated [CHECK]"
        self.flagged_obstrn_unknown_valsou = self.check_features_for_attribute(obstrns_no_foul_lines_areas, 'VALSOU',
                                                                               possible=True)

        # Select all the new features with valsou attribute and check for valid quasou.
        new_valsous = S57Aux.select_by_attribute(objects=new_update_features, attribute='VALSOU')
        self.report += "New or Updated VALSOU features with invalid QUASOU [CHECK]"
        self.flagged_new_valsous_quasou = self._check_features_for_valid_quasou(new_valsous)

        # @ Isolate new or updated offshore platforms
        ofsplf = S57Aux.select_by_object(objects=new_update_features, object_filter=['OFSPLF', ])
        # @ Ensure new or updated offshore platforms have images
        self.report += "New or Updated OFSPLF missing images [CHECK]"
        self.flagged_ofsplf = self.check_features_for_attribute(ofsplf, 'images')

        # @ Isolate new or updated seabed areas
        sbdare = S57Aux.select_by_object(objects=new_update_features, object_filter=['SBDARE', ])

        # Isolate sbdare lines and areas
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)

        # @ Ensure new or updated seabed areas have natsur
        self.report += "New or Updated SBDARE lines and areas with empty/missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_natsur = self.flag_features_with_attribute_value(sbdare_lines_areas, attribute='NATSUR',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # @ Isolate new or updated point seabed areas
        sbdare_points = S57Aux.select_only_points(sbdare)
        # @ Ensure not more natqua than natsur
        self.report += "New or Updated point seabed areas with more NATQUA than NATSUR [CHECK]"
        self.flagged_sbdare_pt_natqua = self.check_attribute_counts(sbdare_points, 'NATSUR', 'NATQUA')
        # @ Ensure not more colour than natsur
        self.report += "New or Updated point seabed areas with more COLOUR than NATSUR [CHECK]"
        self.flagged_sbdare_pt_colour = self.check_attribute_counts(sbdare_points, 'NATSUR', 'COLOUR')
        # @ Ensure no unallowable combinations of natqua and natsur
        self.report += "No unallowable combinations of NATSUR and NATQUA [CHECK]"
        self.flagged_sbdare_pt_allowable_combo = self.allowable_sbdare(sbdare_points)

        # @ Ensure line and area seabed areas have watlev
        self.report += "New or Updated SBDARE lines or areas missing mandatory attribute WATLEV [CHECK]"
        self.flagged_sbdare_watlev = self.check_features_for_attribute(sbdare_lines_areas, 'WATLEV', possible=True)

        # @ Isolate new or updated mooring facilities
        morfac = S57Aux.select_by_object(objects=new_update_features, object_filter=['MORFAC', ])
        # @ Ensure new or updated mooring facilities have catmor
        self.report += "New or Updated MORFAC with empty/missing mandatory attribute CATMOR [CHECK]"
        self.flagged_morfac = self.flag_features_with_attribute_value(morfac, attribute='CATMOR',
                                                                      values_to_flag=['', ],
                                                                      check_attrib_existence=True)

        # @ Isolate new or updated coastline
        coalne = S57Aux.select_by_object(objects=new_update_features, object_filter=['COALNE', ])
        # @ Ensure new or updated coastline has catcoa
        self.report += "New or Updated COALNE with empty/missing mandatory attribute CATCOA [CHECK]"
        self.flagged_coalne = self.flag_features_with_attribute_value(coalne, attribute='CATCOA',
                                                                      values_to_flag=['', ],
                                                                      check_attrib_existence=True)

        # @ Isolate new or updated shoreline construction
        slcons = S57Aux.select_by_object(objects=new_update_features, object_filter=['SLCONS', ])
        # @ Ensure new or updated shoreline construction has catslc
        self.report += "New or Updated SLCONS with empty/missing mandatory attribute CATSLC [CHECK]"
        self.flagged_slcons = self.flag_features_with_attribute_value(slcons, attribute='CATSLC',
                                                                      values_to_flag=['', ],
                                                                      check_attrib_existence=True)
        # @ Isolate new or updated land elevation
        lndelv = S57Aux.select_by_object(objects=new_update_features, object_filter=['LNDELV', ])
        # @ Ensure new or updated land elevation has elevat
        self.report += "New or Updated LNDELV missing mandatory attribute ELEVAT [CHECK]"
        self.flagged_lndelv = self.check_features_for_attribute(lndelv, 'ELEVAT')

        # Select all the new features with VALSOU attribute
        if self.use_mhw:
            new_valsous = S57Aux.select_by_attribute(objects=new_update_features, attribute='VALSOU')
            self.report += "New or Updated VALSOU features with invalid WATLEV [CHECK]"
            self.flagged_new_valsous_watlev = self._check_features_for_valid_watlev(new_valsous)

        new_elevats = S57Aux.select_by_attribute(objects=new_update_features, attribute='ELEVAT')
        self.report += "Invalid New or Updated ELEVAT features [CHECK]"
        self.flagged_new_elevat = self._check_features_for_valid_elevat(new_elevats)

        # @ Isolate M_COVR object
        mcovr = S57Aux.select_by_object(objects=self.all_features, object_filter=['M_COVR', ])
        # @ Ensure M_COVR has catcov
        self.report += "M_COVR with empty/missing mandatory attribute CATCOV [CHECK]"
        self.flagged_m_covr_catcov = self.flag_features_with_attribute_value(mcovr, attribute='CATCOV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure M_COVR has inform
        self.report += "M_COVR missing mandatory attribute INFORM [CHECK]"
        self.flagged_m_covr_inform = self.check_features_for_attribute(mcovr, 'INFORM')
        # @ Ensure M_COVR has ninfom
        self.report += "M_COVR missing mandatory attribute NINFOM [CHECK]"
        self.flagged_m_covr_ninfom = self.check_features_for_attribute(mcovr, 'NINFOM')

        # Ensure all features with images comply with HSSD requirements.
        self.report += "Invalid IMAGES attribute, feature missing image or name check failed per HSSD [CHECK]"
        self.flagged_images_hssd = self._check_features_for_images(self.all_features)

        # New for 2020-- image naming conventions which were tied to HTDs

        # Isolate new or updated seabed areas
        sbdare = S57Aux.select_by_object(objects=new_update_features, object_filter=['SBDARE', ])

        # Isolate new or updated point seabed areas
        sbdare_points = S57Aux.select_only_points(sbdare)

        self.report += "Invalid bottom sample IMAGE name per HSSD [CHECK]"
        self.flagged_images_sbdare_points = self._check_sbdare_images_per_htd(sbdare_points)

        self.report += "Invalid feature IMAGE name per HSSD [CHECK]"
        non_sbdare_features = S57Aux.filter_by_object(objects=self.all_features, object_filter=['SBDARE', ])
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)
        self.flagged_images_features = self._check_nonsbdare_images_per_htd(non_sbdare_features + sbdare_lines_areas)

        if self.profile == 0:  # office
            # For the office profile, ensure all features have onotes
            self.report += "Features missing onotes [CHECK]"
            self.flagged_without_onotes = self.check_features_for_attribute(self.all_features, 'onotes')

            # For the office profile, check for empty hsdrec
            self.report += "Features with empty/unknown attribute hsdrec [CHECK]"
            self.flagged_hsdrec_empty = self.flag_features_with_attribute_value(self.all_features, attribute='hsdrec',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)
            # For the office profile, check for prohibited features by feature type
            self.report += "Features without 'Prohibited feature' keyword [CHECK]"
            prohibited = S57Aux.select_by_object(objects=self.all_features, object_filter=[
                'DRGARE', 'LOGPON', 'PIPARE', 'PIPOHD', 'PIPSOL', 'DMPGRD', 'LIGHTS', 'BOYLAT', 'BOYSAW', 'BOYSPP',
                'DAYMAR', 'FOGSIG', 'CBLSUB', 'CBLARE', 'FAIRWY', 'RTPBCN', 'BOYISD', 'BOYINB', 'BOYCAR', 'CBLOHD',
                'BCNSPP', 'BCNLAT', 'BRIDGE'])
            self.flagged_prohibited_kwds = self.check_for_missing_keywords(prohibited, attr_acronym='onotes',
                                                                           keywords=['Prohibited feature', ])

            # For the office profile, check for prohibited fish haven
            obstrn = S57Aux.select_by_object(objects=self.all_features, object_filter=['OBSTRN', ])
            fish_haven = S57Aux.select_by_attribute_value(objects=obstrn, attribute='CATOBS', value_filter=['5', ])
            self.report += "Fish havens without 'Prohibited feature' keyword [CHECK]"
            self.flagged_fish_haven_kwds = self.check_for_missing_keywords(fish_haven, attr_acronym='onotes',
                                                                           keywords=['Prohibited feature', ])

            # For the office profile, check for prohibited mooring buoys
            morfac = S57Aux.select_by_object(objects=self.all_features, object_filter=['MORFAC', ])
            mooring_buoy = S57Aux.select_by_attribute_value(objects=morfac, attribute='CATMOR', value_filter=['7', ])
            self.report += "Mooring buoy without 'Prohibited feature' keyword [CHECK]"
            self.flagged_mooring_buoy_kwds = self.check_for_missing_keywords(mooring_buoy, attr_acronym='onotes',
                                                                             keywords=['Prohibited feature', ])

            # For office profile, check for M_QUAL attribution
            mqual = S57Aux.select_by_object(objects=self.all_features, object_filter=['M_QUAL', ])
            # Ensure M_QUAL has CATZOC
            self.report += "M_QUAL features with empty/missing mandatory attribute CATZOC [CHECK]"
            self.flagged_m_qual_catzoc = self.flag_features_with_attribute_value(objects=mqual, attribute='CATZOC',
                                                                                 values_to_flag=['', ],
                                                                                 check_attrib_existence=True)
            # Ensure M_QUAL has SURSTA
            self.report += "M_QUAL features missing mandatory attribute SURSTA [CHECK]"
            self.flagged_m_qual_sursta = self.check_features_for_attribute(mqual, 'SURSTA')
            # Ensure M_QUAL has SUREND
            self.report += "M_QUAL features missing mandatory attribute SUREND [CHECK]"
            self.flagged_m_qual_surend = self.check_features_for_attribute(mqual, 'SUREND')
            # Ensure M_QUAL has TECSOU
            self.report += "M_QUAL features empty/missing mandatory attribute TECSOU [CHECK]"
            self.flagged_m_qual_tecsou = self.flag_features_with_attribute_value(objects=mqual, attribute='TECSOU',
                                                                                 values_to_flag=['', ],
                                                                                 check_attrib_existence=True)

            # Ensure all features have descrp (per MCD)
            self.report += "Features have empty or missing mandatory attribute description [CHECK]"
            self.flagged_mcd_description = self.check_features_for_attribute(objects=self.all_features,
                                                                             attribute='descrp')

            # Ensure all features have remrks (per MCD)
            self.report += "Features missing mandatory attribute remarks [CHECK]"
            self.flagged_mcd_remarks = self.check_features_for_attribute(self.all_features, attribute='remrks')

            # New Requirement from mcd in 2020 - character limit for all fields with free text strings
            self.report += "Features with text input fields exceeding %d characters [CHECK]" % self.character_limit
            self.flagged_character_limit = self.check_character_limit(objects=self.all_features,
                                                                      attributes=['images', 'invreq', 'keywrd',
                                                                                  'onotes', 'recomd', 'remrks'],
                                                                      character_limit=self.character_limit)

        # finalize the summary
        self.finalize_summary()
