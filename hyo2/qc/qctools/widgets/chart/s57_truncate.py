from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class S57TruncateTab(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win, prj):
        QtWidgets.QMainWindow.__init__(self)
        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        # - S57 truncate v2
        self.s57TruncateV2 = QtWidgets.QGroupBox("S57 Truncate v2")
        self.s57TruncateV2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.s57TruncateV2)
        ftv2_hbox = QtWidgets.QHBoxLayout()
        self.s57TruncateV2.setLayout(ftv2_hbox)
        # -- parameters
        self.setParametersFTv2 = QtWidgets.QGroupBox("Parameters")
        self.setParametersFTv2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        ftv2_hbox.addWidget(self.setParametersFTv2)
        self._ui_parameters_ftv2()
        # -- execution
        self.executeFTv2 = QtWidgets.QGroupBox("Execution")
        self.executeFTv2.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        ftv2_hbox.addWidget(self.executeFTv2)
        self._ui_execute_ftv2()

        self.vbox.addStretch()

    def _ui_parameters_ftv2(self):
        vbox = QtWidgets.QVBoxLayout()
        self.setParametersFTv2.setLayout(vbox)

        vbox.addStretch()

        # set decimal places
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.set_dec_places_label_ftv2 = QtWidgets.QLabel("Truncate after decimal place: ")
        self.set_dec_places_label_ftv2.setDisabled(False)
        hbox.addWidget(self.set_dec_places_label_ftv2)
        self.set_dec_places_label_ftv2.setFixedHeight(GuiSettings.single_line_height())
        self.set_dec_places_ftv2 = QtWidgets.QLineEdit("")
        hbox.addWidget(self.set_dec_places_ftv2)
        self.set_dec_places_ftv2.setFixedHeight(GuiSettings.single_line_height())
        self.set_dec_places_ftv2.setValidator(QtGui.QIntValidator(0, 99, self.set_dec_places_ftv2))
        self.set_dec_places_ftv2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.set_dec_places_ftv2.setReadOnly(False)
        self.set_dec_places_ftv2.setFont(GuiSettings.console_font())
        self.set_dec_places_ftv2.setFixedWidth(30)
        self.set_dec_places_ftv2.setDisabled(False)
        self.set_dec_places_ftv2.setText("1")

        hbox.addStretch()

        vbox.addStretch()

    def _ui_execute_ftv2(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeFTv2.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width())
        button.setText("S57 Truncate v2")
        button.setToolTip('Truncate the S57 input to the given decimal place')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_truncate_to_decimeters)

        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.single_line_height())
        icon_info = QtCore.QFileInfo(os.path.join(self.media, 'small_info.png'))
        button.setIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        button.setToolTip('Open the manual page')
        button.setStyleSheet("QPushButton { background-color: rgba(255, 255, 255, 0); }\n"
                             "QPushButton:hover { background-color: rgba(230, 230, 230, 100); }\n")
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_open_manual)
        hbox.addStretch()

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_chart_s57_truncate.html")

    def click_truncate_to_decimeters(self):
        # library takes care of progress bar

        version = 2
        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="chart_s57_truncate_%d" % version))
        self.prj.s57_truncate(version=version, decimal_places=int(self.set_dec_places_ftv2.text()))
