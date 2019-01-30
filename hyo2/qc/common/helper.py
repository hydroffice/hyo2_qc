import os
import sys
import ctypes
import platform
import subprocess
from datetime import datetime
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
from appdirs import user_data_dir
import logging

from hyo2.qc import __version__ as qc2_version
from hyo2.qc import name as qc2_name

logger = logging.getLogger(__name__)


class Helper:
    """ A collection class with many helper functions, in alphabetic order """

    @classmethod
    def is_url(cls, value):
        if len(value) > 7:

            https = "https"
            if value[:len(https)] == https:
                return True

        return False

    @classmethod
    def explore_folder(cls, path):
        """Open the passed path using OS-native commands"""
        if cls.is_url(path):
            import webbrowser
            webbrowser.open(path)
            return True

        if not os.path.exists(path):
            logger.warning('invalid path to folder: %s' % path)
            return False

        path = os.path.normpath(path)

        if cls.is_darwin():
            subprocess.call(['open', '--', path])
            return True

        elif cls.is_linux():
            subprocess.call(['xdg-open', path])
            return True

        elif cls.is_windows():
            subprocess.call(['explorer', path])
            return True

        logger.warning("Unknown/unsupported OS")
        return False

    @classmethod
    def explore_qc2_package_folder(cls):
        cls.explore_folder(cls.qc2_package_folder())

    @classmethod
    def file_size(cls, file_path: str) -> int:
        """file size in bytes"""
        if not os.path.exists(file_path):
            raise RuntimeError("the passed file does not exist: %s" % file_path)

        return os.stat(file_path).st_size

    @classmethod
    def first_match(cls, dct, val):
        if not isinstance(dct, dict):
            raise RuntimeError("invalid first input: it is %s instead of a dict" % type(dct))

        # print(dct, val)
        values = [key for key, value in dct.items() if value == val]
        if len(values) != 0:
            return values[0]

        else:
            raise RuntimeError("unknown value %s in dict: %s" % (val, dct))

    @classmethod
    def info_libs(cls):
        msg = "- os: %s %s\n" % (os.name, "64" if cls.is_64bit_os() else "32")
        msg += "- python: %s %s-bit\n" % (platform.python_version(), "64" if cls.is_64bit_python() else "32")
        msg += "- pydro: %s\n" % cls.is_pydro()
        version = qc2_version
        msg += "- hyo2.qc: %s\n" % version

        msg += "- dependencies:\n"

        try:
            from hyo2.grids import __version__ as version
        except Exception:
            version = None
        msg += "  . hyo2.grids: %s\n" % version

        try:
            from hyo2.s57 import __version__ as version
        except Exception:
            version = None
        msg += "  . hyo2.s57: %s\n" % version

        try:
            from hyo2.qc.ext.appdirs.appdirs import __version__ as version
        except Exception:
            version = None
        msg += "  . appdirs: %s\n" % version

        try:
            from numpy import __version__ as version
        except Exception:
            version = None
        msg += "  . numpy: %s\n" % version

        try:
            from  scipy import __version__ as version
        except Exception:
            version = None
        msg += "  . scipy: %s\n" % version

        try:
            from matplotlib import __version__ as version
        except Exception:
            version = None
        msg += "  . matplotlib: %s\n" % version

        try:
            from PySide2 import __version__ as version
        except Exception:
            version = None
        msg += "  . pyside2: %s\n" % version

        try:
            from osgeo.gdal import __version__ as version
        except Exception:
            version = None
        msg += "  . gdal: %s\n" % version

        try:
            from pyproj import __version__ as version
        except Exception:
            version = None
        msg += "  . pyproj: %s\n" % version

        return msg

    @classmethod
    def is_64bit_os(cls):
        """ Check if the current OS is at 64 bits """
        return platform.machine().endswith('64')

    @classmethod
    def is_64bit_python(cls):
        """ Check if the current Python is at 64 bits """
        return platform.architecture()[0] == "64bit"

    @classmethod
    def is_darwin(cls):
        """ Check if the current OS is Mac OS """
        return sys.platform == 'darwin'

    @classmethod
    def is_linux(cls):
        """ Check if the current OS is Linux """
        return sys.platform in ['linux', 'linux2']

    @classmethod
    def is_pydro(cls):
        try:
            # noinspection PyUnresolvedReferences
            import HSTB as _
            return True

        except Exception:
            return False

    @classmethod
    def is_user_admin(cls):
        if cls.is_windows():

            if ctypes.windll.shell32.IsUserAnAdmin():
                logger.debug("user is admin")
                return True
            else:
                logger.debug("user is not admin")
                return False

        else:
            raise RuntimeError("Windows only")

    @classmethod
    def is_windows(cls):
        """ Check if the current OS is Windows """
        return (sys.platform == 'win32') or (os.name is "nt")

    @classmethod
    def list_enc_updates(cls, enc_path):
        if os.path.splitext(enc_path)[-1] != ".000":
            raise RuntimeError("expected a S57 (.000) file, but got: %s" % (os.path.basename(enc_path),))

        updates = list()
        # logger.debug("%s" % os.path.splitext(enc_path)[0])
        for i in range(1, 1000):
            update_path = os.path.splitext(enc_path)[0] + ".%03d" % i
            # print(update_path)
            if os.path.exists(update_path):
                updates.append(update_path)

        return updates

    @classmethod
    def python_path(cls):
        """ Return the python site-specific directory prefix (the temporary folder for PyInstaller) """

        # required by PyInstaller
        if hasattr(sys, '_MEIPASS'):
            if cls.is_windows():
                import win32api
                # noinspection PyProtectedMember
                return win32api.GetLongPathName(sys._MEIPASS)
            else:
                return sys._MEIPASS

        # check if in a virtual environment
        if hasattr(sys, 'real_prefix'):

            if cls.is_windows():
                import win32api
                # noinspection PyProtectedMember
                return win32api.GetLongPathName(sys.real_prefix)
            else:
                return sys.real_prefix

        return sys.prefix

    @classmethod
    def qc2_package_folder(cls):
        _dir = user_data_dir(qc2_name, "HydrOffice")
        if not os.path.exists(_dir):  # create it if it does not exist
            os.makedirs(_dir)

        return _dir

    @classmethod
    def timestamp(cls):
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @classmethod
    def total_size(cls, o, handlers=None, verbose=False):

        dict_handler = lambda d: chain.from_iterable(d.items())
        all_handlers = {tuple: iter,
                        list: iter,
                        deque: iter,
                        dict: dict_handler,
                        set: iter,
                        frozenset: iter,
                        }
        if isinstance(handlers, dict):
            all_handlers.update(handlers)  # user handlers take precedence
        seen = set()  # track which object id's have already been seen
        default_size = getsizeof(0)  # estimate sizeof object without __sizeof__

        def sizeof(o):
            if id(o) in seen:  # do not double count the same object
                return 0
            seen.add(id(o))
            s = getsizeof(o, default_size)

            if verbose:
                print(s, type(o), repr(o), file=stderr)

            for typ, handler in all_handlers.items():
                if isinstance(o, typ):
                    s += sum(map(sizeof, handler(o)))
                    break
            return s

        return sizeof(o)

    @classmethod
    def truncate_too_long(cls, path, max_path_length=260, left_truncation=False):

        max_len = max_path_length

        path_len = len(path)
        if path_len < 260:
            return path

        logger.debug("path truncation required since path would be longer than %d [left: %s]" % (max_len, left_truncation))

        folder_path, filename = os.path.split(path)
        file_base, file_ext = os.path.splitext(filename)

        if left_truncation:
            new_len = max_len - len(folder_path) - len(file_ext) - 2
            if new_len < 1:
                raise RuntimeError("the passed path is too long: %d" % path_len)
            path = os.path.join(folder_path, file_base[(len(file_base) - new_len):] + file_ext)

        else:
            new_len = max_len - len(folder_path) - len(file_ext) - 2
            if new_len < 1:
                raise RuntimeError("the passed path is too long: %d" % path_len)
            path = os.path.join(folder_path, file_base[:new_len] + file_ext)

        return path

    @classmethod
    def web_url(cls, suffix=None):

        url = 'https://www.hydroffice.org/qctools/%s' % (qc2_version.replace('.', '_'), )
        if cls.is_pydro():
            url += "_pydro"

        if suffix and isinstance(suffix, str):
            url += "_" + suffix

        return url
