import os
import logging

from PySide2 import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)

from hyo2.qc.chart.project import ChartProject
from hyo2.qc.qctools.qt_progress import QtProgress
from hyo2.qc.common.grid_callback.qt_grid_callback import QtGridCallback
from hyo2.qc.qctools.widgets.widget import AbstractWidget
from hyo2.qc.qctools.widgets.chart.inputs import InputsTab
from hyo2.qc.qctools.widgets.chart.grid_truncate import GridTruncateTab
from hyo2.qc.qctools.widgets.chart.grid_xyz import GridXyzTab
from hyo2.qc.qctools.widgets.chart.s57_truncate import S57TruncateTab
from hyo2.qc.qctools.widgets.chart.scan import ScanTab
from hyo2.qc.qctools.widgets.chart.triangle import TriangleTab


class ChartWidget(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # overloading

    def __init__(self, main_win):
        AbstractWidget.__init__(self, main_win=main_win)
        self.prj = ChartProject(progress=QtProgress(parent=self))
        self.prj.set_callback(QtGridCallback(progress=self.prj.progress))

        # init default settings
        settings = QtCore.QSettings()
        # - import
        import_folder = settings.value("chart_import_folder")
        if (import_folder is None) or (not os.path.exists(import_folder)):
            settings.setValue("chart_import_folder", self.prj.output_folder)
        # - output folder
        export_folder = settings.value("chart_export_folder")
        if (export_folder is None) or (not os.path.exists(export_folder)):
            settings.setValue("chart_export_folder", self.prj.output_folder)
        else:  # folder exists
            self.prj.output_folder = export_folder
        # - shp
        export_shp = settings.value("chart_export_shp")
        if export_shp is None:
            settings.setValue("chart_export_shp", self.prj.output_shp)
        else:  # exists
            self.prj.output_shp = (export_shp == "true")
        # - kml
        export_kml = settings.value("chart_export_kml")
        if export_kml is None:
            settings.setValue("chart_export_kml", self.prj.output_kml)
        else:  # exists
            self.prj.output_kml = (export_kml == "true")
        # - subfolders
        export_subfolders = settings.value("chart_export_subfolders")
        if export_subfolders is None:
            settings.setValue("chart_export_subfolders", self.prj.output_subfolders)
        else:  # exists
            self.prj.output_subfolders = (export_subfolders == "true")
        # - project folder
        export_project_folder = settings.value("chart_export_project_folder")
        if export_project_folder is None:
            settings.setValue("chart_export_project_folder", self.prj.output_project_folder)
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

        # - grid truncate
        self.tab_grid_truncate = GridTruncateTab(parent_win=self, prj=self.prj)
        self.idx_grid_truncate = self.tabs.insertTab(1, self.tab_grid_truncate,
                                                     QtGui.QIcon(os.path.join(self.media, 'grid_truncate.png')), "")
        self.tabs.setTabToolTip(self.idx_grid_truncate, "Grid truncate")
        self.tabs.setTabEnabled(self.idx_grid_truncate, False)

        # - grid xyz
        self.tab_grid_xyz = GridXyzTab(parent_win=self, prj=self.prj)
        self.idx_grid_xyz = self.tabs.insertTab(2, self.tab_grid_xyz,
                                                QtGui.QIcon(os.path.join(self.media, 'grid_xyz.png')), "")
        self.tabs.setTabToolTip(self.idx_grid_xyz, "Grid xyz")
        self.tabs.setTabEnabled(self.idx_grid_xyz, False)

        # - S57 truncate
        self.tab_s57_truncate = S57TruncateTab(parent_win=self, prj=self.prj)
        self.idx_s57_truncate = self.tabs.insertTab(3, self.tab_s57_truncate,
                                                    QtGui.QIcon(os.path.join(self.media, 's57_truncate.png')), "")
        self.tabs.setTabToolTip(self.idx_s57_truncate, "S57 truncate")
        self.tabs.setTabEnabled(self.idx_s57_truncate, False)

        # - scan features
        self.tab_scan = ScanTab(parent_win=self, prj=self.prj)
        self.idx_scan = self.tabs.insertTab(4, self.tab_scan,
                                            QtGui.QIcon(os.path.join(self.media, 'scan_features.png')), "")
        self.tabs.setTabToolTip(self.idx_scan, "Scan features")
        self.tabs.setTabEnabled(self.idx_scan, False)

        # - triangle
        self.tab_triangle = TriangleTab(parent_win=self, prj=self.prj)
        self.idx_triangle = self.tabs.insertTab(5, self.tab_triangle,
                                                QtGui.QIcon(os.path.join(self.media, 'triangle.png')), "")
        self.tabs.setTabToolTip(self.idx_triangle, "Triangle Rule")
        self.tabs.setTabEnabled(self.idx_triangle, False)

        # noinspection PyUnresolvedReferences
        self.tabs.currentChanged.connect(self.change_tabs)

        # flags
        self.has_grid = False
        self.has_s57 = False
        self.has_ss = False

    def do(self):
        """DEBUGGING"""
        pass

    def grids_loaded(self):
        if self.prj.has_bag_grid():
            self.tabs.setTabEnabled(self.idx_grid_truncate, True)
            self.tabs.setTabEnabled(self.idx_grid_xyz, True)
        self.has_grid = True

    def grids_unloaded(self):
        self.tabs.setTabEnabled(self.idx_grid_truncate, False)
        self.tabs.setTabEnabled(self.idx_grid_xyz, False)
        self.has_grid = False

    def s57_loaded(self):
        self.tabs.setTabEnabled(self.idx_s57_truncate, True)
        self.tabs.setTabEnabled(self.idx_scan, True)
        self.has_s57 = True
        if self.has_ss:
            self.tabs.setTabEnabled(self.idx_triangle, True)

    def s57_unloaded(self):
        self.tabs.setTabEnabled(self.idx_scan, False)
        self.tabs.setTabEnabled(self.idx_s57_truncate, False)
        if self.has_grid is False:
            self.tabs.setTabEnabled(self.idx_triangle, False)
        self.has_s57 = False

    def ss_loaded(self):
        self.has_ss = True
        if self.has_s57:
            self.tabs.setTabEnabled(self.idx_triangle, True)
    
    def ss_unloaded(self):
        self.has_ss = False
        self.tabs.setTabEnabled(self.idx_triangle, False)
