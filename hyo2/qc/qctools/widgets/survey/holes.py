from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.grids import _gappy
import os
import traceback
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common.helper import Helper

logger = logging.getLogger(__name__)


class HolesTab(QtWidgets.QMainWindow):
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

        # - holiday finder v4
        self.holeFinderV4 = QtWidgets.QGroupBox("Holiday finder v4")
        self.vbox.addWidget(self.holeFinderV4)
        hfv4_hbox = QtWidgets.QHBoxLayout()
        self.holeFinderV4.setLayout(hfv4_hbox)
        # -- settings
        self.setSettingsHFv4 = QtWidgets.QGroupBox("Settings")
        hfv4_hbox.addWidget(self.setSettingsHFv4)
        self.locker_v4 = None
        self.settings_hfv4_vbox = None
        self.paramsHFv4 = None
        self.debugHFv4 = None
        self.toggle_mode_v4 = None
        self.upper_limit_v4 = None
        self.upper_limit_label_v4 = None
        self.slider_hole_sizer_v4 = None
        self.slider_pct_min_res_v4 = None
        self.slider_pct_min_res_label_v4 = None
        # self.slider_strategy_v4 = None
        # self.slider_ref_depth_v4 = None
        self.slider_visual_debug_v4 = None
        self.slider_export_ascii_v4 = None
        self._ui_settings_hfv4()
        # -- execution
        self.executeHFv4 = QtWidgets.QGroupBox("Execution")
        hfv4_hbox.addWidget(self.executeHFv4)
        self._ui_execute_hfv4()

        self.vbox.addStretch()

    def keyPressEvent(self, event):
        key = event.key()
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if key == QtCore.Qt.Key_D:

                if self.debugHFv4.isHidden():
                    self.debugHFv4.show()
                else:
                    self.debugHFv4.hide()

                return True
        return super(HolesTab, self).keyPressEvent(event)

    # ########### v4 ##########

    def _ui_settings_hfv4(self):

        hbox = QtWidgets.QHBoxLayout()
        self.setSettingsHFv4.setLayout(hbox)
        hbox.addStretch()

        self.settings_hfv4_vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(self.settings_hfv4_vbox)

        self.settings_hfv4_vbox.addStretch()

        self._ui_settings_mode_hfv4()

        self.settings_hfv4_vbox.addStretch()

        self._ui_settings_params_hfv4()

        self.settings_hfv4_vbox.addStretch()

        self._ui_settings_debug_hfv4()

        self.settings_hfv4_vbox.addStretch()

        hbox.addStretch()

    def _ui_settings_mode_hfv4(self):
        label_hbox = QtWidgets.QHBoxLayout()
        self.settings_hfv4_vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # mode
        text_all = QtWidgets.QLabel("All holes")
        text_all.setAlignment(QtCore.Qt.AlignCenter)
        text_all.setFixedWidth(85)
        label_hbox.addWidget(text_all)
        # stretch
        label_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        self.settings_hfv4_vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # mode
        self.toggle_mode_v4 = QtWidgets.QDial()
        self.toggle_mode_v4.setNotchesVisible(True)
        self.toggle_mode_v4.setWrapping(False)
        self.toggle_mode_v4.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_mode_v4.setRange(0, 2)
        self.toggle_mode_v4.setSliderPosition(2)
        self.toggle_mode_v4.setFixedSize(QtCore.QSize(40, 40))
        self.toggle_mode_v4.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_mode_v4)
        toggle_hbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        self.settings_hfv4_vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # mode
        text_obj = QtWidgets.QLabel("Object detection")
        text_obj.setAlignment(QtCore.Qt.AlignCenter)
        text_obj.setFixedWidth(85)
        label_hbox.addWidget(text_obj)
        text_cov = QtWidgets.QLabel("Full coverage")
        text_cov.setAlignment(QtCore.Qt.AlignCenter)
        text_cov.setFixedWidth(85)
        label_hbox.addWidget(text_cov)
        # stretch
        label_hbox.addStretch()

    def _ui_settings_params_hfv4(self):
        self.paramsHFv4 = QtWidgets.QGroupBox("Parameters")
        self.settings_hfv4_vbox.addWidget(self.paramsHFv4)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(30, 10, 30, 10)
        self.paramsHFv4.setLayout(vbox)

        # slider holiday area limit

        slider_label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(slider_label_hbox)
        # stretch
        slider_label_hbox.addStretch()
        # mode
        self.upper_limit_label_v4 = QtWidgets.QLabel("Upper holiday area limit (as multiple of minimum holiday size):")
        self.upper_limit_label_v4.setAlignment(QtCore.Qt.AlignCenter)
        self.upper_limit_label_v4.setDisabled(True)
        slider_label_hbox.addWidget(self.upper_limit_label_v4)
        # stretch
        slider_label_hbox.addStretch()

        slider_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(slider_hbox)
        # stretch
        slider_hbox.addStretch()

        slider_gbox = QtWidgets.QGridLayout()
        slider_hbox.addLayout(slider_gbox)

        # labels
        text_sz = 36
        text_value = QtWidgets.QLabel("100")
        text_value.setFixedWidth(text_sz + 8)
        text_value.setAlignment(QtCore.Qt.AlignLeft)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(text_value, 0, 0, 1, 1)
        text_value = QtWidgets.QLabel("400")
        text_value.setFixedWidth(text_sz)
        text_value.setAlignment(QtCore.Qt.AlignCenter)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(text_value, 0, 1, 1, 1)
        text_value = QtWidgets.QLabel("1000")
        text_value.setFixedWidth(text_sz + 20)
        text_value.setAlignment(QtCore.Qt.AlignCenter)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(text_value, 0, 2, 1, 1)
        text_value = QtWidgets.QLabel("4000")
        text_value.setFixedWidth(text_sz)
        text_value.setAlignment(QtCore.Qt.AlignCenter)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(text_value, 0, 3, 1, 1)
        text_value = QtWidgets.QLabel("unlimited")
        text_value.setFixedWidth(text_sz + 8)
        text_value.setAlignment(QtCore.Qt.AlignRight)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(text_value, 0, 4, 1, 1)

        # slider
        self.upper_limit_v4 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.upper_limit_v4.setRange(1, 5)
        self.upper_limit_v4.setSingleStep(1)
        self.upper_limit_v4.setValue(5)
        self.upper_limit_v4.setTickInterval(1)
        self.upper_limit_v4.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.upper_limit_v4.setDisabled(True)
        slider_gbox.addWidget(self.upper_limit_v4, 1, 0, 1, 5)

        # stretch
        slider_hbox.addStretch()

        vbox.addSpacing(6)

        # slider minimum resolution

        slider_label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(slider_label_hbox)
        # stretch
        slider_label_hbox.addStretch()
        # mode
        self.slider_pct_min_res_label_v4 = QtWidgets.QLabel(
            "Resolution (as percentage of minimum resolution among tiles):")
        self.slider_pct_min_res_label_v4.setAlignment(QtCore.Qt.AlignCenter)
        self.slider_pct_min_res_label_v4.setDisabled(True)
        self.slider_pct_min_res_label_v4.setHidden(True)
        slider_label_hbox.addWidget(self.slider_pct_min_res_label_v4)
        # stretch
        slider_label_hbox.addStretch()

        slider_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(slider_hbox)
        # stretch
        slider_hbox.addStretch()

        slider_gbox = QtWidgets.QGridLayout()
        slider_hbox.addLayout(slider_gbox)

        # labels
        text_sz = 36
        text_value = QtWidgets.QLabel("50%")
        text_value.setFixedWidth(text_sz)
        text_value.setAlignment(QtCore.Qt.AlignLeft)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        text_value.setHidden(True)
        slider_gbox.addWidget(text_value, 0, 0, 1, 1)
        text_value = QtWidgets.QLabel("66%")
        text_value.setFixedWidth(text_sz)
        text_value.setAlignment(QtCore.Qt.AlignCenter)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        text_value.setHidden(True)
        slider_gbox.addWidget(text_value, 0, 1, 1, 1)
        text_value = QtWidgets.QLabel("100%")
        text_value.setFixedWidth(text_sz)
        text_value.setAlignment(QtCore.Qt.AlignRight)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        text_value.setHidden(True)
        slider_gbox.addWidget(text_value, 0, 2, 1, 1)

        # slider
        self.slider_pct_min_res_v4 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_pct_min_res_v4.setRange(1, 3)
        self.slider_pct_min_res_v4.setSingleStep(1)
        self.slider_pct_min_res_v4.setValue(3)
        self.slider_pct_min_res_v4.setTickInterval(1)
        self.slider_pct_min_res_v4.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider_pct_min_res_v4.setDisabled(True)
        self.slider_pct_min_res_v4.setHidden(True)
        slider_gbox.addWidget(self.slider_pct_min_res_v4, 1, 0, 1, 3)

        # stretch
        slider_hbox.addStretch()

        # # slider sizer
        #
        # slider_label_hbox = QtWidgets.QHBoxLayout()
        # vbox.addLayout(slider_label_hbox)
        # # stretch
        # slider_label_hbox.addStretch()
        # # mode
        # text_obj = QtWidgets.QLabel(
        # "Sizer rule (from coarsest allowed resolution resolution to holiday size in nodes):")
        # text_obj.setAlignment(QtCore.Qt.AlignCenter)
        # slider_label_hbox.addWidget(text_obj)
        # # stretch
        # slider_label_hbox.addStretch()
        #
        # slider_hbox = QtWidgets.QHBoxLayout()
        # vbox.addLayout(slider_hbox)
        # # stretch
        # slider_hbox.addStretch()
        #
        # slider_gbox = QtWidgets.QGridLayout()
        # slider_hbox.addLayout(slider_gbox)
        #
        # self.slider_hole_sizer_v4 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # self.slider_hole_sizer_v4.setRange(1, 3)
        # self.slider_hole_sizer_v4.setSingleStep(1)
        # self.slider_hole_sizer_v4.setValue(3)
        # self.slider_hole_sizer_v4.setTickInterval(1)
        # self.slider_hole_sizer_v4.setTickPosition(QtWidgets.QSlider.TicksBelow)
        # slider_gbox.addWidget(self.slider_hole_sizer_v4, 0, 0, 1, 3)
        # # labels
        # text_sz = 36
        # text_value = QtWidgets.QLabel("2x")
        # text_value.setFixedWidth(text_sz + 8)
        # text_value.setAlignment(QtCore.Qt.AlignLeft)
        # text_value.setStyleSheet("QLabel { color: rgb(155, 155, 155); }")
        # slider_gbox.addWidget(text_value, 1, 0, 1, 1)
        # text_value = QtWidgets.QLabel("2x+1")
        # text_value.setFixedWidth(text_sz)
        # text_value.setAlignment(QtCore.Qt.AlignCenter)
        # text_value.setStyleSheet("QLabel { color: rgb(155, 155, 155); }")
        # slider_gbox.addWidget(text_value, 1, 1, 1, 1)
        # text_value = QtWidgets.QLabel("3x")
        # text_value.setFixedWidth(text_sz + 8)
        # text_value.setAlignment(QtCore.Qt.AlignRight)
        # text_value.setStyleSheet("QLabel { color: rgb(155, 155, 155); }")
        # slider_gbox.addWidget(text_value, 1, 2, 1, 1)
        #
        # # stretch
        # slider_hbox.addStretch()

        # slider ref depth

        # slider_label_hbox = QtWidgets.QHBoxLayout()
        # vbox.addLayout(slider_label_hbox)
        # # stretch
        # slider_label_hbox.addStretch()
        # # strategy
        # text_obj = QtWidgets.QLabel("Analytic approach:")
        # text_obj.setAlignment(QtCore.Qt.AlignCenter)
        # slider_label_hbox.addWidget(text_obj)
        # # stretch
        # slider_label_hbox.addStretch()
        # # mode
        # text_obj = QtWidgets.QLabel("Median depth from:")
        # text_obj.setAlignment(QtCore.Qt.AlignCenter)
        # slider_label_hbox.addWidget(text_obj)
        # # stretch
        # slider_label_hbox.addStretch()
        #
        # slider_hbox = QtWidgets.QHBoxLayout()
        # vbox.addLayout(slider_hbox)
        # # stretch
        # slider_hbox.addStretch()
        #
        # slider_gbox = QtWidgets.QGridLayout()
        # slider_hbox.addLayout(slider_gbox)
        #
        # self.slider_strategy_v4 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # self.slider_strategy_v4.setRange(0, 1)
        # self.slider_strategy_v4.setSingleStep(1)
        # self.slider_strategy_v4.setValue(0)
        # self.slider_strategy_v4.setTickInterval(1)
        # self.slider_strategy_v4.setTickPosition(QtWidgets.QSlider.TicksBelow)
        # slider_gbox.addWidget(self.slider_strategy_v4, 0, 0, 1, 2)
        #
        # # labels
        # text_sz = 48
        # text_value = QtWidgets.QLabel("Per-Tile")
        # text_value.setFixedWidth(text_sz + 8)
        # text_value.setAlignment(QtCore.Qt.AlignLeft)
        # text_value.setStyleSheet("QLabel { color: rgb(155, 155, 155); }")
        # slider_gbox.addWidget(text_value, 1, 0, 1, 1)
        # text_value = QtWidgets.QLabel("Brute Force")
        # text_value.setFixedWidth(text_sz + 8)
        # text_value.setAlignment(QtCore.Qt.AlignRight)
        # text_value.setStyleSheet("QLabel { color: rgb(155, 155, 155); }")
        # slider_gbox.addWidget(text_value, 1, 1, 1, 1)
        #
        # # stretch
        # slider_hbox.addStretch()
        #
        # slider_gbox = QtWidgets.QGridLayout()
        # slider_hbox.addLayout(slider_gbox)
        #
        # self.slider_ref_depth_v4 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # self.slider_ref_depth_v4.setRange(0, 1)
        # self.slider_ref_depth_v4.setSingleStep(1)
        # self.slider_ref_depth_v4.setValue(1)
        # self.slider_ref_depth_v4.setTickInterval(1)
        # self.slider_ref_depth_v4.setTickPosition(QtWidgets.QSlider.TicksBelow)
        # slider_gbox.addWidget(self.slider_ref_depth_v4, 0, 0, 1, 2)
        # # labels
        # text_sz = 48
        # text_value = QtWidgets.QLabel("Tile")
        # text_value.setFixedWidth(text_sz + 8)
        # text_value.setAlignment(QtCore.Qt.AlignLeft)
        # text_value.setStyleSheet("QLabel { color: rgb(155, 155, 155); }")
        # slider_gbox.addWidget(text_value, 1, 0, 1, 1)
        # text_value = QtWidgets.QLabel("Perimeter")
        # text_value.setFixedWidth(text_sz)
        # text_value.setAlignment(QtCore.Qt.AlignRight)
        # text_value.setStyleSheet("QLabel { color: rgb(155, 155, 155); }")
        # slider_gbox.addWidget(text_value, 1, 1, 1, 1)
        #
        # # stretch
        # slider_hbox.addStretch()

        # locker

        vbox.addSpacing(6)

        lock_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(lock_hbox)
        lock_hbox.addStretch()
        self.locker_v4 = QtWidgets.QPushButton()
        self.locker_v4.setIconSize(QtCore.QSize(24, 24))
        self.locker_v4.setFixedHeight(28)
        edit_icon = QtGui.QIcon()
        edit_icon.addFile(os.path.join(self.parent_win.media, 'lock.png'), state=QtGui.QIcon.Off)
        edit_icon.addFile(os.path.join(self.parent_win.media, 'unlock.png'), state=QtGui.QIcon.On)
        self.locker_v4.setIcon(edit_icon)
        self.locker_v4.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.locker_v4.clicked.connect(self.on_editable_v4)
        self.locker_v4.setToolTip("Unlock editing for parameters")
        lock_hbox.addWidget(self.locker_v4)
        lock_hbox.addStretch()

    def _ui_settings_debug_hfv4(self):
        self.debugHFv4 = QtWidgets.QGroupBox("Debug")
        self.debugHFv4.setHidden(True)
        self.settings_hfv4_vbox.addWidget(self.debugHFv4)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(10, 5, 5, 10)
        self.debugHFv4.setLayout(vbox)

        # slider visual debug

        # - labels

        slider_label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(slider_label_hbox)

        # stretch
        slider_label_hbox.addStretch()

        # mode
        text_obj = QtWidgets.QLabel("Visual debug mode:")
        text_obj.setAlignment(QtCore.Qt.AlignCenter)
        slider_label_hbox.addWidget(text_obj)

        slider_label_hbox.addSpacing(15)

        # export ascii
        text_obj = QtWidgets.QLabel("Save oversampled grid:")
        text_obj.setAlignment(QtCore.Qt.AlignCenter)
        slider_label_hbox.addWidget(text_obj)

        # stretch
        slider_label_hbox.addStretch()

        # - values

        slider_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(slider_hbox)
        # stretch
        slider_hbox.addStretch()

        # visual debug

        slider_gbox = QtWidgets.QGridLayout()
        slider_hbox.addLayout(slider_gbox)

        # labels
        text_sz = 36
        text_value = QtWidgets.QLabel("On")
        text_value.setFixedWidth(text_sz + 8)
        text_value.setAlignment(QtCore.Qt.AlignLeft)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(text_value, 0, 0, 1, 1)
        text_value = QtWidgets.QLabel("Off")
        text_value.setFixedWidth(text_sz)
        text_value.setAlignment(QtCore.Qt.AlignCenter)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(text_value, 0, 1, 1, 1)
        # slider
        self.slider_visual_debug_v4 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_visual_debug_v4.setRange(1, 2)
        self.slider_visual_debug_v4.setSingleStep(1)
        self.slider_visual_debug_v4.setValue(2)
        self.slider_visual_debug_v4.setTickInterval(1)
        self.slider_visual_debug_v4.setTickPosition(QtWidgets.QSlider.TicksBelow)
        slider_gbox.addWidget(self.slider_visual_debug_v4, 1, 0, 1, 2)

        spacer = QtWidgets.QSpacerItem(1, 1)
        slider_gbox.addItem(spacer, 1, 2, 1, 1)

        slider_hbox.addSpacing(30)

        # ascii export

        slider_gbox = QtWidgets.QGridLayout()
        slider_hbox.addLayout(slider_gbox)

        # labels
        text_sz = 36
        text_value = QtWidgets.QLabel("On")
        text_value.setFixedWidth(text_sz + 8)
        text_value.setAlignment(QtCore.Qt.AlignLeft)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(text_value, 0, 0, 1, 1)
        text_value = QtWidgets.QLabel("Off")
        text_value.setFixedWidth(text_sz)
        text_value.setAlignment(QtCore.Qt.AlignCenter)
        text_value.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(text_value, 0, 1, 1, 1)
        # slider
        self.slider_export_ascii_v4 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_export_ascii_v4.setRange(1, 2)
        self.slider_export_ascii_v4.setSingleStep(1)
        self.slider_export_ascii_v4.setValue(2)
        self.slider_export_ascii_v4.setTickInterval(1)
        self.slider_export_ascii_v4.setTickPosition(QtWidgets.QSlider.TicksBelow)
        slider_gbox.addWidget(self.slider_export_ascii_v4, 1, 0, 1, 2)

        # stretch
        slider_hbox.addStretch()

    def on_editable_v4(self):
        logger.debug("editable_v4: %s" % self.locker_v4.isChecked())

        if self.locker_v4.isChecked():
            msg = "Do you really want to change the settings?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Holiday Finder v4 settings", msg,
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                self.locker_v4.setChecked(False)
                return

            self.upper_limit_v4.setEnabled(True)
            self.upper_limit_label_v4.setEnabled(True)

            self.slider_pct_min_res_v4.setEnabled(True)
            self.slider_pct_min_res_label_v4.setEnabled(True)

        else:

            self.upper_limit_v4.setDisabled(True)
            self.upper_limit_label_v4.setDisabled(True)

            self.slider_pct_min_res_v4.setDisabled(True)
            self.slider_pct_min_res_label_v4.setDisabled(True)

    def _ui_execute_hfv4(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeHFv4.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Find Holiday v4")
        button.setToolTip('Find holidays in the loaded surface using selected mode')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_find_holes_v4)

        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.single_line_height())
        icon_info = QtCore.QFileInfo(os.path.join(self.media, 'small_info.png'))
        button.setIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        button.setToolTip('Open the manual page')
        button.setStyleSheet(GuiSettings.stylesheet_info_button())
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_open_manual)

        hbox.addStretch()

    def click_find_holes_v4(self):
        """trigger the find holes v4"""
        self._click_find_holes(4)

    # ########### common ##########

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_detect_holidays.html")

    def _click_find_holes(self, version):
        """abstract the find holes calling mechanism"""

        # sanity checks
        # - version
        if not isinstance(version, int):
            raise RuntimeError("passed invalid type for version: %s" % type(version))
        if version not in [4, ]:
            raise RuntimeError("passed invalid Find Holiday version: %s" % version)
        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.prj.grid_list) == 0:
            raise RuntimeError("the grid list is empty")

        self.parent_win.change_info_url(Helper.web_url(suffix="survey_find_holes_%d" % version))

        # for each file in the project grid list
        msg = "Potential holidays per input:\n"
        grid_list = self.prj.grid_list
        opened_folders = list()
        for i, grid_file in enumerate(grid_list):

            # we want to be sure that the label is based on the name of the new file input
            self.prj.clear_survey_label()
            # switcher between different versions of find fliers
            if version == 4:
                self._find_holes(grid_file=grid_file, version=version, idx=(i + 1), total=len(grid_list))

            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Holiday Finder version: %s" % version)

            # export the fliers
            msg += "- %s: certain %d, possible %d\n" \
                   % (self.prj.cur_grid_basename, self.prj.number_of_certain_holes(),
                      self.prj.number_of_possible_holes())
            saved = self._export_holes()

            # open the output folder (if not already open)
            if saved:

                if self.prj.holes_output_folder not in opened_folders:
                    self.prj.open_holes_output_folder()
                    opened_folders.append(self.prj.holes_output_folder)

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Find holidays v%d" % version, msg, QtWidgets.QMessageBox.Ok)

    def _find_holes(self, grid_file, version, idx, total):
        """ find fliers in the loaded surface using passed height parameter """

        # GUI takes care of progress bar

        logger.debug('find holidays v%d ...' % version)

        self.parent_win.progress.start(title="Find holidays v.%d" % version,
                                       text="Data processing [%d/%d]" % (idx, total),
                                       init_value=0)

        try:
            if version == 4:

                algo_mode = self.toggle_mode_v4.value()
                # sizer_mode = self.slider_hole_sizer_v4.value()
                area_value = self.upper_limit_v4.value()
                pct_res_value = self.slider_pct_min_res_v4.value()
                debug_value = self.slider_visual_debug_v4.value()
                # ref_depth_value = self.slider_ref_depth_v4.value()
                # strategy_value = self.slider_strategy_v4.value()
                export_value = self.slider_export_ascii_v4.value()

                if pct_res_value == 1:
                    pct_value = 0.5
                elif pct_res_value == 2:
                    pct_value = 0.666
                else:
                    pct_value = 1.0

                max_size = 0
                if area_value == 1:
                    max_size = 100

                elif area_value == 2:
                    max_size = 400

                elif area_value == 3:
                    max_size = 1000

                elif area_value == 4:
                    max_size = 4000

                elif area_value == 5:
                    max_size = 0

                visual_debug = False
                if debug_value == 1:
                    visual_debug = True

                export_ascii = False
                if export_value == 1:
                    export_ascii = True

                # local_perimeter = False
                # if ref_depth_value == 1:
                local_perimeter = True

                # brute_force = False
                # if strategy_value == 1:
                brute_force = True

                if algo_mode == 0:
                    mode = "OBJECT_DETECTION"
                elif algo_mode == 1:
                    mode = "ALL_HOLES"
                elif algo_mode == 2:
                    mode = "FULL_COVERAGE"
                else:
                    raise RuntimeError("unknown mode: %s" % algo_mode)

                # if sizer_mode == 1:
                #     sizer = "TWO_TIMES"
                # elif sizer_mode == 2:
                #     sizer = "TWO_TIMES_PLUS_ONE_NODE"
                # elif sizer_mode == 3:
                sizer = "THREE_TIMES"

                # else:
                #     raise RuntimeError("unknown mode: %s" % algo_mode)

                class ProgressCallback(_gappy.ProgressCallback):

                    progress = self.parent_win.progress

                    def update(self, n, tot):

                        try:
                            self.progress.update((n / tot) * 100, restart=True)
                        except Exception as exc:
                            print(exc)

                    # noinspection PyMethodOverriding
                    def step_update(self, text, n, tot):

                        try:
                            self.progress.update((n / tot) * 100, text=text, restart=True)
                        except Exception as exc:
                            print(exc)

                cb = ProgressCallback()

                self.prj.find_holes_v4(path=grid_file, mode=mode, sizer=sizer, max_size=max_size, pct_min_res=pct_value,
                                       local_perimeter=local_perimeter, visual_debug=visual_debug,
                                       export_ascii=export_ascii, brute_force=brute_force, cb=cb)

        except Exception as e:
            traceback.print_exc()
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While finding fliers, this exception occurred:\n\n%s"
                                           % e, QtWidgets.QMessageBox.Ok)
            self.parent_win.progress.end()
            return

        self.parent_win.progress.end()

    def _export_holes(self):
        """ export potential holes """
        logger.debug('exporting holes ...')
        saved = self.prj.save_holes()
        logger.debug('exporting holes: done')
        return saved
