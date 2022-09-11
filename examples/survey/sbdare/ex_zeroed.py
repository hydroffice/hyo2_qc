import os
import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.survey.sbdare.sbdare_export_v4 import SbdareExportV4

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

test_0 = ",,"
test_0_list = test_0.split(",")
out = SbdareExportV4._zeroed_list(test_0_list)
logger.debug("%s -> %s -> %s" % (test_0, test_0_list, out))

test_0 = ""
test_0_list = test_0.split(",")
out = SbdareExportV4._zeroed_list(test_0_list)
logger.debug("%s -> %s -> %s" % (test_0, test_0_list, out))
