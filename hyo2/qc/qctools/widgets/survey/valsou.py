import locale
import logging
import os

from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper
from hyo2.qc.common import lib_info
from hyo2.qc.qctools.gui_settings import GuiSettings

logger = logging.getLogger(__name__)


class ValsouTab(QtWidgets.QMainWindow):

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
        
        self.text_set_scale_v7 = None
        self.set_scale_fsv7 = None
        self.set_include_laser_fsv7 = None
        self.toggle_specs_v7 = None
        self.set_overlap_fsv7 = None
        self.toggle_overlap_v7 = None
        self.toggle_mode_v7 = None

        # - VALSOU check v7
        self.valsouCheckV7 = QtWidgets.QGroupBox("VALSOU check v7")
        self.valsouCheckV7.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.valsouCheckV7)
        vcv7_hbox = QtWidgets.QHBoxLayout()
        self.valsouCheckV7.setLayout(vcv7_hbox)
        # -- parameters
        self.setParametersVCv7 = QtWidgets.QGroupBox("Parameters")
        self.setParametersVCv7.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        vcv7_hbox.addWidget(self.setParametersVCv7)
        self._ui_parameters_vcv7()
        # -- execution
        self.executeVCv7 = QtWidgets.QGroupBox("Execution")
        self.executeVCv7.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        vcv7_hbox.addWidget(self.executeVCv7)
        self._ui_execute_vcv7()

        self.vbox.addStretch()

    # ------- v7 --------

    def _ui_parameters_vcv7(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersVCv7.setLayout(hbox)
        hbox.addStretch()

        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # specs
        text_2017 = QtWidgets.QLabel("2017")
        text_2017.setAlignment(QtCore.Qt.AlignCenter)
        text_2017.setFixedWidth(160)
        label_hbox.addWidget(text_2017)
        # # spacing
        # label_hbox.addSpacing(20)
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
        # specs
        self.toggle_specs_v7 = QtWidgets.QDial()
        self.toggle_specs_v7.setNotchesVisible(True)
        self.toggle_specs_v7.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_specs_v7.setRange(2016, 2018)
        self.toggle_specs_v7.setValue(2018)
        self.toggle_specs_v7.setFixedSize(QtCore.QSize(40, 40))
        self.toggle_specs_v7.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_specs_v7)
        # noinspection PyUnresolvedReferences
        self.toggle_specs_v7.valueChanged.connect(self.changed_specs)
        # spacing
        toggle_hbox.addSpacing(120)
        # mode
        self.toggle_mode_v7 = QtWidgets.QDial()
        self.toggle_mode_v7.setNotchesVisible(True)
        self.toggle_mode_v7.setWrapping(False)
        self.toggle_mode_v7.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_mode_v7.setRange(0, 1)
        self.toggle_mode_v7.setSliderPosition(0)
        self.toggle_mode_v7.setFixedSize(QtCore.QSize(40, 40))
        self.toggle_mode_v7.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_mode_v7)
        # stretch
        toggle_hbox.addStretch()

        label2_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label2_hbox)
        # stretch
        label2_hbox.addStretch()
        # specs
        label2_hbox.addSpacing(40)
        text_2016 = QtWidgets.QLabel("2016")
        text_2016.setAlignment(QtCore.Qt.AlignCenter)
        text_2016.setFixedWidth(40)
        label2_hbox.addWidget(text_2016)
        text_2018 = QtWidgets.QLabel("2018+")
        text_2018.setAlignment(QtCore.Qt.AlignCenter)
        text_2018.setFixedWidth(70)
        label2_hbox.addWidget(text_2018)
        # spacing
        label2_hbox.addSpacing(10)
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

        # survey scale
        scale_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(scale_hbox)
        scale_hbox.addStretch()
        self.text_set_scale_v7 = QtWidgets.QLabel("Survey scale:   1 :")
        scale_hbox.addWidget(self.text_set_scale_v7)
        self.text_set_scale_v7.setFixedHeight(GuiSettings.single_line_height())
        self.text_set_scale_v7.setMinimumWidth(90)
        self.set_scale_fsv7 = QtWidgets.QLineEdit("")
        scale_hbox.addWidget(self.set_scale_fsv7)
        self.set_scale_fsv7.setFixedHeight(GuiSettings.single_line_height())
        self.set_scale_fsv7.setValidator(QtGui.QIntValidator(1, 99999999, self.set_scale_fsv7))
        self.set_scale_fsv7.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_scale_fsv7.setReadOnly(False)
        self.set_scale_fsv7.setFont(GuiSettings.console_font())
        self.set_scale_fsv7.setStyleSheet(GuiSettings.stylesheet_console_fg_color())
        self.set_scale_fsv7.setFixedWidth(60)
        self.text_set_scale_v7.setDisabled(True)
        self.set_scale_fsv7.setDisabled(True)
        scale_hbox.addStretch()

        vbox.addSpacing(10)

        options_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(options_hbox)
        options_hbox.addStretch()

        text_set_overlap = QtWidgets.QLabel("Deconflict across grids")
        options_hbox.addWidget(text_set_overlap)
        text_set_overlap.setFixedHeight(GuiSettings.single_line_height())
        text_set_overlap.setMinimumWidth(80)
        # text_set_overlap.setStyleSheet("QLabel { color :  rgba(200, 0, 0, 200); }")
        self.set_overlap_fsv7 = QtWidgets.QCheckBox(self)
        self.set_overlap_fsv7.setToolTip("Test the flagged features across all the input grids")
        options_hbox.addWidget(self.set_overlap_fsv7)
        self.set_overlap_fsv7.setChecked(False)

        options_hbox.addSpacing(10)

        text_set_include_laser = QtWidgets.QLabel("Include TECSOU=laser")
        options_hbox.addWidget(text_set_include_laser)
        text_set_include_laser.setFixedHeight(GuiSettings.single_line_height())
        text_set_include_laser.setMinimumWidth(80)
        # text_set_neighborhood.setStyleSheet("QLabel { color :  rgba(200, 0, 0, 200); }")
        self.set_include_laser_fsv7 = QtWidgets.QCheckBox(self)
        self.set_include_laser_fsv7.setToolTip("Uncheck to skip features with TECSOU=laser")
        options_hbox.addWidget(self.set_include_laser_fsv7)
        self.set_include_laser_fsv7.setChecked(True)

        options_hbox.addStretch()

        vbox.addStretch()

        hbox.addStretch()

    def _ui_execute_vcv7(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeVCv7.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() + 16)
        button.setText("VALSOU check v7")
        button.setToolTip('Check VALSOU values against surface')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_valsou_check_v7)

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

    def changed_specs(self):
        logger.debug("user changed specs: %s" % self.toggle_specs_v7.value())
        specs_version = self.toggle_specs_v7.value()
        if specs_version in [2016, 2017]:
            self.text_set_scale_v7.setEnabled(True)
            self.set_scale_fsv7.setEnabled(True)
            logger.debug("enabling")
        else:
            self.text_set_scale_v7.setDisabled(True)
            self.set_scale_fsv7.setDisabled(True)
            logger.debug("disabling")

    def click_valsou_check_v7(self):
        specs_version = self.toggle_specs_v7.value()
        if specs_version in [2016, 2017]:
            # checks for Survey Scale
            if self.set_scale_fsv7.text() == "":
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.critical(self, "Settings", "First set the survey scale!",
                                               QtWidgets.QMessageBox.Ok)
                return
            locale.setlocale(locale.LC_ALL, "")
            scale = locale.atoi(self.set_scale_fsv7.text())
            if scale == 0:
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.critical(self, "Settings", "Invalid survey scale: %d" %
                                               scale, QtWidgets.QMessageBox.Ok)
                return
        self._click_valsou_check(7)

    # ------- commond methods --------

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_valsou_checks.html")

    def _click_valsou_check(self, version):
        """abstract the feature scan calling mechanism"""

        # sanity checks
        # - version
        if not isinstance(version, int):
            raise RuntimeError("passed invalid type for version: %s" % type(version))
        if version not in [7, ]:
            raise RuntimeError("passed invalid VALSOU check version: %s" % version)
        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.prj.s57_list) == 0:
            raise RuntimeError("the S57 list is empty")
        if len(self.prj.grid_list) == 0:
            raise RuntimeError("the grid list is empty")

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
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.critical(self, "Error", "While reading s57 file, %s" % e,
                                               QtWidgets.QMessageBox.Ok)
                self.parent_win.progress.setValue(100)
                return

            for j, grid_file in enumerate(grid_list):

                idx = (j + 1)*(i*len(s57_list))
                total = len(s57_list)*len(grid_list)

                # switcher between different versions of find fliers
                if version in [7, ]:
                    self._valsou_check(grid_file=grid_file, version=version, idx=idx, total=total)
                else:  # this case should be never reached after the sanity checks
                    raise RuntimeError("unknown VALSOU check version: %s" % version)

                logger.info("survey label: %s" % self.prj.survey_label)

                # de-confliction
                if version == 7 and self.set_overlap_fsv7.isChecked():
                    self.parent_win.progress.start(title="VALSOU check v.%d" % version,
                                                   text="Deconflicting [%d/%d]" % (idx, total),
                                                   init_value=90)
                    self.prj.valsou_check_deconflict_v7()
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

    def _valsou_check(self, grid_file, version, idx, total):
        """ VALSOU check for the loaded s57 features and grid"""

        # GUI takes care of progress bar

        logger.debug('VALSOU check v%d ...' % version)

        self.parent_win.progress.start(title="VALSOU check v.%d" % version,
                                       text="Data loading [%d/%d]" % (idx, total),
                                       init_value=10)

        try:
            self.prj.open_grid(path=grid_file)

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While reading grid file, %s" % e, QtWidgets.QMessageBox.Ok)
            self.parent_win.progress.end()
            return

        self.parent_win.progress.update(value=20, text="VALSOU check v%d [%d/%d]" % (version, idx, total))

        try:
            if version == 7:

                specs_version = self.toggle_specs_v7.value()
                if specs_version in [2016, 2017]:
                    locale.setlocale(locale.LC_ALL, "")
                    scale = locale.atoi(self.set_scale_fsv7.text())
                else:
                    scale = 10000

                with_laser = self.set_include_laser_fsv7.isChecked()
                is_target_detection = self.toggle_mode_v7.value() == 1

                if specs_version == 2016:
                    self.prj.valsou_check_v7(specs_version="2016", survey_scale=scale, with_laser=with_laser,
                                             is_target_detection=is_target_detection)

                elif specs_version == 2017:
                    self.prj.valsou_check_v7(specs_version="2017", survey_scale=scale, with_laser=with_laser,
                                             is_target_detection=is_target_detection)

                elif specs_version == 2018:
                    self.prj.valsou_check_v7(specs_version="2018", survey_scale=scale, with_laser=with_laser,
                                             is_target_detection=is_target_detection)

                else:
                    raise RuntimeError("unknown specs version: %s" % specs_version)

            else:
                RuntimeError("unknown VALSOU check version: %s" % version)

        except Exception as e:
            # noinspection PyCallByClass
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
