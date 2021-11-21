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
class B2YBank(object):
    """Object parsing and outputting data for a specific bank.
    This can be subclassed to handle formats requiring special handling,
    overriding any of get_files(), read_data() or write_data()."""

    def __init__(self, config_object):
        """
        :param config_object: dict containing config parameters
        """
        self.name = config_object.get("bank_name", "DEFAULT")
        self.config = config_object

    def get_files(self):
        """find the transaction file
        :return: list of matching files found
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
        output_data = []

        # give plugins a chance to pre-process the file
        self._preprocess_file(file_path)

        # create a list of column indices to use
        included_cols = []
        for index, column in enumerate(input_columns):
            if column in output_columns:
                included_cols.append(index)

        # create a transaction dataframe TODO: look into read_csv arguments to see which are useful
        df = pd.read_csv(
            filepath_or_buffer=file_path,
            delimiter=delim,
            skipinitialspace=True,  # skip space after delimiter
            header=None,  # don't set column headers initially
            skiprows=header_rows,  # skip header rows
            skipfooter=footer_rows,  # skip footer rows
            skip_blank_lines=True,  # skip blank lines
            # parse_dates=False, # need to work the date parsing functionality out - could work nicely!
            # infer_datetime_format=False,
            # keep_date_col=False,
            # date_parser=None,
            # dayfirst=False, # we probably don't want this because we're converting to ISO
            # decimal='.', # potential for replacing the fix_decimal function, but will require an extra config param
            # encoding=None, # hopefully we don't have to worry about this
            # encoding_errors='strict', # hopefully we don't have to worry about this
            # dialect=None,
            # on_bad_lines="skip",  # skip lines that cause csv errors # TODO: fix errors coming from this line before enabling
            memory_map=True,  # map the file object directly onto memory & access data directly - no I/O overhead
            engine="python",
        )

        print(
            "\nInitial DF\n{}".format(df.head())
        )  # debug to see what our df is like before transformation

        # convert each transaction to match ideal output data

        # set column names based on input column list
        df.columns = input_columns
        # merge duplicate input columns
        df = self._merge_duplicate_columns(df, input_columns)
        print("\nAfter duplicate merge\n{}".format(df.head()))  # debug
        # add missing columns
        df = self._add_missing_columns(df, input_columns, output_columns)
        # process Inflow/Outflow flags # TODO not yet implemented
        df = self._cd_flag_process(cd_flags, df)

        """ TODO: FUNCTIONS NOT YET TACKLED
        # # process Inflow or Outflow flags
        # row = self._cd_flag_process(row, cd_flags)
        # # fix the date format
        # row = self._fix_date(row, date_format)
        # # convert negative inflows to standard outflows
        # fixed_row = self._fix_outflow(fixed_row)
        # # convert positive outflows to standard inflows
        # fixed_row = self._fix_inflow(fixed_row)
        # # fill in blank memo fields
        # fixed_row = self._auto_memo(fixed_row, fill_memo)
        # # convert decimal point
        # fixed_row = self._fix_decimal_point(fixed_row)
        # # remove extra characters in the inflow and outflow
        # fixed_row = self._clean_monetary_values(fixed_row) """

        # remove invalid rows # TODO date checking
        df = self._remove_invalid_rows(df)
        # set final column order
        df = df[output_columns]
        # display parsed line count
        line_count = df.shape[0]
        logging.info("Parsed {} lines".format(line_count))
        print(
            "\nFinal DF\n{}".format(df.head())
        )  # DEBUG - let's see what our Dataframe looks like
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
            df.insert(loc=0, column=col, value="NaN")
        return df

    def _cd_flag_process(self, cd_flags: list, df: DataFrame) -> DataFrame:
        """
        fix columns where inflow/outflow is indicated by a flag in a separate column

        :param cd_flags: list of parameters for applying indicators
        :type cd_flags: list
        :param df: dataframe to be modified
        :type df: DataFrame
        :return: modified dataframe
        :rtype: DataFrame
        """
        if len(cd_flags) == 3:
            indicator_col = int(cd_flags[0])
            outflow_flag = cd_flags[2]
            # if this row is indicated to be outflow, make inflow negative
            # if row[indicator_col] == outflow_flag:
            #    row[inflow_col] = "-" + row[inflow_col]
            print(df["CDFlag"])

        return df

    def _fix_outflow(self, row):
        """
        convert negative inflow into positive outflow
        :param row: list of values
        :return: list of values with corrected outflow column
        """
        inflow_index = self.config["output_columns"].index("Inflow")
        outflow_index = self.config["output_columns"].index("Outflow")
        inflow = row[inflow_index]
        if inflow.startswith("-"):
            row[inflow_index] = ""
            row[outflow_index] = inflow[1:]
        return row

    def _fix_inflow(self, row):
        """
        convert positive outflow into inflow
        :param row: list of values
        :return: list of values with corrected outflow column
        """
        inflow_index = self.config["output_columns"].index("Inflow")
        outflow_index = self.config["output_columns"].index("Outflow")
        outflow = row[outflow_index]
        if outflow.startswith("+"):
            row[outflow_index] = ""
            row[inflow_index] = outflow[1:]
        return row

    def _fix_decimal_point(self, row):
        """
        convert , to . in inflow and outflow strings
        then remove every instance of . except last one
        :param row: list of values
        """
        inflow_index = self.config["output_columns"].index("Inflow")
        outflow_index = self.config["output_columns"].index("Outflow")
        inflow = row[inflow_index].replace(",", ".")
        outflow = row[outflow_index].replace(",", ".")
        dot_count = inflow.count(".") - 1
        row[inflow_index] = inflow.replace(".", "", dot_count)
        dot_count = outflow.count(".") - 1
        row[outflow_index] = outflow.replace(".", "", dot_count)

        return row

    def _clean_monetary_values(self, row):
        """
        remove any characters from inflow or outflow strings except
        digits and '.'
        :param row: list of values
        """
        inflow_index = self.config["output_columns"].index("Inflow")
        outflow_index = self.config["output_columns"].index("Outflow")
        row[inflow_index] = re.sub(r"[^\d\.]", "", row[inflow_index])
        row[outflow_index] = re.sub(r"[^\d\.]", "", row[outflow_index])

        return row

    def _remove_invalid_rows(
        self, df: DataFrame
    ) -> DataFrame:  # not yet implemented
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
        # TODO # filter rows with an invalid date
        """ # check that date matches YYYY-MM-DD format
        date_index = self.config["output_columns"].index("Date")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[date_index]):
            return False """

        return df

    def _auto_memo(self, row, fill_memo):
        """auto fill empty memo field with payee info
        :param row: list of values
        :param fill_memo: boolean
        """
        if fill_memo:
            payee_index = self.config["output_columns"].index("Payee")
            memo_index = self.config["output_columns"].index("Memo")
            if row[memo_index] == "":
                row[memo_index] = row[payee_index]
        return row

    def _fix_date(self, row, date_format):
        """fix date format when required
        convert date to YYYY-MM-DD
        :param row: list of values
        :param date_format: date format string
        """
        if not (date_format):
            return row

        date_col = self.config["input_columns"].index("Date")
        try:
            if row[date_col] == "":
                return row
            # parse our date according to provided formatting string
            input_date = datetime.strptime(row[date_col].strip(), date_format)
            # do our actual date processing
            output_date = datetime.strftime(input_date, "%Y-%m-%d")
            row[date_col] = output_date
        except (ValueError, IndexError):
            pass
        return row

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


class Bank2Ynab(object):
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
                # increment for the summary:
                files_processed += 1
                # create cleaned csv for each file
                output = bank.read_data(src_file)
                """# DEBUG: disabled file output while testing
                if output != []:
                    bank.write_data(src_file, output)
                    # save transaction data for each bank to object
                    self.transaction_data[bank_name] = output
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
