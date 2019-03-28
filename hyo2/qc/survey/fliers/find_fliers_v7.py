import math
from scipy import ndimage
from hyo2.abc.lib.gdal_aux import GdalAux
from osgeo import osr, gdal
# noinspection PyProtectedMember
from hyo2.grids._grids import FLOAT as GRIDS_FLOAT, DOUBLE as GRIDS_DOUBLE
from hyo2.s57.s57 import S57
import numpy as np
import os
import logging

from hyo2.qc.survey.fliers.find_fliers_checks_v7 import \
    check_laplacian_operator_float, check_laplacian_operator_double, \
    check_gaussian_curvature_float, check_gaussian_curvature_double, \
    check_adjacent_cells_float, check_adjacent_cells_double, \
    check_small_groups_float, check_small_groups_double, \
    check_noisy_edges_float, check_noisy_edges_double
from hyo2.qc.survey.fliers.base_fliers import BaseFliers, fliers_algos


logger = logging.getLogger(__name__)


class FindFliersV7(BaseFliers):

    default_filter_distance = 1.0
    default_filter_delta_z = 0.01

    def __init__(self, grids, height=None,
                 check_laplacian=True, check_curv=True, check_adjacent=True, check_slivers=True,
                 check_isolated=True, check_edges=True,
                 filter_fff=False, filter_designated=False,
                 save_proxies=False, save_heights=False, save_curvatures=False,
                 output_folder=None, progress_bar=None):

        super().__init__(grids=grids)
        self.type = fliers_algos["FIND_FLIERS_v7"]

        self.save_proxies = save_proxies
        self.save_heights = save_heights
        self.save_curvatures = save_curvatures

        if output_folder is None:
            raise RuntimeError("missing output folder")
        self.output_folder = output_folder

        # inputs
        self.flier_height = height
        self.cur_height = None
        self.cur_curv_th = None
        self.check_laplacian = check_laplacian  # 1
        self.check_curv = check_curv  # 2
        self.check_adjacent = check_adjacent  # 3
        self.check_slivers = check_slivers  # 4
        self.check_isolated = check_isolated  # 5
        self.check_edges = check_edges  # 6
        self.filter_fff = filter_fff
        self.filter_designated = filter_designated
        self.progress = progress_bar

        # dtm
        self.bathy_values = None
        self.bathy_is_double = False
        self.bathy_hrs = None
        self.bathy_transform = None
        self.bathy_tile = 0

        # designated
        self.designated_soundings = list()

        # intermediate
        self.dtm_mask = None
        self.median = None
        self.nmad = None
        self.gx = None
        self.gy = None
        self.gauss_curv = None
        self.std_gauss_curv = None
        self.dtm_mean = None
        self.dtm_std = None
        self.dtm_mad = None

        # outputs
        self.flag_grid = None

    @property
    def basename(self) -> str:
        algo_type = "FFv7"

        basename = "%s.%s" % (self.grids.current_basename, algo_type)
        if self.flier_height is not None:
            height_str = "%.1f" % self.flier_height
            basename += ".h%s" % height_str.replace(".", "_")

        dot_chk_added = False
        if self.check_laplacian:
            if not dot_chk_added:
                dot_chk_added = True
                basename += ".chk"
            basename += "1"
        if self.check_curv:
            if not dot_chk_added:
                dot_chk_added = True
                basename += ".chk"
            basename += "2"
        if self.check_adjacent:
            if not dot_chk_added:
                dot_chk_added = True
                basename += ".chk"
            basename += "3"
        if self.check_slivers:
            if not dot_chk_added:
                dot_chk_added = True
                basename += ".chk"
            basename += "4"
        if self.check_isolated:
            if not dot_chk_added:
                dot_chk_added = True
                basename += ".chk"
            basename += "5"
        if self.check_edges:
            if not dot_chk_added:
                dot_chk_added = True
                basename += ".chk"
            basename += "6"

        dot_flt_added = False
        if self.filter_fff:
            if not dot_flt_added:
                dot_flt_added = True
                basename += ".flt"
            basename += "1"
        if self.filter_designated:
            if not dot_flt_added:
                dot_flt_added = True
                basename += ".flt"
            basename += "2"

        return basename

    # ######## common helpers ########

    def _calc_gradients(self):
        self.gy, self.gx = np.gradient(self.dtm_mask)

    def _calc_gaussian_curvatures(self):
        """Calculate gaussian (K) curvatures

        The method is based on: "Computation of Surface Curvature from Range Images
        Using Geometrically Intrinsic Weights"*, T. Kurita and P. Boulanger, 1992.
        - gauss_curv: (3)
        """
        if self.gx is None:
            self._calc_gradients()
        gxy, gxx = np.gradient(self.gx)
        gyy, _ = np.gradient(self.gy)
        self.gauss_curv = (gxx * gyy - (gxy ** 2)) / (1 + (self.gx ** 2) + (self.gy ** 2)) ** 2
        self.std_gauss_curv = np.std(self.gauss_curv)

        # logger.info("non masked values: %d" % self.dtm_mask.count())
        # logger.info("gx: %s" % self.gx)
        # logger.info("gy: %s" % self.gy)
        # logger.info("gauss curv: %s" % self.gauss_curv)
        # logger.info("std gauss curv: %s" % self.std_gauss_curv)

    # ######## height estimation ########

    def estimate_height_and_curv_th(self):
        # logger.info("estimation of flier heights ...")

        estimated_height = 1.0
        estimated_curv_th = 6.0

        self.gy = None
        self.gx = None
        # logger.debug("dtm_mask: %s" % self.dtm_mask)
        # np.savetxt('array_%d' % self.bathy_tile, self.dtm_mask)
        self.median = np.ma.median(self.dtm_mask)  # compute the median along a flattened version of the array
        self.dtm_mean = np.ma.mean(self.dtm_mask)
        self.dtm_std = np.ma.std(self.dtm_mask)
        self.dtm_mad = abs(self.median - self.dtm_mean)  # median absolute deviation to measure the data variability
        self.nmad = self.dtm_mad / self.dtm_std
        self._calc_gaussian_curvatures()

        # noinspection PyStringFormat
        logger.debug("proxies -> median: %f, nmad: %f, std curv: %f" % (self.median, self.nmad, self.std_gauss_curv))

        # bug fix for nan cases
        if np.isnan(self.median) or np.isnan(self.nmad) or np.isnan(self.std_gauss_curv):
            logger.warning("skipping calculation due to nan proxies: %s, %s, %s"
                           % (np.isnan(self.median), np.isnan(self.nmad), np.isnan(self.std_gauss_curv)))
            self.cur_height = 1.0
            self.cur_curv_th = 6.0
            return

        # characteristic depth
        if self.median > -20:
            estimated_height = 1.0
        elif self.median > -40:
            estimated_height = 2.0
        elif self.median > -80:
            estimated_height = 4.0
        elif self.median > -160:
            estimated_height = 6.0
        else:  # <= -1000 m
            estimated_height = 8.0

        # correction for variability in range
        if self.nmad < 0.2:
            if estimated_height == 1.0:
                estimated_height += 1.0
            else:
                estimated_height += 2.0
        if self.nmad < 0.1:
            estimated_height += 2.0

        # correction for global roughness
        if self.std_gauss_curv > 0.01:
            if estimated_height == 1.0:
                estimated_height += 1.0
            else:
                estimated_height += 2.0
            estimated_curv_th *= 2.0
        if self.std_gauss_curv > 0.03:
            estimated_curv_th *= 2.0
        if self.std_gauss_curv > 0.1:
            estimated_height += 2.0
            estimated_curv_th *= 2.0

        if self.cur_height is not None:
            logger.debug("using user-selected height: %s" % self.cur_height)
        if (self.check_laplacian or self.check_adjacent or self.check_slivers) and (self.cur_height is None):
            logger.info("estimated fliers height: %.1f" % estimated_height)
            self.cur_height = estimated_height

        logger.info("estimated gaussian threshold: %.1f" % estimated_curv_th)
        self.cur_curv_th = estimated_curv_th

        if self.save_proxies:
            try:
                self._save_proxies_as_geotiff()
            except Exception as e:
                logger.info("unable to save proxies geotiff: %s" % e)
        if self.save_heights:
            try:
                self._save_heights_as_geotiff()
            except Exception as e:
                logger.info("unable to save heights geotiff: %s" % e)
        if self.save_curvatures:
            try:
                self._save_curvatures_as_geotiff()
            except Exception as e:
                logger.info("unable to save curvatures geotiff: %s" % e)

    def _save_proxies_as_geotiff(self) -> None:
        # logger.debug("saving geotiff for heights")

        # median

        geotiff_path = os.path.join(self.output_folder, "%s.t%05d.medians.tif" % (self.basename, self.bathy_tile))
        # logger.debug("heights output: %s" % geotiff_path)

        nodata = -9999.0
        array = np.empty_like(self.dtm_mask, dtype=np.float32)
        array[self.dtm_mask.mask] = nodata
        array[~self.dtm_mask.mask] = self.median

        self._save_array_as_geotiff(geotiff_path=geotiff_path, array=array, nodata=nodata)

        # nmad

        geotiff_path = os.path.join(self.output_folder, "%s.t%05d.nmads.tif" % (self.basename, self.bathy_tile))
        # logger.debug("heights output: %s" % geotiff_path)

        nodata = -9999.0
        array = np.empty_like(self.dtm_mask, dtype=np.float32)
        array[self.dtm_mask.mask] = nodata
        array[~self.dtm_mask.mask] = self.nmad

        self._save_array_as_geotiff(geotiff_path=geotiff_path, array=array, nodata=nodata)

        # std gauss curv

        geotiff_path = os.path.join(self.output_folder, "%s.t%05d.std_gauss_curvs.tif" % (self.basename, self.bathy_tile))
        # logger.debug("heights output: %s" % geotiff_path)

        nodata = -9999.0
        array = np.empty_like(self.dtm_mask, dtype=np.float32)
        array[self.dtm_mask.mask] = nodata
        array[~self.dtm_mask.mask] = self.std_gauss_curv

        self._save_array_as_geotiff(geotiff_path=geotiff_path, array=array, nodata=nodata)

        # gauss curv

        geotiff_path = os.path.join(self.output_folder, "%s.t%05d.gauss_curvs.tif" % (self.basename, self.bathy_tile))
        # logger.debug("heights output: %s" % geotiff_path)

        nodata = -9999.0
        array = np.empty_like(self.dtm_mask, dtype=np.float32)
        array[self.dtm_mask.mask] = nodata
        array[~self.dtm_mask.mask] = self.gauss_curv[~self.dtm_mask.mask]

        self._save_array_as_geotiff(geotiff_path=geotiff_path, array=array, nodata=nodata)

    def _save_heights_as_geotiff(self) -> None:
        # logger.debug("saving geotiff for heights")

        geotiff_path = os.path.join(self.output_folder, "%s.t%05d.th_heights.tif" % (self.basename, self.bathy_tile))
        # logger.debug("heights output: %s" % geotiff_path)

        nodata = -9999.0
        array = np.empty_like(self.dtm_mask, dtype=np.float32)
        array[self.dtm_mask.mask] = nodata
        array[~self.dtm_mask.mask] = self.cur_height

        self._save_array_as_geotiff(geotiff_path=geotiff_path, array=array, nodata=nodata)

    def _save_curvatures_as_geotiff(self) -> None:
        # logger.debug("saving geotiff for curvatures")

        geotiff_path = os.path.join(self.output_folder, "%s.t%05d.th_curvatures.tif" % (self.basename, self.bathy_tile))
        # logger.debug("heights output: %s" % geotiff_path)

        nodata = -9999.0
        array = np.empty_like(self.dtm_mask, dtype=np.float32)
        array[self.dtm_mask.mask] = nodata
        array[~self.dtm_mask.mask] = self.cur_curv_th

        self._save_array_as_geotiff(geotiff_path=geotiff_path, array=array, nodata=nodata)

    def _save_array_as_geotiff(self, geotiff_path: str, array: np.ndarray, nodata: float) -> None:
        driver = gdal.GetDriverByName('GTiff')
        ds = driver.Create(geotiff_path, array.shape[1], array.shape[0], 1, gdal.GDT_Float32, )
        ds.SetProjection(self.bathy_hrs)
        # logger.debug("transform: [%s, %s, %s, %s, %s, %s]"
        #              % (self.bathy_transform[0], self.bathy_transform[1], self.bathy_transform[2],
        #                 self.bathy_transform[3], self.bathy_transform[4], self.bathy_transform[5],))
        ds.SetGeoTransform((self.bathy_transform[0] - self.bathy_transform[1]*0.5,
                            self.bathy_transform[1],
                            self.bathy_transform[2],
                            self.bathy_transform[3] - self.bathy_transform[5]*0.5,
                            self.bathy_transform[4],
                            self.bathy_transform[5],))
        ds.GetRasterBand(1).SetNoDataValue(nodata)
        ds.GetRasterBand(1).WriteArray(array)
        ds.FlushCache()

    # ######## find flier ########

    def run(self):
        logger.info("flier height: %s " % (self.flier_height,))
        logger.debug("save heights: %s" % self.save_heights)
        logger.info("active checks: laplacian: %s, curv: %s, adjacent: %s, slivers: %s, isolated: %s, edges: %s"
                    % (self.check_laplacian, self.check_curv, self.check_adjacent, self.check_slivers,
                       self.check_isolated, self.check_edges))
        logger.info("active filters: FFF: %s, Designated: %s" % (self.filter_fff, self.filter_designated))

        self.bathy_tile = 0
        while self.grids.read_next_tile(layers=[self.grids.depth_layer_name(), ]):

            if self.progress is not None:
                if self.progress.value < 50:
                    self.progress.add(quantum=10)
                elif self.progress.value < 75:
                    self.progress.add(quantum=1)
                elif self.progress.value < 90:
                    self.progress.add(quantum=0.1)
                elif self.progress.value <= 99:
                    self.progress.add(quantum=0.0001)

            self._run_slice()
            self.grids.clear_tiles()
            self.bathy_tile += 1
            logger.debug("new tile: %s" % self.bathy_tile)

    def _run_slice(self):

        # load depths
        self._load_depths()

        # to force recalculation
        self.gy = None
        self.gx = None

        self.cur_height = self.flier_height
        self.estimate_height_and_curv_th()
        if self.cur_height == 0:
            raise RuntimeError("unable to estimate height, and one of the selected algorithms "
                               "needs the estimated height")

        # create a 0 grid of the same size as input grid to be used to store the flagged node
        self.flag_grid = np.zeros(self.bathy_values.shape, dtype=np.int)

        if self.check_laplacian:
            self._check_laplacian_operator()

        if self.check_curv:
            self._check_gaussian_curvature()

        if self.check_adjacent:
            self._check_adjacent_cells()

        if self.check_isolated or self.check_slivers:
            self._check_small_groups()

        if self.check_edges:
            self._check_edges()

        self._georef_fliers()

    def _check_laplacian_operator(self):
        """Check the grid for fliers using the Laplacian operator"""

        # logging.debug("*** CHECK #1: START ***")

        th = -4. * self.cur_height

        lap = ndimage.filters.laplace(self.bathy_values)

        if self.bathy_is_double:
            check_laplacian_operator_double(lap, self.flag_grid, th)
        else:
            check_laplacian_operator_float(lap, self.flag_grid, th)
        # logging.debug("*** CHECK #1: END ***")

        # # The above function call is the optimized version of:
        # lap = (lap < th) or (lap > -th)
        # nz_y, nz_x = lap.nonzero()
        # for i, x in enumerate(nz_x):
        #     y = nz_y[i]
        #     self.flag_grid[y, x] = 1  # check #1

    def _check_gaussian_curvature(self):
        """Check the gaussian curvature"""

        # logging.debug("*** CHECK #2: START ***")

        self._calc_gaussian_curvatures()

        if self.bathy_is_double:
            check_gaussian_curvature_double(self.gauss_curv, self.flag_grid, self.cur_curv_th)
        else:
            check_gaussian_curvature_float(self.gauss_curv, self.flag_grid, self.cur_curv_th)
        # logging.debug("*** CHECK #2: END ***")

        # # The above function call is the optimized version of:
        # flagged = self.gauss_curv > 6.
        # nz_y, nz_x = flagged.nonzero()
        # for i, x in enumerate(nz_x):
        #     y = nz_y[i]
        #     if self.flag_grid[y, x] == 0:  # avoid existing flagged nodes
        #         self.flag_grid[y, x] = 2  # check #2

    def _check_adjacent_cells(self):
        """Check all the adjacent cells"""

        # logging.debug("*** CHECK #3: START ***")

        if self.bathy_is_double:
            check_adjacent_cells_double(self.bathy_values, self.flag_grid, self.cur_height, 0.75, 0.8)
        else:
            check_adjacent_cells_float(self.bathy_values, self.flag_grid, self.cur_height, 0.75, 0.8)
        # logging.debug("*** CHECK #3: END ***")

    def _check_edges(self):
        """Check all the adjacent cells"""

        logging.debug("*** CHECK #6: START ***")

        if self.bathy_is_double:
            check_noisy_edges_double(self.bathy_values, self.flag_grid)
        else:
            check_noisy_edges_float(self.bathy_values, self.flag_grid)

        logging.debug("*** CHECK #6: END ***")

    def _check_small_groups(self, area_limit=3):
        """Check the grid for isolated cells"""

        # logging.debug("*** CHECKS #4/5: START ***")

        if self.cur_height is None:
            th = 0.0  # it will be not used since we are not checking for slivers (just isolated nodes)
        else:
            th = self.cur_height / 2.0

        # make a binary image
        grid_bin = np.isfinite(self.bathy_values)

        if self.bathy_is_double:
            check_small_groups_double(grid_bin, self.bathy_values, self.flag_grid, th, area_limit, self.check_slivers,
                                      self.check_isolated)
        else:
            check_small_groups_float(grid_bin, self.bathy_values, self.flag_grid, th, area_limit, self.check_slivers,
                                     self.check_isolated)
        # logging.debug("*** CHECKS #4/5: END ***")

    def _load_depths(self):
        """Helper function that loads the depths values"""
        # logger.debug("depth layer: %s" % self.grids.depth_layer_name())

        tile = self.grids.tiles[0]
        # logger.debug("types: %s" % (list(tile.types),))

        depth_type = tile.type(self.grids.depth_layer_name())
        depth_idx = tile.band_index(self.grids.depth_layer_name())
        # logger.debug("depth layer: %s [idx: %s]" % (self.grids.grid_data_type(depth_type), depth_idx))

        if depth_type == GRIDS_DOUBLE:

            self.bathy_is_double = True
            self.bathy_values = tile.doubles[depth_idx]
            self.bathy_values[tile.doubles[depth_idx] == tile.doubles_nodata[depth_idx]] = np.nan
            if len(self.bathy_values) == 0:
                raise RuntimeError("No bathy values")

        elif depth_type == GRIDS_FLOAT:

            self.bathy_is_double = False
            self.bathy_values = tile.floats[depth_idx]
            self.bathy_values[tile.floats[depth_idx] == tile.floats_nodata[depth_idx]] = np.nan
            if len(self.bathy_values) == 0:
                raise RuntimeError("No bathy values")

        else:
            raise RuntimeError("Unsupported data type for bathy")

        if self.bathy_hrs is None:
            self.bathy_hrs = tile.bbox.hrs
        self.bathy_transform = [tile.bbox.transform[0], tile.bbox.transform[1], tile.bbox.transform[2],
                                tile.bbox.transform[3], tile.bbox.transform[4], tile.bbox.transform[5],]
        # logger.debug("transform: [%s, %s, %s, %s, %s, %s]"
        #              % (self.bathy_transform[0], self.bathy_transform[1], self.bathy_transform[2],
        #                 self.bathy_transform[3], self.bathy_transform[4], self.bathy_transform[5],))

        # mask to avoid nan issues
        self.dtm_mask = np.ma.masked_invalid(self.bathy_values)

        # logger.debug('dtm: %s (valid: %d, masked: %d)'
        #              % (self.bathy_values.shape, self.dtm_mask.count(), np.ma.count_masked(self.dtm_mask)))

    def _georef_fliers(self):
        """Helper function that looks at the flagged array and store the node != 0 as feature fliers"""

        # selected holes
        fliers_x = list()
        fliers_y = list()
        fliers_z = list()
        fliers_ck = list()

        nz_y, nz_x = self.flag_grid.nonzero()
        for i, x in enumerate(nz_x):
            y = nz_y[i]
            fliers_x.append(x)
            fliers_y.append(y)
            fliers_z.append(self.bathy_values[y, x])
            fliers_ck.append(self.flag_grid[y, x])

        GdalAux.check_gdal_data()

        # logger.debug("crs: %s" % self.bathy_crs)
        try:
            osr_csar = osr.SpatialReference()
            osr_csar.ImportFromWkt(self.bathy_hrs)
            osr_geo = osr.SpatialReference()
            osr_geo.ImportFromEPSG(4326)  # geographic WGS84
            loc2geo = osr.CoordinateTransformation(osr_csar, osr_geo)

        except Exception as e:
            raise IOError("unable to create a valid coords transform: %s" % e)

        if len(fliers_x) == 0:
            logger.info("No fliers detected in current slice, total fliers: %s" % len(self.flagged_fliers))
            return

        tile = self.grids.tiles[0]

        flagged_xs = list()
        flagged_ys = list()
        flagged_zs = list()
        flagged_cks = list()
        for i, x in enumerate(fliers_x):
            flagged_xs.append(tile.convert_easting(int(x)))
            flagged_ys.append(tile.convert_northing(int(fliers_y[i])))
            flagged_zs.append(fliers_z[i])
            flagged_cks.append(fliers_ck[i])
            # logger.debug("#%d: %f %f %d" % (i, xs[i], ys[i], zs[i]))

        logger.info("Initial lists length: %s, %s, %s, %s"
                    % (len(self.flagged_xs), len(self.flagged_ys), len(self.flagged_zs), len(self.flagged_cks)))

        # convert flagged nodes to geographic coords
        try:
            xs = np.array(flagged_xs)
            ys = np.array(flagged_ys)
            cks = np.array(flagged_cks)
            # logger.debug("xs: %s" % xs)
            # logger.debug("ys: %s" % ys)
            # logger.debug("zs: %s" % zs)

            # convert to geographic
            lonlat = np.array(loc2geo.TransformPoints(np.vstack((xs, ys)).transpose()), np.float64)

            # add checks
            lonlat[:, 2] = cks
            # store as list of list
            self.flagged_fliers += lonlat.tolist()
            self.flagged_xs += flagged_xs
            self.flagged_ys += flagged_ys
            self.flagged_zs += flagged_zs
            self.flagged_cks += flagged_cks

            logger.info("Detected %s possible fliers" % len(self.flagged_fliers))
            logger.info("Resulting lists lengths: %s, %s, %s, %s"
                        % (len(self.flagged_xs), len(self.flagged_ys), len(self.flagged_zs), len(self.flagged_cks)))
            # logger.debug(f"Flagged fliers: {self.flagged_fliers}")

        except Exception as e:
            raise RuntimeError("Unable to perform conversion of the flagged fliers to geographic: %s" % e)

    # ### FILTERING ###

    def apply_filters(self, s57_list: list, distance=1.0, delta_z=0.01) -> bool:

        logger.debug("filters -> distance: %s, delta_z: %s" % (distance, delta_z))

        if self.filter_designated:
            self._retrieve_designated()
            self._remove_designated(distance=distance, delta_z=delta_z)

        if self.filter_fff:
            self._remove_fff(s57_list=s57_list, distance=distance, delta_z=delta_z)

        return True

    def _retrieve_designated(self) -> bool:
        logger.debug("retrieving designated soundings ...")

        if self.grids.is_csar():
            logger.debug("retrieving designated soundings: CSAR -> skipped")
            return False

        if self.grids.is_vr():
            logger.debug("retrieving designated soundings: VR -> skipped")
            return False

        # for BAG SR, retrieve the list of designated soundings
        self.designated_soundings = self.grids.designated()
        nr_designated = len(self.designated_soundings)
        logger.debug("retrieved designated soundings: OK -> %d" % nr_designated)
        return True

    def _remove_designated(self, distance=1.0, delta_z=0.01):
        logger.debug("removing co-located designated soundings ...")

        grid_res = self.grids.cur_grids.bbox().res_x
        logger.debug("grid resolution: %.3f" % grid_res)

        nr_initially_flagged = len(self.flagged_fliers)
        logger.debug("initially flagged fliers: %d" % nr_initially_flagged)

        fliers = list()
        xs = list()
        ys = list()
        zs = list()
        cks = list()

        # for each flagged flier
        for flg_idx, flg in enumerate(self.flagged_fliers):
            flg = self.flagged_fliers[flg_idx]
            flg_x = self.flagged_xs[flg_idx]
            flg_y = self.flagged_ys[flg_idx]
            flg_z = self.flagged_zs[flg_idx]
            flg_ck = self.flagged_cks[flg_idx]
            logger.debug("[%d/%d] (%.3f, %.3f, %.3f)" % (flg_idx, nr_initially_flagged, flg_x, flg_y, flg_z))

            remove_flagged = False
            nr_designated = len(self.designated_soundings)
            # for each designated sounding
            for des_idx, designated in enumerate(self.designated_soundings):

                des_x = designated.x
                des_y = designated.y
                des_z = designated.designated_depth

                dist = math.hypot(flg_x - des_x, flg_y - des_y)
                if dist <= (grid_res * distance):
                    d_z = flg_z - des_z
                    if d_z <= delta_z:
                        logger.debug("|-> [%d/%d] (%.3f, %.3f, %.3f) -> dist: %.3f, delta z: %.3f"
                                     % (des_idx, nr_designated, des_x, des_y, des_z, dist, d_z))
                        remove_flagged = True
                        break

            if remove_flagged:
                continue

            fliers.append(flg)
            xs.append(flg_x)
            ys.append(flg_y)
            zs.append(flg_z)
            cks.append(flg_ck)

        nr_resulting_flagged = len(fliers)
        logger.debug("resulting flagged fliers: %d" % nr_resulting_flagged)

        self.flagged_fliers = fliers
        self.flagged_xs = xs
        self.flagged_ys = ys
        self.flagged_zs = zs
        self.flagged_cks = cks

    def _prepare_fff_list(self, s57_path: str, s57_idx: int):
        selected_features = list()

        # open the file
        s57 = S57()
        s57.set_input_filename(s57_path)
        s57.read()
        cur_s57 = s57.input_s57file

        # retrieve all features
        all_features = cur_s57.rec10s
        logger.debug("  [%d] all features: %d" % (s57_idx, len(all_features)))

        for ft in all_features:
            # skip if the feature has not position
            if (len(ft.geo2s) == 0) and (len(ft.geo3s) == 0):
                continue

            # skip if the feature has more than 1 node
            if (len(ft.geo2s) != 1) and (len(ft.geo3s) == 0):
                continue

            # logger.debug("%s" % ft.acronym)

            selected_features.append(ft)

        nr_selected_features = len(selected_features)
        logger.debug("  [%d] selected features: %d" % (s57_idx, nr_selected_features))

        return selected_features

    def _remove_fff(self, s57_list: list, distance=1.0, delta_z=0.01):
        logger.debug("removing specific co-located FFF ...")

        grid_res = self.grids.cur_grids.bbox().res_x
        logger.debug("grid resolution: %.3f" % grid_res)

        nr_initially_flagged = len(self.flagged_fliers)
        logger.debug("initially flagged fliers: %d" % nr_initially_flagged)

        fliers = list()
        xs = list()
        ys = list()
        zs = list()
        cks = list()

        # store the coordinate transform from geo to grid CRS (using GDAL)
        try:
            osr_grid = osr.SpatialReference()
            osr_grid.ImportFromWkt(self.grids.cur_grids.bbox().hrs)
            osr_geo = osr.SpatialReference()
            osr_geo.ImportFromEPSG(4326)  # geographic WGS84
            # self.loc2geo = osr.CoordinateTransformation(osr_bag, osr_geo)
            geo2loc = osr.CoordinateTransformation(osr_geo, osr_grid)

        except Exception as e:
            raise RuntimeError("unable to create a valid coords transform: %s" % e)

        list_selected_features = list()
        # for each S57 file
        for s57_idx, s57_path in enumerate(s57_list):
            list_selected_features.append(self._prepare_fff_list(s57_path=s57_path, s57_idx=s57_idx))

        # for each flagged flier
        for flg_idx, flg in enumerate(self.flagged_fliers):
            flg = self.flagged_fliers[flg_idx]
            flg_x = self.flagged_xs[flg_idx]
            flg_y = self.flagged_ys[flg_idx]
            flg_z = self.flagged_zs[flg_idx]
            flg_ck = self.flagged_cks[flg_idx]
            logger.debug("[%d/%d] (%.3f, %.3f, %.3f)" % (flg_idx, nr_initially_flagged, flg_x, flg_y, flg_z))

            remove_flagged = False
            # for each S57 file
            for selected_features in list_selected_features:

                nr_selected_features = len(selected_features)

                # first retrieve [long, lat, depth]
                for ft_idx, feature in enumerate(selected_features):

                    # manage soundings
                    if len(feature.geo3s) != 0:

                        # retrieve depth value
                        for geo3_idx, geo3 in enumerate(feature.geo3s):

                            try:
                                # invert sign due to the CSAR/BAG convention (depths are negative)
                                soundg_depth = -float(geo3.z)
                                # logger.debug("[%d][%d] %s -> depth value: %f"
                                #              % (ft_idx, geo3_idx, feature.acronym, soundg_depth))
                            except Exception:
                                logger.debug("[%d][%d] %s -> depth value: %s -> skip"
                                             % (ft_idx, geo3_idx, feature.acronym, geo3.z))
                                continue

                            if soundg_depth is None:
                                continue

                            # append [long, lat, depth]
                            soundg_geo = [[geo3.x, geo3.y, soundg_depth], ]
                            soundg_utm = np.array(geo2loc.TransformPoints(np.array(soundg_geo, np.float64)),
                                                  np.float64)

                            ft_x = soundg_utm[0][0]
                            ft_y = soundg_utm[0][1]
                            ft_z = soundg_depth
                            # logger.debug("  |-> [%d/%d] (%.3f, %.3f, %.3f)"
                            #              % (ft_idx, nr_selected_features, ft_x, ft_y, ft_z))

                            dist = math.hypot(flg_x - ft_x, flg_y - ft_y)
                            if dist <= (grid_res * distance):
                                d_z = flg_z - ft_z
                                if d_z <= delta_z:
                                    logger.debug("  |-> [%d/%d] (%.3f, %.3f, %.3f) -> dist: %.3f, delta z: %.3f"
                                                 % (ft_idx, nr_selected_features, ft_x, ft_y, ft_z, dist, d_z))
                                    remove_flagged = True
                                    break

                    # other features (no soundings)
                    else:
                        # retrieve depth value
                        s57_valsou = None
                        for attr in feature.attributes:

                            if attr.acronym == 'VALSOU':
                                try:
                                    # invert sign due to the CSAR/BAG convention (depths are negative)
                                    s57_valsou = -float(attr.value)
                                    # logger.debug("[%d] %s -> VALSOU value: %f"
                                    #              % (ft_idx, feature.acronym, s57_valsou))

                                except Exception:
                                    logger.debug("[%d] %s -> VALSOU value: %s -> skip"
                                                 % (ft_idx, feature.acronym, attr.value))
                                continue

                        if s57_valsou is None:
                            continue

                        # append [long, lat, depth]
                        valsou_geo = [[feature.centroid.x, feature.centroid.y, s57_valsou],]
                        valsou_utm = np.array(geo2loc.TransformPoints(np.array(valsou_geo, np.float64)),
                                              np.float64)

                        ft_x = valsou_utm[0][0]
                        ft_y = valsou_utm[0][1]
                        ft_z = s57_valsou
                        # logger.debug("  |-> [%d/%d] (%.3f, %.3f, %.3f)"
                        #              % (ft_idx, nr_selected_features, ft_x, ft_y, ft_z))

                        dist = math.hypot(flg_x - ft_x, flg_y - ft_y)
                        if dist <= (grid_res * distance):
                            d_z = flg_z - ft_z
                            if d_z <= delta_z:
                                logger.debug("  |-> [%d/%d] (%.3f, %.3f, %.3f) -> dist: %.3f, delta z: %.3f"
                                             % (ft_idx, nr_selected_features, ft_x, ft_y, ft_z, dist, d_z))
                                remove_flagged = True
                                break

            if remove_flagged:
                continue

            fliers.append(flg)
            xs.append(flg_x)
            ys.append(flg_y)
            zs.append(flg_z)
            cks.append(flg_ck)

        nr_resulting_flagged = len(fliers)
        logger.debug("resulting flagged fliers: %d" % nr_resulting_flagged)

        self.flagged_fliers = fliers
        self.flagged_xs = xs
        self.flagged_ys = ys
        self.flagged_zs = zs
        self.flagged_cks = cks
