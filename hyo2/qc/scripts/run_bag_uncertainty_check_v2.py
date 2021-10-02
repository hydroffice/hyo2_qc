import logging
import os

from PySide2 import QtCore, QtWidgets
from hyo2.qc.common import default_logging

default_logging.load()
logger = logging.getLogger()

#version: 0.1

# set settings

ask_for_input_folder = True
ask_for_output_folder = True
write_report_on_disk = True
open_output_folder = True

# create a Qt application (required to get the dialog to select folders)

app = QtWidgets.QApplication([])
app.setApplicationName('run_bag_uncertainty_check')
app.setOrganizationName("HydrOffice")
app.setOrganizationDomain("hydroffice.org")

# manage the input folder by asking to user OR using the hand-written path

if ask_for_input_folder:
    # noinspection PyArgumentList
    input_folder = QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption="Select input folder with BAGs",
                                                              dir=QtCore.QSettings().value(
                                                                  "run_bag_uncertainty_check_folder"))

    if input_folder == str():
        logger.error("input folder not selected")
        exit(-1)

    QtCore.QSettings().setValue("run_bag_uncertainty_check_folder", input_folder)

else:
    input_folder = "U:\\Working\\QCTools\\scripts"

    if not os.path.exists(input_folder):
        logger.error("input folder does not exist: %s" % input_folder)
        exit(-1)

    if not os.path.isdir(input_folder):
        logger.error("input folder is actually not a folder: %s" % input_folder)
        exit(-1)

logger.debug("input folder: %s" % input_folder)

# create a list with all the BAG paths (walking recursively across the sub-folders, if present)

bag_todo_list = list()
try:  # Trapping Exceptions like OSError (File permissions)
    for root, dirs, files in os.walk(input_folder):

        for file in files:

            if file.lower().endswith(".bag"):
                bag_todo_list.append(os.path.join(root, file))

except Exception as e:
    logger.warning("issue in walking through the input folder: %s" % e)

nr_bag_todo = len(bag_todo_list)
if nr_bag_todo == 0:
    logger.error("not BAG files accessible in the input folder: %s" % input_folder)
    exit(-1)

logger.debug("BAG listed: %d" % nr_bag_todo)

# manage the output folder by asking to user OR using the hand-written path (required to instantiate a SurveyProject)

if ask_for_output_folder:
    # noinspection PyArgumentList
    output_folder = QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption="Select output folder",
                                                               dir=QtCore.QSettings().value(
                                                                   "run_bag_uncertainty_check_output_folder"))

    if output_folder == str():
        logger.error("output folder not selected")
        exit(-1)

    QtCore.QSettings().setValue("run_bag_uncertainty_check_output_folder", output_folder)

else:
    output_folder = "U:\\Working\\QCTools\\scripts"

    if not os.path.exists(output_folder):
        logger.error("output folder does not exist: %s" % output_folder)
        exit(-1)

    if not os.path.isdir(output_folder):
        logger.error("output folder is actually not a folder: %s" % output_folder)
        exit(-1)

logger.debug("output folder: %s" % output_folder)

# begin v2 code

import numpy as np
from hyo2.bag import bag
from hyo2.bag.meta import Meta
import datetime

##t=datetime.datetime.now()
##year=str(t.year)
##month=str(t.month)
datetime_string=str(datetime.datetime.now())
datetime_string=datetime_string.split('.')[0]
datetime_string=datetime_string.replace(':','')
report_filename = 'BAG_CHECK_output_'+datetime_stringcd+'.txt'
report_full_filename = os.path.join(output_folder,report_filename)
f = open(report_full_filename,'x')

