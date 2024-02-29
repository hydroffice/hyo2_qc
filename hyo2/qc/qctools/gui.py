import logging
import sys
import traceback

from PySide2 import QtCore, QtWidgets
from hyo2.abc.app.app_style import AppStyle
from hyo2.qc.qctools.mainwin import MainWin

logger = logging.getLogger(__name__)


def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):
    if "Cannot read property 'id' of null" in message:
        return
    logger.info("Qt error: %s [%s] -> %s"
                % (error_type, error_context, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui():
    """Run the QC Tools gui"""

    # sys.argv.append(["--disable-web-security"])  # temporary fix for CORS warning (QTBUG-70228)
    app = QtWidgets.QApplication()
    app.setStyleSheet(AppStyle.load_stylesheet())

    main_win = MainWin()
    sys.excepthook = main_win.exception_hook  # install the exception hook
    main_win.show()
    # main.do()

    if main_win.splash_screen:
        main_win.setDisabled(True)
        msg = "<p align='center'><i><span style='background-color:#ffffaa'><font color='#888888'>" \
              "QC Tools 3 should only be used on projects assigned<br>" \
              "the 2023 HSSD or earlier in your Project Instructions. <br><br>" \
              "If you have been assigned a project that uses <br>" \
              "the 2024 HSSD, please use QC Tools 4!" \
              "</font></i></span></p>"
        msg += "Do you still want to open QC Tools 3?"
        # noinspection PyUnresolvedReferences,PyTypeChecker
        ret = QtWidgets.QMessageBox.warning(main_win, "QC Tools 3", msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ret == QtWidgets.QMessageBox.No:
            logger.info("Please run QC Tools 4!")
            sys.exit()
        main_win.setEnabled(True)
    else:
        logger.info("Splash screen: OFF (Use CTRL+T to reactivate it)")

    sys.exit(app.exec_())
