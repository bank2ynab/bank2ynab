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
from __future__ import unicode_literals # python 2.x support
import csv, os, sys

# check which python version we're running for python 2.x support
if sys.version_info[0] == 2:
    import ConfigParser as configparser
else:
    import configparser

def get_configs():
    # get all our config files
    conf_files = [f for f in os.listdir(".") if f.endswith(".conf")]
    if conf_files == []:
        print("Can't find configuration file.")
    config = configparser.ConfigParser()
    config.read(conf_files, encoding = "utf-8")
    return config
    
def fix_conf_params(section):
    # repair parameters from our config file and return as a dictionary
    config = dict()
    config["input_columns"] = section["Input Columns"].split(",")
    config["output_columns"] = section["Output Columns"].split(",")
    config["input_filename"] = section["Source Filename Pattern"]
    config["path"] = section["Source Path"]
    config["ext"] = section["Source Filename Extension"]
    config["fixed_prefix"] = section["Output Filename Prefix"]
    config["input_delimiter"] = section["Source CSV Delimiter"]
    config["has_headers"] = section.getboolean("Source Has Column Headers")
    config["delete_original"] = section.getboolean("Delete Source File")
        
    # # Direct bank download
    # Bank Download = False
    # Bank Download URL = ""
    # Bank Download Login = ""
    # Bank Download Auth1 = ""
    # Bank Download Auth2 = ""

    return config

def get_files():
    # find the transaction file
    a = g_config["ext"]
    b = g_config["input_filename"]
    c = g_config["fixed_prefix"]
    if b is not "":
        try:
            os.chdir(find_directory(g_config["path"]))
        except:
            print("Your specified download directory was not found: {}".format(g_config["path"]))
            os.chdir(find_directory(""))
        return [f for f in os.listdir(".") if f.endswith(a) if b in f if c not in f]
    return []
    
def clean_data(file):
    # extract data from transaction file
    delim = g_config["input_delimiter"]
    output_columns = g_config["output_columns"]
    has_headers = g_config["has_headers"]
    output_data = []
    with open(file) as transaction_file:
        transaction_reader = csv.reader(transaction_file, delimiter = delim)

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
            output_data[0] = output_columns
    
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
    # write out the new CSV file
    new_filename = g_config["fixed_prefix"] + filename
    print("Writing file: {}".format(new_filename))

    # check what version of python we're running to handle csv
    if sys.version_info[0] == 2:
        access = "wb"
        kwargs = {}
    else:
        access = "wt"
        kwargs = {"newline":""}
    
    with open(new_filename, access, **kwargs) as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)
    return
    
def find_directory(filepath):
    # finds the downloads folder for the active user if path is not set
    if filepath is "":
        if os.name is "nt":
            # Windows
            from winreg import OpenKey,  QueryValueEx, HKEY_CURRENT_USER # import Windows-specific stuff here
            shell_path = "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            dl_key = "{374DE290-123F-4565-9164-39C4925E467B}"
            with OpenKey(HKEY_CURRENT_USER, shell_path) as key:
                dir = QueryValueEx(key, dl_key)[0]
        else:
            # Linux
            userhome = os.path.expanduser('~')
            dir = os.path.join(userhome, "Downloads")      
    else:
        dir = filepath
    return dir
    
def main():
    # initialize variables for summary:
    files_processed = 0
    # get all configuration details
    all_configs = get_configs()
    # process account for each config file
    for section in all_configs.sections():
        # reset starting directory
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
        # create configuration variables
        global g_config
        g_config = fix_conf_params(all_configs[section])
        # find all applicable files
        files = get_files()
        for file in files:
            print("Parsing file: {}\nUsing format: {}".format(file, section))
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
main()
