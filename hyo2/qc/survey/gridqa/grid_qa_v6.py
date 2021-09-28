import os
import sys
from collections import OrderedDict, defaultdict
import numpy as np
# noinspection PyProtectedMember
from hyo2.grids._grids import FLOAT as GRIDS_FLOAT, DOUBLE as GRIDS_DOUBLE, \
    UINT32 as GRIDS_UINT32, UINT64 as GRIDS_UINT64, INT32 as GRIDS_INT32, INT64 as GRIDS_INT64

import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, ScalarFormatter

import warnings

warnings.simplefilter(action="ignore", category=RuntimeWarning)

import logging

from hyo2.qc.survey.gridqa.base_qa import BaseGridQA, qa_algos
from hyo2.qc.survey.gridqa.grid_qa_calc import calc_tvu_qc_dd, calc_tvu_qc_df, calc_tvu_qc_fd, calc_tvu_qc_ff, \
    calc_tvu_qc_a1_dd, calc_tvu_qc_a1_df, calc_tvu_qc_a1_fd, calc_tvu_qc_a1_ff, \
    calc_tvu_qc_a2b_dd, calc_tvu_qc_a2b_df, calc_tvu_qc_a2b_fd, calc_tvu_qc_a2b_ff, \
    calc_tvu_qc_c_dd, calc_tvu_qc_c_df, calc_tvu_qc_c_fd, calc_tvu_qc_c_ff
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class GridInfoV6:

    def __init__(self):
        self.title = str()
        self.histo_x_label = str()
        self.histo_y_label = str()
        self.basename = str()
        self.nr_of_nodes = 0
        self.nr_of_passed_nodes = 0
        self.pct_of_passed_nodes = None
        self.fail_left = None
        self.fail_right = None
        self.min = sys.maxsize
        self.max = -sys.maxsize - 1
        self.mode = None
        self.p2_5 = None
        self.q1 = None
        self.median = None
        self.q3 = None
        self.p97_5 = None

    def __repr__(self):
        msg = "<GridInfo>\n"

        msg += " <title: %s>\n" % self.title
        msg += " <histo_x_label: %s>\n" % self.histo_x_label
        msg += " <histo_y_label: %s>\n" % self.histo_y_label
        msg += " <nr_of_nodes: %s>\n" % self.nr_of_nodes

        if self.nr_of_passed_nodes is not None:
            msg += " <nr_of_passed_nodes: %s>\n" % self.nr_of_passed_nodes
        if self.pct_of_passed_nodes is not None:
            msg += " <pct_of_passed_nodes: %s>\n" % self.pct_of_passed_nodes
        if self.fail_left is not None:
            msg += " <fail_left: %s>\n" % self.fail_left
        if self.fail_right is not None:
            msg += " <fail_right: %s>\n" % self.fail_right

        if self.min is not None:
            msg += " <min: %s>\n" % self.min
        if self.max is not None:
            msg += " <max: %s>\n" % self.max
        if self.mode is not None:
            msg += " <mode: %s>\n" % self.mode
        if self.p2_5:
            msg += " <p2_5: %s>\n" % self.p2_5
        if self.q1 is not None:
            msg += " <q1: %s>\n" % self.q1
        if self.median is not None:
            msg += " <median: %s>\n" % self.median
        if self.q3:
            msg += " <q3: %s>\n" % self.q3
        if self.p97_5:
            msg += " <p97_5: %s>\n" % self.p97_5

        return msg


