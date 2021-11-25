#!/usr/bin/env python3
#
# bank2ynab.py
#
# Searches specified folder or default download folder for exported
# bank transaction file (.csv format) & adjusts format for YNAB import
# Please see here for details: https://github.com/torbengb/bank2ynab
#
# MIT License: https://github.com/torbengb/bank2ynab/blob/master/LICENSE
#
# DISCLAIMER: Please use at your own risk. This tool is neither officially
# supported by YNAB (the company) nor by YNAB (the software) in any way.
# Use of this tool could introduce problems into your budget that YNAB,
# through its official support channels, will not be able to troubleshoot
# or fix. See also the full MIT licence.
#
#
# don't edit below here unless you know what you're doing!
from os.path import abspath, join, dirname, basename
import os
import importlib
import re
from datetime import datetime
import logging
import pandas as pd
from pandas.core.frame import DataFrame

import b2y_utilities

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


# Classes doing the actual work
class B2YBank:
    """Object parsing and outputting data for a specific bank.
    This can be subclassed to handle formats requiring special handling,
    overriding any of get_files(), read_data() or write_data()."""

    def __init__(self, config_object) -> None:
        """
        load bank-specific configuration parameters

        :param config_object: bank's configuration 
        :type config_object: [type]
        """
        self.name = config_object.get("bank_name", "DEFAULT")
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
                directory_list = os.listdir(path)
            except FileNotFoundError:
                directory_list = os.listdir(".")
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
                s = (
                    "\nFormat: {}\n\nError: Can't find download path: {}"
                    "\nTrying default path instead:\t {}"
                )
                logging.error(s.format(self.name, try_path, path))
        return files

    def read_data(self, file_path):
        """extract data from given transaction file
        :param file_path: path to file
        :return: list of cleaned data rows
        """
        delim = self.config["input_delimiter"]
        input_columns = self.config["input_columns"]
        output_columns = self.config["output_columns"]
        header_rows = int(self.config["header_rows"])
        footer_rows = int(self.config["footer_rows"])
        cd_flags = self.config["cd_flags"]
        date_format = self.config["date_format"]
        fill_memo = self.config["payee_to_memo"]

        # give plugins a chance to pre-process the file
        self._preprocess_file(file_path)

        # detect file encoding
        encod = b2y_utilities.detect_encoding(file_path)
        # create a transaction dataframe
        df = pd.read_csv(
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

        # convert each transaction to match ideal output data

        # set column names based on input column list
        df.columns = input_columns

        # debug to see what our df is like before transformation
        logging.debug("\nInitial DF\n{}".format(df.head()))

        # merge duplicate input columns
        df = self._merge_duplicate_columns(df, input_columns)
        # add missing columns
        df = self._add_missing_columns(df, input_columns, output_columns)
        # fix date format
        df["Date"] = self._fix_date(df["Date"], date_format)
        # process Inflow/Outflow flags
        df = self._cd_flag_process(cd_flags, df)
        # fix amounts (convert negative inflows and outflows etc)
        df = self._fix_amount(df)
        # auto fill memo if required
        df = self._auto_memo(df, fill_memo)
        # remove invalid rows
        df = self._remove_invalid_rows(df)
        # set final columns & order
        df = df[output_columns]
        # display parsed line count
        logging.info("Parsed {} lines".format(df.shape[0]))

        logging.info(
            "\nFinal DF\n{}".format(df.head(10))
        )  # view final dataframe # TODO - switch to debug once finished here

        return df

    def _preprocess_file(self, file_path):
        """
        exists solely to be used by plugins for pre-processing a file
        that otherwise can be read normally (e.g. weird format)
        :param file_path: path to file
        """
        # intentionally empty - the plugins can use this function
        return

    def _merge_duplicate_columns(
        self, df: DataFrame, input_columns: list
    ) -> DataFrame:
        """
        Merges columns specified more than once in the input_columns list.
        Note: converts values into strings before merging.

        :param df: the dataframe to work on
        :type df: DataFrame
        :param input_columns: the list of columns in the input file
        :type input_columns: list
        :return: modified dataframe
        :rtype: DataFrame
        """

        # create dictionary mapping column names to indices of duplicates
        cols_to_merge = dict()
        for index, col in enumerate(input_columns):
            if col not in cols_to_merge:
                cols_to_merge[col] = []
            cols_to_merge[col] += [index]

        # go through each key
        for key in cols_to_merge:
            key_cols = cols_to_merge[key]
            if len(key_cols) > 1:
                # change first column to string
                df.iloc[:, key_cols[0]] = "{} ".format(df.iloc[:, key_cols[0]])
                # merge every duplicate column into the 1st instance of the column name
                for dupe_count, key_col in enumerate(key_cols[1:]):
                    # add string version of each column onto the first column
                    df.iloc[:, key_cols[0]] += "{} ".format(
                        df.iloc[:, key_col]
                    )
                    # rename duplicate column
                    df.columns.values[key_col] = "{} {}".format(
                        key, dupe_count
                    )
                # remove excess spaces
                df[key] = (
                    df[key].str.replace("\s{2,}", " ", regex=True).str.strip()
                )

        logging.debug("\nAfter duplicate merge\n{}".format(df.head()))
        return df

    def _add_missing_columns(
        self, df: DataFrame, input_cols: list, output_cols: list
    ) -> DataFrame:
        """
        Adds any missing required columns to the Dataframe.

        :param df: the dataframe to work on
        :type df: DataFrame
        :param input_columns: the list of columns in the input file
        :type input_columns: list
        :param output_columns: the desired list of columns as output
        :type output_columns: list
        :return: modified dataframe
        :rtype: DataFrame
        """
        # compare input & output column lists to find missing columns
        missing_cols = list(set(output_cols).difference(input_cols))
        # add missing output columns
        for col in missing_cols:
            df.insert(loc=0, column=col, value="")
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def _cd_flag_process(self, cd_flags: list, df: DataFrame) -> DataFrame:
        """
        fix columns where inflow/outflow is indicated by a flag in a separate column
        the cd_flag list is in the form "indicator column, outflow flag, inflow flag"
        (the code does not use the indicator flag specified in the flag list, but instead the "CDFlag" column specified in Input Columns)

        :param cd_flags: list of parameters for applying indicators
        :type cd_flags: list
        :param df: dataframe to be modified
        :type df: DataFrame
        :return: modified dataframe
        :rtype: DataFrame
        """
        if len(cd_flags) == 3:
            outflow_flag = cd_flags[2]
            # if this row is indicated to be outflow, make inflow negative
            df.loc[df["CDFlag"] is outflow_flag, ["Inflow"]] = "-{}".format(
                df["Inflow"]
            )

        return df

    def _fix_amount(self, df: DataFrame) -> DataFrame:
        """
        fix currency string formatting
        convert currency values to floats
        convert negative inflows into outflows and vice versa

        :param df: dataframe to modify
        :type df: DataFrame
        :return: modified dataframe
        :rtype: DataFrame
        """
        # fix various formatting issues
        df["Inflow"] = self._clean_monetary_values(df["Inflow"])
        df["Outflow"] = self._clean_monetary_values(df["Outflow"])

        # negative inflow = outflow
        df.loc[df["Inflow"] < 0, ["Outflow"]] = df["Inflow"] * -1
        df.loc[df["Inflow"] < 0, ["Inflow"]] = 0
        # negative outflow = inflow
        df.loc[df["Outflow"] < 0, ["Inflow"]] = df["Outflow"] * -1
        df.loc[df["Outflow"] < 0, ["Outflow"]] = 0

        return df

    def _clean_monetary_values(self, num_series: DataFrame) -> DataFrame:
        """
        convert "," to "." then remove every instance of . except last one
        remove any characters from inflow or outflow strings except
        digits, "-", and "."
        fill in null values with 0

        :param num_series: series of values to modify
        :type num_series: DataFrame
        :return: modified series
        :rtype: DataFrame
        """
        # convert all commas to full stops
        num_series.replace({"\,": "."}, regex=True, inplace=True)
        # remove all except last decimal point
        num_series.replace({"\.(?=.*?\.)": ""}, regex=True, inplace=True)
        # remove all non-digit characters
        num_series.replace(
            {
                "[^\d\.-]": "",
            },
            regex=True,
            inplace=True,
        )
        # fill in null values with 0
        num_series.fillna(value=0, inplace=True)
        return num_series.astype(float)

    def _remove_invalid_rows(self, df: DataFrame) -> DataFrame:
        """
        Removes invalid rows from dataframe.
        An invalid row is one which does not have a date or one without an Inflow or Outflow value.

        :param df: dataframe to be modified
        :type df: DataFrame
        :return: modified dataframe
        :rtype: DataFrame
        """
        # filter out rows where Inflow and Outflow are both blank
        df.query("Inflow.notna() & Outflow.notna()", inplace=True)
        # filter rows with an invalid date
        df.query("Date.notna()", inplace=True)

        return df.reset_index()

    def _auto_memo(self, df: DataFrame, fill_memo: bool) -> DataFrame:
        """
        if memo is blank, fill with contents of payee column

        :param df: dataframe to be modified
        :type df: DataFrame
        :param fill_memo: boolean to check
        :type fill_memo: bool
        :return: modified dataframe
        :rtype: DataFrame
        """
        if fill_memo:
            df["Memo"].fillna(df["Payee"])
        return df

    def _fix_date(self, date_series: DataFrame, date_format: str) -> DataFrame:
        """
        If provided with an input date format, process the date column to the ISO format.
        Any non-parseable dates are returned as a NaT null value

        :param df: dataframe to modify
        :type df: DataFrame
        :param date_format: date format codes according to 1989 C standard (https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
        :type date_format: str
        :return: modified dataframe
        :rtype: DataFrame
        """
        date_series = pd.to_datetime(
            date_series,
            format=date_format,
            infer_datetime_format=True,
            errors="coerce",
        )

        logging.debug("\nFixed dates:\n{}".format(date_series.head()))

        return date_series

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
        new_filename = "{}{}.csv".format(
            self.config["fixed_prefix"], target_fname
        )
        while os.path.isfile(new_filename):
            counter = 1
            new_filename = "{}{}_{}.csv".format(
                self.config["fixed_prefix"], target_fname, counter
            )
            counter += 1
        target_filename = join(target_dir, new_filename)
        logging.info("Writing output file: {}".format(target_filename))
        # write dataframe to csv
        df.to_csv(target_filename, index=False)
        return target_filename


def build_bank(
    bank_config,
):  # mostly commented out for now as plugins need to be fixed
    """Factory method loading the correct class for a given configuration."""
    plugin_module = bank_config.get("plugin", None)
    """ if plugin_module:
        p_mod = importlib.import_module("plugins.{}".format(plugin_module))
        if not hasattr(p_mod, "build_bank"):
            s = (
                "The specified plugin {}.py".format(plugin_module)
                + "does not contain the required "
                "build_bank(config) method."
            )
            raise ImportError(s)
        bank = p_mod.build_bank(bank_config)
        return bank
    else: """  # DEBUG - plugins broken
    return B2YBank(bank_config)


class Bank2Ynab:
    """Main program instance, responsible for gathering configuration,
    creating the right object for each bank, and triggering elaboration."""

    def __init__(self, config_object):
        self.banks = []
        self.transaction_data = {}

        for section in config_object.sections():
            bank_config = b2y_utilities.fix_conf_params(config_object, section)
            bank_object = build_bank(bank_config)
            self.banks.append(bank_object)

    def run(self):
        """Main program flow"""
        # initialize variables for summary:
        files_processed = 0
        # process account for each config file
        for bank in self.banks:
            # find all applicable files
            files = bank.get_files()
            bank_name = bank.name
            for src_file in files:
                logging.info(
                    "\nParsing input file:  {} (format: {})".format(
                        src_file, bank_name
                    )
                )
                try:  # TODO: is this Try/Except the best way to handle format mismatches?
                    # create cleaned csv for each file
                    output_df = bank.read_data(src_file)
                    # increment for the summary:
                    files_processed += 1

                except ValueError as e:
                    logging.info(
                        "No output data from this file for this bank. ({})".format(
                            e
                        )
                    )
            """# DEBUG: disabled file output while testing
            if output != []:
                bank.write_data(src_file, output_df)
                # save transaction data for each bank to object
                self.transaction_data[bank_name] = output_df
                # delete original csv file
                if bank.config["delete_original"] is True:
                    logging.info(
                        "Removing input file: {}".format(src_file)
                    )
                    # os.remove(src_file) DEBUG - disabled deletion while testing
            else:
                logging.info(
                    "No output data from this file for this bank."
                ) """

        logging.info("\nDone! {} files processed.\n".format(files_processed))
