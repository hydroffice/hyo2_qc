from hyo2.qc.common import default_logging
import sys
import logging

default_logging.load()
logger = logging.getLogger()


from hyo2.qc.common.noaa_support.noaa_support import NOAASupport


noaa_support = NOAASupport()

if noaa_support.internal_zip_path_exists():
    internal_zip_path = noaa_support.internal_zip_path()
    logger.debug("internal zip: %s" % internal_zip_path)

    success = noaa_support.unzip_internal_zip()
    logger.debug("installed internal zip: %s" % success)
    if not success:
        exit(-1)

# success = noaa_support.download_from_noaa()
# logger.debug("download from noaa: %s" % success)
# if not success:
#     exit(-1)

# success = noaa_support.download_from_unh()
# logger.debug("download from unh: %s" % success)
# if not success:
#     exit(-1)

# noaa_support.delete_local_noaa_support_files()
# noaa_support.open_local_noaa_support_folder()

# if not noaa_support.local_noaa_support_folder_present():
#     exit(-1)

# logger.debug("Local folder present: %s" % noaa_support.local_noaa_support_folder())
# logger.debug("Local version: %s" % noaa_support.local_noaa_support_folder_version())

bat_exists = noaa_support.check_local_batch_file_exists()
if bat_exists:
    logger.debug("local batch file: %s" % noaa_support.local_batch_file)

