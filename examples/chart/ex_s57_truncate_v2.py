import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.chart.project import ChartProject
from hyo2.qc.common import testing

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

prj = ChartProject(output_folder=testing.output_data_folder())

input_s57_file = testing.input_test_files('.000')[0]
logger.debug('input: %s' % input_s57_file)
prj.add_to_s57_list(input_s57_file)

prj.s57_truncate(version=2, decimal_places=0)

logger.debug(prj)
