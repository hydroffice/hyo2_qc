import os
import logging

from PySide2 import QtWidgets, QtGui, QtCore

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.survey.project import SurveyProject
from hyo2.qc.common.grid_callback.qt_grid_callback import QtGridCallback
from hyo2.qc.qctools.widgets.widget import AbstractWidget
from hyo2.qc.qctools.widgets.survey.inputs import InputsTab
from hyo2.qc.qctools.widgets.survey.fliers import FliersTab
from hyo2.qc.qctools.widgets.survey.holes import HolesTab
from hyo2.qc.qctools.widgets.survey.gridqa import GridQATab
from hyo2.qc.qctools.widgets.survey.scan import ScanTab
from hyo2.qc.qctools.widgets.survey.designated import DesignatedTab
from hyo2.qc.qctools.widgets.survey.valsou import ValsouTab
from hyo2.qc.qctools.widgets.survey.sbdare import SbdareTab
from hyo2.qc.qctools.widgets.survey.submission import SubmissionTab

logger = logging.getLogger(__name__)


class SurveyWidget(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # overloading

    def __init__(self, main_win):
        AbstractWidget.__init__(self, main_win=main_win)
        self.prj = SurveyProject(progress=QtProgress(parent=self))
        self.prj.set_callback(QtGridCallback(progress=self.prj.progress))

        # init default settings
        settings = QtCore.QSettings()
        # - import
        import_folder = settings.value("survey_import_folder")
        if (import_folder is None) or (not os.path.exists(import_folder)):
            settings.setValue("survey_import_folder", self.prj.output_folder)
        # - output folder
        export_folder = settings.value("survey_export_folder")
        if (export_folder is None) or (not os.path.exists(export_folder)):
            settings.setValue("survey_export_folder", self.prj.output_folder)
        else:  # folder exists
            self.prj.output_folder = export_folder
        # - shp
        export_shp = settings.value("survey_export_shp")
        if export_shp is None:
            settings.setValue("survey_export_shp", self.prj.output_shp)
        else:  # exists
            self.prj.output_shp = (export_shp == "true")
        # - kml
        export_kml = settings.value("survey_export_kml")
        if export_kml is None:
            settings.setValue("survey_export_kml", self.prj.output_kml)
        else:  # exists
            self.prj.output_kml = (export_kml == "true")
        # - subfolders
        export_subfolders = settings.value("survey_export_subfolders")
        if export_subfolders is None:
            settings.setValue("survey_export_subfolders", self.prj.output_subfolders)
        else:  # exists
            self.prj.output_subfolders = (export_subfolders == "true")
        # - project folder
        export_project_folder = settings.value("survey_export_project_folder")
        if export_project_folder is None:
            settings.setValue("survey_export_project_folder", self.prj.output_project_folder)
        else:  # exists
            self.prj.output_project_folder = (export_project_folder == "true")

        # make tabs
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setContentsMargins(0, 0, 0, 0)
        self.tabs.setIconSize(QtCore.QSize(36, 36))
        self.tabs.setTabPosition(QtWidgets.QTabWidget.South)

        # - inputs
        self.tab_inputs = InputsTab(parent_win=self, prj=self.prj)
        self.idx_inputs = self.tabs.insertTab(0, self.tab_inputs,
                                              QtGui.QIcon(os.path.join(self.media, 'inputs.png')), "")
        self.tabs.setTabToolTip(self.idx_inputs, "Data inputs")

        # - flier finder
        self.tab_fliers = FliersTab(parent_win=self, prj=self.prj)
        self.idx_fliers = self.tabs.insertTab(1, self.tab_fliers,
                                              QtGui.QIcon(os.path.join(self.media, 'fliers.png')), "")
        self.tabs.setTabToolTip(self.idx_fliers, "Detect fliers")
        self.tabs.setTabEnabled(self.idx_fliers, False)

        # - holiday finder
        self.tab_holes = HolesTab(parent_win=self, prj=self.prj)
        self.idx_holes = self.tabs.insertTab(2, self.tab_holes,
                                             QtGui.QIcon(os.path.join(self.media, 'holes.png')), "")
        self.tabs.setTabToolTip(self.idx_holes, "Detect holidays")
        self.tabs.setTabEnabled(self.idx_holes, False)

        # - grid qa
        self.tab_gridqa = GridQATab(parent_win=self, prj=self.prj)
        self.idx_gridqa = self.tabs.insertTab(3, self.tab_gridqa,
                                              QtGui.QIcon(os.path.join(self.media, 'gridqa.png')), "")
        self.tabs.setTabToolTip(self.idx_gridqa, "Grid QA")
        self.tabs.setTabEnabled(self.idx_gridqa, False)

        # - designated
        self.tab_designated = DesignatedTab(parent_win=self, prj=self.prj)
        self.idx_designated = self.tabs.insertTab(4, self.tab_designated,
                                                  QtGui.QIcon(os.path.join(self.media, 'designated.png')), "")
        self.tabs.setTabToolTip(self.idx_designated, "Scan designated (BAG only)")
        self.tabs.setTabEnabled(self.idx_designated, False)

        # - scan features
        self.tab_scan = ScanTab(parent_win=self, prj=self.prj)
        self.idx_scan = self.tabs.insertTab(6, self.tab_scan,
                                            QtGui.QIcon(os.path.join(self.media, 'scan_features.png')), "")
        self.tabs.setTabToolTip(self.idx_scan, "Scan features")
        self.tabs.setTabEnabled(self.idx_scan, False)

        # - VALSOU checks
        self.tab_valsou = ValsouTab(parent_win=self, prj=self.prj)
        self.idx_valsou = self.tabs.insertTab(7, self.tab_valsou,
                                              QtGui.QIcon(os.path.join(self.media, 'valsou.png')), "")
        self.tabs.setTabToolTip(self.idx_valsou, "VALSOU check")
        self.tabs.setTabEnabled(self.idx_valsou, False)

        # - SBDARE checks
        self.tab_sbdare = SbdareTab(parent_win=self, prj=self.prj)
        self.idx_sbdare = self.tabs.insertTab(8, self.tab_sbdare,
                                              QtGui.QIcon(os.path.join(self.media, 'sbdare.png')), "")
        self.tabs.setTabToolTip(self.idx_sbdare, "SBDARE export")
        self.tabs.setTabEnabled(self.idx_sbdare, False)

        # - Submission tests
        self.tab_submission = SubmissionTab(parent_win=self, prj=self.prj)
        self.idx_submission = self.tabs.insertTab(9, self.tab_submission,
                                                  QtGui.QIcon(os.path.join(self.media, 'submission.png')), "")
        self.tabs.setTabToolTip(self.idx_submission, "Submission checks")
        self.tabs.setTabEnabled(self.idx_submission, True)

        # noinspection PyUnresolvedReferences
        self.tabs.currentChanged.connect(self.change_tabs)

        # flags
        self.has_grid = False
        self.has_s57 = False

    def do(self):
        """DEBUGGING"""
        pass

    def grids_loaded(self):
        self.tabs.setTabEnabled(self.idx_fliers, True)
        self.tabs.setTabEnabled(self.idx_holes, True)
        self.tabs.setTabEnabled(self.idx_gridqa, True)
        if self.prj.has_bag_grid() and self.has_s57:
            self.tabs.setTabEnabled(self.idx_designated, True)
        else:
            self.tabs.setTabEnabled(self.idx_designated, False)
        if self.has_s57:
            self.tabs.setTabEnabled(self.idx_valsou, True)
        
        self.tab_fliers.grids_changed()
        self.has_grid = True

    def grids_unloaded(self):
        self.tabs.setTabEnabled(self.idx_fliers, False)
        self.tabs.setTabEnabled(self.idx_holes, False)
        self.tabs.setTabEnabled(self.idx_gridqa, False)
        self.tabs.setTabEnabled(self.idx_designated, False)
        self.tabs.setTabEnabled(self.idx_valsou, False)
        
        self.tab_fliers.grids_changed()
        self.has_grid = False

    def s57_loaded(self):

        self.tabs.setTabEnabled(self.idx_scan, True)
        self.tabs.setTabEnabled(self.idx_sbdare, True)
        if self.prj.has_bag_grid():
            self.tabs.setTabEnabled(self.idx_designated, True)
        else:
            self.tabs.setTabEnabled(self.idx_designated, False)
        if self.has_grid:
            self.tabs.setTabEnabled(self.idx_valsou, True)

        self.has_s57 = True

    def s57_unloaded(self):

        self.tabs.setTabEnabled(self.idx_scan, False)
        self.tabs.setTabEnabled(self.idx_sbdare, False)
        self.tabs.setTabEnabled(self.idx_valsou, False)

        self.has_s57 = False
