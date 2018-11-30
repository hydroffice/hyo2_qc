from hyo2.qc.common import default_logging
import os
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.survey.sbdare.sbdare_export_v4 import SbdareExportV4

test_0 = ",,"
test_0_list = test_0.split(",")
out = SbdareExportV4._zeroed_list(test_0_list)
logger.debug("%s -> %s -> %s" % (test_0, test_0_list, out))

test_0 = ""
test_0_list = test_0.split(",")
out = SbdareExportV4._zeroed_list(test_0_list)
logger.debug("%s -> %s -> %s" % (test_0, test_0_list, out))
