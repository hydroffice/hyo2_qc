import numpy as np
from matplotlib import rcParams
from scipy.spatial import Delaunay

rcParams['ytick.labelsize'] = 8
rcParams['xtick.labelsize'] = 8
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import logging

logger = logging.getLogger(__name__)

from hyo2.qc.chart.triangle.base_triangle import BaseTriangle, triangle_algos, sounding_units
from hyo2.qc.common.geodesy import Geodesy


class TriangleRuleV2(BaseTriangle):
    def __init__(self, ss, s57, cs, use_valsous, use_contours=False, detect_deeps=False, multiplier=1.0,
                 sounding_unit=sounding_units['feet'], progress=None):

        super(TriangleRuleV2, self).__init__(ss=ss, s57=s57, cs=cs, sounding_unit=sounding_unit, progress=progress)
        self.type = triangle_algos["TRIANGLE_RULE_v2"]
        self.use_valsous = use_valsous
        self.use_contours = use_contours
        self.detect_deeps = detect_deeps
        self.multiplier = multiplier

        self.gd = Geodesy()

        self.all_ss = self.ss.rec10s
        if self.s57 is None:
            self.all_s57 = list()
        else:
            self.all_s57 = self.s57.rec10s
        if self.cs is None:
            self.all_cs = list()
        else:
            self.all_cs = self.cs.rec10s

        self.points2d = None
        self.points3d = None
        self.delaunay = None

        self.edges_a = None
        self.edges_b = None

        self.triangles = None
        self.bad_triangles = None
        self.good_triangles = None

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

    def run(self):
        """Execute the set of check of the feature scan algorithm"""
        logger.debug("using VALSOU features: %s" % self.use_valsous)
        logger.debug("using CONTOURs: %s" % self.use_contours)
        logger.debug("using deeps detection: %s" % self.detect_deeps)
        logger.debug("using chart sounding unit: %s" % self.csu)
        if self.csu == sounding_units["meters"]:
            logger.debug("using multiplier: %s" % self.multiplier)

        self._collect_points()

        self._triangulate()

        self._flag()

        self._plot()

    def _collect_points(self):
        logger.debug('collecting points to triangulate ...')
        self.progress.add(quantum=10, text="Collecting points to triangulate")

        xs = list()
        ys = list()
        zs = list()

        for ft in self.all_s57:

            # just for soundings
            if len(ft.geo3s) > 0:

                for geo3 in ft.geo3s:
                    xs.append(geo3.x)
                    ys.append(geo3.y)
                    zs.append(geo3.z)

            elif ft.acronym == 'DEPCNT':

                if not self.use_contours:
                    continue

                valdco = 0
                for attr in ft.attributes:
                    if attr.acronym == "VALDCO":
                        try:
                            valdco = float(attr.value)
                        except ValueError:
                            pass
                        break

                # logger.debug('%s -> %.3f m (%d points)' % (ft.acronym, valdco, len(ft.geo2s)))
                for idx, geo2 in enumerate(ft.geo2s):

                    if idx % 20:
                        continue

                    xs.append(geo2.x)
                    ys.append(geo2.y)
                    zs.append(valdco)

            # for all the other no-sounding features
            else:

                for attr in ft.attributes:

                    if (len(ft.geo2s)) == 1:

                        if (attr.acronym == "VALSOU") and self.use_valsous:
                            try:
                                z = float(attr.value)
                                xs.append(ft.geo2s[0].x)
                                ys.append(ft.geo2s[0].y)
                                zs.append(z)
                                # print('added: %s' % z)
                            except ValueError:
                                pass
                            break

        self.points2d = np.column_stack((xs, ys))
        self.points3d = np.column_stack((xs, ys, zs))

        logger.debug('collected points: %d' % len(xs))

    def _triangulate(self):
        logger.debug('triangulating')
        self.progress.add(quantum=10, text="Triangulating")

        self.delaunay = Delaunay(self.points2d)

        # print(self.delaunay.simplices)

        # calculate the length of all the edges
        len_edges = list()
        # noinspection PyUnresolvedReferences
        for tri in self.points3d[self.delaunay.simplices]:
            # print(tri[0][0], tri[0][1], tri[0][0], tri[0][1])

            len_a = self.gd.distance(long_1=tri[0][0], lat_1=tri[0][1], long_2=tri[1][0], lat_2=tri[1][1])
            len_edges.append(len_a)

            len_b = self.gd.distance(long_1=tri[1][0], lat_1=tri[1][1], long_2=tri[2][0], lat_2=tri[2][1])
            len_edges.append(len_b)

            len_c = self.gd.distance(long_1=tri[2][0], lat_1=tri[2][1], long_2=tri[0][0], lat_2=tri[0][1])
            len_edges.append(len_c)

        # print(len_edges)
        # print(np.mean(len_edges), np.median(len_edges), np.std(len_edges))
        th_len = float(np.mean(len_edges) + 2 * np.std(len_edges))
        logger.debug('removing threshold: %.1f m' % th_len)

        # remove the triangles with too long edges
        self.good_triangles = list()
        self.bad_triangles = list()
        # noinspection PyUnresolvedReferences
        for idx, tri in enumerate(self.points3d[self.delaunay.simplices]):

            if (len_edges[idx * 3 + 0] > th_len) \
                    or (len_edges[idx * 3 + 1] > th_len) \
                    or (len_edges[idx * 3 + 2] > th_len):
                self.bad_triangles.append(idx)
                # logger.debug('removing triangle #%03d: %s/%s/%s'
                #              % (idx, len_edges[idx*3 + 0], len_edges[idx*3 + 1], len_edges[idx*3 + 2]))
                continue

            else:
                self.good_triangles.append(idx)

        # noinspection PyUnresolvedReferences
        self.triangles = np.delete(self.delaunay.simplices, self.bad_triangles, axis=0)
        # noinspection PyUnresolvedReferences
        self.rem_triangles = np.delete(self.delaunay.simplices, self.good_triangles, axis=0)

        # prepare edge for TIN output
        self.edges_a = [[], []]
        self.edges_b = [[], []]
        for tri in self.points3d[self.triangles]:
            self.edges_a[0].append(tri[0][0])
            self.edges_a[1].append(tri[0][1])
            self.edges_b[0].append(tri[1][0])
            self.edges_b[1].append(tri[1][1])

            self.edges_a[0].append(tri[1][0])
            self.edges_a[1].append(tri[1][1])
            self.edges_b[0].append(tri[2][0])
            self.edges_b[1].append(tri[2][1])

            self.edges_a[0].append(tri[2][0])
            self.edges_a[1].append(tri[2][1])
            self.edges_b[0].append(tri[0][0])
            self.edges_b[1].append(tri[0][1])

            # print("- a: %s, %s" % (tri[0][0], tri[0][1]))
            # print("- b: %s, %s" % (tri[1][0], tri[1][1]))
            # print("- c: %s, %s\n" % (tri[2][0], tri[2][1]))

    def _flag(self):
        logger.debug('searching SS to flag')
        self.progress.add(quantum=10, text="Searching SS to flag")

        for ft in self.all_ss:

            # skip if the feature has not exactly 1 point
            if len(ft.geo3s) != 1:
                continue

            p = np.array([(ft.geo3s[0].x, ft.geo3s[0].y), ])
            ret = self.delaunay.find_simplex(p)

            # skip checks
            if ret == -1:  # out of all the triangles
                continue
            if ret in self.bad_triangles:  # within a bad triangle
                continue

            # flagging using different criteria
            if self.csu == sounding_units['feet']:

                tri = self.points3d[self.delaunay.simplices[ret]]
                min_z = np.min(tri[0, :, 2])

                ft_z = ft.geo3s[0].z

                ft_z_feet = round(ft_z * 3.28084)
                min_z_feet = round(min_z * 3.28084)

                diff_z_feet = min_z_feet - ft_z_feet

                # print(tri)
                # print(ft_z, ft_z_feet, min_z, min_z_feet, diff_z_feet)

                if diff_z_feet > 0.01:
                    self._append_flagged(ft.geo3s[0].x,
                                         ft.geo3s[0].y,
                                         "%.3f" % diff_z_feet)
                    continue

                if self.detect_deeps:

                    max_z = np.max(tri[0, :, 2])
                    max_z_feet = round(max_z * 3.28084)
                    diff_z_feet = max_z_feet - ft_z_feet

                    if diff_z_feet < -3.28084:
                        self._append_flagged(ft.geo3s[0].x,
                                             ft.geo3s[0].y,
                                             "%.3f" % diff_z_feet)

                continue

            elif self.csu == sounding_units['fathoms']:

                tri = self.points3d[self.delaunay.simplices[ret]]
                ft_z = ft.geo3s[0].z
                min_z = np.min(tri[0, :, 2])
                max_z = np.max(tri[0, :, 2])

                # this rule is coming from the Nautical Charting Manual (11 fathom danger curve)
                if (ft_z < 20.1168) and (min_z < 20.1168):  # 11 fathoms = 20.1168 meters

                    ft_z_feet = round(ft_z * 3.28084)
                    min_z_feet = round(min_z * 3.28084)
                    diff_z_feet = min_z_feet - ft_z_feet

                    # we also need fathoms for the output differences
                    ft_z_fathoms = round(ft_z * 0.546807)
                    min_z_fathoms = round(min_z * 0.546807)
                    diff_z_fathoms = min_z_fathoms - ft_z_fathoms

                    if diff_z_feet > 0.01:
                        self._append_flagged(ft.geo3s[0].x,
                                             ft.geo3s[0].y,
                                             "%.3f" % diff_z_fathoms)
                        continue

                    if self.detect_deeps:

                        # max_z_feet = round(max_z * 3.28084)
                        # diff_z_feet = max_z_feet - ft_z_feet
                        max_z_fathoms = round(max_z * 0.546807)
                        diff_z_fathoms = max_z_fathoms - ft_z_fathoms

                        if diff_z_fathoms < -0.546807:
                            self._append_flagged(ft.geo3s[0].x,
                                                 ft.geo3s[0].y,
                                                 "%.3f" % diff_z_fathoms)

                    # print(tri)
                    # print(ft_z, ft_z_feet, min_z, min_z_feet, diff_z_feet)
                    # print(ft_z, ft_z_fathoms, min_z, min_z_fathoms, diff_z_fathoms)

                    continue

                else:
                    ft_z_fathoms = round(ft_z * 0.546807)
                    min_z_fathoms = round(min_z * 0.546807)
                    diff_z_fathoms = min_z_fathoms - ft_z_fathoms

                    if diff_z_fathoms > 0.01:
                        self._append_flagged(ft.geo3s[0].x,
                                             ft.geo3s[0].y,
                                             "%.3f" % diff_z_fathoms)
                        continue

                    if self.detect_deeps:

                        max_z_fathoms = round(max_z * 0.546807)
                        diff_z_fathoms = max_z_fathoms - ft_z_fathoms

                        if diff_z_fathoms < -0.546807:
                            self._append_flagged(ft.geo3s[0].x,
                                                 ft.geo3s[0].y,
                                                 "%.3f" % diff_z_fathoms)

                    # print(tri)
                    # print(ft_z, ft_z_fathoms, min_z, min_z_fathoms, diff_z_fathoms)

                    continue

            elif self.csu == sounding_units['meters']:

                tri = self.points3d[self.delaunay.simplices[ret]]
                min_z = np.min(tri[0, :, 2])

                ft_z = ft.geo3s[0].z

                diff_z = min_z - ft_z

                # print(tri)
                # print(ft_z, ft_z_feet, min_z, min_z_feet, diff_z_feet)

                if diff_z > self.multiplier:
                    self._append_flagged(ft.geo3s[0].x,
                                         ft.geo3s[0].y,
                                         "%.3f" % diff_z)
                    continue

                if self.detect_deeps:

                    max_z = np.max(tri[0, :, 2])
                    diff_z = max_z - ft_z

                    if diff_z < -self.multiplier:
                        self._append_flagged(ft.geo3s[0].x,
                                             ft.geo3s[0].y,
                                             "%.3f" % diff_z)

                continue

            else:
                raise RuntimeError("unknown criteria: %s" % self.csu)

    def _plot(self, save_fig=False):
        logger.debug('plotting')
        self.progress.add(quantum=10, text="Plotting")

        if not save_fig:
            plt.ion()

        ticks = 0.1

        def latitudes(y, pos):
            """The two args are the value and tick position"""
            if ticks > 0.9:
                ret = '%.0f' % y
            elif ticks > 0.09:
                ret = '%.1f' % y
            elif ticks > 0.009:
                ret = '%.2f' % y
            else:
                ret = '%.3f' % y

            return ret

        def longitudes(x, pos):
            """The two args are the value and tick position"""
            if ticks > 0.9:
                ret = '%.0f' % x
            elif ticks > 0.09:
                ret = '%.1f' % x
            elif ticks > 0.009:
                ret = '%.2f' % x
            else:
                ret = '%.3f' % x

            return ret

        lat_formatter = FuncFormatter(latitudes)
        lon_formatter = FuncFormatter(longitudes)

        fig = plt.figure(1, figsize=(10, 10))
        ax = fig.add_subplot(111)
        ax.patch.set_facecolor('0.35')

        ax.triplot(self.points3d[:, 0], self.points3d[:, 1], self.rem_triangles,
                   zorder=1, color='0.5', lw=0.4, linestyle='--')
        ax.triplot(self.points3d[:, 0], self.points3d[:, 1], self.triangles,
                   zorder=2, color='0.55', lw=0.8)

        # noinspection PyUnresolvedReferences
        ax.scatter(self.points3d[:, 0], self.points3d[:, 1], c=self.points3d[:, 2],
                   zorder=3, marker='o', s=14, lw=0, cmap=plt.cm.GnBu)
        # noinspection PyUnresolvedReferences
        m1 = plt.cm.ScalarMappable(cmap=plt.cm.GnBu)
        m1.set_array(self.points3d[:, 2])
        cb1 = plt.colorbar(m1)
        cb1.set_label('depth [m]', size=9)

        # noinspection PyUnresolvedReferences
        diff_cmap = plt.cm.autumn_r
        if self.detect_deeps:
            # noinspection PyUnresolvedReferences
            diff_cmap = plt.cm.RdYlGn_r

        # noinspection PyUnresolvedReferences
        zs = [float(x) for x in self.flagged_features[2]]
        # noinspection PyUnresolvedReferences
        ax.scatter(self.flagged_features[0], self.flagged_features[1], c=zs,
                   zorder=4, marker='x', s=10, lw=1, cmap=diff_cmap)
        # noinspection PyUnresolvedReferences
        m2 = plt.cm.ScalarMappable(cmap=diff_cmap)
        m2.set_array(zs)
        cb2 = plt.colorbar(m2)
        if self.csu == sounding_units['feet']:
            cb2.set_label('depth difference [feet]', size=9)
        elif self.csu == sounding_units['meters']:
            cb2.set_label('depth difference [m]', size=9)
        else:
            cb2.set_label('depth difference [fathoms]', size=9)

        ax.set_aspect('equal')
        ax.grid(True, color='0.45')
        ticks = min((ax.get_yticks()[1] - ax.get_yticks()[0]),
                    (ax.get_xticks()[1] - ax.get_xticks()[0]))
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.xaxis.set_major_formatter(lon_formatter)
        plt.show()
