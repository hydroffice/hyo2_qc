import logging
import os
import traceback
from typing import List, Optional

from hyo2.s57.s57 import S57, S57File

logger = logging.getLogger(__name__)


class Features:

    def __init__(self):

        # features
        self._cur_s57 = None  # type: Optional[S57File]
        self._cur_s57_path = str()
        self._cur_s57_basename = str()
        self._s57_list = list()

        # SS
        self._cur_ss = None  # type: Optional[S57File]
        self._cur_ss_path = str()
        self._cur_ss_basename = str()
        self._ss_list = list()

    # _______________________________________________________________________________
    # ######################        S57 LIST METHODS        #########################

    @property
    def cur_s57(self) -> Optional[S57File]:
        return self._cur_s57

    @property
    def s57_list(self) -> List[str]:
        return self._s57_list

    def add_to_s57_list(self, s57_path: str) -> None:
        if not os.path.exists(s57_path):
            raise RuntimeError("The passed file does not exist: %s" % s57_path)

        # check if supported format
        if os.path.splitext(s57_path)[-1] != ".000":
            logger.warning('skipping unknown s57 file extension for %s' % s57_path)
            return

        # avoid file path duplications
        if s57_path in self._s57_list:
            logger.warning('the file already present: %s' % s57_path)
            return

        for s57_file in self._s57_list:
            if os.path.splitext(s57_path)[0] == os.path.splitext(s57_file)[0]:
                logger.warning('the file basename is already present: %s' % s57_path)
                return

        self._s57_list.append(s57_path)

    def remove_from_s57_list(self, s57_path: str) -> None:
        # case that the s57 file is not in the list
        if s57_path not in self._s57_list:
            logger.warning('the file is not present: %s' % s57_path)
            # logger.warning('s57 files: %s' % self._s57_list)
            return

        self._s57_list.remove(s57_path)

    def clear_s57_list(self) -> None:
        self._s57_list = list()

    @property
    def cur_s57_basename(self) -> str:
        if self.has_s57():
            return self._cur_s57_basename
        else:
            return str()

    @property
    def cur_s57_path(self) -> str:
        if self.has_s57():
            return self._cur_s57_path
        else:
            return str()

    @property
    def cur_ss_basename(self) -> str:
        if self.has_ss():
            return self._cur_ss_basename
        else:
            return str()

    @property
    def cur_ss_path(self) -> str:
        if self.has_ss():
            return self._cur_ss_path
        else:
            return str()

    # ________________________________________________________________________________
    # ############################## FEATURE READ METHODS ############################

    def has_s57(self) -> bool:
        """Return if S57 present"""
        return bool(self._cur_s57)

    def read_feature_file(self, feature_path: str) -> None:
        if not os.path.exists(feature_path):
            raise RuntimeError('the passed path does not exist: %s' % feature_path)

        if os.path.splitext(feature_path)[-1] == ".000":
            self._read_s57_file(feature_path)

        else:
            raise RuntimeError('unknown feature file extension for %s' % feature_path)

    def _read_s57_file(self, s57_path: str) -> None:
        """Read the S57 file"""
        try:
            s57 = S57()
            s57.set_input_filename(s57_path)
            s57.read()
            self._cur_s57 = s57.input_s57file
            self._cur_s57_path = s57_path
            self._cur_s57_basename = os.path.basename(self._cur_s57_path)
            # logger.debug("Read S57 file: %s %s" % (s57_path, self._cur_s57))

        except Exception as e:
            self._cur_s57 = None
            self._cur_s57_path = None
            self._cur_s57_basename = None
            raise e

    # ________________________________________________________________________________
    # ##############################   SS READ METHODS   #############################

    @property
    def cur_ss(self) -> Optional[S57File]:
        return self._cur_ss

    def has_ss(self) -> bool:
        """Return if SS present"""

        return bool(self._cur_ss)

    def read_ss_file(self, ss_path: str) -> None:
        if not os.path.exists(ss_path):
            raise RuntimeError('the passed path does not exist: %s' % ss_path)

        if os.path.splitext(ss_path)[-1] == ".000":
            self._read_ss_file(ss_path)

        else:
            raise RuntimeError('unknown ss file extension for %s' % ss_path)

    def _read_ss_file(self, ss_path: str) -> None:
        """Read the SS file"""
        try:
            ss = S57()
            ss.set_input_filename(ss_path)
            ss.read()
            self._cur_ss = ss.input_s57file
            self._cur_ss_path = ss_path
            self._cur_ss_basename = os.path.basename(self._cur_ss_path)

        except Exception as e:
            self._cur_ss = None
            self._cur_ss_path = None
            self._cur_ss_basename = None
            raise e

    # _______________________________________________________________________________
    # ######################        SS LIST METHODS        #########################

    @property
    def ss_list(self) -> List[str]:
        return self._ss_list

    def add_to_ss_list(self, ss_path: str) -> None:
        if not os.path.exists(ss_path):
            raise RuntimeError("The passed file does not exist: %s" % ss_path)

        # check if supported format
        if os.path.splitext(ss_path)[-1] != ".000":
            logger.warning('skipping unknown s57 file extension for %s' % ss_path)
            return

        # avoid file path duplications
        if ss_path in self._ss_list:
            logger.warning('the file already present: %s' % ss_path)
            return

        for ss_file in self._ss_list:
            if os.path.splitext(ss_path)[0] == os.path.splitext(ss_file)[0]:
                logger.warning('the file basename is already present: %s' % ss_path)
                return

        self._ss_list.append(ss_path)

    def remove_from_ss_list(self, ss_path: str) -> None:
        # case that the s57 file is not in the list
        if ss_path not in self._ss_list:
            logger.warning('the file is not present: %s' % ss_path)
            return

        self._ss_list.remove(ss_path)

    def clear_ss_list(self) -> None:
        self._ss_list = list()

    # _______________________________________________________________________________
    # ######################        TRUNCATE METHODS        #########################

    @classmethod
    def truncate(cls, input_file: str, output_file: str, decimal_places: int) -> bool:

        try:
            s57 = S57()
            s57.set_input_filename(input_file)
            s57.read()
            s57.depth_truncate(output_file, decimal_places)

            return True

        except Exception as e:
            traceback.print_exc()
            logger.warning("Issue in truncating, %s" % e)
            return False
