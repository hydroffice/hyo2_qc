import os
import sys
import subprocess
import logging

from PySide2 import QtCore, QtGui, QtWidgets
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar
from matplotlib.figure import Figure
from matplotlib import rc_context

from hyo2.rori import __version__ as rori_version
from hyo2.rori import __doc__ as rori_name
from hyo2.rori.gui_settings import GuiSettings


matplotlib.use('Qt5Agg')
logger = logging.getLogger(__name__)


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
        self.name = rori_name
        self.version = rori_version
        if self.main_win is None:
            self.setWindowTitle('%s v.%s' % (self.name, self.version))
        else:
            self.setWindowTitle('%s' % (self.name,))
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
            icon_info = QtCore.QFileInfo(os.path.join(self.media, 'rori.png'))
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
        # hssd
        text_1ab = QtWidgets.QLabel("")
        text_1ab.setAlignment(QtCore.Qt.AlignCenter)
        text_1ab.setFixedWidth(100)
        label_hbox.addWidget(text_1ab)
        # spacing
        label_hbox.addSpacing(10)
        # specs
        text_1ab = QtWidgets.QLabel("Great Lakes")
        text_1ab.setAlignment(QtCore.Qt.AlignCenter)
        text_1ab.setFixedWidth(100)
        label_hbox.addWidget(text_1ab)
        # spacing
        label_hbox.addSpacing(10)
        # specs
        text_1ab = QtWidgets.QLabel("")
        text_1ab.setAlignment(QtCore.Qt.AlignCenter)
        text_1ab.setFixedWidth(100)
        label_hbox.addWidget(text_1ab)
        # stretch
        label_hbox.addStretch()

        toggle_hbox = QtWidgets.QHBoxLayout()
        settings_vbox.addLayout(toggle_hbox)
        # stretch
        toggle_hbox.addStretch()
        # HSSD
        self.toggle_hssd = QtWidgets.QDial()
        self.toggle_hssd.setNotchesVisible(True)
        self.toggle_hssd.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_hssd.setRange(0, 1)
        self.toggle_hssd.setValue(0)
        self.toggle_hssd.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_hssd.setInvertedAppearance(False)
        # noinspection PyUnresolvedReferences
        self.toggle_hssd.valueChanged.connect(self.on_settings_changed)
        toggle_hbox.addWidget(self.toggle_hssd)
        # spacing
        toggle_hbox.addSpacing(105)
        # area
        self.toggle_area = QtWidgets.QDial()
        self.toggle_area.setNotchesVisible(True)
        self.toggle_area.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_area.setRange(0, 2)
        self.toggle_area.setValue(0)
        self.toggle_area.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_area.setInvertedAppearance(False)
        # noinspection PyUnresolvedReferences
        self.toggle_area.valueChanged.connect(self.on_settings_changed)
        toggle_hbox.addWidget(self.toggle_area)
        # spacing0
        toggle_hbox.addSpacing(105)
        # specs
        self.toggle_z = QtWidgets.QDial()
        self.toggle_z.setNotchesVisible(True)
        self.toggle_z.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.toggle_z.setRange(0, 1)
        self.toggle_z.setValue(0)
        self.toggle_z.setFixedSize(QtCore.QSize(50, 50))
        self.toggle_z.setInvertedAppearance(False)
        # noinspection PyUnresolvedReferences
        self.toggle_z.valueChanged.connect(self.on_settings_changed)
        toggle_hbox.addWidget(self.toggle_z)
        # stretch
        toggle_hbox.addStretch()

        label2_hbox = QtWidgets.QHBoxLayout()
        settings_vbox.addLayout(label2_hbox)
        # stretch
        label2_hbox.addStretch()
        # specs
        text_special = QtWidgets.QLabel("HSSD 2018 ")
        text_special.setAlignment(QtCore.Qt.AlignRight)
        text_special.setFixedWidth(70)
        label2_hbox.addWidget(text_special)
        text_2 = QtWidgets.QLabel(" HSSD 2019+")
        text_2.setAlignment(QtCore.Qt.AlignLeft)
        text_2.setFixedWidth(70)
        label2_hbox.addWidget(text_2)
        # stretch
        label2_hbox.addSpacing(10)
        # area
        text_special = QtWidgets.QLabel("Pacific Coast ")
        text_special.setAlignment(QtCore.Qt.AlignRight)
        text_special.setFixedWidth(70)
        label2_hbox.addWidget(text_special)
        text_2 = QtWidgets.QLabel(" Atlantic Coast")
        text_2.setAlignment(QtCore.Qt.AlignLeft)
        text_2.setFixedWidth(70)
        label2_hbox.addWidget(text_2)
        # stretch
        label2_hbox.addSpacing(10)
        # specs
        text_special = QtWidgets.QLabel("Depth ")
        text_special.setAlignment(QtCore.Qt.AlignRight)
        text_special.setFixedWidth(70)
        label2_hbox.addWidget(text_special)
        text_2 = QtWidgets.QLabel(" Elevation")
        text_2.setAlignment(QtCore.Qt.AlignLeft)
        text_2.setFixedWidth(70)
        label2_hbox.addWidget(text_2)
        # stretch
        label2_hbox.addStretch()

        settings_vbox.addSpacing(8)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        watlev_text = QtWidgets.QLabel("Always Dry: ")
        watlev_text.setFixedWidth(100)
        hbox.addWidget(watlev_text)
        self.always_dry_min_value = QtWidgets.QLineEdit()
        self.always_dry_min_value.setFixedWidth(120)
        self.always_dry_min_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.always_dry_min_value.setDisabled(True)
        self.always_dry_min_value.setText("")
        hbox.addWidget(self.always_dry_min_value)
        self.always_dry_max_value = QtWidgets.QLineEdit()
        self.always_dry_max_value.setFixedWidth(120)
        self.always_dry_max_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.always_dry_max_value.setDisabled(True)
        self.always_dry_max_value.setText("")
        hbox.addWidget(self.always_dry_max_value)
        hbox.addStretch()
        settings_vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        watlev_text = QtWidgets.QLabel("Covers & Uncovers: ")
        watlev_text.setFixedWidth(100)
        hbox.addWidget(watlev_text)
        self.covers_and_uncovers_min_value = QtWidgets.QLineEdit()
        self.covers_and_uncovers_min_value.setFixedWidth(120)
        self.covers_and_uncovers_min_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.covers_and_uncovers_min_value.setDisabled(True)
        self.covers_and_uncovers_min_value.setText("")
        hbox.addWidget(self.covers_and_uncovers_min_value)
        self.covers_and_uncovers_max_value = QtWidgets.QLineEdit()
        self.covers_and_uncovers_max_value.setFixedWidth(120)
        self.covers_and_uncovers_max_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.covers_and_uncovers_max_value.setDisabled(True)
        self.covers_and_uncovers_max_value.setText("")
        hbox.addWidget(self.covers_and_uncovers_max_value)
        hbox.addStretch()
        settings_vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        watlev_text = QtWidgets.QLabel("Awash: ")
        watlev_text.setFixedWidth(100)
        hbox.addWidget(watlev_text)
        self.awash_min_value = QtWidgets.QLineEdit()
        self.awash_min_value.setFixedWidth(120)
        self.awash_min_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.awash_min_value.setDisabled(True)
        self.awash_min_value.setText("")
        hbox.addWidget(self.awash_min_value)
        self.awash_max_value = QtWidgets.QLineEdit()
        self.awash_max_value.setFixedWidth(120)
        self.awash_max_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.awash_max_value.setDisabled(True)
        self.awash_max_value.setText("")
        hbox.addWidget(self.awash_max_value)
        hbox.addStretch()
        settings_vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        watlev_text = QtWidgets.QLabel("Always underwater: ")
        watlev_text.setFixedWidth(100)
        hbox.addWidget(watlev_text)
        self.always_underwater_min_value = QtWidgets.QLineEdit()
        self.always_underwater_min_value.setFixedWidth(120)
        self.always_underwater_min_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.always_underwater_min_value.setDisabled(True)
        self.always_underwater_min_value.setText("")
        hbox.addWidget(self.always_underwater_min_value)
        self.always_underwater_max_value = QtWidgets.QLineEdit()
        self.always_underwater_max_value.setFixedWidth(120)
        self.always_underwater_max_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.always_underwater_max_value.setDisabled(True)
        self.always_underwater_max_value.setText("")
        hbox.addWidget(self.always_underwater_max_value)
        hbox.addStretch()
        settings_vbox.addLayout(hbox)

        # ### Inputs ###

        self.inputs = QtWidgets.QGroupBox("Input")
        self.vbox.addWidget(self.inputs)
        inputs_vbox = QtWidgets.QVBoxLayout()
        self.inputs.setLayout(inputs_vbox)

        # MHW
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        self.mhw_text = QtWidgets.QLabel("MHW [m]: ")
        hbox.addWidget(self.mhw_text)
        self.mhw_value = QtWidgets.QLineEdit()
        self.mhw_value.setFixedWidth(60)
        self.mhw_value.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.mhw_value))
        self.mhw_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.mhw_value.setText("5.0")
        hbox.addWidget(self.mhw_value)
        depth_text = QtWidgets.QLabel("Depth [m]: ")
        hbox.addWidget(depth_text)
        self.depth_value = QtWidgets.QLineEdit()
        self.depth_value.setFixedWidth(60)
        self.depth_value.setValidator(QtGui.QDoubleValidator(-9999, 9999, 5, self.depth_value))
        self.depth_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.depth_value.setText("1.0")
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

        outputs_hbox = QtWidgets.QHBoxLayout()
        outputs_vbox.addLayout(outputs_hbox)

        outputs_hbox.addStretch()
        # pic
        self.out_pic_label = QtWidgets.QLabel()
        outputs_hbox.addWidget(self.out_pic_label)

        # info
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        out_text_vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(out_text_vbox)
        self.out_main_label = QtWidgets.QLabel()
        self.out_main_label.setFixedWidth(320)
        self.out_main_label.setStyleSheet("font-weight: bold")
        out_text_vbox.addWidget(self.out_main_label)
        self.out_more_label = QtWidgets.QLabel()
        self.out_more_label.setFixedWidth(320)
        out_text_vbox.addWidget(self.out_more_label)
        hbox.addStretch()
        outputs_hbox.addLayout(hbox)

        outputs_hbox.addStretch()

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
            self.levels_ax = self.f.add_subplot(111)
            self.levels_ax.invert_yaxis()

        # toolbar
        self.hbox = QtWidgets.QHBoxLayout()
        outputs_vbox.addLayout(self.hbox)
        # navigation
        self.nav = NavToolbar(canvas=self.c, parent=self.top_widget)
        self.hbox.addWidget(self.nav)

        self.on_settings_changed()
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
        cls.explore_folder(
            "https://www.hydroffice.org/manuals/qctools/user_manual_info.html#rori-your-rock-or-islet-oracle")

    def _draw_grid(self):
        for a in self.f.get_axes():
            a.grid(True)

    def on_first_draw(self):
        """Redraws the figure, it is only called at the first import!!!"""
        with rc_context(self.rc_context):
            # self._set_title()
            self._draw_levels()
            self._draw_grid()
            self.is_drawn = True

    def _draw_levels(self):
        logger.debug("draw levels")

        mhw = float(self.mhw_value.text())
        depth = float(self.depth_value.text())

        if self.toggle_area.value() != 1:
            max_z = 1.5 * max(abs(mhw), abs(depth))
        else:
            max_z = 1.5 * abs(depth)
        alpha = 0.3
        text_color = '#666666'
        text_shift = 0.6

        with rc_context(self.rc_context):

            self.levels_ax.clear()
            # self.levels_ax.set_xlabel('Depth [m]')
            if self.toggle_hssd.value() == 0:  # 2018 HSSD
                if self.toggle_z.value() == 0:
                    self.levels_ax.set_ylabel('Depth [m]')
                    if self.toggle_area.value() == 1:
                        self.levels_ax.axhline(y=0, color='b', linestyle=':')
                        self.levels_ax.text(0.01, -0.01, 'LWD', rotation=0)

                        self.levels_ax.axhline(y=depth, color='r', linestyle='-')
                        self.levels_ax.text(0.01, depth + 0.01, 'depth', rotation=0)

                        self.levels_ax.axhspan(- 1.2192, -max_z, facecolor='orange', alpha=alpha)
                        self.levels_ax.text(text_shift, (- 1.2192 - max_z) / 2.0, 'ALWAYS DRY', color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(-0.6096, - 1.2192, facecolor='yellow', alpha=alpha)
                        self.levels_ax.text(text_shift, (-0.6096 - 1.2192) / 2.0, 'COVERS & UNCOVERS',
                                            color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(0.6096, -0.6096, facecolor='cyan', alpha=alpha)
                        self.levels_ax.text(text_shift, (0.6096 - 0.6096) / 2.0, 'AWASH', color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(max_z, 0.6096, facecolor='#0099ff', alpha=alpha)
                        self.levels_ax.text(text_shift, (max_z + 0.6096) / 2.0, 'ALWAYS UNDERWATER', color=text_color,
                                            rotation=0)
                    else:
                        self.levels_ax.axhline(y=0.0, color='b', linestyle=':')
                        self.levels_ax.text(0.01, 0.01, 'MLLW', rotation=0)

                        self.levels_ax.axhline(y=-mhw, color='orange', linestyle=':')
                        self.levels_ax.text(0.01, -mhw - 0.01, 'MHW', rotation=0)

                        self.levels_ax.axhline(y=depth, color='r', linestyle='-')
                        self.levels_ax.text(0.01, depth + 0.01, 'depth', rotation=0)

                        if self.toggle_area.value() == 0:
                            self.levels_ax.axhspan(-mhw - 0.6096, -max_z, facecolor='orange', alpha=alpha)
                            self.levels_ax.text(text_shift, (-mhw - 0.6096 - max_z) / 2.0, 'ALWAYS DRY',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-0.6096, -mhw - 0.6096, facecolor='yellow', alpha=alpha)
                            self.levels_ax.text(text_shift, (-0.6096 - mhw - 0.6096) / 2.0, 'COVERS & UNCOVERS',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(0.6096, -0.6096, facecolor='cyan', alpha=alpha)
                            self.levels_ax.text(text_shift, (0.6096 - 0.6096) / 2.0, 'AWASH', color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(max_z, 0.6096, facecolor='#0099ff', alpha=alpha)
                            self.levels_ax.text(text_shift, (max_z + 0.6096) / 2.0, 'ALWAYS UNDERWATER',
                                                color=text_color,
                                                rotation=0)
                        else:
                            self.levels_ax.axhspan(-mhw - 0.3048, -max_z, facecolor='orange', alpha=alpha)
                            self.levels_ax.text(text_shift, (-mhw - 0.3048 - max_z) / 2.0, 'ALWAYS DRY',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-0.3048, -mhw - 0.3048, facecolor='yellow', alpha=alpha)
                            self.levels_ax.text(text_shift, (-0.3048 - mhw - 0.3048) / 2.0, 'COVERS & UNCOVERS',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(0.3048, -0.3048, facecolor='cyan', alpha=alpha)
                            self.levels_ax.text(text_shift, (0.3048 - 0.3048) / 2.0, 'AWASH', color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(max_z, 0.3048, facecolor='#0099ff', alpha=alpha)
                            self.levels_ax.text(text_shift, (max_z + 0.3048) / 2.0, 'ALWAYS UNDERWATER',
                                                color=text_color,
                                                rotation=0)
                    self.levels_ax.set_ylim([max_z, -max_z])

                else:
                    self.levels_ax.set_ylabel('Elevation [m]')
                    if self.toggle_area.value() == 1:
                        self.levels_ax.axhline(y=0, color='b', linestyle=':')
                        self.levels_ax.text(0.01, 0.01, 'LWD', rotation=0)

                        self.levels_ax.axhline(y=-depth, color='r', linestyle='-')
                        self.levels_ax.text(0.01, -depth - 0.01, 'depth', rotation=0)

                        self.levels_ax.axhspan(1.2192, max_z, facecolor='orange', alpha=alpha)
                        self.levels_ax.text(text_shift, (1.2192 + max_z) / 2.0, 'ALWAYS DRY', color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(+0.6096, + 1.2192, facecolor='yellow', alpha=alpha)
                        self.levels_ax.text(text_shift, (+0.6096 + 1.2192) / 2.0, 'COVERS & UNCOVERS',
                                            color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(-0.6096, 0.6096, facecolor='cyan', alpha=alpha)
                        self.levels_ax.text(text_shift, (-0.6096 + 0.6096) / 2.0, 'AWASH', color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(-max_z, -0.6096, facecolor='#0099ff', alpha=alpha)
                        self.levels_ax.text(text_shift, (-max_z - 0.6096) / 2.0, 'ALWAYS UNDERWATER', color=text_color,
                                            rotation=0)
                    else:
                        self.levels_ax.axhline(y=0.0, color='orange', linestyle=':')
                        self.levels_ax.text(0.01, 0.01, 'MHW', rotation=0)

                        self.levels_ax.axhline(y=-mhw, color='b', linestyle=':')
                        self.levels_ax.text(0.01, -mhw - 0.01, 'MLLW', rotation=0)

                        self.levels_ax.axhline(y=-mhw - depth, color='r', linestyle='-')
                        self.levels_ax.text(0.01, -mhw - depth - 0.01, 'depth', rotation=0)

                        if self.toggle_area.value() == 0:
                            self.levels_ax.axhspan(0.6096, max_z, facecolor='orange', alpha=alpha)
                            self.levels_ax.text(text_shift, (0.6096 + max_z) / 2.0, 'ALWAYS DRY', color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-mhw + 0.6096, 0.6096, facecolor='yellow', alpha=alpha)
                            self.levels_ax.text(text_shift, (-mhw + 0.6096 + 0.6096) / 2.0, 'COVERS & UNCOVERS',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-mhw - 0.6096, -mhw + 0.6096, facecolor='cyan', alpha=alpha)
                            self.levels_ax.text(text_shift, (-mhw - 0.6096 - mhw + 0.6096) / 2.0, 'AWASH',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-max_z, -mhw - 0.6096, facecolor='#0099ff', alpha=alpha)
                            self.levels_ax.text(text_shift, (-max_z - mhw - 0.6096) / 2.0, 'ALWAYS UNDERWATER',
                                                color=text_color,
                                                rotation=0)
                        else:
                            self.levels_ax.axhspan(0.3048, max_z, facecolor='orange', alpha=alpha)
                            self.levels_ax.text(text_shift, (0.3048 + max_z) / 2.0, 'ALWAYS DRY', color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-mhw + 0.3048, 0.3048, facecolor='yellow', alpha=alpha)
                            self.levels_ax.text(text_shift, (-mhw + 0.3048 + 0.3048) / 2.0, 'COVERS & UNCOVERS',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-mhw - 0.3048, -mhw + 0.3048, facecolor='cyan', alpha=alpha)
                            self.levels_ax.text(text_shift, (-mhw - 0.3048 - mhw + 0.3048) / 2.0, 'AWASH',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-max_z, -mhw - 0.3048, facecolor='#0099ff', alpha=alpha)
                            self.levels_ax.text(text_shift, (-max_z - mhw - 0.3048) / 2.0, 'ALWAYS UNDERWATER',
                                                color=text_color,
                                                rotation=0)

                    self.levels_ax.set_ylim([-max_z, max_z])

            else:  # 2019 HSSD
                if self.toggle_z.value() == 0:
                    self.levels_ax.set_ylabel('Depth [m]')
                    if self.toggle_area.value() == 1:
                        self.levels_ax.axhline(y=0, color='b', linestyle=':')
                        self.levels_ax.text(0.01, -0.01, 'LWD', rotation=0)

                        self.levels_ax.axhline(y=depth, color='r', linestyle='-')
                        self.levels_ax.text(0.01, depth + 0.01, 'depth', rotation=0)

                        self.levels_ax.axhspan(- 0.1, -max_z, facecolor='orange', alpha=alpha)
                        self.levels_ax.text(text_shift, (- 0.1 - max_z) / 2.0, 'ALWAYS DRY', color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(-0.1, - 0.1, facecolor='yellow', alpha=alpha)
                        self.levels_ax.text(text_shift, (-0.1 - 0.1) / 2.0, 'COVERS & UNCOVERS',
                                            color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(0.1, -0.1, facecolor='cyan', alpha=alpha)
                        self.levels_ax.text(text_shift, (0.1 - 0.1) / 2.0, 'AWASH', color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(max_z, 0.1, facecolor='#0099ff', alpha=alpha)
                        self.levels_ax.text(text_shift, (max_z + 0.1) / 2.0, 'ALWAYS UNDERWATER', color=text_color,
                                            rotation=0)
                    else:
                        self.levels_ax.axhline(y=0.0, color='b', linestyle=':')
                        self.levels_ax.text(0.01, 0.01, 'MLLW', rotation=0)

                        self.levels_ax.axhline(y=-mhw, color='orange', linestyle=':')
                        self.levels_ax.text(0.01, -mhw - 0.01, 'MHW', rotation=0)

                        self.levels_ax.axhline(y=depth, color='r', linestyle='-')
                        self.levels_ax.text(0.01, depth + 0.01, 'depth', rotation=0)

                        if self.toggle_area.value() in [0, 2]:
                            self.levels_ax.axhspan(-mhw - 0.1, -max_z, facecolor='orange', alpha=alpha)
                            self.levels_ax.text(text_shift, (-mhw - 0.1 - max_z) / 2.0, 'ALWAYS DRY',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-0.1, -mhw - 0.1, facecolor='yellow', alpha=alpha)
                            self.levels_ax.text(text_shift, (-0.1 - mhw - 0.1) / 2.0, 'COVERS & UNCOVERS',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(0.1, -0.1, facecolor='cyan', alpha=alpha)
                            self.levels_ax.text(text_shift, (0.1 - 0.1) / 2.0, 'AWASH', color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(max_z, 0.1, facecolor='#0099ff', alpha=alpha)
                            self.levels_ax.text(text_shift, (max_z + 0.1) / 2.0, 'ALWAYS UNDERWATER',
                                                color=text_color,
                                                rotation=0)
                    self.levels_ax.set_ylim([max_z, -max_z])

                else:
                    self.levels_ax.set_ylabel('Elevation [m]')
                    if self.toggle_area.value() == 1:
                        self.levels_ax.axhline(y=0, color='b', linestyle=':')
                        self.levels_ax.text(0.01, 0.01, 'LWD', rotation=0)

                        self.levels_ax.axhline(y=-depth, color='r', linestyle='-')
                        self.levels_ax.text(0.01, -depth - 0.01, 'depth', rotation=0)

                        self.levels_ax.axhspan(0.1, max_z, facecolor='orange', alpha=alpha)
                        self.levels_ax.text(text_shift, (0.1 + max_z) / 2.0, 'ALWAYS DRY', color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(+0., + 0.1, facecolor='yellow', alpha=alpha)
                        self.levels_ax.text(text_shift, (+0.1 + 0.1) / 2.0, 'COVERS & UNCOVERS',
                                            color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(-0.1, 0.1, facecolor='cyan', alpha=alpha)
                        self.levels_ax.text(text_shift, (-0.1 + 0.1) / 2.0, 'AWASH', color=text_color,
                                            rotation=0)
                        self.levels_ax.axhspan(-max_z, -0.1, facecolor='#0099ff', alpha=alpha)
                        self.levels_ax.text(text_shift, (-max_z - 0.1) / 2.0, 'ALWAYS UNDERWATER', color=text_color,
                                            rotation=0)
                    else:
                        self.levels_ax.axhline(y=0.0, color='orange', linestyle=':')
                        self.levels_ax.text(0.01, 0.01, 'MHW', rotation=0)

                        self.levels_ax.axhline(y=-mhw, color='b', linestyle=':')
                        self.levels_ax.text(0.01, -mhw - 0.01, 'MLLW', rotation=0)

                        self.levels_ax.axhline(y=-mhw - depth, color='r', linestyle='-')
                        self.levels_ax.text(0.01, -mhw - depth - 0.01, 'depth', rotation=0)

                        if self.toggle_area.value() in [0, 2]:
                            self.levels_ax.axhspan(0.1, max_z, facecolor='orange', alpha=alpha)
                            self.levels_ax.text(text_shift, (0.1 + max_z) / 2.0, 'ALWAYS DRY', color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-mhw + 0.1, 0.1, facecolor='yellow', alpha=alpha)
                            self.levels_ax.text(text_shift, (-mhw + 0.1 + 0.1) / 2.0, 'COVERS & UNCOVERS',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-mhw - 0.1, -mhw + 0.1, facecolor='cyan', alpha=alpha)
                            self.levels_ax.text(text_shift, (-mhw - 0.1 - mhw + 0.1) / 2.0, 'AWASH',
                                                color=text_color,
                                                rotation=0)
                            self.levels_ax.axhspan(-max_z, -mhw - 0.1, facecolor='#0099ff', alpha=alpha)
                            self.levels_ax.text(text_shift, (-max_z - mhw - 0.1) / 2.0, 'ALWAYS UNDERWATER',
                                                color=text_color,
                                                rotation=0)
                    self.levels_ax.set_ylim([-max_z, max_z])

    def on_settings_changed(self):
        if self.toggle_hssd.value() == 0:
            logger.debug("draw HSSD 2018")

            if self.toggle_z.value() == 0:
                logger.debug("draw depth")

                if self.toggle_area.value() == 0:
                    logger.debug("West Coast")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("< -0.6096 MHW")
                    self.covers_and_uncovers_min_value.setText(">= -0.6096 MHW")
                    self.covers_and_uncovers_max_value.setText("< -0.6096 MLLW")
                    self.awash_min_value.setText(">= -0.6096 MLLW")
                    self.awash_max_value.setText("< +0.6096 MLLW")
                    self.always_underwater_min_value.setText(">= +0.6096 MLLW")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("MHW [m]: ")
                    self.mhw_value.setEnabled(True)

                elif self.toggle_area.value() == 1:
                    logger.debug("Great Lakes")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("< -1.2192 LWD")
                    self.covers_and_uncovers_min_value.setText(">= -1.2192 LWD")
                    self.covers_and_uncovers_max_value.setText("< -0.6096 LWD")
                    self.awash_min_value.setText(">= -0.6096 LWD")
                    self.awash_max_value.setText("< +0.6096 LWD")
                    self.always_underwater_min_value.setText(">= +0.6096 LWD")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("LWD [m]: ")
                    self.mhw_value.setDisabled(True)
                    self.mhw_value.setText("0.0")

                elif self.toggle_area.value() == 2:
                    logger.debug("East Coast")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("< -0.3048 MHW")
                    self.covers_and_uncovers_min_value.setText(">= -0.3048 MHW")
                    self.covers_and_uncovers_max_value.setText("< -0.3048 MLLW")
                    self.awash_min_value.setText(">= -0.3048 MLLW")
                    self.awash_max_value.setText("< +0.3048 MLLW")
                    self.always_underwater_min_value.setText(">= +0.3048 MLLW")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("MHW [m]: ")
                    self.mhw_value.setEnabled(True)

                else:
                    logger.warning("unknown area")
                    return

            else:
                logger.debug("draw elevation")

                if self.toggle_area.value() == 0:
                    logger.debug("West Coast")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("> +0.6096 MHW")
                    self.covers_and_uncovers_min_value.setText("<= +0.6096 MHW")
                    self.covers_and_uncovers_max_value.setText("> +0.6096 MLLW")
                    self.awash_min_value.setText("<= +0.6096 MLLW")
                    self.awash_max_value.setText("> -0.6096 MLLW")
                    self.always_underwater_min_value.setText("<= -0.6096 MLLW")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("MHW [m]: ")
                    self.mhw_value.setEnabled(True)

                elif self.toggle_area.value() == 1:
                    logger.debug("Great Lakes")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("> +1.2192 LWD")
                    self.covers_and_uncovers_min_value.setText("<= +1.2192 LWD")
                    self.covers_and_uncovers_max_value.setText("> +0.6096 LWD")
                    self.awash_min_value.setText("<= +0.6096 LWD")
                    self.awash_max_value.setText("> -0.6096 LWD")
                    self.always_underwater_min_value.setText("<= -0.6096 LWD")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("LWD [m]: ")
                    self.mhw_value.setDisabled(True)

                elif self.toggle_area.value() == 2:
                    logger.debug("East Coast")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("> +0.3048 MHW")
                    self.covers_and_uncovers_min_value.setText("<= +0.3048 MHW")
                    self.covers_and_uncovers_max_value.setText("> +0.3048 MLLW")
                    self.awash_min_value.setText("<= +0.3048 MLLW")
                    self.awash_max_value.setText("> -0.3048 MLLW")
                    self.always_underwater_min_value.setText("<= -0.3048 MLLW")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("MHW [m]: ")
                    self.mhw_value.setEnabled(True)

                else:
                    logger.warning("unknown area")
                    return
        else:
            logger.debug("draw HSSD 2019")

            if self.toggle_z.value() == 0:
                logger.debug("draw depth")

                if self.toggle_area.value() in [0, 2]:
                    logger.debug("East/West Coast")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("< -0.1 MHW")
                    self.covers_and_uncovers_min_value.setText(">= -0.1 MHW")
                    self.covers_and_uncovers_max_value.setText("<= -0.1 MLLW")
                    self.awash_min_value.setText("> -0.1 MLLW")
                    self.awash_max_value.setText("<= +0.1 MLLW")
                    self.always_underwater_min_value.setText("> +0.1 MLLW")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("MHW [m]: ")
                    self.mhw_value.setEnabled(True)

                elif self.toggle_area.value() == 1:
                    logger.debug("Great Lakes")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("< -0.1 LWD")
                    self.covers_and_uncovers_min_value.setText(">= -0.1 LWD")
                    self.covers_and_uncovers_max_value.setText("<= -0.1 LWD")
                    self.awash_min_value.setText("> -0.1 LWD")
                    self.awash_max_value.setText("<= +0.1 LWD")
                    self.always_underwater_min_value.setText("> +0.1 LWD")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("LWD [m]: ")
                    self.mhw_value.setDisabled(True)

                else:
                    logger.warning("unknown area")
                    return

            else:
                logger.debug("draw elevation")

                if self.toggle_area.value() in [0, 2]:
                    logger.debug("East/West Coast")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("> +0.1 MHW")
                    self.covers_and_uncovers_min_value.setText("<= +0.1 MHW")
                    self.covers_and_uncovers_max_value.setText(">= +0.1 MLLW")
                    self.awash_min_value.setText("< +0.1 MLLW")
                    self.awash_max_value.setText(">= -0.1 MLLW")
                    self.always_underwater_min_value.setText("< -0.1 MLLW")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("MHW [m]: ")
                    self.mhw_value.setEnabled(True)

                elif self.toggle_area.value() == 1:
                    logger.debug("Great Lakes")
                    self.always_dry_min_value.setText("")
                    self.always_dry_max_value.setText("> +0.1 LWD")
                    self.covers_and_uncovers_min_value.setText("<= +0.1 LWD")
                    self.covers_and_uncovers_max_value.setText(">= +0.1 LWD")
                    self.awash_min_value.setText("< +0.1 LWD")
                    self.awash_max_value.setText(">= -0.1 LWD")
                    self.always_underwater_min_value.setText("< -0.1 LWD")
                    self.always_underwater_max_value.setText("")

                    self.mhw_text.setText("LWD [m]: ")
                    self.mhw_value.setDisabled(True)
                    self.mhw_value.setText("0.0")

                else:
                    logger.warning("unknown area")
                    return

        self.on_calculate()

    def on_calculate(self):
        logger.debug("calculate")

        mhw = float(self.mhw_value.text())
        depth = float(self.depth_value.text())
        elevation = None
        watlev = None

        wl_dict = {
            "Always Dry": None,
            "Awash": 5,
            "Covers & Uncovers": 4,
            "Always Underwater": 3
        }

        if self.toggle_hssd.value() == 0:
            logger.debug("draw HSSD 2018")

            if self.toggle_area.value() == 1:
                if depth < - 1.2192:
                    logger.debug("Islet")
                    elevation = -depth
                else:
                    logger.debug("Rock")
                    if depth < -0.6096:
                        watlev = "Covers & Uncovers"
                    elif depth < 0.6096:
                        watlev = "Awash"
                    else:
                        watlev = "Always Underwater"

                    logger.debug("%s [%s]" % (watlev, wl_dict[watlev]))

            else:

                if self.toggle_area.value() == 0:
                    if depth < (-mhw - 0.6096):
                        logger.debug("Islet")
                        elevation = -mhw - depth
                    else:
                        logger.debug("Rock")
                        if depth < -0.6096:
                            watlev = "Covers & Uncovers"
                        elif depth < 0.6096:
                            watlev = "Awash"
                        else:
                            watlev = "Always Underwater"

                        logger.debug("%s [%s]" % (watlev, wl_dict[watlev]))

                else:
                    if depth < (-mhw - 0.3048):
                        logger.debug("Islet")
                        elevation = -mhw - depth
                    else:
                        logger.debug("Rock")
                        if depth < -0.3048:
                            watlev = "Covers & Uncovers"
                        elif depth < 0.3048:
                            watlev = "Awash"
                        else:
                            watlev = "Always Underwater"

                        logger.debug("%s [%s]" % (watlev, wl_dict[watlev]))

        else:
            logger.debug("draw HSSD 2019")

            if self.toggle_area.value() == 1:
                if depth < - 0.1:
                    logger.debug("Islet")
                    elevation = -depth
                else:
                    logger.debug("Rock")
                    if depth <= -0.1:
                        watlev = "Covers & Uncovers"
                    elif depth <= 0.1:
                        watlev = "Awash"
                    else:
                        watlev = "Always Underwater"

                    logger.debug("%s [%s]" % (watlev, wl_dict[watlev]))

            else:
                if self.toggle_area.value() in [0, 2]:
                    if depth < (-mhw - 0.1):
                        logger.debug("Islet")
                        elevation = -mhw - depth
                    else:
                        logger.debug("Rock")
                        if depth <= -0.1:
                            watlev = "Covers & Uncovers"
                        elif depth <= 0.1:
                            watlev = "Awash"
                        else:
                            watlev = "Always Underwater"

                        logger.debug("%s [%s]" % (watlev, wl_dict[watlev]))

        if elevation is not None:
            logger.debug("elevation: %.3f" % elevation)
            pix = QtGui.QPixmap(os.path.join(self.media, 'islet.png'))
            self.out_pic_label.setPixmap(pix.scaled(60, 60, QtCore.Qt.KeepAspectRatio))
            self.out_main_label.setText("I S L E T")
            self.out_more_label.setText("ELEVAT=%.3f" % elevation)
        else:
            pix = QtGui.QPixmap(os.path.join(self.media, 'rock.png'))
            self.out_pic_label.setPixmap(pix.scaled(60, 60, QtCore.Qt.KeepAspectRatio))
            self.out_main_label.setText("R O C K")
            self.out_more_label.setText("VALSOU=%.3f, WATLEV=%s[%s]" % (depth, watlev, wl_dict[watlev]))

        self._draw_levels()
        self._draw_grid()
        self.c.draw()
