import logging
import math

import numpy as np
from hyo2.abc.lib.gdal_aux import GdalAux
# noinspection PyProtectedMember
from hyo2.grids._grids import FLOAT as GRIDS_FLOAT, DOUBLE as GRIDS_DOUBLE
from hyo2.qc.common.s57_aux import S57Aux
from hyo2.qc.survey.valsou.base_valsou import BaseValsou, valsou_algos
from osgeo import osr

logger = logging.getLogger(__name__)


class ValsouCheckV7(BaseValsou):

    def __init__(self, s57, grids, version="2018", scale=10000, with_laser=True, is_target_detection=False,
                 progress_bar=None):
        if version not in ["2015", "2016", "2017", "2018"]:
            raise RuntimeError("unsupported specs version: %s" % version)

        super().__init__(s57=s57, grids=grids)

        self.type = valsou_algos["VALSOU_CHECK_v7"]
        self.version = version
        self.scale = scale
        self.with_laser = with_laser
        self.is_target_detection = is_target_detection
        self.all_features = self.s57.rec10s
        self.progress = progress_bar

        self.dist_2mm = None
        self.valsou_features = list()
        self.valsou_2mm_features = list()
        self.valsou_1node_features = list()

        self.valsou_geo = None
        self.valsou_utm = None
        self.valsou_closest = None
        self.valsou_closest_2 = None
        self.valsou_visited = None
        self.out_of_bbox = False

        self.deconflicted = False
        self.geo2loc = None

        # dtm
        self.bathy_nodata = None
        self.bathy_values = None
        self.bathy_is_double = False
        self.bathy_hrs = None
        self.bathy_transform = None
        self.bathy_rows = None
        self.bathy_cols = None

        GdalAux.check_gdal_data()

    def run(self, max_dist=3.0, depth_precision=3, flag_out_of_bbox=True):
        """Actually execute the checks"""
        logger.info("valsou check against HSSD %s ..." % self.version)
        logger.info("include TECSOU=laser: %s" % self.with_laser)
        logger.info("is Target Detection: %s" % self.is_target_detection)
        logger.debug("all features: %d" % len(self.all_features))

        if self.version == "2018":
            depth_precision = 2

        # select all the features of interest + split in 2 groups (1-node and 2-mm)
        self._select_features()
        if len(self.valsou_features) == 0:
            logger.warning("no features to check!")
            return
        self._convert_features_to_array_coords(depth_precision=depth_precision)

        # check for features out of the bbox (skip for CSAR VR since there is not a low-res bbox)
        if flag_out_of_bbox and not (self.grids.is_vr() and self.grids.is_csar()):
            logger.debug("checking for out of bbox")
            self._check_out_of_bbox(max_dist=max_dist)
            # reset flagged and return in case that all the features are out-of-the-bbox
            if len(self.valsou_closest) == sum(self.valsou_visited):
                logger.warning("All the features are out of the bbox -> SKIPPING output")
                self.flagged_features = list()
                self.out_of_bbox = True
                return

        count = 0
        while self.grids.read_next_tile(layers=[self.grids.depth_layer_name(), ]):

            if self.progress is not None:
                if self.progress.value < 50:
                    self.progress.add(quantum=0.01)
                elif self.progress.value < 75:
                    self.progress.add(quantum=0.005)
                elif self.progress.value < 90:
                    self.progress.add(quantum=0.001)
                elif self.progress.value <= 99:
                    self.progress.add(quantum=0.0001)

            logger.info("--->>> new tile: %03d" % count)
            count += 1
            self._run_slice(depth_precision=depth_precision, max_dist=max_dist)
            self.grids.clear_tiles()

        # print(self.valsou_visited)
        for i, visited in enumerate(self.valsou_visited):
            if not visited:
                self.flagged_features.append([self.valsou_geo[i][0], self.valsou_geo[i][1], 'not-visited'])
                logger.warning("not visited feature: %s (%s, %s)"
                               % (self.valsou_features[i].acronym, self.valsou_geo[i][0], self.valsou_geo[i][1]))

    def _select_features(self):
        """ Select the required VALSOUs"""

        if self.version in ["2015", "2016", "2017"]:

            # first select all the feature of interest

            # select by feature type
            valsou_filter = ['WRECKS', 'UWTROC', 'OBSTRN']
            valsou_features = S57Aux.select_by_object(objects=self.all_features, object_filter=valsou_filter)
            logger.debug("features that are WRECKS|UWTROC|OBSTRN: %d" % len(valsou_features))

            # select by geometry
            valsou_features = S57Aux.select_only_points(objects=valsou_features)
            logger.debug("features that are only points: %d" % len(valsou_features))

            # select only “description=new or update”
            valsou_features = S57Aux.select_by_attribute_value(objects=valsou_features, attribute='descrp',
                                                               value_filter=['1', '2'])
            logger.debug("features that are new or updated: %d" % len(valsou_features))

            if self.with_laser:
                # select only “tecsou=found by echosounder, MBES, or laser”
                valsou_features = S57Aux.select_by_attribute_value(objects=valsou_features, attribute='TECSOU',
                                                                   value_filter=['1', '3', '7'])
            else:
                # select only “tecsou=found by echosounder, or MBES”
                valsou_features = S57Aux.select_by_attribute_value(objects=valsou_features, attribute='TECSOU',
                                                                   value_filter=['1', '3'])
            logger.debug("features after TECSOU selection: %d" % len(valsou_features))

            # select “watlev!=always dry”
            valsou_features = S57Aux.filter_by_attribute_value(objects=valsou_features, attribute='WATLEV',
                                                               value_filter=['2', ])
            logger.debug("features after WATLEV != always dry: %d" % len(valsou_features))

            # select only feature with valid float VALSOU attribute
            min_z, max_z = self._retrieve_validity_range_from_file_name()
            logger.debug("depth validity range: %s - %s" % (min_z, max_z))
            valsou_features = S57Aux.select_by_attribute_float_range(objects=valsou_features, attribute='VALSOU',
                                                                     min_value=min_z, max_value=max_z)
            logger.debug("features filtered by depth: %d" % len(valsou_features))

            self.valsou_features = valsou_features

            # then split into two groups: 1-node and 2-mm

            # 1-node group first
            valsou_1node_features = S57Aux.filter_by_attribute_value(objects=self.valsou_features, attribute='WATLEV',
                                                                     value_filter=['4', '5'])
            if self.version == "2015":
                valsou_1node_features = S57Aux.filter_by_attribute_value(objects=valsou_1node_features, attribute='descrp',
                                                                         value_filter=['2', ])
            self.valsou_1node_features = valsou_1node_features

            # 2-mm group as complement to 1-node group
            self.valsou_2mm_features = S57Aux.not_included_objects(all_objects=self.valsou_features,
                                                                   sub_objects=self.valsou_1node_features)

            logger.debug("selected %d features (2-mm: %d, 1-node: %d)"
                         % (len(self.valsou_features), len(self.valsou_2mm_features), len(self.valsou_1node_features)))
            if (len(self.valsou_2mm_features) + len(self.valsou_1node_features)) != len(self.valsou_features):
                raise RuntimeError("invalid feature splitting in version %s" % self.version)

        else:
            # first select all the feature of interest

            # select by feature type
            valsou_filter = ['WRECKS', 'UWTROC', 'OBSTRN']
            valsou_features = S57Aux.select_by_object(objects=self.all_features, object_filter=valsou_filter)

            # select by geometry
            valsou_features = S57Aux.select_only_points(objects=valsou_features)

            # select only “description=new or update”
            valsou_features = S57Aux.select_by_attribute_value(objects=valsou_features, attribute='descrp',
                                                               value_filter=['1', '2'])

            if self.with_laser:
                # select only “tecsou=found by echosounder, MBES, or laser”
                valsou_features = S57Aux.select_by_attribute_value(objects=valsou_features, attribute='TECSOU',
                                                                   value_filter=['1', '3', '7'])
            else:
                # select only “tecsou=found by echosounder, or MBES”
                valsou_features = S57Aux.select_by_attribute_value(objects=valsou_features, attribute='TECSOU',
                                                                   value_filter=['1', '3'])

            # select “watlev!=always dry”
            valsou_features = S57Aux.filter_by_attribute_value(objects=valsou_features, attribute='WATLEV',
                                                               value_filter=['2', ])

            # select only feature with valid float VALSOU attribute
            min_z, max_z = self._retrieve_validity_range_from_file_name()
            logger.debug("depth validity range: %s - %s" % (min_z, max_z))
            valsou_features = S57Aux.select_by_attribute_float_range(objects=valsou_features, attribute='VALSOU',
                                                                     min_value=min_z, max_value=max_z)

            self.valsou_features = valsou_features

    def _retrieve_validity_range_from_file_name(self):
        # based on NOAA naming rules

        logger.debug("grid name: %s" % self.grids.current_basename)
        logger.debug("target detection: %s" % self.is_target_detection)

        if self.is_target_detection:

            if "_50cm_" in self.grids.current_basename:
                return -99999, 20

            if "_1m_" in self.grids.current_basename:
                return 18, 40

            if "_4m_" in self.grids.current_basename:
                return 36, 80

            if "_8m_" in self.grids.current_basename:
                return 72, 160

            if "_16m_" in self.grids.current_basename:
                return 144, 320

        else:

            if "_1m_" in self.grids.current_basename:
                return -99999, 20

            if "_2m_" in self.grids.current_basename:
                return 18, 40

            if "_4m_" in self.grids.current_basename:
                return 36, 80

            if "_8m_" in self.grids.current_basename:
                return 72, 160

            if "_16m_" in self.grids.current_basename:
                return 144, 320

        # not following NOAA naming rules
        return -99999, 99999

    def _convert_features_to_array_coords(self, depth_precision):
        # prepare some lists with:
        # - the geographic position of the features (self.valsou_geo)
        # - the local (projected) position of the features (self.valsou_loc)
        # - the array-base coords of the features (self.valsou_array)
        # - the closest array nodes for each feature (self.valsou_closest)
        # - a boolean list of visited features (self.valsou_visited)

        # logger.debug("converting features to array coords ...")

        # first retrieve [long, lat, depth]
        self.valsou_geo = list()
        for feature in self.valsou_features:

            # retrieve depth value
            s57_valsou = None
            for attr in feature.attributes:

                if attr.acronym == 'VALSOU':
                    # invert sign due to the CSAR/BAG convention (depths are negative)
                    s57_valsou = -float(attr.value)
                    # logger.debug("VALSOU value: %f" % s57_valsou)
                    continue

            # append [long, lat, depth]
            self.valsou_geo.append([feature.centroid.x, feature.centroid.y, s57_valsou])
        # logger.debug("lon, lat, d: %s" % self.valsou_geo)

        # store the coordinate transform from CSAR CRS to geo (using GDAL)
        try:
            osr_grid = osr.SpatialReference()
            # logger.debug("cur_grids: %s" % self.grids.cur_grids)
            osr_grid.ImportFromWkt(self.grids.cur_grids.bbox().hrs)
            osr_geo = osr.SpatialReference()
            osr_geo.ImportFromEPSG(4326)  # geographic WGS84
            # self.loc2geo = osr.CoordinateTransformation(osr_bag, osr_geo)
            self.geo2loc = osr.CoordinateTransformation(osr_geo, osr_grid)

        except Exception as e:
            raise RuntimeError("unable to create a valid coords transform: %s" % e)

        # convert s57 features to grid CRS coords
        self.valsou_utm = np.array(self.geo2loc.TransformPoints(np.array(self.valsou_geo, np.float64)),
                                   np.float64)
        # logger.debug("x, y, z: %s" % self.valsou_loc)

        # create a list to flag the visited features
        self.valsou_visited = [False] * len(self.valsou_utm)
        # logger.debug("visited: %s" % self.valsou_visited)

        # convert feature to array coords
        valsou_array = np.copy(self.valsou_utm)
        valsou_array[:, 0] = (self.valsou_utm[:, 0] - self.grids.cur_grids.bbox().transform[0]) \
                             / self.grids.cur_grids.bbox().transform[1]
        valsou_array[:, 1] = (self.valsou_utm[:, 1] - self.grids.cur_grids.bbox().transform[3]) \
                             / self.grids.cur_grids.bbox().transform[5]
        # logger.debug("array: %s" % self.valsou_array)

        # convert to the closest array coordinates
        self.valsou_closest = np.empty_like(valsou_array)
        self.valsou_closest[:, 0] = np.rint(valsou_array[:, 0])
        self.valsou_closest[:, 1] = np.rint(valsou_array[:, 1])
        self.valsou_closest[:, 2] = np.around(valsou_array[:, 2], decimals=depth_precision)
        # logger.debug("closest: %s" % self.valsou_closest)

        # FIXME: bug fix for CARIS misalignments

        # convert feature to array coords
        valsou_array = np.copy(self.valsou_utm)
        valsou_array[:, 0] = (self.valsou_utm[:, 0] - self.grids.cur_grids.bbox().transform[0]) \
                             / self.grids.cur_grids.bbox().transform[1] - 0.5
        valsou_array[:, 1] = (self.valsou_utm[:, 1] - self.grids.cur_grids.bbox().transform[3]) \
                             / self.grids.cur_grids.bbox().transform[5] - 0.5
        # logger.debug("array: %s" % self.valsou_array)

        # convert to the closest array coordinates
        self.valsou_closest_2 = np.empty_like(valsou_array)
        self.valsou_closest_2[:, 0] = np.rint(valsou_array[:, 0])
        self.valsou_closest_2[:, 1] = np.rint(valsou_array[:, 1])
        self.valsou_closest_2[:, 2] = np.around(valsou_array[:, 2], decimals=depth_precision)
        # logger.debug("closest: %s" % self.valsou_closest_2)

        # logger.debug("converting features to array coords ... DONE!")

    def _check_out_of_bbox(self, max_dist):

        r_min = -max_dist
        r_max = self.grids.cur_grids.bbox().rows + max_dist
        c_min = -max_dist
        c_max = self.grids.cur_grids.bbox().cols + max_dist

        # logger.debug("max distance: %s" % max_dist)
        # logger.debug("bbox -> SW: %s, %s" % (r_min, c_min))
        # logger.debug("     -> NE: %s, %s" % (r_max, c_max))

        for i, closest in enumerate(self.valsou_closest):

            # logger.debug("#%d -> closest (%s, %s)" % (i, closest[1], closest[0]))

            if (closest[1] < r_min) or (closest[0] < c_min) or (closest[1] >= r_max) or (closest[0] >= c_max):

                self.flagged_features.append([self.valsou_geo[i][0], self.valsou_geo[i][1], 'out-of-bbox'])
                logger.warning("Feature at (%s, %s) out of bbox" % (self.valsou_geo[i][0], self.valsou_geo[i][1]))

                self.valsou_visited[i] = True
                continue

        # FIXME: bug fix for CARIS misalignments
        for i, closest in enumerate(self.valsou_closest_2):

            # logger.debug("#%d -> closest (%s, %s)" % (i, closest[1], closest[0]))

            if (closest[1] < r_min) or (closest[0] < c_min) or (closest[1] >= r_max) or (closest[0] >= c_max):

                if self.valsou_visited[i]:
                    continue

                self.flagged_features.append([self.valsou_geo[i][0], self.valsou_geo[i][1], 'out-of-bbox'])
                logger.warning("Feature at (%s, %s) out of bbox" % (self.valsou_geo[i][0], self.valsou_geo[i][1]))

                self.valsou_visited[i] = True
                continue

        # logger.debug("visited: %s" % self.valsou_visited)

    def _run_slice(self, depth_precision, max_dist):
        """Apply the algorithm to the current slice"""

        # load depths
        self._load_depths()

        # TODO: *** only used in 2016 and 2017 ***
        # first convert the 2mm at survey scale rule into grid node distance (based on grid resolution)
        self.dist_2mm = 0.002 * self.scale / self.bathy_transform[1]
        logger.debug("2-mm in nodes: %f (scale: %f, res: %f)" % (self.dist_2mm, self.scale, self.bathy_transform[1]))
        # epsilon used to compare floating-point depths
        eps_depth = 10**-(depth_precision + 1)
        logger.debug("epsilon depth: %f" % (eps_depth))

        self._calc_array_coords_in_cur_tile(depth_precision=depth_precision)

        # check each features against the surface slice
        for i, closest in enumerate(self.valsou_closest):

            logger.debug("%d: (%s, %s) -> (%s, %s)"
                         % (i, closest[0], closest[1], self.valsou_geo[i][0], self.valsou_geo[i][1]))

            # skip if already visited in a previous slice
            if self.valsou_visited[i]:
                continue

            # skip if not in the current grid slice (we know the y boundaries of the current slice)
            if (closest[0] < 0) or (closest[0] >= self.bathy_cols) or \
                    (closest[1] < 0) or (closest[1] >= self.bathy_rows):
                if (closest[0] == self.bathy_cols) or (closest[1] == self.bathy_rows):
                    if closest[0] == self.bathy_cols:
                        closest[0] -= 1
                        logger.info("on-right-edge fix: 0 < (%d, %d) >= (%d, %d)"
                                    % (closest[0], closest[1], self.bathy_cols, self.bathy_rows))
                    if closest[1] == self.bathy_rows:
                        closest[1] -= 1
                        logger.info("on-top-edge fix: 0 < (%d, %d) >= (%d, %d)"
                                    % (closest[0], closest[1], self.bathy_cols, self.bathy_rows))
                else:
                    logger.debug("skip: 0 < (%d, %d) >= (%d, %d)"
                                 % (closest[0], closest[1], self.bathy_cols, self.bathy_rows))
                    continue

            # FIXME: bug fix for CARIS misalignments
            # skip if not in the current grid slice (we know the y boundaries of the current slice)
            if (self.valsou_closest_2[i][0] < 0) or (self.valsou_closest_2[i][0] >= self.bathy_cols) or \
                    (self.valsou_closest_2[i][1] < 0) or (self.valsou_closest_2[i][1] >= self.bathy_rows):
                logger.debug("skip (fix): 0 < (%d, %d) >= (%d, %d)"
                             % (self.valsou_closest_2[i][0], self.valsou_closest_2[i][1],
                                self.bathy_cols, self.bathy_rows))
                continue

            # retrieve the depth value of the closest grid node
            depth_closest = self.bathy_values[int(closest[1]), int(closest[0])]
            # FIXME: bug fix for CARIS misalignments
            depth_closest_2 = self.bathy_values[int(self.valsou_closest_2[i][1]), int(self.valsou_closest_2[i][0])]

            # early exit: the closest-node depth matches with the feature depth
            # FIXME: bug fix for CARIS misalignments
            if (abs(round(depth_closest, depth_precision) - round(closest[2], depth_precision)) < eps_depth)\
                    or (abs(round(depth_closest_2, depth_precision) - round(self.valsou_closest_2[i][2], depth_precision))
                        < eps_depth):
                self.valsou_visited[i] = True
                continue

            if self.version in ["2018", ]:
                self.flagged_features.append([self.valsou_geo[i][0], self.valsou_geo[i][1],
                                              'depth discrepancy'])
                logger.info("+1  -> depth discrepancy at %s, %s: %s vs. %s/%s"
                            % (self.valsou_geo[i][0], self.valsou_geo[i][1],
                               round(closest[2], depth_precision), round(depth_closest, depth_precision),
                               round(depth_closest_2, depth_precision)))

            else:

                logger.debug("#%d" % i)
                logger.debug("[*] -> ft depth: %f -> node (%d, %d) -> %f"
                             % (closest[2], closest[1], closest[0], depth_closest))
                # FIXME: bug fix for CARIS misalignments
                logger.debug("[*] -> ft depth: %f -> node (%d, %d) -> %f"
                             % (self.valsou_closest_2[i][2], self.valsou_closest_2[i][1], self.valsou_closest_2[i][0],
                                depth_closest_2))

                # now we identify if the feature belongs to the 2mm or to the 1node group
                if self.valsou_features[i] in self.valsou_2mm_features:
                    apply_2mm_rule = True
                else:
                    apply_2mm_rule = False

                # If here, the area surrounding the feature overlaps for (at least) 1 node with the surface array.
                # We thus run a moving window that collects info of the nodes surrounding the feature
                delta_depth_list = list()
                dist_list = list()
                node_list = list()
                # We need to have different size for the moving window based on the feature group
                if apply_2mm_rule:
                    mov_win = range(-int(math.floor(self.dist_2mm) * 2), int(math.ceil(self.dist_2mm * 2)))
                else:
                    mov_win = range(-int(math.floor(self.dist_2mm) * 2), int(math.ceil(self.dist_2mm * 2)))

                # Looking into the nodes surrounding the feature
                for ii in mov_win:

                    for jj in mov_win:
                        # we set a tuple with (x, y) c
                        node = (closest[0] + jj, closest[1] + ii)
                        # print(closest, node)

                        # we just care about the nodes that are max_dist*grid_resolution
                        dist = math.hypot(node[1] - closest[1], node[0] - closest[0])
                        # print("dist: %s" % dist)

                        if apply_2mm_rule:
                            if dist >= (self.dist_2mm * 2):
                                continue

                        else:
                            if dist >= max_dist:
                                continue

                        # print("valid distance")
                        try:
                            depth = np.around(self.bathy_values[int(node[1]), int(node[0])], decimals=depth_precision)

                        except IndexError as e:  # skip cells outside the array
                            # logger.info("skipping cell in moving window: %s" % e)
                            continue

                        if np.isnan(depth):  # skip cells with nan as value
                            continue

                        delta_depth_list.append(abs(depth - closest[2]))
                        # logger.debug("Depths: %f, %f, %f"
                        #               % (self.grids.bathy[int(node[1]), int(node[0])], depth, closest[2]))
                        dist_list.append(dist)
                        node_list.append(node)

                # set the nodata-under-the-feature token
                nodata_token = str()
                if np.isnan(depth_closest):
                    nodata_token = "[*]"

                # check the results of the inspection of the surrounding nodes
                #
                # - case #1: there are NOT grid nodes in the surrounding area
                if len(dist_list) == 0:
                    logger.info("Could not locate any grid nodes near the feature found at (%s, %s)" %
                                (self.valsou_geo[i][0], self.valsou_geo[i][1]))

                    # an isolated feature: should we flag it in some way?

                # - case #2: there are 1 or more grid nodes in the surrounding area
                else:
                    # first test for depth
                    dist_ind = dist_list.index(np.min(dist_list))  # index of the minimum distance
                    min_depth_list = np.min(delta_depth_list)
                    depth_ind = delta_depth_list.index(min_depth_list)  # index of the minimum depth difference
                    depth_issue = (min_depth_list >= 0.01)
                    if depth_issue:
                        logger.info("!!! -> depth issue: min delta is %.4f" % min_depth_list)

                    # then test for position
                    dist_diff = dist_list[depth_ind]  # distance corresponding to the minimum depth difference
                    if apply_2mm_rule:
                        position_issue = (dist_diff > self.dist_2mm) and (min_depth_list >= 0.005)  # 2-mm rule
                        position_issue_msg = "(2mm rule)"

                    else:
                        position_issue = (dist_diff > 1) and (min_depth_list >= 0.005)  # 1-node rule
                        position_issue_msg = "(1node rule)"
                    position_imperfect = dist_ind != depth_ind

                    # ideal case:
                    # - the node at the minimum distance and the node at the minimum depth difference match
                    # - the minimum depth difference is zero
                    if (not position_imperfect) and (not depth_issue):
                        pass

                    # there are currently 3 possible flagging combination:
                    elif not depth_issue:
                        # 1 - only position issue
                        if position_issue:
                            self.flagged_features.append([self.valsou_geo[i][0], self.valsou_geo[i][1],
                                                          'position issue %s %s' % (position_issue_msg, nodata_token)])
                            logger.info("+1  -> depth OK, position issue %s: %s, %s"
                                        % (position_issue_msg, self.valsou_geo[i][0], self.valsou_geo[i][1]))

                        elif position_imperfect:
                            logger.info("!!! -> depth OK, position imperfect: %s, %s"
                                        % (self.valsou_geo[i][0], self.valsou_geo[i][1]))

                    elif depth_issue:

                        # 2 - depth and position issues
                        if position_issue:
                            self.flagged_features.append([self.valsou_geo[i][0], self.valsou_geo[i][1],
                                                         'depth discrepancy and position issue %s %s'
                                                          % (position_issue_msg, nodata_token)])
                            logger.info("+1  -> depth discrepancy and position issue %s: %s, %s"
                                        % (position_issue_msg, self.valsou_geo[i][0], self.valsou_geo[i][1]))

                        # 3 - only depth issue
                        elif position_imperfect:
                            self.flagged_features.append([self.valsou_geo[i][0], self.valsou_geo[i][1],
                                                          'depth discrepancy %s' % nodata_token])
                            logger.info("+1  -> depth issue, position imperfect: %s, %s"
                                        % (self.valsou_geo[i][0], self.valsou_geo[i][1]))

                        # 3 - only depth issue (as before, but the position is perfect)
                        else:
                            self.flagged_features.append([self.valsou_geo[i][0], self.valsou_geo[i][1],
                                                          'depth discrepancy %s' % nodata_token])
                            logger.info("+1  -> depth issue, position OK: %s, %s"
                                        % (self.valsou_geo[i][0], self.valsou_geo[i][1]))

            self.valsou_visited[i] = True

    def _load_depths(self):
        """Helper function that loads the depths values"""
        # logger.debug("depth layer: %s" % self.grids.depth_layer_name())

        tile = self.grids.tiles[0]
        # logger.debug("types: %s" % (list(tile.types),))
        if len(tile.types) == 0:
            raise RuntimeError("unable to read any type from loaded tile")

        depth_type = tile.type(self.grids.depth_layer_name())
        depth_idx = tile.band_index(self.grids.depth_layer_name())
        # logger.debug("depth layer: %s [idx: %s]" % (self.grids.grid_data_type(depth_type), depth_idx))

        if depth_type == GRIDS_DOUBLE:

            self.bathy_is_double = True
            self.bathy_values = tile.doubles[depth_idx]
            self.bathy_nodata = tile.doubles_nodata[depth_idx]
            self.bathy_values[tile.doubles[depth_idx] == tile.doubles_nodata[depth_idx]] = np.nan
            if len(self.bathy_values) == 0:
                raise RuntimeError("No bathy values")

        elif depth_type == GRIDS_FLOAT:

            self.bathy_is_double = False
            self.bathy_values = tile.floats[depth_idx]
            self.bathy_nodata = tile.floats_nodata[depth_idx]
            self.bathy_values[tile.floats[depth_idx] == tile.floats_nodata[depth_idx]] = np.nan
            if len(self.bathy_values) == 0:
                raise RuntimeError("No bathy values")

        else:
            raise RuntimeError("Unsupported data type for bathy")

        if self.bathy_hrs is None:
            self.bathy_hrs = str(tile.bbox.hrs)
        self.bathy_transform = list(tile.bbox.transform)
        logger.debug("transform: [%s, %s, %s, %s, %s, %s]"
                     % (self.bathy_transform[0], self.bathy_transform[1], self.bathy_transform[2],
                        self.bathy_transform[3], self.bathy_transform[4], self.bathy_transform[5],))
        self.bathy_rows = int(tile.bbox.rows)
        self.bathy_cols = int(tile.bbox.cols)
        logger.debug("shape: %d, %d" % (self.bathy_rows, self.bathy_cols))

    def _calc_array_coords_in_cur_tile(self, depth_precision):
        # convert feature to array coords
        # logger.debug("geo: %s" % self.valsou_geo)
        # logger.debug("loc: %s" % self.valsou_loc)
        valsou_array = np.copy(self.valsou_utm)
        valsou_array[:, 0] = (self.valsou_utm[:, 0] - self.bathy_transform[0]) / self.bathy_transform[1]
        valsou_array[:, 1] = (self.valsou_utm[:, 1] - self.bathy_transform[3]) / self.bathy_transform[5]
        # logger.debug("array: %s" % valsou_array)

        # convert to the closest array coordinates
        self.valsou_closest = np.empty_like(valsou_array)
        self.valsou_closest[:, 0] = np.rint(valsou_array[:, 0])
        self.valsou_closest[:, 1] = np.rint(valsou_array[:, 1])
        self.valsou_closest[:, 2] = np.around(valsou_array[:, 2], decimals=depth_precision)
        # logger.debug("closest: %s" % self.valsou_closest)

        # FIXME: bug fix for CARIS misalignments

        valsou_array = np.copy(self.valsou_utm)
        valsou_array[:, 0] = (self.valsou_utm[:, 0] - self.bathy_transform[0]) / self.bathy_transform[1] - 0.5
        valsou_array[:, 1] = (self.valsou_utm[:, 1] - self.bathy_transform[3]) / self.bathy_transform[5] - 0.5
        # logger.debug("array: %s" % valsou_array)

        # convert to the closest array coordinates
        self.valsou_closest_2 = np.empty_like(valsou_array)
        self.valsou_closest_2[:, 0] = np.rint(valsou_array[:, 0])
        self.valsou_closest_2[:, 1] = np.rint(valsou_array[:, 1])
        self.valsou_closest_2[:, 2] = np.around(valsou_array[:, 2], decimals=depth_precision)
        # logger.debug("closest: %s" % self.valsou_closest_2)
