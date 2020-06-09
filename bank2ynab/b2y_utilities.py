import os
import configparser
import chardet
import logging
import codecs
import csv


# Generic utilities
def get_configs():
    """ Retrieve all configuration parameters."""
    # TODO - fix path for these
    path = os.path.realpath(__file__)
    parent_dir = os.path.dirname(path)
    project_dir = os.path.dirname(parent_dir)
    conf_files = [
        os.path.join(project_dir, "bank2ynab.conf"),
        os.path.join(project_dir, "user_configuration.conf"),
    ]
    try:
        if not os.path.exists(conf_files[0]):
            raise FileNotFoundError
    except FileNotFoundError:
        s = "Configuration file not found: {}".format(conf_files[0])
        logging.error(s)
        raise FileNotFoundError(s)
    else:
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


def detect_encoding(filepath):
    """
    Utility to detect file encoding. This is imperfect, but
    should work for the most common cases.
    :param filepath: string path to a given file
    :return: encoding alias that can be used with open()
    """
    # First try to guess the encoding with chardet. Take it if the
    # confidence is >50% (randomly chosen)
    with open(filepath, "rb") as f:
        file_content = f.read()
        rslt = chardet.detect(file_content)
        confidence, encoding = rslt["confidence"], rslt["encoding"]
        if confidence > 0.5:
            logging.info(
                "Using encoding {} with confidence {}".format(
                    encoding, confidence
                )
            )
            return encoding

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


# -- end of utilities
