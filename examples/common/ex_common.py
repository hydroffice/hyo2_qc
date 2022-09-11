from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.logging import set_logging
from hyo2.qc.common import lib_info
from hyo2.qc.common import testing

set_logging(ns_list=["hyo2.qc", ])

Helper.explore_folder(Helper(lib_info=lib_info).package_folder())
Helper(lib_info=lib_info).explore_package_folder()

print("- This file size: %s" % Helper.file_size(__file__))

print("- Info libs:\n%s" % Helper(lib_info=lib_info).package_info())

print("- Python path: %s" % Helper.python_path())

print("- QC2 package folder: %s" % Helper(lib_info=lib_info).package_folder())

print("- Testing output: %s" % testing.output_data_folder())

print("- Web URL: %s" % Helper(lib_info=lib_info).web_url(suffix="test"))
