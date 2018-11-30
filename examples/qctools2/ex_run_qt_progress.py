import time
from PySide import QtGui

from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.qctools.qt_progress import QtProgress

app = QtGui.QApplication([])

widget = QtGui.QWidget()
widget.show()

progress = QtProgress(parent=widget)

progress.start(title='Test Bar #1', text='Doing stuff')
time.sleep(1.)
progress.update(value=30, text='Updating')
time.sleep(1.)
print("canceled? %s" % progress.canceled)
progress.end()

time.sleep(1.)  # pause

progress.start(title='Test Bar #2', text='Doing stuff')
time.sleep(1.)
progress.update(value=30, text='Updating')
time.sleep(1.)
print("canceled? %s" % progress.canceled)
progress.end()

# app.exec_()
