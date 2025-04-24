import logging
import os
import re

from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.abc.lib.progress.cli_progress import CliProgress
from hyo2.grids.grids_manager import GridsManager
from hyo2.qc.common import lib_info
from hyo2.qc.common.features import Features

logger = logging.getLogger(__name__)


class BaseProject:

    # added dictionary to toggle between office and field
    project_profiles = {
        'office': 0,
        'field': 1,
    }

    def __init__(self, projects_folder, profile=project_profiles['office'], progress=CliProgress()):

        # output folder
        self._output_folder = None   # the project's output folder
        if (projects_folder is None) or (not os.path.exists(projects_folder)):
            projects_folder = self.default_output_folder()
            logger.debug("using default output folder: %s" % projects_folder)
        self.output_folder = projects_folder

        # profile
        self._active_profile = profile

        # progress bar
        if not isinstance(progress, AbstractProgress):
            raise RuntimeError("invalid progress object")
        self.progress = progress

        # used to name the output folder
        self._survey = str()

        # grids
        self._gr = GridsManager()
        self._gr2 = GridsManager()

        # features
        self._ft = Features()

        # outputs
        self._output_shp = True
        self._output_kml = True
        self._output_subfolders = False
        self._output_project_folder = True

        # callback
        self._cb = None

    def set_callback(self, cb):
        self._cb = cb
        self._gr.callback = self._cb
        self._gr2.callback = self._cb

    # output folder

    @classmethod
    def default_output_folder(cls):

        output_folder = os.path.join(Helper(lib_info=lib_info).package_folder(),
                                     cls.__name__.replace("Project", ""))
        if not os.path.exists(output_folder):  # create it if it does not exist
            os.makedirs(output_folder)

        return output_folder

    @property
    def output_folder(self):
        return self._output_folder

    @output_folder.setter
    def output_folder(self, output_folder):
        if not os.path.exists(output_folder):
            raise RuntimeError("the passed output folder does not exist: %s" % output_folder)
        self._output_folder = output_folder

    def open_output_folder(self):
        Helper.explore_folder(self.output_folder)

    # profile

    @property
    def active_profile(self):
        return self._active_profile

    @active_profile.setter
    def active_profile(self, profile):
        if profile not in self.project_profiles.values():
            raise RuntimeError("the passed profile number does not exist: %s" % profile)
        self._active_profile = profile

    # survey label

    @property
    def survey_label(self):
        return self._survey

    @survey_label.setter
    def survey_label(self, value):
        re.sub(r'[^\w\-_\. ]', '_', value)
        logger.debug("survey label: %s" % value)
        self._survey = value

    def make_survey_label(self):
        """Make up the survey name from the path"""

        if self._survey != str():  # survey name is already present
            # logger.debug('survey label already present: %s' % self._survey)
            return

        # try from S57 path
        if self._ft.cur_s57_path:  # if the s57 path is present
            # logger.debug('survey label based on s57_path: %s' % self._ft.cur_s57_path)
            types = ['H1', 'W0', 'F0']
            for m in range(0, len(types)):
                if types[m] in self._ft.cur_s57_path:
                    pt = self._ft.cur_s57_path.index(types[m])
                    self._survey = self._ft.cur_s57_path[pt:(pt + 6)]
                    break

            # in case of missing survey name in the path, create a 6-letter name from the filename
            if not self._survey:
                self._survey = self._ft.cur_s57_basename.split('.')[0]  # get the basename of the path without extension
                if len(self._survey) > 6:  # name too long, shorten it
                    self._survey = self._survey.split('.')[-1][0:6]
                if len(self._survey) < 6:  # name too short, elongate it adding "_"
                    self._survey = "{:_<6}".format(self._survey)

        if self._survey != str():  # survey name is present
            logger.debug('survey label: %s' % self._survey)
            return

        # try from SS path
        if self._ft.cur_ss_path:  # if the s57 path is present
            # logger.debug('survey label based on ss_path: %s' % self._ft.cur_ss_path)
            types = ['H1', 'W0', 'F0']
            for m in range(0, len(types)):
                if types[m] in self._ft.cur_ss_path:
                    pt = self._ft.cur_ss_path.index(types[m])
                    self._survey = self._ft.cur_ss_path[pt:(pt + 6)]
                    break

            # in case of missing survey name in the path, create a 6-letter name from the filename
            if not self._survey:
                self._survey = self._ft.cur_ss_basename.split('.')[0]  # get the basename of the path without extension
                if len(self._survey) > 6:  # name too long, shorten it
                    self._survey = self._survey.split('.')[-1][0:6]
                if len(self._survey) < 6:  # name too short, elongate it adding "_"
                    self._survey = "{:_<6}".format(self._survey)

        if self._survey != str():  # survey name is present
            logger.debug('survey label: %s' % self._survey)
            return

        # try from grids
        if self._gr.current_path:  # if the surface path is present
            types = ['H1', 'W0', 'F0']
            for m in range(0, len(types)):
                if types[m] in self._gr.current_path:
                    pt = self._gr.current_path.index(types[m])
                    self._survey = self._gr.current_path[pt:(pt + 6)]
                    # logger.debug('survey label based on path: %s' % self._gr.current_path)
                    break
            # in case of missing survey name in the path, create a 6-letter name from the filename
            if not self._survey:
                self._survey = self._gr.current_basename.split('.')[0]  # basename of the path without extension
                if len(self._survey) > 6:  # name too long, shorten it
                    self._survey = self._survey.split('.')[-1][0:6]
                elif len(self._survey) < 6:  # name too short, elongate it adding "_"
                    self._survey = "{:_<6}".format(self._survey)
                # logger.debug('survey label based on basename: %s' % self._gr.current_basename)

        if self._survey != str():  # survey name is present
            logger.debug('survey label: %s' % self._survey)
            return

        else:
            raise RuntimeError("unable to create a valid survey label")

    def clear_survey_label(self):
        # logger.debug("clear survey label")
        self._survey = str()

    @classmethod
    def make_survey_label_from_path(cls, file_path):
        file_path.upper()
        survey_label = str()

        types = ['H1', 'W0', 'F0']
        for m in range(0, len(types)):
            if types[m] in file_path:
                pt = file_path.index(types[m])
                survey_label = file_path[pt:(pt + 6)]
                logger.debug('survey label based on path: %s' % file_path)
                break

        # in case of missing survey name in the path, create a 6-letter name from the filename
        if not survey_label:
            survey_label = os.path.basename(file_path).split('.')[0]  # basename of the path without extension
            if len(survey_label) > 6:  # name too long, shorten it
                survey_label = survey_label.split('.')[-1][0:6]
            elif len(survey_label) < 6:  # name too short, elongate it adding "_"
                survey_label = "{:_<6}".format(survey_label)
            logger.debug('survey label based on basename: %s' % os.path.basename(file_path))

        return survey_label

    # clear

    def clear_data(self):
        # grids
        self._gr = GridsManager()
        self._gr2 = GridsManager()
        self._gr.callback = self._cb
        self._gr2.callback = self._cb

        # features
        self._ft = Features()

        # used to name the output folder
        self._survey = str()

    # ################## inputs ###############

    # - S57

    @property
    def s57_list(self):
        return self._ft.s57_list

    def add_to_s57_list(self, s57_path):
        self._ft.add_to_s57_list(s57_path=s57_path)

    def remove_from_s57_list(self, s57_path):
        self._ft.remove_from_s57_list(s57_path=s57_path)

    def clear_s57_list(self):
        self._ft.clear_s57_list()

    def read_feature_file(self, feature_path: str) -> None:
        self._ft.read_feature_file(feature_path=feature_path)
        self.make_survey_label()

    def has_s57(self):
        return self._ft.has_s57()

    @property
    def cur_s57(self):
        return self._ft.cur_s57

    @property
    def cur_s57_basename(self):
        return self._ft.cur_s57_basename

    @property
    def cur_s57_path(self):
        return self._ft.cur_s57_path

    # - SS

    @property
    def ss_list(self):
        return self._ft.ss_list

    def add_to_ss_list(self, ss_path):
        self._ft.add_to_ss_list(ss_path=ss_path)

    def remove_from_ss_list(self, ss_path):
        self._ft.remove_from_ss_list(ss_path=ss_path)

    def clear_ss_list(self):
        self._ft.clear_ss_list()

    def read_ss_file(self, ss_path):
        self._ft.read_ss_file(ss_path=ss_path)
        self.make_survey_label()

    def has_ss(self):
        return self._ft.has_ss()

    @property
    def cur_ss(self):
        return self._ft.cur_ss

    @property
    def cur_ss_basename(self):
        return self._ft.cur_ss_basename

    # - grids

    # 1

    @property
    def grid_list(self):
        return self._gr.grid_list

    def add_to_grid_list(self, path):
        self._gr.add_path(path)

    def remove_from_grid_list(self, path):
        self._gr.remove_path(path)

    def clear_grid_list(self):
        self._gr.clear_grid_list()

    def open_grid(self, path):
        self.set_cur_grid(path=path)
        self.open_to_read_cur_grid()

    def set_cur_grid(self, path, ):
        """Make current the passed file"""
        self._gr.set_current(path)
        self.make_survey_label()

    def open_to_read_cur_grid(self):
        """Open to read the current file"""
        self._gr.open_to_read_current()

    def close_cur_grid(self):
        self._gr.close_current()

    def has_grid(self):
        """Return if a surface is present"""
        return self._gr.has_cur_grids

    @property
    def cur_grid(self):
        return self._gr.cur_grids

    @property
    def cur_grid_basename(self):
        return self._gr.current_basename

    def has_bag_grid(self):
        return self._gr.has_bag

    def has_csar_grid(self):
        return self._gr.has_csar

    def has_kluster_grid(self):
        return self._gr.has_kluster

    @property
    def selected_layers_in_cur_grid(self):
        return self._gr.selected_layers_in_current

    @selected_layers_in_cur_grid.setter
    def selected_layers_in_cur_grid(self, layers):
        if not isinstance(layers, list):
            raise RuntimeError("Required list, but passed %s" % type(layers))
        self._gr.selected_layers_in_current = layers

    @property
    def cur_grid_shape(self):
        if self.has_grid():
            return self._gr.current_shape
        else:
            return list()

    def cur_grid_has_depth_layer(self):
        return self._gr.current_has_depth_layer()

    def cur_grid_has_product_uncertainty_layer(self):
        return self._gr.current_has_product_uncertainty_layer()

    def cur_grid_has_density_layer(self):
        return self._gr.current_has_density_layer()

    def cur_grid_has_tvu_qc_layer(self):
        return len(self._gr.current_tvu_qc_layers()) > 0

    def cur_grid_tvu_qc_layers(self):
        return self._gr.current_tvu_qc_layers()

    def set_cur_grid_tvu_qc_name(self, name):
        self._gr.set_current_tvu_qc_name(name)

    # 2

    @property
    def grid_list2(self):
        return self._gr2.grid_list

    def add_to_grid_list2(self, path):
        self._gr2.add_path(path)

    def remove_from_grid_list2(self, path):
        self._gr2.remove_path(path)

    def clear_grid_list2(self):
        self._gr2.clear_grid_list()

    def set_cur_grid2(self, path, ):
        """Make current the passed file"""
        self._gr2.set_current(path)

    def open_to_read_cur_grid2(self):
        """Open to read the current file"""
        self._gr2.open_to_read_current()

    def has_grid2(self):
        """Return if a surface is present"""
        return self._gr2.has_cur_grids

    @property
    def cur_grid2(self):
        return self._gr2.cur_grids

    @property
    def cur_grid_basename2(self):
        return self._gr2.current_basename

    def has_bag_grid2(self):
        return self._gr2.has_bag

    def has_csar_grid2(self):
        return self._gr2.has_csar

    @property
    def selected_layers_in_cur_grid2(self):
        return self._gr2.selected_layers_in_current

    @selected_layers_in_cur_grid2.setter
    def selected_layers_in_cur_grid2(self, layers):
        if not isinstance(layers, list):
            raise RuntimeError("Required list, but passed %s" % type(layers))
        self._gr2.selected_layers_in_current = layers

    @property
    def cur_grid_shape2(self):
        if self.has_grid2():
            return self._gr2.current_shape
        else:
            return list()

    def cur_grid_has_depth_layer2(self):
        return self._gr2.current_has_depth_layer()

    def cur_grid_has_product_uncertainty_layer2(self):
        return self._gr2.current_has_product_uncertainty_layer()

    def cur_grid_has_density_layer2(self):
        return self._gr2.current_has_density_layer()

    def cur_grid_has_tvu_qc_layer2(self):
        return len(self._gr2.current_tvu_qc_layers()) > 0

    def cur_grid_tvu_qc_layers2(self):
        return self._gr2.current_tvu_qc_layers()

    def set_cur_grid_tvu_qc_name2(self, name):
        self._gr2.set_current_tvu_qc_name(name)

    # ################## outputs ###############

    @property
    def output_shp(self):
        return self._output_shp

    @output_shp.setter
    def output_shp(self, value):
        if not isinstance(value, bool):
            raise RuntimeError("the passed flag is not a boolean: %s" % type(value))

        self._output_shp = value

    @property
    def output_kml(self):
        return self._output_kml

    @output_kml.setter
    def output_kml(self, value):
        if not isinstance(value, bool):
            raise RuntimeError("the passed flag is not a boolean: %s" % type(value))

        self._output_kml = value

    @property
    def output_project_folder(self) -> bool:
        return self._output_project_folder

    @output_project_folder.setter
    def output_project_folder(self, value: bool) -> None:
        self._output_project_folder = value
        logger.info("Output in project folder: %s" % self._output_project_folder)

    @property
    def output_subfolders(self) -> bool:
        return self._output_subfolders

    @output_subfolders.setter
    def output_subfolders(self, value: bool) -> None:
        self._output_subfolders = value
        logger.info("Output in tool folder: %s" % self._output_subfolders)

    # _______________________________________________________________________________
    # ############################## AUXILIARY METHODS ##############################

    @classmethod
    def raise_window(cls):
        from matplotlib import pyplot as plt
        cfm = plt.get_current_fig_manager()
        cfm.window.activateWindow()
        cfm.window.raise_()

    @property
    def timestamp(self):
        return Helper.timestamp()

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <output folder: %s>\n" % self.output_folder
        msg += "  <survey label: %s>\n" % (self._survey if len(self._survey) else "None")

        if len(self.grid_list) > 0:
            msg += "  <grid files>\n"
            for grid in self.grid_list:
                msg += "    <%s>\n" % grid

        if len(self.s57_list) > 0:
            msg += "  <S57 files>\n"
            for s57 in self.s57_list:
                msg += "    <%s>\n" % s57

        if len(self.ss_list) > 0:
            msg += "  <SS files>\n"
            for ss in self.ss_list:
                msg += "    <%s>\n" % ss

        return msg
