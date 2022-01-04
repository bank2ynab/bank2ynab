import unittest
from unittest import TestCase

# from bank2ynab.bank_handler import BankHandler


class TestBankHandler(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @unittest.skip("Not tested yet.")
    def test_preprocess_file(self):
        """Test that preprocess file returns the unchanged filepath."""
        path = "test"
        # test_bank_handler = BankHandler({})
        # test_path = test_bank_handler._preprocess_file(path, [])
        self.assertEqual(path, "test_path")

    @unittest.skip("Not tested yet.")
    def test_get_output_path(self):
        raise NotImplementedError

    '''def test_init_and_name(self):
        """Check parameters are correctly stored in the object."""
        self.b = BankHandler(self.defaults)
        cfe = copy(self.defaults)
        self.assertEqual(self.b.config, cfe)
        self.assertEqual("DEFAULT", self.b.name)'''

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

    def test_write_data(self):

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
            b = BankHandler(config)
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
