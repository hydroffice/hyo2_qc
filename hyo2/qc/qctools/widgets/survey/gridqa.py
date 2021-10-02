import logging
import os

from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper
from hyo2.qc.common import lib_info
from hyo2.qc.qctools.gui_settings import GuiSettings

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

        # - grid qa v6
        self.gridQAV6 = QtWidgets.QGroupBox("Grid QA v6")
        self.vbox.addWidget(self.gridQAV6)
        gqv6_hbox = QtWidgets.QHBoxLayout()
        self.gridQAV6.setLayout(gqv6_hbox)
        # -- parameters
        self.setSettingsGQv6 = QtWidgets.QGroupBox("Settings")
        gqv6_hbox.addWidget(self.setSettingsGQv6)
        self.set_force_tvu_qc_gqv6 = None
        self.text_set_tvu_qc = None
        self.set_toggle_mode_gqv6 = None
        self.text_obj = None
        self.text_cov = None
        self.hist_depth_v6 = None
        self.hist_density_v6 = None
        self.hist_tvu_qc_v6 = None
        self.hist_pct_res_v6 = None
        self.hist_catzoc = None
        # self.hist_catzoc_a1 = None
        # self.hist_catzoc_a2b = None
        # self.hist_catzoc_c = None
        # self.hist_catzoc_all = None
        self.text_slider_a1 = None
        self.text_slider_a2b = None
        self.text_slider_c = None
        self.text_catzoc_slider = None
        self.catzoc_slider = None
        self.depth_vs_density_v6 = None
        self.depth_vs_tvu_qc_v6 = None
        self._ui_settings_gqv6()
        # -- execution
        self.executeGQv6 = QtWidgets.QGroupBox("Execution")
        gqv6_hbox.addWidget(self.executeGQv6)
        self._ui_execute_gqv6()
        # -- variables
        self.toggle_mode_gqv6 = None
        self.force_tvu_qc_gqv6 = False

        self.vbox.addStretch()

    def keyPressEvent(self, event):
        key = event.key()
        if event.modifiers() == QtCore.Qt.ControlModifier:
            # logger.debug("pressed CTRL + %s" % key)
            if key == QtCore.Qt.Key_F:

                if self.set_force_tvu_qc_gqv6.isHidden():
                    self.set_force_tvu_qc_gqv6.show()
                    self.text_set_tvu_qc.show()

                else:
                    self.set_force_tvu_qc_gqv6.hide()
                    self.text_set_tvu_qc.hide()

                return True
        return super(GridQATab, self).keyPressEvent(event)

    # v6

    def _ui_settings_gqv6(self):
        vbox = QtWidgets.QVBoxLayout()
        self.setSettingsGQv6.setLayout(vbox)

        # hidden flagged Force TVU QC calculation

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        self.text_set_tvu_qc = QtWidgets.QLabel("Force TVU QC calculation")
        self.text_set_tvu_qc.setFixedHeight(GuiSettings.single_line_height())
        self.text_set_tvu_qc.setMinimumWidth(80)
        self.text_set_tvu_qc.setHidden(True)
        hbox.addWidget(self.text_set_tvu_qc)
        self.set_force_tvu_qc_gqv6 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.set_force_tvu_qc_gqv6)
        self.set_force_tvu_qc_gqv6.setChecked(True)
        self.set_force_tvu_qc_gqv6.setHidden(True)

        hbox.addStretch()

        vbox.addStretch()

        # histograms label

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        # histograms
        text_hist = QtWidgets.QLabel("<i>Histograms</i>")
        hbox.addWidget(text_hist)
        hbox.addStretch()

        # common histograms

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        # histograms: depth
        text_hist_depth = QtWidgets.QLabel("depth:")
        hbox.addWidget(text_hist_depth)
        text_hist_depth.setFixedHeight(GuiSettings.single_line_height())
        self.hist_depth_v6 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.hist_depth_v6)
        self.hist_depth_v6.setChecked(True)
        # histograms: density
        text_hist_density = QtWidgets.QLabel("density:")
        hbox.addWidget(text_hist_density)
        text_hist_density.setFixedHeight(GuiSettings.single_line_height())
        self.hist_density_v6 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.hist_density_v6)
        self.hist_density_v6.setChecked(True)
        # histograms: tvu qc
        text_hist_tvu_qc = QtWidgets.QLabel("TVU (IHO S-44):")
        hbox.addWidget(text_hist_tvu_qc)
        text_hist_tvu_qc.setFixedHeight(GuiSettings.single_line_height())
        self.hist_tvu_qc_v6 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.hist_tvu_qc_v6)
        self.hist_tvu_qc_v6.setChecked(True)
        hbox.addStretch()

        # VR-only

        vr_only_group = QtWidgets.QGroupBox("VR-only")
        vbox.addWidget(vr_only_group)

        vr_only_vbox = QtWidgets.QVBoxLayout()
        vr_only_group.setLayout(vr_only_vbox)

        # histograms: pct res
        hbox = QtWidgets.QHBoxLayout()
        vr_only_vbox.addLayout(hbox)
        hbox.addStretch()
        text_hist_pct_res = QtWidgets.QLabel("% resolution:")
        hbox.addWidget(text_hist_pct_res)
        text_hist_pct_res.setFixedHeight(GuiSettings.single_line_height())
        self.hist_pct_res_v6 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.hist_pct_res_v6)
        self.hist_pct_res_v6.setChecked(True)
        hbox.addStretch()

        # ObjectDetection/FullCoverage knob

        hbox = QtWidgets.QHBoxLayout()
        vr_only_vbox.addLayout(hbox)
        # stretch
        hbox.addStretch()
        # mode
        self.set_toggle_mode_gqv6 = QtWidgets.QDial()
        self.set_toggle_mode_gqv6.setNotchesVisible(True)
        self.set_toggle_mode_gqv6.setWrapping(False)
        self.set_toggle_mode_gqv6.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.set_toggle_mode_gqv6.setRange(0, 1)
        self.set_toggle_mode_gqv6.setSliderPosition(1)
        self.set_toggle_mode_gqv6.setFixedSize(QtCore.QSize(40, 40))
        self.set_toggle_mode_gqv6.setInvertedAppearance(False)
        hbox.addWidget(self.set_toggle_mode_gqv6)
        # noinspection PyUnresolvedReferences
        self.hist_pct_res_v6.stateChanged.connect(self.click_set_pct_res)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vr_only_vbox.addLayout(hbox)

        # stretch
        hbox.addStretch()
        # mode
        self.text_obj = QtWidgets.QLabel("Object detection")
        self.text_obj.setAlignment(QtCore.Qt.AlignCenter)
        self.text_obj.setFixedWidth(85)
        hbox.addWidget(self.text_obj)
        self.text_cov = QtWidgets.QLabel("Full coverage")
        self.text_cov.setAlignment(QtCore.Qt.AlignCenter)
        self.text_cov.setFixedWidth(85)
        hbox.addWidget(self.text_cov)
        # stretch
        hbox.addStretch()

        # Branch-only

        branch_only_group = QtWidgets.QGroupBox("Branch-only")
        vbox.addWidget(branch_only_group)

        branch_only_vbox = QtWidgets.QVBoxLayout()
        branch_only_group.setLayout(branch_only_vbox)

        hbox = QtWidgets.QHBoxLayout()
        branch_only_vbox.addLayout(hbox)
        hbox.addStretch()
        # catzoc
        text_hist_catzoc = QtWidgets.QLabel("TVU (IHO S-57 CATZOC):")
        hbox.addWidget(text_hist_catzoc)
        text_hist_catzoc.setFixedHeight(GuiSettings.single_line_height())
        self.hist_catzoc = QtWidgets.QCheckBox(self)
        # noinspection PyUnresolvedReferences
        self.hist_catzoc.stateChanged.connect(self.click_set_catzoc)
        hbox.addWidget(self.hist_catzoc)
        self.hist_catzoc.setChecked(False)
        hbox.addStretch()

        slider_hbox = QtWidgets.QHBoxLayout()
        branch_only_vbox.addLayout(slider_hbox)
        slider_hbox.addStretch()

        slider_gbox = QtWidgets.QGridLayout()
        slider_hbox.addLayout(slider_gbox)

        text_sz = 34
        self.text_slider_a1 = QtWidgets.QLabel("A1")
        self.text_slider_a1.setDisabled(True)
        self.text_slider_a1.setFixedWidth(text_sz)
        self.text_slider_a1.setAlignment(QtCore.Qt.AlignLeft)
        self.text_slider_a1.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(self.text_slider_a1, 0, 1, 1, 1)
        self.text_slider_a2b = QtWidgets.QLabel("A2 / B   ")
        self.text_slider_a2b.setDisabled(True)
        self.text_slider_a2b.setFixedWidth(text_sz)
        self.text_slider_a2b.setAlignment(QtCore.Qt.AlignCenter)
        self.text_slider_a2b.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(self.text_slider_a2b, 0, 2, 1, 1)
        self.text_slider_c = QtWidgets.QLabel(" C ")
        self.text_slider_c.setDisabled(True)
        self.text_slider_c.setFixedWidth(text_sz - 8)
        self.text_slider_c.setAlignment(QtCore.Qt.AlignCenter)
        self.text_slider_c.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(self.text_slider_c, 0, 3, 1, 1)
        self.text_slider_all = QtWidgets.QLabel("All ")
        self.text_slider_all.setDisabled(True)
        self.text_slider_all.setFixedWidth(text_sz)
        self.text_slider_all.setAlignment(QtCore.Qt.AlignRight)
        self.text_slider_all.setStyleSheet(GuiSettings.stylesheet_slider_labels())
        slider_gbox.addWidget(self.text_slider_all, 0, 4, 1, 1)

        self.text_catzoc_slider = QtWidgets.QLabel("Choose:")
        self.text_catzoc_slider.setDisabled(True)
        slider_gbox.addWidget(self.text_catzoc_slider, 1, 0, 1, 1)

        self.catzoc_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.catzoc_slider.setRange(1, 4)
        self.catzoc_slider.setSingleStep(1)
        self.catzoc_slider.setValue(4)
        self.catzoc_slider.setTickInterval(1)
        self.catzoc_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.catzoc_slider.setDisabled(True)
        slider_gbox.addWidget(self.catzoc_slider, 1, 1, 1, 4)

        slider_hbox.addStretch()

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
        text_depth_vs_density = QtWidgets.QLabel("Density:")
        hbox.addWidget(text_depth_vs_density)
        text_depth_vs_density.setFixedHeight(GuiSettings.single_line_height())
        self.depth_vs_density_v6 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.depth_vs_density_v6)
        self.depth_vs_density_v6.setChecked(False)
        # depth vs tvu qc
        text_depth_vs_tvu_qc = QtWidgets.QLabel(" TVU (IHO S-44):")
        hbox.addWidget(text_depth_vs_tvu_qc)
        text_depth_vs_tvu_qc.setFixedHeight(GuiSettings.single_line_height())
        self.depth_vs_tvu_qc_v6 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.depth_vs_tvu_qc_v6)
        self.depth_vs_tvu_qc_v6.setChecked(False)
        hbox.addStretch()

        vbox.addSpacing(9)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        vbox.addStretch()

    def _ui_execute_gqv6(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeGQv6.setLayout(vbox)

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("Grid QA v6")
        button.setToolTip('Perform quality assessment on loaded grids')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_grid_qa_v6)

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

    def click_grid_qa_v6(self):
        """trigger the grid qa v6"""
        self._click_grid_qa(6)

    def click_set_catzoc(self):
        """enable catzoc slider when catzoc flag is checked"""
        is_enabled = self.hist_catzoc.isChecked()
        self.catzoc_slider.setEnabled(is_enabled)
        self.text_catzoc_slider.setEnabled(is_enabled)
        self.text_slider_a1.setEnabled(is_enabled)
        self.text_slider_a2b.setEnabled(is_enabled)
        self.text_slider_c.setEnabled(is_enabled)
        self.text_slider_all.setEnabled(is_enabled)

    def click_set_pct_res(self):
        is_enabled = self.hist_pct_res_v6.isChecked()
        self.set_toggle_mode_gqv6.setEnabled(is_enabled)
        self.text_obj.setEnabled(is_enabled)
        self.text_cov.setEnabled(is_enabled)

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
        if version not in [6, ]:
            raise RuntimeError("passed invalid Grid QA version: %s" % version)
        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.prj.grid_list) == 0:
            raise RuntimeError("the grid list is empty")

        url_suffix = "survey_grid_qa_%d" % version
        if self.hist_catzoc.isChecked():
            url_suffix += "_catzoc"
        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix=url_suffix))

        # check for user input as force TVU QC
        if version == 6:
            self.force_tvu_qc_gqv6 = self.set_force_tvu_qc_gqv6.isChecked()
            self.toggle_mode_gqv6 = self.set_toggle_mode_gqv6.value()
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
            if version == 6:
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

        if self.hist_tvu_qc_v6.isChecked() or self.depth_vs_tvu_qc_v6.isChecked():

            # manage the particular case of more than 1 TVU QC layers [but only if the force flag is OFF]
            tvu_qc_layers = self.prj.cur_grid_tvu_qc_layers()
            if len(tvu_qc_layers) == 1:

                if version == 6:
                    self.prj.set_cur_grid_tvu_qc_name(tvu_qc_layers[0])

            elif len(tvu_qc_layers) > 1:

                if version == 6:
                    if self.force_tvu_qc_gqv6:

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

            if version == 6:

                logger.info("knob-selected mode: %s" % self.toggle_mode_gqv6)

                if not self.hist_depth_v6.isChecked() and not self.hist_density_v6.isChecked() \
                        and not self.hist_tvu_qc_v6.isChecked() and not self.hist_pct_res_v6.isChecked() \
                        and not self.hist_catzoc.isChecked()\
                        and not self.depth_vs_density_v6.isChecked() and not self.depth_vs_tvu_qc_v6.isChecked():
                    info_str = "You need to flag at least one plot as output!"
                    # noinspection PyCallByClass
                    QtWidgets.QMessageBox.warning(self, "No outputs", info_str, QtWidgets.QMessageBox.Ok)
                    self.prj.progress.end()
                    return False

                catzoc_hist_selection = self.catzoc_slider.value()
                catzoc_a1 = False
                catzoc_a2b = False
                catzoc_c = False
                if catzoc_hist_selection == 1:
                    catzoc_a1 = True
                elif catzoc_hist_selection == 2:
                    catzoc_a2b = True
                elif catzoc_hist_selection == 3:
                    catzoc_c = True
                else:
                    catzoc_a1 = True
                    catzoc_a2b = True
                    catzoc_c = True

                self.prj.grid_qa_v6(force_tvu_qc=self.force_tvu_qc_gqv6,
                                    calc_object_detection=(self.toggle_mode_gqv6 == 0),
                                    calc_full_coverage=(self.toggle_mode_gqv6 == 1),
                                    hist_depth=self.hist_depth_v6.isChecked(),
                                    hist_density=self.hist_density_v6.isChecked(),
                                    hist_tvu_qc=self.hist_tvu_qc_v6.isChecked(),
                                    hist_pct_res=self.hist_pct_res_v6.isChecked(),
                                    hist_catzoc_a1=(self.hist_catzoc.isChecked() and catzoc_a1),
                                    hist_catzoc_a2b=(self.hist_catzoc.isChecked() and catzoc_a2b),
                                    hist_catzoc_c=(self.hist_catzoc.isChecked() and catzoc_c),
                                    depth_vs_density=self.depth_vs_density_v6.isChecked(),
                                    depth_vs_tvu_qc=self.depth_vs_tvu_qc_v6.isChecked(),
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

        self.prj.close_cur_grid()
        self.prj.progress.end()
        return True
