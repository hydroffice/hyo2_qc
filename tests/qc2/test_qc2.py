import os
import unittest

from hyo2.qc import __author__, __version__


class TestQC2(unittest.TestCase):

    def test_author(self):
        self.assertGreaterEqual(len(__author__.split(";")), 2)

    def test_version(self):
        self.assertGreaterEqual(int(__version__.split(".")[0]), 2)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQC2))
    return s
