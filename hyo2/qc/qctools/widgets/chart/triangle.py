from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging

logger = logging.getLogger(__name__)

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common.helper import Helper
from hyo2.qc.chart.triangle.base_triangle import sounding_units


class TriangleTab(QtWidgets.QMainWindow):
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

        # - Triangle Rule v2
        self.bagTruncateV2 = QtWidgets.QGroupBox("Triangle Rule v2")
        self.bagTruncateV2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.bagTruncateV2)
        btv2_hbox = QtWidgets.QHBoxLayout()
        self.bagTruncateV2.setLayout(btv2_hbox)
        # -- parameters
        self.setParametersBTv2 = QtWidgets.QGroupBox("Parameters")
        self.setParametersBTv2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        btv2_hbox.addWidget(self.setParametersBTv2)
        self.toggle_units_v2 = None
        self.set_use_valsous_v2 = None
        # -- variables
        self.use_valsous_v2 = True
        self.use_depcnt_v2 = True
        self.detect_deeps_v2 = False
        self._ui_parameters_btv2()
        # -- execution
        self.executeBTv2 = QtWidgets.QGroupBox("Execution")
        self.executeBTv2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        btv2_hbox.addWidget(self.executeBTv2)
        self._ui_execute_btv2()

        self.vbox.addStretch()

    def _ui_parameters_btv2(self):
        # - top
        vbox = QtWidgets.QVBoxLayout()
        self.setParametersBTv2.setLayout(vbox)
        vbox.addStretch()

        flag_text_length = 160

        # -- flag valsou
        flag_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(flag_hbox)
        flag_hbox.addStretch()
        text_set_valsous = QtWidgets.QLabel("Use VALSOU features: ")
        flag_hbox.addWidget(text_set_valsous)
        text_set_valsous.setFixedHeight(GuiSettings.single_line_height())
        text_set_valsous.setMinimumWidth(flag_text_length)
        self.set_use_valsous_v2 = QtWidgets.QCheckBox(self)
        flag_hbox.addWidget(self.set_use_valsous_v2)
        self.set_use_valsous_v2.setChecked(self.use_valsous_v2)
        flag_hbox.addStretch()

        # -- flag depcnt
        flag_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(flag_hbox)
        flag_hbox.addStretch()
        text_set_depcnt = QtWidgets.QLabel("Use DEPCNT features: ")
        flag_hbox.addWidget(text_set_depcnt)
        text_set_depcnt.setFixedHeight(GuiSettings.single_line_height())
        text_set_depcnt.setMinimumWidth(flag_text_length)
        self.set_use_depcnt_v2 = QtWidgets.QCheckBox(self)
        flag_hbox.addWidget(self.set_use_depcnt_v2)
        self.set_use_depcnt_v2.setChecked(self.use_depcnt_v2)
        flag_hbox.addStretch()

        # -- calculate deeps
        flag_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(flag_hbox)
        flag_hbox.addStretch()
        text_detect_deeps = QtWidgets.QLabel("Detect deeps: ")
        flag_hbox.addWidget(text_detect_deeps)
        text_detect_deeps.setFixedHeight(GuiSettings.single_line_height())
        text_detect_deeps.setMinimumWidth(flag_text_length)
        self.set_detect_deeps_v2 = QtWidgets.QCheckBox(self)
        flag_hbox.addWidget(self.set_detect_deeps_v2)
        self.set_detect_deeps_v2.setChecked(self.detect_deeps_v2)
        flag_hbox.addStretch()

        # meter multiplier
        meter_multi_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(meter_multi_hbox)
        meter_multi_hbox.addStretch()
        self.text_set_meter_th_v2 = QtWidgets.QLabel("Force threshold (m): ")
        meter_multi_hbox.addWidget(self.text_set_meter_th_v2)
        self.text_set_meter_th_v2.setFixedHeight(GuiSettings.single_line_height())
        self.text_set_meter_th_v2.setMinimumWidth(120)
        self.set_meter_th_v2 = QtWidgets.QLineEdit("")
        meter_multi_hbox.addWidget(self.set_meter_th_v2)
        self.set_meter_th_v2.setFixedHeight(GuiSettings.single_line_height())
        self.set_meter_th_v2.setValidator(QtGui.QDoubleValidator(0.01, 9999.9, 2, self.set_meter_th_v2))
        self.set_meter_th_v2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_meter_th_v2.setReadOnly(False)
        self.set_meter_th_v2.setFont(GuiSettings.console_font())
        self.set_meter_th_v2.setFixedWidth(60)
        self.set_meter_th_v2.setText("1.0")
        self.disable_meter_th()
        meter_multi_hbox.addStretch()

        # - top
        vbox.addSpacing(10)

        # -- Chart Sounding Unit
        csu_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(csu_hbox)
        # stretch
        csu_hbox.addStretch()
        csu_hbox.addSpacing(40)

        # -- left label
        # label
        text_field = QtWidgets.QLabel("Sounding Units: ")
        text_field.setAlignment(QtCore.Qt.AlignVCenter)
        text_field.setFixedWidth(80)
        csu_hbox.addWidget(text_field)

        # -- toggle area
        toggle_vbox = QtWidgets.QVBoxLayout()
        csu_hbox.addLayout(toggle_vbox)

        # --- knob 1 label
        label1_hbox = QtWidgets.QHBoxLayout()
        toggle_vbox.addLayout(label1_hbox)
        # stretch
        label1_hbox.addStretch()
        # feet label
        text_field = QtWidgets.QLabel("Meters")
        text_field.setAlignment(QtCore.Qt.AlignCenter)
        text_field.setFixedWidth(40)
        label1_hbox.addWidget(text_field)
        # stretch
        label1_hbox.addStretch()

        # --- knob
        knob_hbox = QtWidgets.QHBoxLayout()
        toggle_vbox.addLayout(knob_hbox)
        # stretch
        knob_hbox.addStretch()
        # units
        self.toggle_units_v2 = QtWidgets.QDial()
        self.toggle_units_v2.setNotchesVisible(True)
        self.toggle_units_v2.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_units_v2.setRange(0, 2)
        self.toggle_units_v2.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_units_v2.setInvertedAppearance(False)
        # noinspection PyUnresolvedReferences
        self.toggle_units_v2.valueChanged.connect(self.unit_changed)
        knob_hbox.addWidget(self.toggle_units_v2)
        # stretch
        knob_hbox.addStretch()

        # --- knob 2 label
        label2_hbox = QtWidgets.QHBoxLayout()
        toggle_vbox.addLayout(label2_hbox)
        # stretch
        label2_hbox.addStretch()
        # feet label
        text_field = QtWidgets.QLabel("Feet")
        text_field.setAlignment(QtCore.Qt.AlignCenter)
        text_field.setFixedWidth(40)
        label2_hbox.addWidget(text_field)
        # fathoms label
        text_office = QtWidgets.QLabel("Fathoms")
        text_office.setAlignment(QtCore.Qt.AlignCenter)
        text_office.setFixedWidth(45)
        label2_hbox.addWidget(text_office)
        # stretch
        label2_hbox.addStretch()

        # stretch
        csu_hbox.addStretch()

        # - top
        vbox.addStretch()

    def _ui_execute_btv2(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeBTv2.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Triangle Rule v2")
        button.setToolTip('Apply the Triangle Rule')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_triangle_rule)

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

    def enable_meter_th(self):
        self.set_meter_th_v2.setEnabled(True)
        self.text_set_meter_th_v2.setEnabled(True)

    def disable_meter_th(self):
        self.set_meter_th_v2.setDisabled(True)
        self.text_set_meter_th_v2.setDisabled(True)

    def unit_changed(self):
        logger.debug("unit changed")
        if self.toggle_units_v2.value() == 1:
            self.enable_meter_th()
        else:
            self.disable_meter_th()

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_chart_triangle_rule.html")

    def click_triangle_rule(self):

        # library takes care of progress bar

        version = 2
        self.parent_win.change_info_url(Helper.web_url(suffix="chart_triangle_rule_%d" % version))

        if self.toggle_units_v2.value() == 0:
            sounding_unit = sounding_units['feet']
        elif self.toggle_units_v2.value() == 1:
            sounding_unit = sounding_units['meters']
        else:
            sounding_unit = sounding_units['fathoms']

        self.prj.triangle_rule(version=version,
                               use_valsous=self.set_use_valsous_v2.isChecked(),
                               use_depcnts=self.set_use_depcnt_v2.isChecked(),
                               detect_deeps=self.set_detect_deeps_v2.isChecked(),
                               sounding_unit=sounding_unit,
                               meter_th=float(self.set_meter_th_v2.text()))

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Triangle Rule v%d" % version,
                                          self.prj.triangle_msg, QtWidgets.QMessageBox.Ok)
