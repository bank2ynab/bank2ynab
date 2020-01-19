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
import codecs
import csv
import os
import importlib
import re
from datetime import datetime
import logging
import configparser

# API testing stuff
import requests
import json

# configure our logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError


# classes dealing with input and output charsets
class EncodingFileContext(object):
    """ ContextManager class for common operations on files"""

    def __init__(self, file_path, **kwds):
        self.file_path = os.path.abspath(file_path)
        self.stream = None
        self.csv_object = None
        self.params = kwds

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # cleanup
        del self.csv_object
        if self.stream is not None:
            self.stream.close()
        if exc_type is not None:
            # this signals not to suppress any exception
            return False


class EncodingCsvReader(EncodingFileContext):
    """ context manager returning a csv.Reader-compatible object"""

    def __enter__(self):
        encoding = detect_encoding(self.file_path)
        self.stream = open(self.file_path, encoding=encoding)
        self.csv_object = csv.reader(self.stream, **self.params)
        return self.csv_object


class EncodingCsvWriter(EncodingFileContext):
    """ context manager returning a csv.Writer-compatible object
    regardless of Python version"""

    def __enter__(self):
        self.stream = open(self.file_path, "w", encoding="utf-8", newline="")
        self.csv_object = csv.writer(self.stream, **self.params)
        return self.csv_object


def detect_encoding(filepath):
    """
    Utility to detect file encoding. This is imperfect, but
    should work for the most common cases.
    :param filepath: string path to a given file
    :return: encoding alias that can be used with open()
    """
    # because some encodings will happily encode anything even if wrong,
    # keeping the most common near the top should make it more likely that
    # we're doing the right thing.
    encodings = [
        "ascii",
        "utf-8",
        "utf-16",
        "cp1251",
        "utf_32",
        "utf_32_be",
        "utf_32_le",
        "utf_16",
        "utf_16_be",
        "utf_16_le",
        "utf_7",
        "utf_8_sig",
        "cp850",
        "cp852",
        "latin_1",
        "big5",
        "big5hkscs",
        "cp037",
        "cp424",
        "cp437",
        "cp500",
        "cp720",
        "cp737",
        "cp775",
        "cp855",
        "cp856",
        "cp857",
        "cp858",
        "cp860",
        "cp861",
        "cp862",
        "cp863",
        "cp864",
        "cp865",
        "cp866",
        "cp869",
        "cp874",
        "cp875",
        "cp932",
        "cp949",
        "cp950",
        "cp1006",
        "cp1026",
        "cp1140",
        "cp1250",
        "cp1252",
        "cp1253",
        "cp1254",
        "cp1255",
        "cp1256",
        "cp1257",
        "cp1258",
        "euc_jp",
        "euc_jis_2004",
        "euc_jisx0213",
        "euc_kr",
        "gb2312",
        "gbk",
        "gb18030",
        "hz",
        "iso2022_jp",
        "iso2022_jp_1",
        "iso2022_jp_2",
        "iso2022_jp_2004",
        "iso2022_jp_3",
        "iso2022_jp_ext",
        "iso2022_kr",
        "latin_1",
        "iso8859_2",
        "iso8859_3",
        "iso8859_4",
        "iso8859_5",
        "iso8859_6",
        "iso8859_7",
        "iso8859_8",
        "iso8859_9",
        "iso8859_10",
        "iso8859_11",
        "iso8859_13",
        "iso8859_14",
        "iso8859_15",
        "iso8859_16",
        "johab",
        "koi8_r",
        "koi8_u",
        "mac_cyrillic",
        "mac_greek",
        "mac_iceland",
        "mac_latin2",
        "mac_roman",
        "mac_turkish",
        "ptcp154",
        "shift_jis",
        "shift_jis_2004",
        "shift_jisx0213",
    ]
    result = None
    error = (ValueError, UnicodeError, UnicodeDecodeError, UnicodeEncodeError)
    for enc in encodings:
        try:
            with codecs.open(filepath, "r", encoding=enc) as f:
                for line in f:
                    line.encode("utf-8")
                return enc
        except error:
            continue
    return result


# Generic utilities
def get_configs():
    """ Retrieve all configuration parameters."""
    conf_files = ["bank2ynab.conf", "user_configuration.conf"]
    if not os.path.exists(conf_files[0]):
        logging.error("Configuration file not found: {}".format(conf_files[0]))
    config = configparser.RawConfigParser()
    config.read(conf_files, encoding="utf-8")
    return config


