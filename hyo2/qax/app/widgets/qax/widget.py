import os
from pathlib import Path
import logging

from PySide2 import QtGui, QtCore, QtWidgets

from hyo2.abc.app.qt_progress import QtProgress

from hyo2.qax.app.widgets.widget import AbstractWidget
# from hyo2.ca.enc.project import ENCProject
from hyo2.qax.app.widgets.qax.main_tab import MainTab
# from hyo2.ca.catools.widgets.enc.ss_vs_chart_tab import SSvsChartTab
# from hyo2.ca.catools.widgets.enc.sounding_selection_tab import SoundingSelectionTab
# from hyo2.ca.catools.widgets.enc.dtm_vs_chart_tab import DTMvsChartTab

logger = logging.getLogger(__name__)


class QAXWidget(AbstractWidget):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # overloading

    def __init__(self, main_win):
        AbstractWidget.__init__(self, main_win=main_win)
        # self.prj = ENCProject(progress=QtProgress(parent=self))

        # # init default settings
        # settings = QtCore.QSettings()
        # # - output folder
        # export_folder = settings.value("enc_export_folder")
        # if (export_folder is None) or (not os.path.exists(export_folder)):
        #     settings.setValue("enc_export_folder", str(self.prj.output_folder))
        # else:  # folder exists
        #     self.prj.output_folder = Path(export_folder)
        # # - shp
        # export_shp = settings.value("enc_export_shp")
        # if export_shp is None:
        #     settings.setValue("enc_export_shp", self.prj.output_shp)
        # else:  # exists
        #     self.prj.output_shp = (export_shp == "true")
        # # - kml
        # export_kml = settings.value("enc_export_kml")
        # if export_kml is None:
        #     settings.setValue("enc_export_kml", self.prj.output_kml)
        # else:  # exists
        #     self.prj.output_kml = (export_kml == "true")
        # # - import
        # import_folder = settings.value("ss_import_folder")
        # if (import_folder is None) or (not os.path.exists(import_folder)):
        #     settings.setValue("ss_import_folder", str(self.prj.output_folder))
        # import_folder = settings.value("ss_import_folder")
        # if (import_folder is None) or (not os.path.exists(import_folder)):
        #     settings.setValue("enc_import_folder", str(self.prj.output_folder))
        # # - project folder
        # export_project_folder = settings.value("enc_export_project_folder")
        # if export_project_folder is None:
        #     settings.setValue("enc_export_project_folder", str(self.prj.output_project_folder))
        # else:  # exists
        #     self.prj.output_project_folder = (export_project_folder == "true")
        # # - subfolders
        # export_subfolders = settings.value("enc_export_subfolders")
        # if export_subfolders is None:
        #     settings.setValue("enc_export_subfolders", self.prj.output_subfolders)
        # else:  # exists
        #     self.prj.output_subfolders = (export_subfolders == "true")

        # make tabs
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setContentsMargins(0, 0, 0, 0)
        self.tabs.setIconSize(QtCore.QSize(36, 36))
        self.tabs.setTabPosition(QtWidgets.QTabWidget.South)
        # main tab
        # self.tab_inputs = MainTab(parent_win=self, prj=self.prj)

        # self.idx_inputs = self.tabs.insertTab(0, self.tab_inputs,
        #                                       QtGui.QIcon(os.path.join(self.media, 'placeholder.png')), "")
        # self.tabs.setTabToolTip(self.idx_inputs, "QA QC")
    #     # - sounding selection
    #     self.tab_ss = SoundingSelectionTab(parent_win=self, prj=self.prj)
    #     # noinspection PyArgumentList
    #     self.idx_ss = self.tabs.insertTab(1, self.tab_ss,
    #                                       QtGui.QIcon(os.path.join(self.media, 'sounding_selection.png')), "")
    #     self.tabs.setTabToolTip(self.idx_ss, "Sounding Selection")
    #     self.tabs.setTabEnabled(self.idx_ss, False)
    #     # - ss vs chart
    #     self.tab_ss_vs_chart = SSvsChartTab(parent_win=self, prj=self.prj)
    #     # noinspection PyArgumentList
    #     self.idx_ss_vs_chart = self.tabs.insertTab(2, self.tab_ss_vs_chart,
    #                                                QtGui.QIcon(os.path.join(self.media, 'triangle_ss.png')), "")
    #     self.tabs.setTabToolTip(self.idx_ss_vs_chart, "SS vs Chart")
    #     self.tabs.setTabEnabled(self.idx_ss_vs_chart, False)
    #     # - dtm vs chart
    #     self.tab_dtm_vs_chart = DTMvsChartTab(parent_win=self, prj=self.prj)
    #     # noinspection PyArgumentList
    #     self.idx_dtm_vs_chart = self.tabs.insertTab(3, self.tab_dtm_vs_chart,
    #                                                 QtGui.QIcon(os.path.join(self.media, 'triangle_dtm.png')), "")
    #     self.tabs.setTabToolTip(self.idx_dtm_vs_chart, "DTM vs Chart")
    #     self.tabs.setTabEnabled(self.idx_dtm_vs_chart, False)
    #
    #     # noinspection PyUnresolvedReferences
    #     self.tabs.currentChanged.connect(self.change_tabs)
    #
    #     # flags
    #     self.has_ss = False
    #     self.has_dtm = False
    #     self.has_enc = False
    #
    # def dtm_loaded(self):
    #     self.has_dtm = True
    #     self.tabs.setTabEnabled(self.idx_ss, True)
    #     if self.has_enc:
    #         self.tabs.setTabEnabled(self.idx_dtm_vs_chart, True)
    #
    # def dtm_unloaded(self):
    #     self.has_dtm = False
    #     # self.tabs.setTabEnabled(self.idx_dtm_vs_chart, False)
    #     self.tabs.setTabEnabled(self.idx_ss, False)
    #
    # def ss_loaded(self):
    #     self.has_ss = True
    #     if self.has_enc:
    #         self.tabs.setTabEnabled(self.idx_ss_vs_chart, True)
    #
    # def ss_unloaded(self):
    #     self.has_ss = False
    #     self.tabs.setTabEnabled(self.idx_ss_vs_chart, False)
    #
    # def enc_loaded(self):
    #     self.has_enc = True
    #     if self.has_ss:
    #         self.tabs.setTabEnabled(self.idx_ss_vs_chart, True)
    #     if self.has_dtm:
    #         self.tabs.setTabEnabled(self.idx_dtm_vs_chart, True)
    #
    # def enc_unloaded(self):
    #     self.has_enc = False
    #     self.tabs.setTabEnabled(self.idx_ss_vs_chart, False)
    #     self.tabs.setTabEnabled(self.idx_dtm_vs_chart, False)
