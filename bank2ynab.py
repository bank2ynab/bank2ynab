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
# API testing stuff
import requests
import json

# configure our logger
logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)

# main Python2 switch
# any module with different naming should be handled here
__PY2 = False
try:
    import configparser
except ImportError:
    __PY2 = True
    import ConfigParser as configparser
    import cStringIO
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError


# classes dealing with input and output charsets across python versions
# (well, really just for py2...)
class CrossversionFileContext(object):
    """ ContextManager class for common operations on files"""

    def __init__(self, file_path, is_py2, **kwds):
        self.file_path = os.path.abspath(file_path)
        self.stream = None
        self.csv_object = None
        self.params = kwds
        self.is_py2 = is_py2

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


class CrossversionCsvReader(CrossversionFileContext):
    """ context manager returning a csv.Reader-compatible object
    regardless of Python version"""

    def __enter__(self):
        encoding = detect_encoding(self.file_path)
        if self.is_py2:
            self.stream = open(self.file_path, "rb")
            self.csv_object = UnicodeReader(self.stream,
                                            encoding=encoding,
                                            **self.params)
        else:
            self.stream = open(self.file_path, encoding=encoding)
            self.csv_object = csv.reader(self.stream, **self.params)
        return self.csv_object


class CrossversionCsvWriter(CrossversionFileContext):
    """ context manager returning a csv.Writer-compatible object
    regardless of Python version"""

    def __enter__(self):
        if self.is_py2:
            self.stream = open(self.file_path, "wb")
            self.csv_object = UnicodeWriter(
                self.stream,
                encoding="utf-8",
                **self.params)
        else:
            self.stream = open(
                self.file_path, "w",
                encoding="utf-8", newline="")
            self.csv_object = csv.writer(self.stream, **self.params)
        return self.csv_object


def detect_encoding(filepath):
    """
    Utility to detect file encoding. This is imperfect, but
    should work for the most common cases.
    :param filepath: string path to a given file
    :return: encoding alias that can be used with open()in py3
    or codecs.open in py2
    """
    # because some encodings will happily encode anything even if wrong,
    # keeping the most common near the top should make it more likely that
    # we're doing the right thing.
    encodings = ['ascii', 'utf-8', 'utf-16', 'cp1251', 'utf_32', 'utf_32_be',
                 'utf_32_le', 'utf_16', 'utf_16_be',
                 'utf_16_le', 'utf_7', 'utf_8_sig', 'cp850', 'cp852',
                 'latin_1', 'big5', 'big5hkscs', 'cp037', 'cp424',
                 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 'cp855',
                 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862',
                 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874',
                 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026',
                 'cp1140', 'cp1250', 'cp1252', 'cp1253', 'cp1254', 'cp1255',
                 'cp1256', 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004',
                 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz',
                 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2',
                 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
                 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3',
                 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7',
                 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11',
                 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16',
                 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek',
                 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish',
                 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213']
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


# utilities to be used only by py2
# see https://docs.python.org/2/library/csv.html#examples for explanation
class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

    @property
    def line_num(self):
        return self.reader.line_num


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue().decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
# -- end of py2 utilities
# -- end of charset-handling classes


# Generic utilities
def get_configs():
    """ Retrieve all configuration parameters."""
    conf_files = ["bank2ynab.conf", "user_configuration.conf"]
    if not os.path.exists("bank2ynab.conf"):
        logging.error("\nError: Can't find configuration file: bank2ynab.conf")
    config = configparser.RawConfigParser()
    if __PY2:
        config.read(conf_files)
    else:
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
        "api_token": ["YNAB API Access Token", False, ""]
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
            shell_path = ("SOFTWARE\\Microsoft\\Windows\\CurrentVersion"
                          "\\Explorer\\Shell Folders")
            dl_key = "{374DE290-123F-4565-9164-39C4925E467B}"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, shell_path) as key:
                input_dir = winreg.QueryValueEx(key, dl_key)[0]
        else:
            # Linux, OSX
            userhome = os.path.expanduser('~')
            input_dir = os.path.join(userhome, "Downloads")
    else:
        if not os.path.exists(filepath):
            s = "Error: Input directory not found: {}"
            raise FileNotFoundError(s.format(filepath))
        input_dir = filepath
    return input_dir


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
                input("{} (range {} - {}): ".format(msg, min, max)))
            if user_input < min or user_input > max:
                raise ValueError
            break
        except ValueError:
            logging.info(
                "This integer is not in the acceptable range, try again!")
    return user_input

# -- end of utilities


