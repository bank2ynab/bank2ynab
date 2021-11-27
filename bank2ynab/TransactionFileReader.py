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

    def __init__(
            self, *, ext: str,
            file_pattern: str,
            prefix: str,
            regex_active: bool,
            encoding: str,
            try_path: str, delim: str,
            header_rows: int,
            footer_rows: int,) -> None:
        """
        generate bank specific file reader using supplied configuration flags

        :param ext: source file extension (e.g. ".csv")
        :type ext: str
        :param file_pattern: start of filename to match OR regex pattern
        :type file_pattern: str
        :param prefix: post processing prefix to avoid if in filename
        :type prefix: str
        :param regex_active: boolean to indicate whether or not to use regex
        :type regex_active: bool
        :param encoding: file encoding type to use when opening file
        :type: str
        :param try_path: path to search for file
        :type try_path: str
        :param delim: delimiter used to separate values (e.g. ",")
        :type delim: str
        :param header_rows: number of header rows to skip
        :type header_rows: int
        :param footer_rows: number of footer rows to skip
        :type footer_rows: int
        """

        self.ext = ext
        self.file_pattern = file_pattern
        self.prefix = prefix
        self.regex_active = regex_active
        self.encoding = encoding
        self.try_path = try_path
        self.delim = delim
        self.header_rows = header_rows
        self.footer_rows = footer_rows

    def get_files(self) -> list:
        """
        gets list of matching transaction files

        :return: list of files to process
        :rtype: list
        """

        files = list()
        missing_dir = False
        path = ""
        if self.file_pattern != "":
            try:
                path = b2y_utilities.find_directory(self.try_path)
            except FileNotFoundError:
                missing_dir = True
                path = b2y_utilities.find_directory("")
            path = abspath(path)
            try:
                directory_list = listdir(path)
            except FileNotFoundError:
                directory_list = listdir(".")
            if self.regex_active is True:
                files = [
                    join(path, f)
                    for f in directory_list
                    if f.endswith(self.ext)
                    if re.match(self.file_pattern + r".*\.", f)
                    if self.prefix not in f
                ]
            else:
                files = [
                    join(path, f)
                    for f in directory_list
                    if f.endswith(self.ext)
                    if f.startswith(self.file_pattern)
                    if self.prefix not in f
                ]
            if not files and missing_dir:
                logging.error(
                    f"\nFormat: {self.name}\n\nError: Can't find download path: {self.try_path}\nTrying default path instead:\t {path}"
                )
        return files

    def _preprocess_file(self, file_path: str):
        """
        exists solely to be used by plugins for pre-processing a file
        that otherwise can be read normally (e.g. weird format)
        :param file_path: path to file
        """
        # intentionally empty - plugins can use this function
        return

    def read_transactions(self, file_path: str) -> DataFrame:
        """extract data from given transaction file
        :param file_path: path to file
        :return: list of cleaned data rows
        """

        # give plugins a chance to pre-process the file
        # TODO find a better place to do this
        self._preprocess_file(file_path)

        # detect file encoding # TODO allow for provided encoding
        self.encoding = b2y_utilities.detect_encoding(file_path)
        # create a transaction dataframe
        return pd.read_csv(
            filepath_or_buffer=file_path,
            delimiter=self.delim,
            skipinitialspace=True,  # skip space after delimiter
            header=None,  # don't set column headers initially
            skiprows=self.header_rows,  # skip header rows
            skipfooter=self.footer_rows,  # skip footer rows
            skip_blank_lines=True,  # skip blank lines
            encoding=self.encoding,
            memory_map=True,  # access file object directly - no I/O overhead
            engine="python",
        )
