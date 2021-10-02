import logging
import os

from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper
from hyo2.qc.common import lib_info
from hyo2.qc.qctools.gui_settings import GuiSettings

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

        # - SBDARE export v5
        self.sbdareExportV5 = QtWidgets.QGroupBox("SBDARE export v5")
        self.sbdareExportV5.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.sbdareExportV5)
        sav5 = QtWidgets.QHBoxLayout()
        self.sbdareExportV5.setLayout(sav5)
        # -- parameters
        self.setParametersSEv5 = QtWidgets.QGroupBox("Parameters")
        self.setParametersSEv5.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        sav5.addWidget(self.setParametersSEv5)
        self._ui_parameters_sav5()
        # -- execution
        self.executeSEv5 = QtWidgets.QGroupBox("Execution")
        self.executeSEv5.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        sav5.addWidget(self.executeSEv5)
        self._ui_execute_sav5()

    def _ui_parameters_sav5(self):
        hbox = QtWidgets.QHBoxLayout()
        self.setParametersSEv5.setLayout(hbox)
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

    def _ui_execute_sav5(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeSEv5.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() + 16)
        button.setText("SBDARE export v5")
        button.setToolTip('Export SBDARE values')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_sbdare_export_v5)

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

    def click_sbdare_export_v5(self):

        self._click_sbdare_export(5)

    def _click_sbdare_export(self, version):
        """abstract the SBDARE export calling mechanism"""

        # sanity checks
        # - version
        if not isinstance(version, int):
            raise RuntimeError("passed invalid type for version: %s" % type(version))

        if version not in [5]:
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
            if version in [5]:
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
            if version == 5:

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
                    QtCore.QSettings().setValue("bottom_samples_images_folder", images_folder)

                self.prj.sbdare_export_v5(images_folder=images_folder)

            else:
                RuntimeError("unknown SBDARE export version: %s" % version)

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While SBDARE exporting, %s" % e, QtWidgets.QMessageBox.Ok)
            return
