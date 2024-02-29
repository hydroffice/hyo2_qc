import logging
import os

from PySide2 import QtWidgets, QtGui, QtCore
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qc.common.grid_callback.qt_grid_callback import QtGridCallback
from hyo2.qc.qctools.widgets.survey.bag_checks_tab import BAGChecksTab
from hyo2.qc.qctools.widgets.survey.designated_scan_tab import DesignatedScanTab
from hyo2.qc.qctools.widgets.survey.flier_finder_tab import FlierFinderTab
from hyo2.qc.qctools.widgets.survey.grid_qa_tab import GridQATab
from hyo2.qc.qctools.widgets.survey.holiday_finder_tab import HolidayFinderTab
from hyo2.qc.qctools.widgets.survey.inputs_tab import InputsTab
from hyo2.qc.qctools.widgets.survey.sbdare_export_tab import SBDAREExportTab
from hyo2.qc.qctools.widgets.survey.feature_scan_tab import FeatureScanTab
from hyo2.qc.qctools.widgets.survey.submission_checks_tab import SubmissionChecksTab
from hyo2.qc.qctools.widgets.survey.valsou_checks_tab import ValsouChecksTab
from hyo2.qc.qctools.widgets.widget import AbstractWidget
from hyo2.qc.survey.project import SurveyProject

logger = logging.getLogger(__name__)


class SurveyWidget(AbstractWidget):

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
        # noinspection PyArgumentList
        self.idx_inputs = self.tabs.insertTab(0, self.tab_inputs,
                                              QtGui.QIcon(os.path.join(self.media, 'inputs.png')), "")
        self.tabs.setTabToolTip(self.idx_inputs, "Data inputs")

        # - flier finder
        self.tab_fliers = FlierFinderTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_fliers = self.tabs.insertTab(1, self.tab_fliers,
                                              QtGui.QIcon(os.path.join(self.media, 'fliers.png')), "")
        self.tabs.setTabToolTip(self.idx_fliers, "Flier Finder")
        self.tabs.setTabEnabled(self.idx_fliers, False)

        # - holiday finder
        self.tab_holes = HolidayFinderTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_holes = self.tabs.insertTab(3, self.tab_holes,
                                             QtGui.QIcon(os.path.join(self.media, 'holes.png')), "")
        self.tabs.setTabToolTip(self.idx_holes, "Holiday Finder")
        self.tabs.setTabEnabled(self.idx_holes, False)

        # - grid qa
        self.tab_gridqa = GridQATab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_gridqa = self.tabs.insertTab(4, self.tab_gridqa,
                                              QtGui.QIcon(os.path.join(self.media, 'gridqa.png')), "")
        self.tabs.setTabToolTip(self.idx_gridqa, "Grid QA")
        self.tabs.setTabEnabled(self.idx_gridqa, False)

        # - bag checks
        self.tab_bag_checks = BAGChecksTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_bag_checks = self.tabs.insertTab(5, self.tab_bag_checks,
                                                  QtGui.QIcon(os.path.join(self.media, 'bag_checks.png')), "")
        self.tabs.setTabToolTip(self.idx_bag_checks, "BAG Checks")
        self.tabs.setTabEnabled(self.idx_bag_checks, False)

        # - designated
        self.tab_designated = DesignatedScanTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_designated = self.tabs.insertTab(6, self.tab_designated,
                                                  QtGui.QIcon(os.path.join(self.media, 'designated.png')), "")
        self.tabs.setTabToolTip(self.idx_designated, "Designated Scan (BAG only)")
        self.tabs.setTabEnabled(self.idx_designated, False)

        # - scan features
        self.tab_scan = FeatureScanTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_scan = self.tabs.insertTab(7, self.tab_scan,
                                            QtGui.QIcon(os.path.join(self.media, 'scan_features.png')), "")
        self.tabs.setTabToolTip(self.idx_scan, "Feature Scan")
        self.tabs.setTabEnabled(self.idx_scan, False)

        # - VALSOU checks
        self.tab_valsou = ValsouChecksTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_valsou = self.tabs.insertTab(8, self.tab_valsou,
                                              QtGui.QIcon(os.path.join(self.media, 'valsou.png')), "")
        self.tabs.setTabToolTip(self.idx_valsou, "VALSOU Checks")
        self.tabs.setTabEnabled(self.idx_valsou, False)

        # - SBDARE checks
        self.tab_sbdare = SBDAREExportTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_sbdare = self.tabs.insertTab(9, self.tab_sbdare,
                                              QtGui.QIcon(os.path.join(self.media, 'sbdare.png')), "")
        self.tabs.setTabToolTip(self.idx_sbdare, "SBDARE Export")
        self.tabs.setTabEnabled(self.idx_sbdare, False)

        # - Submission tests
        self.tab_submission = SubmissionChecksTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_submission = self.tabs.insertTab(10, self.tab_submission,
                                                  QtGui.QIcon(os.path.join(self.media, 'submission.png')), "")
        self.tabs.setTabToolTip(self.idx_submission, "Submission Checks")
        self.tabs.setTabEnabled(self.idx_submission, True)

        # noinspection PyUnresolvedReferences
        self.tabs.currentChanged.connect(self.change_tabs)

        # flags
        self.has_grid = False
        self.has_s57 = False

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()
        if event.modifiers() == QtCore.Qt.ControlModifier:
            # logger.debug("pressed CTRL + %s" % key)
            if key == QtCore.Qt.Key_T:
                settings = QtCore.QSettings()
                ret = settings.value("splash_screen", 1)
                if ret == 1:
                    settings.setValue("splash_screen", 0)
                    logger.info('Splash-screen: OFF')
                else:
                    settings.setValue("splash_screen", 1)
                    logger.info('Splash-screen: ON')
                return
        return super(SurveyWidget, self).keyPressEvent(event)

    def do(self):
        """DEBUGGING"""
        pass

    def grids_loaded(self):
        self.tabs.setTabEnabled(self.idx_fliers, True)
        if self.prj.has_kluster_grid():
            self.tabs.setTabEnabled(self.idx_holes, False)
        else:
            self.tabs.setTabEnabled(self.idx_holes, True)
        self.tabs.setTabEnabled(self.idx_gridqa, True)
        if self.prj.has_bag_grid():
            self.tabs.setTabEnabled(self.idx_bag_checks, True)
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
        self.tabs.setTabEnabled(self.idx_bag_checks, False)
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
