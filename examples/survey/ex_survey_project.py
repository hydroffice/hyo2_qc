from hyo2.qc.common import default_logging
import logging

from hyo2.qc.survey.project import SurveyProject

default_logging.load()
logger = logging.getLogger()

prj = SurveyProject()
logger.debug(prj)
prj.open_output_folder()
