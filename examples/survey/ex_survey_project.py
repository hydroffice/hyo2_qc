import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.survey.project import SurveyProject

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

prj = SurveyProject()
logger.debug(prj)
prj.open_output_folder()
