from copy import copy
from unittest import TestCase

from os.path import join

import os

from bank2ynab import B2YBank, fix_conf_params

_PY2 = False
try:
    import configparser
except ImportError:
    _PY2 = True
    import ConfigParser as configparser
    import cStringIO

class TestB2YBank(TestCase):

    TESTCONFPATH = join("test-data", "test.conf")

    def setUp(self):
        global _PY2
        self.py2 = _PY2
        self.cp = configparser.ConfigParser()
        self.cp.read([TestB2YBank.TESTCONFPATH])
        self.defaults = dict(self.cp.defaults())
        self.b = None

    def tearDown(self):
        pass

    def test_init_and_name(self):
        """ Check parameters are correctly stored in the object."""
        self.b = B2YBank(self.defaults, self.py2)
        cfe = copy(self.defaults)
        self.assertEqual(self.b.config, cfe)
        self.assertEqual("DEFAULT", self.b.name)

    def test_get_files(self):
        """ Test it's finding the right amount of files"""
        for section_name, num_files in [
                ("test_num_files", 2),
                ("test_num_files_noexist", 0),
                ("test_num_files_extension", 0),
                ]:

            config = fix_conf_params(self.cp, section_name)
            self.b = B2YBank(config, self.py2)
            files = self.b.get_files()
            self.assertEqual(len(files), num_files)
            # todo: this having to remember where we are at all times is not good
            os.chdir("..")

    def test_read_data(self):
        for section_name, num_records, fpath in [
                ("test_record_i18n", 74, "test_raiffeisen_01.csv"),
                ("test_record_headers", 74, "test_headers.csv")
                ]:
            config = fix_conf_params(self.cp, section_name)
            self.b = B2YBank(config, self.py2)
            records = self.b.read_data(join("test-data", fpath))
            self.assertEqual(len(records), num_records)

    #
    # def test_write_data(self):
    #     self.fail()
