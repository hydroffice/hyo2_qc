import argparse
from hyo2.qc import __version__


class CliCommands:

    def __init__(self):
        self.parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.parser.add_argument('--version', action='version', version=__version__)
        self.subparsers = self.parser.add_subparsers()

        self.ff_parser = self.subparsers.add_parser('flier_finder',
                                                    help='Identify potential fliers in gridded bathymetry',
                                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.ff_parser.add_argument('input_dtm', type=str,
                                    help='The input DTM file to be searched for potential fliers.')
        self.ff_parser.add_argument('output_folder', type=str,
                                    help='The output folder for the results of the search.')
        self.ff_parser.add_argument('--enforce_height', required=False, type=float, default=None,
                                    help='Pass a value in meters (e.g., 1.0) to enforce a specific height value. '
                                         'Otherwise, the height value will be automatically estimated.')
        self.ff_parser.add_argument('-l', '--check_laplacian', required=False, type=bool, default=False,
                                    help='True to enable the Laplacian Operator Check.')
        self.ff_parser.add_argument('-c', '--check_curv', required=False, type=bool, default=True,
                                    help='True to enable the Gaussian Curvature Check.')
        self.ff_parser.add_argument('-a', '--check_adjacent', required=False, type=bool, default=True,
                                    help='True to enable the Adjacent Cell Check.')
        self.ff_parser.add_argument('-i', '--check_isolated', required=False, type=bool, default=True,
                                    help='True to enable the Isolated Nodes Check.')
        self.ff_parser.add_argument('-v', '--check_slivers', required=False, type=bool, default=True,
                                    help='True to enable the Edge Slivers Check.')
        self.ff_parser.add_argument('-e', '--check_edges', required=False, type=bool, default=False,
                                    help='True to enable the Noisy Edges Check.')
        self.ff_parser.add_argument('-m', '--check_margins', required=False, type=bool, default=False,
                                    help='True to enable the Noisy Margins Check.')
        self.ff_parser.add_argument('--filter_designated', required=False, type=bool, default=False,
                                    help='True to enable filtering of designated soundings.')
        self.ff_parser.add_argument('--filter_fff', required=False, type=bool, default=False,
                                    help='True to enable filtering of S57 features.')
        self.ff_parser.add_argument('--filter_distance_multiplier', type=float, default=1.0,
                                    help='Remove flags at the passed distance from the FFF or designated features. '
                                         'Distance expressed as a multiple of the grid resolution.')
        self.ff_parser.add_argument('--filter_delta_z', type=float, default=0.01,
                                    help='Remove flags within the passed delta Z from the FFF or designated features. '
                                         'The delta Z is expressed in meters.')
        self.ff_parser.add_argument('--s57_path', required=False, type=str, default=None,
                                    help="Path to the S57 file used by '-filter_fff True'.")
        self.ff_parser.add_argument('-k', '--enable_kml_output', required=False, type=bool, default=False,
                                    help='True to enable KML as an additional output format for the flags.')
        self.ff_parser.add_argument('-s', '--enable_shp_output', required=False, type=bool, default=False,
                                    help='True to enable Shapefile as an additional output format for the flags.')


def get_parser():
    return CliCommands().parser
