from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class GridQATab(QtWidgets.QMainWindow):
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

        # - grid qa v5
        self.gridQAV5 = QtWidgets.QGroupBox("Grid QA v5")
        self.vbox.addWidget(self.gridQAV5)
        gqv5_hbox = QtWidgets.QHBoxLayout()
        self.gridQAV5.setLayout(gqv5_hbox)
        # -- parameters
        self.setSettingsGQv5 = QtWidgets.QGroupBox("Settings")
        gqv5_hbox.addWidget(self.setSettingsGQv5)
        self.set_force_tvu_qc_gqv5 = None
        self.set_toggle_mode_gqv5 = None
        self.hist_depth_v5 = None
        self.hist_density_v5 = None
        self.hist_tvu_qc_v5 = None
        self.hist_pct_res_v5 = None
        self.depth_vs_density_v5 = None
        self.depth_vs_tvu_qc_v5 = None
        self._ui_settings_gqv5()
        # -- execution
        self.executeGQv5 = QtWidgets.QGroupBox("Execution")
        gqv5_hbox.addWidget(self.executeGQv5)
        self._ui_execute_gqv5()
        # -- variables
        self.toggle_mode_gqv5 = None
        self.force_tvu_qc_gqv5 = False

        self.vbox.addStretch()

    # v5

    def _ui_settings_gqv5(self):
        vbox = QtWidgets.QVBoxLayout()
        self.setSettingsGQv5.setLayout(vbox)

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        text_set_tvu_qc = QtWidgets.QLabel("Force TVU QC calculation")
        hbox.addWidget(text_set_tvu_qc)
        text_set_tvu_qc.setFixedHeight(GuiSettings.single_line_height())
        text_set_tvu_qc.setMinimumWidth(80)
        self.set_force_tvu_qc_gqv5 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.set_force_tvu_qc_gqv5)
        self.set_force_tvu_qc_gqv5.setChecked(True)
        hbox.addStretch()

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        # stretch
        hbox.addStretch()
        # mode
        self.set_toggle_mode_gqv5 = QtWidgets.QDial()
        self.set_toggle_mode_gqv5.setNotchesVisible(True)
        self.set_toggle_mode_gqv5.setWrapping(False)
        self.set_toggle_mode_gqv5.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.set_toggle_mode_gqv5.setRange(0, 1)
        self.set_toggle_mode_gqv5.setSliderPosition(1)
        self.set_toggle_mode_gqv5.setFixedSize(QtCore.QSize(40, 40))
        self.set_toggle_mode_gqv5.setInvertedAppearance(False)
        hbox.addWidget(self.set_toggle_mode_gqv5)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        # stretch
        hbox.addStretch()
        # mode
        text_obj = QtWidgets.QLabel("Object detection")
        text_obj.setAlignment(QtCore.Qt.AlignCenter)
        text_obj.setFixedWidth(85)
        hbox.addWidget(text_obj)
        text_cov = QtWidgets.QLabel("Full coverage")
        text_cov.setAlignment(QtCore.Qt.AlignCenter)
        text_cov.setFixedWidth(85)
        hbox.addWidget(text_cov)
        # stretch
        hbox.addStretch()

        vbox.addSpacing(9)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        # histograms
        text_hist = QtWidgets.QLabel("<i>Histograms</i>")
        hbox.addWidget(text_hist)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        # histograms: depth
        text_hist_depth = QtWidgets.QLabel("depth:")
        hbox.addWidget(text_hist_depth)
        text_hist_depth.setFixedHeight(GuiSettings.single_line_height())
        self.hist_depth_v5 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.hist_depth_v5)
        self.hist_depth_v5.setChecked(True)
        # histograms: density
        text_hist_density = QtWidgets.QLabel(" density:")
        hbox.addWidget(text_hist_density)
        text_hist_density.setFixedHeight(GuiSettings.single_line_height())
        self.hist_density_v5 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.hist_density_v5)
        self.hist_density_v5.setChecked(True)
        # histograms: tvu qc
        text_hist_tvu_qc = QtWidgets.QLabel(" TVU QC:")
        hbox.addWidget(text_hist_tvu_qc)
        text_hist_tvu_qc.setFixedHeight(GuiSettings.single_line_height())
        self.hist_tvu_qc_v5 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.hist_tvu_qc_v5)
        self.hist_tvu_qc_v5.setChecked(True)
        # histograms: pct res
        text_hist_pct_res = QtWidgets.QLabel(" % resolution:")
        hbox.addWidget(text_hist_pct_res)
        text_hist_pct_res.setFixedHeight(GuiSettings.single_line_height())
        self.hist_pct_res_v5 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.hist_pct_res_v5)
        self.hist_pct_res_v5.setChecked(True)
        hbox.addStretch()

        vbox.addSpacing(9)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        # plot vs
        text_plot_vs = QtWidgets.QLabel("<i>Plot depth vs.</i>")
        hbox.addWidget(text_plot_vs)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        # depth vs density
        text_depth_vs_density = QtWidgets.QLabel("density:")
        hbox.addWidget(text_depth_vs_density)
        text_depth_vs_density.setFixedHeight(GuiSettings.single_line_height())
        self.depth_vs_density_v5 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.depth_vs_density_v5)
        self.depth_vs_density_v5.setChecked(False)
        # depth vs tvu qc
        text_depth_vs_tvu_qc = QtWidgets.QLabel(" TVU QC:")
        hbox.addWidget(text_depth_vs_tvu_qc)
        text_depth_vs_tvu_qc.setFixedHeight(GuiSettings.single_line_height())
        self.depth_vs_tvu_qc_v5 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.depth_vs_tvu_qc_v5)
        self.depth_vs_tvu_qc_v5.setChecked(False)
        hbox.addStretch()

        vbox.addStretch()

    def _ui_execute_gqv5(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeGQv5.setLayout(vbox)

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Grid QA v5")
        button.setToolTip('Perform quality assessment on loaded grids')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_grid_qa_v5)

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

        vbox.addStretch()

    def click_grid_qa_v5(self):
        """trigger the grid qa v5"""
        self._click_grid_qa(5)

    # common

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_grid_qa.html")

    def _click_grid_qa(self, version):
        """abstract the grid qa calling mechanism"""

        # sanity checks
        # - version
        if not isinstance(version, int):
            raise RuntimeError("passed invalid type for version: %s" % type(version))
        if version not in [5, ]:
            raise RuntimeError("passed invalid Grid QA version: %s" % version)
        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.prj.grid_list) == 0:
            raise RuntimeError("the grid list is empty")

        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="survey_grid_qa_%d" % version))

        # check for user input as force TVU QC
        if version == 5:
            self.force_tvu_qc_gqv5 = self.set_force_tvu_qc_gqv5.isChecked()
            self.toggle_mode_gqv5 = self.set_toggle_mode_gqv5.value()
        else:  # this case should be never reached after the sanity checks
            raise RuntimeError("unknown Grid QA's version: %s" % version)

        # for each file in the project grid list
        msg = "QA results per input:\n"
        grid_list = self.prj.grid_list
        opened_folders = list()
        for i, grid_file in enumerate(grid_list):

            # we want to be sure that the label is based on the name of the new file input
            self.prj.clear_survey_label()
            # switcher between different versions of find fliers
            if version == 5:
                success = self._grid_qa(grid_file=grid_file, version=version, idx=(i + 1), total=len(grid_list))
            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Grid QA version: %s" % version)

            if success:
                msg += "- %s: done\n" % self.prj.cur_grid_basename
            else:
                msg += "- %s: skip\n" % self.prj.cur_grid_basename

            # open the output folder (if not already open)
            if self.prj.gridqa_output_folder not in opened_folders:
                self.prj.open_gridqa_output_folder()
                opened_folders.append(self.prj.gridqa_output_folder)

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Grid QA v%d" % version, msg, QtWidgets.QMessageBox.Ok)

    def _grid_qa(self, grid_file, version, idx, total):
        """ grid qa the loaded surface using passed height parameter """

        # GUI takes care of progress bar

        logger.debug('grid qa v%d ...' % version)

        self.prj.progress.start(title="Grid QA v.%d" % version,
                                text="Data loading [%d/%d]" % (idx, total),
                                init_value=2)

        try:
            self.prj.set_cur_grid(path=grid_file)
            self.prj.open_to_read_cur_grid()

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While reading grid file, %s" % e, QtWidgets.QMessageBox.Ok)
            self.prj.progress.end()
            return False

        self.prj.progress.update(value=10,
                                 text="Grid QA v%d [%d/%d]" % (version, idx, total))

        if self.hist_tvu_qc_v5.isChecked() or self.depth_vs_tvu_qc_v5.isChecked():

            # manage the particular case of more than 1 TVU QC layers [but only if the force flag is OFF]
            tvu_qc_layers = self.prj.cur_grid_tvu_qc_layers()
            if len(tvu_qc_layers) == 1:

                if version == 5:
                    self.prj.set_cur_grid_tvu_qc_name(tvu_qc_layers[0])

            elif len(tvu_qc_layers) > 1:

                if version == 5:
                    if self.force_tvu_qc_gqv5:

                        self.prj.set_cur_grid_tvu_qc_name(tvu_qc_layers[0])

                    else:

                        while True:
                            # noinspection PyCallByClass
                            layer_name, ret = QtWidgets.QInputDialog.getItem(self,
                                                                             'TVU QC layers',
                                                                             'Select layer to use:',
                                                                             tvu_qc_layers,
                                                                             0,
                                                                             False)
                            if not ret:
                                continue
                            self.prj.set_cur_grid_tvu_qc_name(layer_name)
                            break

        self.prj.progress.update(value=20)

        try:

            if version == 5:

                logger.info("knob-selected mode: %s" % self.toggle_mode_gqv5)

                if not self.hist_depth_v5.isChecked() and not self.hist_density_v5.isChecked() \
                        and not self.hist_tvu_qc_v5.isChecked() and not self.hist_pct_res_v5.isChecked() \
                        and not self.depth_vs_density_v5.isChecked() and not self.depth_vs_tvu_qc_v5.isChecked():
                    info_str = "You need to flag at least one plot as output!"
                    # noinspection PyCallByClass
                    QtWidgets.QMessageBox.warning(self, "No outputs", info_str, QtWidgets.QMessageBox.Ok)
                    self.prj.progress.end()
                    return False

                self.prj.grid_qa_v5(force_tvu_qc=self.force_tvu_qc_gqv5,
                                    calc_object_detection=(self.toggle_mode_gqv5 == 0),
                                    calc_full_coverage=(self.toggle_mode_gqv5 == 1),
                                    hist_depth=self.hist_depth_v5.isChecked(),
                                    hist_density=self.hist_density_v5.isChecked(),
                                    hist_tvu_qc=self.hist_tvu_qc_v5.isChecked(),
                                    hist_pct_res=self.hist_pct_res_v5.isChecked(),
                                    depth_vs_density=self.depth_vs_density_v5.isChecked(),
                                    depth_vs_tvu_qc=self.depth_vs_tvu_qc_v5.isChecked(),
                                    progress_bar=self.prj.progress
                                    )

            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Grid QA's version: %s" % version)

        except MemoryError:

            err_str = "While executing Grid QA, there was a memory error. Try to close unused applications!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", err_str, QtWidgets.QMessageBox.Ok)
            self.prj.progress.end()
            return False

        except Exception as e:

            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While executing Grid QA, %s" % e, QtWidgets.QMessageBox.Ok)
            self.prj.progress.end()
            return False

        self.prj.progress.end()
        return True
