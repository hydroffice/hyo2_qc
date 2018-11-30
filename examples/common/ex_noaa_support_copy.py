from hyo2.qc.common import default_logging
import sys
import logging

default_logging.load()
logger = logging.getLogger()


from hyo2.qc.common.noaa_support.noaa_support import NOAASupport


noaa_support = NOAASupport()

system_noaa_support_folder = noaa_support.system_noaa_support_folder()
logger.debug("system folder: %s" % system_noaa_support_folder)
if noaa_support.system_noaa_support_folder_present():
    logger.debug("system version: %s" % noaa_support.system_noaa_support_folder_version())
    noaa_support.delete_system_noaa_support_files()

noaa_support.copy_local_to_system()
logger.debug("system batch file: %s" % noaa_support.system_batch_file())

noaa_support.exec_system_batch()
