import os
from hyo2.abc.lib.lib_info import LibInfo
from hyo2.qc import name
from hyo2.qc import __version__


lib_info = LibInfo()

lib_info.lib_name = name
lib_info.lib_version = __version__
lib_info.lib_author = "Giuseppe Masetti(UNH,CCOM); Tyanne Faulkes(NOAA,OCS); Julia Wallace(NOAA,OCS); " \
                      "Matthew Wilson(NOAA,OCS); Brian Calder(UNH,CCOM)"
lib_info.lib_author_email = "gmasetti@ccom.unh.edu; tyanne.faulkes@noaa.gov; julia.wallace@noaa.gov; " \
                            "matthew.wilson@noaa.gov; brc@ccom.unh.edu"

lib_info.lib_license = "LGPL v3"
lib_info.lib_license_url = "https://www.hydroffice.org/license/"

lib_info.lib_path = os.path.abspath(os.path.dirname(__file__))

lib_info.lib_url = "https://www.hydroffice.org/qctools/"
lib_info.lib_manual_url = "https://www.hydroffice.org/manuals/qctools/index.html"
lib_info.lib_support_email = "qctools@hydroffice.org"
lib_info.lib_latest_url = "https://www.hydroffice.org/latest/qctools.txt"

lib_info.lib_dep_dict = {
    "hyo2.abc": "hyo2.abc",
    "hyo2.s57": "hyo2.s57",
    "hyo2.grids": "hyo2.grids",
    "gdal": "osgeo",
    "numpy": "numpy",
    "pyproj": "pyproj",
    "h5py": "h5py",
    "PySide2": "PySide2",
    "scipy": "scipy",
    "pillow": "PIL",
    "piexif": "piexif",
}
