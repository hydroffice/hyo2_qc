import numpy as np
cimport numpy as np
import warnings
warnings.simplefilter(action="ignore", category=RuntimeWarning)
import logging
logger = logging.getLogger(__name__)

import cython
from libc.math cimport isnan


# noinspection PyUnresolvedReferences
@cython.cdivision(False)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef calc_tvu_qc_dd(double[:, :] bathy, double[:, :] product_uncertainty, double pu_nodata, double[:,:] tvu_qc):

    cdef int rows = bathy.shape[0]
    cdef int cols = bathy.shape[1]

    cdef int r, c
    cdef np.float64_t bathy_value
    cdef np.float64_t pr_unc_value
    cdef np.float64_t NaN = np.nan

    for r in range(rows):

        for c in range(cols):

            bathy_value = bathy[r, c]
            pr_unc_value = product_uncertainty[r, c]

            if isnan(bathy_value) or (pr_unc_value == pu_nodata):
                tvu_qc[r, c] = NaN

            elif bathy_value <= 100.0:
                tvu_qc[r, c] = pr_unc_value / ((0.25 + (0.013 * bathy_value) ** 2) ** 0.5)

            else:
                tvu_qc[r, c] = pr_unc_value / ((1. + (0.023 * bathy_value) ** 2) ** 0.5)


# noinspection PyUnresolvedReferences
@cython.cdivision(False)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef calc_tvu_qc_df(double[:, :] bathy, float[:, :] product_uncertainty, float pu_nodata, double[:,:] tvu_qc):

    cdef int rows = bathy.shape[0]
    cdef int cols = bathy.shape[1]

    cdef int r, c
    cdef np.float64_t bathy_value
    cdef np.float32_t pr_unc_value
    cdef np.float64_t NaN = np.nan

    for r in range(rows):

        for c in range(cols):

            bathy_value = bathy[r, c]
            pr_unc_value = product_uncertainty[r, c]

            if isnan(bathy_value) or (pr_unc_value == pu_nodata):
                tvu_qc[r, c] = NaN
                # logger.debug("is nan: %d %d" % (r, c))

            elif bathy_value <= 100.0:
                tvu_qc[r, c] = pr_unc_value / ((0.25 + (0.013 * bathy_value) ** 2) ** 0.5)

            else:
                tvu_qc[r, c] = pr_unc_value / ((1. + (0.023 * bathy_value) ** 2) ** 0.5)

# noinspection PyUnresolvedReferences
@cython.cdivision(False)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef calc_tvu_qc_fd(float[:, :] bathy, double[:, :] product_uncertainty, double pu_nodata, float[:,:] tvu_qc):

    cdef int rows = bathy.shape[0]
    cdef int cols = bathy.shape[1]

    cdef int r, c
    cdef np.float32_t bathy_value
    cdef np.float64_t pr_unc_value
    cdef np.float32_t NaN = np.nan

    for r in range(rows):

        for c in range(cols):

            bathy_value = bathy[r, c]
            pr_unc_value = product_uncertainty[r, c]

            if isnan(bathy_value) or (pr_unc_value == pu_nodata):
                tvu_qc[r, c] = NaN

            elif bathy_value <= 100.0:
                tvu_qc[r, c] = pr_unc_value / ((0.25 + (0.013 * bathy_value) ** 2) ** 0.5)

            else:
                tvu_qc[r, c] = pr_unc_value / ((1. + (0.023 * bathy_value) ** 2) ** 0.5)


# noinspection PyUnresolvedReferences
@cython.cdivision(False)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
#@cython.profile(True)
cpdef calc_tvu_qc_ff(float[:, :] bathy, float[:, :] product_uncertainty, float pu_nodata, float[:,:] tvu_qc):

    cdef int rows = bathy.shape[0]
    cdef int cols = bathy.shape[1]

    cdef int r, c
    cdef np.float32_t bathy_value
    cdef np.float32_t pr_unc_value
    cdef np.float32_t NaN = np.nan

    for r in range(rows):

        for c in range(cols):

            bathy_value = bathy[r, c]
            pr_unc_value = product_uncertainty[r, c]

            if isnan(bathy_value) or (pr_unc_value == pu_nodata):
                tvu_qc[r, c] = NaN
                # logger.debug("is nan: %d %d" % (r, c))

            elif bathy_value <= 100.0:
                tvu_qc[r, c] = pr_unc_value / ((0.25 + (0.013 * bathy_value) ** 2) ** 0.5)

            else:
                tvu_qc[r, c] = pr_unc_value / ((1. + (0.023 * bathy_value) ** 2) ** 0.5)
