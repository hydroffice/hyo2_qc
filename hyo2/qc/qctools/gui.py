import sys
import traceback
from PySide2 import QtCore, QtWidgets

import logging

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

    sys.argv.append("--disable-web-security")  # temporary fix for CORS warning (QTBUG-70228)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(AppStyle.load_stylesheet())

    main_win = MainWin()
    sys.excepthook = main_win.exception_hook  # install the exception hook
    main_win.show()
    # main.do()

    sys.exit(app.exec_())
