from PySide2 import QtCore, QtGui, QtWidgets

import os
import traceback
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper
from hyo2.qc.survey.scan.base_scan import survey_areas

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
        self.toggle_profile_v7 = None
        self.toggle_specs_v7 = None

        # - feature scan v7
        self.featureScanV7 = QtWidgets.QGroupBox("Feature scan v7")
        self.featureScanV7.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.featureScanV7)
        fsv6_hbox = QtWidgets.QHBoxLayout()
        self.featureScanV7.setLayout(fsv6_hbox)
        # -- parameters
        self.setParametersFSv7 = QtWidgets.QGroupBox("Parameters")
        self.setParametersFSv7.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fsv6_hbox.addWidget(self.setParametersFSv7)
        self._ui_parameters_fsv7()
        # -- execution
        self.executeFSv7 = QtWidgets.QGroupBox("Execution")
        self.executeFSv7.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fsv6_hbox.addWidget(self.executeFSv7)
        self._ui_execute_fsv7()

        # version ui
        self.toggle_profile_v8 = None
        self.toggle_specs_v8 = None
        self.text_atlantic_v8 = None
        self.text_pacific_v8 = None
        self.text_lakes_v8 = None
        self.toggle_area_v8 = None
        self.use_mhw_v8 = None
        self.mhw_text_v8 = None
        self.mhw_value_v8 = None
        self.check_sorind_v8 = None
        self.sorind_text_v8 = None
        self.sorind_value_v8 = None
        self.check_sordat_v8 = None
        self.sordat_text_v8 = None
        self.sordat_value_v8 = None

        # - feature scan v8
        self.featureScanV8 = QtWidgets.QGroupBox("Feature scan v8")
        self.featureScanV8.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.featureScanV8)
        fsv8_hbox = QtWidgets.QHBoxLayout()
        self.featureScanV8.setLayout(fsv8_hbox)
        # -- parameters
        self.setParametersFSv8 = QtWidgets.QGroupBox("Parameters")
        self.setParametersFSv8.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fsv8_hbox.addWidget(self.setParametersFSv8)
        self._ui_parameters_fsv8()
        # -- execution
        self.executeFSv8 = QtWidgets.QGroupBox("Execution")
        self.executeFSv8.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fsv8_hbox.addWidget(self.executeFSv8)
        self._ui_execute_fsv8()

        self.vbox.addStretch()

        self.featureScanV7.hide()

    def keyPressEvent(self, event):
        key = event.key()
        if event.modifiers() == QtCore.Qt.ControlModifier:

            if key == QtCore.Qt.Key_7:

                if self.featureScanV7.isHidden():
                    self.featureScanV7.show()
                else:
                    self.featureScanV7.hide()

                # return True
        return super(ScanTab, self).keyPressEvent(event)

    # ----------- FEATURE SCAN V7 ------------- #

    def _ui_parameters_fsv7(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersFSv7.setLayout(hbox)
        hbox.addStretch()

        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()

        label_up_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_up_hbox)
        # stretch
        label_up_hbox.addStretch()
        # profile
        text_field_empty = QtWidgets.QLabel("")
        text_field_empty.setAlignment(QtCore.Qt.AlignCenter)
        text_field_empty.setFixedWidth(30)
        label_up_hbox.addWidget(text_field_empty)
        text_office_empty = QtWidgets.QLabel("")
        text_office_empty.setAlignment(QtCore.Qt.AlignCenter)
        text_office_empty.setFixedWidth(35)
        label_up_hbox.addWidget(text_office_empty)
        # space
        label_up_hbox.addSpacing(15)
        # specs
        text_2016 = QtWidgets.QLabel("2016")
        text_2016.setAlignment(QtCore.Qt.AlignCenter)
        text_2016.setFixedWidth(25)
        label_up_hbox.addWidget(text_2016)
        # space
        label_up_hbox.addSpacing(15)
        # specs
        text_2017 = QtWidgets.QLabel("2017")
        text_2017.setAlignment(QtCore.Qt.AlignCenter)
        text_2017.setFixedWidth(25)
        label_up_hbox.addWidget(text_2017)
        # stretch
        label_up_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # profile
        self.toggle_profile_v7 = QtWidgets.QDial()
        self.toggle_profile_v7.setNotchesVisible(True)
        self.toggle_profile_v7.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_profile_v7.setRange(0, 1)
        self.toggle_profile_v7.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_profile_v7.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_profile_v7)
        # noinspection PyUnresolvedReferences
        self.toggle_profile_v7.valueChanged.connect(self.click_set_profile)
        # space
        toggle_hbox.addSpacing(35)
        # specs
        self.toggle_specs_v7 = QtWidgets.QDial()
        self.toggle_specs_v7.setNotchesVisible(True)
        self.toggle_specs_v7.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_specs_v7.setRange(2015, 2018)
        self.toggle_specs_v7.setValue(2017)
        self.toggle_specs_v7.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_specs_v7.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_specs_v7)
        # self.toggle_specs_v5.valueChanged.connect(self.click_set_profile)
        # stretch
        toggle_hbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # profile
        text_field = QtWidgets.QLabel("Office")
        text_field.setAlignment(QtCore.Qt.AlignRight)
        text_field.setFixedWidth(45)
        label_hbox.addWidget(text_field)
        text_office = QtWidgets.QLabel("Field")
        text_office.setAlignment(QtCore.Qt.AlignRight)
        text_office.setFixedWidth(35)
        label_hbox.addWidget(text_office)
        # space
        label_hbox.addSpacing(20)
        # specs
        text_2015 = QtWidgets.QLabel("2015")
        text_2015.setAlignment(QtCore.Qt.AlignCenter)
        text_2015.setFixedWidth(25)
        label_hbox.addWidget(text_2015)
        text_2017 = QtWidgets.QLabel("2018 test")
        text_2017.setAlignment(QtCore.Qt.AlignRight)
        text_2017.setFixedWidth(60)
        text_2017.setStyleSheet("QLabel { color :  rgb(200, 0, 0, 200); }")
        label_hbox.addWidget(text_2017)
        # stretch
        label_hbox.addStretch()

        vbox.addStretch()

        hbox.addStretch()

    def _ui_execute_fsv7(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeFSv7.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Feature scan v7")
        button.setToolTip('Scan features in the loaded file checking their validity')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_feature_scan_v7)

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

    def click_feature_scan_v7(self):
        """trigger the feature scan v7"""
        self._click_feature_scan(7)

    # ----------- FEATURE SCAN V8 ------------- #

    def _ui_parameters_fsv8(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersFSv8.setLayout(hbox)
        hbox.addStretch()

        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()

        # FIRST ROW OF KNOBS

        label_up_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_up_hbox)
        # stretch
        label_up_hbox.addStretch()
        # profile
        text_field_empty = QtWidgets.QLabel("")
        text_field_empty.setAlignment(QtCore.Qt.AlignCenter)
        text_field_empty.setFixedWidth(30)
        label_up_hbox.addWidget(text_field_empty)
        text_office_empty = QtWidgets.QLabel("")
        text_office_empty.setAlignment(QtCore.Qt.AlignCenter)
        text_office_empty.setFixedWidth(35)
        label_up_hbox.addWidget(text_office_empty)
        # space
        label_up_hbox.addSpacing(15)
        # specs
        text_2017 = QtWidgets.QLabel("2017")
        text_2017.setAlignment(QtCore.Qt.AlignCenter)
        text_2017.setFixedWidth(25)
        label_up_hbox.addWidget(text_2017)
        # space
        label_up_hbox.addSpacing(15)
        # specs
        text_2018 = QtWidgets.QLabel("2018")
        text_2018.setAlignment(QtCore.Qt.AlignCenter)
        text_2018.setFixedWidth(25)
        label_up_hbox.addWidget(text_2018)

        # stretch
        label_up_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # profile
        self.toggle_profile_v8 = QtWidgets.QDial()
        self.toggle_profile_v8.setNotchesVisible(True)
        self.toggle_profile_v8.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_profile_v8.setRange(0, 1)
        self.toggle_profile_v8.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_profile_v8.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_profile_v8)
        # noinspection PyUnresolvedReferences
        self.toggle_profile_v8.valueChanged.connect(self.click_set_profile)
        # space
        toggle_hbox.addSpacing(35)
        # specs
        self.toggle_specs_v8 = QtWidgets.QDial()
        self.toggle_specs_v8.setNotchesVisible(True)
        self.toggle_specs_v8.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_specs_v8.setRange(2016, 2019)
        self.toggle_specs_v8.setValue(2018)
        self.toggle_specs_v8.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_specs_v8.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_specs_v8)
        # noinspection PyUnresolvedReferences
        self.toggle_specs_v8.valueChanged.connect(self.click_set_specs)
        # stretch
        toggle_hbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # profile
        text_field = QtWidgets.QLabel("Office")
        text_field.setAlignment(QtCore.Qt.AlignRight)
        text_field.setFixedWidth(45)
        label_hbox.addWidget(text_field)
        text_office = QtWidgets.QLabel("Field")
        text_office.setAlignment(QtCore.Qt.AlignRight)
        text_office.setFixedWidth(35)
        label_hbox.addWidget(text_office)
        # space
        label_hbox.addSpacing(20)
        # specs
        text_2016 = QtWidgets.QLabel("2016")
        text_2016.setAlignment(QtCore.Qt.AlignCenter)
        text_2016.setFixedWidth(25)
        label_hbox.addWidget(text_2016)
        text_2019 = QtWidgets.QLabel("2019 test")
        text_2019.setAlignment(QtCore.Qt.AlignRight)
        text_2019.setFixedWidth(70)
        text_2019.setStyleSheet("QLabel { color :  rgb(200, 0, 0, 200); }")
        label_hbox.addWidget(text_2019)
        # stretch
        label_hbox.addStretch()

        vbox.addSpacing(12)

        # SECOND ROW OF KNOBS

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # specs
        self.text_lakes_v8 = QtWidgets.QLabel("Great Lakes")
        self.text_lakes_v8.setAlignment(QtCore.Qt.AlignCenter)
        self.text_lakes_v8.setFixedWidth(120)
        label_hbox.addWidget(self.text_lakes_v8)
        # stretch
        label_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # specs
        self.toggle_area_v8 = QtWidgets.QDial()
        self.toggle_area_v8.setNotchesVisible(True)
        self.toggle_area_v8.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_area_v8.setRange(0, 2)
        self.toggle_area_v8.setValue(0)
        self.toggle_area_v8.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_area_v8.setInvertedAppearance(False)
        # noinspection PyUnresolvedReferences
        # self.toggle_area.valueChanged.connect(self.on_settings_changed)
        toggle_hbox.addWidget(self.toggle_area_v8)
        # stretch
        toggle_hbox.addStretch()

        label2_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label2_hbox)
        # stretch
        label2_hbox.addStretch()
        # specs
        self.text_pacific_v8 = QtWidgets.QLabel("Pacific Coast")
        self.text_pacific_v8.setAlignment(QtCore.Qt.AlignCenter)
        self.text_pacific_v8.setFixedWidth(80)
        label2_hbox.addWidget(self.text_pacific_v8)
        self.text_atlantic_v8 = QtWidgets.QLabel("Atlantic Coast")
        self.text_atlantic_v8.setAlignment(QtCore.Qt.AlignCenter)
        self.text_atlantic_v8.setFixedWidth(80)
        label2_hbox.addWidget(self.text_atlantic_v8)
        # stretch
        label2_hbox.addStretch()

        vbox.addSpacing(12)

        # THIRD ROW

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # spacing
        label_hbox.addSpacing(100)
        # stretch
        label_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        self.use_mhw_v8 = QtWidgets.QCheckBox("")
        self.use_mhw_v8.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.use_mhw_v8.stateChanged.connect(self.change_use_mhw)
        toggle_hbox.addWidget(self.use_mhw_v8)
        self.mhw_text_v8 = QtWidgets.QLabel("MHW [m]: ")
        self.mhw_text_v8.setFixedWidth(100)
        self.mhw_text_v8.setDisabled(True)
        toggle_hbox.addWidget(self.mhw_text_v8)
        self.mhw_value_v8 = QtWidgets.QLineEdit()
        self.mhw_value_v8.setFixedWidth(150)
        self.mhw_value_v8.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value_v8))
        self.mhw_value_v8.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.mhw_value_v8.setText("5.0")
        self.mhw_value_v8.setDisabled(True)
        toggle_hbox.addWidget(self.mhw_value_v8)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        self.check_sorind_v8 = QtWidgets.QCheckBox("")
        self.check_sorind_v8.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.check_sorind_v8.stateChanged.connect(self.change_check_sorind)
        toggle_hbox.addWidget(self.check_sorind_v8)
        self.sorind_text_v8 = QtWidgets.QLabel("SORIND: ")
        self.sorind_text_v8.setDisabled(True)
        self.sorind_text_v8.setFixedWidth(100)
        toggle_hbox.addWidget(self.sorind_text_v8)
        self.sorind_value_v8 = QtWidgets.QLineEdit()
        self.sorind_value_v8.setFixedWidth(150)
        # self.sorind_value_v8.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value_v8))
        self.sorind_value_v8.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.sorind_value_v8.setText("")
        self.sorind_value_v8.setDisabled(True)
        toggle_hbox.addWidget(self.sorind_value_v8)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        self.check_sordat_v8 = QtWidgets.QCheckBox("")
        self.check_sordat_v8.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.check_sordat_v8.stateChanged.connect(self.change_check_sordat)
        toggle_hbox.addWidget(self.check_sordat_v8)
        self.sordat_text_v8 = QtWidgets.QLabel("SORDAT: ")
        self.sordat_text_v8.setDisabled(True)
        self.sordat_text_v8.setFixedWidth(100)
        toggle_hbox.addWidget(self.sordat_text_v8)
        self.sordat_value_v8 = QtWidgets.QLineEdit()
        self.sordat_value_v8.setFixedWidth(150)
        # self.sordat_value_v8.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value_v8))
        self.sordat_value_v8.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.sordat_value_v8.setText("")
        self.sordat_value_v8.setDisabled(True)
        toggle_hbox.addWidget(self.sordat_value_v8)
        # stretch
        toggle_hbox.addStretch()

        label2_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label2_hbox)
        # stretch
        label2_hbox.addStretch()
        # spacing
        label2_hbox.addSpacing(100)
        # stretch
        label2_hbox.addStretch()

        vbox.addStretch()

        hbox.addStretch()

    def _ui_execute_fsv8(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeFSv8.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Feature scan v8")
        button.setToolTip('Scan features in the loaded file checking their validity')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_feature_scan_v8)

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

    def click_feature_scan_v8(self):
        """trigger the feature scan v8"""
        self._click_feature_scan(8)

    # ------------- COMMON PART --------------- #

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_scan_features.html")

    def click_set_profile(self, value):
        """ Change the profile in use """
        self.prj.active_profile = value
        self.toggle_profile_v7.setValue(value)
        logger.info('activated profile #%s' % value)

    def change_use_mhw(self):
        logger.info('use mhw: %s' % self.use_mhw_v8.isChecked())
        enable = self.use_mhw_v8.isChecked()
        self.mhw_text_v8.setEnabled(enable)
        self.mhw_value_v8.setEnabled(enable)

    def change_check_sorind(self):
        logger.info('check SORIND: %s' % self.check_sorind_v8.isChecked())
        enable = self.check_sorind_v8.isChecked()
        self.sorind_text_v8.setEnabled(enable)
        self.sorind_value_v8.setEnabled(enable)

    def change_check_sordat(self):
        logger.info('check SORDAT: %s' % self.check_sordat_v8.isChecked())
        enable = self.check_sordat_v8.isChecked()
        self.sordat_text_v8.setEnabled(enable)
        self.sordat_value_v8.setEnabled(enable)

    def click_set_specs(self, value):
        """ Change the specs in use """
        logger.info('selected specs %d' % value)

        enable = value in [2018, 2019]
        self.text_lakes_v8.setEnabled(enable)
        self.text_atlantic_v8.setEnabled(enable)
        self.text_pacific_v8.setEnabled(enable)
        self.toggle_area_v8.setEnabled(enable)

        self.use_mhw_v8.setEnabled(enable)
        enable2 = enable and self.use_mhw_v8.isChecked()
        self.mhw_text_v8.setEnabled(enable2)
        self.mhw_value_v8.setEnabled(enable2)

        self.check_sorind_v8.setEnabled(enable)
        enable2 = enable and self.check_sorind_v8.isChecked()
        self.sorind_text_v8.setEnabled(enable2)
        self.sorind_value_v8.setEnabled(enable2)

        self.check_sordat_v8.setEnabled(enable)
        enable2 = enable and self.check_sordat_v8.isChecked()
        self.sordat_text_v8.setEnabled(enable2)
        self.sordat_value_v8.setEnabled(enable2)

    def _click_feature_scan(self, version):
        """abstract the feature scan calling mechanism"""

        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="survey_feature_scan_%d" % version))

        # library takes care of progress bar

        try:

            specs_version = None
            survey_area = 0
            use_mhw = False
            mhw_value = 0.0
            sorind = None
            sordat = None

            if version == 7:

                specs_version = self.toggle_specs_v7.value()
                if specs_version == 2015:  # trick: there is not version 2015
                    specs_version = "2015"
                elif specs_version == 2016:
                    specs_version = "2016"
                elif specs_version == 2017:
                    specs_version = "2017"
                elif specs_version == 2018:
                    specs_version = "2018"
                else:
                    raise RuntimeError("unknown specs version: %s" % specs_version)

            elif version == 8:

                specs_version = self.toggle_specs_v8.value()
                if specs_version == 2016:
                    specs_version = "2016"
                elif specs_version == 2017:
                    specs_version = "2017"
                elif specs_version == 2018:
                    specs_version = "2018"
                elif specs_version == 2019:
                    specs_version = "2019"
                else:
                    raise RuntimeError("unknown specs version: %s" % specs_version)

                toggle_survey_area = self.toggle_area_v8.value()
                if toggle_survey_area == 0:
                    survey_area = survey_areas["Pacific Coast"]
                elif toggle_survey_area == 1:
                    survey_area = survey_areas["Great Lakes"]
                elif toggle_survey_area == 2:
                    survey_area = survey_areas["Atlantic Coast"]
                else:
                    raise RuntimeError("unknown survey area: %s" % survey_area)

                use_mhw = self.use_mhw_v8.isChecked()
                mhw_value = float(self.mhw_value_v8.text())

                if self.check_sorind_v8.isChecked():
                    sorind = self.sorind_value_v8.text()
                    is_valid = self.prj.check_sorind(value=sorind)
                    if not is_valid:
                        msg = "An invalid SORIND was entered!\n\nCheck: %s" % sorind
                        # noinspection PyCallByClass
                        QtWidgets.QMessageBox.critical(self, "Feature scan v%d[%s]" % (version, specs_version),
                                                       msg, QtWidgets.QMessageBox.Ok)
                        return

                if self.check_sordat_v8.isChecked():
                    sordat = self.sordat_value_v8.text()
                    is_valid = self.prj.check_sordat(value=sordat)
                    if not is_valid:
                        msg = "An invalid SORDAT was entered!\n\nCheck: %s" % sordat
                        # noinspection PyCallByClass
                        QtWidgets.QMessageBox.critical(self, "Feature scan v%d[%s]" % (version, specs_version),
                                                       msg, QtWidgets.QMessageBox.Ok)
                        return

            else:
                RuntimeError("unknown Feature Scan version: %s" % version)

            self.prj.feature_scan(version=version, specs_version=specs_version,
                                  survey_area=survey_area, use_mhw=use_mhw, mhw_value=mhw_value,
                                  sorind=sorind, sordat=sordat)

            # noinspection PyCallByClass
            QtWidgets.QMessageBox.information(self, "Feature scan v%d[%s]" % (version, specs_version),
                                              self.prj.scan_msg, QtWidgets.QMessageBox.Ok)

        except Exception as e:
            traceback.print_exc()
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While running survey's feature scan v%d, %s" % (version, e),
                                           QtWidgets.QMessageBox.Ok)
            return
