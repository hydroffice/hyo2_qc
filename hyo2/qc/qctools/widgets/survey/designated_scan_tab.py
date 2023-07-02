import locale
import logging
import os

from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper
from hyo2.qc.common import lib_info
from hyo2.qc.qctools.gui_settings import GuiSettings

logger = logging.getLogger(__name__)


class DesignatedScanTab(QtWidgets.QMainWindow):
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

        # - grid qa v2
        self.desScanV2 = QtWidgets.QGroupBox("Designated Scan v2")
        self.desScanV2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.desScanV2)
        dsv2_hbox = QtWidgets.QHBoxLayout()
        self.desScanV2.setLayout(dsv2_hbox)
        # -- parameters
        self.setParametersDSv1 = QtWidgets.QGroupBox("Parameters")
        self.setParametersDSv1.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        dsv2_hbox.addWidget(self.setParametersDSv1)
        self.set_neighborhood_dsv2 = None
        self.set_scale_dsv2 = None
        self._ui_parameters_dsv2()
        # -- execution
        self.executeDSv2 = QtWidgets.QGroupBox("Execution")
        self.executeDSv2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        dsv2_hbox.addWidget(self.executeDSv2)
        self._ui_execute_dsv2()
        # -- variables
        self.neighborhood_dsv2 = False

        self.vbox.addStretch()

    # v2

    def _ui_parameters_dsv2(self):
        vbox = QtWidgets.QVBoxLayout()
        self.setParametersDSv1.setLayout(vbox)

        vbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # specs
        self.toggle_specs_v2 = QtWidgets.QDial()
        self.toggle_specs_v2.setNotchesVisible(True)
        self.toggle_specs_v2.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_specs_v2.setRange(2016, 2017)
        self.toggle_specs_v2.setValue(2017)
        self.toggle_specs_v2.setFixedSize(QtCore.QSize(48, 48))
        self.toggle_specs_v2.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_specs_v2)
        # stretch
        toggle_hbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # specs
        label_hbox.addSpacing(20)
        text_0 = QtWidgets.QLabel("2016")
        text_0.setAlignment(QtCore.Qt.AlignLeft)
        text_0.setFixedWidth(40)
        label_hbox.addWidget(text_0)
        text_1 = QtWidgets.QLabel("2017+")
        text_1.setAlignment(QtCore.Qt.AlignRight)
        text_1.setFixedWidth(40)
        # text_1.setStyleSheet("QLabel { color :  rgb(200, 0, 0, 200); }")
        label_hbox.addWidget(text_1)
        label_hbox.addSpacing(5)
        # stretch
        label_hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        vbox.addSpacing(10)

        # survey scale
        scale_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(scale_hbox)
        scale_hbox.addStretch()
        text_set_scale = QtWidgets.QLabel("Survey scale:   1 :")
        scale_hbox.addWidget(text_set_scale)
        text_set_scale.setFixedHeight(GuiSettings.single_line_height())
        text_set_scale.setMinimumWidth(90)
        self.set_scale_dsv2 = QtWidgets.QLineEdit("")
        scale_hbox.addWidget(self.set_scale_dsv2)
        self.set_scale_dsv2.setFixedHeight(GuiSettings.single_line_height())
        self.set_scale_dsv2.setValidator(QtGui.QIntValidator(1, 99999999, self.set_scale_dsv2))
        self.set_scale_dsv2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_scale_dsv2.setReadOnly(False)
        self.set_scale_dsv2.setFont(GuiSettings.console_font())
        self.set_scale_dsv2.setStyleSheet(GuiSettings.stylesheet_console_fg_color())
        self.set_scale_dsv2.setFixedWidth(60)
        scale_hbox.addStretch()

        vbox.addSpacing(20)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        text_checks = QtWidgets.QLabel("Additional checks:")
        hbox.addWidget(text_checks)
        # text_checks.setFixedHeight(GuiSettings.single_line_height())
        text_checks.setMinimumWidth(80)
        text_checks.setStyleSheet("QLabel { color : #aaaaaa; }")
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        text_set_neighborhood = QtWidgets.QLabel("Evaluate neighborhood")
        hbox.addWidget(text_set_neighborhood)
        text_set_neighborhood.setFixedHeight(GuiSettings.single_line_height())
        text_set_neighborhood.setMinimumWidth(80)
        # text_set_neighborhood.setStyleSheet("QLabel { color :  rgba(200, 0, 0, 200); }")
        self.set_neighborhood_dsv2 = QtWidgets.QCheckBox(self)
        self.set_neighborhood_dsv2.setToolTip("Experimental check that evaluates the neighborhood of each "
                                              "designated sounding")
        hbox.addWidget(self.set_neighborhood_dsv2)
        self.set_neighborhood_dsv2.setChecked(False)
        hbox.addStretch()

        vbox.addStretch()

    def _ui_execute_dsv2(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeDSv2.setLayout(vbox)

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()

        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() * 1.3)
        button.setText("Designated Scan v2")
        button.setToolTip('Perform checks on grid designated soundings')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_scan_designated_v2)

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
        button.clicked.connect(self.click_open_manual_v2)

        hbox.addStretch()

        vbox.addStretch()

    @classmethod
    def click_open_manual_v2(cls):
        logger.debug("open manual")
        Helper.explore_folder(
            "https://www.hydroffice.org/manuals/qctools/stable/user_manual_survey_designated_scan.html"
        )

    def click_scan_designated_v2(self):
        """trigger the scan designated v1"""
        # checks for Survey Scale
        if self.set_scale_dsv2.text() == "":
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Settings", "First set the survey scale!", QtWidgets.QMessageBox.Ok)
            return
        locale.setlocale(locale.LC_ALL, "")
        scale = locale.atoi(self.set_scale_dsv2.text())
        if scale == 0:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Settings", "Invalid survey scale: %d" % scale,
                                           QtWidgets.QMessageBox.Ok)
            return

        self._click_scan_designated(2)

    # common

    def _click_scan_designated(self, version: int):
        """abstract the grid qa calling mechanism"""

        # sanity checks
        # - version
        if version not in [2, ]:
            raise RuntimeError("passed invalid Designated Scan version: %s" % version)
        if len(self.prj.s57_list) == 0:
            raise RuntimeError("the S57 list is empty")
        if len(self.prj.grid_list) == 0:
            raise RuntimeError("the grid list is empty")

        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="survey_designated_scan_%d" % version))

        # check for user input as neighborhood check
        if version == 2:
            self.neighborhood_dsv2 = self.set_neighborhood_dsv2.isChecked()
        else:  # this case should be never reached after the sanity checks
            raise RuntimeError("unknown Designated Scan's version: %s" % version)

        # for each file in the project grid list
        msg = "Flagged features per input:\n"
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

                idx = (j + 1) * (i * len(s57_list))
                total = len(s57_list) * len(grid_list)

                # switcher between different versions of find fliers
                if version == 2:
                    self._scan_designated(grid_file=grid_file, version=version, idx=idx, total=total)
                else:  # this case should be never reached after the sanity checks
                    raise RuntimeError("unknown Grid QA version: %s" % version)

                logger.info("survey label: %s" % self.prj.survey_label)

                # open the output folder (if not already open)
                if self.prj.save_designated():
                    if self.prj.designated_output_folder not in opened_folders:
                        self.prj.open_designated_output_folder()
                        opened_folders.append(self.prj.designated_output_folder)

                msg += "- %s (S57: %s): %d\n" % \
                       (self.prj.cur_grid_basename, self.prj.cur_s57_basename, self.prj.number_of_designated())

                # close the grid file
                self.prj.close_cur_grid()

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Designated Scan v%d" % version, msg, QtWidgets.QMessageBox.Ok)

    def _scan_designated(self, grid_file, version, idx, total):
        """ grid qa the loaded surface using passed height parameter """

        # GUI takes care of progress bar

        logger.debug('designated scan v%d ...' % version)

        self.parent_win.progress.start(title="Designated Scan v.%d" % version,
                                       text="Data loading [%d/%d]" % (idx, total),
                                       init_value=10)

        try:
            self.prj.set_cur_grid(path=grid_file)
            self.prj.open_to_read_cur_grid()

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While reading grid file, %s" % e, QtWidgets.QMessageBox.Ok)
            self.parent_win.progress.end()
            return

        self.parent_win.progress.update(value=20,
                                        text="Scanning designated [%d/%d]" % (idx, total))

        try:

            if version == 2:
                locale.setlocale(locale.LC_ALL, "")
                scale = locale.atoi(self.set_scale_dsv2.text())
                specs_version = "%d" % self.toggle_specs_v2.value()

                passed = self.prj.designated_scan_v2(survey_scale=scale, neighborhood=self.neighborhood_dsv2,
                                                     specs=specs_version)

            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Designated Scan's version: %s" % version)

        except MemoryError:
            err_str = "While executing Designated Scan, there was a memory error. Try to close unused applications!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", err_str, QtWidgets.QMessageBox.Ok)
            self.parent_win.progress.end()
            return

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While executing Designated Scan, %s" % e,
                                           QtWidgets.QMessageBox.Ok)
            self.parent_win.progress.end()
            return

        self.parent_win.progress.end()
        return passed
