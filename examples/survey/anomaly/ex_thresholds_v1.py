import os
import numpy as np
import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.survey.anomaly.anomaly_detector_v1_thresholds import ThresholdsV1

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.ca", ])

np.random.seed(0)

arr_sz = 1000
array = np.random.rand(arr_sz, arr_sz) * 150.0
array[5:8, 5:7] = np.nan
array[15:18, 25:27] = np.nan
# array[int(array.shape[0]*.2), int(array.shape[1]*.1)] = np.nan
# array[int(array.shape[0]*.3), int(array.shape[1]*.1)] = np.nan
# array[int(array.shape[0]*.1), int(array.shape[1]*.7)] = np.nan

array = ThresholdsV1.nan_gaussian_filter(array)

ths = ThresholdsV1()
ths.calculate(array)

ths.plot()
