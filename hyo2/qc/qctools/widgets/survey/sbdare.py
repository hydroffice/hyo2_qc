from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class SbdareTab(QtWidgets.QMainWindow):
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

        # - SBDARE export v3
        self.sbdareExportV3 = QtWidgets.QGroupBox("SBDARE export v3")
        self.sbdareExportV3.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.sbdareExportV3)
        sav3 = QtWidgets.QHBoxLayout()
        self.sbdareExportV3.setLayout(sav3)
        # -- parameters
        self.setParametersSEv3 = QtWidgets.QGroupBox("Parameters")
        self.setParametersSEv3.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        sav3.addWidget(self.setParametersSEv3)
        self._ui_parameters_sav3()
        # -- execution
        self.executeSEv3 = QtWidgets.QGroupBox("Execution")
        self.executeSEv3.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        sav3.addWidget(self.executeSEv3)
        self._ui_execute_sav3()

        # - SBDARE export v4
        self.sbdareExportV4 = QtWidgets.QGroupBox("SBDARE export v4")
        self.sbdareExportV4.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        # self.sbdareExportV4.hide()
        self.vbox.addWidget(self.sbdareExportV4)
        sav4 = QtWidgets.QHBoxLayout()
        self.sbdareExportV4.setLayout(sav4)
        # -- parameters
        self.setParametersSEv4 = QtWidgets.QGroupBox("Parameters")
        self.setParametersSEv4.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        sav4.addWidget(self.setParametersSEv4)
        self._ui_parameters_sav4()
        # -- execution
        self.executeSEv4 = QtWidgets.QGroupBox("Execution")
        self.executeSEv4.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        sav4.addWidget(self.executeSEv4)
        self._ui_execute_sav4()

        self.vbox.addStretch()

        self.sbdareExportV3.hide()

    def keyPressEvent(self, event):
        _ = event.key()

        if event.modifiers() == QtCore.Qt.ControlModifier:

            if event.key() == QtCore.Qt.Key_3:

                if self.sbdareExportV3.isHidden():
                    self.sbdareExportV3.show()
                else:
                    self.sbdareExportV3.hide()

                return True
        return super(SbdareTab, self).keyPressEvent(event)

    def _ui_parameters_sav3(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersSEv3.setLayout(hbox)
        hbox.addStretch()

        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        label_hbox.addStretch()
        empty = QtWidgets.QLabel("")
        empty.setAlignment(QtCore.Qt.AlignLeft)
        label_hbox.addWidget(empty)
        label_hbox.addStretch()

        vbox.addStretch()

        hbox.addStretch()

    def _ui_execute_sav3(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeSEv3.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() + 16)
        button.setText("SBDARE export v3")
        button.setToolTip('Export SBDARE values')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_sbdare_export_v3)

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

    def _ui_parameters_sav4(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersSEv4.setLayout(hbox)
        hbox.addStretch()

        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()

        label_up_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_up_hbox)
        # stretch
        label_up_hbox.addStretch()
        # profile
        text_2013_empty = QtWidgets.QLabel("")
        text_2013_empty.setAlignment(QtCore.Qt.AlignCenter)
        text_2013_empty.setFixedWidth(30)
        label_up_hbox.addWidget(text_2013_empty)
        text_2018_empty = QtWidgets.QLabel("")
        text_2018_empty.setAlignment(QtCore.Qt.AlignCenter)
        text_2018_empty.setFixedWidth(35)
        label_up_hbox.addWidget(text_2018_empty)
        # stretch
        label_up_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # profile
        self.toggle_htd_v4 = QtWidgets.QDial()
        self.toggle_htd_v4.setNotchesVisible(True)
        self.toggle_htd_v4.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_htd_v4.setRange(0, 1)
        self.toggle_htd_v4.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_htd_v4.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_htd_v4)
        # noinspection PyUnresolvedReferences
        self.toggle_htd_v4.valueChanged.connect(self.click_set_htd_v4)
        # stretch
        toggle_hbox.addStretch()

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # profile
        text_2013 = QtWidgets.QLabel("HTD 2013-3")
        text_2013.setAlignment(QtCore.Qt.AlignRight)
        text_2013.setFixedWidth(60)
        label_hbox.addWidget(text_2013)
        text_2018 = QtWidgets.QLabel("HTD 2018-4")
        text_2018.setAlignment(QtCore.Qt.AlignRight)
        text_2018.setFixedWidth(80)
        # text_2018.setStyleSheet("QLabel { color :  rgb(200, 0, 0, 200); }")
        label_hbox.addWidget(text_2018)
        # stretch
        label_hbox.addStretch()

        vbox.addSpacing(18)

        options_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(options_hbox)

        options_hbox.addStretch()

        set_checks_ffv4 = QtWidgets.QGroupBox("Options")
        options_hbox.addWidget(set_checks_ffv4)
        chk_vbox = QtWidgets.QVBoxLayout()
        set_checks_ffv4.setLayout(chk_vbox)

        options_hbox.addStretch()

        self.set_image_folder_v4 = QtWidgets.QCheckBox("Select the path to the images folder")
        self.set_image_folder_v4.setChecked(True)
        self.set_image_folder_v4.setDisabled(True)
        chk_vbox.addWidget(self.set_image_folder_v4)

        self.set_exif_tags_v4 = QtWidgets.QCheckBox("Set EXIF GPS in JPEG images to S57 position")
        self.set_exif_tags_v4.setChecked(True)
        self.set_exif_tags_v4.setDisabled(True)
        chk_vbox.addWidget(self.set_exif_tags_v4)

        vbox.addStretch()

        hbox.addStretch()

    def _ui_execute_sav4(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeSEv4.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() + 16)
        button.setText("SBDARE export v4")
        button.setToolTip('Export SBDARE values')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_sbdare_export_v4)

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

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_sbdare_export.html")

    def click_set_htd_v4(self, value):
        """ Change the HTD in use """

        if value == 0:
            self.set_image_folder_v4.setDisabled(True)
            self.set_exif_tags_v4.setDisabled(True)

        else:
            self.set_image_folder_v4.setEnabled(True)
            self.set_exif_tags_v4.setEnabled(True)

        logger.info('activated htd %s' % value)

    def click_sbdare_export_v3(self):
        self._click_sbdare_export(3)

    def click_sbdare_export_v4(self):
        if self.toggle_htd_v4.value() == 0:
            self._click_sbdare_export(3)

        else:
            self._click_sbdare_export(4)

    def _click_sbdare_export(self, version):
        """abstract the SBDARE export calling mechanism"""

        # sanity checks
        # - version
        if not isinstance(version, int):
            raise RuntimeError("passed invalid type for version: %s" % type(version))

        if version not in [3, 4]:
            raise RuntimeError("passed invalid Feature Scan version: %s" % version)

        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.prj.s57_list) == 0:
            raise RuntimeError("the S57 list is empty")

        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="survey_sbdare_export_%d" % version))

        # for each file in the project grid list
        msg = "Exported SBDARE features per input:\n"
        s57_list = self.prj.s57_list
        opened_folders = list()
        total = len(s57_list)
        for i, s57_file in enumerate(s57_list):

            self.parent_win.progress.start(title="SBDARE export v.%d" % version,
                                           text="Data loading [%d/%d]" % (i + 1, total),
                                           init_value=10)

            # we want to be sure that the label is based on the name of the new file input
            self.prj.clear_survey_label()

            self.parent_win.progress.update(value=20,
                                            text="SBDARE export v%d [%d/%d]" % (version, i + 1, total))

            # switcher between different versions of SBDARE export
            if version in [3, 4]:
                self._sbdare_export(feature_file=s57_file, version=version, idx=(i + 1), total=len(s57_list))
            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown SBDARE export version: %s" % version)

            self.parent_win.progress.update(value=40,
                                            text="SBDARE export v%d [%d/%d]" % (version, i + 1, total))

            # export the flagged features
            logger.debug('exporting SBDARE features ...')
            saved = self.prj.save_sbdare()
            logger.debug('exporting SBDARE features: done')
            msg += "- %s: %d\n" % (self.prj.cur_s57_basename, self.prj.number_of_sbdare_features())

            # open the output folder (if not already open)
            if saved:

                if self.prj.sbdare_output_folder not in opened_folders:
                    self.prj.open_sbdare_output_folder()
                    opened_folders.append(self.prj.sbdare_output_folder)

        warnings = self.prj.sbdare_warnings()
        msg += "\nWarnings: %d\n" % len(warnings)
        logger.info("Warnings: %d" % len(warnings))

        for idx, warning in enumerate(warnings):

            logger.debug("#%02d: %s" % (idx, warning))
            if idx == 9:
                msg += "- ... \n\n" \
                       "The remaining warnings are listed in the Command Shell.\n"
                continue
            if idx > 9:
                continue
            msg += "- %s\n" % warning

        self.parent_win.progress.end()

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "SBDARE export v%d" % version, msg, QtWidgets.QMessageBox.Ok)

    def _sbdare_export(self, feature_file, version, idx, total):
        """ SBDARE export in the loaded s57 features """

        # GUI takes care of progress bar

        logger.debug('SBDARE export v%d ...' % version)

        try:
            self.prj.read_feature_file(feature_path=feature_file)

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While reading s57 file, %s" % e, QtWidgets.QMessageBox.Ok)
            return

        try:
            if version == 3:
                self.prj.sbdare_export_v3()

            elif version == 4:

                images_folder = None
                if self.set_image_folder_v4.isChecked():

                    # ask for images folder
                    # noinspection PyCallByClass
                    images_folder = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                               "Select the folder with the images",
                                                                               QtCore.QSettings().value(
                                                                                   "bottom_samples_images_folder"), )
                    if images_folder == "":
                        logger.debug('selecting images folder: aborted')
                        images_folder = None

                    else:
                        logger.debug("selected images folder: %s" % images_folder)
                        QtCore.QSettings().value("bottom_samples_images_folder", images_folder)

                try:
                    self.prj.sbdare_export_v4(exif=self.set_exif_tags_v4.isChecked(), images_folder=images_folder)
                except Exception as e:
                    # noinspection PyCallByClass
                    QtWidgets.QMessageBox.critical(self, "Error", "While exporting file, %s" % e,
                                                   QtWidgets.QMessageBox.Ok)
                    return

            else:
                RuntimeError("unknown SBDARE export version: %s" % version)

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While SBDARE exporting, %s" % e, QtWidgets.QMessageBox.Ok)
            return
