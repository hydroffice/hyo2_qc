from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.survey.sbdare.sbdare_export_v4 import SbdareExportV4

test_0 = """
hello;hello
hello


"""
out = SbdareExportV4._semi_commaed_str(test_0)
logger.debug("%s -> %s***" % (test_0, out))
