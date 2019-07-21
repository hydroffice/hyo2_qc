import sys
import os
import argparse
import win32api

from hyo2.abc.lib.logging import set_logging
import logging

set_logging(ns_list=["hyo2.qc",])
logger = logging.getLogger()


def run_qc_tools_v3(grid_path, flier_finder, holiday_finder, holiday_finder_mode, grid_qa,
                    survey_name, output_shp=False, output_kml=False):
    from hyo2.qc.survey.project import SurveyProject
    from hyo2.qc import __version__
    print("\n-->> running QC Tools (v.%s)" % __version__)

    grid_folder, grid_name = os.path.split(grid_path)
    prj = SurveyProject(output_folder=grid_folder)

    # disable output formats except .000
    prj.output_svp = False
    prj.output_shp = False
    prj.output_kml = False

    prj.add_to_grid_list(grid_path)

    if survey_name is None:
        prj.clear_survey_label()
    else:
        prj.survey_label = survey_name

    if flier_finder:
        print('running flier finder on: %s' % grid_path)
        prj.set_cur_grid(path=grid_path)
        prj.open_to_read_cur_grid()

        prj.find_fliers_v8(height=None)
        saved = prj.save_fliers()
        if saved:
            print('- found fliers: %d' % prj.number_of_fliers())
        else:
            print('- no fliers found')

    if holiday_finder:
        print('running holiday finder on: %s' % grid_path)

        prj.find_holes_v4(path=grid_path, mode=holiday_finder_mode)
        prj.output_shp = output_shp
        prj.output_kml = output_kml
        saved = prj.save_holes()
        if saved:
            print('- found holidays: certain %d, possible %d'
                  % (prj.number_of_certain_holes(), prj.number_of_possible_holes()))
        else:
            print('- no holidays')

    if grid_qa:
        print('running grid qa on: %s' % grid_path)
        prj.set_cur_grid(path=grid_path)
        prj.open_to_read_cur_grid()

        tvu_qc_layers = prj.cur_grid_tvu_qc_layers()
        if len(tvu_qc_layers) > 0:
            prj.set_cur_grid_tvu_qc_name(tvu_qc_layers[0])
        ret = prj.grid_qa_v5()
        print("- passed? %r" % ret)

    if grid_qa:
        prj.open_gridqa_output_folder()
        return
    if holiday_finder:
        prj.open_holes_output_folder()
        return
    if flier_finder:
        prj.open_fliers_output_folder()
        return


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def make_parser():
    parser = argparse.ArgumentParser(description='Run QCTools from the command line')
    parser.add_argument("grid_path", help="Full path to input dataset")
    parser.add_argument("flier_finder", type=str2bool, help="Should Flier Finder be run, boolean (yes,true,1 or no,false,0)")
    parser.add_argument("holiday_finder", type=str2bool, help="Should Holiday Finder be run, boolean (yes,true,1 or no,false,0)")
    parser.add_argument("holiday_finder_mode", help='Holiday Finder Mode -- "OBJECT_DETECTION" or "FULL_COVERAGE" are accepted')
    parser.add_argument("grid_qa", type=str2bool, help="Should Grid QA be run, boolean (yes,true,1 or no,false,0)")
    parser.add_argument("survey_name", default="None", help="Full path to output folder (.000 and any optional formats will be created here)")
    parser.add_argument("--SHP", action="store_true", help="Output a shapefile in addition to default .000")
    parser.add_argument("--KML", action="store_true", help="Output a KML file in addition to default .000")

    return parser


def main():
    print(">>> QC SCRIPTS <<<")
    parser = make_parser()
    # show help if no arguments were supplied
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        sys.exit()
    args = parser.parse_args()

    # first just print the arguments as they are received (for DEBUGGING)
    print("raw arguments:")
    for i, arg in enumerate(sys.argv):
        print(" - #%d: %s" % (i, arg))

    # interpreting/checking the passed arguments
    grid_path = win32api.GetLongPathName(args.grid_path)
    if not os.path.exists(grid_path):
        raise RuntimeError("the passed path does not exist: %s" % grid_path)
    if (args.holiday_finder_mode != "OBJECT_DETECTION") and (args.holiday_finder_mode != "FULL_COVERAGE"):
        raise RuntimeError("invalid holiday finder mode: %s" % args.holiday_finder_mode)

    # print the interpreted arguments (for DEBUGGING)
    print("\ninterpreted arguments:")
    print(" - grid path: %s" % grid_path)
    print(" - flier finder: %r" % (args.flier_finder))
    print(" - holiday finder: %r (mode: %s)" % (args.holiday_finder, args.holiday_finder_mode))
    print(" - grid qa: %r" % args.grid_qa)
    print(" - survey name: %r" % args.survey_name)
    print(" - output shape files: %r" % args.SHP)
    print(" - output KML files: %r" % args.KML)

    run_qc_tools_v3(grid_path=grid_path,
                    flier_finder=args.flier_finder,
                    holiday_finder=args.holiday_finder, holiday_finder_mode=args.holiday_finder_mode,
                    grid_qa=args.grid_qa,
                    survey_name=args.survey_name,
                    output_shp=args.SHP,
                    output_kml=args.KML)


if __name__ == '__main__':
    main()
