import logging
import re
from os import listdir
from os.path import abspath, join

import pandas as pd
from pandas.core.frame import DataFrame

import b2y_utilities


class TransactionFileReader:
    """
    find all relevant files for a specified config and provide a dataframe to work with
    """

    def __init__(self, config_object) -> None:
        """
        load bank-specific configuration parameters

        :param config_object: bank's configuration
        :type config_object: Configparser config object #TODO correctly typehint this
        """
        self.config = config_object

    def get_files(self) -> list:
        """
        gets list of matching transaction files

        :return: list of files to process
        :rtype: list
        """
        ext = self.config["ext"]
        file_pattern = self.config["input_filename"]
        prefix = self.config["fixed_prefix"]
        regex_active = self.config["regex"]
        files = list()
        missing_dir = False
        try_path = self.config["path"]
        path = ""
        if file_pattern != "":
            try:
                path = b2y_utilities.find_directory(try_path)
            except FileNotFoundError:
                missing_dir = True
                path = b2y_utilities.find_directory("")
            path = abspath(path)
            try:
                directory_list = listdir(path)
            except FileNotFoundError:
                directory_list = listdir(".")
            if regex_active is True:
                files = [
                    join(path, f)
                    for f in directory_list
                    if f.endswith(ext)
                    if re.match(file_pattern + r".*\.", f)
                    if prefix not in f
                ]
            else:
                files = [
                    join(path, f)
                    for f in directory_list
                    if f.endswith(ext)
                    if f.startswith(file_pattern)
                    if prefix not in f
                ]
            if not files and missing_dir:
                logging.error(
                    f"\nFormat: {self.name}\n\nError: Can't find download path: {try_path}\nTrying default path instead:\t {path}"
                )
        return files

    def _preprocess_file(self, file_path: str):
        """
        exists solely to be used by plugins for pre-processing a file
        that otherwise can be read normally (e.g. weird format)
        :param file_path: path to file
        """
        # intentionally empty - the plugins can use this function
        return

    # TODO separate out preprocess step
    def read_transactions(self, file_path: str) -> DataFrame:
        """extract data from given transaction file
        :param file_path: path to file
        :return: list of cleaned data rows
        """
        delim = self.config["input_delimiter"]
        header_rows = int(self.config["header_rows"])
        footer_rows = int(self.config["footer_rows"])

        # give plugins a chance to pre-process the file
        self._preprocess_file(file_path)

        # detect file encoding
        encod = b2y_utilities.detect_encoding(file_path)
        # create a transaction dataframe
        return pd.read_csv(
            filepath_or_buffer=file_path,
            delimiter=delim,
            skipinitialspace=True,  # skip space after delimiter
            header=None,  # don't set column headers initially
            skiprows=header_rows,  # skip header rows
            skipfooter=footer_rows,  # skip footer rows
            skip_blank_lines=True,  # skip blank lines
            encoding=encod,
            memory_map=True,  # access file object directly - no I/O overhead
            engine="python",
        )