# Classes doing the actual work
class B2YBank(object):
    """ Object parsing and outputting data for a specific bank.
    This can be subclassed to handle formats requiring special handling,
    overriding any of get_files(), read_data() or write_data()."""

    def __init__(self, config_object, is_py2=False):
        """
        :param config_object: dict containing config parameters
        :param is_py2: flag signalling we are running under python 2
        """
        self.name = config_object.get("bank_name", "DEFAULT")
        self.config = config_object
        self._is_py2 = is_py2

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
                files = [join(path, f)
                         for f in directory_list
                         if f.endswith(ext)
                         if re.match(file_pattern + r".*\.", f)
                         if prefix not in f]
            else:
                files = [join(path, f)
                         for f in directory_list
                         if f.endswith(ext)
                         if f.startswith(file_pattern)
                         if prefix not in f]
            if files != [] and missing_dir is True:
                s = ("\nFormat: {}\n\nError: Can't find download path: {}"
                     "\nTrying default path instead:\t {}")
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
        with CrossversionCsvReader(file_path,
                                   self._is_py2,
                                   delimiter=delim) as row_count_reader:
            row_count = sum(1 for row in row_count_reader)

        with CrossversionCsvReader(file_path,
                                   self._is_py2,
                                   delimiter=delim) as transaction_reader:
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
                    # fill in blank memo fields
                    fixed_row = self._auto_memo(fixed_row, fill_memo)
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
            indices = filter(lambda i:
                             self.config["input_columns"][i] == header,
                             range(len(self.config["input_columns"])))
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
        if(inflow.startswith("-")):
            row[inflow_index] = ""
            row[outflow_index] = inflow[1:]
        return row

    def _valid_row(self, row):
        """ if our row doesn't have an inflow or outflow, mark as invalid
        :param row: list of values
        """
        inflow_index = self.config["output_columns"].index("Inflow")
        outflow_index = self.config["output_columns"].index("Outflow")
        if row[inflow_index] == "" and row[outflow_index] == "":
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
        convert date to DD/MM/YYYY
        :param row: list of values
        :param date_format: date format string
        """
        if not(date_format):
            return(row)

        date_col = self.config["input_columns"].index("Date")
        try:
            if row[date_col] == "":
                return row
            # parse our date according to provided formatting string
            input_date = datetime.strptime(row[date_col].lstrip(), date_format)
            # do our actual date processing
            output_date = datetime.strftime(input_date, "%d/%m/%Y")
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
            self.config["fixed_prefix"],
            target_fname)
        while os.path.isfile(new_filename):
            counter = 1
            new_filename = "{}{}_{}.csv".format(
                self.config["fixed_prefix"],
                target_fname, counter)
            counter += 1
        target_filename = join(target_dir, new_filename)
        logging.info("Writing output file: {}".format(target_filename))
        with CrossversionCsvWriter(target_filename, self._is_py2) as writer:
            for row in data:
                writer.writerow(row)
        return target_filename


def build_bank(bank_config):
    """ Factory method loading the correct class for a given configuration. """
    plugin_module = bank_config.get("plugin", None)
    if plugin_module:
        p_mod = importlib.import_module("plugins.{}".format(plugin_module))
        if not hasattr(p_mod, "build_bank"):
            s = ("The specified plugin {}.py".format(plugin_module) +
                 "does not contain the required "
                 "build_bank(config, is_py2) method.")
            raise ImportError(s)
        bank = p_mod.build_bank(bank_config, __PY2)
        return bank
    else:
        return B2YBank(bank_config, __PY2)


class Bank2Ynab(object):
    """ Main program instance, responsible for gathering configuration,
    creating the right object for each bank, and triggering elaboration."""

    def __init__(self, config_object, is_py2=False):
        self._is_py2 = is_py2
        self.banks = []
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
                logging.info("\nParsing input file:  {} (format: {})".format(
                    src_file, bank_name))
                # increment for the summary:
                files_processed += 1
                # create cleaned csv for each file
                output = bank.read_data(src_file)
                bank.write_data(src_file, output)
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
        # TODO: get a hold of the transactions
        self.transactions = ""
        self.budget_ids = []
        self.account_ids = []

        self.api_token = get_config_line(config_object, "DEFAULT",
                                         ["YNAB API Access Token", False, ""])
        self.budget_id = None
        self.account_id = None

        # TODO: Fix debug structure, so it will be used in logging instead
        self.debug = False

    def run(self):
        if(self.api_token is not None):
            logging.info("Connecting to YNAB API...")

            error_code = self.list_budgets()  # test API token auth
            if error_code[0] == "401":  # TODO: need to handle other errors
                return error_code

            else:
                if(self.budget_id is None):
                    msg = "No default budget set! \nPick a budget"
                    self.list_budgets()  # create list of budget_ids
                    budget_selection = int_input(1, len(self.budget_ids), msg)
                    self.budget_id = self.budget_ids[budget_selection - 1]

                if(self.account_id is None):
                    msg = "No default account set! \nPick an account"
                    self.list_accounts()  # create list of account_ids
                    account_selection = int_input(
                        1, len(self.account_ids), msg)
                    self.account_id = self.account_ids[account_selection - 1]

                if(self.budget_id is not None and self.account_id is not None):
                    self.post_transactions()
        else:
            logging.info("No API-token provided.")

    def post_transactions(self):
        logging.info("Posting transactions..")
        url = ("https://api.youneedabudget.com/v1/budgets/" +
               "{}/transactions?access_token={}".format(
                   self.budget_id,
                   self.api_token))

        # Globals
        account_id = self.account_id
        payee_id = None
        category_id = None
        cleared = "cleared"
        approved = False
        flag_color = None
        import_id = None

        # TODO: use date, amount, payee and memo from transactions
        date = "2019-01-01"
        amount = 12000000000
        payee_name = None
        memo = None

        data = {
            "transactions": []
        }

        # TODO: CLEANUP, this is just a mess!
        transaction1 = {
            "account_id": account_id,
            "date": date,
            "amount": amount,
            "payee_id": payee_id,
            "payee_name": payee_name,
            "category_id": category_id,
            "memo": memo,
            "cleared": cleared,
            "approved": approved,
            "flag_color": flag_color,
            "import_id": import_id
        }
        # TODO: CLEANUP, this is just a mess!
        transaction2 = {
            "account_id": account_id,
            "date": date,
            "amount": 999299,
            "payee_id": payee_id,
            "payee_name": "woman of power",
            "category_id": category_id,
            "memo": memo,
            "cleared": cleared,
            "approved": approved,
            "flag_color": flag_color,
            "import_id": import_id
        }

        # TODO: should be a loop of some sort
        data['transactions'].append(transaction1)
        data['transactions'].append(transaction2)

        post_response = requests.post(url, json=data)
        if 'error' in json.loads(post_response.text):
            logging.error("error while sending %s" % str(data['transactions']))
            logging.error(json.loads(post_response.text)['error'])

    def list_transactions(self):
        url = ("https://api.youneedabudget.com/v1/budgets/" +
               "{}/transactions?access_token={}".format(
                   self.budget_id,
                   self.api_token))
        response = requests.get(url)
        transactions = response.json()['data']['transactions']
        if len(transactions) > 0:
            logging.debug("Listing transactions:")
            for t in transactions:
                logging.debug(t)
        else:
            logging.debug("no transactions found")

    def list_accounts(self):
        url = ("https://api.youneedabudget.com/v1/budgets/" +
               "{}/accounts?access_token={}".format(
                   self.budget_id,
                   self.api_token))
        response = requests.get(url)
        accounts = response.json()['data']['accounts']
        if len(accounts) > 0:

            logging.info("Listing accounts:")
            index = 0
            for t in accounts:
                index = index + 1
                print("| {} | {}".format(index, t['name']))
                self.account_ids.append(t['id'])

                logging.debug("id: {}".format(t['id']))
                logging.debug("on_budget: {}".format(t['on_budget']))
                logging.debug("closed: {}".format(t['closed']))
        else:
            logging.info("no accounts found")

    def list_budgets(self):
        url = ("https://api.youneedabudget.com/v1/budgets?" +
               "access_token={}".format(
                   self.api_token))
        response = requests.get(url)
        try:
            budgets = response.json()['data']['budgets']
            index = 0
            for x in budgets:
                index = index + 1
                print("| {} | {}".format(index, x['name']))
                self.budget_ids.append(x["id"])
                # debug messages:
                for key, value in x.items():
                    if(type(value) is dict):
                        logging.debug("%s: " % str(key))

                        for subkey, subvalue in value.items():
                            logging.debug("  %s: %s" %
                                          (str(subkey), str(subvalue)))
                    else:
                        logging.debug("%s: %s" % (str(key), str(value)))
        except KeyError:
            return self.api_error_print(response.json()["error"])

    def api_error_print(self, details):
        """
        Prints details about errors returned by the YNAB api
        :param: details: dictionary of returned error info from the YNAB api
        :return id: HTTP error ID
        :return detail: human-understandable explanation of error
        """

        errors = {
            "400": "Bad syntax or validation error",
            "401": "API access token missing, invalid, revoked, or expired",
            "403.1": "The subscription for this account has lapsed.",
            "403.2": "The trial for this account has expired.",
            "404.1": "The specified URI does not exist.",
            "404.2": "Resource not found",
            "409": "Conflict error",
            "429": "Too many requests - rate-limited. Wait a while and try again.",
            "500": "Unexpected error"
        }
        id = details["id"]
        name = details["name"]
        detail = errors[id]
        logging.error("{}: {} ({})".format(detail, id, name))
        return [id, detail]


# Let's run this thing!
if __name__ == "__main__":
    b2y = Bank2Ynab(get_configs(), __PY2)
    b2y.run()
    api = YNAB_API(get_configs())
    api.run()  # I wonder should we call this inside the processing of each individual bank so we can access the data from each bank as it's created?
