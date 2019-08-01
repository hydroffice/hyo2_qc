from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class GridXyzTab(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win, prj):
        QtWidgets.QMainWindow.__init__(self)
        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media

        self.crs = dict()
        utm_n_start = 32600
        utm_s_start = 32700
        for idx in range(1, 61):
            self.crs["%d (WGS 84 / UTM zone %dN)" % (utm_n_start + idx, idx)] = utm_n_start + idx
        for idx in range(1, 61):
            self.crs["%d (WGS 84 / UTM zone %dS)" % (utm_s_start + idx, idx)] = utm_s_start + idx

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        # - Grid XYZ v2
        self.bagXyzV2 = QtWidgets.QGroupBox("Grid XYZ v2")
        self.bagXyzV2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.bagXyzV2)
        xyv2_hbox = QtWidgets.QHBoxLayout()
        self.bagXyzV2.setLayout(xyv2_hbox)
        # -- parameters
        self.setParametersXYv2 = QtWidgets.QGroupBox("Parameters")
        self.setParametersXYv2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        xyv2_hbox.addWidget(self.setParametersXYv2)
        self.set_crs_group_xyv2 = None
        self.set_keep_crs_xyv2 = None
        self.set_geo_crs_xyv2 = None
        self.set_epsg_crs_xyv2 = None
        self.set_epsg_xyv2 = None
        self.set_z_label_xyv2 = None
        self.set_z_xyv2 = None
        self.set_z_depth = None
        self.set_z_elevation = None
        self.set_dec_places_label_xyv2 = None
        self.set_flag_truncation_xyv2 = None
        self.set_dec_places_xyv2 = None
        self.set_output_order_xyv2 = None
        self._ui_parameters_xyv2()
        # -- execution
        self.executeXYv2 = QtWidgets.QGroupBox("Execution")
        self.executeXYv2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        xyv2_hbox.addWidget(self.executeXYv2)
        self._ui_execute_xyv2()

        self.vbox.addStretch()

    def _ui_parameters_xyv2(self):
        vbox = QtWidgets.QVBoxLayout()
        self.setParametersXYv2.setLayout(vbox)

        vbox.addStretch()

        # set crs
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.set_crs_group_xyv2 = QtWidgets.QGroupBox("Coordinate Reference System")
        self.set_crs_group_xyv2.setFlat(True)
        hbox.addWidget(self.set_crs_group_xyv2)

        gvbox = QtWidgets.QVBoxLayout()
        self.set_crs_group_xyv2.setLayout(gvbox)

        self.set_keep_crs_xyv2 = QtWidgets.QRadioButton("Keep original CRS")
        gvbox.addWidget(self.set_keep_crs_xyv2)
        self.set_keep_crs_xyv2.setChecked(True)

        self.set_geo_crs_xyv2 = QtWidgets.QRadioButton("Convert to Geographic WGS84")
        gvbox.addWidget(self.set_geo_crs_xyv2)

        self.set_epsg_crs_xyv2 = QtWidgets.QRadioButton("Convert to EPSG code:")
        gvbox.addWidget(self.set_epsg_crs_xyv2)

        ghbox = QtWidgets.QHBoxLayout()
        gvbox.addLayout(ghbox)
        ghbox.addStretch()
        self.set_epsg_xyv2 = QtWidgets.QComboBox()
        self.set_epsg_xyv2.addItems(list(self.crs.keys()))
        self.set_epsg_xyv2.setEditable(True)
        self.set_epsg_xyv2.setCurrentText("")
        ghbox.addWidget(self.set_epsg_xyv2)
        ghbox.addStretch()

        gvbox.addStretch()

        hbox.addStretch()

        # set elevation/depth
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.set_z_label_xyv2 = QtWidgets.QLabel("Z convention:")
        hbox.addWidget(self.set_z_label_xyv2)
        self.set_z_label_xyv2.setFixedHeight(GuiSettings.single_line_height())
        self.set_z_xyv2 = QtWidgets.QGroupBox("")
        self.set_z_xyv2.setFlat(True)
        self.set_z_xyv2.setHidden(True)
        hbox.addWidget(self.set_z_xyv2)
        self.set_z_depth = QtWidgets.QRadioButton("&Depth")
        hbox.addWidget(self.set_z_depth)
        self.set_z_elevation = QtWidgets.QRadioButton("&Elevation")
        hbox.addWidget(self.set_z_elevation)
        self.set_z_depth.setChecked(True)

        hbox.addStretch()

        # set decimal places
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.set_dec_places_label_xyv2 = QtWidgets.QLabel("Truncate after decimal place: ")
        hbox.addWidget(self.set_dec_places_label_xyv2)
        self.set_dec_places_label_xyv2.setFixedHeight(GuiSettings.single_line_height())
        self.set_flag_truncation_xyv2 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.set_flag_truncation_xyv2)
        self.set_flag_truncation_xyv2.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.set_flag_truncation_xyv2.clicked.connect(self._flag_truncation)
        self.set_dec_places_xyv2 = QtWidgets.QLineEdit("")
        hbox.addWidget(self.set_dec_places_xyv2)
        self.set_dec_places_xyv2.setFixedHeight(GuiSettings.single_line_height())
        self.set_dec_places_xyv2.setValidator(QtGui.QIntValidator(0, 99, self.set_dec_places_xyv2))
        self.set_dec_places_xyv2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_dec_places_xyv2.setReadOnly(False)
        self.set_dec_places_xyv2.setFont(GuiSettings.console_font())
        self.set_dec_places_xyv2.setFixedWidth(30)
        self.set_dec_places_xyv2.setDisabled(True)
        self.set_dec_places_xyv2.setText("1")

        hbox.addStretch()

        # set output order
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.set_output_order_label_xyv2 = QtWidgets.QLabel("Output order: ")
        hbox.addWidget(self.set_output_order_label_xyv2)
        self.set_output_order_xyv2 = QtWidgets.QComboBox()
        self.set_output_order_xyv2.addItems(['xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'])
        self.set_output_order_xyv2.setCurrentText('yxz')
        hbox.addWidget(self.set_output_order_xyv2)

        hbox.addStretch()

        vbox.addStretch()

    def _flag_truncation(self):
        logger.debug("truncation: %s" % self.set_flag_truncation_xyv2.isChecked())

        if self.set_flag_truncation_xyv2.isChecked():
            self.set_dec_places_xyv2.setEnabled(True)
        else:
            self.set_dec_places_xyv2.setDisabled(True)

    def _ui_execute_xyv2(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeXYv2.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() + 6)
        button.setText("Grid XYZ v2")
        button.setToolTip('Export depths as a point cloud')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_truncate)

        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.single_line_height())
        icon_info = QtCore.QFileInfo(os.path.join(self.media, 'small_info.png'))
        button.setIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        button.setToolTip('Open the manual page')
        button.setStyleSheet("QPushButton { background-color: rgba(255, 255, 255, 0); }\n"
                             "QPushButton:hover { background-color: rgba(230, 230, 230, 100); }\n")
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_open_manual)

        hbox.addStretch()

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_chart_grid_xyz.html")

    def click_truncate(self):
        # library takes care of progress bar

        version = 2
        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="chart_grid_xyz_%d" % version))

        if self.set_epsg_crs_xyv2.isChecked():
            epsg_txt = self.set_epsg_xyv2.currentText()
            if epsg_txt in self.crs.keys():
                epsg_code = self.crs[epsg_txt]
            else:
                try:
                    epsg_code = int(epsg_txt)
                except Exception as e:
                    # noinspection PyCallByClass,PyArgumentList
                    QtWidgets.QMessageBox.warning(self, "Invalid EPSG Code",
                                                  "While reading '%s', %s" % (epsg_txt, e),
                                                  QtWidgets.QMessageBox.Ok)
                    return
        else:
            epsg_code = None

        self.prj.grid_xyz(version=version,
                          geographic=self.set_geo_crs_xyv2.isChecked(),
                          elevation=self.set_z_elevation.isChecked(),
                          truncate=self.set_flag_truncation_xyv2.isChecked(),
                          decimal_places=int(self.set_dec_places_xyv2.text()),
                          epsg_code=epsg_code,
                          order=self.set_output_order_xyv2.currentText())
