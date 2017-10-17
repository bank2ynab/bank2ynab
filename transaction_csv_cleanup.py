#! /usr/bin/python
# transaction_csv_cleanup.py
# for Python 3

# Searches specified folder or default download folder for exported
# bank transaction file (.csv format) & adjusts format for YNAB import

# OPERATIONS
#   ~ Find all .conf files & get all configuration within
#   ~ Do following for each configuration found
#   ~ Find & open TransactionExport.csv for processing
#   ~ Change columns from
#       Date, Details, Debit, Credit, Balance to
#       Date, Payee, Category, Memo, Outflow, Inflow & delete Balance column
#   ~ Create blank Category column
#   ~ Copy data from Payee column into Memo column
#   ~ Write new data to new fixed file

# don't edit below here unless you know what you're doing!
import csv, os, sys, configparser

def get_configs():
    # get all our config files
    conf_files = [f for f in os.listdir(".") if f.endswith(".conf")]
    config = configparser.ConfigParser()
    config.read(conf_files)
    return config
    
def fix_conf_params(section): # to do
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
    config["payee_memo_swap"] = section.getboolean("Use Payees for Memo")    
        
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
    
    if b is not "" and g_config["path"] is not "":
        os.chdir(find_directory())
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
        transaction_data = list(transaction_reader)

        # make each row of our new transaction file
        for row in transaction_data:
            # add new row to output list
            output_data.append(fix_row(row))

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
        header = header_swap(header)
        try:
            # check to see if our output header exists in input
            index = g_config["input_columns"].index(header)
            cell = row[index]
        except ValueError:
            # header isn't in input, default to blank cell
            cell = ""
        output.append(cell)
    return output
                
def header_swap(header):
    # replaces one column's value with another if required
    if g_config["payee_memo_swap"] is True:
        if header == "Memo":
            return "Payee"
    return header
                
def write_data(filename, data):
    # write out the new CSV file
    new_filename = g_config["fixed_prefix"] + filename
    with open(new_filename, "w", newline = "") as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)
    return
    
def find_directory():
    # finds the downloads folder for the active user if path is not set
    filepath = g_config["path"]
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
        print("{}, {}".format(section, files))
        for file in files:
            # create cleaned csv for each file
            output = clean_data(file)
            write_data(file, output)
            # delete original csv file
            if g_config["delete_original"] is True:
                os.remove(file)

# Let's run this thing!
main()
