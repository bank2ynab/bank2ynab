import logging
from os.path import basename, dirname, isfile, join

import pandas as pd
from pandas.core.frame import DataFrame

from DataframeCleaner import DataframeCleaner
from TransactionFileReader import TransactionFileReader


class BankHandler:
    """
    handle the flow for data input, parsing, and data output for a given bank configuration
    """

    def __init__(self, config_object) -> None:
        """
        load bank-specific configuration parameters

        :param config_object: bank's configuration
        :type config_object: Configparser config object #TODO correctly typehint this
        """
        self.name = config_object.get("bank_name", "DEFAULT")
        self.config = config_object

    def run(self) -> None:
        bank_transactions = TransactionFileReader(
            ext=self.config["ext"],
            file_pattern=self.config["input_filename"],
            prefix=self.config["fixed_prefix"],
            encoding=self.config["encoding"],
            regex_active=self.config["regex"],
            try_path=self.config["path"],
            delim=self.config["input_delimiter"],
            header_rows=int(self.config["header_rows"]),
            footer_rows=int(self.config["footer_rows"]),
        )
        transaction_files = bank_transactions.get_files()
        # initialise variables
        bank_files_processed = 0
        output_df = (
            []
        )  # TODO temporary empty list until we work out df appending

        for src_file in transaction_files:
            logging.info(f"\nParsing input file: {src_file} ({self.name})")
            try:
                raw_df = bank_transactions.read_transactions(src_file)
                cleaned_df = DataframeCleaner(
                    df=raw_df,
                    input_columns=self.config["input_columns"],
                    output_columns=self.config["output_columns"],
                    cd_flags=self.config["cd_flags"],
                    date_format=self.config["date_format"],
                    fill_memo=self.config["payee_to_memo"],).parse_data()

                bank_files_processed += 1
            except ValueError as e:
                logging.info(
                    f"No output data from this file for this bank. ({e})"
                )
            else:
                if 1 != 2:  # TODO need df alternative to check if df empty
                    self.write_data(src_file, cleaned_df)

                    # save transaction data for each bank to object
                    self.transaction_data = (
                        output_df  # TODO actually append the data
                    )
                    # delete original csv file
                    if self.config["delete_original"] is True:
                        logging.info(f"Removing input file: {src_file}")
                        # os.remove(src_filefile) DEBUG - disabled deletion while testing
                else:
                    logging.info(
                        "No output data from this file for this bank.")
        return bank_files_processed, output_df

    def write_data(self, filename: str, df: DataFrame) -> str:
        """
        write out the new CSV file

        :param filename: path to output file
        :type filename: str
        :param df: cleaned data ready to output
        :type df: DataFrame
        :return: target filename
        :rtype: str
        """
        target_dir = dirname(filename)
        target_fname = basename(filename)[:-4]
        fixed_prefix = self.config["fixed_prefix"]
        new_filename = f"{fixed_prefix}{target_fname}.csv"
        while isfile(new_filename):
            counter = 1
            new_filename = f"{fixed_prefix}{target_fname}_{counter}.csv"
            counter += 1
        target_filename = join(target_dir, new_filename)
        logging.info(f"Writing output file: {target_filename}")
        # write dataframe to csv
        # df.to_csv(target_filename, index=False) # TODO DEBUG file output disabled
        return target_filename
