import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common import testing
from PySide2 import QtWidgets
from hyo2.abc.app.qt_progress import QtProgress

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

app = QtWidgets.QApplication([])
wid = QtWidgets.QWidget()

prj = SurveyProject(output_folder=testing.output_data_folder(), progress=QtProgress(parent=wid))

# add a S57 file
s57_files = testing.input_test_files(".000")
# print("- S57 files: %d" % len(s57_files))
prj.add_to_s57_list(s57_files[0])
# prj.add_to_s57_list(s57_files[1])
# prj.add_to_s57_list(s57_files[2])
# prj.add_to_s57_list(s57_files[3])
# prj.add_to_s57_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\support\\CMECS\\BottomSample_QCTools_Input-Output\\Input\\H12895_FFF.000")
# prj.add_to_s57_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\support\\CMECS\\BottomSample_QCTools_Input-Output\\Input2\\H12850_Final_Feature_File_Office.000")
# prj.add_to_s57_list("C:\\Users\\gmasetti\\Google Drive\\QC Tools\\support\\CMECS\\BottomSample_QCTools_Input-Output\\Input3\\H12679_FFF.000")
print("%s" % (prj.s57_list,))
logger.debug(prj)

do_exif = True

for s57_file in prj.s57_list:

    prj.clear_survey_label()
    prj.read_feature_file(feature_path=s57_file)
    prj.sbdare_export_v4(exif=do_exif)
    saved_ascii = prj.save_sbdare()
    if saved_ascii:
        prj.open_sbdare_output_folder()

    warnings = prj.sbdare_warnings()
    logger.debug("warnings: %d" % len(warnings))
    for warning in warnings:
        logger.info("- %s" % warning)

# for s57_file in prj.s57_list:
#
#     prj.clear_survey_label()
#     prj.read_feature_file(feature_path=s57_file)
#     prj.sbdare_export_v3()
#     saved_ascii = prj.save_sbdare()
#     if saved_ascii:
#         prj.open_sbdare_output_folder()
