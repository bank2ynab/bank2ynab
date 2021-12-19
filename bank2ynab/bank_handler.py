import logging
from os.path import basename, dirname, isfile, join

from dataframe_handler import DataframeHandler
from transactionfile_reader import TransactionFileReader


class BankHandler:
    """
    handle the flow for data input, parsing, and data output
    for a given bank configuration
    """

    def __init__(self, config_dict: dict) -> None:
        # TODO revise this docstring
        """
        load bank-specific configuration parameters

        :param config_dict: bank's configuration
        :type config_dict: dict
        """
        self.name = config_dict.get("bank_name", "DEFAULT")
        self.config_dict = config_dict
        self.bank_files_processed = 0
        self.transaction_data = list()

    def run(self) -> None:
        transaction_reader = TransactionFileReader(
            name=self.config_dict["bank_name"],
            file_pattern=self.config_dict["input_filename"],
            try_path=self.config_dict["path"],
            regex_active=self.config_dict["regex"],
            ext=self.config_dict["ext"],
            prefix=self.config_dict["fixed_prefix"],
        )
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
                    api_columns=self.config_dict["api_columns"],
                    cd_flags=self.config_dict["cd_flags"],
                    date_format=self.config_dict["date_format"],
                    fill_memo=self.config_dict["payee_to_memo"],
                    currency_fix=self.config_dict["currency_mult"],
                )
                df_handler.parse_data()

                self.bank_files_processed += 1
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
                    self.transaction_data.append(df_handler)
                    # delete original csv file
                    if self.config_dict["delete_original"] is True:
                        logging.info(
                            f"Removing input file: {src_file} (commented out)"
                        )
                        # TODO DEBUG - disabled deletion while testing
                        # os.remove(src_filefile)
                else:
                    logging.info(
                        "No output data from this file for this bank."
                    )

    def write_data(self, path: str, df_handler: DataframeHandler) -> str:
        """
        write out the new CSV file

        :param path: path to output file
        :type path: str
        :param df: cleaned data ready to output
        :type df: DataFrame
        :return: target filename
        :rtype: str
        """
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

    def _preprocess_file(self, file_path: str):
        """
        exists solely to be used by plugins for pre-processing a file
        that otherwise can be read normally (e.g. weird format)
        :param file_path: path to file
        """
        # intentionally empty - plugins can use this function
        return
