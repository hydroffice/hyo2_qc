import logging
import sys
import traceback

from PySide2 import QtCore, QtWidgets
from hyo2.rori.mainwin import MainWin
from hyo2.rori.stylesheet import stylesheet

logger = logging.getLogger(__name__)


def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):
    logger.info("Qt error: %s [%s] -> %s"
                % (error_type, error_context, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui():
    """Run the gui"""

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(stylesheet.load(pyside=True))

    main = MainWin()
    main.show()

    sys.exit(app.exec_())
