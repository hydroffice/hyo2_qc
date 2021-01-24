import os
import unittest

from hyo2.qc.common.project import BaseProject
from hyo2.qc.common import testing
from hyo2.grids.grids_manager import layer_types


class TestQC2CommonProject(unittest.TestCase):

    def test_init_project_none_folder(self):
        prj = BaseProject(projects_folder=None)
        self.assertTrue(os.path.exists(prj.output_folder))

    def test_init_project_with_folder(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        self.assertTrue(os.path.exists(prj.output_folder))

    def test_default_output_folder(self):
        out = BaseProject.default_output_folder()
        self.assertTrue("Base" in out)

    def test_output_folder(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        with self.assertRaises(RuntimeError):
            prj.output_folder = "C:/invalid/path/to/folder"

    def test_init_project_valid_profile(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        self.assertTrue(prj.active_profile in BaseProject.project_profiles.values())

    def test_init_project_office_profile(self):
        prj = BaseProject(projects_folder=testing.output_data_folder(), profile=BaseProject.project_profiles['office'])
        self.assertEqual(prj.active_profile, BaseProject.project_profiles['office'])

    def test_init_project_field_profile(self):
        prj = BaseProject(projects_folder=testing.output_data_folder(), profile=BaseProject.project_profiles['field'])
        self.assertEqual(prj.active_profile, BaseProject.project_profiles['field'])

    def test_init_project_survey_label(self):
        prj = BaseProject(projects_folder=None)
        self.assertTrue(len(prj.survey_label) == 0)

    def test_make_project_survey_label(self):
        prj = BaseProject(projects_folder=None)
        prj.add_to_s57_list(testing.input_test_files(".000")[-1])
        prj.read_feature_file(testing.input_test_files(".000")[-1])
        self.assertTrue(len(prj.survey_label) != 0)
        self.assertTrue(len(prj.survey_label) == 6)
        self.assertEqual(prj.survey_label, "tiny__")

    def test_make_project_survey_label_from_path(self):
        prj = BaseProject(projects_folder=None)
        survey_label = prj.make_survey_label_from_path("fake/H012345")
        self.assertTrue(len(survey_label) != 0)
        self.assertTrue(len(survey_label) == 6)
        self.assertEqual(survey_label, "H01234")

    def test_clear_project_data(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.survey_label = "test"
        self.assertTrue(len(prj.survey_label) != 0)
        prj.clear_data()
        self.assertEqual(len(prj.s57_list), 0)
        self.assertEqual(len(prj.ss_list), 0)
        self.assertEqual(len(prj.survey_label), 0)

    # s57

    def test_s57_list(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        self.assertEqual(len(prj.s57_list), 0)

    def test_s57_list_add_fake(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        with self.assertRaises(RuntimeError):
            prj.add_to_s57_list("fake/fake.000")

    def test_s57_list_add_real(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.add_to_s57_list(testing.input_test_files(".000")[0])
        self.assertEqual(len(prj.s57_list), 1)
        prj.add_to_s57_list(testing.input_test_files(".000")[0])
        self.assertEqual(len(prj.s57_list), 1)
        prj.remove_from_s57_list(testing.input_test_files(".000")[0])
        self.assertEqual(len(prj.s57_list), 0)

    def test_s57_list_clear(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.add_to_s57_list(testing.input_test_files(".000")[0])
        prj.clear_s57_list()
        self.assertEqual(len(prj.s57_list), 0)

    def test_s57_read(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        self.assertTrue(prj.cur_s57 is None)
        self.assertFalse(prj.has_s57())
        self.assertEqual(len(prj.cur_s57_basename), 0)
        prj.read_feature_file(testing.input_test_files(".000")[0])
        self.assertTrue(prj.cur_s57 is not None)
        self.assertTrue(prj.has_s57())
        self.assertGreater(len(prj.cur_s57_basename), 0)

    # ss

    def test_ss_list(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        self.assertEqual(len(prj.ss_list), 0)

    def test_ss_list_add_fake(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        with self.assertRaises(RuntimeError):
            prj.add_to_ss_list("fake/fake.000")

    def test_ss_list_add_real(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.add_to_ss_list(testing.input_test_files(".000")[0])
        self.assertEqual(len(prj.ss_list), 1)
        prj.add_to_ss_list(testing.input_test_files(".000")[0])
        self.assertEqual(len(prj.ss_list), 1)
        prj.remove_from_ss_list(testing.input_test_files(".000")[0])
        self.assertEqual(len(prj.ss_list), 0)

    def test_ss_list_clear(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.add_to_ss_list(testing.input_test_files(".000")[0])
        prj.clear_ss_list()
        self.assertEqual(len(prj.ss_list), 0)

    def test_ss_read(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        self.assertTrue(prj.cur_ss is None)
        self.assertFalse(prj.has_ss())
        self.assertEqual(len(prj.cur_ss_basename), 0)
        prj.read_ss_file(testing.input_test_files(".000")[0])
        self.assertTrue(prj.cur_ss is not None)
        self.assertTrue(prj.has_ss())
        self.assertGreater(len(prj.cur_ss_basename), 0)

    # grid

    def test_grid_list(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        self.assertEqual(len(prj.grid_list), 0)

    def test_grid_list_add_fake(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        with self.assertRaises(RuntimeError):
            prj.add_to_grid_list("fake/fake.bag")

    def test_grid_list_add_real(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.add_to_grid_list(testing.input_test_files(".bag")[0])
        self.assertEqual(len(prj.grid_list), 1)
        prj.add_to_grid_list(testing.input_test_files(".bag")[0])
        self.assertEqual(len(prj.grid_list), 1)
        prj.remove_from_grid_list(testing.input_test_files(".bag")[0])
        self.assertEqual(len(prj.grid_list), 0)

    def test_grid_list_clear(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.add_to_grid_list(testing.input_test_files(".bag")[0])
        prj.clear_grid_list()
        self.assertEqual(len(prj.grid_list), 0)

    def test_grid_read(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        self.assertTrue(prj.cur_grid is None)
        self.assertFalse(prj.has_grid())
        with self.assertRaises(RuntimeError):
            _ = prj.cur_grid_basename
        prj.add_to_grid_list(testing.input_test_files(".bag")[0])
        prj.set_cur_grid(testing.input_test_files(".bag")[0])
        prj.open_to_read_cur_grid()
        self.assertTrue(prj.cur_grid is not None)
        self.assertTrue(prj.has_grid())
        self.assertGreater(len(prj.cur_grid_basename), 0)

    def test_cur_grid_has_layers(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        with self.assertRaises(RuntimeError):
            prj.cur_grid_has_depth_layer()
        with self.assertRaises(RuntimeError):
            prj.cur_grid_has_product_uncertainty_layer()
        with self.assertRaises(RuntimeError):
            prj.cur_grid_has_density_layer()
        with self.assertRaises(RuntimeError):
            prj.cur_grid_has_tvu_qc_layer()
        with self.assertRaises(RuntimeError):
            prj.cur_grid_tvu_qc_layers()
        with self.assertRaises(RuntimeError):
            prj.set_cur_grid_tvu_qc_name("fake")

        prj.add_to_grid_list(testing.input_test_files(".bag")[0])
        prj.set_cur_grid(testing.input_test_files(".bag")[0])
        prj.open_to_read_cur_grid()
        self.assertTrue(prj.cur_grid_has_depth_layer())
        self.assertTrue(prj.cur_grid_has_product_uncertainty_layer())
        self.assertFalse(prj.cur_grid_has_density_layer())
        self.assertFalse(prj.cur_grid_has_tvu_qc_layer())
        self.assertEqual(len(prj.cur_grid_tvu_qc_layers()), 0)
        self.assertTrue(prj.has_bag_grid())
        self.assertFalse(prj.has_csar_grid())

    def test_select_layers_in_cur_grid(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.add_to_grid_list(testing.input_test_files(".bag")[0])
        prj.set_cur_grid(testing.input_test_files(".bag")[0])
        prj.open_to_read_cur_grid()
        self.assertEqual(len(prj.selected_layers_in_cur_grid), 0)
        prj.selected_layers_in_cur_grid = [layer_types['depth'], ]
        self.assertEqual(len(prj.selected_layers_in_cur_grid), 1)

    def test_cur_grid_shape(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.add_to_grid_list(testing.input_test_files(".bag")[0])
        prj.set_cur_grid(testing.input_test_files(".bag")[0])
        prj.open_to_read_cur_grid()
        self.assertEquals(prj.cur_grid_shape[0], 0)
        self.assertEquals(prj.cur_grid_shape[1], 0)

    # outputs

    def test_outputs(self):
        prj = BaseProject(projects_folder=testing.output_data_folder())
        prj.output_shp = True
        self.assertTrue(prj.output_shp)
        prj.output_kml = True
        self.assertTrue(prj.output_kml)
        prj.output_svp = True
        self.assertTrue(prj.output_svp)

    # other stuff

    def test_raise_window(self):
        BaseProject.raise_window()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQC2CommonProject))
    return s
