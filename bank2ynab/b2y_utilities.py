import os
import configparser
import chardet
import logging
import codecs
import csv


# Generic utilities
def get_configs():
    """Retrieve all configuration parameters."""
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
    """from a ConfigParser object, return a dictionary of all parameters
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
    """finds the downloads folder for the active user if filepath is not set"""
    if filepath == "":
        if os.name == "nt":
            # Windows
            import winreg
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
