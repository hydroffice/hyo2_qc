import argparse
import logging
import os
from urllib.request import urlopen

from hyo2.abc.app.web_renderer import WebRenderer
from hyo2.abc.lib.helper import Helper
from hyo2.qc import __version__
from hyo2.qc.common import lib_info
from hyo2.qc.qctools import app_info
from hyo2.qc.survey.project import SurveyProject

logger = logging.getLogger(__name__)


class QCToolsParser:

    def __init__(self):
        self._check_latest_release()

        self.parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.parser.add_argument('--version', action='version', version=__version__)
        subparsers = self.parser.add_subparsers()

        ff_parser = subparsers.add_parser('FindFliers', help='Identify potential fliers in gridded bathymetry',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        ff_parser.add_argument('input_dtm', type=str,
                               help='The input DTM file to be searched for potential fliers.')
        ff_parser.add_argument('output_folder', type=str,
                               help='The output folder for the results of the search.')
        ff_parser.add_argument('-enforce_height', required=False, type=float, default=None,
                               help='Pass a value in meters (e.g., 1.0) to enforce a specific height value. '
                                    'Otherwise, the height value will be automatically estimated.')
        ff_parser.add_argument('-check_laplacian', required=False, type=bool, default=False,
                               help='True to enable the Laplacian Operator Check.')
        ff_parser.add_argument('-check_curv', required=False, type=bool, default=True,
                               help='True to enable the Gaussian Curvature Check.')
        ff_parser.add_argument('-check_adjacent', required=False, type=bool, default=True,
                               help='True to enable the Adjacent Cell Check.')
        ff_parser.add_argument('-check_isolated', required=False, type=bool, default=True,
                               help='True to enable the Isolated Nodes Check.')
        ff_parser.add_argument('-check_slivers', required=False, type=bool, default=True,
                               help='True to enable the Edge Slivers Check.')
        ff_parser.add_argument('-check_edges', required=False, type=bool, default=False,
                               help='True to enable the Noisy Edges Check.')
        ff_parser.add_argument('-check_margins', required=False, type=bool, default=False,
                               help='True to enable the Noisy Margins Check.')
        ff_parser.add_argument('-filter_designated', required=False, type=bool, default=False,
                               help='True to enable filtering of designated soundings.')
        ff_parser.add_argument('-filter_fff', required=False, type=bool, default=False,
                               help='True to enable filtering of S57 features.')
        ff_parser.add_argument('-s57_path', required=False, type=str, default=None,
                               help="Path to the S57 file used by '-filter_fff True'.")
        ff_parser.set_defaults(func=self.run_find_fliers)

        self._web = None 

    def run(self):
        self._web = WebRenderer(make_app=True)
        args = self.parser.parse_args()
        try:
            args.func(args)
        except AttributeError as e:
            if "'Namespace' object" not in str(e):
                logger.info(e)
            self.parser.print_help()
            self.parser.exit()

    def _check_web_page(self, token: str = ""):
        try:
            if len(token) > 0:
                url = "%s_cli_%s" % (Helper(lib_info=lib_info).web_url(), token)
            else:
                url = "%s_cli" % Helper(lib_info=lib_info).web_url()
            self._web.open(url=url)
            logger.debug('check %s' % url)

        except Exception as e:
            logger.warning(e)

    @classmethod
    def _check_latest_release(cls):
        try:
            url = "https://www.hydroffice.org/latest/qctools.txt"
            response = urlopen(url, timeout=1)
            latest_version = response.read().split()[0].decode()
            cur_maj, cur_min, cur_fix = app_info.app_version.split('.')
            lat_maj, lat_min, lat_fix = latest_version.split('.')

            if int(lat_maj) > int(cur_maj):
                logger.info("new release available: %s" % latest_version)

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) > int(cur_min)):
                logger.info("new release available: %s" % latest_version)

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) == int(cur_min)) and (int(lat_fix) > int(cur_fix)):
                logger.info("new bugfix available: %s" % latest_version)

        except Exception as e:
            logger.warning(e)

    def run_find_fliers(self, args):

        if not os.path.exists(args.output_folder):
            raise RuntimeError('Unable to locate output folder: %s' % args.output_folder)
        out_folder = args.output_folder
        logger.debug('output folder: %s' % out_folder)
        # create the project
        prj = SurveyProject(output_folder=out_folder)

        if not os.path.exists(args.input_dtm):
            raise RuntimeError('Unable to locate input DTM: %s' % args.input_dtm)
        dtm_file = args.input_dtm
        logger.debug('input DTM: %s' % dtm_file)
        prj.add_to_grid_list(dtm_file)

        if args.s57_path is not None:
            if not os.path.exists(args.s57_path):
                raise RuntimeError('Unable to locate input S57: %s' % args.s57_path)
            s57_file = args.s57_path
            logger.debug('input S57: %s' % s57_file)
            prj.add_to_s57_list(s57_file)

        if args.enforce_height is not None:
            if args.enforce_height <= 0.0:
                raise RuntimeError('Invalid height: %s' % args.enforce_height)
        height_value = args.enforce_height
        # logger.debug('height: %s' % height_value)

        check_laplacian = args.check_laplacian
        check_curv = args.check_curv
        check_adjacent = args.check_adjacent
        check_slivers = args.check_slivers
        check_isolated = args.check_isolated
        check_edges = args.check_edges
        check_margins = args.check_margins

        filter_designated = args.filter_designated
        filter_fff = args.filter_fff

        self._check_web_page(token='FFv8_%d%d%d%d%d%d%d_%d%d' % (check_laplacian, check_curv, check_adjacent,
                                                                 check_slivers, check_isolated, check_edges,
                                                                 check_margins,
                                                                 filter_designated, filter_fff))

        # actual execution
        for i, grid_path in enumerate(prj.grid_list):
            logger.debug(">>> #%d (%s)" % (i, grid_path))

            prj.clear_survey_label()
            prj.set_cur_grid(path=grid_path)
            prj.open_to_read_cur_grid(chunk_size=4294967296)

            prj.find_fliers_v9(height=height_value,
                               check_laplacian=check_laplacian,
                               check_curv=check_curv,
                               check_adjacent=check_adjacent,
                               check_slivers=check_slivers,
                               check_isolated=check_isolated,
                               check_edges=check_edges,
                               check_margins=check_margins,
                               filter_fff=filter_fff,
                               filter_designated=filter_designated)
            prj.close_cur_grid()

            prj.set_cur_grid(path=grid_path)
            prj.open_to_read_cur_grid(chunk_size=4294967296)
            prj.find_fliers_v8_apply_filters()

            saved = prj.save_fliers()
            if saved:
                logger.debug('Fliers saved')
