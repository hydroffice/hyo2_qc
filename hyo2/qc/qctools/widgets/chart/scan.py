from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class ScanTab(QtWidgets.QMainWindow):
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
        # version ui
        self.toggle_specs_v3 = None

        # - feature scan v3
        self.featureScanV3 = QtWidgets.QGroupBox("Feature scan v3")
        self.featureScanV3.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.featureScanV3)
        fsv3_hbox = QtWidgets.QHBoxLayout()
        self.featureScanV3.setLayout(fsv3_hbox)
        # -- parameters
        self.setParametersFSv3 = QtWidgets.QGroupBox("Parameters")
        self.setParametersFSv3.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fsv3_hbox.addWidget(self.setParametersFSv3)
        self._ui_parameters_fsv3()
        # -- execution
        self.executeFSv3 = QtWidgets.QGroupBox("Execution")
        self.executeFSv3.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fsv3_hbox.addWidget(self.executeFSv3)
        self._ui_execute_fsv3()

        self.vbox.addStretch()

    # ----------- FEATURE SCAN V3 ------------- #

    def _ui_parameters_fsv3(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersFSv3.setLayout(hbox)
        hbox.addStretch()

        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()

        label_up_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_up_hbox)
        # stretch
        label_up_hbox.addStretch()
        # specs
        text_2016 = QtWidgets.QLabel("2016")
        text_2016.setAlignment(QtCore.Qt.AlignCenter)
        text_2016.setFixedWidth(25)
        label_up_hbox.addWidget(text_2016)
        # stretch
        label_up_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # specs
        self.toggle_specs_v3 = QtWidgets.QDial()
        self.toggle_specs_v3.setNotchesVisible(True)
        self.toggle_specs_v3.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_specs_v3.setRange(1, 3)
        self.toggle_specs_v3.setValue(2)
        self.toggle_specs_v3.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_specs_v3.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_specs_v3)
        # self.toggle_specs_v2.valueChanged.connect(self.click_set_profile)
        # stretch
        toggle_hbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # specs
        text_2014 = QtWidgets.QLabel("2014")
        text_2014.setAlignment(QtCore.Qt.AlignCenter)
        text_2014.setFixedWidth(25)
        label_hbox.addWidget(text_2014)
        text_2017 = QtWidgets.QLabel("2018 test")
        text_2017.setAlignment(QtCore.Qt.AlignRight)
        text_2017.setFixedWidth(60)
        text_2017.setStyleSheet("QLabel { color :  rgb(200, 0, 0, 200); }")
        label_hbox.addWidget(text_2017)
        # stretch
        label_hbox.addStretch()

        vbox.addStretch()

        hbox.addStretch()

    def _ui_execute_fsv3(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeFSv3.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Feature scan v3")
        button.setToolTip('Scan features in the loaded file checking their validity')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_feature_scan_v3)

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

    def click_feature_scan_v3(self):
        """trigger the feature scan v3"""
        self._click_feature_scan(3)

    # ------------- COMMON PART --------------- #

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_chart_scan_features.html")

    def _click_feature_scan(self, version):
        """abstract the feature scan calling mechanism"""

        # library takes care of progress bar

        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="chart_feature_scan_%d" % version))

        try:

            specs_version = None

            if version == 3:

                specs_version = self.toggle_specs_v3.value()
                if specs_version == 1:  # trick: there is not version 2015
                    specs_version = "2014"
                elif specs_version == 2:
                    specs_version = "2016"
                elif specs_version == 3:
                    specs_version = "2018"
                else:
                    raise RuntimeError("unknown specs version: %s" % specs_version)

            else:
                RuntimeError("unknown Feature Scan version: %s" % version)

            self.prj.feature_scan(version=version, specs_version=specs_version)

            # noinspection PyCallByClass
            QtWidgets.QMessageBox.information(self, "Feature scan v%d[%s]" % (version, specs_version),
                                              self.prj.scan_msg, QtWidgets.QMessageBox.Ok)

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While running chart's feature scan v%d, %s" % (version, e),
                                           QtWidgets.QMessageBox.Ok)
            return
