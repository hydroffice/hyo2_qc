import datetime
import logging
import os
from typing import List, Optional, TYPE_CHECKING

from hyo2.qc.common.s57_aux import S57Aux

if TYPE_CHECKING:
    from hyo2.qc.survey.scan.flags import Flags
    from hyo2.s57.s57 import S57Record10
    from hyo2.abc.app.report import Report

logger = logging.getLogger(__name__)


class Checks:
    survey_areas = {
        "Great Lakes": 0,
        "Pacific Coast": 1,
        "Atlantic Coast": 2,
    }

    def __init__(self, flags: 'Flags', report: 'Report', all_features: List['S57Record10'],
                 survey_area: int, version: str,
                 sorind: Optional[str], sordat: Optional[str],
                 profile: int, use_mhw: bool, mhw_value: float,
                 check_image_names: bool, multimedia_folder: Optional[str]):
        self.flags = flags
        self.report = report

        self.all_fts = all_features  # type: List['S57Record10']
        self.no_carto_fts = list()  # type: List['S57Record10']
        self.new_updated_fts = list()  # type: List['S57Record10']
        self.assigned_fts = list()  # type: List['S57Record10']
        self.new_deleted_fts = list()  # type: List['S57Record10']

        self.survey_area = survey_area
        self.version = version
        self.sorind = sorind
        self.sordat = sordat
        self.profile = profile
        self.use_mhw = use_mhw
        self.mhw_value = mhw_value
        self.check_image_names = check_image_names
        self.multimedia_folder = multimedia_folder

        self.character_limit = 255
        self.onotes_character_limit = 250

    # shared functions

    def _check_features_for_attribute(self, objects: List['S57Record10'], attribute: str, possible: bool = False) \
            -> List[list]:
        """Check if the passed features have the passed attribute"""
        flagged = list()

        for obj in objects:
            # do the test
            has_attribute = False
            for attr in obj.attributes:
                if attr.acronym == attribute:
                    has_attribute = True

            # check passed
            if has_attribute:
                continue

            if possible:
                # add to the flagged report
                self.report += 'Warning: Found missing %s at (%.7f, %.7f)' % (
                    obj.acronym, obj.centroid.x, obj.centroid.y)
                # add to the flagged feature list
                self.flags.append(obj.centroid.x, obj.centroid.y, "warning: missing %s" % attribute,
                                  self.report.cur_section(with_prepended_summary=True))
            else:
                # add to the flagged report
                self.report += 'Found missing %s at (%.7f, %.7f)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
                # add to the flagged feature list
                self.flags.append(obj.centroid.x, obj.centroid.y, "missing %s" % attribute,
                                  self.report.cur_section(with_prepended_summary=True))
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_for_just_one_of_attributes_in_list(self, objects: List['S57Record10'],
                                                           xor_attributes: List[str],
                                                           possible: bool = False) -> List[list]:
        """Check if the passed features have the passed attribute"""
        flagged = list()

        for obj in objects:
            # do the test
            attrs_counter = 0
            for a in xor_attributes:
                for attr in obj.attributes:
                    if attr.acronym == a:
                        attrs_counter += 1

            # check passed
            if attrs_counter == 1:
                continue

            if attrs_counter == 0:

                # add to the flagged report
                if possible:
                    # add to the flagged report
                    self.report += 'Warning: Found missing one among %s at (%.7f, %.7f)' % (
                        xor_attributes, obj.centroid.x, obj.centroid.y)
                    # add to the flagged feature list
                    self.flags.append(obj.centroid.x, obj.centroid.y, "warning: missing one among %s"
                                      % (xor_attributes,), self.report.cur_section(with_prepended_summary=True))
                else:
                    # add to the flagged report
                    self.report += 'Found missing one among %s at (%.7f, %.7f)' % (
                        xor_attributes, obj.centroid.x, obj.centroid.y)
                    # add to the flagged feature list
                    self.flags.append(obj.centroid.x, obj.centroid.y, "missing one among %s"
                                      % (xor_attributes,), self.report.cur_section(with_prepended_summary=True))

            else:
                # add to the flagged report
                if possible:
                    # add to the flagged report
                    self.report += 'Warning: Found %d among %s at (%.7f, %.7f)' % (
                        attrs_counter, xor_attributes, obj.centroid.x, obj.centroid.y)
                    # add to the flagged feature list
                    self.flags.append(obj.centroid.x, obj.centroid.y, "warning: %d among %s"
                                      % (attrs_counter, xor_attributes,),
                                      self.report.cur_section(with_prepended_summary=True))
                else:
                    # add to the flagged report
                    self.report += 'Found %d among %s at (%.7f, %.7f)' % (
                        attrs_counter, xor_attributes, obj.centroid.x, obj.centroid.y)
                    # add to the flagged feature list
                    self.flags.append(obj.centroid.x, obj.centroid.y, "%d among %s"
                                      % (attrs_counter, xor_attributes,),
                                      self.report.cur_section(with_prepended_summary=True))

            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_without_attribute(self, objects: List['S57Record10'], attribute: str, possible: bool = False) \
            -> List[list]:
        """Check if the passed features have the passed attribute"""
        flagged = list()

        for obj in objects:
            # do the test
            has_attribute = False
            for attr in obj.attributes:
                if attr.acronym == attribute:
                    has_attribute = True

            # check passed
            if not has_attribute:
                continue

            if possible:
                # add to the flagged report
                self.report += 'Warning: Found %s at (%.7f, %.7f)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
                # add to the flagged feature list
                self.flags.append(obj.centroid.x, obj.centroid.y, "warning: containing %s (?)" % attribute,
                                  self.report.cur_section(with_prepended_summary=True))
            else:
                # add to the flagged report
                self.report += 'Found %s at (%.7f, %.7f)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
                # add to the flagged feature list
                self.flags.append(obj.centroid.x, obj.centroid.y, "containing %s" % attribute,
                                  self.report.cur_section(with_prepended_summary=True))
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _flag_features_with_attribute_value(self, objects: List['S57Record10'],
                                            attribute: str, values_to_flag: List[str],
                                            check_attrib_existence: bool = False, possible: bool = False) -> List[list]:
        """Flag the passed features if they have the passed values for the passed attribute"""
        flagged = list()

        for obj in objects:
            # do the test
            has_attribute_with_value = False
            has_attribute = False
            for attr in obj.attributes:
                acronym = attr.acronym.strip()
                if acronym == attribute:
                    has_attribute = True
                    if attr.value in values_to_flag:
                        has_attribute_with_value = True

            if check_attrib_existence:
                if not has_attribute:
                    if possible:
                        # add to the flagged report
                        self.report += 'Warning: Found missing attribute %s at (%.7f, %.7f)' \
                                       % (obj.acronym, obj.centroid.x, obj.centroid.y)
                        # add to the flagged feature list
                        self.flags.append(obj.centroid.x, obj.centroid.y,
                                          "warning: missing attribute: %s" % attribute,
                                          self.report.cur_section(with_prepended_summary=True))
                    else:
                        # add to the flagged report
                        self.report += 'Found missing attribute %s at (%.7f, %.7f)' \
                                       % (obj.acronym, obj.centroid.x, obj.centroid.y)
                        # add to the flagged feature list
                        self.flags.append(obj.centroid.x, obj.centroid.y, "missing attribute: %s" % attribute,
                                          self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

            # check passed
            if not has_attribute_with_value:
                continue

            # add to the flagged feature list
            if possible:
                # add to the flagged report
                self.report += 'Warning: Found invalid/prohibited attribute value for %s at (%.7f, %.7f)' \
                               % (obj.acronym, obj.centroid.x, obj.centroid.y)
                self.flags.append(obj.centroid.x, obj.centroid.y,
                                  "warning: invalid/prohibited value for %s" % attribute,
                                  self.report.cur_section(with_prepended_summary=True))
            else:
                # add to the flagged report
                self.report += 'Found invalid/prohibited attribute value for %s at (%.7f, %.7f)' \
                               % (obj.acronym, obj.centroid.x, obj.centroid.y)
                self.flags.append(obj.centroid.x, obj.centroid.y, "invalid/prohibited value for %s" % attribute,
                                  self.report.cur_section(with_prepended_summary=True))
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # ### ALL FEATURES ###

    def file_consistency(self):
        self.report += "Checks for feature file consistency [SECTION]"

        self._check_all_features_for_redundancy_and_geometry()

        if self.version in ["2021", "2022"]:
            # New Requirement in 2021 HSSD character limit for all fields with free text strings
            self.report += "Features with text input fields exceeding %d characters [CHECK]" % self.character_limit
            self.flags.all_fts.chars_limit = self._check_character_limit(objects=self.all_fts,
                                                                         attributes=['images', 'invreq', 'keywrd',
                                                                                     'onotes', 'recomd', 'remrks'],
                                                                         character_limit=self.character_limit)

    def _check_all_features_for_redundancy_and_geometry(self) -> None:
        """Function that identifies the presence of duplicated feature looking at their geometries"""
        logger.debug('Checking for feature redundancy...')
        self.report += "Redundant features [CHECK]"

        tmp_features = list()
        features = list()
        for ft in self.all_fts:
            # skip if the feature has not position
            if (len(ft.geo2s) == 0) and (len(ft.geo3s) == 0):
                # logger.debug("removing: %s" % ft)
                continue

            tmp_features.append(ft)

            # get the attributes as a long string
            attrs_str = str()
            for attr in ft.attributes:
                attrs_str += "%s=%s;" % (attr.acronym.strip(), attr.value)

            # get the point positions as sorted list of string
            geo2x = list()
            geo2y = list()
            if len(ft.geo2s) > 0:
                for geo2 in ft.geo2s:
                    geo2x.append("%.7f" % geo2.x)
                    geo2y.append("%.7f" % geo2.y)
            elif len(ft.geo3s) > 0:
                for geo3 in ft.geo3s:
                    geo2x.append("%.7f" % geo3.x)
                    geo2y.append("%.7f" % geo3.y)
            geo2x.sort()
            geo2y.sort()

            # test for redundancy
            # logger.info("key: %s" % [ft.acronym, attrs_str, geo2x, geo2y])
            i = features.count([ft.acronym, attrs_str, geo2x, geo2y])
            if i > 0:  # we have a redundancy
                if ft.acronym in ["LIGHTS", ]:
                    # add to the flagged report
                    self.report += 'Warning: Redundant %s at (%.7f, %.7f)' % (ft.acronym, ft.centroid.x, ft.centroid.y)
                    # add to the flagged feature list
                    self.flags.append(ft.centroid.x, ft.centroid.y, "warning: redundant %s" % ft.acronym,
                                      self.report.cur_section(with_prepended_summary=True))
                else:
                    # add to the flagged report
                    self.report += 'Redundant %s at (%.7f, %.7f)' % (ft.acronym, ft.centroid.x, ft.centroid.y)
                    # add to the flagged feature list
                    self.flags.append(ft.centroid.x, ft.centroid.y, "redundant %s" % ft.acronym,
                                      self.report.cur_section(with_prepended_summary=True))
                self.flags.all_fts.redundancy.append([ft.acronym, geo2x, geo2y])
            else:
                # populated the feature list
                features.append([ft.acronym, attrs_str, geo2x, geo2y])

        if len(self.flags.all_fts.redundancy) == 0:
            self.report += "OK"

        self.all_fts = tmp_features  # to remove features without geometry

    # ### ASSIGNED FEATURES ###

    def assigned_features(self):

        self.report += "Checks for assigned features [SECTION]"

        # Isolate only features that are assigned
        self.assigned_fts = S57Aux.select_by_attribute_value(objects=self.all_fts, attribute='asgnmt',
                                                             value_filter=['2', ])
        # Ensure assigned features have descrp
        self.report += "Assigned features with empty or missing mandatory attribute description [CHECK]"
        self.flags.ass_fts.description = self._flag_features_with_attribute_value(objects=self.assigned_fts,
                                                                                  attribute='descrp',
                                                                                  values_to_flag=['', ],
                                                                                  check_attrib_existence=True)

        # Ensure assigned features have remrks
        self.report += "Assigned features missing mandatory attribute remarks [CHECK]"
        self.flags.ass_fts.remarks = self._check_features_for_attribute(objects=self.assigned_fts, attribute='remrks')

    # ### NEW OR UPDATED FEATURES ###

    def new_or_updated_features(self):

        self.report += "Checks for new/updated features [SECTION]"

        # Remove carto features
        self.no_carto_fts = S57Aux.filter_by_object(objects=self.all_fts, object_filter=['$AREAS', '$LINES', '$CSYMB',
                                                                                         '$COMPS', '$TEXTS'])

        # Isolate only features with descrp = New or Update
        self.new_updated_fts = S57Aux.select_by_attribute_value(objects=self.no_carto_fts, attribute='descrp',
                                                                value_filter=['1', '2', ])

        # Ensure new or updated features have SORIND
        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORIND [CHECK]"
        self.flags.new_updated_fts.sorind = self._check_features_for_attribute(
            objects=self.new_updated_fts,
            attribute='SORIND')

        # Ensure new or updated features have valid SORIND
        self.report += "New or Updated features (excluding carto notes) with invalid SORIND [CHECK]"
        if self.sorind is None:
            self.flags.new_updated_fts.sorind_invalid = self._check_features_for_valid_sorind(
                objects=self.new_updated_fts,
                check_space=False)
        else:
            self.flags.new_updated_fts.sorind_invalid = self._check_features_for_match_sorind(
                objects=self.new_updated_fts)

        # Ensure new or updated features have SORDAT
        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORDAT [CHECK]"
        self.flags.new_updated_fts.sordat = self._check_features_for_attribute(
            objects=self.new_updated_fts,
            attribute='SORDAT')

        # Ensure new or updated features have valid SORDAT
        self.report += "New or Updated features (excluding carto notes) with invalid SORDAT [CHECK]"
        if self.sordat is None:
            self.flags.new_updated_fts.sordat_invalid = self._check_features_for_valid_sordat(self.new_updated_fts)
        else:
            self.flags.new_updated_fts.sordat_invalid = self._check_features_for_match_sordat(self.new_updated_fts)

        # Select all the new features with VALSOU attribute
        if self.use_mhw:
            new_valsous = S57Aux.select_by_attribute(
                objects=self.new_updated_fts,
                attribute='VALSOU')

            self.report += "New or Updated VALSOU features with invalid WATLEV [CHECK]"
            self.flags.new_updated_fts.valsous_watlev = self._check_features_for_valid_watlev(
                objects=new_valsous)

        new_elevats = S57Aux.select_by_attribute(
            objects=self.new_updated_fts,
            attribute='ELEVAT')

        self.report += "Invalid New or Updated ELEVAT features [CHECK]"
        self.flags.new_updated_fts.elevat = self._check_features_for_valid_elevat(
            objects=new_elevats)

        # Select all the new features with valsou attribute and check for valid quasou.
        new_valsous = S57Aux.select_by_attribute(objects=self.new_updated_fts, attribute='VALSOU')
        self.report += "New or Updated VALSOU features with invalid QUASOU [CHECK]"
        self.flags.new_updated_fts.valsous_quasou = self._check_features_for_valid_quasou(new_valsous)

    @classmethod
    def check_sorind(cls, value: str, check_space: bool = True) -> bool:
        tokens = value.split(',')
        # logger.debug("%s" % tokens)

        if len(value.splitlines()) > 1:
            logger.info('too many attribute lines')
            return False

        elif len(tokens) != 4:
            logger.info('invalid number of comma-separated fields')
            return False

        elif (tokens[0][0] == " " or tokens[1][0] == " " or tokens[2][0] == " " or tokens[3][0] == " ") \
                and check_space:
            logger.info('invalid space after comma field-separator')
            return False

        elif tokens[0] != "US":
            logger.info('first field should be "US", it is: "%s"' % tokens[0])
            return False

        elif tokens[1] != "US":
            logger.info('second field should be "US", it is: "%s"' % tokens[1])
            return False

        elif tokens[2] != "graph":
            logger.info('third field should be "graph", it is: "%s"' % tokens[2])
            return False

        if len(tokens[3]) != 6:
            logger.info('issue with forth field length: %d (it should be 6)' % len(tokens[3]))
            return False

        return True

    def _check_features_for_valid_sorind(self, objects: List['S57Record10'],
                                         check_space: bool = True) -> List[list]:
        """Check if the passed features have valid SORIND"""
        flagged = list()

        for obj in objects:
            # do the test
            is_valid = True
            for attr in obj.attributes:
                if attr.acronym == "SORIND":
                    is_valid = self.check_sorind(attr.value, check_space)
                    break

            # check passed
            if is_valid:
                continue

            # add to the flagged report
            self.report += 'Found %s at (%.7f, %.7f) with invalid SORIND' \
                           % (obj.acronym, obj.centroid.x, obj.centroid.y)
            # add to the flagged feature list
            self.flags.append(obj.centroid.x, obj.centroid.y, "invalid SORIND",
                              self.report.cur_section(with_prepended_summary=True))
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_for_match_sorind(self, objects: List['S57Record10']) -> List[list]:
        """Check if the passed features have valid SORIND"""
        flagged = list()

        for obj in objects:
            # do the test
            is_valid = True
            for attr in obj.attributes:
                if attr.acronym == "SORIND":
                    is_valid = attr.value == self.sorind
                    break

            # check passed
            if is_valid:
                continue

            # add to the flagged report
            self.report += 'Found %s at (%.7f, %.7f) with invalid SORIND' % (
                obj.acronym, obj.centroid.x, obj.centroid.y)
            # add to the flagged feature list
            self.flags.append(obj.centroid.x, obj.centroid.y, "invalid SORIND",
                              self.report.cur_section(with_prepended_summary=True))
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    @classmethod
    def check_sordat(cls, value: str) -> bool:

        # logger.debug("%s" % attr.value)

        cast_issue = False
        timestamp = None
        now = None
        # noinspection PyBroadException
        try:
            timestamp = datetime.datetime(year=int(value[0:4]),
                                          month=int(value[4:6]),
                                          day=int(value[6:8]))
            now = datetime.datetime.now()

        except Exception:
            cast_issue = True

        if cast_issue:
            logger.info('invalid date format: %s' % value)
            return False

        elif len(value) != 8:
            logger.info('the date format is YYYYMMDD, invalid number of digits: %d' % len(value))
            return False

        elif timestamp > now:
            if (timestamp.year > now.year) or (timestamp.year == now.year and timestamp.month > now.month):
                logger.info('the date in use is in the future: %d' % len(value))
                return False

        return True

    def _check_features_for_valid_sordat(self, objects: List['S57Record10']) -> List[list]:
        """Check if the passed features have matching SORDAT"""
        flagged = list()

        for obj in objects:
            # do the test
            is_valid = True
            for attr in obj.attributes:
                if attr.acronym == "SORDAT":
                    is_valid = self.check_sordat(attr.value)
                    break

            # check passed
            if is_valid:
                continue

            # add to the flagged report
            self.report += 'Found %s at (%.7f, %.7f) with invalid SORDAT' % (
                obj.acronym, obj.centroid.x, obj.centroid.y)
            # add to the flagged feature list
            self.flags.append(obj.centroid.x, obj.centroid.y, "invalid SORDAT",
                              self.report.cur_section(with_prepended_summary=True))
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_for_match_sordat(self, objects: List['S57Record10']) -> List[list]:
        """Check if the passed features have matching SORDAT"""
        flagged = list()

        for obj in objects:
            # do the test
            is_valid = True
            for attr in obj.attributes:
                if attr.acronym == "SORDAT":
                    is_valid = attr.value == self.sordat
                    break

            # check passed
            if is_valid:
                continue

            # add to the flagged report
            self.report += 'Found %s at (%.7f, %.7f) with invalid SORDAT' % (
                obj.acronym, obj.centroid.x, obj.centroid.y)
            # add to the flagged feature list
            self.flags.append(obj.centroid.x, obj.centroid.y, "invalid SORDAT",
                              self.report.cur_section(with_prepended_summary=True))
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_for_valid_watlev(self, objects: List['S57Record10']) -> List[list]:
        """Check if the passed features have valid WATLEV"""
        # logger.debug("checking for invalid WATLEV and VALSOU ...")

        flagged = list()

        for obj in objects:
            # do the test
            is_valid = True
            is_invalid_for_valsou = False
            watlev = None
            valsou = None
            for attr in obj.attributes:

                if attr.acronym == "WATLEV":
                    try:
                        watlev = int(attr.value)
                    except ValueError:
                        logger.warning("issue with WATLEV value:'%s' at position: %s, %s" %
                                       (attr.value, obj.centroid.x, obj.centroid.y))

                elif attr.acronym == "VALSOU":
                    try:
                        valsou = float(attr.value)
                    except ValueError:
                        logger.warning("issue with VALSOU value:'%s' at position: %s, %s" %
                                       (attr.value, obj.centroid.x, obj.centroid.y))

                if (watlev is not None) and (valsou is not None):
                    break

            if (watlev is None) or (valsou is None):
                logger.debug("unable to find WATLEV or VALSOU values at position: %s, %s" %
                             (obj.centroid.x, obj.centroid.y))
                continue

            if self.survey_area == self.survey_areas["Great Lakes"]:
                if valsou < - 0.1:
                    is_valid = False
                    is_invalid_for_valsou = True
                else:
                    if valsou <= -0.1:
                        if watlev != 4:  # Covers & Uncovers
                            is_valid = False
                    elif valsou <= 0.1:
                        if watlev != 5:  # Awash
                            is_valid = False
                    else:
                        if watlev != 3:  # Always Underwater
                            is_valid = False

            else:

                if valsou < (-self.mhw_value - 0.1):
                    is_valid = False
                    is_invalid_for_valsou = True
                else:
                    if valsou <= -0.1:
                        if watlev != 4:  # Covers & Uncovers
                            is_valid = False
                    elif valsou <= 0.1:
                        if watlev != 5:  # Awash
                            is_valid = False
                    else:
                        if watlev != 3:  # Always Underwater
                            is_valid = False

            # check passed
            if is_valid:
                continue

            # add to the flagged feature list and to the flagged report
            if is_invalid_for_valsou:
                self.report += 'Found %s at (%.7f, %.7f) with invalid VALSOU (islet ?)' % (
                    obj.acronym, obj.centroid.x, obj.centroid.y)
                self.flags.append(obj.centroid.x, obj.centroid.y, "invalid VALSOU (islet ?)",
                                  self.report.cur_section(with_prepended_summary=True))
            else:
                self.report += 'Found %s at (%.7f, %.7f) with invalid WATLEV' % (
                    obj.acronym, obj.centroid.x, obj.centroid.y)
                self.flags.append(obj.centroid.x, obj.centroid.y, "invalid WATLEV",
                                  self.report.cur_section(with_prepended_summary=True))
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        # logger.debug("checking for invalid WATLEV and VALSOU -> flagged: %d" % len(flagged))

        return flagged

    def _check_features_for_valid_elevat(self, objects: List['S57Record10']) -> List[list]:
        """Check if the passed features have valid ELEVAT"""
        # logger.debug("checking for invalid ELEVAT ...")

        flagged = list()

        for obj in objects:

            elevat = None
            for attr in obj.attributes:
                if attr.acronym == "ELEVAT":
                    elevat = float(attr.value)

                if elevat is not None:
                    break

            if elevat > +0.1:
                continue

            self.report += 'Found %s at (%.7f, %.7f) with invalid ELEVAT' % (
                obj.acronym, obj.centroid.x, obj.centroid.y)
            # add to the flagged feature list and to the flagged report
            self.flags.append(obj.centroid.x, obj.centroid.y, "invalid ELEVAT",
                              self.report.cur_section(with_prepended_summary=True))
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        # logger.debug("checking for invalid ELEVAT -> flagged: %d" % len(flagged))

        return flagged

    def _check_features_for_valid_quasou(self, objects: List['S57Record10']) -> List[list]:
        """Check if the passed features have valid QUASOU"""
        # logger.debug("checking for invalid QUASOU ...")

        # list the allowable combinations of tecsous and quasous
        allowable = [['3', '6'], ['4', '6'], ['5', '6'], ['12', '6'], ['2', '9']]

        flagged = list()
        for obj in objects:

            tecsou = None
            quasou = None

            # check for the TECSOU and QUASOU attributes
            for attr in obj.attributes:
                if attr.acronym == "TECSOU":
                    tecsou = attr.value
                elif attr.acronym == "QUASOU":
                    quasou = attr.value

                if (tecsou is not None) and (quasou is not None):
                    break

            if tecsou is None:
                self.report += 'Could not verify QUASOU found %s at (%.7f, %.7f) because is missing TECSOU' \
                               % (obj.acronym, obj.centroid.x, obj.centroid.y)
                # logger.debug("checking for TECSOU...")
                self.flags.append(obj.centroid.x, obj.centroid.y, 'missing TECSOU required for QUASOU',
                                  self.report.cur_section(with_prepended_summary=True))
                flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                continue

            elif tecsou in ['1', '7', '10']:  # VBES, Lidar, Structure from Motion
                if quasou is not None:
                    # add to the flagged report
                    self.report += "Warning: found %s at (%.7f, %.7f) has TECSOU '%s' without blank QUASOU" \
                                   % (obj.acronym, obj.centroid.x, obj.centroid.y, tecsou)
                    # add to the flagged feature list
                    self.flags.append(obj.centroid.x, obj.centroid.y,
                                      "warning: TECSOU requires blank QUASOU: %s" % (tecsou,),
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                continue

            # if QUASOU is not available?
            if quasou is None:
                logger.debug("Checking for QUASOU...")
                self.report += 'Found %s at (%.7f, %.7f) is missing QUASOU required for TECSOU' \
                               % (obj.acronym, obj.centroid.x, obj.centroid.y)
                self.flags.append(obj.centroid.x, obj.centroid.y, 'missing QUASOU required for TECSOU',
                                  self.report.cur_section(with_prepended_summary=True))
                flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                continue

            # splitting using ','
            tecsou = tecsou.split(',')
            quasou = quasou.split(',')

            # if the list of QUASOU has different length than the list of TECSOU ?
            if len(tecsou) != len(quasou):
                self.report += 'Warning: found %s at (%.7f, %.7f) contains mismatch in the number of TECSOU and ' \
                               'QUASOU attributes' % (obj.acronym, obj.centroid.x, obj.centroid.y)
                self.flags.append(obj.centroid.x, obj.centroid.y, 'warning: mismatch in the number of TECSOU and '
                                                                  'QUASOU attributes',
                                  self.report.cur_section(with_prepended_summary=True))
                flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                continue

            for i in range(len(tecsou)):

                check = [tecsou[i], quasou[i]]
                if check in allowable:
                    continue

                # add to the flagged report
                self.report += 'Warning: found %s at (%.7f, %.7f) has prohibited TECSOU/QUASOU combination %s' \
                               % (obj.acronym, obj.centroid.x, obj.centroid.y, check)
                # add to the flagged feature list
                self.flags.append(obj.centroid.x, obj.centroid.y,
                                  "warning: TECSOU and QUASOU combination is not allowed %s" % (check,),
                                  self.report.cur_section(with_prepended_summary=True))
                flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                break

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # ### NEW OR DELETED FEATURES ###

    def new_or_deleted_features(self):

        self.report += "Checks for new/deleted features [SECTION]"

        # Isolate features with descrp = New or Delete
        self.new_deleted_fts = S57Aux.select_by_attribute_value(objects=self.all_fts, attribute='descrp',
                                                                value_filter=['1', '3'])

        # Ensure new or deleted features have remrks
        self.report += "New/Delete features missing mandatory attribute remarks [CHECK]"
        self.flags.new_deleted_fts.remarks = self._check_features_for_attribute(objects=self.new_deleted_fts,
                                                                                attribute='remrks')

        if self.version in ["2019", "2020", "2021"]:
            # Ensure new or deleted features have recomd
            self.report += "New/Delete features missing mandatory attribute recommendation [CHECK]"
            self.flags.new_deleted_fts.recommend = self._check_features_for_attribute(objects=self.new_deleted_fts,
                                                                                      attribute='recomd')

    # ### IMAGES ###

    def images(self):

        self.report += "Checks for features with images [SECTION]"

        # Ensure all features for valid paths
        self.flags.images.invalid_paths = self._check_features_for_images_path(objects=self.all_fts)

        if not self.check_image_names:
            return

        # Isolate new or updated seabed areas (points + lines & areas)
        sbdare = S57Aux.select_by_object(objects=self.new_updated_fts, object_filter=['SBDARE', ])
        sbdare_points = S57Aux.select_only_points(sbdare)
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)
        non_sbdare_features = S57Aux.filter_by_object(objects=self.all_fts, object_filter=['SBDARE', ])

        if self.version in ["2019", ]:
            self.report += "Invalid IMAGE name per HTD 2018-4/5 [CHECK]"
            self.flags.images.invalid_names = \
                self._check_sbdare_images_per_htd_2018_4(objects=sbdare_points) + \
                self._check_nonsbdare_images_per_htd_2018_5(objects=sbdare_lines_areas + non_sbdare_features)

        elif self.version in ["2020", ]:
            self.report += "Invalid IMAGE name per HSSD 2020 [CHECK]"
            self.flags.images.invalid_names = \
                self._check_sbdare_images_per_htd_2018_4(objects=sbdare_points) + \
                self._check_nonsbdare_images_per_htd_2018_5(objects=sbdare_lines_areas + non_sbdare_features)

        elif self.version in ["2021", "2022"]:

            self.report += "Invalid IMAGE name per HSSD [CHECK]"
            self.flags.images.invalid_names = \
                self._check_sbdare_images_per_hssd_2021(objects=sbdare_points) + \
                self._check_nonsbdare_images_per_hssd_2021(
                    objects=sbdare_points + non_sbdare_features + sbdare_lines_areas)

        if len(self.flags.images.invalid_names) == 0:
            self.report += "OK"

    def _check_features_for_images_path(self, objects: List['S57Record10']) -> List[list]:
        # Checked if passed images have correct separator per HSSD and are found in the multimedia folder
        # logger.debug("checking for invalid IMAGES ...")

        self.report += "Images are not present in the Multimedia folder [CHECK]"

        flagged = list()

        for obj in objects:
            images = None
            for attr in obj.attributes:
                if attr.acronym == "images":
                    images = attr.value

            if images is None:
                continue

            images_list = [image.upper() for image in images.split(";")]

            for image_filename in images_list:

                if "," in image_filename:
                    self.report += 'Found %s at (%.7f, %.7f) with image having invalid separator: %s' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "invalid separator",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                if self.multimedia_folder is None:
                    self.report += 'Found %s at (%.7f, %.7f) with missing images folder: %s' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "missing images folder",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                if images_list.count(image_filename) > 1:
                    self.report += 'Found %s at (%.7f, %.7f) with a list of images without unique name: %s' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "listed image names not unique",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                img_path = os.path.join(self.multimedia_folder, image_filename.strip())
                if not os.path.exists(img_path):
                    self.report += 'Found %s at (%.7f, %.7f) with invalid path to image: %s' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    self.flags.append(obj.centroid.x, obj.centroid.y, "invalid path",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

        if len(flagged) == 0:
            self.report += "OK"

        # logger.debug("checking for invalid images -> flagged: %d" % len(flagged))

        return flagged

    def _check_nonsbdare_images_per_htd_2018_5(self, objects: List['S57Record10']) -> List[list]:
        """"Check if the passed features have valid image name per HTD 2018-5"""
        # logger.debug("checking for invalid IMAGE NAMES per HTD 2018-5...")

        flagged = list()

        for obj in objects:
            images = None
            for attr in obj.attributes:
                if attr.acronym == "images":
                    images = attr.value

            if images is None:
                continue

            images_list = [image.upper() for image in images.split(";")]

            for image_filename in images_list:

                image_filename = os.path.splitext(image_filename)[0]
                tokens = image_filename.split("_")

                if len(tokens) not in [2, 3]:
                    self.report += 'Found %s at (%.7f, %.7f) with image having invalid filenaming (nr. of "_"): %s' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "invalid filenaming",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                if len(tokens[0]) != 6:
                    self.report += 'Found %s at (%.7f, %.7f) with image having invalid survey in filename: %s' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "invalid survey in filename",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                if len(tokens[1]) != 15:
                    self.report += 'Found %s at (%.7f, %.7f) with image having invalid FIDN+FIDS in filename: %s' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "invalid FIDN+FIDS in filename",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

        # logger.debug("checking for invalid image names per HTD 2018-5 -> flagged %d" % len(flagged))

        return flagged

    def _check_sbdare_images_per_htd_2018_4(self, objects: List['S57Record10']) -> List[list]:
        """"Check if the passed features have valid image name per HTD 2018-4"""
        # logger.debug("checking for invalid IMAGE NAMES per HTD 2018-4...")

        flagged = list()

        for obj in objects:
            images = None
            for attr in obj.attributes:
                if attr.acronym == "images":
                    images = attr.value

            if images is None:
                continue

            images_list = [image.upper() for image in images.split(";")]

            for image_filename in images_list:

                image_filename = os.path.splitext(image_filename)[0]
                tokens = image_filename.split("_")

                if len(tokens) != 3:
                    self.report += 'Found %s at (%.7f, %.7f) with image having invalid filenaming (nr. of "_"): %s ' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "invalid filenaming",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                if len(tokens[0]) != 6:
                    self.report += 'Found %s at (%.7f, %.7f) with image having invalid survey in filename: %s ' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "invalid survey in filename",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                if tokens[1] != "SBDARE":
                    self.report += 'Found %s at (%.7f, %.7f) with "_SBDARE_" not present in filename: %s ' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "'_SBDARE_' not present in filename",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                if self.version in ["2019", ]:
                    if len(tokens[2]) != 15:
                        self.report += 'Found %s at (%.7f, %.7f) with image having invalid timestamp in filename: ' \
                                       '%s ' % (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                        # add to the flagged feature list and to the flagged report
                        self.flags.append(obj.centroid.x, obj.centroid.y, "invalid timestamp in filename",
                                          self.report.cur_section(with_prepended_summary=True))
                        flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                        continue
                if self.version in ["2020", ]:
                    if len(tokens[2]) not in [14, 15]:
                        self.report += 'Found %s at (%.7f, %.7f) with image having invalid timestamp in filename: ' \
                                       '%s ' % (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                        # add to the flagged feature list and to the flagged report
                        self.flags.append(obj.centroid.x, obj.centroid.y, "invalid timestamp in filename",
                                          self.report.cur_section(with_prepended_summary=True))
                        flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                        continue

        # logger.debug("checking for invalid image names per HTD 2018-4 -> flagged: %d" % len(flagged))

        return flagged

    def _check_sbdare_images_per_hssd_2021(self, objects: List['S57Record10']) -> List[list]:
        """"Check if the passed features have valid image name per HSSD"""
        # logger.debug("checking for invalid IMAGE NAMES per HSSD...")

        flagged = list()

        for obj in objects:
            images = None
            for attr in obj.attributes:
                if attr.acronym == "images":
                    images = attr.value

            if images is None:
                continue

            images_list = [image.upper() for image in images.split(";")]

            for image_filename in images_list:

                image_filename = os.path.splitext(image_filename)[0]
                tokens = image_filename.split("_")

                if len(tokens) != 3:
                    self.report += 'Found %s at (%.7f, %.7f) with image having invalid filenaming (nr. of "_"): ' \
                                   '%s ' % (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "invalid filenaming",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                if len(tokens[0]) != 6:
                    self.report += 'Found %s at (%.7f, %.7f) with image having invalid survey in filename: %s ' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "invalid survey in filename",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                if tokens[1] != "SBDARE":
                    self.report += 'Found %s at (%.7f, %.7f) with "SBDARE" not stated in filename: %s ' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "'SBDARE' not stated in filename",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

                try:
                    _ = int(tokens[2])
                except ValueError:
                    self.report += 'Found %s at (%.7f, %.7f) with image not having numeric identifier in filename: ' \
                                   '%s ' % (obj.acronym, obj.centroid.x, obj.centroid.y, image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "no numeric identifier in filename",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

        # logger.debug("checking for invalid image names per HSSD -> flagged: %d" % len(flagged))

        return flagged

    def _check_nonsbdare_images_per_hssd_2021(self, objects: List['S57Record10']) -> List[list]:
        """"Check if the passed features have valid image name per HSSD"""
        # create check that makes sure that the image naming convention is just a unique name.

        flagged = list()
        names = dict()

        for obj in objects:
            images = None
            for attr in obj.attributes:
                if attr.acronym == "images":
                    images = attr.value

            if images is None:
                continue

            images_list = [image.lower() for image in images.split(";")]

            for image_filename in images_list:

                image_filename = os.path.splitext(image_filename)[0]
                if image_filename in names.keys():
                    self.report += 'Warning: Found %s at (%.7f, %.7f) with same image filename as %s: %s' % \
                                   (obj.acronym, obj.centroid.x, obj.centroid.y, names[image_filename], image_filename)
                    # add to the flagged feature list and to the flagged report
                    self.flags.append(obj.centroid.x, obj.centroid.y, "warning: duplicated image filename",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                else:
                    names[image_filename] = "%s at (%.7f, %.7f)" % (obj.acronym, obj.centroid.x, obj.centroid.y)

        # logger.debug("checking for invalid image names per HSSD 2021 -> flagged: %d" % len(flagged))

        return flagged

    # SOUNDINGS

    def soundings(self):

        self.report += "Checks for soundings [SECTION]"

        # Isolate sounding features
        sounding_fts = S57Aux.select_by_object(objects=self.all_fts, object_filter=['SOUNDG', ])

        # filter out soundings with tecsou vbes, lidar, photogrammetry
        sounding_filtered_tecsou = S57Aux.filter_by_attribute_value(objects=sounding_fts, attribute='TECSOU',
                                                                    value_filter=['1', '7', '10', ])

        # Ensure soundings have tecsou
        self.report += "SOUNDG with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flags.soundings.tecsou = self._flag_features_with_attribute_value(objects=sounding_fts, attribute='TECSOU',
                                                                               values_to_flag=['', ],
                                                                               check_attrib_existence=True)
        # Ensure soundings have quasou, quasou shall be left blank for vbes, lidar, photogrammetry
        self.report += "SOUNDG with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flags.soundings.quasou = self._flag_features_with_attribute_value(objects=sounding_filtered_tecsou,
                                                                               attribute='QUASOU',
                                                                               values_to_flag=['', ],
                                                                               check_attrib_existence=True)

    # DTONS

    def dtons(self):

        self.report += "Checks for DTONs [SECTION]"

        # Isolate features that are no-carto, descrp = New or Updated, and sftype = DTON
        dtons = S57Aux.select_by_attribute_value(objects=self.new_updated_fts, attribute='sftype', value_filter=['3', ])

        # Remove soundings to prevent WRECK and OBSTRN DtoN objects from getting the image flag twice.
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['WRECKS', 'OBSTRN'])

        # Ensure DTONs have images
        self.report += "Special feature types (DTONS) missing images [CHECK]"
        self.flags.dtons.images = self._check_features_for_attribute(objects=dtons, attribute='images')

    # WRECKS

    def wrecks(self):

        self.report += "Checks for wrecks [SECTION]"

        # Isolate new or updated wrecks
        wrecks = S57Aux.select_by_object(objects=self.new_updated_fts, object_filter=['WRECKS', ])
        # Filter wrecks if they have a known, undefined, and unknown valsou.
        wrecks_valsou = S57Aux.select_by_attribute(objects=wrecks, attribute='VALSOU')
        # logger.debug("Total number of wrecks without undefined VALSOU: %d" % (len(wrecks_valsou)))
        wrecks_undefined_valsou = S57Aux.filter_by_attribute(wrecks, attribute='VALSOU')
        # logger.debug("Total number of wrecks with undefined VALSOU: %d" % (len(wrecks_undefined_valsou)))
        # filter out wrecks with tecsou vbes, lidar, photogrammetry
        wrecks_filtered_tecsou = S57Aux.filter_by_attribute_value(objects=wrecks_valsou, attribute='TECSOU',
                                                                  value_filter=['1', '7', '10', ])
        # select wrecks if they have Height
        wrecks_height = S57Aux.select_by_attribute(objects=wrecks, attribute='HEIGHT')

        # from wrecks with undefined VALSOU, filter out wrecks with HEIGHT
        wrecks_undefined_valsou_no_height = S57Aux.filter_by_attribute(wrecks_undefined_valsou, attribute='HEIGHT')

        # Ensure new or updated wrecks have images
        self.report += "New or Updated WRECKS missing images [CHECK]"
        self.flags.wrecks.images = self._check_features_for_attribute(objects=wrecks, attribute='images')

        # Ensure new or updated wrecks have catwrk
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute CATWRK [CHECK]"
        self.flags.wrecks.catwrk = self._flag_features_with_attribute_value(objects=wrecks, attribute='CATWRK',
                                                                            values_to_flag=['', ],
                                                                            check_attrib_existence=True)

        if self.version in ["2019", "2020", "2021"]:
            self.report += "Warning: New or Updated WRECKS missing mandatory attribute VALSOU [CHECK]"
            self.flags.wrecks.valsou = self._check_features_for_attribute(objects=wrecks, attribute='VALSOU',
                                                                          possible=True)

        if self.version in ["2022"]:
            # Ensure new or updated wrecks should have valsou or height
            self.report += "Warning: New or Updated WRECKS having just one of " \
                           "mandatory attributes VALSOU or HEIGHT [CHECK]"
            self.flags.wrecks.valsou = self._check_features_for_just_one_of_attributes_in_list(
                objects=wrecks, xor_attributes=['VALSOU', 'HEIGHT'], possible=True)

        # If wreck has valsou, must have watlev, quasou, tecsou
        # Ensure wrecks with valsou contain watlev
        self.report += "New or Updated WRECKS with VALSOU with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flags.wrecks.watlev = self._flag_features_with_attribute_value(wrecks_valsou,
                                                                            attribute='WATLEV',
                                                                            values_to_flag=['', ],
                                                                            check_attrib_existence=True)
        # Ensure new or updated wrecks have quasou unless quasou left blank if tecsou is vbes, photogrammetry, or lidar
        self.report += "New or Updated WRECKS with VALSOU with missing mandatory attribute QUASOU [CHECK]"
        self.flags.wrecks.quasou = self._flag_features_with_attribute_value(objects=wrecks_filtered_tecsou,
                                                                            attribute='QUASOU',
                                                                            values_to_flag=['', ],
                                                                            check_attrib_existence=True)

        # Ensure new or updated wrecks have tecsou
        self.report += "New or Updated WRECKS with VALSOU with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flags.wrecks.tecsou = self._flag_features_with_attribute_value(objects=wrecks_valsou, attribute='TECSOU',
                                                                            values_to_flag=['', ],
                                                                            check_attrib_existence=True)

        # If wreck does not have VALSOU...

        if self.version in ["2019", "2020", "2021"]:
            # Warning: Ensure wrecks with unknown valsou have watlev unknown
            self.report += "Warning: New or Updated WRECKS with empty VALSOU shall have WATLEV of 'unknown' [CHECK]"
            self.flags.wrecks.unknown_watlev = self._flag_features_with_attribute_value(wrecks_undefined_valsou,
                                                                                        attribute='WATLEV',
                                                                                        values_to_flag=["1", "2", "3",
                                                                                                        "4",
                                                                                                        "5", "6",
                                                                                                        "7", ],
                                                                                        check_attrib_existence=True,
                                                                                        possible=True)

            # Ensure wrecks with unknown valsou have tecsou "unknown"
            self.report += "New or Updated WRECKS with empty VALSOU shall have TECSOU of 'unknown' [CHECK]"
            self.flags.wrecks.unknown_tecsou = self._flag_features_with_attribute_value(wrecks_undefined_valsou,
                                                                                        attribute='TECSOU',
                                                                                        values_to_flag=["1", "2", "3",
                                                                                                        "4",
                                                                                                        "5", "6", "7",
                                                                                                        "8",
                                                                                                        "9", "10", "11",
                                                                                                        "12", "13",
                                                                                                        "14", ],
                                                                                        check_attrib_existence=True)

            # Ensure wrecks with unknown valsou have quasou "unknown"
            self.report += "New or Updated WRECKS with empty VALSOU shall have QUASOU of NULL [CHECK]"
            self.flags.wrecks.unknown_quasou = self._flag_features_with_attribute_value(wrecks_undefined_valsou,
                                                                                        attribute='QUASOU',
                                                                                        values_to_flag=["1", "2", "3",
                                                                                                        "4",
                                                                                                        "5", "6", "7",
                                                                                                        "8",
                                                                                                        "9", "10",
                                                                                                        "11"])

        if self.version in ["2022"]:
            # Warning: Ensure wrecks with unknown valsou have watlev unknown
            self.report += "Warning: New or Updated WRECKS with empty VALSOU and empty HEIGHT shall have WATLEV of " \
                           "'unknown' [CHECK]"
            self.flags.wrecks.unknown_watlev = self._flag_features_with_attribute_value(
                wrecks_undefined_valsou_no_height,
                attribute='WATLEV',
                values_to_flag=["1", "2", "3", "4",
                                "5", "6", "7", ],
                check_attrib_existence=True,
                possible=True)

            # if wreck has height, WATLEV is always dry
            self.report += "Warning: New or Updated WRECKS with HEIGHT shall have WATLEV of 'Always Dry' [CHECK]"
            self.flags.wrecks.height_watlev = self._flag_features_with_attribute_value(wrecks_height,
                                                                                       attribute='WATLEV',
                                                                                       values_to_flag=["1", "3", "4",
                                                                                                       "5", "6", "7", ],
                                                                                       check_attrib_existence=True,
                                                                                       possible=True)

            # Ensure wrecks with unknown valsou have tecsou "unknown"
            self.report += "New or Updated WRECKS with empty VALSOU and empty HEIGHT shall have TECSOU of 'unknown' " \
                           "[CHECK]"
            self.flags.wrecks.unknown_tecsou = self._flag_features_with_attribute_value(
                wrecks_undefined_valsou_no_height,
                attribute='TECSOU',
                values_to_flag=["1", "2", "3", "4",
                                "5", "6", "7", "8",
                                "9", "10", "11",
                                "12", "13", "14", ],
                check_attrib_existence=True)

            # Ensure wrecks with unknown valsou have quasou "unknown"
            self.report += "New or Updated WRECKS with empty VALSOU shall have QUASOU of NULL [CHECK]"
            self.flags.wrecks.unknown_quasou = self._flag_features_with_attribute_value(
                wrecks_undefined_valsou_no_height,
                attribute='QUASOU',
                values_to_flag=["1", "2", "3", "4",
                                "5", "6", "7", "8",
                                "9", "10", "11"])

            self.report += "Warning: Feature with HEIGHT should not have TECSOU [CHECK]"
            self.flags.wrecks.height_tecsou = self._check_features_without_attribute(objects=wrecks_height,
                                                                                     attribute='TECSOU', possible=False)

            self.report += "Warning: Feature with HEIGHT should not have QUASOU [CHECK]"
            self.flags.wrecks.height_quasou = self._check_features_without_attribute(objects=wrecks_height,
                                                                                     attribute='QUASOU',
                                                                                     possible=False)

    # ROCKS

    def rocks(self):

        self.report += "Checks for underwater rocks [SECTION]"

        # Isolate new or updated rocks
        rocks = S57Aux.select_by_object(objects=self.new_updated_fts, object_filter=['UWTROC', ])
        # Filter rocks if they have a known, undefined, and unknown valsou.
        rocks_valsou = S57Aux.select_by_attribute(objects=rocks, attribute='VALSOU')
        rocks_undefined_valsou = S57Aux.filter_by_attribute(rocks, attribute='VALSOU')
        # filter out rocks with tecsou vbes, lidar, photogrammetry
        rocks_filtered_tecsou = S57Aux.filter_by_attribute_value(objects=rocks_valsou, attribute='TECSOU',
                                                                 value_filter=['1', '7', '10', ])

        # Ensure new or updated rocks have valsou
        self.report += "Warning: New or Updated UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flags.rocks.valsou = self._check_features_for_attribute(objects=rocks, attribute='VALSOU', possible=True)

        # If new or updated rocks have valsou, must have watlev, quasou, tecsou
        self.report += "New or Updated UWTROC with VALSOU with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flags.rocks.watlev = self._flag_features_with_attribute_value(rocks_valsou, attribute='WATLEV',
                                                                           values_to_flag=['', ],
                                                                           check_attrib_existence=True)
        # Ensure new or updated rocks have quasou, quasou should be left blank if vbes, lidar, or photogrammetry
        self.report += "New or Updated UWTROC with VALSOU with missing mandatory attribute QUASOU [CHECK]"
        self.flags.rocks.quasou = self._flag_features_with_attribute_value(objects=rocks_filtered_tecsou,
                                                                           attribute='QUASOU',
                                                                           values_to_flag=['', ],
                                                                           check_attrib_existence=True)

        # Ensure new or updated rocks have tecsou
        self.report += "New or Updated UWTROC with VALSOU with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flags.rocks.tecsou = self._flag_features_with_attribute_value(objects=rocks_valsou, attribute='TECSOU',
                                                                           values_to_flag=['', ],
                                                                           check_attrib_existence=True)

        # If rock does not have VALSOU...
        # Warning: Ensure rocks with unknown valsou have watlev unknown
        self.report += "Warning: New or Updated UWTROC with empty VALSOU shall have WATLEV of 'unknown' [CHECK]"
        self.flags.rocks.unknown_watlev = self._flag_features_with_attribute_value(rocks_undefined_valsou,
                                                                                   attribute='WATLEV',
                                                                                   values_to_flag=["1", "2", "3", "4",
                                                                                                   "5", "6", "7", ],
                                                                                   check_attrib_existence=True,
                                                                                   possible=True)

        # Ensure rocks with unknown valsou have tecsou "unknown"
        self.report += "New or Updated UWTROC with empty VALSOU shall have TECSOU of 'unknown' [CHECK]"
        self.flags.rocks.unknown_tecsou = self._flag_features_with_attribute_value(rocks_undefined_valsou,
                                                                                   attribute='TECSOU',
                                                                                   values_to_flag=["1", "2", "3", "4",
                                                                                                   "5", "6", "7", "8",
                                                                                                   "9", "10", "11",
                                                                                                   "12", "13",
                                                                                                   "14", ],
                                                                                   check_attrib_existence=True)

        # Ensure rocks with unknown valsou have quasou "unknown"
        self.report += "New or Updated UWTROC with empty VALSOU shall have QUASOU of NULL [CHECK]"
        self.flags.rocks.unknown_quasou = self._flag_features_with_attribute_value(rocks_undefined_valsou,
                                                                                   attribute='QUASOU',
                                                                                   values_to_flag=["1", "2", "3", "4",
                                                                                                   "5", "6", "7", "8",
                                                                                                   "9", "10", "11"])

    # OBSTRUCTIONS

    def obstructions(self):

        self.report += "Checks for obstructions [SECTION]"

        # Isolate new or updated obstructions
        obstrns = S57Aux.select_by_object(objects=self.new_updated_fts, object_filter=['OBSTRN', ])

        obstrn_valsou = S57Aux.select_by_attribute(objects=obstrns, attribute='VALSOU')

        obstrn_height = S57Aux.select_by_attribute(objects=obstrns, attribute='HEIGHT')

        # Exclude foul area and ground area obstructions
        obstrns_no_foul_area_ground = S57Aux.filter_by_attribute_value(objects=obstrns, attribute='CATOBS',
                                                                       value_filter=['6', '7', ])

        # select all obstructions without valsous excluding foul ground and area

        obstrn_undefined_valsou = S57Aux.filter_by_attribute(obstrns_no_foul_area_ground, attribute='VALSOU')

        # select all obstructions without valsous and without heights excluding foul ground and area

        obstrn_undefined_valsou_no_height = S57Aux.filter_by_attribute(obstrn_undefined_valsou, attribute='HEIGHT')

        # filter out obstructions with tecsou vbes, lidar, photogrammetry
        obstrn_filtered_tecsou = S57Aux.filter_by_attribute_value(objects=obstrn_valsou, attribute='TECSOU',
                                                                  value_filter=['1', '7', '10', ])

        # Exclude foul area obstructions
        obstrns_no_foul = S57Aux.filter_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])

        # Include foul ground area obstructions
        obstrns_foul_ground = S57Aux.select_by_attribute_value(objects=obstrns, attribute='CATOBS',
                                                               value_filter=['7', ])

        # Include only foul obstructions
        obstrns_foul = S57Aux.select_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])

        # Ensure new or updated obstructions (not foul area) have images
        # Ensure new or updated wrecks have images
        if self.version in ["2019", "2020", "2021"]:
            self.report += "New or Updated OBSTRN (excluding foul areas) missing images [CHECK]"
            self.flags.obstructions.images = self._check_features_for_attribute(objects=obstrns_no_foul,
                                                                                attribute='images')
        if self.version in ["2022"]:
            self.report += "New or Updated OBSTRN (excluding foul ground & areas) missing images [CHECK]"
            self.flags.obstructions.images = self._check_features_for_attribute(objects=obstrns_no_foul_area_ground,
                                                                                attribute='images')

        if self.version in ["2019", "2020", "2021"]:
            # Ensure new or updated obstructions (excluding foul ground) should have valsou
            self.report += "Warning: New or Updated OBSTRN (excluding foul ground & areas) missing mandatory " \
                           "attribute VALSOU [CHECK]"
            self.flags.obstructions.valsou = self._check_features_for_attribute(objects=obstrns_no_foul_area_ground,
                                                                                attribute='VALSOU',
                                                                                possible=True)

        elif self.version in ["2022"]:
            # Ensure new or updated obstructions (excluding foul ground) should have valsou or height
            self.report += "Warning: New or Updated OBSTRN (excluding foul ground & areas) having just one of " \
                           "mandatory attributes VALSOU or HEIGHT [CHECK]"
            self.flags.obstructions.valsou = self._check_features_for_just_one_of_attributes_in_list(
                objects=obstrns_no_foul_area_ground, xor_attributes=['VALSOU', 'HEIGHT'], possible=True)

        # Following checks are for obstructions that are foul.
        # Ensure foul area does not have valsou
        self.report += "Foul area OBSTRN shall not have VALSOU [CHECK]"
        self.flags.obstructions.foul_valsou = self._check_features_without_attribute(objects=obstrns_foul,
                                                                                     attribute='VALSOU', possible=False)

        # If new or updated obstructions have valsou, must have watlev, quasou, tecsou
        self.report += "New or Updated OBSTRN with VALSOU with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flags.obstructions.watlev = self._flag_features_with_attribute_value(obstrn_valsou, attribute='WATLEV',
                                                                                  values_to_flag=['', ],
                                                                                  check_attrib_existence=True)
        # Ensure new or updated obstructions have quasou except with tecsou of vbes, lidar or photogrammetry, those
        # shall be left blank
        self.report += "New or Updated OBSTRN with VALSOU with missing mandatory attribute QUASOU [CHECK]"
        self.flags.obstructions.quasou = self._flag_features_with_attribute_value(objects=obstrn_filtered_tecsou,
                                                                                  attribute='QUASOU',
                                                                                  values_to_flag=['', ],
                                                                                  check_attrib_existence=True)

        # Ensure new or updated obstructions have tecsou
        self.report += "New or Updated OBSTRN with VALSOU with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flags.obstructions.tecsou = self._flag_features_with_attribute_value(objects=obstrn_valsou,
                                                                                  attribute='TECSOU',
                                                                                  values_to_flag=['', ],
                                                                                  check_attrib_existence=True)

        # If obstructions does not have VALSOU...

        if self.version in ["2019", "2020", "2021"]:
            # Warning: Ensure obstructions with unknown valsou have watlev unknown
            self.report += "Warning: New or Updated OBSTRN with empty VALSOU shall have WATLEV of 'unknown' [CHECK]"
            self.flags.obstructions.unknown_watlev = self._flag_features_with_attribute_value(
                obstrn_undefined_valsou,
                attribute='WATLEV',
                values_to_flag=["1", "2", "3", "4", "5", "6", "7", ],
                check_attrib_existence=True,
                possible=True)

            # Ensure obstructions with unknown valsou have tecsou "unknown"
            self.report += "New or Updated OBSTRN with empty VALSOU shall have TECSOU of 'unknown' [CHECK]"
            self.flags.obstructions.unknown_tecsou = self._flag_features_with_attribute_value(
                obstrn_undefined_valsou,
                attribute='TECSOU',
                values_to_flag=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", ],
                check_attrib_existence=True)

            # Ensure obstructions with unknown valsou have quasou "unknown"
            self.report += "New or Updated OBSTRN with empty VALSOU shall have QUASOU of NULL [CHECK]"
            self.flags.obstructions.unknown_quasou = self._flag_features_with_attribute_value(
                obstrn_undefined_valsou,
                attribute='QUASOU',
                values_to_flag=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])

        if self.version in ["2022"]:
            # Warning: Ensure obstructions with unknown valsou have watlev unknown
            self.report += "Warning: New or Updated OBSTRN with empty VALSOU and empty HEIGHT shall have WATLEV of " \
                           "'unknown' [CHECK]"
            self.flags.obstructions.unknown_watlev = self._flag_features_with_attribute_value(
                obstrn_undefined_valsou_no_height,
                attribute='WATLEV',
                values_to_flag=["1", "2", "3",
                                "4", "5", "6",
                                "7", ],
                check_attrib_existence=True,
                possible=True)

            # if obstruction has height, WATLEV is always dry
            self.report += "Warning: New or Updated WRECKS with HEIGHT shall have WATLEV of 'Always Dry' [CHECK]"
            self.flags.obstructions.height_watlev = self._flag_features_with_attribute_value(
                obstrn_height,
                attribute='WATLEV',
                values_to_flag=["1", "3", "4", "5", "6", "7", ],
                check_attrib_existence=True,
                possible=True)

            # Ensure obstructions with unknown valsou have tecsou "unknown"
            self.report += "New or Updated OBSTRN with empty VALSOU and empty HEIGHT shall have TECSOU of 'unknown' " \
                           "[CHECK]"
            self.flags.obstructions.unknown_tecsou = self._flag_features_with_attribute_value(
                obstrn_undefined_valsou_no_height,
                attribute='TECSOU',
                values_to_flag=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", ],
                check_attrib_existence=True)

            # Ensure obstructions with unknown valsou have quasou "unknown"
            self.report += "New or Updated OBSTRN with empty VALSOU shall have QUASOU of NULL [CHECK]"
            self.flags.obstructions.unknown_quasou = self._flag_features_with_attribute_value(
                obstrn_undefined_valsou_no_height,
                attribute='QUASOU',
                values_to_flag=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])

        # New or updated foul ground obstructions shall have WATLEV
        self.report += "New or Updated foul ground OBSTRN with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flags.obstructions.foul_ground_watlev = self._flag_features_with_attribute_value(
            objects=obstrns_foul_ground,
            attribute='WATLEV',
            values_to_flag=['', ],
            check_attrib_existence=True)

        # Ensure new or updated foul ground obstructions do not have valsou
        self.report += "New or Updated foul ground OBSTRN must have VALSOU of NULL [CHECK]"
        self.flags.obstructions.foul_ground_valsou = self._check_features_without_attribute(objects=obstrns_foul_ground,
                                                                                            attribute='VALSOU',
                                                                                            possible=False)

        # Ensure new or updated foul ground obstructions do not have quasou
        self.report += "New or Updated foul ground OBSTRN must have QUASOU of NULL [CHECK]"
        self.flags.obstructions.foul_ground_quasou = self._check_features_without_attribute(objects=obstrns_foul_ground,
                                                                                            attribute='QUASOU',
                                                                                            possible=False)

        # Ensure new or updated foul ground obstructions do not have tecsou
        self.report += "New or Updated foul ground OBSTRN must have TECSOU of NULL [CHECK]"
        self.flags.obstructions.foul_ground_tecsou = self._check_features_without_attribute(objects=obstrns_foul_ground,
                                                                                            attribute='TECSOU',
                                                                                            possible=False)

        # Foul area checks....
        # Warning: Ensure foul area obstructions have watlev unknown
        self.report += "Warning: New or Updated foul area OBSTRN shall have WATLEV of 'unknown' [CHECK]"
        self.flags.obstructions.foul_unknown_watlev = \
            self._flag_features_with_attribute_value(obstrns_foul,
                                                     attribute='WATLEV',
                                                     values_to_flag=["1", "2", "3", "4", "5", "6", "7"],
                                                     check_attrib_existence=True,
                                                     possible=True)

        # Ensure foul area obstructions have tecsou "unknown"
        self.report += "New or Updated foul area OBSTRN shall have TECSOU of 'unknown' [CHECK]"
        self.flags.obstructions.foul_unknown_tecsou = \
            self._flag_features_with_attribute_value(obstrns_foul,
                                                     attribute='TECSOU',
                                                     values_to_flag=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                                                                     "11", "12", "13", "14"],
                                                     check_attrib_existence=True)

        # Ensure foul area obstructions have quasou "unknown"
        self.report += "New or Updated foul area OBSTRN  shall have QUASOU of 'depth unknown' [CHECK]"
        self.flags.obstructions.foul_unknown_quasou = \
            self._flag_features_with_attribute_value(obstrns_foul,
                                                     attribute='QUASOU',
                                                     values_to_flag=["1", "3", "4", "5", "6", "7", "8", "9", "10",
                                                                     "11"],
                                                     check_attrib_existence=True)

        # new warning in 2022: If feature has HEIGHT, then TECSOU and QUASOU should not be populated
        if self.version in ["2022"]:
            self.report += "Warning: Feature with HEIGHT should not have TECSOU [CHECK]"
            self.flags.obstructions.height_tecsou = self._check_features_without_attribute(objects=obstrn_height,
                                                                                           attribute='TECSOU',
                                                                                           possible=False)

            self.report += "Warning: Feature with HEIGHT should not have QUASOU [CHECK]"
            self.flags.obstructions.height_quasou = self._check_features_without_attribute(objects=obstrn_height,
                                                                                           attribute='QUASOU',
                                                                                           possible=False)

    # OFFSHORE PLATFORMS

    def platforms(self):

        self.report += "Checks for offshore platforms [SECTION]"

        # Isolate new or updated offshore platforms
        ofsplf = S57Aux.select_by_object(
            objects=self.new_updated_fts,
            object_filter=['OFSPLF', ])

        # Ensure new or updated offshore platforms have images
        self.report += "New or Updated OFSPLF missing images [CHECK]"
        self.flags.platforms.images = self._check_features_for_attribute(objects=ofsplf, attribute='images')

    # SEABED AREAS

    def sbdares(self):

        self.report += "Checks for seabed areas [SECTION]"

        # @ Isolate new or updated seabed areas
        sbdare = S57Aux.select_by_object(objects=self.new_updated_fts, object_filter=['SBDARE', ])

        # Isolate sbdare lines and areas
        sbdare_lines_areas = S57Aux.select_lines_and_areas(objects=sbdare)

        # Ensure new or updated seabed areas have natsur
        self.report += "New or Updated SBDARE lines and areas with empty/missing mandatory attribute NATSUR [CHECK]"
        self.flags.sbdares.natsur = self._flag_features_with_attribute_value(objects=sbdare_lines_areas,
                                                                             attribute='NATSUR', values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # Ensure line and area seabed areas have watlev
        self.report += "New or Updated SBDARE lines or areas missing mandatory attribute WATLEV [CHECK]"
        self.flags.sbdares.watlev = self._check_features_for_attribute(objects=sbdare_lines_areas, attribute='WATLEV',
                                                                       possible=True)

        # Isolate new or updated point seabed areas
        sbdare_points = S57Aux.select_only_points(objects=sbdare)

        # Ensure not more natqua than natsur
        self.report += "New or Updated point seabed areas with more NATQUA than NATSUR [CHECK]"
        self.flags.sbdares.pt_natqua = self._check_sbdare_attribute_counts(sbdare_points=sbdare_points,
                                                                           limiting_attribute='NATSUR',
                                                                           dependent='NATQUA')

        # Ensure not more colour than natsur
        self.report += "New or Updated point seabed areas with more COLOUR than NATSUR [CHECK]"
        self.flags.sbdares.pt_colour = self._check_sbdare_attribute_counts(sbdare_points=sbdare_points,
                                                                           limiting_attribute='NATSUR',
                                                                           dependent='COLOUR')

        # Ensure no unallowable combinations of natqua and natsur
        self.report += "No unallowable combinations of NATSUR and NATQUA [CHECK]"
        self.flags.sbdares.pt_allowable_combo = self._allowable_sbdare(sbdare_points=sbdare_points)

    def _check_sbdare_attribute_counts(self, sbdare_points: List['S57Record10'], limiting_attribute: str,
                                       dependent: str) -> List[list]:
        """Function to ensure that one attribute (dependent) does not have more values
        than one that relates to it (limiting attribute)"""
        flagged = list()

        for point in sbdare_points:

            attribute_1 = None
            attribute_2 = None

            for attr in point.attributes:
                if attr.acronym == limiting_attribute:
                    attribute_1 = attr.value
                elif attr.acronym == dependent:
                    attribute_2 = attr.value

            if not attribute_2:
                continue
            elif not attribute_1:
                continue
            elif len(attribute_1.split(',')) >= len(attribute_2.split(',')):
                continue
            # add to the flagged feature list
            if dependent == 'NATQUA':
                # add to the flagged report
                self.report += 'Found %s at (%.7f, %.7f) has NATSUR/NATQUA imbalance' \
                               % (point.acronym, point.centroid.x, point.centroid.y)
                self.flags.append(point.centroid.x, point.centroid.y, 'NATSUR/NATQUA imbalance',
                                  self.report.cur_section(with_prepended_summary=True))
            else:
                # add to the flagged report
                self.report += 'Found %s at (%.7f, %.7f) has NATSUR/COLOUR imbalance' \
                               % (point.acronym, point.centroid.x, point.centroid.y)
                self.flags.append(point.centroid.x, point.centroid.y, 'NATSUR/COLOUR imbalance',
                                  self.report.cur_section(with_prepended_summary=True))
            flagged.append([point.acronym, point.centroid.x, point.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _allowable_sbdare(self, sbdare_points: List['S57Record10']) -> List[list]:
        # report section
        # currently unsure whether the pairs with '' first ('UNDEFINED' in CARIS) are allowed by specs
        # the pairs with '0' first ('-' in CARIS) were added based on NOAA Appendix  G.5
        allowable = [['1', '4'], ['2', '4'], ['3', '4'], ['4', '14'], ['4', '17'], ['5', '1'],
                     ['5', '2'], ['5', '3'], ['6', '1'], ['6', '2'], ['6', '3'], ['6', '4'],
                     ['7', '1'], ['7', '2'], ['7', '3'], ['8', '1'], ['8', '4'], ['8', '5'],
                     ['8', '6'], ['8', '7'], ['8', '8'], ['8', '9'], ['8', '11'], ['8', '18'],
                     ['9', '1'], ['9', '4'], ['9', '5'], ['9', '6'], ['9', '7'], ['9', '8'],
                     ['9', '9'], ['9', '17'], ['9', '18'], ['10', '1'], ['10', '2'], ['10', '3'],
                     ['10', '4'],
                     ['', '1'], ['', '2'], ['', '3'], ['', '4'], ['', '5'],
                     ['', '6'], ['', '7'], ['', '8'], ['', '9'], ['', '11'], ['', '14'],
                     ['', '17'], ['', '18'],
                     ['0', '1'], ['0', '2'], ['0', '3'], ['0', '4'], ['0', '5'],
                     ['0', '6'], ['0', '7'], ['0', '8'], ['0', '9'], ['0', '11'], ['0', '14'],
                     ['0', '17'], ['0', '18']]

        flagged = list()
        for sbdare in sbdare_points:

            natqua = None
            natsur = None

            for attr in sbdare.attributes:
                if attr.acronym == 'NATQUA':
                    natqua = attr.value
                elif attr.acronym == 'NATSUR':
                    natsur = attr.value

            if (natqua is None) or (natsur is None):
                continue
            else:
                natqua = natqua.split(',')
                natsur = natsur.split(',')

                for i in range(min(len(natsur), len(natqua))):
                    check = [natqua[i], natsur[i]]
                    if check in allowable:
                        continue
                    # add to the flagged report
                    self.report += 'Found %s at (%.7f, %.7f) has prohibited NATSUR/NATQUA combination ' \
                                   % (sbdare.acronym, sbdare.centroid.x, sbdare.centroid.y)
                    # add to the flagged feature list
                    self.flags.append(sbdare.centroid.x, sbdare.centroid.y,
                                      "NATQUA and NATSUR combination is not allowed",
                                      self.report.cur_section(with_prepended_summary=True))
                    flagged.append([sbdare.acronym, sbdare.centroid.x, sbdare.centroid.y])
                    break

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # MOORINGS

    def moorings(self):

        self.report += "Checks for mooring facilities [SECTION]"

        # Isolate new or updated mooring facilities
        morfac = S57Aux.select_by_object(
            objects=self.new_updated_fts,
            object_filter=['MORFAC', ])

        # Ensure new or updated mooring facilities have catmor
        self.report += "New or Updated MORFAC with empty/missing mandatory attribute CATMOR [CHECK]"
        self.flags.moorings.catmor = self._flag_features_with_attribute_value(
            objects=morfac,
            attribute='CATMOR',
            values_to_flag=['', ],
            check_attrib_existence=True)

    # COASTLINES

    def coastlines(self):

        self.report += "Checks for coastlines and shorelines [SECTION]"

        # Isolate new or updated coastline
        coalne = S57Aux.select_by_object(objects=self.new_updated_fts, object_filter=['COALNE', ])

        # Ensure new or updated coastline has catcoa
        self.report += "New or Updated COALNE with empty/missing mandatory attribute CATCOA [CHECK]"
        self.flags.coastlines.coalne = self._flag_features_with_attribute_value(objects=coalne, attribute='CATCOA',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)

        # Isolate new or updated shoreline construction
        slcons = S57Aux.select_by_object(objects=self.new_updated_fts, object_filter=['SLCONS', ])

        # Ensure new or updated shoreline construction has catslc
        self.report += "New or Updated SLCONS with empty/missing mandatory attribute CATSLC [CHECK]"
        self.flags.coastlines.slcons = self._flag_features_with_attribute_value(objects=slcons, attribute='CATSLC',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)

    # LANDS

    def lands(self):

        self.report += "Checks for land elevations [SECTION]"

        # Isolate new or updated land elevation
        lndelv = S57Aux.select_by_object(objects=self.new_updated_fts, object_filter=['LNDELV', ])

        # @ Ensure new or updated land elevation has elevat
        self.report += "New or Updated LNDELV missing mandatory attribute ELEVAT [CHECK]"
        self.flags.lands.elevat = self._check_features_for_attribute(objects=lndelv, attribute='ELEVAT')

    # META COVERAGES

    def coverages(self):

        self.report += "Checks for metadata coverages [SECTION]"

        # Isolate M_COVR object
        mcovr = S57Aux.select_by_object(objects=self.all_fts, object_filter=['M_COVR', ])

        # Ensure M_COVR has catcov
        self.report += "M_COVR with empty/missing mandatory attribute CATCOV [CHECK]"
        self.flags.coverages.m_covr_catcov = self._flag_features_with_attribute_value(objects=mcovr, attribute='CATCOV',
                                                                                      values_to_flag=['', ],
                                                                                      check_attrib_existence=True)

        # Ensure M_COVR has inform
        self.report += "M_COVR missing mandatory attribute INFORM [CHECK]"
        self.flags.coverages.m_covr_inform = self._check_features_for_attribute(objects=mcovr, attribute='INFORM')

        # Ensure M_COVR has ninfom
        self.report += "M_COVR missing mandatory attribute NINFOM [CHECK]"
        self.flags.coverages.m_covr_ninfom = self._check_features_for_attribute(objects=mcovr, attribute='NINFOM')

    # OFFICE ONLY

    def office_only(self):
        if self.profile != 0:  # Not office
            logger.info('Skipping checks only for the office')
            return

        self.report += "Checks only for office [SECTION]"

        # For the office profile, ensure all features have onotes
        self.report += "Features missing onotes [CHECK]"
        self.flags.office.without_onotes = self._check_features_for_attribute(objects=self.all_fts, attribute='onotes')

        # For the office profile, check for empty hsdrec
        self.report += "Features with empty/unknown attribute hsdrec [CHECK]"
        self.flags.office.hsdrec_empty = self._flag_features_with_attribute_value(objects=self.all_fts,
                                                                                  attribute='hsdrec',
                                                                                  values_to_flag=['', ],
                                                                                  check_attrib_existence=True)

        # For the office profile, check for permitted features by feature type
        self.report += "Features without 'permitted feature' keyword [CHECK]"
        permitted = S57Aux.select_by_object(objects=self.all_fts, object_filter=['DRGARE', 'LOGPON', 'PIPARE',
                                                                                 'PIPOHD', 'PIPSOL', 'DMPGRD',
                                                                                 'CBLSUB', 'CBLARE', 'FAIRWY',
                                                                                 'CBLOHD', 'BRIDGE'])
        self.flags.office.permitted_kwds = self._check_for_missing_keywords(objects=permitted, attr_acronym='onotes',
                                                                            keywords=['permitted feature', ])

        # For the office profile, check for permitted fish haven
        obstrn = S57Aux.select_by_object(objects=self.all_fts, object_filter=['OBSTRN', ])
        fish_haven = S57Aux.select_by_attribute_value(objects=obstrn, attribute='CATOBS', value_filter=['5', ])

        self.report += "Fish havens without 'permitted feature' keyword [CHECK]"
        self.flags.office.fish_haven_kwds = self._check_for_missing_keywords(objects=fish_haven, attr_acronym='onotes',
                                                                             keywords=['permitted feature', ])

        # For the office profile, check for permitted mooring buoys
        morfac = S57Aux.select_by_object(objects=self.all_fts, object_filter=['MORFAC', ])
        mooring_buoy = S57Aux.select_by_attribute_value(objects=morfac, attribute='CATMOR', value_filter=['7', ])
        self.report += "Mooring buoy without 'permitted feature' keyword [CHECK]"
        self.flags.office.mooring_buoy_kwds = self._check_for_missing_keywords(objects=mooring_buoy,
                                                                               attr_acronym='onotes',
                                                                               keywords=['permitted feature', ])

        # For the office profile, ATONS must be removed.
        atons = S57Aux.select_by_object(objects=self.all_fts, object_filter=['LIGHTS', 'BOYLAT', 'BOYSAW', 'BOYSPP',
                                                                             'DAYMAR', 'FOGSIG', 'RTPBCN', 'BOYISD',
                                                                             'BOYINB', 'BOYCAR', 'BCNSPP', 'BCNLAT',
                                                                             'BCNSAW', 'BCNCAR', 'BCNISD'])
        self.report += "ATONs present in MCD deliverable [CHECK]"
        for aton in atons:
            # add to the flagged report
            self.report += 'Found ATON %s at (%.7f, %.7f)' % \
                           (aton.acronym, aton.centroid.x, aton.centroid.y)
            # add to the flagged feature list
            self.flags.append(aton.centroid.x, aton.centroid.y, "ATON %s" % (aton.acronym,),
                              self.report.cur_section(with_prepended_summary=True))
            self.flags.office.atons.append([aton.acronym, aton.centroid.x, aton.centroid.y])
        if len(atons) == 0:
            self.report += "OK"

        # For office profile, check for M_QUAL attribution for new and updated M_QUAL
        mqual = S57Aux.select_by_object(objects=self.new_updated_fts, object_filter=['M_QUAL', ])

        # Ensure M_QUAL has CATZOC
        self.report += "M_QUAL features with empty/missing mandatory attribute CATZOC [CHECK]"
        self.flags.office.m_qual_catzoc = self._flag_features_with_attribute_value(objects=mqual, attribute='CATZOC',
                                                                                   values_to_flag=['', ],
                                                                                   check_attrib_existence=True)

        # Ensure M_QUAL has SURSTA
        self.report += "M_QUAL features missing mandatory attribute SURSTA [CHECK]"
        self.flags.office.m_qual_sursta = self._check_features_for_attribute(objects=mqual, attribute='SURSTA')

        # Ensure M_QUAL has SUREND
        self.report += "M_QUAL features missing mandatory attribute SUREND [CHECK]"
        self.flags.office.m_qual_surend = self._check_features_for_attribute(objects=mqual, attribute='SUREND')

        # Ensure M_QUAL has TECSOU
        self.report += "M_QUAL features empty/missing mandatory attribute TECSOU [CHECK]"
        self.flags.office.m_qual_tecsou = self._flag_features_with_attribute_value(objects=mqual, attribute='TECSOU',
                                                                                   values_to_flag=['', ],
                                                                                   check_attrib_existence=True)

        # Ensure all features have descrp (per MCD)
        self.report += "Features have empty or missing mandatory attribute description [CHECK]"
        self.flags.office.mcd_description = self._check_features_for_attribute(objects=self.all_fts, attribute='descrp')

        # For the office profile, check for empty remarks (per MCD)
        self.report += "Features missing mandatory attribute remarks [CHECK]"
        self.flags.office.mcd_remarks = self._check_features_for_attribute(objects=self.all_fts, attribute='remrks')

        # Requirement only for the office, onotes may not exceed 250 characters
        self.report += "Features with onotes field exceeding %d characters [CHECK]" % self.onotes_character_limit
        self.flags.office.chars_limit = self._check_character_limit(objects=self.all_fts, attributes=['onotes', ],
                                                                    character_limit=self.onotes_character_limit)

    def _check_for_missing_keywords(self, objects: List['S57Record10'], attr_acronym: str, keywords: List[str]) \
            -> List[list]:
        """Check if the passed features do not have the passed keywords in a specific attribute"""
        flagged = list()

        kws = list()
        for keyword in keywords:
            kws.append(keyword.lower())

        for obj in objects:

            # do the test
            has_keywords = False
            for attr in obj.attributes:

                if attr.acronym == attr_acronym:
                    attr_value = attr.value.lower()

                    for kw in kws:
                        if kw in attr_value:
                            has_keywords = True
                            break

                    break

            # keywords found
            if has_keywords:
                continue

            else:
                # add to the flagged report
                self.report += 'Found %s at (%.7f, %.7f), missing %s' % \
                               (obj.acronym, obj.centroid.x, obj.centroid.y, keywords)
                # add to the flagged feature list
                self.flags.append(obj.centroid.x, obj.centroid.y, "missing %s in %s" % (keywords, attr_acronym),
                                  self.report.cur_section(with_prepended_summary=True))
                flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_character_limit(self, objects: List['S57Record10'], attributes: List[str], character_limit: int) \
            -> List[list]:
        """Check if the passed attribute of the passed features is not longer than the passed character limit"""
        flagged = list()

        for obj in objects:
            # do the test
            for attr in obj.attributes:
                if attr.acronym in attributes:
                    nr_chars = len(attr.value)
                    if len(attr.value) > character_limit:
                        # add to the flagged report
                        self.report += 'Found %s at (%.7f, %.7f) exceeds %d-characters limit [%d in %s]' \
                                       % (obj.acronym, obj.centroid.x, obj.centroid.y, character_limit,
                                          nr_chars, attr.acronym)
                        # add to the flagged feature list
                        self.flags.append(obj.centroid.x, obj.centroid.y, '%d-characters limit exceeds [%d in %s]'
                                          % (character_limit, nr_chars, attr.acronym),
                                          self.report.cur_section(with_prepended_summary=True))
                        flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def finalize_summary(self):
        """Add a summary to the report"""
        count = ord('B')

        # Create a summary list
        summary = list()
        summary.append('SUMMARY [SECTION]')
        summary.append('Summary by section: [CHECK]')

        # ### ALL FEATURES ###
        summary.append('Section %s - Checks for feature file consistency: %s' \
                       % (chr(count), self.flags.all_fts.nr_of_flagged()))
        count += 1

        # ### ASSIGNED FEATURES ###
        summary.append('Section %s - Checks for assigned features: %s' \
                       % (chr(count), self.flags.ass_fts.nr_of_flagged()))
        count += 1

        # ### NEW OR UPDATED FEATURES ###
        summary.append('Section %s - Checks for new or updated features: %s' \
                       % (chr(count), self.flags.new_updated_fts.nr_of_flagged()))
        count += 1

        # ### NEW OR DELETED FEATURES ###
        summary.append('Section %s - Checks for new or deleted features: %s' \
                       % (chr(count), self.flags.new_deleted_fts.nr_of_flagged()))
        count += 1

        # ### IMAGES ###
        summary.append('Section %s - Checks for images: %s' \
                       % (chr(count), self.flags.images.nr_of_flagged()))
        count += 1

        # SOUNDINGS
        summary.append('Section %s - Checks for soundings: %s' \
                       % (chr(count), self.flags.soundings.nr_of_flagged()))
        count += 1

        # DTONS
        summary.append('Section %s - Checks for DTONs: %s' \
                       % (chr(count), self.flags.dtons.nr_of_flagged()))
        count += 1

        # WRECKS
        summary.append('Section %s - Checks for wrecks: %s' \
                       % (chr(count), self.flags.wrecks.nr_of_flagged()))
        count += 1

        # ROCKS
        summary.append('Section %s - Checks for underwater rocks: %s' \
                       % (chr(count), self.flags.rocks.nr_of_flagged()))
        count += 1

        # OBSTRUCTIONS
        summary.append('Section %s - Checks for obstructions: %s' \
                       % (chr(count), self.flags.obstructions.nr_of_flagged()))
        count += 1

        # OFFSHORE PLATFORMS
        summary.append('Section %s - Checks for offshore platforms: %s' \
                       % (chr(count), self.flags.platforms.nr_of_flagged()))
        count += 1

        # SEABED AREAS
        summary.append('Section %s - Checks for seabed areas: %s' \
                       % (chr(count), self.flags.sbdares.nr_of_flagged()))
        count += 1

        # MOORINGS
        summary.append('Section %s - Checks for mooring facilities: %s' \
                       % (chr(count), self.flags.moorings.nr_of_flagged()))
        count += 1

        # COASTLINES
        summary.append('Section %s - Checks for coastlines and shorelines: %s' \
                       % (chr(count), self.flags.coastlines.nr_of_flagged()))
        count += 1

        # LANDS
        summary.append('Section %s - Checks for land elevations: %s' \
                       % (chr(count), self.flags.lands.nr_of_flagged()))
        count += 1

        # META COVERAGES
        summary.append('Section %s - Checks for meta coverages: %s' \
                       % (chr(count), self.flags.coverages.nr_of_flagged()))
        count += 1

        # OFFICE ONLY

        if self.profile == 0:  # office profile
            summary.append('Section %s - Checks ONLY for office: %s' \
                           % (chr(count), self.flags.office.nr_of_flagged()))
            count += 1

        # finally prepend it to the report
        self.report -= summary
