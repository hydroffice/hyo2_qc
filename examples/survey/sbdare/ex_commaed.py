from hyo2.qc.common import default_logging
import os
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.survey.sbdare.sbdare_export_v4 import SbdareExportV4

test_0 = """
hello, hello
hello


"""
out = SbdareExportV4._commaed_str(test_0)
logger.debug("%s -> %s***" % (test_0, out))

test_1 = "test\n"
out = SbdareExportV4._commaed_str(test_1)
logger.debug("%s -> %s***" % (test_1, out))
