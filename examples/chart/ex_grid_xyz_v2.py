import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.chart.project import ChartProject
from hyo2.qc.common.grid_callback.cli_grid_callback import CliGridCallback
from hyo2.qc.common import testing

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

prj = ChartProject(output_folder=testing.output_data_folder())
prj.set_callback(CliGridCallback())

input_bag_file = testing.input_test_files('.bag')[1]
logger.debug('input: %s' % input_bag_file)
prj.add_to_grid_list(input_bag_file)

geographic = False
elevation = False
truncate = False
decimal_places = 0
epsg_code = 4326
order = 'xyz'

prj.grid_xyz(version=2, geographic=geographic, elevation=elevation,
             truncate=truncate, decimal_places=decimal_places,
             epsg_code=epsg_code, order=order)

logger.debug(prj)
