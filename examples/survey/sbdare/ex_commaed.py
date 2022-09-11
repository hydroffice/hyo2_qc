import logging
from hyo2.abc.lib.logging import set_logging

from hyo2.qc.survey.sbdare.sbdare_export_v4 import SbdareExportV4

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

test_0 = """
hello, hello
hello


"""
out = SbdareExportV4._commaed_str(test_0)
logger.debug("%s -> %s***" % (test_0, out))

test_1 = "test\n"
out = SbdareExportV4._commaed_str(test_1)
logger.debug("%s -> %s***" % (test_1, out))
