import os

from hyo2.abc.app.app_info import AppInfo
from hyo2.qc import __version__
from hyo2.qc import name

app_info = AppInfo()

app_info.app_name = name
app_info.app_version = __version__
app_info.app_author = "Giuseppe Masetti(UNH,CCOM); Tyanne Faulkes(NOAA,OCS); Matthew Wilson(NOAA,OCS)"
app_info.app_author_email = "gmasetti@ccom.unh.edu; tyanne.faulkes@noaa.gov; matthew.wilson@noaa.gov"

app_info.app_license = "LGPL v3"
app_info.app_license_url = "https://www.hydroffice.org/license/"

app_info.app_path = os.path.abspath(os.path.dirname(__file__))

app_info.app_url = "https://www.hydroffice.org/qctools/"
app_info.app_manual_url = "https://www.hydroffice.org/manuals/qctools/stable/index.html"
app_info.app_support_email = "qctools@hydroffice.org"
app_info.app_latest_url = "https://www.hydroffice.org/latest/qctools.txt"

app_info.app_media_path = os.path.join(app_info.app_path, "media")
app_info.app_main_window_object_name = "MainWindow"
app_info.app_license_path = os.path.join(app_info.app_media_path, "LICENSE")
app_info.app_icon_path = os.path.join(app_info.app_media_path, "app_icon.png")

# icon size
app_info.app_tabs_icon_size = 36
app_info.app_toolbars_icon_size = 24
