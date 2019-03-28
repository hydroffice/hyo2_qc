import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

array_path = r'C:\Users\gmasetti\Desktop\array\array_0'

array = np.loadtxt(array_path)
array = np.ma.array(array, mask=np.isnan(array))
logger.debug("masked array:\n%s" % array)

logger.debug("numpy version: %s" % np.__version__)
logger.debug("np.nanmedian: %s" % np.nanmedian(array))
logger.debug("np.na.median: %s" % np.ma.median(array))
