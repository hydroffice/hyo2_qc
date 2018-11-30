import os
import unittest

from hyo2.qc.chart.project import ChartProject
from hyo2.qc.common import testing


class TestQC2ChartGridTruncate(unittest.TestCase):

    def test_init_project_with_folder(self):
        prj = ChartProject(output_folder=testing.output_data_folder())
        self.assertTrue(os.path.exists(prj.output_folder))

    def test_truncate_without_grids(self):
        prj = ChartProject(output_folder=testing.output_data_folder())
        self.assertFalse(prj.grid_truncate())

    def test_truncate_with_wrong_version(self):
        prj = ChartProject(output_folder=testing.output_data_folder())
        prj.add_to_grid_list(testing.input_test_files(".bag")[0])
        self.assertFalse(prj.grid_truncate(version=1))

    def test_truncate_with_grids(self):
        prj = ChartProject(output_folder=testing.output_data_folder())
        prj.add_to_grid_list(testing.input_test_files(".bag")[0])
        self.assertTrue(prj.grid_truncate())


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQC2ChartGridTruncate))
    return s
