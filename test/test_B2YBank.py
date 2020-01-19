from copy import copy
from unittest import TestCase

from os.path import join, abspath, exists

import os

from bank2ynab import B2YBank, fix_conf_params, build_bank
from plugins.null import NullBank
from test.utils import get_test_confparser


class TestB2YBank(TestCase):

    TESTCONFPATH = join("test-data", "test.conf")

    def setUp(self):
        self.cp = get_test_confparser()
        self.defaults = dict(self.cp.defaults())
        self.b = None

    def tearDown(self):
        pass

    def test_init_and_name(self):
        """ Check parameters are correctly stored in the object."""
        self.b = B2YBank(self.defaults)
        cfe = copy(self.defaults)
        self.assertEqual(self.b.config, cfe)
        self.assertEqual("DEFAULT", self.b.name)

    def test_get_files(self):
        """ Test it's finding the right amount of files"""
        # if you need more tests, add sections to test.conf & specify them here
        for section_name, num_files in [
            ("test_num_files", 2),
            ("test_num_files_noexist", 0),
            ("test_num_files_extension", 0),
            ("test_regex", 1),
            ("test_regex_noexist", 0),
        ]:

            config = fix_conf_params(self.cp, section_name)
            b = B2YBank(config)
            files = b.get_files()
            self.assertEqual(len(files), num_files)
            # hack config to make sure we can deal with absolute paths too
            b.config["path"] = abspath("test-data")
            files = b.get_files()
            self.assertEqual(len(files), num_files)

    def test_read_data(self):
        """ Test that the right number of rows are read from the test files """
        # if you need more tests, add sections to test.conf & specify them here
        for section_name, num_records, fpath in [
            ("test_record_i18n", 74, "test_raiffeisen_01.csv"),
            ("test_record_headers", 74, "test_headers.csv"),
            ("test_delimiter_tab", 74, "test_delimiter_tab.csv"),
        ]:
            config = fix_conf_params(self.cp, section_name)
            b = B2YBank(config)
            records = b.read_data(join("test-data", fpath))
            self.assertEqual(len(records), num_records)

    def test_write_data(self):
        """
        Test that the right amount of files are created
        and that the file paths end up where we expect
        # to do - make sure file contents are what we expect
        """
        # if you need more tests, add sections to test.conf & specify them here
        # todo: incorporate multiple-file scenarios
        # todo: allow incremental file suffixes when files named the same
        for section_name, num_records, fpath in [
            ("test_record_i18n", 74, "fixed_test_raiffeisen_01.csv"),
            ("test_record_headers", 74, "fixed_test_headers.csv"),
        ]:
            config = fix_conf_params(self.cp, section_name)
            b = B2YBank(config)
            for f in b.get_files():
                output_data = b.read_data(f)
                self.assertEqual(len(output_data), num_records)
                result_file = b.write_data(f, output_data)
                # check the file is where we expect it to be
                expected_file = abspath(join("test-data", fpath))
                self.assertTrue(exists(expected_file))
                self.assertEqual(expected_file, result_file)
                # todo: check actual contents are what we expect
                os.unlink(expected_file)

    def test_build_bank(self):
        b2yb = build_bank(self.defaults)
        self.assertIsInstance(b2yb, B2YBank)
        nullconfig = fix_conf_params(self.cp, "test_plugin")
        nullb = build_bank(nullconfig)
        self.assertIsInstance(nullb, NullBank)
        missingconf = fix_conf_params(self.cp, "test_plugin_missing")
        self.assertRaises(ImportError, build_bank, missingconf)

    def test_fix_row(self):
        """ Check output row is the same across different formats """
        # todo: something where the row format is invalid
        # if you need more tests, add sections to test.conf & specify them here
        for section_name in [
            "test_row_format_default",
            "test_row_format_neg_inflow",
            "test_row_format_CD_flag",
            "test_row_format_invalid",
        ]:
            config = fix_conf_params(self.cp, section_name)
            b = B2YBank(config)
            for f in b.get_files():
                output_data = b.read_data(f)
                # test the same two rows in each scenario
                for row, expected_row in [
                    (
                        23,
                        [
                            "2017-09-28",
                            "HOFER DANKT  0527  K2   28.09. 17:17",
                            "",
                            "HOFER DANKT  0527  K2   28.09. 17:17",
                            "44.96",
                            "",
                        ],
                    ),
                    (
                        24,
                        [
                            "2017-09-28",
                            "SOFTWARE Wien",
                            "",
                            "SOFTWARE Wien",
                            "",
                            "307.67",
                        ],
                    ),
                ]:
                    result_row = output_data[row]

                    self.assertCountEqual(expected_row, result_row)

    def test_valid_row(self):
        """ Test making sure row has an outflow or an inflow """
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)

        for row, row_validity in [
            (["Pending", "Payee", "", "", "300", ""], False),
            (["28.09.2017", "Payee", "", "", "", "400"], False),
            (["28.09.2017", "Payee", "", "", "", ""], False),
            (["2017-09-28", "Payee", "", "", "300", ""], True),
            (["2017-09-28", "Payee", "", "", "", "400"], True),
            (["2017-09-28", "Payee", "", "", "", ""], False),
        ]:
            is_valid = b._valid_row(row)
            self.assertEqual(is_valid, row_validity)

    def test_clean_monetary_values(self):
        """ Test cleaning of outflow and inflow of unneeded characters """
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)

        for row, expected_row in [
            (
                ["28.09.2017", "Payee", "", "", "+ £300.01", ""],
                ["28.09.2017", "Payee", "", "", "300.01", ""],
            ),
            (
                ["28.09.2017", "Payee", "", "", "", "- $300"],
                ["28.09.2017", "Payee", "", "", "", "300"],
            ),
        ]:
            result_row = b._clean_monetary_values(row)
            self.assertCountEqual(expected_row, result_row)

    def test_auto_memo(self):
        """ Test auto-filling empty memo field with payee data """
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)
        memo_index = b.config["output_columns"].index("Memo")

        for row, test_memo, fill_memo in [
            (["28.09.2017", "Payee", "", "", "300", ""], "", False),
            (["28.09.2017", "Payee", "", "Memo", "300", ""], "Memo", False),
            (["28.09.2017", "Payee", "", "", "300", ""], "Payee", True),
            (["28.09.2017", "Payee", "", "Memo", "", "400"], "Memo", True),
        ]:
            new_memo = b._auto_memo(row, fill_memo)[memo_index]
            self.assertEqual(test_memo, new_memo)

    def test_fix_outflow(self):
        """ Test conversion of negative Inflow into Outflow """
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)

        for row, expected_row in [
            (
                ["28.09.2017", "Payee", "", "", "300", ""],
                ["28.09.2017", "Payee", "", "", "300", ""],
            ),
            (
                ["28.09.2017", "Payee", "", "", "", "-300"],
                ["28.09.2017", "Payee", "", "", "300", ""],
            ),
            (
                ["28.09.2017", "Payee", "", "", "", "300"],
                ["28.09.2017", "Payee", "", "", "", "300"],
            ),
        ]:
            result_row = b._fix_outflow(row)
            self.assertCountEqual(expected_row, result_row)

    def test_fix_inflow(self):
        """ Test conversion of positive Outflow into Inflow """
        config = fix_conf_params(self.cp, "test_row_format_default")
        b = B2YBank(config)

        for row, expected_row in [
            (
                ["28.09.2017", "Payee", "", "", "300", ""],
                ["28.09.2017", "Payee", "", "", "300", ""],
            ),
            (
                ["28.09.2017", "Payee", "", "", "+300", ""],
                ["28.09.2017", "Payee", "", "", "", "300"],
            ),
            (
                ["28.09.2017", "Payee", "", "", "", "300"],
                ["28.09.2017", "Payee", "", "", "", "300"],
            ),
        ]:
            result_row = b._fix_inflow(row)
            self.assertCountEqual(expected_row, result_row)

    """
    def test_fix_date(self):
        # todo

    def test_cd_flag_process():
        # todo

    def test_preprocess_file(self):
        # todo
    """
