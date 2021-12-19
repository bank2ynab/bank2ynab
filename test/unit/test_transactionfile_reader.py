from unittest import TestCase


class TestTransactionFileReader(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()


"""def test_read_data(self):
        Test that the right number of rows are read from the test files
        # if you need more tests, add sections to test.conf & specify them here
        for section_name, num_records, fpath in [
            ("test_record_i18n", 74, "test_raiffeisen_01.csv"),
            ("test_record_headers", 74, "test_headers.csv"),
            ("test_delimiter_tab", 74, "test_delimiter_tab.csv"),
        ]:
            config = fix_conf_params(self.cp, section_name)
            b = B2YBank(config)
            records = b.read_data(join(self.test_data, fpath))
            self.assertEqual(len(records), num_records)"""
