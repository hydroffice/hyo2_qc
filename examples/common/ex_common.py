from hyo2.qc.common import default_logging

from hyo2.qc.common.helper import Helper
from hyo2.qc.common import testing

default_logging.load()

Helper.explore_folder(Helper.qc2_package_folder())
Helper.explore_qc2_package_folder()

print("- This file size: %s" % Helper.file_size(__file__))

print("- Info libs:\n%s" % Helper.info_libs())

print("- Python path: %s" % Helper.python_path())

print("- QC2 package folder: %s" % Helper.qc2_package_folder())

print("- Testing output: %s" % testing.output_data_folder())

s57_file = testing.input_test_files(".000")[0]
print("- Has ENC updates: %s" % (len(Helper.list_enc_updates(s57_file)) > 0, ))

print("- Web URL: %s" % Helper.web_url(suffix="text", then_call=True))
