import os
import numpy as np
from matplotlib import pyplot as plt
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(os.path.basename(__file__))

from hyo2.qc.survey.fliers.thresholds_v8 import ThresholdsV8

np.random.seed(0)

arr_sz = 1000
# array = np.arange(100, dtype=np.float).reshape(10, 10)
array = np.random.rand(arr_sz, arr_sz) * 100.0
array[5, 5] = np.nan
array[5, 6] = np.nan
array[5, 7] = np.nan
array[6, 5] = np.nan
array[6, 6] = np.nan
array[6, 7] = np.nan
array[7, 5] = np.nan
array[7, 6] = np.nan
array[7, 7] = np.nan
array[int(array.shape[0]*.1), int(array.shape[1]*.1)] = np.nan
array[int(array.shape[0]*.2), int(array.shape[1]*.1)] = np.nan
array[int(array.shape[0]*.3), int(array.shape[1]*.1)] = np.nan
array[int(array.shape[0]*.1), int(array.shape[1]*.7)] = np.nan

# ma_array = np.ma.masked_invalid(array)


ths = ThresholdsV8()
ths.calculate(array)

# logger.debug("nmad:\n%s" % out_mad)

# plt.figure("input")
# m = plt.imshow(ma_array, interpolation='none')
# plt.colorbar(m)
# plt.show()

# ths.plot()
