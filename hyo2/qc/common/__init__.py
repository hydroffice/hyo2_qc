import os

from hyo2.abc.lib.lib_info import LibInfo
from hyo2.qc import __version__
from hyo2.qc import name

lib_info = LibInfo()

lib_info.lib_name = name
lib_info.lib_version = __version__
lib_info.lib_author = "Giuseppe Masetti(UNH,CCOM); Tyanne Faulkes(NOAA,OCS); Matthew Wilson(NOAA,OCS)"
lib_info.lib_author_email = "gmasetti@ccom.unh.edu; tyanne.faulkes@noaa.gov; matthew.wilson@noaa.gov"

lib_info.lib_license = "LGPL v3"
lib_info.lib_license_url = "https://www.hydroffice.org/license/"

lib_info.lib_path = os.path.abspath(os.path.dirname(__file__))

lib_info.lib_url = "https://www.hydroffice.org/qctools/"
lib_info.lib_manual_url = "https://www.hydroffice.org/manuals/qctools/stable/index.html"
lib_info.lib_support_email = "qctools@hydroffice.org"
lib_info.lib_latest_url = "https://www.hydroffice.org/latest/qctools.txt"

lib_info.lib_dep_dict = {
    "hyo2.abc": "hyo2.abc",
    "hyo2.bag": "hyo2.bag",
    "hyo2.grids": "hyo2.grids",
    "hyo2.s57": "hyo2.s57",
    "gdal": "osgeo",
    "h5py": "h5py",
    "numpy": "numpy",
    "piexif": "piexif",
    "pillow": "PIL",
    "pyproj": "pyproj",
    "PySide2": "PySide2",
    "scipy": "scipy",
}
