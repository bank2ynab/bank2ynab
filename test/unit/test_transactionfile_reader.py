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
'''def test_get_files(self):
        """Test it's finding the right amount of files"""
        # if you need more tests, add sections to test.conf & specify them here
        for section_name, num_files in [
            ("test_num_files", 2),
            ("test_num_files_noexist", 0),
            ("test_num_files_extension", 0),
            ("test_regex", 1),
            ("test_regex_noexist", 0),
        ]:

            config = fix_conf_params(self.cp, section_name)
            config["path"] = join(get_project_dir(), config["path"])
            b = B2YBank(config)
            files = b.get_files()
            self.assertEqual(len(files), num_files)
            # hack config to make sure we can deal with absolute paths too
            b.config["path"] = abspath(self.test_data)
            files = b.get_files()
            self.assertEqual(len(files), num_files)'''
