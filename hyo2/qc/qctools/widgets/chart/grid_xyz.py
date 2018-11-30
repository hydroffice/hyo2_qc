from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging
logger = logging.getLogger(__name__)

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common.helper import Helper


class GridXyzTab(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win, prj):
        QtWidgets.QMainWindow.__init__(self)
        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        # - Grid XYZ v1
        self.bagXyzV1 = QtWidgets.QGroupBox("Grid XYZ v1")
        self.bagXyzV1.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.bagXyzV1)
        xyv1_hbox = QtWidgets.QHBoxLayout()
        self.bagXyzV1.setLayout(xyv1_hbox)
        # -- parameters
        self.setParametersXYv1 = QtWidgets.QGroupBox("Parameters")
        self.setParametersXYv1.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        xyv1_hbox.addWidget(self.setParametersXYv1)
        self._ui_parameters_xyv1()
        # -- execution
        self.executeXYv1 = QtWidgets.QGroupBox("Execution")
        self.executeXYv1.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        xyv1_hbox.addWidget(self.executeXYv1)
        self._ui_execute_xyv1()

        self.vbox.addStretch()

    def _ui_parameters_xyv1(self):
        vbox = QtWidgets.QVBoxLayout()
        self.setParametersXYv1.setLayout(vbox)

        vbox.addStretch()

        # set decimal places
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.set_geo_label_xyv1 = QtWidgets.QLabel("Force conversion to geographic WGS84:")
        self.set_geo_label_xyv1.setDisabled(False)
        hbox.addWidget(self.set_geo_label_xyv1)
        self.set_geo_label_xyv1.setFixedHeight(GuiSettings.single_line_height())
        self.set_geo_xyv1 = QtWidgets.QCheckBox("")
        hbox.addWidget(self.set_geo_xyv1)
        self.set_geo_xyv1.setFixedHeight(GuiSettings.single_line_height())
        self.set_geo_xyv1.setDisabled(False)
        self.set_geo_xyv1.setChecked(True)

        hbox.addStretch()

        # set elevation/depth
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.set_z_label_xyv1 = QtWidgets.QLabel("Z convention:")
        self.set_z_label_xyv1.setDisabled(False)
        hbox.addWidget(self.set_z_label_xyv1)
        self.set_z_label_xyv1.setFixedHeight(GuiSettings.single_line_height())
        self.set_z_xyv1 = QtWidgets.QGroupBox("")
        self.set_z_xyv1.setFlat(True)
        self.set_z_xyv1.setHidden(True)
        hbox.addWidget(self.set_z_xyv1)
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

        self.set_dec_places_label_xyv1 = QtWidgets.QLabel("Truncate after decimal place: ")
        hbox.addWidget(self.set_dec_places_label_xyv1)
        self.set_dec_places_label_xyv1.setFixedHeight(GuiSettings.single_line_height())
        self.set_flag_truncation_xyv1 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.set_flag_truncation_xyv1)
        self.set_flag_truncation_xyv1.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.set_flag_truncation_xyv1.clicked.connect(self._flag_truncation)
        self.set_dec_places_xyv1 = QtWidgets.QLineEdit("")
        hbox.addWidget(self.set_dec_places_xyv1)
        self.set_dec_places_xyv1.setFixedHeight(GuiSettings.single_line_height())
        self.set_dec_places_xyv1.setValidator(QtGui.QIntValidator(0, 99, self.set_dec_places_xyv1))
        self.set_dec_places_xyv1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_dec_places_xyv1.setReadOnly(False)
        self.set_dec_places_xyv1.setFont(GuiSettings.console_font())
        self.set_dec_places_xyv1.setFixedWidth(30)
        self.set_dec_places_xyv1.setDisabled(True)
        self.set_dec_places_xyv1.setText("1")

        hbox.addStretch()

        vbox.addStretch()

    def _flag_truncation(self):
        logger.debug("truncation: %s" % self.set_flag_truncation_xyv1.isChecked())

        if self.set_flag_truncation_xyv1.isChecked():
            self.set_dec_places_xyv1.setEnabled(True)
        else:
            self.set_dec_places_xyv1.setDisabled(True)

    def _ui_execute_xyv1(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeXYv1.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() + 6)
        button.setText("Grid XYZ v1")
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

        version = 1
        self.parent_win.change_info_url(Helper.web_url(suffix="chart_grid_xyz_%d" % version))

        self.prj.grid_xyz(version=version,
                          geographic=self.set_geo_xyv1.isChecked(),
                          elevation=self.set_z_elevation.isChecked(),
                          truncate=self.set_flag_truncation_xyv1.isChecked(),
                          decimal_places=int(self.set_dec_places_xyv1.text()))
