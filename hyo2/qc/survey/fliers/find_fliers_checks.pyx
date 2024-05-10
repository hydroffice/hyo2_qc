import warnings

cimport numpy as np
import numpy as np
from scipy import ndimage

warnings.simplefilter(action="ignore", category=RuntimeWarning)
import logging
logger = logging.getLogger(__name__)

import cython
from libcpp.vector cimport vector

cdef extern from "numpy/npy_math.h":
    bint npy_isnan(float x) nogil


# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_laplacian_operator_double(double[:, :] lap, int[:, :] flag_grid, float th):

    cdef unsigned int lap_rows, r
    cdef unsigned int lap_cols, c

    lap_rows = lap.shape[0]
    lap_cols = lap.shape[1]
    for r in range(lap_rows):
        find = False
        for c in range(lap_cols):
            if (lap[r,c] < th) or (lap[r,c] > -th):
                flag_grid[r, c] = 1 # check #1
                logger.info("#1 > @(%d,%d)" % (int(r), int(c)))

# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_laplacian_operator_float(float[:, :] lap, int[:, :] flag_grid, float th):

    cdef unsigned int lap_rows, r
    cdef unsigned int lap_cols, c

    lap_rows = lap.shape[0]
    lap_cols = lap.shape[1]
    for r in range(lap_rows):
        find = False
        for c in range(lap_cols):
            if (lap[r,c] < th) or (lap[r,c] > -th):
                flag_grid[r, c] = 1 # check #1
                logger.info("#1 > @(%d,%d)" % (int(r), int(c)))

# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_gaussian_curvature_double(double[:, :] gauss_curv, int[:, :] flag_grid, float th):

    cdef unsigned int lap_rows, r
    cdef unsigned int lap_cols, c

    lap_rows = gauss_curv.shape[0]
    lap_cols = gauss_curv.shape[1]
    for r in range(lap_rows):
        for c in range(lap_cols):
            if gauss_curv[r,c] > th:
                flag_grid[r, c] = 2 # check #2
                logger.info("#2 > @(%d,%d) -> %f > %f" % (int(r), int(c), gauss_curv[r,c], th))

# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_gaussian_curvature_float(float[:, :] gauss_curv, int[:, :] flag_grid, float th):

    cdef unsigned int lap_rows, r
    cdef unsigned int lap_cols, c

    lap_rows = gauss_curv.shape[0]
    lap_cols = gauss_curv.shape[1]
    for r in range(lap_rows):
        for c in range(lap_cols):
            if gauss_curv[r,c] > th:
                flag_grid[r, c] = 2 # check #2
                logger.info("#2 > @(%d,%d) -> %f > %f" % (int(r), int(c), gauss_curv[r,c], th))

# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_adjacent_cells_double(double[:, :] bathy, int[:, :] flag_grid, float th, float pct1, float pct2):

    # logger.debug("[check adjacent] double bathy, using flier height: %.2f" % th)

    cdef np.npy_intp rows = bathy.shape[0]  # number of rows
    cdef np.npy_intp cols = bathy.shape[1]  # number of columns
    # logger.debug("[check adjacent] rows: %d, cols: %d" % (rows, cols))
    cdef np.npy_intp r, c
    cdef double dep_node, dep_ngb
    cdef float pos_ratio, neg_ratio, thr
    cdef int dif_pos_cnt, dif_neg_cnt, ngb_cnt

    # the grid is traversed row by row

    for r in range(rows):  # we get the row

        # Historically, we were skipping the first and the last row
        # if (r == 0) or (r == rows - 1):
        #     continue

        for c in range(cols):  # we get the column

            if (c == 0) or (c == cols - 1):
                continue

            if flag_grid[r, c] != 0:  # avoid existing flagged nodes
                continue

            # for each node in the grid, the depth is retrieved
            dep_node = bathy[r, c]

            # any further calculation is skipped in case of a no-data value
            if npy_isnan(dep_node):
                continue

            ngb_cnt = 0  # initialize the number of neighbors
            dif_pos_cnt = 0  # initialize the number of neighbors with positive depth diff
            dif_neg_cnt = 0  # initialize the number of neighbors with negative depth diff

            # - left node

            if c > 0:  # if we are not on the first column

                # attempt to retrieve depth
                if flag_grid[r, c - 1] != 0:
                    continue
                dep_ngb = bathy[r, c - 1]
                if npy_isnan(dep_ngb) and c > 1:
                    if flag_grid[r, c - 2] != 0:
                        continue
                    dep_ngb = bathy[r, c - 2]
                if npy_isnan(dep_ngb) and c > 2:
                    if flag_grid[r, c - 3] != 0:
                        continue
                    dep_ngb = bathy[r, c - 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - right node

            if c < cols - 1:  # if we are not on the last column

                # attempt to retrieve depth
                if flag_grid[r, c + 1] != 0:
                    continue
                dep_ngb = bathy[r, c + 1]
                if npy_isnan(dep_ngb) and (c < cols - 2):
                    if flag_grid[r, c + 2] != 0:
                        continue
                    dep_ngb = bathy[r, c + 2]
                if npy_isnan(dep_ngb) and (c < cols - 3):
                    if flag_grid[r, c + 3] != 0:
                        continue
                    dep_ngb = bathy[r, c + 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - bottom node

            if r > 0:  # if we are not on the first row

                # attempt to retrieve depth
                if flag_grid[r - 1, c] != 0:
                    continue
                dep_ngb = bathy[r - 1, c]
                if npy_isnan(dep_ngb) and r > 1:
                    if flag_grid[r - 2, c] != 0:
                        continue
                    dep_ngb = bathy[r - 2, c]
                if npy_isnan(dep_ngb) and r > 2:
                    if flag_grid[r - 3, c] != 0:
                        continue
                    dep_ngb = bathy[r - 3, c]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - top node

            if r < rows - 1:  # if we are not on the last row

                # attempt to retrieve depth
                if flag_grid[r + 1, c] != 0:
                    continue
                dep_ngb = bathy[r + 1, c]
                if npy_isnan(dep_ngb) and (r < rows - 2):
                    if flag_grid[r + 2, c] != 0:
                        continue
                    dep_ngb = bathy[r + 2, c]
                if npy_isnan(dep_ngb) and (r < rows - 3):
                    if flag_grid[r + 3, c] != 0:
                        continue
                    dep_ngb = bathy[r + 3, c]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - bottom-left node

            if (r > 0) and (c > 0):  # if we are not on the first row and col

                # attempt to retrieve depth
                if flag_grid[r - 1, c - 1] != 0:
                    continue
                dep_ngb = bathy[r - 1, c - 1]
                if npy_isnan(dep_ngb) and r > 1 and c > 1:
                    if flag_grid[r - 2, c - 2] != 0:
                        continue
                    dep_ngb = bathy[r - 2, c - 2]
                # if npy_isnan(dep_ngb) and r > 2 and c > 2:
                #     if flag_grid[r - 3, c - 3] != 0:
                #         continue
                #     dep_ngb = bathy[r - 3, c - 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - top-right node

            if (r < rows - 1) and (c < cols - 1):  # if we are not on the last row and col

                # attempt to retrieve depth
                if flag_grid[r + 1, c + 1] != 0:
                    continue
                dep_ngb = bathy[r + 1, c + 1]
                if npy_isnan(dep_ngb) and (r < rows - 2) and (c < cols - 2):
                    if flag_grid[r + 2, c + 2] != 0:
                        continue
                    dep_ngb = bathy[r + 2, c + 2]
                # if npy_isnan(dep_ngb) and (r < rows - 3) and (c < cols - 3):
                #     if flag_grid[r + 3, c + 3] != 0:
                #         continue
                #     dep_ngb = bathy[r + 3, c + 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - bottom-right node

            if (r > 0) and (c < cols - 1):  # if we are not on the first row and last col

                # attempt to retrieve depth
                if flag_grid[r - 1, c + 1] != 0:
                    continue
                dep_ngb = bathy[r - 1, c + 1]
                if npy_isnan(dep_ngb) and r > 1 and (c < cols - 2):
                    if flag_grid[r - 2, c + 2] != 0:
                        continue
                    dep_ngb = bathy[r - 2, c + 2]
                # if npy_isnan(dep_ngb) and r > 2 and c > 2:
                #     if flag_grid[r - 3, c + 3] != 0:
                #         continue
                #     dep_ngb = bathy[r - 3, c + 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - top-left node

            if (r < rows - 1) and (c > 0):  # if we are not on the last row and first col

                # attempt to retrieve depth
                if flag_grid[r + 1, c - 1] != 0:
                    continue
                dep_ngb = bathy[r + 1, c - 1]
                if npy_isnan(dep_ngb) and (r < rows - 2) and c > 1:
                    if flag_grid[r + 2, c - 2] != 0:
                        continue
                    dep_ngb = bathy[r + 2, c - 2]
                # if npy_isnan(dep_ngb) and (r < rows - 3) and c > 2:
                #     if flag_grid[r + 3, c - 3] != 0:
                #         continue
                #     dep_ngb = bathy[r + 3, c - 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            if ngb_cnt == 0:
                continue

            # calculate the ratio among flagged and total neighbors, then use it to decide if a flier
            if (r == 0) or (c == 0) or (r == (rows - 1)) or (c == (cols - 1)):
                thr = 1.0
            elif ngb_cnt <= 4:
                thr = pct1
            else:
                thr = pct2

            pos_ratio = dif_pos_cnt / float(ngb_cnt)
            if pos_ratio >= thr:
                flag_grid[r, c] = 3  # check #3
                logger.info("#3 > + @(%d,%d): %d/%d > node ratio %.2f (threshold: %.2f)"
                             % (r, c, dif_pos_cnt, ngb_cnt, pos_ratio, thr))
                continue

            neg_ratio = dif_neg_cnt / float(ngb_cnt)
            if neg_ratio >= thr:
                flag_grid[r, c] = 3  # check #3
                logger.info("#3 > - @(%d,%d): %d/%d > node ratio %.2f (threshold: %.2f)"
                             % (r, c, dif_neg_cnt, ngb_cnt, neg_ratio, thr))
                continue


# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_adjacent_cells_float(float[:, :] bathy, int[:, :] flag_grid, float th, float pct1, float pct2):

    # logger.debug("[check adjacent] float bathy, using flier height: %.2f" % th)

    cdef np.npy_intp rows = bathy.shape[0]  # number of rows
    cdef np.npy_intp cols = bathy.shape[1]  # number of columns
    cdef np.npy_intp r, c
    cdef float dep_node, dep_ngb
    cdef float pos_ratio, neg_ratio, thr
    cdef int dif_pos_cnt, dif_neg_cnt, ngb_cnt

    # the grid is traversed row by row

    for r in range(rows):  # we get the row

        # Historically, we were skipping the first and the last row
        # if (r == 0) or (r == rows - 1):
        #     continue

        for c in range(cols):  # we get the column

            if (c == 0) or (c == cols - 1):
                continue

            if flag_grid[r, c] != 0:  # avoid existing flagged nodes
                continue

            # for each node in the grid, the depth is retrieved
            dep_node = bathy[r, c]

            # any further calculation is skipped in case of a no-data value
            if npy_isnan(dep_node):
                continue

            ngb_cnt = 0  # initialize the number of neighbors
            dif_pos_cnt = 0  # initialize the number of neighbors with positive depth diff
            dif_neg_cnt = 0  # initialize the number of neighbors with negative depth diff

            # - left node

            if c > 0:  # if we are not on the first column

                # attempt to retrieve depth
                if flag_grid[r, c - 1] != 0:
                    continue
                dep_ngb = bathy[r, c - 1]
                if npy_isnan(dep_ngb) and c > 1:
                    if flag_grid[r, c - 2] != 0:
                        continue
                    dep_ngb = bathy[r, c - 2]
                if npy_isnan(dep_ngb) and c > 2:
                    if flag_grid[r, c - 3] != 0:
                        continue
                    dep_ngb = bathy[r, c - 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - right node

            if c < cols - 1:  # if we are not on the last column

                # attempt to retrieve depth
                if flag_grid[r, c + 1] != 0:
                    continue
                dep_ngb = bathy[r, c + 1]
                if npy_isnan(dep_ngb) and (c < cols - 2):
                    if flag_grid[r, c + 2] != 0:
                        continue
                    dep_ngb = bathy[r, c + 2]
                if npy_isnan(dep_ngb) and (c < cols - 3):
                    if flag_grid[r, c + 3] != 0:
                        continue
                    dep_ngb = bathy[r, c + 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - bottom node

            if r > 0:  # if we are not on the first row

                # attempt to retrieve depth
                if flag_grid[r - 1, c] != 0:
                    continue
                dep_ngb = bathy[r - 1, c]
                if npy_isnan(dep_ngb) and r > 1:
                    if flag_grid[r - 2, c] != 0:
                        continue
                    dep_ngb = bathy[r - 2, c]
                if npy_isnan(dep_ngb) and r > 2:
                    if flag_grid[r - 3, c] != 0:
                        continue
                    dep_ngb = bathy[r - 3, c]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - top node

            if r < rows - 1:  # if we are not on the last row

                # attempt to retrieve depth
                if flag_grid[r + 1, c] != 0:
                    continue
                dep_ngb = bathy[r + 1, c]
                if npy_isnan(dep_ngb) and (r < rows - 2):
                    if flag_grid[r + 2, c] != 0:
                        continue
                    dep_ngb = bathy[r + 2, c]
                if npy_isnan(dep_ngb) and (r < rows - 3):
                    if flag_grid[r + 3, c] != 0:
                        continue
                    dep_ngb = bathy[r + 3, c]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - bottom-left node

            if (r > 0) and (c > 0):  # if we are not on the first row and col

                # attempt to retrieve depth
                if flag_grid[r - 1, c - 1] != 0:
                    continue
                dep_ngb = bathy[r - 1, c - 1]
                if npy_isnan(dep_ngb) and r > 1 and c > 1:
                    if flag_grid[r - 2, c - 2] != 0:
                        continue
                    dep_ngb = bathy[r - 2, c - 2]
                # if npy_isnan(dep_ngb) and r > 2 and c > 2:
                #     if flag_grid[r - 3, c - 3] != 0:
                #         continue
                #     dep_ngb = bathy[r - 3, c - 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - top-right node

            if (r < rows - 1) and (c < cols - 1):  # if we are not on the last row and col

                # attempt to retrieve depth
                if flag_grid[r + 1, c + 1] != 0:
                    continue
                dep_ngb = bathy[r + 1, c + 1]
                if npy_isnan(dep_ngb) and (r < rows - 2) and (c < cols - 2):
                    if flag_grid[r + 2, c + 2] != 0:
                        continue
                    dep_ngb = bathy[r + 2, c + 2]
                # if npy_isnan(dep_ngb) and (r < rows - 3) and (c < cols - 3):
                #     if flag_grid[r + 3, c + 3] != 0:
                #         continue
                #     dep_ngb = bathy[r + 3, c + 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - bottom-right node

            if (r > 0) and (c < cols - 1):  # if we are not on the first row and last col

                # attempt to retrieve depth
                if flag_grid[r - 1, c + 1] != 0:
                    continue
                dep_ngb = bathy[r - 1, c + 1]
                if npy_isnan(dep_ngb) and r > 1 and (c < cols - 2):
                    if flag_grid[r - 2, c + 2] != 0:
                        continue
                    dep_ngb = bathy[r - 2, c + 2]
                # if npy_isnan(dep_ngb) and r > 2 and c > 2:
                #     if flag_grid[r - 3, c + 3] != 0:
                #         continue
                #     dep_ngb = bathy[r - 3, c + 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            # - top-left node

            if (r < rows - 1) and (c > 0):  # if we are not on the last row and first col

                # attempt to retrieve depth
                if flag_grid[r + 1, c - 1] != 0:
                    continue
                dep_ngb = bathy[r + 1, c - 1]
                if npy_isnan(dep_ngb) and (r < rows - 2) and c > 1:
                    if flag_grid[r + 2, c - 2] != 0:
                        continue
                    dep_ngb = bathy[r + 2, c - 2]
                # if npy_isnan(dep_ngb) and (r < rows - 3) and c > 2:
                #     if flag_grid[r + 3, c - 3] != 0:
                #         continue
                #     dep_ngb = bathy[r + 3, c - 3]

                # evaluate depth difference
                if not npy_isnan(dep_ngb):
                    ngb_cnt += 1
                    if dep_node - dep_ngb > th:
                        dif_pos_cnt += 1
                    if dep_node - dep_ngb < -th:
                        dif_neg_cnt += 1

            if ngb_cnt == 0:
                continue

            # calculate the ratio among flagged and total neighbors, then use it to decide if a flier
            if (r == 0) or (c == 0) or (r == (rows - 1)) or (c == (cols - 1)):
                thr = 1.0
            elif ngb_cnt <= 4:
                thr = pct1
            else:
                thr = pct2

            pos_ratio = dif_pos_cnt / float(ngb_cnt)
            if pos_ratio >= thr:
                flag_grid[r, c] = 3  # check #3
                logger.info("#3 > + @(%d,%d): %d/%d > node ratio %.2f (threshold: %.2f)"
                             % (r, c, dif_pos_cnt, ngb_cnt, pos_ratio, thr))
                continue

            neg_ratio = dif_neg_cnt / float(ngb_cnt)
            if neg_ratio >= thr:
                flag_grid[r, c] = 3  # check #3
                logger.info("#3 > - @(%d,%d): %d/%d > node ratio %.2f (threshold: %.2f)"
                             % (r, c, dif_neg_cnt, ngb_cnt, neg_ratio, thr))
                continue


# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_small_groups_float(np.ndarray[np.uint8_t, ndim=2, cast=True] grid_bin, float[:, :] bathy, int[:, :] flag_grid, float th, double area_limit,
                         bint check_slivers, bint check_isolated):

    cdef np.npy_intp last_r, last_c, r, c
    cdef np.npy_intp rows = grid_bin.shape[0]
    cdef np.npy_intp cols = grid_bin.shape[1]

    cdef vector[np.npy_intp] nb_cs
    cdef vector[np.npy_intp] nb_rs
    cdef np.npy_intp nbs_sz, ni

    cdef int i, j, conn_count
    cdef int n_labels
    cdef np.ndarray[np.int32_t, ndim=2] img_labels
    cdef np.int32_t nl

    img_labels, n_labels = ndimage.label(grid_bin)
    cdef np.ndarray[np.float64_t, ndim=1] sizes = ndimage.sum(grid_bin, img_labels, range(1, n_labels + 1))

    for i in range(sizes.shape[0]):

        # check only small groups
        if sizes[i] > area_limit:
            continue

        i += 1
        conn_count = 0
        find = False
        last_r = 0
        last_c = 0
        for r in range(4, rows - 4):  # skip bbox boundaries

            for c in range(4, cols - 4):  # skip bbox boundaries

                # skip if the cell does not belong to the current small group
                if img_labels[r, c] != i:
                    continue
                last_r, last_c = r, c

                nb_rs.clear()
                nb_cs.clear()
                # check for a valid connection to a grid body
                #                n1                      n2                      n3                      n4
                nb_rs.push_back(r + 1); nb_rs.push_back(r - 1); nb_rs.push_back(r - 1); nb_rs.push_back(r + 1)
                nb_cs.push_back(c + 1); nb_cs.push_back(c + 1); nb_cs.push_back(c - 1); nb_cs.push_back(c - 1)
                #                n5                      n6                      n7                      n8                      n9                      n10                     n11                     n12
                nb_rs.push_back(r + 2); nb_rs.push_back(r + 2); nb_rs.push_back(r + 0); nb_rs.push_back(r - 2); nb_rs.push_back(r - 2); nb_rs.push_back(r - 2); nb_rs.push_back(r + 0); nb_rs.push_back(r + 2)
                nb_cs.push_back(c + 0); nb_cs.push_back(c + 2); nb_cs.push_back(c + 2); nb_cs.push_back(c + 2); nb_cs.push_back(c + 0); nb_cs.push_back(c - 2); nb_cs.push_back(c - 2); nb_cs.push_back(c - 2)
                #                n13                     n14                     n15                     n16                     n17                     n18                     n19                     n20
                nb_rs.push_back(r + 3); nb_rs.push_back(r + 3); nb_rs.push_back(r + 0); nb_rs.push_back(r - 3); nb_rs.push_back(r - 3); nb_rs.push_back(r - 3); nb_rs.push_back(r + 0); nb_rs.push_back(r + 3)
                nb_cs.push_back(c + 0); nb_cs.push_back(c + 3); nb_cs.push_back(c + 3); nb_cs.push_back(c + 3); nb_cs.push_back(c + 0); nb_cs.push_back(c - 3); nb_cs.push_back(c - 3); nb_cs.push_back(c - 3)
                #                n21                     n22                     n23                     n24                     n25                     n26                     n27                     n28
                nb_rs.push_back(r + 4); nb_rs.push_back(r + 4); nb_rs.push_back(r + 0); nb_rs.push_back(r - 4); nb_rs.push_back(r - 4); nb_rs.push_back(r - 4); nb_rs.push_back(r + 0); nb_rs.push_back(r + 4)
                nb_cs.push_back(c + 0); nb_cs.push_back(c + 4); nb_cs.push_back(c + 4); nb_cs.push_back(c + 4); nb_cs.push_back(c + 0); nb_cs.push_back(c - 4); nb_cs.push_back(c - 4); nb_cs.push_back(c - 4)

                nbs_sz = nb_rs.size()

                for ni in range(nbs_sz):

                    nl = img_labels[nb_rs[ni], nb_cs[ni]]
                    if (nl != 0) and (nl != i) and (sizes[nl - 1] > area_limit):
                        conn_count += 1
                        find = True

                        if (abs(bathy[r, c] - bathy[nb_rs[ni], nb_cs[ni]]) > th) \
                                and check_slivers:
                            flag_grid[r, c] = 4  # check #4
                            logger.info("#4 > n%s @(%s, %s)" % (ni + 1, r, c))
                        break

                if find:
                    break

            if find:
                break

        # it is an isolated group
        if (last_r > 4) and (last_r < rows - 4) and (last_c > 4) and (last_c < cols - 4):
            if (conn_count == 0) and check_isolated:
                flag_grid[last_r, last_c] = 5  # check #5
                logger.info("#5 > @(%s, %s)" % (last_r, last_c))


# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_small_groups_double(np.ndarray[np.uint8_t, ndim=2, cast=True] grid_bin, double[:, :] bathy,
                                int[:, :] flag_grid, float th, double area_limit,
                                bint check_slivers, bint check_isolated):

    cdef np.npy_intp last_r, last_c, r, c
    cdef np.npy_intp rows = grid_bin.shape[0]
    cdef np.npy_intp cols = grid_bin.shape[1]

    cdef vector[np.npy_intp] nb_cs
    cdef vector[np.npy_intp] nb_rs
    cdef np.npy_intp nbs_sz, ni

    cdef int i, j, conn_count
    cdef int n_labels
    cdef np.ndarray[np.int32_t, ndim=2] img_labels
    cdef np.int32_t nl

    img_labels, n_labels = ndimage.label(grid_bin)
    cdef np.ndarray[np.float64_t, ndim=1] sizes = ndimage.sum(grid_bin, img_labels, range(1, n_labels + 1))

    for i in range(sizes.shape[0]):

        # check only small groups
        if sizes[i] > area_limit:
            continue

        i += 1
        conn_count = 0
        find = False
        last_r = 0
        last_c = 0
        for r in range(4, rows - 4):  # skip bbox boundaries

            for c in range(4, cols - 4):  # skip bbox boundaries

                # skip if the cell does not belong to the current small group
                if img_labels[r, c] != i:
                    continue
                last_r, last_c = r, c

                nb_rs.clear()
                nb_cs.clear()
                # check for a valid connection to a grid body
                #                n1                      n2                      n3                      n4
                nb_rs.push_back(r + 1); nb_rs.push_back(r - 1); nb_rs.push_back(r - 1); nb_rs.push_back(r + 1)
                nb_cs.push_back(c + 1); nb_cs.push_back(c + 1); nb_cs.push_back(c - 1); nb_cs.push_back(c - 1)
                #                n5                      n6                      n7                      n8                      n9                      n10                     n11                     n12
                nb_rs.push_back(r + 2); nb_rs.push_back(r + 2); nb_rs.push_back(r + 0); nb_rs.push_back(r - 2); nb_rs.push_back(r - 2); nb_rs.push_back(r - 2); nb_rs.push_back(r + 0); nb_rs.push_back(r + 2)
                nb_cs.push_back(c + 0); nb_cs.push_back(c + 2); nb_cs.push_back(c + 2); nb_cs.push_back(c + 2); nb_cs.push_back(c + 0); nb_cs.push_back(c - 2); nb_cs.push_back(c - 2); nb_cs.push_back(c - 2)
                #                n13                     n14                     n15                     n16                     n17                     n18                     n19                     n20
                nb_rs.push_back(r + 3); nb_rs.push_back(r + 3); nb_rs.push_back(r + 0); nb_rs.push_back(r - 3); nb_rs.push_back(r - 3); nb_rs.push_back(r - 3); nb_rs.push_back(r + 0); nb_rs.push_back(r + 3)
                nb_cs.push_back(c + 0); nb_cs.push_back(c + 3); nb_cs.push_back(c + 3); nb_cs.push_back(c + 3); nb_cs.push_back(c + 0); nb_cs.push_back(c - 3); nb_cs.push_back(c - 3); nb_cs.push_back(c - 3)
                #                n21                     n22                     n23                     n24                     n25                     n26                     n27                     n28
                nb_rs.push_back(r + 4); nb_rs.push_back(r + 4); nb_rs.push_back(r + 0); nb_rs.push_back(r - 4); nb_rs.push_back(r - 4); nb_rs.push_back(r - 4); nb_rs.push_back(r + 0); nb_rs.push_back(r + 4)
                nb_cs.push_back(c + 0); nb_cs.push_back(c + 4); nb_cs.push_back(c + 4); nb_cs.push_back(c + 4); nb_cs.push_back(c + 0); nb_cs.push_back(c - 4); nb_cs.push_back(c - 4); nb_cs.push_back(c - 4)

                nbs_sz = nb_rs.size()

                for ni in range(nbs_sz):

                    nl = img_labels[nb_rs[ni], nb_cs[ni]]
                    if (nl != 0) and (nl != i) and (sizes[nl - 1] > area_limit):
                        conn_count += 1
                        find = True

                        if (abs(bathy[r, c] - bathy[nb_rs[ni], nb_cs[ni]]) > th) \
                                and check_slivers:
                            flag_grid[r, c] = 4  # check #4
                            logger.info("#4 > n%s @(%s, %s)" % (ni + 1, r, c))
                        break

                if find:
                    break

            if find:
                break

        # it is an isolated group
        if (last_r > 4) and (last_r < rows - 4) and (last_c > 4) and (last_c < cols - 4):
            if (conn_count == 0) and check_isolated:
                flag_grid[last_r, last_c] = 5  # check #5
                logger.info("#5 > @(%s, %s)" % (last_r, last_c))


# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_noisy_edges_double(double[:, :] bathy, int[:, :] flag_grid, int dist, float cf):

    logger.debug("[noisy edges] double bathy (dist: %d, cf: %.2f)" % (dist, cf))

    cdef np.npy_intp rows = bathy.shape[0]  # number of rows
    cdef np.npy_intp cols = bathy.shape[1]  # number of columns
    cdef np.npy_intp r, c
    cdef float dep_node, dep_ngb
    cdef float pos_ratio, neg_ratio, thr
    cdef int ngb_cnt
    cdef float min_dep, max_diff, ngb_diff

    # the grid is traversed row by row

    for r in range(rows):  # we get the row

        if (r == 0) or (r == rows - 1):
            continue

        for c in range(cols):  # we get the column

            if (c == 0) or (c == cols - 1):
                continue

            if flag_grid[r, c] != 0:  # avoid existing flagged nodes
                continue

            # for each node in the grid, the depth is retrieved
            dep_node = bathy[r, c]

            # any further calculation is skipped in case of a no-data value
            if npy_isnan(dep_node):
                continue

            ngb_cnt = 0  # initialize the number of neighbors
            ngb_diff = 0.0
            min_dep = -9999.9
            max_diff = 0.0

            # - left node

            # attempt to retrieve depth
            if flag_grid[r, c - 1] != 0:
                continue
            dep_ngb = bathy[r, c - 1]
            if npy_isnan(dep_ngb) and c > 1:
                if flag_grid[r, c - 2] != 0:
                    continue
                dep_ngb = bathy[r, c - 2]
            if npy_isnan(dep_ngb) and c > 2 and dist > 2:
                if flag_grid[r, c - 3] != 0:
                    continue
                dep_ngb = bathy[r, c - 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - right node

            # attempt to retrieve depth
            if flag_grid[r, c + 1] != 0:
                continue
            dep_ngb = bathy[r, c + 1]
            if npy_isnan(dep_ngb) and (c < cols - 2):
                if flag_grid[r, c + 2] != 0:
                    continue
                dep_ngb = bathy[r, c + 2]
            if npy_isnan(dep_ngb) and (c < cols - 3) and dist > 2:
                if flag_grid[r, c + 3] != 0:
                    continue
                dep_ngb = bathy[r, c + 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom node

            # attempt to retrieve depth
            if flag_grid[r - 1, c] != 0:
                continue
            dep_ngb = bathy[r - 1, c]
            if npy_isnan(dep_ngb) and r > 1:
                if flag_grid[r - 2, c] != 0:
                    continue
                dep_ngb = bathy[r - 2, c]
            if npy_isnan(dep_ngb) and r > 2  and dist > 2:
                if flag_grid[r - 3, c] != 0:
                    continue
                dep_ngb = bathy[r - 3, c]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top node

            # attempt to retrieve depth
            if flag_grid[r + 1, c] != 0:
                continue
            dep_ngb = bathy[r + 1, c]
            if npy_isnan(dep_ngb) and (r < rows - 2):
                if flag_grid[r + 2, c] != 0:
                    continue
                dep_ngb = bathy[r + 2, c]
            if npy_isnan(dep_ngb) and (r < rows - 3)  and dist > 2:
                if flag_grid[r + 3, c] != 0:
                    continue
                dep_ngb = bathy[r + 3, c]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom-left node

            # attempt to retrieve depth
            if flag_grid[r - 1, c - 1] != 0:
                continue
            dep_ngb = bathy[r - 1, c - 1]
            if npy_isnan(dep_ngb) and r > 1 and c > 1  and dist > 2:
                if flag_grid[r - 2, c - 2] != 0:
                    continue
                dep_ngb = bathy[r - 2, c - 2]
            # if npy_isnan(dep_ngb) and r > 2 and c > 2:
            #     if flag_grid[r - 3, c - 3] != 0:
            #         continue
            #     dep_ngb = bathy[r - 3, c - 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top-right node

            # attempt to retrieve depth
            if flag_grid[r + 1, c + 1] != 0:
                continue
            dep_ngb = bathy[r + 1, c + 1]
            if npy_isnan(dep_ngb) and (r < rows - 2) and (c < cols - 2) and dist > 2:
                if flag_grid[r + 2, c + 2] != 0:
                    continue
                dep_ngb = bathy[r + 2, c + 2]
            # if npy_isnan(dep_ngb) and (r < rows - 3) and (c < cols - 3):
            #     if flag_grid[r + 3, c + 3] != 0:
            #         continue
            #     dep_ngb = bathy[r + 3, c + 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom-right node

            # attempt to retrieve depth
            if flag_grid[r - 1, c + 1] != 0:
                continue
            dep_ngb = bathy[r - 1, c + 1]
            if npy_isnan(dep_ngb) and r > 1 and (c < cols - 2) and dist > 2:
                if flag_grid[r - 2, c + 2] != 0:
                    continue
                dep_ngb = bathy[r - 2, c + 2]
            # if npy_isnan(dep_ngb) and r > 2 and c > 2:
            #     if flag_grid[r - 3, c + 3] != 0:
            #         continue
            #     dep_ngb = bathy[r - 3, c + 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top-left node

            # attempt to retrieve depth
            if flag_grid[r + 1, c - 1] != 0:
                continue
            dep_ngb = bathy[r + 1, c - 1]
            if npy_isnan(dep_ngb) and (r < rows - 2) and c > 1  and dist > 2:
                if flag_grid[r + 2, c - 2] != 0:
                    continue
                dep_ngb = bathy[r + 2, c - 2]
            # if npy_isnan(dep_ngb) and (r < rows - 3) and c > 2:
            #     if flag_grid[r + 3, c - 3] != 0:
            #         continue
            #     dep_ngb = bathy[r + 3, c - 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            if ngb_cnt == 0:
                continue

            if ngb_cnt > 6:
                continue

            if min_dep >= -100.0:
                thr = (0.25 + (0.013 * -min_dep) ** 2) ** 0.5

            else:
                thr = (1. + (0.023 * -min_dep) ** 2) ** 0.5

            if max_diff > cf * thr:
                flag_grid[r, c] = 6  # check #6
                logger.debug("(%s, %s) count: %s, max diff: %.2f, min z: %.2f -> th: %.2f"
                             % (r, c, ngb_cnt, max_diff, min_dep, thr))

# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_noisy_edges_float(float[:, :] bathy, int[:, :] flag_grid, int dist, float cf):

    logger.debug("[noisy edges] float bathy (dist: %d, cf: %.2f)" % (dist, cf))

    cdef np.npy_intp rows = bathy.shape[0]  # number of rows
    cdef np.npy_intp cols = bathy.shape[1]  # number of columns
    cdef np.npy_intp r, c
    cdef float dep_node, dep_ngb
    cdef float pos_ratio, neg_ratio, thr
    cdef int ngb_cnt
    cdef float min_dep, max_diff, ngb_diff

    # the grid is traversed row by row

    for r in range(rows):  # we get the row

        if (r == 0) or (r == rows - 1):
            continue

        for c in range(cols):  # we get the column

            if (c == 0) or (c == cols - 1):
                continue

            if flag_grid[r, c] != 0:  # avoid existing flagged nodes
                continue

            # for each node in the grid, the depth is retrieved
            dep_node = bathy[r, c]

            # any further calculation is skipped in case of a no-data value
            if npy_isnan(dep_node):
                continue

            ngb_cnt = 0  # initialize the number of neighbors
            ngb_diff = 0.0
            min_dep = -9999.9
            max_diff = 0.0

            # - left node

            # attempt to retrieve depth
            if flag_grid[r, c - 1] != 0:
                continue
            dep_ngb = bathy[r, c - 1]
            if npy_isnan(dep_ngb) and c > 1:
                if flag_grid[r, c - 2] != 0:
                    continue
                dep_ngb = bathy[r, c - 2]
            if npy_isnan(dep_ngb) and c > 2  and dist > 2:
                if flag_grid[r, c - 3] != 0:
                    continue
                dep_ngb = bathy[r, c - 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - right node

            # attempt to retrieve depth
            if flag_grid[r, c + 1] != 0:
                continue
            dep_ngb = bathy[r, c + 1]
            if npy_isnan(dep_ngb) and (c < cols - 2):
                if flag_grid[r, c + 2] != 0:
                    continue
                dep_ngb = bathy[r, c + 2]
            if npy_isnan(dep_ngb) and (c < cols - 3) and dist > 2:
                if flag_grid[r, c + 3] != 0:
                    continue
                dep_ngb = bathy[r, c + 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom node

            # attempt to retrieve depth
            if flag_grid[r - 1, c] != 0:
                continue
            dep_ngb = bathy[r - 1, c]
            if npy_isnan(dep_ngb) and r > 1:
                if flag_grid[r - 2, c] != 0:
                    continue
                dep_ngb = bathy[r - 2, c]
            if npy_isnan(dep_ngb) and r > 2 and dist > 2:
                if flag_grid[r - 3, c] != 0:
                    continue
                dep_ngb = bathy[r - 3, c]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top node

            # attempt to retrieve depth
            if flag_grid[r + 1, c] != 0:
                continue
            dep_ngb = bathy[r + 1, c]
            if npy_isnan(dep_ngb) and (r < rows - 2):
                if flag_grid[r + 2, c] != 0:
                    continue
                dep_ngb = bathy[r + 2, c]
            if npy_isnan(dep_ngb) and (r < rows - 3) and dist > 2:
                if flag_grid[r + 3, c] != 0:
                    continue
                dep_ngb = bathy[r + 3, c]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom-left node

            # attempt to retrieve depth
            if flag_grid[r - 1, c - 1] != 0:
                continue
            dep_ngb = bathy[r - 1, c - 1]
            if npy_isnan(dep_ngb) and r > 1 and c > 1 and dist > 2:
                if flag_grid[r - 2, c - 2] != 0:
                    continue
                dep_ngb = bathy[r - 2, c - 2]
            # if npy_isnan(dep_ngb) and r > 2 and c > 2:
            #     if flag_grid[r - 3, c - 3] != 0:
            #         continue
            #     dep_ngb = bathy[r - 3, c - 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top-right node

            # attempt to retrieve depth
            if flag_grid[r + 1, c + 1] != 0:
                continue
            dep_ngb = bathy[r + 1, c + 1]
            if npy_isnan(dep_ngb) and (r < rows - 2) and (c < cols - 2) and dist > 2:
                if flag_grid[r + 2, c + 2] != 0:
                    continue
                dep_ngb = bathy[r + 2, c + 2]
            # if npy_isnan(dep_ngb) and (r < rows - 3) and (c < cols - 3):
            #     if flag_grid[r + 3, c + 3] != 0:
            #         continue
            #     dep_ngb = bathy[r + 3, c + 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom-right node

            # attempt to retrieve depth
            if flag_grid[r - 1, c + 1] != 0:
                continue
            dep_ngb = bathy[r - 1, c + 1]
            if npy_isnan(dep_ngb) and r > 1 and (c < cols - 2) and dist > 2:
                if flag_grid[r - 2, c + 2] != 0:
                    continue
                dep_ngb = bathy[r - 2, c + 2]
            # if npy_isnan(dep_ngb) and r > 2 and c > 2:
            #     if flag_grid[r - 3, c + 3] != 0:
            #         continue
            #     dep_ngb = bathy[r - 3, c + 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top-left node

            # attempt to retrieve depth
            if flag_grid[r + 1, c - 1] != 0:
                continue
            dep_ngb = bathy[r + 1, c - 1]
            if npy_isnan(dep_ngb) and (r < rows - 2) and c > 1 and dist > 2:
                if flag_grid[r + 2, c - 2] != 0:
                    continue
                dep_ngb = bathy[r + 2, c - 2]
            # if npy_isnan(dep_ngb) and (r < rows - 3) and c > 2:
            #     if flag_grid[r + 3, c - 3] != 0:
            #         continue
            #     dep_ngb = bathy[r + 3, c - 3]

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            if ngb_cnt == 0:
                # managed by #5
                continue

            if ngb_cnt > 6:
                # not an edge
                continue

            if min_dep >= -100.0:
                thr = (0.25 + (0.013 * -min_dep) ** 2) ** 0.5

            else:
                thr = (1. + (0.023 * -min_dep) ** 2) ** 0.5

            if max_diff > cf * thr:
                flag_grid[r, c] = 6  # check #6
                logger.debug("(%s, %s) count: %s, max diff: %.2f, min z: %.2f -> th: %.2f"
                             % (r, c, ngb_cnt, max_diff, min_dep, thr))


# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_noisy_margins_double(double[:, :] bathy, int[:, :] flag_grid, int dist, float cf):

    logger.debug("[noisy margins] double bathy (dist: %d, cf: %.2f)" % (dist, cf))

    cdef np.npy_intp rows = bathy.shape[0]  # number of rows
    cdef np.npy_intp cols = bathy.shape[1]  # number of columns
    cdef np.npy_intp r, c
    cdef float dep_node, dep_ngb
    cdef float pos_ratio, neg_ratio, thr
    cdef int ngb_cnt
    cdef float min_dep, max_diff, ngb_diff

    # the grid is traversed row by row

    for r in range(rows):  # we get the row

        if (r == 0) or (r == rows - 1):
            continue

        for c in range(cols):  # we get the column

            if (c == 0) or (c == cols - 1):
                continue

            if flag_grid[r, c] != 0:  # avoid existing flagged nodes
                continue

            # for each node in the grid, the depth is retrieved
            dep_node = bathy[r, c]

            # any further calculation is skipped in case of a no-data value
            if npy_isnan(dep_node):
                continue

            ngb_cnt = 0  # initialize the number of neighbors
            ngb_diff = 0.0
            min_dep = -9999.9
            max_diff = 0.0

            # - left node

            # attempt to retrieve depth
            if flag_grid[r, c - 1] != 0:
                continue
            dep_ngb = bathy[r, c - 1]
            if npy_isnan(dep_ngb) and c > 1:
                dep_ngb = bathy[r, c - 2]
            if npy_isnan(dep_ngb) and c > 2 and dist > 2:
                dep_ngb = bathy[r, c - 3]
            if c > 3 and dist > 2:
                if flag_grid[r, c - 2] != 0:
                    continue
                if flag_grid[r, c - 3] != 0:
                    continue
                if flag_grid[r, c - 4] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - right node

            # attempt to retrieve depth
            if flag_grid[r, c + 1] != 0:
                continue
            dep_ngb = bathy[r, c + 1]
            if npy_isnan(dep_ngb) and (c < cols - 2):
                if flag_grid[r, c + 2] != 0:
                    continue
                dep_ngb = bathy[r, c + 2]
            if npy_isnan(dep_ngb) and (c < cols - 3) and dist > 2:
                if flag_grid[r, c + 3] != 0:
                    continue
                dep_ngb = bathy[r, c + 3]
            if (c < cols - 4) and dist > 2:
                if flag_grid[r, c + 2] != 0:
                    continue
                if flag_grid[r, c + 3] != 0:
                    continue
                if flag_grid[r, c + 4] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom node

            # attempt to retrieve depth
            if flag_grid[r - 1, c] != 0:
                continue
            dep_ngb = bathy[r - 1, c]
            if npy_isnan(dep_ngb) and r > 1:
                if flag_grid[r - 2, c] != 0:
                    continue
                dep_ngb = bathy[r - 2, c]
            if npy_isnan(dep_ngb) and r > 2  and dist > 2:
                if flag_grid[r - 3, c] != 0:
                    continue
                dep_ngb = bathy[r - 3, c]
            if r > 3  and dist > 2:
                if flag_grid[r - 2, c] != 0:
                    continue
                if flag_grid[r - 3, c] != 0:
                    continue
                if flag_grid[r - 4, c] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top node

            # attempt to retrieve depth
            if flag_grid[r + 1, c] != 0:
                continue
            dep_ngb = bathy[r + 1, c]
            if npy_isnan(dep_ngb) and (r < rows - 2):
                if flag_grid[r + 2, c] != 0:
                    continue
                dep_ngb = bathy[r + 2, c]
            if npy_isnan(dep_ngb) and (r < rows - 3)  and dist > 2:
                if flag_grid[r + 3, c] != 0:
                    continue
                dep_ngb = bathy[r + 3, c]
            if (r < rows - 4)  and dist > 2:
                if flag_grid[r + 2, c] != 0:
                    continue
                if flag_grid[r + 3, c] != 0:
                    continue
                if flag_grid[r + 4, c] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom-left node

            # attempt to retrieve depth
            if flag_grid[r - 1, c - 1] != 0:
                continue
            dep_ngb = bathy[r - 1, c - 1]
            if npy_isnan(dep_ngb) and r > 1 and c > 1 and dist > 2:
                if flag_grid[r - 2, c - 2] != 0:
                    continue
                dep_ngb = bathy[r - 2, c - 2]
            if r > 2 and c > 2 and dist > 2:
                if flag_grid[r - 1, c - 3] != 0:
                    continue
                if flag_grid[r - 2, c - 3] != 0:
                    continue
                if flag_grid[r - 3, c - 3] != 0:
                    continue
                if flag_grid[r - 1, c - 2] != 0:
                    continue
                if flag_grid[r - 2, c - 2] != 0:
                    continue
                if flag_grid[r - 3, c - 2] != 0:
                    continue
                if flag_grid[r - 2, c - 1] != 0:
                    continue
                if flag_grid[r - 3, c - 1] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top-right node

            # attempt to retrieve depth
            if flag_grid[r + 1, c + 1] != 0:
                continue
            dep_ngb = bathy[r + 1, c + 1]
            if npy_isnan(dep_ngb) and (r < rows - 2) and (c < cols - 2) and dist > 2:
                if flag_grid[r + 2, c + 2] != 0:
                    continue
                dep_ngb = bathy[r + 2, c + 2]
            if (r < rows - 3) and (c < cols - 3) and dist > 2:
                if flag_grid[r + 2, c + 1] != 0:
                    continue
                if flag_grid[r + 3, c + 1] != 0:
                    continue
                if flag_grid[r + 1, c + 2] != 0:
                    continue
                if flag_grid[r + 2, c + 2] != 0:
                    continue
                if flag_grid[r + 3, c + 2] != 0:
                    continue
                if flag_grid[r + 1, c + 3] != 0:
                    continue
                if flag_grid[r + 2, c + 3] != 0:
                    continue
                if flag_grid[r + 3, c + 3] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom-right node

            # attempt to retrieve depth
            if flag_grid[r - 1, c + 1] != 0:
                continue
            dep_ngb = bathy[r - 1, c + 1]
            if npy_isnan(dep_ngb) and r > 1 and (c < cols - 2) and dist > 2:
                if flag_grid[r - 2, c + 2] != 0:
                    continue
                dep_ngb = bathy[r - 2, c + 2]
            if r > 2 and c > 2 and dist > 2:
                if flag_grid[r - 2, c + 1] != 0:
                    continue
                if flag_grid[r - 3, c + 1] != 0:
                    continue
                if flag_grid[r - 1, c + 2] != 0:
                    continue
                if flag_grid[r - 2, c + 2] != 0:
                    continue
                if flag_grid[r - 3, c + 2] != 0:
                    continue
                if flag_grid[r - 1, c + 3] != 0:
                    continue
                if flag_grid[r - 2, c + 3] != 0:
                    continue
                if flag_grid[r - 3, c + 3] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top-left node

            # attempt to retrieve depth
            if flag_grid[r + 1, c - 1] != 0:
                continue
            dep_ngb = bathy[r + 1, c - 1]
            if npy_isnan(dep_ngb) and (r < rows - 2) and c > 1  and dist > 2:
                dep_ngb = bathy[r + 2, c - 2]
            if (r < rows - 3) and c > 2 and dist > 2:
                if flag_grid[r + 2, c - 1] != 0:
                    continue
                if flag_grid[r + 3, c - 1] != 0:
                    continue
                if flag_grid[r + 1, c - 2] != 0:
                    continue
                if flag_grid[r + 2, c - 2] != 0:
                    continue
                if flag_grid[r + 3, c - 2] != 0:
                    continue
                if flag_grid[r + 1, c - 3] != 0:
                    continue
                if flag_grid[r + 2, c - 3] != 0:
                    continue
                if flag_grid[r + 3, c - 3] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            if ngb_cnt == 0:
                continue

            if ngb_cnt >= 6:
                continue

            if min_dep >= -100.0:
                thr = (0.25 + (0.013 * -min_dep) ** 2) ** 0.5

            else:
                thr = (1. + (0.023 * -min_dep) ** 2) ** 0.5

            if max_diff > cf * thr:
                flag_grid[r, c] = 7  # check #7
                logger.debug("(%s, %s) count: %s, max diff: %.2f, min z: %.2f -> th: %.2f"
                             % (r, c, ngb_cnt, max_diff, min_dep, thr))


# noinspection PyUnresolvedReferences
@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef check_noisy_margins_float(float[:, :] bathy, int[:, :] flag_grid, int dist, float cf):

    logger.debug("[noisy margins] float bathy (dist: %d, cf: %.2f)" % (dist, cf))

    cdef np.npy_intp rows = bathy.shape[0]  # number of rows
    cdef np.npy_intp cols = bathy.shape[1]  # number of columns
    cdef np.npy_intp r, c
    cdef float dep_node, dep_ngb
    cdef float pos_ratio, neg_ratio, thr
    cdef int ngb_cnt
    cdef float min_dep, max_diff, ngb_diff

    # the grid is traversed row by row

    for r in range(rows):  # we get the row

        if (r == 0) or (r == rows - 1):
            continue

        for c in range(cols):  # we get the column

            if (c == 0) or (c == cols - 1):
                continue

            if flag_grid[r, c] != 0:  # avoid existing flagged nodes
                continue

            # for each node in the grid, the depth is retrieved
            dep_node = bathy[r, c]

            # any further calculation is skipped in case of a no-data value
            if npy_isnan(dep_node):
                continue

            ngb_cnt = 0  # initialize the number of neighbors
            ngb_diff = 0.0
            min_dep = -9999.9
            max_diff = 0.0

            # - left node

            # attempt to retrieve depth
            if flag_grid[r, c - 1] != 0:
                continue
            dep_ngb = bathy[r, c - 1]
            if npy_isnan(dep_ngb) and c > 1:
                dep_ngb = bathy[r, c - 2]
            if npy_isnan(dep_ngb) and c > 2 and dist > 2:
                dep_ngb = bathy[r, c - 3]
            if c > 3 and dist > 2:
                if flag_grid[r, c - 2] != 0:
                    continue
                if flag_grid[r, c - 3] != 0:
                    continue
                if flag_grid[r, c - 4] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - right node

            # attempt to retrieve depth
            if flag_grid[r, c + 1] != 0:
                continue
            dep_ngb = bathy[r, c + 1]
            if npy_isnan(dep_ngb) and (c < cols - 2):
                if flag_grid[r, c + 2] != 0:
                    continue
                dep_ngb = bathy[r, c + 2]
            if npy_isnan(dep_ngb) and (c < cols - 3) and dist > 2:
                if flag_grid[r, c + 3] != 0:
                    continue
                dep_ngb = bathy[r, c + 3]
            if (c < cols - 4) and dist > 2:
                if flag_grid[r, c + 2] != 0:
                    continue
                if flag_grid[r, c + 3] != 0:
                    continue
                if flag_grid[r, c + 4] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom node

            # attempt to retrieve depth
            if flag_grid[r - 1, c] != 0:
                continue
            dep_ngb = bathy[r - 1, c]
            if npy_isnan(dep_ngb) and r > 1:
                if flag_grid[r - 2, c] != 0:
                    continue
                dep_ngb = bathy[r - 2, c]
            if npy_isnan(dep_ngb) and r > 2  and dist > 2:
                if flag_grid[r - 3, c] != 0:
                    continue
                dep_ngb = bathy[r - 3, c]
            if r > 3  and dist > 2:
                if flag_grid[r - 2, c] != 0:
                    continue
                if flag_grid[r - 3, c] != 0:
                    continue
                if flag_grid[r - 4, c] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top node

            # attempt to retrieve depth
            if flag_grid[r + 1, c] != 0:
                continue
            dep_ngb = bathy[r + 1, c]
            if npy_isnan(dep_ngb) and (r < rows - 2):
                if flag_grid[r + 2, c] != 0:
                    continue
                dep_ngb = bathy[r + 2, c]
            if npy_isnan(dep_ngb) and (r < rows - 3)  and dist > 2:
                if flag_grid[r + 3, c] != 0:
                    continue
                dep_ngb = bathy[r + 3, c]
            if (r < rows - 4)  and dist > 2:
                if flag_grid[r + 2, c] != 0:
                    continue
                if flag_grid[r + 3, c] != 0:
                    continue
                if flag_grid[r + 4, c] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom-left node

            # attempt to retrieve depth
            if flag_grid[r - 1, c - 1] != 0:
                continue
            dep_ngb = bathy[r - 1, c - 1]
            if npy_isnan(dep_ngb) and r > 1 and c > 1 and dist > 2:
                if flag_grid[r - 2, c - 2] != 0:
                    continue
                dep_ngb = bathy[r - 2, c - 2]
            if r > 2 and c > 2 and dist > 2:
                if flag_grid[r - 1, c - 3] != 0:
                    continue
                if flag_grid[r - 2, c - 3] != 0:
                    continue
                if flag_grid[r - 3, c - 3] != 0:
                    continue
                if flag_grid[r - 1, c - 2] != 0:
                    continue
                if flag_grid[r - 2, c - 2] != 0:
                    continue
                if flag_grid[r - 3, c - 2] != 0:
                    continue
                if flag_grid[r - 2, c - 1] != 0:
                    continue
                if flag_grid[r - 3, c - 1] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top-right node

            # attempt to retrieve depth
            if flag_grid[r + 1, c + 1] != 0:
                continue
            dep_ngb = bathy[r + 1, c + 1]
            if npy_isnan(dep_ngb) and (r < rows - 2) and (c < cols - 2) and dist > 2:
                if flag_grid[r + 2, c + 2] != 0:
                    continue
                dep_ngb = bathy[r + 2, c + 2]
            if (r < rows - 3) and (c < cols - 3) and dist > 2:
                if flag_grid[r + 2, c + 1] != 0:
                    continue
                if flag_grid[r + 3, c + 1] != 0:
                    continue
                if flag_grid[r + 1, c + 2] != 0:
                    continue
                if flag_grid[r + 2, c + 2] != 0:
                    continue
                if flag_grid[r + 3, c + 2] != 0:
                    continue
                if flag_grid[r + 1, c + 3] != 0:
                    continue
                if flag_grid[r + 2, c + 3] != 0:
                    continue
                if flag_grid[r + 3, c + 3] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - bottom-right node

            # attempt to retrieve depth
            if flag_grid[r - 1, c + 1] != 0:
                continue
            dep_ngb = bathy[r - 1, c + 1]
            if npy_isnan(dep_ngb) and r > 1 and (c < cols - 2) and dist > 2:
                if flag_grid[r - 2, c + 2] != 0:
                    continue
                dep_ngb = bathy[r - 2, c + 2]
            if r > 2 and c > 2 and dist > 2:
                if flag_grid[r - 2, c + 1] != 0:
                    continue
                if flag_grid[r - 3, c + 1] != 0:
                    continue
                if flag_grid[r - 1, c + 2] != 0:
                    continue
                if flag_grid[r - 2, c + 2] != 0:
                    continue
                if flag_grid[r - 3, c + 2] != 0:
                    continue
                if flag_grid[r - 1, c + 3] != 0:
                    continue
                if flag_grid[r - 2, c + 3] != 0:
                    continue
                if flag_grid[r - 3, c + 3] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            # - top-left node

            # attempt to retrieve depth
            if flag_grid[r + 1, c - 1] != 0:
                continue
            dep_ngb = bathy[r + 1, c - 1]
            if npy_isnan(dep_ngb) and (r < rows - 2) and c > 1  and dist > 2:
                dep_ngb = bathy[r + 2, c - 2]
            if (r < rows - 3) and c > 2 and dist > 2:
                if flag_grid[r + 2, c - 1] != 0:
                    continue
                if flag_grid[r + 3, c - 1] != 0:
                    continue
                if flag_grid[r + 1, c - 2] != 0:
                    continue
                if flag_grid[r + 2, c - 2] != 0:
                    continue
                if flag_grid[r + 3, c - 2] != 0:
                    continue
                if flag_grid[r + 1, c - 3] != 0:
                    continue
                if flag_grid[r + 2, c - 3] != 0:
                    continue
                if flag_grid[r + 3, c - 3] != 0:
                    continue

            # evaluate depth difference
            if not npy_isnan(dep_ngb):
                ngb_cnt += 1
                if dep_ngb > min_dep:
                    min_dep = dep_ngb
                ngb_diff = abs(dep_node - dep_ngb)
                if ngb_diff > max_diff:
                    max_diff = ngb_diff

            if ngb_cnt == 0:
                continue

            if ngb_cnt >= 6:
                continue

            if min_dep >= -100.0:
                thr = (0.25 + (0.013 * -min_dep) ** 2) ** 0.5

            else:
                thr = (1. + (0.023 * -min_dep) ** 2) ** 0.5

            if max_diff > cf * thr:
                flag_grid[r, c] = 7  # check #7
                logger.debug("(%s, %s) count: %s, max diff: %.2f, min z: %.2f -> th: %.2f"
                             % (r, c, ngb_cnt, max_diff, min_dep, thr))
