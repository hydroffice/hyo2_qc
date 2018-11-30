import os
import unittest

from hyo2.qc.common import testing


class TestQC2CommonTesting(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_root_data_folder(self):
        self.assertTrue(os.path.exists(testing.root_data_folder()))

    def test_input_data_folder(self):
        self.assertTrue(os.path.exists(testing.input_data_folder()))

    def test_output_data_folder(self):
        self.assertTrue(os.path.exists(testing.output_data_folder()))

    def test_download_data_folder(self):
        self.assertTrue(os.path.exists(testing.download_data_folder()))

    def test_download_test_files(self):
        self.assertEqual(len(testing.download_test_files(".bag")), 1)
        self.assertEqual(len(testing.download_test_files(".csar")), 1)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQC2CommonTesting))
    return s