import numpy as np
import warnings
import warnings

import numpy as np

warnings.simplefilter(action="ignore", category=RuntimeWarning)
from osgeo import osr
import logging
logger = logging.getLogger(__name__)

from hyo2.qc.survey.designated.base_designated import BaseDesignated, designated_algos
from hyo2.qc.common.s57_aux import S57Aux
from hyo2.grids.common.gdal_aux import GdalAux


class DesignatedScanV2(BaseDesignated):

    # setting dictionary: X.X resolution : (number of nodes, delta depth threshold)
    settings = {
        0.5: (8, 1.0),
        1.0: (6, 1.0),
        2.0: (4, 1.0),
        4.0: (3, 1.0)
    }

    def __init__(self, s57, grids, survey_scale, neighborhood=False, specs="2017"):

        super().__init__(s57=s57, grids=grids)
        # inputs
        self.neighborhood = neighborhood
        self.survey_scale = survey_scale
        self.specs = specs

        self.type = designated_algos["DESIGNATED_SCAN_v2"]
        self.designated = list()
        self.loc2geo = None
        self.geo2loc = None
        self.all_features = self.s57.rec10s

        self.fff_features = list()
        self.fff_geo = None
        self.fff_utm = None
        self.fff_closest = None

    def run(self, depth_precision=3):
        logger.info("parameters: neighborhood: %s" % self.neighborhood)
        logger.debug("all S57 features: %d" % len(self.all_features))

        if self.specs == "2017":
            depth_precision = 2

        # test distance used to horizontally flag
        test_dist = self.survey_scale * 0.002
        logger.info("test distance at scale 1:%d: %.2f m" % (self.survey_scale, test_dist))

        # neighborhood-based test
        test_radius = 0
        test_threshold = 0.0
        if self.neighborhood:

            test_radius = 4
            test_threshold = 1.0
            for res in self.settings.keys():

                if res == self.grids.bbox().transform[1]:
                    test_radius = self.settings[res][0]
                    test_threshold = self.settings[res][1]

            logger.debug('neighborhood test @ %.1f-m resolution: radius: %d, threshold: %.1f m'
                         % (self.grids.bbox().transform[1], test_radius, test_threshold))

        # the heavy-lifting is done in C++
        success = self.grids.test_designated_soundings(test_dist, test_radius, test_threshold, self.specs)
        if not success:
            if self.grids.designated.empty():
                raise RuntimeError("not designated soundings in the input grid: %s." % self.grids.basename())
            return False

        # store the coordinate transform from CSAR CRS to geo (using GDAL)
        GdalAux.check_gdal_data()

        try:
            osr_bag = osr.SpatialReference()
            osr_bag.ImportFromWkt(self.grids.bbox().hrs)
            osr_geo = osr.SpatialReference()
            osr_geo.ImportFromEPSG(4326)  # geographic WGS84
            osr_geo.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            self.loc2geo = osr.CoordinateTransformation(osr_bag, osr_geo)
            # geo2loc = osr.CoordinateTransformation(osr_geo, osr_bag)

        except Exception as e:
            raise RuntimeError("unable to create a valid coords transform: %s" % e)

        # select all the features of interest
        self._select_features()
        if len(self.fff_features) == 0:
            logger.warning("no FFF features to check!")
        else:
            self._convert_features_to_array_coords(depth_precision=depth_precision)

        for idx, des in enumerate(self.grids.designated):

            if des.valid:
                continue

            match = False
            for sample in self.fff_closest:
                # logger.debug("sample: %s" % (sample, ))
                if (abs(sample[1] - des.r) <= 1) and (abs(sample[0] - des.c) <= 1) and \
                        (abs(sample[2] - des.designated_depth) <= 0.01):
                    match = True
                    break
            if match:
                logger.debug("#%d: removing flag because of FFF feature match" % idx)
                continue

            logger.debug("#%d: designated: %s -> valid: %s" % (idx, des.str(), des.valid))
            self._append_flagged(x=des.x, y=des.y, note=des.note)

    def _select_features(self):
        """ Select the required VALSOUs"""

        # first select all the feature of interest

        # select by feature type
        fff_filter = ['WRECKS', 'UWTROC', 'OBSTRN']
        fff_features = S57Aux.select_by_object(objects=self.all_features, object_filter=fff_filter)

        # select by geometry
        fff_features = S57Aux.select_only_points(objects=fff_features)

        # select only “description=new or update”
        self.fff_features = S57Aux.select_by_attribute_value(objects=fff_features, attribute='descrp',
                                                             value_filter=['1', '2'])

    def _convert_features_to_array_coords(self, depth_precision):
        # prepare some lists with:
        # - the geographic position of the features (self.fff_geo)
        # - the local (projected) position of the features (self.fff_loc)
        # - the array-base coords of the features (self.fff_array)
        # - the closest array nodes for each feature (self.fff_closest)

        logger.debug("converting FFF features to array coords ...")

        # first retrieve [long, lat, depth]
        self.fff_geo = list()
        for feature in self.fff_features:

            # retrieve depth value
            s57_valsou = None
            for attr in feature.attributes:

                if attr.acronym == 'VALSOU':
                    try:
                        # invert sign due to the CSAR/BAG convention (depths are negative)
                        s57_valsou = -float(attr.value)
                        # logger.debug("VALSOU value: %f" % s57_valsou)
                    except Exception as e:
                        logger.warning("issue in converting value: %s (%s %s) -> unknown VALSOU?" %
                                       (attr.value, feature.centroid.x, feature.centroid.y))
                    continue

            if s57_valsou is None:
                continue

            # append [long, lat, depth]
            self.fff_geo.append([feature.centroid.x, feature.centroid.y, s57_valsou])
        # logger.debug("lon, lat, d: %s" % self.fff_geo)

        # store the coordinate transform from CSAR CRS to geo (using GDAL)
        try:
            osr_grid = osr.SpatialReference()
            # logger.debug("cur_grids: %s" % self.grids.cur_grids)
            osr_grid.ImportFromWkt(self.grids.bbox().hrs)
            osr_geo = osr.SpatialReference()
            osr_geo.ImportFromEPSG(4326)  # geographic WGS84
            osr_geo.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            # self.loc2geo = osr.CoordinateTransformation(osr_bag, osr_geo)
            self.geo2loc = osr.CoordinateTransformation(osr_geo, osr_grid)

        except Exception as e:
            raise RuntimeError("unable to create a valid coords transform: %s" % e)

        # convert s57 features to grid CRS coords
        self.fff_utm = np.array(self.geo2loc.TransformPoints(np.array(self.fff_geo, np.float64)),
                                np.float64)
        # logger.debug("x, y, z: %s" % self.fff_loc)

        # convert feature to array coords
        fff_array = np.copy(self.fff_utm)
        fff_array[:, 0] = (self.fff_utm[:, 0] - self.grids.bbox().transform[0]) \
                          / self.grids.bbox().transform[1] - 0.5
        fff_array[:, 1] = (self.fff_utm[:, 1] - self.grids.bbox().transform[3]) \
                          / self.grids.bbox().transform[5] - 0.5
        # logger.debug("array: %s" % self.fff_array)

        # convert to the closest array coordinates
        self.fff_closest = np.empty_like(fff_array)
        self.fff_closest[:, 0] = np.rint(fff_array[:, 0])
        self.fff_closest[:, 1] = np.rint(fff_array[:, 1])
        self.fff_closest[:, 2] = np.around(fff_array[:, 2], decimals=depth_precision)
        # logger.debug("closest: %s" % self.valsou_closest)

        logger.debug("converting FFF features to array coords ... DONE! (%d)" % len(self.fff_closest))

    def _append_flagged(self, x, y, note):

        # convert flagged nodes to geographic coords
        try:

            long, lat, _ = self.loc2geo.TransformPoint(x, y)

            self.flagged_designated[0].append(long)
            self.flagged_designated[1].append(lat)
            self.flagged_designated[2].append(note)

            logger.debug("geo-flag: (%.6f, %.6f): %s" % (long, lat, note))

        except Exception as e:
            raise RuntimeError("Unable to perform conversion of the flagged designed to geographic: %s" % e)
