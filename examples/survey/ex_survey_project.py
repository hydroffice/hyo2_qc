from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.survey.project import SurveyProject


prj = SurveyProject()
logger.debug(prj)
prj.open_output_folder()