def fix_conf_params(conf_obj, section_name):
    """ from a ConfigParser object, return a dictionary of all parameters
    for a given section in the expected format.
    Because ConfigParser defaults to values under [DEFAULT] if present, these
    values should always appear unless the file is really bad.

    :param configparser_object: ConfigParser instance
    :param section_name: string of section name in config file
                        (e.g. "MyBank" matches "[MyBank]" in file)
    :return: dict with all parameters
    """
    config = {
        "input_columns": ["Input Columns", False, ","],
        "output_columns": ["Output Columns", False, ","],
        "input_filename": ["Source Filename Pattern", False, ""],
        "path": ["Source Path", False, ""],
        "ext": ["Source Filename Extension", False, ""],
        "regex": ["Use Regex For Filename", True, ""],
        "fixed_prefix": ["Output Filename Prefix", False, ""],
        "input_delimiter": ["Source CSV Delimiter", False, ""],
        "header_rows": ["Header Rows", False, ""],
        "footer_rows": ["Footer Rows", False, ""],
        "date_format": ["Date Format", False, ""],
        "delete_original": ["Delete Source File", True, ""],
        "cd_flags": ["Inflow or Outflow Indicator", False, ","],
        "payee_to_memo": ["Use Payee for Memo", True, ""],
        "plugin": ["Plugin", False, ""],
        "api_token": ["YNAB API Access Token", False, ""],
        "api_account": ["YNAB Account ID", False, "|"],
    }

    for key in config:
        config[key] = get_config_line(conf_obj, section_name, config[key])
    config["bank_name"] = section_name

    # quick n' dirty fix for tabs as delimiters
    if config["input_delimiter"] == "\\t":
        config["input_delimiter"] = "\t"

    return config


def get_config_line(conf_obj, section_name, args):
    """Get parameter for a given section in the expected format."""
    param = args[0]
    boolean = args[1]
    splitter = args[2]
    if boolean is True:
        line = conf_obj.getboolean(section_name, param)
    else:
        line = conf_obj.get(section_name, param)
    if splitter != "":
        line = line.split(splitter)
    return line


def find_directory(filepath):
    """ finds the downloads folder for the active user if filepath is not set
    """
    if filepath == "":
        if os.name == "nt":
            # Windows
            try:
                import winreg
            except ImportError:
                import _winreg as winreg
            shell_path = (
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion"
                "\\Explorer\\Shell Folders"
            )
            dl_key = "{374DE290-123F-4565-9164-39C4925E467B}"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, shell_path) as key:
                input_dir = winreg.QueryValueEx(key, dl_key)[0]
        else:
            # Linux, OSX
            userhome = os.path.expanduser("~")
            input_dir = os.path.join(userhome, "Downloads")
    else:
        if not os.path.exists(filepath):
            s = "Error: Input directory not found: {}"
            raise FileNotFoundError(s.format(filepath))
        input_dir = filepath
    return input_dir


def option_selection(options, msg):
    """
    Used to select from a list of options
    If only one item in list, selects that by default
    Otherwise displays "msg" asking for input selection (integer only)
    :param options: list of [name, option] pairs to select from
    :param msg: the message to display on the input line
    :return option_selected: the selected item from the list
    """
    selection = 1
    count = len(options)
    if count > 1:
        index = 0
        for option in options:
            index += 1
            print("| {} | {}".format(index, option[0]))
        selection = int_input(1, count, msg)
    option_selected = options[selection - 1][1]
    return option_selected


def int_input(min, max, msg):
    """
    Makes a user select an integer between min & max stated values
    :param  min: the minimum acceptable integer value
    :param  max: the maximum acceptable integer value
    :param  msg: the message to display on the input line
    :return user_input: sanitised integer input in acceptable range
    """
    while True:
        try:
            user_input = int(
                input("{} (range {} - {}): ".format(msg, min, max))
            )
            if user_input not in range(min, max + 1):
                raise ValueError
            break
        except ValueError:
            logging.info(
                "This integer is not in the acceptable range, try again!"
            )
    return user_input


def string_num_diff(str1, str2):
    """
    converts strings to floats and subtracts 1 from 2
    also convert output to "milliunits"
    """
    try:
        num1 = float(str1)
    except ValueError:
        num1 = 0.0
    try:
        num2 = float(str2)
    except ValueError:
        num2 = 0.0

    difference = int(1000 * (num2 - num1))
    return difference


