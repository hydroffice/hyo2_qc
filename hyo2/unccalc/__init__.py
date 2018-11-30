"""
Hydro-Package
Uncertainty Calculator
"""
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__version__ = '1.0.0'
__doc__ = "Uncertainty Calculator"
__author__ = 'gmasetti@ccom.unh.edu; tyanne.faulkes@noaa.gov'
__license__ = 'LGPLv3 license'
__copyright__ = 'Copyright 2018 University of New Hampshire, Center for Coastal and Ocean Mapping'


def hyo():
    return __doc__, __version__
