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

import b2y_utilities

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


# Classes doing the actual work
class B2YBank(object):
    """ Object parsing and outputting data for a specific bank.
    This can be subclassed to handle formats requiring special handling,
    overriding any of get_files(), read_data() or write_data()."""

    def __init__(self, config_object):
        """
        :param config_object: dict containing config parameters
        """
        self.name = config_object.get("bank_name", "DEFAULT")
        self.config = config_object

    def get_files(self):
        """ find the transaction file
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
            if files != [] and missing_dir is True:
                s = (
                    "\nFormat: {}\n\nError: Can't find download path: {}"
                    "\nTrying default path instead:\t {}"
                )
                logging.error(s.format(self.name, try_path, path))
        return files

    def read_data(self, file_path):
        """ extract data from given transaction file
        :param file_path: path to file
        :return: list of cleaned data rows
        """
        delim = self.config["input_delimiter"]
        output_columns = self.config["output_columns"]
        header_rows = int(self.config["header_rows"])
        footer_rows = int(self.config["footer_rows"])
        cd_flags = self.config["cd_flags"]
        date_format = self.config["date_format"]
        fill_memo = self.config["payee_to_memo"]
        output_data = []

        # give plugins a chance to pre-process the file
        self._preprocess_file(file_path)

        # get total number of rows in transaction file using a generator
        with b2y_utilities.EncodingCsvReader(
            file_path, delimiter=delim
        ) as row_count_reader:
            row_count = sum(1 for row in row_count_reader)

        with b2y_utilities.EncodingCsvReader(
            file_path, delimiter=delim
        ) as transaction_reader:
            # make each row of our new transaction file
            for line, row in enumerate(transaction_reader):
                # skip header & footer rows
                if header_rows <= line <= (row_count - footer_rows):
                    # skip blank rows
                    if len(row) == 0:
                        continue
                    # process Inflow or Outflow flags
                    row = self._cd_flag_process(row, cd_flags)
                    # fix the date format
                    row = self._fix_date(row, date_format)
                    # create our output_row
                    fixed_row = self._fix_row(row)
                    # convert negative inflows to standard outflows
                    fixed_row = self._fix_outflow(fixed_row)
                    # convert positive outflows to standard inflows
                    fixed_row = self._fix_inflow(fixed_row)
                    # fill in blank memo fields
                    fixed_row = self._auto_memo(fixed_row, fill_memo)
                    # convert decimal point
                    fixed_row = self._fix_decimal_point(fixed_row)
                    # remove extra characters in the inflow and outflow
                    fixed_row = self._clean_monetary_values(fixed_row)
                    # check our row isn't a null transaction
                    if self._valid_row(fixed_row) is True:
                        output_data.append(fixed_row)
        # add in column headers
        line_count = len(output_data)
        logging.info("Parsed {} lines".format(line_count))
        if line_count > 0:
            output_data.insert(0, output_columns)
        return output_data

    def _preprocess_file(self, file_path):
        """
        exists solely to be used by plugins for pre-processing a file
        that otherwise can be read normally (e.g. weird format)
        :param file_path: path to file
        """
        # intentionally empty - the plugins can use this function
        return

    def _fix_row(self, row):
        """
        rearrange a row of our file to match expected output format,
        optionally combining multiple input columns into a single output column
        :param row: list of values
        :return: list of values in correct output format
        """
        output = []
        for header in self.config["output_columns"]:
            # find all input columns with data for this output column
            indices = filter(
                lambda i: self.config["input_columns"][i] == header,
                range(len(self.config["input_columns"])),
            )
            # fetch data from those input columns if they are not empty,
            # and merge them
            cell_parts = []
            for i in indices:
                try:
                    if row[i].lstrip():
                        cell_parts.append(row[i].lstrip())
                except IndexError:
                    pass
            cell = " ".join(cell_parts)
            output.append(cell)
        return output

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

    def _valid_row(self, row):
        """ if our row doesn't have an inflow, outflow or a valid date,
        mark as invalid
        :param row: list of values
        """
        inflow_index = self.config["output_columns"].index("Inflow")
        outflow_index = self.config["output_columns"].index("Outflow")
        if row[inflow_index] == "" and row[outflow_index] == "":
            return False
        # check that date matches YYYY-MM-DD format
        date_index = self.config["output_columns"].index("Date")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[date_index]):
            return False
        return True

    def _auto_memo(self, row, fill_memo):
        """ auto fill empty memo field with payee info
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
        """ fix date format when required
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

    def _cd_flag_process(self, row, cd_flags):
        """ fix rows where inflow or outflow is indicated by
        a flag in a separate column
        :param row: list of values
        :param cd_flags: list of parameters for applying indicators
        """
        if len(cd_flags) == 3:
            indicator_col = int(cd_flags[0])
            outflow_flag = cd_flags[2]
            inflow_col = self.config["input_columns"].index("Inflow")
            # if this row is indicated to be outflow, make inflow negative
            if row[indicator_col] == outflow_flag:
                row[inflow_col] = "-" + row[inflow_col]
        return row

    def write_data(self, filename, data):
        """ write out the new CSV file
        :param filename: path to output file
        :param data: cleaned data ready to output
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
        with b2y_utilities.EncodingCsvWriter(target_filename) as writer:
            for row in data:
                writer.writerow(row)
        return target_filename


def build_bank(bank_config):
    """ Factory method loading the correct class for a given configuration. """
    plugin_module = bank_config.get("plugin", None)
    if plugin_module:
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
    else:
        return B2YBank(bank_config)


class Bank2Ynab(object):
    """ Main program instance, responsible for gathering configuration,
    creating the right object for each bank, and triggering elaboration."""

    def __init__(self, config_object):
        self.banks = []
        self.transaction_data = {}

        for section in config_object.sections():
            bank_config = b2y_utilities.fix_conf_params(config_object, section)
            bank_object = build_bank(bank_config)
            self.banks.append(bank_object)

    def run(self):
        """ Main program flow """
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
                if output != []:
                    bank.write_data(src_file, output)
                    # save transaction data for each bank to object
                    self.transaction_data[bank_name] = output
                    # delete original csv file
                    if bank.config["delete_original"] is True:
                        logging.info(
                            "Removing input file: {}".format(src_file)
                        )
                        os.remove(src_file)
                else:
                    logging.info(
                        "No output data from this file for this bank."
                    )

        logging.info("\nDone! {} files processed.\n".format(files_processed))
