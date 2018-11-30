import sys
import traceback
from PySide import QtGui, QtCore

import logging

logger = logging.getLogger(__name__)

from hyo.rori.mainwin import MainWin
from hyo.rori.stylesheet import stylesheet


def qt_custom_handler(error_type, error_context):
    logger.info("Qt error: %s [%s]" % (str(error_type), str(error_context)))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMsgHandler(qt_custom_handler)


def gui():
    """Run the gui"""

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet(stylesheet.load(pyside=True))

    main = MainWin()
    main.show()

    sys.exit(app.exec_())