class GridQAV6(BaseGridQA):

    def __init__(self, grids, force_tvu_qc,
                 has_depth, has_product_uncertainty, has_density, has_tvu_qc, output_folder,
                 object_detection=True, full_coverage=True, hist_depth=True, hist_density=True, hist_tvu_qc=True,
                 hist_pct_res=True, hist_catzoc_a1=True, hist_catzoc_a2b=True, hist_catzoc_c=True,
                 depth_vs_density=True, depth_vs_tvu_qc=True, progress=None):
        super().__init__(grids=grids)
        self.type = qa_algos["GRID_QA_v6"]
        self.force_tvu_qc = force_tvu_qc
        self.objection_detection = object_detection
        self.full_coverage = full_coverage
        self.progress = progress

        self.has_depth = has_depth
        self.has_product_uncertainty = has_product_uncertainty
        self.has_density = has_density
        self.has_tvu_qc = has_tvu_qc

        self.output_folder = output_folder
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        self._hist_depth = hist_depth
        self._hist_density = hist_density
        self._hist_tvu_qc = hist_tvu_qc
        self._hist_pct_res = hist_pct_res
        self._hist_catzoc_a1 = hist_catzoc_a1
        self._hist_catzoc_a2b = hist_catzoc_a2b
        self._hist_catzoc_c = hist_catzoc_c
        self._depth_vs_density = depth_vs_density
        self._depth_vs_tvu_qc = depth_vs_tvu_qc
        logger.debug("output -> hist: depth %s, density %s, tvu qc %s, pct res %s, tvu catzoc %s" %
                     (self._hist_depth, self._hist_density, self._hist_tvu_qc, self._hist_pct_res,
                      self._hist_catzoc_a1))
        logger.debug("output -> vs: density %s, tvu qc %s" % (self._depth_vs_density, self._depth_vs_tvu_qc))

        self.bathy_first = True
        self.density_first = True
        self.tvu_qc_first = True
        self.pct_od_first = True
        self.pct_cc_first = True
        self.catzoc_a1_first = True
        self.catzoc_a2b_first = True
        self.catzoc_c_first = True

        self.bathy_values = None
        self.density_values = None
        self.tvu_qc_values = None
        self.pct_od_values = None
        self.pct_cc_values = None
        self.catzoc_a1_values = None
        self.catzoc_a2b_values = None
        self.catzoc_c_values = None

        self.bathy_mul = 1
        self.density_mul = 1
        self.tvu_qc_mul = 100
        self.pct_od_mul = 100
        self.pct_cc_mul = 100
        self.catzoc_a1_mul = 100
        self.catzoc_a2b_mul = 100
        self.catzoc_c_mul = 100

        self.bathy_dict = None
        self.density_dict = None
        self.tvu_qc_dict = None
        self.pct_od_dict = None
        self.pct_cc_dict = None
        self.catzoc_a1_dict = None
        self.catzoc_a2b_dict = None
        self.catzoc_c_dict = None

        self.bathy_info = None
        self.density_info = None
        self.tvu_qc_info = None
        self.pct_od_info = None
        self.pct_cc_info = None
        self.catzoc_a1_info = None
        self.catzoc_a2b_info = None
        self.catzoc_c_info = None

        self.tvu_qc_recalculated = False

        self.density_fig = None
        self.density_ax = None
        self.tvu_qc_fig = None
        self.tvu_qc_ax = None
        self.pct_od_fig = None
        self.pct_od_ax = None
        self.pct_cc_fig = None
        self.pct_cc_ax = None
        self.catzoc_a1_fig = None
        self.catzoc_a1_ax = None
        self.catzoc_a2b_fig = None
        self.catzoc_a2b_ax = None
        self.catzoc_c_fig = None
        self.catzoc_c_ax = None

    def run(self):
        logger.info("parameters for Grid QA: force-tvu-qc=%s, has_depth=%s, "
                    "has_product_uncertainty=%s, ""has_density=%s, has_tvu_qc=%s"
                    % (self.force_tvu_qc, self.has_depth, self.has_product_uncertainty, self.has_density,
                       self.has_tvu_qc))

        logger.debug("modes -> objection detection: %s, full_coverage: %s"
                     % (self.objection_detection, self.full_coverage))

        if not self.has_depth:
            logger.critical("unable to identify the depth layer")
            return False

        success = True

        self.bathy_dict = defaultdict(int)
        self.density_dict = defaultdict(int)
        self.tvu_qc_dict = defaultdict(int)
        self.pct_od_dict = defaultdict(int)
        self.pct_cc_dict = defaultdict(int)
        self.catzoc_a1_dict = defaultdict(int)
        self.catzoc_a2b_dict = defaultdict(int)
        self.catzoc_c_dict = defaultdict(int)

        self._init_infos()
        if self._depth_vs_density:
            self._init_plot_depth_vs_density()
        if self._depth_vs_tvu_qc:
            self._init_plot_depth_vs_tvu_qc()

        layers = list()
        if self.has_depth:
            layers.append(self.grids.depth_layer_name())
        if self.has_product_uncertainty:
            layers.append(self.grids.product_uncertainty_layer_name())
        if self.has_density:
            layers.append(self.grids.density_layer_name())
        if self.has_tvu_qc:
            layers.append(self.grids.tvu_qc_layer_name())
        logger.debug("selected layers: %s" % (layers,))

        while self.grids.read_next_tile(layers=layers):

            if self.progress is not None:
                if self.progress.value < 50:
                    self.progress.add(quantum=10)
                elif self.progress.value < 75:
                    self.progress.add(quantum=1)
                elif self.progress.value < 90:
                    self.progress.add(quantum=0.1)
                elif self.progress.value <= 99:
                    self.progress.add(quantum=0.0001)

            # logger.debug("new tile")
            self._run_slice()
            self.grids.clear_tiles()

            # self._memory_info()

        # bathy
        self.bathy_dict = OrderedDict(sorted(self.bathy_dict.items(), key=lambda t: t[0]))
        bathy_counts = np.array(list(self.bathy_dict.values()))
        bathy_density = bathy_counts / bathy_counts.sum()
        bathy_cumsum = np.cumsum(bathy_density)
        bathy_bins = np.array(list(self.bathy_dict.keys())) / self.bathy_mul
        self.bathy_info.mode = bathy_bins[bathy_counts.argmax()]
        # noinspection PyTypeChecker
        self.bathy_info.p2_5 = bathy_bins[np.searchsorted(bathy_cumsum, 0.025)]
        # noinspection PyTypeChecker
        self.bathy_info.q1 = bathy_bins[np.searchsorted(bathy_cumsum, 0.25)]
        # noinspection PyTypeChecker
        self.bathy_info.median = bathy_bins[np.searchsorted(bathy_cumsum, 0.5)]
        # noinspection PyTypeChecker
        self.bathy_info.q3 = bathy_bins[np.searchsorted(bathy_cumsum, 0.75)]
        # noinspection PyTypeChecker
        self.bathy_info.p97_5 = bathy_bins[np.searchsorted(bathy_cumsum, 0.975)]
        # print("bathy: %s" % self.bathy_dict)
        # print("bathy: %s" % self.bathy_info)
        # save the histogram as png
        if self._hist_depth:
            bathy_png_file = "%s.QAv6.depth.png" % os.path.splitext(self.grids.current_basename)[0]
            bathy_png_path = os.path.join(self.output_folder, bathy_png_file)
            bathy_png_path = Helper.truncate_too_long(bathy_png_path, left_truncation=True)
            GridQAV6.plot_hysto(layer_name="Depth", bins=bathy_bins, density=bathy_density,
                                bin_width=(1 / self.bathy_mul), grid_info=self.bathy_info, png_path=bathy_png_path)

        # density
        if self.has_density:
            self.density_dict = OrderedDict(sorted(self.density_dict.items(), key=lambda t: t[0]))
            # logger.debug("density dict: %s" % (self.density_dict, ))
            density_counts = np.array(list(self.density_dict.values()))
            density_density = density_counts / density_counts.sum()
            density_cumsum = np.cumsum(density_density)
            density_bins = np.array(list(self.density_dict.keys())) / self.density_mul

            if len(density_counts) > 0:

                self.density_info.mode = density_bins[density_counts.argmax()]
                # noinspection PyTypeChecker
                self.density_info.p2_5 = density_bins[np.searchsorted(density_cumsum, 0.025)]
                # noinspection PyTypeChecker
                self.density_info.q1 = density_bins[np.searchsorted(density_cumsum, 0.25)]
                # noinspection PyTypeChecker
                self.density_info.median = density_bins[np.searchsorted(density_cumsum, 0.5)]
                # noinspection PyTypeChecker
                self.density_info.q3 = density_bins[np.searchsorted(density_cumsum, 0.75)]
                # noinspection PyTypeChecker
                self.density_info.p97_5 = density_bins[np.searchsorted(density_cumsum, 0.975)]
                self.density_info.pct_of_passed_nodes = self.density_info.nr_of_passed_nodes / float(
                    self.density_info.nr_of_nodes)
                if self.density_info.pct_of_passed_nodes >= 0.95:
                    logger.debug("%.2f%% of grid nodes are populated with at least 5 soundings"
                                 % (self.density_info.pct_of_passed_nodes * 100.0))
                else:
                    logger.warning("%.2f%% of grid nodes are populated with at least 5 soundings (it should be >= 95%%)"
                                   % (self.density_info.pct_of_passed_nodes * 100.0))
                    success = False
                self.density_info.fail_left = 5
                # print("density: %s" % self.density_dict)
                # print("density: %s" % self.density_info)
                # save the histogram as png
                if self._hist_density:
                    density_png_file = "%s.QAv6.density.png" % os.path.splitext(self.grids.current_basename)[0]
                    density_png_path = os.path.join(self.output_folder, density_png_file)
                    density_png_path = Helper.truncate_too_long(density_png_path, left_truncation=True)
                    GridQAV6.plot_hysto(layer_name="Density", bins=density_bins, density=density_density,
                                        bin_width=(1 / self.density_mul), grid_info=self.density_info,
                                        png_path=density_png_path)
                # save the depth vs. density plot as png
                if self._depth_vs_density:
                    self._finish_plot_depth_vs_density()
                # delete the density array
                self.density_values = None

        # tvu qc
        if (self.has_tvu_qc and not self.force_tvu_qc) or self.has_product_uncertainty:

            if len(self.tvu_qc_dict.values()) > 0:

                self.tvu_qc_dict = OrderedDict(sorted(self.tvu_qc_dict.items(), key=lambda t: t[0]))
                tvu_qc_counts = np.array(list(self.tvu_qc_dict.values()))
                tvu_qc_density = tvu_qc_counts / tvu_qc_counts.sum()
                tvu_qc_cumsum = np.cumsum(tvu_qc_density)
                tvu_qc_bins = np.array(list(self.tvu_qc_dict.keys())) / self.tvu_qc_mul
                self.tvu_qc_info.mode = tvu_qc_bins[tvu_qc_counts.argmax()]
                # noinspection PyTypeChecker
                self.tvu_qc_info.p2_5 = tvu_qc_bins[np.searchsorted(tvu_qc_cumsum, 0.025)]
                # noinspection PyTypeChecker
                self.tvu_qc_info.q1 = tvu_qc_bins[np.searchsorted(tvu_qc_cumsum, 0.25)]
                # noinspection PyTypeChecker
                self.tvu_qc_info.median = tvu_qc_bins[np.searchsorted(tvu_qc_cumsum, 0.5)]
                # noinspection PyTypeChecker
                self.tvu_qc_info.q3 = tvu_qc_bins[np.searchsorted(tvu_qc_cumsum, 0.75)]
                # noinspection PyTypeChecker
                self.tvu_qc_info.p97_5 = tvu_qc_bins[np.searchsorted(tvu_qc_cumsum, 0.975)]
                self.tvu_qc_info.pct_of_passed_nodes = self.tvu_qc_info.nr_of_passed_nodes / float(
                    self.tvu_qc_info.nr_of_nodes)
                if self.tvu_qc_info.pct_of_passed_nodes >= 0.95:
                    logger.debug("%.2f%% of grid nodes meets the maximum allowable TVU"
                                 % (self.tvu_qc_info.pct_of_passed_nodes * 100.0))
                else:
                    logger.warning("%.2f%% of grid nodes meets the maximum allowable TVU (it should be >= 95%%)"
                                   % (self.tvu_qc_info.pct_of_passed_nodes * 100.0))
                    success = False
                self.tvu_qc_info.fail_right = 1
                # print("tvu qc: %s" % self.tvu_qc_dict)
                # print("tvu qc: %s" % self.tvu_qc_info)
                # save the histogram as png
                if self._hist_tvu_qc:
                    tvu_qc_png_file = "%s.QAv6.tvu_qc.png" % os.path.splitext(self.grids.current_basename)[0]
                    tvu_qc_png_path = os.path.join(self.output_folder, tvu_qc_png_file)
                    tvu_qc_png_path = Helper.truncate_too_long(tvu_qc_png_path, left_truncation=True)
                    GridQAV6.plot_hysto(layer_name="TVU QC", bins=tvu_qc_bins, density=tvu_qc_density,
                                        bin_width=(1 / self.tvu_qc_mul), grid_info=self.tvu_qc_info,
                                        png_path=tvu_qc_png_path)
                # save the depth vs. tvu qc plot as png
                if self._depth_vs_tvu_qc:
                    self._finish_plot_depth_vs_tvu_qc()
                # delete the array
                self.tvu_qc_values = None
                # del self.grids.tvu_qc

        # res pct
        if self.grids.is_vr():

            # - PCT OD
            if self.objection_detection:
                self.pct_od_dict = OrderedDict(sorted(self.pct_od_dict.items(), key=lambda t: t[0]))
                # logger.debug("%s" % dict(self.pct_od_dict))
                pct_od_counts = np.array(list(self.pct_od_dict.values()))
                pct_od_density = pct_od_counts / pct_od_counts.sum()
                pct_od_cumsum = np.cumsum(pct_od_density)
                pct_od_bins = np.array(list(self.pct_od_dict.keys())) / self.pct_od_mul
                self.pct_od_info.mode = pct_od_bins[pct_od_counts.argmax()]
                # noinspection PyTypeChecker
                self.pct_od_info.p2_5 = pct_od_bins[np.searchsorted(pct_od_cumsum, 0.025)]
                # noinspection PyTypeChecker
                self.pct_od_info.q1 = pct_od_bins[np.searchsorted(pct_od_cumsum, 0.25)]
                # noinspection PyTypeChecker
                self.pct_od_info.median = pct_od_bins[np.searchsorted(pct_od_cumsum, 0.5)]
                # noinspection PyTypeChecker
                self.pct_od_info.q3 = pct_od_bins[np.searchsorted(pct_od_cumsum, 0.75)]
                # noinspection PyTypeChecker
                self.pct_od_info.p97_5 = pct_od_bins[np.searchsorted(pct_od_cumsum, 0.975)]
                self.pct_od_info.pct_of_passed_nodes = self.pct_od_info.nr_of_passed_nodes / float(
                    self.pct_od_info.nr_of_nodes)
                if self.pct_od_info.pct_of_passed_nodes >= 0.95:
                    logger.debug("%.2f%% of grid nodes meets the coarsest allowable resolution"
                                 % (self.pct_od_info.pct_of_passed_nodes * 100.0))
                else:
                    logger.warning("%.2f%% of grid nodes meets the coarsest allowable resolution (it should be >= 95%%)"
                                   % (self.pct_od_info.pct_of_passed_nodes * 100.0))
                    success = False
                self.pct_od_info.fail_right = 1
                # print("pct od: %s" % self.pct_od_dict)
                # print("pct od: %s" % self.pct_od_info)
                # save the histogram as png
                if self._hist_pct_res:
                    pct_od_png_file = "%s.QAv6.pct_res.obj_det.png" % os.path.splitext(self.grids.current_basename)[0]
                    pct_od_png_path = os.path.join(self.output_folder, pct_od_png_file)
                    pct_od_png_path = Helper.truncate_too_long(pct_od_png_path, left_truncation=True)
                    GridQAV6.plot_hysto(layer_name="RES OD", bins=pct_od_bins, density=pct_od_density,
                                        bin_width=0.1, grid_info=self.pct_od_info,
                                        png_path=pct_od_png_path)
                # delete the array
                self.pct_od_values = None

            # - PCT CC
            if self.full_coverage:
                self.pct_cc_dict = OrderedDict(sorted(self.pct_cc_dict.items(), key=lambda t: t[0]))
                # logger.debug("%s" % dict(self.pct_cc_dict))
                pct_cc_counts = np.array(list(self.pct_cc_dict.values()))
                pct_cc_density = pct_cc_counts / pct_cc_counts.sum()
                pct_cc_cumsum = np.cumsum(pct_cc_density)
                pct_cc_bins = np.array(list(self.pct_cc_dict.keys())) / self.pct_cc_mul
                self.pct_cc_info.mode = pct_cc_bins[pct_cc_counts.argmax()]
                # noinspection PyTypeChecker
                self.pct_cc_info.p2_5 = pct_cc_bins[np.searchsorted(pct_cc_cumsum, 0.025)]
                # noinspection PyTypeChecker
                self.pct_cc_info.q1 = pct_cc_bins[np.searchsorted(pct_cc_cumsum, 0.25)]
                # noinspection PyTypeChecker
                self.pct_cc_info.median = pct_cc_bins[np.searchsorted(pct_cc_cumsum, 0.5)]
                # noinspection PyTypeChecker
                self.pct_cc_info.q3 = pct_cc_bins[np.searchsorted(pct_cc_cumsum, 0.75)]
                # noinspection PyTypeChecker
                self.pct_cc_info.p97_5 = pct_cc_bins[np.searchsorted(pct_cc_cumsum, 0.975)]
                self.pct_cc_info.pct_of_passed_nodes = self.pct_cc_info.nr_of_passed_nodes / float(
                    self.pct_cc_info.nr_of_nodes)
                if self.pct_cc_info.pct_of_passed_nodes >= 0.95:
                    logger.debug("%.2f%% of grid nodes meets the coarsest allowable resolution"
                                 % (self.pct_cc_info.pct_of_passed_nodes * 100.0))
                else:
                    logger.warning("%.2f%% of grid nodes meets the coarsest allowable resolution (it should be >= 95%%)"
                                   % (self.pct_cc_info.pct_of_passed_nodes * 100.0))
                    success = False
                self.pct_cc_info.fail_right = 1
                # print("pct od: %s" % self.pct_cc_dict)
                # print("pct od: %s" % self.pct_cc_info)
                # save the histogram as png
                if self._hist_pct_res:
                    pct_cc_png_file = "%s.QAv6.pct_res.full_cov.png" % os.path.splitext(self.grids.current_basename)[0]
                    pct_cc_png_path = os.path.join(self.output_folder, pct_cc_png_file)
                    pct_cc_png_path = Helper.truncate_too_long(pct_cc_png_path, left_truncation=True)
                    GridQAV6.plot_hysto(layer_name="RES FC", bins=pct_cc_bins, density=pct_cc_density,
                                        bin_width=0.1, grid_info=self.pct_cc_info,
                                        png_path=pct_cc_png_path)
                # delete the array
                self.pct_cc_values = None

        # catzoc a1
        if self.has_product_uncertainty and self._hist_catzoc_a1:

            if len(self.catzoc_a1_dict.values()) > 0:

                self.catzoc_a1_dict = OrderedDict(sorted(self.catzoc_a1_dict.items(), key=lambda t: t[0]))
                catzoc_a1_counts = np.array(list(self.catzoc_a1_dict.values()))
                catzoc_a1_density = catzoc_a1_counts / catzoc_a1_counts.sum()
                catzoc_a1_cumsum = np.cumsum(catzoc_a1_density)
                catzoc_a1_bins = np.array(list(self.catzoc_a1_dict.keys())) / self.catzoc_a1_mul
                self.catzoc_a1_info.mode = catzoc_a1_bins[catzoc_a1_counts.argmax()]
                # noinspection PyTypeChecker
                self.catzoc_a1_info.p2_5 = catzoc_a1_bins[np.searchsorted(catzoc_a1_cumsum, 0.025)]
                # noinspection PyTypeChecker
                self.catzoc_a1_info.q1 = catzoc_a1_bins[np.searchsorted(catzoc_a1_cumsum, 0.25)]
                # noinspection PyTypeChecker
                self.catzoc_a1_info.median = catzoc_a1_bins[np.searchsorted(catzoc_a1_cumsum, 0.5)]
                # noinspection PyTypeChecker
                self.catzoc_a1_info.q3 = catzoc_a1_bins[np.searchsorted(catzoc_a1_cumsum, 0.75)]
                # noinspection PyTypeChecker
                self.catzoc_a1_info.p97_5 = catzoc_a1_bins[np.searchsorted(catzoc_a1_cumsum, 0.975)]
                self.catzoc_a1_info.pct_of_passed_nodes = self.catzoc_a1_info.nr_of_passed_nodes / float(
                    self.catzoc_a1_info.nr_of_nodes)
                if self.catzoc_a1_info.pct_of_passed_nodes >= 0.95:
                    logger.debug("%.2f%% of grid nodes meets the maximum allowable TVU per CATZOC A1"
                                 % (self.catzoc_a1_info.pct_of_passed_nodes * 100.0))
                else:
                    logger.warning("%.2f%% of grid nodes meets the maximum allowable TVU per CATZOC A1"
                                   "(it should be >= 95%%)"
                                   % (self.catzoc_a1_info.pct_of_passed_nodes * 100.0))
                    success = False
                self.catzoc_a1_info.fail_right = 1
                # print("catzoc a1: %s" % self.catzoc_a1_dict)
                # print("catzoc a1: %s" % self.catzoc_a1_info)
                # save the histogram as png
                if self._hist_catzoc_a1:
                    catzoca1_png_file = "%s.QAv6.tvu_catzoc_a1.png" % os.path.splitext(self.grids.current_basename)[
                        0]
                    catzoca1_png_path = os.path.join(self.output_folder, catzoca1_png_file)
                    catzoca1_png_path = Helper.truncate_too_long(catzoca1_png_path, left_truncation=True)
                    GridQAV6.plot_hysto(layer_name="TVU CATZOC A1", bins=catzoc_a1_bins, density=catzoc_a1_density,
                                        bin_width=(1 / self.catzoc_a1_mul), grid_info=self.catzoc_a1_info,
                                        png_path=catzoca1_png_path, hist_color='#bababa')

        # catzoc a2 / b (a2b)
        if self.has_product_uncertainty and self._hist_catzoc_a2b:

            if len(self.catzoc_a2b_dict.values()) > 0:

                self.catzoc_a2b_dict = OrderedDict(sorted(self.catzoc_a2b_dict.items(), key=lambda t: t[0]))
                catzoc_a2b_counts = np.array(list(self.catzoc_a2b_dict.values()))
                catzoc_a2b_density = catzoc_a2b_counts / catzoc_a2b_counts.sum()
                catzoc_a2b_cumsum = np.cumsum(catzoc_a2b_density)
                catzoc_a2b_bins = np.array(list(self.catzoc_a2b_dict.keys())) / self.catzoc_a2b_mul
                self.catzoc_a2b_info.mode = catzoc_a2b_bins[catzoc_a2b_counts.argmax()]
                # noinspection PyTypeChecker
                self.catzoc_a2b_info.p2_5 = catzoc_a2b_bins[np.searchsorted(catzoc_a2b_cumsum, 0.025)]
                # noinspection PyTypeChecker
                self.catzoc_a2b_info.q1 = catzoc_a2b_bins[np.searchsorted(catzoc_a2b_cumsum, 0.25)]
                # noinspection PyTypeChecker
                self.catzoc_a2b_info.median = catzoc_a2b_bins[np.searchsorted(catzoc_a2b_cumsum, 0.5)]
                # noinspection PyTypeChecker
                self.catzoc_a2b_info.q3 = catzoc_a2b_bins[np.searchsorted(catzoc_a2b_cumsum, 0.75)]
                # noinspection PyTypeChecker
                self.catzoc_a2b_info.p97_5 = catzoc_a2b_bins[np.searchsorted(catzoc_a2b_cumsum, 0.975)]
                self.catzoc_a2b_info.pct_of_passed_nodes = self.catzoc_a2b_info.nr_of_passed_nodes / float(
                    self.catzoc_a2b_info.nr_of_nodes)
                if self.catzoc_a2b_info.pct_of_passed_nodes >= 0.95:
                    logger.debug("%.2f%% of grid nodes meets the maximum allowable TVU per CATZOC A2 / B"
                                 % (self.catzoc_a2b_info.pct_of_passed_nodes * 100.0))
                else:
                    logger.warning("%.2f%% of grid nodes meets the maximum allowable TVU per CATZOC A2 /B"
                                   "(it should be >= 95%%)"
                                   % (self.catzoc_a2b_info.pct_of_passed_nodes * 100.0))
                    success = False
                self.catzoc_a2b_info.fail_right = 1
                # print("catzoc a2b: %s" % self.catzoc_a2b_dict)
                # print("catzoc a2b: %s" % self.catzoc_a2b_info)
                # save the histogram as png
                if self._hist_catzoc_a2b:
                    catzoca2b_png_file = "%s.QAv6.tvu_catzoc_a2b.png" % \
                                         os.path.splitext(self.grids.current_basename)[0]
                    catzoca2b_png_path = os.path.join(self.output_folder, catzoca2b_png_file)
                    catzoca2b_png_path = Helper.truncate_too_long(catzoca2b_png_path, left_truncation=True)
                    GridQAV6.plot_hysto(layer_name="TVU CATZOC A2 / B", bins=catzoc_a2b_bins,
                                        density=catzoc_a2b_density, bin_width=(1 / self.catzoc_a2b_mul),
                                        grid_info=self.catzoc_a2b_info, png_path=catzoca2b_png_path,
                                        hist_color='#bababa')

        # catzoc c
        if self.has_product_uncertainty and self._hist_catzoc_c:

            if len(self.catzoc_c_dict.values()) > 0:

                self.catzoc_c_dict = OrderedDict(sorted(self.catzoc_c_dict.items(), key=lambda t: t[0]))
                catzoc_c_counts = np.array(list(self.catzoc_c_dict.values()))
                catzoc_c_density = catzoc_c_counts / catzoc_c_counts.sum()
                catzoc_c_cumsum = np.cumsum(catzoc_c_density)
                catzoc_c_bins = np.array(list(self.catzoc_c_dict.keys())) / self.catzoc_c_mul
                self.catzoc_c_info.mode = catzoc_c_bins[catzoc_c_counts.argmax()]
                # noinspection PyTypeChecker
                self.catzoc_c_info.p2_5 = catzoc_c_bins[np.searchsorted(catzoc_c_cumsum, 0.025)]
                # noinspection PyTypeChecker
                self.catzoc_c_info.q1 = catzoc_c_bins[np.searchsorted(catzoc_c_cumsum, 0.25)]
                # noinspection PyTypeChecker
                self.catzoc_c_info.median = catzoc_c_bins[np.searchsorted(catzoc_c_cumsum, 0.5)]
                # noinspection PyTypeChecker
                self.catzoc_c_info.q3 = catzoc_c_bins[np.searchsorted(catzoc_c_cumsum, 0.75)]
                # noinspection PyTypeChecker
                self.catzoc_c_info.p97_5 = catzoc_c_bins[np.searchsorted(catzoc_c_cumsum, 0.975)]
                self.catzoc_c_info.pct_of_passed_nodes = self.catzoc_c_info.nr_of_passed_nodes / float(
                    self.catzoc_c_info.nr_of_nodes)
                if self.catzoc_c_info.pct_of_passed_nodes >= 0.95:
                    logger.debug("%.2f%% of grid nodes meets the maximum allowable TVU per CATZOC C"
                                 % (self.catzoc_c_info.pct_of_passed_nodes * 100.0))
                else:
                    logger.warning("%.2f%% of grid nodes meets the maximum allowable TVU per CATZOC C"
                                   "(it should be >= 95%%)"
                                   % (self.catzoc_c_info.pct_of_passed_nodes * 100.0))
                    success = False
                self.catzoc_c_info.fail_right = 1
                # print("catzoc c: %s" % self.catzoc_c_dict)
                # print("catzoc c: %s" % self.catzoc_c_info)
                # save the histogram as png
                if self._hist_catzoc_c:
                    catzocc_png_file = "%s.QAv6.tvu_catzoc_c.png" % os.path.splitext(self.grids.current_basename)[0]
                    catzocc_png_path = os.path.join(self.output_folder, catzocc_png_file)
                    catzocc_png_path = Helper.truncate_too_long(catzocc_png_path, left_truncation=True)
                    GridQAV6.plot_hysto(layer_name="TVU CATZOC C", bins=catzoc_c_bins, density=catzoc_c_density,
                                        bin_width=(1 / self.catzoc_c_mul), grid_info=self.catzoc_c_info,
                                        png_path=catzocc_png_path, hist_color='#bababa')

        return success

    def _run_slice(self):

        self._create_arrays()
        if len(self.bathy_values) == 0:
            logger.warning("missing depth values!")
            return

        # bathy
        self.bathy_info.nr_of_nodes += len(self.bathy_values)
        if np.min(self.bathy_values) < self.bathy_info.min:
            self.bathy_info.min = np.min(self.bathy_values)
        if np.max(self.bathy_values) > self.bathy_info.max:
            self.bathy_info.max = np.max(self.bathy_values)
        if self.bathy_first:
            self.bathy_first = False
            if (self.bathy_info.max - self.bathy_info.min) < 50:
                self.bathy_mul = 10
        # self.bathy_dict = populate_bathy_dict(self.bathy_values, self.bathy_dict, self.bathy_mul)
        for depth in self.bathy_values:
            depth_key = int(round(depth * self.bathy_mul))
            # print(depth_key)
            self.bathy_dict[depth_key] += 1

        # density
        if self.has_density:
            if len(self.density_values) > 0:
                self.density_info.nr_of_nodes += len(self.density_values)
                self.density_info.nr_of_passed_nodes += np.greater_equal(self.density_values, 5).sum()
                if np.min(self.density_values) < self.density_info.min:
                    self.density_info.min = np.min(self.density_values)
                if np.max(self.density_values) > self.density_info.max:
                    self.density_info.max = np.max(self.density_values)

                for density in self.density_values:
                    density_key = density
                    self.density_dict[density_key] += 1

                if self._depth_vs_density:
                    self._update_plot_depth_vs_density()

        # tvu qc
        if (self.has_tvu_qc and not self.force_tvu_qc) or self.has_product_uncertainty:
            if len(self.tvu_qc_values) > 0:
                self.tvu_qc_info.nr_of_nodes += len(self.tvu_qc_values)
                self.tvu_qc_info.nr_of_passed_nodes += np.less_equal(self.tvu_qc_values, 1).sum()
                if np.min(self.tvu_qc_values) < self.tvu_qc_info.min:
                    self.tvu_qc_info.min = np.min(self.tvu_qc_values)
                if np.max(self.tvu_qc_values) > self.tvu_qc_info.max:
                    self.tvu_qc_info.max = np.max(self.tvu_qc_values)

                for tvu_qc in self.tvu_qc_values:
                    tvu_qc_key = int(round(tvu_qc * self.tvu_qc_mul))
                    self.tvu_qc_dict[tvu_qc_key] += 1

                if self._depth_vs_tvu_qc:
                    self._update_plot_depth_vs_tvu_qc()

        # res pct
        if self.grids.is_vr():

            # - pct od
            if self.objection_detection:
                if len(self.pct_od_values) > 0:

                    # logger.debug("populating pct od dict")
                    self.pct_od_info.nr_of_nodes += len(self.pct_od_values)
                    self.pct_od_info.nr_of_passed_nodes += np.less_equal(self.pct_od_values, 1).sum()
                    if np.min(self.pct_od_values) < self.pct_od_info.min:
                        self.pct_od_info.min = np.min(self.pct_od_values)
                    if np.max(self.pct_od_values) > self.pct_od_info.max:
                        self.pct_od_info.max = np.max(self.pct_od_values)

                    for pct_od in self.pct_od_values:
                        # logger.debug("- value: %s" % pct_od)
                        pct_od_key = round(pct_od * self.pct_od_mul)
                        if np.isfinite(pct_od_key):
                            self.pct_od_dict[int(pct_od_key)] += 1

            # - pct cc
            if self.full_coverage:
                if len(self.pct_cc_values) > 0:

                    # logger.debug("populating pct od dict")
                    self.pct_cc_info.nr_of_nodes += len(self.pct_cc_values)
                    self.pct_cc_info.nr_of_passed_nodes += np.less_equal(self.pct_cc_values, 1).sum()
                    if np.min(self.pct_cc_values) < self.pct_cc_info.min:
                        self.pct_cc_info.min = np.min(self.pct_cc_values)
                    if np.max(self.pct_cc_values) > self.pct_cc_info.max:
                        self.pct_cc_info.max = np.max(self.pct_cc_values)

                    for pct_cc in self.pct_cc_values:
                        # logger.debug("- value: %s" % pct_cc)
                        pct_cc_key = round(pct_cc * self.pct_cc_mul)
                        if np.isfinite(pct_cc_key):
                            self.pct_cc_dict[int(pct_cc_key)] += 1

        # catzoc a1
        if self.has_product_uncertainty and self._hist_catzoc_a1:
            if len(self.catzoc_a1_values) > 0:
                self.catzoc_a1_info.nr_of_nodes += len(self.catzoc_a1_values)
                self.catzoc_a1_info.nr_of_passed_nodes += np.less_equal(self.catzoc_a1_values, 1).sum()
                if np.min(self.catzoc_a1_values) < self.catzoc_a1_info.min:
                    self.catzoc_a1_info.min = np.min(self.catzoc_a1_values)
                if np.max(self.catzoc_a1_values) > self.catzoc_a1_info.max:
                    self.catzoc_a1_info.max = np.max(self.catzoc_a1_values)

                for catzoc_a1 in self.catzoc_a1_values:
                    catzoc_a1_key = int(round(catzoc_a1 * self.catzoc_a1_mul))
                    self.catzoc_a1_dict[catzoc_a1_key] += 1

        # catzoc a2 / catzoc b (a2b)
        if self.has_product_uncertainty and self._hist_catzoc_a2b:
            if len(self.catzoc_a2b_values) > 0:
                self.catzoc_a2b_info.nr_of_nodes += len(self.catzoc_a2b_values)
                self.catzoc_a2b_info.nr_of_passed_nodes += np.less_equal(self.catzoc_a2b_values, 1).sum()
                if np.min(self.catzoc_a2b_values) < self.catzoc_a2b_info.min:
                    self.catzoc_a2b_info.min = np.min(self.catzoc_a2b_values)
                if np.max(self.catzoc_a2b_values) > self.catzoc_a2b_info.max:
                    self.catzoc_a2b_info.max = np.max(self.catzoc_a2b_values)

                for catzoc_a2b in self.catzoc_a2b_values:
                    catzoc_a2b_key = int(round(catzoc_a2b * self.catzoc_a2b_mul))
                    self.catzoc_a2b_dict[catzoc_a2b_key] += 1

        # catzoc c
        if self.has_product_uncertainty and self._hist_catzoc_c:
            if len(self.catzoc_c_values) > 0:
                self.catzoc_c_info.nr_of_nodes += len(self.catzoc_c_values)
                self.catzoc_c_info.nr_of_passed_nodes += np.less_equal(self.catzoc_c_values, 1).sum()
                if np.min(self.catzoc_c_values) < self.catzoc_c_info.min:
                    self.catzoc_c_info.min = np.min(self.catzoc_c_values)
                if np.max(self.catzoc_c_values) > self.catzoc_c_info.max:
                    self.catzoc_c_info.max = np.max(self.catzoc_c_values)

                for catzoc_c in self.catzoc_c_values:
                    catzoc_c_key = int(round(catzoc_c * self.catzoc_c_mul))
                    self.catzoc_c_dict[catzoc_c_key] += 1

    def _init_infos(self):

        self.bathy_info = GridInfoV6()
        self.bathy_info.title = "Depth Distribution"
        self.bathy_info.histo_x_label = "Depth"
        self.bathy_info.histo_y_label = "Percentage of nodes in each depth group"
        self.bathy_info.basename = self.grids.current_basename

        self.density_info = GridInfoV6()
        self.density_info.title = "Data Density"
        self.density_info.histo_x_label = "Soundings per node"
        self.density_info.histo_y_label = "Percentage of nodes in each sounding density group"
        self.density_info.basename = self.grids.current_basename

        self.tvu_qc_info = GridInfoV6()
        self.tvu_qc_info.title = "Uncertainty Standards - NOAA HSSD"
        self.tvu_qc_info.histo_x_label = "Node uncertainty as a fraction of allowable IHO TVU"
        self.tvu_qc_info.histo_y_label = "Percentage of nodes in each uncertainty group"
        self.tvu_qc_info.basename = self.grids.current_basename

        self.catzoc_a1_info = GridInfoV6()
        self.catzoc_a1_info.title = "Uncertainty Standards - CATZOC A1"
        self.catzoc_a1_info.histo_x_label = "Node uncertainty as a fraction of allowable TVU, CATZOC A1"
        self.catzoc_a1_info.histo_y_label = "Percentage of nodes in each uncertainty group"
        self.catzoc_a1_info.basename = self.grids.current_basename

        self.catzoc_a2b_info = GridInfoV6()
        self.catzoc_a2b_info.title = "Uncertainty Standards - CATZOC A2/B"
        self.catzoc_a2b_info.histo_x_label = "Node uncertainty as a fraction of allowable TVU, CATZOC A2/B"
        self.catzoc_a2b_info.histo_y_label = "Percentage of nodes in each uncertainty group"
        self.catzoc_a2b_info.basename = self.grids.current_basename

        self.catzoc_c_info = GridInfoV6()
        self.catzoc_c_info.title = "Uncertainty Standards - CATZOC C"
        self.catzoc_c_info.histo_x_label = "Node uncertainty as a fraction of allowable TVU, CATZOC C"
        self.catzoc_c_info.histo_y_label = "Percentage of nodes in each uncertainty group"
        self.catzoc_c_info.basename = self.grids.current_basename

        if self.objection_detection:
            self.pct_od_info = GridInfoV6()
            self.pct_od_info.title = "Resolution Requirements - Object Detection"
            self.pct_od_info.histo_x_label = "Node resolution as a fraction of allowable"
            self.pct_od_info.histo_y_label = "Percentage of nodes in each resolution group"
            self.pct_od_info.basename = self.grids.current_basename

        if self.full_coverage:
            self.pct_cc_info = GridInfoV6()
            self.pct_cc_info.title = "Resolution Requirements - Full Coverage"
            self.pct_cc_info.histo_x_label = "Node resolution as a fraction of allowable"
            self.pct_cc_info.histo_y_label = "Percentage of nodes in each resolution group"
            self.pct_cc_info.basename = self.grids.current_basename

    def _create_arrays(self):
        """Take care to populate the various arrays"""

        tile = self.grids.tiles[0]
        # logger.debug("types: %s" % (list(tile.types),))

        # - depth layer

        depth_type = tile.type(self.grids.depth_layer_name())
        depth_idx = tile.band_index(self.grids.depth_layer_name())
        # logger.debug("depth layer: %s [idx: %s]" % (self.grids.grid_data_type(depth_type), depth_idx))

        if depth_type == GRIDS_DOUBLE:
            self.bathy_values = -tile.doubles[depth_idx][tile.doubles[depth_idx] != tile.doubles_nodata[depth_idx]]

        elif depth_type == GRIDS_FLOAT:
            self.bathy_values = -tile.floats[depth_idx][tile.floats[depth_idx] != tile.floats_nodata[depth_idx]]

        elif depth_type == "KLUSTER_FLOAT32":
            self.bathy_values = tile.layers[depth_idx][~np.isnan(tile.layers[depth_idx])]

        else:
            raise RuntimeError("Unsupported data type for bathy: %s" % depth_type)
        logger.debug('depth values: %s [%s]' % (self.bathy_values.shape, self.bathy_values.dtype))

        # - density layer

        if self.has_density:
            density_type = tile.type(self.grids.density_layer_name())
            density_idx = tile.band_index(self.grids.density_layer_name())
            # logger.debug("density layer: %s [idx: %s]" % (self.grids.grid_data_type(density_type), density_idx))

            if density_type == GRIDS_UINT32:
                self.density_values = \
                    tile.uint32s[density_idx][tile.uint32s[density_idx] != tile.uint32s_nodata[density_idx]]
                if len(self.density_values) == 0:
                    logger.info("No density values")
            elif density_type == GRIDS_UINT64:
                self.density_values = \
                    tile.uint64s[density_idx][tile.uint64s[density_idx] != tile.uint64s_nodata[density_idx]]
                if len(self.density_values) == 0:
                    logger.info("No density values")
            elif density_type == GRIDS_INT32:
                self.density_values = \
                    tile.int32s[density_idx][tile.int32s[density_idx] != tile.int32s_nodata[density_idx]]
                if len(self.density_values) == 0:
                    logger.info("No density values")
            elif density_type == GRIDS_INT64:
                self.density_values = \
                    tile.int64s[density_idx][tile.int64s[density_idx] != tile.int64s_nodata[density_idx]]
                if len(self.density_values) == 0:
                    logger.info("No density values")
            else:
                raise RuntimeError("Unsupported data type for density: %s" % density_type)
            # logger.debug('density values: %s' % len(self.density_values))

        # tvu qc

        if (self.has_tvu_qc and not self.force_tvu_qc) or self.has_product_uncertainty:

            # calculate the TVU QC layer
            if self.has_tvu_qc and not self.force_tvu_qc:

                tvu_qc_type = tile.type(self.grids.tvu_qc_layer_name())
                tvu_qc_idx = tile.band_index(self.grids.tvu_qc_layer_name())
                # logger.debug("tvu qc layer: %s [idx: %s]" % (self.grids.grid_data_type(tvu_qc_type), tvu_qc_idx))
                if tvu_qc_type == GRIDS_DOUBLE:
                    self.tvu_qc_values = \
                        tile.doubles[tvu_qc_idx][tile.doubles[tvu_qc_idx] != tile.doubles_nodata[tvu_qc_idx]]
                    if len(self.tvu_qc_values) == 0:
                        logger.info("No TVU QC values")
                elif tvu_qc_type == GRIDS_FLOAT:
                    self.tvu_qc_values = \
                        tile.floats[tvu_qc_idx][tile.floats[tvu_qc_idx] != tile.floats_nodata[tvu_qc_idx]]
                    if len(self.tvu_qc_values) == 0:
                        logger.info("No TVU QC values")
                else:
                    raise RuntimeError("Unsupported data type for TVU QC")

            elif self.has_product_uncertainty:

                # logger.info("recalculating TVU QC")
                uncertainty_type = tile.type(self.grids.product_uncertainty_layer_name())
                uncertainty_idx = tile.band_index(self.grids.product_uncertainty_layer_name())
                # logger.debug("uncertainty layer: %s [idx: %s]
                #  % (self.grids.grid_data_type(uncertainty_type), uncertainty_idx))

                if uncertainty_type == GRIDS_DOUBLE:
                    if depth_type == GRIDS_DOUBLE:
                        self.grids.tvu_qc = np.empty_like(tile.doubles[depth_idx])
                        calc_tvu_qc_dd(-tile.doubles[depth_idx],
                                       tile.doubles[uncertainty_idx],
                                       tile.doubles_nodata[uncertainty_idx],
                                       self.grids.tvu_qc)

                    else:  # float
                        self.grids.tvu_qc = np.empty_like(tile.floats[depth_idx])
                        calc_tvu_qc_fd(-tile.floats[depth_idx],
                                       tile.doubles[uncertainty_idx],
                                       tile.doubles_nodata[uncertainty_idx],
                                       self.grids.tvu_qc)

                elif uncertainty_type == GRIDS_FLOAT:
                    if depth_type == GRIDS_DOUBLE:
                        self.grids.tvu_qc = np.empty_like(tile.doubles[depth_idx])
                        calc_tvu_qc_df(-tile.doubles[depth_idx],
                                       tile.floats[uncertainty_idx],
                                       tile.floats_nodata[uncertainty_idx],
                                       self.grids.tvu_qc)

                    else:  # float
                        self.grids.tvu_qc = np.empty_like(tile.floats[depth_idx])
                        calc_tvu_qc_ff(-tile.floats[depth_idx],
                                       tile.floats[uncertainty_idx],
                                       tile.floats_nodata[uncertainty_idx],
                                       self.grids.tvu_qc)

                elif uncertainty_type == "KLUSTER_FLOAT32":
                    self.grids.tvu_qc = np.empty_like(tile.layers[depth_idx])
                    calc_tvu_qc_ff(-tile.layers[depth_idx],
                                   tile.layers[uncertainty_idx],
                                   np.nan,
                                   self.grids.tvu_qc)

                else:
                    raise RuntimeError("Unsupported data type for uncertainty: %s" % uncertainty_type)
                # logger.debug(self.grids.tvu_qc)

                self.tvu_qc_values = np.fabs(self.grids.tvu_qc[~np.isnan(self.grids.tvu_qc)])
                self.grids.tvu_qc = None
                # logger.debug("%s" % (self.tvu_qc_values.shape, ))
                self.tvu_qc_recalculated = True
                self.tvu_qc_info.histo_x_label = "Node uncertainty as a fraction of allowable IHO TVU (computed)"

            else:
                raise RuntimeError("invalid case for TVU QC calculation")

            # logger.debug('tvu qc values: %s' % len(self.tvu_qc_values))

        # catzoc
        if self.has_product_uncertainty and self._hist_catzoc_a1 or self._hist_catzoc_a2b or self._hist_catzoc_c:

            # logger.info("recalculating TVU QC")
            uncertainty_type = tile.type(self.grids.product_uncertainty_layer_name())
            uncertainty_idx = tile.band_index(self.grids.product_uncertainty_layer_name())
            # logger.debug("uncertainty layer: %s [idx: %s]
            #  % (self.grids.grid_data_type(uncertainty_type), uncertainty_idx))

            if uncertainty_type == GRIDS_DOUBLE:
                if depth_type == GRIDS_DOUBLE:
                    self.grids.tvu_qc_a1 = np.empty_like(tile.doubles[depth_idx])
                    calc_tvu_qc_a1_dd(-tile.doubles[depth_idx],
                                      tile.doubles[uncertainty_idx],
                                      tile.doubles_nodata[uncertainty_idx],
                                      self.grids.tvu_qc_a1)
                    self.grids.tvu_qc_a2b = np.empty_like(tile.doubles[depth_idx])
                    calc_tvu_qc_a2b_dd(-tile.doubles[depth_idx],
                                       tile.doubles[uncertainty_idx],
                                       tile.doubles_nodata[uncertainty_idx],
                                       self.grids.tvu_qc_a2b)
                    self.grids.tvu_qc_c = np.empty_like(tile.doubles[depth_idx])
                    calc_tvu_qc_c_dd(-tile.doubles[depth_idx],
                                     tile.doubles[uncertainty_idx],
                                     tile.doubles_nodata[uncertainty_idx],
                                     self.grids.tvu_qc_c)

                else:  # float
                    self.grids.tvu_qc_a1 = np.empty_like(tile.floats[depth_idx])
                    calc_tvu_qc_a1_fd(-tile.floats[depth_idx],
                                      tile.doubles[uncertainty_idx],
                                      tile.doubles_nodata[uncertainty_idx],
                                      self.grids.tvu_qc_a1)
                    self.grids.tvu_qc_a2b = np.empty_like(tile.floats[depth_idx])
                    calc_tvu_qc_a2b_fd(-tile.floats[depth_idx],
                                       tile.doubles[uncertainty_idx],
                                       tile.doubles_nodata[uncertainty_idx],
                                       self.grids.tvu_qc_a2b)
                    self.grids.tvu_qc_c = np.empty_like(tile.floats[depth_idx])
                    calc_tvu_qc_c_fd(-tile.floats[depth_idx],
                                     tile.doubles[uncertainty_idx],
                                     tile.doubles_nodata[uncertainty_idx],
                                     self.grids.tvu_qc_c)

            elif uncertainty_type == GRIDS_FLOAT:
                if depth_type == GRIDS_DOUBLE:
                    self.grids.tvu_qc_a1 = np.empty_like(tile.doubles[depth_idx])
                    calc_tvu_qc_a1_df(-tile.doubles[depth_idx],
                                      tile.floats[uncertainty_idx],
                                      tile.floats_nodata[uncertainty_idx],
                                      self.grids.tvu_qc_a1)
                    self.grids.tvu_qc_a2b = np.empty_like(tile.doubles[depth_idx])
                    calc_tvu_qc_a2b_df(-tile.doubles[depth_idx],
                                       tile.floats[uncertainty_idx],
                                       tile.floats_nodata[uncertainty_idx],
                                       self.grids.tvu_qc_a2b)
                    self.grids.tvu_qc_c = np.empty_like(tile.doubles[depth_idx])
                    calc_tvu_qc_c_df(-tile.doubles[depth_idx],
                                     tile.floats[uncertainty_idx],
                                     tile.floats_nodata[uncertainty_idx],
                                     self.grids.tvu_qc_c)

                else:  # float
                    self.grids.tvu_qc_a1 = np.empty_like(tile.floats[depth_idx])
                    calc_tvu_qc_a1_ff(-tile.floats[depth_idx],
                                      tile.floats[uncertainty_idx],
                                      tile.floats_nodata[uncertainty_idx],
                                      self.grids.tvu_qc_a1)
                    self.grids.tvu_qc_a2b = np.empty_like(tile.floats[depth_idx])
                    calc_tvu_qc_a2b_ff(-tile.floats[depth_idx],
                                       tile.floats[uncertainty_idx],
                                       tile.floats_nodata[uncertainty_idx],
                                       self.grids.tvu_qc_a2b)
                    self.grids.tvu_qc_c = np.empty_like(tile.floats[depth_idx])
                    calc_tvu_qc_c_ff(-tile.floats[depth_idx],
                                     tile.floats[uncertainty_idx],
                                     tile.floats_nodata[uncertainty_idx],
                                     self.grids.tvu_qc_c)

            elif uncertainty_type == "KLUSTER_FLOAT32":
                self.grids.tvu_qc_a1 = np.empty_like(tile.layers[depth_idx])
                calc_tvu_qc_a1_ff(-tile.layers[depth_idx],
                                  tile.layers[uncertainty_idx],
                                  np.nan,
                                  self.grids.tvu_qc_a1)
                self.grids.tvu_qc_a2b = np.empty_like(tile.layers[depth_idx])
                calc_tvu_qc_a2b_ff(-tile.layers[depth_idx],
                                   tile.layers[uncertainty_idx],
                                   np.nan,
                                   self.grids.tvu_qc_a2b)
                self.grids.tvu_qc_c = np.empty_like(tile.layers[depth_idx])
                calc_tvu_qc_c_ff(-tile.layers[depth_idx],
                                 tile.layers[uncertainty_idx],
                                 np.nan,
                                 self.grids.tvu_qc_c)

            else:
                raise RuntimeError("Unsupported data type for uncertainty: %s" % uncertainty_type)
            # logger.debug(self.grids.tvu_qc)

            self.catzoc_a1_values = np.fabs(self.grids.tvu_qc_a1[~np.isnan(self.grids.tvu_qc_a1)])
            self.catzoc_a2b_values = np.fabs(self.grids.tvu_qc_a2b[~np.isnan(self.grids.tvu_qc_a2b)])
            self.catzoc_c_values = np.fabs(self.grids.tvu_qc_c[~np.isnan(self.grids.tvu_qc_c)])
            self.grids.tvu_qc_a1 = None
            self.grids.tvu_qc_a2b = None
            self.grids.tvu_qc_c = None

            # self.tvu_qc_recalculated = True
            # self.tvu_qc_info.histo_x_label = "Node uncertainty as a fraction of allowable IHO TVU (computed)"

        if not self.grids.is_vr():
            return

        # Resolution percentage layers
        pct_success = tile.calculate_pct_of_allowable_resolution(self.grids.depth_layer_name())
        # logger.debug("is VR -> created resolution pct layers: %s" % pct_success)

        # - object detection
        if self.objection_detection:

            pct_od_type = tile.type(self.grids.pct_od_layer_name())
            pct_od_idx = tile.band_index(self.grids.pct_od_layer_name())
            # logger.debug("pct od layer: %s [idx: %s]" % (self.grids.grid_data_type(pct_od_type), pct_od_idx))

            if pct_od_type == GRIDS_FLOAT:
                self.pct_od_values = \
                    tile.floats[pct_od_idx][tile.floats[pct_od_idx] != tile.floats_nodata[pct_od_idx]]
                if len(self.pct_od_values) == 0:
                    logger.info("No pct od values")
            else:
                raise RuntimeError("Unsupported data type for density")
            # logger.debug('pct od values: %s' % len(self.pct_od_values))

        # - complete coverage
        if self.full_coverage:

            pct_cc_type = tile.type(self.grids.pct_cc_layer_name())
            pct_cc_idx = tile.band_index(self.grids.pct_cc_layer_name())
            # logger.debug("pct cc layer: %s [idx: %s]" % (self.grids.grid_data_type(pct_cc_type), pct_cc_idx))

            if pct_cc_type == GRIDS_FLOAT:
                self.pct_cc_values = \
                    tile.floats[pct_cc_idx][tile.floats[pct_cc_idx] != tile.floats_nodata[pct_cc_idx]]
                if len(self.pct_cc_values) == 0:
                    logger.info("No pct cc values")
            else:
                raise RuntimeError("Unsupported data type for density")
            # logger.debug('pct cc values: %s' % len(self.pct_cc_values))

    # plotting

    @classmethod
    def plot_hysto(cls, layer_name, bins, density, bin_width, grid_info, png_path, hist_color=None):
        logger.debug("saving %s histogram as %s" % (layer_name, png_path))

        # prepare sub-title 1
        sub_title_1 = 'Grid source: %s' % grid_info.basename

        # prepare sub-title 2 and 3
        if grid_info.pct_of_passed_nodes is None:
            tmp_str = "Total nodes: %s" % '{:,}'.format(grid_info.nr_of_nodes)
        else:
            pct_pass = "%d" % np.round(100 * grid_info.pct_of_passed_nodes + np.finfo(np.float32).eps)
            if pct_pass == '100':
                pct_pass = '100' if (grid_info.nr_of_passed_nodes == grid_info.nr_of_nodes) else '99.5+'
            tmp_str = "%s%% pass (%s of %s nodes)" \
                      % (pct_pass, '{:,}'.format(grid_info.nr_of_passed_nodes), '{:,}'.format(grid_info.nr_of_nodes))

        if bin_width <= 0.01:

            sub_title_2 = '%s, min=%.2f, mode=%.2f, max=%.2f' \
                          % (tmp_str, grid_info.min, grid_info.mode, grid_info.max)
            sub_title_3 = 'Percentiles: 2.5%%=%.2f, Q1=%.2f, median=%.2f, Q3=%.2f, 97.5%%=%.2f' \
                          % (grid_info.p2_5, grid_info.q1, grid_info.median, grid_info.q3, grid_info.p97_5)

        elif bin_width <= 0.1:

            sub_title_2 = '%s, min=%.2f, mode=%.1f, max=%.2f' \
                          % (tmp_str, grid_info.min, grid_info.mode, grid_info.max)
            sub_title_3 = 'Percentiles: 2.5%%=%.1f, Q1=%.1f, median=%.1f, Q3=%.1f, 97.5%%=%.1f' \
                          % (grid_info.p2_5, grid_info.q1, grid_info.median, grid_info.q3, grid_info.p97_5)

        else:
            sub_title_2 = '%s, min=%.1f, mode=%.0f, max=%.1f' \
                          % (tmp_str, grid_info.min, grid_info.mode, grid_info.max)
            sub_title_3 = 'Percentiles: 2.5%%=%.0f, Q1=%.0f, median=%.0f, Q3=%.0f, 97.5%%=%.0f' \
                          % (grid_info.p2_5, grid_info.q1, grid_info.median, grid_info.q3, grid_info.p97_5)

        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.81, 0.68])  # leaving room for title & subtitle

        hist_color = (.17, .55, .75) if hist_color is None else hist_color

        ax.bar(x=bins, height=100 * density, width=bin_width, align='center', linewidth=0, color=hist_color)
        ax.plot(bins - bin_width / 2., 100 * density, drawstyle="steps-post", fillstyle="bottom")
        ax.grid()

        x_min, x_max = bins.min(), bins.max()
        x_min_nom = max(grid_info.p2_5 - 1.5 * grid_info.p2_5, x_min)
        x_max_nom = min(grid_info.p97_5 + 1.5 * grid_info.p2_5, x_max)
        fail_left, fail_right = grid_info.fail_left, grid_info.fail_right
        if fail_left is None:
            fail_left = x_min = x_min_nom
        else:
            if x_min <= fail_left:
                x_min = min(0.98 * fail_left, x_min_nom)  # show a little red if not perfect
        if fail_right is None:
            fail_right = x_max = x_max_nom
        else:
            if x_max >= fail_right:
                x_max = max(1.02 * fail_right, x_max_nom)  # ditto
        ax.set_xlim((x_min, x_max))
        ax.axvspan(x_min, fail_left, facecolor="red", alpha=0.3)
        ax.axvspan(fail_right, x_max, facecolor="red", alpha=0.3)

        fig.text(.5, .935, grid_info.title, fontsize=14, ha='center')
        fig.text(.5, .89, sub_title_1, fontsize=12, ha='center')
        fig.text(.5, .85, sub_title_2, fontsize=10, ha='center')
        fig.text(.5, .812, sub_title_3, fontsize=10, ha='center')

        ax.set_xlabel(grid_info.histo_x_label)
        ax.set_ylabel(grid_info.histo_y_label)

        str_fmt = '%.1f%%' if ax.get_ylim()[-1] < 10 else '%.0f%%'
        ax.yaxis.set_major_formatter(FormatStrFormatter(str_fmt))

        fig.savefig(png_path, dpi=144, format='png')
        plt.close()

    def _init_plot_depth_vs_density(self):
        self.density_fig = plt.figure()
        self.density_ax = self.density_fig.add_axes([0.1, 0.1, 0.8, 0.74])

    def _update_plot_depth_vs_density(self):

        other_indices = self.density_values.argsort()
        other_len = len(self.density_values)

        d_idx0 = self.density_values[other_indices].searchsorted(5, 'left')
        pass_slice, fail_slice = slice(d_idx0, other_len), slice(0, d_idx0)

        self.density_ax.plot(self.density_values[other_indices][pass_slice],
                             self.bathy_values[other_indices][pass_slice], 'b+', alpha=0.5)
        self.density_ax.plot(self.density_values[other_indices][fail_slice],
                             self.bathy_values[other_indices][fail_slice], 'r+', alpha=0.5)

    def _finish_plot_depth_vs_density(self):

        if self.density_info.nr_of_nodes > 1000:
            self.density_ax.set_xscale('log')
            self.density_ax.get_xaxis().set_major_formatter(ScalarFormatter())

        self.density_ax.grid()
        self.density_ax.set_xlim((round(self.density_info.min / 0.1) * 0.1, self.density_ax.get_xlim()[-1]))
        self.density_ax.set_ylim(self.density_ax.get_ylim()[::-1])
        self.density_fig.text(.5, .90, 'Grid source: %s, total nodes: %s'
                              % (self.density_info.basename, '{:,}'.format(self.density_info.nr_of_nodes)),
                              fontsize=12, ha='center')
        self.density_ax.set_ylabel('Depth')

        png_file = "%s.QAv6.depth_vs_density.png" % os.path.splitext(self.grids.current_basename)[0]
        png_path = os.path.join(self.output_folder, png_file)
        png_path = Helper.truncate_too_long(png_path, left_truncation=True)

        self.density_fig.text(.5, .94, 'Node Depth vs. Sounding Density', fontsize=18, ha='center')
        self.density_ax.set_xlabel('Soundings per node')
        self.density_fig.savefig(png_path, dpi=144, format='png')

    def _init_plot_depth_vs_tvu_qc(self):
        self.tvu_qc_fig = plt.figure()
        self.tvu_qc_ax = self.tvu_qc_fig.add_axes([0.1, 0.1, 0.8, 0.74])

    def _update_plot_depth_vs_tvu_qc(self):

        other_indices = self.tvu_qc_values.argsort()
        other_len = len(self.tvu_qc_values)

        d_idx0 = self.tvu_qc_values[other_indices].searchsorted(1, 'right')
        pass_slice, fail_slice = slice(0, d_idx0), slice(d_idx0, other_len)

        try:
            self.tvu_qc_ax.plot(self.tvu_qc_values[other_indices][pass_slice],
                                self.bathy_values[other_indices][pass_slice], 'b+', alpha=0.5)
        except IndexError as e:
            logger.error("index issue while plotting pass slide, %s" % (e,))

        try:
            self.tvu_qc_ax.plot(self.tvu_qc_values[other_indices][fail_slice],
                                self.bathy_values[other_indices][fail_slice], 'r+', alpha=0.5)
        except IndexError as e:
            logger.error("index issue while plotting fail slice, %s" % (e,))

    def _finish_plot_depth_vs_tvu_qc(self):

        self.tvu_qc_ax.grid()
        self.tvu_qc_ax.set_xlim((round(self.tvu_qc_info.min / 0.1) * 0.1, self.tvu_qc_ax.get_xlim()[-1]))
        self.tvu_qc_ax.set_ylim(self.tvu_qc_ax.get_ylim()[::-1])
        self.tvu_qc_fig.text(.5, .90, 'Grid source: %s, total nodes: %s'
                             % (self.tvu_qc_info.basename, '{:,}'.format(self.tvu_qc_info.nr_of_nodes)),
                             fontsize=12, ha='center')
        self.tvu_qc_ax.set_ylabel('Depth')

        png_file = "%s.QAv6.depth_vs_tvu_qc.png" % os.path.splitext(self.grids.current_basename)[0]
        png_path = os.path.join(self.output_folder, png_file)
        png_path = Helper.truncate_too_long(png_path, left_truncation=True)

        self.tvu_qc_fig.text(.5, .94, 'Node Depth vs. TVU QC', fontsize=18, ha='center')
        sub_title_txt = "Full TVU QC range"
        sub_title = self.tvu_qc_fig.text(.5, .86, sub_title_txt, fontsize=11, ha='center')

        self.tvu_qc_ax.set_xlabel(self.tvu_qc_info.histo_x_label)

        x_min, x_max = self.tvu_qc_ax.get_xlim()
        out_path = Helper.truncate_too_long(png_path.replace('.png', '.full_range.png'), left_truncation=True)
        self.tvu_qc_fig.savefig(out_path, dpi=144, format='png')

        if x_max > 1.0:  # plot zoom on good data, if applicable

            self.tvu_qc_ax.set_xlim((x_min, 1.0))
            sub_title_txt = "Zoom on good data (TVU QC < 1.0)"
            sub_title.set_text(sub_title_txt)
            out_path = Helper.truncate_too_long(png_path.replace('.png', '.zoom_on_good_data.png'),
                                                left_truncation=True)
            self.tvu_qc_fig.savefig(out_path, dpi=144, format='png')
