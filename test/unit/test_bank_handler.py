import sys
from unittest import TestCase

# from bank2ynab.bank_handler import BankHandler


class TestBankHandler(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_test(self):
        print(f"\n\nSys: {sys.path}\n")
        # test_bank_handler = BankHandler(dict())
        # test_bank_handler.run()
        self.assertEqual(1, 1)

    '''def test_init_and_name(self):
        """Check parameters are correctly stored in the object."""
        self.b = B2YBank(self.defaults)
        cfe = copy(self.defaults)
        self.assertEqual(self.b.config, cfe)
        self.assertEqual("DEFAULT", self.b.name)'''

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
    """
    def run(self) -> list:
        transaction_reader = TransactionFileReader(
            name=self.config_dict["bank_name"],
            file_pattern=self.config_dict["input_filename"],
            try_path=self.config_dict["path"],
            regex_active=self.config_dict["regex"],
            ext=self.config_dict["ext"],
            prefix=self.config_dict["fixed_prefix"],
        )
        # initialise variables
        bank_files_processed = 0
        output_data = list()
        for src_file in transaction_reader.files:
            logging.info(f"\nParsing input file: {src_file} ({self.name})")
            try:
                # perform preprocessing operations on file if required
                self._preprocess_file(src_file)
                # get file's encoding
                src_encod = transaction_reader.detect_encoding(src_file)
                # create our base dataframe

                df_handler = DataframeHandler(
                    file_path=src_file,
                    delim=self.config_dict["input_delimiter"],
                    header_rows=int(self.config_dict["header_rows"]),
                    footer_rows=int(self.config_dict["footer_rows"]),
                    encod=src_encod,
                    input_columns=self.config_dict["input_columns"],
                    output_columns=self.config_dict["output_columns"],
                    cd_flags=self.config_dict["cd_flags"],
                    date_format=self.config_dict["date_format"],
                    fill_memo=self.config_dict["payee_to_memo"],
                )
                df_handler.parse_data()

                bank_files_processed += 1
            except ValueError as e:
                logging.info(
                    f"No output data from this file for this bank. ({e})"
                )
            else:
                # make sure our data is not blank before writing
                if not df_handler.df.empty:
                    # write export file
                    self.write_data(src_file, df_handler)
                    # save transaction data for each bank to object
                    output_data.append(df_handler)
                    # delete original csv file
                    if self.config_dict["delete_original"] is True:
                        logging.info(
                            f"Removing input file: {src_file}
                            #NOTE DELETING IS ACTUALLY DISABLED")
                        # os.remove(src_filefile)
                        # # TODO DEBUG - disabled deletion while testing
                else:
                    logging.info(
                        "No output data from this file for this bank."
                    )
        return [bank_files_processed, output_data]

        """
    """
    def write_data(self, path: str, df_handler: DataframeHandler) -> str:

        write out the new CSV file

        :param path: path to output file
        :type path: str
        :param df: cleaned data ready to output
        :type df: DataFrame
        :return: target filename
        :rtype: str

        target_dir = dirname(path)
        target_fname = basename(path)[:-4]
        fixed_prefix = self.config_dict["fixed_prefix"]
        new_filename = f"{fixed_prefix}{target_fname}.csv"
        while isfile(new_filename):
            counter = 1
            new_filename = f"{fixed_prefix}{target_fname}_{counter}.csv"
            counter += 1
        target_filename = join(target_dir, new_filename)
        logging.info(f"Writing output file: {target_filename}")
        # write dataframe to csv
        df_handler.output_csv(target_filename)
        return target_filename
    """
    """def test_write_data(self):

        Test that the right amount of files are created
        and that the file paths end up where we expect
        # to do - make sure file contents are what we expect

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
                expected_file = abspath(join(self.test_data, fpath))
                self.assertTrue(exists(expected_file))
                self.assertEqual(expected_file, result_file)
                # todo: check actual contents are what we expect
                os.unlink(expected_file)"""


"""
    def test_preprocess_file(self):
        raise NotImplementedError
"""
