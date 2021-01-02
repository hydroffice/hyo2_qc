from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging

from hyo2.qc.qctools.gui_settings import GuiSettings
from hyo2.qc.common import lib_info
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)

# for MATT code:
import numpy as np
from hyo2.bag import bag
from hyo2.bag.meta import Meta
import datetime


# end for MATT code


class BAGChecksTab(QtWidgets.QMainWindow):
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

        # - bag checks v1
        self.bag_checks_v1 = QtWidgets.QGroupBox("BAG Checks v1")
        self.bag_checks_v1.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.bag_checks_v1)
        bqv1_hbox = QtWidgets.QHBoxLayout()
        self.bag_checks_v1.setLayout(bqv1_hbox)

        # -- execution
        self.executeBQv1 = QtWidgets.QGroupBox("Execution")
        self.executeBQv1.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        bqv1_hbox.addWidget(self.executeBQv1)
        self._ui_execute_bqv1()

        self.vbox.addStretch()

    def _ui_execute_bqv1(self):
        vbox = QtWidgets.QVBoxLayout()
        self.executeBQv1.setLayout(vbox)

        vbox.addStretch()

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch()
        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(GuiSettings.single_line_height())
        button.setFixedWidth(GuiSettings.text_button_width() * 1.3)
        button.setText("BAG Checks v1")
        button.setToolTip('Perform checks on BAG files')
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_bag_checks_v1)

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

        vbox.addStretch()

    def click_bag_checks_v1(self):
        """trigger the bag checks v1"""
        self._click_bag_checks(1)

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/qctools/user_manual_survey_bag_checks.html")

    def _click_bag_checks(self, version):
        # MATT: This area will need attention with the addition of your code
        """abstract the grid checks calling mechanism"""

        # sanity checks
        # - version
        if not isinstance(version, int):
            raise RuntimeError("passed invalid type for version: %s" % type(version))
        if version not in [1, ]:
            raise RuntimeError("passed invalid Grid Checks version: %s" % version)
        # - list of grids (although the buttons should be never been enabled without grids)
        if len(self.prj.grid_list) == 0:
            raise RuntimeError("the grid list is empty")

        url_suffix = "survey_bag_checks_%d" % version
        self.parent_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix=url_suffix))

        # for each file in the project grid list
        msg = "Checks results per input:\n"
        grid_list = self.prj.grid_list
        opened_folders = list()

        for i, grid_file in enumerate(grid_list):

            # we want to be sure that the label is based on the name of the new file input
            self.prj.clear_survey_label()
            # switcher between different versions of find fliers
            if version == 1:
                success, report = self._bag_checks(grid_file=grid_file, version=version, idx=(i + 1),
                                                   total=len(grid_list))
            else:  # this case should be never reached after the sanity checks
                raise RuntimeError("unknown Bag Checks version: %s" % version)

            if success:
                msg += "- %s: done\n" % self.prj.cur_grid_basename
            else:
                msg += "- %s: skip\n" % self.prj.cur_grid_basename

            # open the output folder (if not already open)
            if self.prj.gridchecks_output_folder not in opened_folders:
                self.prj.open_gridchecks_output_folder()
                opened_folders.append(self.prj.gridchecks_output_folder)

            # MATT code:
            datetime_string = str(datetime.datetime.now())
            datetime_string = datetime_string.split('.')[0]
            datetime_string = datetime_string.replace(':', '')
            report_filename = 'BAG_Checks_output_' + datetime_string + '.txt'
            output_folder = self.prj.gridchecks_output_folder
            report_full_filename = os.path.join(output_folder, report_filename)
            f = open(report_full_filename, 'x')

            for line in report:
                f.write(line)
            f.close()
            # end MATT code

        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "Bag Checks v%d" % version, msg, QtWidgets.QMessageBox.Ok)

    def _bag_checks(self, grid_file, version, idx, total):
        # MATT: This will need attention with addition of your code

        logger.debug('bag checks v%d ...' % version)

        self.prj.progress.start(title="BAG Checks v.%d" % version,
                                text="Data loading [%d/%d]" % (idx, total),
                                init_value=2)

        try:
            self.prj.set_cur_grid(path=grid_file)
            self.prj.open_to_read_cur_grid()

        except Exception as e:
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Error", "While reading grid file, %s" % e, QtWidgets.QMessageBox.Ok)
            self.prj.progress.end()
            return False

        self.prj.progress.update(value=10,
                                 text="BAG Checks v%d [%d/%d]" % (version, idx, total))

        # MATT code:

        report = list()
        w = bag.BAGFile(grid_file)
        report.append('\n** ' + grid_file + ' **\n')

        output_xml = os.path.join(self.prj.gridchecks_output_folder, grid_file + '_metadata')

        meta = Meta(w.metadata())
        w.extract_metadata(output_xml)

        fyle = open(output_xml)
        datum_info_check = 0
        datum_check = 0
        date_check = 0
        time_check = 0
        file_created_date = str()
        start_time = str()
        end_time = str()

        while 1:
            line = fyle.readline()
            if datum_info_check == 0:
                if 'DATUM' in line:
                    datum_info = line
                    datum_info_check = 1
            if datum_check == 0:
                if 'NAD 83' in line:
                    datum = line
                    datum_check = 1
                if 'NAD83' in line:
                    datum = line
                    datum_check = 1
                if 'Nad 83' in line:
                    datum = line
                    datum_check = 1
                if 'Nad83' in line:
                    datum = line
                    datum_check = 1
                if 'WGS 84' in line:
                    datum = line
                    datum_check = 2
                if 'WGS84' in line:
                    datum = line
                    datum_check = 2
                if 'Wgs 84' in line:
                    datum = line
                    datum_check = 2
                if 'Wgs84' in line:
                    datum = line
                    datum_check = 2
            if 'dateStamp' in line:
                if date_check == 0:
                    date_check = 1
            if date_check == 1:
                if 'gco:Date' in line:
                    file_created_date = line
                    date_check = 2
            if 'temporalElement' in line:
                time_check = 1
            if time_check == 1:
                if 'beginPosition' in line:
                    start_time = line
                elif 'endPosition' in line:
                    end_time = line
                    time_check = 2
            if not line:
                break

        if datum_check == 1:
            report.append('\nNAD 83 identified! Here is the datum information found:\n\n')
            report.append(datum)
        elif datum_check == 2:
            report.append('\nWGS 84 identified! Here is the datum information found:\n\n')
            report.append(datum)
        elif datum_check == 0:
            report.append('\nWarning: WGS 84 or NAD 83 could not be identified!\n\n')
            if datum_info_check == 1:
                report.append('Here is some datum information found:\n\n')
                report.append(datum_info)
            else:
                report.append('There was no datum information found.\n\n')

        if len(file_created_date) > 0:
            report.append('\nFile Created Date found:\n')
            report.append('\n' + file_created_date + '\n')
        else:
            report.append('\nNo File Created Date could be found\n')

        if len(start_time) > 0 and len(end_time) > 0:
            report.append('Survey Start and End Dates found:\n\n')
            report.append(start_time)
            report.append(end_time)
            report.append('\n')
        else:
            report.append('Could not find Survey Start and End dates\n')

        if w.has_uncertainty():

            report.append('\nUncertainty layer found\n')

            try:
                elevation = w.elevation()
                uncertainty = w.uncertainty()
            except:
                report.append('\nData cannot be read, something may be wrong with ' + grid_file)
                report.append('\n\nBAG failed this check!\n')
                self.prj.progress.end()
                return True, report

            report.append('\nReading BAG...\n')

            max_depth = 0
            min_depth = -1e5
            nan_uncert_tracker = list()

            for m in range(0, len(elevation)):
                for n in range(0, len(elevation[m])):
                    if elevation[m][n] < max_depth:
                        max_depth = elevation[m][n]
                        max_depth_idx = [m, n]
                    if elevation[m][n] > min_depth:
                        min_depth = elevation[m][n]
                        min_depth_idx = [m, n]
                    if not np.isnan(elevation[m][n]):
                        if np.isnan(uncertainty[m][n]):
                            nan_uncert_tracker.append([m, n])

            uncertainty_flag = abs(np.average([max_depth, min_depth]))
            if uncertainty_flag > 30.0:
                uncertainty_flag = 30.0

            max_uncert = 0
            min_uncert = 1e5

            high_uncert_tracker = list()
            zero_uncert_tracker = list()
            negative_uncert_tracker = list()

            for m in range(0, len(uncertainty)):
                for n in range(0, len(uncertainty[m])):
                    if uncertainty[m][n] > max_uncert:
                        max_uncert = uncertainty[m][n]
                        max_uncert_idx = [m, n]
                    if uncertainty[m][n] < min_uncert:
                        min_uncert = uncertainty[m][n]
                        min_uncert_idx = [m, n]
                    if uncertainty[m][n] >= uncertainty_flag:
                        high_uncert_tracker.append([uncertainty[m][n], [m, n]])
                    if uncertainty[m][n] == 0:
                        zero_uncert_tracker.append([uncertainty[m][n], [m, n]])
                    if uncertainty[m][n] < 0:
                        negative_uncert_tracker.append([uncertainty[m][n], [m, n]])

            report.append('\nmax elevation ' + str(abs(max_depth)) + ' at index ' + str(max_depth_idx))
            report.append('\nmin elevation ' + str(abs(min_depth)) + ' at index ' + str(min_depth_idx))
            if max_uncert > 0:
                report.append('\nmax uncertainty ' + str(max_uncert) + ' at index ' + str(max_uncert_idx))
            else:
                report.append('\nmax uncertainty could not be identified')
            if min_uncert < 1e5:
                report.append('\nmin uncertainty ' + str(min_uncert) + ' at index ' + str(min_uncert_idx))
            else:
                report.append('\nmin uncertainty could not be identified')
            report.append('\n\nRunning Uncertainty Checks...\n')
            report.append(
                '\n' + str(len(high_uncert_tracker)) + ' cells were flagged for having uncertainty greater than ' + str(
                    uncertainty_flag))
            report.append(
                '\n' + str(len(zero_uncert_tracker)) + ' cells were flagged for having uncertainty equal to zero')
            report.append(
                '\n' + str(len(negative_uncert_tracker)) + ' cells were flagged for having uncertainty less than zero')
            report.append(
                '\n' + str(len(nan_uncert_tracker)) + ' cells were flagged for having uncertainty that is not a number')
            if len(high_uncert_tracker) + len(zero_uncert_tracker) + len(negative_uncert_tracker) + len(
                    nan_uncert_tracker) == 0:
                report.append('\n\nBAG passed these checks!\n')
            else:
                report.append('\n\nBAG failed these checks!\n')

        else:
            report.append('\nNo uncertainty layer found\n')
            report.append('\nBAG failed this check!\n')

        self.prj.progress.end()
        return True, report
