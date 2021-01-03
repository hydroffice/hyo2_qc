from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging
from typing import TYPE_CHECKING

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper

if TYPE_CHECKING:
    from hyo2.qc.qctools.widgets.survey.widget import SurveyWidget
    from hyo2.qc.survey.project import SurveyProject

logger = logging.getLogger(__name__)


class BAGChecksTab(QtWidgets.QMainWindow):
    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win: 'SurveyWidget', prj: 'SurveyProject'):
        QtWidgets.QMainWindow.__init__(self)
        # store a project reference
        self.prj: 'SurveyProject' = prj
        self.parent_win: 'SurveyWidget' = parent_win
        self.media: str = self.parent_win.media

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        # - bag checks v1
        self.bag_checks_v1 = QtWidgets.QGroupBox("BAG Checks v1")
        self.vbox.addWidget(self.bag_checks_v1)
        bcv1_hbox = QtWidgets.QHBoxLayout()
        self.bag_checks_v1.setLayout(bcv1_hbox)
        # -- parameters
        self.setSettingsBCv1 = QtWidgets.QGroupBox("Settings")
        bcv1_hbox.addWidget(self.setSettingsBCv1)
        self.check_structure = None
        self.check_metadata = None
        self.check_elevation = None
        self.check_uncertainty = None
        self.check_tracking_list = None
        self._ui_settings_bcv1()
        # -- execution
        self.executeBQv1 = QtWidgets.QGroupBox("Execution")
        bcv1_hbox.addWidget(self.executeBQv1)
        self._ui_execute_bcv1()

        self.vbox.addStretch()

    def _ui_settings_bcv1(self):
        vbox = QtWidgets.QVBoxLayout()
        self.setSettingsBCv1.setLayout(vbox)

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        validation_profile_gb = QtWidgets.QGroupBox("Validation Profile")
        hbox.addWidget(validation_profile_gb)
        rules_hbox = QtWidgets.QHBoxLayout()
        validation_profile_gb.setLayout(rules_hbox)
        self.use_noaa_ocs_rules = QtWidgets.QRadioButton("NOAA OCS", self)
        self.use_noaa_ocs_rules.setChecked(True)
        rules_hbox.addSpacing(8)
        rules_hbox.addWidget(self.use_noaa_ocs_rules)
        self.use_general_rules = QtWidgets.QRadioButton("General", self)
        rules_hbox.addWidget(self.use_general_rules)
        hbox.addStretch()

        vbox.addSpacing(6)

        check_width = 160

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        self.check_structure = QtWidgets.QCheckBox("Check the overall structure", self)
        self.check_structure.setChecked(True)
        self.check_structure.setFixedWidth(check_width)
        hbox.addWidget(self.check_structure)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        self.check_metadata = QtWidgets.QCheckBox("Check the metadata content", self)
        self.check_metadata.setChecked(True)
        self.check_metadata.setFixedWidth(check_width)
        hbox.addWidget(self.check_metadata)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        self.check_elevation = QtWidgets.QCheckBox("Check the elevation layer", self)
        self.check_elevation.setChecked(True)
        self.check_elevation.setFixedWidth(check_width)
        hbox.addWidget(self.check_elevation)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        self.check_uncertainty = QtWidgets.QCheckBox("Check the uncertainty layer", self)
        self.check_uncertainty.setChecked(True)
        self.check_uncertainty.setFixedWidth(check_width)
        hbox.addWidget(self.check_uncertainty)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        self.check_tracking_list = QtWidgets.QCheckBox("Check the tracking list", self)
        self.check_tracking_list.setChecked(True)
        self.check_tracking_list.setFixedWidth(check_width)
        hbox.addWidget(self.check_tracking_list)
        hbox.addStretch()

        vbox.addStretch()

    def _ui_execute_bcv1(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeBQv1.setLayout(vbox)

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() * 1.3)
        button.setText("BAG Checks v1")
        button.setToolTip('Perform checks on BAG files')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_bag_checks_v1)

        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.single_line_height())
        icon_info = QtCore.QFileInfo(os.path.join(self.media, 'small_info.png'))
        button.setIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        button.setToolTip('Open the manual page')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_open_manual)

        hbox.addStretch()

        vbox.addStretch()

    def click_bag_checks_v1(self):
        """trigger the bag checks v1"""
        self._click_bag_checks(1)

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_bag_checks.html")

    def _click_bag_checks(self, version: int):
        """abstract the BAG checks calling mechanism"""

        # version check
        if version not in [1, ]:
            raise RuntimeError("passed invalid Grid Checks version: %s" % version)

        url_suffix = "survey_bag_checks_%d" % version
        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix=url_suffix))

        try:
            self.prj.bag_checks_v1(use_nooa_ocs_profile=self.use_noaa_ocs_rules.isChecked(),
                                   check_structure=self.check_structure.isChecked(),
                                   check_metadata=self.check_metadata.isChecked(),
                                   check_elevation=self.check_elevation.isChecked(),
                                   check_uncertainty=self.check_uncertainty.isChecked(),
                                   check_tracking_list=self.check_tracking_list.isChecked())

        except Exception as e:
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Error", "%s" % e, QtWidgets.QMessageBox.Ok)
            self.prj.progress.end()
            return

        # noinspection PyCallByClass,PyArgumentList
        QtWidgets.QMessageBox.information(self, "BAG Checks v%d" % version, self.prj.bag_checks_message,
                                          QtWidgets.QMessageBox.Ok)