for b in range(0,len(bag_todo_list)):
    w=bag.BAGFile(bag_todo_list[b])
    print('\n',bag_todo_list[b],'\n')
    f.write('\n** '+bag_todo_list[b]+' **\n')

    meta = Meta(w.metadata())
    output_xml = bag_todo_list[b]+'_metadata.xml'
    w.extract_metadata(output_xml)

    fyle = open(output_xml)
    while 1:
        line = fyle.readline()
        if 'DATUM' in line:
            datum = line
        if 'WGS 84' in line:
            check_passed = 1
            break
        if 'NAD 83' in line:
            check_passed = 2
            break
        if not line:
            check_passed = 0
            break

    if check_passed==1:
        print('WGS 84 identified! Here is the datum information found:')
        f.write('\nWGS 84 identified! Here is the datum information found:\n')
        print(datum)
        f.write(datum)
    elif check_passed==2:
        print('NAD 83 identified! Here is the datum information found:')
        f.write('\nNAD 83 identified! Here is the datum information found:\n')
        print(datum)
        f.write(datum)
    else:
        print('Warning: WGS 84 or NAD 83 could not be identified! Here is the datum information found:')
        f.write('\nWarning: WGS 84 or NAD 83 could not be identified! Here is the datum information found:\n')
        print(datum)
        f.write(datum)

    if w.has_uncertainty():
        
        elevation=w.elevation()
        uncertainty=w.uncertainty()
        max_depth=0
        min_depth=-1e5

        for m in range(0,len(elevation)):
            for n in range(0,len(elevation[m])):
                if elevation[m][n]<max_depth:
                    max_depth=elevation[m][n]
                    max_depth_idx=[m,n]
                if elevation[m][n]>min_depth:
                    min_depth=elevation[m][n]
                    min_depth_idx=[m,n]

        uncertainty_flag=abs(np.average([max_depth,min_depth]))

        max_uncert=0
        min_uncert=1e5

        high_uncert_tracker=list()
        zero_uncert_tracker=list()
        negative_uncert_tracker=list()

        for m in range(0,len(uncertainty)):
            for n in range(0,len(uncertainty[m])):
                if uncertainty[m][n]>max_uncert:
                    max_uncert=uncertainty[m][n]
                    max_uncert_idx=[m,n]
                if uncertainty[m][n]<min_uncert:
                    min_uncert=uncertainty[m][n]
                    min_uncert_idx=[m,n]
                if uncertainty[m][n]>=uncertainty_flag:
                    high_uncert_tracker.append([uncertainty[m][n],[m,n]])
                if uncertainty[m][n]==0:
                    zero_uncert_tracker.append([uncertainty[m][n],[m][n]])
                if uncertainty[m][n]<0:
                    negative_uncertainty_tracker=list()

        print('max elevation',abs(max_depth),'at index',max_depth_idx)
        print('min elevation',abs(min_depth),'at index',min_depth_idx)
        print('max uncert',max_uncert,'at index',max_uncert_idx)
        print('min uncert',min_uncert,'at index',min_uncert_idx)
        print(len(high_uncert_tracker),'cells were flagged for having uncertainty greater than',uncertainty_flag)
        print(len(zero_uncert_tracker),'cells were flagged for having uncertainty equal to zero')
        print(len(negative_uncert_tracker),'cells were flagged for having uncertainty less than zero')
        f.write('\nmax elevation '+str(abs(max_depth))+' at index '+str(max_depth_idx))
        f.write('\nmin elevation '+str(abs(min_depth))+' at index '+str(min_depth_idx))
        f.write('\nmax uncert '+str(max_uncert)+' at index '+str(max_uncert_idx))
        f.write('\nmin uncert '+str(min_uncert)+' at index '+str(min_uncert_idx))
        f.write('\n'+str(len(high_uncert_tracker))+' cells were flagged for having uncertainty greater than '+str(uncertainty_flag))
        f.write('\n'+str(len(zero_uncert_tracker))+' cells were flagged for having uncertainty equal to zero')
        f.write('\n'+str(len(negative_uncert_tracker))+' cells were flagged for having uncertainty less than zero') 
        if len(high_uncert_tracker)+len(zero_uncert_tracker)+len(negative_uncert_tracker)==0:
            print('BAG passed this check!')
            f.write('\nBAG passed this check!\n')
        else:
            print('BAG failed this check!')
            f.write('\nBAG failed this check!\n')

    else:
        print('No uncertainty layer.')
        f.write('\nNo uncertainty layer.\n')
        print('BAG failed this check!')
        f.write('\nBAG failed this check!\n')
f.close()

print('\nCheck the output directory for the printed report.')

stop=0
while stop==0:
    user_input=input('\nEnter q to quit ')
    if user_input=='q':
        stop=1
        break

## run_bag_uncertainty_check_v1 code:

### create the project
##
##prj = SurveyProject(output_folder=output_folder)
##
### add all the BAG files to the project
##
##for bag_path in bag_todo_list:
##    prj.add_to_grid_list(bag_path)
##
### create 3 empty lists: one for the BAGs successfully processed, one for the ones without Uncertainty lauyer,
### and another for crashes
##
##bag_done_list = list()
##bag_without_uncertainty_list = list()
##bag_crash_list = list()
##
### actually processing the BAG files
##
##for i, bag_path in enumerate(prj.grid_list):
##
##    try:  # Trapping Exceptions like OSError (File permissions)
##
##        logger.debug(">>>>>> #%03d (%s): processing ..." % (i, bag_path))
##
##        prj.clear_survey_label()
##        prj.open_grid(path=bag_path)
##
##        max_uncert = prj.retrieve_max_uncert(bag_path)
##        min_uncert = prj.retrieve_min_uncert(bag_path)
##        # manage the two possible cases of BAG without uncertainty (None or 0.0)
##        if max_uncert is None:
##            bag_without_uncertainty_list.append(bag_path)
##        elif max_uncert == 0.0:
##            bag_without_uncertainty_list.append(bag_path)
##        elif min_uncert < 0:
##            bag_without_uncertainty_list.append(bag_path)
##        elif min_uncert == 0.0:
##            bag_without_uncertainty_list.append(bag_path)
##
##        bag_done_list.append(bag_path)
##
##        logger.debug(">>>>>> #%03d (%s): OK" % (i, bag_path))
##
##    except Exception as e:
##        logger.warning("******  #%03d (%s): issue in processing (%s)" % (i, bag_path, e))
##        bag_crash_list.append(bag_path)
##        continue
##
### provide a final report (on screen)
##
##report = str()
##report += "- successfully processed: %d/%d\n" % (len(bag_done_list), nr_bag_todo)
##report += "\n- processed without uncertainty: %d/%d\n" % (len(bag_without_uncertainty_list), len(bag_done_list))
##for bag_without_uncertainty in bag_without_uncertainty_list:
##    report += "  . %s\n" % bag_without_uncertainty
##report += "\n- crashes while processing: %d/%d\n" % (len(bag_crash_list), nr_bag_todo)
##for bag_crash in bag_crash_list:
##    report += "  . %s\n" % bag_crash
##
##logger.info("\n%s" % report)
##
### save on disk a final report
##
##if write_report_on_disk:
##
##    report_path = os.path.join(output_folder, "Uncertainty_Scan_Results.txt")
##    try:  # Trapping Exceptions like OSError (File permissions)
##
##        with open(report_path, "w") as fod:
##            fod.write(report)
##
##    except Exception as e:
##        logger.warning("issue in saving report on disk: %s (%s)" % (report_path, e))
##
### open the output folder
##
##if open_output_folder:
##    Helper.explore_folder(output_folder)
##
##logger.debug("DONE!")
