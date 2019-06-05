import sys
import os
import win32api

from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()


def run_qc_tools_v3(grid_path, flier_finder, holiday_finder, holiday_finder_mode, grid_qa,
                    survey_name):
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


def main():

    print(">>> QC SCRIPTS <<<")

    # first just print the arguments as they are received (for DEBUGGING)
    print("raw arguments:")
    for i, arg in enumerate(sys.argv):
        print(" - #%d: %s" % (i, arg))

    exp_nr_argv = 7
    if len(sys.argv) != exp_nr_argv:
        print("ERROR: invalid nunber of arguments: %d (it should be: %d)" % (len(sys.argv), exp_nr_argv))
        return 1

    # interpreting/checking the passed arguments
    grid_path = win32api.GetLongPathName(sys.argv[1])
    if not os.path.exists(grid_path):
        raise RuntimeError("the passed path does not exist: %s" % grid_path)
    flier_finder = sys.argv[2] == "1"
    holiday_finder = sys.argv[3] == "1"
    holiday_finder_mode = sys.argv[4]
    if (holiday_finder_mode != "OBJECT_DETECTION") and (holiday_finder_mode != "FULL_COVERAGE"):
        raise RuntimeError("invalid holiday finder mode: %s" % holiday_finder_mode)
    grid_qa = sys.argv[5] == "1"
    survey_name = None
    if sys.argv[6] != "None":
        survey_name = sys.argv[6]

    # print the interpreted arguments (for DEBUGGING)
    print("\ninterpreted arguments:")
    print(" - grid path: %s" % grid_path)
    print(" - flier finder: %r" % (flier_finder))
    print(" - holiday finder: %r (mode: %s)" % (holiday_finder, holiday_finder_mode))
    print(" - grid qa: %r" % grid_qa)
    print(" - survey name: %r" % survey_name)

    run_qc_tools_v3(grid_path=grid_path,
                    flier_finder=flier_finder,
                    holiday_finder=holiday_finder, holiday_finder_mode=holiday_finder_mode,
                    grid_qa=grid_qa,
                    survey_name=survey_name)


if __name__ == '__main__':
    main()
