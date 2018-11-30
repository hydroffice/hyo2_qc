from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.chart.project import ChartProject
from hyo2.qc.common import testing


prj = ChartProject(output_folder=testing.output_data_folder())
logger.debug(prj)

prj.open_output_folder()

print("change")
