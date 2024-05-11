import datetime
import logging
import sys
from collections import defaultdict

from hyo2.qc.chart.scan.base_scan import BaseScan, scan_algos
from hyo2.qc.common.geodesy import Geodesy
from hyo2.qc.common.s57_aux import S57Aux

logger = logging.getLogger(__name__)


class FeatureScanV3(BaseScan):
    rounding = 8  # ~0.0011 m (at 45 deg of latitude)

    def __init__(self, s57, ss, version="2016", progress=None):
        super(FeatureScanV3, self).__init__(s57=s57, ss=ss, progress=progress)
        self.type = scan_algos["FEATURE_SCAN_v3"]
        self.version = version
        self.gd = Geodesy()

        self.all_features = self.s57.rec10s
        if self.ss is not None:
            self.all_ss = self.ss.rec10s
        else:
            self.all_ss = list()
        self.ss_dict = defaultdict(int)
        self.all_cs = list()
        self.cs_dict = defaultdict(int)

        # summary info
        self.flagged_feature_redundancy = list()
        self.flagged_cs_redundancy = list()
        self.flagged_ss_redundancy = list()
        self.flagged_cs_in_ss = list()
        self.flagged_valsou_in_ss = list()
        self.flagged_valsou_not_in_cs = list()

        self.flagged_prohibited_scamin = list()
        self.flagged_prohibited_recdat = list()
        self.flagged_prohibited_verdat = list()
        self.flagged_mandatory_sorind = list()
        self.flagged_invalid_sorind = list()
        self.flagged_missing_sordat = list()
        self.flagged_invalid_sordat = list()
        self.flagged_missing_ninfom = list()
        self.flagged_soundg_with_status = list()
        self.flagged_wrecks_missing_catwrk = list()
        self.flagged_wrecks_missing_watlev = list()
        self.flagged_wrecks_missing_valsou = list()
        self.flagged_wrecks_missing_quasou = list()
        # @ added requirement that awash wrecks have expsou in 2016
        self.flagged_awash_wrecks_missing_expsou = list()
        self.flagged_uwtroc_missing_valsou = list()
        self.flagged_uwtroc_missing_watlev = list()
        self.flagged_uwtroc_missing_quasou = list()
        self.flagged_obstrn_missing_valsou = list()
        self.flagged_obstrn_missing_watlev = list()
        self.flagged_obstrn_missing_quasou = list()
        # @ obstructions with catobs=foul ground no longer prohibited in 2016
        self.flagged_obstrn_with_catobs = list()
        self.flagged_morfac_missing_catmor = list()
        # @ additional prohibited attributes given to MORFAC in 2016
        self.flagged_morfac_prohibited_boyshp = list()
        self.flagged_morfac_prohibited_colour = list()
        self.flagged_morfac_prohibited_colpat = list()
        self.flagged_sbdare_missing_natsur = list()
        self.flagged_sbdare_with_colour = list()
        self.flagged_sbdare_with_watlev = list()
        self.flagged_sbdare_with_natsur_natqua = list()
        # @ additional mandatory attributes for SBDARE lines and areas in 2016
        self.flagged_sbdare_la_missing_natsur = list()
        self.flagged_sbdare_la_missing_watlev = list()
        self.flagged_coalne_missing_catcoa = list()
        self.flagged_coalne_with_elevat = list()
        # @ mandatory attribute given to CTNARE in 2016
        self.flagged_ctnare_missing_inform = list()
        self.flagged_slcons_missing_catslc = list()
        self.flagged_m_qual_missing_catzoc = list()
        self.flagged_m_qual_missing_tecsou = list()
        self.flagged_m_qual_missing_sursta = list()
        self.flagged_m_qual_missing_surend = list()
        self.flagged_m_cscl_missing_cscale = list()
        # @ added 2016 m_cover requirement for catcov
        self.flagged_m_covr_missing_catcov = list()
        # @ added 2016 carto object requirement for inform
        self.flagged_carto_missing_inform = list()
        self.flagged_carto_missing_ninfom = list()
        self.flagged_carto_missing_ntxtds = list()
        self.flagged_noaa_extended = list()

    def run(self):
        """Execute the set of check of the feature scan algorithm"""
        if self.version == "2014":
            self._run_2014()

        elif self.version == "2016":
            self._run_2016()

        elif self.version == "2018":
            self._run_2018()

        else:
            raise RuntimeError("unsupported specs version: %s" % self.version)

    def _append_flagged(self, x, y, note):
        """Helper function that append the note (if the feature position was already flagged) or add a new one"""
        # check if the point was already flagged
        for i in range(len(self.flagged_features[0])):
            if (self.flagged_features[0][i] == x) and (self.flagged_features[1][i] == y):
                self.flagged_features[2][i] = "%s, %s" % (self.flagged_features[2][i], note)
                return

        # if not flagged, just append the new flagged position
        self.flagged_features[0].append(x)
        self.flagged_features[1].append(y)
        self.flagged_features[2].append(note)

    def _check_feature_redundancy(self):
        """Function that identifies the presence of duplicated feature looking at their geometries"""
        logger.debug('Checking for feature redundancy...')

        tmp_features = list()  # to be returned without duplications
        feature_dict = defaultdict(int)

        for ft in self.all_features:
            # skip if the feature has not position
            if (len(ft.geo2s) == 0) and (len(ft.geo3s) == 0):
                tmp_features.append(ft)
                continue

            # test for redundancy
            feature_tuple = (ft.acronym, round(ft.centroid.x, self.rounding), round(ft.centroid.y, self.rounding))
            feature_dict[feature_tuple] += 1
            if feature_dict[feature_tuple] > 1:  # we have a redundancy
                # add to the flagged feature list
                self._append_flagged(ft.centroid.x, ft.centroid.y, "redundant %s" % ft.acronym)
                # add to the flagged report
                self.report += 'found %s at (%s, %s)' % (ft.acronym, ft.centroid.x, ft.centroid.y)
                self.flagged_feature_redundancy.append([ft.acronym, ft.centroid.x, ft.centroid.y])
            else:
                tmp_features.append(ft)

        # for ft in feature_dict:
        #     print("%s: %s" % (ft, feature_dict[ft]))

        if len(self.flagged_feature_redundancy) == 0:
            self.report += "OK"

        return tmp_features

    def _check_ss_redundancy(self):
        """Function that identifies the presence of duplicated SS looking at their geometries"""
        logger.debug('Checking for SS redundancy...')

        tmp_ss = list()  # to be returned without duplications
        self.ss_dict = defaultdict(int)

        for ss in self.all_ss:
            # skip if the feature has not position
            if (len(ss.geo2s) == 0) and (len(ss.geo3s) == 0):
                tmp_ss.append(ss)
                continue

            # test for redundancy
            ss_tuple = (round(ss.centroid.x, self.rounding), round(ss.centroid.y, self.rounding))
            self.ss_dict[ss_tuple] += 1
            if self.ss_dict[ss_tuple] > 1:  # we have a redundancy
                # add to the flagged feature list
                self._append_flagged(ss.centroid.x, ss.centroid.y, "redundant SS")
                # add to the flagged report
                self.report += 'found %s at (%s, %s)' % (ss.acronym, ss.centroid.x, ss.centroid.y)
                self.flagged_feature_redundancy.append([ss.acronym, ss.centroid.x, ss.centroid.y])

                # reset to 1
                self.ss_dict[ss_tuple] = 1

            else:
                tmp_ss.append(ss)

        # for ss in self.ss_dict:
        #     print("%s: %s" % (ss, self.ss_dict[ss]))

        if len(self.flagged_ss_redundancy) == 0:
            self.report += "OK"

        return tmp_ss

    def _check_cs_redundancy(self):
        """Function that identifies the presence of duplicated CS looking at their geometries"""
        logger.debug('Checking for CS redundancy...')

        tmp_cs = list()  # to be returned without duplications
        self.cs_dict = defaultdict(int)

        for cs in self.all_cs:
            # skip if the feature has not position
            if (len(cs.geo2s) == 0) and (len(cs.geo3s) == 0):
                tmp_cs.append(cs)
                continue

            # test for redundancy
            cs_tuple = (round(cs.centroid.x, self.rounding), round(cs.centroid.y, self.rounding))
            self.cs_dict[cs_tuple] += 1
            if self.cs_dict[cs_tuple] > 1:  # we have a redundancy
                # add to the flagged feature list
                self._append_flagged(cs.centroid.x, cs.centroid.y, "redundant CS")
                # add to the flagged report
                self.report += 'found %s at (%s, %s)' % (cs.acronym, cs.centroid.x, cs.centroid.y)
                self.flagged_cs_redundancy.append([cs.acronym, cs.centroid.x, cs.centroid.y])

                # reset to 1
                self.cs_dict[cs_tuple] = 1

            else:
                tmp_cs.append(cs)

        # for cs in self.cs_dict:
        #     print("%s: %s" % (cs, self.cs_dict[cs]))

        if len(self.flagged_cs_redundancy) == 0:
            self.report += "OK"

        return tmp_cs

    def _check_cs_in_ss(self):
        """
        Chart soundings (cs) must be a subset of the survey-scale soundings (ss).
        Therefore it is critical that all potential cs have a representative ss.
        """
        flagged = list()  # to be returned as a list of missing CS in SS

        for cs in self.all_cs:

            # skip if the feature has not position
            if (len(cs.geo2s) == 0) and (len(cs.geo3s) == 0):
                continue

            # add to the SS default dict
            cs_tuple = (round(cs.centroid.x, self.rounding), round(cs.centroid.y, self.rounding))
            self.ss_dict[cs_tuple] += 1

            # CS is in SS (exactly)
            if self.ss_dict[cs_tuple] == 2:
                # reset to 1
                self.ss_dict[cs_tuple] = 1
                continue

            # check if the candidate flag is close to one SS
            logger.debug('candidate CS-not-in-SS: %s' % (cs_tuple,))
            cs_is_close = False
            for ss in self.all_ss:
                if (cs.centroid.z - ss.centroid.z) > 0.01:
                    continue
                dist = self.gd.distance(lat_1=cs.centroid.y, long_1=cs.centroid.x,
                                        lat_2=ss.centroid.y, long_2=ss.centroid.x)
                if dist < 5.0:
                    logger.debug('found small distance: %s' % dist)
                    cs_is_close = True
                    break
            if cs_is_close:
                continue

            # add to the flagged feature list
            self._append_flagged(cs.centroid.x, cs.centroid.y, "CS not found in SS")
            # add to the flagged report
            self.report += 'CS at (%s, %s) not found in SS' % (cs.centroid.x, cs.centroid.y)
            flagged.append([cs.acronym, cs.centroid.x, cs.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _get_features_from_s57_no_extended(self):

        features = S57Aux.select_only_points(objects=self.all_features)
        features = S57Aux.select_by_attribute(objects=features, attribute='WATLEV')
        features = S57Aux.select_by_attribute(objects=features, attribute='VALSOU')
        features = S57Aux.select_by_object(objects=features, object_filter=['UWTROC', 'WRECKS', 'OBSTRN'])
        features = S57Aux.select_by_attribute_float(objects=features, attribute='VALSOU')

        return features

    def _check_valsou_in_ss(self, features):
        """
        The VALSOUs of all navigationally significant features must be a subset of the survey-scale
        soundings (ss). Check to ensure VALSOUs have a corresponding ss.
        """
        flagged = list()  # to be returned as a list of missing VALSOU features in SS

        for ft in features:

            # skip if the feature has not position
            if (len(ft.geo2s) == 0) and (len(ft.geo3s) == 0):
                continue

            # add to the SS default dict
            ft_tuple = (round(ft.centroid.x, self.rounding), round(ft.centroid.y, self.rounding))
            self.ss_dict[ft_tuple] += 1

            # feature is in SS (exactly)
            if self.ss_dict[ft_tuple] == 2:
                # reset to 1
                self.ss_dict[ft_tuple] = 1
                continue

            # check if the candidate flag is close to one SS
            logger.debug('candidate VALSOU-not-in-SS: %s' % (ft_tuple,))
            ft_is_close = False
            # retrieve valsou
            ft_z = None
            for attr in ft.attributes:
                if attr.acronym == "VALSOU":
                    try:
                        ft_z = float(attr.value)
                    except ValueError:
                        ft_z = None
                    break
            if ft_z is None:
                logger.warning('unable to retrieve VALSOU value')
                continue

            # identify the closest SS
            min_dist = sys.float_info.max
            min_dist_delta_z = sys.float_info.max
            for ss in self.all_ss:

                dist = self.gd.distance(lat_1=ft.centroid.y, long_1=ft.centroid.x,
                                        lat_2=ss.centroid.y, long_2=ss.centroid.x)
                if (dist > 100.0) or (dist > min_dist):
                    continue

                min_dist = dist
                min_dist_delta_z = ft_z - ss.centroid.z
                logger.debug('found small distance: %s' % dist)

            # in case that there is a SS closer than 100m and its difference in depth is very small
            if (min_dist != sys.float_info.max) and (min_dist_delta_z < 0.1):
                continue

            # add to the flagged feature list
            self._append_flagged(ft.centroid.x, ft.centroid.y, "Feature VALSOU not found in SS")
            # add to the flagged report
            self.report += 'Feature VALSOU at (%s, %s) not found in SS' % (ft.centroid.x, ft.centroid.y)
            flagged.append([ft.acronym, ft.centroid.x, ft.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_valsou_not_in_cs(self, features):
        """
        On a chart, a potential chart sounding (cs) cannot be coincident with a feature.
        Check to ensure these are not coincident.
        """
        flagged = list()  # to be returned as a list of feature in CS

        # logger.info('input: %s, %s' % (len(features), len(self.cs_dict)))

        for ft in features:

            # skip if the feature has not position
            if (len(ft.geo2s) == 0) and (len(ft.geo3s) == 0):
                continue

            # add to the CS default dict
            ft_tuple = (round(ft.centroid.x, self.rounding), round(ft.centroid.y, self.rounding))
            self.cs_dict[ft_tuple] += 1

            # feature is in SS (exactly)
            if self.cs_dict[ft_tuple] == 2:
                # reset to 1
                self.cs_dict[ft_tuple] = 1

                # add to the flagged feature list
                self._append_flagged(ft.centroid.x, ft.centroid.y, "CS found on feature")
                # add to the flagged report
                self.report += 'Feature VALSOU at (%s, %s) found in CS' % (ft.centroid.x, ft.centroid.y)
                flagged.append([ft.acronym, ft.centroid.x, ft.centroid.y])
                continue

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_for_attribute(self, objects, attribute, possible=False):
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

            # skip if the feature has not position
            if (len(obj.geo2s) == 0) and (len(obj.geo3s) == 0):
                logger.info('feature %s without position AND %s' % (obj.acronym, attribute))
                continue

            # add to the flagged feature list
            if possible:
                self._append_flagged(obj.centroid.x, obj.centroid.y, "missing %s (?)" % attribute)
            else:
                self._append_flagged(obj.centroid.x, obj.centroid.y, "missing %s" % attribute)
            # add to the flagged report
            self.report += 'found %s at (%s, %s)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_no_attribute(self, objects, attribute):
        """Check if the passed features does not have the passed attribute"""
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

            # skip if the feature has not position
            if (len(obj.geo2s) == 0) and (len(obj.geo3s) == 0):
                logger.info('feature %s without position BUT with %s' % (obj.acronym, attribute))
                continue

            # add to the flagged feature list
            self._append_flagged(obj.centroid.x, obj.centroid.y, "with %s" % attribute)
            # add to the flagged report
            self.report += 'found %s at (%s, %s)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_no_attribute_value(self, objects, attribute, value, value_meaning):
        """Check if the passed features have the passed attribute value"""
        flagged = list()

        for obj in objects:
            # do the test
            has_attribute_value = False
            for attr in obj.attributes:
                if attr.acronym == attribute:
                    if attr.value == value:
                        has_attribute_value = True

            # check passed
            if not has_attribute_value:
                continue

            # skip if the feature has not position
            if (len(obj.geo2s) == 0) and (len(obj.geo3s) == 0):
                logger.info('feature %s without position AND %s with value %s' % (obj.acronym, attribute, value))
                continue

            # add to the flagged feature list
            self._append_flagged(obj.centroid.x, obj.centroid.y,
                                 "with attribute %s set to %s" % (attribute, value_meaning))
            # add to the flagged report
            self.report += 'found %s at (%s, %s)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _hcell_sbdare(self, sbdare_points):
        # report section
        allowable = [['1', '4'], ['2', '4'], ['3', '4'], ['4', '14'], ['4', '17'], ['5', '1'],
                     ['5', '2'], ['5', '3'], ['6', '1'], ['6', '2'], ['6', '3'], ['6', '4'],
                     ['7', '1'], ['7', '2'], ['7', '3'], ['8', '1'], ['8', '4'], ['8', '5'],
                     ['8', '6'], ['8', '7'], ['8', '8'], ['8', '9'], ['8', '11'], ['8', '18'],
                     ['9', '1'], ['9', '4'], ['9', '5'], ['9', '6'], ['9', '7'], ['9', '8'],
                     ['9', '9'], ['9', '17'], ['9', '18'], ['10', '1'], ['10', '2'], ['10', '3'],
                     ['10', '4']]

        flagged = list()
        for sbdare in sbdare_points:

            natqua = None
            natsur = None

            for attr in sbdare.attributes:
                if attr.acronym == 'NATQUA':
                    natqua = attr.value
                elif attr.acronym == 'NATSUR':
                    natsur = attr.value

            check = [natqua, natsur]
            if (check in allowable) or (natqua is None) or (natsur is None):
                continue

            # add to the flagged feature list
            self._append_flagged(sbdare.centroid.x, sbdare.centroid.y,
                                 "NATQUA and NATSUR combination is not allowed")
            # add to the flagged report
            self.report += 'found %s at (%s, %s) has prohibited NATSUR/NATQUA combination [%s, %s]' \
                           % (sbdare.acronym, sbdare.centroid.x, sbdare.centroid.y, natsur, natqua)
            flagged.append([sbdare.acronym, sbdare.centroid.x, sbdare.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_for_extended_attributes(self):
        # report section
        extended_attributes = ['remrks', 'recommendations', 'images', 'description', 'sftype',
                               'dbkyid', 'onotes', 'asgnmt', 'obstim', 'prmsec']

        flagged = list()
        for ft in self.all_features:

            has_extended = False
            for attr in ft.attributes:
                # print(attr.acronym)
                if attr.acronym in extended_attributes:
                    has_extended = True
                    break

            if not has_extended:
                continue

            # add to the flagged feature list
            try:  # it may be without geometry

                self._append_flagged(ft.centroid.x, ft.centroid.y, "With NOAA extended attributes")
                flagged.append([ft.acronym, ft.centroid.x, ft.centroid.y])
                # add to the flagged report
                self.report += 'found %s at (%s, %s) with NOAA extended attribute' \
                               % (ft.acronym, ft.centroid.x, ft.centroid.y)

            except Exception:

                flagged.append([ft.acronym, -1, -1])
                # add to the flagged report
                self.report += 'found %s with NOAA extended attribute' % ft.acronym

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_for_valid_sorind(self, objects, check_space=True):
        """Check if the passed features have valid SORIND"""
        flagged = list()

        for obj in objects:
            # do the test
            is_valid = True
            for attr in obj.attributes:
                if attr.acronym == "SORIND":

                    tokens = attr.value.split(',')
                    # logger.debug("%s" % tokens)

                    if len(attr.value.splitlines()) > 1:
                        logger.info('too many attribute lines')
                        is_valid = False

                    elif len(tokens) != 4:
                        logger.info('invalid number of comma-separated fields')
                        is_valid = False

                    elif (tokens[0][0] == " " or tokens[1][0] == " " or tokens[2][0] == " " or tokens[3][0] == " ") \
                            and check_space:
                        logger.info('invalid space after comma field-separator')
                        is_valid = False

                    elif tokens[0] != "US":
                        logger.info('first field should be "US", it is: "%s"' % tokens[0])
                        is_valid = False

                    elif tokens[1] != "US":
                        logger.info('second field should be "US", it is: "%s"' % tokens[1])
                        is_valid = False

                    elif tokens[2] != "graph":
                        logger.info('third field should be "graph", it is: "%s"' % tokens[2])
                        is_valid = False

                    break

            # check passed
            if is_valid:
                continue

            try:
                # add to the flagged feature list
                self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid SORIND")
                # add to the flagged report
                self.report += 'found %s at (%s, %s)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
                flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

            except RuntimeError as e:
                logger.warning("skipping %s: %s" % (obj.acronym, e))

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _check_features_for_valid_sordat(self, objects):
        """Check if the passed features have valid SORDAT"""
        flagged = list()

        for obj in objects:
            # do the test
            is_valid = True
            for attr in obj.attributes:
                if attr.acronym == "SORDAT":

                    # logger.debug("%s" % attr.value)

                    cast_issue = False
                    timestamp = None
                    now = None
                    try:
                        timestamp = datetime.datetime(year=int(attr.value[0:4]),
                                                      month=int(attr.value[4:6]),
                                                      day=int(attr.value[6:8]))
                        now = datetime.datetime.now()

                    except Exception:
                        cast_issue = True

                    if cast_issue:
                        logger.info('invalid date format: %s' % attr.value)
                        is_valid = False

                    elif len(attr.value) != 8:
                        logger.info('the date format is YYYYMMDD, invalid number of digits: %d' % len(attr.value))
                        is_valid = False

                    elif timestamp > now:
                        if (timestamp.year > now.year) or (timestamp.year == now.year and timestamp.month > now.month):
                            logger.info('the date in use is in the future: %d' % len(attr.value))
                            is_valid = False

                    break

            # check passed
            if is_valid:
                continue

            # add to the flagged feature list
            self._append_flagged(obj.centroid.x, obj.centroid.y, "invalid SORDAT")
            # add to the flagged report
            self.report += 'found %s at (%s, %s)' % (obj.acronym, obj.centroid.x, obj.centroid.y)
            flagged.append([obj.acronym, obj.centroid.x, obj.centroid.y])

        if len(flagged) == 0:
            self.report += "OK"

        return flagged

    def _run_2014(self):
        """2014 checks"""
        logger.debug('checking against specs version: %s' % self.version)

        # PRE-PROCESSING: retrieve soundings for features and SS

        self.progress.add(quantum=2, text="Retrieve soundings from features")
        self.all_cs = S57Aux.select_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        logger.debug('%d soundings in features' % len(self.all_cs))

        if self.all_ss:
            self.progress.add(quantum=2, text="Retrieve soundings from SS")
            self.all_ss = S57Aux.select_by_object(objects=self.all_ss, object_filter=['SOUNDG', ])
            logger.debug('%d soundings in SS' % len(self.all_ss))

        # CHECK REDUNDANCY

        self.progress.add(quantum=2, text="Feature redundancy check")
        self.report += "Redundant features [CHECK]"
        self.all_features = self._check_feature_redundancy()

        if self.all_cs:
            self.progress.add(quantum=2, text="CS redundancy check")
            self.report += "Redundant CS [CHECK]"
            self.all_cs = self._check_cs_redundancy()  # + build CS dict
        else:
            self.report += "Redundant CS [SKIP_CHK]"
            self.flagged_cs_redundancy = -1

        if self.all_ss:
            self.progress.add(quantum=2, text="SS redundancy check")
            self.report += "Redundant SS [CHECK]"
            self.all_ss = self._check_ss_redundancy()  # + build SS dict
        else:
            self.report += "Redundant SS [SKIP_CHK]"
            self.flagged_ss_redundancy = -1

        # (OPTIONAL) CHECK: CS subset of SS

        if self.all_ss and self.all_cs:
            self.progress.add(quantum=2, text="CS subset of SS check")
            self.report += "CS subset of SS [CHECK]"
            self.flagged_cs_in_ss = self._check_cs_in_ss()
        else:
            self.report += "CS subset of SS [SKIP_CHK]"
            self.flagged_cs_in_ss = -1

        # CHECKS: valsous in SS, but not in CS

        if self.all_ss or self.all_cs:  # to avoid useless computations
            features = self._get_features_from_s57_no_extended()
        else:
            features = list()

        if self.all_ss:
            self.progress.add(quantum=2, text="VALSOUs in SS check")
            self.report += "VALSOUs subset of SS [CHECK]"
            self.flagged_valsou_in_ss = self._check_valsou_in_ss(features=features)
        else:
            self.report += "VALSOUs subset of SS [SKIP_CHK]"
            self.flagged_valsou_in_ss = -1

        if self.all_cs:
            self.progress.add(quantum=2, text="VALSOUs not in CS check")
            self.report += "VALSOUs not subset of CS [CHECK]"
            self.flagged_valsou_not_in_cs = self._check_valsou_not_in_cs(features=features)
        else:
            self.report += "VALSOUs not subset of CS [SKIP_CHK]"
            self.flagged_valsou_not_in_cs = -1

        # ATTRIBUTE CHECKS:

        self.progress.add(quantum=1, text="Feature(s) with prohibited attribute SCAMIN")
        self.report += "Feature(s) with prohibited attribute SCAMIN [CHECK]"
        self.flagged_prohibited_scamin = self._check_features_no_attribute(objects=self.all_features,
                                                                           attribute='SCAMIN')

        self.progress.add(quantum=1, text="Feature(s) with prohibited attribute RECDAT")
        self.report += "Feature(s) with prohibited attribute RECDAT [CHECK]"
        self.flagged_prohibited_recdat = self._check_features_no_attribute(objects=self.all_features,
                                                                           attribute='RECDAT')

        self.progress.add(quantum=1, text="Feature(s) with prohibited attribute VERDAT")
        self.report += "Feature(s) with prohibited attribute VERDAT [CHECK]"
        self.flagged_prohibited_verdat = self._check_features_no_attribute(objects=self.all_features,
                                                                           attribute='VERDAT')

        feature_objects = S57Aux.filter_by_object(objects=self.all_features,
                                                  object_filter=['$AREAS', '$LINES', '$CSYMB', '$COMPS', '$TEXTS'])
        new_update_features = S57Aux.select_by_attribute_value(objects=feature_objects, attribute='descrp',
                                                               value_filter=['1', '2', ])

        self.progress.add(quantum=1, text="New/updated feature(s) with mandatory attribute SORIND")
        self.report += "New/updated feature(s) with mandatory attribute SORIND [CHECK]"
        self.flagged_mandatory_sorind = self._check_features_for_attribute(objects=new_update_features,
                                                                           attribute='SORIND')

        self.progress.add(quantum=1, text="New/updated feature(s) with invalid attribute SORIND")
        self.report += "New/updated feature(s) with invalid attribute SORIND [CHECK]"
        self.flagged_invalid_sorind = self._check_features_for_valid_sorind(objects=new_update_features)

        self.progress.add(quantum=1, text="New/updated feature(s) missing mandatory attribute SORDAT")
        self.report += "New/updated feature(s) missing mandatory attribute SORDAT [CHECK]"
        self.flagged_missing_sordat = self._check_features_for_attribute(objects=new_update_features,
                                                                         attribute='SORDAT')

        self.progress.add(quantum=1, text="New/updated feature(s) with invalid attribute SORDAT")
        self.report += "New/updated feature(s) with invalid attribute SORDAT [CHECK]"
        self.flagged_invalid_sordat = self._check_features_for_valid_sordat(objects=new_update_features)

        ninfom_check = S57Aux.filter_by_object(objects=feature_objects,
                                               object_filter=['SOUNDG', 'M_COVR', 'M_QUAL', 'M_CSCL', 'DEPARE'])

        self.progress.add(quantum=1, text="Feature(s) missing mandatory attribute NINFOM")
        self.report += "Feature(s) missing mandatory attribute NINFOM [CHECK]"
        self.flagged_missing_ninfom = self._check_features_for_attribute(objects=ninfom_check,
                                                                         attribute='NINFOM')

        # > Are we sure about this? If you can to the original code there is not SOUNDG, but all the features
        # @ Should be just soundings -- confirmed
        self.progress.add(quantum=1, text="SOUNDG with prohibited attribute STATUS")
        self.report += "SOUNDG with prohibited attribute STATUS [CHECK]"
        self.flagged_soundg_with_status = self._check_features_no_attribute(objects=self.all_cs,
                                                                            attribute='STATUS')

        # wreck specific

        wrecks = S57Aux.select_by_object(self.all_features, ['WRECKS', ])

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute CATWRK")
        self.report += "WRECKS missing mandatory attribute CATWRK [CHECK]"
        self.flagged_wrecks_missing_catwrk = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='CATWRK')

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute WATLEV")
        self.report += "WRECKS missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_missing_watlev = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='WATLEV')

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute VALSOU")
        self.report += "WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_missing_valsou = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='VALSOU')

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute QUASOU")
        self.report += "WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_missing_quasou = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='QUASOU')

        # rock-specific

        rocks = S57Aux.select_by_object(self.all_features, ['UWTROC', ])

        self.progress.add(quantum=1, text="UWTROC missing mandatory attribute VALSOU")
        self.report += "UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_missing_valsou = self._check_features_for_attribute(objects=rocks,
                                                                                attribute='VALSOU')

        self.progress.add(quantum=1, text="UWTROC missing mandatory attribute WATLEV")
        self.report += "UWTROC missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_missing_watlev = self._check_features_for_attribute(objects=rocks,
                                                                                attribute='WATLEV')

        self.progress.add(quantum=1, text="UWTROC missing mandatory attribute QUASOU")
        self.report += "UWTROC missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_missing_quasou = self._check_features_for_attribute(objects=rocks,
                                                                                attribute='QUASOU')

        # obstruction-specific

        obstructions = S57Aux.select_by_object(self.all_features, ['OBSTRN', ])

        self.progress.add(quantum=1, text="OBSTRN missing mandatory attribute VALSOU")
        self.report += "OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_missing_valsou = self._check_features_for_attribute(objects=obstructions,
                                                                                attribute='VALSOU')

        self.progress.add(quantum=1, text="OBSTRN missing mandatory attribute WATLEV")
        self.report += "OBSTRN missing mandatory attribute WATLEV [CHECK]"
        self.flagged_obstrn_missing_watlev = self._check_features_for_attribute(objects=obstructions,
                                                                                attribute='WATLEV')

        self.progress.add(quantum=1, text="OBSTRN missing mandatory attribute QUASOU")
        self.report += "OBSTRN missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_missing_quasou = self._check_features_for_attribute(objects=obstructions,
                                                                                attribute='QUASOU')

        self.progress.add(quantum=1, text="OBSTRN with CATOBS set to foul ground")
        self.report += "OBSTRN with CATOBS set to foul ground [CHECK]"
        self.flagged_obstrn_with_catobs = self._check_features_no_attribute_value(objects=obstructions,
                                                                                  attribute='CATOBS',
                                                                                  value="7",
                                                                                  value_meaning="foul ground")

        # more

        morfac = S57Aux.select_by_object(self.all_features, ['MORFAC', ])
        self.progress.add(quantum=1, text="MORFAC missing mandatory attribute CATMOR")
        self.report += "MORFAC missing mandatory attribute CATMOR [CHECK]"
        self.flagged_morfac_missing_catmor = self._check_features_for_attribute(objects=morfac,
                                                                                attribute='CATMOR')

        sbdare = S57Aux.select_by_object(self.all_features, ['SBDARE', ])
        sbdare_points = S57Aux.select_only_points(sbdare)

        self.progress.add(quantum=1, text="SBDARE missing mandatory attribute NATSUR")
        self.report += "SBDARE missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_missing_natsur = self._check_features_for_attribute(objects=sbdare_points,
                                                                                attribute='NATSUR')

        self.progress.add(quantum=1, text="SBDARE with prohibited attribute COLOUR")
        self.report += "SBDARE with prohibited attribute COLOUR [CHECK]"
        self.flagged_sbdare_with_colour = self._check_features_no_attribute(objects=sbdare_points,
                                                                            attribute='COLOUR')

        self.progress.add(quantum=1, text="SBDARE with prohibited attribute WATLEV")
        self.report += "SBDARE with prohibited attribute WATLEV [CHECK]"
        self.flagged_sbdare_with_watlev = self._check_features_no_attribute(objects=sbdare_points,
                                                                            attribute='WATLEV')

        self.progress.add(quantum=1, text="SBDARE with unallowable NATSUR/NATQUA combination")
        self.report += "SBDARE with unallowable NATSUR/NATQUA combination [CHECK]"
        self.flagged_sbdare_with_natsur_natqua = self._hcell_sbdare(sbdare_points)

        coalne = S57Aux.select_by_object(self.all_features, ['COALNE', ])

        self.progress.add(quantum=1, text="COALNE missing mandatory attribute CATCOA")
        self.report += "COALNE missing mandatory attribute CATCOA [CHECK]"
        self.flagged_coalne_missing_catcoa = self._check_features_for_attribute(objects=coalne,
                                                                                attribute='CATCOA')

        self.progress.add(quantum=1, text="COALNE with prohibited attribute ELEVAT")
        self.report += "COALNE with prohibited attribute ELEVAT [CHECK]"
        self.flagged_coalne_with_elevat = self._check_features_no_attribute(objects=coalne,
                                                                            attribute='ELEVAT')

        slcons = S57Aux.select_by_object(self.all_features, ['SLCONS', ])

        self.progress.add(quantum=1, text="SLCONS missing mandatory attribute CATSLC")
        self.report += "SLCONS missing mandatory attribute CATSLC [CHECK]"
        self.flagged_slcons_missing_catslc = self._check_features_for_attribute(objects=slcons,
                                                                                attribute='CATSLC')

        mqual = S57Aux.select_by_object(self.all_features, ['M_QUAL', ])

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute CATZOC")
        self.report += "M_QUAL missing mandatory attribute CATZOC [CHECK]"
        self.flagged_m_qual_missing_catzoc = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='CATZOC')

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute TECSOU")
        self.report += "M_QUAL missing mandatory attribute TECSOU [CHECK]"
        self.flagged_m_qual_missing_tecsou = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='TECSOU')

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute SURSTA")
        self.report += "M_QUAL missing mandatory attribute SURSTA [CHECK]"
        self.flagged_m_qual_missing_sursta = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='SURSTA')

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute SUREND")
        self.report += "M_QUAL missing mandatory attribute SUREND [CHECK]"
        self.flagged_m_qual_missing_surend = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='SUREND')

        mcscl = S57Aux.select_by_object(self.all_features, ['M_CSCL'])

        self.progress.add(quantum=1, text="M_CSCL missing mandatory attribute CSCALE")
        self.report += "M_CSCL missing mandatory attribute CSCALE [CHECK]"
        self.flagged_m_cscl_missing_cscale = self._check_features_for_attribute(objects=mcscl,
                                                                                attribute='CSCALE')
        # @ added requirement that M_COVR has CATCOV
        mcovr = S57Aux.select_by_object(self.all_features, ['M_COVR'])

        self.progress.add(quantum=1, text="M_COVR missing mandatory attribute CATCOV")
        self.report += "M_COVR missing mandatory attribute CATCOV [CHECK]"
        self.flagged_m_covr_missing_catcov = self._check_features_for_attribute(objects=mcovr,
                                                                                attribute='CATCOV')

        carto_objects = S57Aux.select_by_object(self.all_features, ['$CSYMB', '$AREAS', '$LINES', ])

        self.progress.add(quantum=1, text="Cartographic object(s) missing mandatory object NINFOM")
        self.report += "Cartographic object(s) missing mandatory object NINFOM [CHECK]"
        self.flagged_carto_missing_ninfom = self._check_features_for_attribute(objects=carto_objects,
                                                                               attribute='NINFOM')

        self.progress.add(quantum=1, text="Cartographic object(s) missing mandatory object NTXTDS")
        self.report += "Cartographic object(s) missing mandatory object NTXTDS [CHECK]"
        self.flagged_carto_missing_ntxtds = self._check_features_for_attribute(objects=carto_objects,
                                                                               attribute='NTXTDS')

        self.progress.add(quantum=1, text="Feature(s) with NOAA extended attributes (clear before final submission)")
        self.report += "Feature(s) with NOAA extended attributes (clear before final submission) [CHECK]"

        self.flagged_noaa_extended = self._check_for_extended_attributes()

        # finalize the summary
        self.finalize_summary()

    def _run_2016(self):
        """2016 checks"""
        logger.debug('checking against specs version: %s' % self.version)

        # PRE-PROCESSING: retrieve soundings for features and SS

        self.progress.add(quantum=2, text="Retrieve soundings from features")
        self.all_cs = S57Aux.select_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        logger.debug('%d soundings in features' % len(self.all_cs))

        if self.all_ss:
            self.progress.add(quantum=2, text="Retrieve soundings from SS")
            self.all_ss = S57Aux.select_by_object(objects=self.all_ss, object_filter=['SOUNDG', ])
            logger.debug('%d soundings in SS' % len(self.all_ss))

        # CHECK REDUNDANCY

        self.progress.add(quantum=2, text="Feature redundancy check")
        self.report += "Redundant features [CHECK]"
        logger.warning("report: %s" % self.report)
        self.all_features = self._check_feature_redundancy()

        if self.all_cs:
            self.progress.add(quantum=2, text="CS redundancy check")
            self.report += "Redundant CS [CHECK]"
            self.all_cs = self._check_cs_redundancy()  # + build CS dict
        else:
            self.report += "Redundant CS [SKIP_CHK]"
            self.flagged_cs_redundancy = -1

        if self.all_ss:
            self.progress.add(quantum=2, text="SS redundancy check")
            self.report += "Redundant SS [CHECK]"
            self.all_ss = self._check_ss_redundancy()  # + build SS dict
        else:
            self.report += "Redundant SS [SKIP_CHK]"
            self.flagged_ss_redundancy = -1

        # (OPTIONAL) CHECK: CS subset of SS

        if self.all_ss and self.all_cs:
            self.progress.add(quantum=2, text="CS subset of SS check")
            self.report += "CS subset of SS [CHECK]"
            self.flagged_cs_in_ss = self._check_cs_in_ss()
        else:
            self.report += "CS subset of SS [SKIP_CHK]"
            self.flagged_cs_in_ss = -1

        # CHECKS: valsous in SS, but not in CS

        if self.all_ss or self.all_cs:  # to avoid useless computations
            features = self._get_features_from_s57_no_extended()
        else:
            features = list()

        if self.all_ss:
            self.progress.add(quantum=2, text="VALSOUs in SS check")
            self.report += "VALSOUs subset of SS [CHECK]"
            self.flagged_valsou_in_ss = self._check_valsou_in_ss(features=features)
        else:
            self.report += "VALSOUs subset of SS [SKIP_CHK]"
            self.flagged_valsou_in_ss = -1

        if self.all_cs:
            self.progress.add(quantum=2, text="VALSOUs not in CS check")
            self.report += "VALSOUs not subset of CS [CHECK]"
            self.flagged_valsou_not_in_cs = self._check_valsou_not_in_cs(features=features)
        else:
            self.report += "VALSOUs not subset of CS [SKIP_CHK]"
            self.flagged_valsou_not_in_cs = -1

        # ATTRIBUTE CHECKS:

        self.progress.add(quantum=1, text="Feature(s) with prohibited attribute SCAMIN")
        self.report += "Feature(s) with prohibited attribute SCAMIN [CHECK]"
        self.flagged_prohibited_scamin = self._check_features_no_attribute(objects=self.all_features,
                                                                           attribute='SCAMIN')

        self.progress.add(quantum=1, text="Feature(s) with prohibited attribute RECDAT")
        self.report += "Feature(s) with prohibited attribute RECDAT [CHECK]"
        self.flagged_prohibited_recdat = self._check_features_no_attribute(objects=self.all_features,
                                                                           attribute='RECDAT')

        self.progress.add(quantum=1, text="Feature(s) with prohibited attribute VERDAT")
        self.report += "Feature(s) with prohibited attribute VERDAT [CHECK]"
        self.flagged_prohibited_verdat = self._check_features_no_attribute(objects=self.all_features,
                                                                           attribute='VERDAT')
        # @ removed LNDARE, DEPARE, and DEPCNT from SORIND and SORDAT check per 2016 spec        
        feature_objects = S57Aux.filter_by_object(objects=self.all_features,
                                                  object_filter=['$AREAS', '$LINES', '$CSYMB', '$COMPS', '$TEXTS',
                                                                 'LNDARE', 'DEPARE', 'DEPCNT'])
        new_update_features = S57Aux.select_by_attribute_value(objects=feature_objects, attribute='descrp',
                                                               value_filter=['1', '2', ])

        self.progress.add(quantum=1, text="New/updated feature(s) with mandatory attribute SORIND")
        self.report += "New/updated feature(s) with mandatory attribute SORIND [CHECK]"
        self.flagged_mandatory_sorind = self._check_features_for_attribute(objects=new_update_features,
                                                                           attribute='SORIND')

        self.progress.add(quantum=1, text="New/updated feature(s) with invalid attribute SORIND")
        self.report += "New/updated feature(s) with invalid attribute SORIND [CHECK]"
        self.flagged_invalid_sorind = self._check_features_for_valid_sorind(objects=new_update_features)

        self.progress.add(quantum=1, text="New/updated feature(s) missing mandatory attribute SORDAT")
        self.report += "New/updated feature(s) missing mandatory attribute SORDAT [CHECK]"
        self.flagged_missing_sordat = self._check_features_for_attribute(objects=new_update_features,
                                                                         attribute='SORDAT')

        self.progress.add(quantum=1, text="New/updated feature(s) with invalid attribute SORDAT")
        self.report += "New/udpated feature(s) with invalid attribute SORDAT [CHECK]"
        self.flagged_invalid_sordat = self._check_features_for_valid_sordat(objects=new_update_features)

        # @ ninfom requirement no longer exists, so the ninfom check was removed

        # > Are we sure about this? If you can to the original code there is not SOUNDG, but all the features
        # @ confirmed, this is correct. STATUS is prohibited for SOUNDG.
        self.progress.add(quantum=1, text="SOUNDG with prohibited attribute STATUS")
        self.report += "SOUNDG with prohibited attribute STATUS [CHECK]"
        self.flagged_soundg_with_status = self._check_features_no_attribute(objects=self.all_cs,
                                                                            attribute='STATUS')

        # wreck specific

        wrecks = S57Aux.select_by_object(self.all_features, ['WRECKS', ])

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute CATWRK")
        self.report += "WRECKS missing mandatory attribute CATWRK [CHECK]"
        self.flagged_wrecks_missing_catwrk = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='CATWRK')

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute WATLEV")
        self.report += "WRECKS missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_missing_watlev = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='WATLEV')

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute VALSOU")
        self.report += "WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_missing_valsou = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='VALSOU')

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute QUASOU")
        self.report += "WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_missing_quasou = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='QUASOU')

        awash_wrecks = S57Aux.select_by_attribute_value(wrecks, 'WATLEV', [5])

        self.progress.add(quantum=1, text="Awash WRECKS missing mandatory attribute EXPSOU")
        self.report += "Awash WRECKS missing mandatory attribute EXPSOU [CHECK]"
        self.flagged_awash_wrecks_missing_expsou = self._check_features_for_attribute(objects=awash_wrecks,
                                                                                      attribute='EXPSOU')

        # rock-specific

        rocks = S57Aux.select_by_object(self.all_features, ['UWTROC', ])

        self.progress.add(quantum=1, text="UWTROC missing mandatory attribute VALSOU")
        self.report += "UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_missing_valsou = self._check_features_for_attribute(objects=rocks,
                                                                                attribute='VALSOU')

        self.progress.add(quantum=1, text="UWTROC missing mandatory attribute WATLEV")
        self.report += "UWTROC missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_missing_watlev = self._check_features_for_attribute(objects=rocks,
                                                                                attribute='WATLEV')

        self.progress.add(quantum=1, text="UWTROC missing mandatory attribute QUASOU")
        self.report += "UWTROC missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_missing_quasou = self._check_features_for_attribute(objects=rocks,
                                                                                attribute='QUASOU')

        # obstruction-specific

        obstructions = S57Aux.select_by_object(self.all_features, ['OBSTRN', ])

        self.progress.add(quantum=1, text="OBSTRN missing mandatory attribute VALSOU")
        self.report += "OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_missing_valsou = self._check_features_for_attribute(objects=obstructions,
                                                                                attribute='VALSOU')

        self.progress.add(quantum=1, text="OBSTRN missing mandatory attribute WATLEV")
        self.report += "OBSTRN missing mandatory attribute WATLEV [CHECK]"
        self.flagged_obstrn_missing_watlev = self._check_features_for_attribute(objects=obstructions,
                                                                                attribute='WATLEV')

        self.progress.add(quantum=1, text="OBSTRN missing mandatory attribute QUASOU")
        self.report += "OBSTRN missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_missing_quasou = self._check_features_for_attribute(objects=obstructions,
                                                                                attribute='QUASOU')

        # @ check for no foul area obstructions removed

        # more

        morfac = S57Aux.select_by_object(self.all_features, ['MORFAC', ])
        self.progress.add(quantum=1, text="MORFAC missing mandatory attribute CATMOR")
        self.report += "MORFAC missing mandatory attribute CATMOR [CHECK]"
        self.flagged_morfac_missing_catmor = self._check_features_for_attribute(objects=morfac,
                                                                                attribute='CATMOR')

        # @ added additional attributes prohibited for MORFAC
        self.progress.add(quantum=1, text="MORFAC with prohibited attribute BOYSHP")
        self.report += "MORFAC with prohibited attribute BOYSHP [CHECK]"
        self.flagged_morfac_prohibited_boyshp = self._check_features_no_attribute(objects=morfac,
                                                                                  attribute='BOYSHP')

        self.progress.add(quantum=1, text="MORFAC with prohibited attribute COLOUR")
        self.report += "MORFAC with prohibited attribute COLOUR [CHECK]"
        self.flagged_morfac_prohibited_colour = self._check_features_no_attribute(objects=morfac,
                                                                                  attribute='COLOUR')

        self.progress.add(quantum=1, text="MORFAC with prohibited attribute COLPAT")
        self.report += "MORFAC with prohibited attribute COLPAT [CHECK]"
        self.flagged_morfac_prohibited_colpat = self._check_features_no_attribute(objects=morfac,
                                                                                  attribute='COLPAT')

        sbdare = S57Aux.select_by_object(self.all_features, ['SBDARE', ])
        sbdare_points = S57Aux.select_only_points(sbdare)

        self.progress.add(quantum=1, text="SBDARE missing mandatory attribute NATSUR")
        self.report += "SBDARE missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_missing_natsur = self._check_features_for_attribute(objects=sbdare_points,
                                                                                attribute='NATSUR')

        self.progress.add(quantum=1, text="SBDARE with prohibited attribute COLOUR")
        self.report += "SBDARE with prohibited attribute COLOUR [CHECK]"
        self.flagged_sbdare_with_colour = self._check_features_no_attribute(objects=sbdare_points,
                                                                            attribute='COLOUR')

        self.progress.add(quantum=1, text="SBDARE with prohibited attribute WATLEV")
        self.report += "SBDARE with prohibited attribute WATLEV [CHECK]"
        self.flagged_sbdare_with_watlev = self._check_features_no_attribute(objects=sbdare_points,
                                                                            attribute='WATLEV')

        self.progress.add(quantum=1, text="SBDARE with unallowable NATSUR/NATQUA combination")
        self.report += "SBDARE with unallowable NATSUR/NATQUA combination [CHECK]"
        self.flagged_sbdare_with_natsur_natqua = self._hcell_sbdare(sbdare_points)

        # @ additional requirements for line and area SBDARE objects
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)

        self.progress.add(quantum=1, text="SBDARE lines or areas missing mandatory attribute NATSUR")
        self.report += "SBDARE lines or areas missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_la_missing_natsur = self._check_features_for_attribute(objects=sbdare_lines_areas,
                                                                                   attribute='NATSUR')

        self.progress.add(quantum=1, text="SBDARE lines or areas missing mandatory attribute WATLEV")
        self.report += "SBDARE lines or areas possibly missing mandatory attribute WATLEV [CHECK]"
        self.flagged_sbdare_la_missing_watlev = self._check_features_for_attribute(objects=sbdare_lines_areas,
                                                                                   attribute='WATLEV', possible=True)

        coalne = S57Aux.select_by_object(self.all_features, ['COALNE', ])

        self.progress.add(quantum=1, text="COALNE missing mandatory attribute CATCOA")
        self.report += "COALNE missing mandatory attribute CATCOA [CHECK]"
        self.flagged_coalne_missing_catcoa = self._check_features_for_attribute(objects=coalne,
                                                                                attribute='CATCOA')

        self.progress.add(quantum=1, text="COALNE with prohibited attribute ELEVAT")
        self.report += "COALNE with prohibited attribute ELEVAT [CHECK]"
        self.flagged_coalne_with_elevat = self._check_features_no_attribute(objects=coalne,
                                                                            attribute='ELEVAT')

        # @ additional requirement given for CTNARE

        ctnare = S57Aux.select_by_object(self.all_features, ['CTNARE', ])

        self.progress.add(quantum=1, text="CTNARE missing mandatory attribute INFORM")
        self.report += "CTNARE missing mandatory attribute INFORM [CHECK]"
        self.flagged_ctnare_missing_inform = self._check_features_for_attribute(objects=ctnare,
                                                                                attribute='INFORM')

        slcons = S57Aux.select_by_object(self.all_features, ['SLCONS', ])

        self.progress.add(quantum=1, text="SLCONS missing mandatory attribute CATSLC")
        self.report += "SLCONS missing mandatory attribute CATSLC [CHECK]"
        self.flagged_slcons_missing_catslc = self._check_features_for_attribute(objects=slcons,
                                                                                attribute='CATSLC')

        mqual = S57Aux.select_by_object(self.all_features, ['M_QUAL', ])

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute CATZOC")
        self.report += "M_QUAL missing mandatory attribute CATZOC [CHECK]"
        self.flagged_m_qual_missing_catzoc = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='CATZOC')

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute TECSOU")
        self.report += "M_QUAL missing mandatory attribute TECSOU [CHECK]"
        self.flagged_m_qual_missing_tecsou = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='TECSOU')

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute SURSTA")
        self.report += "M_QUAL missing mandatory attribute SURSTA [CHECK]"
        self.flagged_m_qual_missing_sursta = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='SURSTA')

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute SUREND")
        self.report += "M_QUAL missing mandatory attribute SUREND [CHECK]"
        self.flagged_m_qual_missing_surend = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='SUREND')

        mcscl = S57Aux.select_by_object(self.all_features, ['M_CSCL'])

        self.progress.add(quantum=1, text="M_CSCL missing mandatory attribute CSCALE")
        self.report += "M_CSCL missing mandatory attribute CSCALE [CHECK]"
        self.flagged_m_cscl_missing_cscale = self._check_features_for_attribute(objects=mcscl,
                                                                                attribute='CSCALE')

        mcovr = S57Aux.select_by_object(self.all_features, ['M_COVR'])

        self.progress.add(quantum=1, text="M_COVR missing mandatory attribute CATCOV")
        self.report += "M_COVR missing mandatory attribute CATCOV [CHECK]"
        self.flagged_m_covr_missing_catcov = self._check_features_for_attribute(objects=mcovr,
                                                                                attribute='CATCOV')

        carto_objects = S57Aux.select_by_object(self.all_features, ['$CSYMB', '$AREAS', '$LINES', ])

        # @ NINFOM and NTXTDS requirement removed for carto objects and replaced with only INFORM

        self.progress.add(quantum=1, text="Cartographic object(s) missing mandatory object INFORM")
        self.report += "Cartographic object(s) missing mandatory object INFORM [CHECK]"
        self.flagged_carto_missing_inform = self._check_features_for_attribute(objects=carto_objects,
                                                                               attribute='INFORM')

        self.progress.add(quantum=1, text="Feature(s) with NOAA extended attributes (clear before final submission)")
        self.report += "Feature(s) with NOAA extended attributes (clear before final submission) [CHECK]"

        self.flagged_noaa_extended = self._check_for_extended_attributes()

        # finalize the summary
        self.finalize_summary()

    def _run_2018(self):
        """anticipated 2018 checks"""
        logger.debug('checking against specs version: %s' % self.version)

        # PRE-PROCESSING: retrieve soundings for features and SS

        self.progress.add(quantum=2, text="Retrieve soundings from features")
        self.all_cs = S57Aux.select_by_object(objects=self.all_features, object_filter=['SOUNDG', ])
        logger.debug('%d soundings in features' % len(self.all_cs))

        if self.all_ss:
            self.progress.add(quantum=2, text="Retrieve soundings from SS")
            self.all_ss = S57Aux.select_by_object(objects=self.all_ss, object_filter=['SOUNDG', ])
            logger.debug('%d soundings in SS' % len(self.all_ss))

        # CHECK REDUNDANCY

        self.progress.add(quantum=2, text="Feature redundancy check")
        self.report += "Redundant features [CHECK]"
        self.all_features = self._check_feature_redundancy()

        if self.all_cs:
            self.progress.add(quantum=2, text="CS redundancy check")
            self.report += "Redundant CS [CHECK]"
            self.all_cs = self._check_cs_redundancy()  # + build CS dict
        else:
            self.report += "Redundant CS [SKIP_CHK]"
            self.flagged_cs_redundancy = -1

        if self.all_ss:
            self.progress.add(quantum=2, text="SS redundancy check")
            self.report += "Redundant SS [CHECK]"
            self.all_ss = self._check_ss_redundancy()  # + build SS dict
        else:
            self.report += "Redundant SS [SKIP_CHK]"
            self.flagged_ss_redundancy = -1

        # (OPTIONAL) CHECK: CS subset of SS

        if self.all_ss and self.all_cs:
            self.progress.add(quantum=2, text="CS subset of SS check")
            self.report += "CS subset of SS [CHECK]"
            self.flagged_cs_in_ss = self._check_cs_in_ss()
        else:
            self.report += "CS subset of SS [SKIP_CHK]"
            self.flagged_cs_in_ss = -1

        # CHECKS: valsous in SS, but not in CS

        if self.all_ss or self.all_cs:  # to avoid useless computations
            features = self._get_features_from_s57_no_extended()
        else:
            features = list()

        if self.all_ss:
            self.progress.add(quantum=2, text="VALSOUs in SS check")
            self.report += "VALSOUs subset of SS [CHECK]"
            self.flagged_valsou_in_ss = self._check_valsou_in_ss(features=features)
        else:
            self.report += "VALSOUs subset of SS [SKIP_CHK]"
            self.flagged_valsou_in_ss = -1

        if self.all_cs:
            self.progress.add(quantum=2, text="VALSOUs not in CS check")
            self.report += "VALSOUs not subset of CS [CHECK]"
            self.flagged_valsou_not_in_cs = self._check_valsou_not_in_cs(features=features)
        else:
            self.report += "VALSOUs not subset of CS [SKIP_CHK]"
            self.flagged_valsou_not_in_cs = -1

        # ATTRIBUTE CHECKS:

        self.progress.add(quantum=1, text="Feature(s) with prohibited attribute SCAMIN")
        self.report += "Feature(s) with prohibited attribute SCAMIN [CHECK]"
        self.flagged_prohibited_scamin = self._check_features_no_attribute(objects=self.all_features,
                                                                           attribute='SCAMIN')

        self.progress.add(quantum=1, text="Feature(s) with prohibited attribute RECDAT")
        self.report += "Feature(s) with prohibited attribute RECDAT [CHECK]"
        self.flagged_prohibited_recdat = self._check_features_no_attribute(objects=self.all_features,
                                                                           attribute='RECDAT')

        self.progress.add(quantum=1, text="Feature(s) with prohibited attribute VERDAT")
        self.report += "Feature(s) with prohibited attribute VERDAT [CHECK]"
        self.flagged_prohibited_verdat = self._check_features_no_attribute(objects=self.all_features,
                                                                           attribute='VERDAT')
        # @ removed LNDARE, DEPARE, and DEPCNT from SORIND and SORDAT check per 2016 spec        
        feature_objects = S57Aux.filter_by_object(objects=self.all_features,
                                                  object_filter=['$AREAS', '$LINES', '$CSYMB', '$COMPS', '$TEXTS',
                                                                 'LNDARE', 'DEPARE', 'DEPCNT'])
        new_update_features = S57Aux.select_by_attribute_value(objects=feature_objects, attribute='descrp',
                                                               value_filter=['1', '2', ])

        self.progress.add(quantum=1, text="New/updated feature(s) with mandatory attribute SORIND")
        self.report += "New/updated feature(s) with mandatory attribute SORIND [CHECK]"
        self.flagged_mandatory_sorind = self._check_features_for_attribute(objects=new_update_features,
                                                                           attribute='SORIND')

        self.progress.add(quantum=1, text="New/updated feature(s) with invalid attribute SORIND")
        self.report += "New/updated feature(s) with invalid attribute SORIND [CHECK]"
        self.flagged_invalid_sorind = self._check_features_for_valid_sorind(objects=new_update_features)

        self.progress.add(quantum=1, text="New/updated feature(s) missing mandatory attribute SORDAT")
        self.report += "New/updated feature(s) missing mandatory attribute SORDAT [CHECK]"
        self.flagged_missing_sordat = self._check_features_for_attribute(objects=new_update_features,
                                                                         attribute='SORDAT')

        self.progress.add(quantum=1, text="New/updated feature(s) with invalid attribute SORDAT")
        self.report += "New/udpated feature(s) with invalid attribute SORDAT [CHECK]"
        self.flagged_invalid_sordat = self._check_features_for_valid_sordat(objects=new_update_features)

        # @ ninfom requirement no longer exists, so the ninfom check was removed

        # > Are we sure about this? If you can to the original code there is not SOUNDG, but all the features
        # @ confirmed, this is correct. STATUS is prohibited for SOUNDG.
        self.progress.add(quantum=1, text="SOUNDG with prohibited attribute STATUS")
        self.report += "SOUNDG with prohibited attribute STATUS [CHECK]"
        self.flagged_soundg_with_status = self._check_features_no_attribute(objects=self.all_cs,
                                                                            attribute='STATUS')

        # wreck specific

        wrecks = S57Aux.select_by_object(self.all_features, ['WRECKS', ])

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute CATWRK")
        self.report += "WRECKS missing mandatory attribute CATWRK [CHECK]"
        self.flagged_wrecks_missing_catwrk = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='CATWRK')

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute WATLEV")
        self.report += "WRECKS missing mandatory attribute WATLEV [CHECK]"
        self.flagged_wrecks_missing_watlev = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='WATLEV')

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute VALSOU")
        self.report += "WRECKS missing mandatory attribute VALSOU [CHECK]"
        self.flagged_wrecks_missing_valsou = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='VALSOU')

        self.progress.add(quantum=1, text="WRECKS missing mandatory attribute QUASOU")
        self.report += "WRECKS missing mandatory attribute QUASOU [CHECK]"
        self.flagged_wrecks_missing_quasou = self._check_features_for_attribute(objects=wrecks,
                                                                                attribute='QUASOU')

        awash_wrecks = S57Aux.select_by_attribute_value(wrecks, 'WATLEV', [5])

        self.progress.add(quantum=1, text="Awash WRECKS missing mandatory attribute EXPSOU")
        self.report += "Awash WRECKS missing mandatory attribute EXPSOU [CHECK]"
        self.flagged_awash_wrecks_missing_expsou = self._check_features_for_attribute(objects=awash_wrecks,
                                                                                      attribute='EXPSOU')

        # rock-specific

        rocks = S57Aux.select_by_object(self.all_features, ['UWTROC', ])

        self.progress.add(quantum=1, text="UWTROC missing mandatory attribute VALSOU")
        self.report += "UWTROC missing mandatory attribute VALSOU [CHECK]"
        self.flagged_uwtroc_missing_valsou = self._check_features_for_attribute(objects=rocks,
                                                                                attribute='VALSOU')

        self.progress.add(quantum=1, text="UWTROC missing mandatory attribute WATLEV")
        self.report += "UWTROC missing mandatory attribute WATLEV [CHECK]"
        self.flagged_uwtroc_missing_watlev = self._check_features_for_attribute(objects=rocks,
                                                                                attribute='WATLEV')

        self.progress.add(quantum=1, text="UWTROC missing mandatory attribute QUASOU")
        self.report += "UWTROC missing mandatory attribute QUASOU [CHECK]"
        self.flagged_uwtroc_missing_quasou = self._check_features_for_attribute(objects=rocks,
                                                                                attribute='QUASOU')

        # obstruction-specific

        obstructions = S57Aux.select_by_object(self.all_features, ['OBSTRN', ])

        self.progress.add(quantum=1, text="OBSTRN missing mandatory attribute VALSOU")
        self.report += "OBSTRN missing mandatory attribute VALSOU [CHECK]"
        self.flagged_obstrn_missing_valsou = self._check_features_for_attribute(objects=obstructions,
                                                                                attribute='VALSOU')

        self.progress.add(quantum=1, text="OBSTRN missing mandatory attribute WATLEV")
        self.report += "OBSTRN missing mandatory attribute WATLEV [CHECK]"
        self.flagged_obstrn_missing_watlev = self._check_features_for_attribute(objects=obstructions,
                                                                                attribute='WATLEV')

        self.progress.add(quantum=1, text="OBSTRN missing mandatory attribute QUASOU")
        self.report += "OBSTRN missing mandatory attribute QUASOU [CHECK]"
        self.flagged_obstrn_missing_quasou = self._check_features_for_attribute(objects=obstructions,
                                                                                attribute='QUASOU')

        # @ check for no foul area obstructions removed

        # more

        morfac = S57Aux.select_by_object(self.all_features, ['MORFAC', ])
        self.progress.add(quantum=1, text="MORFAC missing mandatory attribute CATMOR")
        self.report += "MORFAC missing mandatory attribute CATMOR [CHECK]"
        self.flagged_morfac_missing_catmor = self._check_features_for_attribute(objects=morfac,
                                                                                attribute='CATMOR')

        # @ added additional attributes prohibited for MORFAC
        self.progress.add(quantum=1, text="MORFAC with prohibited attribute BOYSHP")
        self.report += "MORFAC with prohibited attribute BOYSHP [CHECK]"
        self.flagged_morfac_prohibited_boyshp = self._check_features_no_attribute(objects=morfac,
                                                                                  attribute='BOYSHP')

        self.progress.add(quantum=1, text="MORFAC with prohibited attribute COLOUR")
        self.report += "MORFAC with prohibited attribute COLOUR [CHECK]"
        self.flagged_morfac_prohibited_colour = self._check_features_no_attribute(objects=morfac,
                                                                                  attribute='COLOUR')

        self.progress.add(quantum=1, text="MORFAC with prohibited attribute COLPAT")
        self.report += "MORFAC with prohibited attribute COLPAT [CHECK]"
        self.flagged_morfac_prohibited_colpat = self._check_features_no_attribute(objects=morfac,
                                                                                  attribute='COLPAT')

        sbdare = S57Aux.select_by_object(self.all_features, ['SBDARE', ])
        sbdare_points = S57Aux.select_only_points(sbdare)

        self.progress.add(quantum=1, text="SBDARE missing mandatory attribute NATSUR")
        self.report += "SBDARE missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_missing_natsur = self._check_features_for_attribute(objects=sbdare_points,
                                                                                attribute='NATSUR')

        self.progress.add(quantum=1, text="SBDARE with prohibited attribute COLOUR")
        self.report += "SBDARE with prohibited attribute COLOUR [CHECK]"
        self.flagged_sbdare_with_colour = self._check_features_no_attribute(objects=sbdare_points,
                                                                            attribute='COLOUR')

        self.progress.add(quantum=1, text="SBDARE with prohibited attribute WATLEV")
        self.report += "SBDARE with prohibited attribute WATLEV [CHECK]"
        self.flagged_sbdare_with_watlev = self._check_features_no_attribute(objects=sbdare_points,
                                                                            attribute='WATLEV')

        self.progress.add(quantum=1, text="SBDARE with unallowable NATSUR/NATQUA combination")
        self.report += "SBDARE with unallowable NATSUR/NATQUA combination [CHECK]"
        self.flagged_sbdare_with_natsur_natqua = self._hcell_sbdare(sbdare_points)

        # @ additional requirements for line and area SBDARE objects
        sbdare_lines_areas = S57Aux.select_lines_and_areas(sbdare)

        self.progress.add(quantum=1, text="SBDARE lines or areas missing mandatory attribute NATSUR")
        self.report += "SBDARE lines or areas missing mandatory attribute NATSUR [CHECK]"
        self.flagged_sbdare_la_missing_natsur = self._check_features_for_attribute(objects=sbdare_lines_areas,
                                                                                   attribute='NATSUR')

        self.progress.add(quantum=1, text="SBDARE lines or areas missing mandatory attribute WATLEV")
        self.report += "SBDARE lines or areas missing mandatory attribute WATLEV [CHECK]"
        self.flagged_sbdare_la_missing_watlev = self._check_features_for_attribute(objects=sbdare_lines_areas,
                                                                                   attribute='WATLEV', possible=True)

        coalne = S57Aux.select_by_object(self.all_features, ['COALNE', ])

        self.progress.add(quantum=1, text="COALNE missing mandatory attribute CATCOA")
        self.report += "COALNE missing mandatory attribute CATCOA [CHECK]"
        self.flagged_coalne_missing_catcoa = self._check_features_for_attribute(objects=coalne,
                                                                                attribute='CATCOA')

        self.progress.add(quantum=1, text="COALNE with prohibited attribute ELEVAT")
        self.report += "COALNE with prohibited attribute ELEVAT [CHECK]"
        self.flagged_coalne_with_elevat = self._check_features_no_attribute(objects=coalne,
                                                                            attribute='ELEVAT')

        # @ additional requirement given for CTNARE

        ctnare = S57Aux.select_by_object(self.all_features, ['CTNARE', ])

        self.progress.add(quantum=1, text="CTNARE missing mandatory attribute INFORM")
        self.report += "CTNARE missing mandatory attribute INFORM [CHECK]"
        self.flagged_ctnare_missing_inform = self._check_features_for_attribute(objects=ctnare,
                                                                                attribute='INFORM')

        slcons = S57Aux.select_by_object(self.all_features, ['SLCONS', ])

        self.progress.add(quantum=1, text="SLCONS missing mandatory attribute CATSLC")
        self.report += "SLCONS missing mandatory attribute CATSLC [CHECK]"
        self.flagged_slcons_missing_catslc = self._check_features_for_attribute(objects=slcons,
                                                                                attribute='CATSLC')

        mqual = S57Aux.select_by_object(self.all_features, ['M_QUAL', ])

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute CATZOC")
        self.report += "M_QUAL missing mandatory attribute CATZOC [CHECK]"
        self.flagged_m_qual_missing_catzoc = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='CATZOC')

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute TECSOU")
        self.report += "M_QUAL missing mandatory attribute TECSOU [CHECK]"
        self.flagged_m_qual_missing_tecsou = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='TECSOU')

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute SURSTA")
        self.report += "M_QUAL missing mandatory attribute SURSTA [CHECK]"
        self.flagged_m_qual_missing_sursta = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='SURSTA')

        self.progress.add(quantum=1, text="M_QUAL missing mandatory attribute SUREND")
        self.report += "M_QUAL missing mandatory attribute SUREND [CHECK]"
        self.flagged_m_qual_missing_surend = self._check_features_for_attribute(objects=mqual,
                                                                                attribute='SUREND')

        mcscl = S57Aux.select_by_object(self.all_features, ['M_CSCL'])

        self.progress.add(quantum=1, text="M_CSCL missing mandatory attribute CSCALE")
        self.report += "M_CSCL missing mandatory attribute CSCALE [CHECK]"
        self.flagged_m_cscl_missing_cscale = self._check_features_for_attribute(objects=mcscl,
                                                                                attribute='CSCALE')

        mcovr = S57Aux.select_by_object(self.all_features, ['M_COVR'])

        self.progress.add(quantum=1, text="M_COVR missing mandatory attribute CATCOV")
        self.report += "M_COVR missing mandatory attribute CATCOV [CHECK]"
        self.flagged_m_covr_missing_catcov = self._check_features_for_attribute(objects=mcovr,
                                                                                attribute='CATCOV')

        carto_objects = S57Aux.select_by_object(self.all_features, ['$CSYMB', '$AREAS', '$LINES', ])

        # @ NINFOM and NTXTDS requirement removed for carto objects and replaced with only INFORM

        self.progress.add(quantum=1, text="Cartographic object(s) missing mandatory object INFORM")
        self.report += "Cartographic object(s) missing mandatory object INFORM [CHECK]"
        self.flagged_carto_missing_inform = self._check_features_for_attribute(objects=carto_objects,
                                                                               attribute='INFORM')

        self.progress.add(quantum=1, text="Feature(s) with NOAA extended attributes (clear before final submission)")
        self.report += "Feature(s) with NOAA extended attributes (clear before final submission) [CHECK]"

        self.flagged_noaa_extended = self._check_for_extended_attributes()

        # finalize the summary
        self.finalize_summary()

    def finalize_summary(self):
        """Add a summary to the report"""
        count = 1

        # Add a summary to the report
        self.report += 'SUMMARY [TOTAL]'

        self.report += 'Check %d - Redundant features: %s' % (count, len(self.flagged_feature_redundancy))
        count += 1

        if self.flagged_cs_redundancy == -1:
            self.report += 'Check %d - Redundant CS [SKIP_REP]' % count
        else:
            self.report += 'Check %d - Redundant CS: %s' % (count, len(self.flagged_cs_redundancy))
        count += 1

        if self.flagged_ss_redundancy == -1:
            self.report += 'Check %d - Redundant SS [SKIP_REP]' % count
        else:
            self.report += 'Check %d - Redundant SS: %s' % (count, len(self.flagged_ss_redundancy))
        count += 1

        if self.flagged_cs_in_ss == -1:
            self.report += 'Check %d - CS subset of SS [SKIP_REP]' % count
        else:
            self.report += 'Check %d - CS subset of SS: %s' % (count, len(self.flagged_cs_in_ss))
        count += 1

        if self.flagged_valsou_in_ss == -1:
            self.report += 'Check %d - VALSOUs subset of SS [SKIP_REP]' % count
        else:
            self.report += 'Check %d - VALSOUs subset of SS: %s' % (count, len(self.flagged_valsou_in_ss))
        count += 1

        if self.flagged_valsou_not_in_cs == -1:
            self.report += 'Check %d - VALSOUs not subset of CS [SKIP_REP]' % count
        else:
            self.report += 'Check %d - VALSOUs not subset of CS: %s' % (count, len(self.flagged_valsou_not_in_cs))
        count += 1

        # Features attributes

        self.report += 'Check %d - Feature(s) with prohibited attribute SCAMIN: %s' \
                       % (count, len(self.flagged_prohibited_scamin))
        count += 1

        self.report += 'Check %d - Feature(s) with prohibited attribute RECDAT: %s' \
                       % (count, len(self.flagged_prohibited_recdat))
        count += 1

        self.report += 'Check %d - Feature(s) with prohibited attribute VERDAT: %s' \
                       % (count, len(self.flagged_prohibited_verdat))
        count += 1

        self.report += 'Check %d - Feature(s) with mandatory attribute SORIND: %s' \
                       % (count, len(self.flagged_mandatory_sorind))
        count += 1

        self.report += 'Check %d - Feature(s) with invalid attribute SORIND: %s' \
                       % (count, len(self.flagged_invalid_sorind))
        count += 1

        self.report += 'Check %d - Feature(s) missing mandatory attribute SORDAT: %s' \
                       % (count, len(self.flagged_missing_sordat))
        count += 1

        self.report += 'Check %d - Feature(s) with invalid attribute SORDAT: %s' \
                       % (count, len(self.flagged_invalid_sordat))
        count += 1

        self.report += 'Check %d - Feature(s) missing mandatory attribute NINFOM: %s' \
                       % (count, len(self.flagged_missing_ninfom))
        count += 1

        self.report += 'Check %d - SOUNDG with prohibited attribute STATUS: %s' \
                       % (count, len(self.flagged_soundg_with_status))
        count += 1

        self.report += 'Check %d - WRECKS missing mandatory attribute CATWRK: %s' \
                       % (count, len(self.flagged_wrecks_missing_catwrk))
        count += 1

        self.report += 'Check %d - WRECKS missing mandatory attribute WATLEV: %s' \
                       % (count, len(self.flagged_wrecks_missing_watlev))
        count += 1

        self.report += 'Check %d - WRECKS missing mandatory attribute VALSOU: %s' \
                       % (count, len(self.flagged_wrecks_missing_valsou))
        count += 1

        self.report += 'Check %d - awash WRECKS missing mandatory attribute EXPSOU: %s' \
                       % (count, len(self.flagged_awash_wrecks_missing_expsou))
        count += 1

        self.report += 'Check %d - WRECKS missing mandatory attribute QUASOU: %s' \
                       % (count, len(self.flagged_wrecks_missing_quasou))
        count += 1

        self.report += 'Check %d - UWTROC missing mandatory attribute VALSOU: %s' \
                       % (count, len(self.flagged_uwtroc_missing_valsou))
        count += 1

        self.report += 'Check %d - UWTROC missing mandatory attribute WATLEV: %s' \
                       % (count, len(self.flagged_uwtroc_missing_watlev))
        count += 1

        self.report += 'Check %d - UWTROC missing mandatory attribute QUASOU: %s' \
                       % (count, len(self.flagged_uwtroc_missing_quasou))
        count += 1

        self.report += 'Check %d - OBSTRN missing mandatory attribute VALSOU: %s' \
                       % (count, len(self.flagged_obstrn_missing_valsou))
        count += 1

        self.report += 'Check %d - OBSTRN missing mandatory attribute WATLEV: %s' \
                       % (count, len(self.flagged_obstrn_missing_watlev))
        count += 1

        self.report += 'Check %d - OBSTRN missing mandatory attribute QUASOU: %s' \
                       % (count, len(self.flagged_obstrn_missing_quasou))
        count += 1

        self.report += 'Check %d - OBSTRN with CATOBS set to foul ground: %s' \
                       % (count, len(self.flagged_obstrn_with_catobs))
        count += 1

        self.report += 'Check %d - MORFAC missing mandatory attribute CATMOR: %s' \
                       % (count, len(self.flagged_morfac_missing_catmor))
        count += 1

        self.report += 'Check %d - MORFAC with prohibited attribute BOYSHP: %s' \
                       % (count, len(self.flagged_morfac_prohibited_boyshp))
        count += 1

        self.report += 'Check %d - MORFAC with prohibited attribute COLOUR: %s' \
                       % (count, len(self.flagged_morfac_prohibited_colour))
        count += 1

        self.report += 'Check %d - MORFAC with prohibited attribute COLPAT: %s' \
                       % (count, len(self.flagged_morfac_prohibited_colpat))
        count += 1

        self.report += 'Check %d - SBDARE points missing mandatory attribute NATSUR: %s' \
                       % (count, len(self.flagged_sbdare_missing_natsur))
        count += 1

        self.report += 'Check %d - SBDARE points with prohibited attribute COLOUR: %s' \
                       % (count, len(self.flagged_sbdare_with_colour))
        count += 1

        self.report += 'Check %d - SBDARE points with prohibited attribute WATLEV: %s' \
                       % (count, len(self.flagged_sbdare_with_watlev))
        count += 1

        self.report += 'Check %d - SBDARE with unallowable NATSUR/NATQUA combination: %s' \
                       % (count, len(self.flagged_sbdare_with_natsur_natqua))
        count += 1

        self.report += 'Check %d - SBDARE lines/areas missing mandatory attribute NATSUR: %s' \
                       % (count, len(self.flagged_sbdare_la_missing_natsur))
        count += 1

        self.report += 'Check %d - SBDARE lines/areas missing mandatory attribute WATLEV: %s' \
                       % (count, len(self.flagged_sbdare_la_missing_watlev))
        count += 1

        self.report += 'Check %d - COALNE missing mandatory attribute CATCOA: %s' \
                       % (count, len(self.flagged_coalne_missing_catcoa))
        count += 1

        self.report += 'Check %d - COALNE with prohibited attribute ELEVAT: %s' \
                       % (count, len(self.flagged_coalne_with_elevat))
        count += 1

        self.report += 'Check %d - CTNARE missing mandatory attribute INFORM: %s' \
                       % (count, len(self.flagged_ctnare_missing_inform))
        count += 1

        self.report += 'Check %d - SLCONS missing mandatory attribute CATSLC: %s' \
                       % (count, len(self.flagged_slcons_missing_catslc))
        count += 1

        self.report += 'Check %d - M_QUAL missing mandatory attribute CATZOC: %s' \
                       % (count, len(self.flagged_m_qual_missing_catzoc))
        count += 1

        self.report += 'Check %d - M_QUAL missing mandatory attribute TECSOU: %s' \
                       % (count, len(self.flagged_m_qual_missing_tecsou))
        count += 1

        self.report += 'Check %d - M_QUAL missing mandatory attribute SURSTA: %s' \
                       % (count, len(self.flagged_m_qual_missing_sursta))
        count += 1

        self.report += 'Check %d - M_QUAL missing mandatory attribute SUREND: %s' \
                       % (count, len(self.flagged_m_qual_missing_surend))
        count += 1

        self.report += 'Check %d - M_CSCL missing mandatory attribute CSCALE: %s' \
                       % (count, len(self.flagged_m_cscl_missing_cscale))
        count += 1

        self.report += 'Check %d - M_COVR missing mandatory attribute CATCOV: %s' \
                       % (count, len(self.flagged_m_covr_missing_catcov))
        count += 1

        self.report += 'Check %d - Cartographic object(s) missing mandatory object NINFOM: %s' \
                       % (count, len(self.flagged_carto_missing_ninfom))
        count += 1

        self.report += 'Check %d - Cartographic object(s) missing mandatory object NTXTDS: %s' \
                       % (count, len(self.flagged_carto_missing_ntxtds))
        count += 1

        self.report += 'Check %d - Cartographic object(s) missing mandatory object INFORM: %s' \
                       % (count, len(self.flagged_carto_missing_inform))
        count += 1

        self.report += 'Check %d - Feature(s) with NOAA extended attributes (clear before final submission): %s' \
                       % (count, len(self.flagged_noaa_extended))
        count += 1
