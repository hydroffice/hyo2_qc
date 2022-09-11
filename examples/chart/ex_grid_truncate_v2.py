import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.chart.project import ChartProject
from hyo2.qc.common import testing

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

prj = ChartProject(output_folder=testing.output_data_folder())

input_bag_file = testing.input_test_files('.bag')[0]
logger.debug('input: %s' % input_bag_file)
prj.add_to_grid_list(input_bag_file)

prj.grid_truncate(version=2, decimal_places=0)

logger.debug(prj)
