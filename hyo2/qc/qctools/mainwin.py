import logging
import os
import ssl
import sys
import traceback
from urllib.request import urlopen
from urllib.error import URLError
import socket

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.abc.lib.helper import Helper
from hyo2.abc.app.dialogs.exception.exception_dialog import ExceptionDialog

from hyo2.qc.common import lib_info
from hyo2.qc.qctools import app_info
from hyo2.qc.qctools.widgets.survey.widget import SurveyWidget
from hyo2.qc.qctools.widgets.chart.widget import ChartWidget
from hyo2.qc.qctools.widgets.info import InfoWidget

logger = logging.getLogger(__name__)


class MainWin(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))
    media = os.path.join(here, "media")

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        logger.info("current configuration:\n%s" % Helper(lib_info=lib_info).package_info())

        # set the application name
        self.name = "QC Tools"
        self.version = app_info.app_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        self.setMinimumSize(500, 500)
        self.resize(920, 840)
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s' % self.name)
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set icons
        icon_info = QtCore.QFileInfo(os.path.join(self.media, 'favicon.png'))
        self.setWindowIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        if Helper.is_windows():

            try:
                # This is needed to display the app icon on the taskbar on Windows 7
                import ctypes
                app_id = '%s v.%s' % (self.name, self.version)
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

            except AttributeError as e:
                logger.debug("Unable to change app icon: %s" % e)

        # make tabs
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setIconSize(QtCore.QSize(52, 52))
        # - survey
        self.tab_survey = SurveyWidget(main_win=self)
        idx = self.tabs.insertTab(0, self.tab_survey,
                                  QtGui.QIcon(os.path.join(self.media, 'survey.png')), "")
        self.tabs.setTabToolTip(idx, "Survey Validation")
        # - chart
        self.tab_chart = ChartWidget(main_win=self)
        idx = self.tabs.insertTab(1, self.tab_chart,
                                  QtGui.QIcon(os.path.join(self.media, 'chart.png')), "")
        self.tabs.setTabToolTip(idx, "Chart Review")
        # info
        self.tab_info = InfoWidget(main_win=self)
        idx = self.tabs.insertTab(3, self.tab_info,
                                  QtGui.QIcon(os.path.join(self.media, 'info.png')), "")
        self.tabs.setTabToolTip(idx, "Info")

        # init default settings
        settings = QtCore.QSettings()
        start_tab = settings.value("start_tab")
        if (start_tab is None) or (start_tab > 1):
            start_tab = 0
            settings.setValue("start_tab", start_tab)
        self.tabs.setCurrentIndex(start_tab)

        self.statusBar().setStyleSheet("QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;}")
        self.status_bar_normal_style = self.statusBar().styleSheet()
        self.statusBar().showMessage("%s" % app_info.app_version, 2000)
        timer = QtCore.QTimer(self)
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(self.update_gui)
        timer.start(300000)  # 5 mins
        self.update_gui()

    def update_gui(self):
        msg = str()
        tokens = list()

        new_release = False
        new_bugfix = False
        latest_version = None
        try:
            response = urlopen('https://www.hydroffice.org/latest/qctools.txt', timeout=1)
            latest_version = response.read().split()[0].decode()

            cur_maj, cur_min, cur_fix = app_info.app_version.split('.')
            lat_maj, lat_min, lat_fix = latest_version.split('.')

            if int(lat_maj) > int(cur_maj):
                new_release = True

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) > int(cur_min)):
                new_release = True

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) == int(cur_min)) and (int(lat_fix) > int(cur_fix)):
                new_bugfix = True

        except (URLError, ssl.SSLError, socket.timeout) as e:
            logger.info("unable to check latest release: %s" % e)

        except ValueError as e:
            logger.info("unable to parse version: %s" % e)

        if new_release:
            logger.info("new release available: %s" % latest_version)
            tokens.append("New release available: %s" % latest_version)
            self.statusBar().setStyleSheet("QStatusBar{background-color:rgba(255,0,0,128);font-size: 8pt;}")

        elif new_bugfix:
            logger.info("new bugfix available: %s" % latest_version)
            tokens.append("New bugfix available: %s" % latest_version)
            self.statusBar().setStyleSheet("QStatusBar{background-color:rgba(255,255,0,128);font-size: 8pt;}")

        else:
            self.statusBar().setStyleSheet(self.status_bar_normal_style)

        msg += "|".join(tokens)

        self.statusBar().showMessage(msg, 3000000)

    def change_info_url(self, url):
        self.tab_info.change_url(url)

    def exception_hook(self, ex_type: type, ex_value: BaseException, tb: traceback) -> None:
        sys.__excepthook__(ex_type, ex_value, tb)

        # first manage case of not being an exception (e.g., keyboard interrupts)
        if not issubclass(ex_type, Exception):
            msg = str(ex_value)
            if not msg:
                msg = ex_value.__class__.__name__
            logger.info(msg)
            self.close()
            return

        dlg = ExceptionDialog(app_info=app_info, lib_info=lib_info, ex_type=ex_type, ex_value=ex_value, tb=tb)
        ret = dlg.exec_()
        if ret == QtWidgets.QDialog.Rejected:
            if not dlg.user_triggered:
                self.close()
        else:
            logger.warning("ignored exception")

    # Quitting #

    def do_you_really_want(self, title="Quit", text="quit"):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(os.path.join(self.media, 'favicon.png')).scaled(QtCore.QSize(60, 60)))
        msg_box.setText('Do you really want to %s?' % text)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        return msg_box.exec_()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        reply = self.do_you_really_want("Quit", "quit %s" % self.name)

        # reply = QtWidgets.QMessageBox.Yes
        if reply == QtWidgets.QMessageBox.Yes:

            # store current tab
            settings = QtCore.QSettings()
            settings.setValue("start_tab", self.tabs.currentIndex())

            event.accept()
            super().closeEvent(event)

        else:

            event.ignore()