# -- end of utilities


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
                path = find_directory(try_path)
            except FileNotFoundError:
                missing_dir = True
                path = find_directory("")
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
        with EncodingCsvReader(file_path, delimiter=delim) as row_count_reader:
            row_count = sum(1 for row in row_count_reader)

        with EncodingCsvReader(
            file_path, delimiter=delim
        ) as transaction_reader:
            # make each row of our new transaction file
            for row in transaction_reader:
                line = transaction_reader.line_num
                # skip header & footer rows
                if header_rows < line <= (row_count - footer_rows):
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
        logging.info("Parsed {} lines".format(len(output_data)))
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
        with EncodingCsvWriter(target_filename) as writer:
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
            bank_config = fix_conf_params(config_object, section)
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
                bank.write_data(src_file, output)
                # save transaction data for each bank to object
                self.transaction_data[bank_name] = output
                # delete original csv file
                if bank.config["delete_original"] is True:
                    logging.info("Removing input file: {}".format(src_file))
                    os.remove(src_file)
        logging.info("\nDone! {} files processed.\n".format(files_processed))


class YNAB_API(object):  # in progress (2)
    """
    uses Personal Access Token stored in user_configuration.conf
    (note for devs: be careful not to accidentally share API access token!)
    """

    def __init__(self, config_object, transactions=None):
        self.transactions = []
        self.account_ids = []
        self.budget_id = None
        self.config = get_configs()
        self.api_token = self.config.get("DEFAULT", "YNAB API Access Token")
        # TODO make user_config section play nice with get_configs()
        self.user_config_path = "user_configuration.conf"
        self.user_config = configparser.RawConfigParser()

        # TODO: Fix debug structure, so it will be used in logging instead
        self.debug = False

    def run(self, transaction_data):
        if self.api_token is not None:
            logging.info("Connecting to YNAB API...")

            # check for API token auth (and other errors)
            error_code = self.list_budgets()
            if error_code[0] == "ERROR":
                return error_code
            else:
                # if no default budget, build budget list and select default
                if self.budget_id is None:
                    msg = "No default budget set! \nPick a budget"
                    budget_ids = self.list_budgets()
                    self.budget_id = option_selection(budget_ids, msg)

                transactions = self.process_transactions(transaction_data)
                if transactions["transactions"] != []:
                    self.post_transactions(transactions)
        else:
            logging.info("No API-token provided.")

    def api_read(self, budget, kwd):
        """
        General function for reading data from YNAB API
        :param  budget: boolean indicating if there's a default budget
        :param  kwd: keyword for data type, e.g. transactions
        :return error_codes: if it fails we return our error
        """
        id = self.budget_id
        api_t = self.api_token
        base_url = "https://api.youneedabudget.com/v1/budgets/"

        if budget is False:
            # only happens when we're looking for the list of budgets
            url = base_url + "?access_token={}".format(api_t)
        else:
            url = base_url + "{}/{}?access_token={}".format(id, kwd, api_t)

        response = requests.get(url)
        try:
            read_data = response.json()["data"][kwd]
        except KeyError:
            # the API has returned an error so let's handle it
            return self.process_api_response(response.json()["error"])
        return read_data

    def process_transactions(self, transaction_data):
        """
        :param transaction_data: dictionary of bank names to transaction lists
        """
        logging.info("Processing transactions...")
        # go through each bank's data
        transactions = []
        for bank in transaction_data:
            # choose what account to write this bank's transactions to
            account_id = self.select_account(bank)
            # save transaction data for each bank in main dict
            account_transactions = transaction_data[bank]
            for t in account_transactions[1:]:
                trans_dict = self.create_transaction(
                    account_id, t, transactions
                )
                transactions.append(trans_dict)
        # compile our data to post
        data = {"transactions": transactions}
        return data

    def create_transaction(self, account_id, this_trans, transactions):
        date = this_trans[0]
        payee = this_trans[1]
        category = this_trans[2]
        memo = this_trans[3]
        amount = string_num_diff(this_trans[4], this_trans[5])

        # assign values to transaction dictionary
        transaction = {
            "account_id": account_id,
            "date": date,
            "payee_name": payee[:50],
            "amount": amount,
            "memo": memo[:100],
            "category": category,
            "cleared": "cleared",
            "import_id": self.create_import_id(amount, date, transactions),
            "payee_id": None,
            "category_id": None,
            "approved": False,
            "flag_color": None,
        }
        return transaction

    def create_import_id(self, amount, date, existing_transactions):
        """
        Create import ID for our transaction
        import_id format = YNAB:amount:ISO-date:occurrences
        Maximum 36 characters ("YNAB" + ISO-date = 10 characters)
        :param amount: transaction amount in "milliunits"
        :param date: date in ISO format
        :param existing_transactions: list of currently-compiled transactions
        :return: properly formatted import ID
        """
        # check is there a duplicate transaction already
        count = 1
        for transaction in existing_transactions:
            try:
                if transaction["import_id"].startswith(
                    "YNAB:{}:{}:".format(amount, date)
                ):
                    count += 1
            except KeyError:
                # transaction doesn't have import id for some reason
                pass
        return "YNAB:{}:{}:{}".format(amount, date, count)

    def post_transactions(self, data):
        # send our data to API
        logging.info("Uploading transactions to YNAB...")
        url = (
            "https://api.youneedabudget.com/v1/budgets/"
            + "{}/transactions?access_token={}".format(
                self.budget_id, self.api_token
            )
        )

        post_response = requests.post(url, json=data)

        # response handling - TODO: make this more thorough!
        try:
            self.process_api_response(json.loads(post_response.text)["error"])
        except KeyError:
            logging.info("Success!")

    def list_transactions(self):
        transactions = self.api_read(True, "transactions")
        if transactions[0] == "ERROR":
            return transactions

        if len(transactions) > 0:
            logging.debug("Listing transactions:")
            for t in transactions:
                logging.debug(t)
        else:
            logging.debug("no transactions found")

    def list_accounts(self):
        accounts = self.api_read(True, "accounts")
        if accounts[0] == "ERROR":
            return accounts

        account_ids = list()
        if len(accounts) > 0:
            for account in accounts:
                account_ids.append([account["name"], account["id"]])
                # debug messages
                logging.debug("id: {}".format(account["id"]))
                logging.debug("on_budget: {}".format(account["on_budget"]))
                logging.debug("closed: {}".format(account["closed"]))
        else:
            logging.info("no accounts found")

        return account_ids

    def list_budgets(self):
        budgets = self.api_read(False, "budgets")
        if budgets[0] == "ERROR":
            return budgets

        budget_ids = list()
        for budget in budgets:
            budget_ids.append([budget["name"], budget["id"]])

            # commented out because this is a bit messy and confusing
            # TODO: make this legible!
            """
            # debug messages:
            for key, value in budget.items():
                if(type(value) is dict):
                    logging.debug("%s: " % str(key))
                    for subkey, subvalue in value.items():
                        logging.debug("  %s: %s" %
                                      (str(subkey), str(subvalue)))
                else:
                    logging.debug("%s: %s" % (str(key), str(value)))
            """
        return budget_ids

    def process_api_response(self, details):
        """
        Prints details about errors returned by the YNAB api
        :param details: dictionary of returned error info from the YNAB api
        :return id: HTTP error ID
        :return detail: human-understandable explanation of error
        """
        # TODO: make this function into a general response handler instead
        errors = {
            "400": "Bad syntax or validation error",
            "401": "API access token missing, invalid, revoked, or expired",
            "403.1": "The subscription for this account has lapsed.",
            "403.2": "The trial for this account has expired.",
            "404.1": "The specified URI does not exist.",
            "404.2": "Resource not found",
            "409": "Conflict error",
            "429": "Too many requests. Wait a while and try again.",
            "500": "Unexpected error",
        }
        id = details["id"]
        name = details["name"]
        detail = errors[id]
        logging.error("{} - {} ({})".format(id, detail, name))

        return ["ERROR", id, detail]

    def select_account(self, bank):
        account_id = ""
        # check if bank has account associated with it already
        try:
            config_line = get_config_line(
                self.config, bank, ["YNAB Account ID", False, "||"]
            )
            # make sure the budget ID matches
            if config_line[0] == self.budget_id:
                account_id = config_line[1]
                logging.info(
                    "Previously-saved account for {} found.".format(bank)
                )
            else:
                raise configparser.NoSectionError(bank)
        except configparser.NoSectionError:
            logging.info("No user configuration for {} found.".format(bank))
        if account_id == "":
            account_ids = self.list_accounts()  # create list of account_ids
            msg = "Pick a YNAB account for transactions from {}".format(bank)
            account_id = option_selection(account_ids, msg)
            # save account selection for bank
            self.save_account_selection(bank, account_id)
        return account_id

    def save_account_selection(self, bank, account_id):
        """
        saves YNAB account to use for each bank
        """
        self.user_config.read(self.user_config_path)
        try:
            self.user_config.add_section(bank)
        except configparser.DuplicateSectionError:
            pass
        self.user_config.set(
            bank,
            "YNAB Account ID",
            "{}||{}".format(self.budget_id, account_id),
        )

        logging.info("Saving default account for {}...".format(bank))
        with open(self.user_config_path, "w", encoding="utf-8") as config_file:
            self.user_config.write(config_file)


# Let's run this thing!
if __name__ == "__main__":
    b2y = Bank2Ynab(get_configs())
    b2y.run()
    api = YNAB_API(get_configs())
    api.run(b2y.transaction_data)
