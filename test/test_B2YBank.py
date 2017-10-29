from copy import copy
from unittest import TestCase

from os.path import join, abspath, exists

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

        # if you need more tests, add sections to test.conf and then specify them here
        for section_name, num_files in [
                ("test_num_files", 2),
                ("test_num_files_noexist", 0),
                ("test_num_files_extension", 0),
                ]:

            config = fix_conf_params(self.cp, section_name)
            b = B2YBank(config, self.py2)
            files = b.get_files()
            self.assertEqual(len(files), num_files)
            # hack config to make sure we can deal with absolute paths too
            b.config["path"] = abspath("test-data")
            files = b.get_files()
            self.assertEqual(len(files), num_files)

    def test_read_data(self):
        # if you need more tests, add sections to test.conf and then specify them here
        for section_name, num_records, fpath in [
                ("test_record_i18n", 74, "test_raiffeisen_01.csv"),
                ("test_record_headers", 74, "test_headers.csv")
                ]:
            config = fix_conf_params(self.cp, section_name)
            b = B2YBank(config, self.py2)
            records = b.read_data(join("test-data", fpath))
            self.assertEqual(len(records), num_records)

    def test_write_data(self):
        # if you need more tests, add sections to test.conf and then specify them here
        # todo: incorporate multiple-file scenarios
        for section_name, num_records, fpath in [
            ("test_record_i18n", 74, "fixed_test_raiffeisen_01.csv"),
            ("test_record_headers", 74, "fixed_test_headers.csv")
        ]:
            config = fix_conf_params(self.cp, section_name)
            b = B2YBank(config, self.py2)
            for f in b.get_files():
                output_data = b.read_data(f)
                self.assertEqual(len(output_data), num_records)
                result_file = b.write_data(f, output_data)
                # check the file is where we expect it to be
                expected_file = abspath(join('test-data', fpath))
                self.assertTrue(exists(expected_file))
                self.assertEqual(expected_file, result_file)
                # todo: check actual contents are what we expect
                os.unlink(expected_file)

