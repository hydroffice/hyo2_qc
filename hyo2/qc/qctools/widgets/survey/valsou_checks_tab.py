import locale
import logging
import os

from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper
from hyo2.qc.common import lib_info
from hyo2.qc.qctools.gui_settings import GuiSettings

logger = logging.getLogger(__name__)


class ValsouChecksTab(QtWidgets.QMainWindow):

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

        # v8 parameters

        self.text_set_scale_v8 = None
        self.set_scale_fsv8 = None
        self.set_include_laser_fsv8 = None
        self.set_overlap_fsv8 = None
        self.toggle_overlap_v8 = None
        self.toggle_mode_v8 = None

        # v8 widgets
        self.valsouCheckv8 = QtWidgets.QGroupBox("VALSOU Check v8")
        self.valsouCheckv8.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.valsouCheckv8)
        vcv8_hbox = QtWidgets.QHBoxLayout()
        self.valsouCheckv8.setLayout(vcv8_hbox)
        # -- parameters
        self.setParametersVCv8 = QtWidgets.QGroupBox("Parameters")
        self.setParametersVCv8.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        vcv8_hbox.addWidget(self.setParametersVCv8)
        self._ui_parameters_vcv8()
        # -- execution
        self.executeVCv8 = QtWidgets.QGroupBox("Execution")
        self.executeVCv8.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        vcv8_hbox.addWidget(self.executeVCv8)
        self._ui_execute_vcv8()

        self.vbox.addStretch()

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/stable/user_manual_survey_valsou_checks.html")

    # ------- v8 --------

    def _ui_parameters_vcv8(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersVCv8.setLayout(hbox)
        hbox.addStretch()

        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # specs
        empty = QtWidgets.QLabel("")
        empty.setAlignment(QtCore.Qt.AlignCenter)
        empty.setFixedWidth(160)
        label_hbox.addWidget(empty)
        # stretch
        label_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # mode
        self.toggle_mode_v8 = QtWidgets.QDial()
        self.toggle_mode_v8.setNotchesVisible(True)
        self.toggle_mode_v8.setWrapping(False)
        self.toggle_mode_v8.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_mode_v8.setRange(0, 1)
        self.toggle_mode_v8.setSliderPosition(0)
        self.toggle_mode_v8.setFixedSize(QtCore.QSize(40, 40))
        self.toggle_mode_v8.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_mode_v8)
        # stretch
        toggle_hbox.addStretch()

        label2_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label2_hbox)
        # stretch
        label2_hbox.addStretch()
        # mode
        text_obj = QtWidgets.QLabel("Full coverage")
        text_obj.setAlignment(QtCore.Qt.AlignCenter)
        text_obj.setFixedWidth(85)
        label2_hbox.addWidget(text_obj)
        text_cov = QtWidgets.QLabel("Object detection")
        text_cov.setAlignment(QtCore.Qt.AlignCenter)
        text_cov.setFixedWidth(85)
        label2_hbox.addWidget(text_cov)
        # stretch
        label2_hbox.addStretch()

        vbox.addSpacing(10)

        options_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(options_hbox)
        options_hbox.addStretch()

        text_set_overlap = QtWidgets.QLabel("Deconflict across grids")
        options_hbox.addWidget(text_set_overlap)
        text_set_overlap.setFixedHeight(GuiSettings.single_line_height())
        text_set_overlap.setMinimumWidth(80)
        # text_set_overlap.setStyleSheet("QLabel { color :  rgba(200, 0, 0, 200); }")
        self.set_overlap_fsv8 = QtWidgets.QCheckBox(self)
        self.set_overlap_fsv8.setToolTip("Test the flagged features across all the input grids")
        options_hbox.addWidget(self.set_overlap_fsv8)
        self.set_overlap_fsv8.setChecked(False)

        options_hbox.addSpacing(10)

        text_set_include_laser = QtWidgets.QLabel("Include TECSOU=laser")
        options_hbox.addWidget(text_set_include_laser)
        text_set_include_laser.setFixedHeight(GuiSettings.single_line_height())
        text_set_include_laser.setMinimumWidth(80)
        # text_set_neighborhood.setStyleSheet("QLabel { color :  rgba(200, 0, 0, 200); }")
        self.set_include_laser_fsv8 = QtWidgets.QCheckBox(self)
        self.set_include_laser_fsv8.setToolTip("Uncheck to skip features with TECSOU=laser")
        options_hbox.addWidget(self.set_include_laser_fsv8)
        self.set_include_laser_fsv8.setChecked(True)

        options_hbox.addStretch()

        vbox.addStretch()

        hbox.addStretch()

    def _ui_execute_vcv8(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeVCv8.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() + 16)
        button.setText("VALSOU check v8")
        button.setToolTip('Check VALSOU values against surface')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_valsou_check_v8)

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

    def click_valsou_check_v8(self):
        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.prj.s57_list) == 0:
            raise RuntimeError("the S57 list is empty")
        if len(self.prj.grid_list) == 0:
            raise RuntimeError("the grid list is empty")

        version = 8
        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="survey_valsou_check_%d" % version))

        # for each file in the project grid list
        msg = "Flagged features per input pair:\n"
        s57_list = self.prj.s57_list
        grid_list = self.prj.grid_list
        opened_folders = list()

        for i, s57_file in enumerate(s57_list):

            # print("s57: %s" % s57_file)
            # we want to be sure that the label is based on the name of the new file input
            self.prj.clear_survey_label()

            try:
                self.prj.read_feature_file(feature_path=s57_file)

            except Exception as e:
                # noinspection PyCallByClass,PyArgumentList
                QtWidgets.QMessageBox.critical(self, "Error", "While reading s57 file, %s" % e,
                                               QtWidgets.QMessageBox.Ok)
                self.parent_win.progress.setValue(100)
                return

            for j, grid_file in enumerate(grid_list):

                idx = (j + 1)*(i*len(s57_list))
                total = len(s57_list)*len(grid_list)

                self._valsou_check_v8(grid_file=grid_file, version=version, idx=idx, total=total)

                logger.info("survey label: %s" % self.prj.survey_label)

                # de-confliction
                if self.set_overlap_fsv8.isChecked():
                    self.parent_win.progress.start(title="VALSOU Check v.%d" % version,
                                                   text="Deconflicting [%d/%d]" % (idx, total),
                                                   init_value=90)
                    self.prj.valsou_check_deconflict()
                    self.parent_win.progress.end()

                # open the output folder (if not already open)
                if self._export_valsou_check():
                    if self.prj.valsou_output_folder not in opened_folders:
                        self.prj.open_valsou_output_folder()
                        opened_folders.append(self.prj.valsou_output_folder)

                if self.prj.valsou_out_of_bbox:
                    msg += "- %s VS. %s: %s\n" % (self.prj.cur_s57_basename, self.prj.cur_grid_basename,
                                                  "no overlap")
                else:
                    msg += "- %s VS. %s: %d\n" % (self.prj.cur_s57_basename, self.prj.cur_grid_basename,
                                                  self.prj.number_of_valsou_features())

                # close the grid file
                self.prj.close_cur_grid()

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "VALSOU check v%d" % version, msg, QtWidgets.QMessageBox.Ok)

    def _valsou_check_v8(self, grid_file, version, idx, total):
        """ VALSOU check for the loaded s57 features and grid"""

        # GUI takes care of progress bar

        logger.debug('VALSOU Check v%d ...' % version)

        self.parent_win.progress.start(title="VALSOU Check v.%d" % version,
                                       text="Data loading [%d/%d]" % (idx, total),
                                       init_value=10)

        try:
            self.prj.open_grid(path=grid_file)

        except Exception as e:
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Error", "While reading grid file, %s" % e, QtWidgets.QMessageBox.Ok)
            self.parent_win.progress.end()
            return

        self.parent_win.progress.update(value=20, text="VALSOU Check v%d [%d/%d]" % (version, idx, total))

        try:
            with_laser = self.set_include_laser_fsv8.isChecked()
            is_tgt_detect = self.toggle_mode_v8.value() == 1
            self.prj.valsou_check_v8(specs_version="2021", with_laser=with_laser, is_target_detection=is_tgt_detect)

        except Exception as e:
            # noinspection PyCallByClass, PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Error", "While VALSOU checking, %s" % e, QtWidgets.QMessageBox.Ok)
            self.parent_win.progress.end()
            return

        self.parent_win.progress.end()

    def _export_valsou_check(self):
        """ export VALSOU features """
        logger.debug('exporting flagged VALSOU features ...')
        saved_s57 = self.prj.save_valsou_features()
        logger.debug('exporting flagged VALSOU features: done')
        return saved_s57
