import logging
import os
from PySide2 import QtWidgets, QtCore
from matplotlib import pyplot as plt
import numpy as np

from hyo2.grids._grids import FLOAT as GRIDS_FLOAT, DOUBLE as GRIDS_DOUBLE
from hyo2.grids.grids_manager import GridsManager
from hyo2.grids.common import default_logging

default_logging.load()
logger = logging.getLogger()

# set settings

ask_for_input_file = True

# create a Qt application (required to get the dialog to select folders)

app = QtWidgets.QApplication([])
app.setApplicationName('plot_depths')
app.setOrganizationName("HydrOffice")
app.setOrganizationDomain("hydroffice.org")

# manage the input file by asking to user OR using the hand-written path

if ask_for_input_file:
    # noinspection PyArgumentList
    path, _ = QtWidgets.QFileDialog.getOpenFileName(parent=None, caption="Select input grid file",
                                                    dir=QtCore.QSettings().value("plot_depths_folder", ""))

    if path == str():
        logger.error("input file not selected")
        exit(-1)

    QtCore.QSettings().setValue("plot_depths_folder", os.path.dirname(path))

else:
    path = r"C:\Users\gmasetti\Google Drive\QC Tools\data\survey\Find Fliers\VR_Test\H13015_MB_VR_MLLW_Final_Extracted.csar"

    if not os.path.exists(path):
        logger.error("input file does not exist: %s" % path)
        exit(-1)

    if not os.path.isfile(path):
        logger.error("input file is actually not a file: %s" % path)
        exit(-1)

logger.debug("input file: %s" % path)

DEFAULT_CHUNK_SIZE = 4294967296  # 4GB

grids = GridsManager()

grids.add_path(path)

for grid_path in grids.grid_list:
    logger.debug(grid_path)
    grids.set_current(grid_path)
    grids.open_to_read_current(DEFAULT_CHUNK_SIZE)
    layer_names = grids.layer_names()

    logger.debug("bbox: %s" % grids.cur_grids.bbox())
    logger.debug("is VR: %s" % grids.is_vr())
    logger.debug("is CSAR: %s" % grids.is_csar())

    logger.debug("layers: %d" % len(layer_names))
    for layer_name in layer_names:
        logger.debug(f" - %s" % layer_name)

    # this approach abstracts the layer names (VR vs SR, BAG vs CSAR)
    layers_to_read = list()
    layers_to_read.append(grids.depth_layer_name())

    while grids.read_next_tile(layers_to_read):

        logger.debug("nr. of loaded tiles: %d" % len(grids.tiles))
        tile = grids.tiles[0]
        logger.debug("Tile info: %s" % tile.str())

        # now we just read the depth layer
        depth_type = tile.type(grids.depth_layer_name())
        depth_idx = tile.band_index(grids.depth_layer_name())
        if depth_type == GRIDS_DOUBLE:
            depth_nodata = tile.doubles_nodata[depth_idx]
            bathy_values = tile.doubles[depth_idx]
        else:  # if depth_type == GRIDS_FLOAT:
            depth_nodata = tile.floats_nodata[depth_idx]
            bathy_values = tile.floats[depth_idx]
        bathy_values[bathy_values == depth_nodata] = np.nan
        plt.imshow(bathy_values)
        plt.show()

        grids.clear_tiles()
