#! /usr/bin/python3
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
import sys
import importlib
import re

# main Python2 switch
# any module with different naming should be handled here
__PY2 = False
try:
    import configparser
except ImportError:
    __PY2 = True
    import ConfigParser as configparser
    import cStringIO


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
    conf_files = [f for f in os.listdir(".") if f.endswith(".conf")]
    if conf_files == []:
        print("\nError: Can't find configuration file: bank2ynab.conf")
    config = configparser.ConfigParser()
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
            "has_headers": ["Source Has Column Headers", True, ""],
            "delete_original": ["Delete Source File", True, ""],
            "plugin": ["Plugin", False, ""]}

    # Bank Download = False
    # Bank Download URL = ""
    # Bank Download Login = ""
    # Bank Download Auth1 = ""
    # Bank Download Auth2 = ""
    for key in config:
        config[key] = get_config_line(conf_obj, section_name, config[key])
    config["bank_name"] = section_name

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
    if filepath is "":
        if os.name is "nt":
            # Windows
            try:
                import winreg
            except ImportError:
                import _winreg as winreg
            shell_path = ("SOFTWARE\Microsoft\Windows\CurrentVersion"
                          "\Explorer\Shell Folders")
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
        if file_pattern is not "":
            try:
                path = find_directory(try_path)
            except FileNotFoundError:
                missing_dir = True
                path = find_directory("")
            path = abspath(path)
            directory_list = os.listdir(path)
            if regex_active is True:
                files = [join(path, f)
                         for f in directory_list if f.endswith(ext)
                         if re.search(file_pattern, f) if prefix not in f]
            else:
                files = [join(path, f)
                         for f in directory_list if f.endswith(ext)
                         if file_pattern in f if prefix not in f]
            if files != [] and missing_dir is True:
                s = ("\nFormat: {}\n\nError: Can't find download path: {}"
                     "\nTrying default path instead:\t {}")
                print(s.format(self.name, try_path, path))
        return files

    def read_data(self, file_path):
        """ extract data from given transaction file
        :param file_path: path to file
        :return: list of cleaned data rows
        """
        delim = self.config["input_delimiter"]
        output_columns = self.config["output_columns"]
        has_headers = self.config["has_headers"]
        output_data = []

        with CrossversionCsvReader(file_path,
                                   self._is_py2,
                                   delimiter=delim) as transaction_reader:
            # make each row of our new transaction file
            for row in transaction_reader:
                # add new row to output list
                fixed_row = self._auto_memo(self._fix_row(row))
                # check our row isn't a null transaction
                if self._valid_row(fixed_row) is True:
                    output_data.append(fixed_row)
            # fix column headers
            if has_headers is False:
                output_data.insert(0, output_columns)
            else:
                if output_data:
                    output_data[0] = output_columns
                else:
                    output_data.append(output_columns)
        print("Parsed {} lines".format(len(output_data)))
        return output_data

    def _fix_row(self, row):
        """
        rearrange a row of our file to match expected output format
        :param row: list of values
        :return: list of values in correct output format
        """
        output = []
        for header in self.config["output_columns"]:
            try:
                # check to see if our output header exists in input
                index = self.config["input_columns"].index(header)
                cell = row[index]
            except (ValueError, IndexError):
                # header isn't in input, default to blank cell
                cell = ""
            output.append(cell)
        return output

    def _valid_row(self, row):
        """ if our row doesn't have an inflow or outflow, mark as invalid
        """
        inflow_index = self.config["output_columns"].index("Inflow")
        outflow_index = self.config["output_columns"].index("Outflow")
        if row[inflow_index] == "" and row[outflow_index] == "":
            return False
        return True

    def _auto_memo(self, row):
        """ auto fill empty memo field with payee info """
        payee_index = self.config["output_columns"].index("Payee")
        memo_index = self.config["output_columns"].index("Memo")
        if row[memo_index] == "":
            row[memo_index] = row[payee_index]
        return row

    def write_data(self, filename, data):
        """ write out the new CSV file
        :param filename: path to output file
        :param data: cleaned data ready to output
        """
        target_dir = dirname(filename)
        target_fname = basename(filename)
        new_filename = self.config["fixed_prefix"] + target_fname
        target_filename = join(target_dir, new_filename)
        print("Writing output file: {}".format(target_filename))
        with CrossversionCsvWriter(target_filename, self._is_py2) as writer:
            for row in data:
                writer.writerow(row)
        return target_filename


def build_bank(bank_config):
    """ Factory method loading the correct class for a given configuration. """
    plugin_module = bank_config.get("plugin", None)
    if plugin_module:
        p_mod = importlib.import_module(".{}".format(plugin_module), "plugins")
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
            for original_file_path in files:
                print("\nParsing input file:  {}".format(original_file_path))
                # increment for the summary:
                files_processed += 1
                # create cleaned csv for each file
                output = bank.read_data(original_file_path)
                bank.write_data(original_file_path, output)
                # delete original csv file
                if bank.config["delete_original"] is True:
                    print("Removing input file: {}".format(original_file_path))
                    os.remove(original_file_path)
        print("\nDone! {} files processed.\n".format(files_processed))


# Let's run this thing!
if __name__ == "__main__":
    b2y = Bank2Ynab(get_configs(), __PY2)
    b2y.run()
