import sys
import traceback
from PySide2 import QtCore, QtWidgets

import logging

logger = logging.getLogger(__name__)

from hyo2.abc.app.app_style import AppStyle
from hyo2.qc.qctools.mainwin import MainWin


def qt_custom_handler(error_type, error_context):
    logger.info("Qt error: %s [%s]" % (str(error_type), str(error_context)))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui():
    """Run the QC Tools gui"""

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(AppStyle.load_stylesheet())

    main_win = MainWin()
    sys.excepthook = main_win.exception_hook  # install the exception hook
    main_win.show()
    # main.do()

    sys.exit(app.exec_())
