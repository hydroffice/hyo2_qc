import platform
import os
import logging

from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


def load(pyside=True):

    if not pyside:
        raise RuntimeError("unsupported")

    here = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")
    if Helper.is_windows():
        import win32api
        # noinspection PyProtectedMember
        here = win32api.GetLongPathName(here).replace("\\", "/")
    style_path = os.path.join(here, "app.stylesheet").replace("\\", "/")

    # logger.debug(f"here: {here}")
    # logger.debug(f"style path: {style_path}")

    style = str()
    with open(style_path) as fid:
        style = fid.read().replace("LOCAL_PATH", here)

    # print(style)
    if platform.system().lower() == 'darwin':  # see issue #12 on github
        mac_fix = '''
        QDockWidget::title
        {
            background-color: #31363b;
            text-align: center;
            height: 12px;
        }
        '''
        style += mac_fix

    return style
