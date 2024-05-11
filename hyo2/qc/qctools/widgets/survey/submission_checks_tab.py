import logging
import os

from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper
from hyo2.qc.common import lib_info
from hyo2.qc.qctools.gui_settings import GuiSettings

logger = logging.getLogger(__name__)


class SubmissionChecksTab(QtWidgets.QMainWindow):
    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win, prj):
        QtWidgets.QMainWindow.__init__(self)
        # Enable dragging and dropping onto the GUI
        self.setAcceptDrops(True)

        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        self.dataInputs = QtWidgets.QGroupBox("Drag-and-drop 'OPR-X###-XX-##' or 'X#####' folders")
        self.dataInputs.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.dataInputs)

        vbox = QtWidgets.QVBoxLayout()
        self.dataInputs.setLayout(vbox)

        # add folder
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_add_root = QtWidgets.QLabel("Root folders:")
        hbox.addWidget(text_add_root)
        # text_add_grids.setFixedHeight(GuiSettings.single_line_height())
        text_add_root.setMinimumWidth(64)
        self.root_folders = QtWidgets.QListWidget()
        hbox.addWidget(self.root_folders)
        self.root_folders.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.root_folders.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.root_folders.customContextMenuRequested.connect(self.make_roots_context_menu)
        self.root_folders.setAlternatingRowColors(True)
        button_add_roots = QtWidgets.QPushButton()
        hbox.addWidget(button_add_roots)
        button_add_roots.setFixedHeight(GuiSettings.single_line_height())
        button_add_roots.setFixedWidth(GuiSettings.single_line_height())
        button_add_roots.setText(" + ")
        button_add_roots.setToolTip('Add (or drag-and-drop) root submission folders')
        # noinspection PyUnresolvedReferences
        button_add_roots.clicked.connect(self.click_add_roots)

        vbox.addSpacing(6)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        text_non_opr = QtWidgets.QLabel("Non-OPR project")
        hbox.addWidget(text_non_opr)
        text_non_opr.setFixedHeight(GuiSettings.single_line_height())
        text_non_opr.setMinimumWidth(80)
        self.set_non_opr_v4 = QtWidgets.QCheckBox(self)
        hbox.addWidget(self.set_non_opr_v4)
        self.set_non_opr_v4.setChecked(False)
        hbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        # clear data
        button_clear_data = QtWidgets.QPushButton()
        hbox.addWidget(button_clear_data)
        button_clear_data.setFixedHeight(GuiSettings.single_line_height())
        # button_clear_data.setFixedWidth(GuiSettings.single_line_height())
        button_clear_data.setText("Clear data")
        button_clear_data.setToolTip('Clear all data loaded')
        # noinspection PyUnresolvedReferences
        button_clear_data.clicked.connect(self.click_clear_data)

        # output folder
        button_open_output = QtWidgets.QPushButton()
        hbox.addWidget(button_open_output)
        button_open_output.setFixedHeight(GuiSettings.single_line_height())
        # button_open_output.setFixedWidth(GuiSettings.single_line_height())
        button_open_output.setText("Output folder")
        button_open_output.setToolTip('Open the folder with the check reports')
        # noinspection PyUnresolvedReferences
        button_open_output.clicked.connect(self.click_open_output)

        hbox.addStretch()

        # self.vbox.addStretch()
        self.vbox.addSpacing(10)

        # - Submission checks v4
        self.toggle_profiles_v4 = None
        self.toggle_behaviors_v4 = None
        self.toggle_specs_v4 = None
        self.recursive_behavior_v4 = None
        self.set_gsf_noaa_only_v4 = None
        self.submissionChecksv4 = QtWidgets.QGroupBox("Submission Checks v4")
        self.submissionChecksv4.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.submissionChecksv4)
        scv4_hbox = QtWidgets.QHBoxLayout()
        self.submissionChecksv4.setLayout(scv4_hbox)
        # -- parameters
        self.setParametersSCv4 = QtWidgets.QGroupBox("Parameters")
        self.setParametersSCv4.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        scv4_hbox.addWidget(self.setParametersSCv4)
        self._ui_parameters_scv4()
        # -- execution
        self.executeSCv4 = QtWidgets.QGroupBox("Execution")
        self.executeSCv4.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        scv4_hbox.addWidget(self.executeSCv4)
        self._ui_execute_scv4()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """Drop files directly onto the widget"""
        if e.mimeData().hasUrls:

            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()

            for url in e.mimeData().urls():

                # Workaround for OSx dragging and dropping
                dropped_folder = str(url.toLocalFile())
                logger.debug("dropped path: %s" % dropped_folder)

                if not os.path.isdir(dropped_folder):
                    msg = 'Drag-and-drop is only possible with existing folder path!\n\n' \
                          'Dropped path:\n' \
                          '%s' % dropped_folder
                    # noinspection PyCallByClass
                    QtWidgets.QMessageBox.critical(self, "Drag-and-drop Error", msg, QtWidgets.QMessageBox.Ok)
                    return

                self._add_roots(selection=dropped_folder)

        else:
            e.ignore()

    def click_add_roots(self):
        """ Read the folder provided by the user"""
        logger.debug('adding root folders ...')

        # ask the folder path to the user
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Add root folder",
                                                               QtCore.QSettings().value("survey_import_folder"))
        if selection == "":
            logger.debug('adding root folder: aborted')
            return

        logger.debug("added: %s" % selection)
        QtCore.QSettings().setValue("survey_import_folder", selection)
        self._add_roots(selection=selection)

    def _add_roots(self, selection):

        valid_folder = False

        is_opr = not self.set_non_opr_v4.isChecked()
        specs_version = self.toggle_specs_v4.value()
        if specs_version == 2020:
            specs_version = "2020"
        elif specs_version == 2021:
            specs_version = "2021"

        valid, err = self.parent_win.prj.is_valid_project_folder(selection, version=specs_version, opr=is_opr)
        if valid:
            valid_folder = True
        else:
            logger.debug("not a valid project folder: %s" % err)

        if not valid_folder:
            valid, err = self.parent_win.prj.is_valid_survey_folder(selection, version=specs_version, opr=is_opr)
            if valid:
                valid_folder = True
            else:
                logger.debug("not a valid survey folder: %s" % err)

        if not valid_folder:
            valid, err = self.parent_win.prj.is_valid_report_folder(selection, version=specs_version, opr=is_opr)
            if valid:
                valid_folder = True
            else:
                logger.debug("not a valid report folder: %s" % err)

        if not valid_folder:
            if is_opr:
                msg = 'The root folder (or its parent folder) is not in one of the supported prescribed formats: \n\n' \
                      '- project folder: "OPR-X###-XX-##"\n' \
                      '- survey folder: "X#####"\n' \
                      '- report folder: "Project_Reports"\n'
            else:
                msg = 'The root folder (or its parent folder) is not in one of the supported prescribed formats: \n\n' \
                      '- project folder: "X[..]-X###-XX-##"\n' \
                      '- survey folder: "X#####"\n' \
                      '- report folder: "Project_Reports"\n'
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Root Folder Error", msg, QtWidgets.QMessageBox.Ok)
            return

        # attempt to add the folder
        try:
            self.parent_win.prj.add_to_submission_list(selection)

        except Exception as e:  # more general case that catches all the exceptions
            msg = '<b>Error reading \"%s\".</b>' % selection
            msg += '<br><br><font color=\"red\">%s</font>' % e
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Submission Folder Error", msg, QtWidgets.QMessageBox.Ok)
            logger.debug('submission folder NOT added: %s' % selection)
            return

        self._update_root_folders()

    def _update_root_folders(self):
        """ update the submission folder list widget """
        submission_list = self.parent_win.prj.submission_list
        self.root_folders.clear()
        for folder in submission_list:

            new_item = QtWidgets.QListWidgetItem()
            if self.prj.is_valid_project_folder(folder)[0]:
                new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'project.png')))

            elif self.prj.is_valid_survey_folder(folder)[0]:
                new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'srv.png')))

            elif self.prj.is_valid_report_folder(folder)[0]:
                new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'report.png')))

            else:
                new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'folder.png')))

            new_item.setText(folder)
            new_item.setFont(GuiSettings.console_font())
            new_item.setForeground(GuiSettings.console_fg_color())
            self.root_folders.addItem(new_item)

    def make_roots_context_menu(self, pos):
        logger.debug('context menu')

        # check if any selection
        sel = self.root_folders.selectedItems()
        if len(sel) == 0:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.information(self, "Folder list",
                                              "You need to first add and select one or more folders!")
            return

        remove_act = QtWidgets.QAction("Remove", self, statusTip="Remove the selected submission folders",
                                       triggered=self.remove_submission_folders)

        menu = QtWidgets.QMenu(parent=self)
        menu.addAction(remove_act)
        menu.exec_(self.root_folders.mapToGlobal(pos))

    def remove_submission_folders(self):
        logger.debug("user want to remove submission folders")

        # remove all the selected folders from the list
        selections = self.root_folders.selectedItems()
        for selection in selections:
            self.prj.remove_from_submission_list(selection.text())

        self._update_root_folders()

    def click_clear_data(self):
        """ Clear all the read data"""
        logger.debug('clear data')
        self.root_folders.clear()
        self.prj.clear_submission_data()

    def click_open_output(self):
        """ Open output data folder """
        logger.debug('open output folder')
        self.prj.open_output_folder()

    # ------- v4 --------

    def _ui_parameters_scv4(self):
        params_vbox = QtWidgets.QVBoxLayout()
        self.setParametersSCv4.setLayout(params_vbox)
        params_vbox.addStretch()

        # knobs

        hbox = QtWidgets.QHBoxLayout()
        params_vbox.addLayout(hbox)
        hbox.addStretch()

        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()

        # knob row

        toggle_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # profiles
        self.toggle_profiles_v4 = QtWidgets.QDial()
        self.toggle_profiles_v4.setNotchesVisible(True)
        self.toggle_profiles_v4.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_profiles_v4.setRange(0, 1)
        self.toggle_profiles_v4.setValue(0)
        self.toggle_profiles_v4.setFixedSize(QtCore.QSize(48, 48))
        self.toggle_profiles_v4.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_profiles_v4)
        # spacing
        toggle_hbox.addSpacing(70)
        # behaviors
        self.toggle_behaviors_v4 = QtWidgets.QDial()
        self.toggle_behaviors_v4.setNotchesVisible(True)
        self.toggle_behaviors_v4.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_behaviors_v4.setRange(0, 1)
        self.toggle_behaviors_v4.setValue(0)
        self.toggle_behaviors_v4.setFixedSize(QtCore.QSize(48, 48))
        self.toggle_behaviors_v4.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_behaviors_v4)
        # spacing
        toggle_hbox.addSpacing(70)
        # specs
        self.toggle_specs_v4 = QtWidgets.QDial()
        self.toggle_specs_v4.setNotchesVisible(True)
        self.toggle_specs_v4.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_specs_v4.setRange(2020, 2021)
        self.toggle_specs_v4.setValue(2021)
        self.toggle_specs_v4.setFixedSize(QtCore.QSize(48, 48))
        self.toggle_specs_v4.setInvertedAppearance(False)
        toggle_hbox.addWidget(self.toggle_specs_v4)
        # noinspection PyUnresolvedReferences
        self.toggle_specs_v4.valueChanged.connect(self.changed_toggle_specs)
        # stretch
        toggle_hbox.addStretch()

        hbox.addStretch()

        # label row

        label_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # profiles
        label_hbox.addSpacing(20)
        text_0 = QtWidgets.QLabel("Field")
        text_0.setAlignment(QtCore.Qt.AlignLeft)
        text_0.setFixedWidth(35)
        label_hbox.addWidget(text_0)
        text_1 = QtWidgets.QLabel("Office")
        text_1.setAlignment(QtCore.Qt.AlignRight)
        text_1.setFixedWidth(35)
        label_hbox.addWidget(text_1)
        label_hbox.addSpacing(20)
        # behaviors
        label_hbox.addSpacing(1)
        text_0 = QtWidgets.QLabel("Recursive")
        text_0.setAlignment(QtCore.Qt.AlignLeft)
        text_0.setFixedWidth(54)
        label_hbox.addWidget(text_0)
        text_1 = QtWidgets.QLabel("Exhaustive")
        text_1.setAlignment(QtCore.Qt.AlignRight)
        text_1.setFixedWidth(54)
        label_hbox.addWidget(text_1)
        label_hbox.addSpacing(1)
        # specs
        label_hbox.addSpacing(20)
        text_0 = QtWidgets.QLabel("2020")
        text_0.setAlignment(QtCore.Qt.AlignLeft)
        text_0.setFixedWidth(35)
        label_hbox.addWidget(text_0)
        text_1 = QtWidgets.QLabel("2021+")
        text_1.setAlignment(QtCore.Qt.AlignRight)
        text_1.setFixedWidth(40)
        # text_1.setStyleSheet("QLabel { color :  rgba(200, 0, 0, 200); }")
        label_hbox.addWidget(text_1)
        label_hbox.addSpacing(5)
        # stretch
        label_hbox.addStretch()

        params_vbox.addSpacing(16)

        hbox = QtWidgets.QHBoxLayout()
        params_vbox.addLayout(hbox)
        hbox.addStretch()
        self.set_gsf_noaa_only_v4 = QtWidgets.QCheckBox("HXXXXX_GSF (NOAA only)")
        hbox.addWidget(self.set_gsf_noaa_only_v4)
        self.set_gsf_noaa_only_v4.setChecked(True)
        hbox.addStretch()

        params_vbox.addStretch()

    def _ui_execute_scv4(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeSCv4.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()

        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setText("Submission Checks")
        button.setToolTip('Check the submission data directory')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_submission_checks_v4)

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
        button.clicked.connect(self.click_open_manual_v4)

        hbox.addStretch()

    def changed_toggle_specs(self):
        self.set_gsf_noaa_only_v4.setEnabled(True)

    @classmethod
    def click_open_manual_v4(cls):
        logger.debug("open manual")
        Helper.explore_folder(
            "https://www.hydroffice.org/manuals/qctools/stable/user_manual_survey_submission_checks.html"
        )

    def click_submission_checks_v4(self):
        """trigger the submission checks v4"""
        self._click_submission_checks(4)

    def _click_submission_checks(self, version: int):
        """abstract the calling mechanism"""

        # sanity checks
        # - version
        if version not in [4, ]:
            raise RuntimeError("passed invalid version: %s" % version)
        # - list of folders (although the buttons should be never been enabled without a folder)
        if len(self.prj.submission_list) == 0:
            msg = "First add one or more submission folders!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Warning", msg, QtWidgets.QMessageBox.Ok)
            return

        self.parent_win.change_info_url(
            Helper(lib_info=lib_info).web_url(suffix="survey_submission_check_%d" % version))

        # for each file in the project grid list
        msg = "Errors/warnings per submission folder:\n"
        opened_folders = list()

        for i, path in enumerate(self.prj.submission_list):

            logger.debug("submission folder: %s" % path)

            # switcher between different versions of find fliers
            if version == 4:

                saved = self._submission_checks(path=path, version=version, idx=i, total=len(self.prj.submission_list))

            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Submission checks version: %s" % version)

            if not saved:
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.critical(self, "Error", "While checking submission: %s" % path,
                                               QtWidgets.QMessageBox.Ok)
                continue

            msg += "- %s:  %2d errors, %2d warnings   \n" % (self.prj.cur_root_name,
                                                             self.prj.number_of_submission_errors(),
                                                             self.prj.number_of_submission_warnings())

            # open the output folder (if not already open)
            # print("output folder: %s" % self.prj.submission_output_folder)
            if self.prj.submission_output_folder not in opened_folders:
                self.prj.open_submission_output_folder()
                opened_folders.append(self.prj.submission_output_folder)

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self,
                                          "Submission checks v%d [HSSD %s]" % (version, self.prj.cur_submission_hssd),
                                          msg, QtWidgets.QMessageBox.Ok)

    def _submission_checks(self, path, version, idx, total):
        """ Submission check for the passed path"""

        # GUI takes care of progress bar

        logger.debug('Submission checks v%d ...' % version)

        self.parent_win.progress.start(title="Submission checks v.%d" % version,
                                       text="Checking [%d/%d]" % (idx, total),
                                       init_value=10)

        saved = False

        try:

            if version == 4:

                is_opr = not self.set_non_opr_v4.isChecked()
                specs_version = self.toggle_specs_v4.value()
                recursive = self.toggle_behaviors_v4.value() == 0
                office = self.toggle_profiles_v4.value() == 1
                noaa_only = self.set_gsf_noaa_only_v4.isChecked()
                if specs_version == 2020:
                    saved = self.prj.submission_checks_v4(path=path, version="2020", recursive=recursive, office=office,
                                                          opr=is_opr, noaa_only=noaa_only)

                elif specs_version == 2021:
                    saved = self.prj.submission_checks_v4(path=path, version="2021", recursive=recursive, office=office,
                                                          opr=is_opr, noaa_only=noaa_only)

                else:
                    raise RuntimeError("unknown specs version: %s" % specs_version)

            else:
                self.parent_win.progress.end()
                RuntimeError("unknown Submission checks version: %s" % version)

        except Exception as e:
            self.parent_win.progress.end()
            logger.error("%s" % e)
            return False

        self.parent_win.progress.end()
        return saved
