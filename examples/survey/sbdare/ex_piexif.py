from hyo2.qc.common import default_logging
import os
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.survey.sbdare.sbdare_export_v4 import SbdareExportV4

lat = 43.13555
lon = -70.9395

img_folder = "C:\\Users\\gmasetti\\Google Drive\\QC Tools\\support\\CMECS\\BottomSample_QCTools_Input-Output\\Output\\H12895_BottomSamples_CMECS\\Images\\"
#img_folder = "C:\\Users\\gmasetti\\Google Drive\\QC Tools\\support\\CMECS\\BottomSample_QCTools_Input-Output\\Input\\Multimedia\\"

img_list = os.listdir(img_folder)

for img_file in img_list:

    if os.path.splitext(img_file)[-1].lower() != ".jpg":
        continue

    img_path = os.path.join(img_folder, img_file)

    if not os.path.exists(img_path):
        logger.error("unable to locate image file: %s" % img_path)
        exit(1)

    SbdareExportV4.geotag_jpeg(img_path, lat, lon)
