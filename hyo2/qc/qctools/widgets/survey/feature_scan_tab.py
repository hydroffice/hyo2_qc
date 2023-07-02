import logging
import os
import traceback
from typing import Optional, TYPE_CHECKING

from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper
from hyo2.qc.common import lib_info
from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.survey.scan.checks import Checks

if TYPE_CHECKING:
    from hyo2.qc.qctools.widgets.survey.survey_widget import SurveyWidget
    from hyo2.qc.survey.project import SurveyProject

logger = logging.getLogger(__name__)


class FeatureScanTab(QtWidgets.QMainWindow):
    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win: 'SurveyWidget', prj: 'SurveyProject'):
        super().__init__(parent_win)
        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media

        self.settings = QtCore.QSettings()
        self.settings.setValue("survey/scan", self.settings.value("survey/scan", 0))
        self.prj.active_profile = self.settings.value("survey/scan", 0)

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        # version ui
        self.toggle_profile = None  # type: Optional[QtWidgets.QDial]
        self.toggle_specs = None  # type: Optional[QtWidgets.QDial]
        self.text_office = None  # type: Optional[QtWidgets.QLabel]
        self.text_office_note = "Office -> ONLY for deliverables from HSD to MCD"
        self.text_atlantic = None  # type: Optional[QtWidgets.QLabel]
        self.text_pacific = None  # type: Optional[QtWidgets.QLabel]
        self.text_lakes = None  # type: Optional[QtWidgets.QLabel]
        self.great_lakes = None  # type: Optional[QtWidgets.QCheckBox]
        self.great_lakes_text = None  # type: Optional[QtWidgets.QLabel]
        self.set_images_folder = None  # type: Optional[QtWidgets.QCheckBox]
        self.set_images_folder_text = None  # type: Optional[QtWidgets.QLabel]
        self.check_image_names = None  # type: Optional[QtWidgets.QCheckBox]
        self.check_image_names_text = None  # type: Optional[QtWidgets.QLabel]
        self.use_mhw = None  # type: Optional[QtWidgets.QCheckBox]
        self.mhw_text = None  # type: Optional[QtWidgets.QLabel]
        self.mhw_value = None  # type: Optional[QtWidgets.QLineEdit]
        self.check_sorind = None  # type: Optional[QtWidgets.QCheckBox]
        self.sorind_text = None  # type: Optional[QtWidgets.QLabel]
        self.sorind_value = None  # type: Optional[QtWidgets.QLineEdit]
        self.check_sordat = None  # type: Optional[QtWidgets.QCheckBox]
        self.sordat_text = None  # type: Optional[QtWidgets.QLabel]
        self.sordat_value = None  # type: Optional[QtWidgets.QLineEdit]

        # - feature scan
        self.featureScan = QtWidgets.QGroupBox("Feature scan v12")
        self.featureScan.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.featureScan)
        fs_hbox = QtWidgets.QHBoxLayout()
        self.featureScan.setLayout(fs_hbox)
        # -- parameters
        self.setParametersFS = QtWidgets.QGroupBox("Parameters")
        self.setParametersFS.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fs_hbox.addWidget(self.setParametersFS)
        self._ui_parameters_fs()
        # -- execution
        self.executeFS = QtWidgets.QGroupBox("Execution")
        self.executeFS.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        fs_hbox.addWidget(self.executeFS)
        self._ui_execute_fs()

        self.vbox.addStretch()

    def keyPressEvent(self, event):
        # key = event.key()
        if event.modifiers() == QtCore.Qt.ControlModifier:
            # if key == QtCore.Qt.Key_8:
            #
            #     if self.featureScanV8.isHidden():
            #         self.featureScanV8.show()
            #     else:
            #         self.featureScanV8.hide()
            pass

            # return True
        return super().keyPressEvent(event)

    # -----------  FEATURE SCAN   ------------- #

    def _ui_parameters_fs(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersFS.setLayout(hbox)
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
        text_office_empty.setFixedWidth(40)
        label_up_hbox.addWidget(text_office_empty)
        # space
        label_up_hbox.addSpacing(40)
        # specs
        text_2020 = QtWidgets.QLabel("2020")
        text_2020.setAlignment(QtCore.Qt.AlignCenter)
        text_2020.setFixedWidth(25)
        label_up_hbox.addWidget(text_2020)
        text_2021 = QtWidgets.QLabel("2021")
        text_2021.setAlignment(QtCore.Qt.AlignCenter)
        text_2021.setFixedWidth(75)
        label_up_hbox.addWidget(text_2021)

        # stretch
        label_up_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # profile
        self.toggle_profile = QtWidgets.QDial()
        self.toggle_profile.setNotchesVisible(True)
        self.toggle_profile.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_profile.setRange(0, 1)
        self.toggle_profile.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_profile.setInvertedAppearance(False)
        self.toggle_profile.setSliderPosition(self.settings.value("survey/scan", 0))
        toggle_hbox.addWidget(self.toggle_profile)
        # noinspection PyUnresolvedReferences
        self.toggle_profile.valueChanged.connect(self.click_set_profile)
        # space
        toggle_hbox.addSpacing(35)
        # specs
        self.toggle_specs = QtWidgets.QDial()
        self.toggle_specs.setNotchesVisible(True)
        self.toggle_specs.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_specs.setRange(2019, 2022)
        self.toggle_specs.setValue(2022)
        self.toggle_specs.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_specs.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_specs)
        # noinspection PyUnresolvedReferences
        self.toggle_specs.valueChanged.connect(self.click_set_specs)
        # stretch
        toggle_hbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # profile
        text_office = QtWidgets.QLabel("Office")
        text_office.setAlignment(QtCore.Qt.AlignRight)
        text_office.setFixedWidth(60)
        label_hbox.addWidget(text_office)
        text_field = QtWidgets.QLabel("Field")
        text_field.setAlignment(QtCore.Qt.AlignRight)
        text_field.setFixedWidth(35)
        label_hbox.addWidget(text_field)
        # space
        label_hbox.addSpacing(20)
        # specs
        text_2019 = QtWidgets.QLabel("2019")
        text_2019.setAlignment(QtCore.Qt.AlignCenter)
        text_2019.setFixedWidth(25)
        label_hbox.addWidget(text_2019)
        text_2022 = QtWidgets.QLabel("2022")
        text_2022.setAlignment(QtCore.Qt.AlignCenter)
        text_2022.setFixedWidth(75)
        # text_2021.setStyleSheet("QLabel { color :  rgb(200, 0, 0, 200); }")
        label_hbox.addWidget(text_2022)
        # stretch
        label_hbox.addStretch()

        vbox.addSpacing(12)

        # Row of disappearing text
        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        hidden = self.prj.active_profile == 1
        if hidden:
            self.text_office = QtWidgets.QLabel("")
        else:
            self.text_office = QtWidgets.QLabel(self.text_office_note)
        # self.text_office.stateChanged.connect(self.click_set_profile)
        self.text_office.setAlignment(QtCore.Qt.AlignCenter)
        self.text_office.setFixedWidth(300)
        self.text_office.setDisabled(False)
        self.text_office.setStyleSheet("QLabel { font-weight: bold; }")
        label_hbox.addWidget(self.text_office)
        # stretch
        label_hbox.addStretch()

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
        self.great_lakes = QtWidgets.QCheckBox("")
        self.great_lakes.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.great_lakes.stateChanged.connect(self.change_great_lakes)
        toggle_hbox.addWidget(self.great_lakes)
        self.great_lakes_text = QtWidgets.QLabel("Use settings for Great Lakes area")
        self.great_lakes_text.setFixedWidth(text_spacing)
        self.great_lakes_text.setDisabled(True)
        toggle_hbox.addWidget(self.great_lakes_text)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.check_image_names = QtWidgets.QCheckBox("")
        self.check_image_names.setChecked(True)
        # noinspection PyUnresolvedReferences
        self.check_image_names.stateChanged.connect(self.change_check_image_names)
        toggle_hbox.addWidget(self.check_image_names)
        self.check_image_names_text = QtWidgets.QLabel("Check image names (HSSD 2021)")
        self.check_image_names_text.setFixedWidth(text_spacing)
        toggle_hbox.addWidget(self.check_image_names_text)
        self.check_image_names.setChecked(True)
        self.check_image_names.setEnabled(False)
        self.check_image_names_text.setEnabled(True)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.set_images_folder = QtWidgets.QCheckBox("")
        self.set_images_folder.setChecked(True)
        # noinspection PyUnresolvedReferences
        self.set_images_folder.stateChanged.connect(self.change_check_image_paths)
        toggle_hbox.addWidget(self.set_images_folder)
        self.set_images_folder_text = QtWidgets.QLabel("Set folder for checking image paths")
        self.set_images_folder_text.setFixedWidth(text_spacing)
        toggle_hbox.addWidget(self.set_images_folder_text)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.use_mhw = QtWidgets.QCheckBox("")
        self.use_mhw.setChecked(True)
        # noinspection PyUnresolvedReferences
        self.use_mhw.stateChanged.connect(self.change_use_mhw)
        toggle_hbox.addWidget(self.use_mhw)
        self.mhw_text = QtWidgets.QLabel("MHW [m] for WATLEV check: ")
        self.mhw_text.setFixedWidth(text_spacing)
        self.mhw_text.setDisabled(False)
        toggle_hbox.addWidget(self.mhw_text)
        self.mhw_value = QtWidgets.QLineEdit()
        self.mhw_value.setFixedWidth(editor_spacing)
        self.mhw_value.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value))
        self.mhw_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.mhw_value.setText("")
        self.mhw_value.setDisabled(False)
        toggle_hbox.addWidget(self.mhw_value)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.check_sorind = QtWidgets.QCheckBox("")
        self.check_sorind.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.check_sorind.stateChanged.connect(self.change_check_sorind)
        toggle_hbox.addWidget(self.check_sorind)
        self.sorind_text = QtWidgets.QLabel("SORIND (US,US,graph,HXXXXX): ")
        self.sorind_text.setDisabled(True)
        self.sorind_text.setFixedWidth(text_spacing)
        toggle_hbox.addWidget(self.sorind_text)
        self.sorind_value = QtWidgets.QLineEdit()
        self.sorind_value.setFixedWidth(editor_spacing)
        # self.sorind_value.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value))
        self.sorind_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.sorind_value.setText("")
        self.sorind_value.setDisabled(True)
        toggle_hbox.addWidget(self.sorind_value)
        # stretch
        toggle_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addSpacing(left_spacing)
        self.check_sordat = QtWidgets.QCheckBox("")
        self.check_sordat.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.check_sordat.stateChanged.connect(self.change_check_sordat)
        toggle_hbox.addWidget(self.check_sordat)
        self.sordat_text = QtWidgets.QLabel("SORDAT (YYYYMMDD): ")
        self.sordat_text.setDisabled(True)
        self.sordat_text.setFixedWidth(text_spacing)
        toggle_hbox.addWidget(self.sordat_text)
        self.sordat_value = QtWidgets.QLineEdit()
        self.sordat_value.setFixedWidth(editor_spacing)
        # self.sordat_value.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value))
        self.sordat_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.sordat_value.setText("")
        self.sordat_value.setDisabled(True)
        toggle_hbox.addWidget(self.sordat_value)
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

    def _ui_execute_fs(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeFS.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Feature Scan v12")
        button.setToolTip('Scan features in the loaded file checking their validity')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_feature_scan)

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

    def click_set_profile(self, value):
        """ Change the profile in use """
        self.prj.active_profile = value
        self.toggle_profile.setValue(value)
        self.settings.setValue("survey/scan", value)
        logger.info('activated profile #%s' % value)

        # check images was optional in 2019 for NOAA contractors
        enable = self.toggle_specs.value() in [2019, ] and (value == 1)
        self.check_image_names.setEnabled(enable)
        self.check_image_names_text.setEnabled(enable)

        # make office text visible
        if value == 1:
            self.text_office.setText("")
        else:
            self.text_office.setText(self.text_office_note)
            self.check_image_names.setChecked(True)

    def change_great_lakes(self):
        logger.info('use Great Lakes: %s' % self.great_lakes.isChecked())
        enable = self.great_lakes.isChecked()
        self.great_lakes_text.setEnabled(enable)

    def change_check_image_names(self):
        logger.info('check image names: %s' % self.check_image_names.isChecked())
        enable = self.check_image_names.isChecked()
        self.check_image_names_text.setEnabled(enable)

    def change_check_image_paths(self):
        logger.info('check image paths: %s' % self.set_images_folder.isChecked())
        enable = self.set_images_folder.isChecked()
        self.set_images_folder_text.setEnabled(enable)

    def change_use_mhw(self):
        logger.info('use mhw: %s' % self.use_mhw.isChecked())
        enable = self.use_mhw.isChecked()
        self.mhw_text.setEnabled(enable)
        self.mhw_value.setEnabled(enable)

    def change_check_sorind(self):
        logger.info('check SORIND: %s' % self.check_sorind.isChecked())
        enable = self.check_sorind.isChecked()
        self.sorind_text.setEnabled(enable)
        self.sorind_value.setEnabled(enable)

    def change_check_sordat(self):
        logger.info('check SORDAT: %s' % self.check_sordat.isChecked())
        enable = self.check_sordat.isChecked()
        self.sordat_text.setEnabled(enable)
        self.sordat_value.setEnabled(enable)

    def click_set_specs(self, value):
        """ Change the specs in use """
        logger.info('selected specs %d' % value)

        # check images was optional in 2019 for NOAA contractors
        check_images_enabled = value in [2019, ] and self.prj.active_profile in [1, ]
        self.check_image_names.setEnabled(check_images_enabled)
        self.check_image_names_text.setEnabled(check_images_enabled)
        if value in [2020, ]:
            self.check_image_names_text.setText('Check image names (HSSD 2020)')
            self.check_image_names.setChecked(True)
        elif value in [2021, ]:
            self.check_image_names_text.setText('Check image names (HSSD 2021)')
            self.check_image_names.setChecked(True)
        else:
            self.check_image_names_text.setText('Check image names (HTDs 2018-4/5, NOAA only)')

        if self.check_image_names.isChecked():
            self.check_image_names_text.setEnabled(True)

    # ------------- COMMON PART --------------- #

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/stable/user_manual_survey_feature_scan.html")

    def click_feature_scan(self):
        """abstract the feature scan calling mechanism"""

        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="survey_feature_scan"))

        # library takes care of progress bar

        try:
            sorind = None
            sordat = None
            images_folder = None

            specs_version = self.toggle_specs.value()
            if specs_version == 2019:
                specs_version = "2019"
            elif specs_version == 2020:
                specs_version = "2020"
            elif specs_version == 2021:
                specs_version = "2021"
            elif specs_version == 2022:
                specs_version = "2022"
            else:
                raise RuntimeError("unknown specs version: %s" % specs_version)

            checked_great_lakes = self.great_lakes.isChecked()
            if checked_great_lakes:
                survey_area = Checks.survey_areas["Great Lakes"]
            else:  # any area different from Great Lakes is fine
                survey_area = Checks.survey_areas["Atlantic Coast"]

            if self.set_images_folder.isChecked():
                # ask for images folder
                # noinspection PyCallByClass
                images_folder = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                           "Select the folder with the images",
                                                                           QtCore.QSettings().value(
                                                                               "feature_scan_images_folder", ""),
                                                                           )
                if images_folder == "":
                    logger.debug('selecting multimedia folder: aborted')
                    return

                logger.debug("selected images folder: %s" % images_folder)
                QtCore.QSettings().setValue("feature_scan_images_folder", images_folder)

            use_mhw = self.use_mhw.isChecked()
            mhw_value = 0.0
            if use_mhw:
                mhw_str = self.mhw_value.text()
                if mhw_str == "":
                    msg = "The MHW field is empty! Enter a valid value or disable the WATLEV check."
                    # noinspection PyArgumentList
                    QtWidgets.QMessageBox.critical(self, "Feature scan [%s]" % (specs_version,),
                                                   msg, QtWidgets.QMessageBox.Ok)
                    return
                else:
                    mhw_value = float(mhw_str)

            image_names_check = self.check_image_names.isChecked()

            if self.check_sorind.isChecked():
                sorind = self.sorind_value.text()
                is_valid = self.prj.check_sorind(value=sorind)
                # noinspection PyArgumentList
                if not is_valid:
                    msg = "An invalid SORIND was entered!\n\nCheck: %s" % sorind
                    # noinspection PyCallByClass,PyArgumentList
                    QtWidgets.QMessageBox.critical(self, "Feature scan [%s]" % (specs_version,),
                                                   msg, QtWidgets.QMessageBox.Ok)
                    return

            if self.check_sordat.isChecked():
                sordat = self.sordat_value.text()
                is_valid = self.prj.check_sordat(value=sordat)
                if not is_valid:
                    msg = "An invalid SORDAT was entered!\n\nCheck: %s" % sordat
                    # noinspection PyCallByClass,PyArgumentList
                    QtWidgets.QMessageBox.critical(self, "Feature scan [%s]" % (specs_version,),
                                                   msg, QtWidgets.QMessageBox.Ok)
                    return

            self.prj.feature_scan(specs_version=specs_version,
                                  survey_area=survey_area, use_mhw=use_mhw, mhw_value=mhw_value,
                                  sorind=sorind, sordat=sordat, multimedia_folder=images_folder,
                                  check_image_names=image_names_check)

            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Feature scan [%s]" % (specs_version,),
                                              self.prj.scan_msg, QtWidgets.QMessageBox.Ok)

        except Exception as e:
            traceback.print_exc()
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Error", "While running survey's feature scan: %s" % (e,),
                                           QtWidgets.QMessageBox.Ok)
            return
