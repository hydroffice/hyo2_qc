import unittest
import os
import sys
from hyo2.qc.common import default_logging
import logging

default_logging.load()
logger = logging.getLogger()

from hyo2.qc.common.progress.cli_progress import CliProgress


class TestQC2CommonProgressCliProgress(unittest.TestCase):

    def setUp(self):
        self.progress = CliProgress()
        sys.stdout = None

    def tearDown(self):
        pass

    def test_start_minimal(self):
        try:
            self.progress.start()
        except Exception as e:
            self.fail(e)

    def test_start_custom_title_text(self):
        try:
            self.progress.start(title='Test Bar', text='Doing stuff')
        except Exception as e:
            self.fail(e)

    def test_start_custom_min_max(self):
        try:
            self.progress.start(min_value=100, max_value=300, init_value=100)
        except Exception as e:
            self.fail(e)

    def test_start_minimal_update(self):
        try:
            self.progress.start()
            self.progress.update(50)
        except Exception as e:
            self.fail(e)

    def test_start_minimal_update_raising(self):
        with self.assertRaises(Exception) as context:
            self.progress.start()
            self.progress.update(1000)

    def test_start_minimal_add(self):
        try:
            self.progress.start()
            self.progress.add(50)
        except Exception as e:
            self.fail(e)

    def test_start_minimal_add_raising(self):
        with self.assertRaises(Exception) as context:
            self.progress.start()
            self.progress.add(1000)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQC2CommonProgressCliProgress))
    return s
