import os
import sys
import numpy as np
import math
import subprocess

from PySide2 import QtCore, QtGui, QtWidgets

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar
from matplotlib.figure import Figure
from matplotlib import rc_context

import logging
logger = logging.getLogger(__name__)

from hyo2.unccalc import __version__ as unc_version
from hyo2.unccalc import __doc__ as unc_name
from hyo2.unccalc.gui_settings import GuiSettings


class MainWin(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, "media")
    font_size = 6
    rc_context = {
        'font.family': 'sans-serif',
        'font.sans-serif': ['Tahoma', 'Bitstream Vera Sans', 'Lucida Grande', 'Verdana'],
        'font.size': font_size,
        'figure.titlesize': font_size + 1,
        'axes.labelsize': font_size,
        'legend.fontsize': font_size,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'axes.linewidth': 0.5,
        'axes.xmargin': 0.01,
        'axes.ymargin': 0.01,
        'lines.linewidth': 1.0,
        'grid.alpha': 0.2,
    }

    def __init__(self, main_win=None):
        super().__init__(main_win)

        self.main_win = main_win

        # set the application name and the version
        self.name = unc_name
        self.version = unc_version
        if self.main_win is None:
            self.setWindowTitle('%s v.%s' % (self.name, self.version))
        else:
            self.setWindowTitle('%s' % (self.name, ))
        self.setMinimumSize(200, 200)
        self.resize(600, 900)

        # only called when stand-alone (without Sound Speed Manager)
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        if _app.applicationName() == 'python':
            _app.setApplicationName('%s v.%s' % (self.name, self.version))
            _app.setOrganizationName("HydrOffice")
            _app.setOrganizationDomain("hydroffice.org")
            logger.debug("set application name: %s" % _app.applicationName())

            # set icons
            icon_info = QtCore.QFileInfo(os.path.join(self.media, 'unccalc.png'))
            self.setWindowIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
            if (sys.platform == 'win32') or (os.name is "nt"):  # is_windows()

                try:
                    # This is needed to display the app icon on the taskbar on Windows 7
                    import ctypes
                    app_id = '%s v.%s' % (self.name, self.version)
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                except AttributeError as e:
                    logger.debug("Unable to change app icon: %s" % e)

        # set palette
        style_info = QtCore.QFileInfo(os.path.join(self.here, 'styles', 'main.stylesheet'))
        style_content = open(style_info.filePath()).read()
        self.setStyleSheet(style_content)

        # settings = QtCore.QSettings()

        # mpl figure settings
        self.is_drawn = False
        self.f_dpi = 120  # dots-per-inch
        self.f_sz = (3.0, 6.0)  # inches
        self.tvu_plot = None
        self.thu_plot = None

        self.iho_color = '#E69F24'
        self.noaa_color = '#1C75C3'

        # outline ui
        self.top_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.top_widget)
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(4, 4, 4, 4)
        self.top_widget.setLayout(self.vbox)

        # ### Settings ###

        self.settings = QtWidgets.QGroupBox("Settings")
        self.vbox.addWidget(self.settings)
        settings_vbox = QtWidgets.QVBoxLayout()
        self.settings.setLayout(settings_vbox)

        label_hbox = QtWidgets.QHBoxLayout()
        settings_vbox.addLayout(label_hbox)
        # stretch
        label_hbox.addStretch()
        # specs
        text_1ab = QtWidgets.QLabel("Order 1")
        text_1ab.setAlignment(QtCore.Qt.AlignCenter)
        text_1ab.setFixedWidth(120)
        label_hbox.addWidget(text_1ab)
        # stretch
        label_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        settings_vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # specs
        self.toggle_order = QtWidgets.QDial()
        self.toggle_order.setNotchesVisible(True)
        self.toggle_order.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_order.setRange(0, 2)
        self.toggle_order.setValue(0)
        self.toggle_order.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_order.setInvertedAppearance(False)
        # noinspection PyUnresolvedReferences
        self.toggle_order.valueChanged.connect(self.on_tvu_changed)
        toggle_hbox.addWidget(self.toggle_order)
        # self.toggle_specs_v5.valueChanged.connect(self.click_set_profile)
        # stretch
        toggle_hbox.addStretch()

        label2_hbox = QtWidgets.QHBoxLayout()
        settings_vbox.addLayout(label2_hbox)
        # stretch
        label2_hbox.addStretch()
        # specs
        text_special = QtWidgets.QLabel("Special Order")
        text_special.setAlignment(QtCore.Qt.AlignCenter)
        text_special.setFixedWidth(80)
        label2_hbox.addWidget(text_special)
        text_2 = QtWidgets.QLabel("Order 2")
        text_2.setAlignment(QtCore.Qt.AlignCenter)
        text_2.setFixedWidth(80)
        label2_hbox.addWidget(text_2)
        # stretch
        label2_hbox.addStretch()

        settings_vbox.addSpacing(8)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        formula_text = QtWidgets.QLabel("TVU: ")
        formula_text.setFixedWidth(60)
        hbox.addWidget(formula_text)
        formula_label = QtWidgets.QLabel()
        formula_label.setPixmap(QtGui.QPixmap(os.path.join(self.media, 'tvu_formula.png')))
        formula_label.setFixedWidth(120)
        hbox.addWidget(formula_label)
        hbox.addSpacing(6)
        self.thu_a_text = QtWidgets.QLabel("a")
        hbox.addWidget(self.thu_a_text)
        self.thu_a_value = QtWidgets.QLineEdit()
        self.thu_a_value.setFixedWidth(60)
        self.thu_a_value.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.thu_a_value))
        self.thu_a_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.thu_a_value.setDisabled(True)
        self.thu_a_value.setText("0.25")
        hbox.addWidget(self.thu_a_value)
        self.thu_b_text = QtWidgets.QLabel(", b")
        hbox.addWidget(self.thu_b_text)
        self.thu_b_value = QtWidgets.QLineEdit()
        self.thu_b_value.setFixedWidth(60)
        self.thu_b_value.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.thu_b_value))
        self.thu_b_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.thu_b_value.setDisabled(True)
        self.thu_b_value.setText("0.0075")
        hbox.addWidget(self.thu_b_value)
        hbox.addStretch()
        settings_vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        formula_text = QtWidgets.QLabel("IHO THU: ")
        formula_text.setFixedWidth(60)
        hbox.addWidget(formula_text)
        formula_label = QtWidgets.QLabel()
        formula_label.setPixmap(QtGui.QPixmap(os.path.join(self.media, 'thu_formula.png')))
        formula_label.setFixedWidth(120)
        hbox.addWidget(formula_label)
        hbox.addSpacing(6)
        self.thu_k_text = QtWidgets.QLabel("k")
        hbox.addWidget(self.thu_k_text)
        self.thu_k_value = QtWidgets.QLineEdit()
        self.thu_k_value.setFixedWidth(60)
        self.thu_k_value.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.thu_k_value))
        self.thu_k_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.thu_k_value.setDisabled(True)
        self.thu_k_value.setText("2.0")
        hbox.addWidget(self.thu_k_value)
        self.tvu_p_text = QtWidgets.QLabel(", p")
        hbox.addWidget(self.tvu_p_text)
        self.thu_p_value = QtWidgets.QLineEdit()
        self.thu_p_value.setFixedWidth(60)
        self.thu_p_value.setValidator(QtGui.QDoubleValidator(0.00001, 1.0, 5, self.thu_p_value))
        self.thu_p_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.thu_p_value.setDisabled(True)
        self.thu_p_value.setText("0.0")
        hbox.addWidget(self.thu_p_value)
        hbox.addStretch()
        settings_vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        formula_text = QtWidgets.QLabel("NOAA THU: ")
        formula_text.setFixedWidth(60)
        hbox.addWidget(formula_text)
        formula_label = QtWidgets.QLabel()
        formula_label.setPixmap(QtGui.QPixmap(os.path.join(self.media, 'thu_formula.png')))
        formula_label.setFixedWidth(120)
        hbox.addWidget(formula_label)
        hbox.addSpacing(6)
        self.noaa_thu_k_text = QtWidgets.QLabel("k")
        hbox.addWidget(self.noaa_thu_k_text)
        self.noaa_thu_k_value = QtWidgets.QLineEdit()
        self.noaa_thu_k_value.setFixedWidth(60)
        self.noaa_thu_k_value.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.noaa_thu_k_value))
        self.noaa_thu_k_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.noaa_thu_k_value.setDisabled(True)
        self.noaa_thu_k_value.setText("5.0")
        hbox.addWidget(self.noaa_thu_k_value)
        self.noaa_thu_p_text = QtWidgets.QLabel(", p")
        hbox.addWidget(self.noaa_thu_p_text)
        self.noaa_thu_p_value = QtWidgets.QLineEdit()
        self.noaa_thu_p_value.setFixedWidth(60)
        self.noaa_thu_p_value.setValidator(QtGui.QDoubleValidator(0.00001, 1.0, 5, self.noaa_thu_p_value))
        self.noaa_thu_p_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.noaa_thu_p_value.setDisabled(True)
        self.noaa_thu_p_value.setText("0.05")
        hbox.addWidget(self.noaa_thu_p_value)
        hbox.addStretch()
        settings_vbox.addLayout(hbox)

        # ### Inputs ###

        self.inputs = QtWidgets.QGroupBox("Input")
        self.vbox.addWidget(self.inputs)
        inputs_vbox = QtWidgets.QVBoxLayout()
        self.inputs.setLayout(inputs_vbox)

        # Depth
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        depth_text = QtWidgets.QLabel("Depth [m]: ")
        hbox.addWidget(depth_text)
        self.depth_value = QtWidgets.QLineEdit()
        self.depth_value.setFixedWidth(60)
        self.depth_value.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.depth_value))
        self.depth_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.depth_value.setText("100.0")
        hbox.addWidget(self.depth_value)
        hbox.addSpacing(16)
        self.calculate = QtWidgets.QPushButton("Run")
        self.calculate.setFixedHeight(28)
        self.calculate.setFixedWidth(42)
        # noinspection PyUnresolvedReferences
        self.calculate.clicked.connect(self.on_calculate)
        hbox.addWidget(self.calculate)
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.single_line_height())
        icon_info = QtCore.QFileInfo(os.path.join(self.media, 'small_info.png'))
        button.setIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        button.setToolTip('Open the manual page')
        button.setStyleSheet(GuiSettings.stylesheet_info_button())
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_open_manual)
        hbox.addStretch()
        inputs_vbox.addLayout(hbox)

        # ### Outputs ###

        self.outputs = QtWidgets.QGroupBox("Outputs")
        self.vbox.addWidget(self.outputs)
        outputs_vbox = QtWidgets.QVBoxLayout()
        self.outputs.setLayout(outputs_vbox)

        # IHO
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()

        self.iho_tpu_box = QtWidgets.QGroupBox("IHO")
        hbox.addWidget(self.iho_tpu_box)
        tvu_vbox = QtWidgets.QVBoxLayout()
        self.iho_tpu_box.setLayout(tvu_vbox)

        iho_tvu_hbox = QtWidgets.QHBoxLayout()
        tvu_vbox.addLayout(iho_tvu_hbox)
        iho_tvu_text = QtWidgets.QLabel("TVU: ")
        iho_tvu_text.setFixedWidth(50)
        iho_tvu_hbox.addWidget(iho_tvu_text)
        self.out_tvu_value = QtWidgets.QLineEdit()
        self.out_tvu_value.setFixedWidth(80)
        self.out_tvu_value.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.out_tvu_value))
        self.out_tvu_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.out_tvu_value.setDisabled(True)
        iho_tvu_hbox.addWidget(self.out_tvu_value)

        iho_tvu_hbox = QtWidgets.QHBoxLayout()
        tvu_vbox.addLayout(iho_tvu_hbox)
        iho_thu_text = QtWidgets.QLabel("THU: ")
        iho_thu_text.setFixedWidth(50)
        iho_tvu_hbox.addWidget(iho_thu_text)
        self.out_thu_value = QtWidgets.QLineEdit()
        self.out_thu_value.setFixedWidth(80)
        self.out_thu_value.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.out_thu_value))
        self.out_thu_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.out_thu_value.setDisabled(True)
        iho_tvu_hbox.addWidget(self.out_thu_value)

        self.noaa_tpu_box = QtWidgets.QGroupBox("NOAA")
        hbox.addWidget(self.noaa_tpu_box)
        noaa_vbox = QtWidgets.QVBoxLayout()
        self.noaa_tpu_box.setLayout(noaa_vbox)

        noaa_hbox = QtWidgets.QHBoxLayout()
        noaa_vbox.addLayout(noaa_hbox)
        noaa_tvu_text = QtWidgets.QLabel("TVU: ")
        noaa_tvu_text.setFixedWidth(50)
        noaa_hbox.addWidget(noaa_tvu_text)
        self.out_noaa_tvu_value = QtWidgets.QLineEdit()
        self.out_noaa_tvu_value.setFixedWidth(80)
        self.out_noaa_tvu_value.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.out_noaa_tvu_value))
        self.out_noaa_tvu_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.out_noaa_tvu_value.setDisabled(True)
        noaa_hbox.addWidget(self.out_noaa_tvu_value)

        noaa_hbox = QtWidgets.QHBoxLayout()
        noaa_vbox.addLayout(noaa_hbox)
        noaa_thu_text = QtWidgets.QLabel("THU: ")
        noaa_thu_text.setFixedWidth(50)
        noaa_hbox.addWidget(noaa_thu_text)
        self.out_noaa_thu_value = QtWidgets.QLineEdit()
        self.out_noaa_thu_value.setFixedWidth(80)
        self.out_noaa_thu_value.setValidator(QtGui.QDoubleValidator(0.00001, 9999, 5, self.out_noaa_thu_value))
        self.out_noaa_thu_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.out_noaa_thu_value.setDisabled(True)
        noaa_hbox.addWidget(self.out_noaa_thu_value)

        hbox.addStretch()
        outputs_vbox.addLayout(hbox)

        # ### PLOTS ###

        # figure and canvas
        with rc_context(self.rc_context):

            self.f = Figure(figsize=self.f_sz, dpi=self.f_dpi)
            self.f.patch.set_alpha(0.0)
            self.c = FigureCanvas(self.f)
            self.c.setParent(self)
            self.c.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c.setFocus()
            outputs_vbox.addWidget(self.c)

            # axes
            self.tvu_ax = self.f.add_subplot(211)
            self.tvu_ax.invert_yaxis()
            self.thu_ax = self.f.add_subplot(212, sharex=self.tvu_ax)
            self.thu_ax.invert_yaxis()

        # toolbar
        self.hbox = QtWidgets.QHBoxLayout()
        outputs_vbox.addLayout(self.hbox)
        # navigation
        self.nav = NavToolbar(canvas=self.c, parent=self.top_widget)
        self.hbox.addWidget(self.nav)

        self.on_first_draw()

    @classmethod
    def is_url(cls, value):
        if len(value) > 7:

            https = "https"
            if value[:len(https)] == https:
                return True

        return False

    @classmethod
    def is_darwin(cls):
        """ Check if the current OS is Mac OS """
        return sys.platform == 'darwin'

    @classmethod
    def is_linux(cls):
        """ Check if the current OS is Linux """
        return sys.platform in ['linux', 'linux2']

    @classmethod
    def is_windows(cls):
        """ Check if the current OS is Windows """
        return (sys.platform == 'win32') or (os.name is "nt")

    @classmethod
    def explore_folder(cls, path):
        """Open the passed path using OS-native commands"""
        if cls.is_url(path):
            import webbrowser
            webbrowser.open(path)
            return True

        if not os.path.exists(path):
            logger.warning('invalid path to folder: %s' % path)
            return False

        path = os.path.normpath(path)

        if cls.is_darwin():
            subprocess.call(['open', '--', path])
            return True

        elif cls.is_linux():
            subprocess.call(['xdg-open', path])
            return True

        elif cls.is_windows():
            subprocess.call(['explorer', path])
            return True

        logger.warning("Unknown/unsupported OS")
        return False

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        cls.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_info.html#uncertainty-calculator")

    @classmethod
    def calc_tvu(cls, a2, b, d):
        return math.sqrt(a2 + (b * d) * (b * d))

    @classmethod
    def calc_thu(cls, k, p, d):
        return k + p * d

    def _set_title(self):
        msg = "Total Propagated Uncertainty"
        self.f.suptitle(msg)

    def _draw_grid(self):
        for a in self.f.get_axes():
            a.grid(True)

    def on_first_draw(self):
        """Redraws the figure, it is only called at the first import!!!"""
        with rc_context(self.rc_context):
            # self._set_title()
            self._draw_tvu()
            self._draw_thu()
            self._draw_grid()
            self.is_drawn = True

    def _draw_tvu(self):
        logger.debug("draw tvu")

        with rc_context(self.rc_context):

            self.tvu_ax.clear()
            self.tvu_ax.set_xlabel('Depth [m]')
            self.tvu_ax.set_ylabel('TVU [m]')

            depth = float(self.depth_value.text())
            depth_min = 0.0
            depth_max = 2 * depth
            ds = list(np.arange(0.001, depth_max, depth / 1000))

            tvu_min = 0.0
            tvu_max = 0.0

            a = float(self.thu_a_value.text())
            b = float(self.thu_b_value.text())
            a2 = a*a
            tvus = [self.calc_tvu(a2, b, d) for d in ds]
            tvu_max = max(tvu_max, max(tvus) * 1.2)

            self.tvu_plot, = self.tvu_ax.plot(ds, tvus,
                                              color=self.iho_color,
                                              linestyle='--',
                                              label='TVU'
                                              )

            self.tvu_ax.set_xlim([depth_min, depth_max])
            self.tvu_ax.set_ylim([tvu_min, tvu_max])
            self.tvu_ax.legend(loc='upper right')

            try:
                tvu = float(self.out_tvu_value.text())
                self.tvu_ax.plot([depth], [tvu], marker='o', markersize=3, color="#C03714")

            except Exception:
                logger.info("skip TVU dot")

    def _draw_thu(self):
        logger.debug("draw thu")

        thu_min = 0.0
        thu_max = 0.0

        with rc_context(self.rc_context):

            self.thu_ax.clear()
            self.thu_ax.set_xlabel('Depth [m]')
            self.thu_ax.set_ylabel('THU [m]')

            depth = float(self.depth_value.text())
            depth_min = 0.0
            depth_max = 2*depth

            ds = list(np.arange(0.001, depth_max, depth/1000))

            k = float(self.thu_k_value.text())
            p = float(self.thu_p_value.text())
            thus = [self.calc_thu(k, p, d) for d in ds]
            thu_max = max(thu_max, max(thus) * 1.2)

            self.thu_plot, = self.thu_ax.plot(ds, thus,
                                              color=self.iho_color,
                                              linestyle='--',
                                              label='IHO THU'
                                              )

            k = float(self.noaa_thu_k_value.text())
            p = float(self.noaa_thu_p_value.text())
            thus = [self.calc_thu(k, p, d) for d in ds]
            thu_max = max(thu_max, max(thus) * 1.2)

            self.thu_plot, = self.thu_ax.plot(ds, thus,
                                              color=self.noaa_color,
                                              linestyle=':',
                                              label='NOAA THU'
                                              )

            self.thu_ax.set_xlim([depth_min, depth_max])
            self.thu_ax.set_ylim([thu_min, thu_max])

            self.thu_ax.legend(loc='upper right')

            try:
                thu = float(self.out_noaa_thu_value.text())
                self.thu_ax.plot([depth], [thu], marker='o', markersize=3, color="blue")
                thu = float(self.out_thu_value.text())
                self.thu_ax.plot([depth], [thu], marker='o', markersize=3, color="#C03714")

            except Exception:
                logger.info("skip THU dot")

    def on_tvu_changed(self):
        if self.toggle_order.value() == 0:
            logger.debug("TVU special order")
            self.thu_a_value.setText("0.25")
            self.thu_b_value.setText("0.0075")
            self.thu_k_value.setText("2.0")
            self.thu_p_value.setText("0.0")

        elif self.toggle_order.value() == 1:
            logger.debug("TVU order 1a/b")
            self.thu_a_value.setText("0.5")
            self.thu_b_value.setText("0.013")
            self.thu_k_value.setText("5.0")
            self.thu_p_value.setText("0.05")

        elif self.toggle_order.value() == 2:
            logger.debug("TVU order 2")
            self.thu_a_value.setText("1.0")
            self.thu_b_value.setText("0.023")
            self.thu_k_value.setText("20.0")
            self.thu_p_value.setText("0.1")

        else:
            logger.warning("unknown TVU order")
            return

        self.on_calculate()

    def on_calculate(self):
        logger.debug("calculate")

        a = float(self.thu_a_value.text())
        b = float(self.thu_b_value.text())
        a2 = a * a
        noaa_a = float(self.thu_a_value.text())
        noaa_b = float(self.thu_b_value.text())
        noaa_a2 = noaa_a * noaa_a
        k = float(self.thu_k_value.text())
        p = float(self.thu_p_value.text())
        noaa_k = float(self.noaa_thu_k_value.text())
        noaa_p = float(self.noaa_thu_p_value.text())
        depth = float(self.depth_value.text())
        self.out_tvu_value.setText("%.3f" % self.calc_tvu(a2, b, depth))
        self.out_noaa_tvu_value.setText("%.3f" % self.calc_tvu(noaa_a2, noaa_b, depth))
        self.out_thu_value.setText("%.3f" % self.calc_thu(k, p, depth))
        self.out_noaa_thu_value.setText("%.3f" % self.calc_thu(noaa_k, noaa_p, depth))

        self._draw_tvu()
        self._draw_thu()
        self._draw_grid()
        self.c.draw()
