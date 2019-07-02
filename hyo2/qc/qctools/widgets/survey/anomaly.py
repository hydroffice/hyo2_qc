from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper
from hyo2.qc.survey.anomaly.anomaly_detector_v1 import AnomalyDetectorV1

logger = logging.getLogger(__name__)


class AnomalyTab(QtWidgets.QMainWindow):
    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win, prj):
        QtWidgets.QMainWindow.__init__(self)
        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media

        self.settings = QtCore.QSettings()
        self.settings.setValue("survey/ad1_laplacian", self.settings.value("survey/ad1_laplacian", 0))
        self.settings.setValue("survey/ad1_gaussian", self.settings.value("survey/ad1_gaussian", 1))
        self.settings.setValue("survey/ad1_adjacent", self.settings.value("survey/ad1_adjacent", 1))
        self.settings.setValue("survey/ad1_slivers", self.settings.value("survey/ad1_slivers", 1))
        self.settings.setValue("survey/ad1_orphans", self.settings.value("survey/ad1_orphans", 1))
        self.settings.setValue("survey/ad1_edges", self.settings.value("survey/ad1_edges", 0))
        self.settings.setValue("survey/ad1_fff", self.settings.value("survey/ad1_fff", 0))
        self.settings.setValue("survey/ad1_designated", self.settings.value("survey/ad1_designated", 0))

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        # - anomaly v1
        self.anomalyDetectorV1 = QtWidgets.QGroupBox("Anomaly Detector v1")
        self.vbox.addWidget(self.anomalyDetectorV1)
        adv1_hbox = QtWidgets.QHBoxLayout()
        self.anomalyDetectorV1.setLayout(adv1_hbox)
        # -- settings
        self.setSettingsADv1 = QtWidgets.QGroupBox("Settings")
        adv1_hbox.addWidget(self.setSettingsADv1)
        self.paramsADv1 = None
        self.debugADv1 = None
        self.editable_v1 = None
        self.show_heights_adv1 = None
        self.set_height_label_adv1 = None
        self.set_height_label2_adv1 = None
        self.set_height_adv1 = None
        self.set_check_laplacian_adv1 = None
        self.set_check_curv_adv1 = None
        self.set_check_adjacent_adv1 = None
        self.set_check_slivers_adv1 = None
        self.set_check_isolated_adv1 = None
        self.set_check_edges_adv1 = None
        self.set_filter_fff_adv1 = None
        self.set_filter_designated_adv1 = None
        self.check_export_proxies_adv1 = None
        self.check_export_heights_adv1 = None
        self.check_export_curvatures_adv1 = None
        self._ui_settings_adv1()
        # -- execution
        self.executeADv1 = QtWidgets.QGroupBox("Execution")
        adv1_hbox.addWidget(self.executeADv1)
        self._ui_execute_adv1()

        self.float_height_adv1 = None

        self.vbox.addStretch()

    def keyPressEvent(self, event):
        key = event.key()
        # noinspection PyUnresolvedReferences
        if event.modifiers() == QtCore.Qt.ControlModifier:

            # noinspection PyUnresolvedReferences
            if key == QtCore.Qt.Key_D:

                if self.debugADv1.isHidden():
                    self.debugADv1.show()
                else:
                    self.debugADv1.hide()

                # return True
        return super().keyPressEvent(event)

    # v1

    def _ui_settings_adv1(self):
        self.settings_adv1_vbox = QtWidgets.QVBoxLayout()
        self.setSettingsADv1.setLayout(self.settings_adv1_vbox)

        self.settings_adv1_vbox.addStretch()

        min_group_box = 240

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(20, 5, 20, 5)
        self.settings_adv1_vbox.addLayout(vbox)

        self._ui_settings_params_checks_adv1(vbox=vbox, min_group_box=min_group_box)
        self._ui_settings_params_filters_adv1(vbox=vbox, min_group_box=min_group_box)
        self._ui_settings_params_debug_adv1(vbox=vbox, min_group_box=min_group_box)
        self._ui_settings_params_lock_adv1(vbox=vbox)

        self.settings_adv1_vbox.addStretch()

    def _ui_settings_params_checks_adv1(self, vbox: QtWidgets.QVBoxLayout, min_group_box: int) -> None:
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        set_checks_adv1 = QtWidgets.QGroupBox("Checks")
        set_checks_adv1.setMinimumWidth(min_group_box)
        hbox.addWidget(set_checks_adv1)
        chk_vbox = QtWidgets.QVBoxLayout()
        set_checks_adv1.setLayout(chk_vbox)

        # set height
        height_hbox = QtWidgets.QHBoxLayout()
        chk_vbox.addLayout(height_hbox)
        self.set_height_label_adv1 = QtWidgets.QLabel("Force flier heights to")
        self.set_height_label_adv1.setDisabled(True)
        height_hbox.addWidget(self.set_height_label_adv1)
        self.set_height_label_adv1.setFixedHeight(GuiSettings.single_line_height())
        self.set_height_adv1 = QtWidgets.QLineEdit("")
        height_hbox.addWidget(self.set_height_adv1)
        self.set_height_adv1.setFixedHeight(GuiSettings.single_line_height())
        # self.set_height_adv1.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.set_height_adv1))
        # noinspection PyUnresolvedReferences
        self.set_height_adv1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_height_adv1.setReadOnly(False)
        self.set_height_adv1.setFont(GuiSettings.console_font())
        self.set_height_adv1.setFixedWidth(60)
        self.set_height_adv1.setDisabled(True)
        self.set_height_label2_adv1 = QtWidgets.QLabel("meters")
        self.set_height_label2_adv1.setDisabled(True)
        height_hbox.addWidget(self.set_height_label2_adv1)
        height_hbox.addStretch()

        chk_vbox.addSpacing(6)

        self.set_check_laplacian_adv1 = QtWidgets.QCheckBox("#1: Laplacian Operator")
        self.set_check_laplacian_adv1.setDisabled(True)
        self.set_check_laplacian_adv1.setChecked(self.settings.value("survey/ad1_laplacian", 0) == 1)
        chk_vbox.addWidget(self.set_check_laplacian_adv1)

        self.set_check_curv_adv1 = QtWidgets.QCheckBox("#2: Gaussian Curvature")
        self.set_check_curv_adv1.setDisabled(True)
        self.set_check_curv_adv1.setChecked(self.settings.value("survey/ad1_gaussian", 1) == 1)
        chk_vbox.addWidget(self.set_check_curv_adv1)

        self.set_check_adjacent_adv1 = QtWidgets.QCheckBox("#3: Adjacent Cells")
        self.set_check_adjacent_adv1.setDisabled(True)
        self.set_check_adjacent_adv1.setChecked(self.settings.value("survey/ad1_adjacent", 1) == 1)
        chk_vbox.addWidget(self.set_check_adjacent_adv1)

        self.set_check_slivers_adv1 = QtWidgets.QCheckBox("#4: Edge Slivers")
        self.set_check_slivers_adv1.setDisabled(True)
        self.set_check_slivers_adv1.setChecked(self.settings.value("survey/ad1_slivers", 1) == 1)
        chk_vbox.addWidget(self.set_check_slivers_adv1)

        self.set_check_isolated_adv1 = QtWidgets.QCheckBox("#5: Isolated Nodes")
        self.set_check_isolated_adv1.setDisabled(True)
        self.set_check_isolated_adv1.setChecked(self.settings.value("survey/ad1_orphans", 0) == 1)
        chk_vbox.addWidget(self.set_check_isolated_adv1)

        self.set_check_edges_adv1 = QtWidgets.QCheckBox("#6: Noisy Edges")
        self.set_check_edges_adv1.setDisabled(True)
        self.set_check_edges_adv1.setChecked(self.settings.value("survey/ad1_edges", 0) == 1)
        chk_vbox.addWidget(self.set_check_edges_adv1)

        hbox.addStretch()

    def _ui_settings_params_filters_adv1(self, vbox: QtWidgets.QVBoxLayout, min_group_box: int) -> None:
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        set_filters_adv1 = QtWidgets.QGroupBox("Filters")
        set_filters_adv1.setMinimumWidth(min_group_box)
        hbox.addWidget(set_filters_adv1)
        flt_vbox = QtWidgets.QVBoxLayout()
        set_filters_adv1.setLayout(flt_vbox)

        # set distance
        distance_hbox = QtWidgets.QHBoxLayout()
        flt_vbox.addLayout(distance_hbox)
        self.set_distance_label_adv1 = QtWidgets.QLabel("Distance <=")
        self.set_distance_label_adv1.setDisabled(True)
        distance_hbox.addWidget(self.set_distance_label_adv1)
        self.set_distance_label_adv1.setFixedHeight(GuiSettings.single_line_height())
        self.set_distance_adv1 = QtWidgets.QLineEdit("")
        distance_hbox.addWidget(self.set_distance_adv1)
        self.set_distance_adv1.setFixedHeight(GuiSettings.single_line_height())
        # self.set_distance_adv1.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.set_distance_adv1))
        # noinspection PyUnresolvedReferences
        self.set_distance_adv1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_distance_adv1.setReadOnly(False)
        self.set_distance_adv1.setFont(GuiSettings.console_font())
        self.set_distance_adv1.setFixedWidth(60)
        # self.set_distance_adv1.setText("%.1f" % AnomalyDetectorV1.default_filter_distance)
        self.set_distance_adv1.setDisabled(True)
        self.set_distance_label2_adv1 = QtWidgets.QLabel("nodes")
        self.set_distance_label2_adv1.setDisabled(True)
        distance_hbox.addWidget(self.set_distance_label2_adv1)
        distance_hbox.addStretch()

        # set delta_z
        delta_z_hbox = QtWidgets.QHBoxLayout()
        flt_vbox.addLayout(delta_z_hbox)
        self.set_delta_z_label_adv1 = QtWidgets.QLabel("Delta Z <=")
        self.set_delta_z_label_adv1.setDisabled(True)
        delta_z_hbox.addWidget(self.set_delta_z_label_adv1)
        self.set_delta_z_label_adv1.setFixedHeight(GuiSettings.single_line_height())
        self.set_delta_z_adv1 = QtWidgets.QLineEdit("")
        delta_z_hbox.addWidget(self.set_delta_z_adv1)
        self.set_delta_z_adv1.setFixedHeight(GuiSettings.single_line_height())
        # self.set_delta_z_adv1.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.set_delta_z_adv1))
        # noinspection PyUnresolvedReferences
        self.set_delta_z_adv1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_delta_z_adv1.setReadOnly(False)
        self.set_delta_z_adv1.setFont(GuiSettings.console_font())
        self.set_delta_z_adv1.setFixedWidth(60)
        # self.set_delta_z_adv1.setText("%.2f" % AnomalyDetectorV1.default_filter_delta_z)
        self.set_delta_z_adv1.setDisabled(True)
        self.set_delta_z_label2_adv1 = QtWidgets.QLabel("meters")
        self.set_delta_z_label2_adv1.setDisabled(True)
        delta_z_hbox.addWidget(self.set_delta_z_label2_adv1)
        delta_z_hbox.addStretch()

        flt_vbox.addSpacing(6)

        self.set_filter_fff_adv1 = QtWidgets.QCheckBox("#1: Use Features from S57 File")
        self.set_filter_fff_adv1.setDisabled(True)
        self.set_filter_fff_adv1.setChecked(self.settings.value("survey/ad1_fff", 0) == 1)
        flt_vbox.addWidget(self.set_filter_fff_adv1)

        self.set_filter_designated_adv1 = QtWidgets.QCheckBox("#2: Use Designated (SR BAG only)")
        self.set_filter_designated_adv1.setDisabled(True)
        self.set_filter_designated_adv1.setChecked(self.settings.value("survey/ad1_designated", 0) == 1)
        flt_vbox.addWidget(self.set_filter_designated_adv1)

        hbox.addStretch()

    def _ui_settings_params_debug_adv1(self, vbox: QtWidgets.QVBoxLayout, min_group_box: int) -> None:
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.debugADv1 = QtWidgets.QGroupBox("Debug")
        self.debugADv1.hide()
        self.debugADv1.setMinimumWidth(min_group_box)
        hbox.addWidget(self.debugADv1)
        dbg_vbox = QtWidgets.QVBoxLayout()
        self.debugADv1.setLayout(dbg_vbox)

        self.check_export_proxies_adv1 = QtWidgets.QCheckBox("Export threshold proxies")
        self.check_export_proxies_adv1.setDisabled(True)
        self.check_export_proxies_adv1.setChecked(False)
        dbg_vbox.addWidget(self.check_export_proxies_adv1)

        self.check_export_heights_adv1 = QtWidgets.QCheckBox("Export height thresholds")
        self.check_export_heights_adv1.setDisabled(True)
        self.check_export_heights_adv1.setChecked(False)
        dbg_vbox.addWidget(self.check_export_heights_adv1)

        self.check_export_curvatures_adv1 = QtWidgets.QCheckBox("Export curvature thresholds")
        self.check_export_curvatures_adv1.setDisabled(True)
        self.check_export_curvatures_adv1.setChecked(False)
        dbg_vbox.addWidget(self.check_export_curvatures_adv1)

        hbox.addStretch()

    def _ui_settings_params_lock_adv1(self, vbox: QtWidgets.QVBoxLayout) -> None:
        vbox.addSpacing(6)

        lock_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(lock_hbox)
        lock_hbox.addStretch()
        self.editable_v1 = QtWidgets.QPushButton()
        self.editable_v1.setIconSize(QtCore.QSize(24, 24))
        self.editable_v1.setFixedHeight(28)
        edit_icon = QtGui.QIcon()
        edit_icon.addFile(os.path.join(self.parent_win.media, 'lock.png'), state=QtGui.QIcon.Off)
        edit_icon.addFile(os.path.join(self.parent_win.media, 'unlock.png'), state=QtGui.QIcon.On)
        self.editable_v1.setIcon(edit_icon)
        self.editable_v1.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.editable_v1.clicked.connect(self.on_editable_v1)
        self.editable_v1.setToolTip("Unlock editing for parameters")
        lock_hbox.addWidget(self.editable_v1)
        lock_hbox.addStretch()

        vbox.addStretch()

    def on_editable_v1(self):
        logger.debug("editable_v1: %s" % self.editable_v1.isChecked())
        if self.editable_v1.isChecked():
            msg = "Do you really want to change the settings?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Anomaly Detector v1 settings", msg,
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                self.editable_v1.setChecked(False)
                return

            self.set_height_label_adv1.setEnabled(True)
            self.set_height_label2_adv1.setEnabled(True)
            self.set_height_adv1.setEnabled(True)

            self.set_check_laplacian_adv1.setEnabled(True)
            self.set_check_curv_adv1.setEnabled(True)
            self.set_check_adjacent_adv1.setEnabled(True)
            self.set_check_slivers_adv1.setEnabled(True)
            self.set_check_isolated_adv1.setEnabled(True)
            self.set_check_edges_adv1.setEnabled(True)

            self.set_distance_label_adv1.setEnabled(True)
            self.set_distance_label2_adv1.setEnabled(True)
            self.set_distance_adv1.setEnabled(True)

            self.set_delta_z_label_adv1.setEnabled(True)
            self.set_delta_z_label2_adv1.setEnabled(True)
            self.set_delta_z_adv1.setEnabled(True)

            self.set_filter_fff_adv1.setEnabled(True)
            self.set_filter_designated_adv1.setEnabled(True)

            self.check_export_proxies_adv1.setEnabled(True)
            self.check_export_heights_adv1.setEnabled(True)
            self.check_export_curvatures_adv1.setEnabled(True)

        else:
            self.set_height_label_adv1.setDisabled(True)
            self.set_height_label2_adv1.setDisabled(True)
            self.set_height_adv1.setDisabled(True)

            self.set_check_laplacian_adv1.setDisabled(True)
            self.set_check_curv_adv1.setDisabled(True)
            self.set_check_adjacent_adv1.setDisabled(True)
            self.set_check_slivers_adv1.setDisabled(True)
            self.set_check_isolated_adv1.setDisabled(True)
            self.set_check_edges_adv1.setDisabled(True)

            self.set_distance_label_adv1.setDisabled(True)
            self.set_distance_label2_adv1.setDisabled(True)
            self.set_distance_adv1.setDisabled(True)

            self.set_delta_z_label_adv1.setDisabled(True)
            self.set_delta_z_label2_adv1.setDisabled(True)
            self.set_delta_z_adv1.setDisabled(True)

            self.set_filter_fff_adv1.setDisabled(True)
            self.set_filter_designated_adv1.setDisabled(True)

            self.check_export_proxies_adv1.setEnabled(True)
            self.check_export_heights_adv1.setEnabled(True)
            self.check_export_curvatures_adv1.setEnabled(True)

    def _parse_filter_distance_adv1(self) -> float:
        str_distance = self.set_distance_adv1.text()

        if str_distance == "":
            logger.warning("using default filter distance: %s" % AnomalyDetectorV1.default_filter_distance)
            self.set_distance_adv1.setText("%.1f" % AnomalyDetectorV1.default_filter_distance)
            return AnomalyDetectorV1.default_filter_distance

        try:

            distance = float(str_distance)

        except ValueError:

            msg = "Unable to parse the distance value: %s.\n" \
                  "Defaulting to %s!" % (str_distance, AnomalyDetectorV1.default_filter_distance)
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
            self.set_distance_adv1.setText("%.1f" % AnomalyDetectorV1.default_filter_distance)
            return AnomalyDetectorV1.default_filter_distance

        logger.info("filter distance: %s" % (distance,))
        return distance

    def _parse_filter_delta_z_adv1(self) -> float:
        str_delta_z = self.set_delta_z_adv1.text()

        if str_delta_z == "":
            logger.warning("using default filter delta_z: %s" % AnomalyDetectorV1.default_filter_delta_z)
            self.set_delta_z_adv1.setText("%.2f" % AnomalyDetectorV1.default_filter_delta_z)
            return AnomalyDetectorV1.default_filter_delta_z

        try:

            delta_z = float(str_delta_z)

        except ValueError:

            msg = "Unable to parse the delta_z value: %s.\n" \
                  "Defaulting to %s!" % (str_delta_z, AnomalyDetectorV1.default_filter_delta_z)
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
            self.set_delta_z_adv1.setText("%.2f" % AnomalyDetectorV1.default_filter_delta_z)
            return AnomalyDetectorV1.default_filter_delta_z

        logger.info("filter delta_z: %s" % (delta_z,))
        return delta_z

    def _ui_execute_adv1(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeADv1.setLayout(vbox)

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() + 50)
        button.setText("Anomaly Detector v1 beta")
        button.setStyleSheet("QPushButton { color: #D73232;}")
        button.setToolTip('Detect anomalies in the loaded surfaces')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_anomaly_detector_v1)
        # button.setDisabled(True)

        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.single_line_height())
        icon_info = QtCore.QFileInfo(os.path.join(self.media, 'small_info.png'))
        button.setIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        button.setToolTip('Open the manual page')
        button.setStyleSheet(GuiSettings.stylesheet_info_button())
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_open_manual_v1)

        hbox.addStretch()

        vbox.addStretch()

    @classmethod
    def click_open_manual_v1(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_detect_anomalies.html")

    # ####### detect anomalies #######

    def click_anomaly_detector_v1(self):
        self._click_anomaly_detector(1)

    def _click_anomaly_detector(self, version):
        """abstract the detect anomalies calling mechanism"""

        # sanity checks
        # - version
        if not isinstance(version, int):
            raise RuntimeError("passed invalid type for version: %s" % type(version))
        if version not in [1, ]:
            raise RuntimeError("passed invalid Anomaly Detector version: %s" % version)
        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.prj.grid_list) == 0:
            raise RuntimeError("the grid list is empty")

        height_mode = "auto"
        if version == 1:
            if self.set_height_adv1.text() != "":
                height_mode = self.set_height_adv1.text()
        else:
            raise RuntimeError("unknown Anomaly Detector' version: %s" % version)

        self.parent_win.change_info_url(
            Helper(lib_info=lib_info).web_url(suffix="survey_anomaly_detector_%d_fh_%s" % (version, height_mode)))

        self._parse_user_height(version=version)

        grid_list = self.prj.grid_list

        # pre checks

        if version == 1:

            if self.set_filter_fff_adv1.isChecked():

                if len(self.prj.s57_list) == 0:
                    msg = "The 'Use Features from S57 File' option is active, but no S57 files have been selected!\n" \
                          "\n" \
                          "Do you want to continue with the analysis?"
                    # noinspection PyCallByClass
                    ret = QtWidgets.QMessageBox.warning(self, "Anomaly Detector v1 filters", msg,
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if ret == QtWidgets.QMessageBox.No:
                        return

            if self.set_filter_designated_adv1.isChecked():
                at_least_one_bag = False
                for grid_file in grid_list:
                    if os.path.splitext(grid_file)[-1] == ".bag":
                        at_least_one_bag = True

                if not at_least_one_bag:
                    msg = "The 'Use Designated (SR BAG only)' option is active, " \
                          "but no BAG files have been selected!\n\n" \
                          "Do you want to continue with the analysis?"
                    # noinspection PyCallByClass
                    ret = QtWidgets.QMessageBox.warning(self, "Anomaly Detector v1 filters", msg,
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if ret == QtWidgets.QMessageBox.No:
                        return

        # for each file in the project grid list
        msg = "Potential anomalies per input:\n"
        opened_folders = list()
        for i, grid_file in enumerate(grid_list):

            # we want to be sure that the label is based on the name of the new file input
            self.prj.clear_survey_label()

            # switcher between different versions of detect anomalies
            if version in [1, ]:
                self._anomaly_detector(grid_file=grid_file, version=version, idx=(i + 1), total=len(grid_list))

            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Anomaly Detector v%s" % version)

            # export the anomalies
            saved = self._export_anomalies()
            msg += "- %s: %d\n" % (self.prj.cur_grid_basename, self.prj.number_of_anomalies())

            # open the output folder (if not already open)
            if saved:

                if self.prj.anomalies_output_folder not in opened_folders:
                    self.prj.open_anomalies_output_folder()
                    opened_folders.append(self.prj.anomalies_output_folder)

            self.prj.close_cur_grid()

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Anomaly Detector v%d" % version, msg, QtWidgets.QMessageBox.Ok)

    def _parse_user_height(self, version):

        # check for user input as anomaly height
        if version == 1:
            str_height = self.set_height_adv1.text()

            if str_height == "":
                self.float_height_adv1 = None

            else:

                fh_tokens = str_height.split(',')
                logger.debug("tokens: %d" % len(fh_tokens))

                # - case of just 1 value
                if len(fh_tokens) == 1:

                    try:

                        self.float_height_adv1 = float(str_height)

                    except ValueError:

                        msg = "Unable to parse the height value: %s.\n" \
                              "Defaulting to internal estimation!" % str_height
                        # noinspection PyCallByClass
                        QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
                        self.float_height_adv1 = None

                # - case of 1 input for each grid
                elif len(fh_tokens) == len(self.prj.grid_list):

                    self.set_height_adv1.clear()

                    try:

                        self.float_height_adv1 = list()
                        for fh_token in fh_tokens:

                            value = float(fh_token)
                            if value <= 0:
                                raise ValueError("invalid float input")
                            self.float_height_adv1.append(value)

                    except ValueError:

                        msg = "Unable to parse all the height values: %s.\n" \
                              "Defaulting to internal estimation!" % str_height
                        # noinspection PyCallByClass
                        QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
                        self.float_height_adv1 = None

                # - case of different number of input than the number of grids (this is an ERROR!)
                else:

                    self.set_height_adv1.clear()
                    self.float_height_adv1 = None

                    msg = "Invalid set of anomaly heights parsing \"%s\":\n" \
                          " - input values: %s\n" \
                          " - loaded grids: %s\n\n" \
                          "Defaulting to internal estimation!\n" \
                          % (str_height, len(fh_tokens), len(self.prj.grid_list))
                    # noinspection PyCallByClass
                    QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
                    logger.debug('detect anomalies v%d: invalid set of anomalies height: %s != %s'
                                 % (version, len(fh_tokens), len(self.prj.grid_list)))

            logger.info("anomaly height: %s" % (self.float_height_adv1,))

        else:  # this case should be never reached after the sanity checks
            raise RuntimeError("unknown Anomaly Detector' version: %s" % version)

    def _anomaly_detector(self, grid_file, version, idx, total):
        """ detect anomalies in the loaded surface using passed height parameter """

        # GUI initializes, then passes progress bar

        logger.debug('detect anomalies v%d ...' % version)

        self.prj.progress.start(title="Anomaly Detector v%d" % version,
                                text="Data loading [%d/%d]" % (idx, total),
                                init_value=2)

        try:
            self.prj.set_cur_grid(path=grid_file)
            self.prj.open_to_read_cur_grid()

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While reading grid file, %s" % e, QtWidgets.QMessageBox.Ok)
            self.prj.progress.setValue(100)
            return

        self.prj.progress.update(value=5, text="Anomaly Detector v%d [%d/%d]" % (version, idx, total))

        settings = QtCore.QSettings()
        try:
            if version == 1:

                height = None
                if type(self.float_height_adv1) is float:
                    height = self.float_height_adv1
                if type(self.float_height_adv1) is list:
                    height = self.float_height_adv1[idx - 1]

                save_proxies = self.check_export_proxies_adv1.isChecked()
                save_heights = self.check_export_heights_adv1.isChecked()
                save_curvatures = self.check_export_curvatures_adv1.isChecked()

                if self.set_check_laplacian_adv1.isChecked():
                    settings.setValue("survey/ad1_laplacian", 1)
                else:
                    settings.setValue("survey/ad1_laplacian", 0)
                if self.set_check_curv_adv1.isChecked():
                    settings.setValue("survey/ad1_gaussian", 1)
                else:
                    settings.setValue("survey/ad1_gaussian", 0)
                if self.set_check_adjacent_adv1.isChecked():
                    settings.setValue("survey/ad1_adjacent", 1)
                else:
                    settings.setValue("survey/ad1_adjacent", 0)
                if self.set_check_slivers_adv1.isChecked():
                    settings.setValue("survey/ad1_slivers", 1)
                else:
                    settings.setValue("survey/ad1_slivers", 0)
                if self.set_check_isolated_adv1.isChecked():
                    settings.setValue("survey/ad1_orphans", 1)
                else:
                    settings.setValue("survey/ad1_orphans", 0)
                if self.set_check_edges_adv1.isChecked():
                    settings.setValue("survey/ad1_edges", 1)
                else:
                    settings.setValue("survey/ad1_edges", 0)
                if self.set_filter_fff_adv1.isChecked():
                    settings.setValue("survey/ad1_fff", 1)
                else:
                    settings.setValue("survey/ad1_fff", 0)
                if self.set_filter_designated_adv1.isChecked():
                    settings.setValue("survey/ad1_designated", 1)
                else:
                    settings.setValue("survey/ad1_designated", 0)

                self.prj.detect_anomalies_v1(height=height,
                                             check_laplacian=self.set_check_laplacian_adv1.isChecked(),
                                             check_curv=self.set_check_curv_adv1.isChecked(),
                                             check_adjacent=self.set_check_adjacent_adv1.isChecked(),
                                             check_slivers=self.set_check_slivers_adv1.isChecked(),
                                             check_isolated=self.set_check_isolated_adv1.isChecked(),
                                             check_edges=self.set_check_edges_adv1.isChecked(),
                                             filter_fff=self.set_filter_fff_adv1.isChecked(),
                                             filter_designated=self.set_filter_designated_adv1.isChecked(),
                                             export_proxies=save_proxies,
                                             export_heights=save_heights,
                                             export_curvatures=save_curvatures,
                                             progress_bar=self.prj.progress
                                             )

                if self.set_check_edges_adv1.isChecked() or self.set_filter_designated_adv1.isChecked():
                    self.prj.close_cur_grid()
                    self.prj.set_cur_grid(path=grid_file)
                    self.prj.open_to_read_cur_grid()

                    distance = self._parse_filter_distance_adv1()
                    delta_z = self._parse_filter_delta_z_adv1()
                    self.prj.detect_anomalies_v1_apply_filters(distance=distance, delta_z=delta_z)

        except MemoryError:
            err_str = "While finding anomalies, there was a memory error. Try to close unused applications!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", err_str, QtWidgets.QMessageBox.Ok)
            self.prj.progress.end()
            return

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While finding anomalies, %s" % e, QtWidgets.QMessageBox.Ok)
            self.prj.progress.end()
            return

        self.prj.progress.end()

    def _export_anomalies(self):
        """ export potential anomalies """
        logger.debug('exporting anomalies ...')
        saved = self.prj.save_anomalies()
        logger.debug('exporting anomalies: done')
        return saved

    def grids_changed(self):
        self.set_height_adv1.clear()
