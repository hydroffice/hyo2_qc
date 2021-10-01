from PySide2 import QtWidgets, QtGui, QtCore

import os
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.grids.grids_manager import GridsManager

logger = logging.getLogger(__name__)


class InputsTab(QtWidgets.QMainWindow):
    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win, prj):
        QtWidgets.QMainWindow.__init__(self)
        # Enable dragging and dropping onto the GUI
        self.setAcceptDrops(True)

        # store a project reference
        self.prj = prj
        self.parent_win = parent_win

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        self.loadData = QtWidgets.QGroupBox("Data inputs  [drag-and-drop to add, right click to drop files]")
        # self.loadData.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.loadData)

        vbox = QtWidgets.QVBoxLayout()
        self.loadData.setLayout(vbox)

        # add grids
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_add_grids = QtWidgets.QLabel("Grid files:")
        hbox.addWidget(text_add_grids)
        # text_add_grids.setFixedHeight(GuiSettings.single_line_height())
        text_add_grids.setMinimumWidth(64)
        self.input_grids = QtWidgets.QListWidget()
        hbox.addWidget(self.input_grids)
        self.input_grids.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.input_grids.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.input_grids.customContextMenuRequested.connect(self.make_grids_context_menu)
        self.input_grids.setAlternatingRowColors(True)
        vbox_buttons = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox_buttons)
        vbox_buttons.addStretch()
        button_add_file_grids = QtWidgets.QPushButton()
        vbox_buttons.addWidget(button_add_file_grids)
        button_add_file_grids.setFixedHeight(36)
        button_add_file_grids.setFixedWidth(36)
        button_add_file_grids.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'add_files.png')))
        button_add_file_grids.setToolTip('Add (or drag-and-drop) BAG and CSAR files')
        # noinspection PyUnresolvedReferences
        button_add_file_grids.clicked.connect(self.click_add_file_grids)
        button_add_folder_grids = QtWidgets.QPushButton()
        vbox_buttons.addWidget(button_add_folder_grids)
        button_add_folder_grids.setFixedHeight(36)
        button_add_folder_grids.setFixedWidth(36)
        button_add_folder_grids.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'add_folder.png')))
        button_add_folder_grids.setToolTip('Add (or drag-and-drop) a Kluster Grid folder')
        # noinspection PyUnresolvedReferences
        button_add_folder_grids.clicked.connect(self.click_add_folder_grids)
        vbox_buttons.addStretch()

        # add s57
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_add_s57 = QtWidgets.QLabel("S57 files:")
        hbox.addWidget(text_add_s57)
        text_add_s57.setFixedHeight(GuiSettings.single_line_height())
        text_add_s57.setMinimumWidth(64)
        self.input_s57 = QtWidgets.QListWidget()
        hbox.addWidget(self.input_s57)
        self.input_s57.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.input_s57.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.input_s57.customContextMenuRequested.connect(self.make_s57_context_menu)
        self.input_s57.setAlternatingRowColors(True)
        button_add_s57 = QtWidgets.QPushButton()
        hbox.addWidget(button_add_s57)
        button_add_s57.setFixedHeight(GuiSettings.single_line_height())
        button_add_s57.setFixedWidth(GuiSettings.single_line_height())
        button_add_s57.setFixedHeight(36)
        button_add_s57.setFixedWidth(36)
        button_add_s57.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'add_files.png')))
        button_add_s57.setToolTip('Add (or drag-and-drop) S57 feature files')
        # noinspection PyUnresolvedReferences
        button_add_s57.clicked.connect(self.click_add_s57)

        vbox.addSpacing(12)

        # clear data
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        button_clear_data = QtWidgets.QPushButton()
        hbox.addWidget(button_clear_data)
        button_clear_data.setFixedHeight(GuiSettings.single_line_height())
        # button_clear_data.setFixedWidth(GuiSettings.single_line_height())
        button_clear_data.setText("Clear data")
        button_clear_data.setToolTip('Clear all data loaded')
        # noinspection PyUnresolvedReferences
        button_clear_data.clicked.connect(self.click_clear_data)
        hbox.addStretch()

        self.vbox.addStretch()
        self.vbox.addStretch()

        # data outputs
        self.savedData = QtWidgets.QGroupBox("Data outputs [drag-and-drop the desired output folder]")
        self.savedData.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.savedData.setMaximumHeight(GuiSettings.single_line_height() * 8)
        self.vbox.addWidget(self.savedData)

        vbox = QtWidgets.QVBoxLayout()
        self.savedData.setLayout(vbox)

        # set optional formats
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_set_formats = QtWidgets.QLabel("Formats:")
        hbox.addWidget(text_set_formats)
        text_set_formats.setFixedHeight(GuiSettings.single_line_height())
        text_set_formats.setMinimumWidth(64)
        self.output_pdf = QtWidgets.QCheckBox("PDF")
        self.output_pdf.setChecked(True)
        self.output_pdf.setDisabled(True)
        hbox.addWidget(self.output_pdf)
        self.output_s57 = QtWidgets.QCheckBox("S57")
        self.output_s57.setChecked(True)
        self.output_s57.setDisabled(True)
        hbox.addWidget(self.output_s57)
        self.output_shp = QtWidgets.QCheckBox("Shapefile")
        self.output_shp.setToolTip('Activate/deactivate the creation of Shapefiles in output')
        self.output_shp.setChecked(self.prj.output_shp)
        # noinspection PyUnresolvedReferences
        self.output_shp.clicked.connect(self.click_output_shp)
        hbox.addWidget(self.output_shp)
        self.output_kml = QtWidgets.QCheckBox("KML")
        self.output_kml.setToolTip('Activate/deactivate the creation of KML files in output')
        self.output_kml.setChecked(self.prj.output_kml)
        # noinspection PyUnresolvedReferences
        self.output_kml.clicked.connect(self.click_output_kml)
        hbox.addWidget(self.output_kml)

        hbox.addSpacing(36)

        text_set_prj_folder = QtWidgets.QLabel("Create project folder: ")
        hbox.addWidget(text_set_prj_folder)
        text_set_prj_folder.setFixedHeight(GuiSettings.single_line_height())
        self.output_prj_folder = QtWidgets.QCheckBox("")
        self.output_prj_folder.setToolTip('Create a sub-folder with project name')
        self.output_prj_folder.setChecked(self.prj.output_project_folder)
        # noinspection PyUnresolvedReferences
        self.output_prj_folder.clicked.connect(self.click_output_project_folder)
        hbox.addWidget(self.output_prj_folder)

        text_set_subfolders = QtWidgets.QLabel("Per-tool sub-folders: ")
        hbox.addWidget(text_set_subfolders)
        text_set_subfolders.setFixedHeight(GuiSettings.single_line_height())
        self.output_subfolders = QtWidgets.QCheckBox("")
        self.output_subfolders.setToolTip('Create a sub-folder for each tool')
        self.output_subfolders.setChecked(self.prj.output_subfolders)
        # noinspection PyUnresolvedReferences
        self.output_subfolders.clicked.connect(self.click_output_subfolders)
        hbox.addWidget(self.output_subfolders)

        hbox.addStretch()

        # add folder
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_add_folder = QtWidgets.QLabel("Folder:")
        hbox.addWidget(text_add_folder)
        text_add_folder.setMinimumWidth(64)
        self.output_folder = QtWidgets.QListWidget()
        hbox.addWidget(self.output_folder)
        self.output_folder.setMinimumHeight(GuiSettings.single_line_height())
        self.output_folder.setMaximumHeight(GuiSettings.single_line_height() * 2)
        self.output_folder.clear()
        new_item = QtWidgets.QListWidgetItem()
        new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'folder.png')))
        new_item.setText("%s" % os.path.abspath(self.prj.output_folder).replace("\\", "/"))
        new_item.setFont(GuiSettings.console_font())
        new_item.setForeground(GuiSettings.console_fg_color())
        self.output_folder.addItem(new_item)
        button_add_folder = QtWidgets.QPushButton()
        hbox.addWidget(button_add_folder)
        button_add_folder.setFixedHeight(36)
        button_add_folder.setFixedWidth(36)
        button_add_folder.setText(" ... ")
        button_add_folder.setToolTip('Add (or drag-and-drop) output folder')
        # noinspection PyUnresolvedReferences
        button_add_folder.clicked.connect(self.click_add_folder)

        # open folder
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        button_default_output = QtWidgets.QPushButton()
        hbox.addWidget(button_default_output)
        button_default_output.setFixedHeight(GuiSettings.single_line_height())
        # button_open_output.setFixedWidth(GuiSettings.single_line_height())
        button_default_output.setText("Use default")
        button_default_output.setToolTip('Use the default output folder')
        # noinspection PyUnresolvedReferences
        button_default_output.clicked.connect(self.click_default_output)

        button_open_output = QtWidgets.QPushButton()
        hbox.addWidget(button_open_output)
        button_open_output.setFixedHeight(GuiSettings.single_line_height())
        # button_open_output.setFixedWidth(GuiSettings.single_line_height())
        button_open_output.setText("Open folder")
        button_open_output.setToolTip('Open the output folder')
        # noinspection PyUnresolvedReferences
        button_open_output.clicked.connect(self.click_open_output)

        hbox.addStretch()

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
            # Workaround for OSx dragging and dropping
            for url in e.mimeData().urls():
                dropped_path = str(url.toLocalFile())
                dropped_path = os.path.abspath(dropped_path).replace("\\", "/")

                logger.debug("dropped path: %s" % dropped_path)
                if os.path.isdir(dropped_path):
                    if GridsManager.is_kluster_path(dropped_path):
                        self._add_grids(selection=dropped_path)
                    else:
                        self._add_folder(selection=dropped_path)

                elif os.path.splitext(dropped_path)[-1] in (".bag", ".csar"):
                    self._add_grids(selection=dropped_path)

                elif os.path.splitext(dropped_path)[-1] in (".000",):
                    self._add_s57(selection=dropped_path)

                else:
                    msg = 'Drag-and-drop is only possible with a single folder or the following file extensions:\n' \
                          '- grid files: .csar or .bag\n' \
                          '- feature files: .000\n\n' \
                          'Dropped path:\n' \
                          '%s' % dropped_path
                    # noinspection PyCallByClass
                    QtWidgets.QMessageBox.critical(self, "Drag-and-drop Error", msg, QtWidgets.QMessageBox.Ok)
        else:
            e.ignore()

    def click_add_file_grids(self):
        """ Read the grids provided by the user"""
        logger.debug('adding grids from file ...')

        # ask the file path to the user
        # selections, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
        # "Add grids", QtCore.QSettings().value("survey_import_folder"),
        #                                                    "BAG file (*.bag);;CSAR file (*.csar);;All files (*.*)")
        # noinspection PyCallByClass
        selections, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Add grids",
                                                               QtCore.QSettings().value("survey_import_folder"),
                                                               "Supported grids (*.bag *.csar);;BAG file (*.bag);;"
                                                               "CSAR file (*.csar);;All files (*.*)")
        if len(selections) == 0:
            logger.debug('adding grids: aborted')
            return
        last_open_folder = os.path.dirname(selections[0])
        if os.path.exists(last_open_folder):
            QtCore.QSettings().setValue("survey_import_folder", last_open_folder)

        for selection in selections:
            self._add_grids(selection=os.path.abspath(selection).replace("\\", "/"))

    def click_add_folder_grids(self):
        """ Read the grids provided by the user"""
        logger.debug('adding grids from folder ...')

        # ask the folder path to the user
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Add Kluster Grid folder",
                                                                   QtCore.QSettings().value("survey_import_folder"),
                                                                   QtWidgets.QFileDialog.ShowDirsOnly)
        if selection == str():
            logger.debug('adding grids: aborted')
            return

        if not GridsManager.is_kluster_path(selection):
            msg = "The folder %s is not a Kluster Grid" % selection
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Data Reading Error", msg, QtWidgets.QMessageBox.Ok)
            logger.debug('folder NOT added: %s' % selection)

        last_open_folder = os.path.dirname(selection)
        if os.path.exists(last_open_folder):
            QtCore.QSettings().setValue("survey_import_folder", last_open_folder)

        self._add_grids(selection=os.path.abspath(selection).replace("\\", "/"))

    def _add_grids(self, selection):

        # attempt to read the data
        try:
            self.parent_win.prj.add_to_grid_list(selection)

        except Exception as e:  # more general case that catches all the exceptions
            msg = '<b>Error reading \"%s\".</b>' % selection
            msg += '<br><br><font color=\"red\">%s</font>' % e
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Data Reading Error", msg, QtWidgets.QMessageBox.Ok)
            logger.debug('surface NOT added: %s' % selection)
            return

        self._update_input_grid_list()
        self.parent_win.grids_loaded()

    def _update_input_grid_list(self):
        """ update the grid list widget """
        grid_list = self.parent_win.prj.grid_list
        self.input_grids.clear()
        for grid in grid_list:
            new_item = QtWidgets.QListWidgetItem()
            if os.path.splitext(grid)[-1] == ".bag":
                new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'bag.png')))
            elif os.path.splitext(grid)[-1] == ".csar":
                new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'csar.png')))
            elif GridsManager.is_kluster_path(grid):
                new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'kluster.png')))
            new_item.setText(grid)
            new_item.setFont(GuiSettings.console_font())
            new_item.setForeground(GuiSettings.console_fg_color())
            self.input_grids.addItem(new_item)

    def make_grids_context_menu(self, pos):
        logger.debug('context menu')

        # check if any selection
        sel = self.input_grids.selectedItems()
        if len(sel) == 0:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.information(self, "Grid list", "You need to first add and select one or more files!")
            return

        remove_act = QtWidgets.QAction("Remove", self, statusTip="Remove the selected grid files",
                                       triggered=self.remove_grid_files)

        menu = QtWidgets.QMenu(parent=self)
        menu.addAction(remove_act)
        menu.exec_(self.input_grids.mapToGlobal(pos))

    def remove_grid_files(self):
        logger.debug("user want to remove grid files")

        # remove all the selected files from the list
        selections = self.input_grids.selectedItems()
        for selection in selections:
            self.prj.remove_from_grid_list(selection.text())

        self._update_input_grid_list()
        if len(self.parent_win.prj.grid_list) == 0:
            self.parent_win.grids_unloaded()
        else:
            self.parent_win.grids_loaded()

    def click_add_s57(self):
        """ Read the S57 files provided by the user"""
        logger.debug('adding s57 features from file ...')

        # ask the file path to the user
        # noinspection PyCallByClass
        selections, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Add S57 features",
                                                               QtCore.QSettings().value("survey_import_folder"),
                                                               "S57 file (*.000);;All files (*.*)")
        if len(selections) == 0:
            logger.debug('adding s57: aborted')
            return
        last_open_folder = os.path.dirname(selections[0])
        if os.path.exists(last_open_folder):
            QtCore.QSettings().setValue("survey_import_folder", last_open_folder)

        for selection in selections:
            selection = os.path.abspath(selection).replace("\\", "/")
            self._add_s57(selection=selection)

    def _add_s57(self, selection):

        # attempt to read the data
        try:
            self.parent_win.prj.add_to_s57_list(selection)

        except Exception as e:  # more general case that catches all the exceptions
            msg = '<b>Error reading \"%s\".</b>' % selection
            msg += '<br><br><font color=\"red\">%s</font>' % e
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Data Reading Error", msg, QtWidgets.QMessageBox.Ok)
            logger.debug('s57 file NOT added: %s' % selection)
            return

        self._update_input_s57_list()
        self.parent_win.s57_loaded()

    def _update_input_s57_list(self):
        """ update the s57 list widget """
        s57_list = self.parent_win.prj.s57_list
        self.input_s57.clear()
        for s57 in s57_list:
            new_item = QtWidgets.QListWidgetItem()
            if os.path.splitext(s57)[-1] == ".000":
                new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 's57.png')))
            new_item.setText(s57)
            new_item.setFont(GuiSettings.console_font())
            new_item.setForeground(GuiSettings.console_fg_color())
            self.input_s57.addItem(new_item)

    def make_s57_context_menu(self, pos):
        logger.debug('context menu')

        # check if any selection
        sel = self.input_s57.selectedItems()
        if len(sel) == 0:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.information(self, "S57 list", "You need to first add and select one or more files!")
            return

        remove_act = QtWidgets.QAction("Remove", self, statusTip="Remove the selected S57 files",
                                       triggered=self.remove_s57_files)

        menu = QtWidgets.QMenu(parent=self)
        menu.addAction(remove_act)
        menu.exec_(self.input_s57.mapToGlobal(pos))

    def remove_s57_files(self):
        logger.debug("user want to remove S57 files")

        # remove all the selected files from the list
        selections = self.input_s57.selectedItems()
        for selection in selections:
            selection = os.path.abspath(selection.text()).replace("\\", "/")
            self.prj.remove_from_s57_list(selection)

        self._update_input_s57_list()
        if len(self.parent_win.prj.s57_list) == 0:
            self.parent_win.s57_unloaded()
        else:
            self.parent_win.s57_loaded()

    def click_clear_data(self):
        """ Clear all the read data"""
        logger.debug('clear data')
        self.parent_win.prj.clear_data()
        self.input_grids.clear()
        self.parent_win.grids_unloaded()
        self.input_s57.clear()
        self.parent_win.s57_unloaded()

    def click_output_kml(self):
        """ Set the KML output"""
        self.prj.output_kml = self.output_kml.isChecked()
        QtCore.QSettings().setValue("survey_export_kml", self.prj.output_kml)

    def click_output_shp(self):
        """ Set the Shapefile output"""
        self.prj.output_shp = self.output_shp.isChecked()
        QtCore.QSettings().setValue("survey_export_shp", self.prj.output_shp)

    def click_output_project_folder(self):
        """ Set the output project folder"""
        self.prj.output_project_folder = self.output_prj_folder.isChecked()
        QtCore.QSettings().setValue("survey_export_project_folder", self.prj.output_project_folder)

    def click_output_subfolders(self):
        """ Set the output in sub-folders"""
        self.prj.output_subfolders = self.output_subfolders.isChecked()
        QtCore.QSettings().setValue("survey_export_subfolders", self.prj.output_subfolders)

    def click_add_folder(self):
        """ Read the grids provided by the user"""
        logger.debug('set output folder ...')

        # ask the output folder
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Set output folder",
                                                               QtCore.QSettings().value("survey_export_folder"), )
        if selection == "":
            logger.debug('setting output folder: aborted')
            return
        logger.debug("selected path: %s" % selection)

        self._add_folder(os.path.abspath(selection).replace("\\", "/"))

    def _add_folder(self, selection):

        path_len = len(selection)
        logger.debug("folder path length: %d" % path_len)
        if path_len > 140:

            msg = 'The selected path is %d characters long. ' \
                  'This may trigger the filename truncation of generated outputs (max allowed path length: 260).\n\n' \
                  'Do you really want to use: %s?' % (path_len, selection)
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Output folder")
            msg_box.setText(msg)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
            reply = msg_box.exec_()

            if reply == QtWidgets.QMessageBox.No:
                return

        # attempt to read the data
        try:
            self.prj.output_folder = selection

        except Exception as e:  # more general case that catches all the exceptions
            msg = '<b>Error setting the output folder to \"%s\".</b>' % selection
            msg += '<br><br><font color=\"red\">%s</font>' % e
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Output Folder Error", msg, QtWidgets.QMessageBox.Ok)
            logger.debug('output folder NOT set: %s' % selection)
            return

        self.output_folder.clear()
        new_item = QtWidgets.QListWidgetItem()
        new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'folder.png')))
        new_item.setText("%s" % self.prj.output_folder)
        new_item.setFont(GuiSettings.console_font())
        new_item.setForeground(GuiSettings.console_fg_color())
        self.output_folder.addItem(new_item)

        QtCore.QSettings().setValue("survey_export_folder", self.prj.output_folder)

        logger.debug("new output folder: %s" % self.prj.output_folder)

    def click_default_output(self):
        """ Set default output data folder """
        self._add_folder(selection=self.prj.default_output_folder())

    def click_open_output(self):
        """ Open output data folder """
        logger.debug('open output folder: %s' % self.prj.output_folder)
        self.prj.open_output_folder()
