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

# main Python2 switch
# any module with different naming should be handled here
__PY2 = False
try:
    import configparser
except ImportError:
    __PY2 = True
    import ConfigParser as configparser
    import cStringIO

import codecs
import csv
import os
import sys


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
    """ context manager returning a csv.Reader-compatible object regardless of Python version"""
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
    """ context manager returning a csv.Writer-compatible object regardless of Python version"""
    def __enter__(self):
        if self.is_py2:
            self.stream = open(self.file_path, "wb")
            self.csv_object = UnicodeWriter(self.stream,
                                        encoding="utf-8",
                                        **self.params)
        else:
            self.stream = open(self.file_path, "w", encoding="utf-8", newline="")
            self.csv_object = csv.writer(self.stream, **self.params)
        return self.csv_object


def detect_encoding(filepath):
    """
    Utility to detect file encoding. This is imperfect, but should work for the most common cases.
    :param filepath: string path to a given file
    :return: encoding alias that can be used with open() in py3 or codecs.open in py2
    """
    # because some encodings will happily encode anything even if wrong,
    # keeping the most common near the top should make it more likely that
    # we're doing the right thing.
    encodings = ['ascii', 'utf-8', 'utf-16', 'cp1251', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be',
                 'utf_16_le', 'utf_7', 'utf_8_sig', 'cp850', 'cp852', 'latin_1', 'big5', 'big5hkscs', 'cp037', 'cp424',
                 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861',
                 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950',
                 'cp1006', 'cp1026', 'cp1140', 'cp1250', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257',
                 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz',
                 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
                 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7',
                 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15',
                 'iso8859_16', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2',
                 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213' ]
    result = None
    for enc in encodings:
        try:
            with codecs.open(filepath, "r", encoding=enc) as f:
                for line in f:
                    line.encode("utf-8")
                return enc
        except ValueError or UnicodeError or UnicodeDecodeError or UnicodeEncodeError:
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
# end of py2 utilities


def get_configs():
    # get all our config files
    conf_files = [f for f in os.listdir(".") if f.endswith(".conf")]
    if conf_files == []:
        print("Can't find configuration file.")
    config = configparser.ConfigParser()
    if __PY2:
        config.read(conf_files)
    else:
        config.read(conf_files, encoding="utf-8")
    return config


def fix_conf_params(configparser_object, section_name):
    # repair parameters from our config file and return as a dictionary
    config = dict()
    config["input_columns"] = configparser_object.get(section_name, "Input Columns").split(",")
    config["output_columns"] = configparser_object.get(section_name, "Output Columns").split(",")
    config["input_filename"] = configparser_object.get(section_name, "Source Filename Pattern")
    config["path"] = configparser_object.get(section_name, "Source Path")
    config["ext"] = configparser_object.get(section_name, "Source Filename Extension")
    config["fixed_prefix"] = configparser_object.get(section_name, "Output Filename Prefix")
    config["input_delimiter"] = configparser_object.get(section_name, "Source CSV Delimiter")
    config["has_headers"] = configparser_object.getboolean(section_name, "Source Has Column Headers")
    config["delete_original"] = configparser_object.getboolean(section_name, "Delete Source File")

    # # Direct bank download
    # Bank Download = False
    # Bank Download URL = ""
    # Bank Download Login = ""
    # Bank Download Auth1 = ""
    # Bank Download Auth2 = ""

    return config


def get_files(format):
    # find the transaction file
    a = g_config["ext"]
    b = g_config["input_filename"]
    c = g_config["fixed_prefix"]
    files = list()
    missing_dir = False
    try_path = g_config["path"]
    path = ""
    if b is not "":
        try:
            path = find_directory(try_path) 
            os.chdir(path)
        except:
            missing_dir = True
            path = find_directory("") 
            os.chdir(path)
        files = [f for f in os.listdir(".") if f.endswith(a) if b in f if c not in f]
        if files != [] and missing_dir is True:
            s = "Format: {}\nCan't find: {}\nTrying: {}".format(format, try_path, path)
            print(s)
    return files
    
def clean_data(file_path):
    # extract data from transaction file
    delim = g_config["input_delimiter"]
    output_columns = g_config["output_columns"]
    has_headers = g_config["has_headers"]
    output_data = []

    with CrossversionCsvReader(file_path, __PY2, delimiter=delim) as transaction_reader:
        # make each row of our new transaction file
        for row in transaction_reader:
            # add new row to output list
            fixed_row = auto_memo(fix_row(row))
            # check our row isn't a null transaction
            if valid_row(fixed_row) is True:
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


def fix_row(row):
    # fixes a row of our file
    output = []
    for header in g_config["output_columns"]:
        try:
            # check to see if our output header exists in input
            index = g_config["input_columns"].index(header)
            cell = row[index]
        except (ValueError, IndexError):
            # header isn't in input, default to blank cell
            cell = ""
        output.append(cell)
    return output


def valid_row(row):
    # if our row doesn't have an inflow or outflow, mark as invalid
    inflow_index = g_config["output_columns"].index("Inflow")
    outflow_index = g_config["output_columns"].index("Outflow")
    if row[inflow_index] == "" and row[outflow_index] == "":
        return False
    return True


def auto_memo(row):
    # auto fill empty memo field with payee info
    payee_index = g_config["output_columns"].index("Payee")
    memo_index = g_config["output_columns"].index("Memo")
    if row[memo_index] == "":
        row[memo_index] = row[payee_index]
    return row


def write_data(filename, data):
    """ write out the new CSV file
    :param filename: path to output file
    :param data: cleaned data ready to output
    """
    new_filename = g_config["fixed_prefix"] + filename
    print("Writing file: {}".format(new_filename))
    with CrossversionCsvWriter(new_filename, __PY2) as writer:
        for row in data:
            writer.writerow(row)
    return


def find_directory(filepath):
    # finds the downloads folder for the active user if path is not set
    if filepath is "":
        if os.name is "nt":
            # Windows
            try:
                import winreg
            except ImportError:
                import _winreg as winreg
            shell_path = "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            dl_key = "{374DE290-123F-4565-9164-39C4925E467B}"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, shell_path) as key:
                input_dir = winreg.QueryValueEx(key, dl_key)[0]
        else:
            # Linux, OSX
            userhome = os.path.expanduser('~')
            input_dir = os.path.join(userhome, "Downloads")
    else:
        if not os.path.exists(filepath):
            raise Exception("Input directory not found: {}".format(filepath))
        input_dir = filepath
    return input_dir
  
  
def main(config_params):
    # initialize variables for summary:
    files_processed = 0
    # get all configuration details
    all_configs = config_params
    # process account for each config file
    for section in all_configs.sections():
        # reset starting directory
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
        # create configuration variables
        global g_config
        g_config = fix_conf_params(all_configs, section)
        # find all applicable files
        files = get_files(section)
        for file in files:
            print("Parsing file: {}".format(file))
            # increment for the summary:
            files_processed += 1
            # create cleaned csv for each file
            output = clean_data(file)
            write_data(file, output)
            # delete original csv file
            if g_config["delete_original"] is True:
                print("Removing file: {}".format(file))
                os.remove(file)
            print("Done!")
    print("{} files processed.".format(files_processed))


# Let's run this thing!
if __name__ == "__main__":
    main(get_configs())

