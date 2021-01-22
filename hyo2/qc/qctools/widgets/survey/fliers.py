from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper
from hyo2.qc.survey.fliers.find_fliers_v8 import FindFliersV8

logger = logging.getLogger(__name__)


class FliersTab(QtWidgets.QMainWindow):
    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win, prj):
        QtWidgets.QMainWindow.__init__(self)
        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media

        self.settings = QtCore.QSettings()
        self.settings.setValue("survey/ff8_laplacian", self.settings.value("survey/ff8_laplacian", 0))
        self.settings.setValue("survey/ff8_gaussian", self.settings.value("survey/ff8_gaussian", 1))
        self.settings.setValue("survey/ff8_adjacent", self.settings.value("survey/ff8_adjacent", 1))
        self.settings.setValue("survey/ff8_slivers", self.settings.value("survey/ff8_slivers", 1))
        self.settings.setValue("survey/ff8_orphans", self.settings.value("survey/ff8_orphans", 1))
        self.settings.setValue("survey/ff8_edges", self.settings.value("survey/ff8_edges", 0))
        self.settings.setValue("survey/ff8_fff", self.settings.value("survey/ff8_fff", 0))
        self.settings.setValue("survey/ff8_designated", self.settings.value("survey/ff8_designated", 0))

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        # - flier finder v8
        self.flierFinderV8 = QtWidgets.QGroupBox("Flier finder v8")
        self.vbox.addWidget(self.flierFinderV8)
        ffv8_hbox = QtWidgets.QHBoxLayout()
        self.flierFinderV8.setLayout(ffv8_hbox)
        # -- settings
        self.setSettingsFFv8 = QtWidgets.QGroupBox("Settings")
        ffv8_hbox.addWidget(self.setSettingsFFv8)
        self.paramsFFv8 = None
        self.debugFFv8 = None
        self.editable_v8 = None
        self.show_heights_ffv8 = None
        self.set_height_label_ffv8 = None
        self.set_height_label2_ffv8 = None
        self.set_height_ffv8 = None
        self.set_check_laplacian_ffv8 = None
        self.set_check_curv_ffv8 = None
        self.set_check_adjacent_ffv8 = None
        self.set_check_slivers_ffv8 = None
        self.set_check_isolated_ffv8 = None
        self.set_check_edges_ffv8 = None
        self.text_pct = None
        self.text_pct_90 = None
        self.text_pct_100 = None
        self.text_pct_125 = None
        self.text_pct_150 = None
        self.text_pct_200 = None
        self.text_distance = None
        self.text_distance_2 = None
        self.text_distance_3 = None
        self.slider_edges_distance_v8 = None
        self.slider_edges_pct_tvu_v8 = None
        self.set_filter_fff_ffv8 = None
        self.set_filter_designated_ffv8 = None
        self._ui_settings_ffv8()
        # -- execution
        self.executeFFv8 = QtWidgets.QGroupBox("Execution")
        ffv8_hbox.addWidget(self.executeFFv8)
        self._ui_execute_ffv8()

        self.float_height_ffv8 = None

        self.vbox.addStretch()

    def keyPressEvent(self, event):
        key = event.key()
        # noinspection PyUnresolvedReferences
        if event.modifiers() == QtCore.Qt.ControlModifier:

            # noinspection PyUnresolvedReferences
            if key == QtCore.Qt.Key_6:
                if self.slider_edges_distance_v8.isHidden():
                    self.slider_edges_distance_v8.show()
                    self.text_distance.show()
                    self.text_distance_2.show()
                    self.text_distance_3.show()

                else:
                    self.slider_edges_distance_v8.hide()
                    self.text_distance.hide()
                    self.text_distance_2.hide()
                    self.text_distance_3.hide()

                # return True
        return super(FliersTab, self).keyPressEvent(event)

    # v8

    def _ui_settings_ffv8(self):
        self.settings_ffv8_vbox = QtWidgets.QVBoxLayout()
        self.setSettingsFFv8.setLayout(self.settings_ffv8_vbox)

        self.settings_ffv8_vbox.addStretch()

        min_group_box = 240

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(20, 5, 20, 5)
        self.settings_ffv8_vbox.addLayout(vbox)

        self._ui_settings_params_checks_ffv8(vbox=vbox, min_group_box=min_group_box)
        self._ui_settings_params_filters_ffv8(vbox=vbox, min_group_box=min_group_box)
        self._ui_settings_params_debug_ffv8(vbox=vbox, min_group_box=min_group_box)
        self._ui_settings_params_lock_ffv8(vbox=vbox)

        self.settings_ffv8_vbox.addStretch()

    def _ui_settings_params_checks_ffv8(self, vbox: QtWidgets.QVBoxLayout, min_group_box: int) -> None:
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        set_checks_ffv8 = QtWidgets.QGroupBox("Checks")
        set_checks_ffv8.setMinimumWidth(min_group_box)
        hbox.addWidget(set_checks_ffv8)
        chk_vbox = QtWidgets.QVBoxLayout()
        set_checks_ffv8.setLayout(chk_vbox)

        # set height
        height_hbox = QtWidgets.QHBoxLayout()
        chk_vbox.addLayout(height_hbox)
        self.set_height_label_ffv8 = QtWidgets.QLabel("Force flier heights to")
        self.set_height_label_ffv8.setDisabled(True)
        height_hbox.addWidget(self.set_height_label_ffv8)
        self.set_height_label_ffv8.setFixedHeight(GuiSettings.single_line_height())
        self.set_height_ffv8 = QtWidgets.QLineEdit("")
        height_hbox.addWidget(self.set_height_ffv8)
        self.set_height_ffv8.setFixedHeight(GuiSettings.single_line_height())
        # self.set_height_ffv8.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.set_height_ffv8))
        # noinspection PyUnresolvedReferences
        self.set_height_ffv8.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_height_ffv8.setReadOnly(False)
        self.set_height_ffv8.setFont(GuiSettings.console_font())
        self.set_height_ffv8.setFixedWidth(60)
        self.set_height_ffv8.setDisabled(True)
        self.set_height_label2_ffv8 = QtWidgets.QLabel("meters")
        self.set_height_label2_ffv8.setDisabled(True)
        height_hbox.addWidget(self.set_height_label2_ffv8)
        height_hbox.addStretch()

        chk_vbox.addSpacing(6)

        self.set_check_laplacian_ffv8 = QtWidgets.QCheckBox("#1: Laplacian Operator")
        self.set_check_laplacian_ffv8.setDisabled(True)
        self.set_check_laplacian_ffv8.setChecked(self.settings.value("survey/ff8_laplacian", 0) == 1)
        chk_vbox.addWidget(self.set_check_laplacian_ffv8)

        self.set_check_curv_ffv8 = QtWidgets.QCheckBox("#2: Gaussian Curvature")
        self.set_check_curv_ffv8.setDisabled(True)
        self.set_check_curv_ffv8.setChecked(self.settings.value("survey/ff8_gaussian", 1) == 1)
        chk_vbox.addWidget(self.set_check_curv_ffv8)

        self.set_check_adjacent_ffv8 = QtWidgets.QCheckBox("#3: Adjacent Cells")
        self.set_check_adjacent_ffv8.setDisabled(True)
        self.set_check_adjacent_ffv8.setChecked(self.settings.value("survey/ff8_adjacent", 1) == 1)
        chk_vbox.addWidget(self.set_check_adjacent_ffv8)

        self.set_check_slivers_ffv8 = QtWidgets.QCheckBox("#4: Edge Slivers")
        self.set_check_slivers_ffv8.setDisabled(True)
        self.set_check_slivers_ffv8.setChecked(self.settings.value("survey/ff8_slivers", 1) == 1)
        chk_vbox.addWidget(self.set_check_slivers_ffv8)

        self.set_check_isolated_ffv8 = QtWidgets.QCheckBox("#5: Isolated Nodes")
        self.set_check_isolated_ffv8.setDisabled(True)
        self.set_check_isolated_ffv8.setChecked(self.settings.value("survey/ff8_orphans", 0) == 1)
        chk_vbox.addWidget(self.set_check_isolated_ffv8)

        self.set_check_edges_ffv8 = QtWidgets.QCheckBox("#6: Noisy Edges")
        self.set_check_edges_ffv8.setDisabled(True)
        self.set_check_edges_ffv8.setChecked(self.settings.value("survey/ff8_edges", 0) == 1)
        self.set_check_edges_ffv8.stateChanged.connect(self.click_set_6)
        chk_vbox.addWidget(self.set_check_edges_ffv8)

        slider_pct_gbox = QtWidgets.QGridLayout()
        chk_vbox.addLayout(slider_pct_gbox)

        # labels
        text_sz = 36
        text_label = QtWidgets.QLabel("")
        slider_pct_gbox.addWidget(text_label, 0, 0, 1, 1)

        self.text_pct_90 = QtWidgets.QLabel("90")
        self.text_pct_90.setFixedWidth(text_sz)
        self.text_pct_90.setAlignment(QtCore.Qt.AlignLeft)
        self.text_pct_90.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        self.text_pct_90.setDisabled(True)
        slider_pct_gbox.addWidget(self.text_pct_90, 0, 1, 1, 1)
        self.text_pct_100 = QtWidgets.QLabel("100")
        self.text_pct_100.setFixedWidth(text_sz)
        self.text_pct_100.setAlignment(QtCore.Qt.AlignLeft)
        self.text_pct_100.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        self.text_pct_100.setDisabled(True)
        slider_pct_gbox.addWidget(self.text_pct_100, 0, 2, 1, 1)
        self.text_pct_125 = QtWidgets.QLabel("125")
        self.text_pct_125.setFixedWidth(text_sz)
        self.text_pct_125.setAlignment(QtCore.Qt.AlignCenter)
        self.text_pct_125.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        self.text_pct_125.setDisabled(True)
        slider_pct_gbox.addWidget(self.text_pct_125, 0, 3, 1, 1)
        self.text_pct_150 = QtWidgets.QLabel("150")
        self.text_pct_150.setFixedWidth(text_sz)
        self.text_pct_150.setAlignment(QtCore.Qt.AlignRight)
        self.text_pct_150.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        self.text_pct_150.setDisabled(True)
        slider_pct_gbox.addWidget(self.text_pct_150, 0, 4, 1, 1)
        self.text_pct_200 = QtWidgets.QLabel("200")
        self.text_pct_200.setFixedWidth(text_sz)
        self.text_pct_200.setAlignment(QtCore.Qt.AlignRight)
        self.text_pct_200.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        self.text_pct_200.setDisabled(True)
        slider_pct_gbox.addWidget(self.text_pct_200, 0, 5, 1, 1)

        self.text_pct = QtWidgets.QLabel("Pct. TVU")
        self.text_pct.setDisabled(True)
        slider_pct_gbox.addWidget(self.text_pct, 1, 0, 1, 1)

        self.slider_edges_pct_tvu_v8 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_edges_pct_tvu_v8.setRange(1, 5)
        self.slider_edges_pct_tvu_v8.setSingleStep(1)
        self.slider_edges_pct_tvu_v8.setValue(2)
        self.slider_edges_pct_tvu_v8.setTickInterval(1)
        self.slider_edges_pct_tvu_v8.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider_edges_pct_tvu_v8.setDisabled(True)
        slider_pct_gbox.addWidget(self.slider_edges_pct_tvu_v8, 1, 1, 1, 5)

        slider_distance_gbox = QtWidgets.QGridLayout()
        chk_vbox.addLayout(slider_distance_gbox)

        # labels
        text_sz = 36
        text_label = QtWidgets.QLabel("")
        slider_distance_gbox.addWidget(text_label, 0, 0, 1, 1)

        self.text_distance_2 = QtWidgets.QLabel("2")
        self.text_distance_2.setFixedWidth(text_sz)
        self.text_distance_2.setAlignment(QtCore.Qt.AlignLeft)
        self.text_distance_2.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        self.text_distance_2.setDisabled(True)
        self.text_distance_2.setHidden(True)
        slider_distance_gbox.addWidget(self.text_distance_2, 0, 1, 1, 4)
        self.text_distance_3 = QtWidgets.QLabel("3")
        self.text_distance_3.setFixedWidth(text_sz)
        self.text_distance_3.setAlignment(QtCore.Qt.AlignRight)
        self.text_distance_3.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        self.text_distance_3.setDisabled(True)
        self.text_distance_3.setHidden(True)
        slider_distance_gbox.addWidget(self.text_distance_3, 0, 5, 1, 1)

        self.text_distance = QtWidgets.QLabel("Distance")
        self.text_distance.setHidden(True)
        self.text_distance.setDisabled(True)
        slider_distance_gbox.addWidget(self.text_distance, 1, 0, 1, 1)

        self.slider_edges_distance_v8 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_edges_distance_v8.setRange(2, 3)
        self.slider_edges_distance_v8.setSingleStep(1)
        self.slider_edges_distance_v8.setValue(3)
        self.slider_edges_distance_v8.setTickInterval(1)
        self.slider_edges_distance_v8.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider_edges_distance_v8.setDisabled(True)
        self.slider_edges_distance_v8.setHidden(True)
        slider_distance_gbox.addWidget(self.slider_edges_distance_v8, 1, 1, 1, 5)

        hbox.addStretch()

    def click_set_6(self):
        enable = self.set_check_edges_ffv8.isChecked()
        self.slider_edges_distance_v8.setEnabled(enable)
        self.text_pct.setEnabled(enable)
        self.text_pct_90.setEnabled(enable)
        self.text_pct_100.setEnabled(enable)
        self.text_pct_125.setEnabled(enable)
        self.text_pct_150.setEnabled(enable)
        self.text_pct_200.setEnabled(enable)
        self.slider_edges_pct_tvu_v8.setEnabled(enable)

        self.text_distance.setEnabled(enable)
        self.text_distance_2.setEnabled(enable)
        self.text_distance_3.setEnabled(enable)
        self.slider_edges_distance_v8.setEnabled(enable)

    def _ui_settings_params_filters_ffv8(self, vbox: QtWidgets.QVBoxLayout, min_group_box: int) -> None:
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        set_filters_ffv8 = QtWidgets.QGroupBox("Filters")
        set_filters_ffv8.setMinimumWidth(min_group_box)
        hbox.addWidget(set_filters_ffv8)
        flt_vbox = QtWidgets.QVBoxLayout()
        set_filters_ffv8.setLayout(flt_vbox)

        # set distance
        distance_hbox = QtWidgets.QHBoxLayout()
        flt_vbox.addLayout(distance_hbox)
        self.set_distance_label_ffv8 = QtWidgets.QLabel("Distance <=")
        self.set_distance_label_ffv8.setDisabled(True)
        distance_hbox.addWidget(self.set_distance_label_ffv8)
        self.set_distance_label_ffv8.setFixedHeight(GuiSettings.single_line_height())
        self.set_distance_ffv8 = QtWidgets.QLineEdit("")
        distance_hbox.addWidget(self.set_distance_ffv8)
        self.set_distance_ffv8.setFixedHeight(GuiSettings.single_line_height())
        # self.set_distance_ffv8.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.set_distance_ffv8))
        # noinspection PyUnresolvedReferences
        self.set_distance_ffv8.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_distance_ffv8.setReadOnly(False)
        self.set_distance_ffv8.setFont(GuiSettings.console_font())
        self.set_distance_ffv8.setFixedWidth(60)
        self.set_distance_ffv8.setText("%.1f" % FindFliersV8.default_filter_distance)
        self.set_distance_ffv8.setDisabled(True)
        self.set_distance_label2_ffv8 = QtWidgets.QLabel("nodes")
        self.set_distance_label2_ffv8.setDisabled(True)
        distance_hbox.addWidget(self.set_distance_label2_ffv8)
        distance_hbox.addStretch()

        # set delta_z
        delta_z_hbox = QtWidgets.QHBoxLayout()
        flt_vbox.addLayout(delta_z_hbox)
        self.set_delta_z_label_ffv8 = QtWidgets.QLabel("Delta Z <=")
        self.set_delta_z_label_ffv8.setDisabled(True)
        delta_z_hbox.addWidget(self.set_delta_z_label_ffv8)
        self.set_delta_z_label_ffv8.setFixedHeight(GuiSettings.single_line_height())
        self.set_delta_z_ffv8 = QtWidgets.QLineEdit("")
        delta_z_hbox.addWidget(self.set_delta_z_ffv8)
        self.set_delta_z_ffv8.setFixedHeight(GuiSettings.single_line_height())
        # self.set_delta_z_ffv8.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.set_delta_z_ffv8))
        # noinspection PyUnresolvedReferences
        self.set_delta_z_ffv8.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_delta_z_ffv8.setReadOnly(False)
        self.set_delta_z_ffv8.setFont(GuiSettings.console_font())
        self.set_delta_z_ffv8.setFixedWidth(60)
        self.set_delta_z_ffv8.setText("%.2f" % FindFliersV8.default_filter_delta_z)
        self.set_delta_z_ffv8.setDisabled(True)
        self.set_delta_z_label2_ffv8 = QtWidgets.QLabel("meters")
        self.set_delta_z_label2_ffv8.setDisabled(True)
        delta_z_hbox.addWidget(self.set_delta_z_label2_ffv8)
        delta_z_hbox.addStretch()

        flt_vbox.addSpacing(6)

        self.set_filter_fff_ffv8 = QtWidgets.QCheckBox("#1: Use Features from S57 File")
        self.set_filter_fff_ffv8.setDisabled(True)
        self.set_filter_fff_ffv8.setChecked(self.settings.value("survey/ff8_fff", 0) == 1)
        flt_vbox.addWidget(self.set_filter_fff_ffv8)

        self.set_filter_designated_ffv8 = QtWidgets.QCheckBox("#2: Use Designated (SR BAG only)")
        self.set_filter_designated_ffv8.setDisabled(True)
        self.set_filter_designated_ffv8.setChecked(self.settings.value("survey/ff8_designated", 0) == 1)
        flt_vbox.addWidget(self.set_filter_designated_ffv8)

        hbox.addStretch()

    def _ui_settings_params_debug_ffv8(self, vbox: QtWidgets.QVBoxLayout, min_group_box: int) -> None:
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.debugFFv8 = QtWidgets.QGroupBox("Debug")
        self.debugFFv8.hide()
        self.debugFFv8.setMinimumWidth(min_group_box)
        hbox.addWidget(self.debugFFv8)
        dbg_vbox = QtWidgets.QVBoxLayout()
        self.debugFFv8.setLayout(dbg_vbox)

        self.check_export_proxies_ffv8 = QtWidgets.QCheckBox("Export threshold proxies")
        self.check_export_proxies_ffv8.setDisabled(True)
        self.check_export_proxies_ffv8.setChecked(False)
        dbg_vbox.addWidget(self.check_export_proxies_ffv8)

        self.check_export_heights_ffv8 = QtWidgets.QCheckBox("Export height thresholds")
        self.check_export_heights_ffv8.setDisabled(True)
        self.check_export_heights_ffv8.setChecked(False)
        dbg_vbox.addWidget(self.check_export_heights_ffv8)

        self.check_export_curvatures_ffv8 = QtWidgets.QCheckBox("Export curvature thresholds")
        self.check_export_curvatures_ffv8.setDisabled(True)
        self.check_export_curvatures_ffv8.setChecked(False)
        dbg_vbox.addWidget(self.check_export_curvatures_ffv8)

        hbox.addStretch()

    def _ui_settings_params_lock_ffv8(self, vbox: QtWidgets.QVBoxLayout) -> None:
        vbox.addSpacing(6)

        lock_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(lock_hbox)
        lock_hbox.addStretch()
        self.editable_v8 = QtWidgets.QPushButton()
        self.editable_v8.setIconSize(QtCore.QSize(24, 24))
        self.editable_v8.setFixedHeight(28)
        edit_icon = QtGui.QIcon()
        edit_icon.addFile(os.path.join(self.parent_win.media, 'lock.png'), state=QtGui.QIcon.Off)
        edit_icon.addFile(os.path.join(self.parent_win.media, 'unlock.png'), state=QtGui.QIcon.On)
        self.editable_v8.setIcon(edit_icon)
        self.editable_v8.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.editable_v8.clicked.connect(self.on_editable_v8)
        self.editable_v8.setToolTip("Unlock editing for parameters")
        lock_hbox.addWidget(self.editable_v8)
        lock_hbox.addStretch()

        vbox.addStretch()

    def on_editable_v8(self):
        logger.debug("editable_v8: %s" % self.editable_v8.isChecked())
        if self.editable_v8.isChecked():
            msg = "Do you really want to change the settings?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Find Fliers v8 settings", msg,
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                self.editable_v8.setChecked(False)
                return

            self.set_height_label_ffv8.setEnabled(True)
            self.set_height_label2_ffv8.setEnabled(True)
            self.set_height_ffv8.setEnabled(True)

            self.set_check_laplacian_ffv8.setEnabled(True)
            self.set_check_curv_ffv8.setEnabled(True)
            self.set_check_adjacent_ffv8.setEnabled(True)
            self.set_check_slivers_ffv8.setEnabled(True)
            self.set_check_isolated_ffv8.setEnabled(True)
            self.set_check_edges_ffv8.setEnabled(True)

            if self.set_check_edges_ffv8.isChecked():
                self.slider_edges_distance_v8.setEnabled(True)
                self.text_pct.setEnabled(True)
                self.text_pct_90.setEnabled(True)
                self.text_pct_100.setEnabled(True)
                self.text_pct_125.setEnabled(True)
                self.text_pct_150.setEnabled(True)
                self.text_pct_200.setEnabled(True)
                self.slider_edges_pct_tvu_v8.setEnabled(True)

                self.text_distance.setEnabled(True)
                self.text_distance_2.setEnabled(True)
                self.text_distance_3.setEnabled(True)
                self.slider_edges_distance_v8.setEnabled(True)

            self.set_distance_label_ffv8.setEnabled(True)
            self.set_distance_label2_ffv8.setEnabled(True)
            self.set_distance_ffv8.setEnabled(True)

            self.set_delta_z_label_ffv8.setEnabled(True)
            self.set_delta_z_label2_ffv8.setEnabled(True)
            self.set_delta_z_ffv8.setEnabled(True)

            self.set_filter_fff_ffv8.setEnabled(True)
            self.set_filter_designated_ffv8.setEnabled(True)

            self.check_export_proxies_ffv8.setEnabled(True)
            self.check_export_heights_ffv8.setEnabled(True)
            self.check_export_curvatures_ffv8.setEnabled(True)

        else:
            self.set_height_label_ffv8.setDisabled(True)
            self.set_height_label2_ffv8.setDisabled(True)
            self.set_height_ffv8.setDisabled(True)

            self.set_check_laplacian_ffv8.setDisabled(True)
            self.set_check_curv_ffv8.setDisabled(True)
            self.set_check_adjacent_ffv8.setDisabled(True)
            self.set_check_slivers_ffv8.setDisabled(True)
            self.set_check_isolated_ffv8.setDisabled(True)
            self.set_check_edges_ffv8.setDisabled(True)

            self.slider_edges_distance_v8.setDisabled(True)
            self.text_pct.setDisabled(True)
            self.text_pct_90.setDisabled(True)
            self.text_pct_100.setDisabled(True)
            self.text_pct_125.setDisabled(True)
            self.text_pct_150.setDisabled(True)
            self.text_pct_200.setDisabled(True)
            self.slider_edges_pct_tvu_v8.setDisabled(True)

            self.text_distance.setDisabled(True)
            self.text_distance_2.setDisabled(True)
            self.text_distance_3.setDisabled(True)
            self.slider_edges_distance_v8.setDisabled(True)

            self.set_distance_label_ffv8.setDisabled(True)
            self.set_distance_label2_ffv8.setDisabled(True)
            self.set_distance_ffv8.setDisabled(True)

            self.set_delta_z_label_ffv8.setDisabled(True)
            self.set_delta_z_label2_ffv8.setDisabled(True)
            self.set_delta_z_ffv8.setDisabled(True)

            self.set_filter_fff_ffv8.setDisabled(True)
            self.set_filter_designated_ffv8.setDisabled(True)

            self.check_export_proxies_ffv8.setDisabled(True)
            self.check_export_heights_ffv8.setDisabled(True)
            self.check_export_curvatures_ffv8.setDisabled(True)

    def _parse_filter_distance_ffv8(self) -> float:
        str_distance = self.set_distance_ffv8.text()

        if str_distance == "":
            logger.warning("using default filter distance: %s" % FindFliersV8.default_filter_distance)
            self.set_distance_ffv8.setText("%.1f" % FindFliersV8.default_filter_distance)
            return FindFliersV8.default_filter_distance

        try:

            distance = float(str_distance)

        except ValueError:

            msg = "Unable to parse the distance value: %s.\n" \
                  "Defaulting to %s!" % (str_distance, FindFliersV8.default_filter_distance)
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
            self.set_distance_ffv8.setText("%.1f" % FindFliersV8.default_filter_distance)
            return FindFliersV8.default_filter_distance

        logger.info("filter distance: %s" % (distance,))
        return distance

    def _parse_filter_delta_z_ffv8(self) -> float:
        str_delta_z = self.set_delta_z_ffv8.text()

        if str_delta_z == "":
            logger.warning("using default filter delta_z: %s" % FindFliersV8.default_filter_delta_z)
            self.set_delta_z_ffv8.setText("%.2f" % FindFliersV8.default_filter_delta_z)
            return FindFliersV8.default_filter_delta_z

        try:

            delta_z = float(str_delta_z)

        except ValueError:

            msg = "Unable to parse the delta_z value: %s.\n" \
                  "Defaulting to %s!" % (str_delta_z, FindFliersV8.default_filter_delta_z)
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
            self.set_delta_z_ffv8.setText("%.2f" % FindFliersV8.default_filter_delta_z)
            return FindFliersV8.default_filter_delta_z

        logger.info("filter delta_z: %s" % (delta_z,))
        return delta_z

    def _ui_execute_ffv8(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeFFv8.setLayout(vbox)

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
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Find fliers v8")
        button.setToolTip('Find fliers in the loaded surfaces')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_find_fliers_v8)
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
        button.clicked.connect(self.click_open_manual_v8)

        hbox.addStretch()

        vbox.addStretch()

    @classmethod
    def click_open_manual_v8(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_detect_fliers.html")

    # ####### find fliers #######

    def click_find_fliers_v8(self):
        """trigger the find fliers v8"""
        self._click_find_fliers(8)

    def _click_find_fliers(self, version):
        """abstract the find fliers calling mechanism"""

        # sanity checks
        # - version
        if not isinstance(version, int):
            raise RuntimeError("passed invalid type for version: %s" % type(version))
        if version not in [8, ]:
            raise RuntimeError("passed invalid Find Fliers version: %s" % version)
        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.prj.grid_list) == 0:
            raise RuntimeError("the grid list is empty")

        height_mode = "auto"
        if version == 8:
            if self.set_height_ffv8.text() != "":
                height_mode = self.set_height_ffv8.text()
        else:
            raise RuntimeError("unknown Find Fliers' version: %s" % version)

        ck = "c"
        if self.set_check_laplacian_ffv8.isChecked():
            ck += "1"
        if self.set_check_curv_ffv8.isChecked():
            ck += "2"
        if self.set_check_adjacent_ffv8.isChecked():
            ck += "3"
        if self.set_check_slivers_ffv8.isChecked():
            ck += "4"
        if self.set_check_isolated_ffv8.isChecked():
            ck += "5"
        if self.set_check_edges_ffv8.isChecked():
            ck += "6"
        ck += "f"
        if self.set_filter_fff_ffv8.isChecked():
            ck += "1"
        if self.set_filter_designated_ffv8.isChecked():
            ck += "2"

        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="survey_find_fliers_%d_fh_%s_%s"
                                                                                 % (version, height_mode, ck)))

        self._parse_user_height(version=version)

        grid_list = self.prj.grid_list

        # pre checks

        if version == 8:

            if self.set_filter_fff_ffv8.isChecked():

                if len(self.prj.s57_list) == 0:
                    msg = "The 'Use Features from S57 File' option is active, but no S57 files have been selected!\n" \
                          "\n" \
                          "Do you want to continue with the analysis?"
                    # noinspection PyCallByClass
                    ret = QtWidgets.QMessageBox.warning(self, "Find Fliers v8 filters", msg,
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if ret == QtWidgets.QMessageBox.No:
                        return

            if self.set_filter_designated_ffv8.isChecked():
                at_least_one_bag = False
                for grid_file in grid_list:
                    if os.path.splitext(grid_file)[-1] == ".bag":
                        at_least_one_bag = True

                if not at_least_one_bag:
                    msg = "The 'Use Designated (SR BAG only)' option is active, " \
                          "but no BAG files have been selected!\n\n" \
                          "Do you want to continue with the analysis?"
                    # noinspection PyCallByClass
                    ret = QtWidgets.QMessageBox.warning(self, "Find Fliers v8 filters", msg,
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if ret == QtWidgets.QMessageBox.No:
                        return

        # for each file in the project grid list
        msg = "Potential fliers per input:\n"
        opened_folders = list()
        for i, grid_file in enumerate(grid_list):

            # we want to be sure that the label is based on the name of the new file input
            self.prj.clear_survey_label()

            # switcher between different versions of find fliers
            if version in [8, ]:
                self._find_fliers(grid_file=grid_file, version=version, idx=(i + 1), total=len(grid_list))

            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Find Fliers v%s" % version)

            # export the fliers
            saved = self._export_fliers()
            msg += "- %s: %d\n" % (self.prj.cur_grid_basename, self.prj.number_of_fliers())

            # open the output folder (if not already open)
            if saved:

                if self.prj.fliers_output_folder not in opened_folders:
                    self.prj.open_fliers_output_folder()
                    opened_folders.append(self.prj.fliers_output_folder)

            self.prj.close_cur_grid()

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Find fliers v%d" % version, msg, QtWidgets.QMessageBox.Ok)

    def _parse_user_height(self, version):

        # check for user input as flier height
        if version == 8:
            str_height = self.set_height_ffv8.text()

            if str_height == "":
                self.float_height_ffv8 = None

            else:

                fh_tokens = str_height.split(',')
                logger.debug("tokens: %d" % len(fh_tokens))

                # - case of just 1 value
                if len(fh_tokens) == 1:

                    try:

                        self.float_height_ffv8 = float(str_height)

                    except ValueError:

                        msg = "Unable to parse the height value: %s.\n" \
                              "Defaulting to internal estimation!" % str_height
                        # noinspection PyCallByClass
                        QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
                        self.float_height_ffv8 = None

                # - case of 1 input for each grid
                elif len(fh_tokens) == len(self.prj.grid_list):

                    self.set_height_ffv8.clear()

                    try:

                        self.float_height_ffv8 = list()
                        for fh_token in fh_tokens:

                            value = float(fh_token)
                            if value <= 0:
                                raise ValueError("invalid float input")
                            self.float_height_ffv8.append(value)

                    except ValueError:

                        msg = "Unable to parse all the height values: %s.\n" \
                              "Defaulting to internal estimation!" % str_height
                        # noinspection PyCallByClass
                        QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
                        self.float_height_ffv8 = None

                # - case of different number of input than the number of grids (this is an ERROR!)
                else:

                    self.set_height_ffv8.clear()
                    self.float_height_ffv8 = None

                    msg = "Invalid set of flier heights parsing \"%s\":\n" \
                          " - input values: %s\n" \
                          " - loaded grids: %s\n\n" \
                          "Defaulting to internal estimation!\n" \
                          % (str_height, len(fh_tokens), len(self.prj.grid_list))
                    # noinspection PyCallByClass
                    QtWidgets.QMessageBox.critical(self, "Error", msg, QtWidgets.QMessageBox.Ok)
                    logger.debug('find fliers v%d: invalid set of fliers height: %s != %s'
                                 % (version, len(fh_tokens), len(self.prj.grid_list)))

            logger.info("flier height: %s" % (self.float_height_ffv8,))

        else:  # this case should be never reached after the sanity checks
            raise RuntimeError("unknown Find Fliers' version: %s" % version)

    def _find_fliers(self, grid_file, version, idx, total):
        """ find fliers in the loaded surface using passed height parameter """

        # GUI initializes, then passes progress bar

        logger.debug('find fliers v%d ...' % version)

        self.prj.progress.start(title="Find Fliers v%d" % version,
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

        self.prj.progress.update(value=5, text="Find Fliers v%d [%d/%d]" % (version, idx, total))

        settings = QtCore.QSettings()
        try:
            if version == 8:

                height = None
                if type(self.float_height_ffv8) is float:
                    height = self.float_height_ffv8
                if type(self.float_height_ffv8) is list:
                    height = self.float_height_ffv8[idx - 1]

                save_proxies = self.check_export_proxies_ffv8.isChecked()
                save_heights = self.check_export_heights_ffv8.isChecked()
                save_curvatures = self.check_export_curvatures_ffv8.isChecked()

                if self.set_check_laplacian_ffv8.isChecked():
                    settings.setValue("survey/ff8_laplacian", 1)
                else:
                    settings.setValue("survey/ff8_laplacian", 0)
                if self.set_check_curv_ffv8.isChecked():
                    settings.setValue("survey/ff8_gaussian", 1)
                else:
                    settings.setValue("survey/ff8_gaussian", 0)
                if self.set_check_adjacent_ffv8.isChecked():
                    settings.setValue("survey/ff8_adjacent", 1)
                else:
                    settings.setValue("survey/ff8_adjacent", 0)
                if self.set_check_slivers_ffv8.isChecked():
                    settings.setValue("survey/ff8_slivers", 1)
                else:
                    settings.setValue("survey/ff8_slivers", 0)
                if self.set_check_isolated_ffv8.isChecked():
                    settings.setValue("survey/ff8_orphans", 1)
                else:
                    settings.setValue("survey/ff8_orphans", 0)
                if self.set_check_edges_ffv8.isChecked():
                    settings.setValue("survey/ff8_edges", 1)
                else:
                    settings.setValue("survey/ff8_edges", 0)
                if self.set_filter_fff_ffv8.isChecked():
                    settings.setValue("survey/ff8_fff", 1)
                else:
                    settings.setValue("survey/ff8_fff", 0)
                if self.set_filter_designated_ffv8.isChecked():
                    settings.setValue("survey/ff8_designated", 1)
                else:
                    settings.setValue("survey/ff8_designated", 0)

                edges_distance = self.slider_edges_distance_v8.value()
                edges_pct_int = self.slider_edges_pct_tvu_v8.value()
                edges_pct = 0.9
                if edges_pct_int == 2:
                    edges_pct = 1.0
                elif edges_pct_int == 3:
                    edges_pct = 1.25
                elif edges_pct_int == 4:
                    edges_pct = 1.5
                elif edges_pct_int == 5:
                    edges_pct = 2.0

                self.prj.find_fliers_v8(height=height,
                                        check_laplacian=self.set_check_laplacian_ffv8.isChecked(),
                                        check_curv=self.set_check_curv_ffv8.isChecked(),
                                        check_adjacent=self.set_check_adjacent_ffv8.isChecked(),
                                        check_slivers=self.set_check_slivers_ffv8.isChecked(),
                                        check_isolated=self.set_check_isolated_ffv8.isChecked(),
                                        check_edges=self.set_check_edges_ffv8.isChecked(),
                                        edges_distance=edges_distance, edges_pct_tvu=edges_pct,
                                        filter_fff=self.set_filter_fff_ffv8.isChecked(),
                                        filter_designated=self.set_filter_designated_ffv8.isChecked(),
                                        export_proxies=save_proxies,
                                        export_heights=save_heights,
                                        export_curvatures=save_curvatures,
                                        progress_bar=self.prj.progress
                                        )

                if self.set_filter_fff_ffv8.isChecked() or self.set_filter_designated_ffv8.isChecked():
                    self.prj.close_cur_grid()
                    self.prj.set_cur_grid(path=grid_file)
                    self.prj.open_to_read_cur_grid()

                    distance = self._parse_filter_distance_ffv8()
                    delta_z = self._parse_filter_delta_z_ffv8()
                    self.prj.find_fliers_v8_apply_filters(distance=distance, delta_z=delta_z)

        except MemoryError:
            err_str = "While finding fliers, there was a memory error. Try to close unused applications!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", err_str, QtWidgets.QMessageBox.Ok)
            self.prj.progress.end()
            return

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While finding fliers, %s" % e, QtWidgets.QMessageBox.Ok)
            self.prj.progress.end()
            return

        self.prj.progress.end()

    def _export_fliers(self):
        """ export potential fliers """
        logger.debug('exporting fliers ...')
        saved = self.prj.save_fliers()
        logger.debug('exporting fliers: done')
        return saved

    def grids_changed(self):
        self.set_height_ffv8.clear()
