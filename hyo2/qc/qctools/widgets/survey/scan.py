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

        self.settings = QtCore.QSettings()
        self.settings.setValue("survey/scan_v9", self.settings.value("survey/scan_v9", 0))
        self.prj.active_profile = self.settings.value("survey/scan_v9", 0)

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        # version ui
        self.toggle_profile_v9 = None
        self.toggle_specs_v9 = None
        self.text_atlantic_v9 = None
        self.text_pacific_v9 = None
        self.text_lakes_v9 = None
        self.toggle_area_v9 = None
        self.ask_multimedia_folder_v9 = None
        self.amf_text_v9 = None
        self.use_htd_v9 = None
        self.htd_text_v9 = None
        self.use_mhw_v9 = None
        self.mhw_text_v9 = None
        self.mhw_value_v9 = None
        self.check_sorind_v9 = None
        self.sorind_text_v9 = None
        self.sorind_value_v9 = None
        self.check_sordat_v9 = None
        self.sordat_text_v9 = None
        self.sordat_value_v9 = None

        # - feature scan v9
        self.featureScanV9 = QtWidgets.QGroupBox("Feature scan v9")
        self.featureScanV9.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.featureScanV9)
        fsv9_hbox = QtWidgets.QHBoxLayout()
        self.featureScanV9.setLayout(fsv9_hbox)
        # -- parameters
        self.setParametersFSv9 = QtWidgets.QGroupBox("Parameters")
        self.setParametersFSv9.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fsv9_hbox.addWidget(self.setParametersFSv9)
        self._ui_parameters_fsv9()
        # -- execution
        self.executeFSv9 = QtWidgets.QGroupBox("Execution")
        self.executeFSv9.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fsv9_hbox.addWidget(self.executeFSv9)
        self._ui_execute_fsv9()

        self.vbox.addStretch()

    def keyPressEvent(self, event):
        key = event.key()
        if event.modifiers() == QtCore.Qt.ControlModifier:

            # if key == QtCore.Qt.Key_8:
            #
            #     if self.featureScanV8.isHidden():
            #         self.featureScanV8.show()
            #     else:
            #         self.featureScanV8.hide()
            pass

                # return True
        return super(ScanTab, self).keyPressEvent(event)

    # ----------- FEATURE SCAN V9 ------------- #

    def _ui_parameters_fsv9(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersFSv9.setLayout(hbox)
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
        text_2018 = QtWidgets.QLabel("2018")
        text_2018.setAlignment(QtCore.Qt.AlignCenter)
        text_2018.setFixedWidth(25)
        label_up_hbox.addWidget(text_2018)
        # space
        label_up_hbox.addSpacing(20)
        # specs
        text_2019 = QtWidgets.QLabel("2019")
        text_2019.setAlignment(QtCore.Qt.AlignCenter)
        text_2019.setFixedWidth(25)
        label_up_hbox.addWidget(text_2019)

        # stretch
        label_up_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # profile
        self.toggle_profile_v9 = QtWidgets.QDial()
        self.toggle_profile_v9.setNotchesVisible(True)
        self.toggle_profile_v9.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_profile_v9.setRange(0, 1)
        self.toggle_profile_v9.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_profile_v9.setInvertedAppearance(False)
        self.toggle_profile_v9.setSliderPosition(self.settings.value("survey/scan_v9", 0))
        toggle_hbox.addWidget(self.toggle_profile_v9)
        # noinspection PyUnresolvedReferences
        self.toggle_profile_v9.valueChanged.connect(self.click_set_profile_v9)
        # space
        toggle_hbox.addSpacing(35)
        # specs
        self.toggle_specs_v9 = QtWidgets.QDial()
        self.toggle_specs_v9.setNotchesVisible(True)
        self.toggle_specs_v9.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_specs_v9.setRange(2017, 2020)
        self.toggle_specs_v9.setValue(2019)
        self.toggle_specs_v9.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_specs_v9.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_specs_v9)
        # noinspection PyUnresolvedReferences
        self.toggle_specs_v9.valueChanged.connect(self.click_set_specs_v9)
        # stretch
        toggle_hbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # profile
        text_office = QtWidgets.QLabel("Office")
        text_office.setAlignment(QtCore.Qt.AlignRight)
        text_office.setFixedWidth(45)
        label_hbox.addWidget(text_office)
        text_field = QtWidgets.QLabel("Field")
        text_field.setAlignment(QtCore.Qt.AlignRight)
        text_field.setFixedWidth(35)
        label_hbox.addWidget(text_field)
        # space
        label_hbox.addSpacing(20)
        # specs
        text_2017 = QtWidgets.QLabel("2017")
        text_2017.setAlignment(QtCore.Qt.AlignCenter)
        text_2017.setFixedWidth(25)
        label_hbox.addWidget(text_2017)
        text_2020 = QtWidgets.QLabel("2020 test")
        text_2020.setAlignment(QtCore.Qt.AlignRight)
        text_2020.setFixedWidth(70)
        text_2020.setStyleSheet("QLabel { color :  rgb(200, 0, 0, 200); }")
        label_hbox.addWidget(text_2020)
        # stretch
        label_hbox.addStretch()

        vbox.addSpacing(12)

        # SECOND ROW OF KNOBS

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # specs
        self.text_lakes_v9 = QtWidgets.QLabel("Great Lakes")
        self.text_lakes_v9.setAlignment(QtCore.Qt.AlignCenter)
        self.text_lakes_v9.setFixedWidth(120)
        self.text_lakes_v9.setDisabled(True)
        label_hbox.addWidget(self.text_lakes_v9)
        # stretch
        label_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # specs
        self.toggle_area_v9 = QtWidgets.QDial()
        self.toggle_area_v9.setNotchesVisible(True)
        self.toggle_area_v9.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_area_v9.setRange(0, 2)
        self.toggle_area_v9.setValue(0)
        self.toggle_area_v9.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_area_v9.setInvertedAppearance(False)
        self.toggle_area_v9.setDisabled(True)
        # noinspection PyUnresolvedReferences
        # self.toggle_area.valueChanged.connect(self.on_settings_changed)
        toggle_hbox.addWidget(self.toggle_area_v9)
        # stretch
        toggle_hbox.addStretch()

        label2_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label2_hbox)
        # stretch
        label2_hbox.addStretch()
        # specs
        self.text_pacific_v9 = QtWidgets.QLabel("Pacific Coast")
        self.text_pacific_v9.setAlignment(QtCore.Qt.AlignCenter)
        self.text_pacific_v9.setFixedWidth(80)
        self.text_pacific_v9.setDisabled(True)
        label2_hbox.addWidget(self.text_pacific_v9)
        self.text_atlantic_v9 = QtWidgets.QLabel("Atlantic Coast")
        self.text_atlantic_v9.setAlignment(QtCore.Qt.AlignCenter)
        self.text_atlantic_v9.setFixedWidth(80)
        self.text_atlantic_v9.setDisabled(True)
        label2_hbox.addWidget(self.text_atlantic_v9)
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

        left_spacing = 20
        text_spacing = 260
        editor_spacing = 120

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.ask_multimedia_folder_v9 = QtWidgets.QCheckBox("")
        self.ask_multimedia_folder_v9.setChecked(True)
        toggle_hbox.addWidget(self.ask_multimedia_folder_v9)
        self.amf_text_v9 = QtWidgets.QLabel("Select the path to the images folder")
        self.amf_text_v9.setFixedWidth(text_spacing)
        toggle_hbox.addWidget(self.amf_text_v9)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.use_htd_v9 = QtWidgets.QCheckBox("")
        self.use_htd_v9.setChecked(True)
        # noinspection PyUnresolvedReferences
        self.use_htd_v9.stateChanged.connect(self.change_use_htd_v9)
        toggle_hbox.addWidget(self.use_htd_v9)
        self.htd_text_v9 = QtWidgets.QLabel('Check Image Names per HTDs (NOAA only)')
        self.htd_text_v9.setFixedWidth(text_spacing)
        toggle_hbox.addWidget(self.htd_text_v9)
        # take care to activate/deactivate the HTD items at the GUI initialization
        enable = self.toggle_specs_v9.value() in [2018, 2019, 2020] and self.prj.active_profile in [1, ]
        self.use_htd_v9.setEnabled(enable)
        self.htd_text_v9.setEnabled(enable)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.use_mhw_v9 = QtWidgets.QCheckBox("")
        self.use_mhw_v9.setChecked(True)
        # noinspection PyUnresolvedReferences
        self.use_mhw_v9.stateChanged.connect(self.change_use_mhw_v9)
        toggle_hbox.addWidget(self.use_mhw_v9)
        self.mhw_text_v9 = QtWidgets.QLabel("MHW [m] for WATLEV check: ")
        self.mhw_text_v9.setFixedWidth(text_spacing)
        self.mhw_text_v9.setDisabled(False)
        toggle_hbox.addWidget(self.mhw_text_v9)
        self.mhw_value_v9 = QtWidgets.QLineEdit()
        self.mhw_value_v9.setFixedWidth(editor_spacing)
        self.mhw_value_v9.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value_v9))
        self.mhw_value_v9.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.mhw_value_v9.setText("")
        self.mhw_value_v9.setDisabled(False)
        toggle_hbox.addWidget(self.mhw_value_v9)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.check_sorind_v9 = QtWidgets.QCheckBox("")
        self.check_sorind_v9.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.check_sorind_v9.stateChanged.connect(self.change_check_sorind_v9)
        toggle_hbox.addWidget(self.check_sorind_v9)
        self.sorind_text_v9 = QtWidgets.QLabel("SORIND (US,US,graph,HXXXXX): ")
        self.sorind_text_v9.setDisabled(True)
        self.sorind_text_v9.setFixedWidth(text_spacing)
        toggle_hbox.addWidget(self.sorind_text_v9)
        self.sorind_value_v9 = QtWidgets.QLineEdit()
        self.sorind_value_v9.setFixedWidth(editor_spacing)
        # self.sorind_value_v9.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value_v9))
        self.sorind_value_v9.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.sorind_value_v9.setText("")
        self.sorind_value_v9.setDisabled(True)
        toggle_hbox.addWidget(self.sorind_value_v9)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.check_sordat_v9 = QtWidgets.QCheckBox("")
        self.check_sordat_v9.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.check_sordat_v9.stateChanged.connect(self.change_check_sordat_v9)
        toggle_hbox.addWidget(self.check_sordat_v9)
        self.sordat_text_v9 = QtWidgets.QLabel("SORDAT (YYYYMMDD): ")
        self.sordat_text_v9.setDisabled(True)
        self.sordat_text_v9.setFixedWidth(text_spacing)
        toggle_hbox.addWidget(self.sordat_text_v9)
        self.sordat_value_v9 = QtWidgets.QLineEdit()
        self.sordat_value_v9.setFixedWidth(editor_spacing)
        # self.sordat_value_v9.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value_v9))
        self.sordat_value_v9.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.sordat_value_v9.setText("")
        self.sordat_value_v9.setDisabled(True)
        toggle_hbox.addWidget(self.sordat_value_v9)
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

    def _ui_execute_fsv9(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeFSv9.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Feature scan v9")
        button.setToolTip('Scan features in the loaded file checking their validity')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_feature_scan_v9)

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

    def click_feature_scan_v9(self):
        """trigger the feature scan v9"""
        self._click_feature_scan(9)

    def click_set_profile_v9(self, value):
        """ Change the profile in use """
        self.prj.active_profile = value
        self.toggle_profile_v9.setValue(value)
        self.settings.setValue("survey/scan_v9", value)
        logger.info('activated profile #%s' % value)

        # take care to activate/deactivate the HTD items
        enable = self.toggle_specs_v9.value() in [2018, 2019, 2020] and value in [1, ]
        self.use_htd_v9.setEnabled(enable)
        self.htd_text_v9.setEnabled(enable)

    def change_use_htd_v9(self):
        logger.info('use HTD check: %s' % self.use_htd_v9.isChecked())
        enable = self.use_htd_v9.isChecked()
        self.htd_text_v9.setEnabled(enable)

    def change_use_mhw_v9(self):
        logger.info('use mhw: %s' % self.use_mhw_v9.isChecked())
        enable = self.use_mhw_v9.isChecked()
        self.mhw_text_v9.setEnabled(enable)
        self.mhw_value_v9.setEnabled(enable)

    def change_check_sorind_v9(self):
        logger.info('check SORIND: %s' % self.check_sorind_v9.isChecked())
        enable = self.check_sorind_v9.isChecked()
        self.sorind_text_v9.setEnabled(enable)
        self.sorind_value_v9.setEnabled(enable)

    def change_check_sordat_v9(self):
        logger.info('check SORDAT: %s' % self.check_sordat_v9.isChecked())
        enable = self.check_sordat_v9.isChecked()
        self.sordat_text_v9.setEnabled(enable)
        self.sordat_value_v9.setEnabled(enable)

    def click_set_specs_v9(self, value):
        """ Change the specs in use """
        logger.info('selected specs %d' % value)

        enable = value in [2018, ]
        self.text_lakes_v9.setEnabled(enable)
        self.text_atlantic_v9.setEnabled(enable)
        self.text_pacific_v9.setEnabled(enable)
        self.toggle_area_v9.setEnabled(enable)

        enable = value in [2018, 2019, 2020]
        self.ask_multimedia_folder_v9.setEnabled(enable)
        self.amf_text_v9.setEnabled(enable)

        enable2 = value in [2018, 2019, 2020] and self.prj.active_profile in [1, ]
        self.use_htd_v9.setEnabled(enable2)
        self.htd_text_v9.setEnabled(enable2)

        self.use_mhw_v9.setEnabled(enable)
        enable3 = enable and self.use_mhw_v9.isChecked()
        self.mhw_text_v9.setEnabled(enable3)
        self.mhw_value_v9.setEnabled(enable3)

        self.check_sorind_v9.setEnabled(enable)
        enable3 = enable and self.check_sorind_v9.isChecked()
        self.sorind_text_v9.setEnabled(enable3)
        self.sorind_value_v9.setEnabled(enable3)

        self.check_sordat_v9.setEnabled(enable)
        enable3 = enable and self.check_sordat_v9.isChecked()
        self.sordat_text_v9.setEnabled(enable3)
        self.sordat_value_v9.setEnabled(enable3)

    # ------------- COMMON PART --------------- #

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_scan_features.html")

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
            images_folder = None
            htd_check = None

            if version == 9:

                specs_version = self.toggle_specs_v9.value()
                if specs_version == 2017:
                    specs_version = "2017"
                elif specs_version == 2018:
                    specs_version = "2018"
                elif specs_version == 2019:
                    specs_version = "2019"
                elif specs_version == 2020:
                    specs_version = "2020"
                else:
                    raise RuntimeError("unknown specs version: %s" % specs_version)

                toggle_survey_area = self.toggle_area_v9.value()
                if toggle_survey_area == 0:
                    survey_area = survey_areas["Pacific Coast"]
                elif toggle_survey_area == 1:
                    survey_area = survey_areas["Great Lakes"]
                elif toggle_survey_area == 2:
                    survey_area = survey_areas["Atlantic Coast"]
                else:
                    raise RuntimeError("unknown survey area: %s" % survey_area)

                if self.ask_multimedia_folder_v9.isChecked():
                    # ask for images folder
                    # noinspection PyCallByClass
                    images_folder = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                               "Select the folder with the images",
                                                                               QtCore.QSettings().value(
                                                                                   "feature_scan_images_folder", ""),
                                                                               )
                    if images_folder == "":
                        logger.debug('selecting multimedia folder: aborted')
                        images_folder = None

                    else:
                        logger.debug("selected images folder: %s" % images_folder)
                        QtCore.QSettings().setValue("feature_scan_images_folder", images_folder)

                use_mhw = self.use_mhw_v9.isChecked()
                mhw_value = 0.0
                if use_mhw:
                    mhw_str = self.mhw_value_v9.text()
                    if mhw_str == "":
                        msg = "The MHW field is empty! Enter a valid value or disable the WATLEV check."
                        # noinspection PyArgumentList
                        QtWidgets.QMessageBox.critical(self, "Feature scan v%d[%s]" % (version, specs_version),
                                                       msg, QtWidgets.QMessageBox.Ok)
                        return
                    else:
                        mhw_value = float(mhw_str)

                htd_check = self.use_htd_v9.isChecked()

                if self.check_sorind_v9.isChecked():
                    sorind = self.sorind_value_v9.text()
                    is_valid = self.prj.check_sorind(value=sorind)
                    # noinspection PyArgumentList
                    if not is_valid:
                        msg = "An invalid SORIND was entered!\n\nCheck: %s" % sorind
                        # noinspection PyCallByClass,PyArgumentList
                        QtWidgets.QMessageBox.critical(self, "Feature scan v%d[%s]" % (version, specs_version),
                                                       msg, QtWidgets.QMessageBox.Ok)
                        return

                if self.check_sordat_v9.isChecked():
                    sordat = self.sordat_value_v9.text()
                    is_valid = self.prj.check_sordat(value=sordat)
                    if not is_valid:
                        msg = "An invalid SORDAT was entered!\n\nCheck: %s" % sordat
                        # noinspection PyCallByClass,PyArgumentList
                        QtWidgets.QMessageBox.critical(self, "Feature scan v%d[%s]" % (version, specs_version),
                                                       msg, QtWidgets.QMessageBox.Ok)
                        return

            else:
                RuntimeError("unknown Feature Scan version: %s" % version)

            self.prj.feature_scan(version=version, specs_version=specs_version,
                                  survey_area=survey_area, use_mhw=use_mhw, mhw_value=mhw_value,
                                  sorind=sorind, sordat=sordat, multimedia_folder=images_folder,
                                  use_htd=htd_check)

            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Feature scan v%d[%s]" % (version, specs_version),
                                              self.prj.scan_msg, QtWidgets.QMessageBox.Ok)

        except Exception as e:
            traceback.print_exc()
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Error", "While running survey's feature scan v%d, %s" % (version, e),
                                           QtWidgets.QMessageBox.Ok)
            return
