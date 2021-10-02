import logging
import os

from PySide2 import QtGui, QtWidgets

logger = logging.getLogger(__name__)

from hyo2.abc.app.tabs.info.info_tab import InfoTab
from hyo2.abc.lib.helper import Helper

from hyo2.qc.qctools import app_info
from hyo2.qc.common import lib_info
from hyo2.unccalc.mainwin import MainWin as UncCalcMainWin
from hyo2.rori.mainwin import MainWin as RorIMainWin


class InfoWidget(InfoTab):

    def __init__(self, main_win: QtWidgets.QMainWindow):
        super().__init__(lib_info=lib_info, app_info=app_info,
                         with_online_manual=True,
                         with_offline_manual=True,
                         with_bug_report=True,
                         with_hydroffice_link=True,
                         with_ccom_link=True,
                         with_noaa_link=True,
                         with_unh_link=True,
                         with_license=True,
                         with_noaa_57=True,
                         with_ocs_email=True,
                         main_win=main_win)

        # RorI
        self.rori = None
        self.rori_action = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'rori.png')),
                                             'Rock or Islet oracle', self)
        # rori_action.setShortcut('Alt+R')
        # noinspection PyUnresolvedReferences
        self.rori_action.triggered.connect(self.show_rori)
        self.toolbar.insertAction(self.noaa_support_action, self.rori_action)

        # UNC calc
        self.unc_calc = None
        self.unc_calc_action = QtWidgets.QAction(QtGui.QIcon(os.path.join(app_info.app_media_path, 'unccalc.png')),
                                                 'Uncertainty Calculator', self)
        self.unc_calc_action.setShortcut('Alt+U')
        # noinspection PyUnresolvedReferences
        self.unc_calc_action.triggered.connect(self.show_unc_calc)
        self.toolbar.insertAction(self.rori_action, self.unc_calc_action)

    def show_unc_calc(self):
        self.change_url(Helper(lib_info=lib_info).web_url("unc_calc"))
        self.unc_calc = UncCalcMainWin(self)
        self.unc_calc.show()

    def show_rori(self):
        self.change_url(Helper(lib_info=lib_info).web_url("rori"))
        self.rori = RorIMainWin(self)
        self.rori.show()
