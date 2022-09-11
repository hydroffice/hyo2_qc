import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.chart.project import ChartProject
from hyo2.qc.common import testing

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

prj = ChartProject(output_folder=testing.output_data_folder())
logger.debug(prj)

prj.open_output_folder()

print("change")
