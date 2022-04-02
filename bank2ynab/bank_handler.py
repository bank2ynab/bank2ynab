import logging
import os
import traceback
from os import path
from typing import Any

import dataframe_handler
import transactionfile_reader
from dataframe_handler import DataframeHandler


class BankHandler:
    """
    Handle the flow for data input, parsing, and data output
    for a given bank configuration.
    """

    def __init__(self, config_dict: dict[str, Any]) -> None:
        """
        Initialise object and load bank-specific configuration parameters.

        :param config_dict: dictionary of all banks' configurations with
        the bank names as keys.
        :type config_dict: dict
        """
        self.name = config_dict.get("bank_name", "DEFAULT")
        self.config_dict = config_dict
        self.files_processed = 0
        self.transaction_list: list[dict] = list()

    def run(self) -> None:
        matching_files = transactionfile_reader.get_files(
            name=self.config_dict["bank_name"],
            file_pattern=self.config_dict["input_filename"],
            try_path=self.config_dict["path"],
            regex_active=self.config_dict["regex"],
            ext=self.config_dict["ext"],
            prefix=self.config_dict["fixed_prefix"],
        )

        file_dfs: list = list()

        for src_file in matching_files:
            logging.info(f"\nParsing input file: {src_file} ({self.name})")
            try:
                # perform preprocessing operations on file if required
                src_file = self._preprocess_file(
                    file_path=src_file,
                    plugin_args=self.config_dict["plugin_args"],
                )
                # get file's encoding
                src_encod = transactionfile_reader.detect_encoding(src_file)
                # create our base dataframe

                df_handler = DataframeHandler()
                df_handler.run(
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
                    date_dedupe=self.config_dict["date_dedupe"],
                    fill_memo=self.config_dict["payee_to_memo"],
                    currency_fix=self.config_dict["currency_mult"],
                )

                self.files_processed += 1
            except ValueError as e:
                logging.info(
                    f"No output data from this file for this bank. ({e})"
                )
                logging.debug(traceback.format_exc())
            else:
                # make sure our data is not blank before writing
                if not df_handler.df.empty:
                    # write export file
                    output_path = get_output_path(
                        input_path=src_file,
                        prefix=self.config_dict["fixed_prefix"],
                        ext=self.config_dict["output_ext"],
                    )
                    logging.info(
                        f"Writing output file: {output_path} (debug -"
                        " commented out)"
                    )
                    df_handler.output_csv(output_path)
                    # save api transaction data for each bank to list
                    file_dfs.append(df_handler.api_transaction_df)
                    # delete original csv file
                    if self.config_dict["delete_original"] is True:
                        logging.info(
                            f"Removing input file: {src_file} (debug -"
                            " commented out)"
                        )
                        os.remove(src_file)
                else:
                    logging.info(
                        "No output data from this file for this bank."
                    )
        # don't add empty transaction dataframes
        if file_dfs:
            combined_df = dataframe_handler.combine_dfs(file_dfs)
            self.transaction_list = combined_df.to_dict(orient="records")

    def _preprocess_file(self, file_path: str, plugin_args: list[Any]) -> str:
        """
        exists solely to be used by plugins for pre-processing a file
        that otherwise can be read normally (e.g. weird format)
        :param file_path: path to file
        """
        # intentionally empty - plugins can use this function
        return file_path


def get_output_path(input_path: str, prefix: str, ext: str) -> str:
    """
    Generate the name of the output file.

    :param path: path to output file
    :type path: str
    :return: target filename
    :rtype: str
    """
    target_dir = path.dirname(input_path)
    target_fname = path.basename(input_path)[:-4]

    new_filename = f"{prefix}{target_fname}{ext}"
    new_path = path.join(target_dir, new_filename)
    counter = 1
    while path.isfile(new_path):
        new_filename = f"{prefix}{target_fname}_{counter}{ext}"
        new_path = path.join(target_dir, new_filename)
        counter += 1
    return new_path
