import os
import unittest

from hyo2.qc.common.helper import Helper


class TestQC2CommonHelper(unittest.TestCase):

    def test_explore_folder_with_fake_path(self):
        self.assertFalse(Helper.explore_folder('z:/fake/path'))

    def test_filesize(self):
        self.assertGreater(Helper.file_size(__file__), 0)

    def test_first_match(self):
        # fake dict
        a_dict = {
            "a": 1,
            "b": 99,
            "c": 1,
        }

        # test if it gives back the first matching key
        self.assertEqual(Helper.first_match(a_dict, 1), "a")

        # test if it raises with a not-existing value
        with self.assertRaises(RuntimeError):
            Helper.first_match(a_dict, 2)

    def test_info_libs(self):
        msg = Helper.info_libs().lower()
        # logger.info(msg)
        self.assertTrue('hyo' in msg)
        self.assertTrue('matplotlib' in msg)
        self.assertTrue('pyside' in msg)
        self.assertTrue('gdal' in msg)
        self.assertTrue('pyproj' in msg)

    def test_is_64bit_os(self):
        self.assertEqual(type(Helper.is_64bit_os()), bool)

    def test_is_64bit_python(self):
        self.assertEqual(type(Helper.is_64bit_python()), bool)

    def test_is_pydro(self):
        self.assertEqual(type(Helper.is_pydro()), bool)

    def test_os(self):
        if Helper.is_windows():
            self.assertFalse(Helper.is_darwin())
            self.assertFalse(Helper.is_linux())

        elif Helper.is_darwin():
            self.assertFalse(Helper.is_windows())
            self.assertFalse(Helper.is_linux())

        elif Helper.is_linux():
            self.assertFalse(Helper.is_windows())
            self.assertFalse(Helper.is_darwin())

    def test_python_path(self):
        """Test python path"""

        python_path = Helper.python_path()
        self.assertTrue(os.path.exists(python_path))

    def test_qc2_package_folder(self):
        """Test qc package folder"""

        qc_path = Helper.qc2_package_folder()
        self.assertTrue(os.path.exists(qc_path))


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQC2CommonHelper))
    return s
