import numpy as np
cimport numpy as np
from scipy import ndimage
import warnings
warnings.simplefilter(action="ignore", category=RuntimeWarning)
import logging
logger = logging.getLogger(__name__)

import cython
from libcpp.vector cimport vector

from libc.math cimport fabs
from libcpp.algorithm cimport sort as std_sort

cdef extern from "numpy/npy_math.h":
    bint npy_isnan(float x) nogil

cdef extern from 'math.h' nogil:
    float NAN
    double sqrt(double m)

# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef calc_proxies_float(float[:, ::1] bathy,
                          float[:, ::1] median,
                          float[:, ::1] nmad,
                          float[:, ::1] std_gauss_curv,
                          float[:, ::1] th_height,
                          float[:, ::1] th_gauss_curv,
                          int filter_size):

    cdef int bathy_rows, r, r_beg, r_end, w_r
    cdef int bathy_cols, c, c_beg, c_end, w_c
    cdef int sorted_sz
    cdef float bathy_sum, bathy_value, v
    cdef float gauss_sum, gauss_value, w

    np_gy = np.zeros((2*filter_size+1, 2*filter_size+1), dtype=np.float32)
    cdef float[:, ::1] gy = np_gy
    np_gx = np.zeros((2*filter_size+1, 2*filter_size+1), dtype=np.float32)
    cdef float[:, ::1] gx = np_gx

    np_gxy = np.zeros((2*filter_size+1, 2*filter_size+1), dtype=np.float32)
    cdef float[:, ::1] gxy = np_gxy
    np_gxx = np.zeros((2*filter_size+1, 2*filter_size+1), dtype=np.float32)
    cdef float[:, ::1] gxx = np_gxx

    np_gyy = np.zeros((2*filter_size+1, 2*filter_size+1), dtype=np.float32)
    cdef float[:, ::1] gyy = np_gyy
    np_gyx = np.zeros((2*filter_size+1, 2*filter_size+1), dtype=np.float32)
    cdef float[:, ::1] gyx = np_gyx

    np_gc = np.zeros((2*filter_size+1, 2*filter_size+1), dtype=np.float32)
    cdef float[:, ::1] gc = np_gc

    bathy_rows = bathy.shape[0]
    bathy_cols = bathy.shape[1]

    cdef vector[float] std_sorted
    cdef vector[float] std_gauss

    for r in range(bathy_rows):

        for c in range(bathy_cols):

            if npy_isnan(bathy[r, c]):
                median[r, c] = NAN
                nmad[r, c] = NAN
                std_gauss_curv[r, c] = NAN
                continue

            r_beg = r - filter_size
            if r_beg < 0:
                r_beg = 0
            r_end = r + filter_size + 1
            if r_end >= bathy_rows:
                r_end = bathy_rows
            c_beg = c - filter_size
            if c_beg < 0:
                c_beg = 0
            c_end = c + filter_size + 1
            if c_end >= bathy_cols:
                c_end = bathy_cols
            # logger.info("filter (%d,%d) -> (%d,%d)(%d,%d)" % (r, c, r_beg, r_end, c_beg, c_end))

            # median[r, c] = np.nanmedian(bathy[r_beg:r_end, c_beg:c_end])

            for w_r in range(0, 2*filter_size + 1):

                for w_c in range(0, 2*filter_size + 1):

                    gx[w_r, w_c] = NAN
                    # gxx[w_r, w_c] = NAN
                    # gxy[w_r, w_c] = NAN
                    gy[w_r, w_c] = NAN
                    # gyy[w_r, w_c] = NAN
                    # gyx[w_r, w_c] = NAN

            std_sorted.clear()
            bathy_sum = 0.0
            for w_r in range(r_beg, r_end):

                for w_c in range(c_beg, c_end):

                    # logger.info("%s %s: %s" % (w_r, w_c, bathy[w_r, w_c]))
                    bathy_value = bathy[w_r, w_c]

                    if w_c == 0:
                        if npy_isnan(bathy_value) or npy_isnan(bathy[w_r, w_c + 1]):
                           gx[w_r - r_beg, w_c - c_beg] = NAN
                        else:
                            gx[w_r - r_beg, w_c - c_beg] = bathy[w_r, w_c + 1] - bathy_value

                    elif w_c == (bathy_cols - 1):
                        if npy_isnan(bathy_value) or npy_isnan(bathy[w_r, w_c - 1]):
                            gx[w_r - r_beg, w_c - c_beg] = NAN
                        else:
                            gx[w_r - r_beg, w_c - c_beg] = bathy_value - bathy[w_r, w_c - 1]

                    else:
                        if npy_isnan(bathy[w_r, w_c - 1]) or npy_isnan(bathy[w_r, w_c + 1]):
                            gx[w_r - r_beg, w_c - c_beg] = NAN
                        else:
                            gx[w_r - r_beg, w_c - c_beg] = (bathy[w_r, w_c + 1] - bathy[w_r, w_c - 1]) / 2.0

                    if w_r == 0:
                        if npy_isnan(bathy_value) or npy_isnan(bathy[w_r + 1, w_c]):
                            gy[w_r - r_beg, w_c - c_beg] = NAN
                        else:
                            gy[w_r - r_beg, w_c - c_beg] = bathy[w_r + 1, w_c] - bathy_value

                    elif w_r == (bathy_rows - 1):
                        if npy_isnan(bathy_value) or npy_isnan(bathy[w_r - 1, w_c]):
                            gy[w_r - r_beg, w_c - c_beg] = NAN
                        else:
                            gy[w_r - r_beg, w_c - c_beg] = bathy_value - bathy[w_r - 1, w_c]

                    else:
                        if npy_isnan(bathy[w_r - 1, w_c]) or npy_isnan(bathy[w_r + 1, w_c]):
                            gy[w_r - r_beg, w_c - c_beg] = NAN
                        else:
                            gy[w_r - r_beg, w_c - c_beg] = (bathy[w_r + 1, w_c] - bathy[w_r - 1, w_c]) / 2.0

                    if npy_isnan(bathy_value):
                        continue

                    std_sorted.push_back(bathy_value)  # for median

                    bathy_sum += bathy_value  # for mean

            std_sort(std_sorted.begin(), std_sorted.end())
            sorted_sz = std_sorted.size()
            if sorted_sz % 2 == 0:
                median[r, c] = (std_sorted[sorted_sz/2] + std_sorted[sorted_sz/2 - 1]) / 2.0
            else:
                median[r, c] = std_sorted[sorted_sz/2]

            mean = bathy_sum / sorted_sz

            v = 0.0
            for si in range(sorted_sz):
                v += (std_sorted[si] - mean) ** 2
            std = sqrt(v / sorted_sz)

            nmad[r, c] = fabs(median[r, c] - mean) / std

            # if (r == 3) and (c == 3):
            #     logger.debug("arr:\n%s" % np.asarray(bathy[r_beg:r_end, c_beg:c_end]))
            #     logger.debug("gx:\n%s" % np.asarray(gx))
            #     logger.debug("gy:\n%s" % np.asarray(gy))

            # gxy, gxx <-> gx
            for w_r in range(0, 2*filter_size + 1):

                for w_c in range(0, 2*filter_size + 1):

                    if w_c == 0:
                        if npy_isnan(gx[w_r, w_c]) or npy_isnan(gx[w_r, w_c + 1]):
                            gxx[w_r, w_c] = NAN
                        else:
                            gxx[w_r, w_c] = gx[w_r, w_c + 1] - gx[w_r, w_c]
                        pass

                    elif w_c == 2*filter_size:
                        if npy_isnan(gx[w_r, w_c])  or npy_isnan(gx[w_r, w_c - 1]):
                            gxx[w_r, w_c] = NAN
                        else:
                            gxx[w_r, w_c] = gx[w_r, w_c] - gx[w_r, w_c - 1]

                    else:
                        if npy_isnan(gx[w_r, w_c - 1]) or npy_isnan(gx[w_r, w_c + 1]):
                            gxx[w_r, w_c] = NAN
                        else:
                            gxx[w_r, w_c] = (gx[w_r, w_c + 1] - gx[w_r, w_c - 1]) / 2.0

                    if w_r == 0:
                        if npy_isnan(gx[w_r, w_c])  or npy_isnan(gx[w_r + 1, w_c]):
                            gxy[w_r, w_c] = NAN
                        else:
                            gxy[w_r, w_c] = gx[w_r + 1, w_c] - npy_isnan(gx[w_r, w_c])

                    elif w_r == 2*filter_size:
                        if npy_isnan(gx[w_r, w_c]) or npy_isnan(gx[w_r - 1, w_c]):
                            gxy[w_r, w_c] = NAN
                        else:
                            gxy[w_r, w_c] = npy_isnan(gx[w_r, w_c]) - gx[w_r - 1, w_c]

                    else:
                        if npy_isnan(gx[w_r - 1, w_c]) or npy_isnan(gx[w_r + 1, w_c]):
                            gxy[w_r, w_c] = NAN
                        else:
                            gxy[w_r, w_c] = (gx[w_r + 1, w_c] - gx[w_r - 1, w_c]) / 2.0
                            
            # gyy, gyx <-> gy
            for w_r in range(0, 2*filter_size + 1):

                for w_c in range(0, 2*filter_size + 1):

                    if w_c == 0:
                        if npy_isnan(gy[w_r, w_c]) or npy_isnan(gy[w_r, w_c + 1]):
                            gyx[w_r, w_c] = NAN
                        else:
                            gyx[w_r, w_c] = gy[w_r, w_c + 1] - gy[w_r, w_c]
                        pass

                    elif w_c == 2*filter_size:
                        if npy_isnan(gy[w_r, w_c])  or npy_isnan(gy[w_r, w_c - 1]):
                            gyx[w_r, w_c] = NAN
                        else:
                            gyx[w_r, w_c] = gy[w_r, w_c] - gy[w_r, w_c - 1]

                    else:
                        if npy_isnan(gy[w_r, w_c - 1]) or npy_isnan(gy[w_r, w_c + 1]):
                            gyx[w_r, w_c] = NAN
                        else:
                            gyx[w_r, w_c] = (gy[w_r, w_c + 1] - gy[w_r, w_c - 1]) / 2.0

                    if w_r == 0:
                        if npy_isnan(gy[w_r, w_c])  or npy_isnan(gy[w_r + 1, w_c]):
                            gyy[w_r, w_c] = NAN
                        else:
                            gyy[w_r, w_c] = gy[w_r + 1, w_c] - npy_isnan(gy[w_r, w_c])

                    elif w_r == 2*filter_size:
                        if npy_isnan(gy[w_r, w_c]) or npy_isnan(gy[w_r - 1, w_c]):
                            gyy[w_r, w_c] = NAN
                        else:
                            gyy[w_r, w_c] = npy_isnan(gy[w_r, w_c]) - gy[w_r - 1, w_c]

                    else:
                        if npy_isnan(gy[w_r - 1, w_c]) or npy_isnan(gy[w_r + 1, w_c]):
                            gyy[w_r, w_c] = NAN
                        else:
                            gyy[w_r, w_c] = (gy[w_r + 1, w_c] - gy[w_r - 1, w_c]) / 2.0

            # gauss curv
            gauss_sum = 0.0
            std_gauss.clear()
            for w_r in range(0, 2*filter_size + 1):

                for w_c in range(0, 2*filter_size + 1):

                    if npy_isnan(gxx[w_r, w_c]) or npy_isnan(gyy[w_r, w_c]) \
                            or npy_isnan(gxy[w_r, w_c]) or npy_isnan(gx[w_r, w_c]) \
                            or npy_isnan(gy[w_r, w_c]):
                        continue

                    gauss_value = (gxx[w_r, w_c]*gyy[w_r, w_c] - (gxy[w_r, w_c] ** 2)) / \
                                  (1 + (gx[w_r, w_c] ** 2) + (gy[w_r, w_c] ** 2)) ** 2
                    gauss_sum += gauss_value
                    std_gauss.push_back(gauss_value)

            if std_gauss.empty():
                std_gauss_curv[r, c] = NAN

            else:
                gc_mean = gauss_sum / std_gauss.size()
                w = 0.0
                for si in range(std_gauss.size()):
                    w += (std_gauss[si] - gc_mean) ** 2
                std_gauss_curv[r, c] = sqrt(w / std_gauss.size())

            # ### THRESHOLDS ###
            # logger.info("thresholds calculation ...")

            pct_height = 4.0  # per cent

            # correction for variability in range
            nmad_value = nmad[r, c]
            if (nmad_value < 0.1) or np.isnan(nmad_value):
                pass
            elif nmad_value < 0.2:
                pct_height += 0.5
            elif nmad_value < 0.3:
                pct_height += 1.0
            elif nmad_value < 0.4:
                pct_height += 1.5
            else:
                pct_height += 2.0

            # correction for global roughness
            std_gauss_curv_value = std_gauss_curv[r, c]
            if (std_gauss_curv_value < 0.01) or (np.isnan(std_gauss_curv_value)):
                pass
            if std_gauss_curv_value < 0.03:
                pct_height += 0.5
            elif std_gauss_curv_value < 0.06:
                pct_height += 1.0
            elif std_gauss_curv_value < 0.1:
                pct_height += 1.5
            else:
                pct_height += 2.0

            median_value = median[r, c]
            if np.isnan(median_value):
                th_height[r, c] = np.nan
            else:
                th_height[r, c] = abs(median_value) * pct_height * 0.01
                if th_height[r, c] < 0.5:
                    th_height[r, c] = 0.5

            # noinspection PyStringFormat
            # logger.debug("proxies -> median: %f, nmad: %f, std curv: %f -> %.1f%% -> %.3f"
            #              % (median, nmad, std_gauss_curv, pct_height, th_height[r, c]))

            # correction for curvature threshold
            if np.isnan(std_gauss_curv_value):
                th_curv = np.nan
            else:
                th_curv = 6.0
                if std_gauss_curv_value > 0.01:
                    th_curv *= 2.0
                if std_gauss_curv_value > 0.03:
                    th_curv *= 2.0
                if std_gauss_curv_value > 0.1:
                    th_curv *= 2.0

            # logger.info("estimated gaussian threshold: %.1f" % th_curv)
            th_gauss_curv[r, c] = th_curv

            # logger.info("thresholds calculation: OK")