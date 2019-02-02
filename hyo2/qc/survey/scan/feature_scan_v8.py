import datetime
import logging

from hyo2.qc.survey.scan.base_scan import BaseScan, scan_algos, survey_areas
from hyo2.qc.common.s57_aux import S57Aux
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class FeatureScanV8(BaseScan):
    def __init__(self, s57, profile=0, version="2018",
                 survey_area=survey_areas["Pacific Coast"], use_mhw=False, mhw_value=0.0,
                 sorind=None, sordat=None):
        super().__init__(s57=s57)

        self.type = scan_algos["FEATURE_SCAN_v8"]
        self.version = version
        self.all_features = self.s57.rec10s
        self.profile = profile
        self.survey_area = survey_area
        self.use_mhw = use_mhw
        self.mhw_value = mhw_value
        self.sorind = sorind
        self.sordat = sordat

        # summary info
        self.redundancy = list()
        self.flagged_sorind = list()
        self.flagged_sorind_invalid = list()
        self.flagged_sordat = list()
        self.flagged_sordat_invalid = list()
        self.flagged_description = list()
        self.flagged_remarks = list()
        self.flagged_dtons = list()
        self.flagged_wrecks_images = list()
        self.flagged_remarks_features = list()
        self.flagged_recommend_features = list()
        self.flagged_awois_features_1 = list()
        self.flagged_awois_features_2 = list()
        self.flagged_soundings_tecsou = list()
        self.flagged_soundings_quasou = list()
        self.flagged_wrecks_catwrk = list()
        self.flagged_wrecks_watlev = list()
        self.flagged_wrecks_valsou = list()
        self.flagged_wrecks_tecsou = list()
        self.flagged_wrecks_quasou = list()
        self.flagged_uwtroc_valsou = list()
        self.flagged_uwtroc_watlev = list()
        self.flagged_uwtroc_quasou = list()
        self.flagged_uwtroc_tecsou = list()
        self.flagged_obstrn_images = list()
        self.flagged_obstrn_valsou = list()
        self.flagged_obstrn_foul_points_valsou = list()
        self.flagged_obstrn_watlev = list()
        self.flagged_obstrn_quasou = list()
        self.flagged_obstrn_tecsou = list()
        self.flagged_obstrn_foul_valsou = list()
        self.flagged_ofsplf = list()
        self.flagged_morfac = list()
        self.flagged_sbdare_natsur = list()
        self.flagged_sbdare_pt_natqua = list()
        self.flagged_sbdare_pt_colour = list()
        self.flagged_sbdare_pt_allowable_combo = list()
        self.flagged_sbdare_2 = list()
        self.flagged_sbdare_watlev = list()
        self.flagged_coalne = list()
        self.flagged_slcons = list()
        self.flagged_lndelv = list()
        self.flagged_new_valsous_watlev = list()
        self.flagged_new_elevat = list()
        self.flagged_m_covr_catcov = list()
        self.flagged_m_covr_inform = list()
        self.flagged_m_covr_ninfom = list()
        self.flagged_onotes = list()
        self.flagged_hsdrec_empty = list()
        self.flagged_prohibited = list()
        self.flagged_fish_haven = list()
        self.flagged_mooring_buoy = list()
        self.flagged_m_qual_catzoc = list()
        self.flagged_m_qual_sursta = list()
        self.flagged_m_qual_surend = list()
        self.flagged_m_qual_surend_sordat = list()
        self.flagged_m_qual_tecsou = list()

    @classmethod
    def check_sorind(cls, value, check_space=True):
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

    @classmethod
    def check_sordat(cls, value):

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

    # noinspection PyStatementEffect
    def check_feature_redundancy_and_geometry(self):
        """Function that identifies the presence of duplicated feature looking at their geometries"""
        logger.debug('Checking for feature redundancy...')

        tmp_features = list()  # to be returned without duplications
        features = list()
        for ft in self.all_features:
            # skip if the feature has not position
            if (len(ft.geo2s) == 0) and (len(ft.geo3s) == 0):
                # logger.debug("removing: %s" % ft)
                continue

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
            i = features.count([ft.acronym, geo2x, geo2y])
            if i > 0:  # we have a redundancy
                if ft.acronym in ["LIGHTS", ]:
                    # add to the flagged feature list
                    self._append_flagged(ft.centroid.x, ft.centroid.y, "possible redundant %s" % ft.acronym)
                    # add to the flagged report
                    self.report += 'possible redundant %s at (%s, %s)' % (ft.acronym, ft.centroid.x, ft.centroid.y)
                else:
                    # add to the flagged feature list
                    self._append_flagged(ft.centroid.x, ft.centroid.y, "redundant %s" % ft.acronym)
                    # add to the flagged report
                    self.report += 'redundant %s at (%s, %s)' % (ft.acronym, ft.centroid.x, ft.centroid.y)
                self.redundancy.append([ft.acronym, geo2x, geo2y])
            else:
                # populated the feature list
                features.append([ft.acronym, geo2x, geo2y])
                tmp_features.append(ft)

        if len(self.redundancy) == 0:
            self.report += "OK"

        return tmp_features

    # noinspection PyStatementEffect
    def check_features_for_attribute(self, objects, attribute, possible=False):
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

            # add to the flagged feature list
            if possible:
                self._append_flagged(obj.centroid.x, obj.centroid.y, "missing %s (?)" % attribute)
            else:
                self._append_flagged(obj.centroid.x, obj.centroid.y, "missing %s" % attribute)
            # add to the flagged report
            self.report += 'found missing %s at (%s, %s)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def flag_features_with_attribute_value(self, objects, attribute, values_to_flag, check_attrib_existence=False):
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
                    # add to the flagged feature list
                    self._append_flagged(obj.centroid.x, obj.centroid.y, "missing attribute: %s" % attribute)
                    # add to the flagged report
                    self.report += 'found missing attribute %s at (%s, %s)' \
                                   % (obj.acronym, obj.centroid.x, obj.centroid.y)
                    flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])
                    continue

            # check passed
            if not has_attribute_with_value:
                continue

            # add to the flagged feature list
            self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid/prohibited value for %s" % attribute)
            # add to the flagged report
            self.report += 'found invalid/prohibited attribute value for %s at (%s, %s)' \
                           % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def flag_features_by_type(self, objects, types_to_flag):
        """Flag the passed features if they have the passed values for the passed attribute"""
        flagged = list()

        for obj in objects:

            if obj.acronym not in types_to_flag:
                continue

            # add to the flagged feature list
            self._append_flagged(obj.centroid.x, obj.centroid.y, "prohibited type %s" % obj.acronym)
            # add to the flagged report
            self.report += 'found prohibited type %s at (%s, %s)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def check_features_without_attribute(self, objects, attribute, possible=False):
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

            # add to the flagged feature list
            if possible:
                self._append_flagged(obj.centroid.x, obj.centroid.y, "containing %s (?)" % attribute)
            else:
                self._append_flagged(obj.centroid.x, obj.centroid.y, "containing %s" % attribute)
            # add to the flagged report
            self.report += 'found %s at (%s, %s)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def _check_features_for_valid_sorind(self, objects, check_space=True):
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

            # add to the flagged feature list
            self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid SORIND")
            # add to the flagged report
            self.report += 'found %s at (%s, %s) with invalid SORIND' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def _check_features_for_match_sorind(self, objects):
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

            # add to the flagged feature list
            self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid SORIND")
            # add to the flagged report
            self.report += 'found %s at (%s, %s) with invalid SORIND' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def _check_features_for_valid_sordat(self, objects):
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

            # add to the flagged feature list
            self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid SORDAT")
            # add to the flagged report
            self.report += 'found %s at (%s, %s) with invalid SORDAT' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def _check_features_for_match_sordat(self, objects):
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

            # add to the flagged feature list
            self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid SORDAT")
            # add to the flagged report
            self.report += 'found %s at (%s, %s) with invalid SORDAT' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def _check_features_for_valid_watlev(self, objects):
        """Check if the passed features have valid WATLEV"""
        logger.debug("checking for invalid WATLEV and VALSOU ...")

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

            if self.version == "2019":
                if self.survey_area == survey_areas["Great Lakes"]:
                    if valsou < - 0.1:
                        is_valid = False
                        is_invalid_for_valsou = True
                    # else:
                    #     if valsou < -0.1:
                    #         if watlev != 4:  # Covers & Uncovers
                    #             is_valid = False
                    else:
                        if valsou < 0.1:
                            if watlev != 5:  # Awash
                                is_valid = False
                        else:
                            if watlev != 3:  # Always Underwater
                                is_valid = False

                elif self.survey_area in [1, 2]:

                    if valsou < (-self.mhw_value - 0.1):
                        is_valid = False
                        is_invalid_for_valsou = True
                    else:
                        if valsou < -0.1:
                            if watlev != 4:  # Covers & Uncovers
                                is_valid = False
                        elif valsou < 0.1:
                            if watlev != 5:  # Awash
                                is_valid = False
                        else:
                            if watlev != 3:  # Always Underwater
                                is_valid = False

                else:
                    raise RuntimeError("unknown area")

                # check passed
                if is_valid:
                    continue
            else:
                if self.survey_area == survey_areas["Great Lakes"]:
                    if valsou < - 1.2192:
                        is_valid = False
                        is_invalid_for_valsou = True
                    else:
                        if valsou < -0.6096:
                            if watlev != 4:  # Covers & Uncovers
                                is_valid = False
                        elif valsou < 0.6096:
                            if watlev != 5:  # Awash
                                is_valid = False
                        else:
                            if watlev != 3:  # Always Underwater
                                is_valid = False

                elif self.survey_area == survey_areas["Pacific Coast"]:

                    if valsou < (-self.mhw_value - 0.6096):
                        is_valid = False
                        is_invalid_for_valsou = True
                    else:
                        if valsou < -0.6096:
                            if watlev != 4:  # Covers & Uncovers
                                is_valid = False
                        elif valsou < 0.6096:
                            if watlev != 5:  # Awash
                                is_valid = False
                        else:
                            if watlev != 3:  # Always Underwater
                                is_valid = False

                elif self.survey_area == survey_areas["Atlantic Coast"]:
                    if valsou < (-self.mhw_value - 0.3048):
                        is_valid = False
                        is_invalid_for_valsou = True
                    else:
                        if valsou < -0.3048:
                            if watlev != 4:  # Covers & Uncovers
                                is_valid = False
                        elif valsou < 0.3048:
                            if watlev != 5:  # Awash
                                is_valid = False
                        else:
                            if watlev != 3:  # Always Underwater
                                is_valid = False

                else:
                    raise RuntimeError("unknown area")

                # check passed
                if is_valid:
                    continue

            # add to the flagged feature list and to the flagged report
            if is_invalid_for_valsou:
                self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid VALSOU (islet ?)")
                self.report += 'found %s at (%s, %s) with invalid VALSOU (islet ?)' % (
                    obj.acronym, obj.centroid.x, obj.centroid.y)
            else:
                self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid WATLEV")
                self.report += 'found %s at (%s, %s) with invalid WATLEV' % (
                    obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        logger.debug("checking for invalid WATLEV and VALSOU -> flagged: %d" % len(flagged))

        return flagged

    # noinspection PyStatementEffect
    def _check_features_for_valid_elevat(self, objects):
        """Check if the passed features have valid ELEVAT"""
        logger.debug("checking for invalid ELEVAT ...")

        flagged = list()

        for obj in objects:
            # do the test
            is_valid = True
            elevat = None
            for attr in obj.attributes:
                if attr.acronym == "ELEVAT":
                    elevat = float(attr.value)

                if elevat is not None:
                    break

            if self.version == "2019":
                if self.survey_area in [0, 1, 2]:
                    if elevat > + 0.1:
                        pass
                    else:
                        is_valid = False

                else:
                    raise RuntimeError("unknown area")
            else:
                if self.survey_area == survey_areas["Great Lakes"]:
                    if elevat > + 1.2192:
                        pass
                    else:
                        is_valid = False

                elif self.survey_area == survey_areas["Pacific Coast"]:
                    if elevat > + 0.6096:
                        pass
                    else:
                        is_valid = False

                elif self.survey_area == survey_areas["Atlantic Coast"]:
                    if elevat > + 0.3048:
                        pass
                    else:
                        is_valid = False

                else:
                    raise RuntimeError("unknown area")
            # check passed
            if is_valid:
                continue

            # add to the flagged feature list and to the flagged report
            self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid ELEVAT")
            self.report += 'found %s at (%s, %s) with invalid ELEVAT' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        logger.debug("checking for invalid ELEVAT -> flagged: %d" % len(flagged))

        return flagged

    # noinspection PyStatementEffect
    def allowable_sbdare(self, sbdare_points):
        # report section
        allowable = [['1', '4'], ['2', '4'], ['3', '4'], ['4', '14'], ['4', '17'], ['5', '1'],
                     ['5', '2'], ['5', '3'], ['6', '1'], ['6', '2'], ['6', '3'], ['6', '4'],
                     ['7', '1'], ['7', '2'], ['7', '3'], ['8', '1'], ['8', '4'], ['8', '5'],
                     ['8', '6'], ['8', '7'], ['8', '8'], ['8', '9'], ['8', '11'], ['8', '18'],
                     ['9', '1'], ['9', '4'], ['9', '5'], ['9', '6'], ['9', '7'], ['9', '8'],
                     ['9', '9'], ['9', '17'], ['9', '18'], ['10', '1'], ['10', '2'], ['10', '3'],
                     ['10', '4'], ['', '1'], ['', '2'], ['', '3'], ['', '4'], ['', '5'],
                     ['', '6'], ['', '7'], ['', '8'], ['', '9'], ['', '11'], ['', '14'],
                     ['', '17'], ['', '18']]

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
                    # add to the flagged feature list
                    self._append_flagged(sbdare.centroid.x, sbdare.centroid.y,
                                         "NATQUA and NATSUR combination is not allowed")
                    # add to the flagged report
                    self.report += 'found %s at (%s, %s) has prohibited NATSUR/NATQUA combination ' \
                                   % (sbdare.acronym, sbdare.centroid.x, sbdare.centroid.y)
                    flagged.append([sbdare.acronym, sbdare.centroid.x, sbdare.centroid.y])
                    break

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    # noinspection PyStatementEffect
    def check_attribute_counts(self, sbdare_points, limiting_attribute, dependent):
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
                self._append_flagged(point.centroid.x, point.centroid.y, 'NATSUR/NATQUA imbalance')
                # add to the flagged report
                self.report += 'found %s at (%s, %s) has NATSUR/NATQUA imbalance' \
                               % (point.acronym, point.centroid.x, point.centroid.y)
            else:
                self._append_flagged(point.centroid.x, point.centroid.y, 'NATSUR/COLOUR imbalance')
                # add to the flagged report
                self.report += 'found %s at (%s, %s) has NATSUR/COLOUR imbalance' \
                               % (point.acronym, point.centroid.x, point.centroid.y)
            flagged.append([point.acronym, point.centroid.x, point.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _append_flagged(self, x, y, note):
        """S57Aux function that append the note (if the feature position was already flagged) or add a new one"""
        # check if the point was already flagged
        for i in range(len(self.flagged_features[0])):
            if (self.flagged_features[0][i] == x) and (self.flagged_features[1][i] == y):
                self.flagged_features[2][i] = "%s, %s" % (self.flagged_features[2][i], note)
                return

        # if not flagged, just append the new flagged position
        self.flagged_features[0].append(x)
        self.flagged_features[1].append(y)
        self.flagged_features[2].append(note)

    def run(self):
        """Execute the set of check of the feature scan algorithm"""
        msg = "Feature Scan settings:\n"
        msg += "- HSSD version: %s\n" % self.version
        msg += "- nr. on features in the S57 file: %d\n" % len(self.all_features)
        msg += "- profile: %s" % ("field" if (self.profile == 1) else "office")
        if self.version in ["2018", "2019"]:
            msg += "\n- survey area: %s\n" % Helper.first_match(survey_areas, self.survey_area)
            msg += "- use MHW: %s [%s]\n" % (self.use_mhw, self.mhw_value)
            msg += "- check SORIND: %s\n" % (self.sorind,)
            msg += "- check SORDAT: %s\n" % (self.sordat,)
        logger.info(msg)

        if self.version == "2015":
            self.run_2015()

        elif self.version == "2016":
            self.run_2016()

        elif self.version == "2017":
            self.run_2017()

        elif self.version == "2018":
            self.run_2018()

        elif self.version == "2019":
            self.run_2019()

        else:
            raise RuntimeError("unsupported specs version: %s" % self.version)

    # noinspection PyStatementEffect
    def run_2015(self):
        """HSSD 2015 checks"""

        self.report += "Redundant features [CHECK]"
        self.all_features = self.check_feature_redundancy_and_geometry()

        carto_filter = ['$AREAS', '$LINES', '$CSYMB', '$COMPS', '$TEXTS']
        no_carto_features = S57Aux.filter_by_object(objects=self.all_features, object_filter=carto_filter)
        new_update_features = S57Aux.select_by_attribute_value(objects=no_carto_features, attribute='descrp',
                                                               value_filter=['1', '2', ])

        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORIND [CHECK]"
        self.flagged_sorind = self.check_features_for_attribute(new_update_features, 'SORIND')

        self.report += "New or Updated features (excluding carto notes) with invalid SORIND [CHECK]"
        self.flagged_sorind_invalid = self._check_features_for_valid_sorind(new_update_features, check_space=False)

        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORDAT [CHECK]"
        self.flagged_sordat = self.check_features_for_attribute(new_update_features, 'SORDAT')

        self.report += "New or Updated features (excluding carto notes) with invalid SORDAT [CHECK]"
        self.flagged_sordat_invalid = self._check_features_for_valid_sordat(new_update_features)

        assigned_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='asgnmt',
                                                             value_filter=['2', ])

        self.report += "Assigned features missing mandatory attribute description [CHECK]"
        self.flagged_description = self.check_features_for_attribute(objects=assigned_features, attribute='descrp')

        self.report += "Assigned features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks = self.check_features_for_attribute(objects=assigned_features, attribute='remrks')

        extended_attribute_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='descrp',
                                                                       value_filter=['1', ])

        self.report += "New features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks_features = self.check_features_for_attribute(
            objects=extended_attribute_features,
            attribute='remrks')

        recommend_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='descrp',
                                                              value_filter=['1', '3'])
        # noinspection PyStatementEffect
        self.report += "New or deleted features missing mandatory attribute recommendation [CHECK]"
        self.flagged_recommend_features = self.check_features_for_attribute(objects=recommend_features,
                                                                            attribute='recomd')

        awois_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='sftype',
                                                          value_filter=['2', ])
        self.report += "AWOIS features missing mandatory attribute dbkyid (2015 only) [CHECK]"
        self.flagged_awois_features_1 = self.check_features_for_attribute(objects=awois_features,
                                                                          attribute='dbkyid')
        self.report += "AWOIS features missing mandatory attribute images (2015 only) [CHECK]"
        self.flagged_awois_features_2 = self.check_features_for_attribute(objects=awois_features,
                                                                          attribute='images')

        sounding_features = S57Aux.select_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        self.report += "SOUNDG missing mandatory attribute TECSOU [CHECK]"
        self.flagged_soundings_tecsou = self.check_features_for_attribute(sounding_features, 'TECSOU')
        self.report += "SOUNDG missing mandatory attribute QUASOU [CHECK]"
        self.flagged_soundings_quasou = self.check_features_for_attribute(sounding_features, 'QUASOU')

        new_features = S57Aux.select_by_attribute_value(objects=no_carto_features, attribute='descrp',
                                                        value_filter=['1', '2'])
        dtons = S57Aux.select_by_attribute_value(objects=new_features, attribute='sftype', value_filter=['3', ])
        # @added 6/15/2015 to prevent SOUNDG DtoN objects from getting the image flag
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['SOUNDG', ])
        # removing wrecks dtons to prevent double-flagging
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['WRECKS', ])
        # removing obstrn dtons to prevent double-flagging
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['OBSTRN', ])
        wrecks = S57Aux.select_by_object(objects=new_features, object_filter=['WRECKS', ])
        # noinspection PyStatementEffect
        self.report += "Special feature types (DTONS) missing images [CHECK]"
        self.flagged_dtons = self.check_features_for_attribute(dtons, 'images')

        self.report += "New or Updated WRECKS) missing images [CHECK]"
        self.flagged_wrecks_images = self.check_features_for_attribute(wrecks, 'images')
        self.report += "New or Updated WRECKS missing mandatory attribute CATWRK [CHECK]"
        self.flagged_wrecks_catwrk = self.check_features_for_attribute(wrecks, 'CATWRK')
        self.report += "New or Updated WRECKS missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_watlev = self.check_features_for_attribute(wrecks, 'WATLEV')
        self.report += "New or Updated WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_valsou = self.check_features_for_attribute(wrecks, 'VALSOU')
        self.report += "New or Updated WRECKS missing mandatory attribute TECSOU [CHECK]"
        self.flagged_wrecks_tecsou = self.check_features_for_attribute(wrecks, 'TECSOU')
        self.report += "New or Updated WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_quasou = self.check_features_for_attribute(wrecks, 'QUASOU')

        rocks = S57Aux.select_by_object(objects=new_features, object_filter=['UWTROC', ])
        self.report += "New or Updated UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_valsou = self.check_features_for_attribute(rocks, 'VALSOU')
        self.report += "New or Updated UWTROC missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_watlev = self.check_features_for_attribute(rocks, 'WATLEV')
        self.report += "New or Updated UWTROC missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_quasou = self.check_features_for_attribute(rocks, 'QUASOU')
        self.report += "New or Updated UWTROC missing mandatory attribute TECSOU [CHECK]"
        self.flagged_uwtroc_tecsou = self.check_features_for_attribute(rocks, 'TECSOU')

        obstrns = S57Aux.select_by_object(objects=new_features, object_filter=['OBSTRN', ])
        self.report += "New or Updated OBSTRN missing mandatory attribute images [CHECK]"
        self.flagged_obstrn_images = self.check_features_for_attribute(obstrns, 'images')
        self.report += "New or Updated OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_valsou = self.check_features_for_attribute(obstrns, 'VALSOU')
        self.report += "New or Updated OBSTRN missing mandatory attribute WATLEV [CHECK]"
        self.flagged_obstrn_watlev = self.check_features_for_attribute(obstrns, 'WATLEV')
        self.report += "New or Updated OBSTRN missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_quasou = self.check_features_for_attribute(obstrns, 'QUASOU')
        self.report += "New or Updated OBSTRN missing mandatory attribute TECSOU [CHECK]"
        self.flagged_obstrn_tecsou = self.check_features_for_attribute(obstrns, 'TECSOU')

        self.report += "New or Updated OFSPLF missing mandatory attribute images (2016 only) [SKIP_CHK]"
        self.flagged_ofsplf = -1

        morfac = S57Aux.select_by_object(objects=self.all_features, object_filter=['MORFAC', ])
        self.report += "MORFAC missing mandatory attribute CATMOR [CHECK]"
        self.flagged_morfac = self.check_features_for_attribute(morfac, 'CATMOR')

        sbdare = S57Aux.select_by_object(objects=self.all_features, object_filter=['SBDARE', ])
        sbdare_points = S57Aux.select_only_points(sbdare)
        self.report += "SBDARE missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_natsur = self.check_features_for_attribute(sbdare, 'NATSUR')
        self.report += "SBDARE missing mandatory attribute COLOUR (2015 only) [CHECK]"
        self.flagged_sbdare_2 = self.check_features_for_attribute(sbdare_points, 'COLOUR')

        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)
        self.report += "SBDARE lines or areas possibly missing mandatory attribute WATLEV [CHECK]"
        self.flagged_sbdare_watlev = self.check_features_for_attribute(sbdare_lines_areas, 'WATLEV', possible=True)

        coalne = S57Aux.select_by_object(objects=self.all_features, object_filter=['COALNE', ])
        self.report += "COALNE missing mandatory attribute CATCOA [CHECK]"
        self.flagged_coalne = self.check_features_for_attribute(coalne, 'CATCOA')

        slcons = S57Aux.select_by_object(objects=self.all_features, object_filter=['SLCONS', ])
        self.report += "SLCONS missing mandatory attribute CATSLC [CHECK]"
        self.flagged_slcons = self.check_features_for_attribute(slcons, 'CATSLC')

        lndelv = S57Aux.select_by_object(objects=self.all_features, object_filter=['LNDELV', ])
        self.report += "LNDELV missing mandatory attribute ELEVAT [CHECK]"
        self.flagged_lndelv = self.check_features_for_attribute(lndelv, 'ELEVAT')

        mcovr = S57Aux.select_by_object(objects=self.all_features, object_filter=['M_COVR', ])
        self.report += "M_COVR missing mandatory attribute CATCOV [CHECK]"
        self.flagged_m_covr_catcov = self.check_features_for_attribute(mcovr, 'CATCOV')
        self.report += "M_COVR missing mandatory attribute INFORM [CHECK]"
        self.flagged_m_covr_inform = self.check_features_for_attribute(mcovr, 'INFORM')
        self.report += "M_COVR missing mandatory attribute NINFOM [CHECK]"
        self.flagged_m_covr_ninfom = self.check_features_for_attribute(mcovr, 'NINFOM')

        no_soundings = S57Aux.filter_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        if self.profile == 0:  # office
            self.report += "Non-sounding features missing onotes (just FYI) [CHECK]"
            self.flagged_onotes = self.check_features_for_attribute(no_soundings, 'onotes')

        # finalize the summary
        self.finalize_summary()

    # noinspection PyStatementEffect
    def run_2016(self):
        """HSSD 2016 checks"""

        self.report += "Redundant features [CHECK]"
        self.all_features = self.check_feature_redundancy_and_geometry()

        carto_filter = ['$AREAS', '$LINES', '$CSYMB', '$COMPS', '$TEXTS']
        no_carto_features = S57Aux.filter_by_object(objects=self.all_features, object_filter=carto_filter)
        new_update_features = S57Aux.select_by_attribute_value(objects=no_carto_features, attribute='descrp',
                                                               value_filter=['1', '2', ])

        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORIND [CHECK]"
        self.flagged_sorind = self.check_features_for_attribute(new_update_features, 'SORIND')

        self.report += "New or Updated features (excluding carto notes) with invalid SORIND [CHECK]"
        self.flagged_sorind_invalid = self._check_features_for_valid_sorind(new_update_features, check_space=False)

        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORDAT [CHECK]"
        self.flagged_sordat = self.check_features_for_attribute(new_update_features, 'SORDAT')

        self.report += "New or Updated features (excluding carto notes) with invalid SORDAT [CHECK]"
        self.flagged_sordat_invalid = self._check_features_for_valid_sordat(new_update_features)

        assigned_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='asgnmt',
                                                             value_filter=['2', ])
        self.report += "Assigned features missing mandatory attribute description [CHECK]"
        self.flagged_description = self.check_features_for_attribute(objects=assigned_features, attribute='descrp')
        self.report += "Assigned features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks = self.check_features_for_attribute(objects=assigned_features, attribute='remrks')

        extended_attrib_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='descrp',
                                                                    value_filter=['1', '3'])
        self.report += "New or deleted features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks_features = self.check_features_for_attribute(objects=extended_attrib_features,
                                                                          attribute='remrks')

        recommend_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='descrp',
                                                              value_filter=['1', '3'])
        self.report += "New or deleted features missing mandatory attribute recommendation [CHECK]"
        self.flagged_recommend_features = self.check_features_for_attribute(objects=recommend_features,
                                                                            attribute='recomd')

        self.report += "AWOIS features missing mandatory attribute dbkyid (2015 only) [SKIP_CHK]"
        self.flagged_awois_features_1 = -1

        self.report += "AWOIS features missing mandatory attribute images (2015 only) [SKIP_CHK]"
        self.flagged_awois_features_2 = -1

        sounding_features = S57Aux.select_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        self.report += "SOUNDG missing mandatory attribute TECSOU [CHECK]"
        self.flagged_soundings_tecsou = self.check_features_for_attribute(sounding_features, 'TECSOU')
        self.report += "SOUNDG missing mandatory attribute QUASOU [CHECK]"
        self.flagged_soundings_quasou = self.check_features_for_attribute(sounding_features, 'QUASOU')

        new_features = S57Aux.select_by_attribute_value(objects=no_carto_features, attribute='descrp',
                                                        value_filter=['1', '2'])
        dtons = S57Aux.select_by_attribute_value(objects=new_features, attribute='sftype', value_filter=['3', ])
        # @added 6/15/2015 to prevent SOUNDG DtoN objects from getting the image flag
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['SOUNDG', ])
        # removing wrecks dtons to prevent double-flagging
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['WRECKS', ])
        # removing obstrn dtons to prevent double-flagging
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['OBSTRN', ])
        wrecks = S57Aux.select_by_object(objects=new_features, object_filter=['WRECKS', ])
        self.report += "Special feature types (DTONS) missing images [CHECK]"
        self.flagged_dtons = self.check_features_for_attribute(dtons, 'images')

        self.report += "New or Updated WRECKS missing images [CHECK]"
        self.flagged_wrecks_images = self.check_features_for_attribute(wrecks, 'images')
        self.report += "New or Updated WRECKS missing mandatory attribute CATWRK [CHECK]"
        self.flagged_wrecks_catwrk = self.check_features_for_attribute(wrecks, 'CATWRK')
        self.report += "New or Updated WRECKS missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_watlev = self.check_features_for_attribute(wrecks, 'WATLEV')
        self.report += "New or Updated WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_valsou = self.check_features_for_attribute(wrecks, 'VALSOU')
        self.report += "New or Updated WRECKS missing mandatory attribute TECSOU [CHECK]"
        self.flagged_wrecks_tecsou = self.check_features_for_attribute(wrecks, 'TECSOU')
        self.report += "New or Updated WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_quasou = self.check_features_for_attribute(wrecks, 'QUASOU')

        rocks = S57Aux.select_by_object(objects=new_features, object_filter=['UWTROC', ])
        self.report += "New or Updated UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_valsou = self.check_features_for_attribute(rocks, 'VALSOU')
        self.report += "New or Updated UWTROC missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_watlev = self.check_features_for_attribute(rocks, 'WATLEV')
        self.report += "New or Updated UWTROC missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_quasou = self.check_features_for_attribute(rocks, 'QUASOU')
        self.report += "New or Updated UWTROC missing mandatory attribute TECSOU [CHECK]"
        self.flagged_uwtroc_tecsou = self.check_features_for_attribute(rocks, 'TECSOU')

        obstrns = S57Aux.select_by_object(objects=new_features, object_filter=['OBSTRN', ])
        self.report += "New or Updated OBSTRN missing mandatory attribute images [CHECK]"
        self.flagged_obstrn_images = self.check_features_for_attribute(obstrns, 'images')
        self.report += "New or Updated OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_valsou = self.check_features_for_attribute(obstrns, 'VALSOU')
        self.report += "New or Updated OBSTRN missing mandatory attribute WATLEV [CHECK]"
        self.flagged_obstrn_watlev = self.check_features_for_attribute(obstrns, 'WATLEV')
        self.report += "New or Updated OBSTRN missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_quasou = self.check_features_for_attribute(obstrns, 'QUASOU')
        self.report += "New or Updated OBSTRN missing mandatory attribute TECSOU [CHECK]"
        self.flagged_obstrn_tecsou = self.check_features_for_attribute(obstrns, 'TECSOU')

        ofsplf = S57Aux.select_by_object(objects=new_features, object_filter=['OFSPLF', ])
        self.report += "New or Updated OFSPLF missing images (2016 only) [CHECK]"
        self.flagged_ofsplf = self.check_features_for_attribute(ofsplf, 'images')

        morfac = S57Aux.select_by_object(objects=self.all_features, object_filter=['MORFAC', ])
        self.report += "MORFAC missing mandatory attribute CATMOR [CHECK]"
        self.flagged_morfac = self.check_features_for_attribute(morfac, 'CATMOR')

        sbdare = S57Aux.select_by_object(objects=self.all_features, object_filter=['SBDARE', ])
        self.report += "SBDARE missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_natsur = self.check_features_for_attribute(sbdare, 'NATSUR')

        self.report += "SBDARE missing mandatory attribute COLOUR (2015 only) [SKIP_CHK]"
        self.flagged_sbdare_2 = -1

        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)
        self.report += "SBDARE lines or areas possibly missing mandatory attribute WATLEV [CHECK]"
        self.flagged_sbdare_watlev = self.check_features_for_attribute(sbdare_lines_areas, 'WATLEV', possible=True)

        coalne = S57Aux.select_by_object(objects=self.all_features, object_filter=['COALNE', ])
        self.report += "COALNE missing mandatory attribute CATCOA [CHECK]"
        self.flagged_coalne = self.check_features_for_attribute(coalne, 'CATCOA')

        slcons = S57Aux.select_by_object(objects=self.all_features, object_filter=['SLCONS', ])
        self.report += "SLCONS missing mandatory attribute CATSLC [CHECK]"
        self.flagged_slcons = self.check_features_for_attribute(slcons, 'CATSLC')

        lndelv = S57Aux.select_by_object(objects=self.all_features, object_filter=['LNDELV', ])
        self.report += "LNDELV missing mandatory attribute ELEVAT [CHECK]"
        self.flagged_lndelv = self.check_features_for_attribute(lndelv, 'ELEVAT')

        mcovr = S57Aux.select_by_object(objects=self.all_features, object_filter=['M_COVR', ])
        self.report += "M_COVR missing mandatory attribute CATCOV [CHECK]"
        self.flagged_m_covr_catcov = self.check_features_for_attribute(mcovr, 'CATCOV')
        self.report += "M_COVR missing mandatory attribute INFORM [CHECK]"
        self.flagged_m_covr_inform = self.check_features_for_attribute(mcovr, 'INFORM')
        self.report += "M_COVR missing mandatory attribute NINFOM [CHECK]"
        self.flagged_m_covr_ninfom = self.check_features_for_attribute(mcovr, 'NINFOM')

        no_soundings = S57Aux.filter_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        if self.profile == 0:  # office
            self.report += "Non-sounding features missing onotes (just FYI) [CHECK]"
            self.flagged_onotes = self.check_features_for_attribute(no_soundings, 'onotes')

        # finalize the summary
        self.finalize_summary()

    # noinspection PyStatementEffect
    def run_2017(self):
        """HSSD 2017 checks"""

        # @ Ensure no feature redundancy
        self.report += "Redundant features [CHECK]"
        self.all_features = self.check_feature_redundancy_and_geometry()

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
        self.flagged_sorind_invalid = self._check_features_for_valid_sorind(new_update_features, check_space=False)
        # @ Ensure new or updated features have SORDAT
        self.report += "New or Updated features (excluding carto notes) missing mandatory attribute SORDAT [CHECK]"
        self.flagged_sordat = self.check_features_for_attribute(new_update_features, 'SORDAT')
        # @ Ensure new or updated features have valid SORDAT
        self.report += "New or Updated features (excluding carto notes) with invalid SORDAT [CHECK]"
        self.flagged_sordat_invalid = self._check_features_for_valid_sordat(new_update_features)

        # @ Isolate only features that are assigned
        assigned_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='asgnmt',
                                                             value_filter=['2', ])
        # @ Ensure assigned features have descrp
        self.report += "Assigned features missing mandatory attribute description [CHECK]"
        self.flagged_description = self.check_features_for_attribute(objects=assigned_features, attribute='descrp')
        # @ Ensure assigned features have remrks
        self.report += "Assigned features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks = self.check_features_for_attribute(objects=assigned_features, attribute='remrks')

        # @ Isolate features with descrp = New or Delete
        extended_attribute_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='descrp',
                                                                       value_filter=['1', '3'])
        # @ Ensure new or deleted features have remrks
        self.report += "New/Delete features missing mandatory attribute remarks [CHECK]"
        self.flagged_remarks_features = self.check_features_for_attribute(
            objects=extended_attribute_features,
            attribute='remrks')

        # @ Isolate features with descrp = New or Delete
        recommend_features = S57Aux.select_by_attribute_value(objects=self.all_features, attribute='descrp',
                                                              value_filter=['1', '3'])
        # @ Ensure new or deleted features have recomd
        self.report += "New/Delete features missing mandatory attribute recommendation [CHECK]"
        self.flagged_recommend_features = self.check_features_for_attribute(objects=recommend_features,
                                                                            attribute='recomd')

        # @ Isolate sounding features
        sounding_features = S57Aux.select_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        # @ Ensure soundings have tecsou
        self.report += "SOUNDG missing mandatory attribute TECSOU [CHECK]"
        self.flagged_soundings_tecsou = self.check_features_for_attribute(sounding_features, 'TECSOU')
        # @ Ensure soundings have quasou
        self.report += "SOUNDG missing mandatory attribute QUASOU [CHECK]"
        self.flagged_soundings_quasou = self.check_features_for_attribute(sounding_features, 'QUASOU')

        # @ Isolate features that are no-carto and have descrp = New or Updated
        new_features = S57Aux.select_by_attribute_value(objects=no_carto_features, attribute='descrp',
                                                        value_filter=['1', '2'])
        # @ Isolate features that are no-carto, descrp = New or Updated, and sftype = DTON
        dtons = S57Aux.select_by_attribute_value(objects=new_features, attribute='sftype', value_filter=['3', ])
        # @ Remove soundings to prevent SOUNDG DtoN objects from getting the image flag
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['SOUNDG', ])
        # @ Removing wrecks dtons to prevent double-flagging
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['WRECKS', ])
        # @ Removing obstrn dtons to prevent double-flagging
        dtons = S57Aux.filter_by_object(objects=dtons, object_filter=['OBSTRN', ])
        # @ Ensure DTONs have images
        self.report += "Special feature types (DTONS) missing images [CHECK]"
        self.flagged_dtons = self.check_features_for_attribute(dtons, 'images')

        # @ Isolate new or updated wrecks
        wrecks = S57Aux.select_by_object(objects=new_features, object_filter=['WRECKS', ])
        # @ Ensure new or updated wrecks have images
        self.report += "New or Updated WRECKS missing images [CHECK]"
        self.flagged_wrecks_images = self.check_features_for_attribute(wrecks, 'images')
        # @ Ensure new or updated wrecks have catwrk
        self.report += "New or Updated WRECKS missing mandatory attribute CATWRK [CHECK]"
        self.flagged_wrecks_catwrk = self.check_features_for_attribute(wrecks, 'CATWRK')
        # @ Ensure new or updated wrecks have watlev
        self.report += "New or Updated WRECKS missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_watlev = self.check_features_for_attribute(wrecks, 'WATLEV')
        # @ Ensure new or updated wrecks have valsou
        self.report += "New or Updated WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_valsou = self.check_features_for_attribute(wrecks, 'VALSOU')
        # @ Ensure new or updated wrecks have tecsou
        self.report += "New or Updated WRECKS missing mandatory attribute TECSOU [CHECK]"
        self.flagged_wrecks_tecsou = self.check_features_for_attribute(wrecks, 'TECSOU')
        # @ Ensure new or updated wrecks have quasou
        self.report += "New or Updated WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_quasou = self.check_features_for_attribute(wrecks, 'QUASOU')

        # @ Isolate new or updated rocks
        rocks = S57Aux.select_by_object(objects=new_features, object_filter=['UWTROC', ])
        # @ Ensure new or updated rocks have valsou
        self.report += "New or Updated UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_valsou = self.check_features_for_attribute(rocks, 'VALSOU')
        # @ Ensure new or updated rocks have watlev
        self.report += "New or Updated UWTROC missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_watlev = self.check_features_for_attribute(rocks, 'WATLEV')
        # @ Ensure new or updated rocks have quasou
        self.report += "New or Updated UWTROC missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_quasou = self.check_features_for_attribute(rocks, 'QUASOU')
        # @ Ensure new or updated rocks have tecsou
        self.report += "New or Updated UWTROC missing mandatory attribute TECSOU [CHECK]"
        self.flagged_uwtroc_tecsou = self.check_features_for_attribute(rocks, 'TECSOU')

        # @ Isolate new or updated obstructions
        obstrns = S57Aux.select_by_object(objects=new_features, object_filter=['OBSTRN', ])
        # @ Exclude foul area obstructions from images check
        obstrns_no_foul = S57Aux.filter_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])
        # @ Ensure new or updated obstructions (excluding foul area obstructions) have images
        self.report += "New or Updated OBSTRN missing mandatory attribute images [CHECK]"
        self.flagged_obstrn_images = self.check_features_for_attribute(obstrns_no_foul, 'images')
        # @ Ensure new or updated obstructions have valsou
        self.report += "New or Updated OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_valsou = self.check_features_for_attribute(obstrns, 'VALSOU')
        # @ Ensure new or updated obstructions have watlev
        self.report += "New or Updated OBSTRN missing mandatory attribute WATLEV [CHECK]"
        self.flagged_obstrn_watlev = self.check_features_for_attribute(obstrns, 'WATLEV')
        # @ Ensure new or updated obstructions have quasou
        self.report += "New or Updated OBSTRN missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_quasou = self.check_features_for_attribute(obstrns, 'QUASOU')
        # @ Ensure new or updated obstructions have tecsou
        self.report += "New or Updated OBSTRN missing mandatory attribute TECSOU [CHECK]"
        self.flagged_obstrn_tecsou = self.check_features_for_attribute(obstrns, 'TECSOU')

        # @ Isolate new or updated offshore platforms
        ofsplf = S57Aux.select_by_object(objects=new_features, object_filter=['OFSPLF', ])
        # @ Ensure new or updated offshore platforms have images
        self.report += "New or Updated OFSPLF missing images [CHECK]"
        self.flagged_ofsplf = self.check_features_for_attribute(ofsplf, 'images')

        # @ Isolate new or updated seabed areas
        sbdare = S57Aux.select_by_object(objects=new_features, object_filter=['SBDARE', ])
        # @ Ensure new or updated seabed areas have natsur
        self.report += "New or Updated SBDARE missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_natsur = self.check_features_for_attribute(sbdare, 'NATSUR')

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

        # @ Isolate line and area seabed areas
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)
        # @ Ensure line and area seabed areas have watlev
        self.report += "New or Updated SBDARE lines or areas missing mandatory attribute WATLEV [CHECK]"
        self.flagged_sbdare_watlev = self.check_features_for_attribute(sbdare_lines_areas, 'WATLEV', possible=True)

        # @ Isolate new or updated mooring facilities
        morfac = S57Aux.select_by_object(objects=new_features, object_filter=['MORFAC', ])
        # @ Ensure new or updated mooring facilities have catmor
        self.report += "New or Updated MORFAC missing mandatory attribute CATMOR [CHECK]"
        self.flagged_morfac = self.check_features_for_attribute(morfac, 'CATMOR')

        # @ Isolate new or updated coastline
        coalne = S57Aux.select_by_object(objects=new_features, object_filter=['COALNE', ])
        # @ Ensure new or updated coastline has catcoa
        self.report += "New or Updated COALNE missing mandatory attribute CATCOA [CHECK]"
        self.flagged_coalne = self.check_features_for_attribute(coalne, 'CATCOA')

        # @ Isolate new or updated shoreline construction
        slcons = S57Aux.select_by_object(objects=new_features, object_filter=['SLCONS', ])
        # @ Ensure new or updated shoreline construction has catslc
        self.report += "New or Updated SLCONS missing mandatory attribute CATSLC [CHECK]"
        self.flagged_slcons = self.check_features_for_attribute(slcons, 'CATSLC')

        # @ Isolate new or updated land elevation
        lndelv = S57Aux.select_by_object(objects=new_features, object_filter=['LNDELV', ])
        # @ Ensure new or updated land elevation has elevat
        self.report += "New or Updated LNDELV missing mandatory attribute ELEVAT [CHECK]"
        self.flagged_lndelv = self.check_features_for_attribute(lndelv, 'ELEVAT')

        # @ Isolate M_COVR object
        mcovr = S57Aux.select_by_object(objects=self.all_features, object_filter=['M_COVR', ])
        # @ Ensure M_COVR has catcov
        self.report += "M_COVR missing mandatory attribute CATCOV [CHECK]"
        self.flagged_m_covr_catcov = self.check_features_for_attribute(mcovr, 'CATCOV')
        # @ Ensure M_COVR has inform
        self.report += "M_COVR missing mandatory attribute INFORM [CHECK]"
        self.flagged_m_covr_inform = self.check_features_for_attribute(mcovr, 'INFORM')
        # @ Ensure M_COVR has ninfom
        self.report += "M_COVR missing mandatory attribute NINFOM [CHECK]"
        self.flagged_m_covr_ninfom = self.check_features_for_attribute(mcovr, 'NINFOM')

        # @ Remove soundings from features
        no_soundings = S57Aux.filter_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        # @ For the office profile, ensure all features have onotes
        if self.profile == 0:  # office
            self.report += "Non-sounding features missing onotes (just FYI) [CHECK]"
            self.flagged_onotes = self.check_features_for_attribute(no_soundings, 'onotes')

        # finalize the summary
        self.finalize_summary()

    # noinspection PyStatementEffect
    def run_2018(self):
        """HSSD 2018 checks """

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
        # @ Ensure new or updated wrecks have watlev
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_watlev = self.flag_features_with_attribute_value(wrecks, attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated wrecks have valsou
        self.report += "New or Updated WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_valsou = self.check_features_for_attribute(wrecks, 'VALSOU')
        # @ Ensure new or updated wrecks have tecsou
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_wrecks_tecsou = self.flag_features_with_attribute_value(wrecks, attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated wrecks have quasou
        self.report += "New or Updated WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_quasou = self.flag_features_with_attribute_value(wrecks, attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Isolate new or updated rocks
        rocks = S57Aux.select_by_object(objects=new_update_features, object_filter=['UWTROC', ])
        # @ Ensure new or updated rocks have valsou
        self.report += "New or Updated UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_valsou = self.check_features_for_attribute(rocks, 'VALSOU')
        # @ Ensure new or updated rocks have watlev
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_watlev = self.flag_features_with_attribute_value(rocks, attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated rocks have quasou
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_quasou = self.flag_features_with_attribute_value(rocks, attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated rocks have tecsou
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_uwtroc_tecsou = self.flag_features_with_attribute_value(rocks, attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # @ Isolate new or updated obstructions
        obstrns = S57Aux.select_by_object(objects=new_update_features, object_filter=['OBSTRN', ])
        # @ Exclude foul area obstructions
        obstrns_no_foul = S57Aux.filter_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])
        # Include only foul obstructions
        obstrns_foul = S57Aux.select_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])
        # Include only point feature foul obstructions.
        obstrns_foul_points = S57Aux.select_only_points(obstrns_foul)
        # @ Ensure new or updated obstructions (excluding foul area obstructions) have images
        self.report += "New or Updated OBSTRN missing mandatory attribute images [CHECK]"
        self.flagged_obstrn_images = self.check_features_for_attribute(obstrns_no_foul, 'images')
        # @ Ensure new or updated obstructions have valsou
        self.report += "New or Updated non-foul OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_valsou = self.check_features_for_attribute(obstrns_no_foul, 'VALSOU')
        self.report += "New or Updated foul area point OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_foul_points_valsou = self.check_features_for_attribute(obstrns_foul_points, 'VALSOU')
        # @ Ensure new or updated obstructions have watlev
        self.report += "New or Updated OBSTRN with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_obstrn_watlev = self.flag_features_with_attribute_value(obstrns, attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated obstructions have quasou
        self.report += "New or Updated OBSTRN with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_quasou = self.flag_features_with_attribute_value(obstrns, attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated obstructions have tecsou
        self.report += "New or Updated OBSTRN missing mandatory attribute TECSOU [CHECK]"
        self.flagged_obstrn_tecsou = self.flag_features_with_attribute_value(obstrns, attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # Isolate line and area foul area obstructions
        obstrns_foul_lines_areas = S57Aux.select_lines_and_areas(obstrns_foul)
        # Check line and area foul area obstructions do not have VALSOU
        self.report += "Warning: Foul line and area obstructions should not have VALSOU [CHECK]"
        self.flagged_obstrn_foul_valsou = self.check_features_without_attribute(objects=obstrns_foul_lines_areas,
                                                                                attribute='VALSOU', possible=True)

        # @ Isolate new or updated offshore platforms
        ofsplf = S57Aux.select_by_object(objects=new_update_features, object_filter=['OFSPLF', ])
        # @ Ensure new or updated offshore platforms have images
        self.report += "New or Updated OFSPLF missing images [CHECK]"
        self.flagged_ofsplf = self.check_features_for_attribute(ofsplf, 'images')

        # @ Isolate new or updated seabed areas
        sbdare = S57Aux.select_by_object(objects=new_update_features, object_filter=['SBDARE', ])
        # @ Ensure new or updated seabed areas have natsur
        self.report += "New or Updated SBDARE with empty/missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_natsur = self.flag_features_with_attribute_value(sbdare, attribute='NATSUR',
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

        # @ Isolate line and area seabed areas
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)
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

        # For the office profile, ensure all features have onotes
        if self.profile == 0:  # office
            self.report += "Features missing onotes [CHECK]"
            self.flagged_onotes = self.check_features_for_attribute(self.all_features, 'onotes')

            # For the office profile, check for empty hsdrec
            self.report += "Features with empty/unknown attribute hsdrec [CHECK]"
            self.flagged_hsdrec_empty = self.flag_features_with_attribute_value(self.all_features, attribute='hsdrec',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)

            # For the office profile, check for prohibited features by feature type
            self.report += "Prohibited Feature types [CHECK]"
            self.flagged_prohibited = self.flag_features_by_type(objects=self.all_features, types_to_flag=[
                'DRGARE', 'LOGPON', 'PIPARE', 'PIPOHD', 'PIPSOL', 'DMPGRD', 'LIGHTS', 'BOYLAT', 'BOYSAW', 'BOYSPP',
                'DAYMAR', 'FOGSIG', 'CBLSUB', 'CBLARE', 'FAIRWY', 'RTPBCN', 'BOYISD', 'BOYINB', 'BOYCAR', 'CBLOHD'])

            # For the office profile, check for prohibited fish haven
            obstrn = S57Aux.select_by_object(objects=self.all_features, object_filter=['OBSTRN', ])
            self.report += "Features with prohibited attribute fish haven [CHECK]"
            self.flagged_fish_haven = self.flag_features_with_attribute_value(objects=obstrn, attribute='CATOBS',
                                                                              values_to_flag=['5', ])

            # For the office profile, check for prohibited mooring buoys
            morfac = S57Aux.select_by_object(objects=self.all_features, object_filter=['MORFAC', ])
            self.report += "Features with prohibited attribute mooring buoy [CHECK]"
            self.flagged_mooring_buoy = self.flag_features_with_attribute_value(objects=morfac, attribute='CATMOR',
                                                                                values_to_flag=['7', ])

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

        # finalize the summary
        self.finalize_summary()

    # noinspection PyStatementEffect
    def run_2019(self):
        """HSSD 2019 checks """

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
        # @ Ensure new or updated wrecks have watlev
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_watlev = self.flag_features_with_attribute_value(wrecks, attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated wrecks have valsou
        self.report += "New or Updated WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_valsou = self.check_features_for_attribute(wrecks, 'VALSOU')
        # @ Ensure new or updated wrecks have tecsou
        self.report += "New or Updated WRECKS with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_wrecks_tecsou = self.flag_features_with_attribute_value(wrecks, attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated wrecks have quasou
        self.report += "New or Updated WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_quasou = self.flag_features_with_attribute_value(wrecks, attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Isolate new or updated rocks
        rocks = S57Aux.select_by_object(objects=new_update_features, object_filter=['UWTROC', ])
        # @ Ensure new or updated rocks have valsou
        self.report += "New or Updated UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_valsou = self.check_features_for_attribute(rocks, 'VALSOU')
        # @ Ensure new or updated rocks have watlev
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_watlev = self.flag_features_with_attribute_value(rocks, attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated rocks have quasou
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_quasou = self.flag_features_with_attribute_value(rocks, attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated rocks have tecsou
        self.report += "New or Updated UWTROC with empty/missing mandatory attribute TECSOU [CHECK]"
        self.flagged_uwtroc_tecsou = self.flag_features_with_attribute_value(rocks, attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)

        # @ Isolate new or updated obstructions
        obstrns = S57Aux.select_by_object(objects=new_update_features, object_filter=['OBSTRN', ])
        # @ Exclude foul area obstructions
        obstrns_no_foul = S57Aux.filter_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])
        # Include only foul obstructions
        obstrns_foul = S57Aux.select_by_attribute_value(objects=obstrns, attribute='CATOBS', value_filter=['6', ])
        # Include only point feature foul obstructions.
        obstrns_foul_points = S57Aux.select_only_points(obstrns_foul)
        # @ Ensure new or updated obstructions (excluding foul area obstructions) have images
        self.report += "New or Updated OBSTRN missing mandatory attribute images [CHECK]"
        self.flagged_obstrn_images = self.check_features_for_attribute(obstrns_no_foul, 'images')
        # @ Ensure new or updated obstructions have valsou
        self.report += "New or Updated non-foul OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_valsou = self.check_features_for_attribute(obstrns_no_foul, 'VALSOU')
        self.report += "New or Updated foul area point OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_foul_points_valsou = self.check_features_for_attribute(obstrns_foul_points, 'VALSOU')
        # @ Ensure new or updated obstructions have watlev
        self.report += "New or Updated OBSTRN with empty/missing mandatory attribute WATLEV [CHECK]"
        self.flagged_obstrn_watlev = self.flag_features_with_attribute_value(obstrns, attribute='WATLEV',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated obstructions have quasou
        self.report += "New or Updated OBSTRN with empty/missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_quasou = self.flag_features_with_attribute_value(obstrns, attribute='QUASOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # @ Ensure new or updated obstructions have tecsou
        self.report += "New or Updated OBSTRN missing mandatory attribute TECSOU [CHECK]"
        self.flagged_obstrn_tecsou = self.flag_features_with_attribute_value(obstrns, attribute='TECSOU',
                                                                             values_to_flag=['', ],
                                                                             check_attrib_existence=True)
        # Isolate line and area foul area obstructions
        obstrns_foul_lines_areas = S57Aux.select_lines_and_areas(obstrns_foul)
        # Check line and area foul area obstructions do not have VALSOU
        self.report += "Warning: Foul line and area obstructions should not have VALSOU [CHECK]"
        self.flagged_obstrn_foul_valsou = self.check_features_without_attribute(objects=obstrns_foul_lines_areas,
                                                                                attribute='VALSOU', possible=True)

        # @ Isolate new or updated offshore platforms
        ofsplf = S57Aux.select_by_object(objects=new_update_features, object_filter=['OFSPLF', ])
        # @ Ensure new or updated offshore platforms have images
        self.report += "New or Updated OFSPLF missing images [CHECK]"
        self.flagged_ofsplf = self.check_features_for_attribute(ofsplf, 'images')

        # @ Isolate new or updated seabed areas
        sbdare = S57Aux.select_by_object(objects=new_update_features, object_filter=['SBDARE', ])
        # @ Ensure new or updated seabed areas have natsur
        self.report += "New or Updated SBDARE with empty/missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_natsur = self.flag_features_with_attribute_value(sbdare, attribute='NATSUR',
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

        # @ Isolate line and area seabed areas
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)
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

        # For the office profile, ensure all features have onotes
        if self.profile == 0:  # office
            self.report += "Features missing onotes [CHECK]"
            self.flagged_onotes = self.check_features_for_attribute(self.all_features, 'onotes')

            # For the office profile, check for empty hsdrec
            self.report += "Features with empty/unknown attribute hsdrec [CHECK]"
            self.flagged_hsdrec_empty = self.flag_features_with_attribute_value(self.all_features, attribute='hsdrec',
                                                                                values_to_flag=['', ],
                                                                                check_attrib_existence=True)

            # For the office profile, check for prohibited features by feature type
            self.report += "Prohibited Feature types [CHECK]"
            self.flagged_prohibited = self.flag_features_by_type(objects=self.all_features, types_to_flag=[
                'DRGARE', 'LOGPON', 'PIPARE', 'PIPOHD', 'PIPSOL', 'DMPGRD', 'LIGHTS', 'BOYLAT', 'BOYSAW', 'BOYSPP',
                'DAYMAR', 'FOGSIG', 'CBLSUB', 'CBLARE', 'FAIRWY', 'RTPBCN', 'BOYISD', 'BOYINB', 'BOYCAR', 'CBLOHD'])

            # For the office profile, check for prohibited fish haven
            obstrn = S57Aux.select_by_object(objects=self.all_features, object_filter=['OBSTRN', ])
            self.report += "Features with prohibited attribute fish haven [CHECK]"
            self.flagged_fish_haven = self.flag_features_with_attribute_value(objects=obstrn, attribute='CATOBS',
                                                                              values_to_flag=['5', ])

            # For the office profile, check for prohibited mooring buoys
            morfac = S57Aux.select_by_object(objects=self.all_features, object_filter=['MORFAC', ])
            self.report += "Features with prohibited attribute mooring buoy [CHECK]"
            self.flagged_mooring_buoy = self.flag_features_with_attribute_value(objects=morfac, attribute='CATMOR',
                                                                                values_to_flag=['7', ])

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

        # finalize the summary
        self.finalize_summary()

    # noinspection PyStatementEffect
    def finalize_summary(self):
        """Add a summary to the report"""
        count = 1

        # Add a summary to the report
        self.report += 'SUMMARY [TOTAL]'

        self.report += 'Check %d - Redundant features: %s' \
                       % (count, len(self.redundancy))
        count += 1

        self.report += 'Check %d - Features (excluding carto notes) missing mandatory attribute SORIND: %s' \
                       % (count, len(self.flagged_sorind))
        count += 1
        self.report += 'Check %d - Features (excluding carto notes) with invalid attribute SORIND: %s' \
                       % (count, len(self.flagged_sorind_invalid))
        count += 1

        self.report += 'Check %d - Features (excluding carto notes) missing mandatory attribute SORDAT: %s' \
                       % (count, len(self.flagged_sordat))
        count += 1
        self.report += 'Check %d - Features (excluding carto notes) with invalid attribute SORDAT: %s' \
                       % (count, len(self.flagged_sordat_invalid))
        count += 1

        self.report += 'Check %d - Assigned features missing mandatory attribute description: %s' \
                       % (count, len(self.flagged_description))
        count += 1
        self.report += 'Check %d - Assigned features with empty/missing mandatory attribute remarks: %s' \
                       % (count, len(self.flagged_remarks))
        count += 1

        self.report += 'Check %d - New or deleted features missing mandatory attribute remarks: %s' \
                       % (count, len(self.flagged_remarks_features))
        count += 1

        self.report += 'Check %d - New or deleted features missing mandatory attribute recomd: %s' \
                       % (count, len(self.flagged_recommend_features))
        count += 1

        self.report += 'Check %d - SOUNDG with empty/missing mandatory attribute TECSOU: %s' \
                       % (count, len(self.flagged_soundings_tecsou))
        count += 1

        self.report += 'Check %d - SOUNDG  with empty/missing mandatory attribute QUASOU: %s' \
                       % (count, len(self.flagged_soundings_quasou))
        count += 1

        self.report += 'Check %d - Special feature types (DTONS) missing images: %s' \
                       % (count, len(self.flagged_dtons))
        count += 1
        self.report += 'Check %d - Special feature types (WRECKS) missing images: %s' \
                       % (count, len(self.flagged_wrecks_images))
        count += 1

        self.report += 'Check %d - New or Updated WRECKS with empty/missing mandatory attribute CATWRK: %s' \
                       % (count, len(self.flagged_wrecks_catwrk))
        count += 1
        self.report += 'Check %d - New or Updated WRECKS with empty/missing mandatory attribute WATLEV: %s' \
                       % (count, len(self.flagged_wrecks_watlev))
        count += 1
        self.report += 'Check %d - New or Updated WRECKS missing mandatory attribute VALSOU: %s' \
                       % (count, len(self.flagged_wrecks_valsou))
        count += 1
        self.report += 'Check %d - New or Updated WRECKS with empty/missing mandatory attribute TECSOU: %s' \
                       % (count, len(self.flagged_wrecks_tecsou))
        count += 1
        self.report += 'Check %d - New or Updated WRECKS with empty/missing mandatory attribute QUASOU: %s' \
                       % (count, len(self.flagged_wrecks_quasou))
        count += 1

        self.report += 'Check %d - New or Updated UWTROC missing mandatory attribute VALSOU: %s' \
                       % (count, len(self.flagged_uwtroc_valsou))
        count += 1
        self.report += 'Check %d - New or Updated UWTROC with empty/missing mandatory attribute WATLEV: %s' \
                       % (count, len(self.flagged_uwtroc_watlev))
        count += 1
        self.report += 'Check %d - New or Updated UWTROC with empty/missing mandatory attribute QUASOU: %s' \
                       % (count, len(self.flagged_uwtroc_quasou))
        count += 1
        self.report += 'Check %d - New or Updated UWTROC with empty/missing mandatory attribute TECSOU: %s' \
                       % (count, len(self.flagged_uwtroc_tecsou))
        count += 1

        self.report += 'Check %d - New or Updated OBSTRN missing mandatory attribute images: %s' \
                       % (count, len(self.flagged_obstrn_images))
        count += 1

        if self.version in ["2018", "2019"]:

            self.report += 'Check %d - New or Updated non-foul OBSTRN missing mandatory attribute VALSOU: %s' \
                           % (count, len(self.flagged_obstrn_valsou))
            count += 1

            self.report += 'Check %d - New or Updated foul area point OBSTRN missing mandatory attribute VALSOU: %s' \
                           % (count, len(self.flagged_obstrn_foul_points_valsou))
            count += 1

        else:

            self.report += 'Check %d - New or Updated OBSTRN missing mandatory attribute VALSOU: %s' \
                           % (count, len(self.flagged_obstrn_valsou))
            count += 1

        self.report += 'Check %d - New or Updated OBSTRN with empty/missing mandatory attribute WATLEV: %s' \
                       % (count, len(self.flagged_obstrn_watlev))
        count += 1

        self.report += 'Check %d - New or Updated OBSTRN with empty/missing mandatory attribute QUASOU: %s' \
                       % (count, len(self.flagged_obstrn_quasou))
        count += 1
        self.report += 'Check %d - New or Updated OBSTRN with empty/missing mandatory attribute TECSOU: %s' \
                       % (count, len(self.flagged_obstrn_tecsou))
        count += 1

        if self.version in ["2018", "2019"]:
            self.report += 'Check %d - Warning: Foul line and area obstructions should not have VALSOU: %s' \
                           % (count, len(self.flagged_obstrn_foul_valsou))

            count += 1

        if self.flagged_ofsplf != -1:
            self.report += 'Check %d - New or Updated OFSPLF missing mandatory attribute images: %s' \
                           % (count, len(self.flagged_ofsplf))
            count += 1

        self.report += 'Check %d - SBDARE with empty/missing mandatory attribute NATSUR: %s' \
                       % (count, len(self.flagged_sbdare_natsur))
        count += 1

        self.report += 'Check %d - SBDARE points with more NATQUA than NATSUR: %s' \
                       % (count, len(self.flagged_sbdare_pt_natqua))
        count += 1

        self.report += 'Check %d - SBDARE points with more COLOUR than NATSUR: %s' \
                       % (count, len(self.flagged_sbdare_pt_colour))
        count += 1

        self.report += 'Check %d - SBDARE points with unallowable NATSUR / NATQUA combination: %s' \
                       % (count, len(self.flagged_sbdare_pt_allowable_combo))
        count += 1

        self.report += 'Check %d - SBDARE lines and areas have empty or missing mandatory attribute WATLEV: %s' \
                       % (count, len(self.flagged_sbdare_watlev))
        count += 1

        self.report += 'Check %d - MORFAC with empty/missing mandatory attribute CATMOR: %s' \
                       % (count, len(self.flagged_morfac))
        count += 1

        self.report += 'Check %d - COALNE with empty/missing mandatory attribute CATCOA: %s' \
                       % (count, len(self.flagged_coalne))
        count += 1
        self.report += 'Check %d - SLCONS with empty/missing mandatory attribute CATSLC: %s' \
                       % (count, len(self.flagged_slcons))
        count += 1

        self.report += 'Check %d - LNDELV missing mandatory attribute ELEVAT: %s' \
                       % (count, len(self.flagged_lndelv))
        count += 1

        if self.version in ["2018", "2019"]:

            if self.use_mhw:
                self.report += 'Check %d - New or Updated VALSOU features with invalid WATLEV: %s' \
                               % (count, len(self.flagged_new_valsous_watlev))
                count += 1

            self.report += 'Check %d - Invalid New or Updated ELEVAT features: %s' \
                           % (count, len(self.flagged_new_elevat))
            count += 1

        self.report += 'Check %d - M_COVR with empty/missing mandatory attribute CATCOV: %s' \
                       % (count, len(self.flagged_m_covr_catcov))
        count += 1
        self.report += 'Check %d - M_COVR missing mandatory attribute INFORM: %s' \
                       % (count, len(self.flagged_m_covr_inform))
        count += 1
        self.report += 'Check %d - M_COVR missing mandatory attribute NINFOM: %s' \
                       % (count, len(self.flagged_m_covr_ninfom))
        count += 1

        if self.profile == 0:  # not used in 'field' profile

            self.report += 'Check %d - Features with empty/missing onotes: %s' \
                           % (count, len(self.flagged_onotes))
            count += 1

            if self.version in ["2018", "2019"]:
                self.report += 'Check %d - Features with empty/unknown attribute hsdrec: %s' \
                               % (count, len(self.flagged_hsdrec_empty))
                count += 1
                self.report += 'Check %d - Features are prohibited by MCD: %s' \
                               % (count, len(self.flagged_prohibited))
                count += 1
                self.report += 'Check %d - Fish havens are prohibited by MCD: %s' \
                               % (count, len(self.flagged_fish_haven))
                count += 1
                self.report += 'Check %d - Mooring buoys are prohibited by MCD: %s' \
                               % (count, len(self.flagged_mooring_buoy))
                count += 1
                self.report += 'Check %d - M_QUAL features with empty/missing mandatory attribute CATZOC: %s' \
                               % (count, len(self.flagged_m_qual_catzoc))
                count += 1
                self.report += 'Check %d - M_QUAL features missing mandatory attribute SURSTA: %s' \
                               % (count, len(self.flagged_m_qual_sursta))
                count += 1
                self.report += 'Check %d - M_QUAL features missing mandatory attribute SUREND: %s' \
                               % (count, len(self.flagged_m_qual_surend))
                count += 1
                self.report += 'Check %d - M_QUAL features with empty/missing mandatory attribute TECSOU: %s' \
                               % (count, len(self.flagged_m_qual_tecsou))
                count += 1
